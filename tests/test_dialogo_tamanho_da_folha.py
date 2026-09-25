"""O diálogo "Tamanho da folha" depois de mudar de propósito (seção 3a do
plano "corrigir bugs do teste do Boécio", item 2/4).

Antes: devolvia um RECORTE substituto (o bug - via `recorte_para_tamanho_cm`,
sempre recentralizado, jogando fora o corte que o usuário já tinha feito).

Agora: só devolve o TAMANHO DE FOLHA escolhido (`ConfigPagina.tamanho_folha_cm`)
e mostra um aviso visível, NÃO bloqueante, quando esse tamanho é menor que o
recorte atual (decisões 1 e 2 do plano - nunca trava, só avisa).

Roda offscreen, sem abrir janela - mesmo padrão de `tests/test_visualizador.py`.
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")

from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_sem_folha_ja_escolhida_comeca_com_o_tamanho_do_recorte(app):
    """Reabrir o diálogo pela primeira vez: ponto de partida é o recorte atual."""
    d = DialogoTamanhoDaFolha(largura_recorte_cm=14.8, altura_recorte_cm=21.0)
    assert d.tamanho_escolhido() == pytest.approx((14.8, 21.0))


def test_com_folha_ja_escolhida_comeca_com_ela_no_lugar_do_recorte(app):
    """Reabrir depois de já ter escolhido uma folha: mostra o que foi escolhido,
    não o tamanho do recorte (que pode ser bem menor que a folha)."""
    d = DialogoTamanhoDaFolha(
        largura_recorte_cm=14.8, altura_recorte_cm=21.0,
        tamanho_atual=(21.0, 29.7),
    )
    assert d.tamanho_escolhido() == pytest.approx((21.0, 29.7))


def test_aviso_vazio_quando_a_folha_cabe(app):
    d = DialogoTamanhoDaFolha(largura_recorte_cm=14.8, altura_recorte_cm=21.0)
    d.campo_largura.setValue(21.0)
    d.campo_altura.setValue(29.7)
    assert d.aviso.text() == ""


def test_aviso_aparece_quando_a_folha_e_menor_que_o_recorte(app):
    """Decisões 1/2 do plano: nunca trava, mas avisa - de forma visível."""
    d = DialogoTamanhoDaFolha(largura_recorte_cm=14.8, altura_recorte_cm=21.0)
    d.campo_largura.setValue(10.0)
    assert d.aviso.text() != ""
    # o botao OK continua clicavel: nao e bloqueante
    assert d.findChild(QtWidgets.QDialogButtonBox) is not None


def test_botao_de_papel_preenche_os_dois_campos(app):
    d = DialogoTamanhoDaFolha(largura_recorte_cm=10.0, altura_recorte_cm=10.0)
    botao_a4 = next(
        b for b in d.findChildren(QtWidgets.QPushButton) if b.text() == "A4")
    botao_a4.click()
    assert d.tamanho_escolhido() == pytest.approx((21.0, 29.7))
    # A4 e maior que o recorte de 10x10: sem aviso
    assert d.aviso.text() == ""
