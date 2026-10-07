"""Verificador 2.1: passa os DOIS jeitos em TODAS as folhas de um livro (150 DPI,
como a analise) e mede quantas letras a linha de corte atravessa.
Uso: python varredura.py <raiz> <livro.pdf> <saida.json> <pasta_tiras>
Letra atravessada = componente escuro do tamanho de letra (altura 6-40 px,
largura 3-60 px a 150 DPI) com pontos dos dois lados da coluna de corte.
Grava, para cada folha, uma tira de +-60 px em volta de cada corte (jpg)."""
import json, sys, time
from pathlib import Path
raiz, livro, saida, tiras = sys.argv[1:5]
sys.path.insert(0, raiz)
import cv2, numpy as np
from core import pipeline
from core.pdf_io import abrir_pdf, pagina_para_array
Path(tiras).mkdir(parents=True, exist_ok=True)

def atravessadas(cinza, x):
    h, w = cinza.shape
    x0, x1 = max(0, x - 80), min(w, x + 80)
    faixa = cinza[:, x0:x1]
    b = cv2.adaptiveThreshold(faixa, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 25, 25)
    n, rot, st, _ = cv2.connectedComponentsWithStats(b, 8)
    xc = x - x0
    cont = 0
    for i in range(1, n):
        l, t, ww, hh, a = st[i]
        if 6 <= hh <= 40 and 3 <= ww <= 60 and a >= 12 and l < xc < l + ww - 1:
            # pontos dos dois lados
            sub = rot[t:t+hh, l:l+ww] == i
            c = xc - l
            if sub[:, :c].sum() >= 3 and sub[:, c+1:].sum() >= 3:
                cont += 1
    return cont

res = []
doc = abrir_pdf(livro)
t0 = time.time()
for i in range(doc.page_count):
    img = pagina_para_array(doc, i, dpi=pipeline.DPI_ANALISE)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    h, w = cinza.shape
    item = {"folha": i + 1, "w": w, "h": h}
    for jeito in ("programa", "scantailor"):
        lb = pipeline.achar_divisao(img, jeito, pipeline.DPI_ANALISE)
        x = int(round(lb.posicao * w))
        item[jeito] = {"divide": bool(lb.e_paisagem), "pos": round(float(lb.posicao), 4),
                       "letras": atravessadas(cinza, x) if lb.e_paisagem else 0}
        if lb.e_paisagem:
            x0, x1 = max(0, x - 60), min(w, x + 60)
            tira = cv2.cvtColor(cinza[:, x0:x1], cv2.COLOR_GRAY2BGR)
            cv2.line(tira, (x - x0, 0), (x - x0, h), (0, 0, 255) if jeito == "scantailor" else (255, 0, 0), 1)
            cv2.imencode(".jpg", tira)[1].tofile(str(Path(tiras) / f"f{i+1:04d}_{jeito}.jpg"))
    res.append(item)
doc.close()
Path(saida).write_text(json.dumps(res, indent=0), encoding="utf-8")
print("folhas", len(res), "s", round(time.time() - t0))
