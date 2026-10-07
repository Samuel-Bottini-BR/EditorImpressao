"""Verificador 2.1: soma de cada resultado do limpar pontinhos (DLL st_ferramentas)
e do detector de gravura (st_gravura) nas paginas-gabarito, com o codigo de <raiz>.
Uso: python somas_ferramentas.py <raiz> <saida.json>"""
import hashlib, json, sys
from pathlib import Path
raiz, saida = sys.argv[1:3]
sys.path.insert(0, raiz)
import cv2, numpy as np
from core import pontinhos_scantailor as P, st_ferramentas as ST
from core import gravura_scantailor as G
GAB = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
res = {"dll": str(ST.padrao().caminho if hasattr(ST.padrao(), "caminho") else "?")}
for png in sorted(GAB.glob("*.png")):
    img = cv2.imdecode(np.fromfile(str(png), np.uint8), cv2.IMREAD_COLOR)
    for forca in ("pouco", "normal", "muito"):
        for dpi in (150, 300):
            b, r = P.preto_e_branco_com_pontinhos_do_scantailor(img, dpi, forca)
            res[f"{png.stem}|{forca}|{dpi}"] = [r.disponivel, hashlib.sha256(b.tobytes()).hexdigest()[:20]]
    g = G.detectar_gravura(img, 300)
    m = getattr(g, "mascara", None)
    res[f"{png.stem}|gravura"] = [m is not None, hashlib.sha256(m.tobytes()).hexdigest()[:20] if m is not None else None]
Path(saida).write_text(json.dumps(res, indent=0), encoding="utf-8")
print(len(res), sum(1 for k, v in res.items() if k != "dll" and v[0]))
