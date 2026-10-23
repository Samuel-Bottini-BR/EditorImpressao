"""Item 2.6, imp-5 (Samuel, 21/10/2026: "Também manda direto para a impressora").

O QUE FAZ
    Manda as folhas montadas (core/impressao.montar_em_memoria) direto para uma
    impressora do Windows, com as escolhas que só existem na impressora (a
    janela do UPDF): qual impressora, cópias, agrupar e frente e verso (virando
    na borda curta no livreto, na comprida na página inteira). Usa o
    QtPrintSupport do PySide6, que já está no projeto (LGPL); nenhuma
    biblioteca nova.

    Cada folha é desenhada como imagem na resolução da impressora (no máximo
    DPI_MAXIMO), uma por vez - é o "Imprimir como imagem" que o Samuel disse que
    precisa (imp-6: "sem ela sai algo errado").

POR QUE MORA EM core/
    Não abre janela nenhuma: pinta num QPrinter, o que o Qt deixa fazer fora do
    fio da tela ("QPainter can be used in a thread to paint onto QImage,
    QPrinter, and QPicture paint devices"). Quem escolhe a impressora e chama é
    a tela (ui/dialogo_impressao.py), num QThread. Nenhum import de ui/.

SEGURO MUDAR: DPI_MAXIMO (mais = mais lento e mais memória por folha).
ARRISCADO MUDAR: setFullPage(True) e o retângulo do papel (sem isso o Qt
    encolhe a folha para dentro da margem da impressora e as margens de 1,3 cm
    deixam de valer).
"""

from __future__ import annotations

from typing import Callable

import fitz

DPI_MAXIMO = 300
_APLICATIVO: list = []      # o QGuiApplication criado aqui, quando nao ha outro

BORDA_CURTA = "curta"
BORDA_COMPRIDA = "comprida"
SO_UM_LADO = "um_lado"


def listar_impressoras() -> list[str]:
    """Os nomes das impressoras do Windows (a de fábrica primeiro)."""
    from PySide6.QtPrintSupport import QPrinterInfo

    padrao = QPrinterInfo.defaultPrinterName()
    nomes = [i.printerName() for i in QPrinterInfo.availablePrinters()]
    if padrao in nomes:
        nomes.remove(padrao)
        nomes.insert(0, padrao)
    return nomes


def imprimir(folhas: fitz.Document, impressora: str = "", copias: int = 1,
             agrupar: bool = True, frente_e_verso: str = BORDA_CURTA,
             arquivo_pdf: str = "",
             progresso: Callable[[int, int, str], None] | None = None,
             cancelado: Callable[[], bool] | None = None) -> int:
    """Imprime as folhas. Devolve quantas páginas foram mandadas.

    arquivo_pdf: em vez da impressora, grava o que iria para ela num PDF (para
    os testes e para conferir sem gastar papel)."""
    from PySide6.QtCore import QMarginsF, QRectF, QSizeF
    from PySide6.QtGui import QImage, QPageLayout, QPageSize, QPainter
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtPrintSupport import QPrinter

    # por linha de comando (sem a janela) o Qt precisa de um aplicativo para
    # pintar; dentro do programa ele ja existe
    if QGuiApplication.instance() is None:
        _APLICATIVO.append(QGuiApplication(["editor-impressao"]))

    # Gravando num PDF (testes, conferir sem papel): QPdfWriter, que nao
    # pergunta nada a impressora nenhuma (o QPrinter leva ~50 s para nascer
    # quando a impressora de fabrica do Windows esta desligada na rede,
    # medido em 22/10/2026). Na impressora de verdade: QPrinter com ela.
    if arquivo_pdf:
        from PySide6.QtGui import QPdfWriter

        impressora_qt = QPdfWriter(arquivo_pdf)
        impressora_qt.setResolution(150)
        impressora_qt.setTitle("Editor de Impressão")
    else:
        from PySide6.QtPrintSupport import QPrinterInfo

        info = QPrinterInfo.printerInfo(impressora) if impressora else QPrinterInfo.defaultPrinter()
        impressora_qt = QPrinter(info, QPrinter.PrinterMode.HighResolution)
        impressora_qt.setCopyCount(max(1, int(copias)))
        impressora_qt.setCollateCopies(bool(agrupar))
        impressora_qt.setDuplex({BORDA_CURTA: QPrinter.DuplexMode.DuplexShortSide,
                                 BORDA_COMPRIDA: QPrinter.DuplexMode.DuplexLongSide}.get(
                                     frente_e_verso, QPrinter.DuplexMode.DuplexNone))
        impressora_qt.setFullPage(True)
        impressora_qt.setDocName("Editor de Impressão")

    def layout_da(pagina: fitz.Page) -> QPageLayout:
        largura, altura = pagina.rect.width, pagina.rect.height
        deitada = largura > altura
        tamanho = QPageSize(QSizeF(min(largura, altura), max(largura, altura)), QPageSize.Unit.Point)
        return QPageLayout(tamanho, QPageLayout.Orientation.Landscape if deitada
                           else QPageLayout.Orientation.Portrait, QMarginsF(0, 0, 0, 0))

    total = folhas.page_count
    if total == 0:
        return 0
    impressora_qt.setPageLayout(layout_da(folhas[0]))
    pintor = QPainter()
    if not pintor.begin(impressora_qt):
        raise RuntimeError("A impressora não aceitou o trabalho.")
    mandadas = 0
    try:
        resolucao = min(DPI_MAXIMO, max(72, impressora_qt.resolution()))
        for n in range(total):
            if cancelado is not None and cancelado():
                break
            if progresso is not None:
                progresso(n, total, f"Mandando a folha {n + 1} de {total} para a impressora")
            pagina = folhas[n]
            if n > 0:
                impressora_qt.setPageLayout(layout_da(pagina))
                impressora_qt.newPage()
            pix = pagina.get_pixmap(dpi=resolucao, alpha=False)
            imagem = QImage(pix.samples, pix.width, pix.height, pix.stride,
                            QImage.Format.Format_RGB888)
            alvo = impressora_qt.pageLayout().fullRectPixels(impressora_qt.resolution())
            pintor.drawImage(QRectF(alvo), imagem)
            del imagem, pix
            mandadas += 1
    finally:
        pintor.end()
    return mandadas
