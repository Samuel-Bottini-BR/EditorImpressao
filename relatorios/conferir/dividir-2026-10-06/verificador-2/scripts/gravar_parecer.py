"""Grava o parecer do verificador-2 do item 2.1 nos tres formatos (relatorio.gravar)."""
import sys
from pathlib import Path
AQUI = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(AQUI / "trabalho" / "novo"))
import relatorio
texto = (AQUI / "parecer-verificador-2-dividir.md").read_text(encoding="utf-8")
print(relatorio.gravar(texto, AQUI / "parecer-verificador-2-dividir", titulo="Parecer do verificador, 2a rodada: dividir (2.1)"))
