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

from PySide6.QtWidgets import QMessageBox, QWidget


def perguntar(pai: QWidget | None, titulo: str, texto: str,
              sim: str = "Sim", nao: str = "Não", padrao_sim: bool = False) -> bool:
    """Pergunta com dois botoes; True se a pessoa clicou em `sim`.

    Esc, X e o botao `nao` devolvem False. O botao padrao (Enter) e o `nao`,
    a menos que padrao_sim=True - pergunta que apaga alguma coisa nunca deve
    ter o "sim" no Enter.
    """
    caixa = QMessageBox(pai)
    caixa.setWindowTitle(titulo)
    caixa.setIcon(QMessageBox.Question)
    caixa.setText(texto)
    botao_sim = caixa.addButton(sim, QMessageBox.AcceptRole)
    botao_nao = caixa.addButton(nao, QMessageBox.RejectRole)
    caixa.setDefaultButton(botao_sim if padrao_sim else botao_nao)
    caixa.setEscapeButton(botao_nao)
    caixa.exec()
    return caixa.clickedButton() is botao_sim


def avisar(pai: QWidget | None, titulo: str, texto: str, botao: str = "entendi",
           icone=QMessageBox.Warning) -> None:
    """Aviso com um botao so ("entendi", como o avisar da janela principal)."""
    caixa = QMessageBox(pai)
    caixa.setWindowTitle(titulo)
    caixa.setIcon(icone)
    caixa.setText(texto)
    caixa.addButton(botao, QMessageBox.AcceptRole)
    caixa.exec()
