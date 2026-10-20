"""Verificador, 20/10/2026: recortes "so a parte que muda, ampliada" para a conferencia cg6 (aba 3).
Parte das imagens tres-<pagina>.jpg do implementador (fase-1 | d97b937 | agora, mesma escala), que
eu abri uma a uma. Cada painel e um terco da largura; a caixa e em fracao do painel.
Grava img/cg6b-<nome>.jpg com rotulos. So le."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PASTA = Path(__file__).resolve().parent.parent
ORIG = Path(r"D:\programas\EditorImpressao\.claude\worktrees\conserto-corte-g6\relatorios\conferir"
            r"\conserto-corte-g6-pesel21-2026-10-20\img")
IMG = PASTA / "img"
IMG.mkdir(exist_ok=True)
FONTE = ImageFont.truetype("arialbd.ttf", 30)

# nome: (pagina, caixa em fracao do painel (x0,y0,x1,y1), quais paineis, rotulos)
HOJE, D97, AGORA = "Hoje no programa", "Conserto de 13/10", "Conserto de agora"
PEDIDOS = {
    "pesel-21": ("pesel_p021", (0.0, 0.72, 1.0, 1.0), (0, 1, 2), (HOJE, D97, AGORA)),
    "cursus-3": ("cursus_p003", (0.55, 0.0, 1.0, 0.45), (0, 2), (HOJE, "Com o conserto")),
    "matematica-32": ("matematica_p032", (0.45, 0.55, 1.0, 1.0), (0, 2), (HOJE, "Com o conserto")),
    "antiphon-260": ("antiphon_p260", (0.0, 0.75, 1.0, 1.0), (0, 2), (HOJE, "Com o conserto")),
    "antiphon-88": ("antiphon_p088", (0.55, 0.0, 1.0, 0.35), (0, 2), (HOJE, "Com o conserto")),
    "camoes-104": ("camoes_p104", (0.0, 0.0, 0.35, 0.4), (0, 2), (HOJE, "Com o conserto")),
}

for nome, (pid, (x0, y0, x1, y1), paineis, rotulos) in PEDIDOS.items():
    im = Image.open(ORIG / f"tres-{pid}__inteira.jpg").convert("RGB")
    w3 = im.width / 3
    topo = 50                                   # o cabecalho de cada painel
    h = im.height - topo
    pedacos = []
    for p in paineis:
        caixa = (round(p * w3 + x0 * w3), round(topo + y0 * h), round(p * w3 + x1 * w3), round(topo + y1 * h))
        pedacos.append(im.crop(caixa))
    alvo = 760 if len(pedacos) == 2 else 520
    pedacos = [c.resize((alvo, round(c.height * alvo / c.width)), Image.LANCZOS) for c in pedacos]
    alto = max(c.height for c in pedacos)
    tela = Image.new("RGB", (sum(c.width for c in pedacos) + 24 * (len(pedacos) - 1), alto + 48), "white")
    d = ImageDraw.Draw(tela)
    x = 0
    for c, r in zip(pedacos, rotulos):
        tela.paste(c, (x, 48))
        d.text((x + 6, 8), r, fill=(160, 60, 0), font=FONTE)
        x += c.width + 24
    tela.save(IMG / f"cg6b-{nome}.jpg", quality=90)
    print(nome, tela.size)
