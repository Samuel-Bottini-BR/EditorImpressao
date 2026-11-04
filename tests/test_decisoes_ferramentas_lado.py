"""D-612, segunda parte (04/11/2026): Cortar, Endireitar e as ferramentas de marcar funcionam também
com a vista em "Duas lado a lado", como o Mover (tests/test_decisoes_mover_lado.py).

Pergunta ao Samuel: "O Cortar, o Endireitar e o marcar também têm que funcionar em 'Duas lado a
lado' e em 'antes / depois', como o Mover?" → "1- sim". Aqui: "Duas lado a lado". (O "antes /
depois" espera a resposta de em qual lado a ferramenta age.)

O defeito (o mesmo do Mover, relatorios/mover-parou): nos pares o mouse ia para as prévias, que
só sabem escolher a página da vez; puxar a beirada do Cortar, desenhar a linha do Endireitar ou
marcar um retângulo não fazia nada. Em `472e410c` estes testes de reversão falham.

O que se mede: o arrasto da MÃO no que está à vista embaixo do ponto (como em
test_decisoes_mover_lado.py), e o que foi parar no projeto (recorte, ângulo, marcação). Guardas:
a Mão e o Zoom nos pares continuam os pares de sempre; "Uma página" igual (D-605).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QWheelEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.test_decisoes_mover import (  # noqa: E402,F401 - as mesmas peças das provas do Mover
    _assentar,
    _esperar,
    _pdf,
    app,
    janela,
    pasta,
)
from tests.test_decisoes_mover_lado import _alvo, _arrastar_na_tela, _lugar_da_vez  # noqa: E402
from ui.widgets.paginas_rolando import DUAS, UMA  # noqa: E402


def _nos_pares(janela, tmp_path, ferramenta: str, pagina: int = 1):
    """Livro aberto (sem marcar nada), a ferramenta escolhida, a página e "Duas lado a lado"
    clicado na barra de baixo. A vista fica nos pares (não muda sozinha)."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf"))
    janela.show()
    tela = janela.tela_conferir
    tela.ir_para_pagina(pagina)
    tela.escolher_ferramenta(ferramenta)
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    assert tela.mostrar == DUAS
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    _assentar(10)
    return tela


def _peca_a_vista(tela, peca) -> bool:
    return tela.lado_a_lado.isAncestorOf(peca) and peca.isVisible()


def _no_lugar(tela, peca, ponto_na_peca: QPoint, fx: float, fy: float) -> QPoint:
    """O ponto da página da vez para a mão: o da peça (se ela está nos pares) ou, no código
    antigo, a fração (fx, fy) do lugar da página nos pares."""
    vista = tela.vista_da_pagina.currentWidget()
    if tela.lado_a_lado.isAncestorOf(peca):
        return peca.mapTo(vista, ponto_na_peca)
    lugar = _lugar_da_vez(tela)
    return QPoint(lugar.left() + int(fx * lugar.width()), lugar.top() + int(fy * lugar.height()))


# --- Cortar --------------------------------------------------------------------------------

def test_reversao_d612_cortar_puxar_a_beirada_nos_pares(janela, tmp_path):
    """D-612 ("1- sim"): no Cortar, com "Duas lado a lado", a mão puxa a beirada da direita do
    retângulo do corte para dentro, na página da vez nos pares: o corte muda (uma ação), a
    vista continua nos pares."""
    tela = _nos_pares(janela, tmp_path, "cortar")
    vis = tela.visualizadores["bordas"]
    assert _esperar(lambda: vis._pixmap is not None)
    _lugar_da_vez(tela)
    vis.grab()
    pagina = janela.projeto.paginas[1]
    antes = tuple(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
    feitas = len(janela.acoes.feitas)
    ret = vis._retangulo_recorte()
    de = _no_lugar(tela, vis, vis._alcas(ret)["l"], 1.0, 0.5)
    _arrastar_na_tela(tela, de, -40)
    depois = tuple(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
    assert depois[2] < antes[2] - 0.02, (
        f"o corte não mudou: embaixo da mão estava {type(_alvo(tela, de)[0]).__name__}")
    assert len(janela.acoes.feitas) == feitas + 1
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert _peca_a_vista(tela, vis)


# --- Endireitar ----------------------------------------------------------------------------

def test_reversao_d612_endireitar_linha_nos_pares(janela, tmp_path):
    """D-612: no Endireitar, com "Duas lado a lado", a mão desenha a linha laranja torta em
    cima da página da vez nos pares; ao soltar, a página gira (o ângulo à mão muda)."""
    tela = _nos_pares(janela, tmp_path, "endireitar")
    vis = tela.visualizadores["angulo"]
    assert _esperar(lambda: vis._pixmap is not None and vis.angulo_conhecido)
    _lugar_da_vez(tela)
    vis.grab()
    pagina = janela.projeto.paginas[1]
    antes = pagina.angulo_manual
    a = vis._area
    de = _no_lugar(tela, vis, QPoint(a.left() + int(a.width() * 0.2), a.center().y()), 0.2, 0.5)
    _arrastar_na_tela(tela, de, int(a.width() * 0.6) if a.width() else 120,
                      -int(a.width() * 0.6 * 0.05) if a.width() else -6)
    assert pagina.angulo_manual is not None and pagina.angulo_manual != antes, (
        f"o ângulo não mudou: embaixo da mão estava {type(_alvo(tela, de)[0]).__name__}")
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado


# --- marcar --------------------------------------------------------------------------------

def test_reversao_d612_marcar_retangulo_nos_pares(janela, tmp_path):
    """D-612: com o Retângulo (ferramenta de marcar) e "Duas lado a lado", a mão desenha um
    retângulo na página da vez nos pares: a marcação ganha uma região."""
    tela = _nos_pares(janela, tmp_path, "retangulo")
    editor = tela.editor_selecao
    assert _esperar(lambda: editor._pixmap is not None)
    _lugar_da_vez(tela)
    editor.grab()
    antes = len(editor.selecao.regioes)
    a = editor._calcular_area()
    de = _no_lugar(tela, editor, QPoint(a.left() + int(a.width() * 0.3),
                                        a.top() + int(a.height() * 0.3)), 0.3, 0.3)
    _arrastar_na_tela(tela, de, 60, 60)
    assert len(editor.selecao.regioes) == antes + 1, (
        f"nada foi marcado: embaixo da mão estava {type(_alvo(tela, de)[0]).__name__}")
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert _peca_a_vista(tela, editor)


@pytest.mark.parametrize("ferramenta", ["mao", "zoom"])
def test_d612_mao_e_zoom_nos_pares_como_antes(janela, tmp_path, ferramenta):
    """Guarda (D-605): a Mão e o Zoom não marcam (só olham): nos pares eles continuam os pares
    de sempre, sem o editor de marcar por cima; clicar na outra página escolhe ela."""
    tela = _nos_pares(janela, tmp_path, ferramenta)
    assert not tela.lado_a_lado.isAncestorOf(tela.editor_selecao)
    pares = tela.lado_a_lado
    outra = next(r for i, r in pares.retangulos() if i != pares.atual and i in (1, 2))
    _arrastar_na_tela(tela, outra.translated(pares.folhas.mapTo(pares, QPoint(0, 0))).center(), 0)
    assert tela.indice_pagina == 2


def test_d612_pincel_nos_pares_a_roda_muda_a_espessura(janela, tmp_path):
    """D-600 ("a roda sozinha continua mudando o pincel") nos pares: com o Pincel, a roda em
    cima da página da vez muda a espessura; Ctrl+roda dá zoom no par (D-570)."""
    tela = _nos_pares(janela, tmp_path, "pincel")
    editor = tela.editor_selecao
    assert _esperar(lambda: editor._pixmap is not None)
    lugar = _lugar_da_vez(tela)
    alvo, ponto = _alvo(tela, lugar.center())
    assert alvo is editor or editor.isAncestorOf(alvo)
    espessura = editor.espessura
    for teclas in (Qt.NoModifier, Qt.ControlModifier):
        roda = QWheelEvent(QPointF(ponto), QPointF(alvo.mapToGlobal(ponto)), QPoint(0, 0),
                           QPoint(0, 120), Qt.NoButton, teclas, Qt.NoScrollPhase, False)
        QApplication.sendEvent(alvo, roda)
        _assentar()
        if teclas == Qt.NoModifier:
            assert editor.espessura > espessura
            assert tela.lado_a_lado.zoom == pytest.approx(1.0)
    assert tela.lado_a_lado.zoom > 1.1 and editor.zoom == pytest.approx(1.0)


# --- o que já funcionava continua ------------------------------------------------------------

@pytest.mark.parametrize("ferramenta,aba", [("cortar", "bordas"), ("endireitar", "angulo"),
                                            ("retangulo", "marcar")])
def test_d612_uma_pagina_volta_a_peca_para_o_lugar_dela(janela, tmp_path, ferramenta, aba):
    """D-605: de "Duas lado a lado" para "Uma página", a peça da ferramenta volta para o lugar de
    sempre (a área da página), à vista; e trocar de ferramenta nos pares tira a peça da anterior."""
    tela = _nos_pares(janela, tmp_path, ferramenta)
    peca = tela.editor_selecao if aba == "marcar" else tela.visualizadores[aba]
    tela.botoes_mostrar[UMA].click()
    _assentar()
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert tela.paginas_de_imagem[aba].isAncestorOf(peca) and peca.isVisible()
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    tela.escolher_ferramenta("mover")
    _assentar()
    assert not tela.lado_a_lado.isAncestorOf(peca)
    assert tela.paginas_de_imagem[aba].isAncestorOf(peca)
    assert tela.lado_a_lado.isAncestorOf(tela.visualizadores["mover"])
