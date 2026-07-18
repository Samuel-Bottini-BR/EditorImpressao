"""TELA 3 - Conferir: a previa e todos os ajustes manuais.

As abas aparecem conforme o que foi marcado na tela 2. Cada aba edita uma
unidade diferente:

    Onde cortar -> FOLHA do PDF de entrada (a linha da lombada)
    Bordas      -> PAGINA de saida (o retangulo do recorte)
    Endireitar  -> PAGINA de saida (o angulo)
    Filtro      -> PAGINA de saida (o filtro e a forca do preto)

O alerta chama atencao, nunca restringe: todo controle continua disponivel em
qualquer pagina, com ou sem alerta.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTabWidget,
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
from ui.estilo import LARANJA, TEXTO_FRACO
from ui.tarefas import GerenciadorPrevias
from ui.widgets.cartao_filtro import CartaoFiltro
from ui.widgets.tira_miniaturas import TiraMiniaturas
from ui.widgets.visualizador import (
    MODO_ANGULO,
    MODO_CORTE,
    MODO_NENHUM,
    MODO_RECORTE,
    Visualizador,
)

DPI_PREVIA = 110          # baixo de proposito: a tela precisa abrir em segundos
ALTURA_MAXIMA_PREVIA = 900

ABA_CORTE, ABA_BORDAS, ABA_ANGULO, ABA_FILTRO = "corte", "bordas", "angulo", "filtro"

ROTULOS_FORCA = {
    "mais_fraco": "mais fraco",
    "normal": "normal",
    "mais_escuro": "mais escuro",
}

CARTOES = [
    (ORIGINAL, "Original", "sem mexer"),
    (PRETO_E_BRANCO, "Preto e branco", "tira o amarelado"),
    (MELHORAR, "Melhorar", "mantem a cor"),
    (MAGICO_PRO, "Magico pro", "cor viva"),
]


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

        self._montar()

    # ------------------------------------------------------------------
    # montagem
    # ------------------------------------------------------------------

    def _montar(self) -> None:
        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(28, 18, 28, 14)
        camadas.setSpacing(10)

        topo = QHBoxLayout()
        titulo = QLabel("Confira antes de processar")
        titulo.setObjectName("secao")
        topo.addWidget(titulo)
        topo.addStretch()

        self.botao_alertas = QPushButton("tudo certo")
        self.botao_alertas.setObjectName("contadorAlerta")
        self.botao_alertas.clicked.connect(self._ir_para_proximo_alerta)
        topo.addWidget(self.botao_alertas)

        self.botao_desfazer = QPushButton("Desfazer")
        self.botao_desfazer.clicked.connect(self.desfazer)
        topo.addWidget(self.botao_desfazer)

        self.botao_refazer = QPushButton("Refazer")
        self.botao_refazer.clicked.connect(self.refazer)
        topo.addWidget(self.botao_refazer)
        camadas.addLayout(topo)

        self.abas = QTabWidget()
        self.abas.currentChanged.connect(self._trocou_de_aba)
        camadas.addWidget(self.abas, 1)

        self.tira = TiraMiniaturas("Folhas")
        self.tira.selecionada.connect(self._escolher_da_tira)
        camadas.addWidget(self.tira)

        rodape = QHBoxLayout()
        botao_voltar = QPushButton("voltar")
        botao_voltar.clicked.connect(self.voltar.emit)
        rodape.addWidget(botao_voltar)

        atalhos = QLabel(
            "setas: mudar de pagina   -   Espaco: esta certo   -   Tab: proxima duvida   "
            "-   1 2 3 4: filtros   -   Delete: apagar   -   Ctrl+Z: desfazer"
        )
        atalhos.setObjectName("atalhos")
        rodape.addWidget(atalhos, 1, Qt.AlignCenter)

        self.botao_processar = QPushButton("Confirmar e processar")
        self.botao_processar.setObjectName("primario")
        self.botao_processar.clicked.connect(self._pedir_processamento)
        rodape.addWidget(self.botao_processar)
        camadas.addLayout(rodape)

    def _pagina_com_visualizador(self, modo: str) -> tuple[QWidget, Visualizador, QLabel, QHBoxLayout]:
        """Molde comum das abas: navegacao, previa, faixa e botoes."""
        pagina = QWidget()
        camadas = QVBoxLayout(pagina)
        camadas.setContentsMargins(14, 12, 14, 12)
        camadas.setSpacing(9)

        linha = QHBoxLayout()
        anterior = QPushButton("<")
        anterior.setFixedWidth(44)
        anterior.clicked.connect(lambda: self._navegar(-1))
        linha.addWidget(anterior)

        visualizador = Visualizador()
        visualizador.definir_modo(modo)
        visualizador.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        linha.addWidget(visualizador, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(44)
        proxima.clicked.connect(lambda: self._navegar(1))
        linha.addWidget(proxima)
        camadas.addLayout(linha, 1)

        faixa = QFrame()
        faixa.setObjectName("faixaInfo")
        faixa_camadas = QHBoxLayout(faixa)
        faixa_camadas.setContentsMargins(14, 10, 14, 10)
        texto = QLabel("")
        texto.setWordWrap(True)
        faixa_camadas.addWidget(texto, 1)
        camadas.addWidget(faixa)
        faixa.setProperty("rotulo", texto)

        botoes = QHBoxLayout()
        camadas.addLayout(botoes)

        pagina.setProperty("faixa", faixa)
        return pagina, visualizador, texto, botoes

    # ------------------------------------------------------------------
    # carga
    # ------------------------------------------------------------------

    def carregar(self, projeto: Projeto, acoes: HistoricoAcoes,
                 previas: GerenciadorPrevias) -> None:
        self.projeto = projeto
        self.acoes = acoes
        self.previas = previas
        self.previas.pronta.connect(self._previa_chegou)

        self.indice_folha = 0
        self.indice_pagina = 0

        self.abas.clear()
        self._abas_ativas: list[str] = []

        if projeto.dividir_folhas:
            self._montar_aba_corte()
        if projeto.cortar_bordas:
            self._montar_aba_bordas()
        if projeto.endireitar:
            self._montar_aba_angulo()
        if projeto.limpar:
            self._montar_aba_filtro()
        if not self._abas_ativas:
            self._montar_aba_filtro()   # sempre ha ao menos uma para conferir

        self._montar_tira()
        self.atualizar()

    def _montar_tira(self) -> None:
        assert self.projeto is not None
        if self.aba_atual == ABA_CORTE:
            self.tira.definir_titulo("Folhas - as laranjas eu nao tive certeza")
            self.tira.montar(
                len(self.projeto.folhas), self.projeto.caminho_entrada,
                {i: i for i in range(len(self.projeto.folhas))},
            )
        else:
            self.tira.definir_titulo("Paginas - as laranjas eu nao tive certeza")
            self.tira.montar(
                len(self.projeto.paginas), self.projeto.caminho_entrada,
                {p.indice: p.folha for p in self.projeto.paginas},
                {
                    p.indice: (p.metade, self.projeto.folhas[p.folha].posicao_corte)
                    for p in self.projeto.paginas
                },
            )

    # --- abas -------------------------------------------------------------

    def _montar_aba_corte(self) -> None:
        pagina, vis, texto, botoes = self._pagina_com_visualizador(MODO_CORTE)
        self.vis_corte, self.texto_corte = vis, texto
        vis.corte_movido.connect(self._mover_corte)

        self.botao_ok_corte = _botao("esta certo", botoes, self._marcar_revisada)
        self.botao_nao_dividir = _botao("nao dividir esta", botoes, self._alternar_dividir)
        _botao("girar", botoes, self._girar)
        _botao("usar em todas", botoes, self._corte_em_todas)
        botoes.addStretch()
        self.botao_sugestao_corte = _botao("", botoes, self._aplicar_sugestao, "sugestao")

        self.abas.addTab(pagina, "Onde cortar")
        self._abas_ativas.append(ABA_CORTE)

    def _montar_aba_bordas(self) -> None:
        pagina, vis, texto, botoes = self._pagina_com_visualizador(MODO_RECORTE)
        self.vis_bordas, self.texto_bordas = vis, texto
        vis.recorte_movido.connect(self._mover_recorte)

        _botao("esta certo", botoes, self._marcar_revisada)
        _botao("nao cortar esta", botoes, self._sem_recorte)
        _botao("voltar ao automatico", botoes, self._recorte_automatico)
        _botao("usar em todas", botoes, self._recorte_em_todas)
        botoes.addStretch()
        self.botao_sugestao_bordas = _botao("", botoes, self._aplicar_sugestao, "sugestao")

        self.abas.addTab(pagina, "Bordas")
        self._abas_ativas.append(ABA_BORDAS)

    def _montar_aba_angulo(self) -> None:
        pagina, vis, texto, botoes = self._pagina_com_visualizador(MODO_ANGULO)
        self.vis_angulo, self.texto_angulo = vis, texto
        vis.angulo_movido.connect(self._mover_angulo)

        _botao("esta certo", botoes, self._marcar_revisada)
        _botao("nao endireitar esta", botoes, self._angulo_zero)
        _botao("voltar ao automatico", botoes, self._angulo_automatico)
        botoes.addStretch()
        self.botao_sugestao_angulo = _botao("", botoes, self._aplicar_sugestao, "sugestao")

        self.abas.addTab(pagina, "Endireitar")
        self._abas_ativas.append(ABA_ANGULO)

    def _montar_aba_filtro(self) -> None:
        pagina = QWidget()
        camadas = QVBoxLayout(pagina)
        camadas.setContentsMargins(14, 12, 14, 12)
        camadas.setSpacing(9)

        explicacao = QLabel("A mesma pagina nos quatro filtros - clique no que preferir")
        explicacao.setObjectName("fraco")
        camadas.addWidget(explicacao)

        linha = QHBoxLayout()
        anterior = QPushButton("<")
        anterior.setFixedWidth(44)
        anterior.clicked.connect(lambda: self._navegar(-1))
        linha.addWidget(anterior)

        self.cartoes: dict[str, CartaoFiltro] = {}
        for chave, nome, explica in CARTOES:
            cartao = CartaoFiltro(chave, nome, explica)
            cartao.escolhido.connect(self._escolher_filtro)
            self.cartoes[chave] = cartao
            linha.addWidget(cartao, 1)

        proxima = QPushButton(">")
        proxima.setFixedWidth(44)
        proxima.clicked.connect(lambda: self._navegar(1))
        linha.addWidget(proxima)
        camadas.addLayout(linha, 1)

        self.painel_forca = QWidget()
        forca_linha = QHBoxLayout(self.painel_forca)
        forca_linha.setContentsMargins(0, 0, 0, 0)
        forca_linha.addWidget(QLabel("Forca do preto:"))
        self.grupo_forca = QButtonGroup(self)
        self.botoes_forca: dict[str, QPushButton] = {}
        for chave in FORCAS:
            botao = QPushButton(ROTULOS_FORCA[chave])
            botao.setCheckable(True)
            botao.clicked.connect(lambda _=False, c=chave: self._escolher_forca(c))
            self.grupo_forca.addButton(botao)
            self.botoes_forca[chave] = botao
            forca_linha.addWidget(botao)
        forca_linha.addStretch()
        camadas.addWidget(self.painel_forca)

        faixa = QFrame()
        faixa.setObjectName("faixaInfo")
        faixa_camadas = QHBoxLayout(faixa)
        faixa_camadas.setContentsMargins(14, 10, 14, 10)
        self.texto_filtro = QLabel("")
        self.texto_filtro.setWordWrap(True)
        faixa_camadas.addWidget(self.texto_filtro, 1)
        camadas.addWidget(faixa)
        pagina.setProperty("faixa", faixa)
        self.faixa_filtro = faixa

        botoes = QHBoxLayout()
        _botao("so nesta", botoes, self._marcar_revisada)
        _botao("usar em todas", botoes, self._filtro_em_todas)
        _botao("so nas proximas", botoes, self._filtro_nas_proximas)
        self.botao_apagar = _botao("apagar pagina", botoes, self.apagar_pagina)
        botoes.addStretch()
        self.botao_sugestao_filtro = _botao("", botoes, self._aplicar_sugestao, "sugestao")
        camadas.addLayout(botoes)

        self.abas.addTab(pagina, "Filtro")
        self._abas_ativas.append(ABA_FILTRO)

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------

    @property
    def aba_atual(self) -> str:
        indice = self.abas.currentIndex()
        abas = getattr(self, "_abas_ativas", [])
        return abas[indice] if 0 <= indice < len(abas) else ABA_FILTRO

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

    # ------------------------------------------------------------------
    # navegacao
    # ------------------------------------------------------------------

    def _navegar(self, passo: int) -> None:
        novo = max(0, min(self._total() - 1, self.indice_atual + passo))
        self._ir_para(novo)

    def _ir_para(self, indice: int) -> None:
        if self.trabalha_com_folhas:
            self.indice_folha = indice
            # mantem a aba de filtro por perto da mesma folha
            for pagina in self.projeto.paginas:  # type: ignore[union-attr]
                if pagina.folha == indice:
                    self.indice_pagina = pagina.indice
                    break
        else:
            self.indice_pagina = indice
            self.indice_folha = self.projeto.paginas[indice].folha  # type: ignore[union-attr]
        self.atualizar()

    def _escolher_da_tira(self, indice: int) -> None:
        self._ir_para(indice)

    def _trocou_de_aba(self, _indice: int) -> None:
        # abas.clear() tambem dispara este sinal, com a lista ainda vazia:
        # sem esta guarda a tela tentaria desenhar controles que nem existem.
        if self.projeto is None or not getattr(self, "_abas_ativas", None):
            return
        self._montar_tira()
        self.atualizar()

    def _ir_para_proximo_alerta(self) -> None:
        """Tab e o contador do topo levam para a proxima pagina marcada."""
        total = self._total()
        itens = (self.projeto.folhas if self.trabalha_com_folhas  # type: ignore[union-attr]
                 else self.projeto.paginas)  # type: ignore[union-attr]
        for salto in range(1, total + 1):
            indice = (self.indice_atual + salto) % total
            if itens[indice].precisa_revisao:
                self._ir_para(indice)
                return

    # ------------------------------------------------------------------
    # desenho
    # ------------------------------------------------------------------

    def atualizar(self) -> None:
        if self.projeto is None or not getattr(self, "_abas_ativas", None):
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
            self.vis_corte.definir_imagem(img)
            self.vis_corte.definir_corte(self.projeto.folhas[self.indice_folha].posicao_corte)
            self.previas.pre_carregar_folhas(self.indice_folha, DPI_PREVIA)
            return

        img = self.previas.pegar(self.indice_pagina, DPI_PREVIA)
        self.previas.pre_carregar(self.indice_pagina, DPI_PREVIA)
        pagina = self.projeto.paginas[self.indice_pagina]

        if aba == ABA_BORDAS:
            self.vis_bordas.definir_imagem(img)
            self.vis_bordas.definir_recorte(pagina.recorte or (0.0, 0.0, 1.0, 1.0))
        elif aba == ABA_ANGULO:
            self.vis_angulo.definir_imagem(img)
            self.vis_angulo.definir_angulo(pagina.angulo_manual or 0.0)
        else:
            self._atualizar_cartoes(img)

    def _atualizar_cartoes(self, img: np.ndarray | None) -> None:
        """Os quatro cartoes mostram a pagina de verdade, cada um com seu filtro."""
        from core.filtros import aplicar_filtro

        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]

        for chave, cartao in self.cartoes.items():
            cartao.definir_selecionado(chave == pagina.filtro)

        if img is None:
            for cartao in self.cartoes.values():
                cartao.definir_amostra(None)
            return

        # A previa ja vem com o filtro da pagina aplicado; para as outras tres
        # amostras recalculamos numa versao pequena, o que e barato.
        from core.pdf_io import limitar_altura

        pequena_base = self._imagem_sem_filtro()
        for chave, cartao in self.cartoes.items():
            if chave == pagina.filtro:
                cartao.definir_amostra(limitar_altura(img, 260))
            elif pequena_base is not None:
                amostra, _ = aplicar_filtro(pequena_base, chave, pagina.forca_preto)
                cartao.definir_amostra(amostra)
            else:
                cartao.definir_amostra(None)

    def _imagem_sem_filtro(self) -> np.ndarray | None:
        """Versao pequena e sem filtro da pagina atual, para os outros cartoes."""
        assert self.projeto is not None and self.previas is not None
        img_folha = self.previas.pegar_folha(self.projeto.paginas[self.indice_pagina].folha, 70)
        if img_folha is None:
            return None
        from core.pipeline import preparar_metade

        pagina = self.projeto.paginas[self.indice_pagina]
        folha = self.projeto.folhas[pagina.folha]
        try:
            return preparar_metade(img_folha, folha, pagina, self.projeto)
        except Exception:  # noqa: BLE001
            return None

    def _atualizar_faixa(self) -> None:
        assert self.projeto is not None
        item = self.item_atual
        aba = self.aba_atual

        alerta = analise.descrever(item.alertas[0]) if item.alertas else None
        rotulos = {
            ABA_CORTE: getattr(self, "texto_corte", None),
            ABA_BORDAS: getattr(self, "texto_bordas", None),
            ABA_ANGULO: getattr(self, "texto_angulo", None),
            ABA_FILTRO: getattr(self, "texto_filtro", None),
        }
        rotulo = rotulos.get(aba)
        if rotulo is None:
            return

        if alerta is not None and not item.revisada:
            rotulo.setText(alerta.mensagem)
            self._pintar_faixa(aba, alerta=True)
            self._mostrar_sugestao(aba, alerta.acao)
        else:
            rotulo.setText(self._texto_tranquilo(aba))
            self._pintar_faixa(aba, alerta=False)
            self._mostrar_sugestao(aba, None)

    def _texto_tranquilo(self, aba: str) -> str:
        assert self.projeto is not None
        if aba == ABA_CORTE:
            folha = self.projeto.folhas[self.indice_folha]
            if not folha.dividir:
                return "Esta folha nao vai ser dividida."
            return "Achei a lombada e vou cortar na linha azul. Se estiver errado, arraste a linha."
        if aba == ABA_BORDAS:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.recorte is None:
                return "Vou cortar a borda sozinho. Arraste o retangulo se quiser mudar."
            return "Voce ajustou o corte desta pagina."
        if aba == ABA_ANGULO:
            pagina = self.projeto.paginas[self.indice_pagina]
            if pagina.angulo_manual is None:
                return "Vou endireitar sozinho. Arraste sobre a pagina para girar na mao."
            return f"Voce girou esta pagina em {pagina.angulo_manual:+.1f} graus."
        pagina = self.projeto.paginas[self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        return f"Esta pagina vai sair em {nome}."

    def _pintar_faixa(self, aba: str, alerta: bool) -> None:
        indice = self._abas_ativas.index(aba) if aba in self._abas_ativas else -1
        if indice < 0:
            return
        faixa = self.abas.widget(indice).property("faixa")
        if faixa is not None:
            faixa.setObjectName("faixaAlerta" if alerta else "faixaInfo")
            faixa.style().unpolish(faixa)
            faixa.style().polish(faixa)

    def _mostrar_sugestao(self, aba: str, rotulo: str | None) -> None:
        botoes = {
            ABA_CORTE: getattr(self, "botao_sugestao_corte", None),
            ABA_BORDAS: getattr(self, "botao_sugestao_bordas", None),
            ABA_ANGULO: getattr(self, "botao_sugestao_angulo", None),
            ABA_FILTRO: getattr(self, "botao_sugestao_filtro", None),
        }
        botao = botoes.get(aba)
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

        if hasattr(self, "botao_nao_dividir"):
            folha = self.projeto.folhas[self.indice_folha]
            self.botao_nao_dividir.setText(
                "dividir esta" if not folha.dividir else "nao dividir esta"
            )

        if hasattr(self, "painel_forca"):
            pagina = self.projeto.paginas[self.indice_pagina]
            self.painel_forca.setVisible(pagina.filtro == PRETO_E_BRANCO)
            for chave, botao in self.botoes_forca.items():
                botao.setChecked(chave == pagina.forca_preto)
            self.botao_apagar.setText(
                "restaurar pagina" if pagina.apagada else "apagar pagina"
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
            texto = "1 pagina para voce olhar"
        else:
            texto = f"{pendentes} paginas para voce olhar"
        if apagadas:
            texto += f"  -  {apagadas} apagadas"
        self.botao_alertas.setText(texto)
        self.botao_alertas.setEnabled(pendentes > 0)

    def _previa_chegou(self, chave: str, img: np.ndarray) -> None:
        """Uma previa ficou pronta; se for a que estamos vendo, redesenha."""
        if self.projeto is None or self.previas is None:
            return
        esperada_pagina = self.previas.chave(self.indice_pagina, DPI_PREVIA)
        esperada_folha = self.previas.chave_folha(self.indice_folha, DPI_PREVIA)
        if chave in (esperada_pagina, esperada_folha) or chave.startswith("folha:"):
            self._atualizar_previa()

    # ------------------------------------------------------------------
    # alteracoes (todas passam pelo historico)
    # ------------------------------------------------------------------

    def _registrar(self, tipo: str, alvo: str, indices: list[int],
                   campos: dict, descricao: str) -> None:
        """Aplica a mudanca e guarda no historico, numa acao so."""
        assert self.projeto is not None and self.acoes is not None
        acao = montar_acao(self.projeto, tipo, alvo, indices, campos, descricao)
        aplicar(self.projeto, acao, acao.depois)
        self.acoes.registrar(acao)
        for indice in (indices if alvo == "pagina" else self._paginas_das_folhas(indices)):
            self.previas.invalidar(indice)  # type: ignore[union-attr]
        self.atualizar()

    def _paginas_das_folhas(self, folhas: list[int]) -> list[int]:
        assert self.projeto is not None
        alvo = set(folhas)
        return [p.indice for p in self.projeto.paginas if p.folha in alvo]

    # --- corte ------------------------------------------------------------

    def _mover_corte(self, posicao: float) -> None:
        self._registrar(
            "mover_corte", "folha", [self.indice_folha],
            {"posicao_corte": round(posicao, 4), "revisada": True},
            f"Linha de corte da folha {self.indice_folha + 1}",
        )

    def _corte_em_todas(self) -> None:
        assert self.projeto is not None
        posicao = self.projeto.folhas[self.indice_folha].posicao_corte
        indices = [f.indice for f in self.projeto.folhas]
        self._registrar(
            "aplicar_em_todas", "folha", indices,
            {"posicao_corte": round(posicao, 4)},
            f"Linha de corte de todas as {len(indices)} folhas",
        )

    def _alternar_dividir(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "nao_dividir", "folha", [self.indice_folha],
            {"dividir": not folha.dividir, "revisada": True},
            f"Folha {self.indice_folha + 1}: "
            + ("dividir" if not folha.dividir else "nao dividir"),
        )

    def _girar(self) -> None:
        assert self.projeto is not None
        folha = self.projeto.folhas[self.indice_folha]
        self._registrar(
            "girar", "folha", [self.indice_folha],
            {"rotacao": (folha.rotacao + 90) % 360},
            f"Girar a folha {self.indice_folha + 1}",
        )

    # --- bordas -----------------------------------------------------------

    def _mover_recorte(self, recorte: tuple) -> None:
        arredondado = tuple(round(float(v), 4) for v in recorte)
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": list(arredondado), "revisada": True},
            f"Corte de borda da pagina {self.indice_pagina + 1}",
        )

    def _sem_recorte(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina],
            {"recorte": [0.0, 0.0, 1.0, 1.0], "revisada": True},
            f"Nao cortar a borda da pagina {self.indice_pagina + 1}",
        )

    def _recorte_automatico(self) -> None:
        self._registrar(
            "recortar", "pagina", [self.indice_pagina], {"recorte": None},
            f"Voltar ao corte automatico na pagina {self.indice_pagina + 1}",
        )

    def _recorte_em_todas(self) -> None:
        assert self.projeto is not None
        recorte = self.projeto.paginas[self.indice_pagina].recorte
        indices = [p.indice for p in self.projeto.paginas]
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"recorte": list(recorte) if recorte else None},
            f"Corte de borda de todas as {len(indices)} paginas",
        )

    # --- angulo -----------------------------------------------------------

    def _mover_angulo(self, angulo: float) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": round(angulo, 2), "revisada": True},
            f"Angulo da pagina {self.indice_pagina + 1}: {angulo:+.1f} graus",
        )

    def _angulo_zero(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina],
            {"angulo_manual": 0.0, "revisada": True},
            f"Nao endireitar a pagina {self.indice_pagina + 1}",
        )

    def _angulo_automatico(self) -> None:
        self._registrar(
            "ajustar_angulo", "pagina", [self.indice_pagina], {"angulo_manual": None},
            f"Voltar ao endireitar automatico na pagina {self.indice_pagina + 1}",
        )

    # --- filtro -----------------------------------------------------------

    def _escolher_filtro(self, filtro: str) -> None:
        assert self.projeto is not None
        atual = self.projeto.paginas[self.indice_pagina].filtro
        nome_antes = NOMES_AMIGAVEIS.get(atual, atual)
        nome_depois = NOMES_AMIGAVEIS.get(filtro, filtro)
        self._registrar(
            "mudar_filtro", "pagina", [self.indice_pagina],
            {"filtro": filtro, "revisada": True},
            f"Filtro da pagina {self.indice_pagina + 1}: {nome_antes} para {nome_depois}",
        )

    def _escolher_forca(self, forca: str) -> None:
        self._registrar(
            "forca_preto", "pagina", [self.indice_pagina],
            {"forca_preto": forca, "revisada": True},
            f"Forca do preto da pagina {self.indice_pagina + 1}: {ROTULOS_FORCA[forca]}",
        )

    def _filtro_em_todas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto},
            f"{nome} em todas as {len(indices)} paginas",
        )

    def _filtro_nas_proximas(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        indices = [p.indice for p in self.projeto.paginas if p.indice >= self.indice_pagina]
        nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
        self._registrar(
            "aplicar_em_todas", "pagina", indices,
            {"filtro": pagina.filtro, "forca_preto": pagina.forca_preto},
            f"{nome} da pagina {self.indice_pagina + 1} em diante ({len(indices)} paginas)",
        )

    # --- gerais -----------------------------------------------------------

    def apagar_pagina(self) -> None:
        assert self.projeto is not None
        pagina = self.projeto.paginas[self.indice_pagina]
        acao = "restaurar" if pagina.apagada else "apagar"
        self._registrar(
            acao, "pagina", [self.indice_pagina],
            {"apagada": not pagina.apagada, "revisada": True},
            f"{acao.capitalize()} a pagina {self.indice_pagina + 1}",
        )

    def _marcar_revisada(self) -> None:
        alvo = "folha" if self.trabalha_com_folhas else "pagina"
        self._registrar(
            "revisar", alvo, [self.indice_atual], {"revisada": True},
            f"Conferir a {alvo} {self.indice_atual + 1}",
        )

    def marcar_certo_e_avancar(self) -> None:
        """Barra de espaco: aprova e ja pula para a proxima."""
        self._marcar_revisada()
        self._navegar(1)

    def _aplicar_sugestao(self) -> None:
        """O botao laranja do alerta: aplica a correcao mais provavel.

        E so um atalho. Todos os controles manuais continuam valendo.
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

    def desfazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        acao = self.acoes.desfazer(self.projeto)
        if acao is not None:
            self.previas.invalidar()  # type: ignore[union-attr]
            self.atualizar()

    def refazer(self) -> None:
        if self.acoes is None or self.projeto is None:
            return
        acao = self.acoes.refazer(self.projeto)
        if acao is not None:
            self.previas.invalidar()  # type: ignore[union-attr]
            self.atualizar()

    # --- teclado ----------------------------------------------------------

    def tratar_tecla(self, evento) -> bool:
        """Atalhos da secao 4.7. Devolve True se consumiu a tecla."""
        if self.projeto is None:
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
        if tecla == Qt.Key_R:
            if hasattr(self, "vis_corte"):
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

    def _pedir_processamento(self) -> None:
        """Avisa se ainda ha duvidas, mas nunca bloqueia."""
        assert self.projeto is not None
        pendentes = self.projeto.pendentes_de_revisao()
        if pendentes > 0:
            from PySide6.QtWidgets import QMessageBox

            caixa = QMessageBox(self)
            caixa.setWindowTitle("Antes de processar")
            caixa.setIcon(QMessageBox.Question)
            caixa.setText(
                f"Ainda tem {pendentes} "
                + ("pagina que eu nao tive certeza." if pendentes == 1
                   else "paginas que eu nao tive certeza.")
            )
            caixa.setInformativeText("Quer conferir antes ou processar assim mesmo?")
            conferir = caixa.addButton("conferir", QMessageBox.RejectRole)
            caixa.addButton("processar assim mesmo", QMessageBox.AcceptRole)
            caixa.exec()
            if caixa.clickedButton() is conferir:
                self._ir_para_proximo_alerta()
                return
        self.processar.emit()


def _botao(texto: str, destino: QHBoxLayout, acao, objeto: str = "") -> QPushButton:
    botao = QPushButton(texto)
    if objeto:
        botao.setObjectName(objeto)
    botao.clicked.connect(acao)
    destino.addWidget(botao)
    return botao
