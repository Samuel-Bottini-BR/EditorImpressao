"""Verificador, 14/11/2026: monta as imagens de prova no modelo do girar (CLAUDE.md §10;
docs/plano/central/modelo-de-print/): uma imagem-resumo com título e uma linha (livro, página,
clique), depois uma faixa por situação com cor e título grande (azul = como é hoje; laranja =
outra situação; verde = já consertado), as mesmas peças lado a lado com o nome em cima, o que
olhar circulado em vermelho e uma frase embaixo do título.

    from modelo import Peca, Faixa, montar
    montar("Erro 3 - resumo", "Os Lusíadas, página 14 ...", [Faixa("azul", "COMO É HOJE",
           "a frase", [Peca("página 14", "x.png", recorte=(x0,y0,x1,y1), circulos=[(x,y,r)])])],
           destino)
Os círculos são em pixels da imagem ORIGINAL (antes do recorte e da redução)."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CORES = {"azul": (37, 99, 235), "laranja": (234, 120, 20), "verde": (22, 150, 70),
         "cinza": (90, 90, 90)}
VERMELHO = (220, 20, 20)
FONTE = r"C:\Windows\Fonts\segoeui.ttf"
FONTE_B = r"C:\Windows\Fonts\segoeuib.ttf"


def _f(tam, negrito=False):
    return ImageFont.truetype(FONTE_B if negrito else FONTE, tam)


@dataclass
class Peca:
    nome: str
    imagem: object                      # caminho ou PIL.Image
    recorte: tuple | None = None        # (x0, y0, x1, y1) na imagem original
    circulos: list = field(default_factory=list)   # [(cx, cy, raio)] na imagem original
    retangulos: list = field(default_factory=list)  # [(x0, y0, x1, y1)] na original (contorno vermelho)
    nome_vermelho: bool = False
    altura: int = 520


@dataclass
class Faixa:
    cor: str
    titulo: str
    frase: str
    pecas: list


def _quebrar(texto, fonte, largura, desenho):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if desenho.textlength(teste, font=fonte) <= largura:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def _peca(p: Peca) -> Image.Image:
    img = p.imagem if isinstance(p.imagem, Image.Image) else Image.open(p.imagem)
    img = img.convert("RGB")
    x0, y0 = 0, 0
    if p.recorte:
        x0, y0 = p.recorte[0], p.recorte[1]
        img = img.crop(p.recorte)
    escala = p.altura / img.height
    img = img.resize((max(1, round(img.width * escala)), p.altura), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    for cx, cy, r in p.circulos:
        cx, cy, r = (cx - x0) * escala, (cy - y0) * escala, r * escala
        for k in range(4):
            d.ellipse((cx - r - k, cy - r - k, cx + r + k, cy + r + k), outline=VERMELHO)
    for a, b, c, e in p.retangulos:
        a, b, c, e = (a - x0) * escala, (b - y0) * escala, (c - x0) * escala, (e - y0) * escala
        for k in range(4):
            d.rectangle((a - k, b - k, c + k, e + k), outline=VERMELHO)
    return img


def montar(titulo: str, linha: str, faixas: list, destino: Path, largura_max: int = 2200) -> Path:
    blocos = []
    medida = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for fx in faixas:
        pecas = [_peca(p) for p in fx.pecas]
        vao = 24
        larg = max(900, sum(i.width for i in pecas) + vao * (len(pecas) + 1),
                   int(medida.textlength(fx.titulo, font=_f(46, True))) + 50)
        frase_l = _quebrar(fx.frase, _f(30), larg - 40, medida)
        alto_titulo = 70 + 40 * len(frase_l) + 16
        alto = alto_titulo + 46 + max(i.height for i in pecas) + vao
        bloco = Image.new("RGB", (larg, alto), (255, 255, 255))
        d = ImageDraw.Draw(bloco)
        cor = CORES[fx.cor]
        d.rectangle((0, 0, larg, alto_titulo), fill=cor)
        d.text((20, 10), fx.titulo, font=_f(46, True), fill=(255, 255, 255))
        for k, l in enumerate(frase_l):
            d.text((20, 70 + 40 * k), l, font=_f(30), fill=(255, 255, 255))
        d.rectangle((0, 0, larg - 1, alto - 1), outline=cor, width=6)
        x = vao
        for p, img in zip(fx.pecas, pecas):
            d.text((x, alto_titulo + 6), p.nome, font=_f(30, True),
                   fill=VERMELHO if p.nome_vermelho else (30, 30, 30))
            bloco.paste(img, (x, alto_titulo + 46))
            d.rectangle((x - 1, alto_titulo + 45, x + img.width, alto_titulo + 46 + img.height),
                        outline=(160, 160, 160))
            x += img.width + vao
        blocos.append(bloco)
    larg = max(max(b.width for b in blocos), int(medida.textlength(titulo, font=_f(52, True))) + 20)
    linhas = _quebrar(linha, _f(30), larg - 40, medida)
    topo = 80 + 40 * len(linhas) + 20
    final = Image.new("RGB", (larg + 40, topo + sum(b.height + 24 for b in blocos)), (245, 245, 245))
    d = ImageDraw.Draw(final)
    d.text((20, 12), titulo, font=_f(52, True), fill=(20, 20, 20))
    for k, l in enumerate(linhas):
        d.text((20, 80 + 40 * k), l, font=_f(30), fill=(40, 40, 40))
    y = topo
    for b in blocos:
        final.paste(b, (20, y))
        y += b.height + 24
    if final.width > largura_max:
        e = largura_max / final.width
        final = final.resize((largura_max, round(final.height * e)), Image.LANCZOS)
    destino.parent.mkdir(parents=True, exist_ok=True)
    final.save(destino, quality=88)
    return destino
