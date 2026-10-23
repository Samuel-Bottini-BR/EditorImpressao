"""Procura no acervo páginas com letra clara em fundo escuro (item 2.9, 20/10/2026).

Lê cada página a 24 DPI (somente leitura) e mede, no miolo da página (sem 10%
de cada beirada, onde fica a borda do scanner): a fração de pontos escuros
(cinza < 90) e, entre os pontos claros (> 170), quantos estão soltos no meio do
escuro. Página com miolo mais escuro que claro é candidata; a lista sai em
JSON e as miniaturas das candidatas numa pasta, para abrir e conferir a olho.

Uso: python procurar_claro_no_escuro.py <pasta do acervo> <pasta das miniaturas>
"""
import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

acervo, saida = Path(sys.argv[1]), Path(sys.argv[2])
saida.mkdir(parents=True, exist_ok=True)
candidatas = []
for pdf in sorted(acervo.glob("*.pdf")):
    doc = fitz.open(pdf)
    for i, pagina in enumerate(doc):
        pix = pagina.get_pixmap(dpi=24, colorspace=fitz.csGRAY)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width]
        h, w = img.shape
        miolo = img[h // 10:h - h // 10, w // 10:w - w // 10]
        escuro = float((miolo < 90).mean())
        claro = float((miolo > 170).mean())
        if escuro > 0.5 and claro > 0.02:
            nome = f"{pdf.stem[:20]}_p{i + 1:04d}"
            candidatas.append({"livro": pdf.name, "pagina": i + 1, "escuro": round(escuro, 3),
                               "claro": round(claro, 3)})
            cv2.imwrite(str(saida / f"{nome}.png"), img)
    doc.close()
    print(pdf.name, sum(1 for c in candidatas if c["livro"] == pdf.name), flush=True)
(saida / "candidatas.json").write_text(json.dumps(candidatas, ensure_ascii=False, indent=1), encoding="utf-8")
