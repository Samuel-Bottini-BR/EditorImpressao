"""O teste que pegaria o "mover e dimensionar para de funcionar" (Samuel, 04/11/2026, Gradus
Primus: "mover e dimensionar para de funcionar em algumas situações, não sei exactamente o que
eu fiz, mas ele parou de funcionar").

NÃO está em tests/ de propósito: o que o Mover deve fazer quando a tela está em "Duas lado a
lado" ou em "antes / depois" é pergunta para o Samuel (relatorios/mover-parou/ONDE-PAREI.md,
"Perguntas para o Samuel"). Depois da resposta, ele entra em tests/ com o que ele escolher.

Diferença para os testes que já existiam (tests/test_decisoes_mover.py): lá o arrasto é
mandado DIRETO ao visualizador do Mover (vis.mousePressEvent(...)), mesmo que ele não esteja à
vista. Aqui o arrasto vai para o que está NA TELA no lugar da página
(tela.vista_da_pagina.currentWidget() e o filho dele embaixo do ponto), como a mão do
Samuel: se ali estão os pares ou o "antes / depois", o arrasto não chega ao Mover.

Rodar (copiado para tests/, para pegar o tests/conftest.py):
    $env:QT_QPA_PLATFORM="offscreen"; ...python.exe -m pytest tests\\_tmp_teste_que_pegaria.py -q
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QMouseEvent  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from tests.test_decisoes_mover import _esperar, _no_mover, app, janela, pasta  # noqa: E402,F401


def _evento(tipo, ponto, botao, botoes):
    return QMouseEvent(tipo, QPointF(ponto), QPointF(ponto), botao, botoes, Qt.NoModifier)


def _arrastar_na_tela(tela, dx: int) -> None:
    """Arrasta no meio do que está à vista no lugar da página (o widget mais de dentro que
    está embaixo do ponto), como a mão: apertar, mover em passos, soltar."""
    vista = tela.vista_da_pagina.currentWidget()
    vista.grab()
    meio = vista.rect().center()
    alvo = vista.childAt(meio) or vista
    de = alvo.mapFrom(vista, meio)
    ate = QPoint(de.x() + dx, de.y())
    QApplication.sendEvent(alvo, _evento(QEvent.MouseButtonPress, de, Qt.LeftButton, Qt.LeftButton))
    for i in range(1, 6):
        p = QPoint(de.x() + dx * i // 5, de.y())
        QApplication.sendEvent(alvo, _evento(QEvent.MouseMove, p, Qt.NoButton, Qt.LeftButton))
    QApplication.sendEvent(alvo, _evento(QEvent.MouseButtonRelease, ate, Qt.LeftButton, Qt.NoButton))
    for _ in range(5):
        QApplication.processEvents()


def test_mover_depois_do_dividir_em_duas_lado_a_lado(janela, tmp_path):
    """O caminho do registro de 04/11: no Dividir com "Duas lado a lado" (a frase do Dividir
    manda escolher "Duas lado a lado" para arrastar a linha, D-601), tecla F → a ferramenta
    Mover; arrastar a página tem de mover (D-008, D-541). Em 249922d2 a tela fica nos pares
    e o arrasto não chega ao Mover: o lugar da página não muda."""
    from ui.widgets.paginas_rolando import DUAS

    tela, _vis = _no_mover(janela, tmp_path)
    tela.escolher_ferramenta("dividir")
    tela.definir_mostrar(DUAS)
    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_F, Qt.NoModifier, "f"))
    assert tela.aba_atual == "mover"
    pagina = janela.projeto.paginas[tela.indice_pagina]
    antes = tuple(pagina.conteudo_deslocamento)
    _arrastar_na_tela(tela, -80)
    assert tuple(pagina.conteudo_deslocamento) != antes, (
        "o arrasto não moveu: a tela está em "
        f"{type(tela.vista_da_pagina.currentWidget()).__name__}")


def test_mover_com_antes_depois_ligado(janela, tmp_path):
    """Na ferramenta Mover, com o "antes / depois" da barra de baixo ligado: arrastar a página
    tem de mover. Em 249922d2 a tela mostra o "antes / depois" e o arrasto não chega ao Mover."""
    tela, _vis = _no_mover(janela, tmp_path)
    tela.botao_antes_depois.click()
    pagina = janela.projeto.paginas[tela.indice_pagina]
    antes = tuple(pagina.conteudo_deslocamento)
    _arrastar_na_tela(tela, -80)
    assert tuple(pagina.conteudo_deslocamento) != antes


def test_mover_em_uma_pagina_continua_movendo(janela, tmp_path):
    """Guarda: em "Uma página" o mesmo arrasto, pelo mesmo caminho, move (passa hoje)."""
    tela, _vis = _no_mover(janela, tmp_path)
    pagina = janela.projeto.paginas[tela.indice_pagina]
    antes = tuple(pagina.conteudo_deslocamento)
    _arrastar_na_tela(tela, -80)
    assert tuple(pagina.conteudo_deslocamento) != antes
