"""Conferencia de MAQUINA (sem janela): desenha uma pagina como o programa do
ramo desenha num LIVRO NOVO (endireitar antes de cortar, Preto e branco, "So
as letras") em duas resolucoes - a da previa da tela (110 DPI) e a do PDF
(300 DPI) - e guarda as imagens, os avisos e os sinais da regra.

Serve para comparar o que a pessoa VE na tela com o que SAI no PDF.
Nao muda o programa. Pasta de dados isolada (nada na pasta do Samuel).

Uso: python desenhar.py <pid ou caminho.pdf[:pagina]> [fora=rede|tudo|so_texto] [reforco=0|1] [dpis=110,300]
     pid = nome de uma das paginas do estudo (ex.: antiphonal1547_p046)
"""
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
RAIZ = BASE.parents[2]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "relatorios" / "para-revisar-impl"))

from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

isolar_pasta_de_dados("verif-para-revisar-desenhar")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import conferir_89  # noqa: E402
from core import misto  # noqa: E402
from core import pipeline as P  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

SAIDA = BASE / "trabalho" / "desenhos"
SAIDA.mkdir(parents=True, exist_ok=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    alvo = sys.argv[1]
    opcoes = dict(a.split("=", 1) for a in sys.argv[2:])
    fora = {"rede": misto.FORA_REDE, "tudo": misto.FORA_TUDO,
            "so_texto": getattr(misto, "FORA_SO_TEXTO", "so_texto")}[opcoes.get("fora", "rede")]
    reforco = opcoes.get("reforco", "1") == "1"
    dpis = [int(d) for d in opcoes.get("dpis", "110,300").split(",")]
    pagina_n = 0
    if alvo.lower().endswith(".pdf") or ".pdf:" in alvo.lower():
        if ".pdf:" in alvo.lower():
            alvo, n = alvo.rsplit(":", 1)
            pagina_n = int(n) - 1
        caminho, nome = alvo, Path(alvo).stem[:24]
    else:
        caminho, nome = str(conferir_89._pdf_da_pagina(alvo)), alvo
    vistos = []
    original = P.medir_para_revisar

    def espiao(*a, **k):
        s = original(*a, **k)
        vistos.append(s)
        return s

    P.medir_para_revisar = espiao
    resumo = {}
    for dpi in dpis:
        projeto = Projeto(caminho_entrada=caminho, nome=nome)
        projeto.filtro_padrao = PRETO_E_BRANCO
        projeto = P.analisar_projeto(projeto)
        projeto.misto_so_as_letras = True
        projeto.misto_fora_do_texto = fora
        projeto.reforcar_texto_falhado = reforco
        doc = abrir_pdf(caminho)
        pagina = projeto.paginas[pagina_n]
        pagina.filtro = PRETO_E_BRANCO
        vistos.clear()
        t0 = time.perf_counter()
        img = P.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
        seg = time.perf_counter() - t0
        doc.close()
        if isinstance(img, tuple):      # (imagem, e_colorida)
            img = img[0]
        img = np.asarray(img)
        sufixo = f"{nome}-p{pagina_n + 1}-{opcoes.get('fora', 'rede')}-{'r1' if reforco else 'r0'}-{dpi}dpi"
        if img.ndim == 3:
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = img
        cv2.imencode(".png", img_bgr)[1].tofile(str(SAIDA / f"{sufixo}.png"))
        s = vistos[-1] if vistos else None
        resumo[dpi] = {"alertas": list(pagina.alertas), "forca": pagina.forca_preto,
                       "ordem": projeto.ordem_do_preparo, "segundos": round(seg, 1),
                       "tamanho": list(img.shape[:2]),
                       "marcas": [[round(v, 3) for v in m] for m in P.marcas_do_aviso(pagina)],
                       "sinais": conferir_89._resumo(s) if s is not None else None,
                       "medido": P._da_para_medir(dpi) if hasattr(P, "_da_para_medir") and False else None}
        print(dpi, json.dumps(resumo[dpi], ensure_ascii=False), flush=True)
    (SAIDA / f"{nome}-p{pagina_n + 1}-{opcoes.get('fora', 'rede')}-{'r1' if reforco else 'r0'}.json").write_text(
        json.dumps(resumo, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
