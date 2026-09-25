"""A trilha de ferramentas: coluna estreita à esquerda, no modelo do Photoshop.

Antes as sete ferramentas eram sete botões largos numa linha atravessando a
tela, e cada linha dessas custava altura da página - que é o que a pessoa
precisa olhar. Numa coluna de 42 px elas custam largura, e largura sobra.

Cada ferramenta é um ícone com a letra do atalho embaixo. O nome inteiro
aparece ao passar o mouse. Os ícones são desenhados à mão, e não emoji: emoji
em rótulo é proibido no projeto, e depende da fonte do sistema.

Um traço fino separa as sete de MARCAR das duas de NAVEGAR. São coisas
diferentes e não devem parecer irmãs.
"""

from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QWidget

from ui.widgets.editor_selecao import (
    FERRAMENTA_COR,
    FERRAMENTA_ELIPSE,
    FERRAMENTA_LACO,
    FERRAMENTA_MAO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_POLIGONO,
    FERRAMENTA_RETANGULO,
    FERRAMENTA_VARINHA,
    FERRAMENTA_ZOOM,
    NOMES_DAS_FERRAMENTAS,
    ORDEM_DA_TRILHA,
    tecla_da_ferramenta,
)

LARGURA = 42          # do desenho aprovado
ALTURA_DO_ITEM = 46
# Abaixo disto o icone fica ilegivel; a trilha prefere apertar ate aqui e
# parar. Serve para janela baixa e para tela em 150%, onde o desenho de 46 px
# por item nao cabe.
ALTURA_MINIMA_DO_ITEM = 30
LADO_DO_ICONE = 26
LADO_MINIMO_DO_ICONE = 18

FUNDO = "#f7f5f2"
BORDA = "#e6e4e0"
TRACO = "#5f5e5a"
ESCOLHIDO_FUNDO = "#e6f1fb"
ESCOLHIDO_BORDA = "#378add"
LETRA_FRACA = "#86827c"

# Depois de qual posicao vai o traco que separa marcar de navegar.
SEPARA_DEPOIS_DE = 7


class TrilhaFerramentas(QWidget):
    """Nove ferramentas, uma sobre a outra, com a letra do atalho."""

    escolhida = Signal(str)

    def __init__(self, parent=None) -> None:
        """Comeca com o Retangulo escolhido e sem rolagem."""
        super().__init__(parent)
        self.setFixedWidth(LARGURA)
        self.setMouseTracking(True)
        self.ferramenta = FERRAMENTA_RETANGULO
        self._sob_o_mouse: str | None = None
        # Quando nem no tamanho minimo as nove cabem - janela muito baixa, ou
        # tela em 150% -, a roda do mouse rola a trilha. As nove tem de ficar
        # alcancaveis SEMPRE: as duas ultimas sao o Zoom e a Mao, e quem nao as
        # ve conclui que o programa nao tem zoom.
        self._deslocamento = 0

    # --- estado -----------------------------------------------------------

    def definir_ferramenta(self, ferramenta: str) -> None:
        """Marca a ferramenta escolhida (por fora, ex.: atalho de teclado) e redesenha."""
        if ferramenta in ORDEM_DA_TRILHA and ferramenta != self.ferramenta:
            self.ferramenta = ferramenta
            self.update()

    def _altura_do_item(self) -> int:
        """Quanto cabe por ferramenta na altura que ha.

        As nove tem de aparecer SEMPRE. Uma trilha cortada esconde justamente a
        Mao e o Zoom, que sao as duas ultimas - e a pessoa conclui que o
        programa nao tem zoom.
        """
        util = self.height() - 20 - 10          # margens e o traco separador
        cabe = util // len(ORDEM_DA_TRILHA) if util > 0 else ALTURA_DO_ITEM
        return int(max(ALTURA_MINIMA_DO_ITEM, min(ALTURA_DO_ITEM, cabe)))

    def _lado_do_icone(self) -> int:
        """Tamanho do icone, acompanhando a altura do item (com um piso legivel)."""
        return int(max(LADO_MINIMO_DO_ICONE,
                       min(LADO_DO_ICONE, self._altura_do_item() - 16)))

    def _altura_total(self) -> int:
        """Altura que a trilha inteira ocupa (margens + as nove + o traco separador)."""
        return 10 + len(ORDEM_DA_TRILHA) * self._altura_do_item() + 10 + 10

    def _rolagem_maxima(self) -> int:
        """Quanto da pra rolar (0 se a trilha inteira ja cabe na altura disponivel)."""
        return max(0, self._altura_total() - self.height())

    def _posicao_de(self, indice: int) -> int:
        """Onde o item comeca, ja contando o traco separador e a rolagem."""
        extra = 10 if indice >= SEPARA_DEPOIS_DE else 0
        return (10 + indice * self._altura_do_item() + extra
                - self._deslocamento)

    def _ferramenta_em(self, y: int) -> str | None:
        """Qual ferramenta esta desenhada na coordenada y (para clique e hover)."""
        altura = self._altura_do_item()
        for indice, ferramenta in enumerate(ORDEM_DA_TRILHA):
            topo = self._posicao_de(indice)
            if topo <= y < topo + altura:
                return ferramenta
        return None

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Desenha o fundo, a borda direita e cada ferramenta (com o traco
        separador antes do item SEPARA_DEPOIS_DE)."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(FUNDO))
        pintor.setPen(QPen(QColor(BORDA), 1))
        pintor.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        for indice, ferramenta in enumerate(ORDEM_DA_TRILHA):
            topo = self._posicao_de(indice)
            if indice == SEPARA_DEPOIS_DE:
                pintor.setPen(QPen(QColor(BORDA), 1))
                pintor.drawLine(8, topo - 6, LARGURA - 8, topo - 6)
            self._desenhar_item(pintor, ferramenta, topo)

    def _desenhar_item(self, pintor: QPainter, ferramenta: str, topo: int) -> None:
        """Um item da trilha: fundo (escolhido/hover), icone e a letra do atalho embaixo."""
        escolhida = ferramenta == self.ferramenta
        altura = self._altura_do_item()
        lado = self._lado_do_icone()

        if escolhida:
            pintor.fillRect(QRect(0, topo, LARGURA, altura), QColor(ESCOLHIDO_FUNDO))
            pintor.fillRect(QRect(0, topo, 3, altura), QColor(ESCOLHIDO_BORDA))
        elif ferramenta == self._sob_o_mouse:
            pintor.fillRect(QRect(0, topo, LARGURA, altura), QColor("#efece6"))

        cor = QColor(ESCOLHIDO_BORDA if escolhida else TRACO)
        pintor.setPen(QPen(cor, 1.4))
        pintor.setBrush(Qt.NoBrush)
        x = (LARGURA - lado) // 2
        self._desenhar_icone(pintor, ferramenta, x, topo + 3, lado)

        pintor.setPen(QColor(ESCOLHIDO_BORDA if escolhida else LETRA_FRACA))
        fonte = pintor.font()
        fonte.setPointSize(7)
        pintor.setFont(fonte)
        pintor.drawText(QRect(0, topo + lado + 4, LARGURA, 12), Qt.AlignCenter,
                        tecla_da_ferramenta(ferramenta))

    def _desenhar_icone(self, pintor: QPainter, ferramenta: str,
                        x: int, y: int, lado: int = LADO_DO_ICONE) -> None:
        """Desenha o icone de UMA ferramenta a mao (QPainterPath/linhas simples,
        nunca emoji - regra 3 do CLAUDE.md)."""
        meio = QPoint(x + lado // 2, y + lado // 2)

        if ferramenta == FERRAMENTA_RETANGULO:
            pintor.drawRoundedRect(QRect(x, y, lado, lado), 4, 4)

        elif ferramenta == FERRAMENTA_ELIPSE:
            pintor.drawEllipse(QRect(x, y, lado, lado))

        elif ferramenta == FERRAMENTA_LACO:
            pintor.drawEllipse(QRect(x, y + 3, lado, lado - 10))
            pintor.drawLine(x + 4, y + lado - 6, x + 1, y + lado)

        elif ferramenta == FERRAMENTA_POLIGONO:
            caminho = QPainterPath()
            caminho.moveTo(x + lado // 2, y)
            caminho.lineTo(x + lado, y + lado // 3)
            caminho.lineTo(x + lado - 5, y + lado)
            caminho.lineTo(x + 5, y + lado)
            caminho.lineTo(x, y + lado // 3)
            caminho.closeSubpath()
            pintor.drawPath(caminho)

        elif ferramenta == FERRAMENTA_PINCEL:
            pintor.drawLine(x + 3, y + lado - 3, x + lado - 6, y + 4)
            pintor.drawLine(x + 6, y + lado - 1, x + lado - 3, y + 7)
            pintor.drawLine(x + 3, y + lado - 3, x + 6, y + lado - 1)

        elif ferramenta == FERRAMENTA_VARINHA:
            pintor.drawLine(x + 2, y + lado - 2, x + lado - 6, y + 5)
            for dx, dy in ((0, -4), (4, 0), (3, -3)):
                pintor.drawLine(x + lado - 5 + dx, y + 4 + dy,
                                x + lado - 3 + dx, y + 6 + dy)

        elif ferramenta == FERRAMENTA_COR:
            pintor.drawLine(x + 2, y + lado - 2, x + lado - 8, y + 6)
            pintor.setBrush(QColor(ESCOLHIDO_BORDA))
            pintor.drawEllipse(QPoint(x + lado - 6, y + 6), 5, 5)
            pintor.setBrush(Qt.NoBrush)

        elif ferramenta == FERRAMENTA_ZOOM:
            raio = lado // 2 - 4
            pintor.drawEllipse(QPoint(meio.x() - 2, meio.y() - 2), raio, raio)
            pintor.drawLine(meio.x() + raio - 4, meio.y() + raio - 4,
                            x + lado, y + lado)

        elif ferramenta == FERRAMENTA_MAO:
            caminho = QPainterPath()
            caminho.moveTo(x + 5, y + lado - 4)
            caminho.lineTo(x + 5, y + 9)
            caminho.lineTo(x + 9, y + 9)
            caminho.lineTo(x + 9, y + 4)
            caminho.lineTo(x + 13, y + 4)
            caminho.lineTo(x + 13, y + 9)
            caminho.lineTo(x + 17, y + 9)
            caminho.lineTo(x + 17, y + 6)
            caminho.lineTo(x + 21, y + 6)
            caminho.lineTo(x + 21, y + lado - 4)
            pintor.drawPath(caminho)

    # --- interacao --------------------------------------------------------

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Clique na trilha escolhe a ferramenta e emite o sinal `escolhida`."""
        if evento.button() != Qt.LeftButton:
            return
        ferramenta = self._ferramenta_em(int(evento.position().y()))
        if ferramenta:
            self.definir_ferramenta(ferramenta)
            self.escolhida.emit(ferramenta)

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Realce de hover + tooltip com o nome completo e o atalho."""
        sob = self._ferramenta_em(int(evento.position().y()))
        if sob != self._sob_o_mouse:
            self._sob_o_mouse = sob
            self.update()
        if sob:
            self.setToolTip(
                f"{NOMES_DAS_FERRAMENTAS[sob]}  ({tecla_da_ferramenta(sob)})")
        else:
            self.setToolTip("")

    def wheelEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Rola a trilha quando ela nao cabe inteira (janela baixa, tela em
        150%) - ver o comentario em __init__ sobre por que isso e obrigatorio."""
        maximo = self._rolagem_maxima()
        if maximo <= 0:
            return
        passo = -evento.angleDelta().y() // 4
        self._deslocamento = max(0, min(maximo, self._deslocamento + passo))
        self.update()

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        # Ao crescer a janela, a trilha volta ao topo sozinha em vez de ficar
        # rolada com espaco em branco embaixo.
        self._deslocamento = min(self._deslocamento, self._rolagem_maxima())
        self.update()

    def leaveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Tira o realce de hover quando o mouse sai da trilha."""
        self._sob_o_mouse = None
        self.update()
