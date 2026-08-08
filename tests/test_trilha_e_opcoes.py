"""Etapa 2: a trilha de ferramentas e a barra de opções.

O que se cobra: as nove ferramentas existem e são alcançáveis, a barra muda
conforme a ferramenta na mão, e **somar/tirar aparecem em todas as de seleção**
- eles não são ferramentas, são modos que modificam a ferramenta escolhida.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.selecao import SOMAR, SUBTRAIR  # noqa: E402
from ui.widgets.barra_opcoes import ALTURA as ALTURA_DA_BARRA  # noqa: E402
from ui.widgets.barra_opcoes import BarraOpcoes  # noqa: E402
from ui.widgets.editor_selecao import (  # noqa: E402
    ATALHOS_DAS_FERRAMENTAS,
    FERRAMENTA_COR,
    FERRAMENTA_MAO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_RETANGULO,
    FERRAMENTA_VARINHA,
    FERRAMENTA_ZOOM,
    FERRAMENTAS,
    ORDEM_DA_TRILHA,
    ZOOM_MAX,
    ZOOM_MIN,
    EditorSelecao,
)
from ui.widgets.trilha_ferramentas import LARGURA as LARGURA_DA_TRILHA  # noqa: E402
from ui.widgets.trilha_ferramentas import TrilhaFerramentas  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


# --- a trilha ---------------------------------------------------------------


def test_as_nove_ferramentas_estao_na_trilha(app):
    assert len(ORDEM_DA_TRILHA) == 9
    esperadas = ["retangulo", "elipse", "laco", "poligono", "pincel",
                 "varinha", "cor", "zoom", "mao"]
    assert list(ORDEM_DA_TRILHA) == esperadas


def test_cada_ferramenta_tem_a_letra_do_desenho(app):
    esperados = {"retangulo": "R", "elipse": "O", "laco": "L", "poligono": "P",
                 "pincel": "B", "varinha": "V", "cor": "C", "zoom": "Z", "mao": "E"}
    assert ATALHOS_DAS_FERRAMENTAS == esperados


def test_as_letras_nao_batem_com_os_numeros_dos_filtros(app):
    """1 2 3 4 continuam trocando o filtro."""
    letras = set(ATALHOS_DAS_FERRAMENTAS.values())
    assert not letras & {"1", "2", "3", "4"}


def test_a_trilha_tem_a_largura_do_desenho(app):
    assert TrilhaFerramentas().width() == LARGURA_DA_TRILHA == 42


@pytest.mark.parametrize("altura", [640, 500, 400, 300, 240, 200])
def test_as_nove_ficam_alcancaveis_em_qualquer_altura(app, altura):
    """Trilha cortada esconde o Zoom e a Mão - as duas últimas."""
    trilha = TrilhaFerramentas()
    trilha.resize(LARGURA_DA_TRILHA, altura)
    trilha._deslocamento = trilha._rolagem_maxima()

    fim = trilha._posicao_de(len(ORDEM_DA_TRILHA) - 1) + trilha._altura_do_item()
    assert fim <= altura, "a última ferramenta não aparece nem rolando a trilha"


def test_clicar_na_trilha_escolhe_a_ferramenta(app):
    trilha = TrilhaFerramentas()
    trilha.resize(LARGURA_DA_TRILHA, 640)
    escolhidas = []
    trilha.escolhida.connect(escolhidas.append)

    meio_do_terceiro = trilha._posicao_de(2) + trilha._altura_do_item() // 2
    assert trilha._ferramenta_em(meio_do_terceiro) == ORDEM_DA_TRILHA[2]


# --- a barra de opções ------------------------------------------------------


def test_a_barra_tem_a_altura_do_desenho(app):
    assert BarraOpcoes().height() == ALTURA_DA_BARRA == 38


def test_a_barra_muda_conforme_a_ferramenta(app):
    barra = BarraOpcoes()

    barra.definir_ferramenta(FERRAMENTA_COR)
    assert "Pegar tudo desta cor" in barra.rotulo.text()
    assert "variação" in barra.dica.text()

    barra.definir_ferramenta(FERRAMENTA_PINCEL)
    assert "Pincel" in barra.rotulo.text()
    assert "tamanho" in barra.dica.text()

    barra.definir_ferramenta(FERRAMENTA_ZOOM)
    assert "Zoom" in barra.rotulo.text()


def test_a_barra_so_mostra_os_controles_da_ferramenta_ativa(app):
    """É o que deixa nove ferramentas caberem sem entulhar a tela."""
    barra = BarraOpcoes()

    barra.definir_ferramenta(FERRAMENTA_PINCEL)
    do_pincel = barra.dentro.count()
    assert do_pincel > 0, "o pincel não trouxe controle nenhum"

    barra.definir_ferramenta(FERRAMENTA_RETANGULO)
    assert barra.dentro.count() == 0, \
        "o retângulo herdou controles da ferramenta anterior"


@pytest.mark.parametrize("ferramenta", [
    "retangulo", "elipse", "laco", "poligono", "pincel", "varinha", "cor"])
def test_somar_e_tirar_aparecem_em_todas_as_de_selecao(app, ferramenta):
    barra = BarraOpcoes()
    barra.definir_ferramenta(ferramenta)
    assert all(b.isVisibleTo(barra) for b in barra.botoes_modo.values()), \
        f"somar/tirar sumiram em {ferramenta}"


@pytest.mark.parametrize("ferramenta", ["zoom", "mao"])
def test_somar_e_tirar_somem_nas_de_navegar(app, ferramenta):
    """Não há o que somar ao aproximar a página."""
    barra = BarraOpcoes()
    barra.definir_ferramenta(ferramenta)
    assert not any(b.isVisibleTo(barra) for b in barra.botoes_modo.values())


def test_a_barra_avisa_quando_o_modo_muda(app):
    barra = BarraOpcoes()
    avisos = []
    barra.operacao_mudou.connect(avisos.append)
    barra._escolher_modo(SUBTRAIR)
    assert avisos == [SUBTRAIR]


# --- zoom e mão, as duas novas ---------------------------------------------


def test_zoom_e_mao_existem_no_editor(app):
    assert FERRAMENTA_ZOOM in FERRAMENTAS
    assert FERRAMENTA_MAO in FERRAMENTAS


def test_o_zoom_tem_limites(app):
    editor = EditorSelecao()
    editor.definir_zoom(999)
    assert editor.zoom == ZOOM_MAX
    editor.definir_zoom(0.01)
    assert editor.zoom == ZOOM_MIN


def test_ajustar_a_tela_volta_ao_comeco(app):
    from PySide6.QtCore import QPoint

    editor = EditorSelecao()
    editor.definir_zoom(4.0)
    editor.deslocamento = QPoint(50, -30)
    editor.ajustar_a_tela()
    assert editor.zoom == 1.0
    assert editor.deslocamento == QPoint(0, 0)


def test_a_area_da_pagina_cresce_com_o_zoom(app):
    """Se a área não mudar, as alças de corte ficariam no lugar errado."""
    import numpy as np

    editor = EditorSelecao()
    editor.resize(400, 400)
    editor.definir_imagem(np.full((200, 100, 3), 200, np.uint8))

    sem_zoom = editor._calcular_area()
    editor.definir_zoom(2.0)
    com_zoom = editor._calcular_area()

    assert com_zoom.width() > sem_zoom.width()
    assert abs(com_zoom.width() / sem_zoom.width() - 2.0) < 0.05


def test_a_ferramenta_de_navegar_nao_marca_nada(app):
    """Clicar com o Zoom não pode deixar rastro na seleção."""
    import numpy as np
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    editor = EditorSelecao()
    editor.resize(400, 400)
    editor.definir_imagem(np.full((200, 200, 3), 200, np.uint8))
    editor.definir_ferramenta(FERRAMENTA_ZOOM)

    evento = QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(200, 200),
                         Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
    editor.mousePressEvent(evento)

    assert editor.selecao.vazia, "o zoom marcou uma região"
    assert editor.zoom > 1.0, "o zoom não aproximou"
