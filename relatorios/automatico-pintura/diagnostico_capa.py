"""D-585, a causa: como o Preto e branco classifica cada gravura marcada de uma página do
"Na escola de Jesus" (cópia do projeto em <worktree>/_tmp/dados), e por quê: as duas medidas
de _e_foto_ou_pintura (espessura e traço) e a de _e_decoracao_colorida (cor larga).
Uso: python relatorios/automatico-pintura/diagnostico_capa.py [indice] [dpi]
"""
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(RAIZ / "_tmp" / "temp")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_com_filtro  # noqa: E402
from core.selecao import GRAVURA, LETRA, PAPEL  # noqa: E402
from modelos import Projeto  # noqa: E402

PASTA = RAIZ / "_tmp/dados/EditorImpressao/projetos/Na escola de Jesus - Catecismo explicado com imagens"
IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 0
DPI = int(sys.argv[2]) if len(sys.argv) > 2 else 110


def medidas_da_zona(img3, zona, caixa, menor_lado, referencia):
    x, y, w, h = caixa
    dist = cv2.distanceTransform(np.pad(zona.astype(np.uint8), 1), cv2.DIST_L2, 5)
    espessura = 2.0 * float(dist.max()) / menor_lado
    lab = cv2.cvtColor(img3[y:y + h, x:x + w], cv2.COLOR_BGR2LAB)
    luz, fundo, nivel = F._fundo_e_nivel(lab)
    traco = float((F._peso_de_traco(luz, fundo, nivel) >= 128).mean())
    deco = F._e_decoracao_colorida(img3, zona, caixa, menor_lado, referencia)
    return espessura, traco, deco


def main():
    projeto = Projeto.de_dicionario(json.loads((PASTA / "projeto.json").read_text(encoding="utf-8")))
    pag = projeto.paginas[IDX]
    doc = abrir_pdf(projeto.caminho_entrada)
    img, _ = renderizar_com_filtro(doc, projeto, pag, "original", dpi=DPI)
    doc.close()
    sel = pag.obter_selecao()
    h, w = img.shape[:2]
    pg, pl, pp = (sel.peso(h, w, t) for t in (GRAVURA, LETRA, PAPEL))
    print(f"pagina {IDX + 1} ({w}x{h}): gravura {(pg > 0.5).mean():.0%}, letra {(pl > 0.5).mean():.0%}, "
          f"papel {(pp > 0.5).mean():.0%}")
    img3 = F._tres_canais(img)
    menor = min(h, w)
    onde = (pg > 0).astype(np.uint8)
    n, rot, med, _c = cv2.connectedComponentsWithStats(onde, connectivity=8)
    ref = F._referencia_do_papel(img3, onde > 0)
    print(f"  referencia do papel (nivel, a, b, raio) = {tuple(round(float(v), 1) for v in ref)}")
    print(f"  limites: espessura >= {F.FOTO_ESPESSURA_MINIMA}, traco < {F.GRAVURA_DE_TRACO_MINIMA}")
    for i in range(1, n):
        x, y, ww, hh = (int(v) for v in med[i, :4])
        zona = rot[y:y + hh, x:x + ww] == i
        esp, tr, deco = medidas_da_zona(img3, zona, (x, y, ww, hh), menor, ref)
        foto = esp >= F.FOTO_ESPESSURA_MINIMA and tr < F.GRAVURA_DE_TRACO_MINIMA
        tipo = "FOTO/PINTURA" if foto else ("DECORACAO" if deco else "DESENHO")
        print(f"  zona {i}: {med[i, 4] / (h * w):.1%} da pagina, espessura {esp:.2f}, traco {tr:.3f}, "
              f"cor larga={deco} -> {tipo}")


main()
