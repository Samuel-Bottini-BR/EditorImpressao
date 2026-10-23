"""A tela cheia dos filtros (etapa 6 do layout, 21/10/2026).

O QUE O SAMUEL DECIDIU
    Rodada 9, 403 (comentário): "uma opção para conseguir abrir os filtros para ver um review de
    como ficaria com cada filtro, abrir em tela cheia, com as opções de cada filtro nessa tela
    cheia". Rodada 10, 503: o botão que abre é o "ícone no título do painel" (Filtro da página).
    Rodada 11, 601 "A — A “um grande”, com a chave “Comparar com o Original”": a fila dos
    filtros à esquerda, o filtro escolhido grande no meio, as opções dele à direita; a chave
    "Comparar com o Original" (começa desligada) vira o antes e depois, com a linha que se
    arrasta; em cima "Filtros da página N", as setas de página e Fechar (Esc); embaixo "Aplicar
    em: só nesta · todas · daqui em diante", "Fechar sem mudar" e "Usar <filtro>"; teclas 1 a 4.
    Rodada 14, 904 A: também pelo menu Ver > "Filtros em tela cheia".

O QUE FAZ, E O QUE NÃO FAZ
    Escolher um filtro aqui só MOSTRA; nada muda na página até "Usar <filtro>" (ou "Fechar sem
    mudar", que não muda nada). "Usar" grava o filtro e o ajuste pelos mesmos caminhos da tela de
    conferir (com desfazer) e, se o "Aplicar em" for "todas" ou "daqui em diante", leva para as
    outras páginas como os botões do painel Filtro.

    TODAS AS OPÇÕES DO FILTRO À DIREITA (Samuel, 22/10/2026, quadro l67-tela-cheia: "mas no
    programa vai aparecer as opções dos filtros né? o agente de layout fez já as opções de preto e
    branco que trouxemos do scan?", e "faça o recomendado"): as mesmas do painel Filtro da página,
    com os mesmos nomes. No Preto e branco: o ajuste, "Só as letras", "Limpar a sujeira", e em
    "Mais ajustes" o "Jeito do preto e branco" (com os dez do ScanTailor, 2.8), "Letra clara em
    fundo escuro" (2.9), "Letras com a cor delas" e "Reduzir cores" (2.11). Nos outros filtros, o
    ajuste, "Letra clara em fundo escuro" e "Reduzir cores". O que se mexe aqui fica guardado só
    nesta tela (self.ajustes e self.opcoes) até "Usar".

    O QUE SE VÊ É O QUE SAI: a página grande é sempre feita pelo mesmo caminho do PDF
    (core.pipeline.renderizar_com_filtro, o mesmo da GerenciadorPrevias.pegar_com_filtro), numa
    CÓPIA da página com as opções mexidas aqui; sem nada mexido, é a própria pegar_com_filtro.
    Antes (21/10) o ajuste mexido aqui mostrava a página só com o filtro, sem o "Só as letras".
    O antes e depois não tem zoom (a página inteira, lado a lado na mesma imagem).

Seguro mudar: tamanhos, textos e o DPI_DA_TELA_CHEIA. Arriscado: aplicar o filtro na página ao
escolher (o "Fechar sem mudar" perderia o sentido) ou desenhar a página no fio da tela (trava).
"""

from __future__ import annotations

import traceback

import numpy as np
from PySide6.QtCore import QObject, QPointF, QRectF, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.filtros import MAGICO_PRO, MELHORAR, NOMES_AMIGAVEIS, ORIGINAL, PRETO_E_BRANCO
from registro import registrar_erro
from ui import estilo
from ui.estilo import estilo_da_caixinha_com_quadrado
from ui.widgets.visualizador import numpy_para_qimage

DPI_DA_TELA_CHEIA = 150          # nítido na tela cheia, sem demorar demais (a prévia é 110)
LARGURA_DAS_OPCOES = 300         # a coluna das opções, à direita (com a barra de rolar)
TECLAS = {Qt.Key_1: ORIGINAL, Qt.Key_2: PRETO_E_BRANCO, Qt.Key_3: MELHORAR, Qt.Key_4: MAGICO_PRO}
SO_NESTA, TODAS, DAQUI_EM_DIANTE = "nesta", "todas", "daqui"


class _Sinais(QObject):
    pronta = Signal(object, object)          # chave, imagem


class _TarefaDasOpcoes(QRunnable):
    """A página com um filtro e opções que ainda não foram gravados, em segundo
    plano, pelo MESMO caminho do PDF (core.pipeline.renderizar_com_filtro) numa
    cópia da página: o que a tela cheia mostra é o que vai sair."""

    def __init__(self, chave, caminho_pdf, projeto, copia, filtro, sinais) -> None:
        super().__init__()
        self.chave, self.caminho_pdf, self.projeto = chave, caminho_pdf, projeto
        self.copia, self.filtro, self.sinais = copia, filtro, sinais

    def run(self) -> None:
        try:
            from core.pdf_io import abrir_pdf
            from core.pipeline import renderizar_com_filtro

            doc = abrir_pdf(self.caminho_pdf)
            try:
                saida, _ = renderizar_com_filtro(doc, self.projeto, self.copia, self.filtro,
                                                 dpi=DPI_DA_TELA_CHEIA)
            finally:
                doc.close()
            self.sinais.pronta.emit(self.chave, saida)
        except Exception:  # noqa: BLE001 - a tela cheia nunca derruba o programa
            registrar_erro("filtros em tela cheia", traceback.format_exc())


def pagina_com_as_opcoes(pagina, filtro: str, ajuste_campo: str | None, ajuste, opcoes: dict):
    """A cópia da página com o `filtro`, o ajuste e as `opcoes` mexidas na tela
    cheia (campo da ConfigPagina -> valor). A página de verdade não muda."""
    from dataclasses import replace

    campos = dict(opcoes)
    if ajuste_campo is not None and ajuste is not None:
        campos[ajuste_campo] = int(ajuste)
    return replace(pagina, filtro=filtro, alertas=list(pagina.alertas), **campos)


class VistaAntesDepois(QWidget):
    """A página grande. Com `depois` só, mostra a página inteira; com `antes`
    também (a chave "Comparar com o Original"), o antes à esquerda da linha e o
    depois à direita, na mesma imagem; a linha se arrasta (cursor de setas
    para os lados e a alça redonda no meio: a pista de que dá para arrastar)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.antes: QPixmap | None = None
        self.depois: QPixmap | None = None
        self.comparando = False
        self.posicao = 0.5
        self.rotulos = ("", "")
        self.aviso = ""
        self._arrastando = False
        self.setMinimumSize(QSize(200, 200))
        self.setMouseTracking(True)

    def definir(self, antes, depois, comparando: bool, rotulos=("", ""), aviso: str = "") -> None:
        conv = (lambda img: None if img is None else QPixmap.fromImage(numpy_para_qimage(img)))
        self.antes, self.depois = conv(antes), conv(depois)
        self.comparando, self.rotulos, self.aviso = comparando, rotulos, aviso
        self.update()

    def _area(self, pix: QPixmap) -> QRectF:
        escala = min((self.width() - 20) / pix.width(), (self.height() - 20) / pix.height())
        w, h = pix.width() * escala, pix.height() * escala
        return QRectF((self.width() - w) / 2, (self.height() - h) / 2, w, h)

    def paintEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(estilo.cor("tela")))
        if self.depois is None:
            pintor.setPen(QColor(estilo.cor("fraco")))
            pintor.drawText(self.rect(), Qt.AlignCenter, "preparando...")
            pintor.end()
            return
        area = self._area(self.depois)
        pintor.drawPixmap(area, self.depois, QRectF(self.depois.rect()))
        if self.comparando and self.antes is not None:
            x = area.left() + area.width() * self.posicao
            parte = QRectF(area.left(), area.top(), x - area.left(), area.height())
            fonte = QRectF(0, 0, self.antes.width() * self.posicao, self.antes.height())
            pintor.drawPixmap(parte, self.antes, fonte)
            pintor.setPen(QPen(QColor(estilo.cor("azul")), 2))
            pintor.drawLine(QPointF(x, area.top()), QPointF(x, area.bottom()))
            pintor.setBrush(QColor(estilo.cor("azul")))
            pintor.drawEllipse(QPointF(x, area.center().y()), 9, 9)
            pintor.setPen(QPen(QColor("white"), 1.6))
            cy = area.center().y()
            pintor.drawLine(QPointF(x - 4, cy), QPointF(x - 1, cy - 3))
            pintor.drawLine(QPointF(x - 4, cy), QPointF(x - 1, cy + 3))
            pintor.drawLine(QPointF(x + 4, cy), QPointF(x + 1, cy - 3))
            pintor.drawLine(QPointF(x + 4, cy), QPointF(x + 1, cy + 3))
            for texto, alinhar, ret in ((self.rotulos[0], Qt.AlignLeft, area.adjusted(8, 8, -8, 0)),
                                        (self.rotulos[1], Qt.AlignRight, area.adjusted(8, 8, -8, 0))):
                if not texto:
                    continue
                largura = pintor.fontMetrics().horizontalAdvance(texto) + 16
                caixa = QRectF(ret.left() if alinhar == Qt.AlignLeft else ret.right() - largura,
                               ret.top(), largura, 22)
                pintor.setPen(Qt.NoPen)
                pintor.setBrush(QColor(0, 0, 0, 160))
                pintor.drawRoundedRect(caixa, 4, 4)
                pintor.setPen(QColor("white"))
                pintor.drawText(caixa, Qt.AlignCenter, texto)
        if self.aviso:
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(0, 0, 0, 170))
            largura = pintor.fontMetrics().horizontalAdvance(self.aviso) + 24
            caixa = QRectF((self.width() - largura) / 2, area.top() + 10, largura, 26)
            pintor.drawRoundedRect(caixa, 5, 5)
            pintor.setPen(QColor("white"))
            pintor.drawText(caixa, Qt.AlignCenter, self.aviso)
        pintor.end()

    def _na_linha(self, x: float) -> bool:
        if not (self.comparando and self.depois is not None):
            return False
        area = self._area(self.depois)
        return abs(x - (area.left() + area.width() * self.posicao)) < 12

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.button() == Qt.LeftButton and self._na_linha(evento.position().x()):
            self._arrastando = True

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        x = evento.position().x()
        if self._arrastando and self.depois is not None:
            area = self._area(self.depois)
            self.posicao = min(1.0, max(0.0, (x - area.left()) / max(1.0, area.width())))
            self.update()
        self.setCursor(Qt.SplitHCursor if (self._arrastando or self._na_linha(x)) else Qt.ArrowCursor)

    def mouseReleaseEvent(self, _evento) -> None:  # noqa: N802 - nome do Qt
        self._arrastando = False


class FiltrosEmTelaCheia(QDialog):
    """A tela cheia dos filtros (ver o começo do arquivo). `conferir` é a TelaConferir dona."""

    fechou = Signal()

    def __init__(self, conferir, parent=None) -> None:
        super().__init__(parent or conferir)
        from core.filtros import filtros_do_livro
        from ui.tela_conferir import CARTOES, ROTULOS_DO_AJUSTE
        from ui.widgets.paineis import CartaozinhoDoFiltro

        self.conferir = conferir
        self.setWindowTitle("Filtros em tela cheia")
        self.setObjectName("filtrosEmTelaCheia")
        estilo.estilizar(self, lambda: estilo.FOLHA_DE_ESTILO)
        self.rotulos_do_ajuste = ROTULOS_DO_AJUSTE
        projeto = conferir.projeto
        filtros = list(filtros_do_livro(projeto))
        self.explicacoes = {c: e for c, _n, e in CARTOES}
        self.nomes = {c: n for c, n, _e in CARTOES}
        self.filtros = [c for c, _n, _e in CARTOES if c in filtros]
        self.escolhido = projeto.paginas[conferir.indice_pagina].filtro
        self.ajustes: dict[str, int] = {}         # o ajuste mexido aqui, por filtro (até "Usar")
        self.opcoes: dict[str, object] = {}       # as outras opções mexidas aqui (campo -> valor)
        self.alcance = SO_NESTA
        self._imagens: dict = {}                  # as feitas aqui (ajuste mexido)
        self._pedidas: set = set()
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._chegou)

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)

        # --- em cima
        alto = QFrame()
        alto.setObjectName("altoDaTelaCheia")
        linha = QHBoxLayout(alto)
        linha.setContentsMargins(14, 8, 14, 8)
        linha.setSpacing(8)
        self.titulo = QLabel("")
        self.titulo.setObjectName("tituloDaTelaCheia")
        linha.addWidget(self.titulo)
        self.anterior = self._botao("‹", "página anterior (seta para a esquerda)", lambda: self._navegar(-1))
        self.proxima = self._botao("›", "próxima página (seta para a direita)", lambda: self._navegar(1))
        linha.addWidget(self.anterior)
        linha.addWidget(self.proxima)
        linha.addSpacing(16)
        self.chave_comparar = QCheckBox("Comparar com o Original")
        estilo.estilizar(self.chave_comparar, lambda: estilo_da_caixinha_com_quadrado(14))
        self.chave_comparar.setCursor(Qt.PointingHandCursor)
        self.chave_comparar.setFocusPolicy(Qt.NoFocus)
        self.chave_comparar.toggled.connect(lambda _m: self.atualizar())
        linha.addWidget(self.chave_comparar)
        linha.addStretch()
        self.botao_fechar = self._botao("Fechar", "Fecha sem mudar nada (Esc)", self.reject)
        linha.addWidget(self.botao_fechar)
        fora.addWidget(alto)

        # --- o meio: fila | página | opções
        meio = QHBoxLayout()
        meio.setContentsMargins(0, 0, 0, 0)
        meio.setSpacing(0)
        fila = QFrame()
        fila.setObjectName("filaDaTelaCheia")
        coluna = QVBoxLayout(fila)
        coluna.setContentsMargins(10, 10, 10, 10)
        coluna.setSpacing(8)
        self.cartoes: dict[str, CartaozinhoDoFiltro] = {}
        teclas = {ORIGINAL: "1", PRETO_E_BRANCO: "2", MELHORAR: "3", MAGICO_PRO: "4"}
        for chave in self.filtros:
            cartao = CartaozinhoDoFiltro(chave, self.nomes[chave], teclas.get(chave, ""))
            cartao.desenho.LADO = QSize(78, 104)
            cartao.desenho.setFixedSize(cartao.desenho.LADO)
            cartao.escolhido.connect(self.escolher)
            amostra = getattr(conferir.cartoes.get(chave), "ultima_amostra", None)
            cartao.definir_amostra(amostra)
            if chave in conferir.cartoes:
                conferir.cartoes[chave].amostra_mudou.connect(self._amostra_mudou)
            self.cartoes[chave] = cartao
            coluna.addWidget(cartao)
        coluna.addStretch()
        # a fila rola quando a janela é baixa (1000 x 600: os quatro não cabem)
        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QFrame.NoFrame)
        rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        rolagem.setWidget(fila)
        rolagem.setFixedWidth(130)
        meio.addWidget(rolagem)
        self.vista = VistaAntesDepois()
        meio.addWidget(self.vista, 1)
        opcoes = QFrame()
        opcoes.setObjectName("opcoesDaTelaCheia")
        self.coluna_opcoes = QVBoxLayout(opcoes)
        self.coluna_opcoes.setContentsMargins(16, 14, 16, 14)
        self.coluna_opcoes.setSpacing(8)
        self.nome_do_filtro = QLabel("")
        self.nome_do_filtro.setObjectName("nomeDoFiltroDaTelaCheia")
        self.nome_do_filtro.setStyleSheet("font-size: 15px; font-weight: 600;")
        self.coluna_opcoes.addWidget(self.nome_do_filtro)
        self.explicacao = QLabel("")
        self.explicacao.setObjectName("fraseDaTelaCheia")
        self.explicacao.setWordWrap(True)
        self.coluna_opcoes.addWidget(self.explicacao)
        from ui.widgets.medidor import Medidor
        self.medidor = Medidor("Força do preto", "mais fraco", "mais escuro", em_duas_linhas=True)
        self.medidor.soltou.connect(self._ajuste_mudou)
        self.medidor.barra.setFocusPolicy(Qt.NoFocus)
        self.coluna_opcoes.addWidget(self.medidor)
        self.frase_do_ajuste = QLabel("")
        self.frase_do_ajuste.setObjectName("fraseDaTelaCheia")
        self.frase_do_ajuste.setWordWrap(True)
        self.coluna_opcoes.addWidget(self.frase_do_ajuste)
        self._montar_as_opcoes()
        self.coluna_opcoes.addStretch()
        # as opções rolam (no Preto e branco são muitas para a janela de 1280 x 657)
        rolagem_opcoes = QScrollArea()
        rolagem_opcoes.setWidgetResizable(True)
        rolagem_opcoes.setFrameShape(QFrame.NoFrame)
        rolagem_opcoes.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        rolagem_opcoes.setWidget(opcoes)
        rolagem_opcoes.setFixedWidth(LARGURA_DAS_OPCOES)
        meio.addWidget(rolagem_opcoes)
        fora.addLayout(meio, 1)

        # --- embaixo
        pe = QFrame()
        pe.setObjectName("peDaTelaCheia")
        linha = QHBoxLayout(pe)
        linha.setContentsMargins(14, 8, 14, 8)
        linha.setSpacing(6)
        linha.addWidget(QLabel("Aplicar em:"))
        self.grupo_alcance = QButtonGroup(self)
        self.botoes_alcance = {}
        for chave, texto in ((SO_NESTA, "só nesta"), (TODAS, "todas"), (DAQUI_EM_DIANTE, "daqui em diante")):
            botao = QPushButton(texto)
            botao.setCheckable(True)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setFocusPolicy(Qt.NoFocus)
            botao.clicked.connect(lambda _c=False, k=chave: self._escolher_alcance(k))
            self.grupo_alcance.addButton(botao)
            self.botoes_alcance[chave] = botao
            linha.addWidget(botao)
        self.botoes_alcance[SO_NESTA].setChecked(True)
        linha.addStretch()
        self.botao_sem_mudar = self._botao("Fechar sem mudar", "Fecha sem mudar nada (Esc)", self.reject)
        linha.addWidget(self.botao_sem_mudar)
        self.botao_usar = QPushButton("")
        self.botao_usar.setObjectName("primario")
        self.botao_usar.setCursor(Qt.PointingHandCursor)
        self.botao_usar.setFocusPolicy(Qt.NoFocus)
        self.botao_usar.clicked.connect(self.usar)
        linha.addWidget(self.botao_usar)
        fora.addWidget(pe)
        estilo.estilizar(alto, self._folha)

        if conferir.previas is not None:
            conferir.previas.pronta.connect(self._previa_chegou)
        janela = conferir.window()
        self.resize(janela.size() if janela is not None else QSize(1280, 760))
        self.atualizar()

    # --- as opções do filtro (22/10/2026) ---------------------------------------

    def _montar_as_opcoes(self) -> None:
        """As opções do painel Filtro da página, com os mesmos nomes e as mesmas
        listas: "Só as letras", "Limpar a sujeira" e "Mais ajustes". Mexer aqui
        só guarda em self.opcoes (ver _guardar_opcao); nada muda na página."""
        from core import claro_no_escuro, cores_scantailor
        from core import pontinhos_scantailor as pontinhos
        from core import preto_e_branco_scantailor
        from core.filtros import ALGORITMOS_PB, NOMES_DOS_ALGORITMOS_PB
        from ui.tela_conferir import FRASES_DA_LIMPEZA
        from ui.widgets.escolhas_do_misto import EscolhasDoMisto
        from ui.widgets.menu_com_amostra import ListaComAmostra, desenho_da_limpeza
        from ui.widgets.paineis import frase_do_painel, lista_estreita, titulo_de_secao

        self._mostrando = False

        def parte(titulo: str) -> QVBoxLayout:
            caixa = QWidget()
            coluna = QVBoxLayout(caixa)
            coluna.setContentsMargins(0, 8, 0, 0)
            coluna.setSpacing(5)
            coluna.addWidget(titulo_de_secao(titulo))
            self.coluna_opcoes.addWidget(caixa)
            self.partes_das_opcoes[titulo] = caixa
            return coluna

        self.partes_das_opcoes: dict[str, QWidget] = {}
        # Só as letras (só no Preto e branco)
        coluna = parte("Só as letras")
        self.escolhas_misto = EscolhasDoMisto(com_amostra=True)
        self.escolhas_misto.so_as_letras_mudou.connect(
            lambda v: self._guardar_opcao("misto_so_as_letras", bool(v)))
        self.escolhas_misto.fora_do_texto_escolhido.connect(
            lambda v: self._guardar_opcao("misto_fora_do_texto", v))
        self.escolhas_misto.papel_escolhido.connect(lambda v: self._guardar_opcao("misto_papel_da_gravura", v))
        self.escolhas_misto.letras_escolhidas.connect(
            lambda v: self._guardar_opcao("misto_letras_na_moldura", v))
        coluna.addWidget(self.escolhas_misto)
        # Limpar a sujeira (só no Preto e branco)
        coluna = parte("Limpar a sujeira")
        coluna.addWidget(frase_do_painel(pontinhos.EXPLICACAO_NA_TELA.split("\n")[0]))
        self.seletor_pontinhos = ListaComAmostra(desenho_da_limpeza)
        for chave in pontinhos.ESCOLHAS:
            self.seletor_pontinhos.addItem(pontinhos.NOMES_NA_TELA[chave], chave)
            self.seletor_pontinhos.definir_detalhes(
                chave, FRASES_DA_LIMPEZA.get(chave, ""), de_fabrica=(chave == pontinhos.PADRAO))
        self.seletor_pontinhos.setToolTip(pontinhos.EXPLICACAO_NA_TELA)
        self.seletor_pontinhos.currentIndexChanged.connect(
            lambda i: self._guardar_opcao("limpar_pontinhos", self.seletor_pontinhos.itemData(i)))
        coluna.addWidget(self.seletor_pontinhos)
        # Mais ajustes (em todo filtro que tem ajuste)
        coluna = parte("Mais ajustes")
        self.rotulo_algoritmo_pb = QLabel("Jeito do preto e branco")
        coluna.addWidget(self.rotulo_algoritmo_pb)
        self.seletor_algoritmo_pb = QComboBox()
        self.seletor_algoritmo_pb.addItem("Automático", "auto")
        for chave in ALGORITMOS_PB:
            self.seletor_algoritmo_pb.addItem(NOMES_DOS_ALGORITMOS_PB[chave], chave)
        self.seletor_algoritmo_pb.insertSeparator(self.seletor_algoritmo_pb.count())
        for chave in preto_e_branco_scantailor.CODIGOS:
            self.seletor_algoritmo_pb.addItem(preto_e_branco_scantailor.NOMES_NA_TELA[chave], chave)
        self.seletor_algoritmo_pb.setToolTip(preto_e_branco_scantailor.EXPLICACAO_NA_TELA)
        self.seletor_algoritmo_pb.currentIndexChanged.connect(
            lambda i: self._guardar_opcao("algoritmo_preto_branco", self.seletor_algoritmo_pb.itemData(i)))
        lista_estreita(self.seletor_algoritmo_pb)
        coluna.addWidget(self.seletor_algoritmo_pb)
        self.caixas: dict[str, QCheckBox] = {}
        for campo, rotulo, dica in (
                ("claro_no_escuro", claro_no_escuro.ROTULO_NA_TELA, claro_no_escuro.EXPLICACAO_NA_TELA),
                ("letras_com_a_cor", cores_scantailor.ROTULO_LETRAS, cores_scantailor.EXPLICACAO_LETRAS),
                ("reduzir_cores", cores_scantailor.ROTULO_REDUZIR, cores_scantailor.EXPLICACAO_REDUZIR)):
            caixa = QCheckBox(rotulo)
            estilo.estilizar(caixa, lambda: estilo_da_caixinha_com_quadrado(15))
            caixa.setToolTip(dica)
            caixa.setCursor(Qt.PointingHandCursor)
            caixa.toggled.connect(lambda marcada, c=campo: self._guardar_opcao(c, bool(marcada)))
            coluna.addWidget(caixa)
            self.caixas[campo] = caixa

    def _valores_da_pagina(self, pagina) -> dict:
        """O que vale numa página (dela ou do livro), campo a campo, nas opções."""
        from core import claro_no_escuro, misto
        from core import pontinhos_scantailor as pontinhos

        projeto = self.conferir.projeto
        ligado, escolhas = misto.escolhas_da_pagina(projeto, pagina)
        return {"misto_so_as_letras": ligado, "misto_fora_do_texto": escolhas.fora_do_texto,
                "misto_papel_da_gravura": escolhas.papel_da_gravura,
                "misto_letras_na_moldura": escolhas.letras_na_moldura,
                "limpar_pontinhos": pontinhos.escolha_da_pagina(projeto, pagina),
                "algoritmo_preto_branco": pagina.algoritmo_preto_branco,
                "claro_no_escuro": claro_no_escuro.ligado(pagina),
                "letras_com_a_cor": bool(getattr(pagina, "letras_com_a_cor", False)),
                "reduzir_cores": bool(getattr(pagina, "reduzir_cores", False))}

    def _guardar_opcao(self, campo: str, valor) -> None:
        """Uma opção mexida aqui: guardada (ou esquecida, se voltou ao que a
        página já tem) e a página grande é refeita. A página não muda."""
        if self._mostrando or valor is None:
            return
        if self._valores_da_pagina(self.pagina).get(campo) == valor:
            self.opcoes.pop(campo, None)
        else:
            self.opcoes[campo] = valor
        self.atualizar()

    def _mostrar_as_opcoes(self) -> None:
        """Mostra nas opções o que vale agora (o da página com o mexido aqui),
        e só as que valem no filtro escolhido (sem virar mudança)."""
        valores = self._valores_da_pagina(self.pagina)
        valores.update(self.opcoes)
        eh_pb = self.escolhido == PRETO_E_BRANCO
        tem_ajuste = self._campo(self.escolhido) is not None
        self._mostrando = True
        try:
            self.partes_das_opcoes["Só as letras"].setVisible(eh_pb)
            self.partes_das_opcoes["Limpar a sujeira"].setVisible(eh_pb)
            self.partes_das_opcoes["Mais ajustes"].setVisible(tem_ajuste)
            self.rotulo_algoritmo_pb.setVisible(eh_pb)
            self.seletor_algoritmo_pb.setVisible(eh_pb)
            self.caixas["letras_com_a_cor"].setVisible(eh_pb)
            self.escolhas_misto.mostrar(valores["misto_so_as_letras"], valores["misto_fora_do_texto"],
                                        valores["misto_papel_da_gravura"], valores["misto_letras_na_moldura"])
            self.seletor_pontinhos.setCurrentIndex(
                max(0, self.seletor_pontinhos.findData(valores["limpar_pontinhos"])))
            self.seletor_algoritmo_pb.setCurrentIndex(
                max(0, self.seletor_algoritmo_pb.findData(valores["algoritmo_preto_branco"])))
            for campo, caixa in self.caixas.items():
                caixa.setChecked(bool(valores[campo]))
        finally:
            self._mostrando = False

    def _mexido(self, filtro: str) -> bool:
        """Se há algo mexido aqui que muda a página no `filtro`."""
        return filtro in self.ajustes or (filtro != ORIGINAL and bool(self.opcoes))

    # --- peças -----------------------------------------------------------------

    def _folha(self) -> str:
        c = estilo.cor
        return (f"QFrame#altoDaTelaCheia {{ background: {c('bar')}; border-bottom: 1px solid {c('linha')}; }}"
                f"QLabel#tituloDaTelaCheia {{ color: {c('forte')}; font-size: 15px; font-weight: 600; }}")

    def _botao(self, texto: str, dica: str, acao) -> QPushButton:
        botao = QPushButton(texto)
        botao.setToolTip(dica)
        botao.setCursor(Qt.PointingHandCursor)
        botao.setFocusPolicy(Qt.NoFocus)
        botao.clicked.connect(lambda _c=False: acao())
        return botao

    @property
    def pagina(self):
        return self.conferir.projeto.paginas[self.conferir.indice_pagina]

    def _campo(self, filtro: str) -> str | None:
        return self.conferir._campo_do_ajuste(filtro)

    def _ajuste_de(self, filtro: str) -> int | None:
        campo = self._campo(filtro)
        if campo is None:
            return None
        return self.ajustes.get(filtro, getattr(self.pagina, campo))

    # --- desenho ---------------------------------------------------------------

    def atualizar(self) -> None:
        """Redesenha tudo para a página e o filtro escolhidos aqui."""
        try:
            indice = self.conferir.indice_pagina
            total = len(self.conferir.projeto.paginas)
            self.titulo.setText(f"Filtros da página {indice + 1}")
            self.anterior.setEnabled(indice > 0)
            self.proxima.setEnabled(indice < total - 1)
            for chave, cartao in self.cartoes.items():
                cartao.definir_selecionado(chave == self.escolhido)
            nome = self.nomes.get(self.escolhido, NOMES_AMIGAVEIS.get(self.escolhido, self.escolhido))
            self.nome_do_filtro.setText(nome)
            self.explicacao.setText(self.explicacoes.get(self.escolhido, "").capitalize() + "."
                                    + ("  (é o filtro desta página)" if self.escolhido == self.pagina.filtro
                                       else ""))
            self.botao_usar.setText(f"Usar {nome}")
            campo = self._campo(self.escolhido)
            self.medidor.setVisible(campo is not None)
            if campo is not None:
                rotulo, esquerda, direita = self.rotulos_do_ajuste[self.escolhido]
                self.medidor.definir_rotulo(rotulo, esquerda, direita)
                self.medidor.definir(self._ajuste_de(self.escolhido))
            frases = []
            if campo is None:
                frases.append("O Original não tem ajuste.")
            elif self._mexido(self.escolhido):
                frases.append(f"Mexido aqui: a página grande já mostra como vai sair; a página só "
                              f"muda quando você clicar em “Usar {nome}”.")
            self.frase_do_ajuste.setText("\n\n".join(frases))
            self.frase_do_ajuste.setVisible(bool(frases))
            self._mostrar_as_opcoes()
            comparando = self.chave_comparar.isChecked()
            aviso = ""
            antes = None
            if comparando and self.escolhido == ORIGINAL:
                aviso = "Escolha outro filtro para comparar com o Original."
                comparando = False
            elif comparando:
                antes = self._imagem(ORIGINAL)
            self.vista.definir(antes, self._imagem(self.escolhido), comparando,
                               ("antes: Original", f"depois: {nome}"), aviso)
        except Exception:  # noqa: BLE001 - nada aqui fecha a janela
            registrar_erro("filtros em tela cheia (atualizar)", traceback.format_exc())

    def _imagem(self, filtro: str):
        """A página grande no `filtro`, como vai sair: sem nada mexido aqui, a de
        verdade (pegar_com_filtro); com algo mexido, a cópia da página com o
        mexido, pelo mesmo caminho do PDF (_TarefaDasOpcoes). None até chegar
        (pedida em segundo plano)."""
        conferir = self.conferir
        indice = conferir.indice_pagina
        if not self._mexido(filtro):
            return conferir.previas.pegar_com_filtro(indice, DPI_DA_TELA_CHEIA, filtro)
        copia = self.pagina_mexida(filtro)
        chave = (indice, filtro, tuple(sorted((k, str(v)) for k, v in self.opcoes.items())),
                 self.ajustes.get(filtro), conferir.previas.chave(indice, DPI_DA_TELA_CHEIA))
        if chave in self._imagens:
            return self._imagens[chave]
        if chave not in self._pedidas:
            self._pedidas.add(chave)
            self._pool.start(_TarefaDasOpcoes(chave, conferir.previas.caminho_pdf, conferir.projeto,
                                              copia, filtro, self._sinais))
        return None

    def pagina_mexida(self, filtro: str):
        """A cópia da página com o `filtro` e tudo o que foi mexido aqui."""
        campo = self._campo(filtro)
        opcoes = self.opcoes if filtro != ORIGINAL else {}
        return pagina_com_as_opcoes(self.pagina, filtro, campo, self.ajustes.get(filtro), opcoes)

    def _chegou(self, chave, img) -> None:
        self._imagens = {k: v for k, v in self._imagens.items() if k[0] == chave[0]}
        self._imagens[chave] = img
        self.atualizar()

    def _previa_chegou(self, *_args) -> None:
        self.atualizar()

    def _amostra_mudou(self, chave: str, img) -> None:
        cartao = self.cartoes.get(chave)
        if cartao is not None:
            cartao.definir_amostra(img)

    # --- ações -------------------------------------------------------------------

    def escolher(self, filtro: str) -> None:
        """Mostra a página no `filtro` (não muda a página: só "Usar" muda)."""
        if filtro in self.filtros:
            self.escolhido = filtro
            self.atualizar()

    def _ajuste_mudou(self, valor: int) -> None:
        campo = self._campo(self.escolhido)
        if campo is None:
            return
        if int(valor) == getattr(self.pagina, campo):
            self.ajustes.pop(self.escolhido, None)
        else:
            self.ajustes[self.escolhido] = int(valor)
        self.atualizar()

    def _escolher_alcance(self, alcance: str) -> None:
        self.alcance = alcance

    def _navegar(self, passo: int) -> None:
        """Outra página: o que foi mexido aqui e não foi usado é esquecido."""
        total = len(self.conferir.projeto.paginas)
        novo = max(0, min(total - 1, self.conferir.indice_pagina + passo))
        if novo == self.conferir.indice_pagina:
            return
        self.conferir.ir_para_pagina(novo)
        self.ajustes.clear()
        self.opcoes.clear()
        self.escolhido = self.pagina.filtro
        self.atualizar()

    def usar(self) -> None:
        """Grava o filtro (e o ajuste mexido) na página, e leva para as outras
        se o "Aplicar em" pedir. Fecha a tela."""
        self.conferir.usar_da_tela_cheia(self.escolhido, self.ajustes.get(self.escolhido), self.alcance,
                                         opcoes=dict(self.opcoes) if self.escolhido != ORIGINAL else {})
        self.accept()

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        tecla = evento.key()
        if tecla == Qt.Key_Escape:
            self.reject()
        elif tecla == Qt.Key_Left:
            self._navegar(-1)
        elif tecla == Qt.Key_Right:
            self._navegar(1)
        elif tecla in TECLAS:
            self.escolher(TECLAS[tecla])
        else:
            super().keyPressEvent(evento)

    def done(self, resultado) -> None:  # noqa: D401 - nome do Qt
        """Ao fechar (de qualquer jeito), solta os sinais da tela de conferir."""
        try:
            if self.conferir.previas is not None:
                self.conferir.previas.pronta.disconnect(self._previa_chegou)
            for cartao in self.conferir.cartoes.values():
                cartao.amostra_mudou.disconnect(self._amostra_mudou)
        except (RuntimeError, TypeError):
            pass
        self.fechou.emit()
        super().done(resultado)
