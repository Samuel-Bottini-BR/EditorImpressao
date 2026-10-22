"""Item 2.4 na tela "O que fazer" (controle mínimo, provisório até o layout).

A caixinha "Margens iguais em todas as páginas" vem desmarcada (regra da Fase 2:
desligado de fábrica); marcada, mostra as quatro margens (de fábrica as do
ScanTailor, 10/5/10/5 mm) e o alinhamento, e tudo vai para o projeto. Reabrir
o livro traz o que foi escolhido. Nenhuma janela aparece na tela
(tests/conftest.py); pasta de dados própria.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    app,
    janela,
    pasta,
)


def test_vem_desmarcada_com_as_margens_do_scantailor(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    assert not tela.cx_margens.isChecked()
    assert projeto.margens_iguais is False
    assert [tela.margens_mm[c].value() for c in ("esquerda", "cima", "direita", "baixo")] == \
        [10.0, 5.0, 10.0, 5.0]
    assert tela.painel_margens.isHidden()


def test_marcar_grava_no_projeto_e_mostra_as_margens(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    tela.cx_margens.setChecked(True)
    tela.margens_mm["esquerda"].setValue(15.0)
    tela.combo_alinhar_vertical.setCurrentIndex(tela.combo_alinhar_vertical.findData("cima"))
    assert projeto.margens_iguais is True
    assert projeto.margens_mm == [15.0, 5.0, 10.0, 5.0]
    assert projeto.margens_alinhamento == ["cima", "meio"]
    assert not tela.painel_margens.isHidden()
    assert "margens iguais" in tela.resumo.text()


def test_mostrar_opcoes_traz_o_que_esta_no_projeto(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    projeto.margens_iguais = True
    projeto.margens_mm = [1.0, 2.0, 3.0, 4.0]
    projeto.margens_alinhamento = ["baixo", "direita"]
    tela.mostrar_opcoes()
    assert tela.cx_margens.isChecked()
    assert [tela.margens_mm[c].value() for c in ("esquerda", "cima", "direita", "baixo")] == \
        [1.0, 2.0, 3.0, 4.0]
    assert tela.combo_alinhar_horizontal.currentData() == "direita"
    assert projeto.margens_mm == [1.0, 2.0, 3.0, 4.0]
