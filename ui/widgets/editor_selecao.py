"""Marcar a mão onde está a gravura, a letra e o papel.

O detector automático acerta a maioria das páginas, mas erra em algumas, e nas
que erra não há como consertar sem uma ferramenta de marcação. É esta.

As ferramentas seguem o que já existe em programa de imagem, porque o Kaique
provavelmente já viu isso em algum lugar:

    retangulo   arrastar de um canto ao outro
    elipse      idem, mas oval
    laco        contornar a mão livre
    poligono    clicar ponto a ponto, duplo clique para fechar
    pincel      pintar por cima, com espessura ajustavel
    varinha     clicar e pegar a mancha inteira daquela cor
    cor         clicar numa cor e pegar TUDO daquela cor na pagina

Cada uma pode SOMAR ou SUBTRAIR, e cada marcação tem um tipo - gravura, letra
ou papel. Tudo vai para a mesma lista de regiões que o detector automático e a
rede neural usam, e por isso as três se somam em vez de competir: a máquina
propõe, a pessoa corrige por cima, e rodar a detecção de novo não apaga a
correção.

Este widget não conhece o projeto nem o pipeline. Ele recebe uma imagem e uma
seleção, devolve a seleção alterada, e avisa por sinal. Assim dá para testar
sem abrir o programa inteiro.
"""

from __future__ import annotations

import cv2
import numpy as np
from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QImage,
    QMouseEvent,
    QPainter,
    QPaintEvent,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from core.selecao import (
    ELIPSE,
    GRAVURA,
    LETRA,
    MAO,
    PAPEL,
    POLIGONO,
    RETANGULO,
    SOMAR,
    SUBTRAIR,
    TRACO,
    Regiao,
    Selecao,
    de_mascara,
)

# --- ferramentas ------------------------------------------------------------

FERRAMENTA_RETANGULO = "retangulo"
FERRAMENTA_ELIPSE = "elipse"
FERRAMENTA_LACO = "laco"
FERRAMENTA_POLIGONO = "poligono"
FERRAMENTA_PINCEL = "pincel"
FERRAMENTA_VARINHA = "varinha"
FERRAMENTA_COR = "cor"

FERRAMENTAS = (
    FERRAMENTA_RETANGULO,
    FERRAMENTA_ELIPSE,
    FERRAMENTA_LACO,
    FERRAMENTA_POLIGONO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_VARINHA,
    FERRAMENTA_COR,
)

NOMES_DAS_FERRAMENTAS = {
    FERRAMENTA_RETANGULO: "Retângulo",
    FERRAMENTA_ELIPSE: "Oval",
    FERRAMENTA_LACO: "Laço",
    FERRAMENTA_POLIGONO: "Ponto a ponto",
    FERRAMENTA_PINCEL: "Pincel",
    FERRAMENTA_VARINHA: "Varinha mágica",
    FERRAMENTA_COR: "Pegar tudo desta cor",
}

AJUDA_DAS_FERRAMENTAS = {
    FERRAMENTA_RETANGULO: "Arraste de um canto ao outro.",
    FERRAMENTA_ELIPSE: "Arraste para desenhar um oval.",
    FERRAMENTA_LACO: "Contorne a área com o botão apertado.",
    FERRAMENTA_POLIGONO: "Clique ponto a ponto. Duplo clique fecha.",
    FERRAMENTA_PINCEL: "Pinte por cima. A roda do mouse muda a espessura.",
    FERRAMENTA_VARINHA: "Clique numa cor e ela pega a mancha inteira.",
    FERRAMENTA_COR: "Clique numa cor e ela pega TUDO daquela cor na página. "
                    "A roda do mouse muda o quanto a cor pode variar.",
}

# Cor de cada tipo na tela. As mesmas dos testes, para quem viu os relatorios
# reconhecer.
CORES = {
    GRAVURA: QColor(255, 60, 0, 90),
    LETRA: QColor(0, 120, 255, 90),
    PAPEL: QColor(120, 200, 120, 70),
}
CORES_BORDA = {
    GRAVURA: QColor(255, 60, 0),
    LETRA: QColor(0, 120, 255),
    PAPEL: QColor(90, 170, 90),
}

# Varinha magica: quanto a cor pode variar e ainda contar como a mesma mancha.
TOLERANCIA_PADRAO = 30
TOLERANCIA_MIN, TOLERANCIA_MAX = 4, 120

# Pincel, em fracao da menor dimensao da pagina.
ESPESSURA_PADRAO = 0.02
ESPESSURA_MIN, ESPESSURA_MAX = 0.002, 0.20


class EditorSelecao(QWidget):
    """Mostra a página com a marcação por cima, e deixa desenhar nela."""

    selecao_mudou = Signal()
    aviso = Signal(str)     # frase curta para a barra de status

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.StrongFocus)

        self._img: np.ndarray | None = None
        self._pixmap: QPixmap | None = None
        self._area = QRect()

        self.selecao = Selecao()
        self.ferramenta = FERRAMENTA_RETANGULO
        self.tipo = GRAVURA
        self.operacao = SOMAR
        self.espessura = ESPESSURA_PADRAO
        self.tolerancia = TOLERANCIA_PADRAO
        # Filtro so para o que for marcado daqui em diante. Vazio quer
        # dizer "use o filtro da pagina", que e o comportamento de sempre.
        self.filtro_da_regiao = ""
        self.mostrar_marcacao = True

        self._desenhando = False
        self._pontos: list[tuple[float, float]] = []
        self._pontos_poligono: list[tuple[float, float]] = []

        # Para desfazer: guardamos o tamanho da lista antes de cada acao, o que
        # e barato e suficiente - toda acao so ACRESCENTA regioes.
        self._marcos: list[int] = []

    # --- entrada ----------------------------------------------------------

    def definir_imagem(self, img: np.ndarray | None) -> None:
        self._img = img
        if img is None:
            self._pixmap = None
        else:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if img.ndim == 3 else \
                cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            altura, largura = rgb.shape[:2]
            imagem = QImage(rgb.data, largura, altura, 3 * largura,
                            QImage.Format_RGB888).copy()
            self._pixmap = QPixmap.fromImage(imagem)
        self.update()

    def definir_selecao(self, selecao: Selecao) -> None:
        self.selecao = selecao
        self._marcos.clear()
        self.update()

    def definir_ferramenta(self, ferramenta: str) -> None:
        if ferramenta in FERRAMENTAS:
            self.ferramenta = ferramenta
            self._pontos_poligono.clear()
            self.aviso.emit(AJUDA_DAS_FERRAMENTAS[ferramenta])
            self.update()

    def definir_tipo(self, tipo: str) -> None:
        if tipo in (GRAVURA, LETRA, PAPEL):
            self.tipo = tipo
            self.update()

    def definir_operacao(self, operacao: str) -> None:
        self.operacao = SUBTRAIR if operacao == SUBTRAIR else SOMAR
        self.update()

    def definir_filtro_da_regiao(self, filtro: str) -> None:
        """Que filtro vale so no que for marcado daqui em diante."""
        self.filtro_da_regiao = filtro or ""
        self.update()

    # --- desfazer ---------------------------------------------------------

    @property
    def pode_desfazer(self) -> bool:
        return bool(self._marcos)

    def desfazer(self) -> None:
        """Volta a marcação ao estado anterior à última ação."""
        if not self._marcos:
            return
        ate = self._marcos.pop()
        self.selecao.regioes = self.selecao.regioes[:ate]
        self.selecao_mudou.emit()
        self.update()

    def limpar_o_que_a_maquina_marcou(self) -> int:
        """Tira a proposta automatica e mantem o que a pessoa desenhou."""
        from core.selecao import AUTOMATICO, REDE

        self._marcar()
        quantas = (self.selecao.limpar_origem(AUTOMATICO)
                   + self.selecao.limpar_origem(REDE))
        self.selecao_mudou.emit()
        self.update()
        return quantas

    def _marcar(self) -> None:
        self._marcos.append(len(self.selecao.regioes))
        if len(self._marcos) > 200:
            self._marcos.pop(0)

    def _acrescentar(self, regiao: Regiao) -> None:
        if not regiao.valida():
            return
        regiao.filtro = self.filtro_da_regiao
        self._marcar()
        self.selecao.acrescentar(regiao)
        self.selecao_mudou.emit()
        self.update()

    # --- geometria --------------------------------------------------------

    def _calcular_area(self) -> QRect:
        if self._pixmap is None or self._pixmap.isNull():
            return QRect()
        largura, altura = self._pixmap.width(), self._pixmap.height()
        escala = min(self.width() / largura, self.height() / altura)
        w, h = int(largura * escala), int(altura * escala)
        return QRect((self.width() - w) // 2, (self.height() - h) // 2, w, h)

    def _para_fracao(self, ponto: QPoint) -> tuple[float, float]:
        """Ponto da tela para fracao da imagem, de 0 a 1."""
        a = self._area
        if a.width() <= 0 or a.height() <= 0:
            return (0.0, 0.0)
        x = (ponto.x() - a.left()) / a.width()
        y = (ponto.y() - a.top()) / a.height()
        return (min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0))

    def _para_tela(self, fx: float, fy: float) -> QPoint:
        a = self._area
        return QPoint(int(a.left() + fx * a.width()), int(a.top() + fy * a.height()))

    # --- desenho na tela --------------------------------------------------

    def paintEvent(self, evento: QPaintEvent) -> None:  # noqa: N802 (nome do Qt)
        pintor = QPainter(self)
        pintor.fillRect(self.rect(), QColor(28, 28, 30))
        if self._pixmap is None or self._pixmap.isNull():
            return

        self._area = self._calcular_area()
        pintor.setRenderHint(QPainter.SmoothPixmapTransform, True)
        pintor.drawPixmap(self._area, self._pixmap)

        if self.mostrar_marcacao:
            self._pintar_marcacao(pintor)
        self._pintar_o_que_esta_sendo_desenhado(pintor)

    def _pintar_marcacao(self, pintor: QPainter) -> None:
        """Pinta a marcacao ja feita, cada tipo na sua cor.

        A mascara e calculada no tamanho da AREA na tela, e nao no da pagina:
        numa pagina de 300 DPI seriam sete milhoes de pixels a cada repintura,
        e a tela travaria ao arrastar.
        """
        largura, altura = self._area.width(), self._area.height()
        if largura <= 0 or altura <= 0 or self.selecao.vazia:
            return

        for tipo in (PAPEL, GRAVURA, LETRA):
            mascara = self.selecao.mascara(altura, largura, tipo)
            if not mascara.any():
                continue
            cor = CORES[tipo]
            capa = np.zeros((altura, largura, 4), np.uint8)
            capa[mascara] = (cor.red(), cor.green(), cor.blue(), cor.alpha())
            imagem = QImage(capa.data, largura, altura, 4 * largura,
                            QImage.Format_RGBA8888).copy()
            pintor.drawImage(self._area.topLeft(), imagem)

    def _pintar_o_que_esta_sendo_desenhado(self, pintor: QPainter) -> None:
        cor = CORES_BORDA.get(self.tipo, QColor(255, 255, 255))
        caneta = QPen(cor, 2, Qt.SolidLine if self.operacao == SOMAR else Qt.DashLine)
        pintor.setPen(caneta)
        pintor.setBrush(Qt.NoBrush)

        if self._desenhando and len(self._pontos) >= 2:
            if self.ferramenta == FERRAMENTA_RETANGULO:
                pintor.drawRect(self._retangulo_dos_pontos())
            elif self.ferramenta == FERRAMENTA_ELIPSE:
                pintor.drawEllipse(self._retangulo_dos_pontos())
            elif self.ferramenta in (FERRAMENTA_LACO, FERRAMENTA_PINCEL):
                pontos = [self._para_tela(x, y) for x, y in self._pontos]
                if self.ferramenta == FERRAMENTA_PINCEL:
                    pintor.setPen(QPen(cor, self._espessura_na_tela(),
                                       Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                pintor.drawPolyline(pontos)

        if self._pontos_poligono:
            pontos = [self._para_tela(x, y) for x, y in self._pontos_poligono]
            pintor.drawPolyline(pontos)
            for p in pontos:
                pintor.drawEllipse(p, 3, 3)

    def _retangulo_dos_pontos(self) -> QRect:
        a = self._para_tela(*self._pontos[0])
        b = self._para_tela(*self._pontos[-1])
        return QRect(a, b).normalized()

    def _espessura_na_tela(self) -> int:
        lado = min(self._area.width(), self._area.height())
        return max(2, int(self.espessura * lado))

    # --- mouse ------------------------------------------------------------

    def mousePressEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if self._pixmap is None or evento.button() != Qt.LeftButton:
            return
        self._area = self._calcular_area()
        ponto = self._para_fracao(evento.position().toPoint())

        if self.ferramenta == FERRAMENTA_VARINHA:
            self._varinha(ponto)
            return
        if self.ferramenta == FERRAMENTA_COR:
            self._tudo_desta_cor(ponto)
            return
        if self.ferramenta == FERRAMENTA_POLIGONO:
            self._pontos_poligono.append(ponto)
            self.update()
            return

        self._desenhando = True
        self._pontos = [ponto]
        self.update()

    def mouseMoveEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if not self._desenhando:
            return
        ponto = self._para_fracao(evento.position().toPoint())
        if self.ferramenta in (FERRAMENTA_LACO, FERRAMENTA_PINCEL):
            # so guarda se andou o bastante: um traco de mil pontos nao e
            # editavel nem cabe no arquivo de projeto
            if not self._pontos or _longe(self._pontos[-1], ponto):
                self._pontos.append(ponto)
        else:
            self._pontos = [self._pontos[0], ponto]
        self.update()

    def mouseReleaseEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        if not self._desenhando or evento.button() != Qt.LeftButton:
            return
        self._desenhando = False
        pontos = list(self._pontos)
        self._pontos = []

        if self.ferramenta in (FERRAMENTA_RETANGULO, FERRAMENTA_ELIPSE):
            if len(pontos) >= 2 and _longe(pontos[0], pontos[-1], 0.01):
                forma = RETANGULO if self.ferramenta == FERRAMENTA_RETANGULO else ELIPSE
                self._acrescentar(self._nova(forma, [pontos[0], pontos[-1]]))
        elif self.ferramenta == FERRAMENTA_LACO:
            if len(pontos) >= 3:
                self._acrescentar(self._nova(POLIGONO, pontos))
        elif self.ferramenta == FERRAMENTA_PINCEL:
            if pontos:
                self._acrescentar(self._nova(TRACO, pontos))
        self.update()

    def mouseDoubleClickEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        """Duplo clique fecha o poligono ponto a ponto."""
        if self.ferramenta == FERRAMENTA_POLIGONO and len(self._pontos_poligono) >= 3:
            self._acrescentar(self._nova(POLIGONO, list(self._pontos_poligono)))
            self._pontos_poligono.clear()
            self.update()

    def wheelEvent(self, evento) -> None:  # noqa: N802
        """A roda muda a espessura do pincel, ou a tolerancia da varinha."""
        passo = 1.1 if evento.angleDelta().y() > 0 else 1 / 1.1
        if self.ferramenta == FERRAMENTA_PINCEL:
            self.espessura = min(max(self.espessura * passo,
                                     ESPESSURA_MIN), ESPESSURA_MAX)
            self.aviso.emit(f"Pincel: {self.espessura * 100:.1f}% da página")
            self.update()
        elif self.ferramenta in (FERRAMENTA_VARINHA, FERRAMENTA_COR):
            self.tolerancia = int(min(max(self.tolerancia * passo,
                                          TOLERANCIA_MIN), TOLERANCIA_MAX))
            self.aviso.emit(f"Varinha: tolerância {self.tolerancia}")
        else:
            super().wheelEvent(evento)

    def keyPressEvent(self, evento) -> None:  # noqa: N802
        if evento.key() == Qt.Key_Escape and self._pontos_poligono:
            self._pontos_poligono.clear()
            self.update()
            return
        if evento.matches(Qt.Key_Z) or (
                evento.key() == Qt.Key_Z and evento.modifiers() & Qt.ControlModifier):
            self.desfazer()
            return
        super().keyPressEvent(evento)

    # --- as ferramentas que precisam olhar a imagem -----------------------

    def _nova(self, forma: str, pontos: list) -> Regiao:
        return Regiao(
            tipo=self.tipo, forma=forma, pontos=pontos, operacao=self.operacao,
            origem=MAO, espessura=self.espessura,
        )

    def _varinha(self, ponto: tuple[float, float]) -> None:
        """Pega a mancha inteira da cor onde se clicou.

        E o preenchimento por semente do Photoshop: cresce a partir do ponto
        enquanto a cor nao se afastar mais que a tolerancia. O resultado vira
        POLIGONO, e nao pixels, para poder ser editado depois como qualquer
        outra marcacao.
        """
        if self._img is None:
            return
        altura, largura = self._img.shape[:2]
        x = int(min(max(ponto[0], 0.0), 0.999) * largura)
        y = int(min(max(ponto[1], 0.0), 0.999) * altura)

        # numa pagina de 300 DPI o preenchimento em resolucao cheia demora e o
        # resultado nao fica melhor: a marcacao e uma area, nao um contorno fino
        escala = min(1.0, 900 / max(altura, largura))
        img = cv2.resize(self._img, (max(8, int(largura * escala)),
                                     max(8, int(altura * escala))),
                         interpolation=cv2.INTER_AREA) if escala < 1 else self._img
        h2, w2 = img.shape[:2]
        semente = (int(x * escala), int(y * escala))

        mascara = np.zeros((h2 + 2, w2 + 2), np.uint8)
        tolerancia = (self.tolerancia,) * 3
        try:
            cv2.floodFill(img.copy(), mascara, semente, 255,
                          tolerancia, tolerancia,
                          cv2.FLOODFILL_MASK_ONLY | (255 << 8) | 4)
        except cv2.error:
            self.aviso.emit("Não consegui pegar essa área. Tente outro ponto.")
            return

        achada = mascara[1:-1, 1:-1] > 0
        if achada.mean() < 0.0002:
            self.aviso.emit("Área pequena demais. Aumente a tolerância com a roda.")
            return

        regioes = de_mascara(achada.astype(np.uint8), tipo=self.tipo, origem=MAO,
                             area_minima=0.0002)
        if not regioes:
            self.aviso.emit("Não consegui transformar isso em uma área.")
            return
        self._marcar()
        for regiao in regioes:
            regiao.operacao = self.operacao
            regiao.filtro = self.filtro_da_regiao
            self.selecao.acrescentar(regiao)
        self.selecao_mudou.emit()
        self.update()

    def _tudo_desta_cor(self, ponto: tuple[float, float]) -> None:
        """Pega TUDO daquela cor na pagina, e nao so a mancha onde se clicou.

        A varinha comum cresce a partir do ponto e para quando a cor muda -
        entao ela pega uma pauta vermelha, e nao as vinte pautas da folha. Esta
        aqui olha a pagina inteira e marca todo pixel parecido com o que foi
        clicado, esteja onde estiver. E o "selecionar faixa de cor" do
        Photoshop.

        Serve justamente para consertar o que o detector erra: a rubricacao
        vermelha espalhada, o carimbo, a mancha de tinta de uma cor so.

        A comparacao e feita em LAB e sem o L, ou seja, so pelo MATIZ: assim a
        parte iluminada e a parte na sombra da mesma tinta contam como a mesma
        cor. Comparar em RGB separaria as duas, e quem clicasse no vermelho
        claro nao pegaria o vermelho escuro da mesma pauta.
        """
        if self._img is None:
            return
        altura, largura = self._img.shape[:2]
        x = int(min(max(ponto[0], 0.0), 0.999) * largura)
        y = int(min(max(ponto[1], 0.0), 0.999) * altura)

        escala = min(1.0, 900 / max(altura, largura))
        img = cv2.resize(self._img, (max(8, int(largura * escala)),
                                     max(8, int(altura * escala))),
                         interpolation=cv2.INTER_AREA) if escala < 1 else self._img

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.int16)
        alvo = lab[min(int(y * escala), lab.shape[0] - 1),
                   min(int(x * escala), lab.shape[1] - 1)]
        distancia = np.abs(lab[:, :, 1:] - alvo[1:]).sum(axis=2)
        parecido = (distancia <= self.tolerancia).astype(np.uint8)

        # Tira o respingo solto e fecha o buraco de um pixel, para a marcacao
        # sair em manchas e nao em poeira.
        nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        parecido = cv2.morphologyEx(parecido, cv2.MORPH_OPEN, nucleo)
        parecido = cv2.morphologyEx(parecido, cv2.MORPH_CLOSE, nucleo)

        if parecido.mean() < 0.0002:
            self.aviso.emit("Quase nada dessa cor. Aumente a tolerância com a roda.")
            return
        if parecido.mean() > 0.97:
            self.aviso.emit("Essa cor cobre a página toda. Diminua a tolerância.")
            return

        regioes = de_mascara(parecido, tipo=self.tipo, origem=MAO,
                             area_minima=0.0002)
        if not regioes:
            self.aviso.emit("Não consegui transformar isso em uma área.")
            return

        self._marcar()
        for regiao in regioes:
            regiao.operacao = self.operacao
            regiao.filtro = self.filtro_da_regiao
            self.selecao.acrescentar(regiao)
        self.aviso.emit(
            f"Peguei {parecido.mean():.0%} da página nessa cor, "
            f"em {len(regioes)} pedaços.")
        self.selecao_mudou.emit()
        self.update()

    def selecionar_com_a_rede(self, ponto: tuple[float, float]) -> bool:
        """Clique assistido pela rede: ela recorta a figura sob o ponto.

        Devolve False se o modelo nao estiver instalado - o programa continua
        funcionando sem ele, so sem este atalho.
        """
        if self._img is None:
            return False
        try:
            from core.rede_selecao import recortar_no_ponto
        except Exception:  # noqa: BLE001
            self.aviso.emit("A seleção assistida não está disponível.")
            return False

        mascara = recortar_no_ponto(self._img, ponto)
        if mascara is None or not mascara.any():
            self.aviso.emit("Não consegui recortar nada aí.")
            return False

        regioes = de_mascara(mascara.astype(np.uint8), tipo=self.tipo,
                             origem=MAO, area_minima=0.0002)
        if not regioes:
            return False
        self._marcar()
        for regiao in regioes:
            regiao.operacao = self.operacao
            regiao.filtro = self.filtro_da_regiao
            self.selecao.acrescentar(regiao)
        self.selecao_mudou.emit()
        self.update()
        return True


def _longe(a: tuple[float, float], b: tuple[float, float],
           minimo: float = 0.004) -> bool:
    return abs(a[0] - b[0]) > minimo or abs(a[1] - b[1]) > minimo
