"""A coluna de ícones da direita e os painéis que ela abre (layout, etapa 3).

Decisões do Samuel que este arquivo segue (página "Layout do Editor de
Impressão"; as palavras dele estão no "Plano de layout (rascunho).md"):

  - rodada 7, 203 D: "Ícones na borda, tudo fechado", com o comentário "eu
    ainda gostaria de ter a opção de ter fechado ou aberto os icones a
    direita. tipo uma seta de dropdown que eu abro ou fecho." -> a coluna de
    ícones (ColunaDeIcones) tem uma seta no alto que esconde e mostra os
    ícones; de fábrica os ícones ficam à vista e nenhum painel aberto;
  - rodada 9, 401 A: "Empurra a página" -> o painel aberto fica AO LADO da
    página (nunca por cima), com 300 px, um por vez;
  - rodada 9, 402 C: Propriedades "Muda conforme a ferramenta (como no
    Photoshop)" -> PainelPropriedades mostra o conteúdo da ferramenta da vez
    (quem monta o de Cortar, Endireitar e Dividir é a tela de conferir);
  - rodada 9, 405 C: Histórico "Os dois" -> desfazer e refazer sempre à mão
    na barra de baixo (ui/tela_conferir.py) e a lista no painel;
  - rodada 10, 504 A, e rodada 11, 602 A: "Para revisar" com as abas "Por
    página | Por motivo", abrindo "Sempre 'Por página'";
  - rodada 7, 203 D, o resto do comentário: "Mas eu também quero ter a opção
    da area de trabalho 1." + rodada 14, 902 C ("Nos dois lugares": menu Ver
    e Configurações) -> etapa 2 da obra (26/10/2026): o lado direito tem dois
    jeitos, ColunaDePaineis.definir_jeito: "icones" (de fábrica, o de
    sempre) e "sanfona", a área de trabalho 1 do desenho
    `1-area-de-trabalho-opcao-1.png` / `13-rodada7-padrao-a-area1-automatico-
    aberto.png`: os painéis empilhados numa coluna, cada um com a sua linha
    de título; clicar na linha abre o painel ali mesmo (um por vez) e os
    outros ficam fechados, só com a linha. A escolha fica guardada
    (configuracoes "lado_direito"; jeito_guardado / guardar_jeito).

Os cinco painéis, na ordem dos ícones (a do protótipo 21-rodada13-base):

  Para revisar        as páginas com dúvida; por página ou juntas pelo motivo
  Automático          o que o programa faz sozinho neste livro
  Propriedades        os botões da ferramenta da vez
  Filtro da página    qual filtro, o deslizante dele, e "só neste pedaço"
  Histórico           as ações da sessão; clicar volta o trabalho até ali

O que NÃO existe ainda no programa e por isso não aparece (não inventado
aqui): receitas e ordem das etapas no Automático; "ver as N em tela cheia" e
as miniaturas no Para revisar; o painel Filtro novo (fila de filtros e partes
que abrem e fecham), que é da etapa seguinte do layout.

Seguro mudar: textos, cores, tamanhos, os desenhos dos ícones. Arriscado:
tirar um painel ou um botão (tudo o que existia continua existindo, só mudou
de lugar) e os nomes `para_revisar`, `marcar_como`, `filtro_da_pagina` e
`historico` de ColunaDePaineis, que a tela de conferir e os testes usam.
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QPointF, QRect, QRectF, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QStyledItemDelegate,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from ui import estilo

LARGURA = 300              # o painel aberto (protótipo: .pd)
LARGURA_DOS_ICONES = 44    # a coluna de ícones (protótipo: .ib)
LARGURA_DA_SETA = 20       # a coluna com os ícones escondidos (protótipo: .ibf)
ALTURA_DO_CABECALHO = 40

PAINEL_REVISAR = "revisar"
PAINEL_AUTOMATICO = "automatico"
PAINEL_PROPRIEDADES = "props"
PAINEL_FILTRO = "filtro"
PAINEL_HISTORICO = "historico"
ORDEM_DOS_PAINEIS = (PAINEL_REVISAR, PAINEL_AUTOMATICO, PAINEL_PROPRIEDADES,
                     PAINEL_FILTRO, PAINEL_HISTORICO)
NOMES_DOS_PAINEIS = {
    PAINEL_REVISAR: "Para revisar",
    PAINEL_AUTOMATICO: "Automático",
    PAINEL_PROPRIEDADES: "Propriedades",
    PAINEL_FILTRO: "Filtro da página",
    PAINEL_HISTORICO: "Histórico",
}

# Os jeitos do lado direito (etapa 2 da obra; R7 203 D e R14 902 C). Os nomes
# são os que o agente de layout pôs na pergunta 902 da rodada 14 ("Ícones na
# borda", "Sanfona (a área de trabalho 1)"); "abas no alto" e "painel solto",
# que a pergunta também listava, não foram pedidos pelo Samuel e não existem.
LADO_ICONES = "icones"
LADO_SANFONA = "sanfona"
JEITOS_DO_LADO_DIREITO = (LADO_ICONES, LADO_SANFONA)
LADO_DE_FABRICA = LADO_ICONES
NOMES_DOS_JEITOS = {
    LADO_ICONES: "Ícones na borda (de fábrica)",
    LADO_SANFONA: "Sanfona (a área de trabalho 1)",
}
ALTURA_DA_LINHA_DA_SANFONA = 34


def jeito_guardado() -> str:
    """O jeito do lado direito que a pessoa escolheu da última vez
    (configuracoes.json, "lado_direito"); valor estranho ou sumido = o de
    fábrica. Nunca levanta exceção."""
    try:
        import configuracoes

        jeito = configuracoes.ler("lado_direito")
    except Exception:  # noqa: BLE001 - a preferência nunca impede a tela de abrir
        return LADO_DE_FABRICA
    return jeito if jeito in JEITOS_DO_LADO_DIREITO else LADO_DE_FABRICA


def guardar_jeito(jeito: str) -> None:
    """Guarda o jeito do lado direito para a próxima vez (falha em silêncio)."""
    try:
        import configuracoes

        configuracoes.escrever("lado_direito", jeito)
    except Exception:  # noqa: BLE001 - preferência não é essencial
        pass


# As duas abas do "Para revisar" (rodada 10, 504 A).
ABA_POR_PAGINA = "pagina"
ABA_POR_MOTIVO = "motivo"

# Quantas ações o painel Histórico mostra (as mais recentes). A lista é refeita
# a cada mudança; sem teto, uma sessão longa deixaria a troca de página lenta.
# Seguro mudar.
ACOES_NO_HISTORICO = 40

BOTAO_DO_PAINEL = """
QPushButton {{
    border: 1px solid {borda}; background: {fundo}; color: {cor};
    border-radius: 6px; padding: 5px 9px; font-size: 13px; text-align: left;
}}
QPushButton:hover {{ border-color: {azul}; }}
"""


# ---------------------------------------------------------------------------
# peças pequenas, usadas pelos painéis e pela tela de conferir
# ---------------------------------------------------------------------------

class Bloco(QWidget):
    """Uma caixa sem fundo próprio, para agrupar peças dentro de um painel.

    Por que existe: a folha de estilo do programa pinta TODO `QWidget` puro
    com o fundo da janela, que é mais escuro que o do painel; uma caixa comum
    dentro do painel aparecia como uma faixa escura. Uma classe filha de
    QWidget não pinta fundo nenhum (regra do Qt), e deixa ver o do painel.
    Arriscado: trocar por QWidget() puro.
    """


class NaoEspreme(Bloco):
    """Uma caixa que nunca deixa o Qt espremer as peças na altura (etapa 4 do
    layout, 20/10/2026): o mínimo dela é a altura que as peças pedem na
    largura de verdade, contando as frases que quebram de linha. Usada no
    corpo dos painéis e no que vai dentro da rolagem: um painel mais alto que
    a janela (o das ferramentas de marcar, com o "Pedaço" aberto) espremia os
    botões até a metade da altura, com o texto cortado, em vez de rolar."""

    def _altura_de_verdade(self, altura: int) -> int:
        """A altura pedida, ou mais, se as frases que quebram de linha pedem
        mais na largura que a caixa tem agora (o sizeHint do Qt conta as
        frases numa largura folgada, com menos linhas)."""
        caixa = self.layout()
        if caixa is not None and caixa.hasHeightForWidth() and self.width() > 0:
            altura = max(altura, caixa.totalHeightForWidth(self.width()))
        return altura

    def sizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        pedido = super().sizeHint()
        return QSize(pedido.width(), self._altura_de_verdade(pedido.height()))

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(super().minimumSizeHint().width(), self.sizeHint().height())

    def event(self, evento) -> bool:  # noqa: D401 - nome do Qt
        """Quando as peças de dentro mudam (uma parte aparece ou some), a
        caixa de fora mede de novo. Sem isto ela continuava com a altura de
        antes, e as peças novas eram espremidas."""
        resposta = super().event(evento)
        if evento.type() in (QEvent.LayoutRequest, QEvent.Resize):
            self._acertar_o_minimo()
        return resposta

    def acertar_tudo(self) -> None:
        """Mede de novo esta caixa e todas as NaoEspreme de dentro, das mais
        fundas para fora. Usado quando o conteúdo trocou enquanto o painel
        estava fechado (escondido, o Qt não mede nada) ou trocou de
        ferramenta: sem isto, na janela de verdade, os botões do Propriedades
        de marcar saíam com 22 pontos de altura para 30 (texto cortado)."""
        caixas = [c for c in self.findChildren(NaoEspreme) if c.isVisibleTo(self)]
        caixas.sort(key=_profundidade, reverse=True)
        for caixa in caixas + [self]:
            if caixa.layout() is not None:
                caixa.layout().invalidate()
                caixa.layout().activate()
            caixa._acertar_o_minimo()

    def _acertar_o_minimo(self) -> None:
        """Põe como altura mínima explícita a que as peças pedem agora. É o
        único mínimo que o Qt respeita em todo caso (a caixa de fora guarda
        as medidas de antes e não as pede de novo)."""
        altura = self._altura_de_verdade(super().sizeHint().height())
        if self.minimumHeight() != altura:
            self.setMinimumHeight(altura)


def _profundidade(widget) -> int:
    """Quantos pais o widget tem (para medir das caixas mais fundas para fora)."""
    n = 0
    while widget is not None:
        widget = widget.parentWidget()
        n += 1
    return n


class _Envelope(NaoEspreme):
    """O que vai dentro da rolagem de um painel. Diz ao Qt que pode ser tão
    estreito quanto o painel: sem isto, uma peça um pouco mais larga (uma
    lista com uma palavra comprida, uma escala de tela maior) deixava o
    conteúdo todo mais largo que o painel, e a ponta direita de cada botão
    ficava escondida, sem barra para chegar até ela. Assim as peças se
    apertam dentro da largura do painel. Na altura, nunca espreme (ver
    NaoEspreme)."""

    def minimumSizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(0, super().minimumSizeHint().height())


def lista_estreita(lista) -> None:
    """Deixa uma lista (QComboBox) encolher até poucas letras dentro do
    painel, em vez de exigir a largura do item mais comprido; a lista aberta
    continua mostrando os itens inteiros."""
    from PySide6.QtWidgets import QComboBox

    lista.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
    lista.setMinimumContentsLength(8)
    lista.view().setMinimumWidth(lista.view().sizeHintForColumn(0) + 28)
    lista.view().setTextElideMode(Qt.ElideNone)


def _nome_da_borda(projeto) -> str:
    """Item 2.13: o nome de ate onde vai o corte da borda preta do livro."""
    from core import borda_preta

    return (borda_preta.NOMES[borda_preta.jeito_valido(getattr(projeto, "borda_preta_ate", None))]
            + ", " + borda_preta.NOMES_DO_FAZER[                      # item 2.14
                borda_preta.fazer_valido(getattr(projeto, "borda_preta_fazer", None))])


def nome_da_conta(jeito: str) -> str:
    """O nome de uma conta do endireitar COMO APARECE NOS PAINEIS.

    A conta antiga do programa chama-se "Editor" na linha dos dois angulos
    (decisao do Samuel, rodada 13 do layout, 805 C: "A conta vira 'Editor'").
    Para a mesma conta nao ter duas palavras no mesmo painel, a lista "Conta",
    a parte "Para o livro todo", o painel Automatico e a frase do Historico
    dizem "a do Editor" tambem. ISTO E LEITURA DA GERENTE (13/10/2026), para o
    Samuel confirmar: a escolha dele foi sobre a linha dos angulos.

    So muda o texto na tela: o codigo gravado no projeto continua "programa"
    (core/endireitar_scantailor.JEITO_PROGRAMA), e o texto de la
    (NOMES_DOS_JEITOS, "a do programa") nao foi mexido; a tela "O que fazer"
    ainda o usa. Seguro mudar: a palavra."""
    from core import endireitar_scantailor as es

    if jeito == es.JEITO_PROGRAMA:
        return "a do Editor"
    return es.NOMES_DOS_JEITOS.get(jeito, str(jeito))


def nome_do_jeito_de_dividir(jeito: str) -> str:
    """O nome de um jeito de dividir a folha COMO APARECE NA TELA.

    Rodada 14 do layout, 907 (Samuel, 20/10/2026: "B — “o do Editor”"): o
    jeito antigo chama-se "o do Editor", como a conta do Endireitar ("a do
    Editor", 805 C). Vale na lista "jeito:" do Dividir, na parte "Para o
    livro todo", no painel Automático, no Histórico e na tela "O que fazer".
    Só muda o texto na tela: o código gravado no projeto continua "programa"
    (core/dividir_scantailor.JEITO_PROGRAMA). Seguro mudar: a palavra."""
    from core import dividir_scantailor as ds

    if jeito == ds.JEITO_PROGRAMA:
        return "o do Editor"
    return ds.NOMES_DOS_JEITOS.get(jeito, str(jeito))


def titulo_de_parte(texto: str) -> QLabel:
    """O título de uma PARTE do Propriedades, em maiúsculas ("SÓ NESTA
    PÁGINA", "PARA O LIVRO TODO": rodada 12, 706 B)."""
    rotulo = QLabel(texto.upper())
    rotulo.setObjectName("parteDoPainel")
    return rotulo


def titulo_de_secao(texto: str) -> QLabel:
    """O título de um grupo de botões dentro do painel ("Corte desta página")."""
    rotulo = QLabel(texto)
    rotulo.setObjectName("secaoDoPainel")
    return rotulo


def frase_do_painel(texto: str) -> QLabel:
    """Uma frase pequena de explicação, que quebra de linha na largura do painel."""
    rotulo = QLabel(texto)
    rotulo.setObjectName("fraseDoPainel")
    rotulo.setWordWrap(True)
    return rotulo


def risco_do_painel() -> QFrame:
    """O risco fino que separa dois grupos dentro do painel."""
    risco = QFrame()
    risco.setObjectName("riscoDoPainel")
    risco.setFixedHeight(1)
    return risco


def _caneta(cor: str, grossura: float = 1.5) -> QPen:
    """Caneta de ponta redonda, para os ícones desenhados à mão."""
    return QPen(QColor(cor), grossura, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)


def _icone_de_fechar() -> QIcon:
    """O "x" do cabeçalho do painel, desenhado à mão na cor do tema."""
    escala, lado = 3, 14
    imagem = QPixmap(lado * escala, lado * escala)
    imagem.fill(Qt.transparent)
    p = QPainter(imagem)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(escala, escala)
    p.setPen(_caneta(estilo.cor("fraco"), 1.6))
    p.drawLine(QPointF(3.5, 3.5), QPointF(10.5, 10.5))
    p.drawLine(QPointF(10.5, 3.5), QPointF(3.5, 10.5))
    p.end()
    imagem.setDevicePixelRatio(escala)
    return QIcon(imagem)


def icone_de_tela_cheia() -> QIcon:
    """Quatro cantinhos para fora (abrir em tela cheia), na cor do tema."""
    pix = QPixmap(32, 32)
    pix.fill(Qt.transparent)
    pintor = QPainter(pix)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.setPen(_caneta(estilo.cor("icone"), 3))
    for (x, y), (dx, dy) in (((5, 5), (1, 1)), ((27, 5), (-1, 1)), ((5, 27), (1, -1)), ((27, 27), (-1, -1))):
        pintor.drawLine(QPointF(x, y), QPointF(x + 8 * dx, y))
        pintor.drawLine(QPointF(x, y), QPointF(x, y + 8 * dy))
    pintor.end()
    return QIcon(pix)


def _quadradinho(cor: QColor) -> QIcon:
    """Um quadradinho colorido (a cor da marcação, no "Marcar como")."""
    escala, lado = 3, 12
    imagem = QPixmap(lado * escala, lado * escala)
    imagem.fill(Qt.transparent)
    p = QPainter(imagem)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(escala, escala)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(cor.red(), cor.green(), cor.blue()))
    p.drawRoundedRect(QRectF(0.5, 0.5, lado - 1, lado - 1), 3, 3)
    p.end()
    imagem.setDevicePixelRatio(escala)
    return QIcon(imagem)


class _BotaoDoPainel(QPushButton):
    """Um botão do painel que corta o próprio texto, em vez de empurrar o
    painel para mais largo que o desenho.

    Achado ao vivo (na coluna antiga, de 172 px): o `QPushButton` não encolhe
    abaixo do que precisa para mostrar o texto inteiro. Um item de histórico
    como "Filtro da página 12: Preto e branco para Melhorar" alargava a
    coluna toda. O texto inteiro fica na dica do mouse.
    """

    def __init__(self, texto: str, parent=None) -> None:
        super().__init__(texto, parent)
        self._texto_completo = ""
        self.setText(texto)

    def setText(self, texto: str) -> None:  # noqa: N802
        # Alguns paineis trocam o texto depois - guardar aqui de novo garante
        # que o elidir usa sempre o texto atual.
        self._texto_completo = texto
        self.setToolTip(texto)
        self._reelidir()

    def text(self) -> str:  # noqa: D401 - nome do Qt
        """O texto INTEIRO (o que aparece pode estar cortado com reticências)."""
        return self._texto_completo

    def minimumSizeHint(self) -> QSize:  # noqa: N802
        # Nao depender do tamanho do texto: e essa dependencia que forcava o
        # painel a crescer para caber o texto inteiro sem cortar.
        cheio = super().minimumSizeHint()
        return QSize(0, cheio.height())

    def sizeHint(self) -> QSize:  # noqa: N802
        """A largura pedida não depende do texto (o painel tem largura fixa)."""
        cheio = super().sizeHint()
        return QSize(min(cheio.width(), LARGURA - 40), cheio.height())

    def resizeEvent(self, evento) -> None:  # noqa: N802
        """Reelide o texto quando o botão muda de tamanho."""
        super().resizeEvent(evento)
        self._reelidir()

    def _reelidir(self) -> None:
        """Corta o texto completo com reticencias para caber na largura atual."""
        disponivel = self.width() - 22 - (18 if not self.icon().isNull() else 0)
        elidido = self.fontMetrics().elidedText(
            self._texto_completo, Qt.ElideRight, max(0, disponivel))
        QPushButton.setText(self, elidido)


# ---------------------------------------------------------------------------
# o painel aberto: cabeçalho com o nome e o "x", corpo com rolagem e pé
# ---------------------------------------------------------------------------

class CabecalhoDoPainel(QFrame):
    """A linha de cima do painel aberto: o nome, a contagem (só no "Para
    revisar"), um subtítulo fraco (a ferramenta ou a página) e o "x" que
    fecha. `text()` devolve o que se lia no cabeçalho antigo ("Para revisar"
    e, com páginas pendentes, o nome seguido do número)."""

    fechar = Signal()
    # a contagem ou o subtítulo mudaram (a linha da sanfona repete os dois)
    mudou = Signal()

    def __init__(self, titulo: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("cabecalhoDoPainel")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(ALTURA_DO_CABECALHO)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(14, 0, 8, 0)
        linha.setSpacing(8)

        self._titulo = titulo
        self._contagem = 0
        self.titulo = QLabel(titulo)
        self.titulo.setObjectName("tituloDoPainel")
        linha.addWidget(self.titulo)

        self.contagem = QLabel("")
        self.contagem.setObjectName("contagemDoPainel")
        self.contagem.setAlignment(Qt.AlignCenter)
        self.contagem.setFixedHeight(18)        # uma bolinha, e não a altura do cabeçalho
        self.contagem.setMinimumWidth(18)
        self.contagem.setVisible(False)
        linha.addWidget(self.contagem, 0, Qt.AlignVCenter)

        self.subtitulo = QLabel("")
        self.subtitulo.setObjectName("subtituloDoPainel")
        # cede lugar: um nome de ferramenta comprido é cortado, não empurra o "x"
        self.subtitulo.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        linha.addWidget(self.subtitulo, 1)

        self.botao_fechar = QPushButton()
        self.botao_fechar.setObjectName("fecharPainel")
        self.botao_fechar.setFixedSize(26, 26)
        self.botao_fechar.setIconSize(QSize(14, 14))
        self.botao_fechar.setCursor(Qt.PointingHandCursor)
        self.botao_fechar.setFocusPolicy(Qt.NoFocus)
        self.botao_fechar.setToolTip("fechar o painel")
        self.botao_fechar.clicked.connect(lambda *_: self.fechar.emit())
        linha.addWidget(self.botao_fechar)
        # o "x" desenhado à mão acompanha a troca de tema
        estilo.estilizar(self.botao_fechar, self._desenhar_o_fechar)

    def por_botao(self, icone, dica: str) -> QPushButton:
        """Um botão pequeno de ícone, antes do "x" (o da tela cheia dos filtros,
        rodada 10, 503: "ícone no título do painel")."""
        botao = QPushButton()
        botao.setObjectName("fecharPainel")          # o mesmo desenho do "x"
        botao.setFixedSize(26, 26)
        botao.setIconSize(QSize(15, 15))
        botao.setCursor(Qt.PointingHandCursor)
        botao.setFocusPolicy(Qt.NoFocus)
        botao.setToolTip(dica)
        self.layout().insertWidget(self.layout().indexOf(self.botao_fechar), botao)
        estilo.estilizar(botao, lambda: (botao.setIcon(icone()), "")[1])
        return botao

    def _desenhar_o_fechar(self) -> str:
        """(Re)desenha o "x" na cor do tema; devolve a folha (vazia) para
        estilo.estilizar, que chama isto de novo a cada troca de tema."""
        self.botao_fechar.setIcon(_icone_de_fechar())
        return ""

    def definir_contagem(self, quantas: int) -> None:
        """A bolinha laranja com o número (0 esconde)."""
        self._contagem = max(0, int(quantas))
        self.contagem.setText(str(self._contagem))
        self.contagem.setVisible(self._contagem > 0)
        self.mudou.emit()

    def definir_subtitulo(self, texto: str) -> None:
        """O texto fraco ao lado do nome ("Cortar as bordas", "página 5")."""
        self.subtitulo.setText(texto)
        self.subtitulo.setToolTip(texto)
        self.mudou.emit()

    def text(self) -> str:  # noqa: D401 - como o botão de título de antes
        """O nome do painel e, se houver, a contagem."""
        if self._contagem:
            return f"{self._titulo}          {self._contagem}"
        return self._titulo


class Painel(QFrame):
    """Um painel da direita, aberto: cabeçalho, corpo (com rolagem) e pé.

    Cada painel preenche o corpo (`self.dentro`) em `atualizar` ou `_montar`.
    `rolagem=False` é para o painel que cuida da própria rolagem (o "Para
    revisar", que tem uma lista).
    """

    fechar_pedido = Signal()

    def __init__(self, titulo: str, parent=None, rolagem: bool = True) -> None:
        super().__init__(parent)
        self.setObjectName("painelDaDireita")
        self.setAttribute(Qt.WA_StyledBackground, True)
        # A largura do desenho, sempre: sem isto, um rotulo comprido empurra o
        # painel para mais largo e ele toma o lugar da página.
        self.setFixedWidth(LARGURA)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(1, 0, 0, 0)      # 1 px: o risco da esquerda (paintEvent)
        camadas.setSpacing(0)
        self.camadas = camadas      # cabecalho, [topo fixo], corpo, pe

        self._titulo = titulo
        self.cabecalho = CabecalhoDoPainel(titulo)
        self.cabecalho.fechar.connect(self.fechar_pedido)
        camadas.addWidget(self.cabecalho)

        self.corpo = NaoEspreme() if rolagem else Bloco()
        self.corpo.setObjectName("corpoDoPainel")
        self.dentro = QVBoxLayout(self.corpo)
        self.dentro.setContentsMargins(12, 12, 10, 12)
        self.dentro.setSpacing(6)

        self.rolagem: QScrollArea | None = None
        if rolagem:
            self.rolagem = _rolagem_do_painel()
            envelope = _Envelope()
            caixa = QVBoxLayout(envelope)
            caixa.setContentsMargins(0, 0, 0, 0)
            caixa.setSpacing(0)
            caixa.addWidget(self.corpo)
            caixa.addStretch(1)
            _por_na_rolagem(self.rolagem, envelope)
            camadas.addWidget(self.rolagem, 1)
        else:
            camadas.addWidget(self.corpo, 1)

        # o pé: botões que ficam sempre à vista, embaixo (escondido se vazio)
        self.pe = QFrame()
        self.pe.setObjectName("peDoPainel")
        self.pe.setAttribute(Qt.WA_StyledBackground, True)
        self.no_pe = QVBoxLayout(self.pe)
        self.no_pe.setContentsMargins(12, 9, 12, 10)
        self.no_pe.setSpacing(6)
        self.pe.setVisible(False)
        camadas.addWidget(self.pe)

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Ao aparecer, mede de novo o corpo (ver NaoEspreme.acertar_tudo)."""
        super().showEvent(evento)
        self.medir_de_novo()

    def medir_de_novo(self) -> None:
        """Mede de novo o corpo logo depois que o Qt arrumar a tela (o
        conteúdo pode ter mudado com o painel escondido)."""
        if isinstance(self.corpo, NaoEspreme):
            QTimer.singleShot(0, self.corpo.acertar_tudo)

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """O risco fino da esquerda, que separa o painel da página."""
        super().paintEvent(evento)
        pintor = QPainter(self)
        pintor.setPen(QPen(QColor(estilo.cor("linha")), 1))
        pintor.drawLine(0, 0, 0, self.height())

    def limpar(self) -> None:
        """Remove todo o conteudo do corpo, antes de `atualizar`/`_montar` repovoar."""
        _esvaziar(self.dentro)

    def _texto(self, texto: str, cor: str = "", tamanho: int = 12) -> QLabel:
        """Rotulo simples de texto fraco, ja adicionado ao corpo do painel."""
        rotulo = QLabel(texto)
        rotulo.setWordWrap(True)
        estilo.estilizar(rotulo, lambda: (
            f"color: {cor or estilo.TEXTO_FRACO}; font-size: {tamanho}px; "
            "background: transparent; border: none;"))
        self.dentro.addWidget(rotulo)
        return rotulo

    def _botao(self, texto: str, acao, escolhido: bool = False) -> QPushButton:
        """Botão de acao do painel, ja adicionado ao corpo e ligado a `acao`.
        escolhido=True destaca em azul (usado para o item atualmente selecionado)."""
        botao = botao_de_lista(texto, escolhido)
        botao.clicked.connect(acao)
        self.dentro.addWidget(botao)
        return botao


def botao_de_lista(texto: str, escolhido: bool = False, apagado: bool = False) -> _BotaoDoPainel:
    """Um botão de lista do painel (um motivo, uma ação do histórico, um tipo
    de marcação): texto à esquerda, cortado com reticências se não couber.
    `escolhido` destaca em azul; `apagado` deixa cinza e em itálico (a ação
    desfeita do histórico)."""
    botao = _BotaoDoPainel(texto)
    botao.setCursor(Qt.PointingHandCursor)
    botao.setFocusPolicy(Qt.NoFocus)          # as setas do teclado trocam de página
    estilo.estilizar(botao, lambda: BOTAO_DO_PAINEL.format(
        borda=estilo.cor("azul") if escolhido else estilo.cor("sep"),
        fundo=estilo.cor("sel") if escolhido else (
            "transparent" if apagado else estilo.cor("botao")),
        cor=estilo.cor("forte") if escolhido else (
            estilo.cor("apagado") if apagado else estilo.cor("texto")),
        azul=estilo.cor("azul")) + ("QPushButton { font-style: italic; }" if apagado else ""))
    return botao


def _rolagem_do_painel() -> QScrollArea:
    """Uma área de rolagem só para cima e para baixo, sem moldura, com o
    fundo do painel (o nome "fundoDoPainel" tem regra em ui/estilo.py)."""
    rolagem = QScrollArea()
    rolagem.setWidgetResizable(True)
    rolagem.setFrameShape(QFrame.NoFrame)
    rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    rolagem.viewport().setObjectName("fundoDoPainel")
    return rolagem


def _por_na_rolagem(rolagem: QScrollArea, conteudo: QWidget) -> None:
    """Põe `conteudo` na rolagem sem deixar o Qt pintar o fundo dele: o
    setWidget liga o "preencher o fundo" sozinho, e o conteúdo apareceria com
    a cor da janela em vez da do painel. Arriscado: tirar a segunda linha."""
    rolagem.setWidget(conteudo)
    conteudo.setAutoFillBackground(False)


def _esvaziar(caixa) -> None:
    """Tira e destrói tudo o que há num layout (peças e layouts de dentro)."""
    while caixa.count():
        item = caixa.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            _esvaziar(item.layout())


# ---------------------------------------------------------------------------
# Para revisar
# ---------------------------------------------------------------------------

class _LinhaPorPagina(QStyledItemDelegate):
    """Desenha uma linha da lista "Por página": "Página N", o motivo em
    laranja e a frase do aviso em letra pequena. Pintada à mão (e não com um
    botão por página) porque um livro pode ter centenas de páginas com
    dúvida, e a lista é refeita quando os avisos mudam."""

    ALTURA = 78
    PAPEL_DO_MOTIVO = Qt.UserRole + 1
    PAPEL_DA_FRASE = Qt.UserRole + 2

    def sizeHint(self, opcao, indice) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(120, self.ALTURA)      # a largura quem dá é a lista

    def paint(self, pintor: QPainter, opcao, indice) -> None:
        """A caixinha da linha: laranja quando é a página da vez."""
        pintor.save()
        pintor.setRenderHint(QPainter.Antialiasing)
        caixa = QRectF(opcao.rect).adjusted(0.5, 3.5, -4.5, -3.5)
        da_vez = bool(opcao.state & QStyle.State_Selected)
        sob_o_mouse = bool(opcao.state & QStyle.State_MouseOver)
        fundo = estilo.cor("aviso_f") if da_vez else estilo.cor("linha_f")
        borda = (estilo.cor("aviso") if da_vez
                 else estilo.cor("fraco") if sob_o_mouse else estilo.cor("linha_b"))
        pintor.setPen(QPen(QColor(borda), 1))
        pintor.setBrush(QColor(fundo))
        pintor.drawRoundedRect(caixa, 7, 7)

        x = int(caixa.left()) + 10
        largura = int(caixa.width()) - 20
        y = int(caixa.top()) + 6
        fonte = QFont(opcao.font)
        fonte.setPixelSize(13)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.cor("forte")))
        pintor.drawText(QRect(x, y, largura, 17), Qt.AlignLeft | Qt.AlignVCenter,
                        str(indice.data(Qt.DisplayRole) or ""))
        y += 17
        fonte.setPixelSize(12)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.cor("aviso")))
        motivo = pintor.fontMetrics().elidedText(
            str(indice.data(self.PAPEL_DO_MOTIVO) or ""), Qt.ElideRight, largura)
        pintor.drawText(QRect(x, y, largura, 16), Qt.AlignLeft | Qt.AlignVCenter, motivo)
        y += 17
        fonte.setPixelSize(11)
        fonte.setBold(False)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.cor("fraco")))
        pintor.drawText(QRect(x, y, largura, int(caixa.bottom()) - y - 4),
                        Qt.AlignLeft | Qt.AlignTop | Qt.TextWordWrap,
                        str(indice.data(self.PAPEL_DA_FRASE) or ""))
        pintor.restore()


class PainelParaRevisar(Painel):
    """As páginas que pedem atenção, de dois jeitos (rodada 10, 504 A: abas
    "Por página | Por motivo"; rodada 11, 602 A: abre sempre em "Por página"):

      Por página    uma linha por página com dúvida, na ordem do livro, com o
                    motivo e a frase do aviso; clicar leva até ela;
      Por motivo    as páginas juntas pelo tipo de aviso (o que este painel
                    já fazia): "ângulo suspeito (2)"; clicar leva à primeira.

    O texto de cada aviso (título e frase) vem de core/analise.descrever: este
    painel só decide onde e como eles aparecem.

    "Está bom" de uma vez (12/10/2026; Samuel, rodada 4 do "Para revisar",
    `rv4-aviso-so-texto`: "com todas as paginas ou com todos os motivos de
    todas as paginas, e eu devo conseguir abrir um selecionador em aba grande"):
    na aba "Por motivo", embaixo de cada motivo, um botão "está bom: todas"
    (aceitar_motivo); no pé do painel, sempre à vista nas duas abas, "ver a
    lista…" (abrir_lista: o seletor grande, ui/janela_dos_avisos.py) e "está
    bom em tudo" (aceitar_tudo). O painel só AVISA quem escuta
    (ui/tela_conferir.py aplica, pelo histórico: o Ctrl+Z desfaz). Os botões
    só mudam quem está na lista, nunca a página. Só entram os avisos que ainda
    pedem um olhar (ConfigPagina.alertas_pendentes). A aparência é provisória
    (junção com o layout de 14/10, 20/10/2026: o pé foi o lugar escolhido pelo
    implementador; fica com o agente de layout). Seguro mudar: os textos.
    Arriscado: pôr o "está bom: todas" ANTES do botão do motivo em
    self.itens (self.itens são só os botões que levam à página).
    """

    ir_para = Signal(int)
    contagem_mudou = Signal(int)
    aceitar_motivo = Signal(str)     # o código do alerta
    aceitar_tudo = Signal()
    abrir_lista = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(NOMES_DOS_PAINEIS[PAINEL_REVISAR], parent, rolagem=False)
        self.dentro.setContentsMargins(12, 10, 8, 10)
        self.dentro.setSpacing(8)
        self.aba = ABA_POR_PAGINA
        self.itens: list[QPushButton] = []      # os botões da aba "Por motivo"
        self._assinatura: tuple | None = None
        self._paginas = 0

        # as duas abas, uma ao lado da outra (a escolhida fica azul)
        linha = QHBoxLayout()
        linha.setContentsMargins(0, 0, 4, 0)
        linha.setSpacing(0)
        self.botoes_de_aba: dict[str, QPushButton] = {}
        for chave, texto, dica in (
                (ABA_POR_PAGINA, "Por página",
                 "Uma linha por página com dúvida, na ordem do livro"),
                (ABA_POR_MOTIVO, "Por motivo",
                 "As páginas com dúvida juntas pelo motivo")):
            botao = QPushButton(texto)
            botao.setObjectName("abaDoPainel")
            botao.setCheckable(True)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            botao.setToolTip(dica)
            botao.clicked.connect(lambda _c=False, k=chave: self.mostrar_aba(k))
            linha.addWidget(botao, 1)
            self.botoes_de_aba[chave] = botao
        self.dentro.addLayout(linha)

        self.frase = frase_do_painel("")
        self.dentro.addWidget(self.frase)
        # O aviso do LIVRO da faixa escura na beirada (12/10/2026; Samuel,
        # rodada 4, Camões 66: "aviso no livro basta"): quando a faixa está em
        # quase todas as páginas, ela sai das páginas e é dita uma vez, aqui
        # (core.pipeline.acertar_faixa_do_livro). Escondida quando não vale.
        self.frase_do_livro = frase_do_painel("")
        self.frase_do_livro.setVisible(False)
        self.dentro.addWidget(self.frase_do_livro)

        self.pilha = QStackedWidget()
        self.pilha.setObjectName("pilhaDoPainel")

        # --- por página ---
        self.lista = QListWidget()
        self.lista.setObjectName("listaDoPainel")
        self.lista.setFrameShape(QFrame.NoFrame)
        self.lista.setItemDelegate(_LinhaPorPagina(self.lista))
        self.lista.setUniformItemSizes(True)
        self.lista.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.lista.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.lista.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lista.setFocusPolicy(Qt.NoFocus)   # as setas do teclado trocam de página
        self.lista.setMouseTracking(True)
        self.lista.viewport().setCursor(Qt.PointingHandCursor)   # pista: dá para clicar
        self.lista.itemClicked.connect(self._clicou_na_lista)
        self.pilha.addWidget(self.lista)

        # --- por motivo ---
        self.rolagem_dos_motivos = _rolagem_do_painel()
        caixa = Bloco()
        self.motivos = QVBoxLayout(caixa)
        self.motivos.setContentsMargins(0, 0, 4, 0)
        self.motivos.setSpacing(6)
        envelope = _Envelope()
        fora = QVBoxLayout(envelope)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.addWidget(caixa)
        fora.addStretch(1)
        _por_na_rolagem(self.rolagem_dos_motivos, envelope)
        self.pilha.addWidget(self.rolagem_dos_motivos)

        self.dentro.addWidget(self.pilha, 1)

        # o pé: "ver a lista…" e "está bom em tudo", sempre à vista (antes
        # ficavam no fim da lista e só apareciam rolando; verificador, 13/10)
        self.botao_ver_a_lista = botao_de_lista("ver a lista…")
        self.botao_ver_a_lista.setToolTip(
            "Abre a lista de todas as páginas com aviso e os motivos, "
            "para escolher em quais dar \"está bom\".")
        self.botao_ver_a_lista.clicked.connect(lambda _c=False: self.abrir_lista.emit())
        self.botao_esta_bom_em_tudo = botao_de_lista("está bom em tudo")
        self.botao_esta_bom_em_tudo.setToolTip(
            "Tira da lista todos os avisos de todas as páginas. "
            "Não muda nada nas páginas; o Desfazer traz de volta.")
        self.botao_esta_bom_em_tudo.clicked.connect(lambda _c=False: self.aceitar_tudo.emit())
        self.no_pe.addWidget(self.botao_ver_a_lista)
        self.no_pe.addWidget(self.botao_esta_bom_em_tudo)
        self.pe.setVisible(False)          # só com aviso pendente (atualizar)
        self.mostrar_aba(ABA_POR_PAGINA)

    # --- as abas ----------------------------------------------------------

    def mostrar_aba(self, aba: str) -> None:
        """Troca entre "Por página" e "Por motivo"."""
        self.aba = aba if aba in (ABA_POR_PAGINA, ABA_POR_MOTIVO) else ABA_POR_PAGINA
        for chave, botao in self.botoes_de_aba.items():
            botao.setChecked(chave == self.aba)
        self.pilha.setCurrentIndex(0 if self.aba == ABA_POR_PAGINA else 1)
        self._escrever_a_frase()

    def abrir_na_aba_de_fabrica(self) -> None:
        """Ao abrir o painel: sempre "Por página" (rodada 11, 602 A)."""
        self.mostrar_aba(ABA_POR_PAGINA)

    def _escrever_a_frase(self) -> None:
        """A frase em cima da lista: quantas páginas e como estão mostradas."""
        n = self._paginas
        if n == 0:
            self.frase.setText("nada pendente")
            return
        quantas = "1 página" if n == 1 else f"{n} páginas"
        if self.aba == ABA_POR_PAGINA:
            self.frase.setText(f"{quantas} para você olhar, na ordem do livro. "
                               "Clique numa para ir até ela.")
        else:
            self.frase.setText(f"{quantas} para você olhar, juntas pelo motivo. "
                               "Clique no motivo para ir à primeira.")

    # --- o conteúdo -------------------------------------------------------

    def atualizar(self, projeto) -> None:
        """Refaz as duas listas a partir do projeto. Só refaz de verdade
        quando os avisos mudaram (a tela chama isto a cada troca de página)."""
        from core import analise

        # Só os avisos que ainda pedem um olhar (ConfigPagina.alertas_pendentes:
        # nem a página inteira foi dada como boa, nem aquele motivo dela).
        pendentes: list[tuple[int, tuple]] = []
        if projeto is not None:
            for pagina in projeto.paginas:
                if pagina.apagada:
                    continue
                alertas = tuple(pagina.alertas_pendentes)
                if alertas:
                    pendentes.append((pagina.indice, alertas))
        frase_da_faixa = analise.OBSERVACOES[analise.FAIXA_NA_BEIRADA]
        faixa_no_livro = projeto is not None and frase_da_faixa in (
            getattr(projeto, "observacoes", None) or [])
        assinatura = (tuple(pendentes), faixa_no_livro)
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura
        self._paginas = len(pendentes)
        self.cabecalho.definir_contagem(self._paginas)
        self.frase_do_livro.setText("No livro inteiro: " + frase_da_faixa + "."
                                    if faixa_no_livro else "")
        self.frase_do_livro.setVisible(faixa_no_livro)
        self.pe.setVisible(bool(pendentes))
        self._montar_por_pagina(pendentes)
        self._montar_por_motivo(pendentes)
        self._escrever_a_frase()
        self.contagem_mudou.emit(self._paginas)

    def _montar_por_pagina(self, pendentes) -> None:
        """Uma linha por página com dúvida, na ordem do livro."""
        from core import analise

        self.lista.clear()
        for indice, alertas in pendentes:
            descricoes = [analise.descrever(a) for a in alertas]
            motivo = " · ".join(
                (getattr(d, "titulo", None) or str(a)) for d, a in zip(descricoes, alertas))
            frase = getattr(descricoes[0], "mensagem", "") or ""
            item = QListWidgetItem(f"Página {indice + 1}")
            item.setData(Qt.UserRole, indice)
            item.setData(_LinhaPorPagina.PAPEL_DO_MOTIVO, motivo)
            item.setData(_LinhaPorPagina.PAPEL_DA_FRASE, frase)
            item.setToolTip(f"Página {indice + 1}: {motivo}\n{frase}\nclicar leva até ela")
            self.lista.addItem(item)

    def _montar_por_motivo(self, pendentes) -> None:
        """As páginas juntas pelo tipo de aviso, dos maiores grupos para os
        menores (o que o painel "Para revisar" já fazia antes das abas)."""
        from core import analise

        _esvaziar(self.motivos)
        self.itens = []
        por_tipo: dict[str, list[int]] = {}
        for indice, alertas in pendentes:
            for alerta in alertas:
                por_tipo.setdefault(alerta, []).append(indice)
        if not por_tipo:
            return
        for alerta, indices in sorted(por_tipo.items(), key=lambda p: -len(p[1])):
            # descrever devolve um Alerta, e nao um texto: sem o .titulo o
            # painel mostrava "Alerta(codigo='cor', titulo=..." na cara do
            # usuario.
            nome = getattr(analise.descrever(alerta), "titulo", None) or alerta
            botao = botao_de_lista(f"{nome}   ({len(indices)})")
            botao.clicked.connect(lambda _c=False, i=indices[0]: self.ir_para.emit(i))
            botao.setToolTip(
                "páginas: " + ", ".join(str(i + 1) for i in indices[:20])
                + ("…" if len(indices) > 20 else ""))
            self.motivos.addWidget(botao)
            self.itens.append(botao)
            # "está bom" neste motivo em todas as páginas (12/10/2026)
            todas = botao_de_lista("está bom: todas" if len(indices) > 1 else "está bom")
            todas.clicked.connect(
                lambda _c=False, codigo=alerta: self.aceitar_motivo.emit(codigo))
            todas.setToolTip(
                f"Tira da lista {'as ' + str(len(indices)) + ' páginas' if len(indices) > 1 else 'a página'} "
                f"com o aviso \"{nome}\". Não muda nada nas páginas; o Desfazer traz de volta.")
            self.motivos.addWidget(todas)
        self.motivos.addWidget(frase_do_painel("clicar no motivo leva à primeira página"))

    def definir_pagina_atual(self, indice: int) -> None:
        """Destaca, na lista "Por página", a página que está na tela (se ela
        tem dúvida). Não avisa ninguém: só mostrar não é ir."""
        escolhida = None
        for linha in range(self.lista.count()):
            if self.lista.item(linha).data(Qt.UserRole) == indice:
                escolhida = self.lista.item(linha)
                break
        if escolhida is None:
            self.lista.clearSelection()
            self.lista.setCurrentRow(-1)
        elif self.lista.currentItem() is not escolhida:
            self.lista.setCurrentItem(escolhida)

    def _clicou_na_lista(self, item: QListWidgetItem) -> None:
        """Clique numa linha da lista "Por página": vai para a página."""
        indice = item.data(Qt.UserRole)
        if indice is not None:
            self.ir_para.emit(int(indice))


# ---------------------------------------------------------------------------
# Automático
# ---------------------------------------------------------------------------

# O painel Automatico mora em ui/automatico.py desde a obra de 26/10/2026,
# etapa 3 (D-002: receita, etapas que se marcam e se arrastam, "Rodar N
# etapas", janela grande, "escolher páginas..."). Antes aqui havia so uma
# lista de tiques "travados" (achado 1-12 da sessao 1 de testes guiados:
# "aqui as opções estão travadas , não consigo desmarcar ou mudar"). O nome
# continua importavel daqui (ver __getattr__ no fim do arquivo).


# ---------------------------------------------------------------------------
# Propriedades (muda conforme a ferramenta)
# ---------------------------------------------------------------------------

class PainelMarcarComo(Bloco):
    """Gravura · letra · papel, um embaixo do outro: o que a próxima marcação
    vai ser. Mora dentro do painel Propriedades, com as ferramentas de marcar.

    (Os dois jeitos novos, "iluminura ou pintura" e "moldura", decididos na
    rodada 12 (705 A), dependem do processamento e ainda não existem.)
    """

    escolheu = Signal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.tipo = ""
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(6)
        cabeca = QHBoxLayout()
        cabeca.setContentsMargins(0, 0, 0, 0)
        cabeca.addWidget(titulo_de_secao("Marcar como"))
        cabeca.addStretch()
        explica = frase_do_painel("o que você marcar agora")
        explica.setWordWrap(False)          # numa linha só, ao lado do título
        cabeca.addWidget(explica)
        fora.addLayout(cabeca)
        caixa = Bloco()
        self.dentro = QVBoxLayout(caixa)
        self.dentro.setContentsMargins(0, 0, 0, 0)
        self.dentro.setSpacing(5)
        fora.addWidget(caixa)
        self._montar()

    def limpar(self) -> None:
        """Tira os três botões, antes de `_montar` desenhá-los de novo."""
        _esvaziar(self.dentro)

    def _montar(self) -> None:
        """(Re)desenha os botões de tipo, destacando o escolhido.

        Item 2.18 (P11 (a) e TINTA3 do Samuel, 05/10/2026): mais três, que
        valem POR CIMA do filtro dentro da área - "pintar por cima" (com a cor
        do botão "cor de pintar..."), "manter a cor da tinta" e "tinta
        preta, fundo original". CONTROLE MÍNIMO, provisório até o layout.

        "manter a cor da tinta" (era "tinta com a cor, papel branco"): nome
        escolhido pelo Samuel na pergunta 11 (Central, 23/10/2026). Só o
        rótulo mudou; o código gravado no projeto.json continua TINTA_COR
        ("tinta_cor"), então projeto antigo abre igual. ARRISCADO trocar o
        código: projetos já gravados perderiam a área."""
        from core.selecao import GRAVURA, LETRA, PAPEL, PINTAR, TINTA_COR, TINTA_PRETA
        from ui.widgets.editor_selecao import CORES_BORDA

        self.limpar()
        self.botoes = {}
        self.botoes_do_papel = {}        # só existem com a "tinta com a cor"
        for tipo, texto in ((GRAVURA, "gravura ou foto"),
                            (LETRA, "letra e traço"),
                            (PAPEL, "papel"),
                            (PINTAR, "pintar por cima"),
                            (TINTA_COR, "manter a cor da tinta"),
                            (TINTA_PRETA, "tinta preta, fundo original")):
            botao = botao_de_lista(texto, escolhido=(tipo == (self.tipo or GRAVURA)))
            # a cor com que a marcação aparece na página (pista visual)
            botao.setIcon(_quadradinho(CORES_BORDA[tipo]))
            botao.setIconSize(QSize(12, 12))
            botao.clicked.connect(lambda _c=False, t=tipo: self.definir_tipo(t))
            self.dentro.addWidget(botao)
            self.botoes[tipo] = botao
            if tipo == TINTA_COR and self.tipo == TINTA_COR:
                self._montar_jeitos_da_cor()
        self.tipo = self.tipo or GRAVURA
        # item 2.18: a cor do "pintar por cima" (abre a caixa de cores do Qt)
        self.botao_cor = botao_de_lista(f"cor de pintar: {self.cor}", escolhido=False)
        self.botao_cor.setIcon(_quadradinho(QColor(self.cor)))
        self.botao_cor.setIconSize(QSize(12, 12))
        self.botao_cor.clicked.connect(self._escolher_cor)
        self.dentro.addWidget(self.botao_cor)

    cor_escolhida = Signal(str)
    cor = "#ffffff"

    # Item 2.18, resposta do Samuel de 22/10/2026 à pergunta b-8-tinta-com-cor:
    # "As duas: A e B como opções separadas". Os dois jeitos aparecem logo
    # abaixo de "manter a cor da tinta", só quando ela é a escolhida;
    # valem para a próxima área marcada (a já marcada guarda o dela).
    # De fábrica a A (False), igual ao de antes: ARRISCADO trocar.
    escurecer_escolhido = Signal(bool)
    escurecer = False
    JEITOS_DA_COR = ((False, "cor como no livro"), (True, "cor escurecida"))

    # Item 2.18, resposta do Samuel de 22/10/2026 à pergunta tc23-1 (o
    # retângulo branco no papel creme do Original): "As duas: escolher o papel
    # em cada área ('papel branco' ou 'papel como o resto da página')". Mesma
    # regra dos dois jeitos da cor: aparecem com o "manter a cor da tinta", em
    # qualquer filtro (b-9), e valem para a próxima área marcada.
    # De fábrica "papel branco" (False), igual ao de antes: ARRISCADO trocar.
    papel_escolhido = Signal(bool)
    papel_da_pagina = False
    JEITOS_DO_PAPEL = ((False, "papel branco"), (True, "papel como o resto da página"))

    def _montar_jeitos_da_cor(self) -> None:
        """Embaixo do botão "manter a cor da tinta", um pouco recuados: "cor como
        no livro" (A) e "cor escurecida" (B) lado a lado; embaixo, "papel
        branco" e "papel como o resto da página" um sob o outro (lado a lado o
        segundo não cabe nos 300 px do painel e sai cortado). Tudo num bloco
        só (um item a mais no `dentro`, como antes do papel).
        CONTROLE MÍNIMO, provisório até o layout (sem emoji, §3)."""
        bloco = Bloco()                  # sem fundo proprio (ver Bloco)
        coluna = QVBoxLayout(bloco)
        coluna.setContentsMargins(18, 0, 0, 0)
        coluna.setSpacing(5)
        self.botoes_da_cor = {}
        self.botoes_do_papel = {}
        for jeitos, escolhido, definir, botoes, Caixa in (
                (self.JEITOS_DA_COR, self.escurecer, self.definir_escurecer, self.botoes_da_cor,
                 QHBoxLayout),
                (self.JEITOS_DO_PAPEL, self.papel_da_pagina, self.definir_papel_da_pagina,
                 self.botoes_do_papel, QVBoxLayout)):
            caixa = Caixa()
            caixa.setContentsMargins(0, 0, 0, 0)
            caixa.setSpacing(5)
            for valor, texto in jeitos:
                botao = botao_de_lista(texto, escolhido=(valor == escolhido))
                botao.clicked.connect(lambda _c=False, v=valor, f=definir: f(v))
                caixa.addWidget(botao)
                botoes[valor] = botao
            coluna.addLayout(caixa)
        self.dentro.addWidget(bloco)

    def definir_papel_da_pagina(self, da_pagina: bool) -> None:
        """Troca entre "papel branco" (False) e "papel como o resto da
        página" (True)."""
        da_pagina = bool(da_pagina)
        if da_pagina == self.papel_da_pagina:
            return
        self.papel_da_pagina = da_pagina
        self._montar()
        self.papel_escolhido.emit(da_pagina)

    def definir_escurecer(self, escurecer: bool) -> None:
        """Troca entre A ("cor como no livro") e B ("cor escurecida")."""
        escurecer = bool(escurecer)
        if escurecer == self.escurecer:
            return
        self.escurecer = escurecer
        self._montar()
        self.escurecer_escolhido.emit(escurecer)

    def _escolher_cor(self) -> None:
        """Abre a caixa de cores; a cor vale para o próximo "pintar por cima"."""
        from PySide6.QtWidgets import QColorDialog

        # aberta sem travar o programa (open, nao exec): o teste_botoes.py
        # clica em todos os botoes e uma caixa que espera resposta o pararia
        self.caixa_de_cor = QColorDialog(QColor(self.cor), self)
        self.caixa_de_cor.setWindowTitle("Cor para pintar por cima")
        self.caixa_de_cor.colorSelected.connect(lambda cor: self.definir_cor(cor.name()))
        self.caixa_de_cor.open()

    def definir_cor(self, cor: str) -> None:
        self.cor = cor or "#ffffff"
        self._montar()
        self.cor_escolhida.emit(self.cor)

    def definir_tipo(self, tipo: str) -> None:
        """Troca o tipo escolhido (gravura/letra/papel) e emite `escolheu`."""
        if tipo == self.tipo:
            return
        self.tipo = tipo
        self._montar()
        self.escolheu.emit(tipo)


class PainelPropriedades(Painel):
    """Os botões da ferramenta da vez (rodada 9, 402 C: "Muda conforme a
    ferramenta (como no Photoshop)").

    O painel só GUARDA e MOSTRA: o conteúdo de Cortar, Endireitar e Dividir é
    montado pela tela de conferir (que tem as ações) e entregue em
    `definir_conteudo`. Os fixos são o das ferramentas de marcar e a frase
    de quem não tem propriedades (Zoom, Mão).

    O das ferramentas de marcar (etapa 4 do layout, 20/10/2026; protótipo da
    rodada 13, `propsMarcarA`) é o "Marcar como" e, embaixo dele, as partes
    que eram filas de botões embaixo da página ("Marcação desta página",
    "Foto", "Pedaço"), montadas pela tela de conferir e entregues em
    `definir_extra_de_marcar`. O "Na área marcada" do protótipo (pintar por
    cima, copiar, colar, mover) ainda não existe no programa e não entrou.
    """

    CONTEUDO_DE_MARCAR = "marcar"
    SEM_PROPRIEDADES = "nada"

    def __init__(self, parent=None) -> None:
        super().__init__(NOMES_DOS_PAINEIS[PAINEL_PROPRIEDADES], parent)
        self.marcar_como = PainelMarcarComo()
        # o conteúdo das ferramentas de marcar: o "Marcar como" e, embaixo,
        # o que a tela entrega em definir_extra_de_marcar
        self.conteudo_de_marcar = NaoEspreme()
        coluna = QVBoxLayout(self.conteudo_de_marcar)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(7)
        coluna.addWidget(self.marcar_como)
        self._coluna_de_marcar = coluna
        self.extra_de_marcar: QWidget | None = None
        self.sem_propriedades = frase_do_painel("")
        self._fixos: dict[str, QWidget] = {
            self.CONTEUDO_DE_MARCAR: self.conteudo_de_marcar,
            self.SEM_PROPRIEDADES: self.sem_propriedades,
        }
        self._da_tela: dict[str, QWidget] = {}
        self.conteudo = ""
        for widget in self._fixos.values():
            self.dentro.addWidget(widget)
            widget.setVisible(False)

    def por_no_alto(self, widget: QWidget) -> None:
        """Põe uma peça fixa no alto do painel, acima do conteúdo da
        ferramenta e separada dele por um risco: o bloco "Girar a folha"
        (rodada 12 do layout, 703 B), que vale em todas as ferramentas."""
        self.dentro.insertWidget(0, widget)
        self.dentro.insertWidget(1, risco_do_painel())

    def definir_conteudo(self, chave: str, widget: QWidget) -> None:
        """Guarda o conteúdo de uma ferramenta (montado pela tela de conferir)."""
        antigo = self._da_tela.pop(chave, None)
        if antigo is not None and antigo is not widget:
            antigo.setParent(None)
            antigo.deleteLater()
        self._da_tela[chave] = widget
        self.dentro.addWidget(widget)
        widget.setVisible(False)

    def definir_extra_de_marcar(self, widget: QWidget) -> None:
        """Põe, embaixo do "Marcar como", as partes das ferramentas de marcar
        que a tela montou ("Marcação desta página", "Foto", "Pedaço"). Troca
        a anterior (outro livro): a peça antiga é destruída."""
        self._tirar_o_extra_de_marcar()
        self.extra_de_marcar = widget
        self._coluna_de_marcar.addWidget(widget)

    def _tirar_o_extra_de_marcar(self) -> None:
        if self.extra_de_marcar is not None:
            self.extra_de_marcar.setParent(None)
            self.extra_de_marcar.deleteLater()
            self.extra_de_marcar = None

    def tirar_conteudos(self) -> None:
        """Joga fora os conteúdos da tela (ao abrir outro livro), inclusive as
        partes de marcar; os fixos ficam."""
        for widget in self._da_tela.values():
            widget.setParent(None)
            widget.deleteLater()
        self._da_tela.clear()
        self._tirar_o_extra_de_marcar()

    def tem_conteudo(self, chave: str) -> bool:
        """Há conteúdo (da tela ou fixo) guardado com esta chave?"""
        return chave in self._da_tela or chave in self._fixos

    def mostrar(self, chave: str, ferramenta: str = "", frase: str = "") -> None:
        """Põe à vista o conteúdo `chave` e escreve o nome da ferramenta ao
        lado do título. Chave desconhecida mostra a frase de "sem
        propriedades" (`frase`)."""
        if not self.tem_conteudo(chave):
            chave = self.SEM_PROPRIEDADES
        if chave == self.SEM_PROPRIEDADES:
            self.sem_propriedades.setText(
                frase or "Esta ferramenta só serve para olhar a página: não tem propriedades.")
        self.conteudo = chave
        for nome, widget in {**self._fixos, **self._da_tela}.items():
            widget.setVisible(nome == chave)
        self.cabecalho.definir_subtitulo(ferramenta)
        self.medir_de_novo()


# ---------------------------------------------------------------------------
# Filtro da página
# ---------------------------------------------------------------------------

class ParteQueAbre(QFrame):
    """Uma parte do painel que abre e fecha (rodada 9, 403 B: "Filtros numa
    fila + partes que abrem e fecham"; desenho das rodadas 10 e 11).

    Fechada, mostra só a seta, o título e, à direita, um resumo do que está
    escolhido ("Força do preto: 52", "Sem limpeza"). Aberta, mostra o corpo.
    A pista visual de que dá para clicar: a seta, a mãozinha do mouse e o
    fundo que acende com o mouse em cima. O que fica aberto é lembrado pelo
    nome da parte enquanto o programa está aberto (ABERTAS), para não fechar
    a cada troca de página. Seguro mudar: as margens."""

    ABERTAS: dict[str, bool] = {}

    def __init__(self, titulo: str, corpo: QWidget, aberta: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("parteQueAbre")
        self.setAttribute(Qt.WA_StyledBackground, True)
        estilo.estilizar(self, lambda: (
            f"QFrame#parteQueAbre {{ border: 1px solid {estilo.cor('sep')}; border-radius: 6px; "
            f"background: transparent; }}"))
        self.nome = titulo
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)
        self.cabeca = _CabecaDaParte(titulo)
        self.cabeca.clicada.connect(self.alternar)
        fora.addWidget(self.cabeca)
        self.caixa_do_corpo = NaoEspreme()
        dentro = QVBoxLayout(self.caixa_do_corpo)
        dentro.setContentsMargins(10, 2, 10, 10)
        dentro.setSpacing(6)
        dentro.addWidget(corpo)
        fora.addWidget(self.caixa_do_corpo)
        self.corpo = corpo
        self.aberta = self.ABERTAS.get(titulo, aberta)
        self._acertar()

    def alternar(self) -> None:
        """Clique no cabeçalho: abre ou fecha."""
        self.abrir(not self.aberta)

    def abrir(self, aberta: bool = True) -> None:
        """Abre (ou fecha, com False) e lembra para a próxima página."""
        self.aberta = bool(aberta)
        ParteQueAbre.ABERTAS[self.nome] = self.aberta
        self._acertar()

    def definir_resumo(self, texto: str) -> None:
        """O que está escolhido, à direita do título."""
        self.cabeca.resumo.setText(texto)
        self.cabeca.resumo.setToolTip(texto)

    def _acertar(self) -> None:
        self.caixa_do_corpo.setVisible(self.aberta)
        self.cabeca.aberta = self.aberta
        self.cabeca.update()


class _CabecaDaParte(QWidget):
    """O cabeçalho clicável de uma ParteQueAbre: seta desenhada, título, resumo."""

    clicada = Signal()

    def __init__(self, titulo: str, parent=None) -> None:
        super().__init__(parent)
        self.aberta = False
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(26, 7, 10, 7)
        linha.setSpacing(8)
        self.titulo = QLabel(titulo)
        self.titulo.setObjectName("secaoDoPainel")
        linha.addWidget(self.titulo)
        self.resumo = QLabel("")
        self.resumo.setObjectName("fraseDoPainel")
        self.resumo.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        self.resumo.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        linha.addWidget(self.resumo, 1)

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.button() == Qt.LeftButton:
            self.clicada.emit()

    def event(self, evento) -> bool:  # noqa: D401 - nome do Qt
        """O mouse entrou ou saiu: redesenha (o fundo aceso)."""
        if evento.type() in (QEvent.HoverEnter, QEvent.HoverLeave):
            self.update()
        return super().event(evento)

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """A seta: para a direita fechada, para baixo aberta (traço, sem símbolo de texto)."""
        super().paintEvent(evento)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        if self.underMouse():
            pintor.setPen(Qt.NoPen)
            cor = QColor(estilo.cor("forte"))
            cor.setAlpha(16)
            pintor.setBrush(cor)
            pintor.drawRoundedRect(QRectF(self.rect()).adjusted(1, 1, -1, -1), 5, 5)
        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(_caneta(estilo.cor("texto"), 1.6))
        cx, cy = 13, self.height() / 2
        if self.aberta:
            pontos = [QPointF(cx - 4, cy - 2), QPointF(cx, cy + 2), QPointF(cx + 4, cy - 2)]
        else:
            pontos = [QPointF(cx - 2, cy - 4), QPointF(cx + 2, cy), QPointF(cx - 2, cy + 4)]
        pintor.drawPolyline(pontos)
        pintor.end()


class _PaginaPequena(QWidget):
    """A página pequena de um CartaozinhoDoFiltro (ou um quadro cinza sem ela)."""

    LADO = QSize(50, 66)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedSize(self.LADO)
        self.pixmap: QPixmap | None = None

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        pintor = QPainter(self)
        ret = QRectF(0.5, 0.5, self.LADO.width() - 1, self.LADO.height() - 1)
        if self.pixmap is not None and not self.pixmap.isNull():
            escala = min(self.LADO.width() / self.pixmap.width(),
                         self.LADO.height() / self.pixmap.height())
            w, h = self.pixmap.width() * escala, self.pixmap.height() * escala
            alvo = QRectF((self.LADO.width() - w) / 2, (self.LADO.height() - h) / 2, w, h)
            pintor.setRenderHint(QPainter.SmoothPixmapTransform)
            pintor.drawPixmap(alvo, self.pixmap, QRectF(self.pixmap.rect()))
            ret = alvo.adjusted(0.5, 0.5, -0.5, -0.5)
        else:
            pintor.fillRect(ret, QColor(estilo.cor("botao")))
        pintor.setPen(_caneta(estilo.cor("sep"), 1))
        pintor.drawRect(ret)
        pintor.end()


class CartaozinhoDoFiltro(QFrame):
    """Um filtro na fila do painel Filtro: a página pequena naquele filtro, o
    nome e a tecla. Clicar escolhe o filtro para a página (rodada 9, 403 B).
    A página pequena é a mesma amostra dos cartões grandes (a tela a manda
    em `definir_amostra`); sem ela, um quadro cinza."""

    escolhido = Signal(str)

    def __init__(self, chave: str, nome: str, tecla: str, parent=None) -> None:
        super().__init__(parent)
        self.chave = chave
        self.selecionado = False
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("cartaozinhoDoFiltro")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setToolTip(nome + (f" (tecla {tecla})" if tecla else ""))
        fora = QVBoxLayout(self)
        # margens pequenas: em 300 pontos de painel, quatro filtros lado a
        # lado; com 3 de cada lado o "Melhorar" saía cortado (verificador, 21/10)
        fora.setContentsMargins(1, 5, 1, 4)
        fora.setSpacing(2)
        self.desenho = _PaginaPequena()
        fora.addWidget(self.desenho, 0, Qt.AlignHCenter)
        self.rotulo = QLabel(nome)
        self.rotulo.setAlignment(Qt.AlignHCenter)
        self.rotulo.setWordWrap(True)
        fora.addWidget(self.rotulo)
        self.rotulo_tecla = QLabel(f"tecla {tecla}" if tecla else "")
        self.rotulo_tecla.setAlignment(Qt.AlignHCenter)
        self.rotulo_tecla.setObjectName("teclaDoFiltro")
        fora.addWidget(self.rotulo_tecla)
        fora.addStretch()
        self._acertar_estilo()

    def definir_amostra(self, img) -> None:
        """A página pequena neste filtro (array do OpenCV), ou None."""
        if img is None:
            self.desenho.pixmap = None
        else:
            from ui.widgets.visualizador import numpy_para_qimage
            self.desenho.pixmap = QPixmap.fromImage(numpy_para_qimage(img))
        self.desenho.update()

    def definir_selecionado(self, selecionado: bool) -> None:
        """Acende (borda azul) o filtro da página."""
        if selecionado != self.selecionado:
            self.selecionado = selecionado
            self._acertar_estilo()

    def _acertar_estilo(self) -> None:
        sel = self.selecionado
        estilo.estilizar(self, lambda: (
            f"QFrame#cartaozinhoDoFiltro {{ border: 2px solid "
            f"{estilo.cor('azul') if sel else 'transparent'}; border-radius: 6px; "
            f"background: {estilo.cor('sel') if sel else 'transparent'}; }}"
            f"QFrame#cartaozinhoDoFiltro:hover {{ border-color: {estilo.cor('azul')}; }}"
            f"QLabel {{ color: {estilo.cor('forte') if sel else estilo.cor('texto')}; font-size: 11px;"
            f" font-weight: {600 if sel else 400}; background: transparent; border: none; }}"
            f"QLabel#teclaDoFiltro {{ color: {estilo.cor('fraco')}; font-size: 10px; font-weight: 400; }}"))

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.button() == Qt.LeftButton:
            self.escolhido.emit(self.chave)


class PainelFiltroDaPagina(Painel):
    """O painel "Filtro da página" decidido (etapa 4 do layout, 20/10/2026).

    Rodada 9, 403 B ("Filtros numa fila + partes que abrem e fecham"), com os
    nomes da rodada 10 (conjunto 2: "Limpar a sujeira", "Guardar a tinta
    forte"...) e as escolhas em "menu com amostra" (502 B), no desenho das
    rodadas 10 e 11:

        fila dos filtros (a página pequena em cada um, nome, tecla)
        Ajuste            o deslizante do filtro da vez
        Só as letras      só no Preto e branco
        Limpar a sujeira  só no Preto e branco
        Mais ajustes      só no Preto e branco: o jeito do preto e branco
        Só neste pedaço   o filtro do que for marcado daqui em diante
        ----
        Esta página   [deixar em branco] [tirar do livro]   (etapa 2 da obra)
        pé: Aplicar em: só nesta · todas · daqui em diante

    O painel só ARRUMA as peças: o deslizante, as listas, o "Só as letras",
    os botões do "Aplicar em" e o "apagar página" são criados pela tela de
    conferir (que tem as ações, o desfazer e os testes que os usam pelo
    nome: seletor_algoritmo_pb, seletor_pontinhos, escolhas_misto...) e
    entregues em `montar`. O que o painel faz sozinho: a fila (sinal
    `filtro_escolhido`) e o "só neste pedaço" (sinal `filtro_do_pedaco`).

    O ícone no título abre a tela cheia dos filtros (etapa 6,
    ui/widgets/filtros_tela_cheia.py). Ainda não estão aqui: em "Mais ajustes", "Letra clara em fundo escuro" e "Letras com a
    cor delas" (não existem no programa). No "Só neste pedaço" (rodada 14b,
    909: "B — Sem o botão de cima, nenhum aceso") não há mais o botão "o
    mesmo da página": nenhum filtro vem aceso, e o pedaço só ganha filtro
    próprio se a pessoa clicar num; clicar de novo no aceso volta a nenhum.
    Seguro mudar: a ordem e os títulos das partes. Arriscado: criar aqui as
    peças da tela (perdem a ligação com o desfazer).
    """

    filtro_escolhido = Signal(str)
    filtro_do_pedaco = Signal(str)
    tela_cheia_pedida = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(NOMES_DOS_PAINEIS[PAINEL_FILTRO], parent)
        # etapa 6 do layout (rodada 10, 503; rodada 11, 601 A): o ícone no
        # título abre a tela cheia dos filtros
        self.botao_tela_cheia = self.cabecalho.por_botao(
            icone_de_tela_cheia, "Ver os filtros em tela cheia (a página grande em cada filtro)")
        self.botao_tela_cheia.clicked.connect(lambda: self.tela_cheia_pedida.emit())
        self.filtro = ""
        self.filtro_pedaco = ""
        self.cartoes: dict[str, CartaozinhoDoFiltro] = {}
        self.partes: dict[str, ParteQueAbre] = {}
        self.botoes_do_pedaco: dict[str, QPushButton] = {}
        self.montado = False
        self._fila = self._apagar = self._aplicar = self._espaco = self._risco = None
        self.sem_filtro = frase_do_painel(
            "Este livro não passa pelos filtros: a etapa “Limpar a folha” está desligada.")
        self.dentro.addWidget(self.sem_filtro)

    def montar(self, filtros: list[tuple[str, str, str]], pecas: dict[str, QWidget]) -> None:
        """Arruma as peças da tela no painel (uma vez por livro).

        filtros: (chave, nome, tecla) de cada filtro do livro, na ordem da fila.
        pecas: "ajuste", "letras", "limpar", "mais" (os corpos das partes),
        "aplicar" (vai para o pé) e "apagar" (desde a etapa 2 da obra de
        26/10/2026, os dois botões "deixar em branco" e "tirar do livro"; era
        só o "apagar página")."""
        from core.filtros import NOMES_AMIGAVEIS

        self.desmontar()
        self.sem_filtro.setVisible(False)
        fila = Bloco()
        linha = QHBoxLayout(fila)
        linha.setContentsMargins(0, 0, 0, 2)
        linha.setSpacing(2)
        for chave, nome, tecla in filtros:
            cartao = CartaozinhoDoFiltro(chave, nome, tecla)
            cartao.escolhido.connect(self.filtro_escolhido)
            self.cartoes[chave] = cartao
            linha.addWidget(cartao, 1)
        self.dentro.addWidget(fila)
        self._fila = fila

        for chave, titulo, aberta in (("ajuste", "Ajuste", False), ("letras", "Só as letras", True),
                                      ("limpar", "Limpar a sujeira", False),
                                      ("mais", "Mais ajustes", False)):
            parte = ParteQueAbre(titulo, pecas[chave], aberta)
            self.partes[chave] = parte
            self.dentro.addWidget(parte)

        # "Só neste pedaço": o filtro do que for marcado daqui em diante
        pedaco = Bloco()
        coluna = QVBoxLayout(pedaco)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(5)
        for chave, texto in [(f, NOMES_AMIGAVEIS.get(f, n)) for f, n, _t in filtros]:
            botao = botao_de_lista(texto)
            botao.clicked.connect(lambda _c=False, k=chave: self._escolher_pedaco(k))
            coluna.addWidget(botao)
            self.botoes_do_pedaco[chave] = botao
        coluna.addWidget(frase_do_painel("vale para o que você marcar daqui em diante"))
        parte = ParteQueAbre("Só neste pedaço", pedaco, False)
        self.partes["pedaco"] = parte
        self.dentro.addWidget(parte)

        # apagar: destrutivo, longe dos outros, depois de um risco
        self._espaco = Bloco()          # Bloco: um QWidget puro pintaria uma faixa escura
        self._espaco.setFixedHeight(4)
        self.dentro.addWidget(self._espaco)
        self._risco = risco_do_painel()
        self.dentro.addWidget(self._risco)
        apagar = Bloco()
        linha = QHBoxLayout(apagar)
        linha.setContentsMargins(0, 2, 0, 0)
        linha.setSpacing(8)
        linha.addWidget(frase_do_painel("Esta página"))
        linha.addWidget(pecas["apagar"], 1)
        self.dentro.addWidget(apagar)
        self._apagar = apagar

        self.no_pe.addWidget(pecas["aplicar"])
        self._aplicar = pecas["aplicar"]
        self.pe.setVisible(True)
        self.montado = True
        self._acertar_pedaco()

    def desmontar(self) -> None:
        """Tira as peças do livro anterior (as da tela são destruídas com ele)."""
        for widget in (self._fila, self._espaco, self._risco, self._apagar, self._aplicar,
                       *self.partes.values()):
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()
        self._fila = self._apagar = self._aplicar = self._espaco = self._risco = None
        self.cartoes.clear()
        self.partes.clear()
        self.botoes_do_pedaco.clear()
        self.pe.setVisible(False)
        self.montado = False
        self.sem_filtro.setVisible(True)

    def atualizar(self, pagina) -> None:
        """A página da vez: o subtítulo, o filtro aceso na fila e o pedaço."""
        if pagina is None:
            self.cabecalho.definir_subtitulo("")
            return
        self.cabecalho.definir_subtitulo(f"página {pagina.indice + 1}")
        self.filtro = pagina.filtro
        for chave, cartao in self.cartoes.items():
            cartao.definir_selecionado(chave == pagina.filtro)
        self._acertar_pedaco()

    def definir_amostra(self, chave: str, img) -> None:
        """A página pequena do filtro `chave` (a mesma do cartão grande)."""
        cartao = self.cartoes.get(chave)
        if cartao is not None:
            cartao.definir_amostra(img)

    def definir_parte(self, chave: str, visivel: bool, resumo: str = "") -> None:
        """Mostra ou esconde uma parte e escreve o resumo dela."""
        parte = self.partes.get(chave)
        if parte is not None:
            parte.setVisible(visivel)
            parte.definir_resumo(resumo)

    def _acertar_pedaco(self) -> None:
        from core.filtros import NOMES_AMIGAVEIS

        for chave, botao in self.botoes_do_pedaco.items():
            escolhido = chave == self.filtro_pedaco
            estilo.estilizar(botao, lambda e=escolhido: BOTAO_DO_PAINEL.format(
                borda=estilo.cor("azul") if e else estilo.cor("sep"),
                fundo=estilo.cor("sel") if e else estilo.cor("botao"),
                cor=estilo.cor("forte") if e else estilo.cor("texto"),
                azul=estilo.cor("azul")))
        parte = self.partes.get("pedaco")
        if parte is not None:
            parte.definir_resumo("nenhum" if not self.filtro_pedaco
                                 else NOMES_AMIGAVEIS.get(self.filtro_pedaco, self.filtro_pedaco))

    def _escolher_pedaco(self, chave: str) -> None:
        """Marca qual filtro vale "só neste pedaço" (chave vazia = nenhum: o
        pedaço sai como o resto da página). Clicar no que já está aceso
        apaga (volta a nenhum)."""
        if chave == self.filtro_pedaco:
            chave = ""
        self.filtro_pedaco = chave
        self._acertar_pedaco()
        self.filtro_do_pedaco.emit(chave)


# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------

class PainelHistorico(Painel):
    """As ações da sessão, a mais recente embaixo. Clicar volta até ali.

    Rodada 9, 405 C ("Os dois"): desfazer e refazer ficam sempre à mão na
    barra de baixo da tela, e aqui há os mesmos dois botões e a lista. As
    ações desfeitas continuam na lista, apagadas, até a pessoa fazer outra
    coisa: clicar numa delas refaz até ali.

    Usa o arquivo de desfazer que já existe - o mesmo JSON Lines que sobrevive
    a fechar o programa. Um segundo mecanismo de histórico ao lado do que já
    funciona seria duas verdades sobre o mesmo trabalho.
    """

    voltar_para = Signal(int)
    desfazer_pedido = Signal()
    refazer_pedido = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(NOMES_DOS_PAINEIS[PAINEL_HISTORICO], parent)
        self.itens: list[QPushButton] = []          # as ações feitas, à vista
        self.itens_desfeitos: list[QPushButton] = []
        self._assinatura: tuple | None = None

        # desfazer e refazer, em cima da lista (fixos: não rolam com ela)
        topo = QFrame()
        topo.setObjectName("topoDoPainel")
        topo.setAttribute(Qt.WA_StyledBackground, True)
        caixa = QVBoxLayout(topo)
        caixa.setContentsMargins(12, 10, 12, 8)
        caixa.setSpacing(5)
        linha = QHBoxLayout()
        linha.setSpacing(6)
        self.botao_desfazer = QPushButton("Desfazer")
        self.botao_refazer = QPushButton("Refazer")
        for botao, sinal in ((self.botao_desfazer, self.desfazer_pedido),
                             (self.botao_refazer, self.refazer_pedido)):
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            botao.setIconSize(QSize(16, 16))
            botao.clicked.connect(lambda *_, s=sinal: s.emit())
            linha.addWidget(botao, 1)
        self.botao_refazer.setLayoutDirection(Qt.RightToLeft)     # a seta à direita do nome
        caixa.addLayout(linha)
        dica = frase_do_painel("Ctrl+Z desfaz · Ctrl+Shift+Z refaz")
        dica.setAlignment(Qt.AlignCenter)
        caixa.addWidget(dica)
        self.camadas.insertWidget(1, topo)      # logo abaixo do cabecalho
        self.botao_desfazer.setEnabled(False)
        self.botao_refazer.setEnabled(False)

        self.no_pe.addWidget(frase_do_painel(
            "Clique numa ação para voltar o trabalho até ali. As desfeitas ficam "
            "apagadas até você fazer outra coisa."))
        self.pe.setVisible(True)
        self._texto("nada ainda")

    def definir_icones(self, desfazer: QIcon, refazer: QIcon) -> None:
        """Os mesmos desenhos da barra de baixo (quem desenha é a tela)."""
        self.botao_desfazer.setIcon(desfazer)
        self.botao_refazer.setIcon(refazer)

    def atualizar(self, acoes) -> None:
        """Mostra as últimas ações feitas (de acoes.feitas) na ordem do tempo,
        a mais recente destacada, e depois dela as desfeitas, apagadas."""
        feitas = list(acoes.feitas) if acoes is not None else []
        desfeitas = list(reversed(acoes.desfeitas)) if acoes is not None else []
        self.botao_desfazer.setEnabled(bool(feitas))
        self.botao_refazer.setEnabled(bool(desfeitas))
        self.botao_desfazer.setToolTip(
            f"Desfazer: {feitas[-1].descricao} (Ctrl+Z)" if feitas else "Nada para desfazer")
        self.botao_refazer.setToolTip(
            f"Refazer: {desfeitas[0].descricao} (Ctrl+Shift+Z)" if desfeitas
            else "Nada para refazer")

        assinatura = (len(feitas), len(desfeitas),
                      feitas[-1].descricao if feitas else "",
                      desfeitas[0].descricao if desfeitas else "")
        if assinatura == self._assinatura:
            return
        self._assinatura = assinatura
        self.limpar()
        self.itens, self.itens_desfeitos = [], []
        if not feitas and not desfeitas:
            self._texto("nada ainda")
            return

        # As ultimas primeiro na leitura, mas na ordem do tempo: a mais recente
        # fica embaixo, como no desenho.
        inicio = max(0, len(feitas) - ACOES_NO_HISTORICO)
        if inicio:
            self._texto(f"(mais {inicio} antes destas)", tamanho=11)
        for posicao, acao in enumerate(feitas[inicio:], start=inicio):
            ultima = posicao == len(feitas) - 1
            botao = self._botao(
                acao.descricao,
                lambda _c=False, p=posicao: self.voltar_para.emit(p + 1),
                escolhido=ultima)
            botao.setToolTip(f"{acao.descricao}\nclicar volta o trabalho até aqui")
            self.itens.append(botao)
        for distancia, acao in enumerate(desfeitas[:ACOES_NO_HISTORICO], start=1):
            botao = botao_de_lista(f"{acao.descricao}  (desfeita)", apagado=True)
            botao.clicked.connect(
                lambda _c=False, p=len(feitas) + distancia: self.voltar_para.emit(p))
            botao.setToolTip(f"{acao.descricao}\ndesfeita: clicar refaz até aqui")
            self.dentro.addWidget(botao)
            self.itens_desfeitos.append(botao)
        # a mais recente à vista (a lista pode ser mais alta que o painel)
        if self.rolagem is not None and self.itens:
            ultimo = self.itens[-1]
            QTimer.singleShot(0, lambda: self._mostrar_o_ultimo(ultimo))

    def _mostrar_o_ultimo(self, botao: QPushButton) -> None:
        """Rola a lista até a ação mais recente (depois que o Qt arrumou as
        peças). O botão pode já ter sido trocado por outro: aí não faz nada."""
        try:
            if self.rolagem is not None and botao in self.itens:
                self.rolagem.ensureWidgetVisible(botao, 0, 30)
        except RuntimeError:        # a peça já foi destruída pelo Qt
            pass


# ---------------------------------------------------------------------------
# a coluna de ícones
# ---------------------------------------------------------------------------

def desenhar_icone_do_painel(pintor: QPainter, painel: str, x: float, y: float,
                             lado: float) -> None:
    """O ícone de um painel, desenhado à mão no quadrado (x, y, lado). A
    caneta já vem escolhida por quem chama (nada de emoji em rótulo)."""
    def pt(fx: float, fy: float) -> QPointF:
        return QPointF(x + lado * fx, y + lado * fy)

    if painel == PAINEL_REVISAR:                 # triângulo de aviso com o "!"
        caminho = QPainterPath()
        caminho.moveTo(pt(0.50, 0.10))
        caminho.lineTo(pt(0.95, 0.88))
        caminho.lineTo(pt(0.05, 0.88))
        caminho.closeSubpath()
        pintor.drawPath(caminho)
        pintor.drawLine(pt(0.50, 0.40), pt(0.50, 0.60))
        pintor.drawPoint(pt(0.50, 0.74))
    elif painel == PAINEL_AUTOMATICO:            # lista de etapas com a seta de "rodar"
        pintor.drawLine(pt(0.08, 0.25), pt(0.60, 0.25))
        pintor.drawLine(pt(0.08, 0.50), pt(0.48, 0.50))
        pintor.drawLine(pt(0.08, 0.75), pt(0.60, 0.75))
        seta = QPainterPath()
        seta.moveTo(pt(0.66, 0.34))
        seta.lineTo(pt(0.95, 0.50))
        seta.lineTo(pt(0.66, 0.66))
        seta.closeSubpath()
        pintor.fillPath(seta, pintor.pen().color())
    elif painel == PAINEL_PROPRIEDADES:          # dois deslizantes
        raio = lado * 0.11
        for fy, fx in ((0.30, 0.66), (0.70, 0.34)):
            centro = pt(fx, fy)
            pintor.drawLine(pt(0.06, fy), QPointF(centro.x() - raio, centro.y()))
            pintor.drawLine(QPointF(centro.x() + raio, centro.y()), pt(0.94, fy))
            pintor.drawEllipse(centro, raio, raio)
    elif painel == PAINEL_FILTRO:                # círculo meio cheio
        centro, raio = pt(0.5, 0.5), lado * 0.42
        pintor.drawEllipse(centro, raio, raio)
        metade = QPainterPath()
        metade.moveTo(centro.x(), centro.y() - raio)
        metade.arcTo(QRectF(centro.x() - raio, centro.y() - raio, 2 * raio, 2 * raio), 90, -180)
        metade.closeSubpath()
        pintor.fillPath(metade, pintor.pen().color())
    elif painel == PAINEL_HISTORICO:             # relógio
        centro, raio = pt(0.5, 0.5), lado * 0.42
        pintor.drawEllipse(centro, raio, raio)
        pintor.drawLine(pt(0.50, 0.26), pt(0.50, 0.50))
        pintor.drawLine(pt(0.50, 0.50), pt(0.68, 0.61))


class ColunaDeIcones(QWidget):
    """A coluna de ícones na borda direita (rodada 7, 203 D): a seta que
    esconde e mostra os ícones e um ícone por painel. Só avisa o que foi
    clicado (`escolhido`, `seta`); quem abre e fecha é a ColunaDePaineis.

    Pintada à mão, como a trilha de ferramentas da esquerda: o ícone do
    painel aberto fica azul; o "Para revisar" leva a bolinha laranja com
    quantas páginas têm dúvida. O mouse vira mãozinha em cima de cada ícone
    (pista visual de que dá para clicar), e o balão diz o nome do painel.
    """

    escolhido = Signal(str)
    seta = Signal()

    LADO_DO_BOTAO = (34, 30)
    ALTURA_DA_SETA = 22
    PASSO = 36                     # o botão e um respiro de 6 px

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        self.aberto: str | None = None
        self.contagem = 0
        self.recolhida = False
        self._sob_o_mouse: str | None = None
        self._apertado: str | None = None
        self.setFixedWidth(LARGURA_DOS_ICONES)

    # --- estado -----------------------------------------------------------

    def definir_aberto(self, painel: str | None) -> None:
        """Qual painel está aberto (o ícone dele fica azul); None = nenhum."""
        self.aberto = painel
        self.update()

    def definir_contagem(self, quantas: int) -> None:
        """Quantas páginas têm dúvida (a bolinha do "Para revisar")."""
        self.contagem = max(0, int(quantas))
        self.update()

    def definir_recolhida(self, recolhida: bool) -> None:
        """Ícones escondidos: sobra uma faixa fina só com a seta de mostrar."""
        self.recolhida = bool(recolhida)
        self.setFixedWidth(LARGURA_DA_SETA if self.recolhida else LARGURA_DOS_ICONES)
        self.update()

    # --- geometria --------------------------------------------------------

    def retangulos(self) -> dict[str, QRect]:
        """O retângulo de cada coisa clicável: "seta" e a chave de cada painel."""
        if self.recolhida:
            return {"seta": QRect(2, 8, LARGURA_DA_SETA - 4, 40)}
        largura, altura = self.LADO_DO_BOTAO
        x = (LARGURA_DOS_ICONES - largura) // 2
        saida = {"seta": QRect(x, 8, largura, self.ALTURA_DA_SETA)}
        y = 8 + self.ALTURA_DA_SETA + 13
        for painel in ORDEM_DOS_PAINEIS:
            saida[painel] = QRect(x, y, largura, altura)
            y += self.PASSO
        return saida

    def _item_em(self, ponto: QPoint) -> str | None:
        for chave, ret in self.retangulos().items():
            if ret.adjusted(-4, -2, 4, 2).contains(ponto):
                return chave
        return None

    def sizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(self.width(), 300)

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Fundo, risco da esquerda, a seta, o traço e cada ícone."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(estilo.cor("bar")))
        pintor.setPen(QPen(QColor(estilo.cor("linha")), 1))
        pintor.drawLine(0, 0, 0, self.height())
        retangulos = self.retangulos()
        seta = retangulos["seta"]

        if self.recolhida:
            pintor.setPen(QPen(QColor(estilo.cor("sep")), 1))
            pintor.setBrush(QColor(estilo.cor(
                "botao_h" if self._sob_o_mouse == "seta" else "botao")))
            pintor.drawRoundedRect(QRectF(seta).adjusted(0.5, 0.5, -0.5, -0.5), 4, 4)
            self._desenhar_setas(pintor, seta, para_a_esquerda=True)
            return

        if self._sob_o_mouse == "seta":
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(estilo.cor("botao_h")))
            pintor.drawRoundedRect(seta, 5, 5)
        self._desenhar_setas(pintor, seta, para_a_esquerda=False)
        pintor.setPen(QPen(QColor(estilo.cor("sep")), 1))
        y_do_traco = seta.bottom() + 7
        pintor.drawLine(10, y_do_traco, LARGURA_DOS_ICONES - 10, y_do_traco)

        for painel in ORDEM_DOS_PAINEIS:
            ret = retangulos[painel]
            aberto = painel == self.aberto
            if aberto or painel == self._sob_o_mouse:
                pintor.setPen(Qt.NoPen)
                pintor.setBrush(QColor(estilo.cor("azul" if aberto else "botao_h")))
                pintor.drawRoundedRect(ret, 6, 6)
            pintor.setBrush(Qt.NoBrush)
            pintor.setPen(_caneta("#FFFFFF" if aberto else estilo.cor("icone"), 1.6))
            lado = 18
            desenhar_icone_do_painel(pintor, painel, ret.center().x() - lado / 2 + 0.5,
                                     ret.center().y() - lado / 2 + 0.5, lado)
            if painel == PAINEL_REVISAR and self.contagem:
                self._desenhar_a_contagem(pintor, ret)

    def _desenhar_setas(self, pintor: QPainter, ret: QRect, para_a_esquerda: bool) -> None:
        """As duas setinhas (">>" esconde os ícones, "<<" mostra)."""
        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(_caneta(estilo.cor("forte" if self._sob_o_mouse == "seta" else "fraco"), 1.5))
        centro = QPointF(ret.center().x() + 0.5, ret.center().y() + 0.5)
        sentido = -1.0 if para_a_esquerda else 1.0
        for desloca in (-2.5, 2.5):
            ponta = QPointF(centro.x() + desloca + sentido * 1.8, centro.y())
            pintor.drawLine(QPointF(ponta.x() - sentido * 3.4, ponta.y() - 3.6), ponta)
            pintor.drawLine(QPointF(ponta.x() - sentido * 3.4, ponta.y() + 3.6), ponta)

    def _desenhar_a_contagem(self, pintor: QPainter, ret: QRect) -> None:
        """A bolinha laranja com o número, no canto do ícone "Para revisar"."""
        texto = str(self.contagem) if self.contagem < 1000 else "999+"
        fonte = QFont(self.font())
        fonte.setPixelSize(10)
        fonte.setBold(True)
        pintor.setFont(fonte)
        largura = max(16, pintor.fontMetrics().horizontalAdvance(texto) + 8)
        bolinha = QRectF(min(ret.right() - largura / 2 - 2, self.width() - largura - 1),
                         ret.top() - 5, largura, 15)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(estilo.cor("aviso")))
        pintor.drawRoundedRect(bolinha, 7.5, 7.5)
        pintor.setPen(QColor("#2A1808"))
        pintor.drawText(bolinha, Qt.AlignCenter, texto)

    # --- interação --------------------------------------------------------

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Guarda onde apertou; a ação é ao soltar em cima do mesmo ícone."""
        if evento.button() == Qt.LeftButton:
            self._apertado = self._item_em(evento.position().toPoint())

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Soltou em cima do que apertou: avisa (a seta ou o painel)."""
        apertado, self._apertado = self._apertado, None
        if evento.button() != Qt.LeftButton or apertado is None:
            return
        if self._item_em(evento.position().toPoint()) != apertado:
            return
        if apertado == "seta":
            self.seta.emit()
        else:
            self.escolhido.emit(apertado)

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """A mãozinha e o fundo mais claro em cima do que dá para clicar."""
        sob = self._item_em(evento.position().toPoint())
        if sob != self._sob_o_mouse:
            self._sob_o_mouse = sob
            self.setCursor(Qt.PointingHandCursor if sob else Qt.ArrowCursor)
            self.update()

    def leaveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        self._sob_o_mouse = None
        self.setCursor(Qt.ArrowCursor)
        self.update()

    def texto_da_dica(self, item: str) -> str:
        """O balão de cada ícone: o nome do painel e o que o clique faz."""
        if item == "seta":
            return "mostrar os ícones dos painéis" if self.recolhida else "esconder os ícones"
        nome = NOMES_DOS_PAINEIS.get(item, "")
        if item == PAINEL_REVISAR and self.contagem:
            nome += (" · 1 página com dúvida" if self.contagem == 1
                     else f" · {self.contagem} páginas com dúvida")
        return nome + ("  (clique para fechar)" if item == self.aberto else "")

    def event(self, evento) -> bool:  # noqa: D401 - nome do Qt
        """O balão do mouse com o nome do painel."""
        if evento.type() == QEvent.ToolTip:
            item = self._item_em(evento.pos())
            if item is None:
                QToolTip.hideText()
            else:
                QToolTip.showText(evento.globalPos(), self.texto_da_dica(item), self)
            return True
        return super().event(evento)


# ---------------------------------------------------------------------------
# a área de trabalho 1: os painéis em sanfona (etapa 2 da obra, 26/10/2026)
# ---------------------------------------------------------------------------

class LinhaDaSanfona(QWidget):
    """A linha de título de um painel FECHADO na sanfona (a área de trabalho
    1): a setinha ">", o ícone e o nome do painel e, à direita, o que o
    cabeçalho dele diria (a contagem do "Para revisar", o nome da ferramenta
    do Propriedades...). Clicar abre o painel ali. Pintada à mão, como a
    coluna de ícones; o mouse vira mãozinha (pista visual de que se clica).
    O painel ABERTO não usa esta linha: o cabeçalho dele (com o "x" que
    fecha) fica no lugar dela."""

    clicada = Signal(str)

    def __init__(self, painel: str, cabecalho: "CabecalhoDoPainel", parent=None) -> None:
        super().__init__(parent)
        self.painel = painel
        self.cabecalho = cabecalho
        self.setFixedHeight(ALTURA_DA_LINHA_DA_SANFONA)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)
        self._sob_o_mouse = False
        self.setToolTip(f"abrir o painel {NOMES_DOS_PAINEIS.get(painel, '')}")
        cabecalho.mudou.connect(self.update)

    def texto_da_direita(self) -> str:
        """A contagem (se houver) ou o subtítulo do cabeçalho do painel."""
        quantas = getattr(self.cabecalho, "_contagem", 0)
        if quantas:
            return str(quantas)
        return self.cabecalho.subtitulo.text()

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        """Fundo (mais claro com o mouse em cima), riscos, a setinha, o ícone,
        o nome e o texto da direita."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(estilo.cor("botao_h" if self._sob_o_mouse else "painel")))
        pintor.setPen(QPen(QColor(estilo.cor("linha")), 1))
        pintor.drawLine(0, self.height() - 1, self.width(), self.height() - 1)
        meio = self.height() / 2
        # a setinha ">" (fechado)
        pintor.setPen(_caneta(estilo.cor("fraco"), 1.5))
        pintor.drawLine(QPointF(13, meio - 4), QPointF(17, meio))
        pintor.drawLine(QPointF(17, meio), QPointF(13, meio + 4))
        # o ícone do painel, o mesmo da coluna de ícones
        pintor.setPen(_caneta(estilo.cor("icone"), 1.4))
        desenhar_icone_do_painel(pintor, self.painel, 26, meio - 8, 16)
        fonte = QFont(self.font())
        fonte.setPixelSize(13)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.cor("texto")))
        pintor.drawText(QRectF(50, 0, self.width() - 130, self.height()),
                        Qt.AlignVCenter | Qt.AlignLeft, NOMES_DOS_PAINEIS.get(self.painel, ""))
        direita = self.texto_da_direita()
        if direita:
            fonte.setBold(False)
            fonte.setPixelSize(12)
            pintor.setFont(fonte)
            com_contagem = bool(getattr(self.cabecalho, "_contagem", 0))
            pintor.setPen(QColor(estilo.cor("aviso" if com_contagem else "apagado")))
            caixa = QRectF(self.width() - 120, 0, 108, self.height())
            texto = pintor.fontMetrics().elidedText(direita, Qt.ElideRight, int(caixa.width()))
            pintor.drawText(caixa, Qt.AlignVCenter | Qt.AlignRight, texto)

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Soltou o botão esquerdo em cima: abre o painel."""
        if evento.button() == Qt.LeftButton and self.rect().contains(evento.position().toPoint()):
            self.clicada.emit(self.painel)

    def enterEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        self._sob_o_mouse = True
        self.update()

    def leaveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        self._sob_o_mouse = False
        self.update()


class _BotaoEsconderASanfona(QPushButton):
    """A seta ">>" no alto da sanfona: esconde os painéis (a página ganha o
    lugar; sobra a faixa fina com a seta de mostrar, como nos ícones)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("fecharPainel")          # o mesmo desenho do "x"
        self.setFixedSize(26, 22)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setToolTip("esconder os painéis")

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """O fundo do botão e as duas setinhas para a direita."""
        super().paintEvent(evento)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.setPen(_caneta(estilo.cor("fraco"), 1.5))
        centro = QPointF(self.width() / 2 + 0.5, self.height() / 2 + 0.5)
        for desloca in (-2.5, 2.5):
            ponta = QPointF(centro.x() + desloca + 1.8, centro.y())
            pintor.drawLine(QPointF(ponta.x() - 3.4, ponta.y() - 3.6), ponta)
            pintor.drawLine(QPointF(ponta.x() - 3.4, ponta.y() + 3.6), ponta)


# ---------------------------------------------------------------------------
# tudo junto: o painel aberto e, na borda, a coluna de ícones
# ---------------------------------------------------------------------------

class ColunaDePaineis(QWidget):
    """O lado direito da tela de trabalho, em um de dois jeitos (etapa 2 da
    obra; R7 203 D e R14 902 C):

    "icones" (de fábrica): o painel aberto (se houver) e a coluna de ícones
    na borda. De fábrica os ícones à vista e NENHUM painel aberto (rodada 7,
    203 D). Clicar num ícone abre o painel dele ao lado da página (ela
    encolhe: 401 A); clicar de novo, ou no "x" do painel, fecha. Um painel
    por vez. A seta no alto esconde os ícones (e o painel aberto junto) e
    mostra de novo.

    "sanfona" (a área de trabalho 1): uma coluna de 300 px com os cinco
    painéis empilhados; o aberto mostra o cabeçalho e o corpo, os outros só a
    linha de título (LinhaDaSanfona), que abre o painel ali mesmo. Um por vez,
    como nos ícones; ao entrar na sanfona sem painel aberto, abre o
    Automático (como no desenho da área de trabalho 1). A seta ">>" no alto
    esconde a coluna; sobra a faixa fina com a seta de mostrar.

    Os dois jeitos usam os MESMOS painéis (nada é montado duas vezes): trocar
    de jeito só muda onde a pilha dos painéis (`area`) fica. Arriscado: montar
    um segundo conjunto de painéis para a sanfona (a tela liga os sinais de um
    conjunto só).
    """

    abriu = Signal(str)        # a chave do painel aberto, ou "" quando fechou
    icones_mudaram = Signal(bool)   # a coluna de ícones apareceu (True) ou sumiu
    jeito_mudou = Signal(str)       # "icones" ou "sanfona"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        linha = QHBoxLayout(self)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(0)
        self._linha = linha

        self.area = QStackedWidget()
        self.area.setFixedWidth(LARGURA)

        self.para_revisar = PainelParaRevisar()
        # etapa 3 da obra: o painel Automatico de verdade (ui/automatico.py;
        # importado aqui dentro: ele importa este arquivo)
        from ui.automatico import PainelAutomatico

        self.automatico = PainelAutomatico(NOMES_DOS_PAINEIS[PAINEL_AUTOMATICO])
        self.propriedades = PainelPropriedades()
        self.marcar_como = self.propriedades.marcar_como
        self.filtro_da_pagina = PainelFiltroDaPagina()
        self.historico = PainelHistorico()

        self.paineis: dict[str, Painel] = {
            PAINEL_REVISAR: self.para_revisar,
            PAINEL_AUTOMATICO: self.automatico,
            PAINEL_PROPRIEDADES: self.propriedades,
            PAINEL_FILTRO: self.filtro_da_pagina,
            PAINEL_HISTORICO: self.historico,
        }
        for painel in self.paineis.values():
            self.area.addWidget(painel)
            painel.fechar_pedido.connect(self.fechar)
        linha.addWidget(self.area)

        # a sanfona (área de trabalho 1): a seta de esconder, uma linha por
        # painel e, no lugar da linha do aberto, a pilha dos painéis
        self.sanfona = QFrame()
        self.sanfona.setObjectName("sanfonaDosPaineis")
        self.sanfona.setAttribute(Qt.WA_StyledBackground, True)
        # a borda da esquerda (1 px) mais os 300 do painel
        self.sanfona.setFixedWidth(LARGURA + 1)
        estilo.estilizar(self.sanfona, lambda: (
            f"QFrame#sanfonaDosPaineis {{ background: {estilo.cor('painel')};"
            f" border: none; border-left: 1px solid {estilo.cor('linha')}; }}"))
        self._coluna_da_sanfona = QVBoxLayout(self.sanfona)
        self._coluna_da_sanfona.setContentsMargins(0, 0, 0, 0)
        self._coluna_da_sanfona.setSpacing(0)
        topo = Bloco()
        linha_do_topo = QHBoxLayout(topo)
        linha_do_topo.setContentsMargins(12, 3, 6, 3)
        rotulo = QLabel("PAINÉIS")
        rotulo.setObjectName("parteDoPainel")
        linha_do_topo.addWidget(rotulo)
        linha_do_topo.addStretch(1)
        self.botao_esconder_a_sanfona = _BotaoEsconderASanfona()
        self.botao_esconder_a_sanfona.clicked.connect(lambda *_: self.alternar_os_icones())
        linha_do_topo.addWidget(self.botao_esconder_a_sanfona)
        self._coluna_da_sanfona.addWidget(topo)
        self.linhas_da_sanfona: dict[str, LinhaDaSanfona] = {}
        for chave in ORDEM_DOS_PAINEIS:
            linha_da_sanfona = LinhaDaSanfona(chave, self.paineis[chave].cabecalho)
            linha_da_sanfona.clicada.connect(self.abrir)
            self.linhas_da_sanfona[chave] = linha_da_sanfona
            self._coluna_da_sanfona.addWidget(linha_da_sanfona)
        self._coluna_da_sanfona.addStretch(1)
        self.sanfona.setVisible(False)
        linha.addWidget(self.sanfona)

        self.icones = ColunaDeIcones()
        self.icones.escolhido.connect(self.alternar)
        self.icones.seta.connect(self.alternar_os_icones)
        self.para_revisar.contagem_mudou.connect(self.icones.definir_contagem)
        linha.addWidget(self.icones)

        self.aberto: str | None = None
        self.icones_a_vista = True
        self.jeito = LADO_DE_FABRICA
        self._acertar()

    # --- o jeito do lado direito (etapa 2 da obra) -------------------------

    def definir_jeito(self, jeito: str) -> None:
        """Troca o jeito do lado direito: "icones" ou "sanfona" (valor
        estranho vira o de fábrica). Na sanfona sem painel aberto, o
        Automático abre (desenho da área de trabalho 1). Avisa (jeito_mudou)
        só se mudou. Quem guarda a escolha é quem chama (guardar_jeito)."""
        jeito = jeito if jeito in JEITOS_DO_LADO_DIREITO else LADO_DE_FABRICA
        if jeito == self.jeito:
            return
        self.jeito = jeito
        if jeito == LADO_SANFONA and self.aberto is None:
            self.abrir(PAINEL_AUTOMATICO)
        self._acertar()
        self.jeito_mudou.emit(jeito)

    def em_sanfona(self) -> bool:
        """O lado direito está na área de trabalho 1 (sanfona)?"""
        return self.jeito == LADO_SANFONA

    # --- abrir e fechar ---------------------------------------------------

    def abrir(self, chave: str) -> None:
        """Abre o painel `chave` (fecha o que estava aberto: um por vez)."""
        if chave not in self.paineis:
            return
        if not self.icones_a_vista:          # painel aberto sem ícones não existe
            self.icones_a_vista = True
            self.icones_mudaram.emit(True)
        self.aberto = chave
        self.area.setCurrentWidget(self.paineis[chave])
        if chave == PAINEL_REVISAR:
            self.para_revisar.abrir_na_aba_de_fabrica()
        self._acertar()
        self.abriu.emit(chave)

    def fechar(self) -> None:
        """Fecha o painel aberto (a página volta a ocupar o lugar dele; na
        sanfona, ele volta a ser só a linha de título)."""
        if self.aberto is None:
            return
        self.aberto = None
        self._acertar()
        self.abriu.emit("")

    def alternar(self, chave: str) -> None:
        """Clique no ícone: abre o painel, ou fecha se já era ele o aberto."""
        if self.aberto == chave:
            self.fechar()
        else:
            self.abrir(chave)

    def alternar_os_icones(self) -> None:
        """A seta do alto: esconde os ícones (e o painel aberto com eles) ou
        mostra de novo (o painel que estava aberto volta). Na sanfona,
        esconde e mostra a coluna inteira."""
        self.mostrar_icones(not self.icones_a_vista)

    def mostrar_icones(self, a_vista: bool) -> None:
        """Mostra ou esconde a coluna de ícones (na sanfona, a coluna dos
        painéis)."""
        self.icones_a_vista = bool(a_vista)
        self._acertar()
        self.icones_mudaram.emit(self.icones_a_vista)

    def mostrar_painel(self, chave: str, visivel: bool) -> None:
        """Do menu Ver (nome de antes): abrir ou fechar um painel. A chave
        antiga "marcar" (o "Marcar como") leva ao Propriedades."""
        chave = PAINEL_PROPRIEDADES if chave == "marcar" else chave
        if visivel:
            self.abrir(chave)
        elif self.aberto == chave:
            self.fechar()

    def _acertar(self) -> None:
        """Põe à vista o que o estado manda (o jeito, o painel, os ícones, o
        ícone azul). Na sanfona a pilha dos painéis vai para o lugar da linha
        do painel aberto; nos ícones, volta para o lado da coluna de ícones."""
        sanfona = self.jeito == LADO_SANFONA and self.icones_a_vista
        coluna = self._coluna_da_sanfona
        if sanfona:
            if self._linha.indexOf(self.area) >= 0:
                self._linha.removeWidget(self.area)
            if coluna.indexOf(self.area) >= 0:
                coluna.removeWidget(self.area)
            if self.aberto is not None:
                lugar = coluna.indexOf(self.linhas_da_sanfona[self.aberto])
                coluna.insertWidget(lugar + 1, self.area, 1)
            # sem painel aberto, as linhas ficam no alto e a mola embaixo
            coluna.setStretch(coluna.count() - 1, 0 if self.aberto is not None else 1)
            for chave, linha in self.linhas_da_sanfona.items():
                linha.setVisible(chave != self.aberto)
        elif coluna.indexOf(self.area) >= 0:
            coluna.removeWidget(self.area)
            self._linha.insertWidget(0, self.area)
        self.sanfona.setVisible(sanfona)
        self.area.setVisible(self.aberto is not None and self.icones_a_vista)
        # na sanfona os ícones somem; com a coluna escondida, sobra a faixa
        # fina com a seta de mostrar (nos dois jeitos)
        self.icones.setVisible(not sanfona)
        self.icones.definir_recolhida(not self.icones_a_vista)
        self.icones.definir_aberto(self.aberto)
        self.updateGeometry()

    def largura_ocupada(self) -> int:
        """Quantos pontos de largura o lado direito toma agora (testes)."""
        if self.sanfona.isVisibleTo(self):
            return self.sanfona.width()
        return self.icones.width() + (LARGURA if self.area.isVisibleTo(self) else 0)


def __getattr__(nome: str):
    """`PainelAutomatico` continua importavel daqui (mora em ui/automatico.py
    desde a etapa 3 da obra; import tardio para nao ser circular)."""
    if nome == "PainelAutomatico":
        from ui.automatico import PainelAutomatico

        return PainelAutomatico
    raise AttributeError(nome)
