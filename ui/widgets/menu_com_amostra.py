"""A lista "com amostra": cada escolha com um desenhinho fixo, o nome, o "de fábrica" e a frase.

O QUE É
    A decisão do Samuel na rodada 10 do layout (07/10/2026, pergunta 502: "B — Menu com
    amostra"; desenho das rodadas 10 e 11, telas `16-rodada10-como-b-menu-com-amostra` e
    `17-rodada11-base-limpar-menu`): as escolhas do "Limpar a sujeira" e do "Só as letras"
    aparecem numa lista que abre, e cada item mostra um DESENHO FIXO do que aquele jeito faz
    (não a própria página: processar a página em cada jeito custaria segundos), o nome em
    negrito, "de fábrica" em verde no que vem de fábrica, e a frase do que ele faz.

COMO É FEITA
    É um QComboBox de verdade (a mesma lista de antes, com currentData, setCurrentIndex,
    findData e o sinal currentIndexChanged), só com outro desenho: o item fechado e os itens
    da lista aberta são pintados aqui. Quem já usava a lista (a tela de conferir, os testes)
    continua igual. Os detalhes de cada item (frase, "de fábrica") vão em `definir_detalhes`;
    o desenho, na função `desenhar(pintor, retangulo, valor)` dada ao criar.

    `desenho_da_limpeza` e `desenho_das_letras` são os dois desenhos de hoje (as palavras "fim,
    ali" com pontinhos de sujeira; a pagininha com texto, gravura, música e mancha).

Seguro mudar: os tamanhos (ALTURA_*, LADO_DA_AMOSTRA) e os desenhos. Arriscado: trocar o
QComboBox por outra peça (quebra quem lê currentData e os testes).
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QPointF, QRect, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QComboBox, QStyle, QStyledItemDelegate

from ui import estilo

LADO_DA_AMOSTRA = QSize(48, 34)      # o desenhinho, na lista fechada e na aberta
ALTURA_FECHADA = 46                  # a lista fechada (amostra + nome + "de fábrica")
LARGURA_MINIMA_ABERTA = 270          # a lista aberta, para a frase caber em poucas linhas
MARGEM = 8


def _amostra(pintor: QPainter, ret: QRectF) -> None:
    """O fundo branco com o risco fino em volta, onde o desenho é feito."""
    pintor.setPen(QPen(QColor("#9A9A9A"), 1))
    pintor.setBrush(QColor("#FBFAF6"))
    pintor.drawRoundedRect(ret, 3, 3)


def desenho_da_limpeza(pintor: QPainter, ret: QRectF, valor) -> None:
    """As palavras "fim, ali" com pontinhos de sujeira em volta (rodada 10).

    Sem limpeza: muitos pontinhos. Limpeza bruta: nenhum, mas o "i" fica sem pingo e a
    vírgula some (é o que ela faz). Limpeza cuidadosa: menos pontinhos quanto mais forte,
    e o pingo e a vírgula ficam."""
    from core import pontinhos_scantailor as ps

    _amostra(pintor, ret)
    bruta = valor == ps.NOSSO
    quantos = {ps.DESLIGADO: 11, ps.NOSSO: 0, ps.POUCO: 7, ps.NORMAL: 4, ps.MUITO: 1}.get(valor, 0)
    fonte = QFont("Times New Roman")
    fonte.setPixelSize(int(ret.height() * 0.42))
    pintor.setFont(fonte)
    pintor.setPen(QColor("#151515"))
    texto = "fım alı" if bruta else "fim, ali"     # sem pingo e sem vírgula na bruta
    pintor.drawText(ret, Qt.AlignCenter, texto)
    # os pontinhos, longe das letras (em cima e embaixo), sempre nos mesmos lugares
    lugares = [(0.12, 0.18), (0.83, 0.22), (0.30, 0.86), (0.66, 0.84), (0.08, 0.70),
               (0.92, 0.72), (0.48, 0.14), (0.20, 0.30), (0.75, 0.10), (0.55, 0.90),
               (0.38, 0.20)]
    pintor.setPen(Qt.NoPen)
    pintor.setBrush(QColor("#202020"))
    for fx, fy in lugares[:quantos]:
        pintor.drawEllipse(QPointF(ret.left() + fx * ret.width(), ret.top() + fy * ret.height()),
                           1.1, 1.1)


def desenho_das_letras(pintor: QPainter, ret: QRectF, valor) -> None:
    """Uma pagininha com texto, uma gravura (fica sempre), música escura e uma mancha clara
    (rodada 10): "Guardar a tinta forte" tira a mancha clara e guarda a música; "Guardar
    tudo" guarda as duas (a mancha vira cinza); "Guardar só o texto" tira as duas."""
    from core import misto

    _amostra(pintor, ret)
    x0, y0, w, h = ret.left(), ret.top(), ret.width(), ret.height()
    pintor.setPen(Qt.NoPen)
    pintor.setBrush(QColor("#222222"))
    for i, largura in enumerate((0.78, 0.70, 0.74)):
        pintor.drawRect(QRectF(x0 + 0.10 * w, y0 + (0.14 + 0.12 * i) * h, largura * w, 0.055 * h))
    # a gravura (fica sempre como no original: cor)
    pintor.setBrush(QColor("#8C5A3C"))
    pintor.drawRect(QRectF(x0 + 0.10 * w, y0 + 0.55 * h, 0.30 * w, 0.32 * h))
    if valor in (misto.FORA_REDE, misto.FORA_TUDO):
        # a música / letra grande: tinta forte
        pintor.setBrush(QColor("#111111"))
        pintor.drawRect(QRectF(x0 + 0.50 * w, y0 + 0.56 * h, 0.16 * w, 0.30 * h))
    if valor == misto.FORA_TUDO:
        # a mancha clara: fica (em cinza, como o preto e branco a deixa)
        pintor.setBrush(QColor("#8A8A8A"))
        pintor.drawEllipse(QRectF(x0 + 0.72 * w, y0 + 0.60 * h, 0.18 * w, 0.22 * h))


class _Delegado(QStyledItemDelegate):
    """Pinta cada item da lista aberta: amostra, nome em negrito, "de fábrica", frase."""

    def __init__(self, lista: "ListaComAmostra") -> None:
        super().__init__(lista)
        self.lista = lista

    def _largura_do_texto(self, opcao) -> int:
        return max(80, opcao.rect.width() - LADO_DA_AMOSTRA.width() - 3 * MARGEM)

    def sizeHint(self, opcao, indice) -> QSize:  # noqa: N802 - nome do Qt
        largura = max(LARGURA_MINIMA_ABERTA, self.lista.width())
        texto = largura - LADO_DA_AMOSTRA.width() - 3 * MARGEM
        frase = self.lista.frase(indice.row())
        fonte = QFont(self.lista.font())
        fonte.setPixelSize(11)
        altura_frase = (QFontMetrics(fonte).boundingRect(QRect(0, 0, texto, 1000),
                                                        Qt.TextWordWrap, frase).height()
                        if frase else 0)
        return QSize(largura, max(LADO_DA_AMOSTRA.height() + 2 * MARGEM, 22 + altura_frase + 2 * MARGEM))

    def paint(self, pintor: QPainter, opcao, indice) -> None:
        pintor.save()
        pintor.setRenderHint(QPainter.Antialiasing)
        ret = opcao.rect
        escolhido = bool(opcao.state & QStyle.State_Selected)
        if escolhido:
            pintor.fillRect(ret, QColor(estilo.cor("sel")))
        amostra = QRectF(ret.left() + MARGEM, ret.top() + MARGEM,
                         LADO_DA_AMOSTRA.width(), LADO_DA_AMOSTRA.height())
        self.lista.desenhar(pintor, amostra, self.lista.itemData(indice.row()))
        x = int(amostra.right()) + MARGEM
        largura = ret.right() - x - MARGEM
        _nome_e_fabrica(pintor, QRect(x, ret.top() + MARGEM - 2, largura, 18),
                        self.lista.itemText(indice.row()), self.lista.de_fabrica(indice.row()),
                        self.lista.font(), na_mesma_linha=True)
        frase = self.lista.frase(indice.row())
        if frase:
            fonte = QFont(self.lista.font())
            fonte.setPixelSize(11)
            pintor.setFont(fonte)
            pintor.setPen(QColor(estilo.cor("fraco")))
            pintor.drawText(QRect(x, ret.top() + MARGEM + 18, largura, ret.height()),
                            Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop, frase)
        if indice.row() == self.lista.currentIndex():
            # o sinal de escolhido, no canto (traço desenhado, sem símbolo de texto)
            pintor.setPen(QPen(QColor(estilo.cor("texto")), 1.6))
            cx, cy = ret.right() - 14, ret.top() + MARGEM + 7
            pintor.drawPolyline([QPointF(cx - 5, cy), QPointF(cx - 1.5, cy + 3.5), QPointF(cx + 5, cy - 4)])
        pintor.restore()


def _nome_e_fabrica(pintor: QPainter, ret: QRect, nome: str, de_fabrica: bool, base: QFont,
                    na_mesma_linha: bool) -> None:
    """O nome em negrito e, se for o caso, "de fábrica" em verde (ao lado ou embaixo)."""
    fonte = QFont(base)
    fonte.setPixelSize(13)
    fonte.setBold(True)
    pintor.setFont(fonte)
    pintor.setPen(QColor(estilo.cor("forte")))
    metricas = QFontMetrics(fonte)
    texto = metricas.elidedText(nome, Qt.ElideRight, ret.width())
    pintor.drawText(ret, Qt.AlignLeft | Qt.AlignVCenter, texto)
    if not de_fabrica:
        return
    pequena = QFont(base)
    pequena.setPixelSize(11)
    pintor.setFont(pequena)
    pintor.setPen(QColor(estilo.cor("ok")))
    if na_mesma_linha:
        x = ret.left() + metricas.horizontalAdvance(texto) + 8
        pintor.drawText(QRect(x, ret.top(), max(0, ret.right() - x), ret.height()),
                        Qt.AlignLeft | Qt.AlignVCenter, "de fábrica")
    else:
        pintor.drawText(QRect(ret.left(), ret.bottom() + 1, ret.width(), 15),
                        Qt.AlignLeft | Qt.AlignVCenter, "de fábrica")


class ListaComAmostra(QComboBox):
    """Um QComboBox que mostra cada escolha com o desenho dela (ver o começo do arquivo)."""

    def __init__(self, desenhar: Callable[[QPainter, QRectF, object], None], parent=None) -> None:
        super().__init__(parent)
        self.desenhar = desenhar
        self._frases: dict[object, str] = {}
        self._de_fabrica: set = set()
        self.setItemDelegate(_Delegado(self))
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)          # o teclado continua da página
        self.setMinimumHeight(ALTURA_FECHADA)

    def definir_detalhes(self, valor, frase: str = "", de_fabrica: bool = False) -> None:
        """A frase do que o jeito `valor` faz e se ele é o de fábrica."""
        self._frases[valor] = frase
        if de_fabrica:
            self._de_fabrica.add(valor)
        else:
            self._de_fabrica.discard(valor)
        self.update()

    def frase(self, linha: int) -> str:
        return self._frases.get(self.itemData(linha), "")

    def de_fabrica(self, linha: int) -> bool:
        return self.itemData(linha) in self._de_fabrica

    def sizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(max(180, super().sizeHint().width()), ALTURA_FECHADA)

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(120, ALTURA_FECHADA)

    def showPopup(self) -> None:  # noqa: N802 - nome do Qt
        """A lista aberta fica pelo menos LARGURA_MINIMA_ABERTA de largura (a frase cabe)."""
        self.view().setMinimumWidth(max(self.width(), LARGURA_MINIMA_ABERTA))
        super().showPopup()

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """A lista fechada: moldura de botão, a amostra do escolhido, o nome e a seta."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        ret = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        aceso = self.isEnabled()
        pintor.setPen(QPen(QColor(estilo.cor("azul") if self.underMouse() and aceso else estilo.cor("sep")), 1))
        pintor.setBrush(QColor(estilo.cor("botao")))
        pintor.drawRoundedRect(ret, 6, 6)
        linha = self.currentIndex()
        if linha < 0:
            pintor.end()
            return
        if not aceso:
            pintor.setOpacity(0.5)
        amostra = QRectF(MARGEM, (self.height() - LADO_DA_AMOSTRA.height()) / 2,
                         LADO_DA_AMOSTRA.width(), LADO_DA_AMOSTRA.height())
        self.desenhar(pintor, amostra, self.itemData(linha))
        x = int(amostra.right()) + MARGEM
        largura = self.width() - x - 28
        fabrica = self.de_fabrica(linha)
        alto = (self.height() - (32 if fabrica else 18)) // 2
        _nome_e_fabrica(pintor, QRect(x, alto, largura, 18), self.itemText(linha), fabrica,
                        self.font(), na_mesma_linha=False)
        # a seta para baixo, desenhada
        pintor.setPen(QPen(QColor(estilo.cor("texto")), 1.6))
        cx, cy = self.width() - 15, self.height() / 2
        caminho = QPainterPath(QPointF(cx - 5, cy - 2.5))
        caminho.lineTo(QPointF(cx, cy + 2.5))
        caminho.lineTo(QPointF(cx + 5, cy - 2.5))
        pintor.setBrush(Qt.NoBrush)
        pintor.drawPath(caminho)
        pintor.end()
