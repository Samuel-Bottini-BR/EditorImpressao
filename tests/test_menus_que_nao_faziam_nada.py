"""Os itens de menu que estavam no programa e não faziam nada (etapa 4 do layout, 20/10/2026).

Bug do inventário de telas de 02/10/2026 ("11 itens de menu mortos"; o código da janela não
tinha `ligar(...)` para eles): Arquivo > "Livros recentes" (vazio), Editar > "Mostrar o
histórico", Página > "Restaurar página apagada", Ver > "Aproximar", "Afastar", "Ajustar à
tela" e "Modo comparar". Clicar não fazia nada, e a pessoa acha que o programa travou.

Teste de reversão (CLAUDE.md 4.7): `test_nenhum_item_de_menu_fica_sem_fazer_nada` falha no
código de antes (os sete não estavam em `janela.menu.ligadas`) e passa no novo. Os quatro
"Painel: ..." do menu Ver ficam de fora: o que eles viram espera a rodada 14 do layout (903).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_gravura_na_aba_marcar import app, conferir, livro  # noqa: F401, E402 - fixtures

# (os quatro "Painel: ..." sairam do menu Ver: viraram o menu Painéis, 903 B)
ESPERAM_A_RODADA_14: set[str] = set()


@pytest.fixture
def janela(app, tmp_path, monkeypatch):  # noqa: F811 - a fixture app vem de cima
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)

    from ui.janela_principal import JanelaPrincipal

    return JanelaPrincipal()


def test_nenhum_item_de_menu_fica_sem_fazer_nada(janela):
    sem_acao = sorted(set(janela.menu.acoes) - janela.menu.ligadas - ESPERAM_A_RODADA_14)
    assert not sem_acao, f"itens de menu que não fazem nada: {sem_acao}"


def test_livros_recentes_mostra_os_livros(janela, monkeypatch):
    import projetos

    menu = janela.menu.menu_recentes
    menu.aboutToShow.emit()
    assert [a.text() for a in menu.actions()] == ["(nenhum livro ainda)"]
    monkeypatch.setattr(projetos, "listar", lambda: [
        projetos.Resumo(nome="Consolação da Filosofia", caminho_entrada="boecio.pdf"),
        projetos.Resumo(nome="", caminho_entrada=r"C:\livros\opus.pdf")])
    pedidos = []
    monkeypatch.setattr(janela.tela_inicio, "pedir_para_continuar", pedidos.append)
    menu.aboutToShow.emit()
    acoes = menu.actions()
    assert [a.text() for a in acoes] == ["Consolação da Filosofia", "opus.pdf"]
    acoes[0].trigger()
    assert [r.nome for r in pedidos] == ["Consolação da Filosofia"], \
        "o livro tem de passar pela mesma conferência do cartão"


def test_aproximar_afastar_e_ajustar(conferir):  # noqa: F811
    editor = conferir.editor_selecao
    conferir.escolher_ferramenta("retangulo")
    editor.ajustar_a_tela()
    conferir.mudar_o_zoom(conferir.PASSO_DO_ZOOM)
    assert editor.zoom == pytest.approx(1.25)
    conferir.mudar_o_zoom(conferir.PASSO_DO_ZOOM)
    conferir.mudar_o_zoom(1 / conferir.PASSO_DO_ZOOM)
    assert editor.zoom == pytest.approx(1.25)
    conferir.mudar_o_zoom(None)
    assert editor.zoom == pytest.approx(1.0)


def test_restaurar_volta_so_a_pagina_apagada(conferir):  # noqa: F811
    pagina = conferir.projeto.paginas[conferir.indice_pagina]
    conferir.restaurar_pagina()
    assert not pagina.apagada and not conferir.acoes.pode_desfazer, \
        "restaurar uma página que não está apagada não pode virar ação"
    conferir.apagar_pagina()
    assert pagina.apagada
    conferir.restaurar_pagina()
    assert not pagina.apagada
    conferir.desfazer()
    assert pagina.apagada, "o restaurar entra no desfazer"


def test_modo_comparar_abre_a_tela_grande_comparando(conferir, monkeypatch):  # noqa: F811
    from ui.tela_ampliada import TelaAmpliada

    vistas = []

    def exec_sem_travar(self):
        vistas.append(self.comparando)
        return 0

    monkeypatch.setattr(TelaAmpliada, "exec", exec_sem_travar)
    conferir.ampliar(comparar=True)
    assert vistas == [True]
    conferir.ampliar()
    assert vistas == [True, False]
