"""Pecas das imagens no modelo do girar (docs/plano/central/modelo-de-print/montar_provas_exemplo.py,
CLAUDE.md §10): faixa colorida com o rotulo grande e, embaixo, o que olhar em uma frase; as mesmas
paginas em todas as faixas; o que olhar circulado em vermelho, sem cobrir o conteudo.
Copiado do modelo (as mesmas fontes, cores e medidas), com uma peca a mais: o circulo em volta de
um PONTO da pagina (a caixa do defeito), e nao da celula inteira."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL = (60, 90, 150)
LARANJA = (190, 90, 10)
VERDE = (25, 130, 60)
ROXO = (110, 60, 150)
CINZA = (40, 40, 40)


def fonte(tamanho: int, negrito: bool = False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, tamanho)


def quebrar(texto: str, f, largura: int) -> list[str]:
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if f.getlength(teste) > largura and atual:
            linhas.append(atual)
            atual = palavra
        else:
            atual = teste
    return linhas + ([atual] if atual else [])


def cabeca(rotulo: str, cor, legenda: str, largura: int = LARGURA) -> Image.Image:
    f_rot, f_leg = fonte(44, True), fonte(26)
    linhas = quebrar(legenda, f_leg, largura - 40) if legenda else []
    img = Image.new("RGB", (largura, 86 + (14 + 36 * len(linhas) + 10 if linhas else 0)), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 82], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 100 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def texto(t: str, tamanho: int = 26, negrito: bool = False, largura: int = LARGURA,
          cor=(30, 30, 30)) -> Image.Image:
    f = fonte(tamanho, negrito)
    linhas = quebrar(t, f, largura - 40)
    alto = int(tamanho * 1.4)
    img = Image.new("RGB", (largura, alto * len(linhas) + 8), FUNDO)
    d = ImageDraw.Draw(img)
    for n, linha in enumerate(linhas):
        d.text((20, 4 + alto * n), linha, fill=cor, font=f)
    return img


def empilhar(partes: list[Image.Image], espaco: int = 16, largura: int = LARGURA) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def lado_a_lado(partes: list[Image.Image], espaco: int = 20) -> Image.Image:
    largura = sum(p.width for p in partes) + espaco * (len(partes) - 1)
    altura = max(p.height for p in partes)
    img = Image.new("RGB", (largura, altura), FUNDO)
    x = 0
    for p in partes:
        img.paste(p, (x, 0))
        x += p.width + espaco
    return img


def caber(img: Image.Image, caixa_l: int, caixa_a: int) -> Image.Image:
    escala = min(caixa_l / img.width, caixa_a / img.height)
    return img.resize((max(1, round(img.width * escala)), max(1, round(img.height * escala))),
                      Image.LANCZOS)


def abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def com_titulo(img: Image.Image, titulo: str, vermelho: bool = False, tamanho: int = 26) -> Image.Image:
    f = fonte(tamanho, True)
    alto = int(tamanho * 1.6)
    largura = max(img.width, int(f.getlength(titulo)) + 10)
    saida = Image.new("RGB", (largura, img.height + alto), FUNDO)
    d = ImageDraw.Draw(saida)
    d.text((largura / 2, 2), titulo, fill=VERMELHO if vermelho else (30, 30, 30), font=f, anchor="mt")
    saida.paste(img, ((largura - img.width) // 2, alto))
    d.rectangle([(largura - img.width) // 2 - 1, alto - 1, (largura + img.width) // 2, alto + img.height],
                outline=(150, 150, 150))
    return saida


def circular(img: Image.Image, caixa_frac, folga: float = 0.35, espessura: int = 7) -> Image.Image:
    """Um circulo vermelho em volta de caixa_frac = (x0, y0, x1, y1) em fracoes da imagem."""
    saida = img.copy()
    d = ImageDraw.Draw(saida)
    x0, y0, x1, y1 = caixa_frac
    w, h = img.width, img.height
    cx, cy = (x0 + x1) / 2 * w, (y0 + y1) / 2 * h
    rx = max((x1 - x0) * w / 2 * (1 + folga), 18)
    ry = max((y1 - y0) * h / 2 * (1 + folga), 18)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=VERMELHO, width=espessura)
    return saida


def recorte(img: Image.Image, caixa_frac) -> Image.Image:
    x0, y0, x1, y1 = caixa_frac
    return img.crop((round(x0 * img.width), round(y0 * img.height),
                     round(x1 * img.width), round(y1 * img.height)))


def salvar(img: Image.Image, destino: Path) -> None:
    assert 900 <= img.width <= 1600, (destino, img.width)
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, optimize=True)
