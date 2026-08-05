"""TELA 4 - Pronto, e a tela de progresso."""

from __future__ import annotations

import time
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import historico
from core.cadernos import (
    conferir_sequencia,
    contar_cadernos,
    instrucoes_de_impressao,
)
from modelos import Projeto
from ui.estilo import TEXTO_FRACO, VERDE, VERMELHO


class TelaProgresso(QWidget):
    """Barra, estimativa de tempo e um cancelar que funciona de verdade."""

    cancelar = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._inicio = 0.0

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(80, 60, 80, 60)
        camadas.setSpacing(18)
        camadas.addStretch()

        self.titulo = QLabel("Processando o livro...")
        self.titulo.setObjectName("titulo")
        self.titulo.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.titulo)

        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        camadas.addWidget(self.barra)

        self.detalhe = QLabel("")
        self.detalhe.setObjectName("fraco")
        self.detalhe.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.detalhe)

        linha = QHBoxLayout()
        linha.addStretch()
        botao = QPushButton("cancelar")
        botao.clicked.connect(self.cancelar.emit)
        linha.addWidget(botao)
        linha.addStretch()
        camadas.addLayout(linha)
        camadas.addStretch()

    def comecar(self, titulo: str) -> None:
        self.titulo.setText(titulo)
        self.barra.setValue(0)
        self.detalhe.setText("")
        self._inicio = time.perf_counter()

    def avancar(self, feito: int, total: int, texto: str) -> None:
        if total <= 0:
            return
        porcentagem = int(100 * feito / total)
        self.barra.setValue(porcentagem)

        # A estimativa sai da media do que ja foi feito - simples e honesta.
        decorrido = time.perf_counter() - self._inicio
        if feito >= 3 and decorrido > 1:
            restante = decorrido / feito * (total - feito)
            self.detalhe.setText(f"{texto}  -  faltam {_tempo(restante)}")
        else:
            self.detalhe.setText(texto)


def _tempo(segundos: float) -> str:
    """Tempo em portugues, sem número quebrado."""
    if segundos < 10:
        return "poucos segundos"
    if segundos < 90:
        return f"cerca de {int(round(segundos / 5) * 5)} segundos"
    minutos = int(round(segundos / 60))
    return "cerca de 1 minuto" if minutos <= 1 else f"cerca de {minutos} minutos"


class TelaFinal(QWidget):
    """Tudo pronto: onde salvou, como imprimir e o que fazer agora."""

    fazer_outro = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.caminho = ""

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(70, 40, 70, 34)
        camadas.setSpacing(14)
        camadas.addStretch()

        self.marca = _Certo()
        camadas.addWidget(self.marca, 0, Qt.AlignCenter)

        titulo = QLabel("Ficou pronto!")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        camadas.addWidget(titulo)

        self.nome = QLabel("")
        self.nome.setAlignment(Qt.AlignCenter)
        self.nome.setStyleSheet("font-size: 17px; font-weight: 600;")
        camadas.addWidget(self.nome)

        self.detalhe = QLabel("")
        self.detalhe.setObjectName("fraco")
        self.detalhe.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.detalhe)

        self.local = QLabel("")
        self.local.setObjectName("fraco")
        self.local.setAlignment(Qt.AlignCenter)
        camadas.addWidget(self.local)

        self.cartao_impressao = QFrame()
        self.cartao_impressao.setObjectName("cartao")
        instrucoes = QVBoxLayout(self.cartao_impressao)
        instrucoes.setContentsMargins(22, 16, 22, 16)
        instrucoes.setSpacing(6)
        rotulo = QLabel("Como imprimir:")
        rotulo.setStyleSheet("font-weight: 600;")
        instrucoes.addWidget(rotulo)
        self.passos = QVBoxLayout()
        instrucoes.addLayout(self.passos)
        camadas.addWidget(self.cartao_impressao)

        camadas.addStretch()

        linha = QHBoxLayout()
        linha.addStretch()
        self.botao_pasta = QPushButton("abrir a pasta")
        self.botao_pasta.clicked.connect(lambda: historico.abrir_pasta(self.caminho))
        linha.addWidget(self.botao_pasta)

        self.botao_imprimir = QPushButton("imprimir agora")
        self.botao_imprimir.clicked.connect(lambda: historico.imprimir(self.caminho))
        linha.addWidget(self.botao_imprimir)

        outro = QPushButton("fazer outro")
        outro.setObjectName("primario")
        outro.clicked.connect(self.fazer_outro.emit)
        linha.addWidget(outro)
        linha.addStretch()
        camadas.addLayout(linha)

    def mostrar(self, projeto: Projeto, caminho: str, num_paginas: int,
                folhas_de_saida: int | None = None) -> None:
        """num_paginas e o total de PAGINAS DO LIVRO.

        Com cadernos, o PDF de saida tem menos páginas que o livro, porque cada
        folha carrega duas. Contar as folhas do arquivo como páginas do livro
        daria um número de cadernos errado - e o usuario separaria os grupos
        errados na hora de dobrar.
        """
        self.caminho = caminho
        arquivo = Path(caminho)

        self.nome.setText(arquivo.name)

        mb = arquivo.stat().st_size / 1024 / 1024 if arquivo.exists() else 0.0
        partes = [f"{num_paginas} páginas", f"{mb:.1f} MB".replace(".", ",")]
        if projeto.montar_cadernos:
            total = contar_cadernos(num_paginas, projeto.paginas_por_caderno)
            partes.append(f"{total} cadernos")
            if folhas_de_saida:
                partes.append(f"{folhas_de_saida} folhas para imprimir")
        self.detalhe.setText("  -  ".join(partes))
        self.local.setText(f"Salvo em: {arquivo.parent}")

        while self.passos.count():
            item = self.passos.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.cartao_impressao.setVisible(projeto.montar_cadernos)
        if projeto.montar_cadernos:
            linhas = instrucoes_de_impressao(num_paginas, projeto.paginas_por_caderno)
            for i, texto in enumerate(linhas, start=1):
                self.passos.addWidget(QLabel(f"{i}. {texto}"))

            # A resposta ao "como ter certeza que estao na sequencia correta sem
            # olhar folha por folha?". Nao entra na lista numerada porque nao e
            # um passo a fazer: e o resultado de uma conferencia ja feita.
            certo, recado = conferir_sequencia(
                num_paginas, projeto.paginas_por_caderno)
            aviso = QLabel(recado)
            aviso.setWordWrap(True)
            aviso.setStyleSheet(
                f"color: {VERDE if certo else VERMELHO}; "
                "margin-top: 8px;"
            )
            self.passos.addWidget(aviso)


class _Certo(QWidget):
    """Um circulo verde com um visto. Desenhado, não emoji (regra 3.4)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(76, 76)

    def paintEvent(self, evento) -> None:  # noqa: N802
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(QPen(QColor(VERDE), 4))
        pintor.drawEllipse(4, 4, 68, 68)
        caneta = QPen(QColor(VERDE), 6)
        caneta.setCapStyle(Qt.RoundCap)
        pintor.setPen(caneta)
        pintor.drawLine(23, 39, 34, 50)
        pintor.drawLine(34, 50, 54, 27)
