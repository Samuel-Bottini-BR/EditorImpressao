"""TELA 3 - Conferir: a prévia e todos os ajustes manuais.

Empilhamento da tela, de cima para baixo, sem nenhuma sobreposicao:

    1. cabecalho (titulo, contador de alertas, desfazer/refazer)
    2. barra de abas
    3. área da imagem            <- fica com todo o espaço que sobrar
    4. faixa de explicação
    5. linha de botões
    6. tira de miniaturas
    7. onde salvar
    8. rodape (voltar / confirmar e processar)

Tudo isso num único QVBoxLayout. A faixa e os botões NAO moram dentro das
páginas das abas: elas guardam só a imagem. Foi por isso que a versão anterior
sobrepunha - a página da aba não tinha altura para caber imagem + faixa +
botões, e o Qt acabava empilhando um por cima do outro.

Por isso tambem usamos QTabBar (só a barra) com QStackedWidget, e não
QTabWidget: assim a faixa e os botões ficam de fora, como irmaos.

As abas aparecem conforme o que foi marcado na tela 2. Cada uma edita uma
unidade diferente:

    Onde cortar -> FOLHA do PDF de entrada (a linha da lombada)
    Bordas      -> PAGINA de saida (o retangulo do recorte)
    Endireitar  -> PAGINA de saida (o ângulo)
    Filtro      -> PAGINA de saida (o filtro e a força do preto)

O alerta chama atenção, nunca restringe: todo controle continua disponível em
qualquer página, com ou sem alerta.
"""

from __future__ import annotations

import functools
import traceback

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTabBar,
    QVBoxLayout,
    QWidget,
)

from core import analise
from core.filtros import (
    FORCAS,
    MAGICO_PRO,
    MELHORAR,
    NOMES_AMIGAVEIS,
    ORIGINAL,
    PRETO_E_BRANCO,
)
from historico_acoes import HistoricoAcoes, aplicar, montar_acao
from modelos import Projeto
from registro import registrar_erro
from ui.estilo import AZUL, AZUL_CLARO, LARANJA, LARANJA_CLARO
from ui.tarefas import GerenciadorPrevias
from ui.widgets.cartao_filtro import CartaoFiltro
from ui.widgets.destino import SeletorDestino
from ui.widgets.tira_miniaturas import TiraMiniaturas
from ui.widgets.visualizador import (
    MODO_ANGULO,
    MODO_CORTE,
    MODO_RECORTE,
    Visualizador,
)

DPI_PREVIA = 110          # baixo de proposito: a tela precisa abrir em segundos

ABA_CORTE, ABA_BORDAS, ABA_ANGULO, ABA_FILTRO = "corte", "bordas", "angulo", "filtro"

TITULOS = {
    ABA_CORTE: "Onde cortar",
    ABA_BORDAS: "Bordas",
    ABA_ANGULO: "Endireitar",
    ABA_FILTRO: "Filtro",
}

ROTULOS_FORCA = {
    "mais_fraco": "mais fraco",
    "normal": "normal",
    "mais_escuro": "mais escuro",
}

CARTOES = [
    (ORIGINAL, "Original", "sem mexer"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado"),
    (MELHORAR, "Melhorar", "mantem a cor"),
    (MAGICO_PRO, "Mágico pro", "cor viva"),
]


def protegido(metodo):
    """Nenhuma acao de botão pode fechar a janela (regra 3.3).

    Qualquer excecao vira aviso em portugues e vai para o arquivo de log. Sem
    isto, um erro dentro de um slot do Qt derruba o programa inteiro e o
    usuario perde o trabalho da tela de conferir.
    """

    @functools.wraps(metodo)
    def envolvido(self, *args, **kwargs):
        try:
            return metodo(self, *args, **kwargs)
        except Exception:  # noqa: BLE001 - e exatamente o ponto
            registrar_erro(f"tela_conferir.{metodo.__name__}", traceback.format_exc())
            self._avisar_problema()
            return None

    return envolvido


class TelaConferir(QWidget):
    voltar = Signal()
    processar = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.projeto: Projeto | None = None
        self.acoes: HistoricoAcoes | None = None
        self.previas: GerenciadorPrevias | None = None

        self.indice_folha = 0
        self.indice_pagina = 0

        self._abas_ativas: list[str] = []
        self._carregando = False

        # Referencias diretas em Python, uma por aba. A versao anterior
        # guardava o widget dentro de setProperty() e o buscava de volta a cada
        # clique; isso devolve um ponteiro que o Python nao mantem vivo e e uma
        # fonte classica de fechamento sem aviso no PySide6.
        self.visualizadores: dict[str, Visualizador] = {}
        self.paginas_de_imagem: dict[str, QWidget] = {}
        self.linhas_de_botoes: dict[str, QWidget] = {}
        self.botoes_de_sugestao: dict[str, QPushButton] = {}
        self.cartoes: dict[str, CartaoFiltro] = {}
        self.botoes_forca: dict[str, QPushButton] = {}

        self._montar()

    # ------------------------------------------------------------------
    # montagem
    # ------------------------------------------------------------------

    def _montar(self) -> None:
        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(20, 10, 20, 8)
        camadas.setSpacing(6)

        camadas.addLayout(self._montar_cabecalho())          # 1

        self.barra_abas = QTabBar()
        self.barra_abas.setExpanding(False)
        self.barra_abas.currentChanged.connect(self._trocou_de_aba)
        camadas.addWidget(self.barra_abas)                   # 2

        # 3 - area da imagem: e a unica linha com stretch, entao fica com todo
        # o espaco que sobrar depois que as outras pegam o minimo delas
        self.area_imagem = QStackedWidget()
        self.area_imagem.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Minimo pequeno para que a soma de todas as linhas caiba na janela
        # minima de 1000x680. Abaixo disso o Qt sobreporia as faixas.
        self.area_imagem.setMinimumHeight(130)
        camadas.addWidget(self.area_imagem, 1)

        self.faixa = QFrame()                                # 4
        self.faixa.setObjectName("faixaInfo")
        self.faixa.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        faixa_camadas = QHBoxLayout(self.faixa)
        faixa_camadas.setContentsMargins(14, 9, 14, 9)
        self.texto_faixa = QLabel("")
        self.texto_faixa.setWordWrap(True)
        faixa_camadas.addWidget(self.texto_faixa, 1)
        camadas.addWidget(self.faixa)

        self.barra_botoes = QStackedWidget()                 # 5
        self.barra_botoes.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        camadas.addWidget(self.barra_botoes)

        self.tira = TiraMiniaturas("Folhas")                 # 6
        self.tira.selecionada.connect(self._escolher_da_tira)
        camadas.addWidget(self.tira)

        # Onde salvar fica AQUI, antes de processar: assim o usuario decide o
        # destino sem esperar o livro inteiro para so entao descobrir o lugar.
        self.destino = SeletorDestino()                      # 7
        camadas.addWidget(self.destino)

        camadas.addLayout(self._montar_rodape())             # 8

    def _montar_cabecalho(self) -> QHBoxLayout:
        topo = QHBoxLayout()
        titulo = QLabel("Confira antes de processar")
        titulo.setObjectName("secao")
        topo.addWidget(titulo)
        topo.addStretch()

        self.botao_alertas = QPushButton("tudo certo")
        self.botao_alertas.setObjectName("contadorAlerta")
        _ligar(self.botao_alertas, self._ir_para_proximo_alerta)
        topo.addWidget(self.botao_alertas)

        self.botao_desfazer = QPushButton("Desfazer")
        _ligar(self.botao_desfazer, self.desfazer)
        topo.addWidget(self.botao_desfazer)

        self.botao_refazer = QPushButton("Refazer")
        _ligar(self.botao_refazer, self.refazer)
        topo.addWidget(self.botao_refazer)
        return topo

    def _montar_rodape(self) -> QVBoxLayout:
        fora = QVBoxLayout()
        fora.setSpacing(4)

        atalhos = QLabel(
            "setas: mudar de página   -   Espaço: está certo   -   Tab: próxima dúvida   "
            "-   1 2 3 4: filtros   -   Delete: apagar   -   Ctrl+Z: desfazer"
        )
        atalhos.setObjectName("atalhos")
        atalhos.setAlignment(Qt.AlignCenter)
        fora.addWidget(atalhos)

        linha = QHBoxLayout()
        botao_voltar = QPushButton("voltar")
        _ligar(botao_voltar, self.voltar.emit)
        linha.addWidget(botao_voltar)
        linha.addStretch()

        self.botao_processar = QPushButton("Confirmar e processar")
        self.botao_processar.setObjectName("primario")
        _ligar(self.botao_processar, self._pedir_processamento)
        linha.addWidget(self.botao_processar)
        fora.addLayout(linha)
        return fora

    # --- paginas de imagem e linhas de botoes -----------------------------

    def _area_de_visualizador(self, aba: str, modo: str) -> Visualizador:
        """Uma página da área de imagem: setas nas laterais e a prévia no meio."""
        pagina = QWidget()
        linha = QHBoxLayout(pagina)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(6)

        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        visualizador = Visualizador()
        visualizador.definir_modo(modo)
        visualizador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        linha.addWidget(visualizador, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)

        self.visualizadores[aba] = visualizador
        self.paginas_de_imagem[aba] = pagina
        return visualizador

    def _linha_de_botoes(self, aba: str) -> QHBoxLayout:
        widget = QWidget()
        linha = QHBoxLayout(widget)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(8)
        self.linhas_de_botoes[aba] = widget
        return linha

    def _montar_aba_corte(self) -> None:
        vis = self._area_de_visualizador(ABA_CORTE, MODO_CORTE)
        vis.corte_movido.connect(self._mover_corte)

        linha = self._linha_de_botoes(ABA_CORTE)
        _botao("está certo", linha, self._marcar_revisada)
        self.botao_nao_dividir = _botao("não dividir esta", linha, self._alternar_dividir)
        _botao("girar", linha, self._girar)
        _botao("usar em todas", linha, self._corte_em_todas)
        linha.addStretch()
        self.botoes_de_sugestao[ABA_CORTE] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _montar_aba_bordas(self) -> None:
        vis = self._area_de_visualizador(ABA_BORDAS, MODO_RECORTE)
        vis.recorte_movido.connect(self._mover_recorte)

        linha = self._linha_de_botoes(ABA_BORDAS)
        _botao("está certo", linha, self._marcar_revisada)
        _botao("não cortar esta", linha, self._sem_recorte)
        _botao("voltar ao automático", linha, self._recorte_automatico)
        _botao("usar em todas", linha, self._recorte_em_todas)
        linha.addStretch()
        self.botoes_de_sugestao[ABA_BORDAS] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _montar_aba_angulo(self) -> None:
        vis = self._area_de_visualizador(ABA_ANGULO, MODO_ANGULO)
        vis.angulo_movido.connect(self._mover_angulo)

        linha = self._linha_de_botoes(ABA_ANGULO)
        _botao("está certo", linha, self._marcar_revisada)
        _botao("não endireitar esta", linha, self._angulo_zero)
        _botao("voltar ao automático", linha, self._angulo_automatico)
        linha.addStretch()
        self.botoes_de_sugestao[ABA_ANGULO] = _botao(
            "", linha, self._aplicar_sugestao, "sugestao"
        )

    def _montar_aba_filtro(self) -> None:
        pagina = QWidget()
        camadas = QVBoxLayout(pagina)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(6)

        explicacao = QLabel("A mesma página nos quatro filtros - clique no que preferir")
        explicacao.setObjectName("fraco")
        camadas.addWidget(explicacao)

        linha = QHBoxLayout()
        linha.setSpacing(6)
        anterior = QPushButton("<")
        anterior.setFixedWidth(40)
        _ligar(anterior, lambda: self._navegar(-1))
        linha.addWidget(anterior)

        for chave, nome, explica in CARTOES:
            cartao = CartaoFiltro(chave, nome, explica)
            cartao.escolhido.connect(self._escolher_filtro)
            self.cartoes[chave] = cartao
            linha.addWidget(cartao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(40)
        _ligar(proxima, lambda: self._navegar(1))
        linha.addWidget(proxima)
        camadas.addLayout(linha, 1)

        self.paginas_de_imagem[ABA_FILTRO] = pagina

        linha_botoes = self._linha_de_botoes(ABA_FILTRO)
        self.painel_forca = QWidget()
        forca_linha = QHBoxLayout(self.painel_forca)
        forca_linha.setContentsMargins(0, 0, 0, 0)
        forca_linha.setSpacing(6)
        forca_linha.addWidget(QLabel("Força do preto:"))
        for chave in FORCAS:
            botao = QPushButton(ROTULOS_FORCA[chave])
            botao.setCheckable(True)
            _ligar(botao, functools.partial(self._escolher_forca, chave))
            self.botoes_forca[chave] = botao
            forca_linha.addWidget(botao)
        linha_botoes.addWidget(self.painel_forca)

        _botao("só nesta", linha_botoes, self._marcar_revisada)
        _botao("usar em todas", linha_botoes, self._filtro_em_todas)
        _botao("só nas próximas", linha_botoes, self._filtro_nas_proximas)
        self.botao_apagar = _botao("apagar página", linha_botoes, self.apagar_pagina)
        linha_botoes.addStretch()
        self.botoes_de_sugestao[ABA_FILTRO] = _botao(
            "", linha_botoes, self._aplicar_sugestao, "sugestao"
        )

    # ------------------------------------------------------------------
    # carga
    # ------------------------------------------------------------------

    def carregar(self, projeto: Projeto, acoes: HistoricoAcoes,
                 previas: GerenciadorPrevias) -> None:
        self._carregando = True
        try:
            self.projeto = projeto
            self.acoes = acoes
            self.previas = previas
            self.previas.pronta.connect(self._previa_chegou)

            self.indice_folha = 0
            self.indice_pagina = 0

            self._limpar_abas()

            if projeto.dividir_folhas:
                self._montar_aba_corte()
                self._abas_ativas.append(ABA_CORTE)
            if projeto.cortar_bordas:
                self._montar_aba_bordas()
                self._abas_ativas.append(ABA_BORDAS)
            if projeto.endireitar:
                self._montar_aba_angulo()
                self._abas_ativas.append(ABA_ANGULO)
            if projeto.limpar or not self._abas_ativas:
                self._montar_aba_filtro()
                self._abas_ativas.append(ABA_FILTRO)

            for aba in self._abas_ativas:
                self.barra_abas.addTab(TITULOS[aba])
                self.area_imagem.addWidget(self.paginas_de_imagem[aba])
                self.barra_botoes.addWidget(self.linhas_de_botoes[aba])

            from modelos import nome_de_saida_sugerido

            self.destino.definir(None, nome_de_saida_sugerido(projeto))
            self.barra_abas.setCurrentIndex(0)
        finally:
            self._carregando = False

        self._montar_tira()
        self.atualizar()

    def _limpar_abas(self) -> None:
        """Descarta as abas de um projeto anterior antes de montar as novas."""
        while self.barra_abas.count():
            self.barra_abas.removeTab(0)
        for pilha in (self.area_imagem, self.barra_botoes):
            while pilha.count():
                widget = pilha.widget(0)
                pilha.removeWidget(widget)
                widget.deleteLater()

        self._abas_ativas.clear()
        self.visualizadores.clear()
        self.paginas_de_imagem.clear()
        self.linhas_de_botoes.clear()
        self.botoes_de_sugestao.clear()
        self.cartoes.clear()
        self.botoes_forca.clear()

    def _montar_tira(self) -> None:
        if self.projeto is None:
            return
        if self.aba_atual == ABA_CORTE:
            self.tira.definir_titulo("Folhas - as laranjas eu não tive certeza")
            self.tira.montar(
                len(self.projeto.folhas), self.projeto.caminho_entrada,
                {i: i for i in range(len(self.projeto.folhas))},
            )
        else:
            self.tira.definir_titulo("Páginas - as laranjas eu não tive certeza")
            self.tira.montar(
                len(self.projeto.paginas), self.projeto.caminho_entrada,
                {p.indice: p.folha for p in self.projeto.paginas},
                {
                    p.indice: (p.metade, self.projeto.folhas[p.folha].posicao_corte)
                    for p in self.projeto.paginas
                },
            )

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------

    @property
    def aba_atual(self) -> str:
        indice = self.barra_abas.currentIndex()
        if 0 <= indice < len(self._abas_ativas):
            return self._abas_ativas[indice]
        return self._abas_ativas[0] if self._abas_ativas else ABA_FILTRO

    @property
    def trabalha_com_folhas(self) -> bool:
        return self.aba_atual == ABA_CORTE

    @property
    def item_atual(self):
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            return self.projeto.folhas[self.indice_folha]
        return self.projeto.paginas[self.indice_pagina]

    @property
    def indice_atual(self) -> int:
        return self.indice_folha if self.trabalha_com_folhas else self.indice_pagina

    def _total(self) -> int:
        assert self.projeto is not None
        return (len(self.projeto.folhas) if self.trabalha_com_folhas
                else len(self.projeto.paginas))

    def _pronta(self) -> bool:
        return (self.projeto is not None and self.previas is not None
                and bool(self._abas_ativas) and not self._carregando)

    # ------------------------------------------------------------------
    # navegacao
    # ------------------------------------------------------------------

    @protegido
    def _navegar(self, passo: int) -> None:
        if not self._pronta():
            return
        self._ir_para(max(0, min(self._total() - 1, self.indice_atual + passo)))

    def _ir_para(self, indice: int) -> None:
        assert self.projeto is not None
        if self.trabalha_com_folhas:
            self.indice_folha = indice
            for pagina in self.projeto.paginas:
                if pagina.folha == indice:
                    self.indice_pagina = pagina.indice
                    break
        else:
            self.indice_pagina = indice
            self.indice_folha = self.projeto.paginas[indice].folha
        self.atualizar()

    @protegido
    def _escolher_da_tira(self, indice: int) -> None:
        if self._pronta():
            self._ir_para(indice)

    @protegido
    def _trocou_de_aba(self, _indice: int) -> None:
        if not self._pronta():
            return
        self.area_imagem.setCurrentIndex(self.barra_abas.currentIndex())
        self.barra_botoes.setCurrentIndex(self.barra_abas.currentIndex())
        self._montar_tira()
        self.atualizar()

    @protegido
    def _ir_para_proximo_alerta(self) -> None:
        if not self._pronta():
            return
        assert self.projeto is not None
        total = self._total()
        itens = (self.projeto.folhas if self.trabalha_com_folhas
                 else self.projeto.paginas)
        for salto in range(1, total + 1):
            indice = (self.indice_atual + salto) % total
            if itens[indice].precisa_revisao:
                self._ir_para(indice)
                return

    # ------------------------------------------------------------------
    # desenho
    # ------------------------------------------------------------------

    @protegido
    def atualizar(self) -> None:
        if not self._pronta():
            return
        self._atualizar_previa()
        self._atualizar_faixa()
        self._atualizar_botoes()
        self._atualizar_tira()
        self._atualizar_contador()

    def _atualizar_previa(self) -> None:
        assert self.previas is not None and self.projeto is not None
        aba = self.aba_atual

        if aba == ABA_CORTE:
            img = self.previas.pegar_folha(self.indice_folha, DPI_PREVIA)
            vis = self.visualizadores[ABA_CORTE]
            vis.definir_imagem(img)
            vis.definir_corte(self.projeto.folhas[self.indice_folha].posicao_corte)
            self.previas.pre_carregar_folhas(self.indice_folha, DPI_PREVIA)
            return

        img = self.previas.pegar(self.indice_pagina, DPI_PREVIA)
        self.previas.pre_carregar(self.indice_pagina, DPI_PREVIA)
        pagina = self.projeto.paginas[self.indice_pagina]

        if aba == ABA_BORDAS:
            vis = self.visualizadores[ABA_BORDAS]
            vis.definir_imagem(img)
            vis.definir_recorte(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
        elif aba == ABA_ANGULO:
            vis = self.visualizadores[ABA_ANGULO]
            vis.definir_imagem(img)
            vis.definir_angulo(pagina.angulo_manual or 0.0)
        else:
            self._atualizar_cartoes(img)

    def _atualizar_cartoes(self, img: np.ndarray | None) -> None:
        """Os quatro cartoes mostram a página de verdade, cada um com seu filtro."""
        from core.filtros import aplicar_filtro
        from core.pdf_io import limitar_altura

        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]

        for chave, cartao in self.cartoes.items():
            cartao.definir_selecionado(chave == pagina.filtro)

        if img is None:
            for cartao in self.cartoes.values():
                cartao.definir_amostra(None)
            return

        base = self._imagem_sem_filtro()
        for chave, cartao in self.cartoes.items():
            if chave == pagina.filtro:
                cartao.definir_amostra(limitar_altura(img, 260))
            elif base is not None:
                amostra, _ = aplicar_filtro(base, chave, pagina.forca_preto)
                cartao.definir_amostra(amostra)
            else:
                cartao.definir_amostra(None)

    def _imagem_sem_filtro(self) -> np.ndarray | None:
        """Versao pequena e sem filtro da página atual, para os outros cartoes."""
        assert self.projeto is not None and self.previas is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        img_folha = self.previas.pegar_folha(pagina.folha, 70)
        if img_folha is None:
            return None

        from core.pipeline import preparar_metade

        folha = self.projeto.folhas[pagina.folha]
        try:
            return preparar_metade(img_folha, folha, pagina, self.projeto)
        except Exception:  # noqa: BLE001 - amostra que falha nao derruba a tela
            registrar_erro("amostra_de_filtro", traceback.format_exc())
            return None

    def _atualizar_faixa(self) -> None:
        item = self.item_atual
        aba = self.aba_atual
        alerta = analise.descrever(item.alertas[0]) if item.alertas else None

        if alerta is not None and not item.revisada:
            self.texto_faixa.setText(alerta.mensagem)
            self._pintar_faixa(alerta=True)
            self._mostrar_sugestao(aba, alerta.acao)
        else:
            self.texto_faixa.setText(self._texto_tranquilo(aba))
            self._pintar_faixa(alerta=False)
            self._mostrar_sugestao(aba, None)

    def _texto_tranquilo(self, aba: str) -> str:
        assert self.projeto is not None
        if aba == ABA_CORTE:
            folha = self.projeto.folhas[self.indice_folha]
            if not folha.dividir:
                return "Esta folha não vai ser dividida."
            return ("Achei a lombada e vou cortar na linha azul. "
                    "Se estiver errado, arraste a linha.")
        if aba == ABA_BORDAS:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.recorte is None:
                return "Vou cortar a borda sozinho. Arraste o retangulo se quiser mudar."
            return "Você ajustou o corte desta página."
        if aba == ABA_ANGULO:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.angulo_manual is None:
                return "Vou endireitar sozinho. Arraste sobre a página para girar na mao."
            return f"Você girou esta página em {pagina.angulo_manual:+.1f} graus."
        pagina = self.projeto.paginas[self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        return f"Esta página vai sair em {nome}."

    def _pintar_faixa(self, alerta: bool) -> None:
        """Troca a cor da faixa.

        A folha de estilo e aplicada direto no widget, sem buscar ninguem por
        propriedade do Qt e sem repolir a arvore inteira.
        """
        borda = LARANJA if alerta else AZUL
        fundo = LARANJA_CLARO if alerta else AZUL_CLARO
        self.faixa.setStyleSheet(
            f"QFrame {{ background: {fundo}; border: 1px solid {borda};"
            f" border-radius: 8px; }}"
        )

    def _mostrar_sugestao(self, aba: str, rotulo: str | None) -> None:
        botao = self.botoes_de_sugestao.get(aba)
        if botao is None:
            return
        botao.setVisible(bool(rotulo))
        if rotulo:
            botao.setText(rotulo)

    def _atualizar_botoes(self) -> None:
        assert self.projeto is not None and self.acoes is not None

        self.botao_desfazer.setEnabled(self.acoes.pode_desfazer)
        self.botao_desfazer.setToolTip(self.acoes.descricao_desfazer())
        self.botao_refazer.setEnabled(self.acoes.pode_refazer)
        self.botao_refazer.setToolTip(self.acoes.descricao_refazer())

        if ABA_CORTE in self._abas_ativas:
            folha = self.projeto.folhas[self.indice_folha]
            self.botao_nao_dividir.setText(
                "dividir esta" if not folha.dividir else "não dividir esta"
            )

        if ABA_FILTRO in self._abas_ativas:
            pagina = self.projeto.paginas[self.indice_pagina]
            self.painel_forca.setVisible(pagina.filtro == PRETO_E_BRANCO)
            for chave, botao in self.botoes_forca.items():
                botao.setChecked(chave == pagina.forca_preto)
            self.botao_apagar.setText(
                "restaurar página" if pagina.apagada else "apagar página"
            )

    def _atualizar_tira(self) -> None:
        assert self.projeto is not None
        itens = (self.projeto.folhas if self.trabalha_com_folhas
                 else self.projeto.paginas)
        for i, item in enumerate(itens):
            self.tira.marcar(i, em_alerta=item.precisa_revisao,
                             apagada=getattr(item, "apagada", False))
        self.tira.selecionar(self.indice_atual)

    def _atualizar_contador(self) -> None:
        assert self.projeto is not None
        pendentes = self.projeto.pendentes_de_revisao()
        apagadas = self.projeto.total_apagadas

        if pendentes == 0:
            texto = "tudo certo"
        elif pendentes == 1:
            texto = "1 página para você olhar"
        else:
            texto = f"{pendentes} páginas para você olhar"
        if apagadas:
            texto += f"  -  {apagadas} apagadas"
        self.botao_alertas.setText(texto)
        self.botao_alertas.setEnabled(pendentes > 0)

    @protegido
    def _previa_chegou(self, chave: str, _img: np.ndarray) -> None:
        """Uma prévia ficou pronta; se for a que estamos vendo, redesenha."""
        if not self._pronta():
            return
        assert self.previas is not None
        esperadas = (
            self.previas.chave(self.indice_pagina, DPI_PREVIA),
            self.previas.chave_folha(self.indice_folha, DPI_PREVIA),
        )
        if chave in esperadas or chave.startswith("folha:"):
            self._atualizar_previa()

    # ------------------------------------------------------------------
    # alteracoes (todas passam pelo historico)
    # ------------------------------------------------------------------

    def _registrar(self, tipo: str, alvo: str, indices: list[int],
                   campos: dict, descricao: str) -> None:
        """Aplica a mudanca e guarda no histórico, numa acao só."""
        assert self.projeto is not None and self.acoes is not None
        acao = montar_acao(self.projeto, tipo, alvo, indices, campos, descricao)
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)

        afetadas = indices if alvo == "pagina" else self._paginas_das_folhas(indices)
        if self.previas is not None:
            for indice in afetadas:
                self.previas.invalidar(indice)
        self.atualizar()

    def _paginas_das_folhas(self, folhas: list[int]) -> list[int]:
        assert self.projeto is not None
        alvo = set(folhas)
        return [p.indice for p in self.projeto.paginas if p.folha in alvo]

    # --- corte ------------------------------------------------------------

    @protegido
    def _mover_corte(self, posicao: float) -> None:
        self._registrar(
            "mover_corte", "folha", [self.indice_folha],
            {"posicao_corte": round(posicao, 4), "revisada": True},
            f"Linha de corte da folha {self.indice_folha + 1}",
        )

    @protegido
    def _corte_em_todas(self) -> None:
        assert self.projeto is not None
        posicao = self.projeto.folhas[self.indice_folha].posicao_corte
        indices = [f.indice for f in self.projeto.folhas]
        self._registrar(
            "aplicar_em_todas", "folha", indices,
            {"posicao_corte": round(posicao, 4)},
            f"Linha de corte de todas as {len(indices)} folhas",
        )

    @protegido
    def _alternar_dividir(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "nao_dividir", "folha", [self.indice_folha],
            {"dividir": not folha.dividir, "revisada": True},
            f"Folha {self.indice_folha + 1}: "
            + ("dividir" if not folha.dividir else "não dividir"),
        )

    @protegido
    def _girar(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "girar", "folha", [self.indice_folha],
            {"rotacao": (folha.rotacao + 90) % 360},
            f"Girar a folha {self.indice_folha + 1}",
        )

    # --- bordas -----------------------------------------------------------

    @protegido
    def _mover_recorte(self, recorte: tuple) -> None:
        arredondado = [round(float(v), 4) for v in recorte]
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": arredondado, "revisada": True},
            f"Corte de borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _sem_recorte(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": [0.0, 0.0, 1.0, 1.0], "revisada": True},
            f"Não cortar a borda da página {self.indice_pagina + 1}",
        )

    @protegido
    def _recorte_automatico(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina], {"recorte": None},
            f"Voltar ao corte automático na página {self.indice_pagina + 1}",
        )

    @protegido
    def _recorte_em_todas(self) -> None:
        assert self.projeto is not None
        recorte = self.projeto.paginas[self.indice_pagina].recorte
        indices = [p.indice for p in self.projeto.paginas]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"recorte": list(recorte) if recorte else None},
            f"Corte de borda de todas as {len(indices)} páginas",
        )

    # --- angulo -----------------------------------------------------------

    @protegido
    def _mover_angulo(self, angulo: float) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": round(angulo, 2), "revisada": True},
            f"Angulo da página {self.indice_pagina + 1}: {angulo:+.1f} graus",
        )

    @protegido
    def _angulo_zero(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": 0.0, "revisada": True},
            f"Não endireitar a página {self.indice_pagina + 1}",
        )

    @protegido
    def _angulo_automatico(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina], {"angulo_manual": None},
            f"Voltar ao endireitar automático na página {self.indice_pagina + 1}",
        )

    # --- filtro -----------------------------------------------------------

    @protegido
    def _escolher_filtro(self, filtro: str) -> None:
        assert self.projeto is not None
        atual = self.projeto.paginas[self.indice_pagina].filtro
        nome_antes = NOMES_AMIGAVEIS.get(atual, atual)
        nome_depois = NOMES_AMIGAVEIS.get(filtro, filtro)
        self._registrar(
            "mudar_filtro", "pagina", [self.indice_pagina],
            {"filtro": filtro, "revisada": True},
            f"Filtro da página {self.indice_pagina + 1}: {nome_antes} para {nome_depois}",
        )

    @protegido
    def _escolher_forca(self, forca: str) -> None:
        self._registrar(
            "forca_preto", "pagina", [self.indice_pagina],
            {"forca_preto": forca, "revisada": True},
            f"Força do preto da página {self.indice_pagina + 1}: {ROTULOS_FORCA[forca]}",
        )

    @protegido
    def _filtro_em_todas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto},
            f"{nome} em todas as {len(indices)} páginas",
        )

    @protegido
    def _filtro_nas_proximas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto},
            f"{nome} da página {self.indice_pagina + 1} em diante ({len(indices)} páginas)",
        )

    # --- gerais -----------------------------------------------------------

    @protegido
    def apagar_pagina(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        acao = "restaurar" if pagina.apagada else "apagar"
        self._registrar(
            acao, "pagina", [self.indice_pagina],
            {"apagada": not pagina.apagada, "revisada": True},
            f"{acao.capitalize()} a página {self.indice_pagina + 1}",
        )

    @protegido
    def _marcar_revisada(self) -> None:
        alvo = "folha" if self.trabalha_com_folhas else "pagina"
        self._registrar(
            "revisar", alvo, [self.indice_atual], {"revisada": True},
            f"Conferir a {alvo} {self.indice_atual + 1}",
        )

    @protegido
    def marcar_certo_e_avancar(self) -> None:
        """Barra de espaço: aprova e já pula para a próxima."""
        self._marcar_revisada()
        self._navegar(1)

    @protegido
    def _aplicar_sugestao(self) -> None:
        """O botão laranja do alerta: aplica a correcao mais provavel.

        E só um atalho. Todos os controles manuais continuam valendo.
        """
        item = self.item_atual
        if not item.alertas:
            return
        correcao = analise.descrever(item.alertas[0]).correcao
        if correcao is None or correcao == "revisar":
            self._marcar_revisada()
        elif correcao.startswith("filtro:"):
            self._escolher_filtro(correcao.split(":", 1)[1])
        elif correcao.startswith("forca:"):
            self._escolher_forca(correcao.split(":", 1)[1])
        elif correcao == "apagar":
            self.apagar_pagina()
        elif correcao == "nao_dividir":
            self._alternar_dividir()
        elif correcao == "angulo_zero":
            self._angulo_zero()
        elif correcao == "sem_recorte":
            self._sem_recorte()

    # --- desfazer / refazer -----------------------------------------------

    @protegido
    def desfazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.desfazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.atualizar()

    @protegido
    def refazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        if self.acoes.refazer(self.projeto) is not None:
            if self.previas is not None:
                self.previas.invalidar()
            self.atualizar()

    # --- teclado ----------------------------------------------------------

    def tratar_tecla(self, evento) -> bool:
        """Atalhos da secao 4.7. Devolve True se consumiu a tecla."""
        if not self._pronta():
            return False

        tecla = evento.key()
        ctrl = evento.modifiers() & Qt.ControlModifier
        shift = evento.modifiers() & Qt.ShiftModifier

        if ctrl and tecla == Qt.Key_Z:
            self.refazer() if shift else self.desfazer()
            return True
        if ctrl and tecla == Qt.Key_Y:
            self.refazer()
            return True
        if ctrl and tecla in (Qt.Key_Return, Qt.Key_Enter):
            self._pedir_processamento()
            return True

        if tecla == Qt.Key_Left:
            self._navegar(-1)
            return True
        if tecla == Qt.Key_Right:
            self._navegar(1)
            return True
        if tecla == Qt.Key_Space:
            self.marcar_certo_e_avancar()
            return True
        if tecla == Qt.Key_Tab:
            self._ir_para_proximo_alerta()
            return True
        if tecla == Qt.Key_Delete:
            if not self.trabalha_com_folhas:
                self.apagar_pagina()
            return True
        if tecla == Qt.Key_R and ABA_CORTE in self._abas_ativas:
            self._girar()
            return True

        atalhos_de_filtro = {
            Qt.Key_1: ORIGINAL, Qt.Key_2: PRETO_E_BRANCO,
            Qt.Key_3: MELHORAR, Qt.Key_4: MAGICO_PRO,
        }
        if tecla in atalhos_de_filtro and not self.trabalha_com_folhas:
            self._escolher_filtro(atalhos_de_filtro[tecla])
            return True

        return False

    # --- saida ------------------------------------------------------------

    def _avisar_problema(self) -> None:
        """O que o usuario ve quando algo deu errado por baixo dos panos."""
        caixa = QMessageBox(self)
        caixa.setWindowTitle("Um momento")
        caixa.setIcon(QMessageBox.Information)
        caixa.setText("Não consegui fazer isso agora.")
        caixa.setInformativeText(
            "O programa continua funcionando e o seu trabalho está salvo. "
            "Tente de novo, ou passe para a próxima página."
        )
        caixa.addButton("entendi", QMessageBox.AcceptRole)
        caixa.exec()

    @protegido
    def _pedir_processamento(self) -> None:
        """Avisa se ainda ha dúvidas, mas nunca bloqueia."""
        if self.projeto is None:
            return
        pendentes = self.projeto.pendentes_de_revisao()
        if pendentes > 0:
            caixa = QMessageBox(self)
            caixa.setWindowTitle("Antes de processar")
            caixa.setIcon(QMessageBox.Question)
            caixa.setText(
                f"Ainda tem {pendentes} "
                + ("página que eu não tive certeza." if pendentes == 1
                   else "páginas que eu não tive certeza.")
            )
            caixa.setInformativeText("Quer conferir antes ou processar assim mesmo?")
            conferir = caixa.addButton("conferir", QMessageBox.RejectRole)
            caixa.addButton("processar assim mesmo", QMessageBox.AcceptRole)
            caixa.exec()
            if caixa.clickedButton() is conferir:
                self._ir_para_proximo_alerta()
                return
        self.processar.emit()


def _ligar(botao: QPushButton, acao) -> None:
    """Liga o clique ignorando o argumento 'checked' que o Qt manda junto."""
    botao.clicked.connect(lambda *_: acao())


def _botao(texto: str, destino: QHBoxLayout, acao, objeto: str = "") -> QPushButton:
    botao = QPushButton(texto)
    if objeto:
        botao.setObjectName(objeto)
    _ligar(botao, acao)
    destino.addWidget(botao)
    return botao
