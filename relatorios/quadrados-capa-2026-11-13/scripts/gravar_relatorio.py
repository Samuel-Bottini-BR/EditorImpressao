"""Grava o relatorio nos tres formatos (CLAUDE.md §2) com relatorio.gravar: le relatorio.md, troca
IMAGENS_AQUI pela lista das imagens (com a frase de cada uma, imagens/legendas.json) e grava o
.md, o .html e o .pdf (o .pdf fica fora do git: *.pdf no .gitignore).
    python gravar_relatorio.py"""
import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
RAIZ = PASTA.parents[1]
sys.path.insert(0, str(RAIZ))
import relatorio  # noqa: E402

texto = (PASTA / "relatorio.md").read_text(encoding="utf-8")
if "IMAGENS_AQUI" in texto:
    leg = json.loads((PASTA / "imagens" / "legendas.json").read_text(encoding="utf-8"))
    ordem = sorted(leg, key=lambda n: int(n.split("-")[0]))
    partes = [f"### {nome.split('.')[0]}\n\n**O que olhar:** {leg[nome]}\n\n![{nome}](imagens/{nome})\n"
              for nome in ordem]
    texto = texto.replace("IMAGENS_AQUI", "\n".join(partes))
feitos = relatorio.gravar(texto, PASTA / "relatorio", titulo="Quadrados na capa do Gradus Primus")
print({k: str(v) for k, v in feitos.items()})
