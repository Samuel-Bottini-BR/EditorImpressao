"""Grava o relatório das 6 perguntas nos três formatos (relatorio.gravar: .md, .html, .pdf).

    python gravar.py
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI.parents[1]))
import relatorio  # noqa: E402

texto = (AQUI / "relatorio_fonte.md").read_text(encoding="utf-8")
print(relatorio.gravar(texto, AQUI / "relatorio", titulo="Seis perguntas com prints (14/11/2026)"))
