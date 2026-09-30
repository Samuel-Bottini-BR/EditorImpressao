"""A janela principal cabe no notebook do Kaique (1920 x 1080 a 150%).

Pedido da gerente (30/09/2026): a altura minima era 680 pontos, e a area util
do notebook, a 150% de escala, e de ~657 (tirada a barra de tarefas e o
titulo da janela): a janela passava da tela. O tamanho inicial (1220 x 800)
tambem passava. Conferido a mao com as fontes de verdade (a 150%, janela
sem ir para a tela): as telas cabem em 600 de altura sem se sobrepor.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QRect  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

AREA_UTIL_DO_KAIQUE = QRect(0, 0, 1280, 688)     # 1920 x 1080 a 150%, sem a barra de tarefas
ALTURA_DO_TITULO = 31


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_a_altura_minima_cabe_no_notebook(app):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    try:
        assert janela.minimumSize().height() <= AREA_UTIL_DO_KAIQUE.height() - ALTURA_DO_TITULO
        assert janela.minimumSize().width() <= AREA_UTIL_DO_KAIQUE.width()
        # e o que os layouts exigem tambem cabe (senao o minimo nao vale)
        assert janela.minimumSizeHint().height() <= janela.minimumSize().height()
    finally:
        janela.close()


def test_o_tamanho_inicial_nao_passa_da_tela(app):
    from ui.janela_principal import LARGURA_E_ALTURA_MINIMAS, JanelaPrincipal

    largura, altura = JanelaPrincipal.tamanho_que_cabe(AREA_UTIL_DO_KAIQUE)
    assert altura + ALTURA_DO_TITULO <= AREA_UTIL_DO_KAIQUE.height()
    assert largura <= AREA_UTIL_DO_KAIQUE.width()
    # tela grande: o tamanho de sempre
    assert JanelaPrincipal.tamanho_que_cabe(QRect(0, 0, 1920, 1040)) == (1220, 800)
    # tela menor que o minimo: fica no minimo (o Windows poe barras de rolagem)
    assert JanelaPrincipal.tamanho_que_cabe(QRect(0, 0, 800, 500)) == LARGURA_E_ALTURA_MINIMAS
