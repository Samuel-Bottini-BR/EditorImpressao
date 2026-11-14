"""Medida 7 (estudo D-701): protótipo C, FORA do programa - "a mesma tinta" decidida pela cor do
MIOLO da tinta, não pela média da letra.

Por que: no m5 (opção 1, protótipo B) a Horas 13 ainda saiu com palavras azul-acinzentadas e
palavras bege no mesmo texto preto. A média de cada peça mistura a tinta com a beirada clara
(papel amarelado): letra grossa fica fria e escura, letra fina fica quente e clara. A cor do
miolo (a metade mais escura dos pontos da peça, na página antes do filtro) é a mesma nas duas.

Como:
  1) unidade = (palavra, peça da segmentação), como no m5 v2;
  2) cor de DECIDIR = a média da metade mais escura dos pontos da unidade na página Original;
  3) dentro da palavra e depois na página, junta as unidades com cor de decidir parecida;
  4) cor de PINTAR = a média (pela segmentação, como hoje) de todo o grupo.
Medidas: as mesmas do m5 (palavras em duas cores; tela x PDF). Grava _dados/m7/.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
os.environ.setdefault("M5_PESO_L", "0.3")
os.environ.setdefault("M5_LIMIAR", "8")
import m5_prototipo as m5  # noqa: E402
from m2_causa import chave  # noqa: E402
from m3_palavras import palavras_em_duas_cores  # noqa: E402

M4 = AQUI.parent / "_dados" / "m4"
SAI = AQUI.parent / "_dados" / "m7"
SAI.mkdir(parents=True, exist_ok=True)


def palavras(tinta):
    t8 = tinta.astype(np.uint8)
    n, rot, caixas, _ = cv2.connectedComponentsWithStats(t8, connectivity=8)
    alt = caixas[1:, 3][caixas[1:, 4] > 20]
    h = float(np.median(alt)) if alt.size else 10.0
    junto = cv2.morphologyEx(t8, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, int(0.35 * h)), 1)))
    return cv2.connectedComponents(junto, connectivity=8)[1]


def jeito_c(letras, original, tinta):
    rotp = palavras(tinta)
    k = chave(letras)[tinta].astype(np.int64)
    w = rotp[tinta].astype(np.int64)
    unidade, inv, cont = np.unique((w << 24) | k, return_inverse=True, return_counts=True)
    inv = inv.ravel()
    nu = unidade.size
    # cor de decidir: a metade mais escura de cada unidade, na página Original
    orig = original[tinta].astype(np.float32)
    luz = orig.mean(1)
    ordem = np.lexsort((luz, inv))                     # por unidade, do mais escuro ao mais claro
    inicio = np.searchsorted(inv[ordem], np.arange(nu))
    metade = np.maximum(1, cont // 2)
    soma = np.zeros((nu, 3), np.float64)
    pos = np.arange(ordem.size) - inicio[inv[ordem]]
    dentro = pos < metade[inv[ordem]]
    np.add.at(soma, inv[ordem][dentro], orig[ordem][dentro])
    miolo = (soma / metade[:, None]).round().astype(np.uint8)
    lab_dec = m5.lab_de(miolo)
    # cor de pintar: a da segmentação (como hoje), média pesada no grupo
    cor_u = unidade & 0xFFFFFF
    seg_u = np.stack([cor_u & 255, (cor_u >> 8) & 255, (cor_u >> 16) & 255], 1).astype(np.float64)
    palavra_u = unidade >> 24
    grupo_global = np.zeros(nu, int)
    # dentro da palavra
    rep_dec, rep_peso, rep_seg = [], [], []
    ordem_p = np.argsort(palavra_u, kind="stable")
    limites = np.flatnonzero(np.diff(palavra_u[ordem_p])) + 1
    for bloco in np.split(ordem_p, limites):
        g, centros = m5.agrupar(lab_dec[bloco], cont[bloco].astype(np.float64))
        for gi, c in enumerate(centros):
            membros = bloco[g == gi]
            peso = cont[membros].astype(np.float64)
            grupo_global[membros] = len(rep_dec)
            rep_dec.append(c)
            rep_peso.append(peso.sum())
            rep_seg.append((seg_u[membros] * peso[:, None]).sum(0) / peso.sum())
    rep_dec, rep_peso, rep_seg = np.asarray(rep_dec), np.asarray(rep_peso), np.asarray(rep_seg)
    # na página
    g2, _ = m5.agrupar(rep_dec, rep_peso)
    cor_final = np.zeros((g2.max() + 1, 3))
    massa = np.zeros(g2.max() + 1)
    np.add.at(cor_final, g2, rep_seg * rep_peso[:, None])
    np.add.at(massa, g2, rep_peso)
    cor_final = (cor_final / massa[:, None]).round().astype(np.uint8)
    saida = letras.copy()
    saida[tinta] = cor_final[g2[grupo_global[inv]]]
    return saida


def main():
    medidas = {}
    for nome in ("horas_p026", "horas_p013", "graduale_p223"):
        por = {}
        for dpi in (110, 300):
            pb = cv2.imread(str(M4 / f"{nome}_{dpi}_pb.png"))
            letras = cv2.imread(str(M4 / f"{nome}_{dpi}_letras.png"))
            original = cv2.imread(str(M4 / f"{nome}_{dpi}_original.png"))
            if original.shape != letras.shape:
                original = cv2.resize(original, letras.shape[1::-1], interpolation=cv2.INTER_AREA)
            tinta = cv2.cvtColor(pb, cv2.COLOR_BGR2GRAY) == 0
            c = jeito_c(letras, original, tinta)
            cv2.imwrite(str(SAI / f"{nome}_{dpi}_C.png"), c)
            m = palavras_em_duas_cores(c, tinta, regiao=m5.regiao(nome, tinta.shape))
            medidas[f"{nome}_{dpi}_C"] = {"fracao_em_duas_cores": m["fracao"], "palavras": m["palavras"]}
            print(nome, dpi, "C", m["fracao"], m["palavras"], flush=True)
            por[dpi] = (tinta, c)
        tg, cg = por[300]
        tp, cp = por[110]
        forma = tp.shape[::-1]
        ambos = (cv2.resize(tg.astype(np.uint8), forma, interpolation=cv2.INTER_NEAREST) > 0) & tp
        y0, y1, x0, x1 = m5.regiao(nome, tp.shape)
        caixa = np.zeros_like(ambos)
        caixa[y0:y1, x0:x1] = True
        ambos &= caixa
        de = np.linalg.norm(m5.lab_de(cv2.resize(cg, forma, interpolation=cv2.INTER_NEAREST)[ambos])
                            - m5.lab_de(cp[ambos]), axis=1)
        medidas[f"{nome}_previa110_x_pdf_C"] = {"diferenca_media": round(float(de.mean()), 2),
                                                "pontos_com_diferenca_visivel": round(float((de > 10).mean()), 3)}
        print(nome, "tela x PDF", medidas[f"{nome}_previa110_x_pdf_C"], flush=True)
    (SAI / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
