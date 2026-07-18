"""TELA 1 - Inicio: arrastar o PDF e a lista de projetos recentes."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

import historico
from core.filtros import NOMES_AMIGAVEIS
from ui.estilo import TEXTO_FRACO
from ui.widgets.area_arrastar import AreaArrastar


class TelaInicio(QWidget):
    abrir_pdf = Signal(str)
    reabrir_projeto = Signal(object)   # historico.Entrada

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(46, 30, 46, 26)
        camadas.setSpacing(18)

        titulo = QLabel("Editor de Impressao")
        titulo.setObjectName("titulo")
        camadas.addWidget(titulo)

        subtitulo = QLabel("Recupere um livro escaneado e prepare para reimprimir")
        subtitulo.setObjectName("subtitulo")
        camadas.addWidget(subtitulo)

        self.area = AreaArrastar()
        self.area.arquivo_escolhido.connect(self.abrir_pdf.emit)
        camadas.addWidget(self.area)

        cabecalho = QHBoxLayout()
        rotulo = QLabel("Projetos recentes")
        rotulo.setObjectName("secao")
        cabecalho.addWidget(rotulo)
        cabecalho.addStretch()
        camadas.addLayout(cabecalho)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        interno = QWidget()
        self.lista = QVBoxLayout(interno)
        self.lista.setContentsMargins(0, 0, 8, 0)
        self.lista.setSpacing(8)
        self.lista.addStretch()
        self.rolagem.setWidget(interno)
        camadas.addWidget(self.rolagem, 1)

        self.recarregar()

    def recarregar(self) -> None:
        """Le o historico do disco e remonta a lista."""
        while self.lista.count() > 1:
            item = self.lista.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        entradas = historico.carregar()
        if not entradas:
            vazio = QLabel(
                "Nenhum livro ainda. Arraste o primeiro PDF ali em cima para comecar."
            )
            vazio.setStyleSheet(f"color: {TEXTO_FRACO}; padding: 14px;")
            self.lista.insertWidget(0, vazio)
            return

        for entrada in entradas:
            self.lista.insertWidget(self.lista.count() - 1, _LinhaProjeto(entrada, self))


class _LinhaProjeto(QFrame):
    """Uma linha da lista de recentes."""

    def __init__(self, entrada: historico.Entrada, tela: TelaInicio) -> None:
        super().__init__()
        self.entrada = entrada
        self.tela = tela
        self.setObjectName("cartao")

        linha = QHBoxLayout(self)
        linha.setContentsMargins(14, 10, 14, 10)
        linha.setSpacing(14)

        textos = QVBoxLayout()
        textos.setSpacing(2)

        nome = QLabel(entrada.nome)
        nome.setStyleSheet("font-weight: 600; font-size: 15px;")
        textos.addWidget(nome)

        filtro = NOMES_AMIGAVEIS.get(entrada.filtro, entrada.filtro)
        detalhe = QLabel(
            f"{entrada.data_amigavel}  -  {entrada.num_paginas} paginas  -  {filtro}"
        )
        detalhe.setStyleSheet(f"color: {TEXTO_FRACO};")
        textos.addWidget(detalhe)

        linha.addLayout(textos, 1)

        abrir = QPushButton("abrir de novo")
        abrir.setEnabled(entrada.existe_entrada)
        if not entrada.existe_entrada:
            abrir.setToolTip("O PDF original nao esta mais nesse lugar.")
        abrir.clicked.connect(lambda: tela.reabrir_projeto.emit(entrada))
        linha.addWidget(abrir)

        pasta = QPushButton("abrir a pasta")
        pasta.setEnabled(entrada.existe_saida)
        pasta.clicked.connect(lambda: historico.abrir_pasta(entrada.caminho_saida))
        linha.addWidget(pasta)
