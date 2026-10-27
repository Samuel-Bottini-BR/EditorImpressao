import sys, fitz
from PIL import Image, ImageDraw
pdf, saida, ini, fim = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
d = fitz.open(pdf)
ims = []
for i in range(ini - 1, min(fim, d.page_count)):
    pix = d[i].get_pixmap(dpi=30)
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    ims.append((i + 1, im, d[i].rect))
H = 260
cols = 6
cel = 230
rows = (len(ims) + cols - 1) // cols
c = Image.new("RGB", (cols * cel, rows * (H + 30)), (60, 60, 60))
dr = ImageDraw.Draw(c)
for k, (n, im, r) in enumerate(ims):
    esc = min((cel - 10) / im.width, H / im.height)
    im2 = im.resize((max(1, int(im.width * esc)), max(1, int(im.height * esc))))
    x, y = (k % cols) * cel + 5, (k // cols) * (H + 30)
    c.paste(im2, (x, y))
    dr.text((x, y + H + 5), f"p{n}  {r.width/72*2.54:.1f}x{r.height/72*2.54:.1f}cm", fill=(255, 255, 0))
c.save(saida)
