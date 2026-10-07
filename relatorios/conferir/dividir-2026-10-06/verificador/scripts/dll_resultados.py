"""Verificador 2.1: resultados do dividir (4 modos) e do limpar pontinhos com a DLL <dll>,
nas paginas-gabarito e em 20 folhas do Hugon. Uso: python dll_resultados.py <raiz> <dll> <saida.json>"""
import hashlib, json, sys
from pathlib import Path
raiz, dll, saida = sys.argv[1:4]
sys.path.insert(0, raiz)
import cv2, numpy as np
from core import st_ferramentas as ST, dividir_scantailor as D, pontinhos_scantailor as P
from core.pdf_io import abrir_pdf, pagina_para_array
bib = ST.BibliotecaScanTailor(Path(dll))
assert bib.disponivel, bib.motivo_indisponivel
imgs = []
for png in sorted(Path(r"D:\programas\EditorImpressao\gabarito\paginas").glob("*.png")):
    imgs.append((png.stem, cv2.imdecode(np.fromfile(str(png), np.uint8), cv2.IMREAD_COLOR)))
doc = abrir_pdf(r"D:\Livros para editar\Tractatus Dogmatici (vol. 3)_  - Hugon, Édouard, O.P._7207.pdf")
for i in range(0, 471, 24):
    imgs.append((f"hugon{i+1}", pagina_para_array(doc, i, dpi=150)))
doc.close()
res = {}
for nome, img in imgs:
    for dpi in (150, 300):
        for modo in range(4):
            r = D.achar(img, dpi, modo, biblioteca=bib)
            res[f"{nome}|{dpi}|{modo}"] = [r.tipo, [(round(c.x_cima, 9), round(c.x_baixo, 9)) for c in r.cortes]]
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b = np.where(g < 128, 0, 255).astype(np.uint8)
    r = P.limpar_pontinhos(b, 300, "normal", biblioteca=bib)
    res[f"{nome}|pontinhos"] = hashlib.sha256(r.imagem.tobytes()).hexdigest()[:20] if r.disponivel else None
Path(saida).write_text(json.dumps(res), encoding="utf-8")
print(len(res))
