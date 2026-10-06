"""Imagens do formulario relatorios/conferir-aqui-10.html (decisoes do modo Misto, 05/10/2026).

So recorta e reduz imagens prontas; nenhuma pagina e processada e o programa nao e tocado.
Fontes:
  - relatorios/fase2-misto-2026-10-05/paineis/ e variantes/ (rodada do Misto, ramo fase2-misto);
  - relatorios/conferencia-4-2026-10-01/cartoes/pb6-horas13-moldura.jpg e tela/tela-caixinha.jpg,
    que so existem na pasta principal (D:/programas/EditorImpressao), fora do git.
Rodar com o Python do .venv:  .venv/Scripts/python.exe relatorios/conferencia-10-2026-10-05/scripts/montar_imagens.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent.parent          # relatorios/conferencia-10-2026-10-05
REL = AQUI.parent                                       # relatorios/
MISTO = REL / "fase2-misto-2026-10-05"
CONF4 = Path(r"D:/programas/EditorImpressao/relatorios/conferencia-4-2026-10-01")
FONTE = ImageFont.truetype(r"C:/Windows/Fonts/segoeuib.ttf", 30)
CINZA = (170, 170, 170)


def gravar(img, nome, largura_max=1600, qualidade=80):
    img = img.convert("RGB")
    if img.width > largura_max:
        img = img.resize((largura_max, round(img.height * largura_max / img.width)), Image.LANCZOS)
    img.save(AQUI / nome, quality=qualidade, optimize=True)
    print(nome, img.size, (AQUI / nome).stat().st_size // 1024, "KB")


def lado_a_lado(pedacos, folga=12):
    alt = max(p.height for p in pedacos)
    larg = sum(p.width for p in pedacos) + folga * (len(pedacos) - 1)
    tela = Image.new("RGB", (larg, alt), CINZA)
    x = 0
    for p in pedacos:
        tela.paste(p, (x, 0))
        x += p.width + folga
    return tela


def com_rotulo(img, texto, altura=48):
    tela = Image.new("RGB", (img.width, img.height + altura), "white")
    tela.paste(img, (0, altura))
    ImageDraw.Draw(tela).text((8, 6), texto, fill="black", font=FONTE)
    return tela


def colunas(caminho, limites):
    img = Image.open(caminho).convert("RGB")
    return [img.crop((x0, 0, x1, img.height)) for x0, x1 in limites]


# 1. Exemplos do Misto (Original | Preto e branco hoje | Misto): os paineis como estao, reduzidos.
for nome in ("escola_p007", "escola_p035", "palatino_p005"):
    gravar(Image.open(MISTO / "paineis" / f"{nome}.jpg"), f"ex-{nome}.jpg")

# 2. P2, papel de dentro da gravura: Misto (papel branco) | variante papel creme. Colunas 1 e 2.
c = colunas(MISTO / "variantes" / "palatino_p005.jpg", [(0, 624), (634, 1260)])
gravar(lado_a_lado(c), "p2-palatino_p005.jpg", 1300)
c = colunas(MISTO / "variantes" / "palatino_p005-detalhe.jpg", [(0, 788), (798, 1584)])
gravar(lado_a_lado(c), "p2-palatino_p005-detalhe.jpg", 1300)

# 3. P3, a foto: Misto (com a cor) | variante foto em cinza. Colunas 1 e 3.
c = colunas(MISTO / "variantes" / "escola_p007.jpg", [(0, 689), (1402, 2091)])
gravar(lado_a_lado(c), "p3-escola_p007.jpg", 1300)
c = colunas(MISTO / "variantes" / "opusmajus_p020.jpg", [(0, 646), (1316, 1962)])
gravar(lado_a_lado(c), "p3-opusmajus_p020.jpg", 1300)

# 4. P4, letras dentro da moldura: detalhe da Horas 11 (Original | Preto e branco hoje | Misto).
gravar(Image.open(MISTO / "paineis" / "horas_p011-detalhe.jpg"), "p4-horas_p011-detalhe.jpg")

# 5. P5, a caixinha das molduras: pagina inteira da Horas 13 do cartao da conferencia 4, com
#    rotulos novos (o cartao antigo dizia ANTES/AGORA, que aqui confundiria).
card = Image.open(CONF4 / "cartoes" / "pb6-horas13-moldura.jpg").convert("RGB")
paginas = card.crop((0, 196, card.width, 1062))
limites = [(0, 640), (655, 1300), (1310, card.width)]
rotulos = ["Original", "Caixinha marcada: traço preto", "Desmarcada (e o Misto): cor"]
c = [com_rotulo(paginas.crop((x0, 0, x1, paginas.height)), t) for (x0, x1), t in zip(limites, rotulos)]
gravar(lado_a_lado(c), "p5-horas_p013-moldura.jpg", 1500)

# 6. P1: a tela "O que fazer" de 01/10 (sem a faixa de titulo e sem a parte ampliada).
tela = Image.open(CONF4 / "tela" / "tela-caixinha.jpg").convert("RGB")
gravar(tela.crop((0, 92, 1500, 1040)), "p1-tela-o-que-fazer.jpg", 1300)

# 7. Risco: Marial 7, canto de cima a esquerda de cada coluna (Original | Preto e branco hoje | Misto)
#    e o mapa de onde o Misto deixa o original (em laranja).
c = colunas(MISTO / "paineis" / "marial_p007.jpg", [(0, 817), (828, 1644), (1655, 2472)])
c = [p.crop((0, 0, 470, 470)) for p in c]
gravar(lado_a_lado(c), "risco-marial_p007-canto.jpg", 1500)
gravar(Image.open(MISTO / "mascaras" / "marial_p007.jpg"), "risco-marial_p007-mapa.jpg", 700)
