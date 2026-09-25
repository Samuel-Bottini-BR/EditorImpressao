"""Tela de Configurações do programa.

Pensada para crescer: atalhos editáveis são a primeira seção, mas o desenho
já reserva espaço para outras seções de configuração entrarem aqui depois,
sem precisar de um menu novo (decisão tomada com o Samuel).

Cada atalho vem do registro único em `atalhos.py` - a mesma tabela que
alimenta o menu e a "Ajuda -> Lista de atalhos", para nunca divergir.
"""

from __future__ import annotations

import functools

import atalhos
import configuracoes
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.estilo import TEXTO_FRACO


class TelaConfiguracoes(QDialog):
    """Lista todo atalho do programa, com captura de tecla e aviso de conflito."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(480, 560)

        raiz = QVBoxLayout(self)

        titulo = QLabel("Atalhos de teclado")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)

        explicacao = QLabel(
            "Clique numa tecla e aperte a combinação que você quer usar no lugar."
        )
        explicacao.setStyleSheet(f"color: {TEXTO_FRACO};")
        explicacao.setWordWrap(True)
        raiz.addWidget(explicacao)

        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        raiz.addWidget(rolagem, 1)

        corpo = QWidget()
        rolagem.setWidget(corpo)
        grade = QGridLayout(corpo)
        grade.setColumnStretch(0, 1)

        self._campos: dict[str, QKeySequenceEdit] = {}
        for linha, atalho in enumerate(atalhos.todas()):
            grade.addWidget(QLabel(atalho.nome), linha, 0)
            campo = QKeySequenceEdit(QKeySequence(atalho.atual))
            campo.setMaximumSequenceLength(1)
            campo.editingFinished.connect(
                functools.partial(self._mudou, atalho.chave, campo))
            grade.addWidget(campo, linha, 1)
            self._campos[atalho.chave] = campo

        self.aviso = QLabel("")
        self.aviso.setStyleSheet("color: #b91c1c;")
        self.aviso.setWordWrap(True)
        raiz.addWidget(self.aviso)

        rodape = QHBoxLayout()
        restaurar = QPushButton("Restaurar todos os padrões")
        restaurar.clicked.connect(self._restaurar_tudo)
        rodape.addWidget(restaurar)
        rodape.addStretch()
        fechar = QPushButton("Fechar")
        fechar.setDefault(True)
        fechar.clicked.connect(self.accept)
        rodape.addWidget(fechar)
        raiz.addLayout(rodape)

    def _mudou(self, chave: str, campo: QKeySequenceEdit) -> None:
        sequencia = campo.keySequence()
        tecla_nova = sequencia.toString() if not sequencia.isEmpty() else ""

        if tecla_nova == atalhos.tecla_atual(chave):
            return  # sem mudança de verdade (ex.: apertou Esc dentro do campo)

        conflito = atalhos.conflito(chave, tecla_nova)
        if conflito:
            self.aviso.setText(
                f'A tecla "{tecla_nova}" já é usada por "{conflito}" - escolha outra.'
            )
            campo.setKeySequence(QKeySequence(atalhos.tecla_atual(chave)))
            return

        atalhos.redefinir(chave, tecla_nova)
        self.aviso.setText("")
        self._salvar()

    def _restaurar_tudo(self) -> None:
        atalhos.restaurar_todos_os_padroes()
        for chave, campo in self._campos.items():
            campo.setKeySequence(QKeySequence(atalhos.tecla_atual(chave)))
        self.aviso.setText("")
        self._salvar()

    def _salvar(self) -> None:
        configuracoes.escrever("atalhos", atalhos.overrides_para_salvar())
        janela = self.parent()
        if janela is not None and hasattr(janela, "menu"):
            janela.menu.reaplicar_atalhos()
