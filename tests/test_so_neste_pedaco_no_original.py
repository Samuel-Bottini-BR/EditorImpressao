"""O "so neste pedaco" da aba Marcar numa pagina em Original.

Lista de bugs do plano (05/10/2026), achado do implementador no conserto do
Preto e branco (`60d8c58`) e confirmado pelo verificador: numa pagina em
Original, um pedaco marcado com Preto e branco, Melhorar ou Magico pro era
ignorado - core/filtros.py::aplicar_filtro_com_selecao saia logo no comeco
com `if filtro in (ORIGINAL, TIRAR_FUNDO): return img, False`.

Decisao do Samuel (conferencia 13, S4): "Sim, do mesmo jeito" - o mesmo
jeito do conserto do Preto e branco: a area marcada obedece INTEIRA ao filtro
escolhido para ela (inclusive o papel que a pessoa pegou junto; a borda e a
que ela desenhou), e o resto da pagina fica Original.

O que se cobra:
    - pedaco em Preto e branco, Melhorar ou Magico pro numa pagina em
      Original: dentro do pedaco, o filtro do pedaco; fora, a pagina como
      veio, ponto por ponto;
    - pagina em Original sem pedaco (com ou sem marcacao de gravura/letra/
      papel): a MESMA imagem de antes, o mesmo objeto (nada e copiado);
    - pedaco em "Original" numa pagina em Original: nada muda;
    - "Tirar o fundo" (pagina intacta ou PDF sem camadas): o pedaco vale do
      mesmo jeito (conferencia 14, "FUNDO: Sim, do mesmo jeito"; a pagina de
      que o fundo foi tirado: tests/test_so_neste_pedaco_no_tirar_o_fundo.py);
    - "Limpar a folha" desligado: o pedaco continua sem valer (outra causa,
      de proposito: ver o comentario em core/pipeline.py::_filtrar).
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
    TIRAR_FUNDO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
)
from core.selecao import AUTOMATICO, GRAVURA, LETRA, MAO, PAPEL, RETANGULO, Regiao, Selecao, retangulo

ALTURA, LARGURA = 600, 400
# o retangulo marcado: um bloco de texto com margem de papel em volta
PEDACO = (0.05, 0.03, 0.95, 0.38)


def _pagina() -> np.ndarray:
    """Papel creme, linhas de texto em cima, uma pintura colorida embaixo."""
    img = np.full((ALTURA, LARGURA, 3), (215, 232, 240), np.uint8)   # papel creme (BGR)
    for y in range(30, 200, 24):
        img[y:y + 8, 30:LARGURA - 30] = (40, 50, 70)                  # texto marrom
    xs = np.linspace(0, 1, 240)[None, :]
    ys = np.linspace(0, 1, 280)[:, None]
    img[260:540, 80:320, 0] = (60 + 100 * xs + 0 * ys).astype(np.uint8)
    img[260:540, 80:320, 1] = (90 + 80 * ys + 0 * xs).astype(np.uint8)
    img[260:540, 80:320, 2] = (140 + 60 * xs * ys).astype(np.uint8)
    return img


def _selecao(filtro_do_pedaco: str | None, tipo: str = LETRA) -> Selecao:
    s = Selecao()
    s.acrescentar(Regiao(tipo=tipo, forma=RETANGULO,
                         pontos=[PEDACO[:2], PEDACO[2:]], origem=MAO,
                         filtro=filtro_do_pedaco or ""))
    return s


def _caixa() -> tuple[int, int, int, int]:
    return (int(round(PEDACO[0] * LARGURA)), int(round(PEDACO[1] * ALTURA)),
            int(round(PEDACO[2] * LARGURA)), int(round(PEDACO[3] * ALTURA)))


def _tres(img: np.ndarray) -> np.ndarray:
    return img if img.ndim == 3 else cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


@pytest.mark.parametrize("pedido", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_o_pedaco_obedece_inteiro_ao_filtro_dele(pedido):
    img = _pagina()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), ORIGINAL, _selecao(pedido))
    esperado, _ = aplicar_filtro(img.copy(), pedido)
    x0, y0, x1, y1 = _caixa()
    assert not mono, "a pagina em Original e colorida: nunca 1 bit"
    # dentro do retangulo inteiro (o papel pego junto tambem), o filtro do pedaco
    assert np.array_equal(_tres(saida)[y0 + 1:y1 - 1, x0 + 1:x1 - 1],
                          _tres(esperado)[y0 + 1:y1 - 1, x0 + 1:x1 - 1]), \
        "o pedaco nao saiu como o filtro escolhido para ele"


@pytest.mark.parametrize("pedido", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_fora_do_pedaco_a_pagina_sai_como_veio(pedido):
    img = _pagina()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), ORIGINAL, _selecao(pedido))
    x0, y0, x1, y1 = _caixa()
    fora = np.ones((ALTURA, LARGURA), bool)
    fora[y0 - 1:y1 + 2, x0 - 1:x1 + 2] = False
    assert np.array_equal(_tres(saida)[fora], img[fora]), "o Original mudou fora do pedaco"


def test_pedaco_em_preto_e_branco_deixa_o_texto_preto_e_branco():
    """O caso do Samuel: pagina em Original, o bloco de texto em Preto e
    branco. Dentro do pedaco so ha preto e branco."""
    img = _pagina()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), ORIGINAL, _selecao(PRETO_E_BRANCO))
    x0, y0, x1, y1 = _caixa()
    dentro = _tres(saida)[y0 + 1:y1 - 1, x0 + 1:x1 - 1]
    assert set(np.unique(dentro).tolist()) <= {0, 255}


# Etapa 9c da obra (26/10/2026; D-027 "virar uma folha branca", D-227 "pintar de
# branco -> no PDF sai branca"; promessas P-075 e P-078): o PAPEL marcado A MAO
# ("Deixar a folha em branco", "pintar de branco") vai a branco tambem no
# Original - e o comportamento antigo que saiu (antes este teste pedia o mesmo
# objeto tambem para ele). O papel do DETECTOR continua sem mudar o Original.
MARCACOES_QUE_NAO_MUDAM = [(GRAVURA, MAO), (LETRA, MAO), (PAPEL, AUTOMATICO)]


@pytest.mark.parametrize("marcacao, origem", MARCACOES_QUE_NAO_MUDAM)
def test_pagina_em_original_sem_pedaco_e_a_mesma_imagem(marcacao, origem):
    """Marcacao sem filtro proprio (a do detector, ou gravura/letra a mao sem
    "so neste pedaco"): a pagina em Original continua saindo como veio, o
    MESMO objeto, como antes do conserto."""
    img = _pagina()
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.4, 0.9, 0.9, tipo=marcacao, origem=origem))
    saida, mono = aplicar_filtro_com_selecao(img, ORIGINAL, s)
    assert saida is img and mono is False


@pytest.mark.parametrize("filtro", [ORIGINAL, TIRAR_FUNDO])
def test_papel_a_mao_sai_branco_no_original_e_no_tirar_o_fundo(filtro):
    """D-027 / D-227 (etapa 9c): o papel marcado a mao vai a branco so na
    area dele; o resto da pagina fica como veio."""
    img = _pagina()
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.4, 0.9, 0.9, tipo=PAPEL, origem=MAO))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), filtro, s)
    assert mono is False
    assert _tres(saida)[int(ALTURA * 0.45):int(ALTURA * 0.85),
                        int(LARGURA * 0.15):int(LARGURA * 0.85)].min() == 255
    assert np.array_equal(_tres(saida)[:int(ALTURA * 0.38)], _tres(img)[:int(ALTURA * 0.38)])


def test_pedaco_em_original_numa_pagina_em_original_nao_muda_nada():
    img = _pagina()
    saida, mono = aplicar_filtro_com_selecao(img, ORIGINAL, _selecao(ORIGINAL))
    assert saida is img and mono is False


@pytest.mark.parametrize("pedido", [PRETO_E_BRANCO, MELHORAR, MAGICO_PRO])
def test_tirar_o_fundo_obedece_ao_pedaco_do_mesmo_jeito(pedido):
    """Conferencia 14 (Samuel): "FUNDO: Sim, do mesmo jeito (só muda se
    alguém marcar um pedaço)". Igual ao Original, ponto por ponto."""
    img = _pagina()
    no_fundo, mono = aplicar_filtro_com_selecao(img.copy(), TIRAR_FUNDO, _selecao(pedido))
    no_original, _ = aplicar_filtro_com_selecao(img.copy(), ORIGINAL, _selecao(pedido))
    assert mono is False
    assert np.array_equal(no_fundo, no_original)
    assert not np.array_equal(_tres(no_fundo), img)


@pytest.mark.parametrize("marcacao, origem", MARCACOES_QUE_NAO_MUDAM)
def test_tirar_o_fundo_sem_pedaco_e_a_mesma_imagem(marcacao, origem):
    img = _pagina()
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.4, 0.9, 0.9, tipo=marcacao, origem=origem))
    saida, mono = aplicar_filtro_com_selecao(img, TIRAR_FUNDO, s)
    assert saida is img and mono is False


def test_limpar_a_folha_desligado_no_projeto_antigo_continua_sem_pedaco(monkeypatch):
    """PROJETO ANTIGO (gravado antes da obra de 26/10/2026, etapa 1:
    Projeto.feito_a_mao_sempre_vale False) sem a marca "mexida a mao":
    "Limpar a folha" desligado continua sendo "nao mexer em pagina nenhuma",
    como era (o PDF dele sai igual). Ver core/etapas.py e o comentario em
    core/pipeline.py::_filtrar_a_pagina."""
    from core import pipeline
    from modelos import ConfigPagina, Projeto

    img = _pagina()
    projeto = Projeto(caminho_entrada="x.pdf", limpar=False, feito_a_mao_sempre_vale=False)
    pagina = ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)
    pagina.guardar_selecao(_selecao(PRETO_E_BRANCO))
    monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, **k: _selecao(PRETO_E_BRANCO))
    saida, mono = pipeline._filtrar(projeto, pagina, img)
    assert saida is img and mono is False


def test_limpar_a_folha_desligado_no_livro_novo_usa_o_pedaco_feito_a_mao():
    """Decisao D-009 do Samuel (26/10/2026): "eu deveria conseguir abrir o
    livro sem escolher nenhuma opção para fazer tudo manualmente." No livro
    novo, o pedaco marcado A MAO ("so neste pedaco") vale com "Limpar a folha"
    desligado: a pagina fica no Original e so o pedaco muda. Substitui o
    comportamento antigo (o teste de cima, que agora vale so no projeto
    antigo)."""
    from core import pipeline
    from modelos import ConfigPagina, Projeto

    img = _pagina()
    projeto = Projeto(caminho_entrada="x.pdf", limpar=False)
    pagina = ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)
    pagina.guardar_selecao(_selecao(PRETO_E_BRANCO))
    saida, _ = pipeline._filtrar(projeto, pagina, img.copy())
    x0, y0, x1, y1 = _caixa()
    assert not np.array_equal(_tres(saida)[y0:y1, x0:x1], img[y0:y1, x0:x1])
    fora = np.ones(img.shape[:2], bool)
    fora[y0:y1 + 1, x0:x1 + 1] = False      # a borda da caixa e do pedaco
    assert np.array_equal(_tres(saida)[fora], img[fora])


def test_o_processamento_da_pagina_em_original_usa_o_pedaco(monkeypatch):
    """Pelo caminho do PDF e da previa (core.pipeline._filtrar), com "Limpar
    a folha" ligado: o pedaco vale."""
    from core import pipeline
    from modelos import ConfigPagina, Projeto

    img = _pagina()
    projeto = Projeto(caminho_entrada="x.pdf", limpar=True)
    pagina = ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)
    monkeypatch.setattr(pipeline, "garantir_selecao", lambda *a, **k: _selecao(PRETO_E_BRANCO))
    saida, _ = pipeline._filtrar(projeto, pagina, img.copy())
    x0, y0, x1, y1 = _caixa()
    assert not np.array_equal(_tres(saida)[y0:y1, x0:x1], img[y0:y1, x0:x1])
