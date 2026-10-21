"""Teste de reversão: o cartão de cada filtro mostra o que o filtro faria na página,
com as caixinhas da página (bug do verificador do 2.9, 21/10/2026).

Bug (ramo `verif-2.9-2026-10-21`, `4d71875`): com "Letra clara em fundo escuro"
marcada, os cartões dos outros filtros mostravam a página SEM inverter. O
cartão Melhorar mostrava a lombada cinza, mas escolher Melhorar deixava a
página preta. Causa: `ui/tarefas._TarefaCartoes.run` chamava `aplicar_filtro`
direto, sem a inversão do 2.9 e sem as cores do 2.11 ("Letras com a cor
delas", "Reduzir cores"). E a chave das prévias e dos cartões não tinha as
três caixinhas: marcar uma reaproveitava os cartões de antes.

Conserto: o cartão passa pela mesma conta da página (core.pipeline.
filtro_na_amostra: inverter, filtro, cores, desinverter), e a chave leva as
três caixinhas. No código antigo os testes falham; no novo, passam.
"""

from __future__ import annotations

import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from core import claro_no_escuro, cores_scantailor  # noqa: E402
from core import st_ferramentas as st  # noqa: E402
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO, aplicar_filtro  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _projeto(**caixinhas) -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf", detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    pagina = ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)
    for campo, valor in caixinhas.items():
        setattr(pagina, campo, valor)
    projeto.paginas = [pagina]
    return projeto


def _pagina_escura() -> np.ndarray:
    """Fundo quase preto com letras claras, e uma faixa cinza (a "lombada")."""
    img = np.full((140, 100, 3), 25, np.uint8)
    img[:, :12] = 120
    for y in range(20, 120, 16):
        img[y:y + 6, 25:90] = 225
    return img


def _cartoes(app, projeto, base, filtros):
    from ui import tarefas

    previas = tarefas.GerenciadorPrevias("x.pdf", projeto, None)
    chegou = {}
    previas.cartoes_prontos.connect(lambda indice, resultados, *_: chegou.update(r=resultados))
    previas.pedir_cartoes(0, base, filtros, 50, 50, 50)
    fim = time.monotonic() + 20
    while "r" not in chegou and time.monotonic() < fim:
        QCoreApplication.processEvents()
        time.sleep(0.01)
    previas.parar()
    assert "r" in chegou, "o cartão nunca respondeu"
    return chegou["r"]


def test_cartao_melhorar_com_letra_clara_em_fundo_escuro(app):
    base = _pagina_escura()
    resultados = _cartoes(app, _projeto(claro_no_escuro=True), base, [MELHORAR])
    esperado = claro_no_escuro.inverter(
        aplicar_filtro(claro_no_escuro.inverter(base), MELHORAR, 50, 50, 50)[0])
    assert np.array_equal(resultados[MELHORAR], esperado)
    sem_inverter = aplicar_filtro(base, MELHORAR, 50, 50, 50)[0]
    assert not np.array_equal(resultados[MELHORAR], sem_inverter)


def test_cartao_original_nao_inverte(app):
    base = _pagina_escura()
    resultados = _cartoes(app, _projeto(claro_no_escuro=True), base, [ORIGINAL])
    assert np.array_equal(resultados[ORIGINAL], aplicar_filtro(base, ORIGINAL, 50, 50, 50)[0])


@pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")
def test_cartao_preto_e_branco_com_letras_com_a_cor(app):
    from tests.test_cores_scantailor import pagina_com_letras_coloridas

    base = pagina_com_letras_coloridas()
    resultados = _cartoes(app, _projeto(letras_com_a_cor=True), base, [PRETO_E_BRANCO])
    saida = aplicar_filtro(base, PRETO_E_BRANCO, 50, 50, 50)[0]
    com_cor = cores_scantailor.aplicar(base, saida, PRETO_E_BRANCO, True, False, 70)
    assert com_cor is not None
    assert resultados[PRETO_E_BRANCO].ndim == 3
    vermelha = resultados[PRETO_E_BRANCO][190:210, 32:36].reshape(-1, 3).mean(0)
    assert vermelha[2] > vermelha[0] + 60, "a letra vermelha do cartão tem de sair vermelha"


def test_chave_muda_com_as_caixinhas(app):
    from ui import tarefas

    projeto = _projeto()
    previas = tarefas.GerenciadorPrevias("x.pdf", projeto, None)
    antes = previas.chave(0, 70, "cartoes")
    for campo in ("claro_no_escuro", "letras_com_a_cor", "reduzir_cores"):
        setattr(projeto.paginas[0], campo, True)
        depois = previas.chave(0, 70, "cartoes")
        assert depois != antes, campo
        antes = depois
    previas.parar()


def test_cartao_preto_e_branco_igual_a_pagina(app):
    """O cartão Preto e branco usa o "Limpar pontinhos" e o jeito da página
    (antes: sempre o nosso limpar, e o cartão apagava os "..." de um slide que
    a página mantinha)."""
    from core import pipeline

    base = _pagina_escura()
    base[60:62, 30:32] = 225                      # um pontinho claro: o "..." do slide
    projeto = _projeto(claro_no_escuro=True)
    projeto.paginas[0].filtro = PRETO_E_BRANCO
    resultados = _cartoes(app, projeto, base, [PRETO_E_BRANCO])
    pagina = pipeline._filtrar(projeto, projeto.paginas[0], base)[0]
    assert np.array_equal(resultados[PRETO_E_BRANCO], pagina)
