"""Lugar 2 dos "8 que comem a página" (D-104): procura no acervo páginas em que o
corte automático de fábrica (livro novo) deixa de fora peças do tamanho de letra
logo ao lado do corte (número de página, reclamo, número de item, nota curta).

Para cada página: a geometria de fábrica (core.pipeline._geometria, 300 DPI) e as
peças de tinta do corte comum (Recorte.pecas); conta as peças do tamanho de
letra INTEIRAS de fora, a até 4% do lado do corte, na faixa do corte no outro
eixo. Só lê o acervo. USO: python varrer_tinta_fora.py <raiz> <saida.json> livro:pag ...
"""
import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "etapa10a_localappdata")


def main():
    import cv2
    import numpy as np
    import reproduzir as R
    from core import pipeline, recortar
    from core.endireitar import rotacionar
    from core.pdf_io import abrir_pdf, pagina_para_array

    saida = {}
    for alvo in sys.argv[3:]:
        livro, n = alvo.split(":")
        projeto, no = R.carregar_de_fabrica(livro, int(n))
        pag = R.paginas_da_folha(projeto, no)[0]
        folha = projeto.folhas[pag.folha]
        doc = abrir_pdf(projeto.caminho_entrada)
        img = pagina_para_array(doc, folha.indice, dpi=300)
        doc.close()
        base = pipeline.preparar_para_recorte(img, folha, pag, projeto)
        rec, ang = pipeline._geometria(base, pag, projeto, dpi=300)
        cinza = cv2.cvtColor(base, cv2.COLOR_BGR2GRAY)
        reta = rotacionar(cinza, ang) if abs(ang) >= 0.1 else cinza
        comum = recortar.detectar_bordas(reta, dpi=300, girada=ang if abs(ang) >= 0.1 else None,
                                         como_veio=cinza if abs(ang) >= 0.1 else None)
        if rec is None or comum.pecas is None or not len(comum.pecas):
            saida[alvo] = 0
            continue
        x, y, w, h = rec
        x0, y0, x1, y1 = x, y, x + w, y + h
        p = comum.pecas
        alt_px = 800.0
        letra = recortar._de_letra(np.column_stack([p[:, 0] * alt_px * reta.shape[1] / reta.shape[0],
                                                    p[:, 1] * alt_px,
                                                    p[:, 2] * alt_px * reta.shape[1] / reta.shape[0],
                                                    p[:, 3] * alt_px]))
        fora = (p[:, 2] <= x0) | (p[:, 0] >= x1) | (p[:, 3] <= y0) | (p[:, 1] >= y1)
        perto = ((p[:, 2] > x0 - .04) & (p[:, 0] < x1 + .04) & (p[:, 3] > y0 - .04) & (p[:, 1] < y1 + .04))
        na_faixa = (((p[:, 1] + p[:, 3]) / 2 > y0) & ((p[:, 1] + p[:, 3]) / 2 < y1)) | \
                   (((p[:, 0] + p[:, 2]) / 2 > x0) & ((p[:, 0] + p[:, 2]) / 2 < x1))
        sel = letra & fora & perto & na_faixa & (p[:, 4] == 0)
        saida[alvo] = {"n": int(sel.sum()), "pecas": p[sel, :4].round(4).tolist(), "corte": [x0, y0, x1, y1]}
        print(alvo, int(sel.sum()), flush=True)
    Path(sys.argv[2]).write_text(json.dumps(saida, indent=1), encoding="utf-8")


main()
