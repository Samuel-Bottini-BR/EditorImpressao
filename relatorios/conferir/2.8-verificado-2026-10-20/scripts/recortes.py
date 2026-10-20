"""Verificador, 20/10/2026 (item 2.8): recortes ampliados para as fotos do Samuel, a partir das imagens
do implementador (pagina inteira em 5 colunas: Original, Hoje, Otsu, Sauvola, Wolf, cada uma 1/5 da
largura, com um cabecalho de texto). A caixa e em fracao de uma coluna. Grava img/28-<nome>.jpg."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ORIG = Path(r"D:\programas\EditorImpressao\.claude\worktrees\fase2-itens\relatorios\conferir\fase2-itens\2.8")
IMG = Path(__file__).resolve().parent.parent / "img"
IMG.mkdir(exist_ok=True)
F = ImageFont.truetype("arialbd.ttf", 26)
ROT = ["Original", "Hoje (Automático)", "Otsu do ScanTailor", "Sauvola do ScanTailor", "Wolf do ScanTailor"]
PEDIDOS = {
    "palatino-66-ferrugem": ("palatino_p066", (0.0, 0.62, 0.55, 0.98)),
    "palatino-67-ferrugem": ("palatino_p067", (0.12, 0.42, 0.42, 0.62)),
}


def faz(nome, pid, caixa):
    im = Image.open(ORIG / f"{pid}-pagina.jpg").convert("RGB")
    w = im.width / 5
    topo = 22
    h = im.height - topo
    x0, y0, x1, y1 = caixa
    cols = [im.crop((round(k * w + x0 * w), round(topo + y0 * h), round(k * w + x1 * w), round(topo + y1 * h)))
            for k in range(5)]
    alvo = 520
    cols = [c.resize((alvo, round(c.height * alvo / c.width)), Image.LANCZOS) for c in cols]
    # duas linhas: Original e Hoje em cima; os tres do ScanTailor embaixo
    t = Image.new("RGB", (alvo * 3 + 40, (cols[0].height + 40) * 2), "white")
    d = ImageDraw.Draw(t)
    for k, c in enumerate(cols):
        lin, col = (0, k) if k < 2 else (1, k - 2)
        x, y = col * (alvo + 20), lin * (c.height + 40)
        t.paste(c, (x, y + 36))
        d.text((x + 4, y + 4), ROT[k], fill=(160, 60, 0), font=F)
    t.save(IMG / f"28-{nome}.jpg", quality=90)
    print(nome, t.size)


for n, (p, c) in PEDIDOS.items():
    faz(n, p, c)
