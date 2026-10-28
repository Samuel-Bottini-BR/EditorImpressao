"""A janela e o fluxo entre as telas.

Inicio -> Conferir (a area de trabalho) -> (processamento) -> Pronto

OBRA DE 26/10/2026, ETAPA 3 (decisoes do Samuel; ONDE-PAREI em relatorios/obra-etapa3/):
  D-002 (25/09) + Kaique (22/09): "Essa pagina não era mais para aparecer – nós tínhamos que
  abrir direto na área de trabalho". O livro abre DIRETO na area de trabalho: a tela "Marque o
  que você quer fazer" (ui/tela_opcoes.py) saiu do caminho. Livro novo: a passada leve (uma
  folha por pagina do PDF, nada medido, a pagina como veio: "sempre abre em Original, sem
  mexer", 29/09) e a medida do livro por tras, que so guarda os avisos (D-284). Livro com
  trabalho salvo: o trabalho volta COMO ESTA, sem analise nova por cima (era o defeito de 29/09:
  o salvo voltava por cima da analise e as opcoes mudadas se perdiam; teste do Kaique de 26/10,
  tarefas 7 e 8).
  O automatico roda quando a pessoa pede, pelo painel Automatico ou pela janela grande
  (ui/automatico.py): rodar_o_automatico mede por tras (ui/tarefas.TarefaAutomatico) e grava no
  projeto aberto, numa acao do Historico (core/automatico.aplicar), depois de perguntar se pula
  as paginas mexidas a mao (D-004). Livro novo mostra o aviso "Livro novo: ainda não passou pelo
  automático" (D-005), cujo "Rodar o automático…" abre a janela com a receita de sempre (D-018).

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
from core.filtros import TIRAR_FUNDO
from core.pdf_io import ErroPDF, abrir_pdf, info_paginas
from core.pipeline import acertar_alertas_do_fundo, aviso_das_opcoes_da_gravura
from historico_acoes import HistoricoAcoes
from modelos import Projeto
from registro import registrar_erro
from ui import estilo
from ui.tarefas import (GerenciadorPrevias, TarefaAutomatico, TarefaConverterZonas,
                        TarefaMedirAoAbrir, TarefaMedirOLivro, TarefaProcessar)
from ui.tela_conferir import TelaConferir
from ui.tela_final import TelaFinal, TelaProgresso
from ui.tela_inicio import TelaInicio

INICIO, PROGRESSO, CONFERIR, FINAL = range(4)
# A tela "O que fazer" saiu do caminho na etapa 3 da obra (D-002): o indice
# nao existe mais. O nome fica para quem ainda o importa (nenhuma tela tem
# este indice). Arriscado: voltar a por a tela no meio do abrir.
OPCOES = -1

# Quantos livros o menu Arquivo > "Livros recentes" mostra (os mais mexidos
# por ultimo). Seguro mudar.
MAXIMO_DE_RECENTES = 10


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
        # Etapa 1 do layout (temas): o tema que a pessoa escolheu da última
        # vez (cinza de fábrica) vale desde o começo; a folha acompanha a
        # troca pelo menu Ver > Tema (_trocar_tema).
        estilo.carregar_o_tema_guardado()
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO)

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
        # O projeto em memoria e o trabalho de verdade (abriu na area de
        # trabalho, _abrir_o_trabalho)? False so no instante entre comecar a
        # abrir um livro e ele abrir: gravar nesse intervalo por cima de um
        # trabalho salvo o apagaria (bug grave de 29/09/2026; ver _salvar_agora).
        self.trabalho_carregado = False
        # Item 1.1: o "Sim, tirar o fundo" de um projeto antigo gravado so com
        # as opcoes (antes da etapa 3 da obra): a pasta do projeto que espera o
        # livro inteiro ir para o filtro em _abrir_o_trabalho.
        self._fundo_pendente: str | None = None
        # Etapa 3 da obra: a medida do livro por tras ao abrir (D-284), a
        # janela grande do Automatico aberta e o pedido da vez.
        self.medida_ao_abrir: TarefaMedirAoAbrir | None = None
        self.janela_do_automatico = None
        self._pedido_da_vez = None
        # Decisao Z1 (b) do Samuel (05/10/2026): a tarefa que converte por
        # tras as zonas do livro aberto para o formato novo (zonas na folha
        # original). None quando nao ha. Ver _comecar_a_converter_as_zonas.
        self.conversao_das_zonas: TarefaConverterZonas | None = None
        # Item 2.5: a passada que mede o tamanho do livro por tras (so com o
        # corte pelo conteudo ligado). Comeca e para junto com a conversao
        # das zonas (_comecar_a_converter_as_zonas / _parar_a_conversao_das_zonas).
        self.medida_do_livro: TarefaMedirOLivro | None = None
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
        # etapa 7 do layout: os botões do livro aberto e do alto da tela dos livros.
        # Etapa 3 da obra: "Rodar o automático..." abre o livro e o Automático de verdade.
        self.tela_inicio.abrir_o_automatico.connect(self._abrir_e_mostrar_o_automatico)
        self.tela_inicio.processar_pedido.connect(self._continuar_e_processar)
        self.tela_inicio.configuracoes_pedidas.connect(lambda: self._abrir_configuracoes())
        self.tela_inicio.ajuda_pedida.connect(lambda: self._mostrar_atalhos())
        self._processar_ao_abrir = False
        self.telas.addWidget(self.tela_inicio)

        self.tela_progresso = TelaProgresso()
        self.tela_progresso.cancelar.connect(self.cancelar)
        self.telas.addWidget(self.tela_progresso)

        self.tela_conferir = TelaConferir()
        self.tela_conferir.voltar.connect(lambda: self._sair_da_conferencia())
        self.tela_conferir.processar.connect(self.processar)
        self.tela_conferir.trabalho_mudou.connect(self._marcar_para_salvar)
        # etapa 9b-1 (D-309, Lista de bugs 332): o cartao deixa de dizer
        # "pronto, PDF gerado" quando o trabalho muda depois do PDF
        self._trabalho_do_pdf = None
        self._marcacao_ligada_ao_cartao = None
        self.tela_conferir.trabalho_mudou.connect(self._ver_se_o_pdf_ficou_velho)
        self.telas.addWidget(self.tela_conferir)
        self._ligar_o_automatico()

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
        self._montar_a_linha_dos_menus()
        conferir = self.tela_conferir

        self.menu.ligar("abrir", self.tela_inicio.area.abrir_dialogo_de_arquivo)
        self.menu.ligar("pasta_de_saida", self._escolher_pasta_de_saida)
        self.menu.ligar("nome_do_arquivo", self._escolher_nome_do_arquivo)
        # etapa 9b-1 (D-274, P-127): o menu Arquivo > "Confirmar e processar"
        # (e a tecla Ctrl+Return) passa pela "Antes de processar", como o
        # botao da area de trabalho. Antes chamava self.processar direto e os
        # avisos pendentes ficavam sem ser mostrados. Arriscado: voltar a
        # ligar o menu em self.processar.
        self.menu.ligar("processar", self._no_trabalho(
            lambda: self.tela_conferir._pedir_processamento()))
        self.menu.ligar("voltar", lambda: self._sair_da_conferencia())
        # etapa 3 da obra: o Automático no menu Arquivo (a janela grande)
        self.menu.ligar("automatico", self._no_trabalho(lambda: self.abrir_o_automatico()))
        self.menu.ligar("sair", self.close)

        # Etapa 2 da obra (26/10/2026): o que mexe no trabalho passa por
        # _no_trabalho, que so deixa agir no trabalho DESTE livro, aberto na
        # area de trabalho (os menus agora ficam acesos tambem na tela "O que
        # fazer", lista unica 1.12; e as teclas ja valiam em qualquer tela).
        trabalho = self._no_trabalho
        self.menu.ligar("desfazer", trabalho(conferir.desfazer))
        self.menu.ligar("refazer", trabalho(conferir.refazer))
        # etapa 9b-1 (P-125, D-020 "Desfazer ligado sem nada"): o Desfazer e
        # o Refazer do menu Editar ficam apagados sem nada para desfazer ou
        # refazer, como os da barra de baixo
        conferir.trabalho_mudou.connect(self._acertar_o_desfazer_do_menu)

        self.menu.ligar("procurar_de_novo", trabalho(conferir._detectar_de_novo))
        self.menu.ligar("limpar_marcacao", trabalho(conferir._limpar_marcacao))
        self.menu.ligar("folha_em_branco", trabalho(conferir._folha_em_branco))

        for chave in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            self.menu.ligar(f"filtro_{chave}",
                            trabalho(lambda f=chave: conferir._escolher_filtro(f)))
            # etapa 9b-1 (D-492, P-085): o clique no item marcado o desmarcava
            # (o Qt alterna); a marca volta a dizer o filtro da pagina
            self.menu.acoes[f"filtro_{chave}"].triggered.connect(
                lambda _marcado=False: self._marcar_o_filtro_no_menu())
        # D-492 (27/10/2026; P-085): o tique do menu Filtro acompanha o filtro
        # da pagina aberta - ao trocar de pagina, ao trocar o filtro (por
        # qualquer lugar: cartao, tecla, menu, desfazer) e ao abrir o menu
        conferir.trabalho_mudou.connect(self._marcar_o_filtro_no_menu)
        self.menu.menus["Filtro"].aboutToShow.connect(self._marcar_o_filtro_no_menu)

        # Etapa 2 da obra: o menu Ferramentas (as da trilha, pelo mesmo ponto
        # unico de troca da tela) e a marca acompanha a trilha
        for ferramenta in self.menu.ferramentas_do_menu:
            self.menu.ligar(f"usar_{ferramenta}",
                            trabalho(lambda f=ferramenta: conferir.escolher_ferramenta(f)))
        conferir.trilha.ferramenta_mudou.connect(self.menu.marcar_ferramenta)

        self.menu.ligar("ir_para_pagina", trabalho(self._perguntar_a_pagina))
        # Item 2.3 (girar): os tres giros e o "Aplicar o giro em", que e o
        # mesmo da barrinha em cima da pagina - os dois ficam sempre iguais.
        self.menu.ligar("girar", trabalho(conferir._girar))
        self.menu.ligar("girar_esquerda", trabalho(conferir._girar_esquerda))
        self.menu.ligar("girar_meia_volta", trabalho(conferir._girar_meia_volta))
        from core.girar import ALCANCES

        for alcance in ALCANCES:
            self.menu.ligar(f"giro_em_{alcance}",
                            lambda _marcado=False, a=alcance: conferir.barra_girar.definir_alcance(a))
        conferir.barra_girar.alcance_mudou.connect(self._alcance_do_giro_mudou)
        conferir.marcacoes_por_converter.connect(self._converter_as_zonas_se_parado)
        self.menu.atalhos_mudaram.connect(self._mostrar_teclas_do_giro)
        # Etapa 2 da obra (Samuel, 07/10/2026): Delete = "Deixar em branco";
        # "Tirar do livro" e o que antes se chamava "Apagar esta página"
        self.menu.ligar("deixar_em_branco", trabalho(conferir.deixar_em_branco_ou_voltar))
        self.menu.ligar("tirar_do_livro", trabalho(conferir.apagar_pagina))
        # Etapa 4 do layout (20/10/2026): os itens que estavam no menu e nao
        # faziam nada (inventario de 02/10, "11 itens de menu mortos"). Os
        # quatro "Painel: ..." do menu Ver viraram o menu Painéis (rodada 14).
        self.menu.ligar("restaurar", trabalho(conferir.restaurar_pagina))
        self.menu.ligar("historico", conferir._mostrar_o_historico)
        self.menu.ligar("mais_zoom", lambda: conferir.mudar_o_zoom(conferir.PASSO_DO_ZOOM))
        self.menu.ligar("menos_zoom", lambda: conferir.mudar_o_zoom(1 / conferir.PASSO_DO_ZOOM))
        self.menu.ligar("ajustar", lambda: conferir.mudar_o_zoom(None))
        self.menu.ligar("comparar", self._modo_comparar)
        self.menu.menu_recentes.aboutToShow.connect(self._montar_livros_recentes)
        # Rodada 14 do layout: o menu Painéis (903 B) e as peças do menu Ver
        # (904 A). Os itens marcados acompanham a tela (abrir pelo ícone, a
        # seta que esconde os ícones), sem virar clique de novo.
        paineis = conferir.paineis
        for chave, painel, _texto in self.menu.PAINEIS_DO_MENU:
            self.menu.ligar(chave, lambda marcado=False, p=painel:
                            paineis.mostrar_painel(p, bool(marcado)))
        self.menu.ligar("painel_fechar", paineis.fechar)
        self.menu.ligar("icones", lambda marcado=False: paineis.mostrar_icones(bool(marcado)))
        self.menu.ligar("miniaturas", lambda marcado=False: conferir.mostrar_miniaturas(bool(marcado)))
        paineis.abriu.connect(lambda chave: self.menu.marcar_painel(chave or None))
        conferir.miniaturas_mudaram.connect(self._miniaturas_mudaram)
        # as miniaturas podem abrir fechadas (lembradas do último livro, 22/10/2026)
        self._miniaturas_mudaram(conferir.miniaturas.aberta)
        self.menu.ligar("todas_as_paginas", conferir.abrir_todas_as_paginas)
        self.menu.ligar("filtros_tela_cheia", conferir.abrir_filtros_em_tela_cheia)
        # etapa 6 da obra (D-015, D-058): Ver > "Ver lado a lado" e a barra de
        # baixo ("Uma página / Duas lado a lado") andam juntos
        self.menu.ligar("lado_a_lado", lambda marcado=False: self._ver_lado_a_lado(bool(marcado)))
        conferir.mostrar_mudou.connect(self._mostrar_mudou)
        self._mostrar_mudou(conferir.mostrar)
        paineis.icones_mudaram.connect(self._icones_mudaram)

        self.menu.ligar("atalhos", self._mostrar_atalhos)
        self.menu.ligar("configuracoes", self._abrir_configuracoes)

        for nome in estilo.TEMAS:
            self.menu.ligar(f"tema_{nome}", lambda _marcado=False, t=nome: self._trocar_tema(t))
        self.menu.marcar_tema(estilo.tema_atual())

        # Etapa 2 da obra: o lado direito (R7 203 D, "Mas eu também quero ter
        # a opção da area de trabalho 1"; R14 902 C, menu Ver e Configurações)
        from ui.widgets.paineis import JEITOS_DO_LADO_DIREITO, jeito_guardado

        for jeito in JEITOS_DO_LADO_DIREITO:
            self.menu.ligar(f"lado_{jeito}",
                            lambda _marcado=False, j=jeito: self._trocar_lado_direito(j))
        paineis.jeito_mudou.connect(self.menu.marcar_lado_direito)
        paineis.definir_jeito(jeito_guardado())
        self.menu.marcar_lado_direito(paineis.jeito)

    def _no_trabalho(self, acao):
        """Embrulha uma ação de menu (e a tecla dela) que mexe no trabalho do
        livro (etapa 2 da obra, 26/10/2026). Ela só age quando o trabalho
        aberto na área de trabalho é o DESTE livro (já conferido), e só na tela
        de trabalho ou na "O que fazer" (onde o Desfazer sempre valeu: o
        verificador, 30/09, r15). Na "O que fazer" de um livro que ainda não
        foi para a área de trabalho, avisa o que fazer em vez de mexer no livro
        de antes (as teclas já valiam ali, e iam para o trabalho do livro
        anterior); nas outras telas não faz nada. Arriscado: ligar um item que
        mexe no trabalho sem passar por aqui."""
        def feito(*_argumentos) -> None:
            # etapa 3 da obra: so existe a area de trabalho (a tela "O que
            # fazer" saiu do caminho)
            if self.telas.currentIndex() != CONFERIR:
                return
            if (self.trabalho_carregado and self.projeto is not None
                    and self.tela_conferir.projeto is self.projeto):
                acao()
        return feito

    def _acertar_o_desfazer_do_menu(self) -> None:
        """P-125 (D-020: "Ctrl+Z desfaz qualquer alteração"; o defeito
        "Desfazer ligado sem nada"): menu Editar > Desfazer aceso só quando há
        o que desfazer, Refazer só quando há o que refazer - o mesmo que a
        barra de baixo mostra (TelaConferir._atualizar_barra_de_baixo). Num
        livro recém-aberto, os dois apagados. Chamado a cada mudança da tela
        (trabalho_mudou: ação feita, desfeita, página aberta). Seguro mudar: o
        texto. Arriscado: apagar o item pelo menu inteiro (Editar) - o
        "Mostrar o histórico" mora nele."""
        acoes = getattr(self.tela_conferir, "acoes", None)
        self.menu.acoes["desfazer"].setEnabled(bool(acoes and acoes.feitas))
        self.menu.acoes["refazer"].setEnabled(bool(acoes and acoes.desfeitas))

    def _marcar_o_filtro_no_menu(self) -> None:
        """D-492 (escolha da gerente, 27/10/2026, apoiada no "o botão tem que
        ser provado que ele faz o que se diz"; promessa P-085): no menu
        Filtro fica marcado SÓ o filtro da página que está na tela. Antes os
        itens eram de marcar mas ninguém acertava a marca: escolhido o Preto
        e branco pelo cartão, o menu ficava sem marca, e a marca de um clique
        no menu ficava lá ao passar para uma página em Original. Página com
        um filtro que o menu não tem ("Tirar o fundo") ou sem livro aberto:
        nenhum marcado. Não vira clique (blockSignals). Barato: lê um campo."""
        from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO

        conferir = self.tela_conferir
        projeto = conferir.projeto
        filtro = None
        if projeto is not None and 0 <= conferir.indice_pagina < len(projeto.paginas):
            filtro = projeto.paginas[conferir.indice_pagina].filtro
        for chave in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO):
            item = self.menu.acoes[f"filtro_{chave}"]
            item.blockSignals(True)
            item.setChecked(chave == filtro)
            item.blockSignals(False)

    def _trocar_lado_direito(self, jeito: str) -> None:
        """Menu Ver > "Lado direito" e Configurações > Aparência (R14 902 C):
        põe o jeito para valer na hora, guarda para a próxima vez e marca o
        menu (etapa 2 da obra; R7 203 D: "Mas eu também quero ter a opção da
        area de trabalho 1")."""
        from ui.widgets.paineis import guardar_jeito

        paineis = self.tela_conferir.paineis
        paineis.definir_jeito(jeito)
        guardar_jeito(paineis.jeito)
        self.menu.marcar_lado_direito(paineis.jeito)

    def _miniaturas_mudaram(self, abertas: bool) -> None:
        """As miniaturas abriram ou fecharam (pela seta ou pelos três
        pontinhos): o "Miniaturas" do menu Ver acompanha."""
        item = self.menu.acoes["miniaturas"]
        item.blockSignals(True)
        item.setChecked(bool(abertas))
        item.blockSignals(False)

    def _ver_lado_a_lado(self, ligado: bool) -> None:
        """Menu Ver > "Ver lado a lado" (D-015, D-058): marcado, a área de
        trabalho mostra "Duas lado a lado"; desmarcado, "Uma página". Fora da
        área de trabalho o item volta a mostrar o que a tela tem."""
        from ui.widgets.paginas_rolando import DUAS, UMA

        conferir = self.tela_conferir
        if self.telas.currentIndex() == CONFERIR and conferir.projeto is not None:
            conferir.definir_mostrar(DUAS if ligado else UMA)
        self._mostrar_mudou(conferir.mostrar)

    def _mostrar_mudou(self, jeito: str) -> None:
        """A barra de baixo trocou entre "Uma página" e "Duas lado a lado": o
        "Ver lado a lado" do menu Ver acompanha, sem virar clique."""
        from ui.widgets.paginas_rolando import DUAS

        item = self.menu.acoes["lado_a_lado"]
        item.blockSignals(True)
        item.setChecked(jeito == DUAS)
        item.blockSignals(False)

    def _icones_mudaram(self, a_vista: bool) -> None:
        """A coluna de ícones apareceu ou sumiu (pela seta ou pelo menu): o
        "Ícones da direita" dos menus Ver e Painéis acompanha."""
        item = self.menu.acoes["icones"]
        item.blockSignals(True)
        item.setChecked(bool(a_vista))
        item.blockSignals(False)

    def _modo_comparar(self) -> None:  # noqa: D401
        """Menu Ver > "Modo comparar": abre a página grande já com dois filtros
        lado a lado (o "comparar" da tela grande). O item não fica marcado: a
        tela grande é uma janela à parte, e ao fechá-la o modo acaba."""
        self.menu.acoes["comparar"].setChecked(False)
        if self.telas.currentIndex() == CONFERIR:
            self.tela_conferir.ampliar(comparar=True)

    def _montar_livros_recentes(self) -> None:
        """Menu Arquivo > "Livros recentes": os livros da tela inicial (os
        mesmos cartões), do mexido por último ao mais antigo; clicar abre o
        livro do jeito que o cartão "continuar" abre. Montado na hora de abrir
        o menu (a lista muda a cada livro). Passa pela mesma conferência do
        cartão (o PDF ainda existe e é o MESMO livro: pedir_para_continuar), e
        o livro aberto é gravado antes (abrir_livro)."""
        menu = self.menu.menu_recentes
        menu.clear()
        try:
            resumos = projetos.listar()[:MAXIMO_DE_RECENTES]
        except Exception:  # noqa: BLE001 - o menu nunca derruba a janela
            registrar_erro("livros recentes", traceback.format_exc())
            resumos = []
        if not resumos:
            vazio = menu.addAction("(nenhum livro ainda)")
            vazio.setEnabled(False)
            return
        for resumo in resumos:
            acao = menu.addAction(resumo.nome or Path(resumo.caminho_entrada).name)
            acao.triggered.connect(lambda _c=False, r=resumo: self.tela_inicio.pedir_para_continuar(r))

    def _continuar_e_processar(self, resumo) -> None:
        """"Confirmar e processar..." do livro aberto (etapa 7 do layout):
        continua o trabalho; quando ele abrir, pede a confirmação de sempre
        (processar). Se a abertura falhar ou for cancelada, nada é processado."""
        self._processar_ao_abrir = True
        self._continuar_projeto(resumo)
        if self.telas.currentIndex() != PROGRESSO and self.telas.currentIndex() != CONFERIR:
            self._processar_ao_abrir = False

    def _trocar_tema(self, nome: str) -> None:
        """Menu Ver > Tema (etapa 1 do layout): põe o tema para valer na hora,
        em tudo o que está aberto, e guarda a escolha para a próxima vez."""
        estilo.definir_tema(nome)
        estilo.reaplicar_em_tudo()
        self.menu.marcar_tema(nome)

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
        self.tela_conferir.girar_do_canto.definir_teclas(teclas)

    def _tela_mudou(self, indice: int) -> None:
        """So a tela de Conferir usa o menu completo; nas outras ele fica apagado.
        A barra de opcoes, na linha dos menus (etapa 2 do layout), so aparece
        na tela de trabalho."""
        if not hasattr(self, "menu"):
            return
        # Lista unica 1.12 (23/10/2026: menus Editar, Marcar, Filtro, Pagina e
        # Paineis cinza na tela das caixinhas): com um livro aberto (a tela de
        # trabalho, ou a "O que fazer" dele) todos os menus ficam acesos; o
        # que mexe no trabalho passa por _no_trabalho (etapa 2 da obra).
        if indice == CONFERIR:
            self.menu.mostrar_tela_de_trabalho()
        else:
            self.menu.mostrar_tela_inicial()
        # Etapa 7 do layout (rodadas 4 a 6): a tela dos livros não tem barra
        # de menus, só "Configurações" e "Ajuda" no alto. As teclas dos menus
        # continuam valendo (as ações também estão na janela).
        if hasattr(self, "linha_dos_menus"):
            self.linha_dos_menus.setVisible(indice != INICIO)
        # e o livro aberto para de ler o PDF ao sair dela (duas leituras do
        # mesmo arquivo ao mesmo tempo já travaram o MuPDF: _montar_tira)
        if hasattr(self, "tela_inicio"):
            self.tela_inicio.mostrar_os_livros()
        for peca in getattr(self, "_pecas_da_tela_de_trabalho", ()):
            peca.setVisible(indice == CONFERIR)
        # etapa 9b-1 (D-033): os botões do "Painel solto" moram na linha dos
        # menus e só aparecem na tela de trabalho (e só nesse jeito)
        if hasattr(self, "tela_conferir"):
            self.tela_conferir.paineis.definir_na_tela(indice == CONFERIR)

    def _montar_a_linha_dos_menus(self) -> None:
        """Etapa 2 do layout (rodada 8, 303 B: "Na mesma linha dos menus"): a
        linha de cima tem os menus, um traço e a barra de opções da
        ferramenta (só o nome e os ajustes: rodada 12, 702 C). A página ganha
        a altura das duas faixas que saíram (abas e barra de opções). O girar,
        que na etapa 2 ficava na ponta desta linha, foi para o painel
        Propriedades e para o canto da página (rodada 12, 703 B e D)."""
        from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

        linha = QWidget()
        linha.setObjectName("linhaDosMenus")
        linha.setAttribute(Qt.WA_StyledBackground, True)
        caixa = QHBoxLayout(linha)
        caixa.setContentsMargins(0, 0, 0, 0)
        caixa.setSpacing(0)
        self.menu.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        # os menus nunca encolhem (o Qt os esconderia atrás de um "..."); quem
        # cede lugar é a dica da barra de opções e o nome dos botões de girar
        self.menu.setMinimumWidth(self.menu.sizeHint().width())
        caixa.addWidget(self.menu, 0, Qt.AlignVCenter)
        traco = QFrame()
        traco.setObjectName("separadorDosMenus")
        traco.setFixedSize(1, 20)
        caixa.addSpacing(6)
        caixa.addWidget(traco, 0, Qt.AlignVCenter)
        caixa.addSpacing(6)
        conferir = self.tela_conferir
        caixa.addWidget(conferir.barra_opcoes, 1)
        # etapa 9b-1 (D-033, o "Painel solto"): os botões dos cinco painéis na
        # linha de cima, à direita (o desenho `13-rodada7-padrao-e-flutuante`);
        # escondidos nos outros jeitos (ColunaDePaineis._acertar)
        caixa.addWidget(conferir.paineis.botoes_do_alto, 0, Qt.AlignVCenter)
        caixa.addSpacing(8)
        # Mola de peso zero no fim: com a barra de opções à vista (peso 1) ela
        # não ganha nada; nas telas sem ela (inicial, "O que fazer") é ela que
        # fica com a sobra, e os menus continuam à esquerda (sem ela, o Qt
        # centralizava os menus: prints do Windows de 09/10/2026). Arriscado:
        # dar peso a ela (tiraria a largura da barra de opções).
        caixa.addStretch(0)
        self._pecas_da_tela_de_trabalho = (traco, conferir.barra_opcoes)
        self.setMenuWidget(linha)
        self.linha_dos_menus = linha
        # as teclas dos menus valem mesmo com a linha escondida (tela dos livros)
        self.addActions(list(self.menu.acoes.values()))

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Etapa 2 do layout: os menus nunca encolhem (quem cede lugar é a
        barra de opções)."""
        super().resizeEvent(evento)
        if hasattr(self, "linha_dos_menus"):
            self.menu.setMinimumWidth(self.menu.sizeHint().width())

    def _escolher_pasta_de_saida(self) -> None:
        """Item de menu "Escolher a pasta de saída...": so lembra a pasta
        padrao, quem decide o destino de verdade e a janela de confirmacao."""
        # Obra 26/10 (etapa 9a): janela do Windows em portugues, caminho
        # conferido na volta (ui/dialogos_de_arquivo.py).
        from ui.dialogos_de_arquivo import escolher_pasta

        if self.projeto is None:
            return
        pasta = escolher_pasta(
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
        """Ponto de entrada de "abrir um livro": valida o PDF, cria (ou
        recupera) o Projeto e o resumo em disco, e abre DIRETO na area de
        trabalho (etapa 3 da obra; D-002, Kaique 22/09: "nós tínhamos que
        abrir direto na área de trabalho").

        Livro novo: a passada leve (core/automatico.livro_leve: uma folha por
        pagina do PDF, nada ligado, a pagina como veio) e a medida por tras
        (D-284). Livro com trabalho salvo: o trabalho volta como esta
        (_abrir_o_trabalho), sem analise nova. Se o salvo nao serve (outro
        livro, outro numero de folhas, arquivo ilegivel), o trabalho antigo e
        guardado ao lado (projetos.guardar_copia_do_trabalho) e o livro abre
        leve, com o aviso do motivo.

        `resumo`: o projeto EXATO a abrir (o do cartao da tela inicial, pelo
        "continuar" ou pelo "comecar de novo"). Sem ele ("Abrir", arrastar,
        Windows), o projeto e achado pela assinatura do arquivo - o mais
        recente, se houver mais de um do mesmo PDF (verificador, 29/09,
        q24-q25). Arriscado: voltar a procurar pela assinatura quando o cartao
        ja disse qual e.

        Antes de tudo, a mudanca do livro aberto que ainda esperava o relogio
        de salvar vai para o disco NA HORA (_guardar_o_livro_aberto; R-A do
        verificador-2, 06/10/2026). Arriscado: mover essa gravacao para depois
        de self.projeto/self.resumo mudarem.
        """
        from core import automatico

        self._guardar_o_livro_aberto()
        try:
            doc = abrir_pdf(caminho)
            try:
                self.total_folhas = doc.page_count
                tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
                # Item 1.1: o PDF vem com camadas (Internet Archive)? So a
                # estrutura de ate 12 paginas, sem desenhar nenhuma.
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
        if isinstance(self.tarefa, TarefaAutomatico):
            self.tarefa.cancelar()
        # A conversao das zonas e a medida do livro de antes param: o que ja
        # fizeram foi gravado com o trabalho dele.
        self._parar_a_conversao_das_zonas(gravar=True)
        self._parar_a_medida_ao_abrir()
        self.trabalho_carregado = False       # ate o trabalho abrir (_salvar_agora)
        self._fundo_pendente = None
        aberto = Projeto(caminho_entrada=caminho, nome=nome)
        aberto.tem_camadas = tem_camadas
        automatico.livro_leve(aberto, tamanhos)
        self.projeto = aberto

        # Abrir o MESMO livro de novo continua o projeto de antes, em vez de
        # criar um ao lado: quem for reabrir de proposito passa pela tela
        # inicial, que tem "comecar de novo" no menu do cartao.
        self.resumo = resumo if resumo is not None else projetos.achar_por_assinatura(caminho)
        salvo = None
        motivo = ""
        recomecou = False
        self.copia_do_trabalho = None
        if self.resumo is None:
            # Item 2.19: a receita de todo livro novo NAO e posta aqui (a pagina
            # abre como veio): ela vem marcada no Automatico (D-018).
            self.resumo = projetos.criar(aberto, self.total_folhas)
        else:
            self.resumo.caminho_entrada = caminho   # pode ter mudado de pasta
            tinha_trabalho = projetos.tem_trabalho_salvo(self.resumo)
            salvo = projetos.carregar_estado(self.resumo)
            if salvo is not None and salvo.paginas:
                motivo = projetos.motivo_sem_analise(salvo, aberto, self.resumo.assinatura)
                if not motivo:
                    # o trabalho de antes volta inteiro; o tem_camadas e fato do
                    # PDF (acabou de ser visto) e o caminho e o de agora
                    salvo.tem_camadas = tem_camadas
                    salvo.caminho_entrada = caminho
                    self.projeto = salvo
                else:
                    recomecou = True
            elif tinha_trabalho:
                recomecou = True
                motivo = "o trabalho salvo não pôde ser lido"
            if salvo is not None and not salvo.paginas:
                # projeto so com as opcoes (de antes da etapa 3: a resposta a
                # pergunta do fundo gravava assim): o "ja perguntou" e o "Sim"
                # do fundo voltam; o resto fica de fabrica
                aberto.perguntou_fundo = bool(salvo.perguntou_fundo)
                if salvo.filtro_padrao == TIRAR_FUNDO and salvo.perguntou_fundo:
                    self._fundo_pendente = self.resumo.pasta
            if recomecou and tinha_trabalho:
                self.copia_do_trabalho = projetos.guardar_copia_do_trabalho(self.resumo)
        self.acoes = HistoricoAcoes(Path(self.resumo.pasta))
        self._giro_da_capa = 0           # a capa nasce como veio no PDF (D2)
        self._abrir_o_trabalho(recomecou, motivo, len(salvo.paginas) if recomecou and salvo else 0)

        # Item 1.1, decisao do Samuel (29/09): a pergunta do fundo aparece "uma
        # vez por livro, inclusive nos que ele ja tem". Agora com o livro ja
        # na area de trabalho (D-135: nao se perde ao abrir direto).
        if tem_camadas and not self.projeto.perguntou_fundo:
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
        estiver aberto. Outro livro aberto no meio: a resposta nao vale.

        Nao (e Esc, e X): fica anotado "ja perguntou" (Projeto.perguntou_fundo)
        e nada mais muda. Sim: desde a etapa 3 da obra o livro ja esta na area
        de trabalho quando a pergunta aparece, entao o fundo sai na hora, numa
        acao do Historico (_tirar_o_fundo_do_livro_inteiro), e grava.
        Arriscado: anotar "ja perguntou" para um "Sim" que nao foi aplicado.
        """
        if pasta is None or self.resumo is None or self.resumo.pasta != pasta:
            return
        if self.projeto is None:
            return
        if not tirar:
            self.projeto.perguntou_fundo = True
            if not projetos.anotar_no_estado(self.resumo, perguntou_fundo=True):
                self._salvar_agora()
            return
        self.projeto.perguntou_fundo = True
        self._tirar_o_fundo_do_livro_inteiro()
        self._salvar_agora()

    def _tirar_o_fundo_do_livro_inteiro(self) -> None:
        """O "Sim" da pergunta do fundo (e o "Sim" guardado de um projeto so
        com as opcoes): o livro inteiro vai para o filtro "Tirar o fundo".

        Decisao do Samuel (29/09, f94f69b): troca SO as paginas que estao em
        "Original"; as que ele pos em outro filtro ficam. O filtro do livro
        vira "Tirar o fundo" e, desde a etapa 3 da obra (o livro abre sem nada
        ligado), o "Limpar a folha" do livro liga junto (sem ele nenhum filtro
        vale). Tudo numa acao so do Historico ("Tirar o fundo em N paginas"); o
        desfazer devolve tambem o filtro e o "Limpar" do livro (campos
        "livro." da acao, historico_acoes.aplicar). D-069 (30/09): depois de
        aberto, o mesmo da pelo Automatico, etapa "Limpar a folha", filtro
        "Tirar o fundo" (e "Original" volta ao como veio).
        """
        from core.filtros import ORIGINAL, TIRAR_FUNDO
        from historico_acoes import aplicar, montar_acao

        self._fundo_pendente = None
        if self.projeto is None:
            return
        self.projeto.perguntou_fundo = True
        indices = [p.indice for p in self.projeto.paginas if p.filtro == ORIGINAL]
        filtro_do_livro = self.projeto.filtro_padrao
        limpar_do_livro = bool(self.projeto.limpar)
        conferir = self.tela_conferir
        if conferir.projeto is not self.projeto or self.acoes is None:
            self.projeto.filtro_padrao = TIRAR_FUNDO
            self.projeto.limpar = True
            return
        if not indices and filtro_do_livro == TIRAR_FUNDO and limpar_do_livro:
            return
        acao = montar_acao(
            self.projeto, "aplicar_em_todas", "pagina", indices, {"filtro": TIRAR_FUNDO},
            f"Tirar o fundo em {len(indices)} páginas (resposta à pergunta do fundo)")
        acao.antes["livro.filtro_padrao"] = filtro_do_livro
        acao.depois["livro.filtro_padrao"] = TIRAR_FUNDO
        acao.antes["livro.limpar"] = limpar_do_livro
        acao.depois["livro.limpar"] = True
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)
        if conferir.previas is not None:
            for indice in indices:
                conferir.previas.invalidar(indice)
        conferir.atualizar()

    def _continuar_projeto(self, resumo: projetos.Resumo) -> None:
        """Retoma um projeto exatamente onde parou: o trabalho salvo volta
        como esta, direto na area de trabalho (etapa 3 da obra: sem analise
        nova; antes ela rodava e o salvo voltava por cima). A tela inicial ja
        conferiu que o livro esta la e que e ELE."""
        self.abrir_livro(resumo.caminho_entrada, resumo=resumo)   # ESTE projeto

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

    # --- o trabalho na area de trabalho -------------------------------------

    def _abrir_o_trabalho(self, recomecou: bool = False, motivo: str = "",
                          paginas_perdidas: int = 0) -> None:
        """Poe o projeto aberto (self.projeto) na area de trabalho: o
        Historico, as previas, a tela, a gravacao, a conversao das zonas e a
        medida por tras. Etapa 3 da obra: era a segunda metade do antigo
        _analise_pronta (o fim da analise); agora o livro abre sem analise.

        recomecou: o trabalho salvo nao serviu (motivo = por que) - o desfazer
        recomeca vazio e o historico antigo fica junto da copia do trabalho
        (HistoricoAcoes.recomecar; Lista de bugs, 06/10/2026). Arriscado:
        carregar o historico antigo num trabalho que recomecou (o Ctrl+Z
        mexeria em paginas de outra conferencia)."""
        from core import automatico

        assert self.acoes is not None and self.projeto is not None
        projeto = self.projeto
        self.trabalho_carregado = True        # agora pode gravar (_salvar_agora)
        acertar_alertas_do_fundo(projeto)
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
        if self.resumo is not None and not recomecou:
            self.tela_conferir.ir_para_pagina(
                min(self.resumo.pagina_atual, max(0, len(projeto.paginas) - 1)))
        # o Automatico comeca do que o livro tem (etapas ligadas, opcoes, ordem)
        self.tela_conferir.paineis.automatico.estado.do_projeto(projeto)
        self.tela_conferir.paineis.automatico.encher_receitas()
        if self.resumo is not None and self._fundo_pendente == self.resumo.pasta:
            self._tirar_o_fundo_do_livro_inteiro()
        self.telas.setCurrentIndex(CONFERIR)
        self._salvar_agora()
        # etapa 7 do layout: "Confirmar e processar..." do livro aberto pede a
        # confirmação de sempre assim que o trabalho abre
        if self._processar_ao_abrir:
            self._processar_ao_abrir = False
            QTimer.singleShot(0, self.processar)
        # Decisao Z1 (b): as zonas de projeto antigo sao convertidas por
        # tras, o livro inteiro, enquanto o Kaique ja trabalha.
        self._comecar_a_converter_as_zonas()
        # D-284: o livro novo e medido por tras (so os avisos)
        if not getattr(projeto, "passou_pelo_automatico", True):
            self._comecar_a_medir_ao_abrir()

        if self.acoes.linhas_perdidas:
            perdidas = self.acoes.linhas_perdidas
            self.avisar(
                "O computador foi desligado no meio da última gravação, e "
                + ("1 ação do fim se perdeu. " if perdidas == 1
                   else f"{perdidas} ações do fim se perderam. ")
                + "O resto do trabalho está aqui.")
        elif recomecou:
            self.avisar(self._frase_do_recomeco(motivo, self.copia_do_trabalho))
        del automatico

    # --- etapa 3 da obra: a medida do livro por tras (D-284) ---------------

    def _comecar_a_medir_ao_abrir(self) -> None:
        """D-284 (`pr-medir-o-livro`, 21/10: "Medir o livro inteiro por trás,
        depois de abrir"): mede todas as folhas por tras e, no fim, poe so os
        avisos (nenhuma pagina muda). Livro com trabalho salvo ja tem os
        avisos da conferencia de antes: so o livro novo e medido (escolha da
        gerente, D-014; anotada no ONDE-PAREI)."""
        from core import automatico

        self._parar_a_medida_ao_abrir()
        if self.projeto is None or not self.projeto.folhas:
            return
        foto = automatico.fotografar(self.projeto, automatico.Pedido(etapas=[]))
        tarefa = TarefaMedirAoAbrir(foto)
        tarefa.terminou.connect(self._medida_ao_abrir_terminou)
        self.medida_ao_abrir = tarefa
        self._projeto_medido = self.projeto
        tarefa.start()

    def _parar_a_medida_ao_abrir(self) -> None:
        tarefa = getattr(self, "medida_ao_abrir", None)
        self.medida_ao_abrir = None
        if tarefa is None:
            return
        tarefa.cancelar()
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)

    def _medida_ao_abrir_terminou(self, tarefa, medidas) -> None:
        """Os avisos medidos entram no livro (so o da vez; um sinal atrasado
        de outro livro nao entra). Nao entra no Historico: aviso nao e
        trabalho."""
        from core import automatico

        if tarefa is None or tarefa is not getattr(self, "medida_ao_abrir", None):
            return
        self.medida_ao_abrir = None
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)
        projeto = self.projeto
        if (projeto is None or projeto is not getattr(self, "_projeto_medido", None)
                or not medidas):
            return
        automatico.avisos_do_livro(projeto, medidas)
        if self.tela_conferir.projeto is projeto:
            self.tela_conferir.atualizar()
        self._marcar_para_salvar()

    # --- etapa 3 da obra: o Automatico (D-002, D-003, D-004, D-005, D-018) --

    def _ligar_o_automatico(self) -> None:
        """Liga o painel Automatico, o aviso do livro novo e a grade de
        "Todas as páginas" ao que roda o automatico (rodar_o_automatico)."""
        painel = self.tela_conferir.paineis.automatico
        painel.rodar_pedido.connect(lambda: self.rodar_o_automatico())
        painel.desligar_pedido.connect(lambda: self.rodar_o_automatico(desligar=True))
        painel.escolher_pedido.connect(lambda: self.escolher_paginas_para_o_automatico())
        painel.receita_guardar_pedida.connect(lambda: self.guardar_receita())
        self.tela_conferir.automatico_pedido.connect(lambda etapa: self.abrir_o_automatico(etapa))
        self.tela_conferir.rodar_do_aviso_pedido.connect(lambda: self._rodar_do_aviso())
        self.tela_conferir.escolhidas_para_o_automatico.connect(self._escolhidas_chegaram)
        self.janela_do_automatico = None

    @property
    def estado_do_automatico(self):
        """O que esta escolhido no Automatico (o mesmo do painel e da janela)."""
        return self.tela_conferir.paineis.automatico.estado

    def abrir_o_automatico(self, etapa: str = "", receita: str | None = None):
        """Abre a janela grande do Automatico (rodada 2: "painel (opção 1) com
        botão que abre a janela (opção 2)"), na `etapa` (o "ajustar ›"). Com
        `receita`, ela vem marcada (D-018). Devolve a janela (testes)."""
        from ui.automatico import JanelaDoAutomatico

        if self.projeto is None or self.telas.currentIndex() != CONFERIR:
            return None
        estado = self.estado_do_automatico
        estado.pagina_atual = self.tela_conferir.indice_pagina
        if receita:
            estado.por_receita(receita)
        self._fechar_a_janela_do_automatico()
        janela = JanelaDoAutomatico(estado, self.projeto.caminho_entrada, self)
        janela.rodar_pedido.connect(lambda: self._da_janela(janela, desligar=False))
        janela.desligar_pedido.connect(lambda: self._da_janela(janela, desligar=True))
        janela.escolher_pedido.connect(lambda: self._escolher_da_janela(janela))
        janela.receita_guardar_pedida.connect(lambda: self.guardar_receita(janela))
        if etapa:
            janela.mostrar_etapa(etapa)
        self.janela_do_automatico = janela
        janela.open()
        return janela

    def _fechar_a_janela_do_automatico(self) -> None:
        janela = getattr(self, "janela_do_automatico", None)
        self.janela_do_automatico = None
        if janela is not None:
            try:
                janela.done(0)
                janela.deleteLater()
            except RuntimeError:
                pass

    def _da_janela(self, janela, desligar: bool) -> None:
        """"Rodar" (ou "Desligar as marcadas") da janela grande: ela fecha e
        o automatico roda."""
        self._fechar_a_janela_do_automatico()
        self.rodar_o_automatico(desligar=desligar)

    def _escolher_da_janela(self, janela) -> None:
        self._fechar_a_janela_do_automatico()
        self._voltar_para_a_janela = True
        self.escolher_paginas_para_o_automatico()

    def escolher_paginas_para_o_automatico(self) -> None:
        """"escolher páginas...": a grade "Todas as páginas" no jeito de
        escolher (rodada 2 nº 5, "Aprovado": "Escolher folhas abrindo a tela
        de todas as páginas (marcar/desmarcar)")."""
        if self.projeto is None:
            return
        self.tela_conferir.abrir_para_escolher(self.estado_do_automatico.escolhidas)

    def _escolhidas_chegaram(self, escolhidas: list) -> None:
        """A grade devolveu as paginas escolhidas: o Automatico passa a rodar
        nelas, e a janela grande volta (se foi dela que se pediu)."""
        from ui.automatico import NAS_ESCOLHIDAS

        self.estado_do_automatico.definir_alcance(NAS_ESCOLHIDAS, escolhidas)
        if getattr(self, "_voltar_para_a_janela", False) or not self.tela_conferir.paineis.automatico.isVisible():
            self._voltar_para_a_janela = False
            self.abrir_o_automatico()
        else:
            self.tela_conferir.paineis.mostrar_painel("automatico", True)

    def _rodar_do_aviso(self) -> None:
        """"Rodar o automático…" do aviso do livro novo (D-005): a janela
        grande com a receita de sempre marcada (D-018, escolha da gerente:
        nada roda antes do "Rodar")."""
        from core import perfis

        if self.projeto is None:
            return
        self.estado_do_automatico.do_projeto(self.projeto)
        self.abrir_o_automatico(receita=perfis.receita_de_sempre())

    def _abrir_e_mostrar_o_automatico(self, resumo) -> None:
        """"Rodar o automático..." do livro aberto da tela inicial (R6): abre
        o livro (o "continuar") e a janela grande do Automatico."""
        self.abrir_livro(resumo.caminho_entrada, resumo=resumo)
        if self.telas.currentIndex() == CONFERIR and self.projeto is not None:
            self.abrir_o_automatico()

    def guardar_receita(self, pai=None) -> None:
        """"Salvar receita...": a caixa nova (D-071: diz o que vai dentro)."""
        from ui.automatico import CaixaDaReceita

        caixa = CaixaDaReceita(self.estado_do_automatico, pai or self)
        self.caixa_da_receita = caixa

        def fechou(_codigo: int) -> None:
            self.tela_conferir.paineis.automatico.encher_receitas()
            janela = getattr(self, "janela_do_automatico", None)
            if janela is not None:
                janela.encher_receitas()
            self.estado_do_automatico.mudou.emit()

        caixa.finished.connect(fechou)
        caixa.open()

    def _perguntar_mexidas(self, quantas: int) -> bool | None:
        """D-004 (28/09): "Automático em livro já mexido à mão: o programa
        pergunta se quer pular as páginas mexidas." Devolve True (pular),
        False (rodar nelas tambem) ou None (desistir)."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Páginas mexidas à mão")
        caixa.setIcon(QMessageBox.Question)
        palavra = "página foi mexida" if quantas == 1 else "páginas foram mexidas"
        caixa.setText(f"{quantas} {palavra} à mão nas etapas que vão rodar. "
                      "Pular essas páginas?")
        caixa.setInformativeText(
            "Pular: elas ficam como você deixou nessas etapas. Rodar nelas também: o "
            "automático passa por cima do que você fez à mão nelas (o Desfazer traz de volta).")
        pular = caixa.addButton(f"Pular as {quantas}" if quantas > 1 else "Pular esta",
                                QMessageBox.AcceptRole)
        rodar = caixa.addButton("Rodar nelas também", QMessageBox.DestructiveRole)
        caixa.addButton("cancelar", QMessageBox.RejectRole)
        caixa.setDefaultButton(pular)
        caixa.exec()
        escolhido = caixa.clickedButton()
        if escolhido is pular:
            return True
        if escolhido is rodar:
            return False
        return None

    def rodar_o_automatico(self, desligar: bool = False, pedido=None, esperar: bool = False,
                           perguntar: bool = True) -> bool:
        """Roda o Automatico no livro aberto (D-002): o pedido do painel/janela
        (ou `pedido`), com a pergunta das paginas mexidas (D-004). O que olha
        as paginas roda num fio de fundo (TarefaAutomatico), com andamento e
        cancelar; no fim, _aplicar_o_automatico grava no projeto aberto.
        `esperar` (testes e linha de comando): mede no mesmo fio.
        `perguntar=False` (testes): nao pergunta das mexidas; vale o
        pedido.pular_mexidas. Devolve False quando nada foi pedido ou a pessoa
        desistiu."""
        from core import automatico

        if self.projeto is None or self.acoes is None or not self.trabalho_carregado:
            return False
        if pedido is None:
            self.estado_do_automatico.pagina_atual = self.tela_conferir.indice_pagina
            pedido = self.estado_do_automatico.pedido(desligar=desligar)
        if not pedido.etapas:
            self.avisar("Marque pelo menos uma etapa no Automático.", titulo="Automático")
            return False
        if pedido.paginas is not None and not pedido.paginas:
            self.avisar("Nenhuma página escolhida. Use \"escolher páginas...\" ou rode no livro todo.",
                        titulo="Automático")
            return False
        mexidas = automatico.paginas_mexidas(self.projeto, pedido) if perguntar else []
        if mexidas:
            resposta = self._perguntar_mexidas(len(mexidas))
            if resposta is None:
                return False
            pedido.pular_mexidas = bool(resposta)
        if not automatico.precisa_medir(pedido):
            self._aplicar_o_automatico(pedido, {})
            return True
        foto = automatico.fotografar(self.projeto, pedido)
        if esperar:
            self._aplicar_o_automatico(pedido, automatico.medir(foto))
            return True
        self._pedido_da_vez = pedido
        self._projeto_do_pedido = self.projeto
        self.tela_progresso.comecar("O automático está olhando as páginas...")
        self.telas.setCurrentIndex(PROGRESSO)
        self._trocar_tarefa(TarefaAutomatico(foto))
        self.tarefa.progresso.connect(self.tela_progresso.avancar)
        self.tarefa.concluida.connect(self._automatico_mediu)
        self.tarefa.falhou.connect(self._automatico_falhou)
        self.tarefa.start()
        return True

    def _automatico_mediu(self, medidas) -> None:
        """A medida do Automatico chegou (so a da vez e do livro de agora)."""
        origem = self.sender()
        if isinstance(origem, TarefaAutomatico) and (origem is not self.tarefa or origem.foi_cancelada):
            return
        self.telas.setCurrentIndex(CONFERIR)
        if self.projeto is None or self.projeto is not getattr(self, "_projeto_do_pedido", None):
            return
        self._aplicar_o_automatico(self._pedido_da_vez, medidas)

    def _automatico_falhou(self, mensagem: str) -> None:
        origem = self.sender()
        if isinstance(origem, TarefaAutomatico) and origem is not self.tarefa:
            return
        self.telas.setCurrentIndex(CONFERIR)
        self.avisar(mensagem)

    def _aplicar_o_automatico(self, pedido, medidas) -> None:
        """Grava o Automatico no projeto aberto, numa acao do Historico
        (fica no acoes.jsonl: achado 1-11), e redesenha. Mudando as opcoes das
        gravuras, guarda antes uma copia do trabalho e avisa (como o "Conferir"
        fazia: core.pipeline.trocar_opcoes_da_gravura)."""
        from core import automatico
        from core.pipeline import aviso_das_opcoes_da_gravura

        assert self.projeto is not None and self.acoes is not None
        projeto = self.projeto
        mudam_as_gravuras = (automatico.GRAVURAS in pedido.etapas and not pedido.desligar
                             and any(pedido.opcoes.get(c, getattr(projeto, c)) != getattr(projeto, c)
                                     for c in automatico.OPCOES[automatico.GRAVURAS]))
        if mudam_as_gravuras and self.resumo is not None and projetos.tem_trabalho_salvo(self.resumo):
            self.copia_do_trabalho = projetos.guardar_copia_do_trabalho(self.resumo)
        resultado = automatico.aplicar(projeto, pedido, medidas)
        if resultado.acao is not None:
            self.acoes.registrar(resultado.acao)
        conferir = self.tela_conferir
        if conferir.previas is not None:
            conferir.previas.invalidar()
        conferir.lista_de_paginas_mudou()
        if automatico.DIVIDIR in pedido.etapas and not pedido.desligar:
            # D-007 (obra etapa 4): "quando eu escolher para começar no
            # automatico e dividir as folhas o livro tem que aparecer em uma
            # pagina por vez para mim" - sai do Dividir (a folha inteira)
            conferir.mostrar_paginas()
        # o painel passa a mostrar o que o livro tem agora (etapas ligadas,
        # opcoes, ordem); onde rodar e as escolhidas ficam como a pessoa deixou
        self.estado_do_automatico.do_projeto(projeto)
        self._salvar_agora()
        self._comecar_a_medir_o_livro()          # item 2.5, se o corte pelo conteudo ligou
        if resultado.gravuras_refeitas:
            titulo, frase = aviso_das_opcoes_da_gravura(projeto, resultado.gravuras_refeitas,
                                                        self.copia_do_trabalho)
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
        self._comecar_a_medir_o_livro()          # item 2.5 (so com a opcao ligada)
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
        self._parar_a_medida_do_livro()          # item 2.5
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

    # --- item 2.5: o tamanho do livro, por tras ---------------------------

    def _comecar_a_medir_o_livro(self) -> None:
        """Com o corte pelo conteudo ligado (Projeto.cortar_pelo_conteudo),
        mede por tras o tamanho do livro (ui/tarefas.TarefaMedirOLivro); no
        fim, as previas sao refeitas, ja do tamanho do livro. Desligado, ou
        tudo ja medido nesta sessao: nao faz nada."""
        from core.pipeline import paginas_sem_medida_do_conteudo

        self._parar_a_medida_do_livro()
        if self.projeto is None or not paginas_sem_medida_do_conteudo(self.projeto):
            return
        tarefa = TarefaMedirOLivro(self.projeto)
        tarefa.terminou.connect(self._medida_do_livro_terminou)
        self.medida_do_livro = tarefa
        tarefa.start()

    def _parar_a_medida_do_livro(self) -> None:
        """Para a passada da vez (trocar de livro, fechar). O que ela mediu
        fica na memoria; o resto, o PDF mede."""
        tarefa = self.medida_do_livro
        self.medida_do_livro = None
        if tarefa is None:
            return
        tarefa.cancelar()
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)

    def _medida_do_livro_terminou(self, tarefa, medidas: int) -> None:
        """A passada acabou: as previas sao refeitas, agora com o tamanho do
        livro inteiro (so a da vez; um sinal atrasado nao entra)."""
        if tarefa is None or tarefa is not self.medida_do_livro:
            return
        self.medida_do_livro = None
        if tarefa.isRunning():
            self._tarefas_saindo.append(tarefa)
        if medidas and self.tela_conferir.previas is not None:
            self.tela_conferir.previas.invalidar()
            self.tela_conferir.atualizar()

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

    def _marca_do_trabalho(self) -> tuple:
        """Um retrato barato do trabalho feito: quantas ações feitas e
        desfeitas e qual a última (a pilha do desfazer muda a cada ação de
        trabalho; folhear não a muda). Serve só para comparar com o retrato
        tirado quando o PDF ficou pronto (_ver_se_o_pdf_ficou_velho)."""
        acoes = getattr(self, "acoes", None)
        if acoes is None:
            return (0, None, 0)
        ultima = acoes.feitas[-1] if acoes.feitas else None
        return (len(acoes.feitas), id(ultima), len(acoes.desfeitas))

    def _ver_se_o_pdf_ficou_velho(self, marcacao: bool = False) -> None:
        """D-309 (Samuel, 05/10/2026: "pode mandar concertar"; "o cartão só
        diz 'PDF gerado' depois de gravar") e Lista de bugs 332 (05/10,
        "o cartão continua 'pronto, PDF gerado' depois de mudar páginas sem
        gerar de novo"): o trabalho mudou depois do PDF pronto -> o cartão
        volta a "N de M conferidas" com "continuar" (os dois jeitos que ele
        já tem; nada novo na tela). Gravado no disco no próximo salvar
        (_salvar_agora -> projetos.atualizar -> gravar_resumo).

        O que conta como mudança: uma ação a mais, a menos ou outra na pilha
        do desfazer (filtro, corte, giro, Automático, desfazer, refazer...) e
        a marcação mexida à mão (marcacao=True; ela não passa pela pilha).
        Folhear não conta. O primeiro retrato de um livro é tirado aqui
        mesmo, na primeira vez que a tela se acerta depois de abrir (o
        trabalho de então é o do PDF que o cartão já dizia pronto).
        Arriscado: contar o folhear como mudança (o cartão nunca ficaria
        pronto)."""
        # a ferramenta de marcar nasce so quando e usada a primeira vez: o
        # aviso dela (marcacao mexida a mao) e ligado aqui, uma vez
        editor = getattr(self.tela_conferir, "editor_selecao", None)
        if editor is not None and self._marcacao_ligada_ao_cartao is not editor:
            self._marcacao_ligada_ao_cartao = editor
            editor.selecao_mudou.connect(lambda: self._ver_se_o_pdf_ficou_velho(marcacao=True))
        resumo = self.resumo
        if resumo is None:
            return
        retrato = (resumo.pasta, self._marca_do_trabalho())
        guardado = self._trabalho_do_pdf
        if guardado is None or guardado[0] != resumo.pasta:
            self._trabalho_do_pdf = retrato
            if not marcacao:
                return
        if not resumo.pdf_gerado:
            self._trabalho_do_pdf = retrato
            return
        if marcacao or retrato != self._trabalho_do_pdf:
            resumo.pdf_gerado = False
            self._trabalho_do_pdf = retrato

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
        """O projeto como deve ir para o disco: o proprio projeto aberto.

        (Ate a etapa 3 da obra havia aqui uma troca das opcoes da tela "O que
        fazer" ainda nao conferidas; a tela saiu do caminho e o Automatico
        grava direto no projeto aberto, numa acao do desfazer.)"""
        return self.projeto

    def _sair_da_conferencia(self) -> None:
        """"Voltar para os livros" (menu Arquivo e o "voltar" da tela): grava
        antes (sair nao pode custar trabalho) e volta aos cartoes. Desde a
        etapa 3 da obra nao ha mais a tela "O que fazer" no meio (D-002)."""
        self._salvar_agora()
        self._fechar_a_janela_do_automatico()
        projetos.esperar_gravacoes(2.0)
        self.tela_inicio.recarregar()
        self.telas.setCurrentIndex(INICIO)

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
        # o retrato do trabalho que foi para este PDF (D-309: mudou depois,
        # o cartao deixa de dizer pronto - _ver_se_o_pdf_ficou_velho)
        self._trabalho_do_pdf = (self.resumo.pasta, self._marca_do_trabalho())

    def _falhou_no_processamento(self, mensagem: str) -> None:
        """Processamento deu erro: volta para Conferir (o projeto continua
        intacto) e mostra o aviso amigavel."""
        self.telas.setCurrentIndex(CONFERIR)
        self.avisar(mensagem)

    def cancelar(self) -> None:
        """Botão "cancelar" da tela de progresso: pede pra thread parar e volta
        para a area de trabalho. Cancelar o Automatico nao muda nada no livro
        (ele so grava no fim: _aplicar_o_automatico). A medida que ja acabou,
        com o resultado ainda na fila, tambem e marcada como cancelada: o
        resultado e ignorado quando chegar (_automatico_mediu)."""
        if isinstance(self.tarefa, TarefaAutomatico):
            self.tarefa.cancelar()
        elif self.tarefa is not None and self.tarefa.isRunning():
            self.tarefa.cancelar()
        self.telas.setCurrentIndex(CONFERIR if self.projeto is not None else INICIO)

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
        # etapa 3 da obra: a medida do livro por tras (D-284) tambem para
        self._parar_a_medida_ao_abrir()
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
