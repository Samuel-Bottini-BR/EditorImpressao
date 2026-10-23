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


def test_os_cartoes_mostram_as_margens_depois_de_medir(app, pasta):
    """"Sim, a tela mostra igual ao que sai" (Samuel, 22/10/2026): a tela pede
    a medida por trás e, quando chega, a página do cartão vem com as margens."""
    import numpy as np

    from core.filtros import ORIGINAL
    from historico_acoes import HistoricoAcoes
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=3)
    projeto = Projeto(caminho_entrada=str(caminho), nome="t", dividir_folhas=False,
                      detectar_regioes=False, margens_iguais=True)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=ORIGINAL) for i in range(3)]
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    try:
        img = np.full((300, 200, 3), 120, np.uint8)
        primeira = tela._com_as_margens(img)
        tela._tarefa_das_margens.wait(60000)
        app.processEvents()
        depois = tela._com_as_margens(img)
        assert depois.shape[0] > img.shape[0] and depois.shape[1] > img.shape[1]
        assert primeira is img
        projeto.margens_iguais = False
        assert tela._com_as_margens(img) is img
    finally:
        previas.parar()
