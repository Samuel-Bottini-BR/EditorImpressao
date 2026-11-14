"""Medida 3 (estudo D-701): a medida "duas cores na mesma palavra" e a mesma página em cada
caminho (resolução da prévia, tela cheia, Automático, comparar e PDF).

1) A medida (proposta para a prova do conserto):
   - palavras = peças de tinta juntadas na horizontal (fechamento com uma barra de
     largura = 0,35 x a altura mediana das letras; o espaço entre letras some, o entre
     palavras fica);
   - cor de cada ponto = a cor que sai; duas cores são "a mesma" se a distância no LAB for
     menor que 6 (diferença que não se vê);
   - palavra "em duas cores" = a segunda cor ocupa mais de 10% da tinta da palavra.
   Resultado: a fração das palavras em duas cores.
2) A mesma página pelo renderizar_pagina (o corpo da prévia, das miniaturas, da tela cheia e
   do Automático) em 110, 150, 180, 220 e 300 pontos por polegada, e o PDF (_pagina_pronta).
   Para cada resolução: a fração de palavras em duas cores, e quanto da tinta sai "azul"
   (B > R + 8) - para ver se a prévia mostra as mesmas cores que o PDF (D-649).
Grava _dados/m3/*.png e medidas.json.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
DADOS = AQUI.parent / "_dados"
os.environ["LOCALAPPDATA"] = str(DADOS / "local")
os.environ["APPDATA"] = str(DADOS / "local")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

SAI = DADOS / "m3"
SAI.mkdir(parents=True, exist_ok=True)


def palavras_em_duas_cores(img: np.ndarray, tinta: np.ndarray, *, limiar_lab=6.0, segunda=0.10,
                           regiao=None) -> dict:
    """A medida (ver o topo). img: a página que sai (BGR); tinta: bool, os pontos de letra."""
    if regiao is not None:
        y0, y1, x0, x1 = regiao
        img, tinta = img[y0:y1, x0:x1], tinta[y0:y1, x0:x1]
    t8 = tinta.astype(np.uint8)
    n, rot, caixas, _ = cv2.connectedComponentsWithStats(t8, connectivity=8)
    alturas = caixas[1:, 3][caixas[1:, 4] > 20]
    h = float(np.median(alturas)) if alturas.size else 10.0
    barra = cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, int(0.35 * h)), 1))
    junto = cv2.morphologyEx(t8, cv2.MORPH_CLOSE, barra)
    npal, rotp, cxp, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 0] *= 100 / 255
    lab[..., 1:] -= 128
    total = duas = 0
    exemplos = []
    for r in range(1, npal):
        pts = (rotp == r) & tinta
        q = int(pts.sum())
        if q < 4 * h:         # pontinho, acento solto
            continue
        cores = lab[pts]
        # agrupa as cores da palavra: cada ponto vai para a cor mais frequente a menos de limiar
        unicas, cont = np.unique(np.round(cores).astype(np.int16), axis=0, return_counts=True)
        ordem = np.argsort(-cont)
        grupos = []
        for i in ordem:
            c = unicas[i].astype(np.float32)
            for g in grupos:
                if np.linalg.norm(g[0] - c) < limiar_lab:
                    g[1] += int(cont[i])
                    break
            else:
                grupos.append([c, int(cont[i])])
        grupos.sort(key=lambda g: -g[1])
        total += 1
        if len(grupos) > 1 and grupos[1][1] / q > segunda:
            duas += 1
            if len(exemplos) < 5:
                x, y, w, hh, _ = cxp[r]
                exemplos.append({"x": int(x), "y": int(y), "larg": int(w), "alt": int(hh),
                                 "parte_da_2a_cor": round(grupos[1][1] / q, 2)})
    return {"palavras": total, "em_duas_cores": duas,
            "fracao": round(duas / total, 3) if total else None, "exemplos": exemplos,
            "altura_mediana_das_letras": h}


def main():
    from core import filtros as F
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    copia = DADOS / "horas_p026.pdf"
    if not copia.exists():
        shutil.copyfile(RAIZ / "gabarito" / "paginas" / "horas_p026.pdf", copia)
    medidas = {}
    for caixas in ({"letras_com_a_cor": True}, {"letras_com_a_cor": True, "reduzir_cores": True}):
        nome = "letras_reduzir" if "reduzir_cores" in caixas else "letras"
        for dpi in (110, 150, 180, 220, 300, "pdf"):
            for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
                g.clear()
            projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(copia),
                                                        caminho_saida=str(SAI / "s.pdf"), nome="h26"))
            pagina = projeto.paginas_ativas[0]
            pagina.filtro = F.PRETO_E_BRANCO
            doc = abrir_pdf(str(copia))
            try:
                base = {}
                for chave in ("letras_com_a_cor", "reduzir_cores"):
                    setattr(pagina, chave, False)
                if dpi == "pdf":
                    pb, _ = pipeline._pagina_pronta(projeto, doc, projeto.folhas[0], pagina,
                                                    pipeline._FolhaDaVez(), 0)
                    for k, v in caixas.items():
                        setattr(pagina, k, v)
                    t = time.perf_counter()
                    img, _ = pipeline._pagina_pronta(projeto, doc, projeto.folhas[0], pagina,
                                                     pipeline._FolhaDaVez(), 0)
                else:
                    pb, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                    for k, v in caixas.items():
                        setattr(pagina, k, v)
                    t = time.perf_counter()
                    img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                segundos = time.perf_counter() - t
            finally:
                doc.close()
            if pb.ndim == 2:
                pb = cv2.cvtColor(pb, cv2.COLOR_GRAY2BGR)
            if img.ndim == 2:
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            tinta = cv2.cvtColor(pb, cv2.COLOR_BGR2GRAY) < 128
            cv2.imwrite(str(SAI / f"{nome}_{dpi}.png"), img)
            fator = img.shape[0] / 5709.0
            # o calendário (sem o título, a moldura e a faixa da direita), na escala desta imagem
            reg = tuple(int(v * fator) for v in (850, 4500, 120, 3000))
            m = palavras_em_duas_cores(img, tinta, regiao=reg)
            b, g, r = (img[..., i].astype(int) for i in range(3))
            azul = (b > r + 8) & tinta
            m["tinta_azul_no_calendario"] = round(float(azul[reg[0]:reg[1], reg[2]:reg[3]].sum()
                                                        / max(1, tinta[reg[0]:reg[1], reg[2]:reg[3]].sum())), 3)
            m["segundos"] = round(segundos, 2)
            m["tamanho"] = list(img.shape[:2])
            medidas[f"{nome}_{dpi}"] = m
            print(nome, dpi, {k: v for k, v in m.items() if k != "exemplos"}, flush=True)
    (SAI / "medidas.json").write_text(json.dumps(medidas, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
