"""Nenhuma caixa do programa mostra botao em ingles.

Achado pelo verificador (30/09/2026, print s25): a confirmacao "Começar de
novo?" mostrava "Yes" e "No". O programa nao carrega a traducao do Qt, entao
toda funcao pronta do Qt que poe botoes padrao (QMessageBox.question,
.warning, .information, .critical; QInputDialog.getText/getInt; os botoes
padrao do QDialogButtonBox) sai em ingles na tela do Kaique. Regra do
CLAUDE.md: interface toda em portugues.

Dois tipos de teste: (1) varre o codigo da interface (ui/ e main.py) atras
dessas funcoes prontas - quem precisar de uma pergunta usa ui/perguntas.py;
(2) confere os textos dos botoes que ui/perguntas.py monta.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QDialogButtonBox  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent

# Funcoes prontas do Qt que poem botoes padrao (em ingles, sem traducao).
PROIBIDAS = [
    r"QMessageBox\.(question|warning|information|critical|about)\(",
    r"QMessageBox\.(Yes|No|Ok|Cancel|Save|Discard|Close|Retry|Abort|Ignore)\b",
    r"QInputDialog\.get(Text|Int|Double|Item|MultiLineText)\(",
    r"QDialogButtonBox\.(Ok|Cancel|Yes|No|Save|Close|Apply|Discard)\b",
]


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _arquivos_da_interface() -> list[Path]:
    return sorted((RAIZ / "ui").rglob("*.py")) + [RAIZ / "main.py"]


def test_nenhuma_caixa_com_botoes_padrao_do_qt():
    achados = []
    for arquivo in _arquivos_da_interface():
        for numero, linha in enumerate(arquivo.read_text(encoding="utf-8").splitlines(), 1):
            if linha.lstrip().startswith("#"):
                continue
            for padrao in PROIBIDAS:
                if re.search(padrao, linha):
                    achados.append(f"{arquivo.relative_to(RAIZ)}:{numero}: {linha.strip()}")
    assert not achados, "botoes em ingles:\n" + "\n".join(achados)


def test_pergunta_tem_os_botoes_escritos_por_nos_e_o_nao_no_enter(app):
    from ui import perguntas

    caixa, sim, nao = perguntas._caixa_de_pergunta(
        None, "Começar de novo?", "texto", sim="Começar de novo", nao="Não")
    textos = {b.text() for b in caixa.buttons()}
    assert textos == {"Começar de novo", "Não"}
    assert caixa.defaultButton() is nao and caixa.escapeButton() is nao
    caixa.deleteLater()


def test_aviso_tem_o_botao_entendi(app):
    from ui import perguntas

    caixa = perguntas._caixa_de_aviso(None, "Um momento", "texto")
    assert [b.text() for b in caixa.buttons()] == ["entendi"]
    caixa.deleteLater()


def test_pedir_texto_e_numero_com_botoes_em_portugues(app):
    from ui import perguntas

    for caixa in (perguntas._caixa_de_texto(None, "Renomear", "Nome:", "x"),
                  perguntas._caixa_de_numero(None, "Ir para a página", "Página:", 3, 1, 10)):
        assert caixa.okButtonText() == "OK"
        assert caixa.cancelButtonText() == "Cancelar"
        caixa.deleteLater()


def test_dialogo_do_tamanho_da_folha_com_cancelar_em_portugues(app):
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha

    dialogo = DialogoTamanhoDaFolha(20.0, 28.0)
    textos = {b.text() for b in dialogo.findChildren(QDialogButtonBox)[0].buttons()}
    assert "Cancel" not in textos and "Cancelar" in textos
    dialogo.deleteLater()
