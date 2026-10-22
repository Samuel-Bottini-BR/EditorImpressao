"""Verificador 22/10: compara dois ou mais PDFs ponto por ponto (soma de cada página: tamanho + pontos das imagens).
Uso: python somas_pdf.py a.pdf b.pdf [c.pdf ...]  -> diz quais páginas diferem do primeiro."""
import hashlib
import sys

import fitz


def somas(caminho):
    out = []
    with fitz.open(caminho) as doc:
        for pg in doc:
            h = hashlib.sha256(f"{pg.rect.width:.3f}x{pg.rect.height:.3f}".encode())
            for info in pg.get_images(full=True):
                pix = fitz.Pixmap(doc, info[0])
                h.update(f"{pix.width}x{pix.height}x{pix.n}".encode()); h.update(pix.samples)
            out.append(h.hexdigest())
    return out


base = somas(sys.argv[1])
for outro in sys.argv[2:]:
    s = somas(outro)
    dif = [i + 1 for i, (a, b) in enumerate(zip(base, s)) if a != b]
    print(f"{outro}: {len(s)} páginas (primeiro {len(base)}); diferentes do primeiro: {dif if dif else 'nenhuma'}")
