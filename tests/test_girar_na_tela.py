"""Girar a folha na tela (item 2.3; provisório até o layout).

Pedido do Samuel (conferência 14, G1): "(c) Os dois" - botões numa barra em
cima da página, com o "aplicar em", e também no menu Página com teclas. A
aparência fica para o agente de layout com ele.

Testes de máquina (sem janela na tela, tests/conftest.py):
    - a barrinha existe, na linha das abas, sem emoji, e cabe na janela de
      1280 x 657 e na mínima de 1000 px (aí só os ícones);
    - cada botão gira as folhas do "aplicar em", numa ação só do desfazer;
    - o menu Página tem os três giros e o "Aplicar o giro em", que anda junto
      com a lista da barrinha;
    - Ctrl+Esquerda e Ctrl+Direita não brigam com nenhuma outra tecla, e a
      tecla R ficou só para o Retângulo;
    - o botão "girar" de sempre (aba Onde cortar) continua girando 1/4 à direita.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtCore import QEvent, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QKeySequence  # noqa: E402

import atalhos  # noqa: E402
from core import girar, pipeline  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)


def _aberta(janela, pasta, folhas=5):
    janela.abrir_livro(str(_pdf(pasta, folhas=folhas)))
    _analisar(janela)
    tela = janela.tela_conferir
    janela.resize(1280, 657)
    janela.show()
    return tela


def _rotacoes(janela):
    return [f.rotacao for f in janela.projeto.folhas]


def test_a_barrinha_existe_na_linha_das_abas_e_sem_emoji(janela, pasta):
    tela = _aberta(janela, pasta)
    barra = tela.barra_girar
    assert barra.parentWidget() is tela.linha_das_abas
    # o nome de cada botao (na janela estreita o botao mostra so o icone)
    textos = [barra._textos[g] for g in barra.botoes_de_giro]
    assert textos == ["¼ à esquerda", "¼ à direita", "meia volta"]
    itens = [barra.combo_alcance.itemText(i) for i in range(barra.combo_alcance.count())]
    assert itens == ["só esta", "todas", "daqui em diante", "só as pares", "só as ímpares"]
    assert barra.alcance() == girar.ALCANCE_ESTA, "começa no mais seguro"
    for texto in textos + itens + [barra.rotulo.text(), barra.rotulo_alcance.text()]:
        assert all(ord(c) < 0x2000 for c in texto), texto
    for botao in barra.botoes_de_giro.values():
        assert not botao.icon().isNull(), "pista visual: a seta desenhada"


@pytest.mark.parametrize("largura, altura", [(1280, 657), (1000, 680)])
def test_a_barrinha_cabe_sem_espremer_as_abas(janela, pasta, app, largura, altura):
    """A barrinha nunca passa da janela nem espreme as abas; quando o nome
    escrito nao cabe, fica so o icone (com o nome no balao). Em 1280 x 657
    com as fontes do Windows cabe com o nome (conferido nos prints do
    relatorio); aqui, sem fontes de verdade (offscreen), so a regra."""
    tela = _aberta(janela, pasta)
    janela.resize(largura, altura)
    for _ in range(5):
        app.processEvents()
    barra, abas = tela.barra_girar, tela.barra_abas
    direita = barra.mapTo(janela, barra.rect().topRight()).x()
    assert direita <= janela.width(), "a barrinha nao passa da janela"
    disponivel = janela.width() - 40
    if abas.sizeHint().width() + 8 + barra.sizeHint().width() <= disponivel:
        # (sem fontes de verdade as abas ficam bem mais largas que no Windows)
        assert abas.width() >= abas.sizeHint().width(), "as abas nao sao espremidas"
    assert abas.height() >= abas.sizeHint().height() > 0, "as abas tem altura"
    margens = tela.layout().contentsMargins()
    sobra = tela.width() - margens.left() - margens.right() - abas.sizeHint().width() - 8
    assert barra._compacta is (sobra < barra.largura_com_texto())
    if barra._compacta:
        assert all(b.text() == "" for b in barra.botoes_de_giro.values())
    assert all("Girar" in b.toolTip() for b in barra.botoes_de_giro.values())


def test_na_janela_minima_so_os_icones(janela, pasta, app):
    tela = _aberta(janela, pasta)
    janela.resize(1000, 680)
    for _ in range(5):
        app.processEvents()
    assert tela.barra_girar._compacta
    assert not tela.barra_girar.rotulo.isVisible()


@pytest.mark.parametrize("alcance, giro, esperado", [
    (girar.ALCANCE_ESTA, girar.GIRO_DIREITA, [0, 0, 90, 0, 0]),
    (girar.ALCANCE_TODAS, girar.GIRO_ESQUERDA, [270, 270, 270, 270, 270]),
    (girar.ALCANCE_DAQUI, girar.GIRO_MEIA_VOLTA, [0, 0, 180, 180, 180]),
    (girar.ALCANCE_PARES, girar.GIRO_DIREITA, [0, 90, 0, 90, 0]),
    (girar.ALCANCE_IMPARES, girar.GIRO_DIREITA, [90, 0, 90, 0, 90]),
])
def test_cada_botao_gira_as_folhas_do_aplicar_em(janela, pasta, alcance, giro, esperado):
    tela = _aberta(janela, pasta)
    tela.ir_para_pagina(2)
    assert tela.indice_folha == 2
    tela.barra_girar.definir_alcance(alcance)
    feitas = len(janela.acoes.feitas)
    tela.barra_girar.botoes_de_giro[giro].click()
    assert _rotacoes(janela) == esperado
    assert len(janela.acoes.feitas) == feitas + 1, "uma ação só do desfazer"
    assert janela.acoes.feitas[-1].descricao.startswith("Girar ")
    tela.desfazer()
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    tela.refazer()
    assert _rotacoes(janela) == esperado


def test_o_menu_pagina_tem_os_tres_giros_e_o_aplicar_em(janela, pasta):
    tela = _aberta(janela, pasta)
    acoes = janela.menu.acoes
    assert acoes["girar_esquerda"].text() == "Girar ¼ à esquerda"
    assert acoes["girar"].text() == "Girar ¼ à direita"
    assert acoes["girar_meia_volta"].text() == "Girar meia volta"
    for chave in ("girar", "girar_esquerda", "girar_meia_volta",
                  *(f"giro_em_{a}" for a in girar.ALCANCES)):
        assert chave in janela.menu.ligadas, chave

    acoes["giro_em_todas"].trigger()
    assert tela.barra_girar.alcance() == girar.ALCANCE_TODAS, "o menu muda a barrinha"
    acoes["girar_esquerda"].trigger()
    assert _rotacoes(janela) == [270] * 5
    acoes["girar_meia_volta"].trigger()
    assert _rotacoes(janela) == [90] * 5
    tela.barra_girar.definir_alcance(girar.ALCANCE_PARES)
    assert acoes["giro_em_pares"].isChecked(), "a barrinha muda o menu"
    assert not acoes["giro_em_todas"].isChecked()
    acoes["girar"].trigger()
    assert _rotacoes(janela) == [90, 180, 90, 180, 90]


def test_as_teclas_do_giro_nao_brigam_com_nenhuma_outra(janela):
    assert atalhos.tecla_atual("girar_esquerda") == "Ctrl+Left"
    assert atalhos.tecla_atual("girar") == "Ctrl+Right"
    usadas = [a.atual for a in atalhos.todas() if a.atual]
    repetidas = {t for t in usadas if usadas.count(t) > 1}
    assert not repetidas, repetidas
    atalhos_do_menu = [a.shortcut().toString() for a in janela.menu.acoes.values()
                       if not a.shortcut().isEmpty()]
    assert len(atalhos_do_menu) == len(set(atalhos_do_menu))
    assert janela.menu.acoes["girar"].shortcut() == QKeySequence("Ctrl+Right")
    # o balao dos botoes mostra a tecla, em portugues
    dica = janela.tela_conferir.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].toolTip()
    assert "Ctrl+seta para a direita" in dica


def test_a_tecla_do_menu_gira_de_verdade(janela, pasta, app):
    """Ctrl+Direita pelo caminho do Qt (atalho do menu), com a janela ativa."""
    tela = _aberta(janela, pasta)
    from PySide6.QtTest import QTest

    janela.raise_()
    janela.activateWindow()
    if not QTest.qWaitForWindowActive(janela, 2000):
        import warnings

        with warnings.catch_warnings():    # offscreen, depois de outras janelas
            warnings.simplefilter("ignore", DeprecationWarning)
            app.setActiveWindow(janela)
    app.processEvents()
    assert app.activeWindow() is janela

    QTest.keyClick(janela, Qt.Key_Right, Qt.ControlModifier)
    app.processEvents()
    assert _rotacoes(janela) == [90, 0, 0, 0, 0]
    assert tela.indice_folha == 0, "Ctrl+Direita não troca de página"
    QTest.keyClick(janela, Qt.Key_Left, Qt.ControlModifier)
    app.processEvents()
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]


def test_a_tecla_r_ficou_so_para_o_retangulo(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta, folhas=5)))
    janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))   # com a aba Marcar
    tela = janela.tela_conferir
    assert "marcar" in tela._abas_ativas
    tela.escolher_ferramenta("elipse")
    evento = QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier, "r")
    assert tela.tratar_tecla(evento)
    assert tela.trilha.ferramenta == "retangulo"
    assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    # nem com o Retangulo trocado para outra letra a R gira (antes girava)
    atalhos.redefinir("ferramenta_retangulo", "Q")
    try:
        tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_R, Qt.NoModifier, "r"))
        assert _rotacoes(janela) == [0, 0, 0, 0, 0]
    finally:
        atalhos.restaurar_padrao("ferramenta_retangulo")


def test_o_botao_girar_de_sempre_continua_um_quarto_a_direita(janela, pasta):
    tela = _aberta(janela, pasta)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("corte"))
    linha = tela.linhas_de_botoes["corte"]
    from PySide6.QtWidgets import QPushButton

    botao = next(b for b in linha.findChildren(QPushButton) if b.text() == "girar")
    botao.click()
    assert _rotacoes(janela) == [90, 0, 0, 0, 0]


def test_girar_grava_no_projeto(janela, pasta):
    """Fechar e abrir de novo: o giro continua (campo de sempre, rotacao)."""
    import json

    import projetos

    tela = _aberta(janela, pasta)
    tela.barra_girar.definir_alcance(girar.ALCANCE_IMPARES)
    tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    janela._salvar_agora()
    arquivos = list(projetos.pasta_dos_projetos().rglob("projeto.json"))
    assert arquivos
    dados = json.loads(arquivos[0].read_text(encoding="utf-8"))
    assert [f["rotacao"] for f in dados["folhas"]] == [180, 0, 180, 0, 180]
