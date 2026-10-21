"""O livro aberto na tela inteira (etapa 7 do layout; rodada 6 e escolhas de 06/10; rodada 7, 201 B e
202 A): as folhas rolando, "Ver lado a lado" em pares com a 1 sozinha, e o folhear que só desenha
o que aparece (nunca o livro inteiro na memória)."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

fitz = pytest.importorskip("fitz")

from tests.test_gravura_na_aba_marcar import app  # noqa: F401, E402 - fixture


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(30):
        pagina = doc.new_page(width=400, height=600)
        pagina.insert_text((50, 80), f"folha {i + 1}", fontsize=30)
    doc.save(str(caminho))
    doc.close()
    return caminho


def test_folhas_rolando_e_lado_a_lado(app, livro):  # noqa: F811
    from ui.widgets.paginas_rolando import PaginasRolando

    vista = PaginasRolando()
    vista.resize(900, 600)
    vista.abrir(str(livro))
    assert vista.total() == 30
    ret = dict(vista.retangulos())
    assert ret[0].top() < ret[1].top(), "uma embaixo da outra"
    vista.definir_lado_a_lado(True)
    ret = dict(vista.retangulos())
    assert ret[1].top() == ret[2].top() and ret[1].left() < ret[2].left(), "2 e 3 lado a lado"
    assert ret[0].top() < ret[1].top() and ret[0].left() >= ret[1].right() - 1, \
        "a folha 1 sozinha, à direita, como num livro"
    vista.ir_para(20)
    assert vista.atual == 20
    vista.parar()


def test_so_guarda_algumas_folhas(app, livro):  # noqa: F811
    from ui.widgets import paginas_rolando as pr
    import numpy as np

    vista = pr.PaginasRolando()
    vista.abrir(str(livro))
    for i in range(30):
        vista._chegou(i, np.zeros((20, 14, 3), dtype=np.uint8))
    assert len(vista.guardadas) <= pr.MAXIMO_GUARDADAS
    vista.parar()


def test_a_folha_e_desenhada_na_resolucao_da_tela(app, livro):  # noqa: F811
    """Verificador, 21/10/2026: no livro aberto, uma página por vez, a página
    saía borrada (desenhada a 70 DPI fixo e aumentada na tela). A folha
    desenhada tem de ter pelo menos a largura, em pixels, que ocupa na tela."""
    import time

    from PySide6.QtWidgets import QApplication

    from ui.widgets.paginas_rolando import PaginasRolando

    vista = PaginasRolando()
    vista.resize(900, 600)
    vista.abrir(str(livro))
    vista.ir_para(0)
    fim = time.time() + 15
    while 0 not in vista.guardadas and time.time() < fim:
        QApplication.processEvents()
        time.sleep(0.02)
    assert 0 in vista.guardadas
    assert vista.guardadas[0].width() >= vista.pixels_necessarios(0) * 0.95, \
        f"{vista.guardadas[0].width()} pixels para {vista.pixels_necessarios(0)} na tela"
    vista.parar()


def test_a_grade_desenha_na_altura_do_quadro(app, livro):  # noqa: F811
    """Verificador, 21/10/2026: a grade "Todas as páginas" saía mole (DPI fixo).
    Cada folha sai com a altura, em pixels, que o quadro precisa."""
    from ui.widgets import todas_as_paginas as tp

    recebidas = []
    sinais = tp._Sinais()
    sinais.pronta.connect(lambda folha, img: recebidas.append(img))
    tp._TarefaDasFolhas(str(livro), [0], sinais, altura_px=420).run()
    assert recebidas and recebidas[0].shape[0] >= 400
