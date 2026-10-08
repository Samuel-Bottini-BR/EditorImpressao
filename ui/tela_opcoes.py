"""TELA 2 - O que fazer: as caixinhas do que o programa deve fazer.

Cada caixinha (dividir, limpar, endireitar, cortar, montar cadernos) liga a um
campo de `Projeto` (modelos.py) em tempo real - _mudou() e chamado a cada
clique e escreve direto no projeto, sem botao "aplicar" separado. O resumo em
portugues embaixo (core.pipeline.resumo_em_portugues) e o que confirma para a
pessoa o que ela acabou de marcar, sem jargao.

Item 1.1 (29/09/2026, decisao do Samuel depois de ver a primeira ligacao):
"Tirar o fundo" e mais um filtro do livro, ao lado dos outros quatro, e so
aparece quando o PDF tem camadas (Projeto.tem_camadas, detectado ao abrir o
livro em ui/janela_principal.abrir_livro). A caixinha "Tirar o fundo
sozinho" da primeira ligacao saiu. escolher_filtro_do_livro e o que o aviso
"Este livro tem fundo separado. Quer tirar o fundo?" usa quando a pessoa
responde que sim.

Item 1.2 (30/09/2026, decisao do Samuel: "o programa tem que ter essas opcoes
para o usuario conseguir usar"): o grupo "Gravuras e fotos", logo abaixo dos
filtros, com as opcoes do detector de gravuras do ScanTailor Advanced, por
livro (Projeto.gravura_forma, gravura_sensibilidade, gravura_mais_sensivel,
gravura_normalizar): "Achar gravuras e fotos" (desmarcada = nao procurar: o
desligar da regra 8), "Este livro tem fotos" (desmarcada = contorno que segue
o desenho; marcada = em retangulo), "Sensibilidade" (so com fotos), "Procurar
tambem imagens claras" e "Igualar a luz da pagina antes". So aparece com
"Limpar a folha" marcada (sem filtro, a gravura nao muda nada). Mudar num
livro com trabalho so vale ao clicar "Conferir", como as outras opcoes; ai a
gravura achada sozinha e refeita e a marcacao a mao fica
(ui/janela_principal._analise_pronta, core.pipeline.trocar_opcoes_da_gravura).

Emenda do Samuel a regra do Preto e branco (conferencia 3, 30/09/2026): no
grupo dos filtros, a caixinha "No Preto e branco, molduras e iluminuras tambem
em preto e branco" (Projeto.pb_decoracao_em_preto_e_branco), desmarcada de
fabrica: a moldura dourada e a iluminura mantem a cor do original; "traco
preto so se eu escolher". Ver _montar_filtros.

Modo Misto (05/10/2026; provisorio ate o layout, excecao da gerente para o
implementador mexer aqui): no grupo dos filtros, a caixinha "So as letras" do
Preto e branco, com os tres botoes ("Guardar a tinta forte" / "Tudo em preto
e branco" / "So o texto achado") e o "Mais opcoes" (papel de dentro das
gravuras, letras dentro de molduras e iluminuras) - ui/widgets/
escolhas_do_misto.py, gravado no livro (Projeto.misto_*, conferencia 10,
P1 (a)). Com "So as letras" marcada, a caixinha das molduras fica apagada
(cinza) e volta como estava ao desmarcar (conferencia 11, P5 (a)). Como as
outras opcoes desta tela, vale ao clicar "Conferir" e nao entra no desfazer
(o desfazer e das acoes na conferencia). Consertos do parecer do verificador
(05/10): "So as letras" e os botoes so aparecem com o Preto e branco escolhido
(a escolha fica guardada quando some), e o resumo diz o que o "So as letras"
vai fazer (core.pipeline._frase_do_so_as_letras).

Limpar pontinhos (decisao do Samuel de 06/10/2026, P7; provisorio ate o
layout, excecao da gerente para o implementador mexer aqui): no grupo dos
filtros, embaixo da caixinha das molduras, a lista "Limpar pontinhos:"
(desligado · o nosso · pouco · normal · muito) do livro
(Projeto.limpar_pontinhos; de fabrica core/pontinhos_scantailor.PADRAO -
"o nosso" ou "desligado"; o do ScanTailor so quando escolhido, decisao
do Samuel de 07/10/2026). Como o "So
as letras", so aparece com o Preto e branco escolhido (a escolha fica
guardada quando some), vale ao clicar "Conferir" e nao entra no desfazer.
Cada pagina pode trocar so nela, na aba Filtro (ui/tela_conferir.py).

Dividir (item 2.1, decisoes do Samuel G2 (a) e G3 (b) de 05/10/2026;
provisorio ate o layout, pedido da gerente): "Dividir folhas ao meio" vem
DESMARCADA no livro novo ("So quando o Kaique pedir, livro a livro"). Marcada,
aparece embaixo dela a lista "Jeito de dividir:" (o do programa · o do
ScanTailor; Projeto.dividir_como). Logo depois, a caixinha "Cortar a beirada
da folha vizinha" (o corte da sobra do ScanTailor, Projeto.cortar_sobra),
desmarcada de fabrica, que vale nas folhas que nao forem divididas. Como as
outras opcoes, vale ao clicar "Conferir" e nao entra no desfazer. Cada folha
pode trocar o jeito so nela, na aba Onde cortar (ui/tela_conferir.py).

Endireitar (item 2.2, decisao G4 (b) do Samuel de 05/10/2026: "O do
ScanTailor de fabrica [...] mas eu vou ter a opcao de escolher"; provisorio
ate o layout): com "Endireitar folhas tortas" marcada, aparece embaixo dela a
lista "Conta do endireitar:" (a do ScanTailor · a do programa;
Projeto.endireitar_como). De fabrica, a do ScanTailor; o livro de antes do
2.2 volta com a do programa. Vale ao clicar "Conferir" e nao entra no
desfazer. Cada pagina pode trocar so nela, na aba Endireitar.
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
    QScrollArea,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from core import dividir_scantailor
from core import endireitar_scantailor
from core import misto
from core import pontinhos_scantailor as pontinhos
from core.cadernos import paginas_por_caderno_valido
from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    ORIGINAL,
    PRETO_E_BRANCO,
    TIRAR_FUNDO,
    filtros_do_livro,
)
from core.pipeline import resumo_em_portugues
from modelos import Projeto
from ui.estilo import TEXTO_FRACO, estilo_da_caixinha_com_quadrado
from ui.widgets.escolhas_do_misto import EscolhasDoMisto
from ui.widgets.folhear_pdf import FolhearPDF

FILTROS_NA_TELA = [
    (ORIGINAL, "Original", "não mexe na página"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado, arquivo pequeno"),
    (MELHORAR, "Melhorar", "limpa o fundo e mantém as cores"),
    (MAGICO_PRO, "Mágico pro", "cor viva e texto nítido"),
    # Item 1.1: so aparece em PDF com camadas (ver _mudou e
    # core.filtros.filtros_do_livro).
    (TIRAR_FUNDO, "Tirar o fundo", "tira o papel e deixa só o que está impresso"),
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
        # Item 2.1 (G2 (a)): o jeito de dividir do livro, so a vista com a
        # caixinha marcada (ver _mudou). Textos em core/dividir_scantailor.
        self.linha_jeito_dividir = QWidget()
        linha = QHBoxLayout(self.linha_jeito_dividir)
        linha.setContentsMargins(26, 2, 0, 0)
        linha.setSpacing(8)
        self.rotulo_jeito_dividir = QLabel("Jeito de dividir:")
        self.combo_jeito_dividir = QComboBox()
        for jeito in dividir_scantailor.JEITOS:
            self.combo_jeito_dividir.addItem(dividir_scantailor.NOMES_DOS_JEITOS[jeito], jeito)
        self.combo_jeito_dividir.setToolTip(
            "Onde a folha é dividida: o do programa procura a lombada no meio das "
            "folhas deitadas; o do ScanTailor divide toda folha mais larga que alta, "
            "na dobra que ele acha. Dá para trocar numa folha só, na aba Onde cortar.")
        self.combo_jeito_dividir.currentIndexChanged.connect(lambda _i: self._mudou())
        linha.addWidget(self.rotulo_jeito_dividir)
        linha.addWidget(self.combo_jeito_dividir)
        linha.addStretch()
        opcoes.addWidget(self.linha_jeito_dividir)
        # Item 2.1 (G3 (b)): o corte da sobra do ScanTailor, desligado de fabrica
        self.cx_cortar_sobra = self._caixa(
            "Cortar a beirada da folha vizinha",
            "o corte da sobra do ScanTailor, nas folhas que não forem divididas", opcoes
        )
        opcoes.addWidget(_separador())

        self.cx_limpar = self._caixa("Limpar a folha", "tira o amarelado", opcoes)
        self.painel_filtros = self._montar_filtros()
        opcoes.addWidget(self.painel_filtros)
        self.painel_gravuras = self._montar_gravuras()
        opcoes.addWidget(self.painel_gravuras)
        opcoes.addWidget(_separador())

        self.cx_endireitar = self._caixa(
            "Endireitar folhas tortas", "corrige páginas inclinadas", opcoes
        )
        # Item 2.2 (G4 (b)): a conta do endireitar do livro, so a vista com a
        # caixinha marcada (ver _mudou). Textos em core/endireitar_scantailor.
        self.linha_conta_endireitar = QWidget()
        linha = QHBoxLayout(self.linha_conta_endireitar)
        linha.setContentsMargins(26, 2, 0, 0)
        linha.setSpacing(8)
        self.rotulo_conta_endireitar = QLabel("Conta do endireitar:")
        self.combo_conta_endireitar = QComboBox()
        for jeito in endireitar_scantailor.JEITOS:
            self.combo_conta_endireitar.addItem(endireitar_scantailor.NOMES_DOS_JEITOS[jeito], jeito)
        self.combo_conta_endireitar.setToolTip(
            "Como a inclinação da página é medida: a conta do ScanTailor ou a do "
            "programa. Quando as duas discordam mais de 0,3 grau, a página vai para "
            "\"Para revisar\". Dá para trocar numa página só, na aba Endireitar.")
        self.combo_conta_endireitar.currentIndexChanged.connect(lambda _i: self._mudou())
        linha.addWidget(self.rotulo_conta_endireitar)
        linha.addWidget(self.combo_conta_endireitar)
        linha.addStretch()
        opcoes.addWidget(self.linha_conta_endireitar)
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

        # O cartao vai dentro de uma area com ROLAGEM (parecer do verificador,
        # 30/09/2026, prints r01-r04): sem ela, numa janela baixa (1440 x 880 com
        # a escala de 125% do Windows = uns 1150 x 680 pontos; o notebook do
        # Kaique, 1920 x 1080 a 125-150%) o Qt espremia as linhas do cartao ate
        # ficarem ilegiveis, umas por cima das outras. Com a rolagem, cada linha
        # fica na altura dela e aparece uma barra quando nao cabe. O resumo e os
        # botoes ficam sempre a vista, fora da rolagem. Arriscado: tirar a
        # rolagem, ou por o resumo dentro dela.
        dentro_da_rolagem = QWidget()
        dentro_da_rolagem.setObjectName("dentroDaRolagem")
        pilha = QVBoxLayout(dentro_da_rolagem)
        pilha.setContentsMargins(0, 0, 6, 0)      # espaco para a barra nao cobrir o cartao
        pilha.addWidget(cartao)
        pilha.addStretch()
        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        self.rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.rolagem.setStyleSheet(
            "QScrollArea { background: transparent; }"
            " QWidget#dentroDaRolagem { background: transparent; }")
        self.rolagem.viewport().setAutoFillBackground(False)
        self.rolagem.setWidget(dentro_da_rolagem)
        self._dentro_da_rolagem = dentro_da_rolagem
        esquerda.addWidget(self.rolagem, 1)

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

        for caixa in (self.cx_dividir, self.cx_cortar_sobra, self.cx_limpar,
                      self.cx_endireitar, self.cx_cortar, self.cx_cadernos):
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
        """Painel de radio-buttons com os filtros do livro (FILTROS_NA_TELA).
        So aparece quando "Limpar a folha" esta marcada - ver _mudou.

        Item 1.1: o "Tirar o fundo" (quinto da lista, na terceira linha da
        grade) nasce escondido e so aparece em PDF com camadas - ver _mudou.
        Os radios ficam guardados por filtro em self.radios_de_filtro (e o
        rotulo de explicacao de cada um em self._rotulos_de_filtro), para
        mostrar/esconder e para escolher_filtro_do_livro.
        """
        painel = QWidget()
        grade = QGridLayout(painel)
        grade.setContentsMargins(34, 6, 0, 6)
        grade.setSpacing(8)

        self.grupo_filtros = QButtonGroup(self)
        self.radios_de_filtro: dict[str, QRadioButton] = {}
        self._rotulos_de_filtro: dict[str, QLabel] = {}
        for i, (chave, nome, explicacao) in enumerate(FILTROS_NA_TELA):
            radio = QRadioButton(nome)
            radio.setProperty("filtro", chave)
            radio.setChecked(chave == ORIGINAL)
            radio.toggled.connect(self._mudou)
            self.grupo_filtros.addButton(radio)
            grade.addWidget(radio, i // 2, (i % 2) * 2)

            rotulo = QLabel(explicacao)
            rotulo.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
            # quebra a linha numa janela estreita (antes saia cortada: r02)
            rotulo.setWordWrap(True)
            grade.addWidget(rotulo, i // 2, (i % 2) * 2 + 1)
            self.radios_de_filtro[chave] = radio
            self._rotulos_de_filtro[chave] = rotulo
        self.radios_de_filtro[TIRAR_FUNDO].setVisible(False)
        self._rotulos_de_filtro[TIRAR_FUNDO].setVisible(False)

        # Emenda do Samuel a regra do Preto e branco (conferencia 3, 30/09/2026,
        # cartao N2): "Mantem a cor original (como o ANTES); traco preto so se
        # eu escolher". A caixinha e esse "se eu escolher", por livro
        # (Projeto.pb_decoracao_em_preto_e_branco): desmarcada de fabrica, a
        # moldura dourada e a iluminura ficam com a cor do original nas paginas
        # em Preto e branco; marcada, saem como desenho de traco preto. Fica
        # embaixo dos filtros, numa linha inteira da grade, com o quadrado a
        # vista (como as do grupo "Gravuras e fotos") e a frase embaixo,
        # quebrando a linha. Seguro mudar: os textos.
        self.cx_decoracao_pb = QCheckBox(
            "No Preto e branco, molduras e iluminuras também em preto e branco")
        # apagada (cinza) por inteiro quando "So as letras" esta marcada (P5):
        # a folha de estilo do programa pinta todo texto da mesma cor, entao o
        # cinza do texto desabilitado tem de ser dito aqui
        self.cx_decoracao_pb.setStyleSheet(estilo_da_caixinha_com_quadrado(14)
                                           + " QCheckBox:disabled { color: #9ca3af; }")
        self.cx_decoracao_pb.setChecked(False)
        self.cx_decoracao_pb.toggled.connect(self._mudou)
        frase = QLabel("desmarcada, a moldura dourada e a iluminura ficam com a cor do "
                       "original; marcada, saem só com o traço em preto")
        frase.setWordWrap(True)
        frase.setContentsMargins(28, 0, 0, 2)
        frase.setStyleSheet(f"QLabel {{ color: {TEXTO_FRACO}; font-size: 12px; }}"
                            " QLabel:disabled { color: #c4c8ce; }")
        self._frase_decoracao_pb = frase
        bloco = QVBoxLayout()
        bloco.setContentsMargins(0, 6, 0, 0)
        bloco.setSpacing(2)
        bloco.addWidget(self.cx_decoracao_pb)
        bloco.addWidget(frase)

        # Modo Misto (05/10/2026): "So as letras" e as escolhas dela, logo
        # abaixo dos filtros e acima da caixinha das molduras (que fica
        # apagada enquanto "So as letras" estiver marcada: ver _mudou)
        self.escolhas_misto = EscolhasDoMisto()
        self.escolhas_misto.setContentsMargins(0, 6, 0, 0)
        self.escolhas_misto.so_as_letras_mudou.connect(lambda _v: self._mudou())
        self.escolhas_misto.fora_do_texto_escolhido.connect(lambda _v: self._mudou())
        self.escolhas_misto.papel_escolhido.connect(lambda _v: self._mudou())
        self.escolhas_misto.letras_escolhidas.connect(lambda _v: self._mudou())
        self.escolhas_misto.botao_mais.toggled.connect(
            lambda _v: self._acertar_altura_da_rolagem())

        # "Limpar pontinhos" do livro (decisao do Samuel, 06/10/2026, P7):
        # de fabrica pontinhos.PADRAO (desde 07/10/2026 nunca o do
        # ScanTailor, que so vale quando escolhido; ver la); opcoes:
        # desligado, o nosso, pouco, normal, muito. Numa linha inteira da
        # grade, embaixo da caixinha das molduras, so com o Preto e branco escolhido (ver
        # _mudou). Seguro mudar: os textos (core/pontinhos_scantailor.py).
        self.linha_pontinhos = QWidget()
        linha = QHBoxLayout(self.linha_pontinhos)
        linha.setContentsMargins(0, 6, 0, 0)
        linha.setSpacing(8)
        self.rotulo_pontinhos = QLabel(pontinhos.ROTULO_NA_TELA)
        self.combo_pontinhos = QComboBox()
        for chave in pontinhos.ESCOLHAS:
            self.combo_pontinhos.addItem(pontinhos.NOMES_NA_TELA[chave], chave)
        self.combo_pontinhos.setCurrentIndex(self.combo_pontinhos.findData(pontinhos.PADRAO))
        self.combo_pontinhos.setToolTip(pontinhos.EXPLICACAO_NA_TELA)
        self.rotulo_pontinhos.setToolTip(pontinhos.EXPLICACAO_NA_TELA)
        self.combo_pontinhos.currentIndexChanged.connect(lambda _i: self._mudou())
        linha.addWidget(self.rotulo_pontinhos)
        linha.addWidget(self.combo_pontinhos)
        linha.addStretch()

        linhas = (len(FILTROS_NA_TELA) + 1) // 2
        grade.addWidget(self.escolhas_misto, linhas, 0, 1, 4)
        grade.addLayout(bloco, linhas + 1, 0, 1, 4)
        grade.addWidget(self.linha_pontinhos, linhas + 2, 0, 1, 4)
        return painel

    def _montar_gravuras(self) -> QWidget:
        """O grupo "Gravuras e fotos" (item 1.2): as opcoes do detector de
        gravuras do ScanTailor, cada uma com uma frase curta EMBAIXO.

        A vista: "Achar gravuras e fotos" (desmarcada = nao procurar: o
        desligar da regra 8) e "Este livro tem fotos". Atras do botao "Mais
        opcoes" (fechado ao abrir; aberto sozinho quando alguma delas nao esta
        no padrao, para a pessoa ver o que mudou): "Sensibilidade" (so vale
        com fotos: o ScanTailor so a usa no retangulo), "Procurar tambem
        imagens claras" e "Igualar a luz da pagina antes".

        Frase EMBAIXO (e nao ao lado, como na primeira versao): ao lado, numa
        grade, as frases cortavam e as linhas se espremiam (verificador,
        30/09, r01-r04); numa coluna so, o Qt da a cada frase a altura que ela
        precisa, e a rolagem do cartao (ver __init__) cuida do resto.
        So aparece com "Limpar a folha" (ver _mudou). Cada mudanca passa por
        _mudou, que grava no projeto. Seguro mudar: os textos.
        """
        painel = QWidget()
        fora = QVBoxLayout(painel)
        fora.setContentsMargins(34, 6, 0, 6)
        fora.setSpacing(2)

        titulo = QLabel("Gravuras e fotos")
        titulo.setStyleSheet("font-weight: bold;")
        fora.addWidget(titulo)

        self._frases_da_gravura: list[QLabel] = []

        def caixa(texto: str, explicacao: str, destino: QVBoxLayout, marcada: bool) -> QCheckBox:
            c = QCheckBox(texto)
            c.setStyleSheet(estilo_da_caixinha_com_quadrado(14))   # com quadrado (ui/estilo.py)
            c.setChecked(marcada)
            destino.addWidget(c)
            destino.addWidget(self._frase(explicacao))
            return c

        self.cx_achar_gravuras = caixa(
            "Achar gravuras e fotos",
            "separa desenho, foto e moldura do texto, para cada um ser tratado do seu jeito",
            fora, True)

        # o que so aparece com "Achar gravuras e fotos" marcada (ver _mudou)
        self.painel_opcoes_gravura = QWidget()
        dentro = QVBoxLayout(self.painel_opcoes_gravura)
        dentro.setContentsMargins(26, 4, 0, 0)
        dentro.setSpacing(2)
        self.cx_tem_fotos = caixa(
            "Este livro tem fotos",
            "procura em retângulo, que pega a foto inteira; desmarcada, segue o contorno do desenho",
            dentro, False)

        self.botao_mais_opcoes = QPushButton("Mais opções")
        self.botao_mais_opcoes.setObjectName("plano")
        self.botao_mais_opcoes.setCheckable(True)
        self.botao_mais_opcoes.setCursor(Qt.PointingHandCursor)
        self.botao_mais_opcoes.toggled.connect(self._abrir_mais_opcoes)
        linha_mais = QHBoxLayout()
        linha_mais.setContentsMargins(0, 4, 0, 0)
        linha_mais.addWidget(self.botao_mais_opcoes)
        linha_mais.addStretch()
        dentro.addLayout(linha_mais)

        self.painel_mais_opcoes = QWidget()
        mais = QVBoxLayout(self.painel_mais_opcoes)
        mais.setContentsMargins(0, 0, 0, 0)
        mais.setSpacing(2)
        linha = QHBoxLayout()
        linha.setContentsMargins(0, 0, 0, 0)
        self.rotulo_sensibilidade = QLabel("Sensibilidade")
        linha.addWidget(self.rotulo_sensibilidade)
        self.deslizante_sensibilidade = QSlider(Qt.Horizontal)
        self.deslizante_sensibilidade.setRange(0, 100)
        self.deslizante_sensibilidade.setSingleStep(10)
        self.deslizante_sensibilidade.setPageStep(10)
        self.deslizante_sensibilidade.setValue(100)
        self.deslizante_sensibilidade.setMinimumWidth(120)
        self.deslizante_sensibilidade.setMaximumWidth(260)
        # desabilitado (sem "Este livro tem fotos") fica cinza: a folha de
        # estilo do programa pinta o deslizante de azul sempre
        self.deslizante_sensibilidade.setStyleSheet(
            "QSlider::sub-page:horizontal:disabled { background: #d1d5db; }"
            "QSlider::handle:horizontal:disabled { border-color: #d1d5db; }")
        linha.addWidget(self.deslizante_sensibilidade, 1)
        self.valor_sensibilidade = QLabel("100")
        self.valor_sensibilidade.setMinimumWidth(32)
        linha.addWidget(self.valor_sensibilidade)
        linha.addStretch()
        mais.addLayout(linha)
        self.explicacao_sensibilidade = self._frase(
            "só com fotos: no máximo, o retângulo pega a foto inteira; menos, "
            "aperta o retângulo e deixa de fora a beirada mais rala")
        mais.addWidget(self.explicacao_sensibilidade)
        self.cx_imagens_claras = caixa(
            "Procurar também imagens claras",
            "acha desenho e foto bem apagados; pode pegar mancha junto", mais, False)
        self.cx_igualar_luz = caixa(
            "Igualar a luz da página antes",
            "acerta a página mais escura de um lado antes de procurar", mais, True)
        self.painel_mais_opcoes.setVisible(False)
        dentro.addWidget(self.painel_mais_opcoes)
        fora.addWidget(self.painel_opcoes_gravura)

        for c in (self.cx_achar_gravuras, self.cx_tem_fotos,
                  self.cx_imagens_claras, self.cx_igualar_luz):
            c.toggled.connect(self._mudou)
        self.deslizante_sensibilidade.valueChanged.connect(self._mudou)
        return painel

    def _frase(self, texto: str) -> QLabel:
        """A frase curta que explica uma opcao do grupo "Gravuras e fotos":
        miuda, cinza, recuada para ficar embaixo do texto da caixinha, e
        quebrando a linha (nunca cortada)."""
        rotulo = QLabel(texto)
        rotulo.setWordWrap(True)
        # o recuo pela margem do widget (e nao pela folha de estilo): assim o
        # Qt conta o recuo ao quebrar a linha, e a frase nunca sai cortada
        rotulo.setContentsMargins(28, 0, 0, 2)
        rotulo.setStyleSheet(f"color: {TEXTO_FRACO}; font-size: 12px;")
        self._frases_da_gravura.append(rotulo)
        return rotulo

    def _acertar_altura_da_rolagem(self) -> None:
        """A rolagem nunca fica mais alta que o cartao: com a janela grande, o
        resumo fica logo embaixo do cartao (e nao la no pe da tela, com um
        buraco no meio). Com a janela baixa, a rolagem encolhe e a barra
        aparece. Chamado ao redimensionar e quando algo aparece ou some."""
        largura = self.rolagem.viewport().width() or self.rolagem.width()
        dentro = self._dentro_da_rolagem
        altura = (dentro.heightForWidth(largura) if dentro.hasHeightForWidth()
                  else dentro.sizeHint().height())
        self.rolagem.setMaximumHeight(max(120, altura + 2))

    def showEvent(self, evento) -> None:  # noqa: N802
        """Toda vez que a tela aparece, as caixinhas voltam a mostrar o que o
        projeto tem AGORA (mostrar_opcoes).

        Parecer do verificador (30/09, r15): depois de desfazer o "Sim" da
        pergunta do fundo (o desfazer devolve o filtro do livro), a tela
        continuava marcando "Tirar o fundo", com o projeto em Original. O
        desfazer e o refazer mudam o projeto por baixo da tela; aqui ela se
        reacerta ao aparecer (e ui/tela_conferir.py a reacerta na hora, se ela
        ja estiver a vista). Seguro: so le o projeto e grava de volta os
        mesmos valores."""
        super().showEvent(evento)
        if self.projeto is not None:
            self.mostrar_opcoes()

    def resizeEvent(self, evento) -> None:  # noqa: N802
        """Ver _acertar_altura_da_rolagem."""
        super().resizeEvent(evento)
        self._acertar_altura_da_rolagem()

    def _abrir_mais_opcoes(self, aberto: bool) -> None:
        """O botao "Mais opcoes": mostra ou esconde as opcoes avancadas."""
        self.painel_mais_opcoes.setVisible(aberto)
        self.botao_mais_opcoes.setText("Menos opções" if aberto else "Mais opções")
        self._acertar_altura_da_rolagem()

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
        de marcar o que fazer.

        Enquanto as caixinhas sao acertadas, self.projeto fica None: cada
        setChecked que muda dispara _mudou, que gravava no projeto o estado de
        TODAS as caixinhas - as ainda nao acertadas com o valor do livro
        anterior (bug "as caixinhas...", Lista de bugs de 29/09: com o livro
        anterior sem "Limpar", o livro salvo com "Limpar" abria sem ele). Com
        None, _mudou nao faz nada, e roda uma vez so no fim, com tudo certo.
        Arriscado: ligar self.projeto antes dos setChecked.
        """
        self.total_folhas = total_folhas

        from pathlib import Path

        nome = Path(projeto.caminho_entrada).name
        self.arquivo.setText(f"{nome}  -  {total_folhas} folhas")

        self.projeto = projeto
        self.mostrar_opcoes()

        self.folhear.abrir(projeto.caminho_entrada)

    def mostrar_opcoes(self) -> None:
        """Acerta as caixinhas, o filtro do livro e o combo pelo projeto da
        tela (self.projeto), sem abrir o folhear. Usado por carregar e pela
        janela quando as opcoes do projeto mudam por fora (o "cancelar" da
        analise devolve as opcoes de antes: ui/janela_principal.py,
        _parar_a_analise).

        Enquanto as caixinhas sao acertadas, self.projeto fica None (ver
        carregar): senao cada setChecked gravaria no projeto as outras
        caixinhas ainda com o valor antigo. Arriscado: tirar isso.
        """
        projeto = self.projeto
        if projeto is None:
            return
        self.projeto = None
        filtro_do_livro = projeto.filtro_padrao

        self.cx_dividir.setChecked(projeto.dividir_folhas)
        # item 2.1: o jeito de dividir e o corte da sobra (projeto em memoria
        # sem os campos: os de fabrica)
        self.combo_jeito_dividir.setCurrentIndex(self.combo_jeito_dividir.findData(
            dividir_scantailor.jeito_valido(getattr(projeto, "dividir_como", None))))
        self.cx_cortar_sobra.setChecked(bool(getattr(projeto, "cortar_sobra", False)))
        self.cx_limpar.setChecked(projeto.limpar)
        self.cx_endireitar.setChecked(projeto.endireitar)
        # item 2.2: a conta do endireitar (projeto em memoria sem o campo: a
        # de fabrica)
        self.combo_conta_endireitar.setCurrentIndex(self.combo_conta_endireitar.findData(
            endireitar_scantailor.jeito_do_livro(projeto)))
        self.cx_cortar.setChecked(projeto.cortar_bordas)
        self.cx_cadernos.setChecked(projeto.montar_cadernos)
        self.combo_caderno.setCurrentText(str(projeto.paginas_por_caderno))

        for botao in self.grupo_filtros.buttons():
            if botao.property("filtro") == filtro_do_livro:
                botao.setChecked(True)

        # item 1.2: o grupo "Gravuras e fotos"
        forma = projeto.gravura_forma
        self.cx_achar_gravuras.setChecked(forma != "desligada")
        self.cx_tem_fotos.setChecked(forma == "retangular")
        try:
            sensibilidade = max(0, min(100, int(projeto.gravura_sensibilidade)))
        except (TypeError, ValueError):
            sensibilidade = 100
        self.deslizante_sensibilidade.setValue(sensibilidade)
        self.cx_imagens_claras.setChecked(bool(projeto.gravura_mais_sensivel))
        self.cx_igualar_luz.setChecked(bool(projeto.gravura_normalizar))
        self.cx_decoracao_pb.setChecked(
            bool(getattr(projeto, "pb_decoracao_em_preto_e_branco", False)))
        # modo Misto (projeto antigo em memoria, sem os campos: os padroes)
        self.escolhas_misto.mostrar(
            bool(getattr(projeto, "misto_so_as_letras", False)),
            getattr(projeto, "misto_fora_do_texto", misto.FORA_DO_TEXTO_PADRAO),
            getattr(projeto, "misto_papel_da_gravura", misto.PAPEL_DA_GRAVURA_PADRAO),
            getattr(projeto, "misto_letras_na_moldura", misto.LETRAS_NA_MOLDURA_PADRAO))
        # "Limpar pontinhos" do livro (projeto em memoria sem o campo: o de
        # fabrica). Sem sinal: quem grava no projeto e o _mudou logo abaixo,
        # ja com self.projeto certo.
        self.combo_pontinhos.blockSignals(True)
        self.combo_pontinhos.setCurrentIndex(self.combo_pontinhos.findData(
            pontinhos.escolha_valida(getattr(projeto, "limpar_pontinhos", pontinhos.PADRAO))))
        self.combo_pontinhos.blockSignals(False)
        # "Mais opcoes" abre sozinho quando alguma das avancadas nao esta no
        # padrao: a pessoa ve o que foi mudado (fechado, ficaria escondido)
        fora_do_padrao = (sensibilidade != 100 or bool(projeto.gravura_mais_sensivel)
                          or not bool(projeto.gravura_normalizar))
        if fora_do_padrao and not self.botao_mais_opcoes.isChecked():
            self.botao_mais_opcoes.setChecked(True)
        self.projeto = projeto
        self._mudou()

    def _sair(self) -> None:
        """Solta o arquivo antes de sair. Ver FolhearPDF.fechar."""
        self.folhear.fechar()
        self.voltar.emit()

    def _seguir(self) -> None:
        """Idem, indo para a conferência: quem lê o livro daqui é o pipeline."""
        self.folhear.fechar()
        self.conferir.emit()

    def escolher_filtro_do_livro(self, filtro: str) -> None:
        """Marca `filtro` como o filtro do livro, como se a pessoa clicasse no
        radio (e marca "Limpar a folha", sem a qual nenhum filtro vale).

        Item 1.1: e o que o "Sim, tirar o fundo" do aviso de livro com
        camadas faz (ui/janela_principal._resposta_do_aviso_do_fundo). Passa
        pelos mesmos sinais do clique: _mudou grava no projeto e o resumo
        acompanha.
        """
        radio = self.radios_de_filtro.get(filtro)
        if radio is None:
            return
        if not self.cx_limpar.isChecked():
            self.cx_limpar.setChecked(True)
        radio.setChecked(True)
        self._mudou()

    def _filtro_escolhido(self) -> str:
        """O filtro marcado no grupo de radio-buttons, ou Preto e branco por padrão."""
        for botao in self.grupo_filtros.buttons():
            if botao.isChecked():
                return str(botao.property("filtro"))
        return ORIGINAL

    def _mudou(self) -> None:
        """Guarda as escolhas e atualiza o resumo ao vivo."""
        if self.projeto is None:
            return

        self.projeto.dividir_folhas = self.cx_dividir.isChecked()
        # item 2.1: o jeito so aparece com "Dividir" marcada (escondido, fica
        # guardado); o corte da sobra e independente
        self.projeto.dividir_como = dividir_scantailor.jeito_valido(
            self.combo_jeito_dividir.currentData())
        self.linha_jeito_dividir.setVisible(self.projeto.dividir_folhas)
        self.projeto.cortar_sobra = self.cx_cortar_sobra.isChecked()
        self.projeto.limpar = self.cx_limpar.isChecked()
        self.projeto.endireitar = self.cx_endireitar.isChecked()
        # item 2.2: a conta so aparece com "Endireitar" marcada (escondida,
        # fica guardada)
        self.projeto.endireitar_como = endireitar_scantailor.jeito_valido(
            self.combo_conta_endireitar.currentData())
        self.linha_conta_endireitar.setVisible(self.projeto.endireitar)
        self.projeto.cortar_bordas = self.cx_cortar.isChecked()
        self.projeto.montar_cadernos = self.cx_cadernos.isChecked()
        self.projeto.filtro_padrao = self._filtro_escolhido()
        self.projeto.paginas_por_caderno = paginas_por_caderno_valido(
            self.combo_caderno.currentData() or 20
        )

        # item 1.2: o grupo "Gravuras e fotos" (a forma sai de duas caixinhas)
        if not self.cx_achar_gravuras.isChecked():
            self.projeto.gravura_forma = "desligada"
        elif self.cx_tem_fotos.isChecked():
            self.projeto.gravura_forma = "retangular"
        else:
            self.projeto.gravura_forma = "livre"
        self.projeto.gravura_sensibilidade = int(self.deslizante_sensibilidade.value())
        self.projeto.gravura_mais_sensivel = self.cx_imagens_claras.isChecked()
        self.projeto.gravura_normalizar = self.cx_igualar_luz.isChecked()
        self.valor_sensibilidade.setText(str(self.projeto.gravura_sensibilidade))
        # emenda N2 (30/09): moldura e iluminura tambem em preto e branco
        self.projeto.pb_decoracao_em_preto_e_branco = self.cx_decoracao_pb.isChecked()
        # modo Misto (05/10): "So as letras" e as escolhas dela
        escolhas = self.escolhas_misto
        so_as_letras = escolhas.caixa.isChecked()
        self.projeto.misto_so_as_letras = so_as_letras
        self.projeto.misto_fora_do_texto = escolhas.fora_do_texto()
        self.projeto.misto_papel_da_gravura = (escolhas.combo_papel.currentData()
                                               or misto.PAPEL_DA_GRAVURA_PADRAO)
        self.projeto.misto_letras_na_moldura = (escolhas.combo_letras.currentData()
                                                or misto.LETRAS_NA_MOLDURA_PADRAO)
        # "So as letras" (e os tres botoes) so aparecem com o Preto e branco
        # escolhido: so nele o Misto vale (core.pipeline._filtrar). Ressalva 3
        # do verificador (05/10): com o Original aparecia e confundia. Escondida,
        # a escolha fica guardada e volta ao escolher o Preto e branco de novo.
        no_preto_e_branco = self.projeto.filtro_padrao == PRETO_E_BRANCO
        self.escolhas_misto.setVisible(no_preto_e_branco)
        # "Limpar pontinhos" do livro (06/10): como o "So as letras", so a
        # vista com o Preto e branco; escondida, a escolha fica guardada
        self.projeto.limpar_pontinhos = pontinhos.escolha_valida(
            self.combo_pontinhos.currentData())
        self.linha_pontinhos.setVisible(no_preto_e_branco)
        # P5 (conferencia 11): a caixinha das molduras fica apagada (cinza)
        # enquanto "So as letras" estiver marcada (e a vista), e volta como
        # estava ao desligar - o valor dela nao muda, so nao vale no Misto
        misto_vale = so_as_letras and no_preto_e_branco
        self.cx_decoracao_pb.setEnabled(not misto_vale)
        self._frase_decoracao_pb.setEnabled(not misto_vale)

        # os painéis so aparecem quando fazem sentido; o filtro "Tirar o
        # fundo" (item 1.1), so em PDF com camadas - fora dele nao faria nada
        # (e se ja estiver escolhido num PDF sem camadas, continua a vista
        # para a pessoa poder sair dele: ver core.filtros.filtros_do_livro)
        self.painel_filtros.setVisible(self.projeto.limpar)
        self.painel_gravuras.setVisible(self.projeto.limpar)
        self.painel_opcoes_gravura.setVisible(self.cx_achar_gravuras.isChecked())
        com_fotos = self.cx_tem_fotos.isChecked()
        for controle in (self.rotulo_sensibilidade, self.deslizante_sensibilidade,
                         self.valor_sensibilidade, self.explicacao_sensibilidade):
            controle.setEnabled(com_fotos)
        cor = "" if com_fotos else f"color: {TEXTO_FRACO};"
        self.rotulo_sensibilidade.setStyleSheet(cor)
        self.valor_sensibilidade.setStyleSheet(cor)
        mostrar_fundo = TIRAR_FUNDO in filtros_do_livro(self.projeto)
        self.radios_de_filtro[TIRAR_FUNDO].setVisible(mostrar_fundo)
        self._rotulos_de_filtro[TIRAR_FUNDO].setVisible(mostrar_fundo)
        self.painel_caderno.setVisible(self.projeto.montar_cadernos)

        self.resumo.setText(resumo_em_portugues(self.projeto, self.total_folhas))
        self._acertar_altura_da_rolagem()
        self.botao_conferir.setEnabled(self.projeto.alguma_funcao_marcada)


def _separador() -> QFrame:
    """Uma linha horizontal fina, para separar os blocos de opcao."""
    linha = QFrame()
    linha.setFrameShape(QFrame.HLine)
    linha.setStyleSheet("color: #e5e7eb; margin: 4px 0;")
    return linha
