"""Procura, em "D:\\Livros para editar" (do Samuel), livros escaneados abertos com as linhas curvas perto da costura (item 2.12, 22/10/2026).

PARA QUÊ
    Pergunta P3 do 2.12: no acervo de teste não havia página bem curva. O
    Samuel respondeu (22/10): "Na pasta livros para editar, procure lá." Este
    script passa pelos PDFs da pasta, separa os escaneados (cada página é uma
    imagem só, quase sem texto digital) e mede a curva das linhas numa amostra
    de páginas de cada um, com a mesma conta de procurar_linhas_curvas.medir.

A PASTA É SÓ PARA LER
    Nada é gravado, movido nem renomeado nela: os PDFs são abertos só para
    leitura (fitz.open) e tudo o que este script grava vai para
    relatorios/conferir/fase2-itens/2.12/procura-livros-para-editar/ (fora do git).

Uso: python procurar_curvas_livros_para_editar.py <parte> <quantas partes>
     (cada processo pega um pedaço da lista; o resultado vai para achados-<parte>.json)
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import cv2
import fitz
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import procurar_linhas_curvas as plc  # noqa: E402

PASTA = Path(r"D:\Livros para editar")
RAIZ = Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "relatorios" / "conferir" / "fase2-itens" / "2.12" / "procura-livros-para-editar"
AMOSTRA = 10   # páginas medidas por livro
DPI = plc.DPI  # 100, a calibragem da conta


def todos_os_pdfs() -> list[Path]:
    pdfs = []
    for raiz, _pastas, arquivos in os.walk(PASTA):
        for a in arquivos:
            if a.lower().endswith(".pdf"):
                pdfs.append(Path(raiz) / a)
    return sorted(pdfs, key=lambda p: str(p).lower())


def escaneado(doc) -> bool:
    """Três páginas do meio: cada uma com uma imagem que cobre quase a
    página e pouco texto digital (o texto do OCR por trás fica, se houver,
    mas não o livro digital)."""
    n = doc.page_count
    if n < 8:
        return False
    for i in (n // 4, n // 2, 3 * n // 4):
        pagina = doc[i]
        area = abs(pagina.rect)
        if area <= 0:
            return False
        imagens = pagina.get_image_info()
        maior = max((abs(fitz.Rect(im["bbox"]) & pagina.rect) for im in imagens), default=0)
        if maior < 0.8 * area:
            return False
    return True


def medir_livro(caminho: Path) -> list[dict]:
    achados = []
    with fitz.open(caminho) as doc:
        if not escaneado(doc):
            return []
        n = doc.page_count
        indices = sorted({int(n * (k + 1) / (AMOSTRA + 1)) for k in range(AMOSTRA)})
        for i in indices:
            pix = doc[i].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()
            partes = ([("esquerda", img[:, : img.shape[1] // 2]), ("direita", img[:, img.shape[1] // 2:])]
                      if img.shape[1] > 1.2 * img.shape[0] else [("inteira", img)])
            for metade, parte in partes:
                m = plc.medir(parte)
                if m is not None:
                    achados.append({"livro": str(caminho), "paginas": n, "pagina_pdf": i + 1,
                                    "metade": metade, **m})
    return achados


def main() -> int:
    parte, partes = int(sys.argv[1]), int(sys.argv[2])
    SAIDA.mkdir(parents=True, exist_ok=True)
    pdfs = todos_os_pdfs()[parte::partes]
    arquivo = SAIDA / f"achados-{parte}.json"
    feitos = SAIDA / f"feitos-{parte}.txt"
    achados: list[dict] = []
    inicio = time.time()
    for k, pdf in enumerate(pdfs):
        try:
            achados += medir_livro(pdf)
            estado = "ok"
        except Exception as erro:  # noqa: BLE001 - PDF estranho: anota e segue
            estado = f"erro {type(erro).__name__}"
        with open(feitos, "a", encoding="utf-8") as f:
            f.write(f"{k + 1}/{len(pdfs)}\t{estado}\t{pdf}\n")
        if k % 20 == 0:
            arquivo.write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    arquivo.write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"parte {parte}: {len(pdfs)} PDFs, {len(achados)} medidas, {time.time() - inicio:.0f} s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
