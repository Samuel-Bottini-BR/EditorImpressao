"""TELA 3 - Conferir: a prévia e todos os ajustes manuais.

Empilhamento da tela, de cima para baixo, sem nenhuma sobreposicao:

    1. cabecalho (titulo, contador de alertas, desfazer/refazer)
    2. barra de abas
    3. área da imagem            <- fica com todo o espaço que sobrar
    4. faixa de explicação
    5. linha de botões
    6. tira de miniaturas
    7. onde salvar
    8. rodape (voltar / confirmar e processar)

Tudo isso num único QVBoxLayout. A faixa e os botões NAO moram dentro das
páginas das abas: elas guardam só a imagem. Foi por isso que a versão anterior
sobrepunha - a página da aba não tinha altura para caber imagem + faixa +
botões, e o Qt acabava empilhando um por cima do outro.

Por isso tambem usamos QTabBar (só a barra) com QStackedWidget, e não
QTabWidget: assim a faixa e os botões ficam de fora, como irmaos.

As abas aparecem conforme o que foi marcado na tela 2. Cada uma edita uma
unidade diferente:

    Onde cortar -> FOLHA do PDF de entrada (a linha da lombada)
    Bordas      -> PAGINA de saida (o retangulo do recorte)
    Endireitar  -> PAGINA de saida (o ângulo)
    Filtro      -> PAGINA de saida (o filtro e a força do preto)

O alerta chama atenção, nunca restringe: todo controle continua disponível em
qualquer página, com ou sem alerta.
"""

from __future__ import annotations

import functools
import traceback

import numpy as np

import atalhos
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from core import analise
from core.filtros import (
    ALGORITMOS_PB,
    MAGICO_PRO,
    MELHORAR,
    NOMES_AMIGAVEIS,
    NOMES_DOS_ALGORITMOS_PB,
    ORIGINAL,
    PRETO_E_BRANCO,
    palavra_do_ajuste,
)
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import Projeto
from registro import registrar_erro
from ui.estilo import AZUL, AZUL_CLARO, LARANJA, LARANJA_CLARO
from ui.tarefas import GerenciadorPrevias
from ui.widgets.barra_opcoes import BarraOpcoes
from ui.widgets.cartao_filtro import CartaoFiltro
from ui.widgets.editor_selecao import (
    FERRAMENTA_RETANGULO,
    ferramenta_da_tecla,
)
from ui.widgets.paineis import ColunaDePaineis
from ui.widgets.trilha_ferramentas import TrilhaFerramentas

from ui.widgets.medidor import Medidor
from ui.widgets.tira_miniaturas import TiraMiniaturas
from ui.widgets.visualizador import (
    MODO_ANGULO,
    MODO_CORTE,
    MODO_RECORTE,
    Visualizador,
)

DPI_PREVIA = 110          # baixo de proposito: a tela precisa abrir em segundos

# Qualidade da prévia, ajustável pelo Samuel (estilo After Effects) nas telas
# de trabalho - troca a resolução usada para renderizar a página nas abas
# Bordas/Endireitar/Marcar. "Rápida" é o valor de sempre (DPI_PREVIA); as
# outras duas custam mais memória/tempo por página, nunca acumulam páginas
# (continua sendo uma só por vez), só deixam ESSA página mais pesada.
QUALIDADES_DA_PREVIA = {"rapida": DPI_PREVIA, "media": 180, "alta": 300}
NOMES_DA_QUALIDADE = {"rapida": "Rápida", "media": "Média", "alta": "Alta"}

ABA_CORTE, ABA_BORDAS, ABA_ANGULO, ABA_FILTRO = "corte", "bordas", "angulo", "filtro"
ABA_MARCAR = "marcar"

TITULOS = {
    ABA_CORTE: "Onde cortar",
    ABA_BORDAS: "Bordas",
    ABA_ANGULO: "Endireitar",
    ABA_MARCAR: "Marcar",
    ABA_FILTRO: "Filtro",
}

# Atalhos que não passam pelo menu (BarraDeMenu já registra os dela sozinha) -
# registrados aqui para a tela de Configurações também poder listá-los e
# remapeá-los. Ver `atalhos.py`.
CHAVE_RECORTE_ESPELHADO = "recorte_espelhado"
CHAVE_RECORTE_PROPORCAO = "recorte_proporcao_travada"
atalhos.registrar(CHAVE_RECORTE_ESPELHADO, "Recorte: espelhado", "M")
atalhos.registrar(CHAVE_RECORTE_PROPORCAO, "Recorte: proporção travada", "T")

CHAVE_NAVEGAR_ANTERIOR = "navegar_anterior"
CHAVE_NAVEGAR_PROXIMA = "navegar_proxima"
CHAVE_MARCAR_CERTO = "marcar_certo"
CHAVE_PROXIMO_ALERTA = "proximo_alerta"
atalhos.registrar(CHAVE_NAVEGAR_ANTERIOR, "Página anterior", "Left")
atalhos.registrar(CHAVE_NAVEGAR_PROXIMA, "Próxima página", "Right")
atalhos.registrar(CHAVE_MARCAR_CERTO, "Marcar como certo e avançar", "Space")
atalhos.registrar(CHAVE_PROXIMO_ALERTA, "Ir para a próxima dúvida", "Tab")

# Nomes de tecla que o QKeySequenceEdit da tela de Configurações devolve para
# essas quatro - não são letras simples, então precisam de uma tradução de
# volta para o Qt.Key que o `tratar_tecla` compara.
_QT_KEY_DAS_TECLAS_DE_NAVEGACAO = {
    "Left": Qt.Key_Left, "Right": Qt.Key_Right,
    "Space": Qt.Key_Space, "Tab": Qt.Key_Tab,
}

# Enquanto o medidor esta sendo arrastado a prévia sai menor: a 110 DPI o
# filtro nao acompanha o dedo. Ao soltar, volta para DPI_PREVIA.
DPI_ARRASTO = 55
ESPERA_ARRASTO_MS = 150   # espera antes de redesenhar, para nao refazer a cada pixel
ESPERA_COMMIT_MS = 450    # fecha a ação quando o medidor foi mexido pelo teclado

# Qual campo da página cada filtro ajusta, e como o medidor se apresenta.
CAMPO_DO_AJUSTE = {
    PRETO_E_BRANCO: "forca_preto",
    MELHORAR: "clareza_melhorar",
    MAGICO_PRO: "intensidade_magico",
}

ROTULOS_DO_AJUSTE = {
    PRETO_E_BRANCO: ("Força do preto", "mais fraco", "mais escuro"),
    MELHORAR: ("Clareza do fundo", "suave", "bem clara"),
    MAGICO_PRO: ("Intensidade", "suave", "bem forte"),
}

CARTOES = [
    (ORIGINAL, "Original", "sem mexer"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado"),
    (MELHORAR, "Melhorar", "mantem a cor"),
    (MAGICO_PRO, "Mágico pro", "cor viva"),
]


def protegido(metodo):
    """Nenhuma acao de botão pode fechar a janela (regra 3.3).

    Qualquer excecao vira aviso em portugues e vai para o arquivo de log. Sem
    isto, um erro dentro de um slot do Qt derruba o programa inteiro e o
    usuario perde o trabalho da tela de conferir.
    """

    @functools.wraps(metodo)
    def envolvido(self, *args, **kwargs):
        try:
            return metodo(self, *args, **kwargs)
        except Exception:  # noqa: BLE001 - e exatamente o ponto
            registrar_erro(f"tela_conferir.{metodo.__name__}", traceback.format_exc())
            self._avisar_problema()
            return None

    return envolvido


class TelaConferir(QWidget):
    voltar = Signal()
    processar = Signal()

    # Alguma coisa do trabalho mudou e precisa ir para o disco. Sai de UM lugar
    # so - o metodo `atualizar`, por onde toda alteracao passa - porque um sinal
    # espalhado por vinte metodos e um sinal que alguem esquece de emitir no
    # vigesimo primeiro, e o trabalho da pessoa some sem ninguem notar.
    trabalho_mudou = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None

        self.indice_folha = 0
        self.indice_pagina = 0

        self._abas_ativas: list[str] = []
        self._carregando = False

        # estado do medidor de ajuste
        self._valor_ao_pegar: int | None = None
        import configuracoes
        self._qualidade_da_previa = configuracoes.ler("qualidade_previa") or "rapida"
        if self._qualidade_da_previa not in QUALIDADES_DA_PREVIA:
            self._qualidade_da_previa = "rapida"
        self._dpi_normal = QUALIDADES_DA_PREVIA[self._qualidade_da_previa]
        self._dpi_atual = self._dpi_normal

        self._agendar = QTimer(self)
        self._agendar.setSingleShot(True)
        self._agendar.timeout.connect(self._redesenhar_previa)

        self._commit = QTimer(self)
        self._commit.setSingleShot(True)
        self._commit.timeout.connect(lambda: self._medidor_soltou(None))

        # Referencias diretas em Python, uma por aba. A versao anterior
        # guardava o widget dentro de setProperty() e o buscava de volta a cada
        # clique; isso devolve um ponteiro que o Python nao mantem vivo e e uma
        # fonte classica de fechamento sem aviso no PySide6.
        self.visualizadores: dict[str, Visualizador] = {}
        self.paginas_de_imagem: dict[str, QWidget] = {}
        self.linhas_de_botoes: dict[str, QWidget] = {}
        self.botoes_de_sugestao: dict[str, QPushButton] = {}
        self.cartoes: dict[str, CartaoFiltro] = {}
        self.botoes_forca: dict[str, QPushButton] = {}
        self._cartoes_cache: dict[str, np.ndarray] = {}
        self._cartoes_cache_chave: tuple | None = None
        self._tira_assinatura: tuple | None = None

        self._montar()

    # ------------------------------------------------------------------
    # montagem
    # ------------------------------------------------------------------

    def _montar(self) -> None:
        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(20, 10, 20, 8)
        camadas.setSpacing(6)

        # O cabecalho e criado mas NAO entra na tela: ver _montar_cabecalho.
        self._cabecalho_escondido = self._montar_cabecalho()

        self.barra_abas = QTabBar()
        self.barra_abas.setExpanding(False)
        self.barra_abas.currentChanged.connect(self._trocou_de_aba)
        camadas.addWidget(self.barra_abas)                   # 2

        # A barra de opcoes: faixa fina que muda conforme a ferramenta na mao.
        # E o que deixa a tela ter nove ferramentas sem entulhar - so os
        # controles da ferramenta ativa aparecem.
        self.barra_opcoes = BarraOpcoes()
        camadas.addWidget(self.barra_opcoes)

        # 3 - a pagina, com a trilha de ferramentas ao lado. E a unica linha
        # com stretch, entao fica com todo o espaco que sobrar.
        meio = QHBoxLayout()
        meio.setContentsMargins(0, 0, 0, 0)
        meio.setSpacing(0)

        self.trilha = TrilhaFerramentas()
        meio.addWidget(self.trilha)

        self.area_imagem = QStackedWidget()
        self.area_imagem.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Minimo pequeno para que a soma de todas as linhas caiba na janela
        # minima de 1000x680. Abaixo disso o Qt sobreporia as faixas.
        self.area_imagem.setMinimumHeight(112)
        meio.addWidget(self.area_imagem, 1)

        # Os quatro paineis, na coluna de 172 px do desenho. Eles recebem o que
        # eram linhas de botoes atravessando a tela.
        self.paineis = ColunaDePaineis()
        meio.addWidget(self.paineis)
        camadas.addLayout(meio, 1)

        self._ligar_paineis()

        self.faixa = QFrame()                                # 4
        self.faixa.setObjectName("faixaInfo")
        self.faixa.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        faixa_camadas = QHBoxLayout(self.faixa)
        faixa_camadas.setContentsMargins(14, 9, 14, 9)
        self.texto_faixa = QLabel("")
        self.texto_faixa.setWordWrap(True)
        faixa_camadas.addWidget(self.texto_faixa, 1)
        camadas.addWidget(self.faixa)

        # A fila de botoes de cada aba. O QStackedWidget reserva, por padrao, a
        # altura da MAIOR pagina dele - entao a aba de Marcar, que agora tem uma
        # linha so, ficava com o buraco da aba de Filtro embaixo. Eram uns
        # 150 px de vazio no meio da tela, tirados justamente da pagina.
        #
        # A conta e feita a mao em _encolher_a_barra_de_botoes: as paginas que
        # nao estao na frente passam a ser ignoradas no calculo, e a pilha
        # ganha a altura da atual. A troca de aba reavalia.
        self.barra_botoes = QStackedWidget()                 # 5
        self.barra_botoes.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        camadas.addWidget(self.barra_botoes)

        # A tira e o botao de processar dividem UMA faixa, como no desenho: a
        # tira a esquerda, "Confirmar e processar" no canto direito. Eram duas
        # faixas empilhadas, e a de baixo custava uns 70 px so para segurar um
        # botao.
        self.tira = TiraMiniaturas("Folhas")                 # 6
        self.tira.selecionada.connect(self._escolher_da_tira)
        self.tira.ampliar_pedido.connect(self._ampliar_miniatura)

        faixa_da_tira = QHBoxLayout()
        faixa_da_tira.setContentsMargins(0, 0, 0, 0)
        faixa_da_tira.setSpacing(10)
        faixa_da_tira.addWidget(self.tira, 1)
        self._montar_rodape()
        faixa_da_tira.addWidget(self.botao_processar)
        camadas.addLayout(faixa_da_tira)


    def _ligar_paineis(self) -> None:
        """Cada painel manda no mesmo lugar em que o botao antigo mandava."""
        painel = self.paineis
        painel.para_revisar.ir_para.connect(self.ir_para_pagina)
        painel.marcar_como.escolheu.connect(self._escolher_tipo_de_marcacao)
        painel.filtro_da_pagina.filtro_do_pedaco.connect(
            self._escolher_filtro_da_regiao)
        painel.filtro_da_pagina.medidor_mudou.connect(self._medidor_soltou)
        painel.historico.voltar_para.connect(self._voltar_no_historico)

    def _voltar_no_historico(self, posicao: int) -> None:
        """Volta o trabalho ate a acao clicada no painel Historico."""
        if self.acoes is None or self.projeto is None:
            return
        self.acoes.voltar_para(self.projeto, posicao)
        if self.previas is not None:
            self.previas.invalidar()
        self.atualizar()

    def _ligar_ferramentas(self) -> None:
        """A trilha manda na barra de opcoes e no editor, nesta ordem.

        Um lugar so decide qual ferramenta esta na mao. Antes havia uma fila de
        botoes que sabia disso e o editor que sabia de novo, e os dois saiam do
        ar quando alguem esquecia de avisar o outro.
        """
        self.trilha.escolhida.connect(self.barra_opcoes.definir_ferramenta)
        self.trilha.escolhida.connect(self.editor_selecao.definir_ferramenta)

        opcoes, editor = self.barra_opcoes, self.editor_selecao
        opcoes.operacao_mudou.connect(editor.definir_operacao)
        opcoes.tolerancia_mudou.connect(
            lambda valor: setattr(editor, "tolerancia", int(valor)))
        opcoes.espessura_mudou.connect(
            lambda valor: setattr(editor, "espessura", float(valor)))
        opcoes.zoom_mudou.connect(editor.definir_zoom)
        opcoes.ajustar_pedido.connect(editor.ajustar_a_tela)

        self.trilha.definir_ferramenta(FERRAMENTA_RETANGULO)
        self.barra_opcoes.definir_ferramenta(FERRAMENTA_RETANGULO)

    def escolher_ferramenta(self, ferramenta: str) -> None:
        """Ponto unico de troca - usado tambem pelos atalhos de letra."""
        self.trilha.definir_ferramenta(ferramenta)
        self.barra_opcoes.definir_ferramenta(ferramenta)
        self.editor_selecao.definir_ferramenta(ferramenta)

    def _montar_cabecalho(self) -> QWidget:
        """Os controles do antigo cabecalho, que agora vivem em outros lugares.

        A FAIXA some da tela - custava 42 px para dizer o que a barra de menu e
        a propria tela ja dizem. Os controles nao somem:

          contador de alertas    virou o painel "Para revisar"
          Desfazer / Refazer     estao no menu Editar e no painel Historico
          observacoes do livro   vao para a faixa de estado

        Eles continuam sendo CRIADOS aqui, e escondidos. O resto da tela ainda
        escreve neles - o contador, por exemplo, e atualizado a cada pagina - e
        deixar de cria-los quebraria isso em silencio: o erro viraria uma caixa
        modal, e numa bateria de testes uma caixa modal trava tudo. Foi
        exatamente o que aconteceu quando eu simplesmente tirei a chamada.
        """
        caixa = QWidget(self)
        caixa.setVisible(False)
        topo = QHBoxLayout(caixa)
        titulo = QLabel("Confira antes de processar")
        titulo.setObjectName("secao")
        topo.addWidget(titulo)

        # Os fatos do livro inteiro ficam aqui, ditos uma vez, em vez de
        # marcarem todas as páginas e afogarem o contador de alertas.
        self.rotulo_observacoes = QLabel("")
        self.rotulo_observacoes.setObjectName("fraco")
        self.rotulo_observacoes.setVisible(False)
        topo.addWidget(self.rotulo_observacoes)

        topo.addStretch()

        self.botao_alertas = QPushButton("tudo certo")
        self.botao_alertas.setObjectName("contadorAlerta")
        _ligar(self.botao_alertas, self._ir_para_proximo_alerta)
        topo.addWidget(self.botao_alertas)

        self.botao_desfazer = QPushButton("Desfazer")
        _ligar(self.botao_desfazer, self.desfazer)
        topo.addWidget(self.botao_desfazer)

        self.botao_refazer = QPushButton("Refazer")
        _ligar(self.botao_refazer, self.refazer)
        topo.addWidget(self.botao_refazer)
        return caixa

    def _montar_rodape(self) -> QVBoxLayout:
        """O rodape encolheu a uma linha, e ela mora ao lado da tira.

        A linha de atalhos saiu: eram 25 px repetindo o que Ajuda ja lista, e a
        lista de Ajuda sai dos proprios menus, entao nao diverge. "voltar" saiu
        tambem - esta em Arquivo. Sobra "Confirmar e processar", que o desenho
        poe no canto direito da faixa da tira.
        """
        fora = QVBoxLayout()
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)

        self.botao_processar = QPushButton("Confirmar e processar")
        self.botao_processar.setObjectName("primario")
        _ligar(self.botao_processar, self._pedir_processamento)
        return fora

    # --- paginas de imagem e linhas de botoes -----------------------------

    def _area_de_visualizador(self, aba: str, modo: str) -> Visualizador:
        """Uma página da área de imagem: setas nas laterais e a prévia no meio."""
        pagina = QWidget()
        linha = QHBoxLayout(pagina)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)

        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        visualizador = Visualizador()
        visualizador.definir_modo(modo)
        visualizador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        linha.addWidget(visualizador, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)

        visualizador.ampliar_pedido.connect(self.ampliar)
        self.visualizadores[aba] = visualizador
        self.paginas_de_imagem[aba] = pagina
        return visualizador

    def _linha_de_botoes(self, aba: str) -> QHBoxLayout:
        widget = QWidget()
        linha = QHBoxLayout(widget)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(8)
        self.linhas_de_botoes[aba] = widget
        return linha

    def _montar_aba_corte(self) -> None:
        vis = self._area_de_visualizador(ABA_CORTE, MODO_CORTE)
        vis.corte_movido.connect(self._mover_corte)

        linha = self._linha_de_botoes(ABA_CORTE)
        _botao("está certo", linha, self._marcar_revisada)
        self.botao_nao_dividir = _botao("não dividir esta", linha, self._alternar_dividir)
        _botao("girar", linha, self._girar)
        _botao("usar em todas", linha, self._corte_em_todas)
        linha.addStretch()
        self.botoes_de_sugestao[ABA_CORTE] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _montar_aba_bordas(self) -> None:
        vis = self._area_de_visualizador(ABA_BORDAS, MODO_RECORTE)
        vis.recorte_movido.connect(self._mover_recorte)
        vis.conteudo_movido.connect(self._mover_conteudo)

        linha = self._linha_de_botoes(ABA_BORDAS)
        _botao("está certo", linha, self._marcar_revisada)
        _botao("não cortar esta", linha, self._sem_recorte)
        _botao("voltar ao automático", linha, self._recorte_automatico)
        _botao("usar em todas", linha, self._recorte_em_todas)
        _botao("tamanho...", linha, self._escolher_tamanho_da_folha)

        self.botao_espelhado = _botao("Espelhado", linha, self._alternar_espelhado)
        self.botao_espelhado.setCheckable(True)
        self.botao_espelhado.setToolTip(
            f"Espelhado  ({atalhos.tecla_atual(CHAVE_RECORTE_ESPELHADO)})")

        self.botao_proporcao_travada = _botao(
            "Proporção travada", linha, self._alternar_proporcao_travada
        )
        self.botao_proporcao_travada.setCheckable(True)
        self.botao_proporcao_travada.setToolTip(
            f"Proporção travada  ({atalhos.tecla_atual(CHAVE_RECORTE_PROPORCAO)})")

        # Fase 2 (aprovada pelo Samuel em 22/09/2026): mover o conteúdo
        # dentro da folha - só faz sentido quando há uma folha maior que o
        # recorte escolhida (`_atualizar_previa` habilita/desabilita este
        # botão, ver `_conferir_tamanho_da_folha` / ABA_BORDAS).
        self.botao_mover_conteudo = _botao(
            "Mover conteúdo", linha, self._alternar_mover_conteudo
        )
        self.botao_mover_conteudo.setCheckable(True)
        self.botao_mover_conteudo.setEnabled(False)
        self.botao_mover_conteudo.setToolTip(
            "Arrastar a página dentro da folha escolhida (aba \"tamanho...\"). "
            "Só disponível quando a folha é maior que o recorte."
        )

        linha.addStretch()

        linha.addWidget(QLabel("Qualidade:"))
        seletor_qualidade = QComboBox()
        for chave, nome in NOMES_DA_QUALIDADE.items():
            seletor_qualidade.addItem(nome, chave)
        seletor_qualidade.setCurrentIndex(
            seletor_qualidade.findData(self._qualidade_da_previa))
        seletor_qualidade.setToolTip(
            "Rápida: abre logo. Alta: mais nítida no zoom, demora mais por página."
        )
        seletor_qualidade.currentIndexChanged.connect(
            lambda i: self._mudar_qualidade_da_previa(seletor_qualidade.itemData(i)))
        linha.addWidget(seletor_qualidade)
        self.botoes_de_sugestao[ABA_BORDAS] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _escolher_tamanho_da_folha(self) -> None:
        """Problema 1, opção A: digitar o tamanho final em vez de arrastar.

        Item 2/4 do teste do Boécio (seção 3a do plano): este botão SÓ decide
        o tamanho da FOLHA (`ConfigPagina.tamanho_folha_cm`) - nunca mais toca
        em `recorte`. Antes ele chamava `recorte_para_tamanho_cm` e
        `_mover_recorte`, o que substituía e recentralizava o corte que o
        usuário já tinha feito à mão (o bug relatado). O recorte serve para
        DUAS coisas agora, sem se atropelar: recortar a imagem original, e
        (separadamente) posicionar-se dentro do tamanho de folha escolhido
        aqui - ver `core/folha.py::compor_na_folha`.
        """
        from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha
        from core.folha import medidas_do_recorte_em_cm

        if not self._pronta() or self.projeto is None:
            return
        vis = self.visualizadores[ABA_BORDAS]
        largura_px, altura_px = vis.tamanho_da_pagina_px()
        if largura_px == 0:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        dpi = vis.dpi_atual()

        atual = medidas_do_recorte_em_cm(
            pagina.recorte or (0.0, 0.0, 1.0, 1.0), largura_px, altura_px, dpi)

        dialogo = DialogoTamanhoDaFolha(
            atual["largura_final"], atual["altura_final"],
            tamanho_atual=pagina.tamanho_folha_cm, parent=self,
        )

        if dialogo.exec() != DialogoTamanhoDaFolha.Accepted:
            return

        self._mudar_tamanho_da_folha(dialogo.tamanho_escolhido())

    @protegido
    def _mudar_tamanho_da_folha(self, tamanho_cm: tuple[float, float]) -> None:
        """Registra `tamanho_folha_cm` no histórico - mesmo padrão de
        `_mover_corte`/`_mover_angulo` (`@protegido` + `_registrar`)."""
        arredondado = (round(tamanho_cm[0], 2), round(tamanho_cm[1], 2))
        self._registrar(
            "tamanho_folha", "pagina", [self.indice_pagina],
            {"tamanho_folha_cm": list(arredondado)},
            f"Tamanho da folha da página {self.indice_pagina + 1}: "
            f"{arredondado[0]:.1f} × {arredondado[1]:.1f} cm",
        )

    def _atualizar_previa_para_recorte(self, vis, pagina) -> None:
        """A aba Bordas, fora do modo "Mover conteúdo": mostra a folha girada
        e dividida, mas NUNCA cortada - o recorte é só um retângulo desenhado
        por cima, sempre em fração da MESMA imagem estável.

        Bug real achado ao vivo (23/09/2026, Samuel: "quando eu diminuo a
        linha verde ele corta a própria folha e o corte vai pra frente
        sozinho"): antes, esta aba mostrava a prévia JÁ cortada por
        `pagina.recorte` (a mesma que `_atualizar_previa_composta` usa) - o
        retângulo do recorte era desenhado como fração de uma imagem que já
        era um recorte, e cada atualização (ao soltar o mouse) reaplicava a
        fração em cima do resultado anterior, comprimindo o corte sozinho a
        cada vez. Ver `core.pipeline.preparar_para_recorte`.
        """
        img = self.previas.pegar_para_recorte(self.indice_pagina, self._dpi_atual)
        vis.definir_imagem(img)
        if img is not None:
            vis.definir_composicao((0.0, 0.0, 1.0, 1.0), (img.shape[1], img.shape[0]))

    def _atualizar_previa_composta(self, vis, pagina, img) -> None:
        """Decisão 3 do plano (passo 8, o item de maior risco): a aba Bordas
        mostra a página JÁ COMPOSTA na folha escolhida (recorte + margem
        branca de verdade), ao vivo - não só um contorno decorativo.

        `img` é o conteúdo (o recorte, já processado - mesma imagem que
        sempre foi mostrada aqui). `core.folha.compor_na_folha` é a MESMA
        função que `core/pipeline.py::processar` usa na exportação final,
        então a prévia sai idêntica ao que vai para o arquivo. Quando não
        cabe (rede de segurança) ou não há folha escolhida, devolve `img`
        sem alteração - detectado comparando o tamanho antes/depois, sem
        duplicar a lógica de "cabe" que já mora em `compor_na_folha`.

        `vis.definir_composicao(...)` ensina ao widget onde o conteúdo fica
        dentro do canvas maior, para o retângulo do recorte e o arrasto do
        mouse continuarem certos (`Visualizador._area_do_conteudo`).
        """
        from core.folha import compor_na_folha, conteudo_como_retangulo

        if img is None:
            vis.definir_imagem(None)
            return

        composto = compor_na_folha(
            img, pagina.tamanho_folha_cm, self._dpi_atual,
            escala=pagina.conteudo_escala, deslocamento=pagina.conteudo_deslocamento,
        )
        vis.definir_imagem(composto)

        tamanho_conteudo_px = (img.shape[1], img.shape[0])
        if composto.shape[:2] == img.shape[:2]:
            retangulo_conteudo = (0.0, 0.0, 1.0, 1.0)
        else:
            retangulo_conteudo = conteudo_como_retangulo(
                pagina.conteudo_escala, pagina.conteudo_deslocamento,
                pagina.tamanho_folha_cm, tamanho_conteudo_px, self._dpi_atual,
            )
        vis.definir_composicao(retangulo_conteudo, tamanho_conteudo_px)

    def _conferir_tamanho_da_folha(self, pagina, vis) -> None:
        """Decisão 2 do plano: se o recorte crescer depois de já haver uma
        folha escolhida e ela ficar pequena demais, avisa DE FORMA VISÍVEL
        E PERSISTENTE na tela (não só no instante do diálogo) - mesmo padrão
        de `_conferir_qualidade_do_preto_e_branco` (alerta computado ao vivo,
        comparando com o estado atual da página).
        """
        from core.analise import FOLHA_MENOR_QUE_O_RECORTE
        from core.folha import medidas_do_recorte_em_cm, tamanho_da_folha_cabe

        largura_px, altura_px = vis.tamanho_da_pagina_px()
        tinha = FOLHA_MENOR_QUE_O_RECORTE in pagina.alertas
        pagina.alertas = [a for a in pagina.alertas if a != FOLHA_MENOR_QUE_O_RECORTE]

        cabe = True
        if pagina.tamanho_folha_cm is not None and largura_px > 0 and altura_px > 0:
            medidas = medidas_do_recorte_em_cm(
                pagina.recorte or (0.0, 0.0, 1.0, 1.0), largura_px, altura_px, vis.dpi_atual())
            cabe = tamanho_da_folha_cabe(
                pagina.tamanho_folha_cm,
                (medidas["largura_final"], medidas["altura_final"]),
            )
            if not cabe:
                pagina.alertas.append(FOLHA_MENOR_QUE_O_RECORTE)

        if tinha != (not cabe):
            self._atualizar_faixa()
            self._atualizar_tira()
            self._atualizar_contador()

    def _mudar_qualidade_da_previa(self, nome_qualidade: str) -> None:
        """Troca a resolução da prévia (estilo After Effects: Rápida/Média/Alta).

        Fica salvo (configuracoes.py) e vale para a próxima vez que o
        programa abrir também.
        """
        import configuracoes

        if nome_qualidade not in QUALIDADES_DA_PREVIA:
            return
        self._qualidade_da_previa = nome_qualidade
        self._dpi_normal = QUALIDADES_DA_PREVIA[nome_qualidade]
        self._dpi_atual = self._dpi_normal
        configuracoes.escrever("qualidade_previa", nome_qualidade)
        self.atualizar()

    def _alternar_espelhado(self) -> None:
        if self.botao_espelhado.isChecked():
            self.botao_proporcao_travada.setChecked(False)
        self._atualizar_modo_arraste_recorte()

    def _alternar_proporcao_travada(self) -> None:
        if self.botao_proporcao_travada.isChecked():
            self.botao_espelhado.setChecked(False)
        self._atualizar_modo_arraste_recorte()

    def _atualizar_modo_arraste_recorte(self) -> None:
        from ui.widgets.visualizador import (
            RECORTE_ESPELHADO,
            RECORTE_LIVRE,
            RECORTE_PROPORCAO,
        )

        if self.botao_espelhado.isChecked():
            modo = RECORTE_ESPELHADO
        elif self.botao_proporcao_travada.isChecked():
            modo = RECORTE_PROPORCAO
        else:
            modo = RECORTE_LIVRE
        self.visualizadores[ABA_BORDAS].definir_modo_arraste_recorte(modo)

    def _alternar_mover_conteudo(self) -> None:
        """Fase 2: troca o visualizador entre editar o RECORTE (padrão) e
        arrastar o CONTEÚDO dentro da folha - são exclusivos (o widget só
        tem um `modo` por vez)."""
        from ui.widgets.visualizador import MODO_CONTEUDO, MODO_RECORTE

        vis = self.visualizadores[ABA_BORDAS]
        if self.botao_mover_conteudo.isChecked():
            vis.definir_modo(MODO_CONTEUDO)
        else:
            vis.definir_modo(MODO_RECORTE)
        # As duas telas usam prévias diferentes (composta vs. só girada/
        # dividida, ver `_atualizar_previa_para_recorte`) - sem isto, a tela
        # só troca na próxima atualização natural, mostrando por um instante
        # o retângulo desenhado sobre a imagem errada.
        self.atualizar()

    def _montar_aba_angulo(self) -> None:
        vis = self._area_de_visualizador(ABA_ANGULO, MODO_ANGULO)
        vis.angulo_movido.connect(self._mover_angulo)

        linha = self._linha_de_botoes(ABA_ANGULO)
        _botao("está certo", linha, self._marcar_revisada)
        _botao("não endireitar esta", linha, self._angulo_zero)
        _botao("voltar ao automático", linha, self._angulo_automatico)
        linha.addStretch()
        self.botoes_de_sugestao[ABA_ANGULO] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _montar_aba_marcar(self) -> None:
        """A aba de marcar a mao onde estao gravura, letra e papel.

        O detector acerta a maioria das paginas. Esta aba existe para as que ele
        erra: sem ela, nao havia como consertar.
        """
        from core.selecao import GRAVURA, LETRA, PAPEL, SOMAR, SUBTRAIR
        from ui.widgets.editor_selecao import (
            FERRAMENTA_ELIPSE,
            FERRAMENTA_LACO,
            FERRAMENTA_PINCEL,
            FERRAMENTA_POLIGONO,
            FERRAMENTA_RETANGULO,
            FERRAMENTA_COR,
            FERRAMENTA_VARINHA,
            NOMES_DAS_FERRAMENTAS,
            EditorSelecao,
        )

        pagina = QWidget()
        linha = QHBoxLayout(pagina)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)

        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        self.editor_selecao = EditorSelecao()
        self.editor_selecao.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editor_selecao.selecao_mudou.connect(self._selecao_mudou)
        self.editor_selecao.aviso.connect(self._mostrar_aviso_da_marcacao)
        linha.addWidget(self.editor_selecao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)
        self.paginas_de_imagem[ABA_MARCAR] = pagina

        # --- os botoes ---
        #
        # Tres linhas sairam daqui na etapa 3, e nao se perderam:
        #
        #   Marcar como               painel "Marcar como", um embaixo do outro
        #   Filtro so neste pedaco    painel "Filtro da pagina"
        #   desfazer, procurar de     menu Marcar e menu Editar, ja na etapa 1
        #   novo, limpar tudo,
        #   deixar a folha em branco
        #
        # Cada uma custava altura da pagina, e a pagina e o que precisa ser
        # olhado. Sobra so o aviso do que foi marcado, que e uma frase e nao um
        # controle.
        painel = QWidget()
        fora = QVBoxLayout(painel)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(4)

        # Problema 2 do plano (redesenho do fluxo): a detecção automática não
        # roda mais sozinha ao abrir esta aba - o Samuel pede quando quiser,
        # aqui ou pelo menu Marcar -> "Procurar de novo" (mesma ação).
        linha_detectar = QHBoxLayout()
        _botao("detectar automaticamente", linha_detectar, self._detectar_de_novo)
        # Fase 3b do plano: mesma granularidade que corte/bordas/filtro já
        # tinham ("usar em todas"/"só nas próximas") - faltava só aqui.
        _botao("usar em todas", linha_detectar, self._marcacao_em_todas)
        _botao("só nas próximas", linha_detectar, self._marcacao_nas_proximas)
        linha_detectar.addStretch()
        fora.addLayout(linha_detectar)

        self.aviso_marcacao = QLabel("")
        self.aviso_marcacao.setObjectName("dica")
        fora.addWidget(self.aviso_marcacao)

        self.linhas_de_botoes[ABA_MARCAR] = painel

    # --- acoes da aba de marcar -------------------------------------------

    def _escolher_tipo_de_marcacao(self, tipo: str) -> None:
        """Quem mostra o estado agora e o painel "Marcar como"."""
        self.editor_selecao.definir_tipo(tipo)
        self.paineis.marcar_como.tipo = tipo
        self.paineis.marcar_como._montar()

    def _escolher_operacao(self, operacao: str) -> None:
        """Somar ou tirar. Quem mostra o estado agora e a barra de opcoes."""
        self.editor_selecao.definir_operacao(operacao)
        self.barra_opcoes._escolher_modo(operacao, avisar=False)

    def _escolher_ferramenta(self, ferramenta: str) -> None:
        """Mantido pelo nome antigo; passa pelo ponto unico de troca."""
        self.escolher_ferramenta(ferramenta)

    def _escolher_filtro_da_regiao(self, filtro: str) -> None:
        """Que filtro vale so no que for marcado daqui em diante.

        Quem mostra o estado agora e o painel "Filtro da pagina".
        """
        self.editor_selecao.definir_filtro_da_regiao(filtro)

    def _mostrar_aviso_da_marcacao(self, texto: str) -> None:
        if hasattr(self, "aviso_marcacao"):
            self.aviso_marcacao.setText(texto)

    def _pagina_marcada(self):
        """A pagina que a aba de marcar esta editando, ou None."""
        if self.projeto is None or not self.projeto.paginas:
            return None
        if not 0 <= self.indice_pagina < len(self.projeto.paginas):
            return None
        return self.projeto.paginas[self.indice_pagina]

    def _selecao_mudou(self) -> None:
        """Grava a marcacao na pagina e joga fora a previa, que ficou velha."""
        pagina = self._pagina_marcada()
        if pagina is None:
            return
        pagina.guardar_selecao(self.editor_selecao.selecao)
        self._mostrar_aviso_da_marcacao(
            self.editor_selecao.selecao.resumo_em_portugues())
        if self.previas is not None:
            self.previas.invalidar(self.indice_pagina)
        # A marcacao nao passa por `atualizar` - ela nao mexe na tira nem no
        # contador. Mas mexe no TRABALHO, e por isso avisa daqui.
        self.trabalho_mudou.emit()

    def _desfazer_marcacao(self) -> None:
        self.editor_selecao.desfazer()
        self._selecao_mudou()

    def _limpar_marcacao(self) -> None:
        from core.selecao import Selecao

        if self._pagina_marcada() is None:
            return
        self.editor_selecao.definir_selecao(Selecao())
        self._selecao_mudou()
        self._mostrar_aviso_da_marcacao(
            "Tirei tudo. O filtro volta a tratar a folha inteira igual.")

    def _folha_em_branco(self) -> None:
        """Manda a folha inteira sair branca, seja capa ou pagina escrita.

        E o mesmo caminho da marcacao a mao: marcar a folha inteira como PAPEL.
        O filtro entende folha inteira marcada como papel como "quero a folha em
        branco", e nao como "aqui e fundo" - ver FOLHA_INTEIRA_EM_BRANCO. Assim
        nao ha um segundo jeito de dizer a mesma coisa dentro do programa, e o
        desfazer funciona igual ao das outras marcacoes.
        """
        from core.selecao import MAO, PAPEL, RETANGULO, Regiao, Selecao

        if self._pagina_marcada() is None:
            return
        folha = Selecao()
        folha.acrescentar(Regiao(tipo=PAPEL, forma=RETANGULO,
                                 pontos=[(0.0, 0.0), (1.0, 1.0)], origem=MAO))
        self.editor_selecao.definir_selecao(folha)
        self._selecao_mudou()
        self._mostrar_aviso_da_marcacao(
            "Esta folha vai sair em branco. Para voltar atrás, desfazer.")

    def _detectar_de_novo(self) -> None:
        """Roda a deteccao outra vez, SEM apagar o que foi feito a mao.

        E o ponto de as tres formas de marcar viverem na mesma lista: da para
        pedir a maquina de novo sem perder a correcao da pessoa.
        """
        from core.detectar_regioes import detectar

        pagina = self._pagina_marcada()
        if pagina is None:
            return

        quantas = self.editor_selecao.limpar_o_que_a_maquina_marcou()
        img = self.previas.pegar(self.indice_pagina, self._dpi_atual) \
            if self.previas is not None else None
        if img is None:
            self._mostrar_aviso_da_marcacao("Espere a página terminar de carregar.")
            return

        try:
            nova = detectar(img)
        except Exception:  # noqa: BLE001 - sem deteccao a marcacao a mao continua
            self._mostrar_aviso_da_marcacao("Não consegui procurar nesta página.")
            return

        for regiao in nova.regioes:
            self.editor_selecao.selecao.acrescentar(regiao)
        pagina.guardar_selecao(self.editor_selecao.selecao)
        self.editor_selecao.update()
        if self.previas is not None:
            self.previas.invalidar(self.indice_pagina)

        achou = len(nova)
        mantidas = "" if not quantas else f" Mantive as suas {quantas and ''}"
        del mantidas
        self._mostrar_aviso_da_marcacao(
            f"Achei {achou} áreas. O que você marcou à mão continua aí."
            if achou else "Não achei nada novo nesta página.")

    # Fase 3b do plano "corrigir bugs do teste do Boécio": faltava aqui o
    # "usar em todas / só nesta" que já existia para corte
    # (`_corte_em_todas`), recorte/bordas (`_recorte_em_todas`) e filtro
    # (`_filtro_em_todas`/`_filtro_nas_proximas`). O "resultado da detecção
    # automática" copiado é a MARCAÇÃO já computada nesta página (detecção +
    # qualquer correção manual, `ConfigPagina.selecao`) - mesmo padrão dos
    # irmãos acima: copia um valor já decidido para as outras páginas, não
    # roda `detectar()` de novo em cada uma (isso exigiria rasterizar e
    # processar o livro inteiro de forma síncrona na interface - a regra do
    # projeto "nenhum processamento pesado trava a interface" não permite
    # isso sem uma tarefa em segundo plano própria, fora do escopo desta
    # entrega; rodar a detecção de verdade página por página continua sendo
    # o botão "detectar automaticamente" de cima).
    @protegido
    def _marcacao_em_todas(self) -> None:
        import copy

        pagina = self._pagina_marcada()
        if pagina is None or not pagina.selecao:
            # Uma marcacao VAZIA copiada para todas apagaria sem querer o
            # trabalho de outras paginas - mesmo cuidado de `_limpar_marcacao`
            # so valer na pagina atual, nunca em lote.
            self._mostrar_aviso_da_marcacao(
                "Marque ou detecte algo nesta página antes de usar em todas.")
            return
        assert self.projeto is not None
        indices = [p.indice for p in self.projeto.paginas]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"selecao": copy.deepcopy(pagina.selecao)},
            f"Marcação da página {self.indice_pagina + 1} em todas as {len(indices)} páginas",
        )

    @protegido
    def _marcacao_nas_proximas(self) -> None:
        import copy

        pagina = self._pagina_marcada()
        if pagina is None or not pagina.selecao:
            self._mostrar_aviso_da_marcacao(
                "Marque ou detecte algo nesta página antes de aplicar nas próximas.")
            return
        assert self.projeto is not None
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"selecao": copy.deepcopy(pagina.selecao)},
            f"Marcação da página {self.indice_pagina + 1} em diante ({len(indices)} páginas)",
        )

    def _montar_aba_filtro(self) -> None:
        pagina = QWidget()
        camadas = QVBoxLayout(pagina)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(6)

        explicacao = QLabel("A mesma página nos quatro filtros - clique no que preferir")
        explicacao.setObjectName("fraco")
        camadas.addWidget(explicacao)

        linha = QHBoxLayout()
        linha.setSpacing(6)
        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        for chave, nome, explica in CARTOES:
            cartao = CartaoFiltro(chave, nome, explica)
            cartao.escolhido.connect(self._escolher_filtro)
            cartao.ampliar_pedido.connect(self._ampliar_com_filtro)
            self.cartoes[chave] = cartao
            linha.addWidget(cartao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)
        camadas.addLayout(linha, 1)

        self.paginas_de_imagem[ABA_FILTRO] = pagina

        # Abaixo da faixa vem AJUSTE (o que muda a página) e, separado dele,
        # APLICAR EM (o que decide onde a mudança vale). Sao coisas diferentes:
        # misturar as duas na mesma linha era o que confundia.
        painel = QWidget()
        fora = QVBoxLayout(painel)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(6)

        self.bloco_ajuste = QFrame()
        self.bloco_ajuste.setObjectName("cartao")
        dentro = QVBoxLayout(self.bloco_ajuste)
        dentro.setContentsMargins(12, 7, 12, 7)
        dentro.setSpacing(2)

        rotulo_bloco = QLabel("AJUSTE")
        rotulo_bloco.setObjectName("rotuloBloco")
        dentro.addWidget(rotulo_bloco)

        self.medidor = Medidor("Força do preto", "mais fraco", "mais escuro")
        self.medidor.arrastando.connect(self._medidor_arrastando)
        self.medidor.soltou.connect(self._medidor_soltou)
        self.medidor.barra.sliderPressed.connect(self._medidor_pegou)
        dentro.addWidget(self.medidor)

        # Problema 5 do plano: só aparece com o Preto e branco escolhido (ver
        # _configurar_medidor). "Automático" é o padrão - o programa decide
        # pela espessura do traço desta página.
        linha_algoritmo = QHBoxLayout()
        linha_algoritmo.addWidget(QLabel("Algoritmo:"))
        self.seletor_algoritmo_pb = QComboBox()
        self.seletor_algoritmo_pb.addItem("Automático", "auto")
        for chave in ALGORITMOS_PB:
            self.seletor_algoritmo_pb.addItem(NOMES_DOS_ALGORITMOS_PB[chave], chave)
        self.seletor_algoritmo_pb.currentIndexChanged.connect(self._mudar_algoritmo_pb)
        linha_algoritmo.addWidget(self.seletor_algoritmo_pb, 1)
        self.caixa_despeckle = QCheckBox("limpar poeirinha")
        self.caixa_despeckle.setToolTip(
            "Remove manchas pretas pequenas demais pra ser letra. "
            "Ligado é o comportamento de sempre."
        )
        self.caixa_despeckle.toggled.connect(self._mudar_despeckle)
        linha_algoritmo.addWidget(self.caixa_despeckle)
        dentro.addLayout(linha_algoritmo)

        fora.addWidget(self.bloco_ajuste)

        linha_botoes = QHBoxLayout()
        linha_botoes.setSpacing(8)
        rotulo_aplicar = QLabel("Aplicar em:")
        rotulo_aplicar.setStyleSheet("font-weight: 600;")
        linha_botoes.addWidget(rotulo_aplicar)

        _botao("só nesta", linha_botoes, self._marcar_revisada, "acaoPrimaria")
        _botao("todas", linha_botoes, self._filtro_em_todas)
        _botao("só nas próximas", linha_botoes, self._filtro_nas_proximas)

        # Apagar e destrutivo: fica de outro lado do separador, para ninguem
        # acertar nele querendo clicar em "só nas próximas".
        separador = QFrame()
        separador.setFrameShape(QFrame.VLine)
        separador.setStyleSheet("color: #d1d5db; margin: 0 8px;")
        linha_botoes.addWidget(separador)
        self.botao_apagar = _botao(
            "apagar página", linha_botoes, self.apagar_pagina, "destrutivo"
        )

        linha_botoes.addStretch()
        self.botoes_de_sugestao[ABA_FILTRO] = _botao(
            "", linha_botoes, self._aplicar_sugestao, "sugestao"
        )
        fora.addLayout(linha_botoes)

        self.linhas_de_botoes[ABA_FILTRO] = painel

    # ------------------------------------------------------------------
    # carga
    # ------------------------------------------------------------------

    def carregar(self, projeto: Projeto, acoes: HistoricoAcoes,
                 previas: GerenciadorPrevias) -> None:
        self._carregando = True
        try:
            self.projeto = projeto
            self.acoes = acoes
            self.previas = previas
            self.previas.pronta.connect(self._previa_chegou)
            self.previas.cartoes_prontos.connect(self._cartoes_prontos)
            self._cartoes_cache = {}
            self._cartoes_cache_chave = None
            self._tira_assinatura = None

            self.indice_folha = 0
            self.indice_pagina = 0

            self._limpar_abas()

            if projeto.dividir_folhas:
                self._montar_aba_corte()
                self._abas_ativas.append(ABA_CORTE)
            if projeto.cortar_bordas:
                self._montar_aba_bordas()
                self._abas_ativas.append(ABA_BORDAS)
            if projeto.endireitar:
                self._montar_aba_angulo()
                self._abas_ativas.append(ABA_ANGULO)
            if projeto.limpar and projeto.detectar_regioes:
                self._montar_aba_marcar()
                self._abas_ativas.append(ABA_MARCAR)
                # A trilha e a barra so podem ser ligadas depois que o editor
                # existe - ele nasce aqui, e nao no construtor da tela.
                self._ligar_ferramentas()
            if projeto.limpar or not self._abas_ativas:
                self._montar_aba_filtro()
                self._abas_ativas.append(ABA_FILTRO)

            for aba in self._abas_ativas:
                self.barra_abas.addTab(TITULOS[aba])
                self.area_imagem.addWidget(self.paginas_de_imagem[aba])
                self.barra_botoes.addWidget(self.linhas_de_botoes[aba])

            self.barra_abas.setCurrentIndex(0)
            self._encolher_a_barra_de_botoes()
        finally:
            self._carregando = False

        self._montar_tira()
        self.atualizar()

    def _limpar_abas(self) -> None:
        """Descarta as abas de um projeto anterior antes de montar as novas."""
        while self.barra_abas.count():
            self.barra_abas.removeTab(0)
        for pilha in (self.area_imagem, self.barra_botoes):
            while pilha.count():
                widget = pilha.widget(0)
                pilha.removeWidget(widget)
                widget.deleteLater()

        self._abas_ativas.clear()
        self.visualizadores.clear()
        self.paginas_de_imagem.clear()
        self.linhas_de_botoes.clear()
        self.botoes_de_sugestao.clear()
        self.cartoes.clear()
        self.botoes_forca.clear()

    def _montar_tira(self) -> None:
        """Recria a tira de miniaturas - mas só quando o conjunto de
        páginas/folhas muda de verdade.

        Remontar refaz a miniatura do livro inteiro do zero, reabrindo o PDF
        numa thread nova - achado ao vivo: se isso acontece enquanto outra
        tarefa de fundo já está lendo o mesmo arquivo, o MuPDF pode travar o
        programa inteiro (regra 3.2). Só trocar de aba, o caso comum, não
        muda nem a quantidade nem o mapeamento - remontar aí é caro à toa.
        """
        if self.projeto is None:
            return
        if self.aba_atual == ABA_CORTE:
            titulo = "Folhas - as laranjas eu não tive certeza"
            quantidade = len(self.projeto.folhas)
            folha_de = {i: i for i in range(len(self.projeto.folhas))}
            corte_de = None
        else:
            titulo = "Páginas - as laranjas eu não tive certeza"
            quantidade = len(self.projeto.paginas)
            folha_de = {p.indice: p.folha for p in self.projeto.paginas}
            corte_de = {
                p.indice: (p.metade, self.projeto.folhas[p.folha].posicao_corte)
                for p in self.projeto.paginas
            }

        self.tira.definir_titulo(titulo)

        assinatura = (
            quantidade,
            tuple(sorted(folha_de.items())),
            tuple(sorted(corte_de.items())) if corte_de is not None else None,
        )
        if assinatura == self._tira_assinatura:
            return
        self._tira_assinatura = assinatura
        self.tira.montar(quantidade, self.projeto.caminho_entrada, folha_de, corte_de)

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------

    @property
    def aba_atual(self) -> str:
        indice = self.barra_abas.currentIndex()
        if 0 <= indice < len(self._abas_ativas):
            return self._abas_ativas[indice]
        return self._abas_ativas[0] if self._abas_ativas else ABA_FILTRO

    @property
    def trabalha_com_folhas(self) -> bool:
        return self.aba_atual == ABA_CORTE

    @property
    def item_atual(self):
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            return self.projeto.folhas[self.indice_folha]
        return self.projeto.paginas[self.indice_pagina]

    @property
    def indice_atual(self) -> int:
        return self.indice_folha if self.trabalha_com_folhas else self.indice_pagina

    def _total(self) -> int:
        assert self.projeto is not None
        return (len(self.projeto.folhas) if self.trabalha_com_folhas
                else len(self.projeto.paginas))

    def _pronta(self) -> bool:
        return (self.projeto is not None and self.previas is not None
                and bool(self._abas_ativas) and not self._carregando)

    # ------------------------------------------------------------------
    # navegacao
    # ------------------------------------------------------------------

    @protegido
    def _navegar(self, passo: int) -> None:
        if not self._pronta():
            return
        self._ir_para(max(0, min(self._total() - 1, self.indice_atual + passo)))

    def _ir_para(self, indice: int) -> None:
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            self.indice_folha = indice
            for pagina in self.projeto.paginas:
                if pagina.folha == indice:
                    self.indice_pagina = pagina.indice
                    break
        else:
            self.indice_pagina = indice
            self.indice_folha = self.projeto.paginas[indice].folha
        self.atualizar()

    @protegido
    def _escolher_da_tira(self, indice: int) -> None:
        if self._pronta():
            self._ir_para(indice)

    @protegido
    def _trocou_de_aba(self, _indice: int) -> None:
        if not self._pronta():
            return
        self.area_imagem.setCurrentIndex(self.barra_abas.currentIndex())
        self.barra_botoes.setCurrentIndex(self.barra_abas.currentIndex())
        # A pilha volta a caber na aba ATUAL. Sem isto ela guardaria a altura
        # da aba mais alta pelo resto da sessao, e o buraco voltaria.
        self._encolher_a_barra_de_botoes()
        self._montar_tira()
        self.atualizar()

    def _encolher_a_barra_de_botoes(self) -> None:
        """Deixa a fila de botoes com a altura da aba que esta na frente."""
        atual = self.barra_botoes.currentWidget()
        if atual is None:
            return
        for indice in range(self.barra_botoes.count()):
            pagina = self.barra_botoes.widget(indice)
            pagina.setSizePolicy(
                QSizePolicy.Preferred,
                QSizePolicy.Preferred if pagina is atual else QSizePolicy.Ignored)
        self.barra_botoes.setFixedHeight(max(0, atual.sizeHint().height()))

    @protegido
    def ir_para_pagina(self, indice: int) -> None:
        """Poe a tela na pagina pedida. E como o projeto volta onde parou.

        Nao e o `_ir_para`: aquele trabalha no indice da ABA - que na aba de
        corte conta FOLHAS, e nao paginas. Aqui o numero e sempre de pagina,
        porque e isso que fica guardado no resumo do projeto.
        """
        if not self._pronta() or self.projeto is None:
            return
        indice = max(0, min(int(indice), len(self.projeto.paginas) - 1))
        self.indice_pagina = indice
        self.indice_folha = self.projeto.paginas[indice].folha
        self.atualizar()

    def _ir_para_proximo_alerta(self) -> None:
        if not self._pronta():
            return
        assert self.projeto is not None
        total = self._total()
        itens = (self.projeto.folhas if self.trabalha_com_folhas
                 else self.projeto.paginas)
        for salto in range(1, total + 1):
            indice = (self.indice_atual + salto) % total
            if itens[indice].precisa_revisao:
                self._ir_para(indice)
                return

    # ------------------------------------------------------------------
    # desenho
    # ------------------------------------------------------------------

    @protegido
    def atualizar(self) -> None:
        if not self._pronta():
            return
        self._atualizar_previa()
        self._atualizar_faixa()
        self._atualizar_botoes()
        self._atualizar_tira()
        self._atualizar_contador()
        self._atualizar_paineis()
        self.trabalho_mudou.emit()

    def _atualizar_paineis(self) -> None:
        """Os quatro da direita leem o mesmo estado que o resto da tela."""
        if self.projeto is None:
            return
        self.paineis.para_revisar.atualizar(self.projeto)
        self.paineis.historico.atualizar(self.acoes)
        pagina = (self.projeto.paginas[self.indice_pagina]
                  if 0 <= self.indice_pagina < len(self.projeto.paginas) else None)
        self.paineis.filtro_da_pagina.atualizar(pagina)

    def _atualizar_previa(self) -> None:
        assert self.previas is not None and self.projeto is not None
        aba = self.aba_atual

        if aba == ABA_CORTE:
            img = self.previas.pegar_folha(self.indice_folha, DPI_PREVIA)
            vis = self.visualizadores[ABA_CORTE]
            vis.definir_imagem(img)
            vis.definir_corte(self.projeto.folhas[self.indice_folha].posicao_corte)
            self.previas.pre_carregar_folhas(self.indice_folha, DPI_PREVIA)
            return

        img = self.previas.pegar(self.indice_pagina, self._dpi_atual)
        self.previas.pre_carregar(self.indice_pagina, self._dpi_atual)
        pagina = self.projeto.paginas[self.indice_pagina]

        if aba == ABA_BORDAS:
            vis = self.visualizadores[ABA_BORDAS]
            vis.definir_dpi(self._dpi_atual)
            if self.botao_mover_conteudo.isChecked():
                self._atualizar_previa_composta(vis, pagina, img)
            else:
                self._atualizar_previa_para_recorte(vis, pagina)
            vis.definir_recorte(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
            self._conferir_tamanho_da_folha(pagina, vis)

            # Fase 2: "Mover conteúdo" só faz sentido com uma folha escolhida.
            # Sem ela, forçar de volta ao modo recorte - não deixar o botão
            # marcado apontando para um modo que não existe mais na tela.
            from ui.widgets.visualizador import MODO_RECORTE

            tem_folha = pagina.tamanho_folha_cm is not None
            self.botao_mover_conteudo.setEnabled(tem_folha)
            if not tem_folha and self.botao_mover_conteudo.isChecked():
                self.botao_mover_conteudo.setChecked(False)
                vis.definir_modo(MODO_RECORTE)
        elif aba == ABA_ANGULO:
            vis = self.visualizadores[ABA_ANGULO]
            vis.definir_imagem(img)
            vis.definir_angulo(pagina.angulo_manual or 0.0)
        elif aba == ABA_MARCAR:
            self._atualizar_marcacao(img, pagina)
        else:
            self._atualizar_cartoes(img)

    def _atualizar_marcacao(self, img, pagina) -> None:
        """Poe a pagina e a marcacao dela no editor.

        Problema 2 do plano (redesenho do fluxo): a deteccao NAO roda mais
        sozinha aqui - antes disparava toda vez que a pagina nao tinha
        marcacao, sem avisar; agora so quando o Samuel pede (botao
        "detectar automaticamente" desta aba, ou menu Marcar -> "Procurar de
        novo" - mesma acao, `_detectar_de_novo`). O pipeline final continua
        detectando sozinho quando precisa (`core/pipeline.py::garantir_selecao`)
        - isso e so a tela deixar de adivinhar por baixo dos panos.
        """
        self.editor_selecao.definir_imagem(img)
        selecao = pagina.obter_selecao()

        self.editor_selecao.definir_selecao(selecao)
        self._mostrar_aviso_da_marcacao(
            selecao.resumo_em_portugues() if not selecao.vazia
            else 'Nada marcado ainda. Clique em "detectar automaticamente" '
                 "ou marque à mão."
        )

    def _atualizar_cartoes(self, img: np.ndarray | None) -> None:
        """Os quatro cartoes mostram a página de verdade, cada um com seu filtro.

        Só o cartão do filtro escolhido é imediato (a imagem já veio pronta).
        Os outros três pedem o cálculo em segundo plano (regra 3.2): aplicar
        preto_e_branco/magico_pro de verdade - k_para_a_letra usa skeletonize -
        pode levar segundos numa página de traço fino, e isso não pode travar
        a tela.
        """
        from core.pdf_io import limitar_altura

        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]

        for chave, cartao in self.cartoes.items():
            cartao.definir_selecionado(chave == pagina.filtro)

        if img is None:
            for cartao in self.cartoes.values():
                cartao.definir_amostra(None)
            return

        for chave, cartao in self.cartoes.items():
            if chave == pagina.filtro:
                cartao.definir_amostra(limitar_altura(img, 260))

        outros = [chave for chave in self.cartoes if chave != pagina.filtro]
        base = self._imagem_sem_filtro()
        if base is None:
            for chave in outros:
                self.cartoes[chave].definir_amostra(None)
            return

        chave_cache = (self.indice_pagina, pagina.forca_preto,
                       pagina.clareza_melhorar, pagina.intensidade_magico)
        if chave_cache == self._cartoes_cache_chave:
            for chave in outros:
                self.cartoes[chave].definir_amostra(self._cartoes_cache.get(chave))
            return

        for chave in outros:
            self.cartoes[chave].definir_amostra(None)
        assert self.previas is not None
        self.previas.pedir_cartoes(
            self.indice_pagina, base, outros,
            pagina.forca_preto, pagina.clareza_melhorar, pagina.intensidade_magico,
        )

    @protegido
    def _cartoes_prontos(self, indice: int, resultados: dict) -> None:
        """Os cartões calculados em segundo plano chegaram.

        Se o usuário já virou a página nesse meio tempo, descarta - senão
        pinta e guarda no cache, para não recalcular ao voltar para cá.
        """
        if self.projeto is None or indice != self.indice_pagina:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        self._cartoes_cache_chave = (indice, pagina.forca_preto,
                                      pagina.clareza_melhorar, pagina.intensidade_magico)
        self._cartoes_cache = resultados
        for chave, amostra in resultados.items():
            if chave in self.cartoes:
                self.cartoes[chave].definir_amostra(amostra)

        self._conferir_qualidade_do_preto_e_branco(pagina, resultados)

    def _conferir_qualidade_do_preto_e_branco(self, pagina, resultados: dict) -> None:
        """Problema 5.4 do plano: aponta sozinho páginas que podem ter saído
        erradas, comparando o resultado com o original - em vez do Samuel
        ter que abrir imagem por imagem procurando problema."""
        from core.analise import ESCURA_DEMAIS, APAGADA_DEMAIS, avaliar_preto_e_branco

        original = resultados.get(ORIGINAL)
        pb = resultados.get(PRETO_E_BRANCO)
        if original is None or pb is None:
            return

        achado = avaliar_preto_e_branco(original, pb)
        tinha_algum = pagina.alertas.count(ESCURA_DEMAIS) or pagina.alertas.count(APAGADA_DEMAIS)
        pagina.alertas = [a for a in pagina.alertas if a not in (ESCURA_DEMAIS, APAGADA_DEMAIS)]
        if achado is not None:
            pagina.alertas.append(achado)

        if achado is not None or tinha_algum:
            self._atualizar_faixa()
            self._atualizar_tira()
            self._atualizar_contador()

    def _imagem_sem_filtro(self) -> np.ndarray | None:
        """Versao pequena e sem filtro da página atual, para os outros cartoes."""
        assert self.projeto is not None and self.previas is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        img_folha = self.previas.pegar_folha(pagina.folha, 70)
        if img_folha is None:
            return None

        from core.pipeline import preparar_metade

        folha = self.projeto.folhas[pagina.folha]
        try:
            return preparar_metade(img_folha, folha, pagina, self.projeto)
        except Exception:  # noqa: BLE001 - amostra que falha nao derruba a tela
            registrar_erro("amostra_de_filtro", traceback.format_exc())
            return None

    def _atualizar_faixa(self) -> None:
        item = self.item_atual
        aba = self.aba_atual
        alerta = analise.descrever(item.alertas[0]) if item.alertas else None

        if alerta is not None and not item.revisada:
            self.texto_faixa.setText(alerta.mensagem)
            self._pintar_faixa(alerta=True)
            self._mostrar_sugestao(aba, alerta.acao)
        else:
            self.texto_faixa.setText(self._texto_tranquilo(aba))
            self._pintar_faixa(alerta=False)
            self._mostrar_sugestao(aba, None)

    def _texto_tranquilo(self, aba: str) -> str:
        assert self.projeto is not None
        if aba == ABA_CORTE:
            folha = self.projeto.folhas[self.indice_folha]
            if not folha.dividir:
                return "Esta folha não vai ser dividida."
            return ("Achei a lombada e vou cortar na linha azul. "
                    "Se estiver errado, arraste a linha.")
        if aba == ABA_BORDAS:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.recorte is None:
                return "Vou cortar a borda sozinho. Arraste o retangulo se quiser mudar."
            return "Você ajustou o corte desta página."
        if aba == ABA_ANGULO:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.angulo_manual is None:
                return "Vou endireitar sozinho. Arraste sobre a página para girar na mao."
            return f"Você girou esta página em {pagina.angulo_manual:+.1f} graus."
        pagina = self.projeto.paginas[self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        return f"Esta página vai sair em {nome}."

    def _pintar_faixa(self, alerta: bool) -> None:
        """Troca a cor da faixa.

        A folha de estilo e aplicada direto no widget, sem buscar ninguem por
        propriedade do Qt e sem repolir a arvore inteira.
        """
        borda = LARANJA if alerta else AZUL
        fundo = LARANJA_CLARO if alerta else AZUL_CLARO
        self.faixa.setStyleSheet(
            f"QFrame {{ background: {fundo}; border: 1px solid {borda};"
            f" border-radius: 8px; }}"
        )

    def _mostrar_sugestao(self, aba: str, rotulo: str | None) -> None:
        botao = self.botoes_de_sugestao.get(aba)
        if botao is None:
            return
        botao.setVisible(bool(rotulo))
        if rotulo:
            botao.setText(rotulo)

    def _atualizar_botoes(self) -> None:
        assert self.projeto is not None and self.acoes is not None

        self.botao_desfazer.setEnabled(self.acoes.pode_desfazer)
        self.botao_desfazer.setToolTip(self.acoes.descricao_desfazer())
        self.botao_refazer.setEnabled(self.acoes.pode_refazer)
        self.botao_refazer.setToolTip(self.acoes.descricao_refazer())

        if ABA_CORTE in self._abas_ativas:
            folha = self.projeto.folhas[self.indice_folha]
            self.botao_nao_dividir.setText(
                "dividir esta" if not folha.dividir else "não dividir esta"
            )

        if ABA_FILTRO in self._abas_ativas:
            pagina = self.projeto.paginas[self.indice_pagina]
            self._configurar_medidor()
            self.botao_apagar.setText(
                "restaurar página" if pagina.apagada else "apagar página"
            )

    def _atualizar_tira(self) -> None:
        assert self.projeto is not None
        itens = (self.projeto.folhas if self.trabalha_com_folhas
                 else self.projeto.paginas)
        for i, item in enumerate(itens):
            self.tira.marcar(i, em_alerta=item.precisa_revisao,
                             apagada=getattr(item, "apagada", False))
        self.tira.selecionar(self.indice_atual)

    def _atualizar_contador(self) -> None:
        assert self.projeto is not None
        pendentes = self.projeto.pendentes_de_revisao()
        apagadas = self.projeto.total_apagadas

        if pendentes == 0:
            texto = "tudo certo"
        elif pendentes == 1:
            texto = "1 página para você olhar"
        else:
            texto = f"{pendentes} páginas para você olhar"
        if apagadas:
            texto += f"  -  {apagadas} apagadas"
        self.botao_alertas.setText(texto)
        self.botao_alertas.setEnabled(pendentes > 0)

        observacoes = getattr(self.projeto, "observacoes", [])
        self.rotulo_observacoes.setVisible(bool(observacoes))
        if observacoes:
            self.rotulo_observacoes.setText("   -   " + "; ".join(observacoes))

    @protegido
    def _previa_chegou(self, chave: str, _img: np.ndarray) -> None:
        """Uma prévia ficou pronta; se for a que estamos vendo, redesenha."""
        if not self._pronta():
            return
        assert self.previas is not None
        esperadas = (
            self.previas.chave(self.indice_pagina, self._dpi_atual),
            self.previas.chave_folha(self.indice_folha, DPI_PREVIA),
            self.previas.chave_para_recorte(self.indice_pagina, self._dpi_atual),
        )
        if chave in esperadas or chave.startswith("folha:"):
            self._atualizar_previa()

    # ------------------------------------------------------------------
    # alteracoes (todas passam pelo historico)
    # ------------------------------------------------------------------

    def _registrar(self, tipo: str, alvo: str, indices: list[int],
                   campos: dict, descricao: str) -> None:
        """Aplica a mudanca e guarda no histórico, numa acao só."""
        assert self.projeto is not None and self.acoes is not None
        acao = montar_acao(self.projeto, tipo, alvo, indices, campos, descricao)
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)

        afetadas = indices if alvo == "pagina" else self._paginas_das_folhas(indices)
        if self.previas is not None:
            for indice in afetadas:
                self.previas.invalidar(indice)
        self.atualizar()

    def _paginas_das_folhas(self, folhas: list[int]) -> list[int]:
        assert self.projeto is not None
        alvo = set(folhas)
        return [p.indice for p in self.projeto.paginas if p.folha in alvo]

    # --- corte ------------------------------------------------------------

    @protegido
    def _mover_corte(self, posicao: float) -> None:
        self._registrar(
            "mover_corte", "folha", [self.indice_folha],
            {"posicao_corte": round(posicao, 4), "revisada": True},
            f"Linha de corte da folha {self.indice_folha + 1}",
        )

    @protegido
    def _corte_em_todas(self) -> None:
        assert self.projeto is not None
        posicao = self.projeto.folhas[self.indice_folha].posicao_corte
        indices = [f.indice for f in self.projeto.folhas]
        self._registrar(
            "aplicar_em_todas", "folha", indices,
            {"posicao_corte": round(posicao, 4)},
            f"Linha de corte de todas as {len(indices)} folhas",
        )

    @protegido
    def _alternar_dividir(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "nao_dividir", "folha", [self.indice_folha],
            {"dividir": not folha.dividir, "revisada": True},
            f"Folha {self.indice_folha + 1}: "
            + ("dividir" if not folha.dividir else "não dividir"),
        )

    @protegido
    def _girar(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "girar", "folha", [self.indice_folha],
            {"rotacao": (folha.rotacao + 90) % 360},
            f"Girar a folha {self.indice_folha + 1}",
        )

    # --- bordas -----------------------------------------------------------

    @protegido
    def _mover_recorte(self, recorte: tuple) -> None:
        arredondado = [round(float(v), 4) for v in recorte]
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": arredondado, "revisada": True},
            f"Corte de borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _sem_recorte(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": [0.0, 0.0, 1.0, 1.0], "revisada": True},
            f"Não cortar a borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _recorte_automatico(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina], {"recorte": None},
            f"Voltar ao corte automático na página {self.indice_pagina + 1}",
        )

    @protegido
    def _recorte_em_todas(self) -> None:
        assert self.projeto is not None
        recorte = self.projeto.paginas[self.indice_pagina].recorte
        indices = [p.indice for p in self.projeto.paginas]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"recorte": list(recorte) if recorte else None},
            f"Corte de borda de todas as {len(indices)} páginas",
        )

    @protegido
    def _mover_conteudo(self, retangulo: tuple) -> None:
        """Fase 2+3 (aprovadas pelo Samuel em 22/09/2026): arrastar E
        redimensionar o CONTEÚDO dentro da folha - grava
        `conteudo_deslocamento` e `conteudo_escala` juntos, numa ação só.

        `retangulo` vem do widget em fração do CANVAS
        (`Visualizador.conteudo_movido` - tanto de `_mover_conteudo` quanto
        de `_redimensionar_conteudo` no widget, o sinal é o mesmo); aqui é
        convertido para o formato salvo em `ConfigPagina` via
        `core.folha.deslocamento_do_retangulo` - o mesmo par de funções
        (`conteudo_como_retangulo`/`deslocamento_do_retangulo`) que a prévia
        composta (passo 8) já usa. Até a Fase 3, `_escala` vinha do
        `deslocamento_do_retangulo` mas era descartado (`_escala, ... =`) -
        só mover mudava x/y, nunca w/h, então `escala` nunca mudava de
        verdade. Agora que redimensionar existe, `escala` também precisa
        ser persistida.
        """
        from core.folha import deslocamento_do_retangulo

        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if pagina.tamanho_folha_cm is None:
            return
        vis = self.visualizadores[ABA_BORDAS]
        tamanho_conteudo_px = vis.tamanho_da_pagina_px()
        if tamanho_conteudo_px == (0, 0):
            return

        escala, deslocamento = deslocamento_do_retangulo(
            retangulo, pagina.tamanho_folha_cm, tamanho_conteudo_px, vis.dpi_atual())
        escala_arredondada = round(escala, 4)
        deslocamento_arredondado = (round(deslocamento[0], 4), round(deslocamento[1], 4))
        if (escala_arredondada == pagina.conteudo_escala
                and deslocamento_arredondado == pagina.conteudo_deslocamento):
            return
        self._registrar(
            "mover_conteudo", "pagina", [self.indice_pagina],
            {
                "conteudo_deslocamento": list(deslocamento_arredondado),
                "conteudo_escala": escala_arredondada,
            },
            f"Posição/tamanho do conteúdo na página {self.indice_pagina + 1}",
        )

    # --- angulo -----------------------------------------------------------

    @protegido
    def _mover_angulo(self, angulo: float) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": round(angulo, 2), "revisada": True},
            f"Angulo da página {self.indice_pagina + 1}: {angulo:+.1f} graus",
        )

    @protegido
    def _angulo_zero(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": 0.0, "revisada": True},
            f"Não endireitar a página {self.indice_pagina + 1}",
        )

    @protegido
    def _angulo_automatico(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina], {"angulo_manual": None},
            f"Voltar ao endireitar automático na página {self.indice_pagina + 1}",
        )

    # --- filtro -----------------------------------------------------------

    @protegido
    def _escolher_filtro(self, filtro: str) -> None:
        assert self.projeto is not None
        atual = self.projeto.paginas[self.indice_pagina].filtro
        nome_antes = NOMES_AMIGAVEIS.get(atual, atual)
        nome_depois = NOMES_AMIGAVEIS.get(filtro, filtro)
        self._registrar(
            "mudar_filtro", "pagina", [self.indice_pagina],
            {"filtro": filtro, "revisada": True},
            f"Filtro da página {self.indice_pagina + 1}: {nome_antes} para {nome_depois}",
        )

    @protegido
    def _mudar_algoritmo_pb(self, indice: int) -> None:
        """Problema 5 do plano: qual dos 3 algoritmos o Preto e branco usa
        nesta página. Chamado pelo seletor da aba Filtro."""
        if not self._pronta() or self.projeto is None:
            return
        novo = self.seletor_algoritmo_pb.itemData(indice)
        if novo is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if novo == pagina.algoritmo_preto_branco:
            return
        nome = NOMES_DOS_ALGORITMOS_PB.get(novo, novo) if novo != "auto" else "Automático"
        self._registrar(
            "mudar_algoritmo_pb", "pagina", [self.indice_pagina],
            {"algoritmo_preto_branco": novo},
            f"Algoritmo do Preto e branco na página {self.indice_pagina + 1}: {nome}",
        )

    @protegido
    def _mudar_despeckle(self, ligado: bool) -> None:
        """Problema 5 do plano: limpar poeirinha vira controle visível."""
        if not self._pronta() or self.projeto is None:
            return
        pagina = self.projeto.paginas[self.indice_pagina]
        if ligado == pagina.despeckle:
            return
        self._registrar(
            "mudar_despeckle", "pagina", [self.indice_pagina],
            {"despeckle": ligado},
            f"Limpar poeirinha na página {self.indice_pagina + 1}: "
            + ("ligado" if ligado else "desligado"),
        )

    # --- medidor de ajuste ------------------------------------------------

    def _campo_do_ajuste(self, filtro: str | None = None) -> str | None:
        """Qual campo da página o medidor edita, conforme o filtro escolhido."""
        if filtro is None:
            if self.projeto is None:
                return None
            filtro = self.projeto.paginas[self.indice_pagina].filtro
        return CAMPO_DO_AJUSTE.get(filtro)

    def _configurar_medidor(self) -> None:
        """Mostra o medidor do filtro atual, com o valor daquela página."""
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        campo = self._campo_do_ajuste(pagina.filtro)

        # Original não tem o que ajustar: o bloco inteiro some.
        self.bloco_ajuste.setVisible(campo is not None)
        if campo is None:
            return

        rotulo, esquerda, direita = ROTULOS_DO_AJUSTE[pagina.filtro]
        self.medidor.definir_rotulo(rotulo, esquerda, direita)
        self.medidor.definir(getattr(pagina, campo))

        # O algoritmo só faz sentido no Preto e branco - Melhorar/Mágico pro
        # não binarizam.
        eh_preto_e_branco = pagina.filtro == PRETO_E_BRANCO
        self.seletor_algoritmo_pb.setVisible(eh_preto_e_branco)
        self.caixa_despeckle.setVisible(eh_preto_e_branco)
        if eh_preto_e_branco:
            indice = self.seletor_algoritmo_pb.findData(pagina.algoritmo_preto_branco)
            self.seletor_algoritmo_pb.blockSignals(True)
            self.seletor_algoritmo_pb.setCurrentIndex(max(0, indice))
            self.seletor_algoritmo_pb.blockSignals(False)
            self.caixa_despeckle.blockSignals(True)
            self.caixa_despeckle.setChecked(pagina.despeckle)
            self.caixa_despeckle.blockSignals(False)

    @protegido
    def _medidor_pegou(self) -> None:
        """Guarda o valor de antes, para o Ctrl+Z voltar ao ponto certo."""
        campo = self._campo_do_ajuste()
        if campo and self.projeto is not None:
            self._valor_ao_pegar = getattr(
                self.projeto.paginas[self.indice_pagina], campo
            )

    @protegido
    def _medidor_arrastando(self, valor: int) -> None:
        """Prévia ao vivo: aplica no objeto e agenda o redesenho.

        Nao registra no histórico a cada passo - seriam dezenas de ações por
        arrasto. O histórico só recebe uma ação, ao soltar.
        """
        if not self._pronta():
            return
        campo = self._campo_do_ajuste()
        if campo is None:
            return
        assert self.projeto is not None

        if self._valor_ao_pegar is None:
            self._valor_ao_pegar = getattr(
                self.projeto.paginas[self.indice_pagina], campo
            )

        setattr(self.projeto.paginas[self.indice_pagina], campo, int(valor))

        # Durante o arrasto a prévia sai em resolução baixa: a 110 DPI o filtro
        # não acompanha o dedo. Ao soltar volta para a resolução normal.
        self._dpi_atual = DPI_ARRASTO
        self._agendar.start(ESPERA_ARRASTO_MS)

        # Sem medidor preso (mexeu pelo teclado), o commit vem por tempo.
        if not self.medidor.barra.isSliderDown():
            self._commit.start(ESPERA_COMMIT_MS)

    @protegido
    def _medidor_soltou(self, valor: int | None = None) -> None:
        """Fecha o arrasto: uma ação só no histórico e prévia em resolução cheia."""
        self._commit.stop()
        if not self._pronta():
            return
        campo = self._campo_do_ajuste()
        if campo is None:
            return
        assert self.projeto is not None

        pagina = self.projeto.paginas[self.indice_pagina]
        novo = int(self.medidor.valor if valor is None else valor)
        antigo = self._valor_ao_pegar
        self._valor_ao_pegar = None
        self._dpi_atual = self._dpi_normal

        if antigo is None or antigo == novo:
            self.atualizar()
            return

        # Volta ao valor de antes para que o "antes" da ação fique correto;
        # o _registrar aplica o novo em seguida.
        setattr(pagina, campo, antigo)
        rotulo = ROTULOS_DO_AJUSTE[pagina.filtro][0]
        self._registrar(
            "ajuste_filtro", "pagina", [self.indice_pagina],
            {campo: novo, "revisada": True},
            f"{rotulo} da página {self.indice_pagina + 1}: {palavra_do_ajuste(novo)}",
        )

    # --- ver de perto -----------------------------------------------------

    @protegido
    def _ampliar_com_filtro(self, _filtro: str) -> None:
        """Veio de um clique num cartão: o filtro já foi escolhido antes."""
        self.ampliar()

    @protegido
    def _ampliar_miniatura(self, indice: int) -> None:
        """Duplo clique na tira: vai para aquela página e abre ampliada."""
        if not self._pronta():
            return
        self._ir_para(indice)
        self.ampliar()

    @protegido
    def ampliar(self) -> None:
        """Abre a página em tamanho grande, no modo da aba atual."""
        if not self._pronta():
            return

        from ui.tela_ampliada import (
            MODO_BORDAS,
            MODO_CORTAR,
            MODO_FILTRO,
            TelaAmpliada,
        )

        modos = {ABA_CORTE: MODO_CORTAR, ABA_BORDAS: MODO_BORDAS}
        modo = modos.get(self.aba_atual, MODO_FILTRO)

        janela = TelaAmpliada(self, modo=modo, parent=self.window())
        # ao fechar, a tela normal se redesenha: o usuário pode ter trocado o
        # filtro ou movido a linha de corte lá dentro
        janela.fechou.connect(self.atualizar)
        janela.exec()

    def _redesenhar_previa(self) -> None:
        """Chamado pelo tempo de espera do arrasto."""
        if not self._pronta():
            return
        assert self.previas is not None
        self.previas.invalidar(self.indice_pagina)
        self._atualizar_previa()

    @protegido
    def _filtro_em_todas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto,
             "clareza_melhorar": pagina.clareza_melhorar,
             "intensidade_magico": pagina.intensidade_magico,
             "algoritmo_preto_branco": pagina.algoritmo_preto_branco,
             "despeckle": pagina.despeckle},
            f"{nome} em todas as {len(indices)} páginas",
        )

    @protegido
    def _filtro_nas_proximas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto,
             "clareza_melhorar": pagina.clareza_melhorar,
             "intensidade_magico": pagina.intensidade_magico,
             "algoritmo_preto_branco": pagina.algoritmo_preto_branco,
             "despeckle": pagina.despeckle},
            f"{nome} da página {self.indice_pagina + 1} em diante ({len(indices)} páginas)",
        )

    # --- gerais -----------------------------------------------------------

    @protegido
    def apagar_pagina(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        acao = "restaurar" if pagina.apagada else "apagar"
        self._registrar(
            acao, "pagina", [self.indice_pagina],
            {"apagada": not pagina.apagada, "revisada": True},
            f"{acao.capitalize()} a página {self.indice_pagina + 1}",
        )

    @protegido
    def _marcar_revisada(self) -> None:
        alvo = "folha" if self.trabalha_com_folhas else "pagina"
        self._registrar(
            "revisar", alvo, [self.indice_atual], {"revisada": True},
            f"Conferir a {alvo} {self.indice_atual + 1}",
        )

    @protegido
    def marcar_certo_e_avancar(self) -> None:
        """Barra de espaço: aprova e já pula para a próxima."""
        self._marcar_revisada()
        self._navegar(1)

    @protegido
    def _aplicar_sugestao(self) -> None:
        """O botão laranja do alerta: aplica a correcao mais provavel.

        E só um atalho. Todos os controles manuais continuam valendo.
        """
        item = self.item_atual
        if not item.alertas:
            return
        correcao = analise.descrever(item.alertas[0]).correcao
        if correcao is None or correcao == "revisar":
            self._marcar_revisada()
        elif correcao.startswith("filtro:"):
            self._escolher_filtro(correcao.split(":", 1)[1])
        elif correcao.startswith("forca:"):
            self._escolher_forca(correcao.split(":", 1)[1])
        elif correcao == "apagar":
            self.apagar_pagina()
        elif correcao == "nao_dividir":
            self._alternar_dividir()
        elif correcao == "angulo_zero":
            self._angulo_zero()
        elif correcao == "sem_recorte":
            self._sem_recorte()

    # --- desfazer / refazer -----------------------------------------------

    @protegido
    def desfazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.desfazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.atualizar()

    @protegido
    def refazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.refazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.atualizar()

    # --- teclado ----------------------------------------------------------

    def tratar_tecla(self, evento) -> bool:
        """Atalhos da secao 4.7. Devolve True se consumiu a tecla."""
        if not self._pronta():
            return False

        tecla = evento.key()
        ctrl = evento.modifiers() & Qt.ControlModifier
        shift = evento.modifiers() & Qt.ShiftModifier

        if ctrl and tecla == Qt.Key_Z:
            self.refazer() if shift else self.desfazer()
            return True
        if ctrl and tecla == Qt.Key_Y:
            self.refazer()
            return True
        if ctrl and tecla in (Qt.Key_Return, Qt.Key_Enter):
            self._pedir_processamento()
            return True

        # As letras das ferramentas (R O L P B V C Z E por padrão, mas
        # remapeáveis pela tela de Configurações). Nao conflitam com os
        # numeros 1 2 3 4, que continuam trocando o filtro. So valem sem Ctrl,
        # senao roubariam Ctrl+O e Ctrl+Z de quem espera abrir e desfazer.
        if not ctrl:
            letra = evento.text().upper()
            ferramenta = ferramenta_da_tecla(letra)
            if ferramenta is not None:
                self.escolher_ferramenta(ferramenta)
                return True
            if ABA_BORDAS in self._abas_ativas:
                if letra == atalhos.tecla_atual(CHAVE_RECORTE_ESPELHADO):
                    self.botao_espelhado.click()
                    return True
                if letra == atalhos.tecla_atual(CHAVE_RECORTE_PROPORCAO):
                    self.botao_proporcao_travada.click()
                    return True

        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_NAVEGAR_ANTERIOR), Qt.Key_Left):
            self._navegar(-1)
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_NAVEGAR_PROXIMA), Qt.Key_Right):
            self._navegar(1)
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_MARCAR_CERTO), Qt.Key_Space):
            self.marcar_certo_e_avancar()
            return True
        if tecla == _QT_KEY_DAS_TECLAS_DE_NAVEGACAO.get(
                atalhos.tecla_atual(CHAVE_PROXIMO_ALERTA), Qt.Key_Tab):
            self._ir_para_proximo_alerta()
            return True
        if tecla == Qt.Key_Delete:
            if not self.trabalha_com_folhas:
                self.apagar_pagina()
            return True
        if tecla == Qt.Key_R and ABA_CORTE in self._abas_ativas:
            self._girar()
            return True

        atalhos_de_filtro = {
            Qt.Key_1: ORIGINAL, Qt.Key_2: PRETO_E_BRANCO,
            Qt.Key_3: MELHORAR, Qt.Key_4: MAGICO_PRO,
        }
        if tecla in atalhos_de_filtro and not self.trabalha_com_folhas:
            self._escolher_filtro(atalhos_de_filtro[tecla])
            return True

        return False

    # --- saida ------------------------------------------------------------

    def _avisar_problema(self) -> None:
        """O que o usuario ve quando algo deu errado por baixo dos panos."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Um momento")
        caixa.setIcon(QMessageBox.Information)
        caixa.setText("Não consegui fazer isso agora.")
        caixa.setInformativeText(
            "O programa continua funcionando e o seu trabalho está salvo. "
            "Tente de novo, ou passe para a próxima página."
        )
        caixa.addButton("entendi", QMessageBox.AcceptRole)
        caixa.exec()

    @protegido
    def _pedir_processamento(self) -> None:
        """Avisa se ainda ha dúvidas, mas nunca bloqueia."""
        if self.projeto is None:
            return
        pendentes = self.projeto.pendentes_de_revisao()
        if pendentes > 0:
            caixa = QMessageBox(self)
            caixa.setWindowTitle("Antes de processar")
            caixa.setIcon(QMessageBox.Question)
            caixa.setText(
                f"Ainda tem {pendentes} "
                + ("página que eu não tive certeza." if pendentes == 1
                   else "páginas que eu não tive certeza.")
            )
            caixa.setInformativeText("Quer conferir antes ou processar assim mesmo?")
            conferir = caixa.addButton("conferir", QMessageBox.RejectRole)
            caixa.addButton("processar assim mesmo", QMessageBox.AcceptRole)
            caixa.exec()
            if caixa.clickedButton() is conferir:
                self._ir_para_proximo_alerta()
                return
        self.processar.emit()


def _ligar(botao: QPushButton, acao) -> None:
    """Liga o clique ignorando o argumento 'checked' que o Qt manda junto."""
    botao.clicked.connect(lambda *_: acao())


def _botao(texto: str, destino: QHBoxLayout, acao, objeto: str = "") -> QPushButton:
    botao = QPushButton(texto)
    if objeto:
        botao.setObjectName(objeto)
    _ligar(botao, acao)
    destino.addWidget(botao)
    return botao
