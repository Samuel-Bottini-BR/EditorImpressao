"""Quadrados na capa (13/11/2026): mede, em cada pagina desenhada por rodar_capa.py, os BLOCOS
BRANCOS onde o original NAO e papel (a capa colorida, a pintura, o fundo escuro).

    python medir_quadros.py <pasta de um livro> [<pasta> ...]

<pasta> tem uma subpasta por variante (pdf.png, previa.png, cartao.png) e a variante "original"
(o filtro Original: a pagina como veio, o mesmo enquadramento). Grava <pasta>/medidas.json e
escreve uma linha por variante.

A medida (a mesma em todas as versoes, para comparar):
  nao_papel  = no original, ponto escuro (cinza < 80% do papel claro, o percentil 95) OU colorido
               (saturacao > 50 em 255): a capa azul, a pintura, a moldura
  bloco      = ponto branco (os tres canais >= 245) que cabe num quadrado branco de lado 1/40 do
               menor lado da pagina (abertura): branco "liso", nao a letra branca fina
  blocos_pct = % dos pontos nao_papel que viraram bloco branco
  blocos_n   = quantos pedacos assim, de pelo menos 2 x 2 quadrados (o tamanho do quadrado do 13-02)
Ressalva: numa capa em que o branco ja era uma area grande no original (titulo branco grande), a
medida conta pouco ou nada; ela nao separa "branco que devia estar la" de "branco que nao devia":
os numeros so apontam onde olhar. A palavra final e a da imagem.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np


def medir(orig: np.ndarray, img: np.ndarray) -> dict:
    if img.shape[:2] != orig.shape[:2]:
        orig = cv2.resize(orig, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    cinza = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY).astype(np.float32)
    sat = cv2.cvtColor(orig, cv2.COLOR_BGR2HSV)[:, :, 1]
    papel = float(np.percentile(cinza, 95))
    nao_papel = (cinza < 0.80 * papel) | (sat > 50)
    branco = (img >= 245).all(axis=2)
    lado = max(3, min(img.shape[:2]) // 40)
    liso = cv2.morphologyEx(branco.astype(np.uint8), cv2.MORPH_OPEN,
                            np.ones((lado, lado), np.uint8)) > 0
    bloco = liso & nao_papel
    n, _r, stats, _c = cv2.connectedComponentsWithStats(bloco.astype(np.uint8), connectivity=8)
    grandes = int(np.sum(stats[1:, cv2.CC_STAT_AREA] >= 4 * lado * lado)) if n > 1 else 0
    return {"blocos_pct": round(100 * float(bloco[nao_papel].mean()), 2) if nao_papel.any() else 0.0,
            "blocos_n": grandes,
            "nao_papel_pct": round(100 * float(nao_papel.mean()), 1)}


def main() -> None:
    for pasta in map(Path, sys.argv[1:]):
        ref = {}
        for nome in ("pdf", "previa", "cartao"):
            arq = pasta / "original" / f"{nome}.png"
            if arq.exists():
                ref[nome] = cv2.imread(str(arq))
        res = {}
        for sub in sorted(p for p in pasta.iterdir() if p.is_dir()):
            for nome, orig in ref.items():
                arq = sub / f"{nome}.png"
                if not arq.exists():
                    continue
                res.setdefault(sub.name, {})[nome] = medir(orig, cv2.imread(str(arq)))
            if sub.name in res:
                print(pasta.name, sub.name, res[sub.name].get("pdf"), flush=True)
        (pasta / "medidas.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
