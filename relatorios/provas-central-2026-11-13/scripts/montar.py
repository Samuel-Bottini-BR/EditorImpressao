"""Monta as imagens finais no "jeito do girar" (docs/plano/central/modelo-de-print):
faixa colorida com o rótulo grande + frase do que olhar; as mesmas páginas lado a lado; o que
olhar circulado em vermelho. Largura 1500.

    python montar.py <item: 1|2|3|4|5>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
CRU = AQUI / "cru"
SAIDA = Path(r"D:\programas\EditorImpressao\relatorios\provas-central-2026-11-13")
FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL, LARANJA, VERDE, ESCURO = (60, 90, 150), (190, 90, 10), (25, 130, 60), (40, 40, 40)
LEGENDAS_ARQ = SAIDA / "legendas.json"


def fonte(t: int, negrito: bool = False):
    return ImageFont.truetype(FONTE_N if negrito else FONTE, t)


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
    f_rot, f_leg = fonte(46, True), fonte(26)
    linhas = quebrar(legenda, f_leg, largura - 40) if legenda else []
    img = Image.new("RGB", (largura, 86 + (14 + 36 * len(linhas) + 10 if linhas else 0)), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 86], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 100 + 36 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def titulo(texto: str, largura: int = LARGURA - 40, cor=(30, 30, 30), tamanho: int = 30) -> Image.Image:
    f = fonte(tamanho, True)
    linhas = quebrar(texto, f, largura)
    t = Image.new("RGB", (largura, 10 + int(tamanho * 1.45) * len(linhas)), FUNDO)
    d = ImageDraw.Draw(t)
    for n, l in enumerate(linhas):
        d.text((0, 4 + int(tamanho * 1.45) * n), l, fill=cor, font=f)
    return t


def empilhar(partes: list[Image.Image], espaco: int = 16, largura: int = LARGURA) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def lado_a_lado(partes: list[Image.Image], espaco: int = 24) -> Image.Image:
    altura = max(p.height for p in partes)
    img = Image.new("RGB", (sum(p.width for p in partes) + espaco * (len(partes) - 1), altura), FUNDO)
    x = 0
    for p in partes:
        img.paste(p, (x, (altura - p.height) // 2))
        x += p.width + espaco
    return img


def caber(img: Image.Image, l: int, a: int) -> Image.Image:
    e = min(l / img.width, a / img.height)
    return img.resize((max(1, round(img.width * e)), max(1, round(img.height * e))), Image.LANCZOS)


def largura(img: Image.Image, l: int) -> Image.Image:
    return img.resize((l, round(img.height * l / img.width)), Image.LANCZOS)


def circular(img: Image.Image, caixa, folga: int = 14, grossura: int = 7) -> Image.Image:
    """Elipse vermelha em volta de caixa=(x0, y0, x1, y1), nas coordenadas da imagem."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = caixa
    d.ellipse([x0 - folga, y0 - folga, x1 + folga, y1 + folga], outline=VERMELHO, width=grossura)
    return img


def retangulo(img: Image.Image, caixa, grossura: int = 6) -> Image.Image:
    img = img.copy()
    ImageDraw.Draw(img).rounded_rectangle(caixa, radius=14, outline=VERMELHO, width=grossura)
    return img


def com_moldura(img: Image.Image, cor=(150, 150, 150)) -> Image.Image:
    out = Image.new("RGB", (img.width + 2, img.height + 2), cor)
    out.paste(img, (1, 1))
    return out


def legenda_embaixo(img: Image.Image, texto: str, tamanho: int = 26, cor=(30, 30, 30)) -> Image.Image:
    f = fonte(tamanho, True)
    linhas = quebrar(texto, f, max(img.width, 200))
    alto = 8 + int(tamanho * 1.4) * len(linhas)
    out = Image.new("RGB", (img.width, img.height + alto), FUNDO)
    out.paste(img, (0, 0))
    d = ImageDraw.Draw(out)
    for n, l in enumerate(linhas):
        d.text((img.width / 2, img.height + 4 + int(tamanho * 1.4) * n), l, fill=cor, font=f, anchor="mt")
    return out


def legenda_em_cima(img: Image.Image, texto: str, tamanho: int = 26, cor=(30, 30, 30)) -> Image.Image:
    f = fonte(tamanho, True)
    linhas = quebrar(texto, f, max(img.width, 200))
    alto = 8 + int(tamanho * 1.4) * len(linhas)
    out = Image.new("RGB", (img.width, img.height + alto), FUNDO)
    d = ImageDraw.Draw(out)
    for n, l in enumerate(linhas):
        d.text((img.width / 2, 2 + int(tamanho * 1.4) * n), l, fill=cor, font=f, anchor="mt")
    out.paste(img, (0, alto))
    return out


def salvar(img: Image.Image, nome: str, legenda: str) -> None:
    assert 900 <= img.width <= 1600, (nome, img.width)
    SAIDA.mkdir(parents=True, exist_ok=True)
    img.save(SAIDA / nome, optimize=True)
    tudo = json.loads(LEGENDAS_ARQ.read_text(encoding="utf-8")) if LEGENDAS_ARQ.exists() else {}
    tudo[nome] = legenda
    LEGENDAS_ARQ.write_text(json.dumps(tudo, ensure_ascii=False, indent=1), encoding="utf-8")
    print("ok", nome, img.size)


def abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def caixa_da_pagina(img: Image.Image, area=(55, 48, 1545, 588), fundo=(43, 43, 43)) -> tuple:
    """Onde está a imagem da página dentro da área de trabalho (o que não é o cinza do fundo)."""
    a = np.asarray(img.crop(area)).astype(int)
    diferente = np.abs(a - np.array(fundo)).sum(axis=2) > 12
    cols = np.where(diferente.mean(axis=0) > 0.30)[0]
    rows = np.where(diferente[:, cols.min():cols.max() + 1].mean(axis=1) > 0.30)[0]
    return (area[0] + int(cols.min()), area[1] + int(rows.min()),
            area[0] + int(cols.max()) + 1, area[1] + int(rows.max()) + 1)


def faixa_preta_em_cima(img: Image.Image, ate: float = 0.35) -> tuple | None:
    """(y0, y1) das linhas quase todas pretas na parte de cima da imagem, ou None."""
    a = np.asarray(img.convert("L")).astype(int)
    alto = int(a.shape[0] * ate)
    pretas = np.where((a[:alto] < 60).mean(axis=1) > 0.85)[0]
    if pretas.size == 0:
        return None
    return int(pretas.min()), int(pretas.max()) + 1


def marcar_o_alto(pg: Image.Image, acima: int = 46, dentro: int = 10, texto: str = "") -> Image.Image:
    """Elipse vermelha no ALTO da página quase toda fora dela (não risca o texto): a página vai
    numa tela com folga em cima, e a elipse cobre a folga e só `dentro` pontos da página."""
    folga_l = 16
    out = Image.new("RGB", (pg.width + 2 * folga_l, pg.height + acima), FUNDO)
    out.paste(pg, (folga_l, acima))
    d = ImageDraw.Draw(out)
    d.ellipse([2, 3, out.width - 3, acima + dentro], outline=VERMELHO, width=6)
    if texto:
        d.text((out.width / 2, acima * 0.42), texto, fill=VERMELHO, font=fonte(20, True), anchor="mm")
    return out
