"""TELA 2 - O que fazer: as caixinhas do que o programa deve fazer.

Cada caixinha (dividir, limpar, endireitar, cortar, montar cadernos) liga a um
campo de `Projeto` (modelos.py) em tempo real - _mudou() e chamado a cada
clique e escreve direto no projeto, sem botao "aplicar" separado. O resumo em
portugues embaixo (core.pipeline.resumo_em_portugues) e o que confirma para a
pessoa o que ela acabou de marcar, sem jargao.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from core.cadernos import paginas_por_caderno_valido
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO
from core.pipeline import resumo_em_portugues
from modelos import Projeto
from ui.estilo import TEXTO_FRACO
from ui.widgets.folhear_pdf import FolhearPDF

FILTROS_NA_TELA = [
    (ORIGINAL, "Original", "não mexe na página"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado, arquivo pequeno"),
    (MELHORAR, "Melhorar", "limpa o fundo e mantém as cores"),
    (MAGICO_PRO, "Mágico pro", "cor viva e texto nítido"),
]

OPCOES_CADERNO = [8, 12, 16, 20, 24, 32, 40]


class TelaOpcoes(QWidget):
    """A tela de "o que fazer": caixinhas de escolha + prevalidacao do PDF."""

    voltar = Signal()
    conferir = Signal()

    def __init__(self, parent=None) -> None:
        """Monta as duas colunas: as caixinhas de escolha a esquerda, o
        folhear do PDF de entrada a direita (ver FolhearPDF e o comentario
        abaixo sobre por que as duas colunas existem)."""
        super().__init__(parent)
        self.projeto: Projeto | None = None
        self.total_folhas = 0

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(46, 26, 46, 22)
        camadas.setSpacing(14)

        self.titulo = QLabel("Marque o que você quer fazer")
        self.titulo.setObjectName("titulo")
        camadas.addWidget(self.titulo)

        self.arquivo = QLabel("")
        self.arquivo.setObjectName("fraco")
        camadas.addWidget(self.arquivo)

        # Duas colunas: as escolhas de um lado, o livro do outro. Antes as
        # escolhas ocupavam a largura toda e sobrava meia tela em branco - e a
        # pessoa marcava "dividir folhas ao meio" sem ter visto se a folha tem
        # mesmo duas páginas. Ver FolhearPDF.
        colunas = QHBoxLayout()
        colunas.setSpacing(20)
        camadas.addLayout(colunas, 1)

        esquerda = QVBoxLayout()
        esquerda.setSpacing(14)
        colunas.addLayout(esquerda, 3)

        cartao = QFrame()
        cartao.setObjectName("cartao")
        opcoes = QVBoxLayout(cartao)
        opcoes.setContentsMargins(20, 16, 20, 16)
        opcoes.setSpacing(6)

        self.cx_dividir = self._caixa(
            "Dividir folhas ao meio", "esta folha tem 2 páginas do livro", opcoes
        )
        opcoes.addWidget(_separador())

        self.cx_limpar = self._caixa("Limpar a folha", "tira o amarelado", opcoes)
        self.painel_filtros = self._montar_filtros()
        opcoes.addWidget(self.painel_filtros)
        opcoes.addWidget(_separador())

        self.cx_endireitar = self._caixa(
            "Endireitar folhas tortas", "corrige páginas inclinadas", opcoes
        )
        opcoes.addWidget(_separador())

        self.cx_cortar = self._caixa(
            "Cortar as bordas", "tira a borda preta e a sombra do scanner", opcoes
        )
        opcoes.addWidget(_separador())

        self.cx_cadernos = self._caixa(
            "Montar cadernos para impressão",
            "para imprimir, dobrar ao meio e costurar", opcoes,
        )
        self.painel_caderno = self._montar_caderno()
        opcoes.addWidget(self.painel_caderno)

        esquerda.addWidget(cartao)

        self.faixa = QFrame()
        self.faixa.setObjectName("faixaInfo")
        faixa_camada = QHBoxLayout(self.faixa)
        faixa_camada.setContentsMargins(16, 12, 16, 12)
        self.resumo = QLabel("")
        self.resumo.setWordWrap(True)
        faixa_camada.addWidget(self.resumo)
        esquerda.addWidget(self.faixa)

        esquerda.addStretch()

        direita = QVBoxLayout()
        direita.setSpacing(6)
        rotulo_livro = QLabel("O livro, como está agora")
        rotulo_livro.setStyleSheet(f"color: {TEXTO_FRACO};")
        direita.addWidget(rotulo_livro)
        self.folhear = FolhearPDF()
        direita.addWidget(self.folhear, 1)
        colunas.addLayout(direita, 2)

        rodape = QHBoxLayout()
        botao_voltar = QPushButton("voltar")
        botao_voltar.clicked.connect(self._sair)
        rodape.addWidget(botao_voltar)
        rodape.addStretch()
        self.botao_conferir = QPushButton("Conferir")
        self.botao_conferir.setObjectName("primario")
        self.botao_conferir.clicked.connect(self._seguir)
        rodape.addWidget(self.botao_conferir)
        camadas.addLayout(rodape)

        for caixa in (self.cx_dividir, self.cx_limpar, self.cx_endireitar,
                      self.cx_cortar, self.cx_cadernos):
            caixa.toggled.connect(self._mudou)

    # --- montagem ---------------------------------------------------------

    def _caixa(self, titulo: str, explicacao: str, destino: QVBoxLayout) -> QCheckBox:
        """Uma caixinha de marcar com a explicacao em portugues simples embaixo."""
        bloco = QVBoxLayout()
        bloco.setSpacing(1)
        caixa = QCheckBox(titulo)
        caixa.setChecked(True)
        bloco.addWidget(caixa)
        rotulo = QLabel("        " + explicacao)
        rotulo.setStyleSheet(f"color: {TEXTO_FRACO};")
        bloco.addWidget(rotulo)
        destino.addLayout(bloco)
        return caixa

    def _montar_filtros(self) -> QWidget:
        """Painel de radio-buttons com os quatro filtros (FILTROS_NA_TELA).
        So aparece quando "Limpar a folha" esta marcada - ver _mudou."""
        painel = QWidget()
        grade = QGridLayout(painel)
        grade.setContentsMargins(34, 6, 0, 6)
        grade.setSpacing(8)

        self.grupo_filtros = QButtonGroup(self)
        for i, (chave, nome, explicacao) in enumerate(FILTROS_NA_TELA):
            radio = QRadioButton(nome)
            radio.setProperty("filtro", chave)
            radio.setChecked(chave == PRETO_E_BRANCO)
            radio.toggled.connect(self._mudou)
            self.grupo_filtros.addButton(radio)
            grade.addWidget(radio, i // 2, (i % 2) * 2)

            rotulo = QLabel(explicacao)
            rotulo.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
            grade.addWidget(rotulo, i // 2, (i % 2) * 2 + 1)
        return painel

    def _montar_caderno(self) -> QWidget:
        """Combo de "páginas por caderno". So aparece quando "Montar cadernos"
        esta marcada - ver _mudou."""
        painel = QWidget()
        linha = QHBoxLayout(painel)
        linha.setContentsMargins(34, 4, 0, 4)
        linha.addWidget(QLabel("páginas por caderno:"))
        self.combo_caderno = QComboBox()
        for valor in OPCOES_CADERNO:
            self.combo_caderno.addItem(str(valor), valor)
        self.combo_caderno.setCurrentText("20")
        self.combo_caderno.currentIndexChanged.connect(self._mudou)
        linha.addWidget(self.combo_caderno)
        linha.addStretch()
        return painel

    # --- uso --------------------------------------------------------------

    def carregar(self, projeto: Projeto, total_folhas: int) -> None:
        """Preenche a tela com o projeto escolhido: cada caixinha volta ao
        valor salvo, e o folhear abre o PDF de entrada para a pessoa ver antes
        de marcar o que fazer."""
        self.projeto = projeto
        self.total_folhas = total_folhas

        from pathlib import Path

        nome = Path(projeto.caminho_entrada).name
        self.arquivo.setText(f"{nome}  -  {total_folhas} folhas")

        self.cx_dividir.setChecked(projeto.dividir_folhas)
        self.cx_limpar.setChecked(projeto.limpar)
        self.cx_endireitar.setChecked(projeto.endireitar)
        self.cx_cortar.setChecked(projeto.cortar_bordas)
        self.cx_cadernos.setChecked(projeto.montar_cadernos)
        self.combo_caderno.setCurrentText(str(projeto.paginas_por_caderno))

        for botao in self.grupo_filtros.buttons():
            if botao.property("filtro") == projeto.filtro_padrao:
                botao.setChecked(True)
        self._mudou()

        self.folhear.abrir(projeto.caminho_entrada)

    def _sair(self) -> None:
        """Solta o arquivo antes de sair. Ver FolhearPDF.fechar."""
        self.folhear.fechar()
        self.voltar.emit()

    def _seguir(self) -> None:
        """Idem, indo para a conferência: quem lê o livro daqui é o pipeline."""
        self.folhear.fechar()
        self.conferir.emit()

    def _filtro_escolhido(self) -> str:
        """O filtro marcado no grupo de radio-buttons, ou Preto e branco por padrão."""
        for botao in self.grupo_filtros.buttons():
            if botao.isChecked():
                return str(botao.property("filtro"))
        return PRETO_E_BRANCO

    def _mudou(self) -> None:
        """Guarda as escolhas e atualiza o resumo ao vivo."""
        if self.projeto is None:
            return

        self.projeto.dividir_folhas = self.cx_dividir.isChecked()
        self.projeto.limpar = self.cx_limpar.isChecked()
        self.projeto.endireitar = self.cx_endireitar.isChecked()
        self.projeto.cortar_bordas = self.cx_cortar.isChecked()
        self.projeto.montar_cadernos = self.cx_cadernos.isChecked()
        self.projeto.filtro_padrao = self._filtro_escolhido()
        self.projeto.paginas_por_caderno = paginas_por_caderno_valido(
            self.combo_caderno.currentData() or 20
        )

        # os painéis so aparecem quando fazem sentido
        self.painel_filtros.setVisible(self.projeto.limpar)
        self.painel_caderno.setVisible(self.projeto.montar_cadernos)

        self.resumo.setText(resumo_em_portugues(self.projeto, self.total_folhas))
        self.botao_conferir.setEnabled(self.projeto.alguma_funcao_marcada)


def _separador() -> QFrame:
    """Uma linha horizontal fina, para separar os blocos de opcao."""
    linha = QFrame()
    linha.setFrameShape(QFrame.HLine)
    linha.setStyleSheet("color: #e5e7eb; margin: 4px 0;")
    return linha
