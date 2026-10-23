"""Tela de Configurações do programa.

Etapa 7 do layout (21/10/2026). Rodada 13, 807 (Samuel: "B — Lista das partes à esquerda"):
as partes ficam numa lista à esquerda e, clicando numa, ela aparece à direita. Rodada 12, 707
("C — Nos dois lugares"): o tema se troca aqui (parte "Aparência") e no menu Ver.

As partes de hoje:
    Aparência            o tema (escuro, cinza de fábrica, claro).
    Atalhos de teclado   cada atalho, com captura de tecla e aviso de conflito (a tela de antes).
    Velocidade           páginas ao mesmo tempo (item 2.16; juntado em 23/10/2026).
    Medidas e receitas   cm/mm/polegadas e a receita do livro novo (item 2.19).
    Impressão            margem da encadernação e a beirada que a impressora não imprime (2.6).

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
    QComboBox,
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

# Juncao de 23/10/2026: as tres ultimas sao dos itens 2.16, 2.19 e 2.6 (ver
# _parte_velocidade); ficam no fim para nao mudar a ordem das do layout.
PARTES = ("Aparência", "Atalhos de teclado", "Velocidade", "Medidas e receitas", "Impressão")


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
        self.pilha.addWidget(self._parte_velocidade())
        self.pilha.addWidget(self._parte_medidas())
        self.pilha.addWidget(self._parte_impressao())
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

    # --- as partes do Implementador B (juncao de 23/10/2026) -----------------
    # Os controles minimos dos itens 2.16, 2.19 e 2.6 (ramo
    # fase2-ferramentas-2026-10-22) eram linhas soltas na tela de antes; na
    # juncao com o layout em partes (etapa 7) viraram tres partes no fim da
    # lista, com os mesmos controles, nomes e titulos. Provisorio: o lugar
    # final e do agente de layout. Seguro mudar: a ordem das partes.

    def _parte_velocidade(self) -> QWidget:
        """Item 2.16 (CONTROLE MINIMO, provisorio ate o layout): quantas paginas
        o programa faz ao mesmo tempo. De fabrica todos os nucleos, como o
        ScanTailor; "Uma página por vez" e o jeito de antes (o desligar da
        regra 8)."""
        parte = QWidget()
        caixa = QVBoxLayout(parte)
        caixa.setContentsMargins(24, 18, 24, 12)
        caixa.setSpacing(10)
        self._cabeca(caixa, "Velocidade", "Quantas páginas o programa faz ao mesmo tempo. Só muda a velocidade, nunca o resultado.")
        linha_nucleos = QHBoxLayout()
        linha_nucleos.addWidget(QLabel("Páginas ao mesmo tempo:"))
        self.combo_nucleos = QComboBox()
        import os

        total = os.cpu_count() or 1
        self.combo_nucleos.addItem(f"Todos os núcleos do processador ({total})", 0)
        self.combo_nucleos.addItem("Uma página por vez (como antes)", 1)
        for n in (2, 4, 8):
            if n < total:
                self.combo_nucleos.addItem(f"{n} páginas", n)
        indice = self.combo_nucleos.findData(int(configuracoes.ler("nucleos") or 0))
        self.combo_nucleos.setCurrentIndex(max(0, indice))
        self.combo_nucleos.setToolTip(
            "Mais páginas ao mesmo tempo = o livro fica pronto mais rápido, usando mais "
            "memória. O resultado é o mesmo. O programa usa menos se faltar memória.")
        self.combo_nucleos.currentIndexChanged.connect(
            lambda _i: configuracoes.escrever("nucleos", int(self.combo_nucleos.currentData())))
        linha_nucleos.addWidget(self.combo_nucleos, 1)
        caixa.addLayout(linha_nucleos)
        caixa.addStretch()
        return parte

    def _parte_medidas(self) -> QWidget:
        """Item 2.19 (CONTROLE MINIMO, provisorio ate o layout): a unidade das
        medidas na tela (core/unidades.py; de fabrica centimetros) e a
        receita de todo livro novo (core/perfis.py; de fabrica nenhuma)."""
        parte = QWidget()
        caixa = QVBoxLayout(parte)
        caixa.setContentsMargins(24, 18, 24, 12)
        caixa.setSpacing(10)
        self._cabeca(caixa, "Medidas e receitas", "A unidade das medidas na tela e a receita com que todo livro novo começa.")
        from core import perfis, unidades

        linha_unidade = QHBoxLayout()
        linha_unidade.addWidget(QLabel("Medidas em:"))
        self.combo_unidade = QComboBox()
        for codigo in unidades.UNIDADES:
            self.combo_unidade.addItem(unidades.NOMES[codigo], codigo)
        self.combo_unidade.setCurrentIndex(max(0, self.combo_unidade.findData(unidades.da_maquina())))
        self.combo_unidade.currentIndexChanged.connect(
            lambda _i: configuracoes.escrever(unidades.CHAVE_DAS_CONFIGURACOES,
                                              self.combo_unidade.currentData()))
        linha_unidade.addWidget(self.combo_unidade, 1)
        caixa.addLayout(linha_unidade)
        linha_receita = QHBoxLayout()
        linha_receita.addWidget(QLabel("Receita de todo livro novo:"))
        self.combo_receita_nova = QComboBox()
        for nome in perfis.nomes():
            self.combo_receita_nova.addItem(nome, nome)
        atual = perfis.do_livro_novo() or perfis.NOME_DE_FABRICA
        self.combo_receita_nova.setCurrentIndex(max(0, self.combo_receita_nova.findData(atual)))
        self.combo_receita_nova.setToolTip(
            "As caixinhas com que todo livro novo começa. As receitas se guardam na tela "
            "\"O que fazer\".")
        self.combo_receita_nova.currentIndexChanged.connect(
            lambda _i: perfis.definir_do_livro_novo(self.combo_receita_nova.currentData()))
        linha_receita.addWidget(self.combo_receita_nova, 1)
        caixa.addLayout(linha_receita)
        caixa.addStretch()
        return parte

    def _parte_impressao(self) -> QWidget:
        """Item 2.6 (CONTROLE MINIMO, provisorio ate o layout): as duas medidas
        da encadernacao que dependem da impressora (g11, 14/10/2026). Ficam nas
        escolhas da janela "Montar para imprimir" (configuracoes.json, chave
        "impressao")."""
        parte = QWidget()
        caixa = QVBoxLayout(parte)
        caixa.setContentsMargins(24, 18, 24, 12)
        caixa.setSpacing(10)
        self._cabeca(caixa, "Impressão", "As duas medidas da encadernação que dependem da impressora.")
        from PySide6.QtWidgets import QDoubleSpinBox

        from core import impressao as imp

        opcoes_de_impressao = imp.OpcoesDeImpressao.de_dicionario(configuracoes.ler("impressao"))
        linha_impressao = QHBoxLayout()
        linha_impressao.addWidget(QLabel("Margem da encadernação:"))
        self.margem_da_impressao = QDoubleSpinBox()
        self.margem_da_impressao.setRange(0.0, 50.0)
        self.margem_da_impressao.setDecimals(1)
        self.margem_da_impressao.setSuffix(" mm")
        self.margem_da_impressao.setValue(opcoes_de_impressao.margem_mm)
        linha_impressao.addWidget(self.margem_da_impressao)
        linha_impressao.addWidget(QLabel("A impressora não imprime:"))
        self.borda_da_impressora = QDoubleSpinBox()
        self.borda_da_impressora.setRange(0.0, 20.0)
        self.borda_da_impressora.setDecimals(1)
        self.borda_da_impressora.setSuffix(" mm da beirada")
        self.borda_da_impressora.setValue(opcoes_de_impressao.borda_da_impressora_mm)
        linha_impressao.addWidget(self.borda_da_impressora)
        caixa.addLayout(linha_impressao)

        def guardar_impressao(_valor=None):
            atual = imp.OpcoesDeImpressao.de_dicionario(configuracoes.ler("impressao"))
            atual.margem_mm = float(self.margem_da_impressao.value())
            atual.borda_da_impressora_mm = float(self.borda_da_impressora.value())
            configuracoes.escrever("impressao", atual.para_dicionario())

        self.margem_da_impressao.valueChanged.connect(guardar_impressao)
        self.borda_da_impressora.valueChanged.connect(guardar_impressao)
        caixa.addStretch()
        return parte

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
