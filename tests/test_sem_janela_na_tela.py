"""Nenhuma rodada de testes abre janela na tela (tests/conftest.py, parte 1).

Pedido da gerente (30/09/2026), depois de uma caixa "Tirar da lista?" de um
teste ficar minutos na tela do Samuel esperando clique.
"""

from __future__ import annotations

import os
import sys
import time

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QDialog, QFileDialog, QInputDialog, QMessageBox)


def _o_conftest():
    """O modulo conftest que o pytest carregou (o nome muda com o jeito de rodar)."""
    for modulo in list(sys.modules.values()):
        if hasattr(modulo, "_CAIXAS_SEM_RESPOSTA") and hasattr(modulo, "LIMITE_DA_CAIXA_S"):
            return modulo
    raise AssertionError("tests/conftest.py nao foi carregado")


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.skipif(os.environ.get("EDITOR_TESTES_COM_TELA") == "1",
                    reason="rodada pedida com tela, de proposito")
def test_o_qt_dos_testes_desenha_fora_da_tela(app):
    assert os.environ["QT_QPA_PLATFORM"] == "offscreen"
    assert QApplication.platformName() == "offscreen"


@pytest.mark.parametrize("chamada", [
    lambda: QMessageBox.question(None, "t", "x"),
    lambda: QMessageBox.warning(None, "t", "x"),
    lambda: QInputDialog.getText(None, "t", "x"),
    lambda: QFileDialog.getOpenFileName(None, "t"),
    lambda: QFileDialog.getExistingDirectory(None, "t"),
])
def test_funcao_pronta_de_caixa_sem_resposta_falha_na_hora(app, chamada):
    comeco = time.monotonic()
    with pytest.raises(RuntimeError, match="sem resposta"):
        chamada()
    assert time.monotonic() - comeco < 1


def test_caixa_modal_sem_resposta_e_fechada_pelo_vigia_e_o_teste_falharia(app, monkeypatch):
    conftest = _o_conftest()
    monkeypatch.setattr(conftest, "LIMITE_DA_CAIXA_S", 0.3)
    for caixa in (QMessageBox(), QDialog()):
        caixa.setWindowTitle("caixa esquecida")
        comeco = time.monotonic()
        caixa.exec()                                   # ninguem clica
        assert time.monotonic() - comeco < 5, "a caixa travou o teste"
    assert len(conftest._CAIXAS_SEM_RESPOSTA) == 2
    assert "caixa esquecida" in conftest._CAIXAS_SEM_RESPOSTA[0]
    conftest._CAIXAS_SEM_RESPOSTA.clear()              # senao ESTE teste falha


def test_caixa_respondida_a_tempo_nao_e_afetada(app):
    from PySide6.QtCore import QTimer

    conftest = _o_conftest()
    caixa = QMessageBox()
    sim = caixa.addButton("Sim", QMessageBox.AcceptRole)
    QTimer.singleShot(50, sim.click)
    caixa.exec()
    assert caixa.clickedButton() is sim
    assert not conftest._CAIXAS_SEM_RESPOSTA
