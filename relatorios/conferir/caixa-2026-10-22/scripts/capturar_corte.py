"""Verificador, 22/10/2026: para cada pagina pedida, a pagina INTEIRA ja endireitada (antes do corte) e a caixa
do corte que o programa usou nela, pelo caminho do livro novo (dividir -> endireitar -> cortar), com as duas
opcoes ligadas (cortar pelo conteudo + borda preta ate a moldura), Original, 300 DPI.
Nao muda o programa: so "escuta" a funcao que endireita e corta (_preparar_endireitando_antes) para saber a
caixa e o angulo, e endireita a pagina inteira com a mesma funcao do programa (rotacionar).
Uso: python capturar_corte.py <raiz do codigo> <pdf> <saida .npz por pagina: prefixo> <paginas 1-based, virgula>"""
import json
import sys

raiz, entrada, prefixo, quais = sys.argv[1:5]
sys.path.insert(0, raiz)
import cv2  # noqa: E402
import numpy as np  # noqa: E402
from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from modelos import Projeto  # noqa: E402

p = Projeto(caminho_entrada=entrada, nome="t", cortar_pelo_conteudo=True, borda_preta=True,
            borda_preta_ate="ate_a_moldura")
p.filtro_padrao = ORIGINAL
p.limpar = False
p.qualidade_dpi = 300
p = pipeline.analisar_projeto(p)
pipeline.medir_conteudo_do_livro(p)

pego = {}
original = pipeline._preparar_endireitando_antes


def escuta(inteira, recorte, angulo, projeto, so_a_geometria):
    pego.update(shape=inteira.shape, recorte=None if recorte is None else tuple(recorte), angulo=float(angulo),
                inteira=inteira)
    return original(inteira, recorte, angulo, projeto, so_a_geometria)


pipeline._preparar_endireitando_antes = escuta
doc = abrir_pdf(entrada)
info = {}
for n in [int(x) for x in quais.split(",")]:
    pg = p.paginas[n - 1]
    f = p.folhas[pg.folha]
    img = pagina_para_array(doc, f.indice, dpi=300)
    # como a geracao do PDF: a geometria da pagina guardada antes de desenhar (no codigo de antes a
    # passada nao a guardava; sem isto a pagina sairia sem o tamanho do livro, diferente do PDF)
    if pipeline._geometria_guardada(f, pg, p) is None:
        pipeline._guardar_geometria(f, pg, p, img, doc)
    pego.clear()
    out, des = pipeline.preparar_metade_e_geometria(img, f, pg, p, dpi=300)
    inteira = pego["inteira"]
    girar = p.endireitar and abs(pego["angulo"]) >= pipeline.ANGULO_MINIMO
    reta = pipeline.rotacionar(inteira, pego["angulo"]) if girar else inteira
    caixa = None if pego["recorte"] is None else pipeline.caixa_em_pontos(inteira.shape, pego["recorte"])
    cv2.imwrite(f"{prefixo}_p{n:03d}_reta.png", reta)
    cv2.imwrite(f"{prefixo}_p{n:03d}_saida.png", out)
    info[n] = {"caixa": None if caixa is None else [int(v) for v in caixa], "angulo": pego["angulo"],
               "girou": bool(girar), "shape": list(reta.shape[:2]), "avisos": list(pg.alertas),
               "metade": pg.metade, "folha": f.indice + 1}
    print(n, info[n])
open(prefixo + "_info.json", "w", encoding="utf-8").write(json.dumps(info, ensure_ascii=False, indent=1))
