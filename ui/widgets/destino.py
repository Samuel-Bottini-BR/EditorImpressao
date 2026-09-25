"""Onde salvar o PDF: a pasta e o nome do arquivo.

Fica na tela de conferir, logo acima do botão de processar, para o usuario
decidir ANTES de esperar o processamento - e não descobrir depois que foi
parar num lugar que ele não queria.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

import configuracoes
from ui.estilo import TEXTO_FRACO, VERMELHO

LARGURA_MAXIMA_CAMINHO = 62


class SeletorDestino(QFrame):
    """Pasta + nome do arquivo, com aviso quando a pasta não aceita gravacao."""

    alterado = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("cartao")
        self._pasta = configuracoes.pasta_de_saida_sugerida()

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(12, 7, 12, 7)
        camadas.setSpacing(4)

        linha_pasta = QHBoxLayout()
        linha_pasta.setSpacing(10)

        rotulo = QLabel("Salvar em:")
        rotulo.setStyleSheet("font-weight: 600;")
        linha_pasta.addWidget(rotulo)

        self.rotulo_pasta = QLabel("")
        self.rotulo_pasta.setStyleSheet(f"color: {TEXTO_FRACO};")
        linha_pasta.addWidget(self.rotulo_pasta, 1)

        botao = QPushButton("Escolher pasta")
        botao.clicked.connect(self.escolher_pasta)
        linha_pasta.addWidget(botao)
        camadas.addLayout(linha_pasta)

        linha_nome = QHBoxLayout()
        linha_nome.setSpacing(10)

        rotulo_nome = QLabel("Nome do arquivo:")
        rotulo_nome.setStyleSheet("font-weight: 600;")
        linha_nome.addWidget(rotulo_nome)

        self.campo_nome = QLineEdit()
        self.campo_nome.setPlaceholderText("nome do arquivo.pdf")
        self.campo_nome.textEdited.connect(lambda _: self._conferir())
        linha_nome.addWidget(self.campo_nome, 1)
        camadas.addLayout(linha_nome)

        self.aviso = QLabel("")
        self.aviso.setWordWrap(True)
        self.aviso.setStyleSheet(f"color: {VERMELHO}; font-size: 12px;")
        self.aviso.setVisible(False)
        camadas.addWidget(self.aviso)

        self._mostrar_pasta()

    # --- uso --------------------------------------------------------------

    def definir(self, pasta: str | Path | None, nome: str) -> None:
        """Preenche pasta e nome de uma vez (ex.: ao abrir a janela de
        confirmar com os valores ja salvos do projeto)."""
        if pasta:
            self._pasta = Path(pasta)
        self.campo_nome.setText(nome)
        self._mostrar_pasta()
        self._conferir()

    @property
    def pasta(self) -> Path:
        """A pasta de destino escolhida."""
        return self._pasta

    @property
    def nome(self) -> str:
        """Nome digitado, sempre terminando em .pdf e sem caractere proibido."""
        from modelos import nome_de_arquivo_seguro

        bruto = self.campo_nome.text().strip() or "livro.pdf"
        limpo = nome_de_arquivo_seguro(bruto)
        if not limpo.lower().endswith(".pdf"):
            limpo += ".pdf"
        return limpo

    @property
    def caminho(self) -> Path:
        """Pasta + nome juntos: o caminho completo do PDF de saida."""
        return self._pasta / self.nome

    def escolher_pasta(self) -> None:
        """Abre o seletor nativo de pastas e valida se da para gravar ali."""
        # Sem DontUseNativeDialog: queremos o seletor de pastas do proprio
        # Windows, que e o que o usuario ja conhece.
        escolhida = QFileDialog.getExistingDirectory(
            self, "Escolha a pasta onde salvar o PDF", str(self._pasta),
            QFileDialog.ShowDirsOnly,
        )
        if not escolhida:
            return

        pode, motivo = configuracoes.pode_gravar_em(escolhida)
        if not pode:
            self._avisar(motivo)
            return

        self._pasta = Path(escolhida)
        configuracoes.lembrar_pasta_de_saida(self._pasta)
        self._mostrar_pasta()
        self._conferir()
        self.alterado.emit()

    # --- interno ----------------------------------------------------------

    def _mostrar_pasta(self) -> None:
        """Mostra o caminho da pasta, encurtado pelo MEIO se for comprido demais."""
        texto = str(self._pasta)
        if len(texto) > LARGURA_MAXIMA_CAMINHO:
            # encurta pelo MEIO: o comeco (o disco) e o fim (a pasta) sao o que
            # o usuario reconhece; o miolo nao ajuda ninguem
            corte = (LARGURA_MAXIMA_CAMINHO - 3) // 2
            texto = f"{texto[:corte]}...{texto[-corte:]}"
        self.rotulo_pasta.setText(texto)
        self.rotulo_pasta.setToolTip(str(self._pasta))

    def _avisar(self, mensagem: str) -> None:
        """Mostra (ou esconde, com string vazia) a faixa de aviso vermelha."""
        self.aviso.setText(mensagem)
        self.aviso.setVisible(bool(mensagem))

    def _conferir(self) -> None:
        """Reavalia o destino a cada mudanca: pasta sem permissao vira aviso
        vermelho, nome ja existente vira aviso neutro (nao bloqueia, so avisa -
        quem pergunta se substitui e a janela de confirmar)."""
        pode, motivo = configuracoes.pode_gravar_em(self._pasta)
        if not pode:
            self._avisar(motivo)
            return
        if self.caminho.exists():
            self._avisar("")
            self.aviso.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
            self.aviso.setText("Já existe um arquivo com esse nome - eu pergunto antes de substituir.")
            self.aviso.setVisible(True)
            return
        self.aviso.setStyleSheet(f"color: {VERMELHO}; font-size: 12px;")
        self._avisar("")

    def pronto_para_gravar(self) -> tuple[bool, str]:
        """(pode gravar?, motivo se nao puder) - usado para ligar/desligar o botão Processar."""
        return configuracoes.pode_gravar_em(self._pasta)
