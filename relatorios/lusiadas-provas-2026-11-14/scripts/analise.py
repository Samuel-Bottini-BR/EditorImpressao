"""Verificador, 14/11/2026: para as páginas de imagem (D-678 p.14, D-689 p.22, D-690 p.8) e a
folha 7 (D-682), lê o projeto que o programa gravou na fase a (_dados/projetos) e mostra:
  - a página preparada (dividida, endireitada; sem filtro) no tamanho do PDF;
  - o que o programa marcou nela (gravura em verde, letra em azul, papel em amarelo), por origem;
  - a página como sai (renderizar_pagina no DPI do PDF), e a do PDF que o programa gravou;
  - na p.22: o Preto e branco da página com cada um dos jeitos de preto (algoritmos), para saber
    se a sujeira é do jeito escolhido ou de todos.
Nada é gravado no projeto (é uma cópia lida do disco).

    .venv\\Scripts\\python.exe relatorios\\lusiadas-provas-2026-11-14\\scripts\\analise.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
TRAB = PASTA / "_dados"
os.environ["LOCALAPPDATA"] = str(TRAB / "dados-analise")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402

import projetos  # noqa: E402

projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from core.selecao import GRAVURA, LETRA, PAPEL  # noqa: E402

SAI = PASTA / "prints" / "analise"
SAI.mkdir(parents=True, exist_ok=True)
PDF_SAIDA = TRAB / "saida" / "lusiadas - preto e branco.pdf"
RES: dict = {}


def bgr(img):
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def sobreposto(img, selecao):
    h, w = img.shape[:2]
    base = bgr(img).astype(np.float32)
    cores = {GRAVURA: (60, 200, 60), LETRA: (230, 120, 30), PAPEL: (40, 220, 240)}
    for tipo, cor in cores.items():
        m = selecao.mascara(h, w, tipo)
        if m.any():
            base[m] = base[m] * 0.55 + np.array(cor, np.float32) * 0.45
            cont, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(base, cont, -1, cor, max(2, w // 400))
    return base.clip(0, 255).astype(np.uint8)


def main():
    pasta = next(p for p in (TRAB / "projetos").iterdir() if (p / "projeto.json").exists())
    resumo = projetos.ler_resumo(pasta)
    projeto = projetos.carregar_estado(resumo)
    dpi = int(getattr(projeto, "qualidade_dpi", 300) or 300)
    RES["dpi"] = dpi
    RES["paginas"] = len(projeto.paginas)
    doc = abrir_pdf(projeto.caminho_entrada)
    saida = fitz.open(str(PDF_SAIDA)) if PDF_SAIDA.exists() else None
    for n in (8, 14, 22):
        pg = projeto.paginas[n - 1]
        folha = projeto.folhas[pg.folha]
        img_folha = pagina_para_array(doc, folha.indice, dpi)
        prep = pipeline.preparar_metade(img_folha, folha, pg, projeto, dpi=dpi)
        sel = pg.obter_selecao()
        final, mono = pipeline.renderizar_pagina(doc, projeto, pg, dpi=dpi)
        sel2 = pg.obter_selecao()          # depois do desenho do tamanho do PDF (a definitiva)
        h, w = prep.shape[:2]
        regs = [{"tipo": r.tipo, "origem": r.origem, "operacao": r.operacao, "forma": r.forma}
                for r in sel2.regioes]
        RES[f"p{n}"] = {
            "folha": folha.indice + 1, "metade": pg.metade, "filtro": pg.filtro,
            "algoritmo_pb": pg.algoritmo_preto_branco, "forca": pg.forca_preto,
            "respeitar": getattr(pg, "respeitar_gravuras_achadas", True),
            "gravuras_cinza": getattr(pg, "gravuras_em_tons_de_cinza", False),
            "so_as_letras": getattr(pg, "misto_so_as_letras", None),
            "alertas": list(pg.alertas), "provisoria_antes": None,
            "regioes": regs,
            "fracao": {t: round(float(sel2.mascara(h, w, t).mean()), 4) for t in (GRAVURA, LETRA, PAPEL)},
            "tamanho": [w, h],
        }
        cv2.imwrite(str(SAI / f"p{n}-1-preparada.jpg"), prep, [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(str(SAI / f"p{n}-2-marcado.jpg"), sobreposto(prep, sel2), [cv2.IMWRITE_JPEG_QUALITY, 88])
        cv2.imwrite(str(SAI / f"p{n}-3-como-sai.png"), final)
        if saida is not None:
            # a página n do livro que sai (a 133 foi tirada só depois: aqui são 134)
            pix = saida[n - 1].get_pixmap(dpi=150)
            pix.save(str(SAI / f"p{n}-4-no-pdf.png"))
    # p.22: cada jeito de preto, na página preparada
    from core import filtros
    pg = projeto.paginas[21]
    folha = projeto.folhas[pg.folha]
    prep = pipeline.preparar_metade(pagina_para_array(doc, folha.indice, dpi), folha, pg, projeto, dpi=dpi)
    jeitos = {}
    for alg in ("auto",) + tuple(filtros.ALGORITMOS_PB):
        try:
            b = filtros.filtro_preto_e_branco(prep, forca=pg.forca_preto, algoritmo=alg)
            preto = float((b < 128).mean())
            jeitos[alg] = round(preto * 100, 2)
            cv2.imwrite(str(SAI / f"p22-pb-{alg}.png"), b)
        except Exception as e:  # noqa: BLE001
            jeitos[alg] = f"erro: {e}"
    RES["p22-jeitos-de-preto-pct-preto"] = jeitos
    cinza = cv2.cvtColor(prep, cv2.COLOR_BGR2GRAY)
    RES["p22-cinza"] = {"min": int(cinza.min()), "p1": float(np.percentile(cinza, 1)),
                        "p50": float(np.percentile(cinza, 50)), "max": int(cinza.max())}
    # folha 7 (páginas 12 e 13): onde o Dividir cortou e o tamanho das duas
    f7 = projeto.folhas[6]
    RES["folha7"] = {"dividir": f7.dividir, "posicao_corte": f7.posicao_corte,
                     "confianca": getattr(f7, "confianca_corte", None), "alertas": list(f7.alertas)}
    for n in (12, 13):
        pg = projeto.paginas[n - 1]
        img = pipeline.preparar_metade(pagina_para_array(doc, projeto.folhas[pg.folha].indice, dpi),
                                       projeto.folhas[pg.folha], pg, projeto, dpi=dpi)
        RES[f"p{n}-tamanho"] = list(img.shape[1::-1])
        cv2.imwrite(str(SAI / f"p{n}-preparada.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if saida is not None:
        RES["pdf"] = {"paginas": saida.page_count,
                      "p12_pt": [round(saida[11].rect.width), round(saida[11].rect.height)],
                      "p13_pt": [round(saida[12].rect.width), round(saida[12].rect.height)]}
    (AQUI / "analise.json").write_text(json.dumps(RES, ensure_ascii=False, indent=1, default=str),
                                       encoding="utf-8")
    print(json.dumps(RES, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
