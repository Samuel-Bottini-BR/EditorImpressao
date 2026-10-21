"""21/10: procura nas paginas-gabarito uma com o aviso "Desenho ou escrita?" (para fotografar a frase nova).
Analise do programa (analisar_projeto) com o codigo desta worktree. So le o gabarito."""
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "verif_pr_dados")
sys.path.insert(0, str(RAIZ))
from core import analise  # noqa: E402
from core import pipeline as P  # noqa: E402
from modelos import Projeto  # noqa: E402

for pdf in sorted(Path(r"D:\programas\EditorImpressao\gabarito\paginas").glob("*.pdf")):
    pr = P.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=pdf.stem))
    achou = [p.indice for p in pr.paginas if analise.DESENHO_OU_ESCRITA in p.alertas]
    print(pdf.stem, achou, flush=True)
