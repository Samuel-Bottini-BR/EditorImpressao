"""Quanto tempo o EscritorPDF leva para gravar um livro sintético (04/11/2026).

PARA QUE SERVE: conferir que ir ao disco aos poucos (core.pdf_io.
PDFQueVaiParaODisco) não deixa a gravação do PDF mais lenta. Roda UMA vez,
com o código da pasta dada (a do conserto ou uma cópia do código antigo), e
imprime os segundos. Quem compara roda os dois alternados, várias vezes.

Uso: python medir_tempo_da_gravacao.py <raiz do código> <pasta de saída> [páginas]
As páginas são imagens de 1762 x 2646 pontos (a página do Rhetorica a 300 DPI)
com papel liso e "texto" de ruído, que se comprimem como um scan (~3 MB cada).
Seguro mudar: tudo (é só medida).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path


def pagina(semente: int):
    import numpy as np

    r = np.random.default_rng(semente)
    img = np.full((2646, 1762, 3), (222, 228, 235), np.uint8)
    for _ in range(60):                                  # "linhas de texto"
        y, x = int(r.integers(100, 2500)), int(r.integers(80, 300))
        img[y:y + 22, x:x + 1300] = r.integers(20, 235, (22, 1300, 3), dtype=np.uint8)
    return img


def main() -> int:
    raiz, saida = Path(sys.argv[1]), Path(sys.argv[2])
    paginas = int(sys.argv[3]) if len(sys.argv) > 3 else 60
    sys.path.insert(0, str(raiz))
    from core.pdf_io import EscritorPDF

    saida.mkdir(parents=True, exist_ok=True)
    destino = saida / "tempo.pdf"
    segundos = 0.0                      # só a gravação: fazer a página não conta
    escritor = EscritorPDF(destino)
    for i in range(paginas):
        img = pagina(i)                 # todas diferentes, como num livro
        t0 = time.perf_counter()
        escritor.escrever_imagem(img, dpi=300)
        segundos += time.perf_counter() - t0
    t0 = time.perf_counter()
    escritor.fechar()
    segundos += time.perf_counter() - t0
    print(f"{segundos:.2f} {destino.stat().st_size / 1024 / 1024:.0f}")
    destino.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
