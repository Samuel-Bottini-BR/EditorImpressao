"""Gera (ou regera) as imagens comparativas de um livro.

Uso:
    python teste_imagens.py "livro.pdf" [pagina ...]

Sem números de página, escolhe sozinho as mais difíceis. Com números, usa
exatamente as que você pedir - serve para ampliar uma iluminura específica.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

from core import analise
from core.endireitar import detectar_angulo
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO, aplicar_filtro
from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array

DPI = 300


def gravar(caminho: Path, img: np.ndarray) -> bool:
    """PNG em caminho com acento. O cv2.imwrite falha calado nesses casos."""
    ok, buffer = cv2.imencode(".png", img)
    if ok:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(buffer.tobytes())
    return ok


def rotular(img: np.ndarray, texto: str) -> np.ndarray:
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    faixa = np.full((50, img.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (12, 34), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (0, 0, 0), 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def juntar(paineis: list[np.ndarray]) -> np.ndarray:
    altura = max(p.shape[0] for p in paineis)
    partes = []
    for p in paineis:
        if p.shape[0] < altura:
            p = np.vstack([p, np.full((altura - p.shape[0], p.shape[1], 3), 255,
                                      dtype=np.uint8)])
        partes.append(p)
        partes.append(np.full((altura, 8, 3), 190, dtype=np.uint8))
    return np.hstack(partes[:-1])


def comparativo(bruta: np.ndarray) -> np.ndarray:
    paineis = []
    for filtro, nome in ((ORIGINAL, "Original"), (PRETO_E_BRANCO, "Preto e branco"),
                         (MELHORAR, "Melhorar"), (MAGICO_PRO, "Magico pro")):
        img, _ = aplicar_filtro(bruta, filtro)
        paineis.append(rotular(limitar_altura(img, 950), nome))
    return juntar(paineis)


def ampliacao(bruta: np.ndarray, fx=0.18, fy=0.30, largura=760, altura=520,
              filtros=(ORIGINAL, MELHORAR, MAGICO_PRO)) -> np.ndarray:
    h, w = bruta.shape[:2]
    y, x = int(h * fy), int(w * fx)
    recorte = bruta[y:min(h, y + altura), x:min(w, x + largura)]
    nomes = {ORIGINAL: "Original", PRETO_E_BRANCO: "Preto e branco",
             MELHORAR: "Melhorar", MAGICO_PRO: "Magico pro"}
    paineis = []
    for filtro in filtros:
        img, _ = aplicar_filtro(recorte, filtro)
        paineis.append(rotular(img, nomes[filtro]))
    return juntar(paineis)


def main(caminho: str, paginas: list[int]) -> int:
    livro = Path(caminho)
    destino = livro.parent / "resultados" / livro.stem[:40]
    doc = abrir_pdf(livro)
    try:
        if not paginas:
            # escolhe sozinho: a mais colorida, a mais torta, a mais amarelada
            amostras = []
            passo = max(1, doc.page_count // 40)
            for i in range(0, doc.page_count, passo):
                img = pagina_para_array(doc, i, dpi=90)
                tem_cor, sat = analise.detectar_cor(img)
                amostras.append((i, sat, abs(detectar_angulo(img).angulo)))
                del img
            paginas = [
                max(amostras, key=lambda a: a[1])[0] + 1,   # mais colorida
                max(amostras, key=lambda a: a[2])[0] + 1,   # mais torta
            ]

        for numero in dict.fromkeys(paginas):
            if not 1 <= numero <= doc.page_count:
                continue
            bruta = pagina_para_array(doc, numero - 1, dpi=DPI)
            gravar(destino / f"pag{numero:04d}_4filtros.png", comparativo(bruta))
            gravar(destino / f"pag{numero:04d}_AMPLIADO.png", ampliacao(bruta))
            print(f"  página {numero}: 2 imagens")
            del bruta
    finally:
        doc.close()

    print(f"em: {destino}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1], [int(a) for a in sys.argv[2:]]))
