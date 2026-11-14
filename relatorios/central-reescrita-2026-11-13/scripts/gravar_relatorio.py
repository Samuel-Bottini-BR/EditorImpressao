"""Junta partes/*.md em relatorio.md e grava nos três formatos (relatorio.gravar, CLAUDE.md §2)."""
from __future__ import annotations

import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\obra-juncao")
import relatorio  # noqa: E402

texto = "\n".join(p.read_text(encoding="utf-8") for p in sorted((PASTA / "partes").glob("*.md")))
print(relatorio.gravar(texto, PASTA / "relatorio", titulo="Central: perguntas reescritas (13/11/2026)"))
