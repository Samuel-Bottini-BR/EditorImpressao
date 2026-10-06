"""O cálculo do "Ajustar o pedaço à figura" e a medida do aviso (core/ajustar_pedaco.py).

Pedido do Samuel (conferencia 13, S3): "(b) e (c) juntas - Mas caso ele nao
queira mudar, fica do jeito que esta." (b) = um aviso na aba Marcar quando um
pedaco com outro filtro pega muito papel em volta da figura; (c) = um botao
que encolhe o retangulo ate a figura. Os dois so sugerem.

O que se cobra (teste de maquina):
    - figura sintetica com folga de papel em volta -> retangulo justo (com a
      margenzinha de seguranca), nunca menor que a figura;
    - figura que nao e retangulo (oval) nao e cortada;
    - pontinhos de sujeira no papel nao seguram o ajuste;
    - retangulo so de papel -> nada a ajustar;
    - o retangulo nunca cresce;
    - a medida do aviso: a fracao do retangulo que e papel liso na borda, e o
      "muito" (PAPEL_DEMAIS) - folga larga avisa, retangulo justo nao;
    - so os retangulos com OUTRO filtro sao ajustados; o resto da marcacao
      fica igual, na mesma ordem.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.ajustar_pedaco import (
    MARGEM,
    PAPEL_DEMAIS,
    ajustar_os_pedacos,
    caixa_justa,
    medir_folga,
    pedacos_com_outro_filtro,
)
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO
from core.selecao import GRAVURA, LETRA, MAO, RETANGULO, SUBTRAIR, Regiao, Selecao

ALTURA, LARGURA = 600, 400
PAPEL = (200, 225, 238)                     # creme (BGR)
FIGURA = (100, 200, 300, 480)               # x0, y0, x1, y1 em pontos


def _pagina(oval: bool = False, sujeira: bool = False) -> np.ndarray:
    """Papel creme com um pouco de grao, texto em cima, e uma figura colorida."""
    rng = np.random.default_rng(7)
    img = np.empty((ALTURA, LARGURA, 3), np.uint8)
    img[:] = PAPEL
    img = np.clip(img.astype(np.int16) + rng.integers(-4, 5, img.shape), 0, 255).astype(np.uint8)
    for y in range(30, 150, 24):
        img[y:y + 8, 30:LARGURA - 30] = (40, 45, 60)
    x0, y0, x1, y1 = FIGURA
    if oval:
        cv2.ellipse(img, ((x0 + x1) // 2, (y0 + y1) // 2), ((x1 - x0) // 2, (y1 - y0) // 2),
                    0, 0, 360, (90, 120, 160), -1)
    else:
        xs = np.linspace(0, 1, x1 - x0)[None, :]
        ys = np.linspace(0, 1, y1 - y0)[:, None]
        img[y0:y1, x0:x1, 0] = (60 + 120 * xs + 0 * ys).astype(np.uint8)
        img[y0:y1, x0:x1, 1] = (90 + 80 * ys + 0 * xs).astype(np.uint8)
        img[y0:y1, x0:x1, 2] = (150 + 60 * xs * ys).astype(np.uint8)
        img[y0:y0 + 30, x0:x1] = (225, 215, 205)         # ceu claro na beira de cima
    if sujeira:
        for (x, y) in ((70, 180), (330, 520), (80, 520), (320, 190)):
            img[y:y + 2, x:x + 2] = (60, 70, 90)          # pontinhos de 2 x 2
    return img


def _fracao(caixa_px) -> tuple[float, float, float, float]:
    x0, y0, x1, y1 = caixa_px
    return (x0 / LARGURA, y0 / ALTURA, x1 / LARGURA, y1 / ALTURA)


FOLGADO = _fracao((60, 170, 340, 540))     # 40 px de papel dos lados, 30/60 em cima/embaixo
JUSTO = _fracao((99, 199, 301, 481))


def _em_pontos(caixa) -> tuple[int, int, int, int]:
    return (int(round(caixa[0] * LARGURA)), int(round(caixa[1] * ALTURA)),
            int(round(caixa[2] * LARGURA)), int(round(caixa[3] * ALTURA)))


def test_encolhe_ate_a_figura():
    img = _pagina()
    justa = caixa_justa(img, FOLGADO)
    assert justa is not None
    x0, y0, x1, y1 = _em_pontos(justa)
    fx0, fy0, fx1, fy1 = FIGURA
    folga = int(np.ceil(MARGEM * min(ALTURA, LARGURA))) + 2
    # nunca corta a figura...
    assert x0 <= fx0 and y0 <= fy0 and x1 >= fx1 and y1 >= fy1, (justa, FIGURA)
    # ...e fica justo nela (so a margenzinha de seguranca)
    assert fx0 - x0 <= folga and fy0 - y0 <= folga
    assert x1 - fx1 <= folga and y1 - fy1 <= folga


def test_o_ceu_claro_na_beira_conta_como_figura():
    """A faixa clara no alto da figura (ceu) nao e papel: nao pode ser cortada."""
    img = _pagina()
    justa = caixa_justa(img, FOLGADO)
    assert _em_pontos(justa)[1] <= FIGURA[1]


def test_oval_nao_e_cortado():
    img = _pagina(oval=True)
    justa = caixa_justa(img, FOLGADO)
    x0, y0, x1, y1 = _em_pontos(justa)
    tinta = np.zeros((ALTURA, LARGURA), bool)
    fx0, fy0, fx1, fy1 = FIGURA
    cv2.ellipse(tinta.view(np.uint8), ((fx0 + fx1) // 2, (fy0 + fy1) // 2),
                ((fx1 - fx0) // 2, (fy1 - fy0) // 2), 0, 0, 360, 1, -1)
    ys, xs = np.nonzero(tinta)
    assert x0 <= xs.min() and y0 <= ys.min() and x1 >= xs.max() and y1 >= ys.max()


def test_pontinhos_de_sujeira_no_papel_nao_seguram_o_ajuste():
    limpo = caixa_justa(_pagina(), FOLGADO)
    sujo = caixa_justa(_pagina(sujeira=True), FOLGADO)
    assert np.allclose(limpo, sujo, atol=1.5 / LARGURA)


def test_retangulo_so_de_papel_nao_tem_o_que_ajustar():
    img = _pagina()
    assert caixa_justa(img, _fracao((310, 160, 390, 190))) is None


def test_nunca_cresce_e_figura_na_beira_fica():
    """A figura encosta no retangulo (o Kaique desenhou por dentro dela): o
    retangulo nao cresce nem anda."""
    img = _pagina()
    por_dentro = _fracao((120, 230, 280, 450))
    justa = caixa_justa(img, por_dentro)
    assert justa is not None
    assert np.allclose(justa, por_dentro, atol=1e-9)


def test_imagem_em_tons_de_cinza_tambem_serve():
    img = cv2.cvtColor(_pagina(), cv2.COLOR_BGR2GRAY)
    justa = caixa_justa(img, FOLGADO)
    assert justa is not None
    x0, y0, x1, y1 = _em_pontos(justa)
    assert x0 > 80 and x1 < 320                    # encolheu dos lados


def test_a_medida_do_aviso():
    img = _pagina()
    folga = medir_folga(img, FOLGADO)
    assert folga is not None
    area_fora = (340 - 60) * (540 - 170)
    area_fig = (300 - 100) * (480 - 200)
    assert folga.fracao_de_papel == pytest.approx(1 - area_fig / area_fora, abs=0.03)
    assert folga.muito
    justo = medir_folga(img, JUSTO)
    assert justo is not None and not justo.muito
    assert justo.fracao_de_papel < PAPEL_DEMAIS


def _selecao() -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[(0.05, 0.04), (0.95, 0.27)],
                         origem="automatico"))                                       # 0: maquina
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[FOLGADO[:2], FOLGADO[2:]],
                         origem=MAO, filtro=ORIGINAL))                               # 1: ajusta
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[FOLGADO[:2], FOLGADO[2:]],
                         origem=MAO, filtro=PRETO_E_BRANCO))                         # 2: mesmo da pagina
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[FOLGADO[:2], FOLGADO[2:]],
                         origem=MAO, filtro=MELHORAR, operacao=SUBTRAIR))            # 3: tirar
    return s


def test_so_os_pedacos_com_outro_filtro():
    """Retangulo de somar, com filtro proprio diferente do da pagina. A
    marcacao da maquina (sem filtro) e o "tirar" (subtrair) ficam de fora."""
    assert pedacos_com_outro_filtro(_selecao(), PRETO_E_BRANCO) == [1]
    # pagina em Original: o pedaco em Preto e branco e que tem outro filtro
    assert pedacos_com_outro_filtro(_selecao(), ORIGINAL) == [2]
    assert pedacos_com_outro_filtro(_selecao(), MELHORAR) == [1, 2]


def test_ajustar_os_pedacos_muda_so_o_que_deve():
    img = _pagina()
    antes = _selecao()
    depois, quantos = ajustar_os_pedacos(img, antes, PRETO_E_BRANCO)
    assert quantos == 1
    assert len(depois.regioes) == len(antes.regioes)
    for i in (0, 2, 3):
        assert depois.regioes[i] == antes.regioes[i]
    ajustado = depois.regioes[1]
    assert ajustado.filtro == ORIGINAL and ajustado.tipo == GRAVURA and ajustado.origem == MAO
    (x0, y0), (x1, y1) = ajustado.pontos
    assert x0 > FOLGADO[0] and y0 > FOLGADO[1] and x1 < FOLGADO[2] and y1 < FOLGADO[3]
    # a selecao de entrada nao foi mexida (o desfazer guarda a de antes)
    assert antes.regioes[1].pontos == [FOLGADO[:2], FOLGADO[2:]]


def test_ajustar_de_novo_nao_muda_mais_nada():
    img = _pagina()
    uma, _ = ajustar_os_pedacos(img, _selecao(), PRETO_E_BRANCO)
    duas, quantos = ajustar_os_pedacos(img, uma, PRETO_E_BRANCO)
    assert quantos == 0
    assert duas.regioes == uma.regioes


def test_a_legenda_solta_embaixo_fica_de_fora():
    """O retangulo folgado pegou a legenda (uma linha de texto bem menor que
    a figura, longe dela): o ajuste encolhe ate a figura, sem a legenda."""
    img = _pagina()
    img[520:528, 140:260] = (40, 45, 60)                 # a legenda, 40 px abaixo da figura
    justa = caixa_justa(img, FOLGADO)
    assert _em_pontos(justa)[3] < 520


def test_dois_desenhos_lado_a_lado_ficam_os_dois():
    img = np.empty((ALTURA, LARGURA, 3), np.uint8)
    img[:] = PAPEL
    img[200:400, 60:180] = (90, 120, 160)
    img[220:380, 230:340] = (120, 90, 60)
    justa = caixa_justa(img, _fracao((20, 150, 380, 450)))
    x0, y0, x1, y1 = _em_pontos(justa)
    assert x0 <= 60 and x1 >= 340 and y0 <= 200 and y1 >= 400
