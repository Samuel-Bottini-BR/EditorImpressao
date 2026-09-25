"""Teste visual dos filtros (Etapa 2).

Uso:
    python teste_filtros.py "livro.pdf" [pagina1 pagina2 ...]

Gera em saida_teste/filtros/ um PNG por página com os quatro filtros lado a
lado e uma faixa de titulo, mais um recorte ampliado do texto para julgar
nitidez e bleed-through.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import cv2
import numpy as np

from core.filtros import (
    FORCAS,
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    doxapy_disponivel,
    filtro_preto_e_branco,
)
from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array

SAIDA = Path("saida_teste/filtros")
ALTURA_PAINEL = 1000


def _rotular(img: np.ndarray, texto: str) -> np.ndarray:
    """Cola uma faixa branca com o nome do filtro em cima da imagem."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    faixa = np.full((60, img.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (14, 42), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.line(faixa, (0, 59), (img.shape[1], 59), (180, 180, 180), 1)
    return np.vstack([faixa, img])


def _lado_a_lado(paineis: list[np.ndarray]) -> np.ndarray:
    """Junta os paineis numa unica imagem horizontal, com uma tarja cinza
    entre eles e preenchimento branco para igualar a altura de todos."""
    altura = max(p.shape[0] for p in paineis)
    ajustados = []
    for p in paineis:
        if p.shape[0] < altura:
            preenchimento = np.full((altura - p.shape[0], p.shape[1], 3), 255, dtype=np.uint8)
            p = np.vstack([p, preenchimento])
        ajustados.append(p)
        ajustados.append(np.full((altura, 8, 3), 210, dtype=np.uint8))
    return np.hstack(ajustados[:-1])


def _recorte_texto(img: np.ndarray, frac_y=0.35, frac_x=0.12, largura=700, altura=280):
    """Pega um pedaco do miolo do texto para avaliar de perto."""
    h, w = img.shape[:2]
    y = int(h * frac_y)
    x = int(w * frac_x)
    return img[y : y + altura, x : x + largura]


def main(caminho: str, paginas: list[int]) -> int:
    """Para cada pagina pedida, gera o comparativo dos quatro filtros lado a
    lado (visao geral + recorte de texto ampliado) e um terceiro painel so do
    Preto e branco nas tres posicoes da força do preto."""
    SAIDA.mkdir(parents=True, exist_ok=True)
    print(f"Binarizacao: {'DoxaPy (Sauvola)' if doxapy_disponivel() else 'scikit-image (plano B)'}")

    doc = abrir_pdf(caminho)
    if not paginas:
        paginas = [1, doc.page_count // 2, doc.page_count]
    paginas = [p for p in dict.fromkeys(paginas) if 1 <= p <= doc.page_count]

    filtros = [ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO]
    rotulos = ["Original", "Preto e branco", "Melhorar", "Mágico pro"]

    for numero in paginas:
        idx = numero - 1
        bruta = pagina_para_array(doc, idx, dpi=300)
        print(f"\nPagina {numero}  ({bruta.shape[1]}x{bruta.shape[0]} px)")

        paineis, recortes = [], []
        for filtro, rotulo in zip(filtros, rotulos):
            t0 = time.perf_counter()
            saida, mono = aplicar_filtro(bruta, filtro)
            dt = time.perf_counter() - t0

            if saida.ndim == 2:
                saida_bgr = cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
            else:
                saida_bgr = saida
            print(f"  {rotulo:<16} {dt:5.2f} s   1 bit: {mono}")

            paineis.append(_rotular(limitar_altura(saida_bgr, ALTURA_PAINEL), rotulo))
            recortes.append(_rotular(_recorte_texto(saida_bgr), rotulo))

        cv2.imwrite(str(SAIDA / f"pagina_{numero:03d}_comparativo.png"), _lado_a_lado(paineis))
        cv2.imwrite(str(SAIDA / f"pagina_{numero:03d}_zoom.png"), _lado_a_lado(recortes))

        # forca do preto: as tres posicoes do controle
        forcas = []
        for forca in ("mais_fraco", "normal", "mais_escuro"):
            pb = filtro_preto_e_branco(bruta, forca=forca)
            forcas.append(_rotular(_recorte_texto(cv2.cvtColor(pb, cv2.COLOR_GRAY2BGR)), forca))
        cv2.imwrite(str(SAIDA / f"pagina_{numero:03d}_forca.png"), _lado_a_lado(forcas))

    doc.close()
    print(f"\nOK. Imagens em: {SAIDA.resolve()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], [int(a) for a in sys.argv[2:]]))
