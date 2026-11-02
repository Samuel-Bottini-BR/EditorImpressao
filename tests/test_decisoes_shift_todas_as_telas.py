"""As provas de comportamento da D-600: Shift + roda move a imagem para os lados em todas as
telas que mostram página com zoom (CLAUDE.md §11, regra 4; Livro de decisões,
docs/plano/DECISOES.md).

  D-600 (02/11/2026). Samuel, testando a D-599: "3- shift não funciona no automatico para mover
      para o lado. No duas paginas lado a lado está funcionando" · "e no automatico pode colocar
      o shift tambem, o shift tem que funcionar em todas as telas".
      No Livro: "Shift + roda move a imagem para os lados em todas as telas do programa que
      mostram página com zoom (área de trabalho, "antes e depois" do Automático e as outras),
      como já faz no "Duas lado a lado"."

O que se mede, em cada tela, com a imagem mais larga que o espaço dela: depois de Shift + roda,
a barra de rolar de baixo (ou, no Visualizador, o deslocamento para os lados) andou; a altura,
o zoom e a página da vez ficaram onde estavam; roda para cima volta. E a roda sem Shift continua
fazendo o que fazia (na janela do Automático e no "Ver de perto", dar zoom; D-577).
A área de trabalho ("Uma página" e "Duas lado a lado", D-599) tem as provas dela em
tests/test_decisoes_9b2.py e tests/test_zoom_no_ponteiro.py.

Teste de reversão (§4.7): no código de antes (`091b200`), no Automático o Shift + roda dava zoom
(a imagem não ia para os lados), no "Ver de perto" e no "comparar" também, e no livro aberto
descia a página inteira.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_automatico_ver_como_fica import (  # noqa: E402,F401 - fixtures
    _abrir,
    _assentar,
    _esperar,
    _livro,
    app,
    janela,
    pasta,
)


def _roda(vista, ponto, passos: int = -1, shift: bool = True) -> None:
    """Um dente da roda do mouse em `ponto` da `vista` (120 = um dente, como no Windows; para
    baixo é negativo), com o Shift apertado ou não. O Windows manda o Shift + roda como roda de
    cima para baixo (angleDelta em y) com o Shift nas teclas."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    teclas = Qt.ShiftModifier if shift else Qt.NoModifier
    evento = QWheelEvent(QPointF(ponto), QPointF(vista.mapToGlobal(QPoint(int(ponto.x()), int(ponto.y())))),
                         QPoint(0, 0), QPoint(0, 120 * passos), Qt.NoButton, teclas,
                         Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


# --- o Automático: "A página, antes e depois" e a tela cheia dele ------------------------------

@pytest.mark.parametrize("onde", ["pagina da direita", "tela cheia"])
def test_d600_automatico_antes_e_depois_shift_roda_anda_para_os_lados(janela, app, tmp_path, onde):
    """D-600: "shift não funciona no automatico para mover para o lado" · "o shift tem que
    funcionar em todas as telas". Na janela grande do Automático, na "A página, antes e depois"
    (a coluna da direita) e na tela cheia dela, com zoom: Shift + roda para baixo anda para a
    direita (a barra de baixo anda), sem mudar a altura, o zoom nem a página; para cima volta.
    A roda sem Shift continua dando zoom (D-577). Falha no código de antes: o Shift + roda dava
    zoom."""
    from PySide6.QtWidgets import QApplication

    grande = _abrir(janela, app, tmp_path, pagina=1)
    grande.resize(1400, 800)
    grande.show()
    _assentar(app)
    painel = grande.antes_e_depois
    if onde == "tela cheia":
        painel.botao_tela_cheia.click()
        _assentar(app)
        painel.tela_cheia.resize(1400, 850)
        _assentar(app)
        vista = painel.tela_cheia.visor
    else:
        vista = painel.visor
    vista.definir_zoom(2.0)
    QApplication.sendPostedEvents(vista.rolagem)
    _assentar(app)
    deitada, de_pe = vista.rolagem.horizontalScrollBar(), vista.rolagem.verticalScrollBar()
    assert deitada.maximum() > 0, "com zoom 2 a página devia ser mais larga que o espaço"
    deitada.setValue(deitada.maximum() // 2)              # no meio: dá para ir para os dois lados
    x, y, zoom, pagina = deitada.value(), de_pe.value(), vista.zoom, painel._indice
    porta = vista.rolagem.viewport()
    ponto = vista.mapFrom(porta, porta.rect().center())   # o ponteiro no meio da tela

    _roda(vista, ponto, passos=-1)
    _assentar(app)
    assert vista.zoom == zoom, f"{onde}: o Shift + roda deu zoom ({zoom} -> {vista.zoom})"
    assert deitada.value() > x, f"{onde}: Shift + roda para baixo não andou para a direita"
    assert de_pe.value() == y and painel._indice == pagina, f"{onde}: andou para cima/baixo ou trocou de página"
    andou = deitada.value()
    ponto = vista.mapFrom(porta, porta.rect().center())
    _roda(vista, ponto, passos=1)
    _assentar(app)
    assert deitada.value() < andou and de_pe.value() == y and vista.zoom == zoom

    # a roda sem Shift continua dando zoom (D-577)
    ponto = vista.mapFrom(porta, porta.rect().center())
    _roda(vista, ponto, passos=1, shift=False)
    _assentar(app)
    assert vista.zoom > zoom, f"{onde}: a roda sem Shift não deu mais zoom"


def test_d600_comparar_da_tela_cheia_do_automatico_shift_roda_anda_para_os_lados(janela, app, tmp_path):
    """D-600 no "comparar" da tela cheia do Automático (duas telas, o zoom e a posição andam
    juntos, D-577): com zoom, Shift + roda na tela da esquerda leva a página para os lados nas
    duas, sem mudar a altura nem o zoom; para cima volta. Falha no código de antes: dava zoom."""
    grande = _abrir(janela, app, tmp_path, pagina=1)
    grande.resize(1400, 800)
    grande.show()
    _assentar(app)
    painel = grande.antes_e_depois
    painel.botao_tela_cheia.click()
    _assentar(app)
    tela = painel.tela_cheia
    tela.resize(1400, 850)
    tela.botao_comparar.click()
    _esperar(app, painel)
    _assentar(app)
    a, b = tela.vista_a, tela.vista_b
    assert a._pixmap is not None and b._pixmap is not None
    a.definir_zoom(3.0)
    _assentar(app)
    assert a._largura_base() * a.zoom > a.width(), "com zoom 3 a página devia passar da largura"
    x, y, zoom = a.deslocamento.x(), a.deslocamento.y(), a.zoom

    _roda(a, a.rect().center(), passos=-1)
    _assentar(app)
    assert a.zoom == zoom and b.zoom == zoom, "o Shift + roda deu zoom"
    assert a.deslocamento.x() < x, "Shift + roda para baixo não levou a página para a esquerda (ver a direita)"
    assert a.deslocamento.y() == y
    assert b.deslocamento == a.deslocamento, "a tela da direita não acompanhou"
    andou = a.deslocamento.x()
    _roda(b, b.rect().center(), passos=1)                  # na da direita também
    _assentar(app)
    assert a.deslocamento.x() > andou and a.deslocamento == b.deslocamento and a.zoom == zoom


# --- o "Ver de perto" (ui/tela_ampliada.py) ------------------------------------------------------

def _ver_de_perto(janela, app, tmp_path):
    """O livro aberto na área de trabalho e o "Ver de perto" (sem o exec, que prende o teste),
    com a página à vista."""
    import time

    from ui.tela_ampliada import MODO_FILTRO, TelaAmpliada

    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    ampliada = TelaAmpliada(tela, modo=MODO_FILTRO, parent=janela)
    ampliada.resize(1280, 860)
    ampliada.show()
    fim = time.monotonic() + 60
    while ampliada.vista._pixmap is None and time.monotonic() < fim:
        _assentar(app)
        time.sleep(0.02)
    assert ampliada.vista._pixmap is not None, "a página do \"Ver de perto\" não chegou"
    _assentar(app)
    return tela, ampliada


def test_d600_ver_de_perto_shift_roda_anda_para_os_lados(janela, app, tmp_path):
    """D-600 no "Ver de perto": com zoom, Shift + roda leva a página para os lados (para baixo:
    ver o que está à direita), sem mudar a altura, o zoom nem a página; para cima volta. A roda
    sem Shift continua dando zoom. No "comparar" dele as duas telas andam juntas. Falha no
    código de antes: o Shift + roda dava zoom."""
    tela, ampliada = _ver_de_perto(janela, app, tmp_path)
    try:
        vista = ampliada.vista
        # o zoom que deixa a página com o dobro da largura da tela (a janela pode ser larga)
        vista.definir_zoom(min(7.0, max(2.0, 2.0 * vista.width() / vista._largura_base())))
        _assentar(app)
        assert vista._largura_base() * vista.zoom > vista.width()
        x, y, zoom, pagina = vista.deslocamento.x(), vista.deslocamento.y(), vista.zoom, tela.indice_pagina

        _roda(vista, vista.rect().center(), passos=-1)
        _assentar(app)
        assert vista.zoom == zoom, f"o Shift + roda deu zoom ({zoom} -> {vista.zoom})"
        assert vista.deslocamento.x() < x and vista.deslocamento.y() == y
        assert tela.indice_pagina == pagina
        andou = vista.deslocamento.x()
        _roda(vista, vista.rect().center(), passos=1)
        _assentar(app)
        assert vista.deslocamento.x() > andou and vista.zoom == zoom

        # o "comparar": a de baixo acompanha
        ampliada.botao_comparar.setChecked(True)
        ampliada._alternar_comparar()
        _assentar(app)
        outra = ampliada.vista_b
        antes = vista.deslocamento.x()
        _roda(vista, vista.rect().center(), passos=-1)
        _assentar(app)
        assert vista.deslocamento.x() < antes and outra.deslocamento == vista.deslocamento

        # a roda sem Shift continua dando zoom
        _roda(vista, vista.rect().center(), passos=1, shift=False)
        _assentar(app)
        assert vista.zoom > zoom

        # com zoom, uma página ainda mais estreita que a vista também anda (D-599, a mesma
        # regra da área de trabalho): o Shift + roda não dá zoom (no print de 02/11, com zoom
        # 3 no "Ver de perto" largo, ele afastava a página)
        ampliada.botao_comparar.setChecked(False)
        ampliada._alternar_comparar()
        _assentar(app)
        vista.ajustar_a_tela()
        vista.definir_zoom(1.5)
        _assentar(app)
        assert vista._largura_base() * vista.zoom < vista.width(), "a página devia caber de lado"
        antes = vista.deslocamento.x()
        _roda(vista, vista.rect().center(), passos=-1)
        _assentar(app)
        assert vista.zoom == 1.5, f"página estreita com zoom: o Shift + roda deu zoom ({vista.zoom})"
        assert vista.deslocamento.x() < antes
    finally:
        ampliada.close()


# --- a área de trabalho, ferramentas de marcar (ui/tela_conferir._roda_na_pagina) ---------------

@pytest.mark.parametrize("ferramenta", ["pincel", "varinha", "retangulo", "laco"])
def test_d600_marcar_com_zoom_shift_roda_anda_para_os_lados(janela, app, tmp_path, ferramenta):
    """D-600, pergunta 2 do ONDE-PAREI (02/11/2026): "Quer que o Shift + roda leve a página para
    os lados também nessas ferramentas (a roda sozinha continua mudando o pincel)?" → Samuel:
    "sim". Na área de trabalho, com zoom e uma ferramenta de marcar, Shift + roda para baixo
    leva a página para a esquerda (ver o que está à direita), sem mudar a altura, o zoom, a
    página, o tamanho do pincel nem a tolerância da varinha; para cima volta. A roda sozinha
    continua da ferramenta (D-568: o Pincel muda de tamanho). Falha no código de antes: o
    Shift + roda não andava (no Pincel mudava o tamanho, no Retângulo não fazia nada)."""
    import time

    janela.abrir_livro(_livro(tmp_path))
    _assentar(app)
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    tela.escolher_ferramenta(ferramenta)
    janela.show()
    janela.move(-3000, -3000)
    editor = tela.editor_selecao
    fim = time.monotonic() + 60
    while editor._pixmap is None and time.monotonic() < fim:
        _assentar(app)
        time.sleep(0.02)
    assert editor._pixmap is not None, "a página não chegou ao editor de marcar"
    assert editor.ferramenta == ferramenta
    tela.botao_mais_zoom.click()
    tela.botao_mais_zoom.click()
    _assentar(app)
    assert editor.zoom > 1.2
    x, y, zoom, pagina = editor.deslocamento.x(), editor.deslocamento.y(), editor.zoom, tela.indice_pagina
    espessura, tolerancia = editor.espessura, editor.tolerancia
    meio = editor.rect().center()

    _roda(editor, meio, passos=-1)
    _assentar(app)
    assert editor.deslocamento.x() < x, f"{ferramenta}: Shift + roda para baixo não andou para os lados"
    assert editor.deslocamento.y() == y and editor.zoom == zoom and tela.indice_pagina == pagina
    assert editor.espessura == espessura and editor.tolerancia == tolerancia, \
        f"{ferramenta}: o Shift + roda mexeu no pincel ou na tolerância"
    andou = editor.deslocamento.x()
    _roda(editor, meio, passos=1)
    _assentar(app)
    assert editor.deslocamento.x() > andou and editor.zoom == zoom

    if ferramenta == "pincel":                             # a roda sozinha continua do pincel
        _roda(editor, meio, passos=1, shift=False)
        _assentar(app)
        assert editor.espessura != espessura and editor.zoom == zoom


# --- o livro aberto (ui/tela_inicio.LivroAberto, ui/widgets/paginas_rolando.py) -----------------

@pytest.mark.parametrize("continuo", [True, False])
def test_d600_livro_aberto_pagina_mais_larga_shift_roda_anda_para_os_lados(app, tmp_path, continuo):
    """D-600 no livro aberto: no "Tamanho real", uma página mais larga que a tela; Shift + roda
    anda para os lados (a barra de baixo), sem descer a página nem trocar de folha, com o
    "Rolar sem parar" ligado ou não; para cima volta. A roda sem Shift continua descendo.
    Falha no código de antes: o Shift + roda descia a tela inteira (o rolar padrão do Qt)."""
    from PySide6.QtCore import QPointF

    from ui.widgets import paginas_rolando as pr

    caminho = tmp_path / "largo.pdf"
    doc = fitz.open()
    for i in range(4):
        doc.new_page(width=1400, height=1000).insert_text((50, 80), f"folha {i + 1}", fontsize=30)
    doc.save(str(caminho))
    doc.close()
    vista = pr.PaginasRolando()
    try:
        vista.resize(700, 500)
        vista.show()
        vista.move(-3000, -3000)
        vista.abrir(str(caminho))
        vista.definir_jeito(caber=pr.TAMANHO_REAL, continuo=continuo)
        vista.ir_para(1)
        _assentar(app)
        deitada, de_pe = vista.horizontalScrollBar(), vista.verticalScrollBar()
        assert deitada.maximum() > 0, "a página devia ser mais larga que a tela"
        deitada.setValue(deitada.maximum() // 2)
        de_pe.setValue(min(de_pe.maximum(), de_pe.value() + 40))   # longe do começo e do fim
        x, y, folha = deitada.value(), de_pe.value(), vista.atual
        porta = vista.viewport()
        meio = QPointF(porta.rect().center())

        _roda(porta, meio, passos=-1)
        _assentar(app)
        assert deitada.value() > x, "Shift + roda para baixo não andou para a direita"
        assert de_pe.value() == y and vista.atual == folha, "Shift + roda desceu ou trocou de folha"
        andou = deitada.value()
        _roda(porta, meio, passos=1)
        _assentar(app)
        assert deitada.value() < andou and de_pe.value() == y and vista.atual == folha

        _roda(porta, meio, passos=-1, shift=False)       # sem Shift: desce, como sempre
        _assentar(app)
        assert de_pe.value() > y or vista.atual != folha
    finally:
        vista.parar()
