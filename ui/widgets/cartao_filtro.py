"""Os quatro cartoes de filtro da aba Filtro.

Cada cartao mostra a PAGINA REAL processada com aquele filtro, nunca um exemplo
generico. O usuario escolhe olhando o resultado, não lendo o nome.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
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

    def definir_marcas(self, caixas) -> None:
        """As marcas do aviso (12/10/2026): retângulos laranja por cima da
        amostra, mostrando ONDE está o problema ("onde sumiu, tem que aparecer
        selecionado automaticamente", Samuel, rodada 5 do "Para revisar").
        caixas: lista de (x0, y0, x1, y1) em fração da página; vazia tira."""
        self.amostra.definir_marcas(caixas)

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
        self._marcas: list = []

    def definir(self, img: np.ndarray | None) -> None:
        """Guarda o array numpy como QPixmap e pede um redesenho."""
        self._pixmap = None if img is None else QPixmap.fromImage(numpy_para_qimage(img))
        self.update()

    def definir_marcas(self, caixas) -> None:
        """Guarda as marcas do aviso (ver CartaoFiltro.definir_marcas); só
        redesenha se mudaram."""
        novas = [tuple(c) for c in (caixas or [])]
        if novas != self._marcas:
            self._marcas = novas
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
        # juncao de 23/10/2026: o desenho nitido do layout (pixels de verdade)
        # e as marcas do aviso do "Para revisar", em pontos de tela
        largura = round(escalado.width() / razao)
        altura = round(escalado.height() / razao)
        x = round((self.width() - largura) / 2)
        y = round((self.height() - altura) / 2)
        pintor.drawPixmap(x, y, escalado)
        pintar_marcas(pintor, self._marcas, x, y, largura, altura)


# A cor das marcas do aviso: o laranja dos avisos ("elas já vão aparecer
# laranjas", Samuel, rodada 4 do "Para revisar"). Provisória: a aparência é
# do agente de layout.
COR_DA_MARCA = QColor(230, 126, 34)


def pintar_marcas(pintor: QPainter, caixas, x: int, y: int, largura: int, altura: int) -> None:
    """Desenha as marcas do aviso (caixas em fração da página) por cima de uma
    imagem que está em (x, y) com `largura` x `altura` pontos de tela:
    contorno laranja tracejado, sem preencher (o que está embaixo tem de
    continuar à vista). Usada pelos cartões de filtro e pela aba Marcar."""
    if not caixas or largura <= 0 or altura <= 0:
        return
    pintor.save()
    caneta = QPen(COR_DA_MARCA, 2, Qt.DashLine)
    pintor.setPen(caneta)
    pintor.setBrush(Qt.NoBrush)
    for x0, y0, x1, y1 in caixas:
        pintor.drawRect(int(x + x0 * largura), int(y + y0 * altura),
                        max(3, int((x1 - x0) * largura)), max(3, int((y1 - y0) * altura)))
    pintor.restore()
