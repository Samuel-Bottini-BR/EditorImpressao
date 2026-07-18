"""A página em tamanho grande, ocupando a janela inteira.

Serve para conferir de perto: o usuário aproxima, anda pela página e decide.
Abre de três jeitos - clicando num cartão de filtro, dando duplo clique numa
miniatura, ou clicando na própria prévia.

O modo comparar mostra dois filtros lado a lado com o zoom e a posição
amarrados, que é a única forma honesta de escolher entre dois filtros
parecidos: comparar de longe não resolve.

A imagem sai em resolução maior que a da prévia da tela de conferir. Esticar a
prévia de 110 DPI deixaria tudo borrado justamente na hora de olhar de perto.
"""

from __future__ import annotations

import traceback

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from core.filtros import MAGICO_PRO, MELHORAR, NOMES_AMIGAVEIS, ORIGINAL, PRETO_E_BRANCO
from registro import registrar_erro
from ui.estilo import FOLHA_DE_ESTILO, TEXTO_FRACO
from ui.widgets.visualizador import (
    MODO_CORTE,
    MODO_NENHUM,
    MODO_RECORTE,
    ZOOM_MAX,
    ZOOM_MIN,
    Visualizador,
)

# Bem acima dos 110 DPI da prévia: e para isso que a tela existe.
DPI_AMPLIADA = 220

MODO_FILTRO, MODO_CORTAR, MODO_BORDAS = "filtro", "corte", "bordas"

ORDEM_DOS_FILTROS = [ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO]


class TelaAmpliada(QDialog):
    """Janela cheia com a página ampliada."""

    fechou = Signal()

    def __init__(self, conferir, modo: str = MODO_FILTRO, parent=None) -> None:
        super().__init__(parent or conferir)
        self.conferir = conferir
        self.modo = modo
        self.comparando = False

        self.setWindowTitle("Ver de perto")
        self.setStyleSheet(FOLHA_DE_ESTILO)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)
        self.resize(1280, 860)

        self._montar()
        self._ligar_visualizadores()
        self.atualizar()

    # ------------------------------------------------------------------
    # montagem
    # ------------------------------------------------------------------

    def _montar(self) -> None:
        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(14, 10, 14, 10)
        camadas.setSpacing(8)

        camadas.addLayout(self._montar_barra())

        corpo = QHBoxLayout()
        corpo.setSpacing(10)

        self.anterior = QPushButton("<")
        self.anterior.setFixedWidth(44)
        self.anterior.clicked.connect(lambda *_: self._navegar(-1))
        corpo.addWidget(self.anterior)

        self.vista = Visualizador()
        self.vista.definir_modo(self._modo_do_visualizador())
        corpo.addWidget(self.vista, 1)

        # segunda vista, só no modo comparar
        self.vista_b = Visualizador()
        self.vista_b.definir_modo(MODO_NENHUM)
        self.vista_b.setVisible(False)
        corpo.addWidget(self.vista_b, 1)

        self.proxima = QPushButton(">")
        self.proxima.setFixedWidth(44)
        self.proxima.clicked.connect(lambda *_: self._navegar(1))
        corpo.addWidget(self.proxima)

        camadas.addLayout(corpo, 1)
        camadas.addWidget(self._montar_rodape())

    def _montar_barra(self) -> QHBoxLayout:
        barra = QHBoxLayout()
        barra.setSpacing(8)

        self.rotulo_pagina = QLabel("")
        self.rotulo_pagina.setStyleSheet("font-weight: 600; font-size: 15px;")
        barra.addWidget(self.rotulo_pagina)

        self.rotulo_filtro = QLabel("")
        self.rotulo_filtro.setObjectName("contadorAlerta")
        self.rotulo_filtro.setStyleSheet(
            "background: #dbeafe; color: #1d4ed8; border: 1px solid #2563eb;"
            " border-radius: 8px; padding: 4px 12px; font-weight: 600;"
        )
        barra.addWidget(self.rotulo_filtro)

        barra.addStretch()

        botao_menos = QPushButton("-")
        botao_menos.setFixedWidth(40)
        botao_menos.setToolTip("Afastar")
        botao_menos.clicked.connect(lambda *_: self._zoom(1 / 1.4))
        barra.addWidget(botao_menos)

        self.rotulo_zoom = QLabel("100%")
        self.rotulo_zoom.setMinimumWidth(56)
        self.rotulo_zoom.setAlignment(Qt.AlignCenter)
        self.rotulo_zoom.setStyleSheet(f"color: {TEXTO_FRACO};")
        barra.addWidget(self.rotulo_zoom)

        botao_mais = QPushButton("+")
        botao_mais.setFixedWidth(40)
        botao_mais.setToolTip("Aproximar")
        botao_mais.clicked.connect(lambda *_: self._zoom(1.4))
        barra.addWidget(botao_mais)

        ajustar = QPushButton("ajustar à tela")
        ajustar.clicked.connect(lambda *_: self._ajustar())
        barra.addWidget(ajustar)

        self.botao_comparar = QPushButton("comparar")
        self.botao_comparar.setCheckable(True)
        self.botao_comparar.clicked.connect(lambda *_: self._alternar_comparar())
        barra.addWidget(self.botao_comparar)

        self.combo_comparar = QComboBox()
        for chave in ORDEM_DOS_FILTROS:
            self.combo_comparar.addItem(NOMES_AMIGAVEIS.get(chave, chave), chave)
        self.combo_comparar.setVisible(False)
        self.combo_comparar.currentIndexChanged.connect(lambda *_: self.atualizar())
        barra.addWidget(self.combo_comparar)

        fechar = QPushButton("X")
        fechar.setFixedWidth(40)
        fechar.setToolTip("Fechar (Esc)")
        fechar.clicked.connect(lambda *_: self.close())
        barra.addWidget(fechar)
        return barra

    def _montar_rodape(self) -> QFrame:
        rodape = QFrame()
        linha = QHBoxLayout(rodape)
        linha.setContentsMargins(0, 0, 0, 0)
        linha.setSpacing(8)

        self.botoes_de_filtro: dict[str, QPushButton] = {}
        if self.modo == MODO_FILTRO:
            linha.addWidget(QLabel("Filtro:"))
            for chave in ORDEM_DOS_FILTROS:
                botao = QPushButton(NOMES_AMIGAVEIS.get(chave, chave))
                botao.setCheckable(True)
                botao.clicked.connect(
                    lambda _=False, c=chave: self._escolher_filtro(c)
                )
                self.botoes_de_filtro[chave] = botao
                linha.addWidget(botao)

        linha.addStretch()
        ajuda = QLabel(
            "roda do mouse: aproximar   -   arrastar com o botão do meio: mover   "
            "-   setas: mudar de página   -   1 2 3 4: filtros   -   Esc: voltar"
        )
        ajuda.setObjectName("atalhos")
        linha.addWidget(ajuda)
        return rodape

    def _ligar_visualizadores(self) -> None:
        self.vista.vista_mudou.connect(self._vista_a_mudou)
        self.vista_b.vista_mudou.connect(self._vista_b_mudou)
        self.vista.corte_movido.connect(self._corte_movido)
        self.vista.recorte_movido.connect(self._recorte_movido)

        # a prévia chega de outra thread; quando chega, redesenhamos
        if self.conferir.previas is not None:
            self.conferir.previas.pronta.connect(self._previa_chegou)

        self._recarregar = QTimer(self)
        self._recarregar.setSingleShot(True)
        self._recarregar.timeout.connect(self.atualizar)

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------

    def _modo_do_visualizador(self) -> str:
        if self.modo == MODO_CORTAR:
            return MODO_CORTE
        if self.modo == MODO_BORDAS:
            return MODO_RECORTE
        return MODO_NENHUM

    @property
    def projeto(self):
        return self.conferir.projeto

    def _indice(self) -> int:
        if self.modo == MODO_CORTAR:
            return self.conferir.indice_folha
        return self.conferir.indice_pagina

    def _total(self) -> int:
        if self.projeto is None:
            return 0
        if self.modo == MODO_CORTAR:
            return len(self.projeto.folhas)
        return len(self.projeto.paginas)

    # ------------------------------------------------------------------
    # desenho
    # ------------------------------------------------------------------

    def atualizar(self) -> None:
        if self.projeto is None or self.conferir.previas is None:
            return
        try:
            self._atualizar_imagens()
            self._atualizar_rotulos()
        except Exception:  # noqa: BLE001 - nada aqui pode fechar a janela
            registrar_erro("tela_ampliada.atualizar", traceback.format_exc())

    def _atualizar_imagens(self) -> None:
        previas = self.conferir.previas

        if self.modo == MODO_CORTAR:
            img = previas.pegar_folha(self.conferir.indice_folha, DPI_AMPLIADA)
            self.vista.definir_imagem(img)
            folha = self.projeto.folhas[self.conferir.indice_folha]
            self.vista.definir_corte(folha.posicao_corte)
            return

        indice = self.conferir.indice_pagina
        pagina = self.projeto.paginas[indice]

        img = previas.pegar(indice, DPI_AMPLIADA)
        self.vista.definir_imagem(img)
        if self.modo == MODO_BORDAS:
            self.vista.definir_recorte(pagina.recorte or (0.0, 0.0, 1.0, 1.0))

        if self.comparando:
            self.vista_b.definir_imagem(self._imagem_do_outro_filtro())

    def _imagem_do_outro_filtro(self) -> np.ndarray | None:
        """A mesma página com o filtro escolhido no seletor do comparar."""
        from core.filtros import aplicar_filtro
        from core.pipeline import preparar_metade

        outro = self.combo_comparar.currentData()
        pagina = self.projeto.paginas[self.conferir.indice_pagina]
        folha = self.projeto.folhas[pagina.folha]

        bruta = self.conferir.previas.pegar_folha(pagina.folha, DPI_AMPLIADA)
        if bruta is None:
            return None
        preparada = preparar_metade(bruta, folha, pagina, self.projeto)
        if not self.projeto.limpar or outro == ORIGINAL:
            return preparada
        saida, _ = aplicar_filtro(
            preparada, outro, pagina.forca_preto,
            pagina.clareza_melhorar, pagina.intensidade_magico,
        )
        return saida

    def _atualizar_rotulos(self) -> None:
        indice = self._indice()
        unidade = "Folha" if self.modo == MODO_CORTAR else "Página"
        self.rotulo_pagina.setText(f"{unidade} {indice + 1} de {self._total()}")

        if self.modo == MODO_CORTAR:
            self.rotulo_filtro.setText("onde cortar")
        else:
            pagina = self.projeto.paginas[self.conferir.indice_pagina]
            nome = NOMES_AMIGAVEIS.get(pagina.filtro, pagina.filtro)
            self.rotulo_filtro.setText(nome if not self.comparando else f"{nome}  |  "
                                       f"{self.combo_comparar.currentText()}")
            for chave, botao in self.botoes_de_filtro.items():
                botao.setChecked(chave == pagina.filtro)

        self.rotulo_zoom.setText(f"{int(self.vista.zoom * 100)}%")
        self.anterior.setEnabled(indice > 0)
        self.proxima.setEnabled(indice < self._total() - 1)

    def _previa_chegou(self, _chave: str, _img) -> None:
        # junta varias chegadas numa atualizacao so
        self._recarregar.start(60)

    # ------------------------------------------------------------------
    # acoes
    # ------------------------------------------------------------------

    def _zoom(self, fator: float) -> None:
        self.vista.definir_zoom(self.vista.zoom * fator)
        self._atualizar_rotulos()

    def _ajustar(self) -> None:
        self.vista.ajustar_a_tela()
        self.vista_b.ajustar_a_tela()
        self._atualizar_rotulos()

    def _vista_a_mudou(self, zoom: float, deslocamento) -> None:
        if self.comparando:
            self.vista_b.aplicar_vista(zoom, deslocamento)
        self.rotulo_zoom.setText(f"{int(zoom * 100)}%")

    def _vista_b_mudou(self, zoom: float, deslocamento) -> None:
        if self.comparando:
            self.vista.aplicar_vista(zoom, deslocamento)
            self.rotulo_zoom.setText(f"{int(zoom * 100)}%")

    def _alternar_comparar(self) -> None:
        self.comparando = self.botao_comparar.isChecked()
        self.vista_b.setVisible(self.comparando)
        self.combo_comparar.setVisible(self.comparando)

        if self.comparando:
            # começa comparando com um filtro diferente do atual
            atual = self.projeto.paginas[self.conferir.indice_pagina].filtro
            for chave in ORDEM_DOS_FILTROS:
                if chave != atual:
                    self.combo_comparar.setCurrentIndex(ORDEM_DOS_FILTROS.index(chave))
                    break
            self.vista_b.aplicar_vista(self.vista.zoom, self.vista.deslocamento)
        self.atualizar()

    def _navegar(self, passo: int) -> None:
        novo = max(0, min(self._total() - 1, self._indice() + passo))
        self.conferir._ir_para(novo)
        self.atualizar()

    def _escolher_filtro(self, filtro: str) -> None:
        self.conferir._escolher_filtro(filtro)
        self.atualizar()

    def _corte_movido(self, posicao: float) -> None:
        self.conferir._mover_corte(posicao)
        self.atualizar()

    def _recorte_movido(self, recorte: tuple) -> None:
        self.conferir._mover_recorte(recorte)
        self.atualizar()

    # ------------------------------------------------------------------
    # teclado
    # ------------------------------------------------------------------

    def keyPressEvent(self, evento) -> None:  # noqa: N802
        tecla = evento.key()

        if tecla == Qt.Key_Escape:
            self.close()
            return
        if tecla == Qt.Key_Left:
            self._navegar(-1)
            return
        if tecla == Qt.Key_Right:
            self._navegar(1)
            return
        if tecla in (Qt.Key_Plus, Qt.Key_Equal):
            self._zoom(1.4)
            return
        if tecla == Qt.Key_Minus:
            self._zoom(1 / 1.4)
            return
        if tecla == Qt.Key_0:
            self._ajustar()
            return

        atalhos = {
            Qt.Key_1: ORIGINAL, Qt.Key_2: PRETO_E_BRANCO,
            Qt.Key_3: MELHORAR, Qt.Key_4: MAGICO_PRO,
        }
        if tecla in atalhos and self.modo != MODO_CORTAR:
            self._escolher_filtro(atalhos[tecla])
            return

        super().keyPressEvent(evento)

    def closeEvent(self, evento) -> None:  # noqa: N802
        try:
            if self.conferir.previas is not None:
                self.conferir.previas.pronta.disconnect(self._previa_chegou)
        except (RuntimeError, TypeError):
            pass  # ja estava desligado
        self.fechou.emit()
        evento.accept()
