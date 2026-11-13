"""Imagens do item 2 (dv-211-215): Preto e branco + Letras com a cor delas + Reduzir cores."""
from __future__ import annotations

import fitz
from PIL import Image

from montar import (AZUL, CRU, ESCURO, LARGURA, VERDE, abrir, caber, cabeca, circular, com_moldura,
                    empilhar, largura, retangulo, salvar, titulo)

P = CRU / "p2"
# recorte nas coordenadas da página de hoje (a página inteira a 300 DPI); a de antes saiu cortada
# pelo "O que fazer" de fábrica e fica deslocada (-934, -151) (achado por comparação de imagem)
RECORTE = (1500, 1680, 2700, 2140)
DESLOCA_ANTES = (-934, -151)
LEONARD = (15, 12, 600, 108)
THEODORE = (15, 352, 640, 448)


def original() -> Image.Image:
    with fitz.open(str(CRU.parent / "livros" / "horas_paginas_25a27_hoje.pdf")) as d:
        pix = d[1].get_pixmap(dpi=300, clip=fitz.Rect(*(v * 72 / 300 for v in RECORTE)))
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def trecho(img: Image.Image, desloca=(0, 0)) -> Image.Image:
    x0, y0, x1, y1 = RECORTE
    dx, dy = desloca
    t = img.crop((x0 + dx, y0 + dy, x1 + dx, y1 + dy))
    t = circular(t, LEONARD, folga=10, grossura=6)
    t = circular(t, THEODORE, folga=10, grossura=6)
    return com_moldura(largura(t, 1100))


def palavras():
    antes = abrir(P / "antes" / "pdf-p26-300dpi.png")
    hoje = abrir(P / "hoje" / "pdf-p26-300dpi.png")
    orig = original()
    orig = com_moldura(largura(orig, 1100))
    img = empilhar([
        cabeca("ANTES do conserto (27/10)", AZUL,
               "Programa de antes do conserto (commit 50f03701; abria pela tela \"O que fazer\" > "
               "\"Conferir\", de fábrica). Livro de Horas, página 26, como sai no PDF: Preto e branco + \"Letras com a cor delas\" + \"Reduzir cores\". Em vermelho, "
               "\"S. Leonard\" e \"Theodore\": parte das letras sai PRETA e parte CLARA na mesma "
               "palavra (\"L\", \"n\", \"rd\" pretos; \"eo\", \"a\" claros)."),
        trecho(antes, DESLOCA_ANTES),
        cabeca("HOJE", VERDE,
               "Programa de hoje (obra-2026-10-26, 3a721bf8), as mesmas caixinhas na mesma página. "
               "Nenhuma letra sai preta nem some. MAS a palavra ainda sai em DUAS cores: \"S.\", \"L\", "
               "\"n\" e \"Th\" em azul-acinzentado; \"eo\", \"ard\", \"eodore\" em bege claro."),
        trecho(hoje),
        cabeca("Para comparar: o scan", ESCURO,
               "O mesmo trecho no scan (filtro Original, sem caixinha): cada palavra é de uma tinta "
               "só, cinza-escura, sem diferença entre as letras."),
        orig,
    ])
    salvar(img, "2-cores-a-palavras-antes-e-hoje.png",
           "Horas 26, \"S. Leonard\" e \"Theodore\" no PDF (Preto e branco + Letras com a cor delas + "
           "Reduzir cores): antes, metade preta e metade clara; hoje nada sai preto, mas a palavra "
           "ainda sai em duas cores (azul e bege).")


def janela():
    tela = abrir(P / "hoje" / "janela-caixinhas.png")
    tela = retangulo(tela, (1189, 600, 1515, 690), grossura=5)       # as duas caixinhas
    tela = retangulo(tela, (1188, 492, 1516, 528), grossura=4)       # "Mais ajustes"
    img = empilhar([
        cabeca("ONDE FICAM AS CAIXINHAS (hoje)", ESCURO,
               "Programa de hoje, janela 1280 x 657. Painel \"Filtro da página\" (ícone de meia-lua à "
               "direita), filtro \"Preto e branco\", parte \"Mais ajustes\" aberta: \"Letras com a cor "
               "delas\" e \"Reduzir cores\" à vista e marcadas (quadros vermelhos). Livro de Horas, "
               "página 26."),
        com_moldura(largura(tela, LARGURA - 40)),
    ])
    salvar(img, "2-cores-b-onde-ficam-as-caixinhas.png",
           "Onde ficam as caixinhas hoje: painel \"Filtro da página\" > Preto e branco > \"Mais ajustes\": "
           "\"Letras com a cor delas\" e \"Reduzir cores\" à vista.")


if __name__ == "__main__":
    palavras()
    janela()
