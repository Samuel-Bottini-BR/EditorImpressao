"""O menu "Painéis" e as peças novas do menu Ver (rodada 14 do layout, 20/10/2026).

903 (Samuel: "B — Um menu novo, “Painéis”"): os cinco painéis da direita, marcado o aberto, "Fechar o
painel" e os ícones da direita; os quatro "Painel: ..." do menu Ver (que nunca fizeram nada) saíram.
904 ("A — Sim, no menu Ver"): "Miniaturas" e "Ícones da direita" no menu Ver.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_menus_que_nao_faziam_nada import app, janela  # noqa: F401, E402 - fixtures


def _textos(menu):
    return [a.text() for a in menu.actions() if not a.isSeparator()]


def test_o_menu_paineis_tem_os_cinco(janela):  # noqa: F811
    paineis = janela.menu.menus["Painéis"]
    assert _textos(paineis) == ["Propriedades", "Filtro da página", "Para revisar", "Automático",
                                "Histórico", "Fechar o painel", "Ícones da direita"]
    assert not any(t.startswith("Painel:") for t in _textos(janela.menu.menus["Ver"]))
    assert {"Miniaturas", "Ícones da direita"} <= set(_textos(janela.menu.menus["Ver"]))


def test_abrir_e_fechar_pelo_menu_e_a_marca_acompanha(janela):  # noqa: F811
    colunas = janela.tela_conferir.paineis
    acoes = janela.menu.acoes
    acoes["painel_filtro"].trigger()
    assert colunas.aberto == "filtro"
    assert acoes["painel_filtro"].isChecked() and not acoes["painel_props"].isChecked()
    colunas.abrir("historico")                       # pelo ícone: o menu acompanha
    assert acoes["painel_historico"].isChecked() and not acoes["painel_filtro"].isChecked()
    acoes["painel_historico"].trigger()              # clicar no marcado fecha
    assert colunas.aberto is None and not acoes["painel_historico"].isChecked()
    acoes["painel_props"].trigger()
    acoes["painel_fechar"].trigger()
    assert colunas.aberto is None and not acoes["painel_props"].isChecked()


def test_icones_e_miniaturas_pelo_menu(janela):  # noqa: F811
    colunas = janela.tela_conferir.paineis
    acoes = janela.menu.acoes
    assert acoes["icones"].isChecked()
    acoes["icones"].trigger()
    assert not colunas.icones_a_vista
    colunas.alternar_os_icones()                     # pela seta: o menu acompanha
    assert colunas.icones_a_vista and acoes["icones"].isChecked()
    acoes["miniaturas"].trigger()
    assert janela.tela_conferir.tira.isHidden()
    acoes["miniaturas"].trigger()
    assert not janela.tela_conferir.tira.isHidden()
