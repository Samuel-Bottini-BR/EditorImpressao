"""Os quatro cartoes de filtro da aba Filtro.

Cada cartao mostra a PAGINA REAL processada com aquele filtro, nunca um exemplo
generico. O usuario escolhe olhando o resultado, não lendo o nome.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from ui import estilo
from ui.widgets.visualizador import numpy_para_qimage

ALTURA_AMOSTRA = 150


class CartaoFiltro(QFrame):
    """Um cartao: amostra em cima, nome e explicação embaixo."""

    escolhido = Signal(str)
    ampliar_pedido = Signal(str)   # clicar no cartão abre a página ampliada
    # Etapa 4 do layout (20/10/2026): a mesma amostra vai também para a fila
    # de filtros do painel "Filtro da página" (o filtro e a imagem, ou None)
    amostra_mudou = Signal(str, object)

    def __init__(self, filtro: str, nome: str, explicacao: str, parent=None) -> None:
        super().__init__(parent)
        self.filtro = filtro
        self.selecionado = False
        self._pixmap: QPixmap | None = None
        self.ultima_amostra = None

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
        estilo.estilizar(rotulo_explicacao, lambda: f"color: {estilo.TEXTO_FRACO}; font-size: 12px;")
        camadas.addWidget(rotulo_explicacao)

        self._aplicar_borda()

    def definir_amostra(self, img: np.ndarray | None) -> None:
        """Poe (ou tira, com None) a imagem mostrada no cartao. None mostra
        "preparando..." - ver _Amostra.paintEvent. Avisa a fila do painel
        Filtro (amostra_mudou)."""
        self.amostra.definir(img)
        self.ultima_amostra = img           # a tela cheia dos filtros começa com ela
        self.amostra_mudou.emit(self.filtro, img)

    def definir_selecionado(self, selecionado: bool) -> None:
        """Liga/desliga a borda azul de destaque. Nao redesenha a toa se o
        estado nao mudou."""
        if self.selecionado == selecionado:
            return
        self.selecionado = selecionado
        self._aplicar_borda()

    def _aplicar_borda(self) -> None:
        """Redesenha o estilo do cartão (borda + cor do nome) conforme selecionado."""
        selecionado = self.selecionado
        espessura = 3 if selecionado else 1
        estilo.estilizar(self, lambda: (
            f"QFrame#cartao {{ background: {estilo.cor('painel')};"
            f" border: {espessura}px solid {estilo.AZUL if selecionado else estilo.BORDA};"
            f" border-radius: 10px; }}"))
        estilo.estilizar(self.rotulo_nome, lambda: (
            "font-weight: 600; font-size: 15px; background: transparent;"
            + (f" color: {estilo.cor('forte')};" if selecionado else "")))

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        """Clicar escolhe o filtro E abre a página ampliada.

        As duas coisas juntas de propósito: quem clica num cartão quer ver
        aquele filtro de perto. A escolha vem primeiro para a tela ampliada
        já abrir com o filtro certo.
        """
        if evento.button() == Qt.LeftButton:
            self.escolhido.emit(self.filtro)
            self.ampliar_pedido.emit(self.filtro)


class _Amostra(QWidget):
    """Só a imagem, centralizada e proporcional."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(ALTURA_AMOSTRA)
        self._pixmap: QPixmap | None = None

    def definir(self, img: np.ndarray | None) -> None:
        """Guarda o array numpy como QPixmap e pede um redesenho."""
        self._pixmap = None if img is None else QPixmap.fromImage(numpy_para_qimage(img))
        self.update()

    def paintEvent(self, evento) -> None:  # noqa: N802
        """Desenha a amostra centralizada e proporcional, ou "preparando..." se
        ainda nao chegou."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform)
        pintor.fillRect(self.rect(), QColor(estilo.cor("painel")))

        if self._pixmap is None:
            pintor.setPen(QColor(estilo.TEXTO_FRACO))
            pintor.drawText(self.rect(), Qt.AlignCenter, "preparando...")
            return

        # nos pixels de verdade (escala do Windows), para não sair mole
        from ui.widgets.todas_as_paginas import razao_do_pintor
        razao = razao_do_pintor(pintor)
        escalado = self._pixmap.scaled(
            self.size() * razao, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        escalado.setDevicePixelRatio(razao)
        pintor.drawPixmap(
            round((self.width() - escalado.width() / razao) / 2),
            round((self.height() - escalado.height() / razao) / 2),
            escalado,
        )
