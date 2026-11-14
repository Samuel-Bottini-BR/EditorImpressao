"""Monta as imagens novas da reescrita da Central no modelo de print do girar (CLAUDE.md §10 e §11.13,
docs/plano/central/modelo-de-print/): título, faixas com nome (azul = como é hoje, verde = a outra
opção ou o jeito de acertar, laranja = outro caminho de hoje), as mesmas páginas, o que olhar
circulado em vermelho, uma frase por faixa.

    python montar.py            (lê ../cru/, grava em ../novas/imagens/)

Fontes: Segoe UI do Windows. Cada função monta uma pergunta e devolve {nome: legenda}.
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
CRU = AQUI.parent / "cru"
SAIDA = AQUI.parent / "novas" / "imagens"
ANTIGAS = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd\183aeec5-8cdf-43a6-b2cd-a085a307d07b\scratchpad\artifact-files\f5e9efcb-3ac3-4e35-845a-ea51f84f7c04")

FONTE = "C:/Windows/Fonts/segoeui.ttf"
FONTE_N = "C:/Windows/Fonts/segoeuib.ttf"
LARGURA = 1500
FUNDO = (250, 249, 246)
VERMELHO = (220, 20, 20)
AZUL, LARANJA, VERDE, CINZA = (60, 90, 150), (190, 90, 10), (25, 130, 60), (40, 40, 40)


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
    f_rot, f_leg = fonte(44, True), fonte(27)
    linhas = quebrar(legenda, f_leg, largura - 40)
    img = Image.new("RGB", (largura, 84 + 16 + 38 * len(linhas) + 8), FUNDO)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, largura, 84], fill=cor)
    d.text((20, 12), rotulo, fill="white", font=f_rot)
    for n, texto in enumerate(linhas):
        d.text((20, 98 + 38 * n), texto, fill=(30, 30, 30), font=f_leg)
    return img


def topo(titulo: str, frase: str, largura: int = LARGURA) -> Image.Image:
    return cabeca(titulo, CINZA, frase, largura)


def texto(t: str, largura: int = LARGURA - 40, tamanho: int = 26, negrito: bool = True) -> Image.Image:
    f = fonte(tamanho, negrito)
    linhas = quebrar(t, f, largura)
    img = Image.new("RGB", (largura, 8 + (tamanho + 10) * len(linhas)), FUNDO)
    for n, linha in enumerate(linhas):
        ImageDraw.Draw(img).text((0, 4 + (tamanho + 10) * n), linha, fill=(30, 30, 30), font=f)
    return img


def empilhar(partes, espaco: int = 16, largura: int = LARGURA) -> Image.Image:
    altura = sum(p.height for p in partes) + espaco * (len(partes) + 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    y = espaco
    for p in partes:
        img.paste(p, ((largura - p.width) // 2, y))
        y += p.height + espaco
    return img


def lado_a_lado(partes, espaco: int = 20) -> Image.Image:
    altura = max(p.height for p in partes)
    largura = sum(p.width for p in partes) + espaco * (len(partes) - 1)
    img = Image.new("RGB", (largura, altura), FUNDO)
    x = 0
    for p in partes:
        img.paste(p, (x, 0))
        x += p.width + espaco
    return img


def abrir(caminho: Path) -> Image.Image:
    return Image.open(caminho).convert("RGB")


def tela(img: Image.Image, circulos=(), caixa=None, largura: int = LARGURA - 40) -> Image.Image:
    """Foto da tela (ou o pedaço `caixa`), com elipses vermelhas em `circulos` (coordenadas da foto
    original, [x0, y0, x1, y1]) e na largura pedida."""
    img = img.copy()
    d = ImageDraw.Draw(img)
    for c in circulos:
        d.ellipse(c, outline=VERMELHO, width=5)
    if caixa:
        img = img.crop(caixa)
    return img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)


def salvar(img: Image.Image, nome: str, legendas: dict, legenda: str) -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    img.save(SAIDA / nome, optimize=True)
    legendas[nome] = legenda
    print(nome, img.size)


def gravar_legendas(legendas: dict) -> None:
    arq = SAIDA / "legendas.json"
    antigas = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    antigas.update(legendas)
    arq.write_text(json.dumps(antigas, ensure_ascii=False, indent=1), encoding="utf-8")
