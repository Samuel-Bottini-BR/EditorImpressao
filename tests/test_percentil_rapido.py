"""O percentil pelo histograma (core.filtros._percentil) da o mesmo numero
que o np.percentile, ate o ultimo bit (regra 6, 30/09/2026). Teste de maquina."""

import numpy as np
import pytest

from core import filtros

QS = [0, 1, 2, 3, 5, 20, 33.3, 50, 80, 85, 90, 95, 97, 99, 99.9, 100]


@pytest.mark.parametrize("semente", range(6))
def test_percentil_igual_ao_numpy_em_imagens_aleatorias(semente):
    rng = np.random.default_rng(semente)
    for forma in [(1,), (2,), (3,), (7, 5), (100, 101), (333,), (257, 129)]:
        for tipo in ("uniforme", "papel", "constante"):
            if tipo == "uniforme":
                img = rng.integers(0, 256, forma, dtype=np.uint8)
            elif tipo == "papel":
                img = np.clip(rng.normal(200, 25, forma), 0, 255).astype(np.uint8)
            else:
                img = np.full(forma, rng.integers(0, 256), np.uint8)
            for q in QS:
                esperado = float(np.percentile(img, q))
                obtido = filtros._percentil(img, q)
                assert obtido == esperado, (forma, tipo, q, obtido, esperado)
                assert np.float64(obtido).tobytes() == np.float64(esperado).tobytes()


def test_percentil_em_fatia_com_passo_e_em_mascara():
    rng = np.random.default_rng(11)
    img = np.clip(rng.normal(180, 40, (401, 303)), 0, 255).astype(np.uint8)
    fatia = img[::4, ::4]
    assert filtros._percentil(fatia, 85) == float(np.percentile(fatia, 85))
    canal = np.dstack([img, img // 2, img // 3])[:, :, 1]     # coluna com passo 3
    assert filtros._percentil(canal, 90) == float(np.percentile(canal, 90))
    escolhidos = img[img > 120]
    for q in (20, 50, 80):
        assert filtros._percentil(escolhidos, q) == float(np.percentile(escolhidos, q))


def test_percentil_de_outro_tipo_usa_o_numpy():
    valores = np.linspace(0, 1, 1001, dtype=np.float32)
    assert filtros._percentil(valores, 37) == float(np.percentile(valores, 37))
    with pytest.raises(IndexError):
        filtros._percentil(np.zeros(0, np.uint8), 50)
