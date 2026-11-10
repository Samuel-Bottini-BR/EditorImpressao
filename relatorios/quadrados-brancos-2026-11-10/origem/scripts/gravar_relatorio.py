"""Grava o relatorio nos tres formatos (CLAUDE.md §2) com relatorio.gravar: le
origem/relatorio-completo.md e grava de novo o .md, o .html (imagens de imagens/) e o .pdf
(o .pdf fica fora do git: *.pdf no .gitignore).

    python gravar_relatorio.py
"""
import sys
from pathlib import Path

ORIGEM = Path(__file__).resolve().parents[1]
RAIZ = ORIGEM.parents[2]
sys.path.insert(0, str(RAIZ))

import relatorio  # noqa: E402

texto = (ORIGEM / "relatorio-completo.md").read_text(encoding="utf-8")
feitos = relatorio.gravar(texto, ORIGEM / "relatorio-completo",
                          titulo="Quadrados brancos: de onde vieram")
print({k: str(v) for k, v in feitos.items()})
