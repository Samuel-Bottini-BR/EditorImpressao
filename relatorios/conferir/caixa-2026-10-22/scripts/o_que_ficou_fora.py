"""Verificador 22/10, passo 3: O QUE o aviso "Corte deixou algo de fora" esta vendo. Pelo caminho do livro novo
(nao precisou dividir -> endireitada -> cortada com as duas opcoes -> Original, 300 DPI), escuta a funcao do
programa que acha a caixa do livro (_caixa_do_livro) e pega as pecas que ela conta como "tiradas"
(corte_pelo_conteudo.tiradas_do_corte, a mesma conta do aviso). Desenha a pagina endireitada inteira, com o que
o corte tira em vermelho claro e cada peca "tirada" cercada por um retangulo azul POR FORA (nada por cima).
Uso: python o_que_ficou_fora.py <raiz do codigo> <pdf> <prefixo saida> <livro> <paginas 1-based, virgula>"""
import json
import sys

raiz, entrada, prefixo, livro_nome, quais = sys.argv[1:6]
sys.path.insert(0, raiz)
import cv2  # noqa: E402
import numpy as np  # noqa: E402
from core import pipeline, corte_pelo_conteudo as cpc  # noqa: E402
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
orig_prep = pipeline._preparar_endireitando_antes
orig_caixa = pipeline._caixa_do_livro


def escuta_prep(inteira, recorte, angulo, projeto, so_a_geometria):
    pego.update(angulo=float(angulo), inteira=inteira)
    return orig_prep(inteira, recorte, angulo, projeto, so_a_geometria)


def escuta_caixa(folha, pagina, projeto):
    r = orig_caixa(folha, pagina, projeto)
    if r is not None:
        pego["achado"] = r
    return r


pipeline._preparar_endireitando_antes = escuta_prep
pipeline._caixa_do_livro = escuta_caixa
doc = abrir_pdf(entrada)
info = {}
for n in [int(x) for x in quais.split(",")]:
    pg = p.paginas[n - 1]
    f = p.folhas[pg.folha]
    img = pagina_para_array(doc, f.indice, dpi=300)
    if pipeline._geometria_guardada(f, pg, p) is None:
        pipeline._guardar_geometria(f, pg, p, img, doc)
    pego.clear()
    pipeline.preparar_metade_e_geometria(img, f, pg, p, dpi=300)
    inteira = pego["inteira"]
    girar = p.endireitar and abs(pego["angulo"]) >= pipeline.ANGULO_MINIMO
    reta = pipeline.rotacionar(inteira, pego["angulo"]) if girar else inteira
    if "achado" not in pego:
        info[n] = {"sem_caixa": True}; print(n, "sem caixa"); continue
    medido, caixa, _ = pego["achado"]
    W, H = medido.medida.largura, medido.medida.altura
    sx, sy = reta.shape[1] / W, reta.shape[0] / H
    tiradas = cpc.tiradas_do_corte(caixa, medido.candidatas)
    mm = medido.medida.mm_por_ponto
    lista = []
    for (a, b, c, d) in tiradas:
        lista.append({"x0": round(a * sx), "y0": round(b * sy), "x1": round(c * sx), "y1": round(d * sy),
                      "mm": [round((c - a) * mm[0], 1), round((d - b) * mm[1], 1)]})
    cx = [round(caixa[0] * sx), round(caixa[1] * sy), round(caixa[2] * sx), round(caixa[3] * sy)]
    # desenho: fora da caixa em vermelho claro (como no desenhar.py), retangulo azul por fora de cada peca
    g = cv2.cvtColor(reta, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    fora = np.ones(g.shape, bool); fora[max(0, cx[1]):cx[3], max(0, cx[0]):cx[2]] = False
    out = reta.copy(); verm = np.zeros_like(reta); verm[..., 2] = 255
    verm[..., 1] = (g * 205).astype(np.uint8); verm[..., 0] = (g * 205).astype(np.uint8)
    out[fora] = verm[fora]
    for t in lista:
        m = 14
        cv2.rectangle(out, (t["x0"] - m, t["y0"] - m), (t["x1"] + m, t["y1"] + m), (255, 80, 0), 7)
    cv2.imwrite(f"{prefixo}_p{n:03d}_fora.png", out)
    info[n] = {"caixa": cx, "tiradas": lista, "avisos": list(pg.alertas)}
    print(n, cx, len(lista), [t["mm"] for t in lista][:8])
open(prefixo + "_fora.json", "w", encoding="utf-8").write(json.dumps(info, ensure_ascii=False, indent=1))
