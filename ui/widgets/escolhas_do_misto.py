"""As escolhas do modo Misto: a caixinha "Só as letras" e o que vem com ela.

PROVISÓRIO ATÉ O LAYOUT (05/10/2026). Exceção da gerente para o implementador
mexer em ui/ só nisto: ligar o Misto à tela. O Samuel (conferência 14): "ele
tem que mostrar as outras opções, isso podemos discutir como vai ser no
layout, com o agente de layout". A aparência final é do agente de layout.

O QUE MOSTRA (o mesmo widget na tela "O que fazer", para o livro, e na aba
Filtro, para a página)
    - a caixinha "Só as letras" (com o quadrado à vista, regra O1);
    - logo abaixo, só com ela marcada, três botões lado a lado, bem visíveis,
      o escolhido destacado em azul (conferência 8: "tem que ser algo bem
      visivel para eu poder escolher"): "Guardar a tinta forte" (A, de
      fábrica), "Guardar tudo" (B), "Guardar só o texto" (C) (nomes da
      Rodada 10 do layout, 07/10/2026), e uma frase curta dizendo o que o
      escolhido faz;
    - num "Mais opções" recolhido: o papel de dentro das gravuras (P2) e as
      letras dentro de molduras e iluminuras (P4).
    Português sem jargão, sem emoji.

O QUE NÃO FAZ
    Não grava nada: avisa pelos sinais e quem usa decide onde gravar (o livro
    em ui/tela_opcoes.py; a página, com desfazer, em ui/tela_conferir.py).
    mostrar() acerta os controles SEM emitir sinal (é o que se chama ao trocar
    de página, ao desfazer e ao abrir).

Os valores são os de core/misto.py (FORA_REDE, PAPEL_BRANCO...). Seguro mudar:
os textos e o desenho. Arriscado: emitir sinal dentro de mostrar() (cada troca
de página viraria uma ação no desfazer).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core import misto
from ui import estilo
from ui.estilo import estilo_da_caixinha_com_quadrado

# (valor, texto do botão, o que ele faz em uma frase)
# Nomes e frases do conjunto 2 do layout (Rodada 10, pergunta 501, escolhidos
# pelo Samuel em 07/10/2026, com o A trocado por ele: "guardar tinta forte
# estava bom ao invez de guardar o que é escuro, mude esse."). Antes: "Tudo em
# preto e branco" (B) e "Só o texto achado" (C).
BOTOES_DO_TEXTO = [
    (misto.FORA_REDE, "Guardar a tinta forte",
     "fora do texto achado, guarda a tinta tão escura quanto as letras "
     "(música, letra grande, desenho); a mancha clara sai"),
    (misto.FORA_TUDO, "Guardar tudo",
     "nada sai: tudo o que não é gravura vira preto e branco, como no Preto e "
     "branco de sempre"),
    (misto.FORA_APAGAR, "Guardar só o texto",
     "guarda só o texto que o programa achou; o resto que não é gravura vira "
     "papel branco"),
]

ESCOLHAS_DO_PAPEL = [
    (misto.PAPEL_BRANCO, "branco"),
    (misto.PAPEL_COMO_ESCANEADO, "como foi escaneado"),
]

ESCOLHAS_DAS_LETRAS = [
    (misto.LETRAS_COR_PAPEL_BRANCO, "com a cor delas e papel branco atrás"),
    (misto.LETRAS_COR_FUNDO_ORIGINAL, "com a cor delas e o fundo como foi escaneado"),
    (misto.LETRAS_PRETAS, "pretas"),
]

EXPLICACAO_DA_CAIXINHA = ("no Preto e branco, só as letras viram preto e branco; "
                          "gravuras, fotos, molduras e iluminuras ficam como no original")

def estilo_dos_botoes() -> str:
    """A folha dos três botões, com as cores do tema da vez (ui/estilo.py)."""
    return (
        f"QPushButton#escolhaDoMisto {{ padding: 6px 12px; border: 2px solid {estilo.BORDA};"
        f" border-radius: 8px; background: {estilo.cor('botao')}; font-weight: 600; }}"
        f" QPushButton#escolhaDoMisto:hover {{ border-color: {estilo.AZUL}; }}"
        f" QPushButton#escolhaDoMisto:checked {{ background: {estilo.AZUL}; color: white;"
        f" border-color: {estilo.AZUL_ESCURO}; }}")


class EscolhasDoMisto(QWidget):
    """A caixinha "Só as letras" com os três botões e o "Mais opções".

    compacto=True (aba Filtro, onde a altura é pouca e a largura sobra): sem
    as frases (a da caixinha e a do botão escolhido vão para a dica do
    mouse), o "Mais opções" na linha dos botões e as duas escolhas dele na
    linha da caixinha, à direita (que fica vazia) - a 1280 x 657 a aba não
    tem altura para mais uma linha (print de 05/10: numa linha a mais, os
    botões saíam espremidos).
    compacto=False (tela "O que fazer", coluna estreita: a 1280 de largura
    sobram uns 600 pontos): o "Mais opções" numa linha embaixo dos botões e
    cada escolha com o nome em cima da lista - senão a linha passava da
    coluna e saía cortada (print de 05/10).
    """

    so_as_letras_mudou = Signal(bool)
    fora_do_texto_escolhido = Signal(str)
    papel_escolhido = Signal(str)
    letras_escolhidas = Signal(str)

    def __init__(self, compacto: bool = False, parent=None) -> None:
        super().__init__(parent)
        self._acertando = False
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(3 if compacto else 4)

        self.caixa = QCheckBox("Só as letras")
        estilo.estilizar(self.caixa, lambda: estilo_da_caixinha_com_quadrado(14))
        self.caixa.setToolTip(EXPLICACAO_DA_CAIXINHA[0].upper() + EXPLICACAO_DA_CAIXINHA[1:] + ".")
        self.caixa.toggled.connect(self._caixa_mudou)
        self._compacto = compacto
        linha_da_caixa = QHBoxLayout()
        linha_da_caixa.setContentsMargins(0, 0, 0, 0)
        linha_da_caixa.addWidget(self.caixa)
        linha_da_caixa.addStretch()
        fora.addLayout(linha_da_caixa)
        if not compacto:
            fora.addWidget(self._frase(EXPLICACAO_DA_CAIXINHA))

        # o que so aparece com a caixinha marcada
        self.painel = QWidget()
        dentro = QVBoxLayout(self.painel)
        dentro.setContentsMargins(26, 0, 0, 0)
        dentro.setSpacing(3)

        linha = QHBoxLayout()
        linha.setSpacing(6)
        self.grupo = QButtonGroup(self)
        self.grupo.setExclusive(True)
        self.botoes: dict[str, QPushButton] = {}
        self._frases: dict[str, str] = {}
        for valor, texto, frase in BOTOES_DO_TEXTO:
            botao = QPushButton(texto)
            botao.setObjectName("escolhaDoMisto")
            # compacto: um pouco mais baixos, para a linha caber a 1280 x 657
            estilo.estilizar(botao, lambda: (
                estilo_dos_botoes().replace("padding: 6px 12px", "padding: 3px 10px")
                if compacto else estilo_dos_botoes()))
            botao.setCheckable(True)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setToolTip(frase[0].upper() + frase[1:] + ".")
            botao.setProperty("valor", valor)
            botao.clicked.connect(lambda _marcado=False, v=valor: self._botao_clicado(v))
            self.grupo.addButton(botao)
            self.botoes[valor] = botao
            self._frases[valor] = frase
            linha.addWidget(botao)
        self.botao_mais = QPushButton("Mais opções")
        self.botao_mais.setObjectName("plano")
        self.botao_mais.setCheckable(True)
        self.botao_mais.setCursor(Qt.PointingHandCursor)
        self.botao_mais.toggled.connect(self._abrir_mais)
        if compacto:
            # da altura dos botoes ao lado (o "plano" de fabrica e mais alto)
            self.botao_mais.setStyleSheet("padding: 3px 8px;")
            linha.addWidget(self.botao_mais)
        linha.addStretch()
        dentro.addLayout(linha)

        self.frase_do_escolhido = self._frase("")
        self.frase_do_escolhido.setContentsMargins(2, 0, 0, 2)
        dentro.addWidget(self.frase_do_escolhido)
        self.frase_do_escolhido.setVisible(not compacto)
        if not compacto:
            linha_mais = QHBoxLayout()
            linha_mais.setContentsMargins(0, 0, 0, 0)
            linha_mais.addWidget(self.botao_mais)
            linha_mais.addStretch()
            dentro.addLayout(linha_mais)

        self.painel_mais = QWidget()
        mais = QHBoxLayout(self.painel_mais) if compacto else QVBoxLayout(self.painel_mais)
        mais.setContentsMargins(0, 2, 0, 0)
        mais.setSpacing(8 if compacto else 3)
        self.combo_papel = self._combo(ESCOLHAS_DO_PAPEL, self._papel_mudou)
        self.combo_letras = self._combo(ESCOLHAS_DAS_LETRAS, self._letras_mudou)
        if compacto:
            # na linha da caixinha: da altura dela, para a linha nao crescer
            for combo in (self.combo_papel, self.combo_letras):
                combo.setStyleSheet("QComboBox { padding: 0px 6px; font-size: 13px; }")
                combo.setMaximumHeight(22)
        for rotulo, combo in (("Papel de dentro das gravuras:", self.combo_papel),
                              ("Letras dentro de molduras e iluminuras:", self.combo_letras)):
            par = QHBoxLayout() if compacto else QVBoxLayout()
            par.setSpacing(6 if compacto else 1)
            par.addWidget(QLabel(rotulo))
            if compacto:
                par.addWidget(combo)
            else:
                linha_do_combo = QHBoxLayout()
                linha_do_combo.addWidget(combo)
                linha_do_combo.addStretch()
                par.addLayout(linha_do_combo)
            mais.addLayout(par)
        self.painel_mais.setVisible(False)
        if compacto:
            linha_da_caixa.addWidget(self.painel_mais)
        else:
            dentro.addWidget(self.painel_mais)

        self.painel.setVisible(False)
        fora.addWidget(self.painel)
        self.mostrar(False, misto.FORA_DO_TEXTO_PADRAO, misto.PAPEL_DA_GRAVURA_PADRAO,
                     misto.LETRAS_NA_MOLDURA_PADRAO)

    # --- montagem -------------------------------------------------------------

    @staticmethod
    def _frase(texto: str) -> QLabel:
        rotulo = QLabel(texto)
        rotulo.setWordWrap(True)
        rotulo.setContentsMargins(28, 0, 0, 2)
        estilo.estilizar(rotulo, lambda: f"color: {estilo.TEXTO_FRACO}; font-size: 12px;")
        return rotulo

    @staticmethod
    def _combo(escolhas, ao_mudar) -> QComboBox:
        combo = QComboBox()
        for valor, texto in escolhas:
            combo.addItem(texto, valor)
        combo.currentIndexChanged.connect(lambda _i, c=combo: ao_mudar(c.currentData()))
        return combo

    # --- uso --------------------------------------------------------------------

    def mostrar(self, so_as_letras: bool, fora_do_texto: str, papel: str, letras: str) -> None:
        """Acerta os controles com os valores dados, sem emitir sinal."""
        self._acertando = True
        try:
            self.caixa.setChecked(bool(so_as_letras))
            botao = self.botoes.get(fora_do_texto) or self.botoes[misto.FORA_DO_TEXTO_PADRAO]
            botao.setChecked(True)
            self.frase_do_escolhido.setText(self._frases[botao.property("valor")])
            for combo, valor in ((self.combo_papel, papel), (self.combo_letras, letras)):
                indice = combo.findData(valor)
                combo.setCurrentIndex(max(0, indice))
            # "Mais opcoes" abre sozinho quando alguma nao esta no padrao, para
            # a pessoa ver o que foi mudado (como no grupo "Gravuras e fotos")
            fora_do_padrao = (papel != misto.PAPEL_DA_GRAVURA_PADRAO
                              or letras != misto.LETRAS_NA_MOLDURA_PADRAO)
            if fora_do_padrao and not self.botao_mais.isChecked():
                self.botao_mais.setChecked(True)
            self.painel.setVisible(bool(so_as_letras))
            self.painel_mais.setVisible(self.botao_mais.isChecked()
                                        and (not self._compacto or bool(so_as_letras)))
        finally:
            self._acertando = False

    def fora_do_texto(self) -> str:
        """O valor do botão escolhido."""
        botao = self.grupo.checkedButton()
        return str(botao.property("valor")) if botao is not None else misto.FORA_DO_TEXTO_PADRAO

    # --- sinais -----------------------------------------------------------------

    def _caixa_mudou(self, marcada: bool) -> None:
        self.painel.setVisible(marcada)
        if self._compacto:        # mora na linha da caixinha, fora do painel
            self.painel_mais.setVisible(marcada and self.botao_mais.isChecked())
        if not self._acertando:
            self.so_as_letras_mudou.emit(marcada)

    def _botao_clicado(self, valor: str) -> None:
        self.frase_do_escolhido.setText(self._frases[valor])
        if not self._acertando:
            self.fora_do_texto_escolhido.emit(valor)

    def _abrir_mais(self, aberto: bool) -> None:
        self.painel_mais.setVisible(aberto and (not self._compacto or self.caixa.isChecked()))
        self.botao_mais.setText("Menos opções" if aberto else "Mais opções")

    def _papel_mudou(self, valor) -> None:
        if not self._acertando and valor is not None:
            self.papel_escolhido.emit(str(valor))

    def _letras_mudou(self, valor) -> None:
        if not self._acertando and valor is not None:
            self.letras_escolhidas.emit(str(valor))
