"""Passo 1 do 1.3: imagens de trabalho, linhas do Internet Archive (R0) e desenho das zonas.

Uso (ambiente de teste, nunca o .venv do programa):
    .venv-ocr\\Scripts\\python.exe relatorios\\fase1-1.3-comparacao-ocr-2026-09-28\\scripts\\preparar.py

Grava:
- saida_teste\\ocr-1.3\\imagens\\<pagina>.png  -- a imagem que todos os detectores recebem;
- saida_teste\\ocr-1.3\\linhas\\R0\\<pagina>.json -- as linhas do texto invisivel do PDF (so livros do IA);
- relatorios\\...\\zonas\\<pagina>.jpg -- as zonas por cima da pagina, para o Samuel conferir.

Seguro mudar: tamanho e cores das imagens das zonas.
"""

from __future__ import annotations

import time

import cv2
import fitz
import numpy as np

import comum as C


def linhas_ia(pagina: str, zoom: float) -> list[dict]:
    """Linhas do texto invisivel que o Internet Archive pos no PDF (R0)."""
    doc = fitz.open(C.GABARITO / "paginas" / f"{pagina}.pdf")
    dados = doc[0].get_text("dict")
    linhas = []
    for bloco in dados["blocks"]:
        if bloco.get("type") != 0:
            continue
        for ln in bloco["lines"]:
            texto = "".join(s["text"] for s in ln["spans"]).strip()
            if not texto:
                continue
            x0, y0, x1, y1 = (v * zoom for v in ln["bbox"])
            linhas.append({"poligono": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]})
    return linhas


def desenhar_zonas(pagina: str, img: np.ndarray, zonas: dict) -> np.ndarray:
    """Dois paineis: as zonas por cima da pagina, e a tinta pintada pela zona."""
    h, w = img.shape[:2]
    zm = C.mascaras_zonas(zonas, (h, w))
    tinta = C.tinta(img, C.dpi_trabalho(pagina))
    tinta_texto = C.tirar_grade(tinta, zm["tabela"]) & zm["texto"]

    a = img.copy()
    cor = np.zeros_like(a)
    cor[zm["texto"]] = (0, 170, 0)
    cor[zm["figura"]] = (220, 0, 0)
    cor[zm["neutro"]] = (130, 130, 130)
    sel = zm["texto"] | zm["figura"] | zm["neutro"]
    a[sel] = (0.65 * a[sel] + 0.35 * cor[sel]).astype(np.uint8)
    for nome, rgb in (("texto", (0, 130, 0)), ("figura", (200, 0, 0)), ("neutro", (90, 90, 90))):
        cont, _ = cv2.findContours(zm[nome].astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(a, cont, -1, rgb, max(2, w // 600))

    b = np.full_like(img, 255)
    b[tinta] = (150, 150, 150)                 # tinta fora de zona: cinza
    b[tinta_texto] = (0, 150, 0)                # tinta de texto: verde
    b[tinta & zm["figura"]] = (210, 0, 0)       # tinta de figura: vermelho
    alvo = 1100
    esc = alvo / h
    a = cv2.resize(a, (int(w * esc), alvo), interpolation=cv2.INTER_AREA)
    b = cv2.resize(b, (int(w * esc), alvo), interpolation=cv2.INTER_AREA)
    sep = np.full((alvo, 12, 3), 255, np.uint8)
    return np.hstack([a, sep, b])


def main() -> None:
    zonas = C.carregar_zonas()
    (C.TRABALHO / "imagens").mkdir(parents=True, exist_ok=True)
    (C.RELATORIO / "zonas").mkdir(parents=True, exist_ok=True)
    for pagina in C.PAGINAS:
        img, zoom = C.render_pagina(pagina)
        cv2.imwrite(str(C.caminho_imagem(pagina)), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        if C.livro(pagina) in C.LIVROS_IA:
            t0 = time.perf_counter()
            linhas = linhas_ia(pagina, zoom)
            C.gravar_linhas("R0", pagina, linhas, [time.perf_counter() - t0])
        painel = desenhar_zonas(pagina, img, zonas[pagina])
        cv2.imwrite(str(C.RELATORIO / "zonas" / f"{pagina}.jpg"),
                    cv2.cvtColor(painel, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 82])
        print(pagina, img.shape[1], "x", img.shape[0], "px, dpi", C.dpi_trabalho(pagina))


if __name__ == "__main__":
    main()
