"""Consertos da conferencia 5 do Samuel (01/10/2026), testes de maquina.

Respostas literais em relatorios/conferencia-samuel-2026-10-01.md. Cada teste
diz o cartao que ele protege. As imagens sao sinteticas (pequenas e rapidas);
o teste de olho e a rodada de antes/depois nas paginas-gabarito.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import aplicar_filtro_com_selecao
from core.selecao import GRAVURA, Selecao, retangulo

PAPEL = (200, 222, 232)          # BGR do papel creme
OURO = (60, 170, 215)            # BGR de um dourado


def _pagina_com_letra_dourada_na_decoracao():
    """Moldura dourada larga (decoracao), uma pintura com traco fino e, no
    papel da zona, um "O" dourado grosso (anel) e, ao lado, um "I" dourado. A zona de gravura
    cobre a moldura e o papel de dentro (como a iluminura da Horas 11, em que
    o oval com o titulo esta dentro da zona). Fora da zona, linhas de texto."""
    img = np.full((1200, 900, 3), PAPEL, np.uint8)
    for y in range(700, 1150, 30):
        img[y:y + 10, 120:780:14] = 40
    cv2.rectangle(img, (60, 60), (840, 600), OURO, 60)
    img[440:560, 120:780] = (150, 210, 140)        # uma pintura com traco fino
    img[440:560, 120:780:3] = (30, 50, 20)         # (para a zona nao ser "foto")
    cv2.ellipse(img, (400, 330), (22, 36), 0, 0, 360, OURO, 10)       # o "O"
    img[290:370, 520:530] = OURO                                       # o "I"
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.56, tipo=GRAVURA))
    return img, s


# --- A2: "queremos a pagina inteiramente branca" (Horas 11) ------------------

@pytest.mark.parametrize("filtro", ["magico_pro", "preto_e_branco"])
def test_miolo_da_letra_dourada_vai_a_branco(filtro):
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), filtro, s)
    saida = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    miolo = saida[315:345, 393:407]
    assert int(miolo.min()) >= 250, "o miolo do O ficou creme"


def test_sem_fio_creme_em_volta_da_letra_dourada():
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", s)
    # a faixa de papel encostada no "I" (sem o conserto: 201 a 247, creme)
    assert int(saida[300:360, 530:536].min()) >= 250, "fio creme do lado de fora da letra"
    assert int(saida[300:360, 514:520].min()) >= 250, "fio creme do lado de fora da letra"


def test_a_letra_dourada_continua_com_a_cor_no_magico_pro():
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", s)
    centro = saida[300:360, 523:527].astype(int)
    assert int(np.abs(centro - np.array(OURO)).max()) <= 3, "o dourado da letra mudou"


# --- M2 / P4: a letra dentro da decoracao sai preta no Preto e branco --------
# M2 (Horas 26): "As letras ainda estao saindo com alguns pedacos cinzas dentro
# delas"; P4: titulos dentro da iluminura ou da moldura "saem pretos, como o
# resto do texto". No Magico pro continuam com a cor.

AZUL = (170, 90, 50)             # BGR de uma letra azul


def _pagina_com_letra_azul_e_mancha():
    img, s = _pagina_com_letra_dourada_na_decoracao()
    img[290:370, 600:612] = AZUL                         # um "I" azul
    img[300:312, 680:692] = (190, 205, 228)              # mancha clara rosada
    return img, s


def test_letra_colorida_na_decoracao_sai_preta_no_preto_e_branco():
    img, s = _pagina_com_letra_azul_e_mancha()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "preto_e_branco", s)
    assert saida.ndim == 3, "a decoracao continua em cor"
    assert int(saida[300:360, 602:610].max()) <= 10, "a letra azul nao saiu preta"
    assert int(saida[300:360, 522:528].max()) <= 10, "a letra dourada nao saiu preta"
    assert int(saida[315:345, 393:407].min()) >= 250, "o miolo do O nao ficou branco"
    # a moldura continua dourada
    assert int(np.abs(saida[40:80, 300:600].astype(int) - np.array(OURO)).max()) <= 3
    # a mancha clara nao vira ponto preto
    assert int(saida[300:312, 680:692].min()) >= 150, "a mancha virou ponto preto"


def test_letra_colorida_na_decoracao_fica_com_a_cor_no_magico_pro():
    img, s = _pagina_com_letra_azul_e_mancha()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", s)
    assert int(np.abs(saida[320:340, 603:609].astype(int) - np.array(AZUL)).max()) <= 3


# --- M1/A4 (Horas 13) e M3/A5/V2 (Horas 27): a moldura sai inteira -----------
# "ela apaga um pedaco da moldura dourada, ali perto do escrito pag. 54";
# "Temos uma falha no canto superior esquerdo da imagem". O vao que o
# ScanTailor deixa numa barra da moldura e emendado (_emendar_as_barras).

def test_o_vao_dourado_da_barra_e_emendado():
    from core.detectar_regioes import _emendar_as_barras

    gravura = np.zeros((300, 400), np.uint8)
    gravura[50:60, 20:150] = 1                  # barra, um pedaco...
    gravura[50:60, 170:380] = 1                 # ...um vao de 20 pontos, e o resto
    nao_papel = gravura.copy()
    nao_papel[50:60, 150:170] = 1               # no vao, dourado (nao e papel)
    emendada = _emendar_as_barras(gravura, nao_papel)
    assert emendada[50:60, 150:170].all(), "o vao dourado ficou de fora"


def test_papel_entre_duas_gravuras_nao_e_emendado():
    from core.detectar_regioes import _emendar_as_barras

    gravura = np.zeros((300, 400), np.uint8)
    gravura[50:60, 20:150] = 1
    gravura[50:60, 170:380] = 1
    nao_papel = gravura.copy()
    nao_papel[50:60, 155:158] = 1               # uma letra no meio do papel
    emendada = _emendar_as_barras(gravura, nao_papel)
    assert not emendada[50:60, 150:170].any(), "o papel entre as duas virou gravura"



# --- A1/I2: a letra colorida (dourada) nao some no Preto e branco -----------
# Horas 47: "o 'JESUS' e o 'C' dourados quase somem" - "Eu preciso conseguir
# enchergar todas as letras da folha".

def _pagina_com_letra_dourada_clara():
    """Papel creme, linhas de texto preto e um bloco de "letras" douradas
    claras (o brilho delas e quase o do papel)."""
    img = np.full((900, 700, 3), PAPEL, np.uint8)
    for y in range(100, 800, 40):
        img[y:y + 14, 60:640:9] = 40                      # texto preto
    for x in range(80, 400, 40):
        img[300:330, x:x + 8] = (120, 195, 225)          # hastes douradas claras
    return img


def test_letra_dourada_sai_preta_e_cheia():
    from core.filtros import filtro_preto_e_branco

    saida = filtro_preto_e_branco(_pagina_com_letra_dourada_clara())
    for x in range(80, 400, 40):
        assert float((saida[302:328, x + 1:x + 7] == 0).mean()) >= 0.9, "a letra dourada sumiu"


def test_pagina_sem_cor_sai_igual():
    """A porta (COR_DE_TINTA_NA_PAGINA): sem tinta colorida, o Preto e branco
    e o mesmo de antes, ponto a ponto."""
    from core.filtros import _com_a_tinta_colorida, filtro_preto_e_branco

    img = _pagina_com_letra_dourada_clara()
    cinza = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)
    binaria = np.full(cinza.shape[:2], 255, np.uint8)
    assert np.array_equal(_com_a_tinta_colorida(cinza, binaria), binaria)
    assert np.array_equal(filtro_preto_e_branco(cinza),
                          filtro_preto_e_branco(cv2.cvtColor(cinza, cv2.COLOR_BGR2GRAY)))
