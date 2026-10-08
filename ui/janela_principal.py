"""A janela e o fluxo entre as telas.

Inicio -> Opcoes -> (análise) -> Conferir -> (processamento) -> Pronto

Item 1.1 (29/09/2026): ao abrir pela primeira vez um livro com camadas
(Internet Archive), a janela pergunta "Este livro tem fundo separado. Quer
tirar o fundo?" - ver _perguntar_se_tira_o_fundo.
"""

from __future__ import annotations

import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

import configuracoes
import historico
import projetos
from core.camadas import pdf_tem_camadas
from core.misto import CAMPOS_DO_MISTO
from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
from core.pipeline import (
    CAMPOS_DA_GRAVURA,
    acertar_alertas_do_fundo,
    aviso_das_opcoes_da_gravura,
    trazer_divisao_da_analise,
    trocar_opcoes_da_gravura,
)
from historico_acoes import HistoricoAcoes
from modelos import Projeto
from registro import registrar_erro
from ui.estilo import FOLHA_DE_ESTILO
from ui.tarefas import GerenciadorPrevias, TarefaAnalise, TarefaConverterZonas, TarefaProcessar
from ui.tela_conferir import TelaConferir
from ui.tela_final import TelaFinal, TelaProgresso
from ui.tela_inicio import TelaInicio
from ui.tela_opcoes import TelaOpcoes

INICIO, OPCOES, PROGRESSO, CONFERIR, FINAL = range(5)


# (largura, altura) minimas da janela, em pontos. Ver JanelaPrincipal.__init__.
LARGURA_E_ALTURA_MINIMAS = (1000, 600)


class JanelaPrincipal(QMainWindow):
    """A janela unica do programa: um QStackedWidget com as cinco telas do
    fluxo (ver INICIO..FINAL acima) e a orquestracao entre elas - abrir livro,
    disparar analise e processamento em thread, salvar sozinho, etc.
    Nao ha varias janelas nem dialogo modal para o fluxo principal: trocar de
    tela e so mudar o indice do QStackedWidget."""

    def __init__(self) -> None:
        """Cria as cinco telas, liga os sinais entre elas e monta o menu.
        Comeca sempre na tela de INICIO."""
        super().__init__()
        self.setWindowTitle("Editor de Impressão")
        # Cabe no notebook do Kaique (1920 x 1080 com escala de 150%: area util
        # de ~1280 x 657 pontos, tirada a barra de tarefas e o titulo). Antes o
        # minimo era 1000 x 680 e o tamanho inicial 1220 x 800: a janela
        # passava da tela (pedido da gerente, 30/09). As telas cabem em 600 de
        # altura sem se sobrepor (conferido com as fontes de verdade, a 150%;
        # a lista de opcoes e os paineis da direita ja tem rolagem). Arriscado:
        # subir o minimo de novo acima de ~650.
        self.setMinimumSize(*LARGURA_E_ALTURA_MINIMAS)
        self.resize(*self.tamanho_que_cabe(self.screen().availableGeometry()))
        self.setStyleSheet(FOLHA_DE_ESTILO)

        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None
        self.tarefa = None
        # Tarefas (QThread) que sairam de self.tarefa ainda rodando - uma
        # analise cancelada termina a pagina em que esta antes de parar.
        # Ficam guardadas aqui ate acabar: se o Python soltasse a ultima
        # referencia, o Qt destruiria a thread rodando e derrubaria o
        # programa sem mensagem (verificador, 30/09, s33). Ver _trocar_tarefa.
        self._tarefas_saindo: list = []
        self.total_folhas = 0
        self.resumo: projetos.Resumo | None = None
        # Item 1.1: a caixa "Este livro tem fundo separado..." aberta agora
        # (None quando nao ha). Guardada para os testes (pytest e
        # teste_botoes.py) acharem a caixa e clicarem num dos botoes.
        self.aviso_do_fundo: QMessageBox | None = None
        # A copia do trabalho antigo guardada na ultima vez que a conferencia
        # recomecou por cima de um projeto salvo (projetos.
        # guardar_copia_do_trabalho); None se nao houve copia.
        self.copia_do_trabalho = None
        # O projeto em memoria e o trabalho de verdade (voltou de
        # _analise_pronta)? False entre abrir o livro (ou disparar uma nova
        # analise) e o fim da analise: nesse intervalo o projeto em memoria
        # esta vazio ou pela metade, e gravar por cima de um trabalho salvo o
        # apagaria (bug grave de 29/09/2026; ver _salvar_agora).
        self.trabalho_carregado = False
        # O valor de trabalho_carregado quando a analise em curso comecou: e
        # o que volta se ela for cancelada ou der erro (_parar_a_analise).
        self._carregado_antes_da_analise = False
        # As opcoes da tela "O que fazer" do trabalho carregado, guardadas ao
        # sair da conferencia para "O que fazer" (_sair_da_conferencia). Se a
        # pessoa mudar uma opcao, clicar "Conferir" e cancelar, sao elas que
        # voltam (_parar_a_analise). None quando nao ha o que devolver.
        self._opcoes_do_trabalho: dict | None = None
        # Item 1.1: "Sim, tirar o fundo" respondido antes de o trabalho salvo
        # carregar (projeto antigo, ou pelo "continuar"): a pasta do projeto
        # que espera o livro inteiro ir para o filtro em _analise_pronta.
        self._fundo_pendente: str | None = None
        # Decisao Z1 (b) do Samuel (05/10/2026): a tarefa que converte por
        # tras as zonas do livro aberto para o formato novo (zonas na folha
        # original). None quando nao ha. Ver _comecar_a_converter_as_zonas.
        self.conversao_das_zonas: TarefaConverterZonas | None = None
        # D2 do girar (06/10/2026): o giro da primeira folha com que a capa do
        # cartao (capa.png) foi desenhada por ultimo, nesta sessao. A capa
        # nasce como veio no PDF (projetos.garantir_miniatura): 0. Ver
        # _acertar_a_capa.
        self._giro_da_capa = 0

        # Salvar sozinho, com um respiro. Gravar a cada mudanca travaria a tela
        # ao arrastar o medidor - sao dezenas de mudancas por segundo, e o
        # projeto de um livro de mil paginas nao e um arquivo pequeno. O relogio
        # junta a rajada e grava uma vez depois que a mao para.
        #
        # NAO existe botao de salvar e nunca se pergunta "quer salvar?". Essa
        # pergunta e uma armadilha para quem nao e tecnico: um "nao" por engano
        # apaga um dia de trabalho.
        #
        # O relogio grava POR TRAS (_salvar_por_tras, R1 de 05/10/2026): ele
        # dispara a cada pagina folheada, e gravar o projeto inteiro no fio da
        # janela a deixava 0,25 a 0,37 s parada a cada pagina num livro de 268
        # paginas (mais com o disco lento ou o computador sem memoria livre).
        self._relogio_de_salvar = QTimer(self)
        self._relogio_de_salvar.setSingleShot(True)
        self._relogio_de_salvar.setInterval(600)
        self._relogio_de_salvar.timeout.connect(self._salvar_por_tras)

        self.telas = QStackedWidget()
        self.setCentralWidget(self.telas)
        self.telas.currentChanged.connect(self._tela_mudou)

        self.tela_inicio = TelaInicio()
        self.tela_inicio.abrir_pdf.connect(self.abrir_livro)
        self.tela_inicio.continuar_projeto.connect(self._continuar_projeto)
        self.tela_inicio.recomecar_projeto.connect(self._recomecar_projeto)
        self.tela_inicio.vai_tirar_da_lista.connect(self._soltar_o_livro_tirado_da_lista)
        self.telas.addWidget(self.tela_inicio)

        self.tela_opcoes = TelaOpcoes()
        # o voltar das opcoes remonta os cartoes (_voltar_das_opcoes). Ligado
        # por lambda DE PROPOSITO: ligado direto ao metodo, o
        # tests/test_misto_na_tela.py caia com "access violation" em 5 de 6
        # rodadas (06/10/2026, PySide6 6.11; com lambda, 0 de 6). Causa nao
        # achada. Arriscado: trocar pelo metodo sem repetir aquele teste.
        self.tela_opcoes.voltar.connect(lambda: self._voltar_das_opcoes())
        self.tela_opcoes.conferir.connect(self.analisar)
        self.telas.addWidget(self.tela_opcoes)

        self.tela_progresso = TelaProgresso()
        self.tela_progresso.cancelar.connect(self.cancelar)
        self.telas.addWidget(self.tela_progresso)

        self.tela_conferir = TelaConferir()
        self.tela_conferir.voltar.connect(self._sair_da_conferencia)
        self.tela_conferir.processar.connect(self.processar)
        self.tela_conferir.trabalho_mudou.connect(self._marcar_para_salvar)
        self.telas.addWidget(self.tela_conferir)

        self.tela_final = TelaFinal()
        self.tela_final.fazer_outro.connect(self._recomecar)
        self.telas.addWidget(self.tela_final)

        self._montar_menu()

        # Carrega as teclas que o Samuel remapeou, por cima dos padroes - so
        # depois de _montar_menu(), porque so ai TODA acao (menu, ferramentas
        # de marcar, navegacao, espelhado/proporcao) ja se registrou em
        # atalhos.py. reaplicar_atalhos() copia o resultado para os QAction de
        # verdade, que ja tinham nascido com a tecla padrao.
        import atalhos

        atalhos.carregar_de(configuracoes.ler("atalhos"))
        self.menu.reaplicar_atalhos()

        self.telas.setCurrentIndex(INICIO)
        self._tela_mudou(INICIO)

    # ------------------------------------------------------------------
    # a barra de menu
    # ------------------------------------------------------------------

    def _montar_menu(self) -> None:
        """Liga cada item do menu a uma acao que ja existe.

        Nada aqui e funcionalidade nova: sao os mesmos comandos que eram botoes
        soltos na tela, agora num lugar so, com o atalho escrito ao lado.
        """
        from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO
        from ui.barra_de_menu import BarraDeMenu

        self.menu = BarraDeMenu(self)
        self.setMenuBar(self.menu)
        conferir = self.tela_conferir

        self.menu.ligar("abrir", self.tela_inicio.area.abrir_dialogo_de_arquivo)
        self.menu.ligar("pasta_de_saida", self._escolher_pasta_de_saida)
        self.menu.ligar("nome_do_arquivo", self._escolher_nome_do_arquivo)
        self.menu.ligar("processar", self.processar)
        self.menu.ligar("voltar", self._sair_da_conferencia)
        self.menu.ligar("sair", self.close)

        self.menu.ligar("desfazer", conferir.desfazer)
        self.menu.ligar("refazer", conferir.refazer)

        self.menu.ligar("procurar_de_novo", conferir._detectar_de_novo)
        self.menu.ligar("limpar_marcacao", conferir._limpar_marcacao)
        self.menu.ligar("folha_em_branco", conferir._folha_em_branco)

        for chave in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            self.menu.ligar(f"filtro_{chave}",
                            lambda _marcado=False, f=chave: conferir._escolher_filtro(f))

        self.menu.ligar("ir_para_pagina", self._perguntar_a_pagina)
        # Item 2.3 (girar): os tres giros e o "Aplicar o giro em", que e o
        # mesmo da barrinha em cima da pagina - os dois ficam sempre iguais.
        self.menu.ligar("girar", conferir._girar)
        self.menu.ligar("girar_esquerda", conferir._girar_esquerda)
        self.menu.ligar("girar_meia_volta", conferir._girar_meia_volta)
        from core.girar import ALCANCES

        for alcance in ALCANCES:
            self.menu.ligar(f"giro_em_{alcance}",
                            lambda _marcado=False, a=alcance: conferir.barra_girar.definir_alcance(a))
        conferir.barra_girar.alcance_mudou.connect(self._alcance_do_giro_mudou)
        conferir.marcacoes_por_converter.connect(self._converter_as_zonas_se_parado)
        self.menu.atalhos_mudaram.connect(self._mostrar_teclas_do_giro)
        self.menu.ligar("apagar", conferir.apagar_pagina)

        self.menu.ligar("atalhos", self._mostrar_atalhos)
        self.menu.ligar("configuracoes", self._abrir_configuracoes)

    def _converter_as_zonas_se_parado(self) -> None:
        """O giro (item 2.3) achou zonas ainda no formato antigo: se a
        conversao por tras nao estiver andando (parou, ou falhou numa folha),
        comeca de novo. Andando, deixa como esta."""
        tarefa = self.conversao_das_zonas
        if tarefa is None or not tarefa.isRunning():
            self._comecar_a_converter_as_zonas()

    def _alcance_do_giro_mudou(self, alcance: str) -> None:
        """A lista "aplicar em" da barrinha mudou: o menu Pagina acompanha."""
        item = self.menu.acoes.get(f"giro_em_{alcance}")
        if item is not None and not item.isChecked():
            item.setChecked(True)

    def _mostrar_teclas_do_giro(self) -> None:
        """Escreve a tecla de cada giro no balao dos botoes da barrinha
        (a tecla de verdade e a do menu, que pode ter sido trocada nas
        Configuracoes)."""
        from core.girar import GIRO_DIREITA, GIRO_ESQUERDA, GIRO_MEIA_VOLTA

        teclas = {}
        for giro, chave in ((GIRO_ESQUERDA, "girar_esquerda"), (GIRO_DIREITA, "girar"),
                            (GIRO_MEIA_VOLTA, "girar_meia_volta")):
            atalho = self.menu.acoes[chave].shortcut()
            if not atalho.isEmpty():
                texto = atalho.toString(QKeySequence.NativeText)
                # no balao, em portugues (o menu mostra como o Qt escreve)
                for ingles, portugues in (("Left", "seta para a esquerda"),
                                          ("Right", "seta para a direita"),
                                          ("Up", "seta para cima"), ("Down", "seta para baixo")):
                    texto = texto.replace(ingles, portugues)
                teclas[giro] = texto
        self.tela_conferir.barra_girar.definir_teclas(teclas)

    def _tela_mudou(self, indice: int) -> None:
        """So a tela de Conferir usa o menu completo; nas outras ele fica apagado."""
        if not hasattr(self, "menu"):
            return
        if indice == CONFERIR:
            self.menu.mostrar_tela_de_trabalho()
        else:
            self.menu.mostrar_tela_inicial()

    def _escolher_pasta_de_saida(self) -> None:
        """Item de menu "Escolher a pasta de saída...": so lembra a pasta
        padrao, quem decide o destino de verdade e a janela de confirmacao."""
        from PySide6.QtWidgets import QFileDialog

        if self.projeto is None:
            return
        pasta = QFileDialog.getExistingDirectory(
            self, "Onde salvar o livro pronto",
            self.projeto.caminho_saida or str(historico.pasta_de_saida_padrao()))
        if pasta:
            configuracoes.lembrar_pasta_de_saida(Path(pasta))
            self.avisar(f"O livro pronto vai para:\n{pasta}", titulo="Pasta escolhida")

    def _escolher_nome_do_arquivo(self) -> None:
        """Item de menu "Nome do arquivo...": pede o nome e ja monta o caminho
        de saida completo com a pasta atual (ou a sugerida)."""
        from modelos import nome_de_saida_sugerido
        from ui import perguntas

        if self.projeto is None:
            return
        atual = Path(self.projeto.caminho_saida).name if self.projeto.caminho_saida \
            else nome_de_saida_sugerido(self.projeto)
        novo, certo = perguntas.pedir_texto(
            self, "Nome do arquivo", "Como o PDF pronto vai se chamar:", atual)
        if certo and novo.strip():
            pasta = (Path(self.projeto.caminho_saida).parent
                     if self.projeto.caminho_saida
                     else configuracoes.pasta_de_saida_sugerida())
            self.projeto.caminho_saida = str(Path(pasta) / novo.strip())

    def _perguntar_a_pagina(self) -> None:
        """Item de menu "Ir para a página...": pede o número e pula direto."""
        from ui import perguntas

        if self.projeto is None or not self.projeto.paginas:
            return
        total = len(self.projeto.paginas)
        numero, certo = perguntas.pedir_numero(
            self, "Ir para a página", f"Página (1 a {total}):",
            self.tela_conferir.indice_pagina + 1, 1, total)
        if certo:
            self.tela_conferir.ir_para_pagina(numero - 1)

    def _abrir_configuracoes(self) -> None:
        from ui.tela_configuracoes import TelaConfiguracoes

        TelaConfiguracoes(self).exec()

    def _mostrar_atalhos(self) -> None:
        """A lista sai dos proprios menus - nunca de uma segunda lista."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Lista de atalhos")
        caixa.setText("O que dá para fazer, e por qual tecla:")
        caixa.setDetailedText(self.menu.texto_dos_atalhos())
        caixa.addButton("fechar", QMessageBox.AcceptRole)
        caixa.exec()

    # ------------------------------------------------------------------
    # avisos
    # ------------------------------------------------------------------

    @staticmethod
    def tamanho_que_cabe(area_util) -> tuple[int, int]:
        """O tamanho inicial da janela: 1220 x 800, ou menos se a area util da
        tela (QRect, sem a barra de tarefas) for menor - tirando uns 40 pontos
        para o titulo e a moldura da janela. Nunca abaixo do minimo."""
        largura_min, altura_min = LARGURA_E_ALTURA_MINIMAS
        largura = max(largura_min, min(1220, area_util.width() - 16))
        altura = max(altura_min, min(800, area_util.height() - 40))
        return largura, altura

    def avisar(self, mensagem: str, titulo: str = "Um momento") -> None:
        """Regra 3.3: erro vira aviso gentil e o programa continua aberto."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle(titulo)
        caixa.setIcon(QMessageBox.Information)
        caixa.setText(mensagem)
        caixa.addButton("entendi", QMessageBox.AcceptRole)
        caixa.exec()

    # ------------------------------------------------------------------
    # fluxo
    # ------------------------------------------------------------------

    def abrir_livro(self, caminho: str, resumo: projetos.Resumo | None = None) -> None:
        """Ponto de entrada de "abrir um livro novo": valida o PDF, cria (ou
        recupera) o Projeto e o resumo em disco, e vai para a tela de Opções.
        Chamada tambem por _continuar_projeto/_recomecar_projeto, que so
        preenchem o Projeto com o que ja estava salvo depois desta abertura.

        `resumo`: o projeto EXATO a abrir (o do cartao da tela inicial, pelo
        "continuar" ou pelo "comecar de novo"). Sem ele ("Abrir", arrastar,
        Windows), o projeto e achado pela assinatura do arquivo - o mais
        recente, se houver mais de um do mesmo PDF. Antes o cartao tambem
        passava pela assinatura, e o "continuar" do cartao mais antigo abria
        o mais recente (verificador, 29/09, q24-q25). Arriscado: voltar a
        procurar pela assinatura quando o cartao ja disse qual e.

        Antes de tudo, a mudanca do livro aberto que ainda esperava o relogio
        de salvar vai para o disco NA HORA (_guardar_o_livro_aberto; R-A do
        verificador-2, 06/10/2026): trocar de livro pelo Ctrl+O menos de
        0,6 s depois de uma mudanca a perdia.
        Arriscado: mover essa gravacao para depois de self.projeto/self.resumo
        mudarem (gravaria o livro novo, ou nada).
        """
        self._guardar_o_livro_aberto()
        try:
            doc = abrir_pdf(caminho)
            try:
                self.total_folhas = doc.page_count
                info_paginas(doc)
                # Item 1.1: o PDF vem com camadas (Internet Archive)? Só a
                # estrutura de até 12 páginas, sem desenhar nenhuma
                # (milissegundos). Decide se o filtro "Tirar o fundo" aparece
                # e se a janela pergunta se quer tirar o fundo.
                tem_camadas = pdf_tem_camadas(doc)
            finally:
                doc.close()
        except ErroPDF as erro:
            self.avisar(str(erro))
            return
        except Exception:  # noqa: BLE001
            registrar_erro("abrir", traceback.format_exc())
            self.avisar("Não consegui abrir esse arquivo. Ele pode não ser um PDF.")
            return

        nome = Path(caminho).stem
        # Uma analise do livro de antes (trocar de livro no meio) e marcada
        # como cancelada, rodando ou ja terminada com o resultado na fila: o
        # resultado dela nao pode chegar no livro novo (_analise_pronta
        # ignora resultado de analise cancelada).
        if isinstance(self.tarefa, TarefaAnalise):
            self.tarefa.cancelar()
        # A conversao das zonas do livro de antes para: o que ela ja fez foi
        # gravado com o trabalho dele; o resto continua da proxima vez.
        self._parar_a_conversao_das_zonas(gravar=True)
        self.trabalho_carregado = False       # ate a analise acabar (_salvar_agora)
        self._fundo_pendente = None
        self._opcoes_do_trabalho = None
        self.projeto = Projeto(caminho_entrada=caminho, nome=nome)
        self.projeto.tem_camadas = tem_camadas

        # Abrir o MESMO livro de novo continua o projeto de antes, em vez de
        # criar um ao lado: quem for reabrir de propósito passa pela tela
        # inicial, que tem "começar de novo" no menu do cartão.
        self.resumo = resumo if resumo is not None else projetos.achar_por_assinatura(caminho)
        livro_novo = self.resumo is None
        salvo = None
        if livro_novo:
            self.resumo = projetos.criar(self.projeto, self.total_folhas)
        else:
            self.resumo.caminho_entrada = caminho   # pode ter mudado de pasta
            # Livro com projeto salvo, aberto por QUALQUER caminho ("Abrir",
            # arrastar, Windows, "continuar"): a tela "O que fazer" vem com as
            # opcoes salvas. Antes so o "continuar" as trazia; pelo "Abrir",
            # "Dividir folhas ao meio" desmarcada voltava marcada e a
            # conferencia recomecava sem a pessoa mudar nada (parecer do
            # verificador de 29/09, p25-p26), e o filtro do livro aparecia em
            # Original (print t10 da rodada de 18:26).
            salvo = projetos.carregar_estado(self.resumo)
            self._trazer_opcoes_salvas(salvo)
        self.acoes = HistoricoAcoes(Path(self.resumo.pasta))
        self._giro_da_capa = 0           # a capa nasce como veio no PDF (D2)

        self.tela_opcoes.carregar(self.projeto, self.total_folhas)
        self.telas.setCurrentIndex(OPCOES)

        # Item 1.1, decisao do Samuel (29/09, Registro de mudancas): a
        # pergunta aparece "uma vez por livro, inclusive nos que ele ja tem:
        # na proxima vez que abrir, e depois nao pergunta mais". Por qualquer
        # caminho (Abrir, arrastar, Windows, "continuar"). Ja perguntou =
        # Projeto.perguntou_fundo no projeto salvo (projeto antigo sem o
        # campo: ainda nao). Substitui a decisao da gerente de perguntar so em
        # projeto novo. Livro sem camadas: nunca pergunta. Depois do "comecar
        # de novo" (o projeto salvo e apagado) pergunta de novo.
        ja_perguntou = salvo is not None and salvo.perguntou_fundo
        if tem_camadas and not ja_perguntou:
            self._perguntar_se_tira_o_fundo()

    def _perguntar_se_tira_o_fundo(self) -> None:
        """Item 1.1: "Este livro tem fundo separado. Quer tirar o fundo?"

        Palavras do Samuel (29/09/2026): "Ao abrir um livro com camadas, o
        programa pode avisar: 'Este livro tem fundo separado. Quer tirar o
        fundo?'". Sim = o filtro do livro vira "Tirar o fundo" (todas as
        paginas nascem nele, na analise); Nao = nada muda (tudo em Original).

        A caixa e aberta com open(), e nao exec(): nao para o programa
        esperando a resposta (o resto da janela fica parado atras dela, que e
        modal para a janela, mas a interface nao congela) e os testes
        automaticos conseguem responder clicando no botao (self.aviso_do_fundo).
        Fechar pelo X ou pelo Esc vale como "Nao".
        """
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Fundo separado")
        caixa.setIcon(QMessageBox.Question)
        caixa.setText("Este livro tem fundo separado. Quer tirar o fundo?")
        caixa.setInformativeText(
            "Tirar o fundo deixa o papel branco e só o que está impresso, em "
            "todas as páginas. Dá para mudar depois, página por página, na "
            "lista de filtros.")
        sim = caixa.addButton("Sim, tirar o fundo", QMessageBox.AcceptRole)
        nao = caixa.addButton("Não, deixar como está", QMessageBox.RejectRole)
        caixa.setDefaultButton(nao)
        caixa.setEscapeButton(nao)
        # O livro que perguntou e identificado pela PASTA do projeto, e nao
        # pelo objeto Projeto: pelo "continuar", a analise termina atras da
        # pergunta e troca o objeto da tela (o salvo volta por cima). Antes a
        # resposta dada depois disso era jogada fora (verificador, s19-s21).
        pasta = self.resumo.pasta if self.resumo is not None else None

        def respondeu(_codigo: int) -> None:
            self._resposta_do_aviso_do_fundo(pasta, caixa.clickedButton() is sim)
            if self.aviso_do_fundo is caixa:
                self.aviso_do_fundo = None
            caixa.deleteLater()

        caixa.finished.connect(respondeu)
        self.aviso_do_fundo = caixa
        caixa.open()

    def _resposta_do_aviso_do_fundo(self, pasta: str | None, tirar: bool) -> None:
        """Aplica a resposta do aviso do item 1.1, a QUALQUER momento.

        A resposta vale para o projeto que perguntou (`pasta`), enquanto ele
        estiver aberto - antes, durante ou depois da analise (pelo
        "continuar" a analise roda atras da pergunta). Outro livro aberto no
        meio: a resposta nao vale (so pelo teste; a caixa e modal).

        Nao (e Esc, e X): fica anotado "ja perguntou" (Projeto.perguntou_fundo)
        na hora, e nada mais muda. Projeto antigo nunca vem com o fundo
        tirado sem o "Sim".

        Sim - depende de haver trabalho na tela:
          - trabalho carregado (conferencia aberta): aplica ja
            (_tirar_o_fundo_do_livro_inteiro) e grava;
          - livro sem trabalho salvo (novo, ou so com as opcoes): o filtro do
            livro vira "Tirar o fundo" e e gravado com as opcoes, junto com o
            "ja perguntou". As paginas nascem nele na analise. Fechar antes de
            "Conferir" nao perde nada: o filtro do livro ja esta no disco;
          - projeto com trabalho salvo, ainda nao carregado ("O que fazer", ou
            "Olhando o livro..." do "continuar"): o "Sim" espera o trabalho
            carregar (_fundo_pendente, em _analise_pronta) e so entao conta
            como respondido. Se o programa fechar, a pessoa voltar ou cancelar
            antes, nada foi aplicado e NADA fica anotado: a pergunta volta na
            proxima abertura (verificador, s23). Escolhido por ser o mais
            simples e seguro: mexer no projeto.json do trabalho sem o carregar
            (trocar filtros direto no disco) pularia o Historico e a trava
            que nao grava por cima do trabalho antes da analise.

        Seguro mudar: os textos. Arriscado: anotar "ja perguntou" para um
        "Sim" que ainda nao foi aplicado (o "Sim" se perdia calado).
        """
        from core.filtros import TIRAR_FUNDO

        if pasta is None or self.resumo is None or self.resumo.pasta != pasta:
            return
        if self.projeto is None:
            return
        na_tela_o_que_fazer = (self.telas.currentIndex() == OPCOES
                               and self.tela_opcoes.projeto is self.projeto)
        if not tirar:
            self.projeto.perguntou_fundo = True
            if not projetos.anotar_no_estado(self.resumo, perguntou_fundo=True):
                self._salvar_agora()
            return

        if self.trabalho_carregado:
            self.projeto.perguntou_fundo = True
            self._tirar_o_fundo_do_livro_inteiro()
            self._salvar_agora()
            return
        if na_tela_o_que_fazer:
            self.tela_opcoes.escolher_filtro_do_livro(TIRAR_FUNDO)
        else:
            self.projeto.filtro_padrao = TIRAR_FUNDO
        self._fundo_pendente = pasta
        if not projetos.tem_trabalho_salvo(self.resumo):
            self.projeto.perguntou_fundo = True
            self._salvar_agora()          # opcoes, com o filtro do livro

    def _tirar_o_fundo_do_livro_inteiro(self) -> None:
        """O "Sim" da pergunta do fundo num livro com paginas carregadas.

        Decisao do Samuel (29/09, f94f69b): troca SO as paginas que estao em
        "Original"; as que ele pos em outro filtro ficam. E o filtro do livro
        vira "Tirar o fundo". Tudo numa acao so do Historico ("Tirar o fundo
        em N paginas"), e o desfazer devolve tambem o filtro do livro (campo
        "livro.filtro_padrao" da acao, historico_acoes.aplicar; verificador,
        s17). So o filtro muda: corte, conferidas e alertas ficam.
        Marca o projeto como "ja perguntou" (o "Sim" foi aplicado).
        """
        from core.filtros import ORIGINAL, TIRAR_FUNDO
        from historico_acoes import aplicar, montar_acao

        self._fundo_pendente = None
        if self.projeto is None:
            return
        self.projeto.perguntou_fundo = True
        indices = [p.indice for p in self.projeto.paginas if p.filtro == ORIGINAL]
        filtro_do_livro = self.projeto.filtro_padrao
        conferir = self.tela_conferir
        if conferir.projeto is not self.projeto or self.acoes is None:
            self.projeto.filtro_padrao = TIRAR_FUNDO
            return
        if not indices and filtro_do_livro == TIRAR_FUNDO:
            return
        acao = montar_acao(
            self.projeto, "aplicar_em_todas", "pagina", indices, {"filtro": TIRAR_FUNDO},
            f"Tirar o fundo em {len(indices)} páginas (resposta à pergunta do fundo)")
        acao.antes["livro.filtro_padrao"] = filtro_do_livro
        acao.depois["livro.filtro_padrao"] = TIRAR_FUNDO
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)
        if conferir.previas is not None:
            for indice in indices:
                conferir.previas.invalidar(indice)
        conferir.atualizar()

    def _continuar_projeto(self, resumo: projetos.Resumo) -> None:
        """Retoma um projeto exatamente onde parou.

        A tela inicial ja conferiu que o livro esta la e que e ELE - o cartao
        so oferece "continuar" quando a assinatura bate. Aqui a analise roda de
        novo (e barata perto de perder o trabalho) e o estado salvo volta por
        cima dela, em `_analise_pronta`.
        """
        self.abrir_livro(resumo.caminho_entrada, resumo=resumo)   # ESTE projeto
        if self.projeto is None:
            return

        # As opcoes salvas ja vieram em abrir_livro (do projeto do cartao).
        # Aqui vem de novo, do mesmo projeto: nao muda nada, e fica por
        # garantia caso abrir_livro deixe de traze-las.
        self._trazer_opcoes_salvas(projetos.carregar_estado(resumo))
        self.analisar()

    def _trazer_opcoes_salvas(self, salvo: Projeto | None) -> None:
        """Poe no projeto recem-aberto as opcoes da tela "O que fazer" do
        projeto salvo (dividir, limpar, filtro do livro, endireitar, cortar,
        cadernos) e redesenha a tela. Sem salvo, nada muda (opcoes de fabrica).

        Usado por abrir_livro (qualquer caminho de abertura) e por
        _continuar_projeto. O tem_camadas nao volta do salvo (item 1.1: e fato
        do PDF, acabou de ser detectado em abrir_livro); o "Tirar o fundo"
        volta com o filtro do livro, aqui, e com o das paginas, em
        _analise_pronta. Seguro mudar: acrescentar opcao nova da tela.
        Arriscado: trazer folhas/paginas daqui (quem traz e _analise_pronta,
        depois de conferir que combinam).
        """
        if salvo is None or self.projeto is None:
            return
        self.projeto.dividir_folhas = salvo.dividir_folhas
        # item 2.1: o jeito de dividir e o corte da sobra (o salvo de antes
        # do 2.1 ja volta "programa" e sem sobra: modelos.Projeto.de_dicionario)
        self.projeto.dividir_como = getattr(salvo, "dividir_como", self.projeto.dividir_como)
        self.projeto.cortar_sobra = bool(getattr(salvo, "cortar_sobra", False))
        self.projeto.limpar = salvo.limpar
        self.projeto.filtro_padrao = salvo.filtro_padrao
        self.projeto.endireitar = salvo.endireitar
        # item 2.2: a conta do endireitar (o salvo de antes do 2.2 ja volta
        # "programa": modelos.Projeto.de_dicionario)
        self.projeto.endireitar_como = getattr(salvo, "endireitar_como", self.projeto.endireitar_como)
        self.projeto.cortar_bordas = salvo.cortar_bordas
        self.projeto.montar_cadernos = salvo.montar_cadernos
        self.projeto.paginas_por_caderno = salvo.paginas_por_caderno
        self.projeto.perguntou_fundo = salvo.perguntou_fundo      # item 1.1
        # item 1.2: o grupo "Gravuras e fotos"
        for campo in CAMPOS_DA_GRAVURA:
            setattr(self.projeto, campo, getattr(salvo, campo))
        # emenda N2 do Samuel (30/09): moldura e iluminura tambem no P&B
        self.projeto.pb_decoracao_em_preto_e_branco = bool(
            getattr(salvo, "pb_decoracao_em_preto_e_branco", False))
        # modo Misto (05/10): "So as letras" e as escolhas do livro (projeto
        # antigo, sem os campos, volta com os padroes: Misto desligado)
        for campo in CAMPOS_DO_MISTO:
            setattr(self.projeto, campo, getattr(salvo, campo, getattr(self.projeto, campo)))
        # "Limpar pontinhos" do livro (06/10): o projeto.json antigo ja volta
        # "nosso" (modelos.Projeto.de_dicionario); objeto sem o campo, o de agora
        self.projeto.limpar_pontinhos = getattr(salvo, "limpar_pontinhos",
                                                self.projeto.limpar_pontinhos)
        self.tela_opcoes.carregar(self.projeto, self.total_folhas)

    def _recomecar_projeto(self, resumo: projetos.Resumo) -> None:
        """Joga fora os ajustes e abre o livro limpo. O PDF nao e tocado.

        Antes de apagar (R-A do verificador-2, 06/10/2026): o livro aberto
        vai para o disco (_guardar_o_livro_aberto) - se for OUTRO livro, a
        ultima mudanca dele nao se perde. Se for ESTE mesmo, o trabalho dele e
        justamente o que vai ser jogado fora: depois de gravado, a janela o
        solta (self.resumo = None), para o abrir_livro logo abaixo nao o
        gravar de novo por cima dos arquivos apagados. E espera a fila do
        fio de gravar, para nenhuma gravacao por tras chegar depois do
        apagar. Arriscado: apagar antes de gravar o livro aberto, ou deixar
        self.resumo apontando para a pasta apagada.
        """
        from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO

        pasta = Path(resumo.pasta)
        self._guardar_o_livro_aberto()
        if self.resumo is not None and projetos.mesmo_arquivo(self.resumo.pasta, pasta):
            self._parar_a_conversao_das_zonas()
            self.resumo = None
            self.trabalho_carregado = False
        projetos.esperar_gravacoes()
        for arquivo in (projetos.ARQUIVO_ESTADO, ARQUIVO_ACOES, ARQUIVO_POSICAO):
            try:
                (pasta / arquivo).unlink(missing_ok=True)
            except OSError:
                pass
        resumo.conferidas = 0
        resumo.pagina_atual = 0
        resumo.pdf_gerado = False
        projetos.gravar_resumo(resumo)
        self.tela_inicio.recarregar()
        self.abrir_livro(resumo.caminho_entrada, resumo=resumo)   # ESTE projeto, limpo

    def _soltar_o_livro_tirado_da_lista(self, resumo: projetos.Resumo) -> None:
        """O "Tirar da lista" foi confirmado na tela inicial e a pasta do
        projeto vai ser apagada (TelaInicio.vai_tirar_da_lista, emitido ANTES
        de apagar). Se e o livro aberto, a janela o solta AGORA: para o
        relogio de salvar, para a conversao das zonas dele SEM gravar, e fica
        sem livro aberto (self.resumo = None, como o "comecar de novo" do
        proprio livro). Livro que nao e o aberto: nada muda.

        R-B do verificador-3 (06/10/2026): a janela continuava com o livro
        tirado em self.resumo, e o fechar (closeEvent -> _salvar_agora), o
        relogio de salvar (_salvar_por_tras, que o fim da conversao das zonas
        liga em _conversao_terminou) e o parar da conversao ao trocar de
        livro (abrir_livro, gravar=True) gravavam o livro de novo: a pasta
        voltava, e o cartao tambem (Siebmacher: 69,6 s depois, quando a
        conversao terminou). Com self.resumo None, _salvar_agora e
        _marcar_para_salvar nao fazem nada, e o sinal atrasado da conversao
        parada nao entra (_conversao_terminou confere a tarefa da vez). A
        segunda camada fica em projetos (o gravador nao recria pasta de
        projeto que sumiu).

        Nao grava nada antes: a pessoa confirmou que a conferencia desse
        livro se perde, e o que a conversao fez e refeito na proxima vez (se
        o "Tirar da lista" falhar e o cartao ficar). Arriscado: gravar aqui
        (recriaria o que vai ser apagado, se viesse depois), ou deixar
        self.resumo apontando para a pasta apagada.
        Teste: tests/test_tirar_da_lista_nao_volta.py.
        """
        if self.resumo is None or not projetos.mesmo_arquivo(self.resumo.pasta, resumo.pasta):
            return
        self._relogio_de_salvar.stop()
        self._parar_a_conversao_das_zonas(gravar=False)
        self.resumo = None
        self.trabalho_carregado = False
        self._fundo_pendente = None
        self._opcoes_do_trabalho = None

    # --- analise ----------------------------------------------------------

    def analisar(self) -> None:
        """Dispara a análise (dividir/endireitar/recorte/alertas) numa
        TarefaAnalise em QThread - a interface nunca congela (regra 3)."""
        if self.projeto is None:
            return
        # Ate a analise acabar, nada e gravado por cima do trabalho salvo
        # (_salvar_agora). Se ela for cancelada ou der erro, o marcador volta
        # ao valor de antes (_parar_a_analise): senao, depois de "cancelar"
        # em "Olhando o livro..." nada mais era gravado ate fechar, sem aviso
        # (bug grave do verificador, 29/09, prints q21-q23).
        self._carregado_antes_da_analise = self.trabalho_carregado
        self.trabalho_carregado = False
        self.tela_progresso.comecar("Olhando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        # A analise trabalha numa COPIA rasa do projeto: ela so troca
        # tem_camadas, observacoes, folhas e paginas (atribui listas novas,
        # nao mexe nas de antes - core.pipeline.analisar_projeto), entao o
        # projeto da tela (com o trabalho) fica intacto ate _analise_pronta.
        # E isso que torna seguro voltar o marcador ao cancelar: antes, um
        # cancelar no instante em que a analise terminava podia deixar as
        # paginas novas, em branco, no projeto da tela. Arriscado: passar
        # self.projeto direto, ou analisar_projeto passar a mexer DENTRO das
        # listas do projeto recebido.
        import copy

        self._trocar_tarefa(TarefaAnalise(copy.copy(self.projeto)))
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._analise_pronta)
        self.tarefa.falhou.connect(self._falhou_na_analise)
        self.tarefa.start()

    def _analise_pronta(self, projeto: Projeto) -> None:
        assert self.acoes is not None
        # Resultado de uma analise que nao e mais a da vez (cancelada, ou de
        # um livro de antes: trocar de livro no meio) nao entra: traria as
        # paginas de outro livro, ou de uma analise que a pessoa desistiu,
        # para o projeto aberto. Chamada direta (testes) nao tem remetente.
        origem = self.sender()
        if isinstance(origem, TarefaAnalise) and (
                origem is not self.tarefa or origem.foi_cancelada):
            return

        # O trabalho da sessao passada volta AQUI, depois da analise: filtro de
        # cada pagina, corte, angulo, marcacao, apagadas, conferidas. Sem isto,
        # quem conferiu 80 paginas e fechou o programa reabria do zero.
        #
        # So volta se combinar com o livro recem-analisado - mesmo arquivo,
        # mesma contagem de folhas e de paginas. Se a pessoa mudou "dividir
        # folhas ao meio" entre uma sessao e outra, a pagina 40 salva nao e a
        # pagina 40 de agora, e devolver o corte de uma na outra estragaria o
        # trabalho em silencio. Ver projetos.combina_com.
        paginas_perdidas = 0
        motivo = ""
        gravuras_refeitas = 0
        recomecou = False         # o trabalho salvo nao serviu (ver o else abaixo)
        self.copia_do_trabalho = None
        if self.resumo is not None:
            salvo = projetos.carregar_estado(self.resumo)
            # A assinatura do projeto entra na comparacao: livro que mudou de
            # pasta, ou copia do mesmo PDF em outra pasta, e o mesmo livro
            # (bug grave de 29/09; ver projetos._mesmo_livro).
            if projetos.combina_com(salvo, projeto, assinatura=self.resumo.assinatura):
                # Item 1.1: o salvo volta por cima, menos o tem_camadas, que e
                # fato do PDF (a analise acabou de detectar; um projeto salvo
                # antes de 29/09 nem tem o campo). O filtro "Tirar o fundo" de
                # cada pagina volta com o salvo, como qualquer filtro - pelo
                # "Abrir" ou pelo "continuar", do mesmo jeito.
                salvo.tem_camadas = projeto.tem_camadas
                # O mesmo arquivo pode ter chegado escrito de outro jeito
                # (`\` pelo Windows, `/` pela caixa "Abrir"; bug grave de
                # 29/09, projetos.mesmo_arquivo). Fica o caminho que acabou
                # de ser aberto - existe e funciona agora -, e nao a forma
                # antiga gravada no projeto (as previas e o PDF final abrem
                # por ele). Vale tambem para o livro que mudou de pasta e para
                # a copia em outra pasta: o caminho novo passa a ser o gravado
                # (aqui no projeto.json; no resumo, em abrir_livro).
                salvo.caminho_entrada = projeto.caminho_entrada
                # Item 1.2: as opcoes do grupo "Gravuras e fotos" vem da tela
                # (as que a pessoa acabou de escolher), e nao do salvo. Se
                # mudaram, a gravura achada sozinha das paginas ja marcadas
                # vai ser refeita (a marcacao a mao fica: ver
                # core.pipeline.garantir_selecao). ANTES, uma copia do
                # trabalho (um ajuste feito numa regiao automatica se perde) e,
                # depois, o aviso. Arriscado: refazer sem a copia, ou sem
                # avisar (pedido da gerente, 30/09).
                gravuras_refeitas = trocar_opcoes_da_gravura(salvo, projeto)
                # A caixinha "No Preto e branco, molduras e iluminuras tambem
                # em preto e branco" (emenda N2 do Samuel, 30/09) tambem vem da
                # tela: so muda a imagem do filtro, nao a marcacao, e as previas
                # sao refeitas (GerenciadorPrevias novo, logo abaixo).
                salvo.pb_decoracao_em_preto_e_branco = bool(
                    getattr(projeto, "pb_decoracao_em_preto_e_branco", False))
                # Modo Misto (05/10): as escolhas do livro tambem vem da tela
                # (so mudam a imagem do filtro; as da pagina ficam no salvo)
                for campo in CAMPOS_DO_MISTO:
                    setattr(salvo, campo, getattr(projeto, campo))
                # "Limpar pontinhos" do livro (06/10): tambem vem da tela
                salvo.limpar_pontinhos = projeto.limpar_pontinhos
                # Item 2.1: o jeito de dividir e o corte da sobra vem da tela;
                # com o jeito trocado, as folhas que seguem o livro ganham a
                # divisao da analise nova (a que a pessoa mexeu fica)
                trazer_divisao_da_analise(salvo, projeto)
                if gravuras_refeitas:
                    self.copia_do_trabalho = projetos.guardar_copia_do_trabalho(self.resumo)
                projeto = salvo
            else:
                # Rede de seguranca (29/09/2026, bug grave "livro que mudou de
                # pasta perde o trabalho de vez"): o _salvar_agora, logo
                # abaixo, regrava o projeto.json com a conferencia nova. Antes
                # disso, o trabalho antigo e guardado ao lado, com data e hora
                # no nome (projetos.guardar_copia_do_trabalho). Vale tambem
                # para o projeto.json que nao deu para ler (salvo None): ele
                # seria regravado igual. Sem projeto salvo, nao faz nada.
                # Arriscado: tirar isto, ou mover para depois do _salvar_agora.
                # So ha o que guardar se havia trabalho (paginas, ou um
                # projeto.json ilegivel): um projeto so com as opcoes (livro
                # novo; a resposta a pergunta do fundo grava assim) ganhava
                # uma copia vazia inutil a cada livro novo com camadas
                # (verificador, 30/09).
                recomecou = True
                if projetos.tem_trabalho_salvo(self.resumo):
                    self.copia_do_trabalho = projetos.guardar_copia_do_trabalho(self.resumo)
                if salvo is not None:
                    paginas_perdidas = len(salvo.paginas)
                    motivo = projetos.motivo_para_nao_combinar(
                        salvo, projeto, assinatura=self.resumo.assinatura)

        self.projeto = projeto
        self.trabalho_carregado = True        # agora pode gravar (_salvar_agora)
        self._opcoes_do_trabalho = None       # as opcoes deste trabalho valem
        # A tela "O que fazer" passa a mexer NESTE projeto (o que vai para a
        # conferencia e para o disco). Antes ela ficava com o objeto de antes
        # da analise, e o que se marcava la, na volta, se perdia. Achado ao
        # ligar o item 1.1. (As caixinhas continuam perdendo o que se muda na
        # volta quando o projeto salvo volta por cima: bug registrado em
        # 29/09, para depois.)
        self.tela_opcoes.projeto = projeto
        # Item 1.1: pagina fora do filtro "Tirar o fundo" (ou livro sem
        # camadas) nao fica com o alerta "conferir o fundo tirado" de uma
        # sessao anterior; as que estao nele sao acertadas pela tela de
        # conferir, pagina a pagina.
        acertar_alertas_do_fundo(projeto)

        # O desfazer de um projeto ja trabalhado tambem volta do disco - so
        # quando o trabalho voltou. Se a conferencia recomecou (o else acima:
        # trabalho que nao combina, projeto.json ilegivel, livro novo), o
        # desfazer recomeca vazio, e o historico antigo fica junto da copia
        # do trabalho (HistoricoAcoes.recomecar). Lista de bugs, 06/10/2026
        # (parecer do verificador, item 5): antes carregava sempre, e depois
        # de mudar "Dividir folhas ao meio" o primeiro Ctrl+Z pos a pagina 1
        # do livro recomecado em Preto e branco, uma acao da conferencia
        # anterior feita em outra pagina. Na mesma sessao, o historico da
        # memoria nem era trocado (sem acoes.jsonl, carregar() nao mexe).
        # Arriscado: voltar a carregar() no recomeco, ou chamar recomecar()
        # antes de guardar a copia do trabalho (logo acima).
        if recomecou:
            self.acoes.recomecar(self.copia_do_trabalho)
        else:
            self.acoes.carregar()

        if self.previas is not None:
            self.previas.parar()
        self.previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, self)
        # item 1.2: se o detector de gravuras falhar numa previa, a frase
        # aparece uma vez (ver _avisar_da_gravura)
        self.previas.pronta.connect(lambda *_: self._avisar_da_gravura())

        self.tela_conferir.carregar(projeto, self.acoes, self.previas)
        if self.resumo is not None:
            self.tela_conferir.ir_para_pagina(self.resumo.pagina_atual)
        # Item 1.1: "Sim, tirar o fundo" respondido antes de o trabalho
        # carregar (projeto antigo, "continuar", ou com um cancelar no meio):
        # vale agora, e so agora conta como respondido (_salvar_agora, logo
        # abaixo, grava o "ja perguntou" junto com o trabalho).
        if self.resumo is not None and self._fundo_pendente == self.resumo.pasta:
            self._tirar_o_fundo_do_livro_inteiro()
        self.telas.setCurrentIndex(CONFERIR)
        self._salvar_agora()
        # Decisao Z1 (b): as zonas de projeto antigo sao convertidas por
        # tras, o livro inteiro, enquanto o Kaique ja trabalha.
        self._comecar_a_converter_as_zonas()

        if self.acoes.linhas_perdidas:
            self.avisar(
                f"O computador foi desligado no meio da última gravação, e "
                f"{self.acoes.linhas_perdidas} ação(ões) do fim se perderam. "
                "O resto do trabalho está aqui.")
        elif paginas_perdidas:
            self.avisar(self._frase_do_recomeco(motivo, self.copia_do_trabalho))
        elif gravuras_refeitas:
            # O titulo e o texto de cada caso ("procurar de novo" ou "nao
            # procurar mais") vem de core.pipeline.aviso_das_opcoes_da_gravura
            # (parecer do verificador, 30/09, r09: o texto dizia "procuradas de
            # novo" tambem no "nao procurar", numa caixa "Um momento").
            titulo, frase = aviso_das_opcoes_da_gravura(
                self.projeto, gravuras_refeitas, self.copia_do_trabalho)
            self.avisar(frase, titulo)

    # --- zonas do livro inteiro, por tras (decisao Z1 (b), 05/10/2026) ----

    def _comecar_a_converter_as_zonas(self) -> None:
        """Pedido do Samuel (conferencia 9, Z1 (b)): "O livro inteiro, por
        tras, ao abrir - ele poderia fazer isso quando abre o livro e fica
        carregando dai né?".

        Se o trabalho que acabou de voltar tem zonas no formato antigo
        (core/zonas_na_folha.paginas_por_converter), uma TarefaConverterZonas
        converte todas, uma folha por vez. A tela de
        conferir ja esta aberta: o Kaique trabalha enquanto isso, e o
        andamento aparece na faixa azul ("Preparando as marcações do
        livro… 12 de 50"; TelaConferir.mostrar_andamento_das_marcacoes).
        Pagina que ele abrir antes e convertida pela previa, como antes. No
        fim, grava (com a copia de seguranca do projeto.json antigo antes,
        projetos.salvar_estado).

        Arriscado: rodar a conversao numa copia do projeto (o que ela anota
        nao chegaria ao disco), ou esquecer de parar a tarefa ao trocar de
        livro e ao fechar (_parar_a_conversao_das_zonas, closeEvent).
        """
        from core.zonas_na_folha import paginas_por_converter

        self._parar_a_conversao_das_zonas()
        if self.projeto is None or not paginas_por_converter(self.projeto):
            return
        tarefa = TarefaConverterZonas(self.projeto)
        tarefa.andamento.connect(self._andamento_da_conversao)
        tarefa.terminou.connect(self._conversao_terminou)
        self.conversao_das_zonas = tarefa
        self.tela_conferir.mostrar_andamento_das_marcacoes(
            0, len(paginas_por_converter(self.projeto)))
        tarefa.start()          # prioridade normal: ver ui/tarefas.TarefaConverterZonas

    def _parar_a_conversao_das_zonas(self, gravar: bool = False) -> None:
        """Para a conversao da vez (trocar de livro, nova conferencia, fechar).

        Parar no meio nao estraga nada: o que foi convertido esta na memoria
        e vai para o disco na proxima gravacao (com gravar=True, agora,
        antes de o projeto aberto mudar); o resto continua no formato antigo
        e e convertido da proxima vez que o livro abrir. A tarefa que ainda
        termina a pagina dela vai para self._tarefas_saindo (o Qt derrubaria
        o programa se a QThread fosse destruida rodando; ver _trocar_tarefa).
        """
        tarefa = self.conversao_das_zonas
        self.conversao_das_zonas = None
        if tarefa is None:
            return
        tarefa.cancelar()
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)
        self.tela_conferir.mostrar_andamento_das_marcacoes(0, 0)
        if gravar and tarefa.feitas:
            self._salvar_agora()

    def _andamento_da_conversao(self, tarefa, feitas: int, total: int) -> None:
        """Uma pagina a mais convertida: atualiza a faixa (so a da vez; um
        sinal atrasado de uma tarefa parada nao entra)."""
        if tarefa is None or tarefa is not self.conversao_das_zonas:
            return
        self.tela_conferir.mostrar_andamento_das_marcacoes(feitas, total)

    def _conversao_terminou(self, tarefa, convertidas: int) -> None:
        """A conversao chegou ao fim: tira o andamento da faixa e grava logo
        (o relogio de salvar), para o formato novo ir para o disco mesmo se
        o Kaique nao mexer em mais nada."""
        if tarefa is None or tarefa is not self.conversao_das_zonas:
            return
        self.conversao_das_zonas = None
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)   # ainda saindo do run()
        self.tela_conferir.mostrar_andamento_das_marcacoes(0, 0)
        if convertidas:
            self._marcar_para_salvar()

    @staticmethod
    def _frase_do_recomeco(motivo: str, copia) -> str:
        """O aviso de quando a conferencia recomeca por cima de um trabalho salvo.

        Pedido da gerente (29/09/2026): antes dizia "Voce mudou as opcoes desde
        a ultima vez, e o livro ficou com outro numero de paginas..." para
        qualquer motivo - inclusive o livro que so tinha mudado de pasta -, e
        nao dizia que havia copia. Agora diz o motivo de verdade
        (projetos.motivo_para_nao_combinar) e onde esta a copia do trabalho
        anterior (projetos.guardar_copia_do_trabalho), ou que ela nao pode ser
        feita. So o texto mudou: quando o aviso aparece continua igual.
        """
        frase = "Comecei a conferência deste livro de novo"
        frase += f": {motivo}." if motivo else "."
        if copia is not None:
            # A letra da unidade fica grudada no resto do caminho: o Qt so
            # achava lugar de quebrar a linha depois de "D:" (as barras nao
            # quebram), e o "D:" ficava sozinho numa linha (print p23 do
            # verificador, 29/09). O WORD JOINER (U+2060) e invisivel e
            # proibe a quebra ali; a caixa se alarga para o caminho caber e,
            # com espaco no nome, quebra no espaco. Ressalva: quem copiar o
            # texto da caixa leva o sinal junto.
            caminho = str(copia)
            if len(caminho) > 2 and caminho[1] == ":":
                caminho = caminho[:2] + "⁠" + caminho[2:]
            frase += ("\n\nO trabalho anterior não foi apagado. Guardei uma cópia "
                      f"dele, que pode ser recuperada:\n{caminho}")
        else:
            frase += "\n\nNão consegui guardar uma cópia do trabalho anterior."
        return frase

    # --- salvar sozinho ---------------------------------------------------

    def _marcar_para_salvar(self) -> None:
        """Alguma coisa mudou. Grava daqui a pouco, quando a mao parar."""
        if self.resumo is not None and self.projeto is not None:
            self._relogio_de_salvar.start()
            self._acertar_a_capa()

    def _acertar_a_capa(self) -> None:
        """A capa do cartao na tela inicial acompanha o giro da primeira folha
        (D2 do verificador, 06/10/2026). So compara um numero; quando o giro
        mudou (girar, desfazer, ou um projeto girado antes deste conserto),
        a capa e desenhada de novo POR TRAS (projetos.refazer_miniatura_por_
        tras): nada e desenhado no fio da janela. Num projeto ja girado, a
        capa e refeita uma vez por sessao, mesmo que ja estivesse certa
        (barato, e o arquivo nao diz com que giro foi feito).
        Arriscado: desenhar a capa aqui, no fio da janela."""
        if (self.resumo is None or self.projeto is None or not self.trabalho_carregado
                or not self.projeto.folhas):
            return
        giro = int(self.projeto.folhas[0].rotacao) % 360
        if giro == self._giro_da_capa:
            return
        self._giro_da_capa = giro
        projetos.refazer_miniatura_por_tras(self.resumo, giro)

    def _salvar_por_tras(self) -> None:
        """O que o relogio de salvar chama: o mesmo que _salvar_agora, mas o
        projeto.json vai para o disco num fio de fundo
        (projetos.salvar_estado_por_tras), e a janela so tira a fotografia
        do projeto (centesimos de segundo).

        Por que (R1 do verificador, 05/10/2026): o relogio dispara a cada
        pagina folheada, e a gravacao inteira no fio da janela (3 a 6 MB num
        livro de 268 paginas) a deixava 0,25 a 0,37 s parada a cada pagina -
        mais com disco lento ou computador sem memoria livre. Fechar, trocar
        de livro e processar continuam gravando na hora (_salvar_agora), e
        essa gravacao espera a fila antes: a ordem no disco nao muda.
        Arriscado: chamar isto no closeEvent (o programa sairia antes de o
        arquivo chegar ao disco).
        """
        self._salvar_agora(por_tras=True)

    def _salvar_agora(self, por_tras: bool = False) -> None:
        """Grava de verdade. Chamado ao sair da tela, ao processar e ao
        fechar o programa (e pelo relogio, com por_tras=True: ver
        _salvar_por_tras) - sempre na pasta do projeto aberto.

        Nunca grava por cima de um trabalho salvo com um projeto que ainda
        nao foi analisado (self.trabalho_carregado False: entre abrir o livro
        e o fim da analise). Bug grave de 29/09/2026 achado pelo verificador:
        abrir um livro salvo e fechar na tela "O que fazer" (ou em "Olhando o
        livro...") gravava um projeto de 0 paginas por cima, sem copia. Livro
        sem trabalho salvo continua gravando nesse intervalo (so as opcoes;
        e o que o "continuar" traz de volta). Arriscado: tirar essa trava, ou
        marcar trabalho_carregado antes de _analise_pronta.
        """
        self._relogio_de_salvar.stop()
        if self.resumo is None or self.projeto is None:
            return
        if not self.trabalho_carregado and projetos.tem_trabalho_salvo(self.resumo):
            return
        if por_tras:
            projetos.salvar_estado_por_tras(self.resumo, self._o_que_gravar())
        else:
            projetos.salvar_estado(self.resumo, self._o_que_gravar())
        projetos.atualizar(self.resumo, self.projeto,
                           pagina_atual=self.tela_conferir.indice_pagina, por_tras=por_tras)

    def _guardar_o_livro_aberto(self) -> None:
        """Grava NA HORA o livro aberto, antes de a janela trocar de livro
        (abrir_livro: Ctrl+O, menu Arquivo > Abrir, arrastar, o "continuar"
        do cartao; e o "comecar de novo", _recomecar_projeto).

        R-A do verificador-2 (06/10/2026): mudar alguma coisa e abrir outro
        livro menos de ~0,6 s depois perdia a mudanca. O relogio de salvar
        (600 ms) ainda nao tinha disparado; quando disparava, self.projeto
        ja era o livro novo, e a mudanca do livro de antes nunca ia para o
        disco. Agora, se o relogio esta contando (ha mudanca ainda nao
        gravada), grava ja: e o _salvar_agora (espera a fila do fio de
        gravar, grava e para o relogio), com as mesmas travas dele - nada e
        gravado por cima de um trabalho salvo que ainda nao foi carregado.

        Com o relogio parado nao ha o que gravar: tudo ja foi para o disco
        ou esta na fila do fio de gravar (que quem le o projeto espera). Nao
        regravar a toa importa: regravar mudaria o "mexido em" do projeto
        (o "Abrir" acha o projeto MAIS RECENTE do mesmo PDF) e custaria o
        projeto inteiro de novo (3 a 6 MB num livro grande).

        Nao grava se a pasta do projeto ja nao existe: e o projeto que a
        pessoa tirou da lista na tela inicial ("Tirar da lista" apaga a
        pasta). Grava-lo recriaria a pasta, e o cartao voltaria para a lista.
        So o relogio e parado.

        Arriscado: tirar essa conferencia da pasta; chamar isto depois de
        self.projeto ou self.resumo mudarem (gravaria o livro novo, e o de
        antes perderia a ultima mudanca); um caminho novo que mude o
        trabalho sem passar pelo relogio de salvar (trabalho_mudou) nem
        gravar na hora - aqui ele nao seria visto.
        Teste: tests/test_trocar_de_livro_grava.py.
        """
        pendente = self._relogio_de_salvar.isActive()
        if self.resumo is None or not Path(self.resumo.pasta).is_dir():
            self._relogio_de_salvar.stop()
            return
        if pendente:
            self._salvar_agora()

    def _o_que_gravar(self) -> Projeto:
        """O projeto como deve ir para o disco.

        Normalmente o proprio projeto aberto. Mas se a pessoa saiu da
        conferencia para "O que fazer" e mudou uma opcao (ex.: desmarcou
        "Dividir folhas ao meio") sem clicar "Conferir", a opcao nova NAO vai
        para o disco: grava-se o projeto com as opcoes do trabalho
        (self._opcoes_do_trabalho, guardadas em _sair_da_conferencia), e as
        paginas de sempre. Antes, fechar ou voltar para o inicio gravava a
        opcao nova com as paginas de antes, e a abertura seguinte recomecava a
        conferencia (bug achado em 30/09; decisao da gerente). A opcao nova so
        vale quando o "Conferir" termina (_analise_pronta limpa o guardado).

        Copia rasa: as paginas e folhas sao as mesmas (nada e duplicado na
        memoria); so as opcoes da copia sao trocadas. Arriscado: gravar
        self.projeto direto enquanto _opcoes_do_trabalho estiver guardado.
        """
        if self.projeto is None or self._opcoes_do_trabalho is None:
            return self.projeto
        import copy

        gravar = copy.copy(self.projeto)
        for campo, valor in self._opcoes_do_trabalho.items():
            setattr(gravar, campo, valor)
        return gravar

    # As opcoes da tela "O que fazer" que mudam quais paginas existem ou como
    # nascem (ver _parar_a_analise).
    OPCOES_DO_LIVRO = ("dividir_folhas", "limpar", "filtro_padrao", "endireitar",
                       "cortar_bordas", "montar_cadernos", "paginas_por_caderno",
                       *CAMPOS_DA_GRAVURA,      # item 1.2: "Gravuras e fotos"
                       # emenda N2 do Samuel (30/09): moldura e iluminura no P&B
                       "pb_decoracao_em_preto_e_branco",
                       # modo Misto (05/10): "So as letras" e as escolhas dela
                       *CAMPOS_DO_MISTO,
                       # "Limpar pontinhos" do livro (06/10)
                       "limpar_pontinhos",
                       # item 2.1: o jeito de dividir e o corte da sobra
                       "dividir_como", "cortar_sobra",
                       # item 2.2: a conta do endireitar
                       "endireitar_como")

    def _sair_da_conferencia(self) -> None:
        """Voltar para as opcoes grava antes: sair nao pode custar trabalho.

        E guarda as opcoes do trabalho como estao agora: se a pessoa mudar uma
        opcao la, clicar "Conferir" e cancelar, a conferencia volta com as
        paginas de antes e tem de voltar com as opcoes de antes tambem
        (_parar_a_analise; verificador, 30/09, s34-s36).
        """
        self._salvar_agora()
        if self.trabalho_carregado and self.projeto is not None:
            self._opcoes_do_trabalho = {campo: getattr(self.projeto, campo)
                                        for campo in self.OPCOES_DO_LIVRO}
        self.telas.setCurrentIndex(OPCOES)

    def _falhou_na_analise(self, mensagem: str) -> None:
        """Analise deu erro: volta para Opções e mostra o aviso amigavel (regra 3.3).

        O marcador trabalho_carregado volta ao valor de antes da analise
        (_parar_a_analise): o projeto da tela nao foi tocado (a analise
        trabalha numa copia), e o que se fizer depois tem de ser gravado.
        """
        origem = self.sender()
        if isinstance(origem, TarefaAnalise) and origem is not self.tarefa:
            return                        # erro de uma analise que nao e mais a da vez
        self._parar_a_analise()
        self.telas.setCurrentIndex(OPCOES)
        self.avisar(mensagem)

    def _trocar_tarefa(self, nova) -> None:
        """Poe `nova` em self.tarefa sem soltar uma tarefa que ainda roda.

        Bug antigo achado pelo verificador (30/09, s33): "Conferir" logo
        depois do "cancelar" (menos de 0,1 s) trocava self.tarefa enquanto a
        analise cancelada ainda terminava a pagina dela; sem nenhuma
        referencia no Python, o QThread era destruido rodando e o Qt
        derrubava o programa inteiro, sem mensagem e sem nada no erros.log
        (queda nativa, nenhuma excecao para o sys.excepthook pegar). A antiga
        vai para self._tarefas_saindo ate acabar; as que ja acabaram saem de
        la a cada troca. O resultado dela nao entra (_analise_pronta ignora
        o que nao vem da tarefa da vez). Arriscado: atribuir self.tarefa
        direto, em qualquer lugar.
        """
        self._tarefas_saindo = [t for t in self._tarefas_saindo if t.isRunning()]
        antiga = self.tarefa
        if antiga is not None and antiga.isRunning():
            self._tarefas_saindo.append(antiga)
        self.tarefa = nova

    def _parar_a_analise(self) -> None:
        """A analise da vez acabou sem resultado (cancelada ou com erro): o
        marcador trabalho_carregado volta ao que era quando ela comecou.

        Seguro porque a analise trabalha numa copia (analisar): o projeto da
        tela e o mesmo de antes. Se antes ele era o trabalho carregado (veio
        da conferencia), continua sendo, e volta a ser gravado; se nao era
        (livro recem-aberto com trabalho salvo), continua sem gravar por
        cima. Bug grave de 29/09 (verificador, q21-q23).
        """
        if isinstance(self.tarefa, TarefaAnalise):
            self.trabalho_carregado = self._carregado_antes_da_analise
        # As opcoes tambem voltam ao que eram quando se saiu da conferencia:
        # a pessoa mudou uma opcao em "O que fazer" (ex.: desmarcou "Dividir
        # folhas ao meio"), clicou "Conferir" e cancelou. A conferencia volta
        # com as paginas de antes; se a opcao nova ficasse, seria gravada com
        # elas, e na abertura seguinte a conferencia recomecava sem a pessoa
        # querer (verificador, 30/09, s34-s36). Com o trabalho nao carregado
        # (livro recem-aberto), nao ha paginas de antes: a opcao nova fica.
        if (self.trabalho_carregado and self.projeto is not None
                and self._opcoes_do_trabalho is not None):
            for campo, valor in self._opcoes_do_trabalho.items():
                setattr(self.projeto, campo, valor)
            if self.tela_opcoes.projeto is self.projeto:
                self.tela_opcoes.mostrar_opcoes()

    # --- processamento ----------------------------------------------------

    def processar(self) -> None:
        """Ponto de entrada de "Confirmar e processar": pede o destino (com a
        janela de confirmacao) e dispara TarefaProcessar em QThread."""
        if self.projeto is None:
            return

        caminho = self._resolver_destino()
        if caminho is None:
            return  # o usuario desistiu ou a pasta nao serve

        self.projeto.caminho_saida = str(caminho)
        configuracoes.lembrar_pasta_de_saida(caminho.parent)
        # O cartao da tela inicial deixa de dizer "pronto, PDF gerado" enquanto
        # o PDF esta sendo gravado: o destino pode ser outro nome, ou o mesmo
        # arquivo sendo substituido. So _processamento_pronto (PDF gravado com
        # sucesso) o poe de volta em verdadeiro; cancelado ou com erro, fica
        # falso. Gravado no disco pelo _salvar_agora logo abaixo
        # (projetos.atualizar -> gravar_resumo). Ver _anotar_pdf_gerado.
        if self.resumo is not None:
            self.resumo.pdf_gerado = False
        # Grava na pasta DO PROJETO aberto (resumo.pasta). Ate 29/09/2026
        # chamava historico.salvar_projeto, que escolhia a pasta pelo NOME do
        # livro e gravava por cima de outro projeto de mesmo nome (bug grave
        # achado pelo verificador). Arriscado: gravar por qualquer outro
        # caminho que nao seja _salvar_agora.
        self._salvar_agora()

        self.tela_progresso.comecar("Processando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        self._trocar_tarefa(TarefaProcessar(self.projeto))
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._processamento_pronto)
        self.tarefa.falhou.connect(self._falhou_no_processamento)
        self.tarefa.cancelada.connect(lambda: self.telas.setCurrentIndex(CONFERIR))
        self.tarefa.start()

    def _resolver_destino(self) -> Path | None:
        """A janela de confirmacao: pasta, nome e os dois avisos.

        Ela substitui a faixa "Salvar em / Nome do arquivo" que ficava sempre na
        tela de trabalho. O destino importa num momento so - o de gravar - e
        ocupava uma faixa de altura o tempo todo.

        A propria janela ja nao deixa seguir com pasta que nao aceita gravacao,
        e avisa quando o arquivo existe e quando ha pagina nao conferida. Aqui
        so sobra a pergunta de substituir, que e destrutiva e merece um passo a
        parte.
        """
        from modelos import nome_de_saida_sugerido
        from ui.janela_confirmar import pedir_confirmacao

        assert self.projeto is not None
        caminho = pedir_confirmacao(
            self.projeto, nome_de_saida_sugerido(self.projeto), self)
        if caminho is None:
            return None

        if caminho.exists():
            return self._perguntar_sobre_substituir(caminho)
        return caminho

    def _perguntar_sobre_substituir(self, caminho: Path) -> Path | None:
        """Já existe arquivo com esse nome: substituir, renomear ou desistir.

        Devolve o caminho em que o PDF vai ser gravado (o mesmo, para
        substituir; o `nome (2).pdf` livre, para renomear) ou None (cancelar).
        Quem grava esse caminho em `projeto.caminho_saida` - de onde o
        processamento (core/pipeline.py) e a proxima "Antes de processar"
        leem - e o `processar`. Aqui nao se guarda o caminho em lugar nenhum.

        Arriscado: voltar a mexer num seletor de destino daqui. Ate 02/10/2026
        o "salvar como (2)" chamava `self.tela_conferir.destino.definir(...)`,
        mas o seletor saiu da tela Conferir e foi para ui/janela_confirmar.py
        (que ja esta fechada neste ponto); dava AttributeError, "Aconteceu um
        problema inesperado" e o PDF nao era gerado. Teste:
        tests/test_ja_existe_arquivo_com_esse_nome.py.
        """
        alternativo = configuracoes.caminho_sem_repetir(caminho.parent, caminho.name)

        caixa = QMessageBox(self)
        caixa.setWindowTitle("Já existe um arquivo com esse nome")
        caixa.setIcon(QMessageBox.Question)
        caixa.setText(f"Já existe um arquivo chamado:\n{caminho.name}")
        caixa.setInformativeText(
            f"Posso substituir o antigo ou salvar como:\n{alternativo.name}"
        )
        botao_substituir = caixa.addButton("substituir o antigo", QMessageBox.DestructiveRole)
        botao_renomear = caixa.addButton(
            f"salvar como {alternativo.name}", QMessageBox.AcceptRole
        )
        caixa.addButton("cancelar", QMessageBox.RejectRole)
        caixa.setDefaultButton(botao_renomear)
        caixa.exec()

        escolhido = caixa.clickedButton()
        if escolhido is botao_substituir:
            return caminho
        if escolhido is botao_renomear:
            # So devolve: o processar grava em projeto.caminho_saida (ver o
            # docstring - o seletor de destino nao mora mais na tela Conferir).
            return alternativo
        return None

    def _avisar_da_gravura(self) -> None:
        """Item 1.2 (bug de 30/09): o detector de gravuras do ScanTailor faltou
        ou falhou nesta sessao? Mostra a frase em portugues, UMA vez (o
        detalhe tecnico ja foi para o erros.log, em
        core.detectar_regioes._avisar_uma_vez). Chamado quando chega uma
        previa e quando o processar termina. Nunca levanta excecao."""
        try:
            from core.detectar_regioes import aviso_da_gravura_para_a_tela

            frase = aviso_da_gravura_para_a_tela()
        except Exception:  # noqa: BLE001
            return
        if frase:
            self.avisar(frase, "Gravuras e fotos")

    def _processamento_pronto(self, caminho: str) -> None:
        """PDF gravado: registra no histórico e mostra a tela Pronto com o
        número certo de páginas DO LIVRO (ver comentário abaixo sobre cadernos).

        PDF antigo aberto em outro programa (conserto de 05/10/2026, achado do
        verificador): o PDF novo foi gravado como "nome (2).pdf" e chega aqui
        como sucesso, com `caminho` = o "(2)" e o nome do antigo em
        TarefaProcessar.antigo_preso. O destino guardado passa a ser o "(2)"
        (projeto.caminho_saida, e o resumo do cartao por _anotar_pdf_gerado),
        e a tela "Ficou pronto!" ganha uma frase explicando. Nenhuma caixa de
        aviso e nada no erros.log. Arriscado: guardar o destino depois do
        historico.registrar/_salvar_agora (gravariam o nome antigo).
        """
        assert self.projeto is not None
        self._avisar_da_gravura()      # item 1.2
        antigo_preso = getattr(self.tarefa, "antigo_preso", "") or ""
        if not isinstance(antigo_preso, str):
            antigo_preso = ""
        if antigo_preso:
            self.projeto.caminho_saida = str(caminho)
        try:
            import fitz

            with fitz.open(caminho) as doc:
                folhas_de_saida = doc.page_count
        except Exception:  # noqa: BLE001
            folhas_de_saida = 0

        # Paginas DO LIVRO: com cadernos, o arquivo tem metade das paginas,
        # porque cada folha leva duas. Quem conta caderno e a pagina do livro.
        if self.projeto.montar_cadernos:
            paginas = len(self.projeto.paginas_ativas) if self.projeto.paginas else folhas_de_saida * 2
        else:
            paginas = folhas_de_saida or len(self.projeto.paginas_ativas)

        historico.registrar(self.projeto, paginas)
        self._anotar_pdf_gerado(caminho)
        self._salvar_agora()          # na pasta do projeto, nao pelo nome (ver processar)
        self.tela_inicio.recarregar()

        self.tela_final.mostrar(self.projeto, caminho, paginas, folhas_de_saida,
                                antigo_preso=antigo_preso)
        self.telas.setCurrentIndex(FINAL)

    def _anotar_pdf_gerado(self, caminho: str) -> None:
        """O PDF foi gravado com sucesso: o cartao do livro na tela inicial
        passa a mostrar "pronto, PDF gerado" e o botao "abrir a pasta".

        Bug da Lista de bugs (02/10/2026, achado na janela real): o campo
        `pdf_gerado` do resumo (projetos.Resumo, lido em ui/tela_inicio.py)
        nunca virava verdadeiro - so o "comecar de novo" o punha em falso -, e
        o cartao nunca dizia que o livro estava pronto.

        So e chamado por _processamento_pronto (o sinal `concluida` da
        TarefaProcessar, emitido depois de o PDF ser gravado). Cancelado ou
        com erro nao passa aqui, e o processar ja o pos em falso ao comecar.
        Quem grava no disco e o _salvar_agora, logo depois
        (projetos.atualizar -> gravar_resumo). Arriscado: marcar em outro
        lugar (ex.: ao comecar o processamento), o que faria o cartao
        prometer um PDF que pode nao existir. Teste:
        tests/test_cartao_pdf_gerado.py.
        """
        if self.resumo is None:
            return
        self.resumo.pdf_gerado = True
        self.resumo.caminho_saida = str(caminho)

    def _falhou_no_processamento(self, mensagem: str) -> None:
        """Processamento deu erro: volta para Conferir (o projeto continua
        intacto) e mostra o aviso amigavel."""
        self.telas.setCurrentIndex(CONFERIR)
        self.avisar(mensagem)

    def cancelar(self) -> None:
        """Botão "cancelar" da tela de progresso: pede pra thread parar e volta
        para Conferir (se ja havia analise) ou Opções.

        Cancelar a analise devolve o marcador trabalho_carregado ao valor de
        antes (_parar_a_analise); sem isso, voltar a conferencia depois de
        "cancelar" deixava de gravar tudo ate fechar (bug grave, 29/09).
        """
        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
        self._parar_a_analise()
        destino = CONFERIR if self.projeto and self.projeto.paginas else OPCOES
        self.telas.setCurrentIndex(destino)

    def _recomecar(self) -> None:
        """Botão "fazer outro" da tela final: volta para o inicio."""
        self.tela_inicio.recarregar()
        self.telas.setCurrentIndex(INICIO)

    def _voltar_das_opcoes(self) -> None:
        """Botao "voltar" da tela de opcoes: volta para o inicio com os
        cartoes remontados.

        Ressalva 1 do verificador-3 (06/10/2026): antes o voltar so trocava
        de tela, e o cartao continuava com a capa (e o andamento) de quando a
        tela inicial foi montada - um livro girado mostrava a capa sem o giro
        ate o programa ser aberto de novo, embora a capa.png ja estivesse
        certa no disco. A capa nova e gravada por tras
        (projetos.refazer_miniatura_por_tras): espera-se ela chegar ao disco
        (no maximo 2 s; costuma ser centesimos) antes de ler os resumos, como
        o "fazer outro" (_recomecar) ja faz. Arriscado: tirar a espera (o
        cartao poderia ler a capa velha de novo)."""
        projetos.esperar_gravacoes(2.0)
        self.tela_inicio.recarregar()
        self.telas.setCurrentIndex(INICIO)

    # ------------------------------------------------------------------
    # teclado e fechamento
    # ------------------------------------------------------------------

    def keyPressEvent(self, evento) -> None:  # noqa: N802
        """Repassa a tecla para a tela de Conferir tratar primeiro (setas,
        atalhos de filtro etc); só cai no comportamento padrão do Qt se ela nao usar."""
        if self.telas.currentIndex() == CONFERIR:
            if self.tela_conferir.tratar_tecla(evento):
                evento.accept()
                return
        super().keyPressEvent(evento)

    def closeEvent(self, evento) -> None:  # noqa: N802
        """Sair no meio de um trabalho não pode deixar thread solta nem perder
        o que foi feito.

        Grava ANTES de encerrar as threads: a prévia que ainda vier não muda o
        trabalho, e esperar por ela só atrasaria o fechamento.

        E não pergunta nada. A pergunta "quer salvar?" é o que este programa
        não faz - um "não" por engano apagaria um dia de trabalho do Kaique.
        """
        # Decisao Z1 (b): a conversao das zonas para ANTES de gravar (so a
        # bandeira; a pagina em curso termina logo abaixo): o que ja foi
        # convertido vai para o disco agora, e o resto continua da proxima
        # vez que o livro abrir. Nada fica pela metade: a gravacao e inteira
        # (projetos.salvar_estado) e a pagina convertida e trocada sob a
        # trava das zonas.
        conversao = self.conversao_das_zonas
        self._parar_a_conversao_das_zonas()
        self._salvar_agora()
        if conversao is not None:
            conversao.wait(3000)

        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(3000)
        # As que ja estavam saindo (canceladas) tambem: fechar com uma thread
        # rodando derruba o processo na saida.
        for tarefa in self._tarefas_saindo:
            tarefa.wait(3000)
        if self.previas is not None:
            self.previas.parar()
        self.tela_conferir.tira.parar()
        # (Aqui havia um segundo salvamento, historico.salvar_projeto, que
        # gravava na pasta escolhida pelo NOME do livro: com dois PDFs
        # diferentes de mesmo nome, fechar com o segundo aberto apagava o
        # trabalho do primeiro. Bug grave de 29/09/2026. O _salvar_agora, la
        # em cima, ja grava tudo na pasta do projeto aberto.)
        evento.accept()
