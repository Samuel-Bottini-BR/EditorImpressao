"""Junta imagens lado a lado na mesma altura, com um título em cima de cada (para olhar).

USO: python lado_a_lado.py saida.jpg altura "titulo1=img1.png" "titulo2=img2.png" ...
A imagem sai em JPG (qualidade 80). Só para conferir; não mexe nas imagens de entrada.
"""

from __future__ import annotations

import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def juntar(saida: str, altura: int, pares: list[tuple[str, str]], qualidade: int = 80) -> None:
    fonte = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 22)
    pedacos = []
    for titulo, caminho in pares:
        img = cv2.imread(caminho, cv2.IMREAD_COLOR)
        escala = altura / img.shape[0]
        img = cv2.resize(img, (max(1, int(img.shape[1] * escala)), altura), interpolation=cv2.INTER_AREA)
        img = cv2.copyMakeBorder(img, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(160, 160, 160))
        largura = max(img.shape[1], 260)
        topo = Image.new("RGB", (largura, 34), "white")
        ImageDraw.Draw(topo).text((4, 4), titulo, fill="black", font=fonte)
        corpo = np.full((img.shape[0], largura, 3), 255, np.uint8)
        corpo[:, :img.shape[1]] = img
        pedacos.append(np.vstack([cv2.cvtColor(np.asarray(topo), cv2.COLOR_RGB2BGR), corpo]))
        pedacos.append(np.full((pedacos[-1].shape[0], 16, 3), 255, np.uint8))
    cv2.imwrite(saida, np.hstack(pedacos[:-1]), [cv2.IMWRITE_JPEG_QUALITY, qualidade])


if __name__ == "__main__":
    juntar(sys.argv[1], int(sys.argv[2]), [tuple(a.split("=", 1)) for a in sys.argv[3:]])
