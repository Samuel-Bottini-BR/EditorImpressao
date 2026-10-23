"""Gera o Egenloff folhas 1-14 pelo programa (analisar + processar) e mede cada pagina."""
import sys, json
sys.path.insert(0, r'D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo')
import fitz
from core import pipeline
from core.filtros import ORIGINAL
from modelos import Projeto
ORIG = r'D:\Livros para editar\Egenloff15271880ModelbuchWHZ_231103_053749.pdf'
COPIA = r'D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo\saida_teste\livro\egenloff_1a14.pdf'
import os
if not os.path.exists(COPIA):
    d = fitz.open(ORIG); n = fitz.open(); n.insert_pdf(d, from_page=0, to_page=13); n.save(COPIA)
cfg = sys.argv[1]
campos = {"so25": {"cortar_pelo_conteudo": True},
          "as_duas": {"cortar_pelo_conteudo": True, "borda_preta": True, "borda_preta_ate": "ate_a_moldura"},
          "hoje": {}}[cfg]
p = Projeto(caminho_entrada=COPIA, nome="egenloff", **campos)
p.filtro_padrao = ORIGINAL; p.limpar = False; p.qualidade_dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 150
p = pipeline.analisar_projeto(p)
p.caminho_saida = COPIA.replace('.pdf', f'_{cfg}.pdf')
pipeline.processar(p)
with fitz.open(p.caminho_saida) as d:
    tam = [(round(pg.rect.width * 25.4 / 72), round(pg.rect.height * 25.4 / 72)) for pg in d]
print(cfg, tam)
livro = pipeline.tamanho_do_livro(p)
print('livro', None if livro is None else (round(livro.largura_mm), round(livro.altura_mm), sorted(livro.muito_maiores)))
print('alertas', {pg.indice: pg.alertas for pg in p.paginas if pg.alertas})
for pg in p.paginas[:6]:
    f = p.folhas[pg.folha]; ch = pipeline._chave_da_geometria(f, pg, p)
    med = pipeline._CONTEUDOS.get(ch); geo = pipeline._GEOMETRIAS.get(ch)
    print(pg.indice, 'tam', pipeline._TAMANHOS.get(ch), 'med', None if med is None else (med.medida.tamanho_mm, med.medida.mm_por_ponto, med.medida.largura, med.medida.altura), 'geo', geo)
from core.pdf_io import abrir_pdf, pagina_para_array
doc = abrir_pdf(p.caminho_entrada)
for i in (2, 3, 4):
    pg = p.paginas[i]; f = p.folhas[pg.folha]
    img = pagina_para_array(doc, f.indice, dpi=p.qualidade_dpi)
    out, des = pipeline.preparar_metade_e_geometria(img, f, pg, p, dpi=p.qualidade_dpi)
    print('desenho', i, img.shape[:2], out.shape[:2], [round(v, 4) for v in des['recorte']] if des.get('recorte') else None, round(out.shape[0]*25.4/300), 'livro', pipeline.tamanho_do_livro(p).como_tupla(), 'muito', pipeline.tamanho_do_livro(p).muito_maiores)
