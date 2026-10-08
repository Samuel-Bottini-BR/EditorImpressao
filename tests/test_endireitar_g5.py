"""A tela do endireitar (item 2.2, decisão G5 (c) do Samuel, conferência 14:
"Os dois juntos"; aparência provisória até o layout).

Testes de máquina, sem janela na tela (tests/conftest.py):
- linha-guia: a conta da correção (deitada, em pé, de qualquer lado, clique);
- visualizador: a alça gira em volta do centro, a linha-guia endireita pela
  linha desenhada, a imagem gira ao vivo e a grade fica parada; sem o ângulo
  de agora (automático ainda não medido), alça e linha não fazem nada;
- aba Endireitar: as setas de 0,1 grau giram e gravam numa ação só; o
  número digitado grava; o "aplicar em" vale para várias páginas e avisa
  quando a página da vez fica fora ("só as pares" numa ímpar).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

import numpy as np  # noqa: E402
from PySide6.QtCore import QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtTest import QTest  # noqa: E402

from core import girar  # noqa: E402
from tests.test_endireitar_na_tela import _aba_endireitar  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    app,
    janela,
    pasta,
)
from ui.widgets.visualizador import (  # noqa: E402
    MODO_ANGULO,
    Visualizador,
    correcao_da_linha_guia,
)


# ------------------------------------------------------------------ a conta da linha

@pytest.mark.parametrize("a, b, esperado", [
    ((10, 50), (210, 50), 0.0),                       # ja deitada
    ((10, 50), (210, 50 + 200 * np.tan(np.radians(2))), 2.0),     # desce: gira anti-horario
    ((210, 50), (10, 50 - 200 * np.tan(np.radians(-1.5))), -1.5),  # desenhada da direita
    ((100, 10), (100 + 200 * np.tan(np.radians(1)), 210), -1.0),   # em pe, pende 1 grau
])
def test_correcao_da_linha_guia(a, b, esperado):
    assert correcao_da_linha_guia(QPointF(*a), QPointF(*b)) == pytest.approx(esperado, abs=1e-6)


def test_clique_nao_e_linha():
    assert correcao_da_linha_guia(QPointF(10, 10), QPointF(15, 12)) is None


# ------------------------------------------------------------------ o visualizador

@pytest.fixture
def vis(app):
    v = Visualizador()
    v.resize(400, 560)
    v.definir_modo(MODO_ANGULO)
    img = np.full((700, 500, 3), 255, np.uint8)
    img[100:110, 50:450] = 0                         # uma "linha de texto"
    v.definir_imagem(img)
    v.definir_angulo(0.0, da_imagem=0.0)
    v.grab()                                         # desenha: calcula a area da pagina
    yield v
    v.deleteLater()


def _arrastar(v, de, para):
    QTest.mousePress(v, Qt.LeftButton, Qt.NoModifier, de)
    QTest.mouseMove(v, para)
    QTest.mouseRelease(v, Qt.LeftButton, Qt.NoModifier, para)


def test_alca_gira_em_volta_do_centro(vis):
    soltos = []
    vis.angulo_movido.connect(soltos.append)
    centro = QPointF(vis._area.center())
    alca = vis.centro_da_alca()
    # leva a alca 3 graus no sentido do relogio, em volta do centro
    r = np.hypot(alca.x() - centro.x(), alca.y() - centro.y())
    direcao = np.arctan2(alca.y() - centro.y(), alca.x() - centro.x()) + np.radians(3)
    destino = QPoint(round(centro.x() + r * np.cos(direcao)), round(centro.y() + r * np.sin(direcao)))
    _arrastar(vis, alca.toPoint(), destino)
    assert len(soltos) == 1
    assert soltos[0] == pytest.approx(-3.0, abs=0.3)  # horario = negativo no programa
    assert vis.giro_ao_vivo() == pytest.approx(soltos[0])


def test_linha_guia_endireita_pela_linha(vis):
    vis.definir_angulo(0.5, da_imagem=0.5)
    soltos = []
    vis.angulo_movido.connect(soltos.append)
    _arrastar(vis, QPoint(80, 200), QPoint(280, 207))   # desce 7 em 200: ~2 graus
    assert soltos == [pytest.approx(0.5 + np.degrees(np.arctan2(7, 200)), abs=0.05)]
    assert vis.linha_guia() is None


def test_clique_na_pagina_nao_muda_o_angulo(vis):
    soltos = []
    vis.angulo_movido.connect(soltos.append)
    _arrastar(vis, QPoint(150, 300), QPoint(152, 301))
    assert soltos == [] and vis.angulo == 0.0


def test_sem_o_angulo_de_agora_nada_gira(vis):
    vis.definir_angulo(None)
    assert not vis.angulo_conhecido
    soltos = []
    vis.angulo_movido.connect(soltos.append)
    _arrastar(vis, vis.centro_da_alca().toPoint(), QPoint(100, 100))
    _arrastar(vis, QPoint(80, 200), QPoint(280, 230))
    assert soltos == []


def test_a_imagem_gira_ao_vivo_e_a_grade_fica(vis):
    reta = vis.grab().toImage()
    vis.definir_angulo(4.0)                          # a imagem ainda e a de 0 grau
    assert vis.giro_ao_vivo() == pytest.approx(4.0)
    torta = vis.grab().toImage()
    assert reta != torta
    vis.definir_angulo(4.0, da_imagem=4.0)            # chegou a imagem nova
    assert vis.giro_ao_vivo() == 0.0


# ------------------------------------------------------------------ a aba Endireitar

def test_setas_giram_e_gravam_numa_acao_so(janela, pasta):
    tela = _aba_endireitar(janela, pasta)
    pagina = janela.projeto.paginas[0]
    tela._angulo_zero()                              # angulo conhecido: 0
    assert pagina.angulo_manual == 0.0
    assert tela.botao_angulo_anti_horario.isEnabled()
    acoes_antes = len(tela.acoes.feitas)
    for _ in range(3):
        tela.botao_angulo_anti_horario.click()
    tela.botao_angulo_horario.click()
    vis = tela.visualizadores["angulo"]
    assert vis.angulo == pytest.approx(0.2)
    assert pagina.angulo_manual == 0.0               # ainda nao gravou
    assert tela.campo_angulo.value() == pytest.approx(0.2)
    tela._gravar_angulo_timer.timeout.emit()         # o instante depois do ultimo clique
    assert pagina.angulo_manual == pytest.approx(0.2)
    assert len(tela.acoes.feitas) == acoes_antes + 1
    tela.desfazer()
    assert pagina.angulo_manual == 0.0


def test_numero_digitado_grava(janela, pasta):
    tela = _aba_endireitar(janela, pasta)
    tela._angulo_zero()
    tela.campo_angulo.setValue(-1.25)
    tela.campo_angulo.editingFinished.emit()
    assert janela.projeto.paginas[0].angulo_manual == pytest.approx(-1.25)


def test_aplicar_em_todas_e_so_as_pares_numa_impar(janela, pasta):
    tela = _aba_endireitar(janela, pasta)
    projeto = janela.projeto
    combo = tela.combo_alcance_do_angulo
    combo.setCurrentIndex(combo.findData(girar.ALCANCE_TODAS))
    tela._angulo_zero()
    assert [p.angulo_manual for p in projeto.paginas] == [0.0] * len(projeto.paginas)
    assert not any(p.revisada for p in projeto.paginas[1:])   # so a da vez fica conferida
    tela._angulo_automatico()
    assert all(p.angulo_manual is None for p in projeto.paginas)
    # "so as pares" na pagina 1: avisa e nada muda
    combo.setCurrentIndex(combo.findData(girar.ALCANCE_PARES))
    tela._angulo_zero()
    assert all(p.angulo_manual is None for p in projeto.paginas)
    assert janela.avisos and "página ímpar" in janela.avisos[-1]
