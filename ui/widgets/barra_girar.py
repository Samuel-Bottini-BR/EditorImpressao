"""A barrinha de girar a folha, na linha das abas, em cima da página (item 2.3).

PROVISÓRIA até o layout. Pedido do Samuel (conferência 14, G1): "(c) Os dois -
Os botões tem que existir, mas o que vai decidir como vai ser para clicar e
como vai ficar é o agente de layout comigo, mas por enquanto pode ser assim."
Exceção explícita da gerente (06/10/2026) para o implementador mexer em ui/
só para isto.

O que tem, da esquerda para a direita:

    Girar a folha:  [seta] ¼ à esquerda  [seta] ¼ à direita  [seta] meia volta
    aplicar em: [só esta  v]

- Os três botões mandam `girar_pedido(giro)` (giro em graus no sentido do
  relógio, core/girar.GIRO_*). Quem decide QUAIS folhas giram é a tela
  (ui/tela_conferir._girar_folhas), lendo `alcance()`.
- "aplicar em" é uma lista (só esta / todas / daqui em diante / só as pares /
  só as ímpares), com a setinha da lista como pista visual. Vale até a pessoa
  trocar (nesta sessão do programa); começa em "só esta", o mais seguro.
- Ícones desenhados à mão (QPainter), nunca emoji nem símbolo de fonte (regra
  do projeto: emoji quebrou no Windows; a seta de fonte depende da fonte).

Por que na linha das abas: é a única faixa em cima da página com sobra de
largura em 1280 x 657 (as abas ocupam uns 520 px de 1240) e não custa altura
nenhuma da página. Em janela estreita (a mínima é 1000 px) a barra mostra só
os ícones, com o nome no balão, em vez de empurrar as abas (definir_compacta).

Seguro mudar: textos, cores, tamanhos, a ordem dos botões.
Arriscado: o valor de `giro` de cada botão (o sentido tem de bater com
core/endireitar.girar_90 e core/zonas_na_folha) e os dados da lista
(core/girar.ALCANCES), que a tela e o menu Página usam.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QWidget

from core.girar import (
    ALCANCE_ESTA,
    ALCANCES,
    GIRO_DIREITA,
    GIRO_ESQUERDA,
    GIRO_MEIA_VOLTA,
    NOMES_DOS_ALCANCES,
    NOMES_DOS_GIROS,
)
from ui import estilo

LADO_DO_ICONE = 18

def _estilo() -> str:
    """A folha da barrinha, com as cores do tema da vez (ui/estilo.py)."""
    return f"""
QPushButton {{
    background: {estilo.FUNDO_CARTAO};
    border: 1px solid {estilo.BORDA};
    border-radius: 6px;
    padding: 4px 9px;
    font-size: 13px;
}}
QPushButton:hover {{ border-color: {estilo.AZUL}; }}
QPushButton:pressed {{ background: {estilo.AZUL_CLARO}; }}
QComboBox {{ padding: 3px 8px; font-size: 13px; }}
QLabel {{ color: {estilo.TEXTO_FRACO}; font-size: 13px; background: transparent; }}
"""


def icone_de_giro(giro: int, cor: str | None = None) -> QIcon:
    """Seta curva desenhada à mão: 3/4 de círculo para os quartos de volta
    (a ponta mostra o sentido) e meio círculo com ponta para a meia volta.
    Sem `cor`, usa a cor do texto do tema da vez."""
    cor = cor or estilo.TEXTO
    escala = 3
    lado = LADO_DO_ICONE * escala
    pixmap = QPixmap(lado, lado)
    pixmap.fill(Qt.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.Antialiasing)
    caneta = QPen(QColor(cor), 2.0 * escala)
    caneta.setCapStyle(Qt.RoundCap)
    p.setPen(caneta)
    margem = 4.0 * escala
    caixa = QRectF(margem, margem, lado - 2 * margem, lado - 2 * margem)
    centro, raio = caixa.center(), caixa.width() / 2

    # Angulos do Qt: em graus, 0 = 3 horas, positivo = contra o relogio.
    if giro == GIRO_MEIA_VOLTA:
        inicio, varredura = 180.0, -180.0            # de 9 h, por cima, ate 3 h
    elif giro == GIRO_ESQUERDA:
        inicio, varredura = 0.0, 270.0               # contra o relogio
    else:
        inicio, varredura = 180.0, -270.0            # a favor do relogio
    caminho = QPainterPath()
    caminho.arcMoveTo(caixa, inicio)
    caminho.arcTo(caixa, inicio, varredura)
    p.drawPath(caminho)

    # a ponta da seta, no fim do arco, apontando no sentido do giro
    fim = math.radians(inicio + varredura)
    ponta = QPointF(centro.x() + raio * math.cos(fim), centro.y() - raio * math.sin(fim))
    sentido = -1.0 if varredura < 0 else 1.0
    # tangente do arco no fim (no sentido em que ele anda), em coordenadas de tela
    tx, ty = -math.sin(fim) * sentido, -math.cos(fim) * sentido
    tamanho = 5.6 * escala
    nx, ny = -ty, tx
    base = QPointF(ponta.x() - tx * tamanho, ponta.y() - ty * tamanho)
    seta = QPainterPath()
    seta.moveTo(ponta.x() + tx * 1.0, ponta.y() + ty * 1.0)
    seta.lineTo(base.x() + nx * tamanho * 0.7, base.y() + ny * tamanho * 0.7)
    seta.lineTo(base.x() - nx * tamanho * 0.7, base.y() - ny * tamanho * 0.7)
    seta.closeSubpath()
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(cor))
    p.drawPath(seta)
    p.end()
    pixmap.setDevicePixelRatio(escala)
    return QIcon(pixmap)


class BarraGirar(QWidget):
    """Três botões de girar e o "aplicar em". Só avisa; quem gira é a tela."""

    girar_pedido = Signal(int)        # giro em graus, sentido do relogio
    alcance_mudou = Signal(str)       # core/girar.ALCANCE_*

    def __init__(self, parent=None) -> None:
        """Monta a barra com "só esta" escolhido."""
        super().__init__(parent)
        self.setObjectName("barraGirar")
        # a troca de tema refaz a folha e, por ela, os ícones (changeEvent)
        estilo.estilizar(self, _estilo)
        # do tamanho do que tem dentro, nunca mais: a sobra da linha e das abas
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(0, 0, 0, 2)
        linha.setSpacing(5)

        self.rotulo = QLabel("Girar a folha:")
        linha.addWidget(self.rotulo)

        self.botoes_de_giro: dict[int, QPushButton] = {}
        self._textos: dict[int, str] = {}
        for giro in (GIRO_ESQUERDA, GIRO_DIREITA, GIRO_MEIA_VOLTA):
            texto = NOMES_DOS_GIROS[giro]
            botao = QPushButton(texto)
            botao.setIcon(icone_de_giro(giro))
            botao.setIconSize(QSize(LADO_DO_ICONE, LADO_DO_ICONE))
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)      # nao rouba as setas do teclado
            botao.clicked.connect(lambda *_, g=giro: self.girar_pedido.emit(g))
            linha.addWidget(botao)
            self.botoes_de_giro[giro] = botao
            self._textos[giro] = texto

        self.rotulo_alcance = QLabel("aplicar em:")
        linha.addSpacing(4)
        linha.addWidget(self.rotulo_alcance)
        self.combo_alcance = QComboBox()
        self.combo_alcance.setFocusPolicy(Qt.NoFocus)
        self.combo_alcance.setCursor(Qt.PointingHandCursor)
        for alcance in ALCANCES:
            self.combo_alcance.addItem(NOMES_DOS_ALCANCES[alcance], alcance)
        # a dica explica a regra do "aplicar em" (decisao do Samuel,
        # 06/10/2026: as escolhidas copiam o giro da folha da vez)
        self.combo_alcance.setToolTip(
            "Em quais folhas o giro vale. Todas ficam viradas como esta folha.")
        self.combo_alcance.currentIndexChanged.connect(
            lambda *_: self.alcance_mudou.emit(self.alcance()))
        linha.addWidget(self.combo_alcance)
        self._compacta = False
        self.definir_teclas({})

    def changeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Troca de tema (folha nova): os ícones desenhados à mão ganham a cor
        do texto do tema novo."""
        super().changeEvent(evento)
        from PySide6.QtCore import QEvent
        if evento.type() == QEvent.StyleChange and hasattr(self, "botoes_de_giro"):
            for giro, botao in self.botoes_de_giro.items():
                botao.setIcon(icone_de_giro(giro))

    # --- estado -----------------------------------------------------------

    def alcance(self) -> str:
        """Onde o próximo giro vale (core/girar.ALCANCE_*)."""
        valor = self.combo_alcance.currentData()
        return valor if valor in ALCANCES else ALCANCE_ESTA

    def definir_alcance(self, alcance: str) -> None:
        """Escolhe o "aplicar em" por fora (o menu Página)."""
        indice = self.combo_alcance.findData(alcance)
        if indice >= 0 and indice != self.combo_alcance.currentIndex():
            self.combo_alcance.setCurrentIndex(indice)

    def definir_teclas(self, teclas: dict[int, str]) -> None:
        """Põe a tecla de cada giro no balão do botão (vem do menu Página,
        que é quem tem os atalhos; ver ui/barra_de_menu.py)."""
        for giro, botao in self.botoes_de_giro.items():
            tecla = teclas.get(giro, "")
            dica = f"Girar {self._textos[giro]}"
            botao.setToolTip(f"{dica}  ({tecla})" if tecla else dica)

    # --- tamanho ----------------------------------------------------------

    def largura_com_texto(self) -> int:
        """A largura que a barra pede com o nome escrito nos botões."""
        compacta = self._compacta
        self.definir_compacta(False)
        largura = self.sizeHint().width()
        self.definir_compacta(compacta)
        return largura

    def definir_compacta(self, compacta: bool) -> None:
        """Janela estreita: só os ícones (o nome continua no balão). Quem
        decide é a tela (ui/tela_conferir._acertar_a_barra_girar), que sabe
        quanto sobra ao lado das abas."""
        self._compacta = bool(compacta)
        for giro, botao in self.botoes_de_giro.items():
            botao.setText("" if compacta else self._textos[giro])
        self.rotulo.setVisible(not compacta)
