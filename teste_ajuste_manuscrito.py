"""O medidor resolve o caso difícil? Comparativo por valor de ajuste.

Uso:
    python teste_ajuste_manuscrito.py "livro.pdf" [pagina]

Gera, para a página escolhida, a mesma imagem com o ajuste em 0, 25, 50, 75 e
100 - um comparativo por filtro. Serve para responder, com imagem, se o
usuário consegue salvar uma página difícil só mexendo no medidor.

Também mede o quanto o fundo ficou uniforme: num scan de pergaminho, o que
incomoda não é a cor, é o fundo manchado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO, aplicar_filtro
from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array

SAIDA = Path("saida_teste/ajustes")
VALORES = (0, 25, 50, 75, 100)


def manchado(img: np.ndarray) -> float:
    """Desvio do fundo claro: quanto maior, mais manchado o papel ficou."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    papel = cinza[cinza >= np.percentile(cinza, 70)]
    return float(papel.std()) if papel.size else 0.0


def _rotular(img: np.ndarray, texto: str) -> np.ndarray:
    """Poe uma faixa branca com o texto em cima da imagem, para o comparativo."""
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    faixa = np.full((46, img.shape[1], 3), 255, dtype=np.uint8)
    cv2.putText(faixa, texto, (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.85,
                (0, 0, 0), 2, cv2.LINE_AA)
    return np.vstack([faixa, img])


def main(caminho: str, numero: int = 1) -> int:
    """Roda os tres filtros com ajuste na pagina pedida e grava um painel
    (visao geral + zoom) por filtro, com o fundo manchado e a fracao de tinta
    impressos no console para cada valor."""
    SAIDA.mkdir(parents=True, exist_ok=True)
    doc = abrir_pdf(caminho)
    bruta = pagina_para_array(doc, numero - 1, dpi=300)
    doc.close()

    for filtro, rotulo in ((PRETO_E_BRANCO, "forca do preto"),
                           (MELHORAR, "clareza do fundo"),
                           (MAGICO_PRO, "intensidade")):
        print(f"\n{filtro}  ({rotulo})")
        paineis, zooms = [], []

        for valor in VALORES:
            ajustes = {"forca_preto": valor} if filtro == PRETO_E_BRANCO else (
                {"clareza": valor} if filtro == MELHORAR else {"intensidade": valor}
            )
            saida, _ = aplicar_filtro(bruta, filtro, **ajustes)
            cor = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)

            tinta = float((cv2.cvtColor(cor, cv2.COLOR_BGR2GRAY) < 128).mean())
            print(f"   {valor:>3}: fundo manchado {manchado(saida):5.1f}   "
                  f"tinta {tinta * 100:5.1f}%")

            paineis.append(_rotular(limitar_altura(cor, 760), f"{rotulo} {valor}"))
            h, w = cor.shape[:2]
            y, x = int(h * 0.30), int(w * 0.18)
            zooms.append(_rotular(cor[y:y + 260, x:x + 560], f"{valor}"))

        cv2.imwrite(str(SAIDA / f"{filtro}_pag{numero}.png"), np.hstack(paineis))
        cv2.imwrite(str(SAIDA / f"{filtro}_pag{numero}_zoom.png"), np.hstack(zooms))

    print(f"\nimagens em: {SAIDA.resolve()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    numero = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    raise SystemExit(main(sys.argv[1], numero))
