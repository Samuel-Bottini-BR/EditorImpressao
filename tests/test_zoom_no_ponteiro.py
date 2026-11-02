"""Provas de dois consertos da área de trabalho (01/11/2026; CLAUDE.md §4.7: falham no código de
antes, `obra-2026-10-26` = 6b4e4f9, e passam no novo).

  Bug de 31/10/2026 (D-577, 4º teste do Samuel, na versão de teste): "mesmo assim, na area de
      trabalho o zoom se comporta sozinho, porque ele se direciona somente para o centro da pagina
      e não onde o mouse está, que é como o zoom se comporta em outros lugares no programa."
      Na área de trabalho, Ctrl + roda (D-568) dava zoom a partir do centro; agora o ponto da
      página debaixo do mouse continua debaixo dele, na "Uma página" (a Mão e as ferramentas de
      página) e no "Duas lado a lado" (D-570). Os botões "–" / "+" continuam pelo centro, e a roda
      sem Ctrl continua como a D-568 manda (sem zoom troca de página; com zoom anda pela página).

  Bug de 31/10/2026 (print do Samuel, janela 1280 x 657): no painel Filtro, parte "Mais ajustes",
      os nomes apareciam cortados: "Igual" ("Igualar a luz da página"), "Suavi" ("Suavizar as
      letras"), "Tirar o chu" ("Tirar o chuvisco"). Agora aparecem inteiros, com os mesmos nomes e
      os mesmos controles.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_9b2 import _aberto, _dividido, _pdf, app, janela, pasta  # noqa: E402,F401


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _roda_em(vista, x: float, y: float, passos: int = 1, ctrl: bool = True,
             shift: bool = False) -> None:
    """Uma volta da roda do mouse com o ponteiro em (x, y) da `vista` (como o Windows manda)."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    teclas = Qt.NoModifier
    if ctrl:
        teclas |= Qt.ControlModifier
    if shift:
        teclas |= Qt.ShiftModifier
    ponto = QPointF(x, y)
    evento = QWheelEvent(ponto, vista.mapToGlobal(ponto), QPoint(0, 0), QPoint(0, 120 * passos),
                         Qt.NoButton, teclas, Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


def _area_da_pagina(vista):
    """Onde a página está desenhada agora na vista (a conta do desenho de cada uma)."""
    if hasattr(vista, "_calcular_area"):                 # o editor de marcar (a Mão)
        return vista._calcular_area()
    vista.repaint()                                      # o Visualizador guarda no desenho
    return vista._area


def _na_pagina(vista, x: float, y: float) -> tuple[float, float]:
    """O ponto (x, y) da tela em fração da página (0 a 1)."""
    area = _area_da_pagina(vista)
    return (x - area.left()) / area.width(), (y - area.top()) / area.height()


# --- conserto 1: o zoom vai para onde está o mouse -------------------------------------------

@pytest.mark.parametrize("ferramenta", ["mao", "endireitar"])
def test_bug_31_10_ctrl_roda_na_uma_pagina_vai_para_onde_esta_o_mouse(janela, tmp_path, ferramenta):
    """Bug de 31/10/2026 (consertado em 01/11/2026): "o zoom [...] se direciona somente para o
    centro da pagina e não onde o mouse está". Na "Uma página", com o ponteiro longe do meio
    (em cima, à esquerda), Ctrl + roda aumenta (D-568) e o ponto da página debaixo do ponteiro
    continua debaixo dele: de 100% e de novo já com zoom, e também com três voltas seguidas sem
    a tela se redesenhar no meio (D-026: zoom confiável). Na Mão (o editor de marcar) e numa
    ferramenta de página (Endireitar). Os botões "–" / "+" continuam pelo centro. Falha no
    código de antes: a página crescia a partir do meio e o ponto saía de baixo do ponteiro."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta(ferramenta)
    tela.ir_para_pagina(4)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    vista = tela.editor_selecao if ferramenta == "mao" else tela.visualizadores["angulo"]
    _esperar(lambda: getattr(vista, "_pixmap", None) is not None, motivo="a prévia")
    assert abs(vista.zoom - 1.0) < 1e-6
    area = _area_da_pagina(vista)
    x, y = area.left() + 0.25 * area.width(), area.top() + 0.3 * area.height()
    antes = _na_pagina(vista, x, y)

    _roda_em(vista, x, y)                                 # de 100% para mais
    assert vista.zoom > 1.2 and tela.indice_pagina == 4
    assert tela.rotulo_do_zoom.text() == f"{round(vista.zoom * 100)}%"
    depois = _na_pagina(vista, x, y)
    largura, altura = _area_da_pagina(vista).width(), _area_da_pagina(vista).height()
    assert abs(depois[0] - antes[0]) * largura <= 2 and abs(depois[1] - antes[1]) * altura <= 2, \
        f"o ponto debaixo do mouse saiu do lugar: {antes} -> {depois}"

    for _ in range(3):                                    # três voltas, sem redesenhar no meio
        _roda_em(vista, x, y)
    depois = _na_pagina(vista, x, y)
    largura, altura = _area_da_pagina(vista).width(), _area_da_pagina(vista).height()
    assert abs(depois[0] - antes[0]) * largura <= 3 and abs(depois[1] - antes[1]) * altura <= 3, \
        f"o ponto debaixo do mouse saiu do lugar: {antes} -> {depois}"

    _roda_em(vista, x, y, passos=-1)                      # para menos, ainda com zoom
    assert vista.zoom > 1.0
    depois = _na_pagina(vista, x, y)
    largura, altura = _area_da_pagina(vista).width(), _area_da_pagina(vista).height()
    assert abs(depois[0] - antes[0]) * largura <= 3 and abs(depois[1] - antes[1]) * altura <= 3

    # os botões (sem mouse) continuam pelo centro: o meio da página fica no meio
    tela.mudar_o_zoom(None)
    assert vista.zoom == 1.0 and (vista.deslocamento.x(), vista.deslocamento.y()) == (0, 0)
    tela.botao_mais_zoom.click()
    assert (vista.deslocamento.x(), vista.deslocamento.y()) == (0, 0)


def test_bug_31_10_ctrl_roda_no_lado_a_lado_vai_para_onde_esta_o_mouse(janela, tmp_path):
    """Bug de 31/10/2026 (consertado em 01/11/2026), no "Duas lado a lado" (D-570: "Sim, zoom
    também no lado a lado"): com o ponteiro numa página do par, longe do meio, Ctrl + roda
    aumenta e o ponto da página debaixo do ponteiro continua debaixo dele (o rolar anda o que
    for preciso). O "+" da barra de baixo continua pelo centro. Falha no código de antes: o
    zoom punha o par no meio da largura e o alto da página da vez no alto da tela."""
    from PySide6.QtCore import QPoint, QPointF

    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.ir_para_pagina(4)
    tela.definir_mostrar(DUAS)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    pares = tela.lado_a_lado
    porta = pares.viewport()
    # as prévias à vista chegaram (cada uma acerta a proporção da sua página e a arrumação é
    # refeita: só depois disso o lugar das páginas é o de verdade)
    _esperar(lambda: pares.atual in pares.guardadas and not pares._refazer.isActive(),
             motivo="as prévias do lado a lado")
    _assentar(10)
    pares.ir_para(pares.atual)                            # a janela já tem o tamanho de verdade
    _assentar()
    # a página da vez (à vista, o alto dela no alto da tela)
    posicao = pares.atual
    ret = next(r for p, r in pares.retangulos_exatos() if p == posicao)
    no_conteudo = QPointF(ret.left() + 0.3 * ret.width(), ret.top() + 0.35 * ret.height())
    ponto = pares.folhas.mapTo(porta, no_conteudo.toPoint())
    fx = (no_conteudo.x() - ret.left()) / ret.width()
    fy = (no_conteudo.y() - ret.top()) / ret.height()
    assert porta.rect().contains(ponto), f"o ponteiro precisa estar na página à vista: {ponto}"

    for passo in range(1, 4):
        _roda_em(porta, ponto.x(), ponto.y())
        _assentar()
        assert pares.zoom > 1.2 ** passo
        assert tela.rotulo_do_zoom.text() == f"{round(pares.zoom * 100)}%"
        novo = next(r for p, r in pares.retangulos_exatos() if p == posicao)
        agora = pares.folhas.mapTo(porta, QPoint(round(novo.left() + fx * novo.width()),
                                                   round(novo.top() + fy * novo.height())))
        assert abs(agora.x() - ponto.x()) <= 2 and abs(agora.y() - ponto.y()) <= 2, \
            f"o ponto debaixo do mouse saiu do lugar: {ponto} -> {agora} (zoom {pares.zoom:.2f})"

    # o "+" da barra de baixo continua pelo centro (o par no meio da largura)
    tela.botao_ajustar_a_tela.click()
    _assentar()
    tela.botao_mais_zoom.click()
    _assentar()
    barra = pares.horizontalScrollBar()
    assert abs(barra.value() - (barra.maximum() + barra.minimum()) // 2) <= 1


def test_bug_01_11_shift_roda_no_lado_a_lado_com_zoom_anda_para_os_lados(janela, tmp_path):
    """Defeito de 01/11/2026 (Samuel, testando a junção d6d6e6f: "funciona o zoom mas com shift
    para os lados não funciona ele rola as paginas para pagina, no caso troca de pagina."). No
    "Duas lado a lado", COM zoom, Shift + roda anda pelo par para os lados (D-568: com zoom a
    roda anda pela página, Shift para os lados, como na "Uma página"): a barra de baixo anda,
    o rolar de cima para baixo e a página da vez ficam onde estavam; roda para cima volta.
    Sem Shift, a roda continua rolando para cima e para baixo. Falha no código de antes
    (a6b9e02): o Shift + roda rolava as páginas (de cima para baixo) e trocava a página."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.ir_para_pagina(4)
    tela.definir_mostrar(DUAS)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    pares = tela.lado_a_lado
    porta = pares.viewport()
    _esperar(lambda: pares.atual in pares.guardadas and not pares._refazer.isActive(),
             motivo="as prévias do lado a lado")
    _assentar(10)
    tela.botao_mais_zoom.click()
    tela.botao_mais_zoom.click()
    _assentar()
    assert pares.zoom > 1.5
    deitada, de_pe = pares.horizontalScrollBar(), pares.verticalScrollBar()
    assert deitada.maximum() > 0
    x, y, pagina = deitada.value(), de_pe.value(), tela.indice_pagina
    meio_x, meio_y = porta.width() / 2, porta.height() / 2

    _roda_em(porta, meio_x, meio_y, passos=-1, ctrl=False, shift=True)
    _assentar()
    assert deitada.value() > x, "Shift + roda para baixo não andou para a direita"
    assert de_pe.value() == y and tela.indice_pagina == pagina, "Shift + roda rolou as páginas"
    andou = deitada.value()
    _roda_em(porta, meio_x, meio_y, passos=1, ctrl=False, shift=True)
    _assentar()
    assert deitada.value() < andou and de_pe.value() == y and tela.indice_pagina == pagina

    _roda_em(porta, meio_x, meio_y, passos=-1, ctrl=False)    # sem Shift: rola para baixo
    _assentar()
    assert de_pe.value() > y


# --- conserto 2: os nomes inteiros no "Mais ajustes" -----------------------------------------

LETRA_DO_WINDOWS = Path("C:/Windows/Fonts/segoeui.ttf")


@pytest.fixture
def letra_do_windows(app):
    """A letra da tela do Windows (Segoe UI, a do estilo do programa) também nos testes sem
    janela: sem ela, o Qt "offscreen" mede cada letra do tamanho de um quadrado (o nome
    "Igualar a luz da página" daria 373 pontos em vez de 178) e a medida não vale nada. Sai no
    fim, para não mudar as medidas dos outros testes."""
    from PySide6.QtGui import QFontDatabase

    if not LETRA_DO_WINDOWS.exists():
        pytest.skip("sem a letra Segoe UI (este teste é do Windows)")
    numero = QFontDatabase.addApplicationFont(str(LETRA_DO_WINDOWS))
    yield
    if numero >= 0:
        QFontDatabase.removeApplicationFont(numero)


def test_bug_31_10_nomes_inteiros_no_mais_ajustes_do_painel_filtro(letra_do_windows, janela, tmp_path):
    """Bug de 31/10/2026 (consertado em 01/11/2026): no print do Samuel (janela 1280 x 657), no
    painel Filtro, parte "Mais ajustes", os nomes saíam cortados: "Igual" ("Igualar a luz da
    página"), "Suavi" ("Suavizar as letras"), "Tirar o chu" ("Tirar o chuvisco"). Com o Preto e
    branco (o filtro em que todos aparecem) e a parte aberta, cada nome tem o espaço do texto
    inteiro e cabe na largura do painel; os nomes e os controles são os mesmos. Falha no código
    de antes: os três ficavam na mesma linha, espremidos."""
    from PySide6.QtCore import QPoint

    from core import luz_scantailor
    from core.filtros import PRETO_E_BRANCO
    from tests.ajudante_do_automatico import rodar_como_o_conferir
    from ui.tela_conferir import PAINEL_FILTRO

    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto(f) for f in range(2)]))
    assert rodar_como_o_conferir(janela, limpar=True, filtro_padrao=PRETO_E_BRANCO)
    tela = janela.tela_conferir
    tela.escolher_ferramenta("zoom")
    tela.ir_para_pagina(0)
    tela.paineis.abrir(PAINEL_FILTRO)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    painel = tela.paineis.filtro_da_pagina
    painel.filtro_escolhido.emit(PRETO_E_BRANCO)
    painel.partes["mais"].abrir(True)
    _assentar(10)
    assert tela.projeto.paginas[0].filtro == PRETO_E_BRANCO

    nomes = {tela.caixa_luz_igualar: luz_scantailor.ROTULO_IGUALAR,
             tela.caixa_luz_suavizar: luz_scantailor.ROTULO_SUAVIZAR,
             tela.rotulo_luz_chuvisco: luz_scantailor.ROTULO_CHUVISCO + ":"}
    porta = painel.rolagem.viewport()
    for controle, nome in nomes.items():
        assert controle.text() == nome                    # o nome é o mesmo
        assert controle.isVisible(), nome
        preciso = controle.sizeHint().width()             # o texto inteiro (e o quadradinho)
        assert controle.width() >= preciso, \
            f"“{nome}” cortado: {controle.width()} de {preciso} pontos"
        direita = controle.mapTo(porta, QPoint(controle.width(), 0)).x()
        assert direita <= porta.width(), f"“{nome}” passa da largura do painel"
    # o "Tirar o chuvisco" continua com o número ao lado, inteiro também
    seletor = tela.seletor_luz_chuvisco
    assert seletor.isVisible() and seletor.width() >= seletor.minimumSizeHint().width()
    assert seletor.mapTo(porta, QPoint(seletor.width(), 0)).x() <= porta.width()
