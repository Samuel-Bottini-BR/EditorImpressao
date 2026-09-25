"""Diálogo "Tamanho da folha" - escolher o tamanho FÍSICO da página final
digitando, em vez de arrastar o retângulo verde à mão (Problema 1, opção A).

Mudou de propósito na seção 3a do plano "corrigir bugs do teste do Boécio"
(item 2/4 relatado pelo Samuel): ANTES este diálogo devolvia um RECORTE
substituto (via `recorte_para_tamanho_cm`), que `ui/tela_conferir.py`
aplicava direto em cima do corte que o usuário já tinha feito - jogando fora
o trabalho dele. AGORA só devolve o tamanho de folha escolhido
(`tamanho_escolhido()`); quem decide o que fazer com isso é
`ui/tela_conferir.py::_escolher_tamanho_da_folha`, que registra
`ConfigPagina.tamanho_folha_cm` sem tocar em `recorte`.

Não trava nunca (decisões 1 e 2 do plano, confirmadas com o Samuel): o campo
aceita qualquer valor, mesmo menor que o recorte atual - só mostra um aviso
visível (`self.aviso`), o botão OK continua clicável.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from core.folha import TAMANHOS_DE_PAPEL_CM, tamanho_da_folha_cabe
from ui.estilo import FOLHA_DE_ESTILO


class DialogoTamanhoDaFolha(QDialog):
    """Devolve o tamanho escolhido via `tamanho_escolhido()` depois de aceito.

    `largura_recorte_cm`/`altura_recorte_cm` são o tamanho FÍSICO do recorte
    atual do usuário (em cm) - servem de referência para o aviso de "menor
    que o recorte", e também como valor inicial dos campos quando a página
    ainda não tem uma folha escolhida (`tamanho_atual=None`, o padrão: a
    folha É do tamanho do recorte, comportamento de sempre). Se a página já
    tinha uma folha escolhida antes (`tamanho_atual`), o diálogo reabre
    mostrando ELA, não o recorte.
    """

    def __init__(
        self,
        largura_recorte_cm: float,
        altura_recorte_cm: float,
        tamanho_atual: tuple[float, float] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Tamanho da folha")
        self.setStyleSheet(FOLHA_DE_ESTILO)
        self.setMinimumWidth(340)

        self._largura_recorte_cm = largura_recorte_cm
        self._altura_recorte_cm = altura_recorte_cm
        largura_inicial, altura_inicial = tamanho_atual or (
            largura_recorte_cm, altura_recorte_cm)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(20, 16, 20, 16)
        camadas.setSpacing(10)

        camadas.addWidget(QLabel("Tamanho final da folha impressa:"))

        formulario = QFormLayout()
        self.campo_largura = QDoubleSpinBox()
        self.campo_largura.setRange(1.0, 200.0)
        self.campo_largura.setDecimals(2)
        self.campo_largura.setSuffix(" cm")
        self.campo_largura.setValue(largura_inicial)
        formulario.addRow("Largura:", self.campo_largura)

        self.campo_altura = QDoubleSpinBox()
        self.campo_altura.setRange(1.0, 200.0)
        self.campo_altura.setDecimals(2)
        self.campo_altura.setSuffix(" cm")
        self.campo_altura.setValue(altura_inicial)
        formulario.addRow("Altura:", self.campo_altura)
        camadas.addLayout(formulario)

        papeis = QHBoxLayout()
        papeis.addWidget(QLabel("Papel comum:"))
        for nome, (largura, altura) in TAMANHOS_DE_PAPEL_CM.items():
            botao = QPushButton(nome)
            botao.clicked.connect(
                lambda _checked=False, w=largura, h=altura: self._usar_tamanho(w, h))
            papeis.addWidget(botao)
        papeis.addStretch()
        camadas.addLayout(papeis)

        self.aviso = QLabel("")
        self.aviso.setStyleSheet("color: #b45309;")
        self.aviso.setWordWrap(True)
        camadas.addWidget(self.aviso)

        botoes = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        camadas.addWidget(botoes)

        # O aviso se atualiza sozinho enquanto a pessoa digita - nunca impede
        # de continuar, so avisa (decisoes 1/2 do plano).
        self.campo_largura.valueChanged.connect(self._conferir_se_cabe)
        self.campo_altura.valueChanged.connect(self._conferir_se_cabe)
        self._conferir_se_cabe()

    def _usar_tamanho(self, largura: float, altura: float) -> None:
        self.campo_largura.setValue(largura)
        self.campo_altura.setValue(altura)

    def tamanho_escolhido(self) -> tuple[float, float]:
        return self.campo_largura.value(), self.campo_altura.value()

    def _conferir_se_cabe(self) -> None:
        cabe = tamanho_da_folha_cabe(
            self.tamanho_escolhido(),
            (self._largura_recorte_cm, self._altura_recorte_cm),
        )
        self.aviso.setText(
            "" if cabe else
            f"Esse tamanho é menor que o corte que você já fez "
            f"({self._largura_recorte_cm:.1f} × {self._altura_recorte_cm:.1f} cm) - "
            "não vou mudar o seu corte, mas ele não vai caber inteiro na folha."
        )
