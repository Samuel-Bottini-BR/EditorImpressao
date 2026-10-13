"""Confere um PDF de saida: quantas paginas tem e guarda a imagem de uma pagina (so leitura)."""
import sys, fitz
from pathlib import Path
pdf, pagina, nome = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = fitz.open(pdf)
print("paginas no PDF:", len(d), [ (round(p.rect.width), round(p.rect.height)) for p in d][:8])
if pagina:
    pg = d[pagina - 1]
    imgs = pg.get_images(full=True)
    print("imagens na pagina:", [(i[2], i[3], i[5], i[8]) for i in imgs])
    pix = pg.get_pixmap(dpi=300)
    destino = Path(__file__).resolve().parent.parent / "trabalho" / "desenhos" / f"{nome}.png"
    pix.save(destino); print(destino, pix.width, pix.height)
