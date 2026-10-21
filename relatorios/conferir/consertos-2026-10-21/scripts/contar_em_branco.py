"""Verificador, 21/10: quais paginas de um livro inteiro ganham o aviso "Parece em branco", com o codigo de uma pasta
(--raiz), pela analise do programa (analisar_projeto, livro novo). So le o PDF.
Uso: contar_em_branco.py --raiz <pasta> --pdf <pdf> --saida <json>"""
import json
import os
import sys
import tempfile
from pathlib import Path

args = sys.argv[1:]
RAIZ = Path(args[args.index("--raiz") + 1]).resolve()
PDF = Path(args[args.index("--pdf") + 1])
SAIDA = Path(args[args.index("--saida") + 1])
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "verif_embranco_dados")
sys.path.insert(0, str(RAIZ))
from core import analise  # noqa: E402
from core import pipeline as P  # noqa: E402
from modelos import Projeto  # noqa: E402

assert Path(P.__file__).resolve().is_relative_to(RAIZ)
pr = P.analisar_projeto(Projeto(caminho_entrada=str(PDF), nome=PDF.stem))
marcadas = [p.indice + 1 for p in pr.paginas if analise.EM_BRANCO in p.alertas]
obs = list(getattr(pr, "observacoes", []))
res = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {}
res[PDF.name] = {"paginas": len(pr.paginas), "em_branco": marcadas, "observacoes": obs}
SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(PDF.name[:40], len(pr.paginas), marcadas, obs)
