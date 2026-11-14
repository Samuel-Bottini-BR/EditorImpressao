"""Medida 5 (estudo D-701): protótipo do conserto, FORA do programa (nada em core/ muda).

Lê as páginas do m4 (pb, letras, reduzir em cada resolução) e monta dois jeitos:

  A "cada palavra numa cor": as peças de letra de uma palavra que têm a mesma tinta (cor
    parecida, a claridade pesa menos) ganham a cor média da palavra; DEPOIS vai a
    redução de cores do ScanTailor como hoje (a conta dele, refeita em numpy = DLL).
  B "a mesma tinta, a mesma cor": como A, e as palavras da página com a mesma tinta são
    juntadas numa cor só (sem a conta de cubos do ScanTailor).

Uma palavra com uma letra de outra tinta (capitular vermelha encostada) não se mistura: dentro
da palavra, as peças da segmentação só se juntam se a cor for parecida (distância < LIMIAR).
(1ª versão juntava pela tinta encostada e misturava a pauta vermelha com as notas do Graduale.)

Medidas por página e resolução (região do texto):
  - fração das palavras em duas cores (a medida do m3);
  - prévia x PDF: diferença de cor média (LAB) entre 110/150 e 300 nos pontos de letra.
Grava _dados/m5/<pagina>_<dpi>_<jeito>.png e medidas.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from m2_causa import chave, posterizar  # noqa: E402
from m3_palavras import palavras_em_duas_cores  # noqa: E402

M4 = AQUI.parent / "_dados" / "m4"
SAI = AQUI.parent / "_dados" / __import__("os").environ.get("M5_SAIDA", "m5")
SAI.mkdir(parents=True, exist_ok=True)
LIMIAR = float(__import__("os").environ.get("M5_LIMIAR", "12"))   # distância de "mesma tinta" (LAB)
PESO_L = float(__import__("os").environ.get("M5_PESO_L", "0.5"))   # quanto a claridade pesa
# a região do texto, em fração da página (sem moldura, título e faixa da beirada)
REGIOES = {"horas_p026": (0.149, 0.788, 0.037, 0.915), "horas_p013": (0.05, 0.95, 0.05, 0.95),
           "graduale_p223": (0.05, 0.95, 0.05, 0.95)}


def lab_de(bgr):
    lab = cv2.cvtColor(np.asarray(bgr, np.uint8).reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
    lab = lab.astype(np.float32)
    lab[:, 0] *= 100 / 255
    lab[:, 1:] -= 128
    return lab


def bgr_de(lab):
    lab = np.asarray(lab, np.float32).reshape(-1, 3).copy()
    lab[:, 0] *= 255 / 100
    lab[:, 1:] += 128
    return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8).reshape(-1, 1, 3),
                        cv2.COLOR_LAB2BGR).reshape(-1, 3)


def distancia(a, b):
    d = np.asarray(a, np.float32) - np.asarray(b, np.float32)
    return float(np.sqrt((PESO_L * d[0]) ** 2 + d[1] ** 2 + d[2] ** 2))


def agrupar(cores_lab, pesos):
    """Agrupamento guloso: do maior para o menor, cada item entra no primeiro grupo a menos
    de LIMIAR; a cor do grupo é a média pesada. Devolve (grupo de cada item, cores dos grupos)."""
    ordem = np.argsort(-np.asarray(pesos))
    centros, somas, massa = [], [], []
    grupo = np.zeros(len(pesos), int)
    for i in ordem:
        for g, c in enumerate(centros):
            if distancia(cores_lab[i], c) < LIMIAR:
                grupo[i] = g
                somas[g] += cores_lab[i] * pesos[i]
                massa[g] += pesos[i]
                centros[g] = somas[g] / massa[g]
                break
        else:
            grupo[i] = len(centros)
            centros.append(cores_lab[i].copy())
            somas.append(cores_lab[i] * pesos[i])
            massa.append(float(pesos[i]))
    return grupo, centros


def cor_por_palavra(letras, tinta):
    """Jeito A, parte 1: dentro de cada palavra, as peças da MESMA tinta com a cor média delas.

    Peça = a peça da segmentação do ScanTailor (cada uma já sai com uma cor exata só); assim
    uma pauta vermelha encostada nas notas pretas continua separada delas (são peças de cor
    diferente), mesmo que a tinta se toque. Palavra = a tinta juntada na horizontal."""
    t8 = tinta.astype(np.uint8)
    n, rot, caixas, _ = cv2.connectedComponentsWithStats(t8, connectivity=8)
    alt = caixas[1:, 3][caixas[1:, 4] > 20]
    h = float(np.median(alt)) if alt.size else 10.0
    junto = cv2.morphologyEx(t8, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, int(0.35 * h)), 1)))
    _, rotp = cv2.connectedComponents(junto, connectivity=8)
    k = chave(letras)[tinta].astype(np.int64)
    w = rotp[tinta].astype(np.int64)
    unidade, inv, cont = np.unique((w << 24) | k, return_inverse=True, return_counts=True)
    palavra_u = unidade >> 24
    cor_u = unidade & 0xFFFFFF
    bgr_u = np.stack([cor_u & 255, (cor_u >> 8) & 255, (cor_u >> 16) & 255], 1).astype(np.uint8)
    lab_u = lab_de(bgr_u)
    nova_u = np.zeros_like(lab_u)
    ordem = np.argsort(palavra_u, kind="stable")
    limites = np.flatnonzero(np.diff(palavra_u[ordem])) + 1
    for bloco in np.split(ordem, limites):
        g, centros = agrupar(lab_u[bloco], cont[bloco].astype(np.float64))
        nova_u[bloco] = np.asarray(centros)[g]
    saida = letras.copy()
    saida[tinta] = bgr_de(nova_u)[inv.ravel()]
    return saida, rot, rotp


def mesma_tinta_na_pagina(img_palavras, tinta, rot):
    """Jeito B, parte 2: as cores das palavras (já uniformes) juntadas por tinta na página."""
    k = chave(img_palavras)[tinta]
    unicas, inv, cont = np.unique(k, return_inverse=True, return_counts=True)
    bgr = np.stack([unicas & 255, (unicas >> 8) & 255, (unicas >> 16) & 255], 1).astype(np.uint8)
    lab = lab_de(bgr)
    g, centros = agrupar(lab, cont.astype(np.float64))
    cores = bgr_de(np.asarray(centros))
    saida = img_palavras.copy()
    saida[tinta] = cores[g[inv]]
    return saida


def posterizar_imagem(img, tinta):
    seg = np.full_like(img, 255)
    seg[tinta] = img[tinta]
    mapa, *_ = posterizar(seg)
    k = chave(seg)[tinta]
    unicas, inv = np.unique(k, return_inverse=True)
    novo = np.array([mapa.get(int(c), int(c)) for c in unicas], np.uint32)[inv.ravel()]
    saida = img.copy()
    saida[tinta] = np.stack([novo & 255, (novo >> 8) & 255, (novo >> 16) & 255], 1).astype(np.uint8)
    return saida


def regiao(nome, forma):
    y0, y1, x0, x1 = REGIOES[nome]
    return int(y0 * forma[0]), int(y1 * forma[0]), int(x0 * forma[1]), int(x1 * forma[1])


def main():
    medidas = {}
    for nome in REGIOES:
        por_dpi = {}
        for dpi in (110, 150, 300):
            pb = M4 / f"{nome}_{dpi}_pb.png"
            if not pb.exists():
                continue
            pb = cv2.imread(str(pb))
            letras = cv2.imread(str(M4 / f"{nome}_{dpi}_letras.png"))
            hoje = cv2.imread(str(M4 / f"{nome}_{dpi}_reduzir.png"))
            tinta = cv2.cvtColor(pb, cv2.COLOR_BGR2GRAY) == 0
            a1, rot, _ = cor_por_palavra(letras, tinta)
            a = posterizar_imagem(a1, tinta)
            b = mesma_tinta_na_pagina(a1, tinta, rot)
            reg = regiao(nome, tinta.shape)
            for jeito, img in (("letras", letras), ("hoje", hoje), ("A", a), ("B", b)):
                cv2.imwrite(str(SAI / f"{nome}_{dpi}_{jeito}.png"), img)
                m = palavras_em_duas_cores(img, tinta, regiao=reg)
                medidas[f"{nome}_{dpi}_{jeito}"] = {"fracao_em_duas_cores": m["fracao"],
                                                    "palavras": m["palavras"]}
                print(nome, dpi, jeito, m["fracao"], m["palavras"], flush=True)
            por_dpi[dpi] = {"tinta": tinta, "letras": letras, "hoje": hoje, "A": a, "B": b}
        # prévia x PDF: a imagem de 300 reduzida ao tamanho da prévia, comparada ponto a ponto
        if 300 in por_dpi:
            grande = por_dpi[300]
            for dpi in (110, 150):
                if dpi not in por_dpi:
                    continue
                pequena = por_dpi[dpi]
                forma = pequena["tinta"].shape[::-1]
                t_g = cv2.resize(grande["tinta"].astype(np.uint8), forma, interpolation=cv2.INTER_NEAREST) > 0
                ambos = t_g & pequena["tinta"]
                y0, y1, x0, x1 = regiao(nome, pequena["tinta"].shape)
                caixa = np.zeros_like(ambos)
                caixa[y0:y1, x0:x1] = True
                ambos &= caixa
                for jeito in ("letras", "hoje", "A", "B"):
                    g_img = cv2.resize(grande[jeito], forma, interpolation=cv2.INTER_NEAREST)
                    la = lab_de(g_img[ambos])
                    lb = lab_de(pequena[jeito][ambos])
                    de = np.linalg.norm(la - lb, axis=1)
                    chave_m = f"{nome}_previa{dpi}_x_pdf_{jeito}"
                    medidas[chave_m] = {"diferenca_media": round(float(de.mean()), 2),
                                        "pontos_com_diferenca_visivel": round(float((de > 10).mean()), 3)}
                    print(chave_m, medidas[chave_m], flush=True)
    (SAI / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
