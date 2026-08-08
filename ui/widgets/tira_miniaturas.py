"""A tira de miniaturas do rodape da tela de conferir.

As miniaturas são geradas em segundo plano e bem pequenas (~90 px). Enquanto
não chegam, o quadro fica cinza com o número - a tela nunca espera por elas.
"""

from __future__ import annotations

import traceback

import numpy as np
from PySide6.QtCore import QObject, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array
from registro import registrar_erro
from ui.estilo import AZUL, BORDA, LARANJA, TEXTO_FRACO
from ui.widgets.visualizador import numpy_para_qimage

# A tira toda ocupa 58 px no desenho aprovado - contra os 144 de antes. Cada
# linha de altura sai da PAGINA, que e o que precisa ser olhado; a tira serve
# para achar a pagina, e para isso a miniatura nao precisa ser grande.
ALTURA_MINIATURA = 40
LARGURA_MAXIMA = 62


class _Sinais(QObject):
    pronta = Signal(int, object)


class _TarefaMiniaturas(QRunnable):
    """Gera as miniaturas de todas as folhas, em lote e em segundo plano."""

    def __init__(self, caminho_pdf: str, indices: list[int], sinais: _Sinais) -> None:
        super().__init__()
        self.caminho_pdf = caminho_pdf
        self.indices = indices
        self.sinais = sinais
        self.parar = False

    def run(self) -> None:
        try:
            doc = abrir_pdf(self.caminho_pdf)
            try:
                for indice in self.indices:
                    if self.parar:
                        return
                    img = pagina_para_array(doc, indice, dpi=20)
                    self.sinais.pronta.emit(indice, limitar_altura(img, ALTURA_MINIATURA))
            finally:
                doc.close()
        except Exception:  # noqa: BLE001
            registrar_erro("miniaturas", traceback.format_exc())


class Miniatura(QFrame):
    """Um quadrinho da tira."""

    def __init__(self, numero: int, parent=None) -> None:
        super().__init__(parent)
        self.numero = numero
        self.selecionada = False
        self.em_alerta = False
        self.apagada = False
        self._pixmap: QPixmap | None = None

        self.setFixedSize(QSize(LARGURA_MAXIMA, ALTURA_MINIATURA + 14))
        self.setCursor(Qt.PointingHandCursor)

    def definir_imagem(self, img: np.ndarray) -> None:
        self._pixmap = QPixmap.fromImage(numpy_para_qimage(img))
        self.update()

    def paintEvent(self, evento) -> None:  # noqa: N802
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        area = self.rect().adjusted(3, 3, -3, -3)
        pintor.fillRect(area, QColor("#ffffff"))

        if self._pixmap is not None:
            escalado = self._pixmap.scaled(
                area.width() - 6, ALTURA_MINIATURA - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            pintor.drawPixmap(
                area.left() + (area.width() - escalado.width()) // 2,
                area.top() + 2, escalado,
            )
        else:
            pintor.fillRect(area.adjusted(0, 0, 0, -20), QColor("#f3f4f6"))

        if self.apagada:
            pintor.fillRect(area, QColor(255, 255, 255, 165))

        # moldura: laranja quando ha alerta, azul quando selecionada
        if self.selecionada:
            cor, espessura = QColor(AZUL), 3
        elif self.em_alerta:
            cor, espessura = QColor(LARANJA), 2
        else:
            cor, espessura = QColor(BORDA), 1
        caneta = pintor.pen()
        caneta.setColor(cor)
        caneta.setWidth(espessura)
        pintor.setPen(caneta)
        pintor.drawRect(area)

        rodape = area.adjusted(0, area.height() - 18, 0, 0)
        pintor.setPen(QColor(LARANJA) if self.em_alerta else QColor(TEXTO_FRACO))
        rotulo = str(self.numero)
        if self.em_alerta:
            rotulo += "  !"
        if self.apagada:
            rotulo = "apagada"
        pintor.drawText(rodape, Qt.AlignCenter, rotulo)

    def _tira(self):
        tira = self.parent()
        while tira is not None and not isinstance(tira, TiraMiniaturas):
            tira = tira.parent()
        return tira

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira.selecionada.emit(self.numero - 1)

    def mouseDoubleClickEvent(self, evento) -> None:  # noqa: N802
        """Duplo clique abre a página em tamanho grande."""
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira.ampliar_pedido.emit(self.numero - 1)


class TiraMiniaturas(QWidget):
    """A tira inteira, com rolagem horizontal."""

    selecionada = Signal(int)
    ampliar_pedido = Signal(int)   # duplo clique numa miniatura

    def __init__(self, titulo: str, parent=None) -> None:
        super().__init__(parent)
        self._miniaturas: list[Miniatura] = []
        self._tarefa: _TarefaMiniaturas | None = None
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._receber)
        self._mapa_folha: dict[int, list[int]] = {}
        self._cortes: dict[int, tuple[str, float]] = {}

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(2)

        # O rotulo acima da tira saiu: custava 18 px e dizia o que a propria
        # cor ja diz. A explicacao das cores foi para a dica do mouse.
        self.rotulo = QLabel(titulo)
        self.rotulo.setVisible(False)
        self.setToolTip("A selecionada tem borda grossa. "
                        "As laranjas são as que eu não tive certeza.")

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFixedHeight(ALTURA_MINIATURA + 18)
        self.rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.rolagem.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        interno = QWidget()
        self.linha = QHBoxLayout(interno)
        self.linha.setContentsMargins(2, 2, 2, 2)
        self.linha.setSpacing(6)
        self.linha.addStretch()
        self.rolagem.setWidget(interno)
        fora.addWidget(self.rolagem)

    def montar(self, quantidade: int, caminho_pdf: str, folha_de: dict[int, int],
               corte_de: dict[int, tuple[str, float]] | None = None) -> None:
        """Cria os quadros e dispara a geracao das imagens.

        folha_de mapeia o indice do item (página ou folha) para a folha do PDF
        de onde ele vem - duas páginas de uma mesma folha reaproveitam a mesma
        leitura, entao o PDF e lido uma vez só por folha.

        corte_de diz, para cada página, qual metade da folha ela e. Sem isso a
        miniatura de uma página mostraria a folha dupla inteira, e o usuario
        veria a mesma imagem em duas páginas seguidas.
        """
        self.limpar()
        self._cortes = corte_de or {}

        for i in range(quantidade):
            mini = Miniatura(i + 1)
            self._miniaturas.append(mini)
            self.linha.insertWidget(self.linha.count() - 1, mini)
            self._mapa_folha.setdefault(folha_de.get(i, i), []).append(i)

        indices_de_folha = sorted(self._mapa_folha)
        self._tarefa = _TarefaMiniaturas(caminho_pdf, indices_de_folha, self._sinais)
        self._pool.start(self._tarefa)

    def limpar(self) -> None:
        if self._tarefa is not None:
            self._tarefa.parar = True
            self._tarefa = None
        for mini in self._miniaturas:
            self.linha.removeWidget(mini)
            mini.deleteLater()
        self._miniaturas.clear()
        self._mapa_folha.clear()

    def _receber(self, indice_folha: int, img: np.ndarray) -> None:
        for indice in self._mapa_folha.get(indice_folha, []):
            if 0 <= indice < len(self._miniaturas):
                self._miniaturas[indice].definir_imagem(self._metade(indice, img))

    def _metade(self, indice: int, img: np.ndarray) -> np.ndarray:
        """Recorta a metade que esta página representa."""
        dados = self._cortes.get(indice)
        if not dados:
            return img
        metade, posicao = dados
        largura = img.shape[1]
        corte = max(1, min(largura - 1, int(posicao * largura)))
        if metade == "esquerda":
            return img[:, :corte]
        if metade == "direita":
            return img[:, corte:]
        return img

    # --- estado -----------------------------------------------------------

    def marcar(self, indice: int, em_alerta: bool = False, apagada: bool = False) -> None:
        if 0 <= indice < len(self._miniaturas):
            mini = self._miniaturas[indice]
            mini.em_alerta = em_alerta
            mini.apagada = apagada
            mini.update()

    def selecionar(self, indice: int) -> None:
        for i, mini in enumerate(self._miniaturas):
            estava = mini.selecionada
            mini.selecionada = i == indice
            if estava != mini.selecionada:
                mini.update()
        if 0 <= indice < len(self._miniaturas):
            self.rolagem.ensureWidgetVisible(self._miniaturas[indice], 200, 0)

    def definir_titulo(self, texto: str) -> None:
        self.rotulo.setText(texto)

    def parar(self) -> None:
        self.limpar()
        self._pool.waitForDone(2000)
