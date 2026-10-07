"""Verificador 2.1: as imagens do parecer (o que sai de cada jeito, ampliado na dobra)."""
import json, sys
from pathlib import Path
import cv2, numpy as np
sys.path.insert(0, "trabalho/novo")
from core.pdf_io import abrir_pdf, pagina_para_array
OUT = Path("imagens"); OUT.mkdir(exist_ok=True)
FONTE = cv2.FONT_HERSHEY_SIMPLEX

def titulo(img, texto, cor=(0, 0, 0), alt=44):
    img = cv2.copyMakeBorder(img, alt, 0, 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
    cv2.putText(img, texto, (8, alt - 14), FONTE, 0.8, cor, 2, cv2.LINE_AA)
    return img

def comparar(livro, folha, varre, nome, faixa_y=(0.12, 0.62), dpi=200, larg=260):
    d = {x["folha"]: x for x in json.load(open(varre))}[folha]
    doc = abrir_pdf(livro); img = pagina_para_array(doc, folha - 1, dpi=dpi); doc.close()
    if img.ndim == 2: img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    h, w = img.shape[:2]; y0, y1 = int(h * faixa_y[0]), int(h * faixa_y[1])
    paineis = []
    for jeito, cor, rot in (("programa", (200, 80, 0), "o do programa"), ("scantailor", (0, 0, 220), "o do ScanTailor")):
        x = int(round(d[jeito]["pos"] * w))
        esq = img[y0:y1, max(0, x - larg):x].copy(); dir_ = img[y0:y1, x:x + larg].copy()
        sep = np.full((y1 - y0, 24, 3), 255, np.uint8); sep[:, 10:14] = cor
        p = np.hstack([esq, sep, dir_])
        p = titulo(p, f"{rot}: corta a {d[jeito]['pos']*100:.0f}%", cor)
        paineis.append(p)
    sep = np.full((paineis[0].shape[0], 40, 3), 255, np.uint8)
    final = np.hstack([paineis[0], sep, paineis[1]])
    cv2.imwrite(str(OUT / nome), final, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(nome, final.shape)

H = r"D:\Livros para editar\Tractatus Dogmatici (vol. 3)_  - Hugon, Édouard, O.P._7207.pdf"
P = r"D:\Livros para editar\2 - TEOLOGIA\Padre M. Teixeira Leite Penido - O Corpo Místico.pdf"
comparar(H, 119, "trabalho/varre_hugon.json", "v1-hugon-119-o-que-sai-de-cada-lado.jpg")
comparar(H, 221, "trabalho/varre_hugon.json", "v2-hugon-221-o-que-sai-de-cada-lado.jpg")
comparar(P, 109, "trabalho/varre_penido.json", "v3-penido-109-o-que-sai-de-cada-lado.jpg", larg=320)
comparar(P, 113, "trabalho/varre_penido.json", "v4-penido-113-o-que-sai-de-cada-lado.jpg", larg=320)
