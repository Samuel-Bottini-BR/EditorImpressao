import sys
sys.path.insert(0, r'D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo')
from core import pipeline, corte_pelo_conteudo as cc
from core.filtros import ORIGINAL
from modelos import Projeto
COPIA = r'D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo\saida_teste\livro\egenloff_1a14.pdf'
campos = {"so25": {"cortar_pelo_conteudo": True}, "as_duas": {"cortar_pelo_conteudo": True, "borda_preta": True}}[sys.argv[1]]
p = Projeto(caminho_entrada=COPIA, nome="e", **campos); p.filtro_padrao = ORIGINAL; p.limpar = False; p.qualidade_dpi = 300
p = pipeline.analisar_projeto(p)
pipeline.medir_conteudo_do_livro(p)
from core.pdf_io import abrir_pdf, pagina_para_array
doc = abrir_pdf(COPIA)
pg = p.paginas[2]; f = p.folhas[pg.folha]
img = pagina_para_array(doc, f.indice, dpi=300)
pipeline._guardar_geometria(f, pg, p, img, doc)
out, des = pipeline.preparar_metade_e_geometria(img, f, pg, p, dpi=300)
ch = pipeline._chave_da_geometria(f, pg, p); med = pipeline._CONTEUDOS[ch]
m = med.medida
print(sys.argv[1], 'alertas', pg.alertas, 'caixa', [round(v) for v in m.caixa], 'limite', None if m.limite is None else [round(v) for v in m.limite], 'img', (m.largura, m.altura), 'cand', len(med.candidatas), 'pecas', None if med.pecas is None else len(med.pecas))
print('recorte', [round(v, 3) for v in des['recorte']])
import cv2
x, y, w, h = des['recorte']; H, W = img.shape[:2]
print('corte px', round(x*W), round(y*H), round((x+w)*W), round((y+h)*H))
for c in med.candidatas:
    (a0, b0, a1, b1), s = c
    if b1 > 3800: print('peca', [round(v) for v in (a0, b0, a1, b1)], s)
cv2.imwrite(r'D:\programas\EditorImpressao\.claude\worktrees\caixa-conteudo\saida_teste\livro\eg3_' + sys.argv[1] + '.jpg', cv2.resize(out, None, fx=0.2, fy=0.2))
livro = pipeline.tamanho_do_livro(p)
cx = cc.caixa_do_corte(m, livro); print('cx', [round(v) for v in cx])
print('sp', [round(v) for v in cc.sem_partir(cx, med.candidatas, cc.caixa_do_corte(m), m)])
x0,y0,x1,y1 = cx
for (a0,b0,a1,b1),_s in med.candidatas:
    if (b0 < y0 < b1 or b0 < y1 < b1) and not (a1 <= x0 or a0 >= x1): print('atravessa y', [round(v) for v in (a0,b0,a1,b1)])
