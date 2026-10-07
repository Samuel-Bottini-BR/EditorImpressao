"""Verificador 2.1: abre um projeto.json (COPIA) com o codigo de <raiz>, como o
programa abre (Projeto.de_dicionario), e grava: a divisao de cada folha, a soma
de cada previa (renderizar_pagina, o que a tela mostra, 100 DPI) e o PDF final
(processar, 300 DPI do projeto), com a soma de cada pagina desenhada a 72 DPI.
Uso: python processar_antigo.py <raiz> <projeto.json> <saida_dir> [max_previas]"""
import hashlib, json, sys, time
from pathlib import Path
raiz, pj, saida = sys.argv[1:4]
maxp = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
sys.path.insert(0, raiz)
import fitz
from core import pipeline
from core.pdf_io import abrir_pdf
from modelos import Projeto
Path(saida).mkdir(parents=True, exist_ok=True)
projeto = Projeto.de_dicionario(json.loads(Path(pj).read_text(encoding="utf-8")))
res = {"folhas": [(f.dividir, round(f.posicao_corte, 6)) for f in projeto.folhas],
       "paginas": len(projeto.paginas), "ativas": [(p.indice, p.folha, p.metade) for p in projeto.paginas_ativas],
       "dividir_como": getattr(projeto, "dividir_como", None), "dividir_folhas": projeto.dividir_folhas}
doc = abrir_pdf(projeto.caminho_entrada)
prev = {}
t = time.time()
for p in projeto.paginas_ativas[:maxp]:
    img, _ = pipeline.renderizar_pagina(doc, projeto, p, dpi=100)
    prev[p.indice] = hashlib.sha256(img.tobytes()).hexdigest()[:20] + f"|{img.shape}"
doc.close()
res["previas"] = prev; res["t_previas"] = round(time.time() - t, 1)
projeto.caminho_saida = str(Path(saida).resolve() / "saida.pdf")
t = time.time()
final = pipeline.processar(projeto)
res["t_processar"] = round(time.time() - t, 1)
pdf = fitz.open(final)
res["pdf"] = [hashlib.sha256(pg.get_pixmap(dpi=72).samples).hexdigest()[:20] for pg in pdf]
res["pdf_tamanhos"] = [(round(pg.rect.width), round(pg.rect.height)) for pg in pdf]
pdf.close()
Path(saida, "resultado.json").write_text(json.dumps(res, indent=0), encoding="utf-8")
print(json.dumps({k: (v if not isinstance(v, (list, dict)) else len(v)) for k, v in res.items()}))
