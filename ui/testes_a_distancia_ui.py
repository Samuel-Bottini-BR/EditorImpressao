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
         abertura NAO liga os testes a distancia: uma pergunta do Windows so,
         sempre, pela peca unica (atualizacao.preparar_ao_abrir, por tras).
         O botao das Configuracoes continua chamando `ligar`, sem mudanca.

Esta e a parte da TELA. A regra (quais comandos ligam) fica em
core/testes_a_distancia.py; aqui so se pede a senha e se chama `ligar` de la.
Todos os caminhos (esta janela, a caixinha e o botao das Configuracoes) chamam
a mesma `ligar` - sem comando proprio (CLAUDE.md 11.12).

Texto da tela em portugues, sem jargao (regra do Kaique): nada de "OpenSSH",
"Tailscale", "firewall" aqui.
"""

from __future__ import annotations

import threading
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


def _rodar_por_tras(trabalho: Callable[[], object]) -> threading.Thread:
    """Roda `trabalho` num fio que nao e o da tela, solto (daemon), e devolve o fio (4 consertos, 21/11/2026).

    Por que por tras: a pergunta do Windows segura quem pergunta ate a resposta, e a preparacao pode levar minutos
    (Visual C++, a instalacao antiga); no fio da tela a janela ficava parada ("Nao esta respondendo"; CLAUDE.md §3).
    Por que solto: se o Kaique fechar o programa no meio, o fio morre junto, sem segurar a saida; o trabalho com
    licenca e outro processo e termina sozinho, e a proxima abertura le o Windows (atualizacao.o_que_falta_no_computador).
    O trabalho nao mexe na tela (so no Windows e no registro): nada volta para o fio da tela.
    Arriscado: fio nao-solto (o programa nao fecharia enquanto a pergunta estivesse na tela); mexer em janela daqui.
    """
    fio = threading.Thread(target=trabalho, name="primeira-abertura", daemon=True)
    fio.start()
    return fio


def numero_da_janela(parent) -> int | None:
    """O numero da janela do programa no Windows (a dona da pergunta do Windows, D-806), lido no fio da tela.

    None sem janela (os testes chamam com None) ou se o Qt nao der o numero: a pergunta sai sem dona, e a peca do
    Windows diz no registro que a janela nao estava na frente.
    """
    if parent is None:
        return None
    try:
        return int(parent.winId()) or None
    except (AttributeError, RuntimeError, TypeError, ValueError):
        return None


def primeira_vez_se_preciso(parent=None,
                            instalado: Callable[[], bool] = atualizacao.instalado_pelo_velopack,
                            conta_de_testes: Callable[[], bool] | None = None,
                            por_tras: Callable[[Callable[[], object]], object] | None = None) -> None:
    """Na primeira abertura do programa instalado: a senha e a pergunta do Windows, uma vez (D-721, D-728, D-733,
    D-735), e a pergunta de novo nas aberturas seguintes ate o "Sim" (D-741, D-749).

    1. Se a opcao dos testes a distancia esta ligada, a janela da senha aparece (como antes). Desligada, a janela nao
       aparece.
    2. A senha digitada NAO liga os testes a distancia nesta entrega (D-825, opcao B, Samuel 21/11/2026: "ok"): ela
       nao vai a lugar nenhum (nem ao Windows, nem as Configuracoes); so o registro anota que foi digitada. Com
       "Agora não", o aviso "Sem a senha..." de sempre (core.testes_a_distancia.ligar(""), que nao toca o Windows).
    3. Depois, SEMPRE, a pergunta do Windows, por tras (atualizacao.preparar_ao_abrir, num fio que nao e o da tela):
       na primeira vez, logo depois do clique; nas seguintes, so se a leitura do Windows disser que falta preparar.
    A janela da senha so aparece se a primeira abertura ainda nao aconteceu nesta conta (a marca de "senha ja
    perguntada"); depois, nunca mais sozinha.

    D-728 (16/11/2026): pelo codigo (nao instalado pelo instalador) nao faz NADA: nem mostra a janela, nem marca
    "senha ja perguntada". D-736: na conta dos testes a distancia nao faz nada (nem marca).
    `instalado`, `conta_de_testes` e `por_tras` vem como parametro so para os testes (`por_tras`: quem roda o trabalho
    por tras; os testes rodam na hora). O main.py usa o padrao.
    Seguro mudar: o texto. Arriscado: tirar o `instalado()` daqui (a janela voltaria a aparecer pelo codigo) ou marcar
    antes dele; pular a pergunta do Windows quando nao ha senha (o ajudante da atualizacao nunca nasceria); rodar a
    pergunta no fio da tela (a janela congela); deixar a senha chegar ao ligar (os testes a distancia ainda tem os
    defeitos de 18/11 e nao fazem parte desta entrega).
    """
    if not instalado():
        return
    if (conta_de_testes or atualizacao.e_a_conta_de_testes)():
        return
    rodar = por_tras or _rodar_por_tras
    # D-806 (conserto 2): a janela do programa vai como dona da pergunta, para ela vir no meio da tela; a peca do
    # Windows a traz para a frente antes de perguntar. O numero e lido aqui, no fio da tela.
    janela = numero_da_janela(parent)
    if td.senha_ja_perguntada():
        # D-741: a janela da senha nao volta (D-721: a senha vai nas Configuracoes), mas a pergunta do Windows volta
        # ate o "Sim" (quem decide e a leitura do Windows, por tras).
        rodar(lambda: atualizacao.preparar_ao_abrir(janela, primeira_vez=False))
        return
    td.marcar_senha_perguntada()
    senha = perguntar_senha(parent) if td.esta_ligado() else None
    if senha:
        atualizacao.registrar("primeira abertura: a senha dos testes à distância foi digitada, mas nesta versão "
                              "ela não liga os testes; eles ligam na atualização que os trouxer consertados")
    elif senha is not None:
        resultado = td.ligar("")  # nao toca o Windows; so o aviso "Sem a senha..." de sempre
        if not resultado.ok and resultado.mensagem:
            perguntas.avisar(parent, "Testes à distância", resultado.mensagem)
    rodar(lambda: atualizacao.preparar_ao_abrir(janela, primeira_vez=True))
