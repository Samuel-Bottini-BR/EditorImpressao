"""Misto, jeito de fabrica "Guardar a tinta forte": o desenho de traco claro
nao pode sumir (conserto de 06/10/2026, ramo misto-desenho-apagado).

O defeito (estudo relatorios/revisar-criterios-2026-10-06): fora das linhas
de texto e fora das gravuras achadas, so ficava o pedaco de tinta tao escuro
quanto a letra e maior que (altura da linha / 6)^2. Numa capitular gravada
que o detector de gravura nao reconhece (Palatino 76 e 67), a hachura e feita
de tracinhos claros e pequenos: ia toda a branco, e da letra S sobrava a
moldura. O Preto e branco puro guarda esses tracos. O Samuel: "o papel saia
branco, e o desenho tambem saia perfeito".

O conserto (core.misto._desenho_colado_a_tinta_forte): a tinta apagada que
esta AMONTOADA junto da tinta forte guardada (o desenho em volta da moldura
da capitular) volta, como no Preto e branco; a tinta clara SOLTA, longe da
tinta forte (a escrita do verso na margem), continua indo a branco.

Paginas desenhadas aqui; testes de maquina.
"""

from __future__ import annotations

import numpy as np

from core.misto import FORA_APAGAR, FORA_REDE, aplicar_misto
from core.selecao import Selecao

PAPEL_CREME = (200, 222, 232)       # BGR
ALTURA_LINHA = 20.0


def _texto(img, y0, y1, x0=100, x1=700, passo=16, cor=(30, 30, 30)):
    """Linhas de "letras": tracos de 4 x 12 pontos a cada `passo`."""
    for y in range(y0, y1, 40):
        for x in range(x0, x1, passo):
            img[y:y + 12, x:x + 4] = cor


def _capitular(img, x0, y0, lado=240):
    """Uma capitular gravada: a moldura quadrada escura (tao escura quanto a
    letra) e, dentro, hachura de tracinhos CLAROS e pequenos (6 x 2 pontos,
    cinza 120: mais claros que a letra e menores que o pedaco minimo da rede)."""
    img[y0:y0 + 4, x0:x0 + lado] = (30, 30, 30)
    img[y0 + lado - 4:y0 + lado, x0:x0 + lado] = (30, 30, 30)
    img[y0:y0 + lado, x0:x0 + 4] = (30, 30, 30)
    img[y0:y0 + lado, x0 + lado - 4:x0 + lado] = (30, 30, 30)
    for y in range(y0 + 8, y0 + lado - 8, 6):
        for x in range(y % 12 + x0 + 8, x0 + lado - 14, 10):
            img[y:y + 2, x:x + 6] = (120, 120, 120)
    return (slice(y0 + 10, y0 + lado - 10), slice(x0 + 10, x0 + lado - 10))


def _pagina():
    """Texto (dentro das linhas do leitor), uma capitular gravada fora das
    linhas e uma "escrita do verso" clara na margem de baixo, longe de tudo."""
    img = np.full((1000, 800, 3), PAPEL_CREME, np.uint8)
    _texto(img, 60, 140)
    miolo = _capitular(img, 100, 300)
    _texto(img, 800, 880, x0=150, x1=500, cor=(130, 140, 150))   # verso, claro
    linhas = np.zeros(img.shape[:2], bool)
    linhas[50:150, 90:710] = True
    return img, linhas, miolo


def _rodar(img, linhas, modo=FORA_REDE, medidas=None, altura_linha=ALTURA_LINHA):
    saida, _ = aplicar_misto(img.copy(), Selecao(), fora_do_texto=modo, linhas=linhas,
                             altura_linha=altura_linha, medidas=medidas)
    return saida


def test_a_pagina_de_teste_tem_o_defeito_no_preto_e_branco_puro():
    """O Preto e branco puro (Misto sem linhas) guarda a hachura e o verso:
    a pagina de teste reproduz o caso."""
    img, _linhas, miolo = _pagina()
    puro, _ = aplicar_misto(img.copy(), Selecao())
    assert float((puro[miolo] == 0).mean()) > 0.08, "a hachura nem vira tinta no Preto e branco"
    assert float((puro[800:880, 150:500] == 0).mean()) > 0.05, "o verso nem vira tinta"


def test_a_hachura_clara_da_capitular_fica():
    img, linhas, miolo = _pagina()
    puro, _ = aplicar_misto(img.copy(), Selecao())
    saida = _rodar(img, linhas)
    tinta_pura = puro[miolo] == 0
    guardada = (saida[miolo] == 0) & tinta_pura
    assert guardada.sum() >= 0.95 * tinta_pura.sum(), "a hachura clara da capitular sumiu"
    assert int(saida[300:304, 100:340].max()) == 0, "a moldura da capitular sumiu"


def test_a_escrita_clara_do_verso_continua_indo_a_branco():
    img, linhas, _miolo = _pagina()
    saida = _rodar(img, linhas)
    assert int(saida[790:890, 140:510].min()) == 255, "a escrita do verso voltou"


def test_o_texto_das_linhas_nao_muda():
    img, linhas, _miolo = _pagina()
    saida = _rodar(img, linhas)
    puro, _ = aplicar_misto(img.copy(), Selecao())
    assert np.array_equal(saida[linhas], puro[linhas])


def test_o_aviso_continua_medindo_so_a_tinta_forte():
    """O "Para revisar" (core.pipeline, forte_fora) nao muda com o conserto: a
    hachura que volta entra em guardada_fora e em desenho_fora, nao em
    forte_fora."""
    img, linhas, _miolo = _pagina()
    medidas: dict = {}
    _rodar(img, linhas, medidas=medidas)
    assert medidas["desenho_fora"] > 0
    assert medidas["guardada_fora"] == pytest_approx(medidas["forte_fora"] + medidas["desenho_fora"])
    so_texto: dict = {}
    _rodar(img, linhas, modo=FORA_APAGAR, medidas=so_texto)
    assert so_texto["forte_fora"] == pytest_approx(medidas["forte_fora"])
    assert so_texto["guardada_fora"] == 0.0 and so_texto["desenho_fora"] == 0.0


def test_so_o_texto_achado_continua_apagando_a_capitular():
    """O conserto e so do jeito de fabrica: no "So o texto achado" tudo o
    que esta fora das linhas vai a branco, como antes."""
    img, linhas, miolo = _pagina()
    saida = _rodar(img, linhas, modo=FORA_APAGAR)
    assert int(saida[miolo].min()) == 255


def test_numero_de_pagina_com_um_pontinho_claro_nao_muda():
    """Pagina sem desenho: um numero de pagina escuro fora das linhas (do
    tamanho de uma letra) e um pontinho claro encostado nele (sujeira). O
    pontinho continua indo a branco - o amontoado e pequeno demais para ser
    desenho (menos de DESENHO_MINIMO * altura da linha^2 de tinta)."""
    img = np.full((600, 600, 3), PAPEL_CREME, np.uint8)
    _texto(img, 60, 140, x1=500)
    img[400:416, 300:304] = (30, 30, 30)            # o "1" do numero da pagina
    img[400:403, 300:310] = (30, 30, 30)
    img[418:421, 306:309] = (120, 120, 120)          # o pontinho claro ao lado
    linhas = np.zeros(img.shape[:2], bool)
    linhas[50:150, 90:510] = True
    puro, _ = aplicar_misto(img.copy(), Selecao())
    assert int(puro[418:421, 306:309].min()) == 0, "o pontinho nem vira tinta"
    hoje = _rodar(img, linhas, altura_linha=40.0)
    assert int(hoje[400:416, 300:304].max()) == 0, "o numero sumiu"
    assert int(hoje[418:421, 306:309].min()) == 255, "o pontinho de sujeira voltou"


def test_mancha_clara_colada_numa_pauta_grande_continua_indo_a_branco():
    """Graduale 223: a mancha do verso encostada nas linhas da pauta. A
    pauta e enorme e a mancha e uma fatia minima dela (menos de
    FATIA_APAGADA): nao e desenho comido, a mancha continua indo a branco."""
    img = np.full((700, 800, 3), PAPEL_CREME, np.uint8)
    _texto(img, 60, 140)
    for y in range(300, 380, 16):                    # a pauta: 5 linhas escuras
        img[y:y + 4, 100:700] = (30, 30, 30)
    img[320:328, 300:306] = (130, 140, 150)          # a mancha clara encostada
    linhas = np.zeros(img.shape[:2], bool)
    linhas[50:150, 90:710] = True
    puro, _ = aplicar_misto(img.copy(), Selecao())
    mancha = (slice(321, 328), slice(300, 306))
    assert int(puro[mancha].min()) == 0, "a mancha nem vira tinta"
    saida = _rodar(img, linhas)
    assert float((saida[300:304, 100:700] == 0).mean()) > 0.9, "a pauta sumiu"
    assert not ((puro[mancha] == 0) & (saida[mancha] == 0)).any(), "a mancha do verso voltou"


def test_sombra_da_lombada_na_borda_nao_volta():
    """Horas 11 e 14: a sombra da lombada e uma faixa escura fina encostada na
    borda da imagem, com graozinhos claros colados nela. Nao e desenho comido:
    os graozinhos continuam indo a branco (a beirada e assunto do corte)."""
    img = np.full((1000, 800, 3), PAPEL_CREME, np.uint8)
    _texto(img, 60, 140)
    img[100:900, 0:4] = (30, 30, 30)                 # a sombra escura, na borda
    for y in range(110, 890, 9):                     # graozinhos claros colados
        img[y:y + 5, 5:11] = (120, 120, 120)
    linhas = np.zeros(img.shape[:2], bool)
    linhas[50:150, 90:710] = True
    puro, _ = aplicar_misto(img.copy(), Selecao())
    graos = (slice(160, 880), slice(5, 11))
    assert (puro[graos] == 0).mean() > 0.3, "os graozinhos nem viram tinta"
    medidas: dict = {}
    saida = _rodar(img, linhas, medidas=medidas, altura_linha=40.0)
    assert medidas["desenho_fora"] == 0.0
    assert not ((puro[graos] == 0) & (saida[graos] == 0) & (img[graos][:, :, 0] > 100)).any()


def test_scan_sem_tons_de_cinza_nao_muda():
    """Cursus p. 3: o scan ja veio em preto e branco (letra preta pura). Ali o
    escuro nao separa desenho de sujeira granulada; o conserto nao vale e a
    pagina sai como antes (os graozinhos pequenos vao a branco)."""
    img = np.full((1000, 800, 3), 255, np.uint8)
    _texto(img, 60, 140, cor=(0, 0, 0))
    _capitular(img, 100, 300)
    img[(img[:, :, 0] < 255)] = 0                    # tudo preto puro
    linhas = np.zeros(img.shape[:2], bool)
    linhas[50:150, 90:710] = True
    medidas: dict = {}
    # altura de linha 40: os tracinhos da hachura (12 pontos) ficam menores
    # que o pedaco minimo da rede, como os graozinhos do Cursus
    _rodar(img, linhas, medidas=medidas, altura_linha=40.0)
    assert medidas["tinta_fora"] > medidas["forte_fora"], "a pagina de teste mudou"
    assert medidas["desenho_fora"] == 0.0
    assert medidas["guardada_fora"] == pytest_approx(medidas["forte_fora"])


def pytest_approx(valor):
    import pytest

    return pytest.approx(valor, abs=1e-9)
