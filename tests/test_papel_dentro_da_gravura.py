"""Dentro da gravura: o papel vai a branco, a pintura e a foto ficam.

Bug de 28/09/2026 (Lista de bugs do plano): quadradinhos brancos na roupa do
anjo (Escola de Jesus, p. 35). A limpeza do papel feita para pagina de texto
rodava tambem dentro da gravura e tomava o pano quase branco por papel; como a
cor do JPEG vem em quadrados de 16x16 pontos, uns quadrados passavam e outros
nao. A mesma limpeza lavava a branco a foto da estatua do Opus Majus 20.

Regra do resultado da Fase 1 (Samuel, 28/09): todo o papel totalmente branco,
inclusive o papel dentro da gravura (o fundo do retrato do Palatino 5); so
pintura de verdade mantem a cor; sem quadradinhos.

As tres paginas daqui sao sinteticas, cada uma imitando um dos casos reais:
  - o pano do anjo: pintura de tom continuo, com um pano claro e creme;
  - o retrato do Palatino 5: xilogravura (traco sobre papel), com o papel de
    dentro mais escuro e mais amarelado que o da margem;
  - a grade do JPEG: a cor em quadrados de 16x16, nos dois casos acima.
Os tres filtros que tratam a gravura (Magico pro, Melhorar e Preto e branco)
passam pelo mesmo caminho, _limpar_cada_gravura, e sao testados os tres.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import MAGICO_PRO, MELHORAR, PRETO_E_BRANCO, aplicar_filtro_com_selecao
from core.selecao import GRAVURA, Selecao, retangulo

FILTROS_DA_GRAVURA = [MAGICO_PRO, MELHORAR, PRETO_E_BRANCO]


def _cor(h: int, s: int, v: int) -> tuple[int, int, int]:
    """BGR a partir de HSV na escala do OpenCV (matiz 0..179)."""
    bgr = cv2.cvtColor(np.uint8([[[h, s, v]]]), cv2.COLOR_HSV2BGR)[0, 0]
    return tuple(int(x) for x in bgr)


def _gravura(img: np.ndarray, x0: int, y0: int, x1: int, y1: int) -> Selecao:
    """Selecao com um retangulo de gravura, em pontos da imagem."""
    alt, larg = img.shape[:2]
    selecao = Selecao()
    selecao.acrescentar(retangulo(x0 / larg, y0 / alt, x1 / larg, y1 / alt, tipo=GRAVURA))
    return selecao


def _filtrar(img: np.ndarray, filtro: str, selecao: Selecao) -> np.ndarray:
    saida, _mono = aplicar_filtro_com_selecao(img.copy(), filtro, selecao)
    return saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)


def _luz(img: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)[:, :, 0].astype(np.float32)


# --- a pintura com o pano do anjo -------------------------------------------

def _pagina_com_pintura(quadrados_de_jpeg: bool = False):
    """Texto no pe (a limpeza do papel da pagina liga) e, no alto, uma pintura:
    folhagem escura salpicada - muitos pedacos, como a pintura do anjo, que tem
    857 - e no meio um pano quase branco, creme, com dobras suaves.

    Com quadrados_de_jpeg, a cor do pano muda de quadrado em quadrado de 16x16,
    uns dentro e outros fora da faixa de "cor de papel" antiga (saturacao 60),
    que e o que fazia os quadradinhos na roupa do anjo.
    """
    rng = np.random.default_rng(3)
    img = np.full((900, 700, 3), (205, 228, 245), np.uint8)   # papel ambar
    for y in range(560, 870, 18):                             # o texto
        for x in range(30, 670, 12):
            img[y:y + 6, x:x + 6] = 30

    img[30:520, 30:670] = _cor(40, 120, 120)                  # fundo da pintura
    for y in range(34, 512, 11):
        for x in range(34, 662, 11):
            if rng.random() < 0.8:
                img[y:y + 5, x:x + 5] = _cor(45, 140, 45)     # folhagem

    yy, xx = np.mgrid[0:900, 0:700]
    pano = ((xx - 350) / 170) ** 2 + ((yy - 275) / 210) ** 2 <= 1
    hsv = np.zeros((900, 700, 3), np.uint8)
    hsv[..., 0] = 15
    hsv[..., 1] = 35
    if quadrados_de_jpeg:
        hsv[..., 1] = np.where(((yy // 16) + (xx // 16)) % 2 == 0, 50, 70)
    hsv[..., 2] = np.clip(232 + 16 * np.sin(xx / 23.0), 0, 255).astype(np.uint8)
    img[pano] = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[pano]
    return img, pano, _gravura(img, 25, 25, 675, 525)


@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_pano_quase_branco_com_sombreado_dentro_da_gravura_mantem_a_cor(filtro):
    """A roupa do anjo: tom claro de pintura nao e papel."""
    img, pano, selecao = _pagina_com_pintura()
    saida = _filtrar(img, filtro, selecao)

    chapado = float((saida[pano].min(axis=1) >= 254).mean())
    assert chapado < 0.10, f"o pano virou branco chapado em {chapado:.0%} dele"

    luz = _luz(saida)[pano]
    dobras = float(np.percentile(luz, 90) - np.percentile(luz, 10))
    assert dobras >= 12, f"as dobras do pano sumiram (sobrou {dobras:.0f} tons)"


# --- a xilogravura com o papel escurecido ------------------------------------

def _xilogravura(quadrados_de_jpeg: bool = False):
    """Folha inteira marcada como gravura, como o Palatino 5: letras no alto e
    um retrato oval de traco. Dentro do oval o papel e mais escuro e mais
    amarelado que o da margem (o do Palatino 5 chega a saturacao 100, e a trava
    antiga de "cor de papel" parava em 60); a hachura cobre o oval, menos um
    "rosto" liso no meio, que tambem e papel.
    """
    alt, larg = 900, 700
    img = np.full((alt, larg, 3), _cor(21, 55, 222), np.uint8)   # papel da margem
    for y in range(30, 300, 18):
        for x in range(30, larg - 30, 12):
            img[y:y + 6, x:x + 6] = 30

    yy, xx = np.mgrid[0:alt, 0:larg]
    elipse = ((xx - 350) / 300) ** 2 + ((yy - 600) / 270) ** 2
    oval = elipse <= 1
    tostado = np.empty((alt, larg, 3), np.uint8)
    tostado[:] = _cor(21, 95, 200)
    if quadrados_de_jpeg:
        xadrez = ((yy // 16) + (xx // 16)) % 2 == 0
        tostado[xadrez] = _cor(21, 85, 200)
        tostado[~xadrez] = _cor(21, 105, 200)
    img[oval] = tostado[oval]

    rosto = ((xx - 350) / 120) ** 2 + ((yy - 560) / 110) ** 2 <= 1
    hachura = oval & (((xx + yy) % 10) < 3) & ~rosto
    img[hachura] = (35, 45, 55)
    contorno = np.abs(elipse - 1) < 0.02
    img[contorno] = (30, 30, 30)

    distancia = cv2.distanceTransform((~(hachura | contorno)).astype(np.uint8),
                                      cv2.DIST_L2, 3)
    papel_do_oval = oval & ~hachura & ~contorno & (distancia >= 3)
    return img, papel_do_oval, hachura, rosto, _gravura(img, 0, 0, larg, alt)


@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_papel_dentro_da_gravura_vai_a_branco(filtro):
    """O fundo do retrato do Palatino 5: papel entre os tracos vai a branco,
    e o traco continua preto."""
    img, papel, hachura, rosto, selecao = _xilogravura()
    saida = _filtrar(img, filtro, selecao)

    branco = float((saida[papel].min(axis=1) >= 250).mean())
    assert branco >= 0.95, f"so {branco:.0%} do papel do retrato ficou branco"

    branco_rosto = float((saida[papel & rosto].min(axis=1) >= 250).mean())
    assert branco_rosto >= 0.95, f"so {branco_rosto:.0%} do rosto (papel liso) ficou branco"

    assert float(saida[hachura].mean()) < 90, "a hachura clareou junto com o papel"


# --- a grade de 16 pontos do JPEG --------------------------------------------

def _degrau_na_grade(luz: np.ndarray, onde: np.ndarray) -> float:
    """Quanto a luz salta MAIS nas divisas da grade de 16 do que fora delas.

    Mede, nas colunas e linhas que caem na divisa entre dois quadrados de 16x16,
    o salto medio de luz de um ponto para o vizinho, e desconta o salto medio
    nas outras colunas e linhas (o sombreado de verdade). Zero quer dizer que a
    grade nao aparece.
    """
    dx = np.abs(np.diff(luz, axis=1))
    dy = np.abs(np.diff(luz, axis=0))
    ox = onde[:, 1:] & onde[:, :-1]
    oy = onde[1:, :] & onde[:-1, :]
    divisa_x = np.zeros_like(ox)
    divisa_x[:, 15::16] = True
    divisa_y = np.zeros_like(oy)
    divisa_y[15::16, :] = True
    na_divisa = np.concatenate([dx[ox & divisa_x], dy[oy & divisa_y]])
    fora = np.concatenate([dx[ox & ~divisa_x], dy[oy & ~divisa_y]])
    return float(na_divisa.mean() - fora.mean())


@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_sem_degraus_na_grade_de_16_pontos_no_pano(filtro):
    """A roupa do anjo sem quadradinhos: a grade do JPEG nao pode virar
    degrau de claro e escuro no resultado."""
    img, pano, selecao = _pagina_com_pintura(quadrados_de_jpeg=True)
    saida = _filtrar(img, filtro, selecao)

    miolo = cv2.erode(pano.astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    antes = _degrau_na_grade(_luz(img), miolo)
    depois = _degrau_na_grade(_luz(saida), miolo)
    # A entrada ja tem um degrauzinho (a cor muda de quadrado em quadrado, e a
    # luz um pouco junto), e a curva do Melhorar estica o contraste: medido,
    # 6,6 viram 8,0. O defeito era outro tamanho: com os quadradinhos, 22,7.
    assert depois <= antes * 1.5 + 1.0, (
        f"a grade de 16 pontos apareceu no pano: salto de {depois:.1f} tons "
        f"nas divisas (no original, {antes:.1f})")


@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_sem_degraus_na_grade_de_16_pontos_no_papel(filtro):
    """O papel do retrato com a cor em quadrados de 16: vai a branco inteiro,
    sem xadrez."""
    img, papel, _hachura, rosto, selecao = _xilogravura(quadrados_de_jpeg=True)
    saida = _filtrar(img, filtro, selecao)

    branco = float((saida[papel].min(axis=1) >= 250).mean())
    assert branco >= 0.95, f"so {branco:.0%} do papel quadriculado ficou branco"

    miolo = cv2.erode((papel & rosto).astype(np.uint8), np.ones((9, 9), np.uint8)) > 0
    assert _degrau_na_grade(_luz(saida), miolo) <= 1.0, "o xadrez do JPEG aparece no rosto"
