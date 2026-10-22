"""Verificador, 22/10/2026: tempo da passada que mede o livro + geracao do PDF, com as duas opcoes
ligadas (cortar pelo conteudo + borda preta ate a moldura), filtro Original, 300 DPI, livro novo.
Uso: python tempo_total.py <raiz do codigo> <pdf de entrada> <pdf de saida> <json de saida>
Grava no json: tempos, tamanho de cada pagina do PDF (mm) e os avisos de cada pagina."""
import json
import sys
import time

raiz, entrada, saida, js = sys.argv[1:5]
sys.path.insert(0, raiz)
import fitz  # noqa: E402
from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from modelos import Projeto  # noqa: E402

p = Projeto(caminho_entrada=entrada, nome="t", cortar_pelo_conteudo=True, borda_preta=True,
            borda_preta_ate="ate_a_moldura")
p.filtro_padrao = ORIGINAL
p.limpar = False
p.qualidade_dpi = 300
t0 = time.perf_counter()
p = pipeline.analisar_projeto(p)
t1 = time.perf_counter()
pipeline.medir_conteudo_do_livro(p)
t2 = time.perf_counter()
p.caminho_saida = saida
pipeline.processar(p)
t3 = time.perf_counter()
with fitz.open(saida) as d:
    tam = [(round(pg.rect.width * 25.4 / 72, 1), round(pg.rect.height * 25.4 / 72, 1)) for pg in d]
r = {"raiz": raiz, "analise": round(t1 - t0, 1), "passada": round(t2 - t1, 1), "geracao": round(t3 - t2, 1),
     "total": round(t3 - t1, 1), "paginas": len(tam), "tamanhos_mm": tam,
     "avisos": {pg.indice: list(pg.alertas) for pg in p.paginas if pg.alertas}}
open(js, "w", encoding="utf-8").write(json.dumps(r, ensure_ascii=False))
print(raiz.rstrip("\\/").split("\\")[-1], "passada", r["passada"], "geracao", r["geracao"], "total", r["total"])
