"""Os filtros lendo da selecao: cada area tratada do seu jeito."""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
)
from core.selecao import GRAVURA, LETRA, PAPEL, Selecao, retangulo


def pagina_de_teste(altura=400, largura=300):
    """Meia pagina de gravura em degrade, meia de texto sobre papel amarelado."""
    img = np.zeros((altura, largura, 3), np.uint8)
    # papel amarelado
    img[:, :] = (190, 220, 235)
    # gravura na metade de cima: degrade cinza, tom continuo
    for y in range(altura // 2):
        img[y, :] = (60 + y // 2, 70 + y // 2, 90 + y // 2)
    # texto na metade de baixo
    for y in range(altura // 2 + 20, altura - 20, 24):
        img[y:y + 8, 30:largura - 30] = (25, 25, 25)
    return img


@pytest.fixture
def img():
    return pagina_de_teste()


# --- sem selecao nada muda --------------------------------------------------

@pytest.mark.parametrize("filtro", [ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_selecao_vazia_da_o_resultado_de_sempre(img, filtro):
    """Todo projeto antigo e toda pagina nao marcada caem aqui."""
    antes, mono_antes = aplicar_filtro(img.copy(), filtro)
    depois, mono_depois = aplicar_filtro_com_selecao(img.copy(), filtro, Selecao())
    assert mono_antes == mono_depois
    assert np.array_equal(antes, depois)


def test_selecao_none_tambem_e_aceita(img):
    antes, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    depois, _ = aplicar_filtro_com_selecao(img.copy(), MAGICO_PRO, None)
    assert np.array_equal(antes, depois)


# --- a gravura nao pode ser binarizada --------------------------------------

def test_preto_e_branco_preserva_tom_continuo_na_gravura(img):
    """Binarizar uma gravura de meio-tom e joga-la fora."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.5, tipo=GRAVURA))

    saida, mono = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, s)

    # a pagina deixa de caber em 1 bit, porque tem gravura em tom continuo
    assert mono is False

    metade = saida.shape[0] // 2
    gravura = saida[: metade - 10]
    tons = np.unique(cv2.cvtColor(gravura, cv2.COLOR_BGR2GRAY))
    assert len(tons) > 8, "a gravura foi binarizada"


def test_preto_e_branco_sem_gravura_continua_em_um_bit(img):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.5, 1.0, 1.0, tipo=LETRA))
    _saida, mono = aplicar_filtro_com_selecao(img, PRETO_E_BRANCO, s)
    assert mono is True


# --- o papel vai a branco ---------------------------------------------------

@pytest.mark.parametrize("filtro", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_papel_marcado_fica_branco(img, filtro):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.3, 0.3, tipo=PAPEL))

    saida, _ = aplicar_filtro_com_selecao(img, filtro, s)
    canto = saida[5:100, 5:80]
    assert canto.min() >= 250, "o papel marcado nao ficou branco"


def test_o_que_esta_fora_do_papel_nao_e_afetado(img):
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.3, 0.3, tipo=PAPEL))

    com, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    sem, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    # longe do canto marcado, o resultado e o mesmo
    assert np.array_equal(com[250:, 150:], sem[250:, 150:])


# --- a letra recebe so nitidez ----------------------------------------------

def test_letra_marcada_nao_recebe_realce_de_fundo(img):
    """Realce de fundo na letra e o que fabricava grao no papel em volta."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.5, 1.0, 1.0, tipo=LETRA))

    com, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    sem, _ = aplicar_filtro(img.copy(), MAGICO_PRO)
    metade = img.shape[0] // 2
    assert not np.array_equal(com[metade + 30:], sem[metade + 30:])


# --- a ordem e a mistura ----------------------------------------------------

def test_subtrair_devolve_a_area_ao_tratamento_comum(img):
    """O buraco tem de voltar a valer o tratamento comum, nao o do papel.

    A marcacao cobre a METADE DE CIMA, que na pagina de teste e a gravura
    escura: so ali a diferenca entre "virou branco" e "nao virou" aparece.
    """
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.5, tipo=PAPEL))
    s.acrescentar(retangulo(0.3, 0.1, 0.7, 0.4, tipo=PAPEL, operacao="subtrair"))

    saida, _ = aplicar_filtro_com_selecao(img, MELHORAR, s)
    assert saida[10, 10].min() >= 250        # fora do buraco: virou branco
    assert saida[100, 150].min() < 250       # dentro do buraco: continua gravura


def test_borda_suave_nao_deixa_degrau(img):
    """Corte seco entre area tratada e nao tratada aparece na impressao.

    A travessia tem de ser uma rampa com varios degraus intermediarios, e nao
    um salto de uma vez. Medido sobre a gravura, que e escura: sobre o papel
    claro os dois lados ja sao quase brancos e nao daria para ver diferenca.
    """
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 0.45, tipo=PAPEL, suavidade=0.08))

    saida, _ = aplicar_filtro_com_selecao(img, MELHORAR, s)
    linha = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)[100, :].astype(int)

    esquerda, direita = linha[20], linha[280]
    assert esquerda > direita + 40, "os dois lados deveriam ser bem diferentes"

    # na travessia ha varios valores entre um lado e o outro
    travessia = linha[110:190]
    intermediarios = ((travessia > direita + 10) & (travessia < esquerda - 10)).sum()
    assert intermediarios >= 10, "a borda saiu como degrau, nao como rampa"


# --- robustez ---------------------------------------------------------------

def test_pagina_em_cinza_tambem_funciona():
    cinza = np.full((200, 150), 200, np.uint8)
    cinza[80:120, 20:130] = 30
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.3, tipo=GRAVURA))
    saida, _ = aplicar_filtro_com_selecao(cinza, PRETO_E_BRANCO, s)
    assert saida.shape[:2] == cinza.shape[:2]


def test_selecao_so_de_tipo_ausente_nao_quebra(img):
    """Marcar so 'fora' nao muda o filtro, mas nao pode derrubar nada."""
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.2, 0.2, tipo="fora"))
    saida, _ = aplicar_filtro_com_selecao(img, MAGICO_PRO, s)
    assert saida.shape == img.shape
