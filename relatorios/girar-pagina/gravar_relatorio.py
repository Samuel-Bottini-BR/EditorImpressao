"""Grava o relatório do conserto D-618 nos três formatos (relatorio.gravar: .md, .html, .pdf).

Rodar da raiz da cópia girar-pagina:
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\girar-pagina\\gravar_relatorio.py
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))

import relatorio  # noqa: E402

TEXTO = (AQUI / "relatorio.md").read_text(encoding="utf-8")
relatorio.gravar(TEXTO, AQUI / "relatorio", titulo="Girar só a página numa folha dividida (D-618)")
print("ok")
