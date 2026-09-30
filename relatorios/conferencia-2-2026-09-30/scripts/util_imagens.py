"""Pecas de desenho das imagens da segunda conferencia do Samuel (30/09/2026).

Nao faz parte do programa: so monta as figuras do formulario
relatorios/conferir-aqui-2.html. Tudo em RGB (numpy uint8).

O que tem aqui:
- rotulo: poe uma faixa com texto grande EM CIMA da imagem ("ORIGINAL",
  "ANTES", "DEPOIS"...), com acentos (usa PIL e a fonte Arial do Windows);
- lado_a_lado / um_embaixo_do_outro: junta imagens com espaco branco;
- marcar: retangulo grosso com um texto curto do lado (o "olhe aqui");
- seta: seta grossa apontando para um lugar;
- zonas_por_cima: as zonas do gabarito do OCR contornadas por cima da pagina
  ORIGINAL, com um veu bem leve, sem esconder nada (a imagem antiga, com a
  tinta pintada, confundia: a tinta fora de zona saia cinza e parecia apagada).

Seguro mudar: cores, tamanhos de letra, espessuras.
Arriscado mudar: nada aqui mexe em numero nenhum; so desenho.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTE = Path(r"C:\Windows\Fonts\arial.ttf")
FONTE_NEGRITO = Path(r"C:\Windows\Fonts\arialbd.ttf")

VERDE = (0, 150, 0)
VERMELHO = (220, 0, 0)
CINZA = (70, 70, 70)
AMARELO = (255, 200, 0)
AZUL = (0, 90, 220)
MAGENTA = (230, 0, 200)


def fonte(tam: int, negrito: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTE_NEGRITO if negrito else FONTE), tam)


def _quebrar(texto: str, f, largura: int, d: ImageDraw.ImageDraw) -> list[str]:
    linhas = []
    for par in texto.split("\n"):
        atual = ""
        for palavra in par.split(" "):
            teste = (atual + " " + palavra).strip()
            if d.textlength(teste, font=f) <= largura or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = palavra
        linhas.append(atual)
    return linhas


def rotulo(img: np.ndarray, texto: str, fundo=(30, 42, 54), cor=(255, 255, 255),
           tam: int | None = None, sub: str = "") -> np.ndarray:
    """Faixa com o rotulo em cima da imagem. 'sub' vai numa segunda linha menor."""
    w = img.shape[1]
    tam = tam or max(22, min(44, w // 14))
    f, fs = fonte(tam), fonte(max(16, int(tam * 0.62)), negrito=False)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    linhas = _quebrar(texto, f, w - 20, tmp)
    linhas_sub = _quebrar(sub, fs, w - 20, tmp) if sub else []
    alt = 12 + len(linhas) * int(tam * 1.18) + len(linhas_sub) * int(tam * 0.62 * 1.25) + 10
    faixa = Image.new("RGB", (w, alt), fundo)
    d = ImageDraw.Draw(faixa)
    y = 10
    for ln in linhas:
        d.text((10, y), ln, font=f, fill=cor)
        y += int(tam * 1.18)
    for ln in linhas_sub:
        d.text((10, y), ln, font=fs, fill=cor)
        y += int(tam * 0.62 * 1.25)
    return np.vstack([np.asarray(faixa), img])


def na_altura(img: np.ndarray, alt: int) -> np.ndarray:
    esc = alt / img.shape[0]
    return cv2.resize(img, (max(1, int(round(img.shape[1] * esc))), alt),
                      interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_CUBIC)


def na_largura(img: np.ndarray, larg: int) -> np.ndarray:
    esc = larg / img.shape[1]
    return cv2.resize(img, (larg, max(1, int(round(img.shape[0] * esc)))),
                      interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_CUBIC)


def lado_a_lado(imgs: list[np.ndarray], espaco: int = 18, por_baixo: bool = False) -> np.ndarray:
    """Junta na horizontal; completa com branco se as alturas diferirem.

    por_baixo=True completa EM CIMA: com rotulos de alturas diferentes, as imagens (que
    tem a mesma altura) ficam na mesma linha, e a mesma coisa fica na mesma altura."""
    alt = max(i.shape[0] for i in imgs)
    partes = []
    for k, i in enumerate(imgs):
        if i.shape[0] < alt:
            branco = np.full((alt - i.shape[0], i.shape[1], 3), 255, np.uint8)
            i = np.vstack([branco, i] if por_baixo else [i, branco])
        partes.append(i)
        if k < len(imgs) - 1:
            partes.append(np.full((alt, espaco, 3), 255, np.uint8))
    return np.hstack(partes)


def um_embaixo_do_outro(imgs: list[np.ndarray], espaco: int = 18) -> np.ndarray:
    larg = max(i.shape[1] for i in imgs)
    partes = []
    for k, i in enumerate(imgs):
        if i.shape[1] < larg:
            pad = larg - i.shape[1]
            i = np.hstack([i, np.full((i.shape[0], pad, 3), 255, np.uint8)])
        partes.append(i)
        if k < len(imgs) - 1:
            partes.append(np.full((espaco, larg, 3), 255, np.uint8))
    return np.vstack(partes)


def moldura(img: np.ndarray, cor=(160, 160, 160), esp: int = 2) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1] - 1, out.shape[0] - 1), cor, esp)
    return out


def marcar(img: np.ndarray, ret_px, cor=MAGENTA, esp: int | None = None, texto: str = "",
           tam: int | None = None, texto_embaixo: bool = False) -> np.ndarray:
    """Retangulo grosso em volta de ret_px = (x0, y0, x1, y1) e um texto curto encostado."""
    out = img.copy()
    esp = esp or max(3, img.shape[1] // 250)
    x0, y0, x1, y1 = map(int, ret_px)
    cv2.rectangle(out, (x0, y0), (x1, y1), (255, 255, 255), esp + 4)
    cv2.rectangle(out, (x0, y0), (x1, y1), cor, esp)
    if texto:
        tam = tam or max(18, img.shape[1] // 32)
        pil = Image.fromarray(out)
        d = ImageDraw.Draw(pil)
        f = fonte(tam)
        tw = d.textlength(texto, font=f)
        tx = min(max(0, x0), max(0, out.shape[1] - tw - 12))
        ty = y1 + esp + 4 if texto_embaixo or y0 - tam - 16 < 0 else y0 - tam - 16
        ty = min(ty, out.shape[0] - tam - 12)
        d.rectangle((tx, ty, tx + tw + 12, ty + tam + 10), fill=cor)
        d.text((tx + 6, ty + 3), texto, font=f, fill=(255, 255, 255))
        out = np.asarray(pil).copy()
    return out


def seta(img: np.ndarray, de, para, cor=MAGENTA, esp: int | None = None) -> np.ndarray:
    out = img.copy()
    esp = esp or max(4, img.shape[1] // 200)
    de = tuple(map(int, de)); para = tuple(map(int, para))
    cv2.arrowedLine(out, de, para, (255, 255, 255), esp + 4, cv2.LINE_AA, tipLength=0.22)
    cv2.arrowedLine(out, de, para, cor, esp, cv2.LINE_AA, tipLength=0.2)
    return out


def zonas_por_cima(img: np.ndarray, zm: dict, esp: int | None = None, veu: float = 0.12) -> np.ndarray:
    """Zonas contornadas por cima da pagina original, com veu bem leve.

    Verde = tem de ser texto; vermelho = figura (nao pode ter linha);
    cinza = nao conta. Nada da pagina fica escondido.
    """
    out = img.copy()
    esp = esp or max(2, img.shape[1] // 450)
    for nome, cor in (("neutro", CINZA), ("figura", VERMELHO), ("texto", VERDE)):
        m = zm[nome]
        # o cinza ("nao conta") leva um veu mais forte: com o veu leve ele sumia no papel
        v = min(0.45, veu * 3) if nome == "neutro" else veu
        if v > 0 and m.any():
            out[m] = ((1 - v) * out[m] + v * np.array(cor)).astype(np.uint8)
    for nome, cor in (("figura", VERMELHO), ("texto", VERDE), ("neutro", CINZA)):  # cinza por ultimo: a caixinha nao parece vermelha
        m = zm[nome]
        if nome == "figura" and m.any() and zm["neutro"].any():
            # a caixinha cinza DENTRO da figura (letra de diagrama) nao ganha borda vermelha
            # propria: junta a figura com as caixinhas cinzas que encostam nela
            perto = cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)
            n, rot = cv2.connectedComponents(zm["neutro"].astype(np.uint8))
            encostam = np.unique(rot[perto & zm["neutro"]])
            m = m | np.isin(rot, encostam[encostam > 0])
        cont, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, cont, -1, cor, esp, cv2.LINE_AA)
    return out


LEGENDA_ZONAS = "verde = tem de ser texto · vermelho = figura (não pode ter linha) · cinza = não conta"


def gravar(img: np.ndarray, caminho: Path, qualidade: int = 85, largura_max: int = 2000) -> Path:
    if img.shape[1] > largura_max:
        img = na_largura(img, largura_max)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(caminho), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, qualidade])
    return caminho
