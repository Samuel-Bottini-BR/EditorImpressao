"""Junta numa pasta 'cru' o que o montar.py precisa (copias e o original a 75 DPI)."""
import json
import shutil
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

AQUI = Path(__file__).resolve().parent
CRU = AQUI / "cru"
CRU.mkdir(exist_ok=True)
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
ESCOLA = ACERVO / "Na escola de Jesus - Catecismo explicado com imagens..pdf"
HORAS = ACERVO / "Livro de Horas - Luís XIV.pdf"

for n in ("original", "melhorar_forte_respeitar", "magico_fraco_sem_respeitar"):
    shutil.copy(AQUI / "saida" / f"{n}_pdf.png", CRU / f"{n}_pdf.png")
shutil.copy(AQUI / "saida" / "melhorar_forte_respeitar_previa.png", CRU)
for n in ("melhorar_forte_respeitar", "magico_fraco_sem_respeitar"):
    shutil.copy(AQUI / "saida_candidato" / f"{n}_pdf.png", CRU / f"cand_{n}_pdf.png")


def originais(pdf, paginas, prefixo, molde_saida):
    doc = fitz.open(str(pdf))
    for p in paginas:
        ref = cv2.imread(str(molde_saida.format(p=p)))
        pix = doc[p - 1].get_pixmap(dpi=75)
        o = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3][:, :, ::-1]
        o = cv2.resize(np.ascontiguousarray(o), (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(CRU / f"{prefixo}_orig_p{p:03d}.jpg"), o, [cv2.IMWRITE_JPEG_QUALITY, 90])


def copiar(pasta, variante, paginas, prefixo):
    for p in paginas:
        shutil.copy(AQUI / pasta / f"{variante}_p{p:03d}.jpg", CRU / f"{prefixo}_p{p:03d}.jpg")


ESC = [int(v) for v in sys.argv[1].split(",")]
HOR = [int(v) for v in sys.argv[2].split(",")]
originais(ESCOLA, ESC, "escola", str(AQUI / "livro" / "melhorar_forte_respeitar_p{p:03d}.jpg"))
originais(HORAS, HOR, "horas", str(AQUI / "horas" / "melhorar_forte_respeitar_p{p:03d}.jpg"))
for v in ("melhorar_forte_respeitar", "magico_fraco_sem_respeitar"):
    copiar("livro", v, ESC, f"escola_{v}")
    copiar("livro_cand", v, ESC, f"escola_cand_{v}")
    copiar("horas", v, HOR, f"horas_{v}")
    copiar("horas_cand", v, HOR, f"horas_cand_{v}")

AZUL, LARANJA, VERDE = [60, 90, 150], [190, 90, 10], [25, 130, 60]
extra = []
for v, nome, ajuste in (("melhorar_forte_respeitar", "Melhorar", "Clareza \"bem forte\""),
                        ("magico_fraco_sem_respeitar", "Mágico pro", "Intensidade \"bem fraco\"")):
    n = 3 if v.startswith("melhorar") else 4
    extra.append({
        "arquivo": f"{n}-livro-escola-{'melhorar' if n == 3 else 'magico-pro'}.png",
        "titulo": f"Na escola de Jesus — {nome}",
        "linha": f"Livro novo, {nome} escolhido à mão, {ajuste}. Oito das páginas com mais quadrados "
                 "(só a gravura de cada página, o mesmo recorte nas três faixas; como sai no PDF).",
        "paginas": ESC,
        "faixas": [
            ["ORIGINAL", AZUL, "Como veio no PDF.", "escola_orig_p{p:03d}.jpg"],
            [f"HOJE — {nome}", LARANJA, "Buracos brancos nas partes claras e cinzentas das pinturas "
             "(céu, água, nuvens, roupas claras).", f"escola_{v}_p{{p:03d}}.jpg"],
            [f"CONSERTADO (simulação) — {nome}", VERDE, "SIMULAÇÃO, não está no programa: a pintura "
             "fica inteira; o papel e o vão entre as letras continuam indo a branco.", f"escola_cand_{v}_p{{p:03d}}.jpg"],
        ]})
extra.append({
    "arquivo": "5-outro-livro-horas.png",
    "titulo": "Livro de Horas — Melhorar",
    "linha": "Outro livro do acervo, livro novo, Melhorar \"bem forte\" escolhido à mão. A página 47 "
             "tem pintura clara (colunas, céu): o mesmo defeito, mais fraco.",
    "paginas": HOR,
    "circular": [47],
    "faixas": [
        ["ORIGINAL", AZUL, "Como veio no PDF.", "horas_orig_p{p:03d}.jpg"],
        ["HOJE — Melhorar", LARANJA, "Manchas brancas nas colunas e no céu da pintura de cima e na "
         "paisagem de baixo.", "horas_melhorar_forte_respeitar_p{p:03d}.jpg"],
        ["CONSERTADO (simulação) — Melhorar", VERDE, "SIMULAÇÃO, não está no programa.",
         "horas_cand_melhorar_forte_respeitar_p{p:03d}.jpg"],
    ]})
(CRU / "extra.json").write_text(json.dumps(extra, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")
