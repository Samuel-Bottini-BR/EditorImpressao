"""A janela que aparece ao clicar em "Confirmar e processar".

"Salvar em" e "Nome do arquivo" moravam na tela de trabalho, ocupando uma faixa
inteira de altura o tempo todo. Eles importam num momento so - o de gravar -, e
e aqui que passam a aparecer. So isso devolve uma faixa de altura para a
pagina, que e o que a pessoa precisa olhar.

Alem da pasta e do nome, esta janela avisa duas coisas antes de comecar um
processamento que pode levar minutos:

  o arquivo ja existe            para nao apagar por engano o trabalho de ontem
  ha paginas nao conferidas      porque processar sem olhar e o caminho mais
                                 curto para reimprimir um livro errado
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

from ui.estilo import FOLHA_DE_ESTILO, TEXTO_FRACO
from ui.widgets.destino import SeletorDestino

LARANJA, LARANJA_FUNDO = "#ef9f27", "#faeeda"


class JanelaConfirmar(QDialog):
    """Pasta, nome e os avisos. Devolve o caminho escolhido, ou None."""

    def __init__(self, projeto, nome_sugerido: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Confirmar e processar")
        self.setStyleSheet(FOLHA_DE_ESTILO)
        self.setMinimumWidth(620)
        self.projeto = projeto

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(22, 18, 22, 16)
        camadas.setSpacing(12)

        titulo = QLabel("Onde salvar o livro pronto")
        titulo.setObjectName("secao")
        camadas.addWidget(titulo)

        self.destino = SeletorDestino()
        self.destino.definir(projeto.caminho_saida or None, nome_sugerido)
        self.destino.alterado.connect(self._reavaliar)
        camadas.addWidget(self.destino)

        self.aviso_existe = self._faixa_de_aviso()
        camadas.addWidget(self.aviso_existe)

        self.aviso_conferir = self._faixa_de_aviso()
        camadas.addWidget(self.aviso_conferir)

        resumo = QLabel(self._frase_do_livro())
        resumo.setStyleSheet(f"color: {TEXTO_FRACO};")
        camadas.addWidget(resumo)

        botoes = QDialogButtonBox()
        self.botao_processar = botoes.addButton(
            "Processar", QDialogButtonBox.AcceptRole)
        self.botao_processar.setObjectName("primario")
        botoes.addButton("voltar", QDialogButtonBox.RejectRole)
        botoes.accepted.connect(self.accept)
        botoes.rejected.connect(self.reject)
        camadas.addWidget(botoes)

        self._reavaliar()

    # --- pedacos ----------------------------------------------------------

    def _faixa_de_aviso(self) -> QFrame:
        faixa = QFrame()
        faixa.setStyleSheet(
            f"QFrame {{ background: {LARANJA_FUNDO}; border: 1px solid {LARANJA}; "
            "border-radius: 8px; }} QLabel { background: transparent; }")
        linha = QHBoxLayout(faixa)
        linha.setContentsMargins(14, 10, 14, 10)
        rotulo = QLabel("")
        rotulo.setWordWrap(True)
        linha.addWidget(rotulo)
        faixa.rotulo = rotulo
        faixa.hide()
        return faixa

    def _frase_do_livro(self) -> str:
        paginas = [p for p in self.projeto.paginas if not p.apagada]
        apagadas = len(self.projeto.paginas) - len(paginas)
        frase = f"{len(paginas)} páginas vão para o PDF"
        if apagadas:
            frase += f", e {apagadas} foram apagadas"
        return frase + "."

    # --- avisos -----------------------------------------------------------

    def _nao_conferidas(self) -> int:
        return sum(1 for p in self.projeto.paginas
                   if not p.apagada and not p.revisada)

    def _reavaliar(self) -> None:
        caminho = self.destino.caminho

        if caminho.exists():
            self.aviso_existe.rotulo.setText(
                f"Já existe um arquivo chamado <b>{caminho.name}</b> nessa "
                "pasta. Se continuar, ele será substituído.")
            self.aviso_existe.show()
        else:
            self.aviso_existe.hide()

        faltam = self._nao_conferidas()
        if faltam:
            self.aviso_conferir.rotulo.setText(
                f"Ainda há <b>{faltam} página(s)</b> que você não conferiu. "
                "Dá para processar assim mesmo, mas o que não foi olhado sai "
                "do jeito que o programa decidiu sozinho.")
            self.aviso_conferir.show()
        else:
            self.aviso_conferir.hide()

        pode, motivo = self.destino.pronto_para_gravar()
        self.botao_processar.setEnabled(pode)
        self.botao_processar.setToolTip("" if pode else motivo)

    # --- resultado --------------------------------------------------------

    @property
    def caminho(self) -> Path:
        return self.destino.caminho


def pedir_confirmacao(projeto, nome_sugerido: str, parent=None) -> Path | None:
    """Mostra a janela. Devolve o caminho escolhido, ou None se desistiu."""
    janela = JanelaConfirmar(projeto, nome_sugerido, parent)
    if janela.exec() != QDialog.Accepted:
        return None
    return janela.caminho
