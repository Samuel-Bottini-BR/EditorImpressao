"""Tempo da passada que mede o livro (core.pipeline.medir_conteudo_do_livro),
com as duas opcoes ligadas. Uso: python tempo_passada.py <raiz do codigo> <pdf> [folhas]"""
import sys, time
raiz, pdf = sys.argv[1], sys.argv[2]
sys.path.insert(0, raiz)
import fitz
from core import pipeline
from core.filtros import ORIGINAL
from modelos import Projeto
n = int(sys.argv[3]) if len(sys.argv) > 3 else None
if n:
    copia = pdf.replace('.pdf', f'_{n}.pdf')
    import os
    if not os.path.exists(copia):
        d = fitz.open(pdf); o = fitz.open(); o.insert_pdf(d, from_page=0, to_page=n - 1); o.save(copia)
    pdf = copia
p = Projeto(caminho_entrada=pdf, nome="t", cortar_pelo_conteudo=True, borda_preta=True)
p.filtro_padrao = ORIGINAL; p.limpar = False; p.qualidade_dpi = 300
p = pipeline.analisar_projeto(p)
t = time.perf_counter(); m = pipeline.medir_conteudo_do_livro(p); s = time.perf_counter() - t
print(f"{raiz.split(chr(92))[-1] or raiz} paginas {m} passada {s:.1f} s ({s / max(1, m):.2f} s/pagina)")
