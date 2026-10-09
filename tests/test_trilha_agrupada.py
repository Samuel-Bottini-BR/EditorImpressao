"""A tela de trabalho sem abas (layout, etapa 2, 08/10/2026).

Decisões do Samuel conferidas aqui:
  - 25/09: estilo Photoshop, sem abas: as abas viraram ferramentas da trilha;
  - rodada 8, 302 C: trilha agrupada como no Photoshop, com a letra do atalho
    no balão do mouse, também nas ferramentas escondidas no mesmo botão;
  - rodada 8, 303 B: a barra de opções da ferramenta na linha dos menus;
  - rodada 9, 405 C: desfazer e refazer sempre à mão (barra de baixo).

Testes de máquina (sem janela na tela, tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QEvent, QPoint, Qt  # noqa: E402
from PySide6.QtGui import QMouseEvent  # noqa: E402

from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)
from ui.widgets.trilha_agrupada import (  # noqa: E402
    FERRAMENTA_CORTAR,
    FERRAMENTA_DIVIDIR,
    FERRAMENTA_ENDIREITAR,
    FERRAMENTA_FILTROS,
    GRUPOS,
    LARGURA,
    TrilhaAgrupada,
    grupo_de,
)


def _aberta(janela, pasta, dividir=True):
    janela.abrir_livro(str(_pdf(pasta, folhas=5)))
    if dividir:
        janela.tela_opcoes.cx_dividir.setChecked(True)
    _analisar(janela)
    janela.resize(1280, 657)
    janela.show()
    return janela.tela_conferir


def _clicar(trilha, indice, botao=Qt.LeftButton):
    centro = trilha.retangulos()[indice].center()
    for tipo in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease):
        trilha.event(QMouseEvent(tipo, centro, trilha.mapToGlobal(centro), botao,
                                 botao, Qt.NoModifier))


# --- a peça sozinha -----------------------------------------------------------


def test_a_trilha_tem_os_grupos_do_prototipo(app):
    grupos = [g for g in GRUPOS if g != "-"]
    assert ("retangulo", "elipse") in grupos
    assert ("laco", "poligono") in grupos
    assert ("varinha", "cor") in grupos
    assert grupos[:3] == [(FERRAMENTA_DIVIDIR,), (FERRAMENTA_CORTAR,), (FERRAMENTA_ENDIREITAR,)]
    assert TrilhaAgrupada().width() == LARGURA == 44


def test_o_balao_mostra_a_letra_tambem_das_escondidas(app):
    """Pedido do Samuel na rodada 8: "quando eu passar em cima da agrupada tem
    que mostrar a letra dela de atalho"."""
    trilha = TrilhaAgrupada()
    texto = trilha.texto_da_dica(grupo_de("laco"))
    assert "Laço" in texto and "[L]" in texto
    assert "Ponto a ponto [P]" in texto
    assert "segure o botão" in texto
    # as de página não têm letra, e o balão não inventa uma
    assert "[" not in trilha.texto_da_dica(grupo_de(FERRAMENTA_CORTAR))


def test_clicar_escolhe_a_que_esta_a_vista(app):
    trilha = TrilhaAgrupada()
    trilha.resize(LARGURA, 600)
    escolhidas = []
    trilha.escolhida.connect(escolhidas.append)
    _clicar(trilha, grupo_de("laco"))
    assert escolhidas == ["laco"]
    trilha.definir_ferramenta("poligono")
    assert trilha.a_vista(grupo_de("laco")) == "poligono"
    _clicar(trilha, grupo_de("laco"))
    assert escolhidas[-1] == "poligono"


def test_o_botao_direito_abre_o_grupo_com_as_letras(app):
    trilha = TrilhaAgrupada()
    trilha.resize(LARGURA, 600)
    _clicar(trilha, grupo_de("retangulo"), Qt.RightButton)
    menu = trilha.menu_do_grupo
    assert menu is not None
    textos = [a.text() for a in menu.actions() if a.text()]
    assert any(t.startswith("Retângulo\t") for t in textos)
    assert any(t.startswith("Oval\t") for t in textos)
    menu.close()


def test_so_aparecem_as_ferramentas_do_livro(app):
    trilha = TrilhaAgrupada()
    trilha.resize(LARGURA, 600)
    trilha.definir_disponiveis({FERRAMENTA_CORTAR, FERRAMENTA_FILTROS})
    assert set(trilha.retangulos()) == {grupo_de(FERRAMENTA_CORTAR), grupo_de(FERRAMENTA_FILTROS)}


@pytest.mark.parametrize("altura", [380, 600, 800])
def test_todos_os_botoes_cabem(app, altura):
    trilha = TrilhaAgrupada()
    trilha.resize(LARGURA, altura)
    fundo = max(r.bottom() for r in trilha.retangulos().values())
    assert fundo < max(altura, 380), "botão para fora da trilha"


# --- na janela ----------------------------------------------------------------


def test_sem_abas_na_tela_e_a_trilha_troca_o_modo(janela, pasta):
    tela = _aberta(janela, pasta)
    assert not tela.barra_abas.isVisible(), "as abas sairam da tela (estilo Photoshop)"
    for ferramenta, aba in ((FERRAMENTA_DIVIDIR, "corte"), (FERRAMENTA_CORTAR, "bordas"),
                            (FERRAMENTA_FILTROS, "filtro")):
        if aba in tela._abas_ativas:
            tela.trilha.escolher(ferramenta)
            assert tela.aba_atual == aba
            assert tela.trilha.ferramenta == ferramenta
    if "marcar" in tela._abas_ativas:
        tela.trilha.escolher("laco")
        assert tela.aba_atual == "marcar"
        assert tela.barra_opcoes.ferramenta == "laco"


def test_trocar_de_aba_por_dentro_acerta_a_trilha(janela, pasta):
    """Quem ainda troca a "aba" por dentro (atalhos, testes antigos) deixa a
    trilha marcando a ferramenta certa."""
    tela = _aberta(janela, pasta)
    if "bordas" in tela._abas_ativas:
        tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("bordas"))
        assert tela.trilha.ferramenta == FERRAMENTA_CORTAR
        assert tela.barra_opcoes.rotulo.text().startswith("Cortar as bordas")


def test_escolher_ferramenta_de_pagina_pelo_ponto_unico_troca_a_tela(janela, pasta):
    """O ponto unico de troca (escolher_ferramenta) com uma ferramenta de
    pagina leva a tela para ela, e nao so acende o icone (achado em 09/10/2026:
    a trilha marcava Endireitar e a tela ficava na de marcar)."""
    tela = _aberta(janela, pasta)
    for ferramenta, aba in ((FERRAMENTA_ENDIREITAR, "angulo"), (FERRAMENTA_CORTAR, "bordas"),
                            (FERRAMENTA_DIVIDIR, "corte"), (FERRAMENTA_FILTROS, "filtro")):
        if "marcar" in tela._abas_ativas:
            tela.escolher_ferramenta("laco")
        if aba in tela._abas_ativas:
            tela.escolher_ferramenta(ferramenta)
            assert tela.aba_atual == aba
            assert tela.trilha.ferramenta == ferramenta


def test_os_controles_do_endireitar_g5_moram_na_ferramenta_endireitar(janela, pasta):
    """Etapa 2: os controles novos do endireitar (item 2.2, G5: o angulo em
    numero com as setas de 0,1 grau e o "aplicar em"; a "conta:" do G4)
    aparecem na fila de botoes embaixo da faixa quando a ferramenta e o
    Endireitar, e somem com as outras ferramentas (lugar PROVISORIO ate o
    painel Propriedades, etapa 4)."""
    tela = _aberta(janela, pasta)
    if "angulo" not in tela._abas_ativas:
        pytest.skip("este livro nao endireita")
    tela.trilha.escolher(FERRAMENTA_ENDIREITAR)
    assert tela.aba_atual == "angulo"
    for controle in (tela.campo_angulo, tela.botao_angulo_anti_horario,
                     tela.botao_angulo_horario, tela.combo_alcance_do_angulo,
                     tela.combo_conta_do_endireitar):
        assert controle.isVisible(), controle
        assert tela.barra_botoes.currentWidget().isAncestorOf(controle)
    tela.trilha.escolher(FERRAMENTA_CORTAR)
    assert not tela.campo_angulo.isVisible()


def test_a_barra_de_opcoes_mora_na_linha_dos_menus(janela, pasta):
    tela = _aberta(janela, pasta)
    assert tela.barra_opcoes.parentWidget() is janela.linha_dos_menus
    assert janela.menuWidget() is janela.linha_dos_menus
    assert tela.barra_opcoes.isVisible()
    janela._voltar_das_opcoes()
    assert not tela.barra_opcoes.isVisible(), "fora da tela de trabalho ela some"


def test_a_barra_de_baixo_navega_e_desfaz(janela, pasta):
    tela = _aberta(janela, pasta, dividir=False)
    tela.ir_para_pagina(0)
    assert tela.rotulo_da_pagina.text() == f"página 1 de {len(janela.projeto.paginas)}"
    assert not tela.botao_anterior.isEnabled()
    tela.botao_proxima.click()
    assert tela.indice_pagina == 1
    assert "conferidas" in tela.rotulo_do_livro.text()
    assert not tela.botao_desfazer_embaixo.isEnabled()
    tela._marcar_revisada()
    if janela.acoes.feitas:
        assert tela.botao_desfazer_embaixo.isEnabled()
        feitas = len(janela.acoes.feitas)
        tela.botao_desfazer_embaixo.click()
        assert len(janela.acoes.feitas) == feitas - 1
        assert tela.botao_refazer_embaixo.isEnabled()


def test_as_setas_dos_lados_viraram_as_da_barra_de_baixo(janela, pasta):
    tela = _aberta(janela, pasta)
    for pagina in tela.paginas_de_imagem.values():
        for botao in pagina.findChildren(type(tela.botao_anterior)):
            if botao.text() in ("<", ">"):
                assert not botao.isVisible()
    assert tela.botao_anterior.text() == "‹" and tela.botao_proxima.text() == "›"


def test_o_botao_do_historico_abre_o_painel(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.paineis.historico.definir_recolhido(True)
    tela.botao_historico_embaixo.click()
    assert not tela.paineis.historico.recolhido
