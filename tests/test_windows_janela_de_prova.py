"""Testes da janela de prova (`janela_de_prova.py`; plano da parte do Windows, peça 10a).

Só o que não pede licença: a janela monta (fora da tela), tem as seis provas da sessão A, e as provas sem pergunta
do Windows (lançar solto, programa que não existe) dão o resultado certo. As provas com a pergunta do Windows (1, 2
e 3 da sessão A) NÃO rodam aqui: são à vista, com o Samuel (D-767, D-785).

Seguro mexer: acrescentar casos sem pergunta. Arriscado: chamar aqui uma prova que pede a licença.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tests.test_windows_peca import _pasta_da_conta_no_disco_do_sistema  # noqa: F401 - a pasta da conta (autouse)

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="a peça só existe no Windows")

RAIZ = Path(__file__).resolve().parent.parent


def test_a_janela_tem_as_seis_provas_da_sessao_a(tmp_path):
    """A janela abre (fora da tela) com uma linha por prova da sessão A, na ordem do plano."""
    import janela_de_prova as jp
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    janela = jp.montar_janela(None, tmp_path / "registro.txt")
    janela.show()
    app.processEvents()
    textos = [b.text() for b in janela.botoes]
    assert len(textos) == 6
    assert textos[1].endswith("clique Sim") and textos[2].endswith("clique Não") and "navegador" in textos[3]
    janela.dizer("linha de teste com acento: ção")
    assert "ção" in (tmp_path / "registro.txt").read_text(encoding="utf-8")
    janela.close()


def test_as_provas_sem_pergunta_dao_o_resultado_certo():
    """Prova 1 (lançar solto): o script roda depois de quem o lançou fechar. Prova 5 (programa que não existe):
    frase em português, sem pergunta."""
    import janela_de_prova as jp

    linhas: list[str] = []
    jp.prova_lancar_solto(linhas.append, None, None)
    assert any("quem o lançou" in l and l.endswith("já tinha fechado: sim") for l in linhas), linhas
    linhas.clear()
    jp.prova_programa_que_nao_existe(linhas.append, None, None)
    assert any("FALHOU" in l and "não achei o programa" in l for l in linhas), linhas


def test_a_janela_usa_a_peca_e_nao_fala_com_o_windows_sozinha():
    """A janela importa a peça do programa (nunca uma cópia) e não importa nada que fale com o Windows por fora
    dela (o porteiro também barra)."""
    texto = (RAIZ / "janela_de_prova.py").read_text(encoding="utf-8")
    assert "from core import windows" in texto
    for proibido in ("import ctypes", "import subprocess", "import winreg"):
        assert proibido not in texto
