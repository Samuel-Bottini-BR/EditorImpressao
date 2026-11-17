"""A janela da senha dos testes a distancia, e a primeira abertura.

De onde vem (frente do notebook do Kaique, 16/11/2026):
  D-721  na primeira vez que o programa abre, uma janela pequena pede "a senha
         dos testes a distancia"; o Kaique digita a que o Samuel passar. Sem a
         senha, os testes ficam desligados; da para por a senha depois nas
         Configuracoes.

Esta e a parte da TELA. A regra (quais comandos ligam) fica em
core/testes_a_distancia.py; aqui so se pede a senha e se chama `ligar` de la.
Todos os caminhos (esta janela, a caixinha e o botao das Configuracoes) chamam
a mesma `ligar` - sem comando proprio (CLAUDE.md 11.12).

Texto da tela em portugues, sem jargao (regra do Kaique): nada de "OpenSSH",
"Tailscale", "firewall" aqui.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

from core import testes_a_distancia as td
from ui import perguntas


class JanelaSenhaDosTestes(QDialog):
    """A janela pequena que pede a senha dos testes a distancia (D-721).

    Devolve a senha digitada em `self.senha` (vazia se a pessoa disser "Agora
    nao" ou fechar). Nao mostra a senha na tela (campo de senha).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.senha = ""
        self.setWindowTitle("Testes à distância")
        self.setModal(True)
        caixa = QVBoxLayout(self)
        caixa.setContentsMargins(22, 20, 22, 16)
        caixa.setSpacing(12)

        titulo = QLabel("Digite a senha dos testes à distância")
        titulo.setObjectName("titulo")
        caixa.addWidget(titulo)
        frase = QLabel(
            "É a senha que o Samuel passou a você. Com ela, o Samuel pode fazer testes neste "
            "computador pela rede dele. Se você não tiver a senha agora, pode pôr depois, "
            "em Configurações.")
        frase.setWordWrap(True)
        caixa.addWidget(frase)

        self.campo = QLineEdit()
        self.campo.setEchoMode(QLineEdit.Password)
        self.campo.setPlaceholderText("Senha dos testes")
        self.campo.returnPressed.connect(self._confirmar)
        caixa.addWidget(self.campo)

        rodape = QHBoxLayout()
        rodape.addStretch()
        agora_nao = QPushButton("Agora não")
        agora_nao.setCursor(Qt.PointingHandCursor)
        agora_nao.clicked.connect(self.reject)
        rodape.addWidget(agora_nao)
        confirmar = QPushButton("OK")
        confirmar.setDefault(True)
        confirmar.setCursor(Qt.PointingHandCursor)
        confirmar.clicked.connect(self._confirmar)
        rodape.addWidget(confirmar)
        caixa.addLayout(rodape)

    def _confirmar(self) -> None:
        self.senha = self.campo.text()
        self.accept()


def perguntar_senha(parent=None) -> str:
    """Mostra a janela e devolve a senha digitada (vazia se "Agora não"/fechar)."""
    janela = JanelaSenhaDosTestes(parent)
    if janela.exec() == QDialog.Accepted:
        return janela.senha
    return ""


def pedir_senha_e_ligar(parent=None) -> td.Resultado:
    """Pede a senha e liga os testes a distancia (D-721). O caminho unico que a
    janela da primeira vez, a caixinha e o botao das Configuracoes usam.

    Sem senha, nada liga, e avisa em portugues. Se a pessoa disser "Nao" a
    pergunta do Windows, idem (nada e instalado).
    """
    senha = perguntar_senha(parent)
    resultado = td.ligar(senha)
    if not resultado.ok and resultado.mensagem:
        perguntas.avisar(parent, "Testes à distância", resultado.mensagem)
    return resultado


def primeira_vez_se_preciso(parent=None) -> None:
    """Na primeira abertura do programa, pede a senha uma vez (D-721).

    So aparece se a janela ainda nao apareceu antes. Depois, nunca mais sozinha
    (da para por a senha nas Configuracoes). Nao faz nada se a opcao estiver
    desligada (o Kaique pode te-la desligado).
    """
    if td.senha_ja_perguntada():
        return
    td.marcar_senha_perguntada()
    if not td.esta_ligado():
        return
    pedir_senha_e_ligar(parent)
