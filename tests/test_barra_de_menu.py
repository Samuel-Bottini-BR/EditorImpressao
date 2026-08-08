"""A barra de menu, e o que saiu da tela por causa dela.

Etapa 1 do redesenho. O que se cobra aqui e a **lista de conferência da seção
5**: nenhum controle pode se perder no caminho. Botão que virou item de menu
tem de existir no menu, e apontar para a mesma ação.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def janela(app, tmp_path, monkeypatch):
    import projetos

    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)

    from ui.janela_principal import JanelaPrincipal

    return JanelaPrincipal()


# --- os menus do desenho ----------------------------------------------------


def test_os_sete_menus_do_desenho(janela):
    esperados = ["Arquivo", "Editar", "Marcar", "Filtro", "Página", "Ver", "Ajuda"]
    assert list(janela.menu.menus) == esperados


def test_na_tela_inicial_so_tres_menus_ficam_de_pe(janela):
    """Como no desenho: Arquivo · Ver · Ajuda."""
    janela.menu.mostrar_tela_inicial()
    ativos = [t for t, m in janela.menu.menus.items() if m.menuAction().isEnabled()]
    assert ativos == ["Arquivo", "Ver", "Ajuda"]


def test_na_tela_de_trabalho_todos_valem(janela):
    janela.menu.mostrar_tela_de_trabalho()
    assert all(m.menuAction().isEnabled() for m in janela.menu.menus.values())


# --- a lista de conferência da seção 5 --------------------------------------

# (controle que existia como botão, item de menu onde ele passa a morar)
MUDOU_DE_LUGAR = [
    ("procurar de novo", "procurar_de_novo", "Marcar"),
    ("limpar tudo", "limpar_marcacao", "Marcar"),
    ("deixar a folha em branco", "folha_em_branco", "Marcar"),
    ("desfazer", "desfazer", "Editar"),
    ("refazer", "refazer", "Editar"),
    ("voltar", "voltar", "Arquivo"),
    ("Salvar em", "pasta_de_saida", "Arquivo"),
    ("Nome do arquivo", "nome_do_arquivo", "Arquivo"),
    ("Confirmar e processar", "processar", "Arquivo"),
]


@pytest.mark.parametrize("era, chave, menu", MUDOU_DE_LUGAR)
def test_nenhum_controle_se_perdeu(janela, era, chave, menu):
    assert chave in janela.menu.acoes, f'"{era}" não tem destino no menu {menu}'
    acao = janela.menu.acoes[chave]
    assert acao.text(), f'"{era}" virou um item de menu sem texto'
    assert chave in janela.menu.ligadas, \
        f'o item de menu de "{era}" não faz nada quando clicado'


def test_os_quatro_filtros_estao_no_menu_com_as_teclas(janela):
    from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO

    teclas = {ORIGINAL: "1", PRETO_E_BRANCO: "2", MELHORAR: "3", MAGICO_PRO: "4"}
    for filtro, tecla in teclas.items():
        acao = janela.menu.acoes[f"filtro_{filtro}"]
        assert acao.shortcut().toString() == tecla
        assert f"filtro_{filtro}" in janela.menu.ligadas


def test_ligar_um_nome_que_nao_existe_levanta(janela):
    """Menu que aponta para o vazio é pior do que menu que não existe."""
    with pytest.raises(KeyError):
        janela.menu.ligar("acao_inventada", lambda: None)


# --- a ajuda não pode mentir ------------------------------------------------


def test_a_lista_de_atalhos_sai_dos_proprios_menus(janela):
    """Duas listas separadas divergem na primeira mudança."""
    texto = janela.menu.texto_dos_atalhos()

    for titulo in janela.menu.menus:
        assert titulo in texto, f"o menu {titulo} não aparece na ajuda"

    assert "Ctrl+Z" in texto
    assert "Desfazer" in texto


def test_todo_atalho_do_menu_aparece_na_ajuda(janela):
    texto = janela.menu.texto_dos_atalhos()
    for chave, acao in janela.menu.acoes.items():
        atalho = acao.shortcut().toString()
        if atalho:
            assert atalho in texto, f"o atalho de {chave} ({atalho}) sumiu da ajuda"


# --- o que saiu da tela de trabalho -----------------------------------------


def test_salvar_em_e_nome_do_arquivo_sairam_da_tela(app):
    """Eles importam num momento só - o de gravar - e tomavam uma faixa inteira."""
    from ui.tela_conferir import TelaConferir

    tela = TelaConferir()
    assert not hasattr(tela, "destino"), \
        "a faixa de destino continua ocupando altura na tela de trabalho"


def test_a_janela_de_confirmar_avisa_das_paginas_nao_conferidas(app, tmp_path):
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.janela_confirmar import JanelaConfirmar

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), nome="x")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(10)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(10)]
    for pagina in projeto.paginas[:6]:
        pagina.revisada = True

    janela = JanelaConfirmar(projeto, "saida.pdf")
    assert janela.aviso_conferir.isVisibleTo(janela)
    assert "4 página(s)" in janela.aviso_conferir.rotulo.text()


def test_a_janela_de_confirmar_cala_quando_tudo_foi_conferido(app, tmp_path):
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.janela_confirmar import JanelaConfirmar

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), nome="x")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(3)]
    for pagina in projeto.paginas:
        pagina.revisada = True

    janela = JanelaConfirmar(projeto, "saida.pdf")
    assert not janela.aviso_conferir.isVisibleTo(janela)


def test_a_janela_de_confirmar_avisa_que_vai_substituir(app, tmp_path):
    from modelos import ConfigFolha, ConfigPagina, Projeto
    from ui.janela_confirmar import JanelaConfirmar

    ja_existe = tmp_path / "saida.pdf"
    ja_existe.write_bytes(b"%PDF-1.4")

    projeto = Projeto(caminho_entrada=str(tmp_path / "x.pdf"), nome="x")
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0, revisada=True)]
    projeto.caminho_saida = str(ja_existe)

    janela = JanelaConfirmar(projeto, "saida.pdf")
    janela.destino.definir(tmp_path, "saida.pdf")
    janela._reavaliar()

    assert janela.aviso_existe.isVisibleTo(janela)
    assert "substituído" in janela.aviso_existe.rotulo.text()
