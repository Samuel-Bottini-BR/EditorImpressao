"""Problema 5.4 do plano: alerta "esta página pode não ter processado bem",
comparando o resultado do Preto e branco com o original."""

from __future__ import annotations

import numpy as np

from core.analise import (
    APAGADA_DEMAIS,
    ESCURA_DEMAIS,
    avaliar_preto_e_branco,
)


def pagina_com_texto_normal() -> np.ndarray:
    """Papel claro com bastante texto - tinta normal, nem escassa nem excessiva."""
    img = np.full((300, 400, 3), 235, np.uint8)
    for y in range(20, 280, 14):
        img[y:y + 6, 30:370] = (20, 20, 20)
    return img


def test_resultado_parecido_com_o_esperado_nao_gera_alerta():
    original = pagina_com_texto_normal()
    cinza = original[:, :, 0]
    resultado = np.where(cinza < 128, 0, 255).astype(np.uint8)
    assert avaliar_preto_e_branco(original, resultado) is None


def test_resultado_todo_preto_gera_escura_demais():
    original = pagina_com_texto_normal()
    resultado = np.zeros((300, 400), np.uint8)  # tudo preto - mancha virou tinta
    assert avaliar_preto_e_branco(original, resultado) == ESCURA_DEMAIS


def test_resultado_quase_sem_tinta_gera_apagada_demais():
    original = pagina_com_texto_normal()
    resultado = np.full((300, 400), 255, np.uint8)  # texto sumiu inteiro
    assert avaliar_preto_e_branco(original, resultado) == APAGADA_DEMAIS


def test_pagina_em_branco_nao_gera_apagada_demais():
    """Uma capa em branco de verdade não tem tinta nem no original - não é
    "apagou", é "não tinha nada mesmo"."""
    original = np.full((300, 400, 3), 250, np.uint8)
    resultado = np.full((300, 400), 255, np.uint8)
    assert avaliar_preto_e_branco(original, resultado) is None


def test_sem_imagem_nao_quebra():
    assert avaliar_preto_e_branco(None, None) is None
