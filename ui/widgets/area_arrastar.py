"""A área de arrastar o PDF da tela de inicio.

Clicar nela (ou Arquivo > Abrir) abre a janela de escolher o PDF, que mora em
ui/dialogos_de_arquivo.py (em português, com atalhos; etapa 9a, 26/10/2026).
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from ui import estilo


class AreaArrastar(QWidget):
    """Aceita arrastar-e-soltar e tambem clique para procurar."""

    arquivo_escolhido = Signal(str)

    def __init__(self, parent=None, cartao: bool = False) -> None:
        """cartao=True (etapa 7 do layout, rodada 6: "Cartão '+' no começo da
        grade"): o desenho de cartão, com o "+" azul redondo no meio;
        `grande` (a página sem livro nenhum, da tela 6) muda só o texto."""
        super().__init__(parent)
        self.cartao = cartao
        self.grande = False
        self.setAcceptDrops(True)
        # Baixa de proposito. Abrir livro novo se faz uma vez por livro, e a
        # caixa antiga tomava um terco da tela para isso - o espaco pertence
        # aos projetos, que e o que a pessoa vem ver todo dia.
        self.setMinimumHeight(62)
        self.setCursor(Qt.PointingHandCursor)
        self._por_cima = False

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento) -> None:  # noqa: N802
        """Desenha a caixa tracejada, o icone de arquivo (a mao, nunca emoji)
        e o texto - muda de cor quando um PDF esta sendo arrastado por cima."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        if self.cartao:
            self._pintar_o_cartao(pintor)
            return

        area = self.rect().adjusted(2, 2, -2, -2)
        pintor.setBrush(QColor(estilo.AZUL_CLARO if self._por_cima else estilo.cor("bar2")))
        pintor.setPen(QPen(QColor(estilo.AZUL if self._por_cima else estilo.BORDA), 2, Qt.DashLine))
        pintor.drawRoundedRect(area, 14, 14)

        # Icone a esquerda e as duas linhas ao lado dele, como no desenho
        # aprovado - e nao centralizado, que so funcionava na caixa alta.
        # Icone desenhado a mao: nada de emoji em rotulo.
        margem = 22
        self._desenhar_icone_arquivo(pintor, margem, (self.height() - 32) // 2)

        texto_x = margem + 44
        meio = self.height() // 2

        pintor.setPen(QColor(estilo.TEXTO))
        fonte = pintor.font()
        fonte.setPointSize(11)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.drawText(texto_x, meio - 4, "Arraste o PDF de um livro novo aqui")

        fonte.setBold(False)
        fonte.setPointSize(9)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.TEXTO_FRACO))
        pintor.drawText(texto_x, meio + 16, "ou clique para procurar no computador")

    def _pintar_o_cartao(self, pintor: QPainter) -> None:
        """O cartão "+": borda tracejada, o círculo azul com o "+" desenhado, o
        nome e a frase. Acende em azul com um PDF arrastado por cima."""
        from PySide6.QtCore import QPointF, QRectF

        area = QRectF(self.rect()).adjusted(1.5, 1.5, -1.5, -1.5)
        pintor.setBrush(QColor(estilo.AZUL_CLARO) if self._por_cima else Qt.NoBrush)
        pintor.setPen(QPen(QColor(estilo.AZUL if self._por_cima else estilo.BORDA), 1.2, Qt.DashLine))
        pintor.drawRoundedRect(area, 10, 10)
        raio = 30 if self.grande else 21
        centro = QPointF(area.center().x(), area.center().y() - (36 if self.grande else 28))
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(estilo.AZUL))
        pintor.drawEllipse(centro, raio, raio)
        pintor.setPen(QPen(QColor("white"), 3 if self.grande else 2.4))
        braco = raio * 0.45
        pintor.drawLine(QPointF(centro.x() - braco, centro.y()), QPointF(centro.x() + braco, centro.y()))
        pintor.drawLine(QPointF(centro.x(), centro.y() - braco), QPointF(centro.x(), centro.y() + braco))
        fonte = pintor.font()
        fonte.setPixelSize(17 if self.grande else 14)
        fonte.setBold(True)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.cor("forte")))
        y = centro.y() + raio + 10
        pintor.drawText(QRectF(area.left(), y, area.width(), 26), Qt.AlignCenter,
                        "Abrir um PDF" if self.grande else "Abrir um PDF novo")
        fonte.setBold(False)
        fonte.setPixelSize(12)
        pintor.setFont(fonte)
        pintor.setPen(QColor(estilo.TEXTO_FRACO))
        quebra = "\n"
        frase = (f"clique aqui para procurar no computador,{quebra}ou arraste o PDF de um livro para cá"
                 if self.grande else f"clique aqui, ou arraste{quebra}o PDF de um livro para cá")
        pintor.drawText(QRectF(area.left() + 8, y + 28, area.width() - 16, 40), Qt.AlignHCenter | Qt.AlignTop, frase)

    def _desenhar_icone_arquivo(self, pintor: QPainter, x: int, y: int) -> None:
        """Um icone de folha com a quina dobrada, desenhado a mao com QPainterPath."""
        largura, altura, dobra = 26, 32, 8

        pintor.setPen(QPen(QColor(estilo.AZUL), 2))
        pintor.setBrush(QColor(estilo.cor("bar2")))

        from PySide6.QtGui import QPainterPath

        caminho = QPainterPath()
        caminho.moveTo(x, y)
        caminho.lineTo(x + largura - dobra, y)
        caminho.lineTo(x + largura, y + dobra)
        caminho.lineTo(x + largura, y + altura)
        caminho.lineTo(x, y + altura)
        caminho.closeSubpath()
        pintor.drawPath(caminho)

        pintor.drawLine(x + largura - dobra, y, x + largura - dobra, y + dobra)
        pintor.drawLine(x + largura - dobra, y + dobra, x + largura, y + dobra)

        pintor.setPen(QPen(QColor(estilo.AZUL), 1))
        for i in range(3):
            linha_y = y + 14 + i * 6
            fim = x + largura - (10 if i == 2 else 6)
            pintor.drawLine(x + 6, linha_y, fim, linha_y)

    # --- interacao --------------------------------------------------------

    def dragEnterEvent(self, evento) -> None:  # noqa: N802
        """So aceita o arrasto (e acende a cor azul) se for mesmo um PDF."""
        if self._pdf_de(evento):
            evento.acceptProposedAction()
            self._por_cima = True
            self.update()

    def dragLeaveEvent(self, evento) -> None:  # noqa: N802
        """Volta a cor normal quando o arrasto sai da area sem soltar."""
        self._por_cima = False
        self.update()

    def dropEvent(self, evento) -> None:  # noqa: N802
        """PDF solto na area: emite arquivo_escolhido com o caminho."""
        self._por_cima = False
        self.update()
        caminho = self._pdf_de(evento)
        if caminho:
            self.arquivo_escolhido.emit(caminho)

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        """Clique com o botão esquerdo abre o seletor de arquivo.

        O menu Arquivo > Abrir (ui/janela_principal.py, _montar_menu) chama
        `abrir_dialogo_de_arquivo` diretamente, e NAO este metodo - de
        propósito, para nao precisar simular um QMouseEvent falso so para
        acionar o clique (ver o metodo abaixo)."""
        if evento.button() != Qt.LeftButton:
            return
        self.abrir_dialogo_de_arquivo()

    def abrir_dialogo_de_arquivo(self) -> None:
        """Abre o seletor de PDF. Usado pelo clique na área e pelo menu Arquivo > Abrir.

        Etapa 9a (26/10/2026, teste do Kaique: a janela saía em inglês, sem
        Área de Trabalho/Downloads, e o caminho digitado errado não avisava):
        a janela vem de ui/dialogos_de_arquivo.py - a do Windows quando dá, a
        do Qt em português quando não dá - e abre na última pasta de onde se
        abriu um livro."""
        from ui.dialogos_de_arquivo import escolher_pdf_para_abrir

        caminho = escolher_pdf_para_abrir(self, "Escolha o PDF do livro")
        if caminho:
            self.arquivo_escolhido.emit(caminho)

    @staticmethod
    def _pdf_de(evento) -> str | None:
        """Extrai o caminho do primeiro PDF entre as URLs arrastadas, ou None."""
        dados = evento.mimeData()
        if not dados.hasUrls():
            return None
        for url in dados.urls():
            caminho = url.toLocalFile()
            if caminho.lower().endswith(".pdf"):
                return caminho
        return None
