"""A mistura rapida (core.filtros._misturar_por_partes) da o MESMO resultado,
ponto por ponto, que a conta inteira de _misturar (regra 6, 30/09/2026).

Teste de maquina: nao e "parecido", e igual (np.array_equal)."""

import numpy as np
import pytest

from core import filtros


def _conta_inteira(base, tratada, peso):
    """A conta de _misturar como era antes do caminho rapido."""
    p = peso[:, :, None] if base.ndim == 3 else peso
    saida = base.astype(np.float32) * (1.0 - p) + tratada.astype(np.float32) * p
    return np.clip(saida, 0, 255).astype(base.dtype)


def _peso(rng, forma, tipo):
    """Peso como o da marcacao: quase tudo 0 ou 1, com uma faixa suave."""
    peso = np.zeros(forma, tipo)
    peso[forma[0] // 4: forma[0] // 2, :] = 1
    borda = rng.random(forma).astype(tipo)
    faixa = slice(forma[0] // 2, forma[0] // 2 + 7)
    peso[faixa, :] = borda[faixa, :]
    peso[rng.random(forma) < 0.01] = 0.5
    peso[0, 0] = 1.25          # fora de 0..1 (nao deveria vir, mas a conta aguenta)
    peso[0, 1] = -0.25
    return peso


@pytest.mark.parametrize("canais", [None, 3])
@pytest.mark.parametrize("tipo", [np.float32, np.float64])
def test_misturar_rapido_e_igual_a_conta_inteira(canais, tipo):
    rng = np.random.default_rng(7)
    forma = (61, 47) if canais is None else (61, 47, canais)
    base = rng.integers(0, 256, forma, dtype=np.uint8)
    tratada = rng.integers(0, 256, forma, dtype=np.uint8)
    peso = _peso(rng, forma[:2], tipo)
    esperado = _conta_inteira(base, tratada, peso)
    obtido = filtros._misturar(base, tratada, peso)
    assert obtido.dtype == esperado.dtype and obtido.shape == esperado.shape
    assert np.array_equal(obtido, esperado)


def test_misturar_rapido_com_branco_e_mascara_binaria():
    rng = np.random.default_rng(3)
    base = rng.integers(0, 256, (80, 90, 3), dtype=np.uint8)
    copia = base.copy()
    mascara = (rng.random((80, 90)) < 0.3).astype(np.float32)
    esperado = _conta_inteira(base, np.full_like(base, 255), mascara)
    assert np.array_equal(filtros._misturar(base, np.full_like(base, 255), mascara), esperado)
    assert np.array_equal(base, copia)          # nao mexe na entrada


def test_misturar_caso_fora_do_comum_usa_a_conta_inteira():
    rng = np.random.default_rng(5)
    base = rng.integers(0, 256, (20, 30, 3), dtype=np.uint8)
    tratada = rng.random((20, 30, 3)).astype(np.float32) * 300    # float, fora de 0..255
    peso = _peso(rng, (20, 30), np.float32)
    assert filtros._misturar_por_partes(base, tratada, peso) is None
    assert np.array_equal(filtros._misturar(base, tratada, peso),
                          _conta_inteira(base, tratada, peso))


def test_misturar_rapido_com_imagens_fatiadas():
    """Base e tratada que sao fatias (nao contiguas) da memoria."""
    rng = np.random.default_rng(9)
    grande = rng.integers(0, 256, (70, 120, 3), dtype=np.uint8)
    base = grande[:, ::2]
    tratada = rng.integers(0, 256, (70, 120, 3), dtype=np.uint8)[:, 1::2]
    peso = _peso(rng, base.shape[:2], np.float32)
    assert np.array_equal(filtros._misturar(base, tratada, peso),
                          _conta_inteira(base, tratada, peso))
    cinza = base[:, :, 1]          # fatia de fatia, com passo 6 entre pontos
    assert np.array_equal(filtros._misturar(cinza, tratada[:, :, 0], peso),
                          _conta_inteira(cinza, tratada[:, :, 0], peso))
