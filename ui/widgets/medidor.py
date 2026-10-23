"""O medidor deslizante dos ajustes de filtro.

Um controle contínuo no lugar dos três botões que existiam antes. O usuário
arrasta e vê o resultado mudando na hora; nunca aparece número técnico nenhum,
só as palavras nas pontas e a palavra do momento ao lado.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
)

from core.filtros import AJUSTE_MAX, AJUSTE_MIN, AJUSTE_PADRAO, palavra_do_ajuste
from ui import estilo


class Medidor(QFrame):
    """Rótulo, pontas nomeadas, barra deslizante e a palavra do valor atual.

    Emite dois sinais diferentes de propósito:
      - arrastando: a cada passo, para a prévia acompanhar ao vivo
      - soltou: uma vez só, ao largar - é o que vira uma ação no desfazer
    """

    arrastando = Signal(int)
    soltou = Signal(int)

    def __init__(self, rotulo: str, ponta_esquerda: str, ponta_direita: str,
                 parent=None, em_duas_linhas: bool = False) -> None:
        """em_duas_linhas=True (painel "Filtro da página", etapa 4 do layout,
        20/10/2026: o painel tem 300 pontos de largura): o nome e a palavra
        do valor em cima, e "pontas + barra" embaixo, com a barra podendo
        encolher. False: tudo numa linha, como sempre foi."""
        super().__init__(parent)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(2)

        linha = QHBoxLayout()
        linha.setSpacing(8)
        linha_de_cima = QHBoxLayout() if em_duas_linhas else linha

        self.rotulo = QLabel(rotulo)
        self.rotulo.setStyleSheet("font-weight: 600;")
        linha_de_cima.addWidget(self.rotulo)

        esquerda = QLabel(ponta_esquerda)
        estilo.estilizar(esquerda, lambda: f"color: {estilo.TEXTO_FRACO}; font-size: 12px;")
        linha.addWidget(esquerda)
        self.ponta_esquerda = esquerda

        self.barra = QSlider(Qt.Horizontal)
        self.barra.setMinimum(AJUSTE_MIN)
        self.barra.setMaximum(AJUSTE_MAX)
        self.barra.setValue(AJUSTE_PADRAO)
        self.barra.setSingleStep(5)
        self.barra.setPageStep(10)
        self.barra.setTickInterval(25)
        self.barra.setTickPosition(QSlider.TicksBelow)
        self.barra.setMinimumWidth(60 if em_duas_linhas else 180)
        self.barra.valueChanged.connect(self._mudou)
        self.barra.sliderReleased.connect(self._largou)
        linha.addWidget(self.barra, 1)

        direita = QLabel(ponta_direita)
        estilo.estilizar(direita, lambda: f"color: {estilo.TEXTO_FRACO}; font-size: 12px;")
        linha.addWidget(direita)
        self.ponta_direita = direita

        self.palavra = QLabel(palavra_do_ajuste(AJUSTE_PADRAO))
        self.palavra.setMinimumWidth(72)
        self.palavra.setAlignment(Qt.AlignCenter)
        estilo.estilizar(self.palavra, lambda: f"color: {estilo.AZUL}; font-weight: 600;")
        if em_duas_linhas:
            linha_de_cima.addStretch()
            self.palavra.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            linha_de_cima.addWidget(self.palavra)
            camadas.addLayout(linha_de_cima)
        else:
            linha.addWidget(self.palavra)

        camadas.addLayout(linha)

    # --- uso --------------------------------------------------------------

    @property
    def valor(self) -> int:
        """O valor atual do medidor, de AJUSTE_MIN a AJUSTE_MAX (0-100)."""
        return int(self.barra.value())

    def definir(self, valor: int) -> None:
        """Muda o valor SEM disparar os sinais.

        Usado ao trocar de página: mostrar o ajuste que aquela página já tem
        não pode ser confundido com o usuário mexendo no controle.
        """
        self.barra.blockSignals(True)
        self.barra.setValue(int(valor))
        self.barra.blockSignals(False)
        self.palavra.setText(palavra_do_ajuste(self.valor))

    def definir_rotulo(self, rotulo: str, ponta_esquerda: str,
                       ponta_direita: str) -> None:
        """Troca o texto do rotulo e das pontas - usado ao trocar de filtro,
        onde o mesmo medidor passa a significar outra coisa ("Força do preto"
        vira "Clareza do fundo", por exemplo)."""
        self.rotulo.setText(rotulo)
        self.ponta_esquerda.setText(ponta_esquerda)
        self.ponta_direita.setText(ponta_direita)

    # --- interno ----------------------------------------------------------

    def _mudou(self, valor: int) -> None:
        """A cada passo do arrasto: atualiza a palavra e emite `arrastando`."""
        self.palavra.setText(palavra_do_ajuste(valor))
        self.arrastando.emit(int(valor))

    def _largou(self) -> None:
        """Ao soltar o mouse: emite `soltou`, o sinal que vira acao no desfazer."""
        self.soltou.emit(self.valor)
