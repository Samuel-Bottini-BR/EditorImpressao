"""Girar a folha: o bloco do painel Propriedades e os botões do canto da página.

Pedido do Samuel (conferência 14, G1): "(c) Os dois - Os botões tem que
existir, mas o que vai decidir como vai ser para clicar e como vai ficar é o
agente de layout comigo". O lugar foi decidido no layout:

  - rodada 12, 703 ("Quero a opção B e D"): girar em DOIS lugares, um bloco
    "Girar a folha" no alto do painel Propriedades e botões pequenos no canto
    de cima da área da página;
  - rodada 13, 803 B ("Só no painel"): a lista "aplicar em" fica só no bloco
    do painel; os botões do canto giram sempre SÓ ESTA folha.

Antes (etapa 2 do layout) a barrinha morava na ponta da linha dos menus, um
lugar provisório. As duas peças:

    BarraGirar (no painel Propriedades, em todas as ferramentas)
        Girar a folha
        [seta] ¼ à esquerda   [seta] ¼ à direita
        [seta] meia volta     aplicar em: [só esta folha  v]

    GirarDoCanto (por cima do canto direito de cima da área da página)
        [seta] [seta] [seta]          <- só esta folha, sempre

- Os botões mandam `girar_pedido(giro)` (giro em graus no sentido do relógio,
  core/girar.GIRO_*). Quem decide QUAIS folhas giram é a tela
  (ui/tela_conferir._girar_folhas): as do `alcance()` para o bloco do painel
  e para o menu Página; só a da vez para os botões do canto.
- "aplicar em" é uma lista (só esta folha / todas as folhas / daqui em diante
  / só as pares / só as ímpares; as palavras dizem "folha" desde a rodada 12
  do layout, 709 B: ver nomes_dos_alcances), com a setinha da lista como
  pista visual. Vale até a pessoa trocar (nesta sessão do programa); começa
  em "só esta folha", o mais seguro.
- Ícones desenhados à mão (QPainter), nunca emoji nem símbolo de fonte (regra
  do projeto: emoji quebrou no Windows; a seta de fonte depende da fonte).

Seguro mudar: textos, cores, tamanhos, a ordem dos botões.
Arriscado: o valor de `giro` de cada botão (o sentido tem de bater com
core/endireitar.girar_90 e core/zonas_na_folha) e os dados da lista
(core/girar.ALCANCES), que a tela e o menu Página usam.
"""

from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.girar import (
    ALCANCE_ESTA,
    ALCANCE_TODAS,
    ALCANCES,
    GIRO_DIREITA,
    GIRO_ESQUERDA,
    GIRO_MEIA_VOLTA,
    NOMES_DOS_ALCANCES,
    NOMES_DOS_GIROS,
)
from ui import estilo

LADO_DO_ICONE = 18


def nomes_dos_alcances(coisa: str) -> dict[str, str]:
    """As palavras de uma lista "aplicar em", dizendo o que ela conta.

    Decisão do Samuel (rodada 12 do layout, 709 B, 12/10/2026): "As palavras
    dentro da lista dizem folha ou página". Há duas listas com o mesmo nome:
    a do girar conta FOLHAS e a do endireitar conta PÁGINAS. `coisa` é
    "folha" ou "página": "só esta folha", "todas as folhas"... As outras
    três palavras ("daqui em diante", "só as pares", "só as ímpares") ficam
    como estavam (a rodada 13 ainda pergunta sobre elas).

    Só muda o texto na tela: os códigos (core/girar.ALCANCES), que são o que
    o programa usa e grava, são os mesmos. Seguro mudar: as palavras.
    """
    nomes = dict(NOMES_DOS_ALCANCES)
    nomes[ALCANCE_ESTA] = f"só esta {coisa}"
    nomes[ALCANCE_TODAS] = f"todas as {coisa}s"
    return nomes

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
QLabel#secaoDoPainel {{ font-size: 12px; font-weight: 600; }}
"""


def _estilo_do_canto() -> str:
    """A folha dos botões do canto da página: uma caixinha com a cor do
    painel e três botões só com o ícone."""
    return f"""
QFrame#girarDoCanto {{
    background: {estilo.cor("painel")};
    border: 1px solid {estilo.BORDA};
    border-radius: 8px;
}}
QPushButton {{
    background: {estilo.FUNDO_CARTAO};
    border: 1px solid {estilo.BORDA};
    border-radius: 5px;
    padding: 0px;
}}
QPushButton:hover {{ border-color: {estilo.AZUL}; }}
QPushButton:pressed {{ background: {estilo.AZUL_CLARO}; }}
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
    """O bloco "Girar a folha" do painel Propriedades: os três botões com o
    nome e o "aplicar em". Só avisa; quem gira é a tela."""

    girar_pedido = Signal(int)        # giro em graus, sentido do relogio
    alcance_mudou = Signal(str)       # core/girar.ALCANCE_*

    def __init__(self, parent=None) -> None:
        """Monta o bloco com "só esta folha" escolhido."""
        super().__init__(parent)
        self.setObjectName("barraGirar")
        # a troca de tema refaz a folha e, por ela, os ícones (changeEvent)
        estilo.estilizar(self, _estilo)
        coluna = QVBoxLayout(self)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(6)

        self.rotulo = QLabel("Girar a folha")
        self.rotulo.setObjectName("secaoDoPainel")
        coluna.addWidget(self.rotulo)

        primeira = QHBoxLayout()
        primeira.setSpacing(6)
        segunda = QHBoxLayout()
        segunda.setSpacing(6)
        coluna.addLayout(primeira)
        coluna.addLayout(segunda)

        self.botoes_de_giro: dict[int, QPushButton] = {}
        self._textos: dict[int, str] = {}
        for giro, linha in ((GIRO_ESQUERDA, primeira), (GIRO_DIREITA, primeira),
                            (GIRO_MEIA_VOLTA, segunda)):
            texto = NOMES_DOS_GIROS[giro]
            botao = QPushButton(texto)
            botao.setIcon(icone_de_giro(giro))
            botao.setIconSize(QSize(LADO_DO_ICONE, LADO_DO_ICONE))
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)      # nao rouba as setas do teclado
            botao.clicked.connect(lambda *_, g=giro: self.girar_pedido.emit(g))
            linha.addWidget(botao, 0 if giro == GIRO_MEIA_VOLTA else 1)
            self.botoes_de_giro[giro] = botao
            self._textos[giro] = texto

        self.rotulo_alcance = QLabel("aplicar em:")
        segunda.addSpacing(4)
        segunda.addWidget(self.rotulo_alcance)
        self.combo_alcance = QComboBox()
        self.combo_alcance.setFocusPolicy(Qt.NoFocus)
        self.combo_alcance.setCursor(Qt.PointingHandCursor)
        # rodada 12 do layout, 709 B: a lista do girar diz FOLHA
        nomes = nomes_dos_alcances("folha")
        for alcance in ALCANCES:
            self.combo_alcance.addItem(nomes[alcance], alcance)
        # a dica explica a regra do "aplicar em" (decisao do Samuel,
        # 06/10/2026: as escolhidas copiam o giro da folha da vez)
        self.combo_alcance.setToolTip(
            "Em quais folhas o giro vale. Todas ficam viradas como esta folha.")
        self.combo_alcance.currentIndexChanged.connect(
            lambda *_: self.alcance_mudou.emit(self.alcance()))
        segunda.addWidget(self.combo_alcance, 1)
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


class GirarDoCanto(QFrame):
    """Os três botões pequenos de girar, por cima do canto direito de cima da
    área da página (rodada 12, 703 D). Giram sempre SÓ ESTA folha (rodada 13,
    803 B: a lista "aplicar em" fica só no painel Propriedades). Só avisa
    (`girar_pedido`); quem gira e quem põe a peça no canto é a tela."""

    girar_pedido = Signal(int)        # giro em graus, sentido do relogio

    LADO_DO_BOTAO = (30, 24)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("girarDoCanto")
        self.setAttribute(Qt.WA_StyledBackground, True)
        estilo.estilizar(self, _estilo_do_canto)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(7, 6, 7, 6)
        linha.setSpacing(3)
        self.botoes_de_giro: dict[int, QPushButton] = {}
        for giro in (GIRO_ESQUERDA, GIRO_DIREITA, GIRO_MEIA_VOLTA):
            botao = QPushButton()
            botao.setFixedSize(*self.LADO_DO_BOTAO)
            botao.setIcon(icone_de_giro(giro))
            botao.setIconSize(QSize(LADO_DO_ICONE - 2, LADO_DO_ICONE - 2))
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)      # nao rouba as setas do teclado
            botao.clicked.connect(lambda *_, g=giro: self.girar_pedido.emit(g))
            linha.addWidget(botao)
            self.botoes_de_giro[giro] = botao
        self.definir_teclas({})
        self.adjustSize()

    def changeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Troca de tema: os ícones ganham a cor do texto do tema novo."""
        super().changeEvent(evento)
        from PySide6.QtCore import QEvent
        if evento.type() == QEvent.StyleChange and hasattr(self, "botoes_de_giro"):
            for giro, botao in self.botoes_de_giro.items():
                botao.setIcon(icone_de_giro(giro))

    def definir_teclas(self, teclas: dict[int, str]) -> None:
        """O balão de cada botão: o que faz, que é só nesta folha, e a tecla."""
        for giro, botao in self.botoes_de_giro.items():
            tecla = teclas.get(giro, "")
            dica = f"Girar {NOMES_DOS_GIROS[giro]} (só esta folha)"
            botao.setToolTip(f"{dica}  ({tecla})" if tecla else dica)
