"""Monta, para cada pagina pedida, as tres paginas prontas lado a lado, na
MESMA escala: ordem antiga (B), ordem nova de hoje (C) e ordem nova
consertada (C depois). Para o verificador abrir e olhar.

Le as paginas prontas a 300 DPI de _tmp/finais (gravadas pelo medir.py nas
duas rodadas: "<base>__B.jpg", "<base>__C.jpg" e "<base>__C__depois.jpg") e
o comparacao.json. Grava em relatorios/conferir/conserto-corte-g6-2026-10-13/
img/tres-<base>.jpg (pasta que o git ignora: imagem pesada se refaz).

USO  python montar.py [base,base,...]     (sem nada: as que mudaram, as 8 e o gabarito do G6)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
FINAIS = RAIZ / "_tmp" / "finais"
DESTINO = RAIZ / "relatorios" / "conferir" / "conserto-corte-g6-2026-10-13" / "img"
ALTURA = 1500          # altura, em pontos, da pagina mais alta das tres


def pct(v: float) -> str:
    return f"{100 * v:.1f}%".replace(".", ",")


def quadro(img: np.ndarray, f: float, titulo: str, linha2: str, altura: int) -> np.ndarray:
    p = cv2.resize(img, (max(1, round(img.shape[1] * f)), max(1, round(img.shape[0] * f))),
                   interpolation=cv2.INTER_AREA)
    p = cv2.copyMakeBorder(p, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(0, 0, 200))
    tela = np.full((altura + 70, p.shape[1] + 24, 3), 228, np.uint8)
    tela[60:60 + p.shape[0], 12:12 + p.shape[1]] = p
    cv2.putText(tela, titulo, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(tela, linha2, (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)
    return tela


def main() -> int:
    comp = json.loads((PASTA / "comparacao.json").read_text(encoding="utf-8"))
    tres = comp["tres_colunas"]
    if len(sys.argv) > 1:
        bases = sys.argv[1].split(",")
    else:
        sys.path.insert(0, str(AQUI))
        import comparar as C

        bases = list(dict.fromkeys(comp["mudaram_na_ordem_nova"] + C.AS_OITO
                                   + [b for b in tres if b.split("__")[0] in C.GABARITO_DO_G6]))
    DESTINO.mkdir(parents=True, exist_ok=True)
    for base in bases:
        imgs = [cv2.imread(str(FINAIS / f"{base}__{sufixo}.jpg")) for sufixo in ("B", "C", "C__depois")]
        if any(i is None for i in imgs):
            print("falta imagem de", base)
            continue
        f = ALTURA / max(i.shape[0] for i in imgs)
        altura = max(round(i.shape[0] * f) for i in imgs) + 4
        t = tres[base]
        partes = []
        for img, nome, chave in zip(imgs, ("ORDEM ANTIGA", "ORDEM NOVA, HOJE", "ORDEM NOVA, CONSERTADA"),
                                    ("antiga_B", "nova_de_hoje", "nova_consertada")):
            r = t[chave]
            lados = " ".join(f"{k} {v['mm']:.0f}" for k, v in r["lados_escuro"].items())
            partes.append(quadro(img, f, f"{nome}  {r['tamanho_mm'][0]:.0f} x {r['tamanho_mm'][1]:.0f} mm",
                                 f"faixa escura {pct(r['beirada_escuro'])}  (mm: {lados})  tinta de fora "
                                 f"{100 * r['tinta_perdida']:.2f}%", altura))
        junto = np.hstack(partes)
        cabeca = np.full((40, junto.shape[1], 3), 60, np.uint8)
        cv2.putText(cabeca, f"{base}   (sem filtro, 300 DPI, mesma escala)", (12, 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
        cv2.imwrite(str(DESTINO / f"tres-{base}.jpg"), np.vstack([cabeca, junto]),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        print("gravado", DESTINO / f"tres-{base}.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
