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


def test_esqueleto_em_partes_igual_ao_skeletonize(monkeypatch):
    """Pecas soltas, pecas que so se tocam na diagonal, uma faixa alta na
    beirada e uma peca larga: o esqueleto em partes e o do skeletonize."""
    import cv2
    from skimage.morphology import skeletonize

    monkeypatch.setattr(filtros, "PONTOS_PARA_DIVIDIR_O_ESQUELETO", 1000)
    rng = _rng(6)
    img = np.zeros((400, 300), np.uint8)
    for _ in range(120):                           # "letras" grossas e finas
        x, y = int(rng.integers(5, 290)), int(rng.integers(5, 390))
        cv2.ellipse(img, (x, y), (int(rng.integers(2, 9)), int(rng.integers(2, 9))),
                    float(rng.integers(0, 180)), 0, 360, 255, int(rng.integers(1, 4)))
    img[:, :12] = 255                              # faixa escura da beirada (alta)
    img[200:215, 30:290] = 255                     # fio largo
    img[50, 50] = img[51, 51] = img[52, 52] = 255  # pecas ligadas so na diagonal
    tinta = img > 0
    assert np.array_equal(filtros._esqueleto(tinta), skeletonize(tinta))


def test_tapar_buracos_igual_ao_scipy():
    """core.detectar_regioes.tapar_buracos = scipy binary_fill_holes."""
    from scipy.ndimage import binary_fill_holes

    from core.detectar_regioes import tapar_buracos

    rng = _rng(7)
    for forma, p in [((1, 1), .5), ((1, 7), .5), ((5, 1), .5), ((3, 3), .7),
                     ((60, 80), .3), ((60, 80), .6), ((60, 80), .8), ((200, 150), .55)]:
        for _ in range(15):
            m = rng.random(forma) < p
            assert np.array_equal(tapar_buracos(m), binary_fill_holes(m)), forma
    for valor in (False, True):
        m = np.full((20, 30), valor)
        assert np.array_equal(tapar_buracos(m), binary_fill_holes(m))


def test_neutralizar_o_papel_por_tabela_igual_ao_de_antes():
    """core.analise._neutralizar_o_papel (tabela) = a conta em float de antes."""
    import cv2

    from core import analise

    def antigo(img):
        cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        papel = cinza >= np.percentile(cinza, analise.PERCENTIL_DO_PAPEL)
        if papel.sum() < 100:
            return img
        medias = [float(img[:, :, c][papel].mean()) for c in range(3)]
        geral = sum(medias) / 3.0
        if geral < 1:
            return img
        saida = img.astype(np.float32)
        for canal in range(3):
            if medias[canal] >= 1:
                fator = geral / medias[canal]
                saida[:, :, canal] *= min(max(fator, 1 / analise.CORRECAO_MAXIMA),
                                          analise.CORRECAO_MAXIMA)
        return np.clip(saida, 0, 255).astype(np.uint8)

    rng = _rng(8)
    for amarelo in (0, 25, 60):
        img = np.clip(rng.normal(170, 50, (120, 90, 3)), 0, 255).astype(np.uint8)
        img[:, :, 0] = np.clip(img[:, :, 0].astype(int) - amarelo, 0, 255)  # papel amarelado
        assert np.array_equal(analise._neutralizar_o_papel(img), antigo(img))
