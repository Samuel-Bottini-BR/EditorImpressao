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

import atalhos
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

# As duas de NAVEGACAO, novas. Elas nao marcam nada: mudam o que se ve. Antes
# nao havia como olhar a pagina de perto sem sair da tela, e conferir marcacao
# fina - pauta de partitura, contorno de letra - de longe nao da.
FERRAMENTA_ZOOM = "zoom"
FERRAMENTA_MAO = "mao"

FERRAMENTAS_DE_NAVEGACAO = (FERRAMENTA_ZOOM, FERRAMENTA_MAO)

FERRAMENTAS = (
    FERRAMENTA_RETANGULO,
    FERRAMENTA_ELIPSE,
    FERRAMENTA_LACO,
    FERRAMENTA_POLIGONO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_VARINHA,
    FERRAMENTA_COR,
    FERRAMENTA_ZOOM,
    FERRAMENTA_MAO,
)

NOMES_DAS_FERRAMENTAS = {
    FERRAMENTA_RETANGULO: "Retângulo",
    FERRAMENTA_ELIPSE: "Oval",
    FERRAMENTA_LACO: "Laço",
    FERRAMENTA_POLIGONO: "Ponto a ponto",
    FERRAMENTA_PINCEL: "Pincel",
    FERRAMENTA_VARINHA: "Varinha mágica",
    FERRAMENTA_COR: "Pegar tudo desta cor",
    FERRAMENTA_ZOOM: "Zoom",
    FERRAMENTA_MAO: "Mão",
}

# A letra do atalho de cada uma, como no desenho aprovado. Nao conflitam com os
# numeros 1 2 3 4, que continuam trocando o filtro.
ATALHOS_DAS_FERRAMENTAS = {
    FERRAMENTA_RETANGULO: "R",
    FERRAMENTA_ELIPSE: "O",
    FERRAMENTA_LACO: "L",
    FERRAMENTA_POLIGONO: "P",
    FERRAMENTA_PINCEL: "B",
    FERRAMENTA_VARINHA: "V",
    FERRAMENTA_COR: "C",
    FERRAMENTA_ZOOM: "Z",
    FERRAMENTA_MAO: "E",
}

# Registra cada ferramenta no registro único de atalhos (atalhos.py), para a
# tela de Configurações poder listar e remapear - ver `tecla_da_ferramenta`.
for _ferramenta, _tecla_padrao in ATALHOS_DAS_FERRAMENTAS.items():
    atalhos.registrar(f"ferramenta_{_ferramenta}", NOMES_DAS_FERRAMENTAS[_ferramenta],
                       _tecla_padrao)
del _ferramenta, _tecla_padrao


def tecla_da_ferramenta(ferramenta: str) -> str:
    """A tecla de hoje para essa ferramenta - já considera remapeamento."""
    return atalhos.tecla_atual(f"ferramenta_{ferramenta}") or \
        ATALHOS_DAS_FERRAMENTAS.get(ferramenta, "")


def ferramenta_da_tecla(tecla: str) -> str | None:
    """A ferramenta de hoje ligada a essa tecla, ou None. Usa o atalho atual,
    não o padrão - é o que faz o remapeamento funcionar de verdade."""
    for ferramenta in FERRAMENTAS:
        if tecla and tecla_da_ferramenta(ferramenta) == tecla:
            return ferramenta
    return None

# A ordem da trilha. O traco entre a setima e a oitava separa as de MARCAR das
# de NAVEGAR - sao coisas diferentes e nao devem parecer irmas.
ORDEM_DA_TRILHA = (
    FERRAMENTA_RETANGULO, FERRAMENTA_ELIPSE, FERRAMENTA_LACO,
    FERRAMENTA_POLIGONO, FERRAMENTA_PINCEL, FERRAMENTA_VARINHA,
    FERRAMENTA_COR,
    FERRAMENTA_ZOOM, FERRAMENTA_MAO,
)

AJUDA_DAS_FERRAMENTAS = {
    FERRAMENTA_RETANGULO: "Arraste de um canto ao outro.",
    FERRAMENTA_ELIPSE: "Arraste para desenhar um oval.",
    FERRAMENTA_LACO: "Contorne a área com o botão apertado.",
    FERRAMENTA_POLIGONO: "Clique ponto a ponto. Duplo clique fecha.",
    FERRAMENTA_PINCEL: "Pinte por cima. A roda do mouse muda a espessura.",
    FERRAMENTA_VARINHA: "Clique numa cor e ela pega a mancha inteira.",
    FERRAMENTA_COR: "Clique numa cor e ela pega TUDO daquela cor na página. "
                    "A roda do mouse muda o quanto a cor pode variar.",
    FERRAMENTA_ZOOM: "Clique para aproximar. Com Alt, afasta. "
                     "A roda do mouse também aproxima e afasta.",
    FERRAMENTA_MAO: "Arraste para andar pela página aproximada.",
}

# Ate onde da para aproximar. Abaixo de 1 a pagina ficaria menor que a area, o
# que nao serve para nada aqui.
ZOOM_MIN, ZOOM_MAX = 1.0, 8.0
PASSO_DO_ZOOM = 1.25

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

# Escolher por cor trabalha em resolucao alta e com pouca simplificacao: o
# alvo dela e coisa fina - pauta de partitura, contorno de letra rubricada.
# Medido na pagina 126 do Graduale, a 900 px a pauta saia picada; a 2000 ela
# sai inteira.
LADO_DA_ESCOLHA_POR_COR = 2000
AREA_MINIMA_DA_COR = 0.00002    # pedaco menor que isto e respingo
TOLERANCIA_DA_COR = 0.0008      # simplificacao do contorno, 5x mais fina

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
        """Comeca sem imagem, com a ferramenta Retangulo e uma Selecao vazia.
        Quem usa o widget chama definir_imagem/definir_selecao depois."""
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

        # Zoom e deslocamento. 1,0 quer dizer "do tamanho da area". Como toda a
        # geometria sai de _calcular_area, as alcas e a marcacao continuam no
        # lugar certo em qualquer aproximacao, sem conta nenhuma a mais.
        self.zoom = 1.0
        self.deslocamento = QPoint(0, 0)
        self._arrastando_vista = False
        self._ponto_do_arrasto = QPoint()
        self._deslocamento_inicial = QPoint()

    # --- zoom e deslocamento ---------------------------------------------

    def definir_zoom(self, zoom: float) -> None:
        """Ajusta o zoom (preso a ZOOM_MIN/MAX). Volta o deslocamento a zero
        se cair de volta em 100%, para nao deixar a pagina "presa" fora do centro."""
        novo = float(min(max(zoom, ZOOM_MIN), ZOOM_MAX))
        if abs(novo - self.zoom) < 1e-4:
            return
        self.zoom = novo
        if self.zoom <= 1.0:
            self.deslocamento = QPoint(0, 0)
        self.aviso.emit(f"Zoom: {self.zoom * 100:.0f}%")
        self.update()

    def ajustar_a_tela(self) -> None:
        """Volta ao zoom 100% (a pagina inteira cabendo na area)."""
        self.zoom = 1.0
        self.deslocamento = QPoint(0, 0)
        self.aviso.emit("Zoom: 100%")
        self.update()

    # --- entrada ----------------------------------------------------------

    def definir_imagem(self, img: np.ndarray | None) -> None:
        """Poe a imagem de fundo (converte BGR/cinza para QPixmap). None limpa a tela."""
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
        """Troca a Selecao mostrada/editada (ex.: ao trocar de página) e
        limpa o historico de desfazer, que so vale para a selecao anterior."""
        self.selecao = selecao
        self._marcos.clear()
        self.update()

    def definir_ferramenta(self, ferramenta: str) -> None:
        """Troca a ferramenta ativa: muda o cursor e a dica na barra de status."""
        if ferramenta not in FERRAMENTAS:
            return
        self.ferramenta = ferramenta
        self._pontos_poligono.clear()
        self.aviso.emit(AJUDA_DAS_FERRAMENTAS[ferramenta])
        # O cursor diz qual ferramenta esta na mao sem a pessoa ter de olhar
        # para a trilha.
        self.setCursor({
            FERRAMENTA_MAO: Qt.OpenHandCursor,
            FERRAMENTA_ZOOM: Qt.CrossCursor,
        }.get(ferramenta, Qt.ArrowCursor))
        self.update()

    def definir_tipo(self, tipo: str) -> None:
        """Que tipo (gravura/letra/papel) a proxima marcacao vai receber."""
        if tipo in (GRAVURA, LETRA, PAPEL):
            self.tipo = tipo
            self.update()

    def definir_operacao(self, operacao: str) -> None:
        """Somar ou subtrair - o modo que a proxima marcacao vai usar."""
        self.operacao = SUBTRAIR if operacao == SUBTRAIR else SOMAR
        self.update()

    def definir_filtro_da_regiao(self, filtro: str) -> None:
        """Que filtro vale so no que for marcado daqui em diante."""
        self.filtro_da_regiao = filtro or ""
        self.update()

    # --- desfazer ---------------------------------------------------------

    @property
    def pode_desfazer(self) -> bool:
        """Ha alguma acao de marcacao para desfazer nesta pagina?"""
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
        """Guarda um marco de desfazer (tamanho da lista de regiões ANTES da
        proxima acao). Toda acao so ACRESCENTA regiões, entao guardar so o
        tamanho basta - nao precisa copiar a lista inteira."""
        self._marcos.append(len(self.selecao.regioes))
        if len(self._marcos) > 200:
            self._marcos.pop(0)

    def _acrescentar(self, regiao: Regiao) -> None:
        """Aplica o filtro-do-pedaço atual a regiao, marca para desfazer e
        adiciona a selecao."""
        if not regiao.valida():
            return
        regiao.filtro = self.filtro_da_regiao
        self._marcar()
        self.selecao.acrescentar(regiao)
        self.selecao_mudou.emit()
        self.update()

    # --- geometria --------------------------------------------------------

    def _calcular_area(self) -> QRect:
        """Onde a pagina e desenhada, ja com o zoom e o deslocamento.

        Toda a geometria da marcacao sai daqui. Por isso as alcas e as regioes
        continuam certas em qualquer aproximacao: quem muda e a area, e nao
        cada conta espalhada pelo arquivo.
        """
        if self._pixmap is None or self._pixmap.isNull():
            return QRect()
        largura, altura = self._pixmap.width(), self._pixmap.height()
        escala = min(self.width() / largura, self.height() / altura) * self.zoom
        w, h = max(1, int(largura * escala)), max(1, int(altura * escala))
        x = (self.width() - w) // 2 + self.deslocamento.x()
        y = (self.height() - h) // 2 + self.deslocamento.y()
        return QRect(x, y, w, h)

    def _para_fracao(self, ponto: QPoint) -> tuple[float, float]:
        """Ponto da tela para fracao da imagem, de 0 a 1."""
        a = self._area
        if a.width() <= 0 or a.height() <= 0:
            return (0.0, 0.0)
        x = (ponto.x() - a.left()) / a.width()
        y = (ponto.y() - a.top()) / a.height()
        return (min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0))

    def _para_tela(self, fx: float, fy: float) -> QPoint:
        """Fracao da imagem (0 a 1) para ponto de tela - o inverso de _para_fracao."""
        a = self._area
        return QPoint(int(a.left() + fx * a.width()), int(a.top() + fy * a.height()))

    # --- desenho na tela --------------------------------------------------

    # Fundo em volta da pagina. E o mesmo tom da area da pagina no desenho
    # aprovado - um cinza-creme claro, nao preto.
    #
    # Era quase preto, 28-28-30, escolhido para as cores da marcacao saltarem.
    # O efeito na tela foi outro: a area de marcar e larga e baixa, uma pagina
    # em pe cabe nela como uma fatia fina no meio, e o fundo tomava o resto.
    # O que o Samuel viu foi "a area de visualizacao aparecendo como um
    # retangulo preto" - e nao era falha de renderizacao, era este fundo.
    #
    # As cores da marcacao nao perdem nada: elas sao pintadas por cima da
    # PAGINA, e nao do fundo.
    FUNDO_DA_AREA = QColor("#f1efe8")

    def paintEvent(self, evento: QPaintEvent) -> None:  # noqa: N802 (nome do Qt)
        """Desenha o fundo, a pagina, a marcacao ja feita e o que esta sendo
        desenhado no momento (arrasto em andamento, ou poligono ponto a ponto)."""
        pintor = QPainter(self)
        pintor.fillRect(self.rect(), self.FUNDO_DA_AREA)
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
        """A forma em andamento (retangulo/elipse/laço/pincel sendo arrastado,
        ou os pontos ja marcados do poligono)."""
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
        """O retangulo entre o primeiro e o ultimo ponto arrastados, em tela."""
        a = self._para_tela(*self._pontos[0])
        b = self._para_tela(*self._pontos[-1])
        return QRect(a, b).normalized()

    def _espessura_na_tela(self) -> int:
        """Converte a espessura do pincel (fracao da pagina) para pixels de tela."""
        lado = min(self._area.width(), self._area.height())
        return max(2, int(self.espessura * lado))

    # --- mouse ------------------------------------------------------------

    def mousePressEvent(self, evento: QMouseEvent) -> None:  # noqa: N802
        """Comeca a acao da ferramenta ativa: zoom/mao navegam sem marcar
        nada; varinha/cor/poligono agem no clique; as demais comecam um
        arrasto que termina em mouseReleaseEvent."""
        if self._pixmap is None or evento.button() != Qt.LeftButton:
            return
        self._area = self._calcular_area()

        # As duas de navegacao vem antes: elas nao marcam nada, e nao devem
        # deixar rastro na selecao.
        if self.ferramenta == FERRAMENTA_ZOOM:
            afastar = bool(evento.modifiers() & Qt.AltModifier)
            self.definir_zoom(self.zoom / PASSO_DO_ZOOM if afastar
                              else self.zoom * PASSO_DO_ZOOM)
            return
        if self.ferramenta == FERRAMENTA_MAO:
            self._arrastando_vista = True
            self._ponto_do_arrasto = evento.position().toPoint()
            self._deslocamento_inicial = QPoint(self.deslocamento)
            self.setCursor(Qt.ClosedHandCursor)
            return

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
        """Continua o arrasto: move a vista (ferramenta Mao) ou acrescenta
        pontos a forma sendo desenhada."""
        if self._arrastando_vista:
            andou = evento.position().toPoint() - self._ponto_do_arrasto
            self.deslocamento = self._deslocamento_inicial + andou
            self.update()
            return
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
        """Termina o arrasto e transforma os pontos acumulados numa Regiao de
        verdade (retangulo/elipse precisam de 2 pontos distantes, laço de 3+,
        pincel de qualquer quantidade)."""
        if self._arrastando_vista:
            self._arrastando_vista = False
            self.setCursor(Qt.OpenHandCursor)
            return
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
        elif self.ferramenta in FERRAMENTAS_DE_NAVEGACAO:
            self.definir_zoom(self.zoom * (PASSO_DO_ZOOM if passo > 1
                                           else 1 / PASSO_DO_ZOOM))
        else:
            super().wheelEvent(evento)

    def keyPressEvent(self, evento) -> None:  # noqa: N802
        """Esc cancela um poligono em andamento; Ctrl+Z desfaz a ultima marcacao."""
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
        """Monta uma Regiao com o tipo/operacao/espessura correntes do editor."""
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

        # Em resolucao cheia: quem escolhe por cor esta atras de coisa fina -
        # uma pauta de dois pixels, o contorno de uma letra rubricada. A 900
        # px a pauta some no reamostrar, e a marcacao sai grossa e picada.
        escala = min(1.0, LADO_DA_ESCOLHA_POR_COR / max(altura, largura))
        img = cv2.resize(self._img, (max(8, int(largura * escala)),
                                     max(8, int(altura * escala))),
                         interpolation=cv2.INTER_AREA) if escala < 1 else self._img

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(np.int16)
        alvo = lab[min(int(y * escala), lab.shape[0] - 1),
                   min(int(x * escala), lab.shape[1] - 1)]
        distancia = np.abs(lab[:, :, 1:] - alvo[1:]).sum(axis=2)
        parecido = (distancia <= self.tolerancia).astype(np.uint8)

        # Fecha o buraco de um pixel, para a marcacao sair em manchas e nao
        # em poeira. NAO se abre a mascara: a abertura come a pauta fina, que
        # e justamente o que se estava tentando pegar.
        nucleo = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        parecido = cv2.morphologyEx(parecido, cv2.MORPH_CLOSE, nucleo)

        if parecido.mean() < 0.0002:
            self.aviso.emit("Quase nada dessa cor. Aumente a tolerância com a roda.")
            return
        if parecido.mean() > 0.97:
            self.aviso.emit("Essa cor cobre a página toda. Diminua a tolerância.")
            return

        regioes = de_mascara(parecido, tipo=self.tipo, origem=MAO,
                             area_minima=AREA_MINIMA_DA_COR,
                             tolerancia=TOLERANCIA_DA_COR)
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
    """Os dois pontos (em fracao da pagina) estao mais longe que `minimo`?
    Usado para nao guardar ponto demais no laço/pincel (um traco de mil
    pontos nao e editavel nem cabe bem no arquivo de projeto)."""
    return abs(a[0] - b[0]) > minimo or abs(a[1] - b[1]) > minimo
