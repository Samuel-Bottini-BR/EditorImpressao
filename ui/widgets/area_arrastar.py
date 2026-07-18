"""A área de arrastar o PDF da tela de inicio."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QFileDialog, QWidget

from ui.estilo import AZUL, AZUL_CLARO, BORDA, TEXTO, TEXTO_FRACO


class AreaArrastar(QWidget):
    """Aceita arrastar-e-soltar e tambem clique para procurar."""

    arquivo_escolhido = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(210)
        self.setCursor(Qt.PointingHandCursor)
        self._por_cima = False

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento) -> None:  # noqa: N802
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        area = self.rect().adjusted(2, 2, -2, -2)
        pintor.setBrush(QColor(AZUL_CLARO if self._por_cima else "#ffffff"))
        pintor.setPen(QPen(QColor(AZUL if self._por_cima else BORDA), 2, Qt.DashLine))
        pintor.drawRoundedRect(area, 14, 14)

        # icone de arquivo desenhado a mao: nada de emoji (regra 3.4)
        centro_x = self.width() // 2
        topo = self.height() // 2 - 62
        self._desenhar_icone_arquivo(pintor, centro_x, topo)

        pintor.setPen(QColor(TEXTO))
        fonte = pintor.font()
        fonte.setPointSize(13)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.drawText(
            self.rect().adjusted(0, 28, 0, 0), Qt.AlignHCenter | Qt.AlignVCenter,
            "Arraste o PDF do livro aqui",
        )

        fonte.setBold(False)
        fonte.setPointSize(11)
        pintor.setFont(fonte)
        pintor.setPen(QColor(TEXTO_FRACO))
        pintor.drawText(
            self.rect().adjusted(0, 78, 0, 0), Qt.AlignHCenter | Qt.AlignVCenter,
            "ou clique para procurar",
        )

    def _desenhar_icone_arquivo(self, pintor: QPainter, cx: int, topo: int) -> None:
        largura, altura, dobra = 46, 58, 14
        x, y = cx - largura // 2, topo

        pintor.setPen(QPen(QColor(AZUL), 2))
        pintor.setBrush(QColor("#ffffff"))

        from PySide6.QtGui import QPainterPath

        caminho = QPainterPath()
        caminho.moveTo(x, y)
        caminho.lineTo(x + largura - dobra, y)
        caminho.lineTo(x + largura, y + dobra)
        caminho.lineTo(x + largura, y + altura)
        caminho.lineTo(x, y + altura)
        caminho.closeSubpath()
        pintor.drawPath(caminho)

        pintor.drawLine(x + largura - dobra, y, x + largura - dobra, y + dobra)
        pintor.drawLine(x + largura - dobra, y + dobra, x + largura, y + dobra)

        pintor.setPen(QPen(QColor(AZUL), 2))
        for i in range(3):
            linha_y = y + 26 + i * 9
            pintor.drawLine(x + 10, linha_y, x + largura - 10, linha_y)

    # --- interacao --------------------------------------------------------

    def dragEnterEvent(self, evento) -> None:  # noqa: N802
        if self._pdf_de(evento):
            evento.acceptProposedAction()
            self._por_cima = True
            self.update()

    def dragLeaveEvent(self, evento) -> None:  # noqa: N802
        self._por_cima = False
        self.update()

    def dropEvent(self, evento) -> None:  # noqa: N802
        self._por_cima = False
        self.update()
        caminho = self._pdf_de(evento)
        if caminho:
            self.arquivo_escolhido.emit(caminho)

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        if evento.button() != Qt.LeftButton:
            return
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Escolha o PDF do livro", str(Path.home()), "Arquivos PDF (*.pdf)"
        )
        if caminho:
            self.arquivo_escolhido.emit(caminho)

    @staticmethod
    def _pdf_de(evento) -> str | None:
        dados = evento.mimeData()
        if not dados.hasUrls():
            return None
        for url in dados.urls():
            caminho = url.toLocalFile()
            if caminho.lower().endswith(".pdf"):
                return caminho
        return None
