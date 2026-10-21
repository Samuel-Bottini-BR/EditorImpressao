"""Grava o relatorio do conserto nos tres formatos (CLAUDE.md, secao 2: .md,
.html e .pdf), a partir do .md escrito a mao em
relatorios/conferir/conserto-corte-g6-2026-10-13/conserto-corte-g6.md.
As imagens (img/tres-*.jpg) sao feitas antes pelo montar.py.

USO  python relatorio_final.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402

DESTINO = RAIZ / "relatorios" / "conferir" / "conserto-corte-g6-2026-10-13" / "conserto-corte-g6.md"

if __name__ == "__main__":
    texto = DESTINO.read_text(encoding="utf-8")
    for formato, caminho in relatorio.gravar(texto, DESTINO).items():
        print(formato, caminho)
