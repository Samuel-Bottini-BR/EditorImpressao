"""Os quatro cartoes de filtro da aba Filtro.

Cada cartao mostra a PAGINA REAL processada com aquele filtro, nunca um exemplo
generico. O usuario escolhe olhando o resultado, não lendo o nome.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui.estilo import AZUL, BORDA, TEXTO_FRACO
from ui.widgets.visualizador import numpy_para_qimage

ALTURA_AMOSTRA = 150


class CartaoFiltro(QFrame):
    """Um cartao: amostra em cima, nome e explicação embaixo."""

    escolhido = Signal(str)

    def __init__(self, filtro: str, nome: str, explicacao: str, parent=None) -> None:
        super().__init__(parent)
        self.filtro = filtro
        self.selecionado = False
        self._pixmap: QPixmap | None = None

        self.setObjectName("cartao")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumWidth(150)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(8, 8, 8, 8)
        camadas.setSpacing(4)

        self.amostra = _Amostra()
        camadas.addWidget(self.amostra, 1)

        self.rotulo_nome = QLabel(nome)
        self.rotulo_nome.setAlignment(Qt.AlignCenter)
        self.rotulo_nome.setStyleSheet("font-weight: 600; font-size: 15px;")
        camadas.addWidget(self.rotulo_nome)

        rotulo_explicacao = QLabel(explicacao)
        rotulo_explicacao.setAlignment(Qt.AlignCenter)
        rotulo_explicacao.setWordWrap(True)
        rotulo_explicacao.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
        camadas.addWidget(rotulo_explicacao)

        self._aplicar_borda()

    def definir_amostra(self, img: np.ndarray | None) -> None:
        self.amostra.definir(img)

    def definir_selecionado(self, selecionado: bool) -> None:
        if self.selecionado == selecionado:
            return
        self.selecionado = selecionado
        self._aplicar_borda()

    def _aplicar_borda(self) -> None:
        cor = AZUL if self.selecionado else BORDA
        espessura = 3 if self.selecionado else 1
        self.setStyleSheet(
            f"QFrame#cartao {{ background: white; border: {espessura}px solid {cor};"
            f" border-radius: 10px; }}"
        )
        self.rotulo_nome.setStyleSheet(
            "font-weight: 600; font-size: 15px;"
            + (f" color: {AZUL};" if self.selecionado else "")
        )

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        if evento.button() == Qt.LeftButton:
            self.escolhido.emit(self.filtro)


class _Amostra(QWidget):
    """Só a imagem, centralizada e proporcional."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(ALTURA_AMOSTRA)
        self._pixmap: QPixmap | None = None

    def definir(self, img: np.ndarray | None) -> None:
        self._pixmap = None if img is None else QPixmap.fromImage(numpy_para_qimage(img))
        self.update()

    def paintEvent(self, evento) -> None:  # noqa: N802
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform)
        pintor.fillRect(self.rect(), QColor("#f9fafb"))

        if self._pixmap is None:
            pintor.setPen(QColor(TEXTO_FRACO))
            pintor.drawText(self.rect(), Qt.AlignCenter, "preparando...")
            return

        escalado = self._pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        pintor.drawPixmap(
            (self.width() - escalado.width()) // 2,
            (self.height() - escalado.height()) // 2,
            escalado,
        )
