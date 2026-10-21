"""Verificador, 21/10 (item 2.9): procura MINHA de paginas com letra clara em fundo escuro, em mais pastas que a
do implementador (ele leu so LIVROS PARA TESTE, 14 livros). So le os PDFs, a 24 DPI. Mesmo criterio dele
(miolo > 50% escuro e > 2% claro) e mais um mais frouxo (> 35% escuro e > 5% claro), para nao perder faixas.
Uso: python procurar.py <saida> <pasta> [<pasta> ...]"""
import json
import sys
from pathlib import Path

import fitz
import numpy as np

saida = Path(sys.argv[1]); saida.mkdir(parents=True, exist_ok=True)
achadas, lidos = [], 0
for pasta in sys.argv[2:]:
    for pdf in sorted(Path(pasta).rglob("*.pdf")):
        try:
            doc = fitz.open(pdf)
        except Exception as e:  # noqa: BLE001
            print("nao abriu", pdf, e); continue
        lidos += 1
        for i, pg in enumerate(doc):
            try:
                pix = pg.get_pixmap(dpi=24, colorspace=fitz.csGRAY)
            except Exception:  # noqa: BLE001
                continue
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.stride)[:, :pix.width]
            h, w = img.shape
            m = img[h // 10:h - h // 10, w // 10:w - w // 10]
            if m.size == 0:
                continue
            esc, cla = float((m < 90).mean()), float((m > 170).mean())
            if (esc > 0.5 and cla > 0.02) or (esc > 0.35 and cla > 0.05):
                nome = f"{len(achadas):03d}_{pdf.stem[:25]}_p{i + 1}.png"
                pix.save(str(saida / nome))
                achadas.append({"livro": str(pdf), "pagina": i + 1, "escuro": round(esc, 3), "claro": round(cla, 3), "png": nome})
        doc.close()
        print(lidos, pdf.name[:50], len(achadas), flush=True)
(saida / "achadas.json").write_text(json.dumps(achadas, ensure_ascii=False, indent=1), encoding="utf-8")
print("FIM livros", lidos, "achadas", len(achadas))
