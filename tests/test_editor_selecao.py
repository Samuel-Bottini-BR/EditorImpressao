"""O editor de seleção: marcar a mão onde está cada coisa.

Roda sem abrir janela, com a plataforma "offscreen" do Qt.
"""

from __future__ import annotations

import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from core.selecao import GRAVURA, LETRA, PAPEL, SOMAR, SUBTRAIR, Selecao, retangulo  # noqa: E402
from ui.widgets.editor_selecao import (  # noqa: E402
    FERRAMENTA_ELIPSE,
    FERRAMENTA_LACO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_POLIGONO,
    FERRAMENTA_RETANGULO,
    FERRAMENTA_VARINHA,
    NOMES_DAS_FERRAMENTAS,
    EditorSelecao,
)


@pytest.fixture(scope="module")
def app():
    existente = QtWidgets.QApplication.instance()
    yield existente or QtWidgets.QApplication([])


@pytest.fixture
def pagina():
    """Papel claro com um quadrado escuro no meio."""
    img = np.full((400, 300, 3), 235, np.uint8)
    img[120:280, 90:210] = (40, 40, 40)
    return img


@pytest.fixture
def editor(app, pagina):
    e = EditorSelecao()
    e.resize(300, 400)
    e.definir_imagem(pagina)
    e.definir_selecao(Selecao())
    e._area = e._calcular_area()
    return e


def clicar(editor, fx, fy, botao=None):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    botao = botao or Qt.LeftButton
    ponto = QPointF(editor._para_tela(fx, fy))
    return QMouseEvent(QMouseEvent.Type.MouseButtonPress, ponto, botao, botao,
                       Qt.NoModifier)


def soltar(editor, fx, fy):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    ponto = QPointF(editor._para_tela(fx, fy))
    return QMouseEvent(QMouseEvent.Type.MouseButtonRelease, ponto, Qt.LeftButton,
                       Qt.NoButton, Qt.NoModifier)


def mover(editor, fx, fy):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    ponto = QPointF(editor._para_tela(fx, fy))
    return QMouseEvent(QMouseEvent.Type.MouseMove, ponto, Qt.NoButton,
                       Qt.LeftButton, Qt.NoModifier)


def arrastar(editor, x0, y0, x1, y1):
    editor.mousePressEvent(clicar(editor, x0, y0))
    editor.mouseMoveEvent(mover(editor, (x0 + x1) / 2, (y0 + y1) / 2))
    editor.mouseMoveEvent(mover(editor, x1, y1))
    editor.mouseReleaseEvent(soltar(editor, x1, y1))


# --- as ferramentas ---------------------------------------------------------

def test_retangulo_marca_a_area_arrastada(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(GRAVURA)
    arrastar(editor, 0.2, 0.2, 0.8, 0.8)

    assert len(editor.selecao) == 1
    m = editor.selecao.mascara(200, 200, GRAVURA)
    assert m[100, 100]
    assert not m[10, 10]


def test_oval_tambem_marca(editor):
    editor.definir_ferramenta(FERRAMENTA_ELIPSE)
    arrastar(editor, 0.1, 0.1, 0.9, 0.9)
    m = editor.selecao.mascara(200, 200, GRAVURA)
    assert m[100, 100]
    assert not m[5, 5]      # o canto fica de fora de um oval


def test_laco_fecha_o_contorno(editor):
    editor.definir_ferramenta(FERRAMENTA_LACO)
    editor.mousePressEvent(clicar(editor, 0.2, 0.2))
    for x, y in [(0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]:
        editor.mouseMoveEvent(mover(editor, x, y))
    editor.mouseReleaseEvent(soltar(editor, 0.2, 0.8))

    assert len(editor.selecao) == 1
    assert editor.selecao.mascara(200, 200, GRAVURA)[100, 100]


def test_pincel_pinta_uma_faixa(editor):
    editor.definir_ferramenta(FERRAMENTA_PINCEL)
    editor.espessura = 0.1
    editor.mousePressEvent(clicar(editor, 0.1, 0.5))
    for x in (0.4, 0.7, 0.9):
        editor.mouseMoveEvent(mover(editor, x, 0.5))
    editor.mouseReleaseEvent(soltar(editor, 0.9, 0.5))

    m = editor.selecao.mascara(200, 200, GRAVURA)
    assert m[100, 100]      # em cima da faixa
    assert not m[20, 100]   # acima dela


def test_poligono_fecha_no_duplo_clique(editor):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    editor.definir_ferramenta(FERRAMENTA_POLIGONO)
    for x, y in [(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)]:
        editor.mousePressEvent(clicar(editor, x, y))
    assert editor.selecao.vazia, "nao pode fechar antes do duplo clique"

    ponto = QPointF(editor._para_tela(0.2, 0.8))
    editor.mouseDoubleClickEvent(QMouseEvent(
        QMouseEvent.Type.MouseButtonDblClick, ponto, Qt.LeftButton,
        Qt.LeftButton, Qt.NoModifier))

    assert len(editor.selecao) == 1
    assert editor.selecao.mascara(200, 200, GRAVURA)[100, 100]


def test_varinha_pega_a_mancha_da_cor(editor):
    """Clicar no quadrado escuro tem de pegar o quadrado, e nao a folha."""
    editor.definir_ferramenta(FERRAMENTA_VARINHA)
    editor.mousePressEvent(clicar(editor, 0.5, 0.5))

    assert len(editor.selecao) >= 1
    m = editor.selecao.mascara(400, 300, GRAVURA)
    assert m[200, 150], "nao pegou o quadrado"
    assert not m[20, 20], "vazou para o papel"


# --- somar e subtrair -------------------------------------------------------

def test_subtrair_abre_buraco(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    arrastar(editor, 0.0, 0.0, 1.0, 1.0)
    editor.definir_operacao(SUBTRAIR)
    arrastar(editor, 0.3, 0.3, 0.7, 0.7)

    m = editor.selecao.mascara(200, 200, GRAVURA)
    assert m[10, 10]
    assert not m[100, 100]


def test_cada_tipo_vai_para_a_sua_camada(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(GRAVURA)
    arrastar(editor, 0.0, 0.0, 0.45, 1.0)
    editor.definir_tipo(LETRA)
    arrastar(editor, 0.55, 0.0, 1.0, 1.0)

    g = editor.selecao.mascara(100, 100, GRAVURA)
    ll = editor.selecao.mascara(100, 100, LETRA)
    assert g[50, 20] and not g[50, 80]
    assert ll[50, 80] and not ll[50, 20]


# --- desfazer ---------------------------------------------------------------

def test_desfazer_volta_uma_acao(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    arrastar(editor, 0.1, 0.1, 0.4, 0.4)
    arrastar(editor, 0.6, 0.6, 0.9, 0.9)
    assert len(editor.selecao) == 2

    editor.desfazer()
    assert len(editor.selecao) == 1
    editor.desfazer()
    assert editor.selecao.vazia
    assert not editor.pode_desfazer

    editor.desfazer()   # desfazer com a lista vazia nao pode quebrar
    assert editor.selecao.vazia


def test_limpar_a_maquina_preserva_a_mao(editor):
    """Rodar a deteccao de novo nao pode apagar o trabalho manual."""
    from core.selecao import AUTOMATICO, REDE

    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 0.5, origem=AUTOMATICO))
    s.acrescentar(retangulo(0.5, 0.5, 1.0, 1.0, origem=REDE))
    editor.definir_selecao(s)

    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    arrastar(editor, 0.2, 0.7, 0.4, 0.9)
    assert len(editor.selecao) == 3

    assert editor.limpar_o_que_a_maquina_marcou() == 2
    assert len(editor.selecao) == 1
    assert editor.selecao.regioes[0].origem == "mao"


# --- coisas que nao podem quebrar -------------------------------------------

def test_sem_imagem_nao_quebra(app):
    e = EditorSelecao()
    e.resize(200, 200)
    e.mousePressEvent(clicar(e, 0.5, 0.5) if e._pixmap else _clique_solto())
    assert e.selecao.vazia


def _clique_solto():
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    return QMouseEvent(QMouseEvent.Type.MouseButtonPress, QPointF(10, 10),
                       Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)


def test_clique_sem_arrastar_nao_cria_regiao(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    arrastar(editor, 0.5, 0.5, 0.5005, 0.5005)
    assert editor.selecao.vazia, "um clique acidental virou regiao"


def test_rede_ausente_nao_quebra(editor, monkeypatch):
    import core.rede_selecao as rede

    monkeypatch.setattr(rede, "disponivel", lambda: False)
    assert editor.selecionar_com_a_rede((0.5, 0.5)) is False


def test_todas_as_ferramentas_tem_nome_em_portugues():
    for ferramenta, nome in NOMES_DAS_FERRAMENTAS.items():
        assert nome and nome[0].isupper()
        assert not any(c in nome for c in "_<>{}")


def test_o_papel_tambem_pode_ser_marcado(editor):
    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    editor.definir_tipo(PAPEL)
    arrastar(editor, 0.1, 0.1, 0.9, 0.9)
    assert editor.selecao.mascara(100, 100, PAPEL)[50, 50]


def test_pintar_nao_quebra_com_selecao_cheia(editor):
    """A repintura roda a cada movimento do mouse: nao pode explodir."""
    from PySide6.QtGui import QPaintEvent

    editor.definir_ferramenta(FERRAMENTA_RETANGULO)
    for k in range(6):
        arrastar(editor, 0.05 * k, 0.05 * k, 0.5 + 0.05 * k, 0.5 + 0.05 * k)
    editor.paintEvent(QPaintEvent(editor.rect()))


def test_pegar_tudo_desta_cor_pega_a_pagina_toda_e_nao_so_a_mancha(qtbot=None):
    """A varinha cresce a partir do ponto; esta olha a folha inteira.

    Numa partitura com pautas vermelhas, a varinha comum pega UMA pauta - ou
    vaza pelo pergaminho, que e continuo. Esta aqui pega as vinte pautas, que e
    o que serve para consertar o que o detector errou.
    """
    import cv2
    import numpy as np
    from PySide6.QtWidgets import QApplication

    from core.selecao import GRAVURA
    from ui.widgets.editor_selecao import (
        FERRAMENTA_COR,
        FERRAMENTA_VARINHA,
        EditorSelecao,
    )

    QApplication.instance() or QApplication([])

    # pergaminho creme, com tres riscas vermelhas separadas
    pagina = np.full((300, 200, 3), (180, 200, 215), np.uint8)
    for y in (60, 150, 240):
        pagina[y:y + 6, 20:180] = (40, 40, 200)      # vermelho, em BGR

    editor = EditorSelecao()
    editor.definir_imagem(pagina)
    editor.definir_tipo(GRAVURA)

    # a varinha comum pega so a risca onde se clicou
    editor.definir_ferramenta(FERRAMENTA_VARINHA)
    editor._varinha((0.5, 60.0 / 300.0 + 0.005))
    uma = float(editor.selecao.mascara(300, 200, GRAVURA).mean())

    # a nova pega as tres
    editor.definir_selecao(type(editor.selecao)())
    editor.definir_ferramenta(FERRAMENTA_COR)
    editor._tudo_desta_cor((0.5, 60.0 / 300.0 + 0.005))
    todas = float(editor.selecao.mascara(300, 200, GRAVURA).mean())

    assert todas > uma * 2, (uma, todas)
