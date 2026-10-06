"""Rodada 3: imagens montadas a partir de imagens que ja existem (sem rodar o
programa de novo).

- conserto-desenho-apagado.jpg: as imagens do relatorio do conserto
  (ramo misto-desenho-apagado, .claude/worktrees/consertos/relatorios/conferir/
  misto-desenho-apagado-2026-10-06/imagens), Palatino 76 e Siebmacher 7,
  uma embaixo da outra, reduzidas para 1800 px.
- copias de imagens das rodadas 1 e 2 (marial, matematica, righetti, fecho).
- tela-para-revisar.jpg: o print da tela de conferir (relatorios/prints-telas-
  2026-10-02/conferir-filtro-1280x657.png) e, ao lado, uma COPIA com o painel
  "Para revisar" pintado de laranja transparente (nada por cima do print).

Uso: python imagens_prontas.py
"""
import shutil

import numpy as np
from PIL import Image, ImageDraw

import comum
from figuras import DESTINO, _com_titulo, _fonte

RAIZ = comum.RAIZ
CONSERTO = RAIZ / ".claude/worktrees/consertos/relatorios/conferir/misto-desenho-apagado-2026-10-06/imagens"
R1 = RAIZ / "relatorios/revisar-decisoes/rodada-1/img"
R2 = RAIZ / "relatorios/revisar-decisoes/rodada-2/img"


def salvar(img: Image.Image, nome: str) -> None:
    destino = DESTINO / nome
    q = 88
    while True:
        img.save(destino, quality=q)
        if destino.stat().st_size < 590_000 or q <= 70:
            break
        q -= 4
    print(nome, img.size, destino.stat().st_size // 1024, "KB")


def empilhar(arquivos, titulos, legendas, nome):
    partes = []
    for arq, tit in zip(arquivos, titulos):
        im = Image.open(arq).convert("RGB")
        f = 1800 / im.width
        im = im.resize((1800, round(im.height * f)), Image.LANCZOS)
        cab = Image.new("RGB", (1800, 46), "white")
        ImageDraw.Draw(cab).text((6, 8), tit, font=_fonte(28, True), fill=(20, 20, 20))
        partes += [cab, im, Image.new("RGB", (1800, 20), "white")]
    alto = sum(p.height for p in partes) + 40 * len(legendas) + 10
    tela = Image.new("RGB", (1800, alto), "white")
    y = 0
    for p in partes:
        tela.paste(p, (0, y))
        y += p.height
    d = ImageDraw.Draw(tela)
    for i, t in enumerate(legendas):
        d.text((6, y + 4 + 40 * i), t, font=_fonte(26), fill=(40, 40, 40))
    salvar(tela, nome)


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    empilhar([CONSERTO / "palatino_p076__inteira.jpg", CONSERTO / "siebmacher_p007__esquerda.jpg"],
             ["Palatino 76", "Siebmacher 7 (página da esquerda)"],
             ["Da esquerda para a direita: original · como sai hoje · com o conserto · Preto e branco de sempre · em azul, o que voltou.",
              "O conserto (em conferência) traz de volta o desenho claro que o programa apagava."],
             "conserto-desenho-apagado.jpg")
    for origem, nome in ((R2 / "resp-marial454-marcar.jpg", "marial454-tirar.jpg"),
                         (R2 / "righetti041e.jpg", "faixa-righetti041e.jpg"),
                         (R2 / "resp-matematica032.jpg", "faixa-matematica032.jpg"),
                         (R1 / "fecho-graduale222.jpg", "so-texto-graduale222.jpg")):
        shutil.copy(origem, DESTINO / nome)
        print(nome, "copiada")

    tela = Image.open(RAIZ / "relatorios/prints-telas-2026-10-02/conferir-filtro-1280x657.png").convert("RGB")
    a = np.asarray(tela).astype(np.float32)
    copia = a * 0.6 + 255 * 0.4
    y0, y1, x0, x1 = 205, 285, 1358, 1560
    copia[y0:y1, x0:x1] = copia[y0:y1, x0:x1] * 0.45 + np.array([255, 130, 0]) * 0.55
    w = (1800 - 24) // 2 - 4
    q1 = _com_titulo(np.asarray(tela.resize((w, round(tela.height * w / tela.width)), Image.LANCZOS)),
                     "A tela de conferir (como é hoje)", w + 4)
    c = Image.fromarray(copia.astype(np.uint8))
    q2 = _com_titulo(np.asarray(c.resize((w, round(c.height * w / c.width)), Image.LANCZOS)),
                     "Onde olhar: em laranja, o painel 'Para revisar'", w + 4)
    leg = ["'Para revisar' é o painel no alto, à direita, da tela de conferir. Ali aparecem as páginas que o programa",
           "acha que alguém deve olhar antes de imprimir; clicar leva até elas. Hoje ele diz 'nada pendente'."]
    out = Image.new("RGB", (1800, q1.height + 20 + 40 * len(leg)), "white")
    out.paste(q1, (0, 0))
    out.paste(q2, (q1.width + 24, 0))
    d = ImageDraw.Draw(out)
    for i, t in enumerate(leg):
        d.text((6, q1.height + 8 + 40 * i), t, font=_fonte(26), fill=(40, 40, 40))
    salvar(out, "tela-para-revisar.jpg")


if __name__ == "__main__":
    main()
