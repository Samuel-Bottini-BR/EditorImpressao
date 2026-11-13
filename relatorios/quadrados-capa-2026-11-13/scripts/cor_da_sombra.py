"""Quadrados na capa (13/11/2026): onde o passo "sombra da foto de celular" (core.filtros.
_sombra_em_quadros) acha "sombra", quanta COR tem o original ali? Compara as capas coloridas com
as fotos de celular para as quais o passo foi feito (Razoes 57, Atanasio 8). So mede; nao muda nada.
    python cor_da_sombra.py <raiz> <pdf> <pagina> [<pdf> <pagina> ...]"""
import os, sys, json
from pathlib import Path
RAIZ = Path(sys.argv[1]).resolve()
DADOS = Path(__file__).resolve().parents[1] / "_trabalho" / "dados" / "cor"
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS); os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
sys.path.insert(0, str(RAIZ)); os.chdir(RAIZ)
import cv2, numpy as np
from core import filtros as F
from core.pdf_io import abrir_pdf, pagina_para_array
args = sys.argv[2:]
for pdf, pag in zip(args[::2], args[1::2]):
    doc = abrir_pdf(pdf)
    try:
        img = pagina_para_array(doc, int(pag) - 1, dpi=150)
    finally:
        doc.close()
    cinza = F._cinza_para_binarizar(img)
    r = F._sombra_em_quadros(cinza)
    if r is None:
        print(json.dumps({"livro": Path(pdf).stem[:30], "pagina": pag, "sombra": 0})); continue
    luz, sombra = r
    sat = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]
    s = cv2.resize(sat, (sombra.shape[1], sombra.shape[0]), interpolation=cv2.INTER_AREA)
    print(json.dumps({"livro": Path(pdf).stem[:30], "pagina": pag,
                      "quadros_de_sombra_pct": round(100 * float(sombra.mean()), 1),
                      "cor_media_na_sombra": round(float(s[sombra].mean()), 1) if sombra.any() else None,
                      "cor_maxima_na_sombra": round(float(np.percentile(s[sombra], 90)), 1) if sombra.any() else None}))
