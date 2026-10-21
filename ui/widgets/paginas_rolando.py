"""As páginas do livro, uma embaixo da outra, para folhear o livro aberto (etapa 7 do layout).

O QUE O SAMUEL DECIDIU
    Rodada 6 (05/10) e página de escolhas (06/10): o livro aberto, na tela inteira, com as "páginas
    rolando, uma embaixo da outra, com a coluna de miniaturas (proposta 1)", e o pedido: "quero ter a
    opção de clicar e ver como ia ficar as paginas lado a lado ... como opção um botão". Rodada 7:
    o botão "Ver lado a lado" fica em cima das páginas, no canto direito (201 B), e ligado mostra os
    pares rolando, um embaixo do outro (202 A), com a página 1 sozinha à direita, como num livro.

COMO FUNCIONA (e o que é arriscado mudar)
    Mostra as folhas COMO ESTÃO NO PDF (sem filtro, sem dividir), como o folhear de antes
    (ui/widgets/folhear_pdf.py). Uma folha só é desenhada quando aparece na tela, em segundo plano
    (uma por vez, abrindo e fechando o PDF a cada folha, como a tira de miniaturas: o arquivo nunca
    fica preso); as desenhadas ficam guardadas até MAXIMO_GUARDADAS (as mais longe saem). Assim um
    livro de 1000 folhas não enche a memória. Arriscado: desenhar no fio da tela (trava) ou guardar
    todas (memória).
"""

from __future__ import annotations

import traceback
from collections import OrderedDict

from PySide6.QtCore import QObject, QRect, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QScrollArea, QWidget

from registro import registrar_erro
from ui import estilo
from ui.widgets.visualizador import numpy_para_qimage

# A folha é desenhada na resolução de que a tela precisa: a largura mostrada
# (em pontos) vezes a escala do Windows (125%, 150%...), com uma folga. Antes
# era 70 DPI fixo, e numa folha pequena (o Boécio) a página de 350 pontos saía
# aumentada de uma imagem menor, borrada (verificador, 21/10/2026). Os limites
# seguram o tempo de desenhar e a memória.
DPI_MINIMO, DPI_MAXIMO = 40, 220
FOLGA_DE_NITIDEZ = 1.05
MAXIMO_GUARDADAS = 40          # folhas desenhadas guardadas (~0,5 MB cada)
LARGURA_UMA = 350              # o desenho da rodada 6: 350 x 497 em 1280 x 657
LARGURA_PAR = 300              # rodada 7: cada página do par com 300
ESPACO = 18


class _Sinais(QObject):
    pronta = Signal(int, object)


class _Tarefa(QRunnable):
    def __init__(self, caminho: str, indice: int, dpi: float, sinais: _Sinais) -> None:
        super().__init__()
        self.caminho, self.indice, self.dpi, self.sinais = caminho, indice, dpi, sinais

    def run(self) -> None:
        from core.pdf_io import abrir_pdf, pagina_para_array
        try:
            doc = abrir_pdf(self.caminho)
            try:
                img = pagina_para_array(doc, self.indice, dpi=self.dpi)
            finally:
                doc.close()
            self.sinais.pronta.emit(self.indice, img)
        except Exception:  # noqa: BLE001 - a página fica cinza, nada fecha
            registrar_erro("páginas rolando", traceback.format_exc())


class _Folhas(QWidget):
    """O desenho de todas as folhas (só as visíveis são pintadas)."""

    def __init__(self, dono: "PaginasRolando") -> None:
        super().__init__()
        self.dono = dono

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform)
        visivel = evento.rect()
        for indice, ret in self.dono.retangulos():
            if not ret.intersects(visivel):
                continue
            pix = self.dono.guardadas.get(indice)
            if pix is not None and pix.width() < self.dono.pixels_necessarios(indice) * 0.95:
                self.dono.pedir(indice)          # ficou pequena (o lado a lado desligou): refaz
            if pix is None:
                pintor.fillRect(ret, QColor(estilo.cor("cabeca")))
                pintor.setPen(QColor(estilo.cor("fraco")))
                pintor.drawText(ret, Qt.AlignCenter, str(indice + 1))
                self.dono.pedir(indice)
            else:
                pintor.drawPixmap(ret, pix)
            if indice == self.dono.atual:
                pintor.setPen(QColor(estilo.cor("azul")))
                pintor.drawRect(ret.adjusted(-2, -2, 1, 1))
        pintor.end()


class PaginasRolando(QScrollArea):
    """O folhear do livro aberto (ver o começo do arquivo)."""

    pagina_mudou = Signal(int)       # a folha mais visível agora

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignHCenter)
        self.caminho = ""
        self.tamanhos: list[tuple[float, float]] = []   # largura x altura de cada folha (pontos do PDF)
        self.lado_a_lado = False
        self.atual = 0
        self.guardadas: OrderedDict[int, QPixmap] = OrderedDict()
        self._pedidas: set[int] = set()
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._chegou)
        self._ret: list[tuple[int, QRect]] = []
        self.folhas = _Folhas(self)
        self.setWidget(self.folhas)
        self.verticalScrollBar().valueChanged.connect(lambda _v: self._acompanhar())

    # --- uso --------------------------------------------------------------------

    def abrir(self, caminho: str) -> None:
        """Mostra o livro `caminho` (lê só o tamanho de cada folha agora)."""
        from core.pdf_io import ErroPDF, abrir_pdf
        self.limpar()
        self.caminho = caminho
        try:
            doc = abrir_pdf(caminho)
            try:
                self.tamanhos = [(p.rect.width, p.rect.height) for p in doc]
            finally:
                doc.close()
        except ErroPDF:
            self.tamanhos = []          # PDF que não abre: a tela fica sem páginas, sem erro
        except Exception:  # noqa: BLE001
            registrar_erro("páginas rolando (abrir)", traceback.format_exc())
            self.tamanhos = []
        self._arrumar()

    def limpar(self) -> None:
        self.caminho = ""
        self.tamanhos = []
        self.guardadas.clear()
        self._pedidas.clear()
        self._pool.clear()
        self._arrumar()

    def definir_lado_a_lado(self, ligado: bool) -> None:
        """Liga ou desliga os pares (rodada 7, 202 A), ficando na mesma folha."""
        atual = self.atual
        self.lado_a_lado = bool(ligado)
        self._arrumar()
        self.ir_para(atual)

    def ir_para(self, indice: int) -> None:
        """Rola até a folha `indice` (o alto dela no alto da tela)."""
        for i, ret in self._ret:
            if i == indice:
                self.verticalScrollBar().setValue(max(0, ret.top() - ESPACO))
                break
        self.atual = indice
        self.folhas.update()
        self._pedir_as_visiveis()

    def total(self) -> int:
        return len(self.tamanhos)

    # --- desenho ------------------------------------------------------------------

    def retangulos(self) -> list[tuple[int, QRect]]:
        return self._ret

    def _arrumar(self) -> None:
        """Calcula onde cada folha fica (uma por linha, ou em pares)."""
        largura_da_tela = max(200, self.viewport().width())
        ret = []
        y = ESPACO
        if self.lado_a_lado:
            w = min(LARGURA_PAR, (largura_da_tela - 3 * ESPACO) // 2)
            linhas = [[None, 0]] + [[i, i + 1] for i in range(1, len(self.tamanhos), 2)]
            meio = largura_da_tela // 2
            for linha in linhas:
                altura = 0
                for lado, indice in enumerate(linha):
                    if indice is None or indice >= len(self.tamanhos):
                        continue
                    lw, lh = self.tamanhos[indice]
                    h = int(w * lh / max(1.0, lw))
                    x = meio - w if lado == 0 else meio
                    ret.append((indice, QRect(x, y, w, h)))
                    altura = max(altura, h)
                y += altura + ESPACO
        else:
            w = min(LARGURA_UMA, largura_da_tela - 2 * ESPACO)
            for indice, (lw, lh) in enumerate(self.tamanhos):
                h = int(w * lh / max(1.0, lw))
                ret.append((indice, QRect((largura_da_tela - w) // 2, y, w, h)))
                y += h + ESPACO
        self._ret = ret
        self.folhas.resize(QSize(largura_da_tela, max(y, 10)))
        self.folhas.update()
        self._pedir_as_visiveis()

    def _pedir_as_visiveis(self) -> None:
        """Pede as folhas que estão na tela (e uma tela acima e abaixo),
        sem esperar a pintura (a janela pode não estar sendo pintada)."""
        topo = self.verticalScrollBar().value()
        altura = max(1, self.viewport().height())
        faixa = QRect(0, topo - altura, self.folhas.width(), altura * 3)
        for indice, ret in self._ret:
            if ret.intersects(faixa):
                self.pedir(indice)

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        atual = self.atual
        self._arrumar()
        self.ir_para(atual)

    def _acompanhar(self) -> None:
        """A folha mais visível vira a atual (a pílula e as miniaturas acompanham)."""
        topo = self.verticalScrollBar().value()
        meio = topo + self.viewport().height() // 3
        melhor = None
        for indice, ret in self._ret:
            if ret.top() <= meio <= ret.bottom() + ESPACO:
                melhor = indice
                break
        self._pedir_as_visiveis()
        if melhor is not None and melhor != self.atual:
            self.atual = melhor
            self.folhas.update()
            self.pagina_mudou.emit(melhor)

    # --- as folhas desenhadas ---------------------------------------------------------

    def pixels_necessarios(self, indice: int) -> int:
        """Quantos pixels de largura a folha `indice` ocupa de verdade na tela
        (a largura mostrada vezes a escala do Windows)."""
        largura = next((ret.width() for i, ret in self._ret if i == indice), LARGURA_UMA)
        return int(round(largura * self.devicePixelRatioF()))

    def dpi_para(self, indice: int) -> float:
        """O DPI que dá a folha `indice` com a largura de que a tela precisa."""
        if not 0 <= indice < len(self.tamanhos):
            return DPI_MINIMO
        largura_pt = max(1.0, self.tamanhos[indice][0])
        dpi = 72.0 * self.pixels_necessarios(indice) * FOLGA_DE_NITIDEZ / largura_pt
        return max(DPI_MINIMO, min(DPI_MAXIMO, dpi))

    def pedir(self, indice: int) -> None:
        if not self.caminho or indice in self._pedidas:
            return
        guardada = self.guardadas.get(indice)
        if guardada is not None and guardada.width() >= self.pixels_necessarios(indice) * 0.95:
            return
        self._pedidas.add(indice)
        self._pool.start(_Tarefa(self.caminho, indice, self.dpi_para(indice), self._sinais))

    def _chegou(self, indice: int, img) -> None:
        self._pedidas.discard(indice)
        if not self.caminho:
            return
        self.guardadas[indice] = QPixmap.fromImage(numpy_para_qimage(img))
        self.guardadas.move_to_end(indice)
        while len(self.guardadas) > MAXIMO_GUARDADAS:
            longe = max(self.guardadas, key=lambda i: abs(i - self.atual))
            self.guardadas.pop(longe)
        self.folhas.update()

    def parar(self) -> None:
        """Interrompe o que falta desenhar (ao voltar para os livros)."""
        self._pool.clear()
        self._pool.waitForDone(2000)
