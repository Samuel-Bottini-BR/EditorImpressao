"""A prévia da página, com os ajustes manuais em cima dela.

Tres modos, conforme a aba:
  - CORTE:  linha tracejada azul que o usuario arrasta para mover a lombada
  - RECORTE: retangulo com alcas nos cantos e nos lados
  - ANGULO: arrastar gira a página, com linhas-guia para alinhar pelo texto

Nada de campo numerico: o usuario ve a página e mexe na página.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QCursor,
    QImage,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.estilo import AZUL, LARANJA, TEXTO_FRACO, VERDE

MODO_NENHUM = "nenhum"
MODO_CORTE = "corte"
MODO_RECORTE = "recorte"
MODO_ANGULO = "angulo"

TAMANHO_ALCA = 12
DISTANCIA_PEGA = 14
GRAUS_POR_PIXEL = 0.02  # sensibilidade do giro ao arrastar

# Zoom: 1,0 e "ajustado a tela". Nao passa de 8x porque acima disso a previa
# ja mostraria o pixel, e nao mais detalhe.
ZOOM_MIN, ZOOM_MAX = 1.0, 8.0
PASSO_DA_RODA = 1.25


def numpy_para_qimage(img: np.ndarray) -> QImage:
    """Converte o array do OpenCV em QImage, copiando os bytes.

    A copia e obrigatoria: sem ela o QImage aponta para memória que o Python
    pode liberar a qualquer momento, e a janela mostra lixo ou fecha sozinha.
    """
    if img is None or img.size == 0:
        return QImage()

    if img.ndim == 2:
        altura, largura = img.shape
        contigua = np.ascontiguousarray(img)
        qimg = QImage(contigua.data, largura, altura, largura, QImage.Format_Grayscale8)
    else:
        altura, largura, canais = img.shape
        if canais == 4:
            img = img[:, :, :3]
        contigua = np.ascontiguousarray(img[:, :, ::-1])  # BGR -> RGB
        qimg = QImage(contigua.data, largura, altura, largura * 3, QImage.Format_RGB888)
    return qimg.copy()


class Visualizador(QWidget):
    """Mostra a página e deixa o usuario corrigir o que o automático errou."""

    corte_movido = Signal(float)      # nova posicao 0-1
    recorte_movido = Signal(tuple)    # (x, y, largura, altura) em 0-1
    angulo_movido = Signal(float)     # graus
    vista_mudou = Signal(float, object)   # zoom, deslocamento (para o comparar)
    ampliar_pedido = Signal()             # duplo clique: abrir em tela cheia

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        # Minimo baixo de proposito. Com 340 px a area da imagem nao cabia em
        # janelas pequenas e o Qt acabava desenhando a faixa e os botoes por
        # cima da pagina. A imagem se ajusta sozinha ao que sobrar.
        self.setMinimumHeight(150)
        self.setMouseTracking(True)
        # Pede o espaço que houver, em qualquer tela onde for usado. Deixar
        # isso a cargo de quem monta a tela ja custou uma janela ampliada com
        # a página espremida numa faixa no alto.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._pixmap: QPixmap | None = None
        self._area = QRect()          # onde a imagem foi desenhada
        self.modo = MODO_NENHUM
        self.carregando = True

        self.posicao_corte = 0.5
        self.recorte = (0.0, 0.0, 1.0, 1.0)
        self.angulo = 0.0

        self._arrastando: str | None = None
        self._ponto_inicial = QPoint()
        self._angulo_inicial = 0.0
        self._recorte_inicial = self.recorte

        # Zoom e deslocamento. 1,0 quer dizer "do tamanho da janela"; acima
        # disso a imagem passa a ser maior que a área e o usuário arrasta para
        # andar por ela. Como toda a geometria dos controles e calculada a
        # partir de self._area, a linha de corte e as alças do recorte
        # continuam certas em qualquer zoom, sem conta nenhuma a mais.
        self.zoom = 1.0
        self.deslocamento = QPoint(0, 0)
        self._arrastando_vista = False
        self._deslocamento_inicial = QPoint(0, 0)

    # --- zoom -------------------------------------------------------------

    def definir_zoom(self, zoom: float, ancora: QPoint | None = None) -> None:
        """Muda o zoom mantendo sob o cursor o mesmo ponto da imagem."""
        novo = float(min(max(zoom, ZOOM_MIN), ZOOM_MAX))
        if abs(novo - self.zoom) < 1e-4:
            return

        if ancora is not None and self._area.width() > 0:
            # posicao do cursor dentro da imagem, de 0 a 1
            rx = (ancora.x() - self._area.left()) / self._area.width()
            ry = (ancora.y() - self._area.top()) / self._area.height()
            largura_nova = self._largura_base() * novo
            altura_nova = self._altura_base() * novo
            centro_x = self.width() / 2 + self.deslocamento.x()
            centro_y = self.height() / 2 + self.deslocamento.y()
            del centro_x, centro_y
            # mantem o ponto (rx, ry) parado sob o cursor
            esquerda = ancora.x() - rx * largura_nova
            topo = ancora.y() - ry * altura_nova
            self.deslocamento = QPoint(
                int(esquerda + largura_nova / 2 - self.width() / 2),
                int(topo + altura_nova / 2 - self.height() / 2),
            )

        self.zoom = novo
        if self.zoom <= 1.0:
            self.deslocamento = QPoint(0, 0)
        self.vista_mudou.emit(self.zoom, self.deslocamento)
        self.update()

    def ajustar_a_tela(self) -> None:
        self.zoom = 1.0
        self.deslocamento = QPoint(0, 0)
        self.vista_mudou.emit(self.zoom, self.deslocamento)
        self.update()

    def aplicar_vista(self, zoom: float, deslocamento: QPoint) -> None:
        """Copia a vista de outro visualizador (usado no modo comparar)."""
        self.zoom = float(zoom)
        self.deslocamento = QPoint(deslocamento)
        self.update()

    def _largura_base(self) -> float:
        """Largura que a imagem teria ajustada a janela, antes do zoom."""
        if self._pixmap is None or self._pixmap.isNull():
            return 0.0
        escala = min(self.width() / self._pixmap.width(),
                     self.height() / self._pixmap.height())
        return self._pixmap.width() * escala

    def _altura_base(self) -> float:
        if self._pixmap is None or self._pixmap.isNull():
            return 0.0
        escala = min(self.width() / self._pixmap.width(),
                     self.height() / self._pixmap.height())
        return self._pixmap.height() * escala

    def wheelEvent(self, evento) -> None:  # noqa: N802
        if self._pixmap is None:
            return
        passos = evento.angleDelta().y() / 120.0
        if not passos:
            return
        self.definir_zoom(self.zoom * (PASSO_DA_RODA ** passos),
                          ancora=evento.position().toPoint())
        evento.accept()

    # --- conteudo ---------------------------------------------------------

    def definir_imagem(self, img: np.ndarray | None) -> None:
        """Troca a imagem. None quer dizer "ainda vem".

        Quando a nova ainda não chegou, a anterior CONTINUA na tela em vez de
        apagar tudo. Sem isso, mexer na linha de corte ou no medidor faz a
        página piscar em branco a cada ajuste - e justamente no momento em que
        o usuário está olhando o detalhe.
        """
        if img is None:
            self.carregando = True
        else:
            self._pixmap = QPixmap.fromImage(numpy_para_qimage(img))
            self.carregando = False
        self.update()

    def definir_modo(self, modo: str) -> None:
        self.modo = modo
        self.setCursor(QCursor(Qt.SizeHorCursor if modo == MODO_CORTE else Qt.ArrowCursor))
        self.update()

    def definir_corte(self, posicao: float) -> None:
        self.posicao_corte = float(min(max(posicao, 0.02), 0.98))
        self.update()

    def definir_recorte(self, recorte: tuple) -> None:
        self.recorte = tuple(recorte)
        self.update()

    def definir_angulo(self, angulo: float) -> None:
        self.angulo = float(angulo)
        self.update()

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento: QPaintEvent) -> None:  # noqa: N802 (nome do Qt)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor("#ffffff"))

        if self._pixmap is None:
            pintor.setPen(QColor(TEXTO_FRACO))
            texto = "Preparando a prévia..." if self.carregando else "Sem prévia"
            pintor.drawText(self.rect(), Qt.AlignCenter, texto)
            return

        largura = max(1, int(self._largura_base() * self.zoom))
        altura = max(1, int(self._altura_base() * self.zoom))
        x = (self.width() - largura) // 2 + self.deslocamento.x()
        y = (self.height() - altura) // 2 + self.deslocamento.y()
        self._area = QRect(x, y, largura, altura)

        # Com zoom alto, escalar o pixmap inteiro custaria caro; desenhamos
        # direto no retangulo e deixamos o Qt cuidar do recorte.
        pintor.setRenderHint(QPainter.SmoothPixmapTransform, self.zoom <= 4.0)
        pintor.drawPixmap(self._area, self._pixmap)
        pintor.setPen(QPen(QColor("#e5e7eb"), 1))
        pintor.drawRect(self._area.adjusted(0, 0, -1, -1))

        if self.carregando:
            self._desenhar_aviso_de_espera(pintor)

        if self.modo == MODO_CORTE:
            self._desenhar_corte(pintor)
        elif self.modo == MODO_RECORTE:
            self._desenhar_recorte(pintor)
        elif self.modo == MODO_ANGULO:
            self._desenhar_guias(pintor)

    def _desenhar_aviso_de_espera(self, pintor: QPainter) -> None:
        """Selo discreto no canto enquanto a nova imagem não chega.

        A página que esta na tela continua sendo a de antes; o selo avisa
        que ela ainda vai mudar.
        """
        area = QRect(self._area.left() + 8, self._area.top() + 8, 112, 24)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(QColor(31, 41, 55, 190))
        pintor.drawRoundedRect(area, 6, 6)
        pintor.setPen(QColor("white"))
        pintor.drawText(area, Qt.AlignCenter, "atualizando...")

    def _desenhar_corte(self, pintor: QPainter) -> None:
        x = self._area.left() + int(self.posicao_corte * self._area.width())

        caneta = QPen(QColor(AZUL), 3, Qt.DashLine)
        pintor.setPen(caneta)
        pintor.drawLine(x, self._area.top(), x, self._area.bottom())

        # pega larga no topo, para o usuario saber que da para arrastar
        pintor.setBrush(QColor(AZUL))
        pintor.setPen(Qt.NoPen)
        pintor.drawRoundedRect(x - 26, self._area.top() - 2, 52, 20, 5, 5)
        pintor.setPen(QColor("white"))
        pintor.drawText(QRect(x - 26, self._area.top() - 2, 52, 20),
                        Qt.AlignCenter, "arraste")

    def _desenhar_recorte(self, pintor: QPainter) -> None:
        r = self._retangulo_recorte()

        # escurece o que vai ser jogado fora
        sombra = QColor(0, 0, 0, 70)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(sombra)
        pintor.drawRect(QRect(self._area.left(), self._area.top(), self._area.width(),
                              r.top() - self._area.top()))
        pintor.drawRect(QRect(self._area.left(), r.bottom(), self._area.width(),
                              self._area.bottom() - r.bottom()))
        pintor.drawRect(QRect(self._area.left(), r.top(), r.left() - self._area.left(),
                              r.height()))
        pintor.drawRect(QRect(r.right(), r.top(), self._area.right() - r.right(), r.height()))

        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(QPen(QColor(VERDE), 2))
        pintor.drawRect(r)

        pintor.setBrush(QColor(VERDE))
        pintor.setPen(Qt.NoPen)
        for ponto in self._alcas(r).values():
            pintor.drawRoundedRect(
                QRect(ponto.x() - TAMANHO_ALCA // 2, ponto.y() - TAMANHO_ALCA // 2,
                      TAMANHO_ALCA, TAMANHO_ALCA), 3, 3,
            )

    def _desenhar_guias(self, pintor: QPainter) -> None:
        """Linhas horizontais para o usuario comparar com as linhas de texto."""
        pintor.setPen(QPen(QColor(LARANJA), 1, Qt.DashLine))
        passo = max(30, self._area.height() // 10)
        y = self._area.top() + passo
        while y < self._area.bottom():
            pintor.drawLine(self._area.left(), y, self._area.right(), y)
            y += passo

        pintor.setPen(QColor(TEXTO_FRACO))
        pintor.drawText(
            QRect(self._area.left() + 8, self._area.top() + 6, 240, 22),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"inclinacao: {self.angulo:+.1f} graus",
        )

    # --- geometria --------------------------------------------------------

    def _retangulo_recorte(self) -> QRect:
        x, y, w, h = self.recorte
        return QRect(
            self._area.left() + int(x * self._area.width()),
            self._area.top() + int(y * self._area.height()),
            max(10, int(w * self._area.width())),
            max(10, int(h * self._area.height())),
        )

    def _alcas(self, r: QRect) -> dict[str, QPoint]:
        return {
            "no": r.topLeft(), "ne": r.topRight(),
            "so": r.bottomLeft(), "se": r.bottomRight(),
            "n": QPoint(r.center().x(), r.top()), "s": QPoint(r.center().x(), r.bottom()),
            "o": QPoint(r.left(), r.center().y()), "l": QPoint(r.right(), r.center().y()),
        }

    # --- mouse ------------------------------------------------------------

    def mouseDoubleClickEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if evento.button() == Qt.LeftButton and self._pixmap is not None:
            self.ampliar_pedido.emit()

    def mousePressEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if self._pixmap is None:
            return
        ponto = evento.position().toPoint()

        # Arrastar para andar pela imagem: botão do meio sempre, e tambem o
        # esquerdo quando não ha o que editar ou quando o Ctrl esta apertado.
        # Assim a linha de corte continua sendo arrastada com o botão esquerdo.
        quer_mover = (
            evento.button() == Qt.MiddleButton
            or (evento.button() == Qt.LeftButton
                and (self.modo == MODO_NENHUM
                     or evento.modifiers() & Qt.ControlModifier))
        )
        if quer_mover and self.zoom > 1.0:
            self._arrastando_vista = True
            self._ponto_inicial = ponto
            self._deslocamento_inicial = QPoint(self.deslocamento)
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            return

        if evento.button() != Qt.LeftButton:
            return
        self._ponto_inicial = ponto

        if self.modo == MODO_CORTE:
            self._arrastando = "corte"
            self._mover_corte(ponto)
        elif self.modo == MODO_RECORTE:
            self._arrastando = self._alca_sob(ponto) or (
                "mover" if self._retangulo_recorte().contains(ponto) else None
            )
            self._recorte_inicial = self.recorte
        elif self.modo == MODO_ANGULO:
            self._arrastando = "angulo"
            self._angulo_inicial = self.angulo

    def mouseMoveEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        ponto = evento.position().toPoint()

        if self._arrastando_vista:
            self.deslocamento = self._deslocamento_inicial + (ponto - self._ponto_inicial)
            self.vista_mudou.emit(self.zoom, self.deslocamento)
            self.update()
            return

        if self._arrastando is None:
            if self.modo == MODO_RECORTE:
                self._atualizar_cursor(ponto)
            return

        if self._arrastando == "corte":
            self._mover_corte(ponto)
        elif self._arrastando == "angulo":
            delta = ponto.x() - self._ponto_inicial.x()
            self.definir_angulo(self._angulo_inicial + delta * GRAUS_POR_PIXEL)
        else:
            self._mover_recorte(ponto)

    def mouseReleaseEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if self._arrastando_vista:
            self._arrastando_vista = False
            self.setCursor(QCursor(
                Qt.SizeHorCursor if self.modo == MODO_CORTE else Qt.ArrowCursor
            ))
            return

        if self._arrastando is None:
            return
        arrastava = self._arrastando
        self._arrastando = None

        # O sinal so sai ao soltar: assim um arrasto inteiro vira UMA acao no
        # desfazer, e nao uma acao por pixel percorrido.
        if arrastava == "corte":
            self.corte_movido.emit(self.posicao_corte)
        elif arrastava == "angulo":
            self.angulo_movido.emit(self.angulo)
        else:
            self.recorte_movido.emit(self.recorte)

    # --- ajudantes --------------------------------------------------------

    def _mover_corte(self, ponto: QPoint) -> None:
        if self._area.width() <= 0:
            return
        relativo = (ponto.x() - self._area.left()) / self._area.width()
        self.definir_corte(relativo)

    def _alca_sob(self, ponto: QPoint) -> str | None:
        for nome, centro in self._alcas(self._retangulo_recorte()).items():
            if (abs(centro.x() - ponto.x()) <= DISTANCIA_PEGA
                    and abs(centro.y() - ponto.y()) <= DISTANCIA_PEGA):
                return nome
        return None

    def _atualizar_cursor(self, ponto: QPoint) -> None:
        alca = self._alca_sob(ponto)
        formatos = {
            "no": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor,
            "ne": Qt.SizeBDiagCursor, "so": Qt.SizeBDiagCursor,
            "n": Qt.SizeVerCursor, "s": Qt.SizeVerCursor,
            "o": Qt.SizeHorCursor, "l": Qt.SizeHorCursor,
        }
        self.setCursor(QCursor(formatos.get(alca, Qt.ArrowCursor)))

    def _mover_recorte(self, ponto: QPoint) -> None:
        if self._area.width() <= 0 or self._area.height() <= 0:
            return
        dx = (ponto.x() - self._ponto_inicial.x()) / self._area.width()
        dy = (ponto.y() - self._ponto_inicial.y()) / self._area.height()
        x, y, w, h = self._recorte_inicial
        lado = self._arrastando or ""

        if lado == "mover":
            x, y = x + dx, y + dy
        else:
            if "o" in lado:
                x, w = x + dx, w - dx
            if "l" in lado:
                w = w + dx
            if "n" in lado:
                y, h = y + dy, h - dy
            if "s" in lado:
                h = h + dy

        minimo = 0.05
        w, h = max(minimo, w), max(minimo, h)
        x = min(max(0.0, x), 1.0 - w)
        y = min(max(0.0, y), 1.0 - h)
        self.definir_recorte((x, y, min(w, 1.0 - x), min(h, 1.0 - y)))
