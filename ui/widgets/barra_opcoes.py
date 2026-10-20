"""A barra de opções: faixa fina que muda conforme a ferramenta na mão.

É a peça central do layout novo. Mostra só os controles da ferramenta ativa e
nada mais - é assim que um programa tem cinquenta ferramentas sem entulhar a
tela, e é o que resolve o aperto de hoje, em que tudo aparece ao mesmo tempo em
quatro linhas de botões.

**Somar e Tirar ficam sempre à direita**, em todas as ferramentas de seleção.
Eles saem da fila de ferramentas porque não são ferramentas: são modos que
modificam a ferramenta escolhida. Misturá-los com Retângulo e Laço fazia
parecer que se escolhe um OU outro.

**Só o nome e os ajustes** (decisão do Samuel, rodada 12 do layout, 702 C,
12/10/2026: "Mostrar só o nome da ferramenta"). A barra mora na linha dos
menus, onde a frase do que fazer era cortada quando faltava lugar. Agora ela
mostra o nome da ferramenta e os ajustes dela (o deslizante, o botão), e mais
nada: a frase do que fazer aparece no balão da ferramenta, na trilha
(ui/widgets/trilha_agrupada.py, USOS), e a dica de cada ajuste ("a roda do
mouse também muda...") no balão do próprio ajuste. O rótulo `dica` continua
existindo, vazio e fora da tela, só para quem ainda o consulta.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QWidget,
)

from core.selecao import SOMAR, SUBTRAIR
from ui import estilo
from ui.widgets.editor_selecao import (
    ESPESSURA_MAX,
    ESPESSURA_MIN,
    FERRAMENTA_COR,
    FERRAMENTA_MAO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_VARINHA,
    FERRAMENTA_ZOOM,
    FERRAMENTAS_DE_NAVEGACAO,
    NOMES_DAS_FERRAMENTAS,
    TOLERANCIA_MAX,
    TOLERANCIA_MIN,
    ZOOM_MAX,
    ZOOM_MIN,
)

ALTURA = 38          # do desenho aprovado

BOTAO_DE_MODO = """
QPushButton {{
    border: 1px solid {borda}; background: {fundo}; color: {cor};
    border-radius: 4px; padding: 2px 12px; font-size: 12px;
}}
"""


class BarraOpcoes(QFrame):
    """Uma faixa por ferramenta. Só a da ferramenta ativa fica visível."""

    tolerancia_mudou = Signal(int)
    espessura_mudou = Signal(float)
    zoom_mudou = Signal(float)
    ajustar_pedido = Signal()
    operacao_mudou = Signal(str)

    def __init__(self, parent=None) -> None:
        """Monta o esqueleto fixo (rotulo, area de controles, dica, botões
        somar/tirar) e comeca ja no estado da ferramenta "retangulo"."""
        super().__init__(parent)
        self.setFixedHeight(ALTURA)
        # Etapa 2 do layout: a barra mora na linha dos menus (R8 303 B), sem
        # fundo nem risco próprios - a linha dos menus já tem os dela.
        estilo.estilizar(self, lambda: (
            "QFrame { background: transparent; border: none; }"
            f" QLabel {{ color: {estilo.cor('forte')}; }}"))

        self.linha = QHBoxLayout(self)
        self.linha.setContentsMargins(12, 0, 12, 0)
        self.linha.setSpacing(10)

        self.rotulo = QLabel("")
        self.rotulo.setStyleSheet("border: none; font-weight: 600;")
        self.linha.addWidget(self.rotulo)

        self.controles = QWidget()
        self.controles.setStyleSheet("border: none;")
        self.dentro = QHBoxLayout(self.controles)
        self.dentro.setContentsMargins(0, 0, 0, 0)
        self.dentro.setSpacing(8)
        self.linha.addWidget(self.controles)

        # Rodada 12 do layout, 702 C: a frase do que fazer NÃO aparece mais
        # aqui (só o nome e os ajustes). O rótulo fica criado, vazio e fora da
        # linha, para quem ainda o consulta não quebrar.
        self.dica = QLabel("", self)
        self.dica.setVisible(False)
        self.linha.addStretch(1)

        self._montar_modos()
        self.definir_ferramenta(NOMES_DAS_FERRAMENTAS and "retangulo")

    # --- somar e tirar, sempre a direita ----------------------------------

    def _montar_modos(self) -> None:
        """Cria os botões somar/tirar (ver o comentário do modulo: nao sao
        ferramentas, sao modos que ficam sempre visiveis a direita)."""
        self.botoes_modo: dict[str, QPushButton] = {}
        for chave, texto in ((SOMAR, "somar"), (SUBTRAIR, "tirar")):
            botao = QPushButton(texto)
            botao.setCursor(Qt.PointingHandCursor)
            botao.clicked.connect(lambda _c=False, m=chave: self._escolher_modo(m))
            self.linha.addWidget(botao)
            self.botoes_modo[chave] = botao
        self._escolher_modo(SOMAR, avisar=False)

    def _escolher_modo(self, modo: str, avisar: bool = True) -> None:
        """Marca visualmente o botão escolhido. avisar=False so no estado
        inicial, para nao emitir um sinal antes de qualquer coisa estar ligada."""
        self.operacao = modo
        for chave, botao in self.botoes_modo.items():
            escolhido = chave == modo
            estilo.estilizar(botao, lambda escolhido=escolhido: BOTAO_DE_MODO.format(
                borda=estilo.cor("azul") if escolhido else estilo.cor("sep"),
                fundo=estilo.cor("azul") if escolhido else estilo.cor("botao"),
                cor="#ffffff" if escolhido else estilo.cor("texto")))
        if avisar:
            self.operacao_mudou.emit(modo)

    # --- troca de ferramenta ----------------------------------------------

    def definir_ferramenta(self, ferramenta: str) -> None:
        """Refaz a faixa para a ferramenta pedida."""
        self.ferramenta = ferramenta
        self._limpar()

        # só o nome (rodada 12, 702 C); a dica de cada ajuste vai no balão dele
        self.rotulo.setText(NOMES_DAS_FERRAMENTAS.get(ferramenta, ""))
        self.dica.setText("")

        if ferramenta == FERRAMENTA_COR:
            self._deslizante("variação", TOLERANCIA_MIN, TOLERANCIA_MAX, 30,
                             lambda v: self.tolerancia_mudou.emit(int(v)),
                             sufixo="média",
                             dica="a roda do mouse também muda a variação")

        elif ferramenta == FERRAMENTA_VARINHA:
            self._deslizante("tolerância", TOLERANCIA_MIN, TOLERANCIA_MAX, 30,
                             lambda v: self.tolerancia_mudou.emit(int(v)),
                             dica="a roda do mouse também muda a tolerância")

        elif ferramenta == FERRAMENTA_PINCEL:
            self._deslizante("tamanho", int(ESPESSURA_MIN * 1000),
                             int(ESPESSURA_MAX * 1000), 20,
                             lambda v: self.espessura_mudou.emit(v / 1000.0),
                             dica="a roda do mouse também muda o tamanho")

        elif ferramenta == FERRAMENTA_ZOOM:
            self._deslizante("aproximar", int(ZOOM_MIN * 100), int(ZOOM_MAX * 100),
                             100, lambda v: self.zoom_mudou.emit(v / 100.0),
                             sufixo="%",
                             dica="clique na página para aproximar; com Alt, afasta")
            self._botao("ajustar à tela", self.ajustar_pedido.emit)

        # Somar e tirar valem nas ferramentas de MARCAR, e em nenhuma das de
        # navegar: nao ha o que somar ao aproximar a pagina.
        de_marcar = ferramenta not in FERRAMENTAS_DE_NAVEGACAO
        for botao in self.botoes_modo.values():
            botao.setVisible(de_marcar)

    def largura_desejada(self) -> int:
        """A largura para mostrar tudo: o nome, os ajustes e somar/tirar (a
        barrinha de girar, na mesma linha, fica só com os ícones quando o
        que sobra não dá para ela com o nome escrito)."""
        return self.sizeHint().width() + 20

    def definir_ferramenta_da_pagina(self, nome: str, dica: str = "") -> None:
        """As ferramentas que eram abas (Dividir, Cortar, Endireitar e, até a
        etapa 4, Os quatro filtros) não têm controles aqui: a barra diz só o
        nome (rodada 12, 702 C; `dica` é aceita e ignorada, para quem ainda a
        passa). Os botões delas moram no painel Propriedades. Somar e tirar
        somem. A ferramenta de marcar guardada (self.ferramenta) não muda,
        para voltar a ela ao voltar a marcar."""
        self._limpar()
        self.rotulo.setText(nome)
        self.dica.setText("")
        for botao in self.botoes_modo.values():
            botao.setVisible(False)

    def _limpar(self) -> None:
        """Remove os controles da ferramenta anterior antes de montar a nova faixa."""
        while self.dentro.count():
            item = self.dentro.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

    def _deslizante(self, nome: str, minimo: int, maximo: int, valor: int,
                    aviso, sufixo: str = "", dica: str = "") -> QSlider:
        """Monta rotulo + slider (+ sufixo opcional), ligando o slider ao
        callback `aviso`. `dica` vai para o balão do rótulo e do deslizante
        (era a frase que ficava escrita na barra; rodada 12, 702 C)."""
        rotulo = QLabel(nome)
        estilo.estilizar(rotulo, lambda: f"color: {estilo.TEXTO_FRACO}; border: none;")
        rotulo.setToolTip(dica)
        self.dentro.addWidget(rotulo)

        deslizante = QSlider(Qt.Horizontal)
        deslizante.setFixedWidth(110)
        deslizante.setRange(minimo, maximo)
        deslizante.setValue(valor)
        deslizante.setToolTip(dica)
        deslizante.valueChanged.connect(aviso)
        self.dentro.addWidget(deslizante)

        if sufixo:
            fim = QLabel(sufixo)
            estilo.estilizar(fim, lambda: f"color: {estilo.TEXTO_FRACO}; border: none;")
            self.dentro.addWidget(fim)
        return deslizante

    def _botao(self, texto: str, acao) -> QPushButton:
        """Um botão simples na faixa de controles, com o estilo neutro de BOTAO_DE_MODO."""
        botao = QPushButton(texto)
        botao.setCursor(Qt.PointingHandCursor)
        estilo.estilizar(botao, lambda: BOTAO_DE_MODO.format(
            borda=estilo.cor("sep"), fundo=estilo.cor("botao"), cor=estilo.cor("texto")))
        botao.clicked.connect(acao)
        self.dentro.addWidget(botao)
        return botao
