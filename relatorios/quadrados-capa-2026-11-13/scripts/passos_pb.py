"""Quadrados na capa (13/11/2026): o Preto e branco de fabrica ("auto") PASSO A PASSO na pagina
crua (so para achar a causa, CLAUDE.md §4.10: fora da conferencia). Grava cada passo de
core.filtros.filtro_preto_e_branco como PNG e diz quantos pontos mudaram de um passo para o
outro na caixa da capa (metade da direita).

    python passos_pb.py <raiz da versao> <livro.pdf> <pagina 1-based> <saida> [dpi]
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
SAIDA = Path(sys.argv[4]).resolve()
DADOS = Path(__file__).resolve().parents[1] / "_trabalho" / "dados" / "passos"
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import luz_scantailor  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402


def main() -> None:
    pdf, numero = sys.argv[2], int(sys.argv[3])
    dpi = int(sys.argv[5]) if len(sys.argv) > 5 else 300
    SAIDA.mkdir(parents=True, exist_ok=True)
    doc = abrir_pdf(pdf)
    try:
        img = pagina_para_array(doc, numero - 1, dpi=dpi)
    finally:
        doc.close()
    cv2.imwrite(str(SAIDA / "0-original.png"), img)
    cinza = F._cinza_para_binarizar(img)
    cinza = luz_scantailor.cinza_para_binarizar(cinza)
    cv2.imwrite(str(SAIDA / "1-cinza.png"), cinza)
    janela = F.janela_para_altura(cinza.shape[0])
    algoritmo = F.escolher_algoritmo_automatico(cinza)
    k_meio = F.k_para_a_letra(cinza)
    k = F.k_do_sauvola(F.AJUSTE_PADRAO, k_meio)
    passos = {}
    b = F.binarizar(cinza, janela=janela, k=k, algoritmo=algoritmo)
    passos["2-binarizar"] = b
    b = F._sem_a_sombra_da_lombada(cinza, b)
    passos["3-sem_sombra_lombada"] = b
    b = F._com_a_tinta_colorida(img, b)
    passos["4-com_tinta_colorida"] = b
    if algoritmo == F.ALGORITMO_OTSU:
        meio = F._otsu_com_a_borda_do_sauvola(cinza, b, janela, k_meio)
        passos["5a-otsu_com_borda_sauvola"] = meio
        b = F._a_borda_no_medidor(cinza, b, meio, janela, k_meio, F.AJUSTE_PADRAO)
        passos["5b-borda_no_medidor"] = b
    b = luz_scantailor.preto_e_branco_suavizado(b)
    passos["6-suavizado"] = b
    final = F.filtro_preto_e_branco(img)
    passos["7-filtro_inteiro"] = final
    h, w = cinza.shape
    capa = (slice(0, h), slice(w // 2 + w // 50, w - w // 30))
    info = {"algoritmo": algoritmo, "janela": janela, "k_meio": k_meio, "k": k, "dpi": dpi,
            "forma": [h, w]}
    anterior = None
    for nome, imagem in passos.items():
        cv2.imwrite(str(SAIDA / f"{nome}.png"), imagem)
        preto = float((imagem[capa] < 128).mean())
        mudou = None if anterior is None else float((imagem[capa] != anterior[capa]).mean())
        info[nome] = {"preto_na_capa": round(preto, 4), "mudou_na_capa": mudou}
        if not nome.startswith("5a"):
            anterior = imagem
    (SAIDA / "passos.json").write_text(json.dumps(info, indent=1), encoding="utf-8")
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
