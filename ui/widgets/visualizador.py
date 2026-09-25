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

from core.folha import (  # noqa: F401 - reexportados, ver comentario abaixo
    TAMANHOS_DE_PAPEL_CM,
    medidas_do_recorte_em_cm,
    recorte_cabe_na_pagina,
    recorte_para_tamanho_cm,
)
from ui.estilo import AZUL, LARANJA, TEXTO_FRACO, VERDE

# Mesmo tom da área de marcar (ui/widgets/editor_selecao.py) - um cinza-creme
# claro, para sempre sobrar uma faixa visível ao redor da página, mesmo no
# zoom "ajustar à tela". Branco puro (o fundo de antes) ficava invisível
# contra o papel escaneado, que já é quase branco.
FUNDO_DA_AREA = QColor("#f1efe8")

# Folga reservada ao redor da página no zoom "ajustar à tela" (zoom 1,0), em
# pixels de tela. Sem ela a imagem preenchia 100% do widget e a moldura
# nunca aparecia de cara ao abrir a página.
PADDING_MOLDURA = 32

MODO_NENHUM = "nenhum"
MODO_CORTE = "corte"
MODO_RECORTE = "recorte"
MODO_ANGULO = "angulo"

# Fase 2 (item 1.3/1.4 do handoff antigo, aprovada pelo Samuel em 22/09/2026
# depois de ficar de fora da entrega original do plano): arrastar o
# CONTEÚDO (a página já recortada) dentro da folha maior - distinto de
# MODO_RECORTE, que edita o RECORTE (a fração da imagem ORIGINAL). Só
# existe quando há uma folha maior que o conteúdo (`compor_na_folha` sobrou
# margem de verdade) - ver `ui/tela_conferir.py::_alternar_mover_conteudo`.
MODO_CONTEUDO = "conteudo"

# Como arrastar uma alça do retângulo de recorte muda os outros lados.
# LIVRE: cada lado se move sozinho (comportamento de sempre).
# ESPELHADO: mexer num lado move o lado oposto na mesma medida, mantendo o
# centro do retângulo parado.
# PROPORCAO: qualquer alça redimensiona os 4 lados mantendo a razão
# largura/altura atual, a partir do centro.
RECORTE_LIVRE = "livre"
RECORTE_ESPELHADO = "espelhado"
RECORTE_PROPORCAO = "proporcao"

TAMANHO_ALCA = 12
DISTANCIA_PEGA = 14
GRAUS_POR_PIXEL = 0.02  # sensibilidade do giro ao arrastar

# Zoom: 1,0 e "ajustado a tela". Nao passa de 8x porque acima disso a previa
# ja mostraria o pixel, e nao mais detalhe.
ZOOM_MIN, ZOOM_MAX = 1.0, 8.0
PASSO_DA_RODA = 1.25


# `medidas_do_recorte_em_cm`, `TAMANHOS_DE_PAPEL_CM`, `recorte_para_tamanho_cm`
# e `recorte_cabe_na_pagina` moraram aqui e MUDARAM DE LUGAR (seção 3a do
# plano "corrigir bugs do teste do Boécio"): são puramente aritméticas, sem
# nada de PySide6, e agora moram em `core/folha.py` - importadas no topo
# deste arquivo e reexportadas, então nada que já importava daqui quebra.

# --- Problema 1, opções B e C: tamanho e posição do CONTEÚDO dentro da folha
# -----------------------------------------------------------------------------
# `conteudo` é sempre (x, y, w, h) em fração da FOLHA (0-1), igual ao
# `recorte` - mas é outra coisa: onde o material escaneado fica desenhado
# dentro da página final, depois que o tamanho da folha (A) já foi decidido.

GUIA_CENTRO_H = "centro_h"
GUIA_CENTRO_V = "centro_v"
GUIA_BORDA_ESQUERDA = "borda_esquerda"
GUIA_BORDA_DIREITA = "borda_direita"
GUIA_BORDA_CIMA = "borda_cima"
GUIA_BORDA_BAIXO = "borda_baixo"

TOLERANCIA_DA_GUIA = 0.01  # 1% da folha - perto o bastante de "bateu"


def _candidatos_do_eixo(inicio: float, tamanho: float) -> list[tuple[float, str, float]]:
    """(distância até a guia, nome da guia, posição que encaixaria nela)."""
    return [
        (abs((inicio + tamanho / 2) - 0.5), "centro", 0.5 - tamanho / 2),
        (abs(inicio), "inicio", 0.0),
        (abs(1.0 - (inicio + tamanho)), "fim", 1.0 - tamanho),
    ]


def guias_ativas(
    conteudo: tuple[float, float, float, float],
    tolerancia: float = TOLERANCIA_DA_GUIA,
) -> list[str]:
    """As guias que o conteúdo já está bem perto de bater, para desenhar."""
    x, y, w, h = conteudo
    ativas = []
    nomes_x = {"centro": GUIA_CENTRO_H, "inicio": GUIA_BORDA_ESQUERDA, "fim": GUIA_BORDA_DIREITA}
    nomes_y = {"centro": GUIA_CENTRO_V, "inicio": GUIA_BORDA_CIMA, "fim": GUIA_BORDA_BAIXO}
    for distancia, nome, _posicao in _candidatos_do_eixo(x, w):
        if distancia <= tolerancia:
            ativas.append(nomes_x[nome])
    for distancia, nome, _posicao in _candidatos_do_eixo(y, h):
        if distancia <= tolerancia:
            ativas.append(nomes_y[nome])
    return ativas


def encaixar_no_ima(
    conteudo: tuple[float, float, float, float],
    tolerancia: float = TOLERANCIA_DA_GUIA,
) -> tuple[float, float, float, float]:
    """Puxa a posição do conteúdo para a guia mais próxima de cada eixo, se
    estiver dentro da tolerância. Nunca muda w/h, só x/y - o ímã posiciona,
    não redimensiona."""
    x, y, w, h = conteudo

    distancia_x, _nome, nova_x = min(_candidatos_do_eixo(x, w), key=lambda c: c[0])
    if distancia_x <= tolerancia:
        x = nova_x

    distancia_y, _nome, nova_y = min(_candidatos_do_eixo(y, h), key=lambda c: c[0])
    if distancia_y <= tolerancia:
        y = nova_y

    return (x, y, w, h)


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
    # (x, y, largura, altura) em fracao do CANVAS (a folha) - Fase 2, ver
    # MODO_CONTEUDO. `ui/tela_conferir.py::_mover_conteudo` converte para
    # (escala, deslocamento) antes de gravar em ConfigPagina.
    conteudo_movido = Signal(tuple)
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
        self.modo_arraste_recorte = RECORTE_LIVRE
        self._dpi = 300.0

        self._arrastando: str | None = None
        self._ponto_inicial = QPoint()
        self._angulo_inicial = 0.0
        self._recorte_inicial = self.recorte

        # Passo 8 do plano (item 2/4 do teste do Boécio, decisão 3): quando a
        # imagem exibida é a página JÁ COMPOSTA na folha (recorte + margem
        # branca, `core/folha.py::compor_na_folha`), o CONTEÚDO editável (o
        # recorte) não ocupa mais o pixmap inteiro - só uma fração dele.
        # `_retangulo_conteudo` guarda essa fração (padrão: o pixmap inteiro,
        # ou seja, "sem composição nenhuma" - o comportamento de sempre,
        # usado por toda tela que nunca chama `definir_composicao`, como as
        # abas Corte/Ângulo). `_tamanho_conteudo_px` é o tamanho do CONTEÚDO
        # em pixels (não do canvas maior) - é o que `tamanho_da_pagina_px()`
        # devolve quando setado, porque é o que os cálculos de cm do recorte
        # (`ui/tela_conferir.py::_escolher_tamanho_da_folha`) precisam.
        self._retangulo_conteudo: tuple[float, float, float, float] = (0.0, 0.0, 1.0, 1.0)
        self._tamanho_conteudo_px: tuple[int, int] | None = None

        # Fase 2 (MODO_CONTEUDO): estado do arrasto do conteúdo dentro da
        # folha, e quais guias estão "grudando" agora (para desenhar).
        self._retangulo_conteudo_inicial = self._retangulo_conteudo
        self._guias_ativas_agora: list[str] = []

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

    def _escala_ajustada(self) -> float:
        """A escala de "ajustar à tela", já descontando a folga da moldura."""
        largura_util = max(1.0, self.width() - 2 * PADDING_MOLDURA)
        altura_util = max(1.0, self.height() - 2 * PADDING_MOLDURA)
        return min(largura_util / self._pixmap.width(),
                   altura_util / self._pixmap.height())

    def _largura_base(self) -> float:
        """Largura que a imagem teria ajustada a janela, antes do zoom."""
        if self._pixmap is None or self._pixmap.isNull():
            return 0.0
        return self._pixmap.width() * self._escala_ajustada()

    def _altura_base(self) -> float:
        if self._pixmap is None or self._pixmap.isNull():
            return 0.0
        return self._pixmap.height() * self._escala_ajustada()

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

    def definir_modo_arraste_recorte(self, modo: str) -> None:
        self.modo_arraste_recorte = modo

    def definir_dpi(self, dpi: float) -> None:
        """A resolução com que a prévia atual foi renderizada - ver
        `medidas_do_recorte_em_cm`. Sem isso os números em cm ficam errados
        sempre que a qualidade da prévia ou o zoom-de-arrasto mudam."""
        if dpi > 0:
            self._dpi = float(dpi)

    def dpi_atual(self) -> float:
        return self._dpi

    def tamanho_da_pagina_px(self) -> tuple[int, int]:
        """(largura, altura) em pixels do CONTEÚDO (o recorte) atual, ou
        (0, 0) sem imagem.

        Passo 8 do plano: quando a prévia mostra a página já composta numa
        folha maior (`definir_composicao`), isto continua sendo o tamanho do
        CONTEÚDO - não o do canvas maior -, porque é o que os cálculos de cm
        do recorte precisam (`ui/tela_conferir.py::_escolher_tamanho_da_folha`).
        Sem composição (o caso de sempre), é o tamanho do próprio pixmap.
        """
        if self._tamanho_conteudo_px is not None:
            return self._tamanho_conteudo_px
        if self._pixmap is None:
            return (0, 0)
        return (self._pixmap.width(), self._pixmap.height())

    def definir_composicao(
        self, retangulo_conteudo: tuple[float, float, float, float],
        tamanho_conteudo_px: tuple[int, int],
    ) -> None:
        """Onde o CONTEÚDO (o recorte) fica dentro do pixmap atual, quando o
        pixmap é a página já composta numa folha maior (decisão 3 do plano).

        `retangulo_conteudo` é (x, y, w, h) em fração do PIXMAP INTEIRO -
        mesmo formato de `core.folha.conteudo_como_retangulo`. (0,0,1,1)
        (o padrão, antes desta função ser chamada) quer dizer "o conteúdo
        ocupa o pixmap inteiro" - sem folha escolhida, ou quando a folha não
        coube e a composição foi abortada (rede de segurança) -, e nesse
        caso todo o mapeamento tela<->fração volta a ser idêntico ao de
        antes deste passo.
        """
        self._retangulo_conteudo = tuple(retangulo_conteudo)
        self._tamanho_conteudo_px = tuple(tamanho_conteudo_px)
        self.update()

    def _area_do_conteudo(self) -> QRect:
        """A região de `self._area` (o pixmap inteiro, na tela) onde o
        CONTEÚDO (o recorte) está desenhado. Sem composição, é `self._area`
        inteira - por isso todo o resto do modo recorte (`_retangulo_recorte`,
        `_mover_recorte`) usa isto no lugar de `self._area` direto, e continua
        funcionando exatamente igual a antes quando não há composição."""
        x, y, w, h = self._retangulo_conteudo
        if (x, y, w, h) == (0.0, 0.0, 1.0, 1.0):
            return self._area
        return QRect(
            self._area.left() + int(x * self._area.width()),
            self._area.top() + int(y * self._area.height()),
            int(w * self._area.width()),
            int(h * self._area.height()),
        )

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento: QPaintEvent) -> None:  # noqa: N802 (nome do Qt)
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), FUNDO_DA_AREA)

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
        elif self.modo == MODO_CONTEUDO:
            self._desenhar_conteudo(pintor)

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

        # Escurece o que vai ser jogado fora do recorte - mas só dentro da
        # ÁREA DO CONTEÚDO, nunca em `self._area` inteira.
        #
        # BUG REAL achado no teste ao vivo do Samuel (22/09/2026: "a área da
        # folha ao redor do recorte não está branca de verdade"): antes do
        # passo 8, `self._area` era sempre a imagem inteira e o que ficava
        # fora do recorte era conteúdo que seria cortado - escurecer fazia
        # sentido. Depois do passo 8, `self._area` pode ser o canvas da
        # FOLHA (maior que o conteúdo, com margem branca de verdade
        # desenhada por `compor_na_folha`) - e a mesma sombra passou a cobrir
        # também essa margem branca, tingindo-a de cinza (preto a 70/255 de
        # opacidade sobre 255 dá 185 - exatamente o valor medido ao
        # reproduzir). Ver `tests/test_visualizador.py`,
        # `test_margem_da_folha_fica_branca_de_verdade`.
        area = self._area_do_conteudo()
        sombra = QColor(0, 0, 0, 70)
        pintor.setPen(Qt.NoPen)
        pintor.setBrush(sombra)
        pintor.drawRect(QRect(area.left(), area.top(), area.width(),
                              r.top() - area.top()))
        pintor.drawRect(QRect(area.left(), r.bottom(), area.width(),
                              area.bottom() - r.bottom()))
        pintor.drawRect(QRect(area.left(), r.top(), r.left() - area.left(),
                              r.height()))
        pintor.drawRect(QRect(r.right(), r.top(), area.right() - r.right(), r.height()))

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

        # Os números em cm só aparecem enquanto arrasta (decisão do Samuel) -
        # sempre visível poluiria a tela em quem só está olhando a página.
        if self._arrastando is not None and self._pixmap is not None:
            self._desenhar_medidas_do_recorte(pintor, r)

    def _desenhar_medidas_do_recorte(self, pintor: QPainter, r: QRect) -> None:
        # `self.recorte` é fração do CONTEÚDO - usa o tamanho do conteúdo em
        # px, não o do pixmap inteiro (que pode ser a folha composta, maior).
        largura_conteudo_px, altura_conteudo_px = self.tamanho_da_pagina_px()
        medidas = medidas_do_recorte_em_cm(
            self.recorte, largura_conteudo_px, altura_conteudo_px, self._dpi)

        pintor.setPen(QColor("white"))
        fonte = pintor.font()
        fonte.setPointSize(9)
        pintor.setFont(fonte)

        def etiqueta(centro: QPoint, texto: str) -> None:
            largura = max(48, 10 * len(texto))
            caixa = QRect(centro.x() - largura // 2, centro.y() - 10, largura, 20)
            pintor.setBrush(QColor(17, 24, 39, 210))
            pintor.setPen(Qt.NoPen)
            pintor.drawRoundedRect(caixa, 4, 4)
            pintor.setPen(QColor("white"))
            pintor.drawText(caixa, Qt.AlignCenter, texto)

        alcas = self._alcas(r)
        etiqueta(alcas["o"] + QPoint(-30, 0), f'{medidas["esquerda"]:.2f} cm')
        etiqueta(alcas["l"] + QPoint(30, 0), f'{medidas["direita"]:.2f} cm')
        etiqueta(alcas["n"] + QPoint(0, -18), f'{medidas["cima"]:.2f} cm')
        etiqueta(alcas["s"] + QPoint(0, 18), f'{medidas["baixo"]:.2f} cm')
        etiqueta(
            QPoint(r.center().x(), r.top() - 26),
            f'{medidas["largura_final"]:.2f} × {medidas["altura_final"]:.2f} cm',
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

    def _desenhar_conteudo(self, pintor: QPainter) -> None:
        """MODO_CONTEUDO (Fase 2+3): contorno do conteúdo arrastável, alças
        nos 4 cantos pra redimensionar (proporcional - Fase 3, confirmada
        pelo Samuel em 22/09/2026) + linhas-guia de alinhamento
        (`guias_ativas`), quando alguma estiver ativa.

        As alças são a pista visual que faltava (causa raiz do "ainda não
        consigo movimentar o conteúdo" - ver `mousePressEvent`): sem elas,
        nada na tela mostrava onde o retângulo arrastável começava."""
        r = self._area_do_conteudo()

        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(QPen(QColor(AZUL), 2))
        pintor.drawRect(r)

        pintor.setBrush(QColor(AZUL))
        pintor.setPen(Qt.NoPen)
        for nome, ponto in self._alcas(r).items():
            if nome not in ("no", "ne", "so", "se"):
                continue
            pintor.drawRoundedRect(
                QRect(ponto.x() - TAMANHO_ALCA // 2, ponto.y() - TAMANHO_ALCA // 2,
                      TAMANHO_ALCA, TAMANHO_ALCA), 3, 3,
            )

        if not self._guias_ativas_agora:
            return
        caneta = QPen(QColor(LARANJA), 1, Qt.DashLine)
        pintor.setPen(caneta)
        area = self._area
        if GUIA_CENTRO_H in self._guias_ativas_agora:
            x = area.center().x()
            pintor.drawLine(x, area.top(), x, area.bottom())
        if GUIA_CENTRO_V in self._guias_ativas_agora:
            y = area.center().y()
            pintor.drawLine(area.left(), y, area.right(), y)
        if GUIA_BORDA_ESQUERDA in self._guias_ativas_agora:
            pintor.drawLine(area.left(), area.top(), area.left(), area.bottom())
        if GUIA_BORDA_DIREITA in self._guias_ativas_agora:
            pintor.drawLine(area.right(), area.top(), area.right(), area.bottom())
        if GUIA_BORDA_CIMA in self._guias_ativas_agora:
            pintor.drawLine(area.left(), area.top(), area.right(), area.top())
        if GUIA_BORDA_BAIXO in self._guias_ativas_agora:
            pintor.drawLine(area.left(), area.bottom(), area.right(), area.bottom())

    # --- geometria --------------------------------------------------------

    def _retangulo_recorte(self) -> QRect:
        """`self.recorte` é fração do CONTEÚDO, não do pixmap inteiro - ver
        `_area_do_conteudo` (passo 8 do plano). Sem composição os dois são a
        mesma área, então isto continua idêntico ao de sempre."""
        area = self._area_do_conteudo()
        x, y, w, h = self.recorte
        return QRect(
            area.left() + int(x * area.width()),
            area.top() + int(y * area.height()),
            max(10, int(w * area.width())),
            max(10, int(h * area.height())),
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
        elif self.modo == MODO_CONTEUDO:
            alca = self._alca_conteudo_sob(ponto)
            if alca is not None:
                # Fase 3 (Samuel, 22/09/2026: "quero conseguir redimensionar
                # o conteudo tambem") - arrastar um canto redimensiona.
                self._arrastando = f"conteudo_{alca}"
                self._retangulo_conteudo_inicial = self._retangulo_conteudo
            elif self._area.contains(ponto):
                # BUG REAL achado ao vivo (22/09/2026, reprodução com mouse
                # de verdade): antes só iniciava o arrasto clicando EXATAMENTE
                # em cima do conteúdo, sem nenhuma pista visual (sem alça, sem
                # cursor diferente) de onde esse retângulo começava - um
                # clique real, nunca pixel-perfect, caía na margem branca com
                # facilidade e não fazia nada, o que para o Samuel "parecia
                # simplesmente não funcionar". Agora qualquer clique dentro da
                # folha visível arrasta o conteúdo - como mover uma foto
                # dentro de uma moldura.
                self._arrastando = "conteudo"
                self._retangulo_conteudo_inicial = self._retangulo_conteudo

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
            elif self.modo == MODO_CONTEUDO:
                self._atualizar_cursor_conteudo(ponto)
            return

        if self._arrastando == "corte":
            self._mover_corte(ponto)
        elif self._arrastando == "angulo":
            delta = ponto.x() - self._ponto_inicial.x()
            self.definir_angulo(self._angulo_inicial + delta * GRAUS_POR_PIXEL)
        elif self._arrastando == "conteudo":
            self._mover_conteudo(ponto)
        elif self._arrastando.startswith("conteudo_"):
            self._redimensionar_conteudo(ponto, self._arrastando[len("conteudo_"):])
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
        elif arrastava == "conteudo" or arrastava.startswith("conteudo_"):
            self._guias_ativas_agora = []
            self.conteudo_movido.emit(self._retangulo_conteudo)
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

    def _alca_conteudo_sob(self, ponto: QPoint) -> str | None:
        """Igual a `_alca_sob`, mas só os 4 CANTOS do retângulo do conteúdo -
        redimensionar o conteúdo é sempre proporcional (Fase 3), não tem
        alça de lado (esticar só um lado distorceria a imagem)."""
        cantos = self._alcas(self._area_do_conteudo())
        for nome in ("no", "ne", "so", "se"):
            centro = cantos[nome]
            if (abs(centro.x() - ponto.x()) <= DISTANCIA_PEGA
                    and abs(centro.y() - ponto.y()) <= DISTANCIA_PEGA):
                return nome
        return None

    def _atualizar_cursor_conteudo(self, ponto: QPoint) -> None:
        """MODO_CONTEUDO: cursor de redimensionar sobre um canto, cursor de
        "mover" (mãozinha) sobre o resto da folha - a pista visual que
        faltava pro Samuel achar onde clicar (ver `mousePressEvent`)."""
        alca = self._alca_conteudo_sob(ponto)
        formatos = {
            "no": Qt.SizeFDiagCursor, "se": Qt.SizeFDiagCursor,
            "ne": Qt.SizeBDiagCursor, "so": Qt.SizeBDiagCursor,
        }
        if alca is not None:
            self.setCursor(QCursor(formatos[alca]))
        elif self._area.contains(ponto):
            self.setCursor(QCursor(Qt.SizeAllCursor))
        else:
            self.setCursor(QCursor(Qt.ArrowCursor))

    def _mover_recorte(self, ponto: QPoint) -> None:
        """Calcula o novo recorte a partir do arrasto, em fração 0-1 da página.

        BUG REAL corrigido (achado ao vivo por reprodução real de mouse,
        22/09/2026 - "só abri o selecionador pro lado esquerdo"): o clamp
        final só limitava w/h por BAIXO (`max(minimo, w)`), nunca por CIMA
        antes de clampar x/y. Perto da borda da página, um arrasto que fazia
        w (ou h) passar de `1.0 - x` deixava `x = min(x, 1.0 - w)` com
        `1.0 - w` NEGATIVO - o clamp empurrava o lado ANCORADO (oposto ao que
        estava sendo arrastado) para fora da página, mesmo em alças que nunca
        deveriam mexer nele (ex.: arrastar a alça direita empurrava o lado
        esquerdo para x negativo). Ver `tests/test_visualizador.py`, seção
        "Bug real achado ao vivo".

        A correção: cada modo agora clampa em cima do lado que REALMENTE fica
        parado (a âncora - o lado oposto ao arrastado no modo livre, ou o
        CENTRO nos modos Espelhado/Proporção), nunca em cima de x/y "cru".

        Passo 8 do plano: o arrasto é normalizado pelo tamanho da ÁREA DO
        CONTEÚDO na tela (`_area_do_conteudo`), não mais sempre por
        `self._area` inteira - com uma folha maior que o recorte, o conteúdo
        ocupa só uma fração do pixmap exibido, e um arrasto de N pixels de
        tela precisa valer uma fração MAIOR do recorte (o conteúdo é menor
        na tela). Sem composição os dois são a mesma área.
        """
        area = self._area_do_conteudo()
        if area.width() <= 0 or area.height() <= 0:
            return
        dx = (ponto.x() - self._ponto_inicial.x()) / area.width()
        dy = (ponto.y() - self._ponto_inicial.y()) / area.height()
        x, y, w, h = self._recorte_inicial
        lado = self._arrastando or ""
        minimo = 0.05

        if lado == "mover":
            # Só translada - w/h nunca mudam aqui, então `1.0 - w` já é
            # sempre válido (w/h vieram de um recorte que já era válido).
            w, h = max(minimo, w), max(minimo, h)
            x = min(max(0.0, x + dx), 1.0 - w)
            y = min(max(0.0, y + dy), 1.0 - h)
            self.definir_recorte((x, y, w, h))
            return

        if self.modo_arraste_recorte == RECORTE_ESPELHADO:
            # O lado oposto ao arrastado se move a mesma medida, para o
            # centro do retângulo nunca sair do lugar - então é o CENTRO que
            # é a âncora aqui, não um dos lados. O maior retângulo centrado
            # em `centro` que ainda cabe em [0,1] é o limite de verdade.
            centro_x, centro_y = x + w / 2, y + h / 2
            if "o" in lado:
                w = w - 2 * dx
            if "l" in lado or "e" in lado:
                w = w + 2 * dx
            if "n" in lado:
                h = h - 2 * dy
            if "s" in lado:
                h = h + 2 * dy
            largura_max = 2 * min(centro_x, 1.0 - centro_x)
            altura_max = 2 * min(centro_y, 1.0 - centro_y)
            w = min(max(minimo, w), max(minimo, largura_max))
            h = min(max(minimo, h), max(minimo, altura_max))
            self.definir_recorte((centro_x - w / 2, centro_y - h / 2, w, h))
            return

        if self.modo_arraste_recorte == RECORTE_PROPORCAO:
            # Também ancorado no centro (a razão largura/altura não pode
            # mudar, então os dois eixos são limitados pelo MESMO fator).
            centro_x, centro_y = x + w / 2, y + h / 2
            fatores = []
            if "o" in lado or "l" in lado or "e" in lado:
                sinal = -1.0 if "o" in lado else 1.0
                fatores.append(1.0 + (sinal * 2 * dx) / w if w else 1.0)
            if "n" in lado or "s" in lado:
                sinal = -1.0 if "n" in lado else 1.0
                fatores.append(1.0 + (sinal * 2 * dy) / h if h else 1.0)
            fator = sum(fatores) / len(fatores) if fatores else 1.0

            menor_lado = min(w, h)
            fator_minimo = (minimo / menor_lado) if menor_lado else 0.0
            fator_max_x = (2 * min(centro_x, 1.0 - centro_x)) / w if w else fator
            fator_max_y = (2 * min(centro_y, 1.0 - centro_y)) / h if h else fator
            fator = min(max(fator, fator_minimo), min(fator_max_x, fator_max_y))

            w, h = w * fator, h * fator
            self.definir_recorte((centro_x - w / 2, centro_y - h / 2, w, h))
            return

        # RECORTE_LIVRE (padrão): cada eixo tem um lado ANCORADO (o que não
        # está sendo arrastado - fica exatamente onde estava) e um lado que
        # se move. Só o lado que se move é limitado a [0, 1]; o ancorado
        # nunca é recalculado a partir de w/h "estourado", que era a causa
        # do bug.
        esquerda, topo, direita, baixo = x, y, x + w, y + h
        novo_w, novo_h = w, h   # eixo nao tocado preserva o valor EXATO de antes
        if "o" in lado:
            esquerda = min(max(0.0, esquerda + dx), direita - minimo)
            novo_w = direita - esquerda
        if "l" in lado or "e" in lado:
            direita = max(min(1.0, direita + dx), esquerda + minimo)
            novo_w = direita - esquerda
        if "n" in lado:
            topo = min(max(0.0, topo + dy), baixo - minimo)
            novo_h = baixo - topo
        if "s" in lado:
            baixo = max(min(1.0, baixo + dy), topo + minimo)
            novo_h = baixo - topo

        self.definir_recorte((esquerda, topo, novo_w, novo_h))

    def _mover_conteudo(self, ponto: QPoint) -> None:
        """Fase 2 (aprovada pelo Samuel em 22/09/2026): arrasta o CONTEÚDO
        (a página já recortada) dentro do canvas da folha - MODO_CONTEUDO,
        distinto de MODO_RECORTE (que edita o RECORTE, outra coisa).

        Trabalha inteiramente em fração do CANVAS (`self._retangulo_conteudo`,
        o mesmo formato de `core.folha.conteudo_como_retangulo`) - só depois
        de soltar o mouse (`conteudo_movido`) é que
        `ui/tela_conferir.py::_mover_conteudo` converte para (escala,
        deslocamento), o formato salvo em `ConfigPagina`. `w`/`h` nunca mudam
        aqui - só x/y, sempre mantendo o conteúdo inteiro dentro do canvas
        [0,1]. Redimensionar (mudar w/h arrastando um canto) é
        `_redimensionar_conteudo`, logo abaixo - Fase 3.

        Linhas-guia + ímã: `guias_ativas`/`encaixar_no_ima` já existiam,
        testadas, mas nunca tinham sido ligadas a nenhuma tela até agora.
        """
        if self._area.width() <= 0 or self._area.height() <= 0:
            return
        dx = (ponto.x() - self._ponto_inicial.x()) / self._area.width()
        dy = (ponto.y() - self._ponto_inicial.y()) / self._area.height()
        x0, y0, w, h = self._retangulo_conteudo_inicial

        x = min(max(0.0, x0 + dx), 1.0 - w)
        y = min(max(0.0, y0 + dy), 1.0 - h)
        candidato = (x, y, w, h)

        self._guias_ativas_agora = guias_ativas(candidato)
        self._retangulo_conteudo = encaixar_no_ima(candidato)
        self.update()

    def _redimensionar_conteudo(self, ponto: QPoint, lado: str) -> None:
        """Fase 3 (confirmada pelo Samuel em 22/09/2026: "quero conseguir
        redimensionar o conteudo tambem") - arrasta um CANTO do conteúdo pra
        mudar o tamanho (`w`/`h` de `self._retangulo_conteudo`).

        Sempre proporcional (mantém a razão largura/altura - esticar só um
        lado distorceria a imagem escaneada) e ancorado no CENTRO do
        conteúdo: a posição (`conteudo_deslocamento`, calculada depois a
        partir do centro do retângulo) não muda ao redimensionar, só o
        tamanho (`conteudo_escala`). Mesmo algoritmo de RECORTE_PROPORCAO em
        `_mover_recorte` (mesmas contas, mesmo sinal por canto) - aqui não
        existe outro modo porque redimensionar conteúdo é sempre assim, não
        faria sentido esticar só um eixo.

        Sem ímã/guias: `guias_ativas`/`encaixar_no_ima` só conhecem POSIÇÃO
        (centro/bordas do retângulo), não existe no código nenhuma noção de
        "tamanho padrão" pra grudar - decisão deixada em aberto pro Samuel,
        ver relatório da investigação.
        """
        if self._area.width() <= 0 or self._area.height() <= 0:
            return
        dx = (ponto.x() - self._ponto_inicial.x()) / self._area.width()
        dy = (ponto.y() - self._ponto_inicial.y()) / self._area.height()
        x, y, w, h = self._retangulo_conteudo_inicial
        centro_x, centro_y = x + w / 2, y + h / 2

        fatores = []
        if "o" in lado or "l" in lado or "e" in lado:
            sinal = -1.0 if "o" in lado else 1.0
            fatores.append(1.0 + (sinal * 2 * dx) / w if w else 1.0)
        if "n" in lado or "s" in lado:
            sinal = -1.0 if "n" in lado else 1.0
            fatores.append(1.0 + (sinal * 2 * dy) / h if h else 1.0)
        fator = sum(fatores) / len(fatores) if fatores else 1.0

        minimo = 0.05
        menor_lado = min(w, h)
        fator_minimo = (minimo / menor_lado) if menor_lado else 0.0
        fator_max_x = (2 * min(centro_x, 1.0 - centro_x)) / w if w else fator
        fator_max_y = (2 * min(centro_y, 1.0 - centro_y)) / h if h else fator
        fator = min(max(fator, fator_minimo), min(fator_max_x, fator_max_y))

        novo_w, novo_h = w * fator, h * fator
        self._retangulo_conteudo = (
            centro_x - novo_w / 2, centro_y - novo_h / 2, novo_w, novo_h)
        self.update()
