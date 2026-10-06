"""As imagens do relatorio: tres quadros lado a lado, sempre separados -
original | resultado | "onde olhar" (uma COPIA do original, com a area do
problema pintada em cor transparente). Nunca se desenha nada por cima do
resultado.

Cores do terceiro quadro:
  vermelho = o que o Preto e branco de hoje imprime e este jeito apagou
  laranja  = a "tinta forte fora do texto" que o programa conta hoje (o aviso)
  azul     = as linhas que o leitor de texto achou
  verde    = o que o programa achou como gravura (fica como no original)

Uso: python figuras.py   (grava ../imagens/*.jpg)
"""

from __future__ import annotations

import json

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import comum
import medir

DESTINO = comum.PASTA / "imagens"
CORES = {"sumiu": (230, 30, 30), "contou": (255, 140, 0), "linhas": (40, 110, 230),
         "gravura": (40, 170, 60)}
NOMES_DOS_JEITOS = {"a": "Guardar a tinta forte", "c": "Só o texto achado", "pb": "Preto e branco de hoje"}

# (arquivo, pagina, jeito do resultado, caixa (x0,y0,x1,y1 em fracao), camadas, legenda do 3o quadro)
FIGURAS = [
    ("hoje-a-toa-graduale222", "graduale_p222__inteira", "a", (0, 0, 1, 1), ["contou"],
     "laranja: a tinta que o programa conta (a música)"),
    ("hoje-a-toa-palatino010", "palatino_p010__inteira", "a", (0, 0, 1, 1), ["contou"],
     "laranja: a tinta que o programa conta (a moldura)"),
    ("hoje-com-razao-palatino076", "palatino_p076__inteira", "a", (0.03, 0.08, 0.52, 0.42), ["sumiu"],
     "vermelho: o desenho da letra S que sumiu"),
    ("a-palatino067", "palatino_p067__inteira", "a", (0.03, 0.33, 0.5, 0.62), ["sumiu"],
     "vermelho: o desenho de dentro da letra M que sumiu"),
    ("a-palatino066", "palatino_p066__inteira", "a", (0.0, 0.72, 0.62, 0.98), ["sumiu"],
     "vermelho: a letra M do rodapé que sumiu"),
    ("a-ljs47-103", "ljs47_p103__inteira", "a", (0.0, 0.45, 1.0, 0.95), ["sumiu"],
     "vermelho: os traços do desenho que sumiram"),
    ("linha-na-figura-boecio003-a", "boecio_p003__inteira", "a", (0.08, 0.2, 0.92, 0.9), ["linhas"],
     "azul: o que o leitor achou como texto (o 'IHS' dentro da gravura)"),
    ("linha-na-figura-boecio003-c", "boecio_p003__inteira", "c", (0.08, 0.2, 0.92, 0.9), ["sumiu", "linhas"],
     "vermelho: o que sumiu; azul: o 'IHS' que o leitor achou"),
    ("linha-na-figura-palatino057-c", "palatino_p057__inteira", "c", (0.0, 0.0, 1.0, 0.32), ["sumiu", "linhas"],
     "vermelho: o que sumiu; azul: o pedaço de floreio que o leitor achou como texto"),
    ("gravura-errada-marial454", "marial_p454__inteira", "a", (0.0, 0.15, 1.0, 0.75), ["gravura"],
     "verde: o que o programa achou como gravura (remendo e mancha)"),
    ("gravura-errada-antiphon260", "antiphon_p260__inteira", "a", (0, 0, 1, 1), ["gravura"],
     "verde: o que o programa achou como gravura (pega as pautas)"),
    ("c-boecio007", "boecio_p007__inteira", "c", (0.0, 0.0, 1.0, 0.4), ["sumiu"],
     "vermelho: a capitular e os sinais que sumiram"),
    ("c-escola197", "escola_p197__inteira", "c", (0.0, 0.0, 0.55, 0.42), ["sumiu"],
     "vermelho: os números que sumiram"),
    ("c-graduale222", "graduale_p222__inteira", "c", (0, 0, 1, 1), ["sumiu"],
     "vermelho: a música que sumiu"),
    ("c-rhetorica129", "rhetorica_p129__inteira", "c", (0, 0, 1, 1), ["sumiu"],
     "vermelho: a gravura que sumiu"),
]


def _fonte(tamanho: int):
    for nome in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def _rotulo(img_rgb: np.ndarray, texto: str) -> np.ndarray:
    alto = 44
    tela = Image.new("RGB", (img_rgb.shape[1], img_rgb.shape[0] + alto), (255, 255, 255))
    tela.paste(Image.fromarray(img_rgb), (0, alto))
    d = ImageDraw.Draw(tela)
    fonte = _fonte(22)
    while d.textlength(texto, font=fonte) > img_rgb.shape[1] - 10 and fonte.size > 12:
        fonte = _fonte(fonte.size - 1)
    d.text((6, 10), texto, fill=(30, 30, 30), font=fonte)
    return np.asarray(tela)


def _ler(base: str, nome: str, forma) -> np.ndarray:
    img = cv2.imread(str(comum.DADOS / f"{base}__{nome}.jpg"))
    return cv2.resize(img, (forma[1], forma[0]), interpolation=cv2.INTER_AREA)


def figura(arquivo, base, jeito, caixa, camadas, legenda) -> None:
    dados = json.loads((comum.DADOS / f"{base}.json").read_text(encoding="utf-8"))
    z = dict(np.load(comum.DADOS / f"{base}.npz"))
    s, m = medir.sinais(dados, z)
    alt, larg = z["base_tinta"].shape
    # trabalha na resolucao dos jpg (lado maior 2400)
    f = min(1.0, 2400 / max(alt, larg))
    forma = (round(alt * f), round(larg * f))
    ori = _ler(base, "original", forma)
    res = _ler(base, jeito, forma)

    def peq(mascara):
        return cv2.resize(mascara.astype(np.uint8) * 255, (forma[1], forma[0]),
                          interpolation=cv2.INTER_AREA) > 40

    resultado_tinta = z["a_tinta"] if jeito == "a" else z["c_tinta"]
    sumiu = z["base_tinta"] & ~resultado_tinta & ~z["imagem"]
    raio = max(2, int(round(dados["altura_linha"] * 0.06)))
    sumiu = cv2.dilate(sumiu.astype(np.uint8), np.ones((raio, raio), np.uint8)) > 0
    mascaras = {"sumiu": peq(sumiu), "contou": peq(cv2.dilate(m["forte"].astype(np.uint8),
                                                              np.ones((raio, raio), np.uint8)) > 0),
                "linhas": peq(z["linhas"]), "gravura": peq(z["imagem"])}
    onde = ori.astype(np.float32)
    onde = onde * 0.55 + 255 * 0.45          # o original mais claro, para a cor aparecer
    for c in camadas:
        bgr = np.array(CORES[c][::-1], np.float32)
        mm = mascaras[c]
        onde[mm] = onde[mm] * 0.45 + bgr * 0.55
    onde = onde.astype(np.uint8)

    x0, y0, x1, y1 = caixa
    ya, yb, xa, xb = int(y0 * forma[0]), int(y1 * forma[0]), int(x0 * forma[1]), int(x1 * forma[1])
    quadros = []
    nome_res = "Resultado: " + NOMES_DOS_JEITOS[jeito]
    for img, texto in ((ori, "Original"), (res, nome_res), (onde, "Onde olhar - " + legenda)):
        q = cv2.cvtColor(img[ya:yb, xa:xb], cv2.COLOR_BGR2RGB)
        quadros.append(q)
    # cada quadro com no maximo 620 px de largura e 900 de altura
    escala = min(620 / quadros[0].shape[1], 900 / quadros[0].shape[0], 1.0)
    prontos = []
    textos = ["Original", nome_res, "Onde olhar"]
    for q, t in zip(quadros, textos):
        q = cv2.resize(q, (max(1, round(q.shape[1] * escala)), max(1, round(q.shape[0] * escala))),
                       interpolation=cv2.INTER_AREA)
        q = cv2.copyMakeBorder(q, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(150, 150, 150))
        prontos.append(_rotulo(q, t))
    sep = np.full((prontos[0].shape[0], 18, 3), 255, np.uint8)
    junto = np.hstack([prontos[0], sep, prontos[1], sep, prontos[2]])
    DESTINO.mkdir(parents=True, exist_ok=True)
    Image.fromarray(junto).save(DESTINO / f"{arquivo}.jpg", quality=82)
    print(arquivo, junto.shape, flush=True)


def main() -> None:
    import sys

    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for fig in FIGURAS:
        if so and fig[0] not in so:
            continue
        figura(*fig)


if __name__ == "__main__":
    main()
