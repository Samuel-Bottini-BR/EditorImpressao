"""D-582 (a): como o filtro classifica cada gravura que o Automatico marcou na capa."""
import json, os, sys
from pathlib import Path
AQUI = Path(__file__).resolve().parents[2] / "_tmp"   # a copia do projeto mora em <worktree>/_tmp/dados
sys.path.insert(0, str(AQUI.parent))
os.environ["LOCALAPPDATA"] = str(AQUI / "dados"); os.environ["TEMP"] = os.environ["TMP"] = str(AQUI / "temp")
import numpy as np
from core.pdf_io import abrir_pdf
from core.pipeline import renderizar_com_filtro
from core import filtros as F
from core.selecao import GRAVURA, LETRA, PAPEL
from modelos import Projeto
PASTA = AQUI / "dados/EditorImpressao/projetos/Na escola de Jesus - Catecismo explicado com imagens"
projeto = Projeto.de_dicionario(json.loads((PASTA / "projeto.json").read_text(encoding="utf-8")))
IDX = int(os.environ.get("PAG", "0"))
pag = projeto.paginas[IDX]
doc = abrir_pdf(projeto.caminho_entrada)
img, _ = renderizar_com_filtro(doc, projeto, pag, "original", dpi=110)
doc.close()
sel = pag.obter_selecao()
h, w = img.shape[:2]
pg, pl, pp = (sel.peso(h, w, t) for t in (GRAVURA, LETRA, PAPEL))
print(f"pagina {IDX+1}: gravura cobre {(pg>0.5).mean():.0%}, letra {(pl>0.5).mean():.0%}, papel {(pp>0.5).mean():.0%} da pagina")
img3 = F._tres_canais(img)
rot, foto, deco, ref = F._tipos_das_zonas(img3, pg, com_decoracao=True)
for z in range(1, len(foto)):
    area = (rot == z).mean()
    tipo = "FOTO/PINTURA (tons de cinza)" if foto[z] else ("DECORACAO COLORIDA (fica com a cor)" if deco[z] else "DESENHO (preto e branco)")
    print(f"  zona {z}: {area:.1%} da pagina -> {tipo}")
print("capa automatica?", F._e_a_capa_automatica(sel))
