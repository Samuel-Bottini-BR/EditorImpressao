"""Folha de contato das candidatas da procura (so para o verificador olhar)."""
import glob
import os
import sys

from PIL import Image, ImageDraw

fs = sorted(glob.glob(os.path.join(sys.argv[1], "*.png")))
ini = int(sys.argv[3]) if len(sys.argv) > 3 else 0
fs = fs[ini:ini + 98]
W, H, cols = 140, 200, 14
t = Image.new("L", (cols * W, ((len(fs) + cols - 1) // cols) * (H + 14)), 255)
d = ImageDraw.Draw(t)
for i, f in enumerate(fs):
    im = Image.open(f).convert("L"); im.thumbnail((W - 4, H - 4))
    x, y = (i % cols) * W, (i // cols) * (H + 14)
    t.paste(im, (x + 2, y + 14)); d.text((x + 2, y), os.path.basename(f)[:3], fill=0)
t.save(sys.argv[2]); print(len(fs), t.size)
