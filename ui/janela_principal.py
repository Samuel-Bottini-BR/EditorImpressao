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
from PySide6.QtWidgets import QMainWindow, QMessageBox, QStackedWidget

import configuracoes
import historico
import projetos
from core.camadas import pdf_tem_camadas
from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
from core.pipeline import acertar_alertas_do_fundo
from historico_acoes import HistoricoAcoes
from modelos import Projeto
from registro import registrar_erro
from ui.estilo import FOLHA_DE_ESTILO
from ui.tarefas import GerenciadorPrevias, TarefaAnalise, TarefaProcessar
from ui.tela_conferir import TelaConferir
from ui.tela_final import TelaFinal, TelaProgresso
from ui.tela_inicio import TelaInicio
from ui.tela_opcoes import TelaOpcoes

INICIO, OPCOES, PROGRESSO, CONFERIR, FINAL = range(5)


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
        self.setMinimumSize(1000, 680)
        self.resize(1220, 800)
        self.setStyleSheet(FOLHA_DE_ESTILO)

        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None
        self.tarefa = None
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

        # Salvar sozinho, com um respiro. Gravar a cada mudanca travaria a tela
        # ao arrastar o medidor - sao dezenas de mudancas por segundo, e o
        # projeto de um livro de mil paginas nao e um arquivo pequeno. O relogio
        # junta a rajada e grava uma vez depois que a mao para.
        #
        # NAO existe botao de salvar e nunca se pergunta "quer salvar?". Essa
        # pergunta e uma armadilha para quem nao e tecnico: um "nao" por engano
        # apaga um dia de trabalho.
        self._relogio_de_salvar = QTimer(self)
        self._relogio_de_salvar.setSingleShot(True)
        self._relogio_de_salvar.setInterval(600)
        self._relogio_de_salvar.timeout.connect(self._salvar_agora)

        self.telas = QStackedWidget()
        self.setCentralWidget(self.telas)
        self.telas.currentChanged.connect(self._tela_mudou)

        self.tela_inicio = TelaInicio()
        self.tela_inicio.abrir_pdf.connect(self.abrir_livro)
        self.tela_inicio.continuar_projeto.connect(self._continuar_projeto)
        self.tela_inicio.recomecar_projeto.connect(self._recomecar_projeto)
        self.telas.addWidget(self.tela_inicio)

        self.tela_opcoes = TelaOpcoes()
        self.tela_opcoes.voltar.connect(lambda: self.telas.setCurrentIndex(INICIO))
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
        self.menu.ligar("girar", conferir._girar)
        self.menu.ligar("apagar", conferir.apagar_pagina)

        self.menu.ligar("atalhos", self._mostrar_atalhos)
        self.menu.ligar("configuracoes", self._abrir_configuracoes)

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
        from PySide6.QtWidgets import QInputDialog, QLineEdit

        from modelos import nome_de_saida_sugerido

        if self.projeto is None:
            return
        atual = Path(self.projeto.caminho_saida).name if self.projeto.caminho_saida \
            else nome_de_saida_sugerido(self.projeto)
        novo, certo = QInputDialog.getText(
            self, "Nome do arquivo", "Como o PDF pronto vai se chamar:",
            QLineEdit.Normal, atual)
        if certo and novo.strip():
            pasta = (Path(self.projeto.caminho_saida).parent
                     if self.projeto.caminho_saida
                     else configuracoes.pasta_de_saida_sugerida())
            self.projeto.caminho_saida = str(Path(pasta) / novo.strip())

    def _perguntar_a_pagina(self) -> None:
        """Item de menu "Ir para a página...": pede o número e pula direto."""
        from PySide6.QtWidgets import QInputDialog

        if self.projeto is None or not self.projeto.paginas:
            return
        total = len(self.projeto.paginas)
        numero, certo = QInputDialog.getInt(
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
        """
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
        self.projeto.limpar = salvo.limpar
        self.projeto.filtro_padrao = salvo.filtro_padrao
        self.projeto.endireitar = salvo.endireitar
        self.projeto.cortar_bordas = salvo.cortar_bordas
        self.projeto.montar_cadernos = salvo.montar_cadernos
        self.projeto.paginas_por_caderno = salvo.paginas_por_caderno
        self.projeto.perguntou_fundo = salvo.perguntou_fundo      # item 1.1
        self.tela_opcoes.carregar(self.projeto, self.total_folhas)

    def _recomecar_projeto(self, resumo: projetos.Resumo) -> None:
        """Joga fora os ajustes e abre o livro limpo. O PDF nao e tocado."""
        import shutil
        from historico_acoes import ARQUIVO_ACOES, ARQUIVO_POSICAO

        pasta = Path(resumo.pasta)
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

        self.tarefa = TarefaAnalise(copy.copy(self.projeto))
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

        # O desfazer de um projeto ja trabalhado tambem volta do disco.
        self.acoes.carregar()

        if self.previas is not None:
            self.previas.parar()
        self.previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, self)

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

        if self.acoes.linhas_perdidas:
            self.avisar(
                f"O computador foi desligado no meio da última gravação, e "
                f"{self.acoes.linhas_perdidas} ação(ões) do fim se perderam. "
                "O resto do trabalho está aqui.")
        elif paginas_perdidas:
            self.avisar(self._frase_do_recomeco(motivo, self.copia_do_trabalho))

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

    def _salvar_agora(self) -> None:
        """Grava de verdade. Chamado pelo relogio, ao sair da tela, ao
        processar e ao fechar o programa - sempre na pasta do projeto aberto.

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
        projetos.salvar_estado(self.resumo, self.projeto)
        projetos.atualizar(self.resumo, self.projeto,
                           pagina_atual=self.tela_conferir.indice_pagina)

    # As opcoes da tela "O que fazer" que mudam quais paginas existem ou como
    # nascem (ver _parar_a_analise).
    OPCOES_DO_LIVRO = ("dividir_folhas", "limpar", "filtro_padrao", "endireitar",
                       "cortar_bordas", "montar_cadernos", "paginas_por_caderno")

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
        # Grava na pasta DO PROJETO aberto (resumo.pasta). Ate 29/09/2026
        # chamava historico.salvar_projeto, que escolhia a pasta pelo NOME do
        # livro e gravava por cima de outro projeto de mesmo nome (bug grave
        # achado pelo verificador). Arriscado: gravar por qualquer outro
        # caminho que nao seja _salvar_agora.
        self._salvar_agora()

        self.tela_progresso.comecar("Processando o livro...")
        self.telas.setCurrentIndex(PROGRESSO)

        self.tarefa = TarefaProcessar(self.projeto)
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
        """Já existe arquivo com esse nome: substituir, renomear ou desistir."""
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
            self.tela_conferir.destino.definir(alternativo.parent, alternativo.name)
            return alternativo
        return None

    def _processamento_pronto(self, caminho: str) -> None:
        """PDF gravado: registra no histórico e mostra a tela Pronto com o
        número certo de páginas DO LIVRO (ver comentário abaixo sobre cadernos)."""
        assert self.projeto is not None
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
        self._salvar_agora()          # na pasta do projeto, nao pelo nome (ver processar)
        self.tela_inicio.recarregar()

        self.tela_final.mostrar(self.projeto, caminho, paginas, folhas_de_saida)
        self.telas.setCurrentIndex(FINAL)

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
        self._salvar_agora()

        if self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
            self.tarefa.wait(3000)
        if self.previas is not None:
            self.previas.parar()
        self.tela_conferir.tira.parar()
        # (Aqui havia um segundo salvamento, historico.salvar_projeto, que
        # gravava na pasta escolhida pelo NOME do livro: com dois PDFs
        # diferentes de mesmo nome, fechar com o segundo aberto apagava o
        # trabalho do primeiro. Bug grave de 29/09/2026. O _salvar_agora, la
        # em cima, ja grava tudo na pasta do projeto aberto.)
        evento.accept()
