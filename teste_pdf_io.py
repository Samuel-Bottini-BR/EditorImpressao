"""Teste de linha de comando da Etapa 1 (core/pdf_io.py).

Uso:
    python teste_pdf_io.py "caminho\\do\\livro.pdf"

Faz, sem abrir nenhuma janela:
  1. abre o PDF e lista as paginas (tamanho, retrato/paisagem)
  2. rasteriza 3 paginas e salva como PNG
  3. gera um PDF de saida com essas 3 paginas (colorido e 1 bit)
  4. gera um PDF por copia direta, sem rasterizar
  5. mede memoria e tempo lendo o livro inteiro, uma pagina por vez
"""

from __future__ import annotations

import sys
import time
import tracemalloc
from pathlib import Path

import cv2

from core.pdf_io import (
    DPI_PADRAO,
    EscritorPDF,
    ErroPDF,
    abrir_pdf,
    dpi_seguro,
    info_paginas,
    limitar_altura,
    pagina_para_array,
)

SAIDA = Path("saida_teste")


def main(caminho: str) -> int:
    SAIDA.mkdir(exist_ok=True)

    try:
        doc = abrir_pdf(caminho)
    except ErroPDF as e:
        print(f"ERRO: {e}")
        return 1

    infos = info_paginas(doc)
    print(f"Arquivo: {Path(caminho).name}")
    print(f"Paginas: {len(infos)}")

    paisagens = sum(1 for i in infos if i.paisagem)
    print(f"Em paisagem (candidatas a folha dupla): {paisagens} de {len(infos)}")
    for i in infos[:3]:
        orient = "paisagem" if i.paisagem else "retrato"
        print(
            f"  pagina {i.indice + 1}: {i.largura_pt:.0f} x {i.altura_pt:.0f} pt  [{orient}]"
        )

    print(f"\nDPI pedido: {DPI_PADRAO} -> DPI usado: {dpi_seguro(doc[0], DPI_PADRAO)}")

    # --- 2 e 3: rasterizar algumas paginas e escrever um PDF novo -------------
    alvos = [0, len(infos) // 2, len(infos) - 1]
    alvos = sorted(set(a for a in alvos if 0 <= a < len(infos)))

    print("\nRasterizando e salvando PNG:")
    with EscritorPDF(SAIDA / "teste_rasterizado.pdf") as saida:
        for idx in alvos:
            img = pagina_para_array(doc, idx, dpi=DPI_PADRAO)
            h, w = img.shape[:2]
            print(f"  pagina {idx + 1}: {w} x {h} px")
            cv2.imwrite(str(SAIDA / f"pagina_{idx + 1:03d}.png"), limitar_altura(img, 1200))
            saida.escrever_imagem(img, dpi=DPI_PADRAO)

    with EscritorPDF(SAIDA / "teste_1bit.pdf") as saida:
        for idx in alvos:
            img = pagina_para_array(doc, idx, dpi=DPI_PADRAO)
            saida.escrever_imagem(img, dpi=DPI_PADRAO, monocromatico=True)

    # --- 4: copia direta, sem rasterizar -------------------------------------
    with EscritorPDF(SAIDA / "teste_copia_direta.pdf") as saida:
        for idx in alvos:
            saida.copiar_pagina(doc, idx)

    for nome in ("teste_rasterizado.pdf", "teste_1bit.pdf", "teste_copia_direta.pdf"):
        kb = (SAIDA / nome).stat().st_size / 1024
        print(f"  {nome}: {kb:,.0f} KB")

    # --- 5: livro inteiro, uma pagina por vez --------------------------------
    print("\nLendo o livro inteiro, uma pagina por vez...")
    tracemalloc.start()
    inicio = time.perf_counter()
    for i in range(len(infos)):
        img = pagina_para_array(doc, i, dpi=DPI_PADRAO)
        del img  # solta antes da proxima - e o que impede o travamento
    decorrido = time.perf_counter() - inicio
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  {len(infos)} paginas em {decorrido:.1f} s ({decorrido / len(infos):.2f} s/pagina)")
    print(f"  pico de memoria Python: {pico / 1024 / 1024:.0f} MB")

    doc.close()
    print(f"\nOK. Resultados em: {SAIDA.resolve()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
