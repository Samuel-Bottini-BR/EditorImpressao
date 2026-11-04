"""D-612 (04/11/2026): a ferramenta Mover funciona também com a vista em "Duas lado a lado".

Pergunta no chat: "Ao escolher Mover, Cortar, Endireitar ou marcar, a tela passa sozinha para Uma
página? É isso que destrava o Mover. Sugiro que sim." → Samuel: "1 - ele tem que funcionar com
paginas lado a lado também". Na prática (Livro de decisões): o Mover (arrastar, puxar o canto, o
número do tamanho) funciona também com a vista em "Duas lado a lado", nas páginas dos pares; a vista
NÃO muda sozinha. Cortar, Endireitar, marcar e o "antes / depois" ficam como estão (perguntado).

O defeito (Samuel, 04/11/2026, Gradus Primus: "mover e dimensionar para de funcionar em algumas
situações"; achado do agente mover-parou, relatorios/mover-parou/ONDE-PAREI.md): com a vista em
"Duas lado a lado" (por exemplo vindo do Dividir, onde a frase manda escolher "Duas lado a lado"
para arrastar a linha), a tecla F mostrava os pares no lugar da página e o arrasto não chegava ao
Mover: a página não andava. Em `dd7a648c` estes testes de reversão falham.

Diferença para tests/test_decisoes_mover.py: lá o arrasto é mandado DIRETO ao visualizador do
Mover, mesmo escondido. Aqui o arrasto vai para o que está NA TELA embaixo do ponto (o widget mais
de dentro, como a mão do Samuel), no meio da página da vez dentro dos pares.

Decisões tocadas (as provas antigas continuam nos arquivos delas): D-008 e D-541 (arrastar, canto,
número; a vista se ajusta), D-540 (tecla F), D-006/D-015 (os pares), D-601/D-609/D-610 (no Dividir
o "Duas lado a lado" continua a folha inteira com a linha), D-605 (o novo não estraga o testado).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QMouseEvent, QWheelEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.test_decisoes_mover import (  # noqa: E402,F401 - as mesmas peças das provas do Mover
    _assentar,
    _caixa_da_tinta,
    _esperar,
    _gerar,
    _impresso_na_tela,
    _no_mover,
    app,
    janela,
    pasta,
)
from ui.widgets.paginas_rolando import DUAS, UMA  # noqa: E402


# --- a mão ---------------------------------------------------------------------------

def _evento(tipo, ponto, botao, botoes):
    return QMouseEvent(tipo, QPointF(ponto), QPointF(ponto), botao, botoes, Qt.NoModifier)


def _alvo(tela, ponto_na_vista: QPoint):
    """O widget mais de dentro que está embaixo do ponto (coordenadas da vista da página),
    e o ponto nas coordenadas dele: para onde a mão manda o clique."""
    vista = tela.vista_da_pagina.currentWidget()
    alvo = vista.childAt(ponto_na_vista) or vista
    return alvo, alvo.mapFrom(vista, ponto_na_vista)


def _arrastar_na_tela(tela, de_na_vista: QPoint, dx: int, dy: int = 0) -> None:
    """Apertar, mover em passos e soltar no que está à vista embaixo do ponto (como a mão)."""
    alvo, de = _alvo(tela, de_na_vista)
    QApplication.sendEvent(alvo, _evento(QEvent.MouseButtonPress, de, Qt.LeftButton, Qt.LeftButton))
    for i in range(1, 6):
        p = QPoint(de.x() + dx * i // 5, de.y() + dy * i // 5)
        QApplication.sendEvent(alvo, _evento(QEvent.MouseMove, p, Qt.NoButton, Qt.LeftButton))
    QApplication.sendEvent(alvo, _evento(QEvent.MouseButtonRelease, QPoint(de.x() + dx, de.y() + dy),
                                         Qt.LeftButton, Qt.NoButton))
    _assentar()


def _lugar_da_vez(tela):
    """O retângulo (na vista da página) da página da vez dentro dos pares."""
    pares = tela.lado_a_lado
    pares.grab()
    ret = next(r for i, r in pares.retangulos() if i == pares.atual)
    topo = pares.folhas.mapTo(tela.vista_da_pagina.currentWidget(), ret.topLeft())
    return ret.translated(topo - ret.topLeft())


def _nos_pares_no_mover(janela, tmp_path, pagina: int = 1):
    """Livro aberto, ferramenta Mover pela tecla F, e o botão "Duas lado a lado" da barra de
    baixo clicado (como o Samuel faz). A tela fica nos pares (a vista não muda sozinha)."""
    tela, vis = _no_mover(janela, tmp_path, pagina)
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    assert tela.mostrar == DUAS
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert _esperar(lambda: vis._pixmap is not None)
    _lugar_da_vez(tela)
    vis.grab()
    return tela, vis


# --- D-612: arrastar e puxar o canto nos pares ---------------------------------------------

def test_reversao_d612_arrastar_a_pagina_da_vez_nos_pares_move(janela, tmp_path):
    """D-612 ("ele tem que funcionar com paginas lado a lado também") + D-541 ("arrastar em
    qualquer lugar da área branca ou da página move"). Ferramenta Mover, "Duas lado a lado"
    clicado: a mão aperta no meio da página da vez, nos pares, e arrasta para a esquerda. O
    conteúdo anda (uma ação no Histórico), a vista continua "Duas lado a lado" e o PDF mostra o
    impresso onde a tela mostra (até 1%). Em dd7a648c o arrasto caía nos pares e nada andava."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    pagina = janela.projeto.paginas[1]
    feitas = len(janela.acoes.feitas)
    lugar = _lugar_da_vez(tela)
    _arrastar_na_tela(tela, lugar.center(), -int(lugar.width() * 0.12))
    assert pagina.conteudo_deslocamento[0] < -0.06, (
        "o arrasto não moveu: embaixo da mão estava "
        f"{type(_alvo(tela, lugar.center())[0]).__name__}")
    assert len(janela.acoes.feitas) == feitas + 1
    # a vista NÃO mudou sozinha (D-612)
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    # a tela e o PDF saem da mesma conta (D-473), como na "Uma página"
    vis.grab()
    pdf = _caixa_da_tinta(_gerar(janela, tmp_path, "nos-pares")[1])
    assert pdf == pytest.approx(_impresso_na_tela(vis), abs=0.01)
    # Ctrl+Z volta como veio
    tela.desfazer()
    assert tuple(janela.projeto.paginas[1].conteudo_deslocamento) == (0.0, 0.0)


def test_reversao_d612_vindo_do_dividir_em_duas_lado_a_lado(janela, tmp_path):
    """O caminho do registro de 04/11 (mover-parou): no Dividir com "Duas lado a lado" (D-601), a
    tecla F leva ao Mover ainda em "Duas lado a lado" (a vista não muda sozinha, D-612) e o
    arrasto da mão move a página da vez."""
    tela, _vis = _no_mover(janela, tmp_path, 1)
    tela.escolher_ferramenta("dividir")
    tela.definir_mostrar(DUAS)
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem      # D-601: a folha inteira
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier, "f"))
    assert tela.aba_atual == "mover" and tela.mostrar == DUAS
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    vis = tela.visualizadores["mover"]
    assert _esperar(lambda: vis._pixmap is not None)
    pagina = janela.projeto.paginas[tela.indice_pagina]
    lugar = _lugar_da_vez(tela)
    _arrastar_na_tela(tela, lugar.center(), -int(lugar.width() * 0.12))
    assert pagina.conteudo_deslocamento[0] < -0.06


def test_reversao_d612_puxar_o_canto_nos_pares_aumenta_e_o_numero_acompanha(janela, tmp_path):
    """D-541 ("puxar um dos quatro cantos aumenta ou diminui sempre na mesma proporção") nos
    pares: a mão puxa o canto de baixo à direita da página da vez para fora; o conteúdo aumenta
    e o número "Tamanho do conteúdo (%)" mostra o tamanho novo."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    vista = tela.vista_da_pagina.currentWidget()
    if tela.lado_a_lado.isAncestorOf(vis):
        canto = vis.mapTo(vista, vis._alcas(vis._area_do_conteudo())["se"])
    else:                                       # o código antigo: o canto da página nos pares
        canto = _lugar_da_vez(tela).bottomRight()
    _arrastar_na_tela(tela, canto, 30, 30)
    escala = janela.projeto.paginas[1].conteudo_escala
    assert escala > 1.05, "puxar o canto nos pares não aumentou"
    assert tela.campo_tamanho_do_conteudo.value() == round(escala * 100)


def test_d612_numero_do_tamanho_e_tecla_f_nos_pares(janela, tmp_path):
    """D-541 ("o número 'Tamanho do conteúdo (%)' faz o mesmo") e D-540 (tecla F) com a vista em
    "Duas lado a lado": o número diminui a página da vez e a página nos pares mostra o tamanho
    novo; a tecla F de novo não tira a vista dos pares."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    tela.campo_tamanho_do_conteudo.setValue(80)
    _assentar()
    assert janela.projeto.paginas[1].conteudo_escala == pytest.approx(0.8)
    assert vis._retangulo_conteudo[2] == pytest.approx(0.8, abs=0.01)
    assert tela.lado_a_lado.isAncestorOf(vis) and vis.isVisible()
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier, "f"))
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado


# --- o que já funcionava continua (D-605) --------------------------------------------------

def test_d612_os_pares_continuam_pares(janela, tmp_path):
    """D-006/D-015 (pares rolando): com o Mover nos pares, a outra página do par continua a
    prévia (sem a peça do Mover em cima) e clicar nela faz dela a página da vez, como sempre; o
    Mover passa a mexer nela."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    pares = tela.lado_a_lado
    outra = next(r for i, r in pares.retangulos() if i != pares.atual and i in (1, 2))
    lugar_da_outra = outra.translated(pares.folhas.mapTo(pares, QPoint(0, 0)))
    alvo, _p = _alvo(tela, lugar_da_outra.center())
    assert alvo is not vis and not vis.isAncestorOf(alvo)
    # clicar na outra (sem arrastar): ela vira a da vez; nada se move
    feitas = len(janela.acoes.feitas)
    _arrastar_na_tela(tela, lugar_da_outra.center(), 0)
    assert tela.indice_pagina == 2
    assert len(janela.acoes.feitas) == feitas
    assert _esperar(lambda: vis._pixmap is not None and tela._mover_da_vez)
    # agora o Mover mexe nela
    lugar = _lugar_da_vez(tela)
    _arrastar_na_tela(tela, lugar.center(), int(lugar.width() * 0.1))
    assert janela.projeto.paginas[2].conteudo_deslocamento[0] > 0.04
    assert tuple(janela.projeto.paginas[1].conteudo_deslocamento) == (0.0, 0.0)


def test_d612_uma_pagina_outra_ferramenta_e_dividir_como_antes(janela, tmp_path):
    """D-605: "Uma página" volta a mostrar o Mover de sempre (a mesma peça, no lugar dela) e o
    arrasto move; outra ferramenta em "Duas lado a lado" mostra os pares como antes (sem a peça do
    Mover); no Dividir o "Duas lado a lado" continua a folha inteira com a linha (D-601)."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    tela.botoes_mostrar[UMA].click()
    _assentar()
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert tela.paginas_de_imagem["mover"].isAncestorOf(vis)
    assert not tela.lado_a_lado.isAncestorOf(vis)
    vis.grab()
    centro = tela.vista_da_pagina.mapFrom(vis, vis._area.center())
    _arrastar_na_tela(tela, centro, -int(vis._area.width() * 0.1))
    assert janela.projeto.paginas[1].conteudo_deslocamento[0] < -0.05
    # outra ferramenta nos pares: os pares de sempre
    tela.escolher_ferramenta("cortar")
    tela.definir_mostrar(DUAS)
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert not tela.lado_a_lado.isAncestorOf(vis)
    # Dividir: a folha inteira com a linha
    tela.escolher_ferramenta("dividir")
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert tela.mostrar == DUAS


def test_d612_ctrl_roda_na_pagina_da_vez_da_zoom_nos_pares(janela, tmp_path):
    """D-570/D-568: nos pares, Ctrl+roda dá zoom no par (o "N%" da barra de baixo), também com o
    ponteiro em cima da página da vez do Mover; o Mover não ganha zoom próprio ali."""
    tela, vis = _nos_pares_no_mover(janela, tmp_path, pagina=1)
    lugar = _lugar_da_vez(tela)
    alvo, ponto = _alvo(tela, lugar.center())
    if alvo is tela.lado_a_lado.folhas:
        # o desenho dos pares não trata a roda: no Windows ela sobe à área de rolar (o Qt só
        # faz essa subida com eventos de verdade, não com sendEvent)
        porta = tela.lado_a_lado.viewport()
        alvo, ponto = porta, porta.mapFrom(tela.lado_a_lado.folhas, ponto)
    roda = QWheelEvent(QPointF(ponto), QPointF(alvo.mapToGlobal(ponto)), QPoint(0, 0), QPoint(0, 120),
                       Qt.NoButton, Qt.ControlModifier, Qt.NoScrollPhase, False)
    QApplication.sendEvent(alvo, roda)
    _assentar()
    assert tela.lado_a_lado.zoom > 1.1
    assert vis.zoom == pytest.approx(1.0)
    assert tela.rotulo_do_zoom.text() == f"{round(tela.lado_a_lado.zoom * 100)}%"
