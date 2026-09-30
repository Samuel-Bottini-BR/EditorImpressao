"""A regra do Preto e branco do Samuel (30/09/2026), testada em paginas sinteticas.

"No Preto e branco, tudo sai em preto e branco, inclusive moldura dourada,
titulo colorido e iluminura. A moldura nao deve sair dourada (como no detector
antigo) nem preta chapada (como no novo): deve sair como desenho em preto e
branco, com os tracos e detalhes em preto e o fundo da faixa em branco, sem
perder o desenho. O titulo 'NOVEMBRE.' da Horas 26 sai preto no Preto e branco.
Nos outros filtros (Magico pro, Melhorar, Original), sai com a cor original."

Foto e pintura de tom continuo: o Samuel ainda nao decidiu; ate la ficam como
estavam (em tom continuo), e a pagina com foto nao cabe em 1 bit.

Quem faz: core/filtros.py, _preto_e_branco_com_gravura. Teste de maquina: as
paginas sao desenhadas aqui, sem o acervo.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    PRETO_E_BRANCO,
    aplicar_filtro_com_selecao,
)
from core.selecao import GRAVURA, Selecao, retangulo

PAPEL = (200, 222, 232)          # creme, em BGR
DOURADO = (70, 175, 215)         # faixa dourada clara, em BGR
CONTORNO = (40, 60, 120)         # linha marrom-avermelhada do contorno


def _moldura(altura=1200, largura=900, faixa=48, margem=100):
    """Pagina creme com uma moldura dourada (faixa de `faixa` pontos) com o
    contorno marrom fino dos dois lados, como as das Horas 13, 26 e 27.
    Devolve a imagem e a mascara da faixa (para marcar como gravura)."""
    img = np.full((altura, largura, 3), PAPEL, np.uint8)
    faixa_m = np.zeros((altura, largura), np.uint8)
    cv2.rectangle(faixa_m, (margem, margem), (largura - margem, altura - margem), 255, faixa)
    img[faixa_m > 0] = DOURADO
    meia = faixa // 2
    for d in (-meia, meia):     # o contorno fino, fora e dentro da faixa
        cv2.rectangle(img, (margem + d, margem + d),
                      (largura - margem - d, altura - margem - d), CONTORNO, 3)
    return img, faixa_m > 0


def _gravura_so_na_moldura(faixa):
    """Selecao de gravura que cobre so a faixa da moldura (forma livre)."""
    s = Selecao()
    altura, largura = faixa.shape
    # quatro tiras (cima, baixo, esquerda, direita) cobrindo a faixa, como
    # a forma livre do detector marca uma moldura
    ys, xs = np.nonzero(faixa)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    esp = 60
    for (a, b, c, d) in ((x0 - 6, y0 - 6, x1 + 6, y0 + esp), (x0 - 6, y1 - esp, x1 + 6, y1 + 6),
                         (x0 - 6, y0 - 6, x0 + esp, y1 + 6), (x1 - esp, y0 - 6, x1 + 6, y1 + 6)):
        s.acrescentar(retangulo(a / largura, b / altura, c / largura, d / altura, tipo=GRAVURA))
    return s


# --- a moldura dourada vira desenho -----------------------------------------

def test_a_moldura_dourada_sai_como_desenho_em_um_bit():
    """Nem dourada nem preta chapada: contorno preto, miolo da faixa branco."""
    img, faixa = _moldura()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO,
                                             _gravura_so_na_moldura(faixa))

    assert mono is True, "sem foto, a pagina inteira tem de caber em 1 bit"
    assert saida.ndim == 2 and set(np.unique(saida)) <= {0, 255}

    # o meio da faixa (longe do contorno) sai branco: nao e preta chapada
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    assert miolo.any()
    preto_no_miolo = float((saida[miolo] == 0).mean())
    assert preto_no_miolo < 0.05, f"a faixa saiu preta chapada ({preto_no_miolo:.0%})"

    # e o contorno fino sai preto: o desenho nao se perde
    meia = 24
    y = 100 - meia            # a linha de fora, no alto da moldura
    linha = saida[y - 1:y + 2, 300:600]
    assert float((linha == 0).mean()) > 0.6, "o contorno da moldura sumiu"


def test_nos_outros_filtros_a_moldura_continua_dourada():
    """Melhorar e Magico pro: a moldura com a cor do original."""
    img, faixa = _moldura()
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    for filtro in (MELHORAR, MAGICO_PRO):
        saida, mono = aplicar_filtro_com_selecao(img.copy(), filtro,
                                                 _gravura_so_na_moldura(faixa))
        assert mono is False
        sat = cv2.cvtColor(saida, cv2.COLOR_BGR2HSV)[:, :, 1]
        assert float(np.median(sat[miolo])) > 80, f"{filtro}: a moldura perdeu o dourado"


# --- o titulo colorido dentro da gravura sai preto -------------------------

def _titulo(img, mascara, x, y, cor):
    """Um "titulo" de letras de traco fino (7 pontos): hastes e anilhas, sem
    as juntas grossas das fontes do OpenCV (que chegam a 21 pontos e nao
    parecem letra impressa)."""
    for i in range(6):
        cx = x + i * 90
        if i % 2:
            cv2.ellipse(img, (cx + 25, y + 45), (25, 45), 0, 0, 360, cor, 7)
            cv2.ellipse(mascara, (cx + 25, y + 45), (25, 45), 0, 0, 360, 255, 7)
        else:
            cv2.line(img, (cx + 25, y), (cx + 25, y + 90), cor, 7)
            cv2.line(mascara, (cx + 25, y), (cx + 25, y + 90), 255, 7)


def test_o_titulo_colorido_dentro_da_gravura_sai_preto():
    """O 'NOVEMBRE.' da Horas 26: azul no original, preto no Preto e branco.

    A zona e a faixa estreita do titulo, como o detector a marca junto da
    moldura (zona fina: nao e foto - ver FOTO_ESPESSURA_MINIMA)."""
    img = np.full((2400, 1800, 3), PAPEL, np.uint8)
    letra = np.zeros(img.shape[:2], np.uint8)
    _titulo(img, letra, 100, 210, (150, 80, 40))        # azul medio
    _titulo(img, letra, 300, 510, (50, 50, 200))        # vermelho
    miolo = cv2.erode(letra, np.ones((3, 3), np.uint8)) > 0

    s = Selecao()
    s.acrescentar(retangulo(0.03, 190 / 2400, 0.97, 320 / 2400, tipo=GRAVURA))
    s.acrescentar(retangulo(0.10, 490 / 2400, 0.60, 620 / 2400, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)

    assert mono is True
    assert float((saida[miolo] == 0).mean()) > 0.95, "o titulo colorido nao saiu preto"
    # e o papel em volta, branco
    assert float((saida[1300:1500, 50:1750] == 255).mean()) > 0.99


# --- a xilogravura: traco preto, papel branco, sem virar mancha -----------

def test_a_gravura_de_traco_vira_desenho_com_o_papel_branco():
    img = np.full((800, 600, 3), (196, 212, 226), np.uint8)
    for x in range(60, 540, 8):           # hachura vertical fina
        img[100:700, x:x + 3] = (70, 75, 85)
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)

    assert mono is True
    assert set(np.unique(saida)) <= {0, 255}
    faixa = saida[300:500, 60:540]
    preto = float((faixa == 0).mean())
    # 3 de cada 8 pontos sao traco: nem sumiu, nem virou mancha
    assert 0.25 < preto < 0.55, f"fracao de preto na hachura: {preto:.2f}"


def test_a_nota_quadrada_larga_sai_cheia():
    """Mancha de tinta preta mais larga que o elemento (nota do Graduale):
    nao pode sair oca, so com o contorno."""
    img = np.full((1200, 900, 3), (205, 215, 225), np.uint8)
    for x in range(100, 800, 120):
        img[500:560, x:x + 60] = (45, 45, 50)      # notas de 60 x 60, tinta
    s = Selecao()
    s.acrescentar(retangulo(0.02, 0.41, 0.98, 0.48, tipo=GRAVURA))   # faixa fina
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert mono is True
    assert float((saida[510:550, 110:150] == 0).mean()) > 0.95, "a nota saiu oca"


# --- a foto de tom continuo fica como estava (o Samuel ainda nao decidiu) ---

def test_foto_de_tom_continuo_fica_em_tons_e_a_moldura_vira_desenho():
    img, faixa = _moldura(altura=1200, largura=900)
    # uma "foto" lisa em degrade no miolo da moldura
    degrade = np.linspace(60, 200, 400).astype(np.uint8)
    img[400:800, 250:650] = np.dstack([degrade[None, :]] * 3).repeat(400, axis=0)

    s = _gravura_so_na_moldura(faixa)
    s.acrescentar(retangulo(250 / 900, 400 / 1200, 650 / 900, 800 / 1200, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)

    assert mono is False, "com foto a pagina nao cabe em 1 bit"
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)
    assert len(np.unique(cinza[450:750, 300:600])) > 30, "a foto perdeu o tom continuo"
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    assert set(np.unique(cinza[miolo])) <= {0, 255}, "a moldura tinha de sair em preto e branco"
    assert float((cinza[miolo] == 0).mean()) < 0.05


def test_pagina_em_cinza_com_gravura_nao_quebra():
    cinza = np.full((600, 400), 210, np.uint8)
    cinza[100:500:6, 50:350] = 60
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(cinza, PRETO_E_BRANCO, s)
    assert saida.shape[:2] == cinza.shape and mono is True


def test_sem_foto_o_preto_e_branco_nao_roda_o_melhorar(monkeypatch):
    """Regra 6 (velocidade): com moldura e titulo so (sem foto), o Preto e
    branco nao passa mais pelo Melhorar - era ~3 s por pagina a 300 DPI."""
    import core.filtros as F

    chamadas = []
    original = F.filtro_melhorar
    monkeypatch.setattr(F, "filtro_melhorar",
                        lambda *a, **k: chamadas.append(1) or original(*a, **k))
    img, faixa = _moldura()
    F.aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _gravura_so_na_moldura(faixa))
    assert not chamadas, "o Melhorar rodou no Preto e branco sem foto"
