"""O livro aberto ao lado das opções, para folhear enquanto se escolhe.

Pedido do Samuel: "gostaria de poder visualizar o PDF e poder folhear ele
enquanto escolho as opções que vão ser aplicadas nele". Sem isto a pessoa marca
"dividir folhas ao meio" sem ter visto se a folha tem mesmo duas páginas, e só
descobre o engano na tela seguinte.

Mostra a folha COMO ELA É no arquivo, sem filtro nenhum. O que os filtros fazem
se vê na tela de conferir, com a prévia lado a lado; misturar as duas coisas
aqui faria a pessoa julgar o filtro por uma imagem pequena.

Uma folha de cada vez na memória, como no resto do programa: a página é
rasterizada quando pedida e a anterior é solta. O documento fica aberto
enquanto a tela existe - abrir e fechar a cada clique custaria caro num livro
de 900 folhas - e é fechado em `fechar()`.
"""

from __future__ import annotations

import traceback

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.pdf_io import ErroPDF, abrir_pdf, limitar_altura, pagina_para_array
from registro import registrar_erro
from ui.estilo import FOLHA_DE_ESTILO
from ui.widgets.visualizador import Visualizador

# Baixo de proposito: aqui a folha serve para RECONHECER a página, e nao para
# julgar qualidade. A tela precisa responder na hora quando se vira a folha.
DPI_DO_FOLHEAR = 90

# Teto de altura da imagem guardada. Uma folha de 300 DPI tem 3500 px de altura
# e nao cabe na area util; guardar o tamanho cheio so gastaria memoria.
ALTURA_MAXIMA = 1600


class FolhearPDF(QWidget):
    """Uma folha por vez, com setas, contador e botão de tela cheia."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._doc = None
        self._indice = 0
        self._total = 0

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(0, 0, 0, 0)
        camadas.setSpacing(8)

        self.visor = Visualizador()
        self.visor.ampliar_pedido.connect(self.abrir_em_tela_cheia)
        camadas.addWidget(self.visor, 1)

        barra = QHBoxLayout()
        barra.setSpacing(8)

        self.botao_anterior = QPushButton("<")
        self.botao_anterior.setFixedWidth(40)
        self.botao_anterior.clicked.connect(lambda: self.virar(-1))
        barra.addWidget(self.botao_anterior)

        self.contador = QLabel("")
        self.contador.setAlignment(Qt.AlignCenter)
        barra.addWidget(self.contador, 1)

        self.botao_proxima = QPushButton(">")
        self.botao_proxima.setFixedWidth(40)
        self.botao_proxima.clicked.connect(lambda: self.virar(1))
        barra.addWidget(self.botao_proxima)

        self.botao_tela_cheia = QPushButton("tela cheia")
        self.botao_tela_cheia.clicked.connect(self.abrir_em_tela_cheia)
        barra.addWidget(self.botao_tela_cheia)

        camadas.addLayout(barra)

    # --- uso --------------------------------------------------------------

    def abrir(self, caminho: str, indice: int = 0) -> None:
        """Abre o arquivo e mostra a folha pedida."""
        self.fechar()
        try:
            self._doc = abrir_pdf(caminho)
            self._total = self._doc.page_count
        except (ErroPDF, Exception):  # noqa: BLE001 - a tela nao pode cair aqui
            registrar_erro("folhear", traceback.format_exc())
            self._doc, self._total = None, 0
            self.visor.definir_imagem(None)
            self.contador.setText("não consegui abrir este arquivo para mostrar")
            self._atualizar_botoes()
            return
        self.ir_para(indice)

    def fechar(self) -> None:
        """Solta o arquivo. Chamar ao sair da tela."""
        if self._doc is not None:
            try:
                self._doc.close()
            except Exception:  # noqa: BLE001
                pass
        self._doc = None
        self._total = 0

    def virar(self, passo: int) -> None:
        self.ir_para(self._indice + passo)

    def ir_para(self, indice: int) -> None:
        if self._doc is None or self._total == 0:
            return
        self._indice = max(0, min(int(indice), self._total - 1))
        try:
            img = pagina_para_array(self._doc, self._indice, dpi=DPI_DO_FOLHEAR)
            self.visor.definir_imagem(limitar_altura(img, ALTURA_MAXIMA))
        except Exception:  # noqa: BLE001 - folha ruim nao derruba a tela
            registrar_erro("folhear", traceback.format_exc())
            self.visor.definir_imagem(None)
        self.contador.setText(f"folha {self._indice + 1} de {self._total}")
        self._atualizar_botoes()

    def _atualizar_botoes(self) -> None:
        tem = self._doc is not None and self._total > 0
        self.botao_anterior.setEnabled(tem and self._indice > 0)
        self.botao_proxima.setEnabled(tem and self._indice < self._total - 1)
        self.botao_tela_cheia.setEnabled(tem)

    def abrir_em_tela_cheia(self) -> None:
        if self._doc is None or self._total == 0:
            return
        janela = TelaCheiaDoPDF(self._doc, self._indice, self)
        janela.exec()
        # Volta para a folha em que a pessoa parou la dentro: seria estranho
        # fechar a tela cheia na folha 80 e reaparecer na 3.
        self.ir_para(janela.indice)

    # o teclado: setas viram a folha, como num leitor de verdade
    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.virar(-1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.virar(1)
        else:
            super().keyPressEvent(evento)


class TelaCheiaDoPDF(QDialog):
    """A mesma folha ocupando a janela inteira, para olhar de perto.

    Reaproveita o documento ja aberto em vez de abrir outro: o arquivo do
    acervo e so de leitura, e dois descritores para o mesmo livro de 300 MB nao
    trariam nada.
    """

    fechou = Signal()

    def __init__(self, doc, indice: int, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Folhear o livro")
        self.setStyleSheet(FOLHA_DE_ESTILO)
        self.setSizeGripEnabled(True)

        self._doc = doc
        self.indice = indice
        self._total = doc.page_count

        camadas = QVBoxLayout(self)
        camadas.setContentsMargins(14, 14, 14, 12)
        camadas.setSpacing(8)

        self.visor = Visualizador()
        camadas.addWidget(self.visor, 1)

        barra = QHBoxLayout()
        barra.setSpacing(8)
        anterior = QPushButton("<")
        anterior.setFixedWidth(44)
        anterior.clicked.connect(lambda: self.ir_para(self.indice - 1))
        barra.addWidget(anterior)
        self.contador = QLabel("")
        self.contador.setAlignment(Qt.AlignCenter)
        barra.addWidget(self.contador, 1)
        proxima = QPushButton(">")
        proxima.setFixedWidth(44)
        proxima.clicked.connect(lambda: self.ir_para(self.indice + 1))
        barra.addWidget(proxima)
        fechar = QPushButton("fechar")
        fechar.setObjectName("primario")
        fechar.clicked.connect(self.accept)
        barra.addWidget(fechar)
        camadas.addLayout(barra)

        self._anterior, self._proxima = anterior, proxima

        # Tamanho pedido a tela ANTES de maximizar. So o showMaximized nao
        # basta: se o gerenciador de janelas ignorar o pedido - acontece -, a
        # "tela cheia" abre do tamanho de um selo, que e o oposto do pedido.
        # Com a geometria posta na mao, o pior caso ainda e uma janela grande.
        tela = self.screen() or QGuiApplication.primaryScreen()
        if tela is not None:
            self.setGeometry(tela.availableGeometry())
        self.showMaximized()
        self.ir_para(indice)

    def ir_para(self, indice: int) -> None:
        self.indice = max(0, min(int(indice), self._total - 1))
        try:
            # Aqui vale mais DPI: a folha ocupa a tela toda e a pessoa veio
            # justamente olhar de perto.
            img = pagina_para_array(self._doc, self.indice, dpi=150)
            self.visor.definir_imagem(limitar_altura(img, 2200))
        except Exception:  # noqa: BLE001
            registrar_erro("folhear", traceback.format_exc())
            self.visor.definir_imagem(None)
        self.contador.setText(f"folha {self.indice + 1} de {self._total}")
        self._anterior.setEnabled(self.indice > 0)
        self._proxima.setEnabled(self.indice < self._total - 1)

    def keyPressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.key() in (Qt.Key_Left, Qt.Key_PageUp):
            self.ir_para(self.indice - 1)
        elif evento.key() in (Qt.Key_Right, Qt.Key_PageDown):
            self.ir_para(self.indice + 1)
        elif evento.key() == Qt.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(evento)
