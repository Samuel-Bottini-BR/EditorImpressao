"""Contas do core/filtros.py refeitas para a regra 6 (30/09/2026) dao o MESMO
resultado, ponto por ponto, que a versao de antes. Teste de maquina."""

import numpy as np
import pytest

from core import filtros


def _rng(semente=0):
    return np.random.default_rng(semente)


@pytest.mark.parametrize("forma", [(57, 43), (57, 43, 3), (31, 29, 4)])
def test_pintar_de_branco_igual_a_mascara(forma):
    rng = _rng(1)
    img = rng.integers(0, 256, forma, dtype=np.uint8)
    mascara = rng.random(forma[:2]) < 0.4
    esperado = img.copy()
    esperado[mascara] = 255
    obtido = img.copy()
    filtros._pintar_de_branco(obtido, mascara)
    assert np.array_equal(obtido, esperado)


def test_pintar_de_branco_em_fatia_usa_o_caminho_antigo():
    rng = _rng(2)
    grande = rng.integers(0, 256, (40, 80, 3), dtype=np.uint8)
    fatia = grande[:, ::2]                     # nao contigua: mexe na propria fatia
    mascara = rng.random(fatia.shape[:2]) < 0.5
    esperado = grande.copy()
    esperado[:, ::2][mascara] = 255
    filtros._pintar_de_branco(fatia, mascara)
    assert np.array_equal(grande, esperado)


def test_copiar_o_cinza_igual_a_mascara():
    rng = _rng(3)
    img = rng.integers(0, 256, (61, 47, 3), dtype=np.uint8)
    cinza = rng.integers(0, 256, (61, 47), dtype=np.uint8)
    mascara = rng.random((61, 47)) < 0.3
    esperado = img.copy()
    esperado[mascara] = cinza[mascara][:, None]
    obtido = img.copy()
    filtros._copiar_o_cinza(obtido, mascara, cinza)
    assert np.array_equal(obtido, esperado)


def _amarelado_antigo(img, fora_da_gravura=None):
    """tirar_o_amarelado_da_tinta como era antes de 30/09/2026."""
    import cv2

    saturacao = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1].astype(np.float32)
    guardar = np.clip(
        (saturacao - filtros.SATURACAO_DE_GRAO)
        / max(1.0, filtros.SATURACAO_DE_RUBRICA - filtros.SATURACAO_DE_GRAO), 0.0, 1.0)
    peso = 1.0 - guardar
    if fora_da_gravura is not None:
        peso = peso * np.clip(fora_da_gravura, 0.0, 1.0)
    if not peso.any():
        return img
    ycc = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float32)
    ycc[:, :, 1] = 128.0 + (ycc[:, :, 1] - 128.0) * (1.0 - peso)
    ycc[:, :, 2] = 128.0 + (ycc[:, :, 2] - 128.0) * (1.0 - peso)
    return cv2.cvtColor(np.clip(ycc, 0, 255).astype(np.uint8), cv2.COLOR_YCrCb2BGR)


@pytest.mark.parametrize("tipo", [None, np.float32, np.float64])
def test_tirar_o_amarelado_igual_ao_de_antes(tipo):
    rng = _rng(4)
    img = rng.integers(0, 256, (90, 70, 3), dtype=np.uint8)
    fora = None if tipo is None else rng.random((90, 70)).astype(tipo)
    assert np.array_equal(filtros.tirar_o_amarelado_da_tinta(img, fora),
                          _amarelado_antigo(img, fora))


def test_achatar_iluminacao_igual_ao_de_antes():
    rng = _rng(5)
    img = np.clip(rng.normal(190, 30, (300, 220, 3)), 0, 255).astype(np.uint8)
    novo = filtros._achatar_iluminacao(img, 200.0)
    # o caminho antigo: a conta com copias (forca-se o "else")
    import cv2

    fundo = filtros._estimar_fundo_cinza(filtros._para_cinza(img)).astype(np.float32)
    ganho = 200.0 / (fundo + 1.0)
    np.clip(ganho, filtros.GANHO_MIN, filtros.GANHO_MAX, out=ganho)
    razao = fundo / 200.0
    peso = np.clip((razao - filtros.PESO_RAZAO_MIN)
                   / (filtros.PESO_RAZAO_MAX - filtros.PESO_RAZAO_MIN), 0.0, 1.0)
    ganho = 1.0 + (ganho - 1.0) * peso
    antigo = np.clip(img.astype(np.float32) * ganho[:, :, None], 0, 255).astype(np.uint8)
    assert cv2.norm(novo, antigo, cv2.NORM_INF) == 0
    assert np.array_equal(novo, antigo)
