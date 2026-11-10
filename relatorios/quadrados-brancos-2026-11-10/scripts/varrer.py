"""Varre um livro inteiro, livro novo, filtro escolhido a mao (como o painel), no tamanho
do PDF (core.pipeline._pagina_pronta), e mede em cada pagina os pontos que viraram branco
puro onde o original NAO era papel (luz entre 45% e 80% do nivel do papel: nem tinta
escura, nem papel) e quantos blocos disso ha (pedaco >= meio quadrado de 24x24).
Uso: python varrer.py <saida> <livro.pdf> <variante> [CANDIDATO=1 no ambiente]"""
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reproduzir as R  # noqa: E402  (prepara LOCALAPPDATA e o caminho do programa)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402


def medir(orig, img):
    cinza = F._para_cinza(orig).astype(np.float32)
    nivel = float(np.percentile(cinza[::4, ::4], F.BRANCO_PERCENTIL))
    nao_papel = (cinza < 0.80 * nivel) & (cinza > 0.45 * nivel)
    if img.ndim == 2:
        branco = img >= 255
    else:
        branco = (img >= 255).all(axis=2)
    novo = branco & nao_papel
    n, _r, st, _c = cv2.connectedComponentsWithStats(novo.astype(np.uint8), 8)
    blocos = int((st[1:, cv2.CC_STAT_AREA] >= 288).sum())
    return round(100 * float(novo.mean()), 3), blocos, round(100 * float(nao_papel.mean()), 1)


def main():
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    pdf, variante = sys.argv[2], sys.argv[3]
    paginas = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    if os.environ.get("CANDIDATO") == "1":
        import candidato
        candidato.instalar()
    projeto = R.livro_novo(pdf)
    lista = paginas or list(range(1, len(projeto.paginas) + 1))
    res = {}
    arq = saida / f"{variante}.json"
    doc = abrir_pdf(pdf)
    try:
        for numero in lista:
            t = time.monotonic()
            p, pag = R.preparar(projeto, numero - 1, variante)
            folha = p.folhas[pag.folha]
            img, _ = pipeline._pagina_pronta(p, doc, folha, pag, pipeline._FolhaDaVez(), 0)
            orig = pagina_para_array(doc, folha.indice, dpi=p.qualidade_dpi)
            if orig.shape[:2] != img.shape[:2]:
                orig = cv2.resize(orig, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
            pct, blocos, nao_papel = medir(orig, img)
            res[numero] = {"branco_em_pintura_pct": pct, "blocos": blocos, "pintura_pct": nao_papel}
            pequena = cv2.resize(img, (img.shape[1] // 4, img.shape[0] // 4), interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(saida / f"{variante}_p{numero:03d}.jpg"), pequena, [cv2.IMWRITE_JPEG_QUALITY, 85])
            print(numero, res[numero], f"{time.monotonic() - t:.1f}s", flush=True)
            arq.write_text(json.dumps(res, indent=1), encoding="utf-8")
    finally:
        doc.close()


if __name__ == "__main__":
    main()
