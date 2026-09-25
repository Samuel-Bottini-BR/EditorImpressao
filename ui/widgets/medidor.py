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
from ui.estilo import AZUL, TEXTO_FRACO


class Medidor(QFrame):
    """Rótulo, pontas nomeadas, barra deslizante e a palavra do valor atual.

    Emite dois sinais diferentes de propósito:
      - arrastando: a cada passo, para a prévia acompanhar ao vivo
      - soltou: uma vez só, ao largar - é o que vira uma ação no desfazer
    """

    arrastando = Signal(int)
    soltou = Signal(int)

    def __init__(self, rotulo: str, ponta_esquerda: str, ponta_direita: str,
                 parent=None) -> None:
        super().__init__(parent)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(2)

        linha = QHBoxLayout()
        linha.setSpacing(8)

        self.rotulo = QLabel(rotulo)
        self.rotulo.setStyleSheet("font-weight: 600;")
        linha.addWidget(self.rotulo)

        esquerda = QLabel(ponta_esquerda)
        esquerda.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
        linha.addWidget(esquerda)

        self.barra = QSlider(Qt.Horizontal)
        self.barra.setMinimum(AJUSTE_MIN)
        self.barra.setMaximum(AJUSTE_MAX)
        self.barra.setValue(AJUSTE_PADRAO)
        self.barra.setSingleStep(5)
        self.barra.setPageStep(10)
        self.barra.setTickInterval(25)
        self.barra.setTickPosition(QSlider.TicksBelow)
        self.barra.setMinimumWidth(180)
        self.barra.valueChanged.connect(self._mudou)
        self.barra.sliderReleased.connect(self._largou)
        linha.addWidget(self.barra, 1)

        direita = QLabel(ponta_direita)
        direita.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
        linha.addWidget(direita)

        self.palavra = QLabel(palavra_do_ajuste(AJUSTE_PADRAO))
        self.palavra.setMinimumWidth(72)
        self.palavra.setAlignment(Qt.AlignCenter)
        self.palavra.setStyleSheet(f"color: {AZUL}; font-weight: 600;")
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
        linha = self.layout().itemAt(0).layout()
        linha.itemAt(1).widget().setText(ponta_esquerda)
        linha.itemAt(3).widget().setText(ponta_direita)

    # --- interno ----------------------------------------------------------

    def _mudou(self, valor: int) -> None:
        """A cada passo do arrasto: atualiza a palavra e emite `arrastando`."""
        self.palavra.setText(palavra_do_ajuste(valor))
        self.arrastando.emit(int(valor))

    def _largou(self) -> None:
        """Ao soltar o mouse: emite `soltou`, o sinal que vira acao no desfazer."""
        self.soltou.emit(self.valor)
