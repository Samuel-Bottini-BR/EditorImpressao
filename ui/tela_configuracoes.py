"""Tela de Configurações do programa.

Pensada para crescer: atalhos editáveis são a primeira seção, mas o desenho
já reserva espaço para outras seções de configuração entrarem aqui depois,
sem precisar de um menu novo (decisão tomada com o Samuel).

Cada atalho vem do registro único em `atalhos.py` - a mesma tabela que
alimenta o menu e a "Ajuda -> Lista de atalhos", para nunca divergir.
"""

from __future__ import annotations

import functools

import atalhos
import configuracoes
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui import estilo


class TelaConfiguracoes(QDialog):
    """Lista todo atalho do programa, com captura de tecla e aviso de conflito."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.resize(480, 560)

        raiz = QVBoxLayout(self)

        # Item 2.16 (CONTROLE MINIMO, provisorio ate o layout): quantas paginas
        # o programa faz ao mesmo tempo. De fabrica todos os nucleos, como o
        # ScanTailor; "Uma página por vez" e o jeito de antes (o desligar da
        # regra 8). So muda a velocidade, nunca o resultado.
        titulo_velocidade = QLabel("Velocidade")
        titulo_velocidade.setObjectName("titulo")
        raiz.addWidget(titulo_velocidade)
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
        raiz.addLayout(linha_nucleos)

        # Item 2.19 (CONTROLE MINIMO, provisorio ate o layout): a unidade das
        # medidas na tela (core/unidades.py; de fabrica centimetros) e a
        # receita de todo livro novo (core/perfis.py; de fabrica nenhuma).
        from core import perfis, unidades

        titulo_medidas = QLabel("Medidas e receitas")
        titulo_medidas.setObjectName("titulo")
        raiz.addWidget(titulo_medidas)
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
        raiz.addLayout(linha_unidade)
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
        raiz.addLayout(linha_receita)

        # Item 2.6 (CONTROLE MINIMO, provisorio ate o layout): as duas medidas
        # da encadernacao que dependem da impressora (g11, 14/10/2026: "1 cm a
        # partir de onde a impressora imprime (1,3 cm do papel)"; "A impressora
        # ainda come mais uns 3 mm na borda"). Ficam nas escolhas da janela
        # "Montar para imprimir" (configuracoes.json, chave "impressao").
        from PySide6.QtWidgets import QDoubleSpinBox

        from core import impressao as imp

        titulo_impressao = QLabel("Impressão")
        titulo_impressao.setObjectName("titulo")
        raiz.addWidget(titulo_impressao)
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
        raiz.addLayout(linha_impressao)

        def guardar_impressao(_valor=None):
            atual = imp.OpcoesDeImpressao.de_dicionario(configuracoes.ler("impressao"))
            atual.margem_mm = float(self.margem_da_impressao.value())
            atual.borda_da_impressora_mm = float(self.borda_da_impressora.value())
            configuracoes.escrever("impressao", atual.para_dicionario())

        self.margem_da_impressao.valueChanged.connect(guardar_impressao)
        self.borda_da_impressora.valueChanged.connect(guardar_impressao)

        titulo = QLabel("Atalhos de teclado")
        titulo.setObjectName("titulo")
        raiz.addWidget(titulo)

        explicacao = QLabel(
            "Clique numa tecla e aperte a combinação que você quer usar no lugar."
        )
        estilo.estilizar(explicacao, lambda: f"color: {estilo.TEXTO_FRACO};")
        explicacao.setWordWrap(True)
        raiz.addWidget(explicacao)

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
        fechar = QPushButton("Fechar")
        fechar.setDefault(True)
        fechar.clicked.connect(self.accept)
        rodape.addWidget(fechar)
        raiz.addLayout(rodape)

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
