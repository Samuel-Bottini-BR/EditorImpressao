"""Verificador, 20/10/2026 (item 2.8): as somas das paginas-gabarito com tudo DE FABRICA, escritas
por mim (nao uso o script do implementador), com o codigo de uma pasta dada (--raiz).
Filtros: Original, Preto e branco, Melhorar, e tambem Preto e branco com "So as letras".
Cada pagina sai pelo caminho do programa (analisar_projeto -> renderizar_pagina no DPI do projeto).

USO  python somas.py --raiz <pasta do programa> --saida <arquivo.json>
So le o gabarito; pasta de dados do programa isolada; nada do programa muda."""
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

args = sys.argv[1:]
RAIZ = Path(args[args.index("--raiz") + 1]).resolve()
SAIDA = Path(args[args.index("--saida") + 1])
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "verif28_dados")
sys.path.insert(0, str(RAIZ))

from core import pipeline as P  # noqa: E402
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

assert Path(P.__file__).resolve().is_relative_to(RAIZ)
PAGINAS = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
pids = sorted(p.stem for p in PAGINAS.glob("*.pdf"))
if "--pid" in args:                      # uma pagina por processo (memoria)
    pids = [args[args.index("--pid") + 1]]
res = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {}
for pid in pids:
    projeto = P.analisar_projeto(Projeto(caminho_entrada=str(PAGINAS / f"{pid}.pdf"), nome=pid))
    doc = abrir_pdf(projeto.caminho_entrada)
    for pg in projeto.paginas_ativas:
        nome = pid if len(projeto.paginas_ativas) == 1 else f"{pid}-{pg.metade}"
        for rot, filtro, letras in (("original", ORIGINAL, False), ("pb", PRETO_E_BRANCO, False),
                                    ("melhorar", MELHORAR, False), ("pb_so_letras", PRETO_E_BRANCO, True)):
            pg.filtro = filtro
            projeto.misto_so_as_letras = letras
            img, _ = P.renderizar_pagina(doc, projeto, pg, dpi=projeto.qualidade_dpi)
            res[f"{nome}|{rot}"] = hashlib.md5(img.tobytes() + str(img.shape).encode()).hexdigest()
    doc.close()
    print(pid, len(res), flush=True)
SAIDA.write_text(json.dumps(res, indent=1, sort_keys=True), encoding="utf-8")
print("somas:", len(res), "paginas:", len(pids))
