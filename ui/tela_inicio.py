"""TELA 1 - Inicio: arrastar um livro novo, e continuar os que ja existem.

O que havia antes tinha quatro defeitos, todos visiveis num print: quatro
projetos com o mesmo nome e nenhum jeito de distingui-los; "abrir a pasta"
apagado em um deles sem explicar por que; a caixa de arrastar ocupando um terco
da tela para uma acao que se faz uma vez por livro; e "abrir de novo" que na
verdade nao retomava trabalho nenhum.

Os cartoes resolvem os quatro. **A miniatura da primeira pagina e o que
distingue livros de nome igual** - a pessoa reconhece o livro pela aparencia. A
barra de progresso diz onde o trabalho parou. E nada de botao apagado sem
explicacao: quando o PDF sai do lugar, o cartao inteiro fica laranja e diz o
que houve.

Medidas do desenho aprovado (1366x768): faixa de arrastar com 62 px de altura,
cartao de 304x220, area da miniatura com 112 px.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

import historico
import projetos
from ui.estilo import TEXTO_FRACO
from ui.widgets.area_arrastar import AreaArrastar

LARGURA_DO_CARTAO = 304
ALTURA_DO_CARTAO = 220
ALTURA_DA_CAPA = 112
ESPACO_ENTRE_CARTOES = 24

LARANJA, LARANJA_FUNDO = "#ef9f27", "#faeeda"
VERDE = "#1d9e75"

# O botao do cartao NAO usa o #primario da folha de estilo: aquele tem 13 px de
# recheio e fonte 16, feito para o "Confirmar e processar" do rodape. Dentro de
# um cartao de 220 px ele empurra o proprio texto para fora e o botao sai azul
# e vazio - foi o que apareceu no primeiro print.
BOTAO_DO_CARTAO = """
QPushButton {{
    background: {fundo}; color: {cor}; border: {borda};
    border-radius: 6px; font-size: 12px; padding: 4px 12px;
}}
QPushButton:hover {{ background: {aceso}; }}
"""


class TelaInicio(QWidget):
    abrir_pdf = Signal(str)
    continuar_projeto = Signal(object)      # projetos.Resumo
    recomecar_projeto = Signal(object)      # projetos.Resumo

    # Mantido por compatibilidade com a janela, que ainda escuta o nome antigo.
    reabrir_projeto = Signal(object)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._resumos: list[projetos.Resumo] = []

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(40, 24, 40, 22)
        camadas.setSpacing(14)

        titulo = QLabel("Editor de Impressão")
        titulo.setObjectName("titulo")
        camadas.addWidget(titulo)

        subtitulo = QLabel("Recupere um livro escaneado e prepare para reimprimir")
        subtitulo.setObjectName("subtitulo")
        camadas.addWidget(subtitulo)

        # A faixa de arrastar cabe numa linha: abrir livro novo se faz uma vez
        # por livro, e nao merecia um terco da tela.
        self.area = AreaArrastar()
        self.area.setFixedHeight(62)
        self.area.arquivo_escolhido.connect(self.abrir_pdf.emit)
        camadas.addWidget(self.area)

        cabecalho = QHBoxLayout()
        rotulo = QLabel("Continuar de onde parou")
        rotulo.setObjectName("secao")
        cabecalho.addWidget(rotulo)
        cabecalho.addStretch()
        self.busca = QLineEdit()
        self.busca.setPlaceholderText("procurar pelo nome")
        self.busca.setFixedWidth(196)
        self.busca.setClearButtonEnabled(True)
        self.busca.textChanged.connect(self._remontar)
        cabecalho.addWidget(self.busca)
        camadas.addLayout(cabecalho)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        # Nunca rola de lado: os cartoes quebram linha sozinhos. Deixar a barra
        # horizontal ligada punha uma faixa escura atravessada no pe da tela.
        self.rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        interno = QWidget()
        self.grade = QGridLayout(interno)
        self.grade.setContentsMargins(0, 0, 8, 0)
        self.grade.setSpacing(ESPACO_ENTRE_CARTOES)
        self.grade.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.rolagem.setWidget(interno)
        camadas.addWidget(self.rolagem, 1)

        self.recarregar()

    # --- montagem ---------------------------------------------------------

    def recarregar(self) -> None:
        """Le os resumos do disco. Nao abre o historico de projeto nenhum.

        E o que mantem a tela rapida com cinquenta projetos e um livro de mil
        paginas na lista: cada cartao sai de um arquivo pequeno.
        """
        self._resumos = projetos.listar()
        self._remontar()

    def _remontar(self) -> None:
        while self.grade.count():
            item = self.grade.takeAt(0)
            velho = item.widget()
            if velho is not None:
                # setParent(None) ANTES do deleteLater. So tirar do layout nao
                # tira da tela: o widget continua filho do painel e continua
                # sendo pintado na posicao antiga ate o Qt processar a fila -
                # e aparece um cartao fantasma ao lado dos de verdade, que e
                # exatamente o defeito que estes cartoes vieram consertar.
                velho.setParent(None)
                velho.deleteLater()

        procurado = self.busca.text().strip().lower()
        mostrar = [r for r in self._resumos
                   if not procurado or procurado in r.nome.lower()]

        if not mostrar:
            self.grade.addWidget(self._recado(procurado), 0, 0)
            return

        # Quantos cabem por linha. A folga de 6 px existe porque o desenho
        # aprovado nao tem margens iguais dos dois lados: 40 px a esquerda e 38
        # a direita, para os quatro cartoes caberem numa tela de 1366. Sem ela,
        # a conta erra por dois pixels e o quarto cartao cai para a linha de
        # baixo - que e o oposto do desenho.
        FOLGA = 6
        largura = self.rolagem.viewport().width() + ESPACO_ENTRE_CARTOES + FOLGA
        por_linha = max(1, largura // (LARGURA_DO_CARTAO + ESPACO_ENTRE_CARTOES))
        for posicao, resumo in enumerate(mostrar):
            cartao = CartaoDeProjeto(resumo, self)
            self.grade.addWidget(cartao, posicao // por_linha, posicao % por_linha)

    def _recado(self, procurado: str) -> QLabel:
        texto = (f'Nenhum projeto com "{procurado}" no nome.' if procurado
                 else "Nenhum livro ainda. Arraste o primeiro PDF ali em cima "
                      "para começar.")
        recado = QLabel(texto)
        recado.setStyleSheet(f"color: {TEXTO_FRACO}; padding: 14px;")
        return recado

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """A grade se refaz quando a janela muda de largura."""
        super().resizeEvent(evento)
        self._remontar()

    # --- acoes dos cartoes ------------------------------------------------

    def pedir_para_continuar(self, resumo: projetos.Resumo) -> None:
        situacao, caminho = projetos.procurar_o_livro(resumo)

        if situacao == projetos.TROCADO:
            QMessageBox.warning(
                self, "Este não é o mesmo livro",
                f"Existe um arquivo chamado {Path(caminho).name} nesse lugar, "
                "mas ele não é o livro deste projeto - alguém o substituiu.\n\n"
                "Não vou aplicar os ajustes deste projeto num livro diferente: "
                "isso estragaria o trabalho sem aparecer.\n\n"
                'Use "procurar de novo" e aponte onde está o livro certo.')
            return

        if situacao == projetos.SUMIU:
            self.procurar_o_livro_a_mao(resumo)
            return

        if situacao == projetos.RELIGADO:
            resumo.caminho_entrada = caminho
            projetos.gravar_resumo(resumo)

        self.continuar_projeto.emit(resumo)

    def procurar_o_livro_a_mao(self, resumo: projetos.Resumo) -> None:
        from PySide6.QtWidgets import QFileDialog

        caminho, _filtro = QFileDialog.getOpenFileName(
            self, f"Onde está o livro de {resumo.nome}?", "", "PDF (*.pdf)")
        if not caminho:
            return

        if resumo.assinatura and projetos.assinatura_do_arquivo(caminho) != resumo.assinatura:
            QMessageBox.warning(
                self, "Este não é o mesmo livro",
                "Esse arquivo não é o livro deste projeto. Os ajustes salvos "
                "aqui foram feitos em outro livro, e aplicá-los neste "
                "estragaria as páginas.")
            return

        resumo.caminho_entrada = caminho
        projetos.gravar_resumo(resumo)
        self.recarregar()
        self.continuar_projeto.emit(resumo)

    def pedir_para_recomecar(self, resumo: projetos.Resumo) -> None:
        resposta = QMessageBox.question(
            self, "Começar de novo?",
            f"Isto joga fora todos os ajustes de {resumo.nome} e abre o livro "
            "limpo.\n\nO livro em si não é tocado. O que se perde é a "
            "conferência já feita.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            self.recomecar_projeto.emit(resumo)

    def pedir_para_renomear(self, resumo: projetos.Resumo) -> None:
        novo, certo = QInputDialog.getText(
            self, "Renomear", "Nome deste projeto:", QLineEdit.Normal, resumo.nome)
        if certo and novo.strip():
            projetos.renomear(resumo, novo)
            self.recarregar()

    def pedir_para_remover(self, resumo: projetos.Resumo) -> None:
        resposta = QMessageBox.question(
            self, "Tirar da lista?",
            f"{resumo.nome} sai desta tela e a conferência feita nele se "
            "perde.\n\nO livro em PDF continua onde está - ele nunca esteve "
            "guardado aqui dentro.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if resposta == QMessageBox.Yes:
            projetos.remover_da_lista(resumo)
            self.recarregar()


class CartaoDeProjeto(QFrame):
    """Um livro na tela inicial: capa, nome, andamento e o que dá para fazer."""

    def __init__(self, resumo: projetos.Resumo, tela: TelaInicio) -> None:
        super().__init__()
        self.resumo = resumo
        self.tela = tela
        self.setObjectName("cartao")
        self.setFixedSize(LARGURA_DO_CARTAO, ALTURA_DO_CARTAO)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._abrir_menu)

        situacao, _caminho = projetos.procurar_o_livro(resumo)
        self.perdido = situacao in (projetos.SUMIU, projetos.TROCADO)

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(0)

        camadas.addWidget(self._montar_capa())

        corpo = QVBoxLayout()
        corpo.setContentsMargins(18, 10, 18, 10)
        corpo.setSpacing(5)

        # O nome e cortado com reticencias em vez de vazar do cartao. O nome
        # inteiro fica na dica do mouse, junto com o caminho do livro.
        self.rotulo_nome = QLabel()
        self.rotulo_nome.setStyleSheet("font-size: 15px; background: transparent;")
        self.rotulo_nome.setToolTip(f"{resumo.nome}\n{resumo.caminho_entrada}")
        corpo.addWidget(self.rotulo_nome)

        detalhe = QLabel(f"{resumo.total_paginas} páginas · {resumo.data_amigavel}")
        detalhe.setStyleSheet(
            f"color: {TEXTO_FRACO}; font-size: 12px; background: transparent;")
        corpo.addWidget(detalhe)

        if self.perdido:
            corpo.addWidget(self._montar_aviso_de_perdido())
        else:
            corpo.addWidget(self._montar_progresso())
            corpo.addLayout(self._montar_rodape())

        camadas.addLayout(corpo)
        self._aplicar_cor()

    # --- pedacos ----------------------------------------------------------

    def _montar_capa(self) -> QWidget:
        capa = QLabel()
        capa.setFixedHeight(ALTURA_DA_CAPA)
        capa.setAlignment(Qt.AlignCenter)
        capa.setStyleSheet(
            f"background: {LARANJA_FUNDO if self.perdido else '#f1efe8'};")

        caminho = projetos.garantir_miniatura(self.resumo)
        imagem = QPixmap(caminho) if caminho else QPixmap()
        if imagem.isNull():
            capa.setText("sem capa")
            capa.setStyleSheet(capa.styleSheet() + f"color: {TEXTO_FRACO};")
        else:
            capa.setPixmap(imagem.scaled(
                QSize(LARGURA_DO_CARTAO, ALTURA_DA_CAPA - 16),
                Qt.KeepAspectRatio, Qt.SmoothTransformation))
        return capa

    def _montar_progresso(self) -> QWidget:
        caixa = QWidget()
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(0, 0, 0, 0)
        dentro.setSpacing(4)

        pronto = self.resumo.pdf_gerado
        barra = QProgressBar()
        barra.setTextVisible(False)
        barra.setFixedHeight(6)
        barra.setRange(0, 100)
        barra.setValue(100 if pronto else int(self.resumo.progresso * 100))
        cor = VERDE if pronto else "#378add"
        barra.setStyleSheet(
            "QProgressBar { background: #e6e4e0; border: none; border-radius: 3px; }"
            f"QProgressBar::chunk {{ background: {cor}; border-radius: 3px; }}")
        dentro.addWidget(barra)
        return caixa

    def _montar_rodape(self) -> QHBoxLayout:
        linha = QHBoxLayout()
        linha.setContentsMargins(0, 0, 0, 0)

        frase = QLabel(self.resumo.frase_do_progresso)
        frase.setStyleSheet(
            f"color: {'#0f6e56' if self.resumo.pdf_gerado else '#185fa5'}; "
            "font-size: 12px; background: transparent;")
        linha.addWidget(frase)
        linha.addStretch()

        if self.resumo.pdf_gerado:
            botao = QPushButton("abrir a pasta")
            botao.setStyleSheet(BOTAO_DO_CARTAO.format(
                fundo="#ffffff", cor="#5f5e5a", borda="1px solid #d3d1c7",
                aceso="#f7f5f2"))
            botao.clicked.connect(
                lambda: historico.abrir_pasta(self.resumo.caminho_saida))
        else:
            botao = QPushButton("continuar")
            botao.setStyleSheet(BOTAO_DO_CARTAO.format(
                fundo="#378add", cor="#ffffff", borda="none", aceso="#2f76bd"))
            botao.clicked.connect(lambda: self.tela.pedir_para_continuar(self.resumo))
        botao.setFixedHeight(26)
        botao.setCursor(Qt.PointingHandCursor)
        linha.addWidget(botao)
        return linha

    def _montar_aviso_de_perdido(self) -> QWidget:
        """Nunca um botao apagado sem explicacao - era a queixa do print."""
        caixa = QWidget()
        caixa.setStyleSheet("background: transparent;")
        dentro = QVBoxLayout(caixa)
        dentro.setContentsMargins(0, 0, 0, 0)
        dentro.setSpacing(2)

        aviso = QLabel("o PDF saiu do lugar")
        aviso.setStyleSheet("color: #8a5a10; font-size: 12px;")
        dentro.addWidget(aviso)

        procurar = QPushButton("procurar de novo")
        procurar.setFlat(True)
        procurar.setCursor(Qt.PointingHandCursor)
        procurar.setStyleSheet(
            "QPushButton { border: none; color: #185fa5; font-size: 12px; "
            "text-align: left; padding: 0; }")
        procurar.clicked.connect(
            lambda: self.tela.procurar_o_livro_a_mao(self.resumo))
        dentro.addWidget(procurar)
        return caixa

    def _aplicar_cor(self) -> None:
        if not self.perdido:
            return
        # O seletor precisa ser QFrame#cartao e nao so o widget: sem ele, o Qt
        # aplica o fundo aos FILHOS tambem, e cada rotulo do cartao ganha uma
        # caixinha branca atras - foi o que apareceu no primeiro print.
        self.setStyleSheet(
            f"QFrame#cartao {{ border: 2px solid {LARANJA}; "
            f"background: {LARANJA_FUNDO}; border-radius: 10px; }}"
            "QLabel, QPushButton { background: transparent; }")

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        self._encurtar_o_nome()

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().showEvent(evento)
        self._encurtar_o_nome()

    def _encurtar_o_nome(self) -> None:
        """Nome comprido sai com reticencias, em vez de vazar do cartao."""
        from PySide6.QtGui import QFontMetrics

        largura = max(40, self.rotulo_nome.width())
        metrica = QFontMetrics(self.rotulo_nome.font())
        self.rotulo_nome.setText(
            metrica.elidedText(self.resumo.nome, Qt.ElideRight, largura))

    # --- menu do botao direito --------------------------------------------

    def _abrir_menu(self, posicao) -> None:
        menu = QMenu(self)
        if not self.perdido:
            menu.addAction("continuar",
                           lambda: self.tela.pedir_para_continuar(self.resumo))
        else:
            menu.addAction("procurar o livro",
                           lambda: self.tela.procurar_o_livro_a_mao(self.resumo))
        menu.addAction("começar de novo",
                       lambda: self.tela.pedir_para_recomecar(self.resumo))
        menu.addSeparator()
        menu.addAction("renomear", lambda: self.tela.pedir_para_renomear(self.resumo))
        abrir = menu.addAction(
            "abrir a pasta de saída",
            lambda: historico.abrir_pasta(self.resumo.caminho_saida))
        abrir.setEnabled(bool(self.resumo.caminho_saida)
                         and Path(self.resumo.caminho_saida).exists())
        if not abrir.isEnabled():
            abrir.setToolTip("Este livro ainda não gerou PDF nenhum.")
        menu.addSeparator()
        menu.addAction("remover da lista",
                       lambda: self.tela.pedir_para_remover(self.resumo))
        menu.exec(self.mapToGlobal(posicao))

    def mouseDoubleClickEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if not self.perdido:
            self.tela.pedir_para_continuar(self.resumo)
