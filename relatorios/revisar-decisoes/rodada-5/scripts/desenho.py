"""Pecas de desenho comuns das imagens da rodada 4 (o formato que o Samuel
entende, igual as rodadas 1 a 3): quadros com titulo em cima, folha inteira com
a parte ampliada em amarelo transparente, legenda fixa embaixo, largura 1800 px,
JPEG abaixo de ~590 KB.

Funcoes:
  quadro(img_bgr, titulo, larg, alt_max)      -> PIL.Image com titulo e borda
  amarelo(img_bgr, caixa)                     -> copia com a caixa (fracao) em amarelo
  tingir(img_bgr, mascara, cor_rgb, forca)    -> copia com a mascara pintada
  contorno(img_bgr, mascara, cor_rgb, esp)    -> copia com o CONTORNO da mascara
                                                 desenhado (o "delineado")
  recortar(img, caixa)                        -> pedaco (caixa em fracao)
  montar(fileiras, legendas, destino)         -> grava o JPEG final
Nada aqui le o programa.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

LARGURA = 1800
VAO = 24


def fonte(tamanho: int, negrito: bool = False):
    nomes = ("arialbd.ttf", "segoeuib.ttf") if negrito else ("arial.ttf", "segoeui.ttf")
    for nome in nomes + ("DejaVuSans.ttf",):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def escala(img: np.ndarray, larg: int, alt: int, ampliar_ate: float = 3.0) -> np.ndarray:
    f = min(larg / img.shape[1], alt / img.shape[0], ampliar_ate)
    nova = (max(1, round(img.shape[1] * f)), max(1, round(img.shape[0] * f)))
    return cv2.resize(img, nova, interpolation=cv2.INTER_CUBIC if f > 1 else cv2.INTER_AREA)


def quadro(img_bgr: np.ndarray, titulo: str, larg: int, alt_max: int = 900,
           ampliar_ate: float = 3.0) -> Image.Image:
    if img_bgr.ndim == 2:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2BGR)
    q = escala(img_bgr, larg - 4, alt_max, ampliar_ate)
    q = cv2.copyMakeBorder(q, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(150, 150, 150))
    q = cv2.cvtColor(q, cv2.COLOR_BGR2RGB)
    alto = 46
    tela = Image.new("RGB", (larg, q.shape[0] + alto), (255, 255, 255))
    tela.paste(Image.fromarray(q), ((larg - q.shape[1]) // 2, alto))
    d = ImageDraw.Draw(tela)
    f = fonte(28, True)
    while d.textlength(titulo, font=f) > larg - 8 and f.size > 14:
        f = fonte(f.size - 1, True)
    d.text(((larg - d.textlength(titulo, font=f)) / 2, 8), titulo, fill=(25, 25, 25), font=f)
    return tela


def tingir(img_bgr: np.ndarray, mascara: np.ndarray, cor_rgb, forca: float = 0.45,
           clarear: bool = False) -> np.ndarray:
    x = img_bgr.astype(np.float32)
    if x.ndim == 2:
        x = np.repeat(x[:, :, None], 3, axis=2)
    if clarear:
        x = x * 0.6 + 255 * 0.4
    if mascara.shape != x.shape[:2]:
        mascara = cv2.resize(mascara.astype(np.uint8) * 255, (x.shape[1], x.shape[0]),
                             interpolation=cv2.INTER_NEAREST) > 0
    x[mascara] = x[mascara] * (1 - forca) + np.array(cor_rgb[::-1], np.float32) * forca
    return x.astype(np.uint8)


def amarelo(img_bgr: np.ndarray, caixa) -> np.ndarray:
    a, l = img_bgr.shape[:2]
    m = np.zeros((a, l), bool)
    x0, y0, x1, y1 = caixa
    m[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)] = True
    return tingir(img_bgr, m, (255, 200, 0), 0.4)


def contorno(img_bgr: np.ndarray, mascara: np.ndarray, cor_rgb, espessura: int = 6,
             tracejado: bool = True) -> np.ndarray:
    """O delineado: a linha em volta de cada area da mascara, tracejada (como o
    "selecionar" dos programas de imagem), por cima de uma COPIA."""
    x = img_bgr.copy()
    if x.ndim == 2:
        x = cv2.cvtColor(x, cv2.COLOR_GRAY2BGR)
    if mascara.shape != x.shape[:2]:
        mascara = cv2.resize(mascara.astype(np.uint8) * 255, (x.shape[1], x.shape[0]),
                             interpolation=cv2.INTER_NEAREST) > 0
    conts, _ = cv2.findContours(mascara.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cor = tuple(int(c) for c in cor_rgb[::-1])
    for c in conts:
        pts = c[:, 0, :]
        if not tracejado:
            cv2.polylines(x, [pts], True, cor, espessura, cv2.LINE_AA)
            continue
        passo = max(6, espessura * 4)
        for i in range(0, len(pts), passo * 2):
            seg = pts[i:i + passo]
            if len(seg) > 1:
                cv2.polylines(x, [seg], False, (255, 255, 255), espessura + 4, cv2.LINE_AA)
                cv2.polylines(x, [seg], False, cor, espessura, cv2.LINE_AA)
    return x


def recortar(img: np.ndarray, caixa) -> np.ndarray:
    a, l = img.shape[:2]
    x0, y0, x1, y1 = caixa
    return img[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)]


def rotulo(img_bgr: np.ndarray, texto: str, xy, cor_rgb=(20, 20, 20), tamanho: int = 40,
           fundo=(255, 255, 255)) -> np.ndarray:
    """Escreve um numero/palavra num quadradinho (numa COPIA)."""
    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(im)
    f = fonte(tamanho, True)
    w = d.textlength(texto, font=f)
    x, y = xy
    d.rectangle([x - 6, y - 4, x + w + 6, y + tamanho + 8], fill=fundo, outline=cor_rgb, width=3)
    d.text((x, y), texto, fill=cor_rgb, font=f)
    return cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)


def montar(fileiras: list[list[Image.Image]], legendas: list[str], destino: Path,
           titulo: str | None = None) -> None:
    alturas = [max(q.height for q in f) for f in fileiras]
    topo = 56 if titulo else 0
    alto = topo + sum(alturas) + VAO * (len(fileiras) - 1) + 16 + 38 * len(legendas)
    tela = Image.new("RGB", (LARGURA, alto), (255, 255, 255))
    d = ImageDraw.Draw(tela)
    if titulo:
        f = fonte(32, True)
        while d.textlength(titulo, font=f) > LARGURA - 10 and f.size > 16:
            f = fonte(f.size - 1, True)
        d.text((6, 8), titulo, fill=(10, 10, 10), font=f)
    y = topo
    for f_, h in zip(fileiras, alturas):
        x = 0
        for q in f_:
            tela.paste(q, (x, y))
            x += q.width + VAO
        y += h + VAO
    y = y - VAO + 10
    for texto in legendas:
        f = fonte(26)
        while d.textlength(texto, font=f) > LARGURA - 10 and f.size > 15:
            f = fonte(f.size - 1)
        d.text((6, y), texto, fill=(40, 40, 40), font=f)
        y += 38
    destino.parent.mkdir(parents=True, exist_ok=True)
    q = 88
    while True:
        tela.save(destino, quality=q)
        if destino.stat().st_size < 590_000 or q <= 64:
            break
        q -= 4
    print(destino.name, tela.size, q, destino.stat().st_size // 1024, "KB", flush=True)


def largura_de(n: int) -> int:
    """Largura de cada quadro numa fileira de n quadros."""
    return (LARGURA - (n - 1) * VAO) // n
