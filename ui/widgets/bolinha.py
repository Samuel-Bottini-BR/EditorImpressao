"""A bolinha de carregamento da barra de baixo (etapa 9b-2 da obra, 27/10/2026).

O QUE O SAMUEL DECIDIU (docs/plano/DECISOES.md)
    D-064 (22/10/2026, `pr-tela-engana`): "não precisa do mostrado como sai no pdf, é só colocar uma
    bolinha de carregamento, pode ter uma pro livro inteiro e outra para a pagina que estamos,
    quando passsamos o mouse em cima mostra a mensagem de porcentagem e quantas paginas carregaram
    já." D-473 (escolha da gerente apoiada em D-066, "precisamos que o pdf saia que nem está na
    tela"): enquanto a imagem do PDF não fica pronta, a tela mostra a prévia com a bolinha.

O QUE FAZ
    Um círculo pequeno que gira enquanto `carregando` é verdadeiro (um arco que anda, como as
    bolinhas de carregar das páginas da internet). Parada, não desenha nada (o lugar fica, para a
    barra não pular). O texto do balão (o "%" e quantas páginas) é posto por quem a usa
    (ui/tela_conferir._acertar_as_bolinhas).

Seguro mudar: tamanho, cor, velocidade. Arriscado: pôr o relógio para girar com ela parada (gasta
processador à toa).
"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui import estilo

LADO = 14            # pontos
PASSO_GRAUS = 30     # quanto o arco anda a cada tique
TIQUE_MS = 80


class BolinhaDeCarregamento(QWidget):
    """Ver o começo do arquivo."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(QSize(LADO, LADO))
        self.carregando = False
        self._angulo = 0
        self._relogio = QTimer(self)
        self._relogio.setInterval(TIQUE_MS)
        self._relogio.timeout.connect(self._andar)

    def definir(self, carregando: bool, dica: str = "") -> None:
        """Liga (gira) ou desliga (some) a bolinha e põe o texto do balão."""
        carregando = bool(carregando)
        if dica != self.toolTip():
            self.setToolTip(dica)
        if carregando == self.carregando:
            return
        self.carregando = carregando
        if carregando:
            self._relogio.start()
        else:
            self._relogio.stop()
        self.update()

    def _andar(self) -> None:
        self._angulo = (self._angulo + PASSO_GRAUS) % 360
        self.update()

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        if not self.carregando:
            return
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        area = QRectF(2, 2, LADO - 4, LADO - 4)
        fundo = QPen(QColor(estilo.cor("desligado")), 2)
        pintor.setPen(fundo)
        pintor.drawEllipse(area)
        arco = QPen(QColor(estilo.cor("azul")), 2)
        arco.setCapStyle(Qt.RoundCap)
        pintor.setPen(arco)
        pintor.drawArc(area, -self._angulo * 16, 100 * 16)
