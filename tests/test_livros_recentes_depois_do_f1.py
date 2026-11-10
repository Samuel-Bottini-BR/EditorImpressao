"""O menu Arquivo > "Livros recentes" continua abrindo depois da Lista de atalhos (F1).

Bug: 07/11/2026, teste como o Kaique: o programa fecha ao abrir Livros recentes (N12, Palatino;
Central `k0711-fechou`, Samuel: "Consertar"). Contra a D-376 ("nenhuma exceção pode fechar a
janela").

A causa: o texto do F1 (`BarraDeMenu.texto_dos_atalhos`) perguntava `a.menu()` a cada item dos
menus. No PySide6 6.11.1 isso faz o submenu "Livros recentes" virar filho, do lado do Python, do
item temporário `a`; quando o item some, o Python marca o submenu como apagado (o Qt continua com
ele). Na próxima abertura do menu, `menu.clear()` em `_montar_livros_recentes` dava
"RuntimeError: Internal C++ object (PySide6.QtWidgets.QMenu) already deleted", a caixa de erro
abria no meio da abertura do submenu e, ao fechá-la, o Qt quebrava (Qt6Widgets.dll,
QMenu::internalDelayedPopup). Detalhe em relatorios/livros-recentes-2026-11-10/ONDE-PAREI.md.

Teste de reversão (CLAUDE.md 4.7): falha no código de antes (o menu fica "apagado" para o Python
depois do F1) e passa no novo. Sem janela na tela (conftest: offscreen).
"""

from __future__ import annotations

import gc

import pytest

pytest.importorskip("PySide6")

import shiboken6  # noqa: E402

from tests.test_gravura_na_aba_marcar import app  # noqa: F401, E402 - fixture


@pytest.fixture
def janela(app, tmp_path, monkeypatch):  # noqa: F811 - a fixture app vem de cima
    """A janela principal, com a pasta de projetos do teste (nunca a do Samuel)."""
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)

    from ui.janela_principal import JanelaPrincipal

    return JanelaPrincipal()


def _apertar_f1(janela, monkeypatch) -> None:
    """Ajuda > "Lista de atalhos" (F1), como o Kaique: a caixa abre e é fechada na hora."""
    from PySide6.QtWidgets import QMessageBox

    monkeypatch.setattr(QMessageBox, "exec", lambda self: 0)
    janela.menu.acoes["atalhos"].trigger()


def test_livros_recentes_abre_depois_da_lista_de_atalhos(janela, monkeypatch):
    """07/11/2026, teste como o Kaique: o programa fecha ao abrir Livros recentes (depois do F1)."""
    import projetos

    _apertar_f1(janela, monkeypatch)
    gc.collect()
    menu = janela.menu.menu_recentes
    assert shiboken6.isValid(menu), (
        "depois do F1 o menu 'Livros recentes' ficou apagado para o Python: ao abrir o menu, "
        "o programa dá erro e fecha (teste do Kaique, 07/11/2026)")

    monkeypatch.setattr(projetos, "listar", lambda: [
        projetos.Resumo(nome="Palatino", caminho_entrada="palatino30.pdf"),
        projetos.Resumo(nome="", caminho_entrada=r"C:\livros\lusiadas.pdf")])
    pedidos = []
    monkeypatch.setattr(janela.tela_inicio, "pedir_para_continuar", pedidos.append)
    for _vez in range(2):                    # abrir o menu duas vezes, como o Kaique tentou
        menu.aboutToShow.emit()
        acoes = menu.actions()
        assert [a.text() for a in acoes] == ["Palatino", "lusiadas.pdf"]
    acoes[0].trigger()
    assert [r.nome for r in pedidos] == ["Palatino"], \
        "o livro tem de passar pela mesma conferência do cartão 'continuar'"


def test_a_lista_de_atalhos_nao_mudou_de_texto(janela, monkeypatch):
    """O conserto não muda o que o F1 mostra: a mesma lista, tirada dos próprios menus, sem os
    submenus ("Livros recentes", "Aplicar o giro em", "Lado direito", "Tema") como linha."""
    texto = janela.menu.texto_dos_atalhos()
    assert texto == janela.menu.texto_dos_atalhos(), "chamar duas vezes tem de dar o mesmo texto"
    linhas = [linha.strip() for linha in texto.splitlines()]
    for submenu in ("Livros recentes", "Aplicar o giro em", "Lado direito", "Tema"):
        assert submenu not in linhas, f"o submenu '{submenu}' apareceu como item na lista"
    assert "Abrir um livro...  —  Ctrl+O" in linhas
    # e os submenus guardados pela barra continuam vivos para o Python depois de montar a lista
    gc.collect()
    for nome in ("menu_recentes", "menus_do_giro", "menu_do_lado_direito"):
        assert shiboken6.isValid(getattr(janela.menu, nome)), \
            f"o submenu guardado em '{nome}' ficou apagado para o Python depois do F1"
