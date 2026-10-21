"""Procura no acervo páginas com as linhas curvas perto da lombada (item 2.12, 21/10/2026).

Lê uma página a cada PASSO de cada livro a 100 DPI, em cinza (somente leitura);
folha deitada (mais larga que alta) é cortada ao meio, como o dividir faz. Em
cada página passa o desentortar "automático" do ScanTailor (core.desentortar_scantailor)
e mede quanto ele mexeu: a média da diferença, ponto a ponto, no miolo da
página (sem 8% de cada beirada). Página reta: o ScanTailor acha linhas retas e
quase não mexe; página curva: mexe muito perto da lombada. A lista sai em JSON
ordenada, e as miniaturas (antes | depois) das 40 que mais mexeram numa pasta,
para abrir e conferir a olho.

Uso (da pasta da worktree):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\fase2-itens\\scripts\\procurar_paginas_curvas.py <pasta do acervo> <pasta de saída> [PASSO]
"""
import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
from core import desentortar_scantailor as ds  # noqa: E402

DPI = 100
acervo, saida = Path(sys.argv[1]), Path(sys.argv[2])
passo = int(sys.argv[3]) if len(sys.argv) > 3 else 5
saida.mkdir(parents=True, exist_ok=True)
achados = []
for pdf in sorted(acervo.glob("*.pdf")):
    doc = fitz.open(pdf)
    for i in range(0, len(doc), passo):
        pix = doc[i].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].copy()
        h, w = img.shape
        metades = [("inteira", 0, img)]
        if w > h * 1.15:
            metades = [("esquerda", 1, img[:, :w // 2].copy()), ("direita", 2, img[:, w // 2:].copy())]
        for nome, lado, pagina in metades:
            r = ds.desentortar(pagina, DPI, ds.AUTOMATICO, lado=lado)
            if not r.disponivel:
                continue
            ph, pw = pagina.shape
            my, mx = ph * 8 // 100, pw * 8 // 100
            dif = float(np.abs(r.imagem[my:ph - my, mx:pw - mx].astype(np.int16)
                               - pagina[my:ph - my, mx:pw - mx]).mean())
            achados.append({"livro": pdf.name, "pagina": i + 1, "metade": nome, "lado": lado,
                            "achou_curvas": r.achou_curvas, "diferenca": round(dif, 2)})
    doc.close()
    print(pdf.name, flush=True)
achados.sort(key=lambda a: -a["diferenca"])
(saida / "achados.json").write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
for k, a in enumerate(achados[:40]):
    doc = fitz.open(acervo / a["livro"])
    pix = doc[a["pagina"] - 1].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    doc.close()
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width].copy()
    h, w = img.shape
    if a["metade"] == "esquerda":
        img = img[:, :w // 2].copy()
    elif a["metade"] == "direita":
        img = img[:, w // 2:].copy()
    r = ds.desentortar(img, DPI, ds.AUTOMATICO, lado=a["lado"])
    lado_a_lado = np.hstack([img, np.full((img.shape[0], 10), 0, np.uint8), r.imagem])
    cv2.imwrite(str(saida / f"{k:02d}_{Path(a['livro']).stem[:18]}_p{a['pagina']:04d}_{a['metade']}.png"),
                lado_a_lado)
