"""Varre o acervo (somente leitura): em quantas folhas a regra da tampa (D-495) acharia algo."""
import sys, json, glob, os
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\obra-etapa4")
import cv2
from core.pdf_io import abrir_pdf, pagina_para_array, info_paginas
from core.endireitar import girar_90
from core.dividir_a_mao import achar_a_tampa
ACERVO = r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE"
saida = {}
os.makedirs("_tmp/e4/varre", exist_ok=True)
for pdf in sorted(glob.glob(ACERVO + "/*.pdf")):
    nome = os.path.basename(pdf)[:30]
    doc = abrir_pdf(pdf)
    n = len(info_paginas(doc))
    giros = (270,) if "Righetti" in pdf else (0,)
    achadas = []
    for i in range(n):
        img = pagina_para_array(doc, i, dpi=150)
        for g in giros:
            im = girar_90(img, g) if g else img
            t = achar_a_tampa(im, g, 150)
            if t:
                achadas.append((i + 1, t))
                if len(achadas) <= 6:
                    x0, y0, x1, y1 = t[1:]
                    h, w = im.shape[:2]
                    v = im.copy()
                    cv2.rectangle(v, (int(x0*w), int(y0*h)), (int(x1*w)-1, int(y1*h)-1), (0, 0, 255), 6)
                    cv2.imwrite(f"_tmp/e4/varre/{nome[:12]}_{i+1}.jpg", cv2.resize(v, None, fx=0.4, fy=0.4))
    doc.close()
    saida[nome] = {"folhas": n, "com_tampa": len(achadas), "exemplos": achadas[:8]}
    print(nome, n, len(achadas), achadas[:3], flush=True)
json.dump(saida, open("_tmp/e4/varrer_tampa.json", "w"), indent=1)
