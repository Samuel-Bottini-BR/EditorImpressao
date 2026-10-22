"""Verificador 22/10, passo 1: a captura (cap_<livro>_<lado>_pNNN_saida.png) bate com a pagina do PDF gerado?
Desenha a pagina do PDF a 60 DPI, reduz a captura ao mesmo tamanho e mede a diferenca media (0-255).
Uso: python captura_bate.py <pasta trabalho>"""
import json, sys
import cv2, fitz, numpy as np
t = sys.argv[1]
pdfs = {"egenloff": "egenloff_1a14", "marial": "marial_300_100"}
for livro, nome in pdfs.items():
    for lado in ("antes", "novo"):
        doc = fitz.open(f"{t}/saida_{nome}_{lado}.pdf")
        info = json.load(open(f"{t}/cap_{livro}_{lado}_info.json", encoding="utf-8"))
        res = []
        for k in sorted(info, key=int):
            n = int(k)
            pm = doc[n - 1].get_pixmap(dpi=60, colorspace=fitz.csGRAY)
            p = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width).astype(np.float32)
            c = cv2.imread(f"{t}/cap_{livro}_{lado}_p{n:03d}_saida.png", cv2.IMREAD_GRAYSCALE)
            pr = c.shape[1] / c.shape[0]; pp = pm.width / pm.height
            c = cv2.resize(c, (pm.width, pm.height), interpolation=cv2.INTER_AREA).astype(np.float32)
            d = float(np.abs(c - p).mean())
            res.append((n, round(d, 1), round(pr / pp, 3)))
        ruins = [r for r in res if r[1] > 4 or abs(r[2] - 1) > 0.01]
        print(livro, lado, len(res), "paginas; diferenca media max", max(r[1] for r in res), "| fora do esperado:", ruins)
