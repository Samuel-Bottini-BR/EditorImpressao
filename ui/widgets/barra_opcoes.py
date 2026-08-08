"""A barra de opções: faixa fina que muda conforme a ferramenta na mão.

É a peça central do layout novo. Mostra só os controles da ferramenta ativa e
nada mais - é assim que um programa tem cinquenta ferramentas sem entulhar a
tela, e é o que resolve o aperto de hoje, em que tudo aparece ao mesmo tempo em
quatro linhas de botões.

**Somar e Tirar ficam sempre à direita**, em todas as ferramentas de seleção.
Eles saem da fila de ferramentas porque não são ferramentas: são modos que
modificam a ferramenta escolhida. Misturá-los com Retângulo e Laço fazia
parecer que se escolhe um OU outro.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QWidget,
)

from core.selecao import SOMAR, SUBTRAIR
from ui.estilo import TEXTO_FRACO
from ui.widgets.editor_selecao import (
    ESPESSURA_MAX,
    ESPESSURA_MIN,
    FERRAMENTA_COR,
    FERRAMENTA_MAO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_VARINHA,
    FERRAMENTA_ZOOM,
    FERRAMENTAS_DE_NAVEGACAO,
    NOMES_DAS_FERRAMENTAS,
    TOLERANCIA_MAX,
    TOLERANCIA_MIN,
    ZOOM_MAX,
    ZOOM_MIN,
)

ALTURA = 38          # do desenho aprovado

BOTAO_DE_MODO = """
QPushButton {{
    border: 1px solid {borda}; background: {fundo}; color: {cor};
    border-radius: 4px; padding: 2px 12px; font-size: 12px;
}}
"""


class BarraOpcoes(QFrame):
    """Uma faixa por ferramenta. Só a da ferramenta ativa fica visível."""

    tolerancia_mudou = Signal(int)
    espessura_mudou = Signal(float)
    zoom_mudou = Signal(float)
    ajustar_pedido = Signal()
    operacao_mudou = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(ALTURA)
        self.setStyleSheet(
            "QFrame { background: #fdfdfc; border-bottom: 1px solid #e6e4e0; }")

        self.linha = QHBoxLayout(self)
        self.linha.setContentsMargins(12, 0, 12, 0)
        self.linha.setSpacing(10)

        self.rotulo = QLabel("")
        self.rotulo.setStyleSheet("border: none;")
        self.linha.addWidget(self.rotulo)

        self.controles = QWidget()
        self.controles.setStyleSheet("border: none;")
        self.dentro = QHBoxLayout(self.controles)
        self.dentro.setContentsMargins(0, 0, 0, 0)
        self.dentro.setSpacing(8)
        self.linha.addWidget(self.controles)

        self.dica = QLabel("")
        self.dica.setStyleSheet(f"color: {TEXTO_FRACO}; border: none;")
        self.linha.addStretch()
        self.linha.addWidget(self.dica)
        self.linha.addStretch()

        self._montar_modos()
        self.definir_ferramenta(NOMES_DAS_FERRAMENTAS and "retangulo")

    # --- somar e tirar, sempre a direita ----------------------------------

    def _montar_modos(self) -> None:
        self.botoes_modo: dict[str, QPushButton] = {}
        for chave, texto in ((SOMAR, "somar"), (SUBTRAIR, "tirar")):
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.clicked.connect(lambda _c=False, m=chave: self._escolher_modo(m))
            self.linha.addWidget(botao)
            self.botoes_modo[chave] = botao
        self._escolher_modo(SOMAR, avisar=False)

    def _escolher_modo(self, modo: str, avisar: bool = True) -> None:
        self.operacao = modo
        for chave, botao in self.botoes_modo.items():
            escolhido = chave == modo
            botao.setStyleSheet(BOTAO_DE_MODO.format(
                borda="#378add" if escolhido else "#d3d1c7",
                fundo="#e6f1fb" if escolhido else "#ffffff",
                cor="#185fa5" if escolhido else "#5f5e5a"))
        if avisar:
            self.operacao_mudou.emit(modo)

    # --- troca de ferramenta ----------------------------------------------

    def definir_ferramenta(self, ferramenta: str) -> None:
        """Refaz a faixa para a ferramenta pedida."""
        self.ferramenta = ferramenta
        self._limpar()

        self.rotulo.setText(f"{NOMES_DAS_FERRAMENTAS.get(ferramenta, '')}:")

        if ferramenta == FERRAMENTA_COR:
            self._deslizante("variação", TOLERANCIA_MIN, TOLERANCIA_MAX, 30,
                             lambda v: self.tolerancia_mudou.emit(int(v)),
                             sufixo="média")
            self.dica.setText("a roda do mouse também muda a variação")

        elif ferramenta == FERRAMENTA_VARINHA:
            self._deslizante("tolerância", TOLERANCIA_MIN, TOLERANCIA_MAX, 30,
                             lambda v: self.tolerancia_mudou.emit(int(v)))
            self.dica.setText("a roda do mouse também muda a tolerância")

        elif ferramenta == FERRAMENTA_PINCEL:
            self._deslizante("tamanho", int(ESPESSURA_MIN * 1000),
                             int(ESPESSURA_MAX * 1000), 20,
                             lambda v: self.espessura_mudou.emit(v / 1000.0))
            self.dica.setText("a roda do mouse também muda o tamanho")

        elif ferramenta == FERRAMENTA_ZOOM:
            self._deslizante("aproximar", int(ZOOM_MIN * 100), int(ZOOM_MAX * 100),
                             100, lambda v: self.zoom_mudou.emit(v / 100.0),
                             sufixo="%")
            self._botao("ajustar à tela", self.ajustar_pedido.emit)
            self.dica.setText("clique na página para aproximar; com Alt, afasta")

        elif ferramenta == FERRAMENTA_MAO:
            self.dica.setText("arraste a página para andar por ela")

        else:
            self.dica.setText("")

        # Somar e tirar valem nas ferramentas de MARCAR, e em nenhuma das de
        # navegar: nao ha o que somar ao aproximar a pagina.
        de_marcar = ferramenta not in FERRAMENTAS_DE_NAVEGACAO
        for botao in self.botoes_modo.values():
            botao.setVisible(de_marcar)

    def _limpar(self) -> None:
        while self.dentro.count():
            item = self.dentro.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _deslizante(self, nome: str, minimo: int, maximo: int, valor: int,
                    aviso, sufixo: str = "") -> QSlider:
        rotulo = QLabel(nome)
        rotulo.setStyleSheet(f"color: {TEXTO_FRACO}; border: none;")
        self.dentro.addWidget(rotulo)

        deslizante = QSlider(Qt.Horizontal)
        deslizante.setFixedWidth(110)
        deslizante.setRange(minimo, maximo)
        deslizante.setValue(valor)
        deslizante.valueChanged.connect(aviso)
        self.dentro.addWidget(deslizante)

        if sufixo:
            fim = QLabel(sufixo)
            fim.setStyleSheet(f"color: {TEXTO_FRACO}; border: none;")
            self.dentro.addWidget(fim)
        return deslizante

    def _botao(self, texto: str, acao) -> QPushButton:
        botao = QPushButton(texto)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setStyleSheet(BOTAO_DE_MODO.format(
            borda="#d3d1c7", fundo="#ffffff", cor="#5f5e5a"))
        botao.clicked.connect(acao)
        self.dentro.addWidget(botao)
        return botao
