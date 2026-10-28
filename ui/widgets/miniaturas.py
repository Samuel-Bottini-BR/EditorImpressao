"""As miniaturas da tela de trabalho com o cabeçalho "PÁGINAS" (etapa 5 do layout, 21/10/2026).

O QUE O SAMUEL DECIDIU
    - Rodada 7, 204 A e o comentário: miniaturas embaixo, à esquerda ou à direita JUNTO DA
      PÁGINA (o menu da direita não muda de lugar); "eu quero poder só arrastar a barra para onde
      eu quiser, e quero conseguir fechar ou abrir as minaturas com um drop down".
    - Rodada 7, 205: as opções ("em pares" etc.) "quando eu apertasse um especie de 3 pontinhos".
    - Rodada 8, 301 A: "Cabeçalho com o nome": PÁGINAS, a seta que abre e fecha, os três
      pontinhos e a alça de arrastar.
    - Rodada 13, 808 A: o botão "ver todas" (abre "Todas as páginas") no cabeçalho; com as
      miniaturas de lado, ele vai para uma linha logo abaixo do cabeçalho.
    - Rodada 13, 801 A: com as miniaturas fechadas ou de lado, o "Confirmar e processar" desce
      para a barra de baixo (quem faz isso é a tela de conferir: ver `lugar` e `aberta`).

O QUE ESTE ARQUIVO FAZ
    PainelDeMiniaturas = cabeçalho + a tira (ui/widgets/tira_miniaturas.TiraMiniaturas). O
    cabeçalho tem a alça (arrastar: sinais `arrastando`/`soltou`, com o ponto da tela; quem
    mostra os lugares de encaixe e decide é a tela de conferir), o nome, a seta (abre e fecha
    a tira), os três pontinhos (menu: Ver em pares · Lugar · Fechar/Abrir) e "ver todas".
    De lado e fechadas, as miniaturas viram uma faixa fininha só com a seta e a alça.

Seguro mudar: tamanhos e textos. Arriscado: criar outra TiraMiniaturas aqui (a tela de conferir
conversa com `self.tira`; duas tiras leriam o PDF duas vezes).
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QAction, QActionGroup, QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui import estilo
from ui.widgets.tira_miniaturas import TiraMiniaturas

EMBAIXO, ESQUERDA, DIREITA = "embaixo", "esquerda", "direita"
LUGARES = (EMBAIXO, ESQUERDA, DIREITA)
NOMES_DOS_LUGARES = {EMBAIXO: "embaixo", ESQUERDA: "à esquerda", DIREITA: "à direita, junto da página"}
LARGURA_DE_LADO = 150          # a coluna, com as miniaturas de lado (cabe o cabeçalho e um par)
LARGURA_FECHADA_DE_LADO = 26   # a faixa fininha, de lado e fechada
ALTURA_DO_CABECALHO = 24


class _BotaoDesenhado(QPushButton):
    """Um botão pequeno, sem moldura, com um desenho feito à mão (seta, três
    pontinhos, grade): sem símbolo de texto, que pode sair quadrado no Windows."""

    def __init__(self, desenho: str, dica: str, texto: str = "", parent=None) -> None:
        super().__init__(texto, parent)
        self.desenho = desenho          # "abaixo", "acima", "direita", "esquerda", "pontos", "grade"
        self.setToolTip(dica)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName("botaoDoCabecalhoDasMiniaturas")
        self.setFixedHeight(20)
        if not texto:
            self.setFixedWidth(22)

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().paintEvent(evento)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(QPen(QColor(estilo.cor("texto")), 1.5))
        pintor.setBrush(QColor(estilo.cor("texto")))
        cx = 11 if self.text() else self.width() / 2
        cy = self.height() / 2
        d = self.desenho
        if d == "pontos":
            for dx in (-4, 0, 4):
                pintor.drawEllipse(QPointF(cx + dx, cy), 1.2, 1.2)
        elif d == "grade":
            pintor.setBrush(Qt.NoBrush)
            for dx in (-4, 1):
                for dy in (-4, 1):
                    pintor.drawRect(QRectF(cx + dx, cy + dy, 3.5, 3.5))
        else:
            pintor.setBrush(Qt.NoBrush)
            pontos = {"abaixo": [(-4, -2), (0, 2), (4, -2)], "acima": [(-4, 2), (0, -2), (4, 2)],
                      "direita": [(-2, -4), (2, 0), (-2, 4)], "esquerda": [(2, -4), (-2, 0), (2, 4)]}[d]
            pintor.drawPolyline([QPointF(cx + x, cy + y) for x, y in pontos])
        pintor.end()


class _Alca(QWidget):
    """A alça de arrastar: seis pontinhos. Apertar e arrastar move as
    miniaturas para outro lugar (a tela mostra onde dá para soltar)."""

    arrastando = Signal(QPoint)    # o ponto do mouse, na tela
    soltou = Signal(QPoint)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(16, 20))
        self.setCursor(Qt.OpenHandCursor)
        self.setToolTip("Arraste para pôr as miniaturas embaixo, à esquerda ou à direita da página.")
        self._apertada = False

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(estilo.cor("fraco")))
        for x in (5.5, 10.5):
            for y in (5.5, 10, 14.5):
                pintor.drawEllipse(QPointF(x, y), 1.3, 1.3)
        pintor.end()

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.button() == Qt.LeftButton:
            self._apertada = True
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if self._apertada:
            self.arrastando.emit(evento.globalPosition().toPoint())

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if self._apertada and evento.button() == Qt.LeftButton:
            self._apertada = False
            self.setCursor(Qt.OpenHandCursor)
            self.soltou.emit(evento.globalPosition().toPoint())


class PainelDeMiniaturas(QFrame):
    """O cabeçalho "PÁGINAS" e a tira (ver o começo do arquivo)."""

    lugar_pedido = Signal(str)
    aberta_mudou = Signal(bool)
    em_pares_mudou = Signal(bool)
    ver_todas = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("miniaturas")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.lugar = EMBAIXO
        self.aberta = True
        self.em_pares = False

        self.tira = TiraMiniaturas("Folhas")
        self.alca = _Alca()
        self.titulo = QLabel("PÁGINAS")
        self.titulo.setObjectName("tituloDasMiniaturas")
        self.seta = _BotaoDesenhado("abaixo", "Fechar as miniaturas")
        self.seta.clicked.connect(lambda: self.definir_aberta(not self.aberta, avisar=True))
        self.pontos = _BotaoDesenhado("pontos", "Mais opções das miniaturas")
        self.pontos.clicked.connect(self._abrir_o_menu)
        self.botao_ver_todas = _BotaoDesenhado("grade", "Abre todas as páginas do livro, em grade",
                                               "ver todas")
        self.botao_ver_todas.setStyleSheet("padding-left: 20px; padding-right: 6px;")
        self.botao_ver_todas.clicked.connect(lambda: self.ver_todas.emit())
        self._montar_o_menu()

        self.cabecalho = QWidget()
        self.cabecalho.setObjectName("cabecalhoDasMiniaturas")
        self.cabecalho.setAttribute(Qt.WA_StyledBackground, True)
        self.linha_do_ver_todas = QWidget()
        self.linha_do_ver_todas.setObjectName("cabecalhoDasMiniaturas")
        self.linha_do_ver_todas.setAttribute(Qt.WA_StyledBackground, True)
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)
        fora.addWidget(self.cabecalho)
        fora.addWidget(self.linha_do_ver_todas)
        fora.addWidget(self.tira, 1)
        estilo.estilizar(self, self._folha)
        self._arrumar_o_cabecalho()

    # --- desenho ------------------------------------------------------------

    def _folha(self) -> str:
        c = estilo.cor
        return (f"QFrame#miniaturas {{ background: {c('bar')}; border-top: 1px solid {c('linha')}; }}"
                f"QWidget#cabecalhoDasMiniaturas {{ background: {c('bar')}; }}"
                f"QLabel#tituloDasMiniaturas {{ color: {c('fraco')}; font-size: 11px; font-weight: 600;"
                f" letter-spacing: 1px; background: transparent; }}"
                f"QPushButton#botaoDoCabecalhoDasMiniaturas {{ background: transparent; border: 1px solid"
                f" transparent; border-radius: 4px; color: {c('texto')}; font-size: 12px; padding: 0px; }}"
                f"QPushButton#botaoDoCabecalhoDasMiniaturas:hover {{ background: {c('botao_h')}; }}")

    def _arrumar_o_cabecalho(self) -> None:
        """Embaixo: tudo numa linha. De lado: o "ver todas" numa linha logo
        abaixo do cabeçalho (808 A). De lado e fechada: só a alça e a seta,
        uma em cima da outra, numa faixa fininha."""
        for caixa in (self.cabecalho, self.linha_do_ver_todas):
            antigo = caixa.layout()
            if antigo is not None:
                while antigo.count():
                    antigo.takeAt(0)
                QWidget().setLayout(antigo)            # descarta o layout antigo
        de_lado = self.lugar != EMBAIXO
        fininha = de_lado and not self.aberta
        if fininha:
            linha = QVBoxLayout(self.cabecalho)
            linha.setContentsMargins(3, 6, 3, 6)
            linha.setSpacing(6)
            linha.addWidget(self.alca, 0, Qt.AlignHCenter)
            linha.addWidget(self.seta, 0, Qt.AlignHCenter)
            linha.addStretch()
            for peca in (self.titulo, self.pontos, self.botao_ver_todas):
                peca.setVisible(False)
        else:
            linha = QHBoxLayout(self.cabecalho)
            linha.setContentsMargins(6, 2, 6, 2)
            linha.setSpacing(4)
            linha.addWidget(self.alca)
            linha.addWidget(self.titulo)
            linha.addWidget(self.seta)
            linha.addWidget(self.pontos)
            if de_lado:
                linha.addStretch()
                baixo = QHBoxLayout(self.linha_do_ver_todas)
                baixo.setContentsMargins(6, 0, 6, 4)
                baixo.addWidget(self.botao_ver_todas)
                baixo.addStretch()
            else:
                linha.addWidget(self.botao_ver_todas)
                linha.addStretch()
            # Lista de bugs de 22/10/2026 (etapa 9b-2): só DEPOIS de cada peça
            # estar no lugar (com pai); antes, o "ver todas" sem pai aparecia
            # por um instante como janela solta
            for peca in (self.titulo, self.pontos, self.botao_ver_todas):
                peca.setVisible(True)
        self.linha_do_ver_todas.setVisible(de_lado and self.aberta)
        self.cabecalho.setSizePolicy(QSizePolicy.Preferred,
                                     QSizePolicy.Expanding if fininha else QSizePolicy.Fixed)
        self.tira.setVisible(self.aberta)
        self.tira.definir_arranjo(de_lado, self.em_pares)
        if de_lado:
            self.setFixedWidth(LARGURA_FECHADA_DE_LADO if fininha else LARGURA_DE_LADO)
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if de_lado:
            self.seta.desenho = "abaixo" if self.aberta else ("direita" if self.lugar == ESQUERDA else "esquerda")
        else:
            self.seta.desenho = "abaixo" if self.aberta else "acima"
        self.seta.setToolTip("Fechar as miniaturas" if self.aberta else "Abrir as miniaturas")
        self.seta.update()
        self._acertar_o_menu()

    # --- o menu dos três pontinhos -------------------------------------------

    def _montar_o_menu(self) -> None:
        self.menu = QMenu(self)
        self.acao_em_pares = QAction("Ver em pares", self.menu)
        self.acao_em_pares.setCheckable(True)
        self.acao_em_pares.toggled.connect(lambda marcado: self.definir_em_pares(marcado, avisar=True))
        self.menu.addAction(self.acao_em_pares)
        self.menu_lugar = self.menu.addMenu("Lugar")
        grupo = QActionGroup(self.menu_lugar)
        self.acoes_de_lugar = {}
        for lugar in LUGARES:
            acao = QAction(NOMES_DOS_LUGARES[lugar], self.menu_lugar)
            acao.setCheckable(True)
            grupo.addAction(acao)
            acao.triggered.connect(lambda _m=False, lu=lugar: self.lugar_pedido.emit(lu))
            self.menu_lugar.addAction(acao)
            self.acoes_de_lugar[lugar] = acao
        self.menu.addSeparator()
        self.acao_abrir_fechar = QAction("Fechar as miniaturas", self.menu)
        self.acao_abrir_fechar.triggered.connect(
            lambda: self.definir_aberta(not self.aberta, avisar=True))
        self.menu.addAction(self.acao_abrir_fechar)

    def _acertar_o_menu(self) -> None:
        self.acao_em_pares.blockSignals(True)
        self.acao_em_pares.setChecked(self.em_pares)
        self.acao_em_pares.blockSignals(False)
        self.acoes_de_lugar[self.lugar].setChecked(True)
        self.acao_abrir_fechar.setText("Fechar as miniaturas" if self.aberta else "Abrir as miniaturas")

    def _abrir_o_menu(self) -> None:
        self.menu.popup(self.pontos.mapToGlobal(QPoint(0, self.pontos.height())))

    # --- uso -------------------------------------------------------------------

    def definir_lugar(self, lugar: str) -> None:
        """Embaixo, à esquerda ou à direita (quem muda de lugar na tela é a tela)."""
        self.lugar = lugar if lugar in LUGARES else EMBAIXO
        self._arrumar_o_cabecalho()

    def definir_aberta(self, aberta: bool, avisar: bool = False) -> None:
        """Abre ou fecha a tira (o cabeçalho fica)."""
        if bool(aberta) == self.aberta:
            return
        self.aberta = bool(aberta)
        self._arrumar_o_cabecalho()
        if avisar:
            self.aberta_mudou.emit(self.aberta)

    def definir_em_pares(self, em_pares: bool, avisar: bool = False) -> None:
        """Liga ou desliga o "em pares" (1 sozinha, depois 2 e 3...)."""
        if bool(em_pares) == self.em_pares:
            return
        self.em_pares = bool(em_pares)
        self._arrumar_o_cabecalho()
        if avisar:
            self.em_pares_mudou.emit(self.em_pares)

    def definir_titulo(self, texto: str) -> None:
        """PÁGINAS, ou FOLHAS com a ferramenta Dividir (a tira mostra folhas)."""
        self.titulo.setText(texto)
