"""O "so neste pedaco" da aba Marcar numa pagina em Preto e branco.

Bug da Lista de bugs do plano (05/10/2026, P6 da conferencia 10; o Samuel
mandou consertar na conferencia 11: "(a) Consertar ja (so mudam as paginas
que tem pedaco marcado; as outras ficam iguais)", do jeito completo
recomendado pela gerente: "a area que voce marcou obedece inteira ao filtro
escolhido para ela, inclusive as partes claras (ceu, nuvens)").

O defeito: core/filtros.py::aplicar_filtro_com_selecao saia do ramo do Preto
e branco antes de chamar _filtro_so_no_pedaco. O Kaique marcava a pintura com
"so neste pedaco: Original" e ela saia cinza, sem aviso. So "ligar" a
chamada nao bastava (simulacao da conferencia 11): ela trata como papel tudo
o que e mais claro que 60% do papel, e o papel segue a pagina - o ceu, as
nuvens e partes do leao da Escola 7 saiam cinza e manchados.

O que se cobra:
    - pedaco em Original numa pagina em Preto e branco: a pintura sai como
      veio, INCLUSIVE as partes claras; a pagina deixa de ser 1 bit;
    - pedaco em Melhorar/Magico pro: a pintura sai como esse filtro faria;
    - o papel que a pessoa pegou junto no retangulo tambem obedece ao pedaco
      (a borda e a que ela desenhou). Isso muda, SO no Preto e branco, a regra
      de 07/08 "o papel de dentro da regiao segue a pagina" (tests/
      test_filtro_com_selecao.py::test_o_papel_dentro_da_regiao_segue_a_pagina,
      que agora vale para o Melhorar e o Magico pro): no Preto e branco ela
      nunca tinha valido de verdade, porque o pedaco era ignorado;
    - fora do pedaco nada muda; sem pedaco, nada muda (a prova nas 32
      paginas do gabarito esta em
      relatorios/conferir/so-neste-pedaco-2026-10-05/).
"""

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
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao

ALTURA, LARGURA = 600, 400
# a "pintura" e o retangulo marcado (com margem de papel em volta), em fracoes
PINTURA = (80, 260, 320, 540)            # x0, y0, x1, y1 em pontos
PEDACO = (0.12, 0.38, 0.88, 0.95)
# dentro da pintura, um "ceu" claro (mais claro que 60% do papel, mais escuro
# que o papel) e o resto em tom continuo
CEU = (100, 280, 300, 360)


def _pagina() -> np.ndarray:
    """Papel creme, linhas de texto em cima, e uma pintura colorida com ceu
    claro embaixo."""
    img = np.full((ALTURA, LARGURA, 3), (215, 232, 240), np.uint8)   # papel creme (BGR)
    for y in range(30, 200, 24):
        img[y:y + 8, 30:LARGURA - 30] = (30, 30, 35)                  # texto
    x0, y0, x1, y1 = PINTURA
    xs = np.linspace(0, 1, x1 - x0)[None, :]
    ys = np.linspace(0, 1, y1 - y0)[:, None]
    img[y0:y1, x0:x1, 0] = (60 + 100 * xs + 0 * ys).astype(np.uint8)    # tom continuo colorido
    img[y0:y1, x0:x1, 1] = (90 + 80 * ys + 0 * xs).astype(np.uint8)
    img[y0:y1, x0:x1, 2] = (140 + 60 * xs * ys).astype(np.uint8)
    cx0, cy0, cx1, cy1 = CEU
    img[cy0:cy1, cx0:cx1] = (205, 190, 180)                             # ceu claro azulado
    img[cy0 + 20:cy0 + 40, cx0 + 40:cx0 + 140] = (220, 215, 212)        # nuvem quase branca
    return img


def _selecao(filtro_do_pedaco: str | None) -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO,
                         pontos=[PEDACO[:2], PEDACO[2:]], origem=MAO,
                         filtro=filtro_do_pedaco or ""))
    return s


def _miolo(img: np.ndarray, caixa, folga: int = 12) -> np.ndarray:
    x0, y0, x1, y1 = caixa
    return img[y0 + folga:y1 - folga, x0 + folga:x1 - folga]


def _tres(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


def test_pedaco_em_original_sai_como_veio_inclusive_o_ceu():
    img = _pagina()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(ORIGINAL))
    assert not mono, "com a pintura em cor a pagina nao cabe em 1 bit"
    saida = _tres(saida)
    # a pintura inteira, ceu e nuvem incluidos, como veio (ponto por ponto)
    assert np.array_equal(_miolo(saida, PINTURA), _miolo(img, PINTURA)), \
        "a pintura nao saiu como veio"
    assert np.array_equal(_miolo(saida, CEU, 4), _miolo(img, CEU, 4)), \
        "o ceu claro da pintura nao seguiu o pedaco (o defeito da simulacao)"


@pytest.mark.parametrize("pedido", [MELHORAR, MAGICO_PRO])
def test_pedaco_em_outro_filtro_sai_como_esse_filtro(pedido):
    img = _pagina()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(pedido))
    esperado, _ = aplicar_filtro(img.copy(), pedido)
    assert not mono
    assert np.array_equal(_miolo(_tres(saida), PINTURA), _miolo(_tres(esperado), PINTURA))


def test_o_texto_fora_do_pedaco_continua_em_preto_e_branco():
    img = _pagina()
    com, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(ORIGINAL))
    cinza = cv2.cvtColor(_tres(com), cv2.COLOR_BGR2GRAY)
    assert len(np.unique(cinza[10:220, 10:LARGURA - 10])) <= 2, "o texto deixou de ser preto e branco"


def test_fora_do_pedaco_nada_muda():
    """Fora do retangulo (e da borda suave dele), o mesmo resultado da mesma
    pagina com o retangulo marcado sem filtro proprio."""
    img = _pagina()
    com, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(ORIGINAL))
    sem, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(None))
    longe = np.ones((ALTURA, LARGURA), bool)
    y0, y1 = int(PEDACO[1] * ALTURA) - 6, int(PEDACO[3] * ALTURA) + 6
    x0, x1 = int(PEDACO[0] * LARGURA) - 6, int(PEDACO[2] * LARGURA) + 6
    longe[y0:y1, x0:x1] = False
    assert np.array_equal(_tres(com)[longe], _tres(sem)[longe])


def test_o_papel_que_a_pessoa_pegou_junto_tambem_obedece_ao_pedaco():
    """O jeito completo, ao pe da letra: a area marcada obedece INTEIRA. O
    papel entre a pintura e a beirada do retangulo sai no filtro do pedaco
    (no Original, como veio). A borda e a que a pessoa desenhou.

    (Tentou-se deixar essa margem seguir a pagina, pelo claro ligado ao papel
    de fora; na Opus Majus 20 a parede clara da foto virava manchas brancas.
    Ver o docstring de core.filtros._filtro_so_no_pedaco.)"""
    img = _pagina()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(ORIGINAL))
    a, l = ALTURA, LARGURA
    retangulo = (int(PEDACO[0] * l), int(PEDACO[1] * a), int(PEDACO[2] * l), int(PEDACO[3] * a))
    assert np.array_equal(_miolo(_tres(saida), retangulo, 1), _miolo(img, retangulo, 1))
    # e logo fora da beirada desenhada, a pagina (papel branco)
    fora = cv2.cvtColor(_tres(saida), cv2.COLOR_BGR2GRAY)[retangulo[1] - 6:retangulo[1] - 2,
                                                            retangulo[0]:retangulo[2]]
    assert fora.min() == 255


def test_pedaco_em_preto_e_branco_numa_pagina_em_preto_e_branco_continua_1_bit():
    """Pedir para o pedaco o mesmo filtro da pagina nao muda nada."""
    img = _pagina()
    pedido, mono_pedido = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO,
                                                     _selecao(PRETO_E_BRANCO))
    sem, mono_sem = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _selecao(None))
    assert mono_pedido == mono_sem
    assert np.array_equal(pedido, sem)


def test_pedaco_que_nao_cobre_nada_nao_tira_o_1_bit():
    """Um pedaco desenhado e depois todo tirado (somar + subtrair a mesma
    area) nao cobre ponto nenhum: a pagina continua em 1 bit, igual."""
    from core.selecao import SUBTRAIR

    img = _pagina()
    s = Selecao()
    for operacao in ("somar", SUBTRAIR):
        s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[PEDACO[:2], PEDACO[2:]],
                             origem=MAO, filtro=ORIGINAL, operacao=operacao))
    assert not s.peso_do_filtro(ALTURA, LARGURA, ORIGINAL).any()
    com, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    # a gravura tambem foi somada e tirada: sobra o Preto e branco da folha toda
    sem, mono_sem = aplicar_filtro(img.copy(), PRETO_E_BRANCO)
    assert mono and mono_sem
    assert np.array_equal(com, sem)
