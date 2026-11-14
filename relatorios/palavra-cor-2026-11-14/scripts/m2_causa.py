"""Medida 2 (estudo D-701): por que a mesma palavra sai em duas cores.

Usa as imagens do m1 (Livro de Horas 26, caminho inteiro, como sai no PDF):
  - pb.png: Preto e branco sem caixinha (quais pontos são letra: preto = 0);
  - letras.png: + "Letras com a cor delas" (cada peça com a cor média dela: a segmentação do
    ScanTailor);
  - letras_reduzir.png: + "Reduzir cores" (a posterização do ScanTailor por cima).

1) Refaz em numpy a conta do Posterizer.cpp do ScanTailor (normalizePalette + cubos de
   255/nível por canal + "a cor mais frequente do cubo"), sem o "forçar preto e branco"
   (como o programa chama no Preto e branco desde a etapa 10b), e confere que dá o mesmo que a
   DLL nos pontos de letra.
2) Para cada letra de "S. Leonard" e "S. Theodore": a cor média dela (segmentação), o cubo em
   que cai e a cor que sai.
3) De onde vem a cor de cada cubo: a peça maior que tem exatamente aquela cor.
Grava _dados/m2/medidas.json e imprime o resumo.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
M1 = AQUI.parent / "_dados" / "m1"
SAI = AQUI.parent / "_dados" / "m2"
SAI.mkdir(parents=True, exist_ok=True)

NIVEL = 4
# trechos das duas linhas (pontos da página a 300 DPI, achados na imagem do m1)
LINHAS = {"S. Leonard": (1540, 1660, 560, 1450), "S. Theodore": (1890, 2010, 560, 1500)}


def chave(bgr: np.ndarray) -> np.ndarray:
    b, g, r = (bgr[..., i].astype(np.uint32) for i in range(3))
    return (r << 16) | (g << 8) | b


def rgb_de(k: int) -> tuple[int, int, int]:
    return (k >> 16) & 255, (k >> 8) & 255, k & 255


def posterizar(img_segmentada: np.ndarray, nivel=NIVEL):
    """O Posterizer.cpp sem normalizar a saída e sem forçar preto e branco. Devolve
    (mapa cor->cor, cubo de cada cor, min, max)."""
    k = chave(img_segmentada).ravel()
    cores, contagem = np.unique(k, return_counts=True)
    total = k.size
    branco, preto = 0xFFFFFF, 0x000000
    hist = np.zeros((3, 256), np.int64)
    for c, n in zip(cores.tolist(), contagem.tolist()):
        if c == preto:
            hist[:, 0] += n
            continue
        if c == branco:
            hist[:, 255] += n
            continue
        r, g, b = rgb_de(c)
        hist[0, r] += n
        hist[1, g] += n
        hist[2, b] += n
    vale = (hist / total >= 0.0005).any(axis=0)
    niveis = np.nonzero(vale)[0]
    mn, mx = int(niveis.min()), int(niveis.max())
    passo = 255.0 / nivel
    cubo_de = {}
    grupos: dict[tuple, list] = {}
    stat = dict(zip(cores.tolist(), contagem.tolist()))
    for c in cores.tolist():
        if c in (branco, preto):
            norm = rgb_de(c)
        else:
            norm = tuple(min(255, max(0, round((v - mn) / (mx - mn) * 255))) for v in rgb_de(c))
        # o ScanTailor chama de "blue" o índice do verde e vice-versa; para o cubo, tanto faz
        cubo = tuple(int(v / passo) for v in norm)
        cubo_de[c] = cubo
        grupos.setdefault(cubo, []).append(c)
    mapa = {}
    for cubo, lista in grupos.items():
        mais = max(lista, key=lambda c: stat[c])   # a cor mais frequente do cubo
        for c in lista:
            mapa[c] = mais
    return mapa, cubo_de, mn, mx, stat


def main():
    pb = cv2.imread(str(M1 / "pb.png"))
    letras = cv2.imread(str(M1 / "letras.png"))
    reduz = cv2.imread(str(M1 / "letras_reduzir.png"))
    tinta = cv2.cvtColor(pb, cv2.COLOR_BGR2GRAY) == 0
    # a imagem que a DLL posteriza: a segmentação (cor de cada peça) com o resto branco
    seg = np.full_like(letras, 255)
    seg[tinta] = letras[tinta]
    mapa, cubo_de, mn, mx, stat = posterizar(seg)
    k_seg = chave(seg)
    k_red = chave(reduz)
    previsto = np.vectorize(lambda c: mapa.get(int(c), int(c)), otypes=[np.uint32])(k_seg[tinta])
    acerto = float((previsto == k_red[tinta]).mean())
    print(f"conta refeita = DLL em {acerto:.4%} dos pontos de letra; min={mn} max={mx}")

    # peças da segmentação: componentes ligados da tinta
    n, rotulos, caixas, _ = cv2.connectedComponentsWithStats(tinta.astype(np.uint8), connectivity=8)
    # de onde vem cada cor final: a maior peça com aquela cor exata
    cor_final = sorted(set(mapa.values()), key=lambda c: -stat[c])
    origem = {}
    for c in cor_final[:12]:
        onde = (k_seg == c) & tinta
        rot = Counter(rotulos[onde].tolist()).most_common(1)
        if rot:
            r = rot[0][0]
            x, y, w, h, area = caixas[r]
            origem[hex(c)] = {"rgb": rgb_de(c), "pontos_com_esta_cor": int(stat[c]),
                              "cubo": cubo_de[c],
                              "peca_maior": {"x": int(x), "y": int(y), "larg": int(w), "alt": int(h),
                                             "area": int(area)}}
    medidas = {"acerto_da_conta_refeita": acerto, "min": mn, "max": mx, "origem_das_cores": origem,
               "linhas": {}}
    for nome, (y0, y1, x0, x1) in LINHAS.items():
        sub = rotulos[y0:y1, x0:x1]
        pecas = [r for r in np.unique(sub) if r != 0 and caixas[r][4] > 150]
        pecas.sort(key=lambda r: caixas[r][0])
        lista = []
        for r in pecas:
            pontos = rotulos == r
            cores_seg = Counter(k_seg[pontos].tolist()).most_common(2)
            cores_red = Counter(k_red[pontos].tolist()).most_common(2)
            c = cores_seg[0][0]
            lista.append({"x": int(caixas[r][0]), "area": int(caixas[r][4]),
                          "cor_media_rgb": rgb_de(c), "cubo": cubo_de.get(c),
                          "sai_rgb": rgb_de(cores_red[0][0]),
                          "cores_na_peca": len(cores_red)})
        medidas["linhas"][nome] = lista
        print(nome)
        for item in lista:
            print("  ", item)
    print("cores finais mais usadas e de onde vêm:")
    for k, v in origem.items():
        print("  ", k, v)
    (SAI / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
