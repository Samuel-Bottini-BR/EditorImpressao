"""O "Ajustar o pedaço à figura" com o retângulo de QUATRO cantos.

Por que existe (junção do ramo pedaco-e-salvo-2 ao fase-1, 06/10/2026): desde
a frente de geometria (core/zonas_na_folha.py, decisão D2), as zonas ficam
presas à folha original. Quando o ângulo ou o corte da página muda depois de
o pedaço ser desenhado, o retângulo é levado para o preparo novo e pode
deixar de ficar alinhado com a página: aí ele passa a ter QUATRO pontos (os
cantos, na ordem (x0,y0) (x1,y0) (x1,y1) (x0,y1)), e não mais os dois de
sempre. O core/ajustar_pedaco.py lia só os dois primeiros pontos - com quatro
cantos isso é a beira de cima do retângulo, uma tira sem altura, e o aviso e
o botão erravam.

O que se cobra (teste de máquina):
    - o retângulo de quatro cantos, levemente girado, em volta da figura com
      papel sobrando é medido pela caixa que contém os quatro cantos (o aviso
      "Sobrou papel" aparece);
    - o botão o encolhe até a figura, e o resultado volta a ser o retângulo
      de dois pontos (alinhado com a página de agora), sem cortar a figura;
    - o retângulo de dois pontos continua medido como antes.
"""

from __future__ import annotations

import math

import numpy as np

from core.ajustar_pedaco import ajustar_os_pedacos, avaliar_os_pedacos
from core.filtros import ORIGINAL, PRETO_E_BRANCO
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

ALTURA, LARGURA = 600, 400
PAPEL = (200, 225, 238)                     # creme (BGR)
FIGURA = (100, 200, 300, 480)               # x0, y0, x1, y1 em pontos
FOLGADO = (60 / LARGURA, 170 / ALTURA, 340 / LARGURA, 540 / ALTURA)


def _pagina() -> np.ndarray:
    """Papel creme com uma figura colorida no meio (a mesma ideia de
    tests/test_ajustar_pedaco.py, sem o texto)."""
    rng = np.random.default_rng(7)
    img = np.empty((ALTURA, LARGURA, 3), np.uint8)
    img[:] = PAPEL
    img = np.clip(img.astype(np.int16) + rng.integers(-4, 5, img.shape), 0, 255).astype(np.uint8)
    x0, y0, x1, y1 = FIGURA
    xs = np.linspace(0, 1, x1 - x0)[None, :]
    ys = np.linspace(0, 1, y1 - y0)[:, None]
    img[y0:y1, x0:x1, 0] = (60 + 120 * xs + 0 * ys).astype(np.uint8)
    img[y0:y1, x0:x1, 1] = (90 + 80 * ys + 0 * xs).astype(np.uint8)
    img[y0:y1, x0:x1, 2] = (150 + 60 * xs * ys).astype(np.uint8)
    return img


def _cantos_girados(caixa, graus: float) -> list[tuple[float, float]]:
    """Os quatro cantos de `caixa` (fração), girados `graus` em volta do
    centro, em pontos de verdade (a página não é quadrada) e de volta a
    fração - como core/zonas_na_folha deixa o retângulo levado."""
    x0, y0, x1, y1 = (caixa[0] * LARGURA, caixa[1] * ALTURA,
                      caixa[2] * LARGURA, caixa[3] * ALTURA)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c, s = math.cos(math.radians(graus)), math.sin(math.radians(graus))
    cantos = []
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        dx, dy = x - cx, y - cy
        cantos.append(((cx + c * dx - s * dy) / LARGURA, (cy + s * dx + c * dy) / ALTURA))
    return cantos


def _selecao(pontos) -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=pontos,
                         origem=MAO, filtro=ORIGINAL))
    return s


def test_quatro_cantos_e_medido_pela_caixa_inteira():
    cantos = _cantos_girados(FOLGADO, 1.5)
    folgas = avaliar_os_pedacos(_pagina(), _selecao(cantos), PRETO_E_BRANCO)
    assert 0 in folgas
    x0, y0, x1, y1 = folgas[0].caixa
    xs = [p[0] for p in cantos]
    ys = [p[1] for p in cantos]
    assert (x0, y0, x1, y1) == (min(xs), min(ys), max(xs), max(ys))
    assert folgas[0].muito                     # o aviso "Sobrou papel" aparece
    assert folgas[0].muda


def test_quatro_cantos_ajustado_vira_retangulo_de_dois_pontos():
    cantos = _cantos_girados(FOLGADO, 1.5)
    nova, quantos = ajustar_os_pedacos(_pagina(), _selecao(cantos), PRETO_E_BRANCO)
    assert quantos == 1
    pontos = nova.regioes[0].pontos
    assert len(pontos) == 2
    (x0, y0), (x1, y1) = pontos
    fx0, fy0, fx1, fy1 = FIGURA
    # nunca corta a figura, e encolheu
    assert x0 * LARGURA <= fx0 + 0.5 and y0 * ALTURA <= fy0 + 0.5
    assert x1 * LARGURA >= fx1 - 0.5 and y1 * ALTURA >= fy1 - 0.5
    assert x0 > min(p[0] for p in cantos) and x1 < max(p[0] for p in cantos)


def test_dois_pontos_continua_como_antes():
    pontos = [FOLGADO[:2], FOLGADO[2:]]
    folgas = avaliar_os_pedacos(_pagina(), _selecao(pontos), PRETO_E_BRANCO)
    assert folgas[0].caixa == FOLGADO
