"""Tesseract no item 1.3: caixas de linha do hOCR (T1, T3a, T3b; T2 e o filtro sai daqui).

Uso (ambiente de teste):
    .venv-ocr\\Scripts\\python.exe rodar_tesseract.py [pagina ...]

Configuracoes (nomes da pesquisa, secao 5.4):
- T1   modelo tessdata_best do idioma do livro (ita, por, fra, eng, lat, script/Fraktur), --psm 3;
- T3a  modelo frak2021 da UB Mannheim (CC0), --psm 3;
- T3b  modelo GT4HistOCR da UB Mannheim, --psm 3.
O filtro do Internet Archive (descartar linha com confianca media das palavras
menor que 20) e aplicado depois, em medir.py: T2 = T1 filtrado, T3a/T3b
filtrados. Cada linha guarda a confianca media para isso.

Tempo: 3 rodadas por pagina, mediana. Inclui abrir o programa e carregar o
modelo, porque e assim que o pytesseract chama o tesseract.exe (processo novo a
cada pagina). Os modelos ficam em modelos\\tessdata (fora do git).
"""

from __future__ import annotations

import re
import sys
import time
from html.parser import HTMLParser

import pytesseract
from PIL import Image

import comum as C

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

CONFIGS = {
    "T1": None,               # idioma do livro
    "T3a": "frak2021",
    "T3b": "GT4HistOCR",
}
RODADAS = int(__import__("os").environ.get("RODADAS", "3"))
CLASSES_LINHA = {"ocr_line", "ocr_textfloat", "ocr_header", "ocr_caption"}


class _LeitorHocr(HTMLParser):
    """Junta, para cada linha do hOCR, a caixa e as confiancas das palavras."""

    def __init__(self) -> None:
        super().__init__()
        self.linhas: list[dict] = []
        self._pilha: list[str | None] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classe = a.get("class", "")
        titulo = a.get("title", "")
        marca = None
        if classe in CLASSES_LINHA:
            m = re.search(r"bbox (\d+) (\d+) (\d+) (\d+)", titulo)
            x0, y0, x1, y1 = map(int, m.groups())
            self.linhas.append({"poligono": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                                "confs": [], "classe": classe})
            marca = "linha"
        elif classe == "ocrx_word" and self.linhas:
            m = re.search(r"x_wconf (\d+)", titulo)
            if m:
                self.linhas[-1]["confs"].append(int(m.group(1)))
        self._pilha.append(marca)

    def handle_endtag(self, tag):
        if self._pilha:
            self._pilha.pop()


def linhas_do_hocr(hocr: bytes) -> list[dict]:
    leitor = _LeitorHocr()
    leitor.feed(hocr.decode("utf-8", errors="replace"))
    saida = []
    for ln in leitor.linhas:
        confs = ln.pop("confs")
        ln["conf"] = sum(confs) / len(confs) if confs else 0.0
        ln["palavras"] = len(confs)
        saida.append(ln)
    return saida


def rodar(pagina: str, config: str) -> None:
    modelo = CONFIGS[config] or C.IDIOMA_LIVRO[C.livro(pagina)]
    img = Image.open(C.caminho_imagem(pagina))
    dpi = C.dpi_trabalho(pagina)
    # DPI de verdade so quando o scan tem; nos de "72 dpi" (Horas, Graduale)
    # o numero do arquivo nao e o fisico e o Tesseract estima sozinho.
    extra = f"--dpi {int(round(dpi))}" if dpi >= 150 else ""
    cfg = f"--tessdata-dir {C.MODELOS_TESS.as_posix()} --psm 3 {extra}"  # sem aspas: o pytesseract as passa literalmente no Windows
    tempos, hocr = [], b""
    for _ in range(RODADAS):
        t0 = time.perf_counter()
        hocr = pytesseract.image_to_pdf_or_hocr(img, lang=modelo, config=cfg, extension="hocr")
        tempos.append(time.perf_counter() - t0)
    linhas = linhas_do_hocr(hocr)
    C.gravar_linhas(config, pagina, linhas, tempos, {"modelo": modelo, "opcoes": cfg})
    print(f"{config:4s} {pagina:16s} {modelo:15s} {len(linhas):4d} linhas  "
          f"{min(tempos):6.2f}-{max(tempos):6.2f} s", flush=True)


def main(paginas: list[str], configs: list[str]) -> None:
    print(pytesseract.get_tesseract_version())
    for config in configs:
        for pagina in paginas:
            rodar(pagina, config)


if __name__ == "__main__":
    # Argumentos: paginas e/ou configuracoes (T1, T3a, T3b); sem nada, tudo.
    args = sys.argv[1:]
    main([a for a in args if a not in CONFIGS] or C.PAGINAS,
         [a for a in args if a in CONFIGS] or list(CONFIGS))
