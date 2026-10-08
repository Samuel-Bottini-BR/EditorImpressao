"""Rodada 4, pergunta da faixa do scanner: o programa ou o ScanTailor ja acham a
borda preta sozinhos?

Para cada pagina da lista (o PDF de uma pagina, folha CRUA, antes de qualquer corte):
  1. desenha a folha a 150 DPI;
  2. o corte do NOSSO programa, como ele roda hoje (core.recortar.detectar_bordas,
     o mesmo que core.pipeline chama com "Cortar bordas" ligado, que e o de fabrica);
  3. a "caixa da pagina" do ScanTailor (PageFinder::findPageBox, o item 2.13 do
     plano), pelo programa de teste que o pesquisador compilou em 01/10
     (D:\\programas\\EditorImpressao-arquivos\\ferramentas\\pesquisa-fase2-2026-10-01\\
     build\\Release\\prova.exe; nao faz parte do programa; nada foi recompilado).
Grava <TRABALHO>/faixa/<pid>.png, <pid>.json (as duas caixas em fracao da folha).

Nada aqui muda o programa. Uso: python faixa_testes.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import cv2
import numpy as np

import comum

PROVA = Path(r"D:\programas\EditorImpressao-arquivos\ferramentas\pesquisa-fase2-2026-10-01\build\Release\prova.exe")
QT = Path(r"D:\programas\EditorImpressao-arquivos\ferramentas\qt\6.11.1\msvc2022_64\bin")  # o Qt com que o teste foi compilado
DESTINO = comum.TRABALHO / "faixa"
DPI = 150

PAGINAS = ["egenloff_p003", "egenloff_p007", "egenloff_p012", "egenloff_p047", "matematica_p032",
           "camoes_p027", "camoes_p066", "camoes_p104", "cursus_p314", "antiphon_p088",
           "siebmacher_p007", "marial_p007"]


def folha_crua(pid: str) -> np.ndarray:
    import fitz

    with fitz.open(comum.caminho_pdf(pid)) as doc:
        pix = doc[0].get_pixmap(dpi=DPI)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
        img = cv2.cvtColor(img[:, :, :3], cv2.COLOR_RGB2BGR)
    return img


def caixa_scantailor(png: Path, alt: int, larg: int):
    env = dict(os.environ)
    env["PATH"] = str(QT) + os.pathsep + env.get("PATH", "")
    env["QT_PLUGIN_PATH"] = str(QT.parent / "plugins")
    r = subprocess.run([str(PROVA), str(png), str(DPI)], capture_output=True, text=True, env=env,
                       timeout=600)
    m = re.search(r"caixa da pagina: x (-?\d+)-(-?\d+), y (-?\d+)-(-?\d+) \((\d+) ms\)", r.stdout)
    if not m:
        print(r.stdout, r.stderr)
        return None, None
    x0, x1, y0, y1, ms = (int(v) for v in m.groups())
    return (x0 / larg, y0 / alt, x1 / larg, y1 / alt), ms


def main() -> None:
    from core.recortar import detectar_bordas

    DESTINO.mkdir(parents=True, exist_ok=True)
    for pid in PAGINAS:
        img = folha_crua(pid)
        alt, larg = img.shape[:2]
        png = DESTINO / f"{pid}.png"
        cv2.imwrite(str(png), img)
        r = detectar_bordas(img, dpi=DPI)
        nosso = (r.x, r.y, r.x + r.largura, r.y + r.altura)   # (x0, y0, x1, y1) em fracao
        st, ms = caixa_scantailor(png, alt, larg)
        dados = {"pid": pid, "tamanho": [larg, alt], "nosso": nosso, "scantailor": st, "ms": ms}
        (DESTINO / f"{pid}.json").write_text(json.dumps(dados), encoding="utf-8")
        print(pid, "nosso", [round(v, 3) for v in nosso], "scantailor",
              st and [round(v, 3) for v in st], ms, "ms", flush=True)


if __name__ == "__main__":
    main()
