"""Tela de Configurações do programa.

Etapa 7 do layout (21/10/2026). Rodada 13, 807 (Samuel: "B — Lista das partes à esquerda"):
as partes ficam numa lista à esquerda e, clicando numa, ela aparece à direita. Rodada 12, 707
("C — Nos dois lugares"): o tema se troca aqui (parte "Aparência") e no menu Ver.

As partes de hoje:
    Aparência            o tema (escuro, cinza de fábrica, claro).
    Atalhos de teclado   cada atalho, com captura de tecla e aviso de conflito (a tela de antes).

Ainda não entram (não existem no programa; não foram inventadas): "Para todos os livros" (a
troca do retângulo do corte do G6 para todos os livros) e o "Lado direito" (rodada 14, 902 C:
os outros jeitos do lado direito ainda não foram construídos). Os nomes das partes foram
sugestão do agente de layout na rodada 13.

Cada atalho vem do registro único em `atalhos.py` - a mesma tabela que alimenta o menu e a
"Ajuda -> Lista de atalhos", para nunca divergir. Seguro mudar: textos e tamanhos. Arriscado:
gravar o tema por outro caminho que não `janela._trocar_tema` (o menu Ver deixaria de acompanhar).
"""

from __future__ import annotations

import functools

import atalhos
import configuracoes
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QListWidget,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui import estilo

PARTES = ("Aparência", "Atalhos de teclado")


class TelaConfiguracoes(QDialog):
    """As Configurações com a lista das partes à esquerda (807 B)."""

    def __init__(self, parent=None, parte: str = "Aparência") -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(760, 560)

        raiz = QVBoxLayout(self)
        raiz.setContentsMargins(0, 0, 0, 12)
        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)
        self.lista = QListWidget()
        self.lista.setObjectName("partesDasConfiguracoes")
        self.lista.setFixedWidth(210)
        for nome in PARTES:
            self.lista.addItem(nome)
        estilo.estilizar(self.lista, lambda: (
            f"QListWidget#partesDasConfiguracoes {{ background: {estilo.cor('painel')}; border: none;"
            f" border-right: 1px solid {estilo.cor('linha')}; padding: 10px 8px; font-size: 13px; }}"
            f"QListWidget#partesDasConfiguracoes::item {{ padding: 9px 10px; border-radius: 4px; }}"
            f"QListWidget#partesDasConfiguracoes::item:selected {{ background: {estilo.cor('sel')};"
            f" color: {estilo.cor('forte')}; }}"))
        self.lista.setCursor(Qt.PointingHandCursor)
        corpo.addWidget(self.lista)
        self.pilha = QStackedWidget()
        self.pilha.addWidget(self._parte_aparencia())
        self.pilha.addWidget(self._parte_atalhos())
        corpo.addWidget(self.pilha, 1)
        raiz.addLayout(corpo, 1)
        self.lista.currentRowChanged.connect(self.pilha.setCurrentIndex)
        self.lista.setCurrentRow(PARTES.index(parte) if parte in PARTES else 0)

        rodape = QHBoxLayout()
        rodape.setContentsMargins(16, 0, 16, 0)
        rodape.addStretch()
        fechar = QPushButton("Fechar")
        fechar.setDefault(True)
        fechar.clicked.connect(self.accept)
        rodape.addWidget(fechar)
        raiz.addLayout(rodape)

    # --- as partes -----------------------------------------------------------

    @staticmethod
    def _cabeca(caixa: QVBoxLayout, titulo: str, frase: str) -> None:
        rotulo = QLabel(titulo)
        rotulo.setObjectName("titulo")
        caixa.addWidget(rotulo)
        explicacao = QLabel(frase)
        explicacao.setWordWrap(True)
        estilo.estilizar(explicacao, lambda: f"color: {estilo.TEXTO_FRACO};")
        caixa.addWidget(explicacao)

    def _parte_aparencia(self) -> QWidget:
        """Aparência: o tema (rodada 7: os três, cinza de fábrica; 707 C)."""
        parte = QWidget()
        caixa = QVBoxLayout(parte)
        caixa.setContentsMargins(24, 18, 24, 12)
        caixa.setSpacing(10)
        self._cabeca(caixa, "Aparência", "As cores do programa. Vale na hora, em todas as telas.")
        linha = QHBoxLayout()
        self.grupo_tema = QButtonGroup(self)
        self.botoes_tema: dict[str, QRadioButton] = {}
        for nome in estilo.TEMAS:
            texto = estilo.NOMES_DOS_TEMAS[nome] + (" (de fábrica)" if nome == estilo.TEMA_DE_FABRICA else "")
            botao = QRadioButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setChecked(nome == estilo.tema_atual())
            botao.toggled.connect(lambda marcado, t=nome: marcado and self._trocar_tema(t))
            self.grupo_tema.addButton(botao)
            self.botoes_tema[nome] = botao
            linha.addWidget(botao)
        linha.addStretch()
        caixa.addLayout(linha)
        caixa.addStretch()
        return parte

    def _trocar_tema(self, nome: str) -> None:
        """Troca o tema pelo mesmo caminho do menu Ver > Tema (a janela marca o
        menu e repinta tudo); sem a janela, só pelo estilo."""
        janela = self.parent()
        if janela is not None and hasattr(janela, "_trocar_tema"):
            janela._trocar_tema(nome)
        else:
            estilo.definir_tema(nome)
            estilo.reaplicar_em_tudo()

    def _parte_atalhos(self) -> QWidget:
        """Atalhos de teclado: a tela de antes, inteira."""
        parte = QWidget()
        raiz = QVBoxLayout(parte)
        raiz.setContentsMargins(24, 18, 24, 6)
        self._cabeca(raiz, "Atalhos de teclado",
                     "Clique numa tecla e aperte a combinação que você quer usar no lugar.")
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
        self.aviso.setObjectName("avisoErro")   # cor do tema (ui/estilo.py)
        self.aviso.setWordWrap(True)
        raiz.addWidget(self.aviso)

        rodape = QHBoxLayout()
        restaurar = QPushButton("Restaurar todos os padrões")
        restaurar.clicked.connect(self._restaurar_tudo)
        rodape.addWidget(restaurar)
        rodape.addStretch()
        raiz.addLayout(rodape)
        return parte

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
