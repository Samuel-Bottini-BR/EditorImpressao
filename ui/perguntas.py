"""Caixas de pergunta e de aviso com os botoes em portugues.

As funcoes prontas do Qt (QMessageBox.question, .warning, .information) poem
botoes padrao, e o programa nao carrega traducao do Qt: saiam "Yes", "No" e
"OK" na tela do Kaique (verificador, 30/09/2026, print s25; regra do
CLAUDE.md: interface toda em portugues, sem jargao). Aqui os botoes tem o
texto escrito por nos.

Quem usa: ui/tela_inicio.py ("Começar de novo?", "Tirar da lista?", os avisos
de livro trocado) e o que mais precisar de uma pergunta simples.

Testes e o teste_botoes.py podem trocar `perguntar` e `avisar` por respostas
fixas (monkeypatch), como faziam com QMessageBox.question.

Seguro mudar: os textos padrao dos botoes. Arriscado: trocar o botao padrao
(o que o Enter aperta) das perguntas que apagam algo - tem de ser o "nao".
"""

from __future__ import annotations

from PySide6.QtWidgets import QInputDialog, QLineEdit, QMessageBox, QWidget

# Os botoes das caixas de digitar (renomear, ir para a pagina, nome do arquivo):
# como no Windows em portugues.
TEXTO_OK = "OK"
TEXTO_CANCELAR = "Cancelar"


def _caixa_de_pergunta(pai, titulo: str, texto: str, sim: str, nao: str,
                       padrao_sim: bool = False):
    """Monta (sem mostrar) a caixa de perguntar; devolve (caixa, sim, nao)."""
    caixa = QMessageBox(pai)
    caixa.setWindowTitle(titulo)
    caixa.setIcon(QMessageBox.Question)
    caixa.setText(texto)
    botao_sim = caixa.addButton(sim, QMessageBox.AcceptRole)
    botao_nao = caixa.addButton(nao, QMessageBox.RejectRole)
    caixa.setDefaultButton(botao_sim if padrao_sim else botao_nao)
    caixa.setEscapeButton(botao_nao)
    return caixa, botao_sim, botao_nao


def perguntar(pai: QWidget | None, titulo: str, texto: str,
              sim: str = "Sim", nao: str = "Não", padrao_sim: bool = False) -> bool:
    """Pergunta com dois botoes; True se a pessoa clicou em `sim`.

    Esc, X e o botao `nao` devolvem False. O botao padrao (Enter) e o `nao`,
    a menos que padrao_sim=True - pergunta que apaga alguma coisa nunca deve
    ter o "sim" no Enter.
    """
    caixa, botao_sim, _botao_nao = _caixa_de_pergunta(pai, titulo, texto, sim, nao, padrao_sim)
    caixa.exec()
    return caixa.clickedButton() is botao_sim


def _caixa_de_aviso(pai, titulo: str, texto: str, botao: str = "entendi",
                    icone=QMessageBox.Warning):
    """Monta (sem mostrar) a caixa de aviso com um botao so."""
    caixa = QMessageBox(pai)
    caixa.setWindowTitle(titulo)
    caixa.setIcon(icone)
    caixa.setText(texto)
    caixa.addButton(botao, QMessageBox.AcceptRole)
    return caixa


def avisar(pai: QWidget | None, titulo: str, texto: str, botao: str = "entendi",
           icone=QMessageBox.Warning) -> None:
    """Aviso com um botao so ("entendi", como o avisar da janela principal)."""
    _caixa_de_aviso(pai, titulo, texto, botao, icone).exec()


def _caixa_de_texto(pai, titulo: str, rotulo: str, valor: str = "") -> QInputDialog:
    """Monta (sem mostrar) a caixa de digitar um texto, com OK/Cancelar."""
    caixa = QInputDialog(pai)
    caixa.setWindowTitle(titulo)
    caixa.setLabelText(rotulo)
    caixa.setInputMode(QInputDialog.TextInput)
    caixa.setTextEchoMode(QLineEdit.Normal)
    caixa.setTextValue(valor)
    caixa.setOkButtonText(TEXTO_OK)
    caixa.setCancelButtonText(TEXTO_CANCELAR)
    return caixa


def pedir_texto(pai: QWidget | None, titulo: str, rotulo: str,
                valor: str = "") -> tuple[str, bool]:
    """Como QInputDialog.getText, mas com "Cancelar" em portugues.
    Devolve (texto, clicou_ok)."""
    caixa = _caixa_de_texto(pai, titulo, rotulo, valor)
    certo = bool(caixa.exec())
    return caixa.textValue(), certo


def _caixa_de_numero(pai, titulo: str, rotulo: str, valor: int,
                     minimo: int, maximo: int) -> QInputDialog:
    """Monta (sem mostrar) a caixa de digitar um numero, com OK/Cancelar."""
    caixa = QInputDialog(pai)
    caixa.setWindowTitle(titulo)
    caixa.setLabelText(rotulo)
    caixa.setInputMode(QInputDialog.IntInput)
    caixa.setIntRange(minimo, maximo)
    caixa.setIntValue(valor)
    caixa.setOkButtonText(TEXTO_OK)
    caixa.setCancelButtonText(TEXTO_CANCELAR)
    return caixa


def pedir_numero(pai: QWidget | None, titulo: str, rotulo: str, valor: int,
                 minimo: int, maximo: int) -> tuple[int, bool]:
    """Como QInputDialog.getInt, mas com "Cancelar" em portugues.
    Devolve (numero, clicou_ok)."""
    caixa = _caixa_de_numero(pai, titulo, rotulo, valor, minimo, maximo)
    certo = bool(caixa.exec())
    return caixa.intValue(), certo
