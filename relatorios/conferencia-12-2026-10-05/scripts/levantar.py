"""Levantamento (so leitura): que tipo de zona de imagem o Misto acha em cada pagina do gabarito."""
import sys
import comum12  # noqa: F401
from comum11 import preparada
from core import filtros as F
from core.misto import _peso_da_imagem

for pid in sys.argv[1:]:
    img, sel, aj = preparada(pid)
    h, w = img.shape[:2]
    peso = _peso_da_imagem(sel, h, w)
    if not peso.any():
        print(pid, "sem zona de imagem", flush=True); continue
    rot, foto, deco, ref = F._tipos_das_zonas(F._tres_canais(img), peso)
    import numpy as np
    for i in range(1, len(foto)):
        ys, xs = np.nonzero(rot == i)
        tipo = "foto" if foto[i] else ("decoracao" if deco[i] else "desenho")
        print(pid, i, tipo, "caixa(frac)=%.2f,%.2f,%.2f,%.2f" % (xs.min()/w, ys.min()/h, xs.max()/w, ys.max()/h), "area=%.3f" % (len(xs)/(h*w)), flush=True)
