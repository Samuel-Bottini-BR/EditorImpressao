"""Problema 5 do plano: mais de um jeito de binarizar (Sauvola/Otsu/Wolf),
e a escolha automática por página."""

from __future__ import annotations

import numpy as np
import pytest

from core.filtros import (
    ALGORITMO_OTSU,
    ALGORITMO_SAUVOLA,
    ALGORITMO_WOLF,
    ALGORITMOS_PB,
    binarizar,
    escolher_algoritmo_automatico,
    filtro_preto_e_branco,
)


def pagina_com_traco(espessura_px: int, altura=300, largura=400) -> np.ndarray:
    """Papel claro com linhas de "letra" de uma espessura controlada."""
    img = np.full((altura, largura, 3), 235, np.uint8)
    for y in range(20, altura - 20, max(espessura_px * 4, 20)):
        img[y:y + espessura_px, 30:largura - 30] = (20, 20, 20)
    return img


@pytest.fixture
def cinza_traco_fino():
    from core.filtros import _cinza_para_binarizar

    return _cinza_para_binarizar(pagina_com_traco(espessura_px=2))


@pytest.fixture
def cinza_traco_grosso():
    from core.filtros import _cinza_para_binarizar

    return _cinza_para_binarizar(pagina_com_traco(espessura_px=18))


def test_os_tres_algoritmos_existem():
    assert set(ALGORITMOS_PB) == {ALGORITMO_SAUVOLA, ALGORITMO_OTSU, ALGORITMO_WOLF}


def test_binarizar_com_otsu_da_imagem_binaria(cinza_traco_fino):
    saida = binarizar(cinza_traco_fino, algoritmo=ALGORITMO_OTSU)
    assert set(np.unique(saida)).issubset({0, 255})
    assert saida.shape == cinza_traco_fino.shape


def test_binarizar_com_wolf_da_imagem_binaria(cinza_traco_fino):
    saida = binarizar(cinza_traco_fino, janela=25, k=0.2, algoritmo=ALGORITMO_WOLF)
    assert set(np.unique(saida)).issubset({0, 255})
    assert saida.shape == cinza_traco_fino.shape


def test_binarizar_sauvola_continua_igual_de_antes(cinza_traco_fino):
    """Não pode ter mudado o comportamento padrão - algoritmo="sauvola" é
    literalmente o mesmo caminho de código de antes desta mudança."""
    saida = binarizar(cinza_traco_fino, janela=25, k=0.2)
    assert saida.dtype == np.uint8
    assert set(np.unique(saida)).issubset({0, 255})


def test_escolhe_otsu_para_traco_grosso(cinza_traco_grosso):
    assert escolher_algoritmo_automatico(cinza_traco_grosso) == ALGORITMO_OTSU


def test_escolhe_sauvola_para_traco_fino(cinza_traco_fino):
    assert escolher_algoritmo_automatico(cinza_traco_fino) == ALGORITMO_SAUVOLA


def test_escolhe_sauvola_para_pagina_em_branco():
    from core.filtros import _cinza_para_binarizar

    branco = _cinza_para_binarizar(np.full((300, 400, 3), 250, np.uint8))
    assert escolher_algoritmo_automatico(branco) == ALGORITMO_SAUVOLA


def test_filtro_preto_e_branco_auto_nao_quebra():
    saida = filtro_preto_e_branco(pagina_com_traco(espessura_px=18), algoritmo="auto")
    assert set(np.unique(saida)).issubset({0, 255})


def test_filtro_preto_e_branco_aceita_algoritmo_forcado():
    saida = filtro_preto_e_branco(pagina_com_traco(espessura_px=2),
                                   algoritmo=ALGORITMO_WOLF)
    assert set(np.unique(saida)).issubset({0, 255})


def test_filtro_preto_e_branco_sem_algoritmo_continua_automatico():
    """Chamar sem passar `algoritmo` (código antigo, ou testes antigos) tem
    que continuar funcionando - "auto" é o padrão do parâmetro."""
    saida = filtro_preto_e_branco(pagina_com_traco(espessura_px=6))
    assert set(np.unique(saida)).issubset({0, 255})
