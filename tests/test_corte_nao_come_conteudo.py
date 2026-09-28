"""O corte automatico de bordas nao pode comer conteudo (Lista de bugs, 28/09/2026).

O defeito, achado pelo Samuel na conferencia 6.7: na Escola de Jesus p. 35 o
corte comeu o comeco das linhas e o "37" do pe da pagina virou "3". A
investigacao (relatorios/investigacao-bugs-6-7-2026-09-28/) achou duas causas,
e cada teste abaixo prende uma delas:

1. o corte poe uma caixa justa em volta da MASSA da tinta e descarta a tinta
   mais de fora (SOBRA_DE_TINTA); a borda da caixa passa no meio de uma letra
   ou de um numero de pagina - a peca de tinta sai partida;
2. o endireitar gira a pagina DEPOIS do corte, sem aumentar a folha, e os
   cantos do conteudo saem para fora (o comeco e o fim das linhas somem).

Decisao do Samuel (28/09, opcao a): consertar so o "nao comer conteudo". O
"seguir a beirada do papel" fica para o ScanTailor (itens 2.5 e 2.13).

As paginas sao sinteticas (texto desenhado com cv2.putText), para o teste nao
depender do acervo nem do gabarito, que ficam fora do git.
"""

from __future__ import annotations

import cv2
import numpy as np

from core.endireitar import rotacionar
from core.pipeline import preparar_metade
from core.recortar import detectar_bordas
from modelos import ConfigFolha, ConfigPagina, Projeto

_PALAVRAS = ("mente felizes inclinados ao bem isentos de enfermidades "
             "e da morte").split()

# Cinza abaixo disto e tinta, nas paginas sinteticas (papel 238, tinta 40).
_TINTA = 150


def _pagina_de_texto(esquerda: int = 50, direita: int = 500,
                     numero: bool = True) -> np.ndarray:
    """Pagina de 800 x 560 pontos com linhas de texto alinhadas a esquerda.

    Com `numero`, poe um "37" no pe, a direita, passando 6 pontos (1,1% da
    largura) do fim da linha mais comprida - como o numero de pagina da Escola
    35, que passa 1,2%. Ele carrega pouca tinta, e e justamente a tinta "mais
    de fora" que o corte descarta.
    """
    img = np.full((800, 560, 3), 238, np.uint8)
    y, k = 70, 0
    while y < 710:
        x = esquerda
        while True:
            palavra = _PALAVRAS[k % len(_PALAVRAS)]
            k += 1
            (largura, _), _ = cv2.getTextSize(palavra, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            if x + largura > direita:
                break
            cv2.putText(img, palavra, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (40, 40, 40), 2, cv2.LINE_AA)
            x += largura + 9
        y += 26
    if numero:
        tinta = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < _TINTA
        fim_do_texto = int(np.flatnonzero(tinta.any(axis=0)).max())
        (largura, _), _ = cv2.getTextSize("37", cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
        cv2.putText(img, "37", (fim_do_texto + 9 - largura, 750), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (40, 40, 40), 2, cv2.LINE_AA)
    return img


def _pecas_partidas(img: np.ndarray, recorte) -> list[tuple[int, int, int, int]]:
    """As pecas de tinta que a caixa do corte atravessa (nem inteiras dentro,
    nem inteiras fora). A caixa e convertida para pontos como aplicar_recorte."""
    altura, largura = img.shape[:2]
    x0, y0 = int(recorte.x * largura), int(recorte.y * altura)
    x1 = int((recorte.x + recorte.largura) * largura)
    y1 = int((recorte.y + recorte.altura) * altura)
    tinta = (cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < _TINTA).astype(np.uint8)
    n, _, caixas, _ = cv2.connectedComponentsWithStats(tinta, 8)
    partidas = []
    for i in range(1, n):
        cx, cy, cw, ch = (int(v) for v in caixas[i, :4])
        dentro = cx >= x0 and cy >= y0 and cx + cw <= x1 and cy + ch <= y1
        fora = cx + cw <= x0 or cx >= x1 or cy + ch <= y0 or cy >= y1
        if not dentro and not fora:
            partidas.append((cx, cy, cw, ch))
    return partidas


def test_o_corte_nao_parte_o_numero_da_pagina():
    """O "37" passa do fim das linhas: hoje a borda do corte cai no meio do 7."""
    img = _pagina_de_texto()

    recorte = detectar_bordas(img)

    assert _pecas_partidas(img, recorte) == [], (
        "a borda do corte passou no meio de uma peca de tinta (o '37' do pe)")
    # E continua cortando: nao e para voltar a manter a folha inteira.
    assert recorte.largura < 0.95 and recorte.altura < 0.95


def test_o_corte_ainda_ignora_o_risco_que_encosta_na_beirada():
    """Nao partir peca nao pode virar "manter tudo": o risco da beirada da
    folha vizinha encosta na beirada da imagem e continua fora do corte."""
    img = _pagina_de_texto(numero=False)
    img[:, 548:551] = 60      # risco de cima a baixo, colado na direita

    recorte = detectar_bordas(img)

    assert recorte.x + recorte.largura < 540 / 560, (
        "o risco da beirada segurou a borda direita do corte")


def test_o_risco_tracejado_da_beirada_nao_arrasta_o_corte():
    """O risco da beirada da folha vem em trechos (tracejado e torto), e cada
    trecho e uma peca que encosta na seguinte. Sem limite, a borda de baixo ia
    de trecho em trecho ate o pe da imagem (Horas 14: +9% de altura; aqui, de
    89% para 97%). ESTICAR_NO_MAXIMO segura isso."""
    img = _pagina_de_texto(numero=False)
    for k, y in enumerate(range(30, 770, 14)):   # trechos de 16 pontos, desencontrados
        x = 24 if k % 2 == 0 else 34
        img[y:y + 16, x:x + 2] = 60

    recorte = detectar_bordas(img)

    assert recorte.y + recorte.altura < 0.95, (
        "o risco tracejado arrastou a borda de baixo do corte")


def test_cortar_e_endireitar_nao_empurra_o_texto_para_fora():
    """Pagina torta 1,5 grau: depois de cortar e endireitar (preparar_metade),
    nenhuma letra pode encostar na beirada da imagem, e a tinta nao pode sumir.

    Hoje o endireitar gira dentro do retangulo justo do corte, e as pontas das
    linhas saem da folha ("para" virava "oara" na Escola 35).
    """
    torta = rotacionar(_pagina_de_texto(esquerda=40, direita=515, numero=False), 1.5)
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.dividir_folhas = False      # cortar_bordas e endireitar: ligados, o padrao

    saida = preparar_metade(torta, ConfigFolha(indice=0), ConfigPagina(indice=0, folha=0),
                            projeto)

    tinta = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY) < _TINTA
    beirada = np.zeros_like(tinta)
    beirada[:3] = beirada[-3:] = True
    beirada[:, :3] = beirada[:, -3:] = True
    assert int((tinta & beirada).sum()) == 0, "tem letra encostando na beirada (cortada)"
    tinta_antes = int((cv2.cvtColor(torta, cv2.COLOR_BGR2GRAY) < _TINTA).sum())
    assert tinta.sum() >= 0.97 * tinta_antes, "sumiu tinta no corte + endireitar"
    # A folha endireitada ainda e cortada (nao voltou ao tamanho inteiro).
    assert saida.shape[0] < torta.shape[0] and saida.shape[1] < torta.shape[1]


def test_recorte_manual_nao_e_alargado_pelo_giro():
    """O recorte que a pessoa escolheu na aba Bordas e respeitado como esta:
    a folga para o giro so vale para o corte automatico."""
    torta = rotacionar(_pagina_de_texto(esquerda=40, direita=515, numero=False), 1.5)
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.dividir_folhas = False
    pagina = ConfigPagina(indice=0, folha=0, recorte=(0.1, 0.1, 0.8, 0.8))

    saida = preparar_metade(torta, ConfigFolha(indice=0), pagina, projeto)

    assert saida.shape[:2] == (640, 448)
