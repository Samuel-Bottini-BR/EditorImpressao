"""Teste da Etapa 3: lombada, deskew e recorte de bordas.

Uso:
    python teste_dividir.py "livro.pdf" [quantas_paginas]

Gera em saida_teste/dividir/ uma imagem por folha com a linha de corte
desenhada, e imprime a confianca de cada uma.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2
import numpy as np

from core.dividir import detectar_lombada, dividir_imagem
from core.endireitar import detectar_angulo
from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array
from core.recortar import aplicar_recorte, detectar_bordas

SAIDA = Path("saida_teste/dividir")


def main(caminho: str, quantas: int) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    doc = abrir_pdf(caminho)
    total = doc.page_count
    indices = list(range(min(quantas, total)))

    print(f"{total} folhas. Analisando {len(indices)}.\n")
    print(f"{'folha':>6} {'corte':>7} {'conf':>6} {'angulo':>8} {'conf':>6}  {'recorte (x,y,l,a)':>28}")
    print("-" * 78)

    baixa_confianca = []
    t0 = time.perf_counter()

    for idx in indices:
        img = pagina_para_array(doc, idx, dpi=150)

        lombada = detectar_lombada(img)
        inclinacao = detectar_angulo(img)
        recorte = detectar_bordas(img)

        marca = "  <-- conferir" if lombada.confianca < 0.5 else ""
        if lombada.confianca < 0.5:
            baixa_confianca.append(idx + 1)

        print(
            f"{idx + 1:>6} {lombada.posicao:>7.3f} {lombada.confianca:>6.2f} "
            f"{inclinacao.angulo:>8.2f} {inclinacao.confianca:>6.2f}  "
            f"({recorte.x:.3f},{recorte.y:.3f},{recorte.largura:.3f},{recorte.altura:.3f})"
            f"{marca}"
        )

        # desenho: linha de corte em azul + retangulo do recorte em verde
        vis = limitar_altura(img.copy(), 700)
        h, w = vis.shape[:2]
        x = int(lombada.posicao * w)
        cv2.line(vis, (x, 0), (x, h), (255, 0, 0), 3)
        rx, ry = int(recorte.x * w), int(recorte.y * h)
        rw, rh = int(recorte.largura * w), int(recorte.altura * h)
        cv2.rectangle(vis, (rx, ry), (rx + rw, ry + rh), (0, 170, 0), 2)
        cv2.imwrite(str(SAIDA / f"folha_{idx + 1:03d}_corte.png"), vis)

    dt = time.perf_counter() - t0
    print("-" * 78)
    print(f"{dt / max(1, len(indices)):.2f} s por folha (análise a 150 DPI)")
    pct = 100 * len(baixa_confianca) / max(1, len(indices))
    print(f"Marcadas para revisao: {len(baixa_confianca)} de {len(indices)} ({pct:.0f}%)")
    if baixa_confianca:
        print(f"  folhas: {baixa_confianca}")

    # amostra: uma folha dividida de fato, ja com o recorte aplicado
    img = pagina_para_array(doc, min(35, total - 1), dpi=200)
    lombada = detectar_lombada(img)
    esq, dir_ = dividir_imagem(img, lombada.posicao)
    for nome, parte in (("esquerda", esq), ("direita", dir_)):
        cortada = aplicar_recorte(parte, detectar_bordas(parte))
        cv2.imwrite(str(SAIDA / f"amostra_{nome}.png"), limitar_altura(cortada, 900))

    doc.close()
    print(f"\nOK. Imagens em: {SAIDA.resolve()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 15))
