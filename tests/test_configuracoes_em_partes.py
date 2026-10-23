"""As Configurações com a lista das partes à esquerda (etapa 7 do layout; rodada 13, 807 B) e o
tema também nelas (rodada 12, 707 C: "Nos dois lugares")."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_menus_que_nao_faziam_nada import app, janela  # noqa: F401, E402 - fixtures


def test_as_partes_na_lista_e_a_da_vez_a_direita(janela):  # noqa: F811
    from ui.tela_configuracoes import PARTES, TelaConfiguracoes

    tela = TelaConfiguracoes(janela)
    assert [tela.lista.item(i).text() for i in range(tela.lista.count())] == list(PARTES)
    assert tela.pilha.currentIndex() == 0
    tela.lista.setCurrentRow(1)
    assert tela.pilha.currentIndex() == 1 and tela._campos, "os atalhos continuam"


def test_o_tema_pelas_configuracoes_marca_o_menu_ver(janela):  # noqa: F811
    from ui import estilo
    from ui.tela_configuracoes import TelaConfiguracoes

    antes = estilo.tema_atual()
    tela = TelaConfiguracoes(janela)
    try:
        tela.botoes_tema["claro"].setChecked(True)
        assert estilo.tema_atual() == "claro"
        assert janela.menu.acoes["tema_claro"].isChecked()
    finally:
        janela._trocar_tema(antes)
