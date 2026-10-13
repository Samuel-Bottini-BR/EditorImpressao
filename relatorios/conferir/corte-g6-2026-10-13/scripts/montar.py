"""Imagem lado a lado (ordem antiga | ordem nova) de cada pagina, com os
quatro cantos ampliados embaixo.

Le as paginas prontas que o medir.py guardou (_tmp/finais/<base>__B.jpg e
__C.jpg, 300 DPI, sem filtro) e o dados.json. Esquerda: B = cortar antes
(ordem antiga) com o MESMO angulo do livro novo. Direita: C = endireitar
antes (livro novo). As duas na mesma escala (o mesmo milimetro tem o mesmo
tamanho nas duas), para se ver a pagina que cresceu.

USO   python montar.py base[,base...]     ->  img/lado-<base>.jpg
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[2]
FINAIS = RAIZ / "_tmp" / "finais"
ALTURA = 1000          # altura da pagina maior, na miniatura
CANTO_PX = 640         # lado do canto, em pontos da pagina a 300 DPI (5,4 cm)
CANTO_NA_TELA = 340
FUNDO = (232, 228, 222)
ROTULOS = {"B": "ORDEM ANTIGA  (corta, depois endireita)",
           "C": "ORDEM NOVA, livro novo  (endireita, depois corta)"}


def _texto(img, texto, x, y, tamanho=0.6, cor=(20, 20, 20), grosso=1):
    cv2.putText(img, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, tamanho, cor, grosso, cv2.LINE_AA)


def _coluna(img: np.ndarray, fator: float, largura: int, cfg: str, r: dict) -> np.ndarray:
    a, l = img.shape[:2]
    mini = cv2.resize(img, (max(1, round(l * fator)), max(1, round(a * fator))),
                      interpolation=cv2.INTER_AREA)
    mini = cv2.copyMakeBorder(mini, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(0, 0, 200))
    quadro = np.full((ALTURA + 4 + 70, largura, 3), FUNDO, np.uint8)
    _texto(quadro, ROTULOS[cfg], 8, 24, 0.62, grosso=2)
    le = r["lados_escuro"]
    _texto(quadro, f"{r['tamanho_mm'][0]:.0f} x {r['tamanho_mm'][1]:.0f} mm   giro {r['angulo']:+.2f} grau   "
                   f"faixa escura na beirada {100 * r['beirada_escuro']:.1f}% da pagina", 8, 46, 0.5)
    _texto(quadro, "faixa por lado (mm): esq {:.1f}  dir {:.1f}  topo {:.1f}  pe {:.1f}   "
                   "pecas partidas {}  fora {}".format(le["esq"]["mm"], le["dir"]["mm"], le["topo"]["mm"],
                                                       le["pe"]["mm"], r["pecas_partidas"], r["pecas_fora"]),
           8, 64, 0.5)
    x = (largura - mini.shape[1]) // 2
    quadro[70:70 + mini.shape[0], x:x + mini.shape[1]] = mini
    # os quatro cantos
    lado = min(CANTO_PX, a, l)
    cantos = [("canto de cima, esquerda", img[:lado, :lado]), ("canto de cima, direita", img[:lado, l - lado:]),
              ("canto de baixo, esquerda", img[a - lado:, :lado]), ("canto de baixo, direita", img[a - lado:, l - lado:])]
    grade = np.full((2 * (CANTO_NA_TELA + 30) + 10, largura, 3), FUNDO, np.uint8)
    folga = (largura - 2 * CANTO_NA_TELA) // 3
    for i, (nome, c) in enumerate(cantos):
        c = cv2.resize(np.ascontiguousarray(c), (CANTO_NA_TELA, CANTO_NA_TELA), interpolation=cv2.INTER_AREA)
        cv2.rectangle(c, (0, 0), (CANTO_NA_TELA - 1, CANTO_NA_TELA - 1), (0, 0, 200), 2)
        gx = folga + (i % 2) * (CANTO_NA_TELA + folga)
        gy = 26 + (i // 2) * (CANTO_NA_TELA + 30)
        _texto(grade, nome, gx, gy - 7, 0.48)
        grade[gy:gy + CANTO_NA_TELA, gx:gx + CANTO_NA_TELA] = c
    return np.vstack([quadro, grade])


def montar(base: str, dados: dict, destino: Path | None = None) -> Path:
    d = dados[base]
    imgs = {c: cv2.imread(str(FINAIS / f"{base}__{c}.jpg")) for c in ("B", "C")}
    maior = max(i.shape[0] for i in imgs.values())
    fator = ALTURA / maior
    largura = max(2 * CANTO_NA_TELA + 60, max(round(i.shape[1] * fator) for i in imgs.values()) + 24)
    colunas = [_coluna(imgs[c], fator, largura, c, d[c]) for c in ("B", "C")]
    meio = np.full((colunas[0].shape[0], 10, 3), 255, np.uint8)
    corpo = np.hstack([colunas[0], meio, colunas[1]])
    topo = np.full((40, corpo.shape[1], 3), (60, 60, 60), np.uint8)
    _texto(topo, f"{base.replace('__inteira', '').replace('__', ' ')}   (sem filtro, 300 DPI; cantos ampliados embaixo)",
           10, 27, 0.7, (255, 255, 255), 2)
    destino = destino or (PASTA / "img" / f"lado-{base}.jpg")
    destino.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(destino), np.vstack([topo, corpo]), [cv2.IMWRITE_JPEG_QUALITY, 82])
    return destino


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    for base in sys.argv[1].split(","):
        print(montar(base, dados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
