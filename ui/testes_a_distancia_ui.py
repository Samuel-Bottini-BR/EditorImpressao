"""A janela da senha dos testes a distancia, e a primeira abertura.

De onde vem (frente do notebook do Kaique, 16/11/2026):
  D-721  na primeira vez que o programa abre, uma janela pequena pede "a senha
         dos testes a distancia"; o Kaique digita a que o Samuel passar. Sem a
         senha, os testes ficam desligados; da para por a senha depois nas
         Configuracoes.
  D-728  essa janela da primeira vez SO aparece no programa instalado pelo
         instalador (o do Kaique). Aberto pelo codigo (atalho "(desenvolvimento)"
         do Samuel), ela nunca aparece e nada dos testes a distancia liga sozinho -
         igual a atualizacao, que pelo codigo nao faz nada. A regra de "instalado"
         e a mesma da atualizacao: atualizacao.instalado_pelo_velopack (um lugar
         so, CLAUDE.md 11.12).
  D-733  (17/11/2026) na primeira abertura, UMA pergunta do Windows cria o
         ajudante da atualizacao e faz o Visual C++ e tirar o Inno antigo; a
         senha, se digitada, entra na mesma pergunta.
  D-735  (17/11/2026) essa pergunta do Windows aparece SEMPRE, com ou sem a
         senha: "Agora não" na senha nao pula a pergunta do Windows.
  D-736  (17/11/2026) na conta dos testes a distancia, a primeira abertura nao
         faz nada (ninguem responderia a pergunta numa sessao de longe).
  D-741  (17/11/2026) se o Kaique disser "Nao" a pergunta do Windows, ela volta
         a cada abertura ate ele dizer "Sim"; depois do "Sim", nunca mais.
  D-825  (21/11/2026, opcao B) nesta entrega a senha digitada na primeira
         abertura NAO liga os testes a distancia.
  D-834  (23/11/2026, atualizador novo) a pergunta do Windows vem antes da
         janela do programa, logo depois do clique, pela atualizacao
         (atualizacao.Atualizacao); a janela da senha vem depois, com a janela
         principal ja aberta. As regras D-733/D-735/D-741 de cima continuam
         valendo, cumpridas la (a pergunta volta enquanto a pasta do programa
         nao aceitar gravacao).

Esta e a parte da TELA. A regra (quais comandos ligam) fica em
core/testes_a_distancia.py; aqui so se pede a senha e se chama `ligar` de la.
Todos os caminhos (esta janela, a caixinha e o botao das Configuracoes) chamam
a mesma `ligar` - sem comando proprio (CLAUDE.md 11.12).

Texto da tela em portugues, sem jargao (regra do Kaique): nada de "OpenSSH",
"Tailscale", "firewall" aqui.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

import atualizacao
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


def primeira_vez_se_preciso(parent=None,
                            instalado: Callable[[], bool] = atualizacao.instalado_pelo_velopack,
                            conta_de_testes: Callable[[], bool] | None = None) -> None:
    """Na primeira abertura do programa instalado, com a janela já aberta: a janela da senha dos testes à distância,
    uma vez (D-721, D-728). Desde o atualizador novo (23/11/2026) NÃO há pergunta do Windows aqui: ela vem antes da
    janela, logo depois do clique no atalho (D-806, D-834), pela atualização (atualizacao.Atualizacao). A senha
    continua sem ligar nada nesta versão (D-825, opção B: "ok").

    1. Se a opção dos testes à distância está ligada, a janela da senha aparece (como antes). Desligada, não aparece.
    2. A senha digitada NÃO vai a lugar nenhum (nem ao Windows, nem às Configurações); só o registro anota que foi
       digitada. Com "Agora não", o aviso "Sem a senha..." de sempre (core.testes_a_distancia.ligar(""), que não toca
       o Windows).
    A janela da senha só aparece se a primeira abertura ainda não aconteceu nesta conta (a marca de "senha já
    perguntada"); depois, nunca mais sozinha (o botão das Configurações continua chamando `ligar`, sem mudança).

    D-728 (16/11/2026): pelo código (não instalado pelo instalador) não faz NADA: nem mostra a janela, nem marca
    "senha já perguntada". D-736: na conta dos testes à distância não faz nada (nem marca).
    `instalado` e `conta_de_testes` vêm como parâmetro só para os testes; o main.py usa o padrão.
    Seguro mudar: o texto. Arriscado: tirar o `instalado()` daqui (a janela voltaria a aparecer pelo código) ou marcar
    antes dele; deixar a senha chegar ao `ligar` (os testes à distância ainda têm os defeitos de 18/11 e não fazem
    parte desta entrega); voltar a perguntar ao Windows daqui (a pergunta só piscava na barra, D-806).
    """
    if not instalado():
        return
    if (conta_de_testes or atualizacao.e_a_conta_de_testes)():
        return
    if td.senha_ja_perguntada():
        return
    td.marcar_senha_perguntada()
    senha = perguntar_senha(parent) if td.esta_ligado() else None
    if senha:
        atualizacao.registrar("primeira abertura: a senha dos testes à distância foi digitada, mas nesta versão "
                              "ela não liga os testes; eles ligam na atualização que os trouxer consertados")
    elif senha is not None:
        resultado = td.ligar("")  # não toca o Windows; só o aviso "Sem a senha..." de sempre
        if not resultado.ok and resultado.mensagem:
            perguntas.avisar(parent, "Testes à distância", resultado.mensagem)
