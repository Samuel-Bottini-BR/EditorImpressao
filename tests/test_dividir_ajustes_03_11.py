"""Testes de reversão dos achados do verificador clicando de 03/11/2026 no Dividir e na janela
do Automático (relatório: .claude/worktrees/verif-03-11/relatorios/verif-03-11/relatorio.md,
ressalvas dos testes 1 e 2), consertados no ramo `dividir-ajustes-2026-11-03`.

D-605 (Samuel, 03/11/2026): "A partir de agora, nenhuma função nova, ou nova escolha dentro do
programa pode alterar o que já está escolhido e testado, coisas novas não podem criar novos
problemas". Cada conserto aqui desfaz um problema que o conserto de 03/11 (D-602) deixou, sem
mudar o que já estava escolhido.

- Seta → depois da lista "motor de corte" (ressalva 5 do teste 1).
- A tira de miniaturas depois do Ctrl+Z (ressalva 4 do teste 1, print t1-22).
- A coluna do meio da etapa 6 cortada em 1536 x 824 (ressalva 3 do teste 2, print t2m-02).

Os itens D-606 e D-607 têm a prova nos arquivos de decisões (tests/test_decisoes_dividir.py e
tests/test_decisoes_automatico.py). Todos falham no código de antes (75ed04af).
"""

from __future__ import annotations

import time

import numpy as np
import pytest

pytest.importorskip("fitz")
pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from tests.test_decisoes_dividir import (  # noqa: E402,F401  (fixtures app, pasta, janela)
    _pagina,
    _pdf,
    app,
    janela,
    pasta,
)


def _assentar(vezes: int = 5) -> None:
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


def _aberto() -> np.ndarray:
    return np.concatenate([_pagina(600), _pagina(760)], axis=1)


def _no_dividir(janela, tmp_path, folhas: int):
    from ui.tela_conferir import ABA_CORTE

    janela.show()
    janela.activateWindow()
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto() for _ in range(folhas)]))
    tela = janela.tela_conferir
    tela.escolher_ferramenta("dividir")
    tela._ir_para(0)
    assert tela.aba_atual == ABA_CORTE
    _assentar()
    return tela


# --- seta → depois da lista "motor de corte" -------------------------------------------------

def test_reversao_seta_troca_de_folha_depois_de_escolher_o_motor(janela, tmp_path):
    """Achado do verificador clicando (03/11/2026, ressalva 5 do teste 1): "Depois de usar a
    lista "motor de corte", a seta do teclado (→) não trocou de folha. O teclado ficou com a
    lista." Agora a lista não pega o teclado (como as outras listas da área de trabalho, D-021
    e etapa 9b-1: "o teclado fica com a página"): abrir a lista com o mouse, escolher o outro
    motor, e a seta → vai à folha seguinte, como antes de usar a lista.
    No código de antes (75ed04af) o clique dava o teclado à lista: este teste falha lá."""
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication

    tela = _no_dividir(janela, tmp_path, 3)
    # como o verificador: o teclado com a janela (clicar nas miniaturas e na página não
    # dá o teclado a nenhum botão); antes de usar a lista, a seta anda
    if QApplication.focusWidget() is not None:
        QApplication.focusWidget().clearFocus()
    _assentar()
    QTest.keyClick(QApplication.focusWidget() or janela, Qt.Key_Right)
    _assentar()
    assert tela.indice_folha == 1, "antes de usar a lista, a seta → anda"
    QTest.keyClick(QApplication.focusWidget() or janela, Qt.Key_Left)
    _assentar()
    assert tela.indice_folha == 0
    combo = tela.combo_jeito_da_folha
    antes = combo.currentData()
    QTest.mouseClick(combo, Qt.LeftButton)              # abre a lista
    _assentar()
    vista = combo.view()
    outro = next(i for i in range(combo.count()) if combo.itemData(i) != antes)
    QTest.mouseClick(vista.viewport(), Qt.LeftButton, Qt.NoModifier,
                     vista.visualRect(vista.model().index(outro, 0)).center())
    _assentar()
    if vista.window().isVisible():                     # o offscreen às vezes não fecha
        combo.hidePopup()
        combo.setCurrentIndex(outro)
    _assentar()
    assert combo.currentData() != antes, "o motor foi trocado"
    # o teclado de volta na janela grande (a lista aberta é outra janela): quem fica com ele é
    # o "foco" da janela (no offscreen o foco da aplicação fica na lista escondida)
    assert janela.focusWidget() is not combo, "a lista não fica com o teclado"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Right)
    _assentar()
    assert tela.indice_folha == 1, "a seta → foi à folha seguinte"
    QTest.keyClick(janela.focusWidget() or janela, Qt.Key_Left)
    _assentar()
    assert tela.indice_folha == 0, "e a ← volta"
