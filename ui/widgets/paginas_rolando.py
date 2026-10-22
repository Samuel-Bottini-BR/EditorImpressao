"""As páginas do livro aberto, na tela inteira (etapa 7 do layout; refeito em 22/10/2026 como no UPDF).

O QUE O SAMUEL DECIDIU
    Rodada 6 (05/10) e página de escolhas (06/10): o livro aberto, na tela inteira, com as "páginas
    rolando, uma embaixo da outra, com a coluna de miniaturas (proposta 1)", e o pedido: "quero ter a
    opção de clicar e ver como ia ficar as paginas lado a lado ... como opção um botão". Rodada 7: os
    pares rolando (202 A), com a página 1 sozinha à direita, como num livro.
    Conferência de 22/10/2026, quadro "O livro aberto na tela inteira", "Está pior": "Eu não consigo
    ver a página direito, e elas estão de maneira muito ruim, da uma na internet como o updf faz. Tem
    uma pagina maior que outra ali". Refeito como o UPDF: jeitos de MOSTRAR (uma página / duas lado a
    lado, cada um rolando sem parar ou não) e de CABER (a página, a altura, a largura, tamanho real),
    escolhidos na barra de baixo do livro aberto (ui/tela_inicio.LivroAberto).

COMO FUNCIONA (e o que é arriscado mudar)
    - Mostra as folhas COMO ESTÃO NO PDF (sem filtro, sem dividir).
    - TODAS AS PÁGINAS DE UMA LINHA TÊM A MESMA ALTURA NA TELA: no par, as duas ficam do mesmo
      tamanho, como num livro de verdade, mesmo que o scan de uma seja maior (no jeito antigo as duas
      tinham a mesma largura e a de scan maior saía mais alta). Isso é só na tela; o PDF não muda.
      No "Tamanho real" todas usam a altura da página típica do livro (a do meio, por tamanho).
    - PÁGINA NÍTIDA: cada folha é desenhada no tamanho EXATO, em pixels de verdade, do lugar onde é
      pintada (a escala do Windows incluída, lida do próprio pintor: todas_as_paginas.razao_do_pintor)
      e pintada 1 para 1, num lugar que cai em pixel inteiro. Antes ela era desenhada um pouco maior e
      reduzida ao pintar (ou desenhada na escala do widget e aumentada no grab), e saía mole.
      Arriscado: voltar a pintar com escala (drawPixmap num retângulo) quando o tamanho já bate.
    - Uma folha só é desenhada quando aparece na tela, em segundo plano (uma por vez, abrindo e
      fechando o PDF a cada folha, pelo core.pdf_io, que desenha em outro processo); as desenhadas
      ficam guardadas até MAXIMO_GUARDADAS e MAXIMO_DE_BYTES (as mais longe saem). Assim um livro de
      1000 folhas não enche a memória. Arriscado: desenhar no fio da tela (trava) ou guardar todas.
"""

from __future__ import annotations

import statistics
import traceback
from collections import OrderedDict

import cv2
import numpy as np
from PySide6.QtCore import QObject, QPointF, QRect, QRectF, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QScrollArea, QWidget

from registro import registrar_erro
from ui import estilo
from ui.widgets.visualizador import numpy_para_qimage

# Jeitos de mostrar e de caber (os nomes da barra de baixo ficam em ui/tela_inicio.py).
UMA, DUAS = "uma", "duas"
CABER_PAGINA, CABER_ALTURA, CABER_LARGURA, TAMANHO_REAL = "pagina", "altura", "largura", "real"
JEITOS_DE_MOSTRAR = (UMA, DUAS)
JEITOS_DE_CABER = (CABER_PAGINA, CABER_ALTURA, CABER_LARGURA, TAMANHO_REAL)

MARGEM = 18                    # em volta das páginas e entre uma linha e outra
ALTURA_MINIMA = 60             # nenhuma página fica menor que isto (pontos)
MAXIMO_GUARDADAS = 40          # folhas desenhadas guardadas
MAXIMO_DE_BYTES = 240 * 2**20  # e no máximo isto de memória nelas (as da tela ficam sempre)
MAXIMO_DE_PIXELS = 16_000_000  # folha maior que isto na tela é desenhada menor e aumentada
ESPACO = MARGEM                # (nome antigo, para quem importava)


def no_tamanho(img: np.ndarray, largura: int, altura: int) -> np.ndarray:
    """A imagem com exatamente `largura` x `altura` pixels. A folha já vem
    desenhada no DPI que dá essa altura, então a diferença é de 1 ou 2 pixels
    (arredondamento): corta ou completa a beirada, SEM reamostrar (reamostrar
    por 0,998 borraria a página inteira). Diferença maior (o PDF limitou o DPI
    de uma folha enorme): reduz ou aumenta de verdade."""
    h, w = img.shape[:2]
    if abs(h - altura) > 2 or abs(w - largura) > 2:
        modo = cv2.INTER_AREA if (w > largura or h > altura) else cv2.INTER_CUBIC
        return cv2.resize(img, (max(1, largura), max(1, altura)), interpolation=modo)
    img = img[:altura, :largura]
    falta_h, falta_w = altura - img.shape[0], largura - img.shape[1]
    if falta_h > 0 or falta_w > 0:
        img = cv2.copyMakeBorder(img, 0, max(0, falta_h), 0, max(0, falta_w), cv2.BORDER_REPLICATE)
    return np.ascontiguousarray(img)


class _Sinais(QObject):
    pronta = Signal(int, object, int, int)      # índice, imagem, largura e altura pedidas


class _Tarefa(QRunnable):
    """Desenha uma folha com `largura` x `altura` pixels, em segundo plano."""

    def __init__(self, caminho: str, indice: int, largura: int, altura: int, sinais: _Sinais) -> None:
        super().__init__()
        self.caminho, self.indice, self.sinais = caminho, indice, sinais
        self.largura, self.altura = largura, altura

    def run(self) -> None:
        from core.pdf_io import abrir_pdf, pagina_para_array
        try:
            doc = abrir_pdf(self.caminho)
            try:
                altura_pt = max(1.0, doc[self.indice].rect.height)
                img = pagina_para_array(doc, self.indice, dpi=72.0 * self.altura / altura_pt)
            finally:
                doc.close()
            self.sinais.pronta.emit(self.indice, no_tamanho(img, self.largura, self.altura),
                                    self.largura, self.altura)
        except Exception:  # noqa: BLE001 - a página fica cinza, nada fecha
            registrar_erro("páginas rolando", traceback.format_exc())


def _em_pixels(ret: QRectF, razao: float) -> QRect:
    """O retângulo `ret` (pontos) nos pixels de verdade, com as beiradas
    arredondadas uma a uma: duas páginas com o mesmo alto e o mesmo baixo dão
    exatamente a mesma altura em pixels."""
    x0, y0 = round(ret.left() * razao), round(ret.top() * razao)
    x1, y1 = round(ret.right() * razao), round(ret.bottom() * razao)
    return QRect(x0, y0, max(1, x1 - x0), max(1, y1 - y0))


class _Folhas(QWidget):
    """O desenho de todas as folhas (só as visíveis são pintadas)."""

    def __init__(self, dono: "PaginasRolando") -> None:
        super().__init__()
        self.dono = dono

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        from ui.widgets.todas_as_paginas import razao_do_pintor

        pintor = QPainter(self)
        razao = razao_do_pintor(pintor)
        visivel = QRectF(evento.rect())
        for indice, ret in self.dono.retangulos_exatos():
            if not ret.intersects(visivel):
                continue
            px = _em_pixels(ret, razao)
            largura, altura = self.dono.tamanho_para_desenhar(px.width(), px.height())
            pix = self.dono.guardadas.get(indice)
            if pix is None or (pix.width(), pix.height()) != (largura, altura):
                self.dono.pedir(indice, largura, altura)
            if pix is None:
                pintor.fillRect(ret, QColor(estilo.cor("cabeca")))
                pintor.setPen(QColor(estilo.cor("fraco")))
                pintor.drawText(ret, Qt.AlignCenter, str(indice + 1))
            elif (pix.width(), pix.height()) == (px.width(), px.height()):
                # 1 para 1, começando num pixel inteiro: sem nenhuma reamostragem
                copia = QPixmap(pix)
                copia.setDevicePixelRatio(razao)
                pintor.setRenderHint(QPainter.SmoothPixmapTransform, False)
                pintor.drawPixmap(QPointF(px.left() / razao, px.top() / razao), copia)
            else:                       # ainda a de antes (outro tamanho), até chegar a nova
                pintor.setRenderHint(QPainter.SmoothPixmapTransform, True)
                pintor.drawPixmap(QRectF(px.left() / razao, px.top() / razao,
                                         px.width() / razao, px.height() / razao), pix, QRectF(pix.rect()))
            if indice == self.dono.atual and self.dono.continuo:
                pintor.setPen(QColor(estilo.cor("azul")))
                pintor.drawRect(ret.adjusted(-2, -2, 1, 1))
        pintor.end()


class PaginasRolando(QScrollArea):
    """O folhear do livro aberto (ver o começo do arquivo)."""

    pagina_mudou = Signal(int)       # a folha da vez agora

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(False)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.caminho = ""
        self.tamanhos: list[tuple[float, float]] = []   # largura x altura de cada folha (pontos do PDF)
        self.mostrar = UMA
        self.continuo = True
        self.caber = CABER_PAGINA
        self.atual = 0
        self.guardadas: OrderedDict[int, QPixmap] = OrderedDict()
        self._pedidas: dict[int, tuple[int, int]] = {}
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._chegou)
        self._ret: list[tuple[int, QRectF]] = []
        self._roda = 0                  # a roda do mouse acumulada (folhear sem rolar)
        self.folhas = _Folhas(self)
        self.setWidget(self.folhas)
        self.verticalScrollBar().valueChanged.connect(lambda _v: self._acompanhar())
        self.horizontalScrollBar().valueChanged.connect(lambda _v: self._pedir_as_visiveis())

    # --- uso --------------------------------------------------------------------

    def abrir(self, caminho: str) -> None:
        """Mostra o livro `caminho` (lê só o tamanho de cada folha agora)."""
        from core.pdf_io import ErroPDF, abrir_pdf
        self.limpar()
        self.caminho = caminho
        try:
            doc = abrir_pdf(caminho)
            try:
                self.tamanhos = [(p.rect.width, p.rect.height) for p in doc]
            finally:
                doc.close()
        except ErroPDF:
            self.tamanhos = []          # PDF que não abre: a tela fica sem páginas, sem erro
        except Exception:  # noqa: BLE001
            registrar_erro("páginas rolando (abrir)", traceback.format_exc())
            self.tamanhos = []
        self._arrumar()

    def limpar(self) -> None:
        self.caminho = ""
        self.tamanhos = []
        self.guardadas.clear()
        self._pedidas.clear()
        self._pool.clear()
        self.atual = 0
        self._arrumar()

    @property
    def lado_a_lado(self) -> bool:
        """Se está mostrando duas lado a lado (nome de antes)."""
        return self.mostrar == DUAS

    def definir_lado_a_lado(self, ligado: bool) -> None:
        """O "Ver lado a lado" de antes: o mesmo que escolher "Duas lado a lado"."""
        self.definir_jeito(mostrar=DUAS if ligado else UMA)

    def definir_jeito(self, mostrar: str | None = None, continuo: bool | None = None,
                      caber: str | None = None) -> None:
        """Troca o jeito de mostrar (uma / duas), o rolar sem parar e o jeito de
        caber, ficando na mesma folha. Valor desconhecido é ignorado."""
        if mostrar in JEITOS_DE_MOSTRAR:
            self.mostrar = mostrar
        if continuo is not None:
            self.continuo = bool(continuo)
        if caber in JEITOS_DE_CABER:
            self.caber = caber
        atual = self.atual
        self._arrumar()
        self.ir_para(atual)

    def ir_para(self, indice: int) -> None:
        """Vai à folha `indice`: rolando sem parar, o alto dela (ou do par) no
        alto da tela; sem rolar, mostra a linha dela."""
        if not self.tamanhos:
            self.atual = 0
            return
        indice = max(0, min(len(self.tamanhos) - 1, int(indice)))
        mudou_de_linha = self._linha_de(indice) != self._linha_de(self.atual)
        self.atual = indice
        if not self.continuo and (mudou_de_linha or not any(i == indice for i, _r in self._ret)):
            self._arrumar()
        for i, ret in self._ret:
            if i == indice or (self._linha_de(i) == self._linha_de(indice)):
                self.verticalScrollBar().setValue(max(0, int(ret.top() - MARGEM)) if self.continuo else 0)
                break
        self.folhas.update()
        self._pedir_as_visiveis()

    def passo(self, quanto: int) -> int:
        """A folha que vem `quanto` linhas depois da atual (no par, a primeira
        do par seguinte), dentro do livro."""
        linhas = self._linhas()
        if not linhas:
            return 0
        n = max(0, min(len(linhas) - 1, self._linha_de(self.atual) + quanto))
        return next(i for i in linhas[n] if i is not None)

    def total(self) -> int:
        return len(self.tamanhos)

    def altura_das_paginas(self) -> list[tuple[int, float]]:
        """(índice, altura na tela em pontos) das folhas arrumadas agora."""
        return [(i, r.height()) for i, r in self._ret]

    # --- a arrumação ------------------------------------------------------------

    def retangulos(self) -> list[tuple[int, QRect]]:
        """Onde cada folha fica (pontos, arredondado)."""
        return [(i, r.toRect()) for i, r in self._ret]

    def retangulos_exatos(self) -> list[tuple[int, QRectF]]:
        return self._ret

    def _linhas(self) -> list[list[int | None]]:
        """As linhas: uma folha por linha, ou em pares com a 1 sozinha à direita."""
        n = len(self.tamanhos)
        if self.mostrar == DUAS:
            linhas = [[None, 0]] if n else []
            linhas += [[i, i + 1 if i + 1 < n else None] for i in range(1, n, 2)]
            return linhas
        return [[i] for i in range(n)]

    def _linha_de(self, indice: int) -> int:
        if self.mostrar == DUAS:
            return 0 if indice <= 0 else (indice + 1) // 2
        return indice

    def _altura_real(self) -> float:
        """A altura de "Tamanho real": a da folha típica (a do meio, por tamanho)
        a 100%, igual para todas, para nenhuma ficar maior que a outra."""
        if not self.tamanhos:
            return 400.0
        return statistics.median(h for _w, h in self.tamanhos) * self.logicalDpiY() / 72.0

    def _altura_da_linha(self, proporcoes: float, largura: float, altura: float) -> float:
        """A altura comum das folhas de uma linha, pelo jeito de caber.
        `proporcoes` é a soma de largura/altura das folhas (no par, os dois lugares)."""
        if self.caber == CABER_ALTURA:
            h = altura - 2 * MARGEM
        elif self.caber == CABER_LARGURA:
            h = (largura - 2 * MARGEM) / proporcoes
        elif self.caber == TAMANHO_REAL:
            h = self._altura_real()
        else:
            h = min(altura - 2 * MARGEM, (largura - 2 * MARGEM) / proporcoes)
        return max(float(ALTURA_MINIMA), h)

    def _arrumar(self) -> None:
        """Calcula onde cada folha fica."""
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        livre = self.maximumViewportSize()
        barra = self.style().pixelMetric(self.style().PixelMetric.PM_ScrollBarExtent)
        # a barra de rolar de pé sempre descontada (nada pula de tamanho quando ela aparece);
        # a deitada só nos jeitos em que a página pode passar da largura
        largura = max(200, livre.width() - barra)
        altura = max(150, livre.height() - (barra if self.caber in (CABER_ALTURA, TAMANHO_REAL) else 0))
        linhas = self._linhas()
        if not self.continuo and linhas:
            linhas = [linhas[min(len(linhas) - 1, self._linha_de(self.atual))]]
        arrumadas = []
        maior = 0.0
        for linha in linhas:
            presentes = [i for i in linha if i is not None]
            prop = {i: self.tamanhos[i][0] / max(1.0, self.tamanhos[i][1]) for i in presentes}
            # no par, os dois lugares contam (a 1, sozinha, fica do tamanho das outras)
            soma = sum(prop.values()) if len(linha) == len(presentes) else 2 * sum(prop.values())
            h = self._altura_da_linha(max(0.05, soma), largura, altura)
            arrumadas.append((linha, prop, h))
            maior = max(maior, h * soma)
        total_w = max(float(largura), maior + 2 * MARGEM)
        meio = total_w / 2
        ret: list[tuple[int, QRectF]] = []
        y = float(MARGEM)
        for linha, prop, h in arrumadas:
            if not self.continuo:
                y = max(float(MARGEM), (altura - h) / 2)
            if len(linha) == 1:
                i = linha[0]
                w = h * prop[i]
                ret.append((i, QRectF(meio - w / 2, y, w, h)))
            else:
                esquerda, direita = linha
                if esquerda is not None:
                    w = h * prop[esquerda]
                    ret.append((esquerda, QRectF(meio - w, y, w, h)))
                if direita is not None:
                    ret.append((direita, QRectF(meio, y, h * prop[direita], h)))
            y += h + MARGEM
        self._ret = ret
        alto_total = y if self.continuo else max(y, float(altura))
        self.folhas.resize(QSize(int(total_w + 0.999), int(alto_total + 0.999)))
        self.folhas.update()
        self._pedir_as_visiveis()

    def tamanho_para_desenhar(self, largura: int, altura: int) -> tuple[int, int]:
        """O tamanho em que a folha é desenhada: o da tela, ou menor se passar
        de MAXIMO_DE_PIXELS (aí ela é aumentada ao pintar)."""
        if largura * altura <= MAXIMO_DE_PIXELS:
            return largura, altura
        f = (MAXIMO_DE_PIXELS / (largura * altura)) ** 0.5
        return max(1, int(largura * f)), max(1, int(altura * f))

    def _pedir_as_visiveis(self) -> None:
        """Pede as folhas que estão na tela (e uma tela acima e abaixo), sem
        esperar a pintura (a janela pode não estar sendo pintada), no tamanho
        da escala do Windows deste widget."""
        topo = self.verticalScrollBar().value()
        alto = max(1, self.viewport().height())
        faixa = QRectF(0, topo - alto, self.folhas.width(), alto * 3)
        razao = self.devicePixelRatioF()
        for indice, ret in self._ret:
            if ret.intersects(faixa):
                px = _em_pixels(ret, razao)
                self.pedir(indice, *self.tamanho_para_desenhar(px.width(), px.height()))

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        atual = self.atual
        self._arrumar()
        self.ir_para(atual)

    def wheelEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Sem "Rolar sem parar": a roda rola dentro da página e, no fim dela,
        passa para a próxima (no começo, para a anterior), como no UPDF."""
        if self.continuo:
            super().wheelEvent(evento)
            return
        barra = self.verticalScrollBar()
        delta = evento.angleDelta().y()
        no_fim = barra.value() >= barra.maximum()
        no_comeco = barra.value() <= barra.minimum()
        if (delta < 0 and no_fim) or (delta > 0 and no_comeco):
            self._roda += delta
            if abs(self._roda) >= 120:
                para = self.passo(-1 if self._roda > 0 else 1)
                voltando = self._roda > 0
                self._roda = 0
                if para != self.atual:
                    self.ir_para(para)
                    if voltando:
                        barra.setValue(barra.maximum())
                    self.pagina_mudou.emit(self.atual)
            evento.accept()
            return
        self._roda = 0
        super().wheelEvent(evento)

    def _acompanhar(self) -> None:
        """Rolando sem parar, a folha mais visível vira a atual (a pílula e as
        miniaturas acompanham)."""
        self._pedir_as_visiveis()
        if not self.continuo:
            return
        topo = self.verticalScrollBar().value()
        meio = topo + self.viewport().height() // 3
        melhor = None
        for indice, ret in self._ret:
            if ret.top() <= meio <= ret.bottom() + MARGEM:
                melhor = indice
                break
        if melhor is not None and melhor != self.atual:
            self.atual = melhor
            self.folhas.update()
            self.pagina_mudou.emit(melhor)

    # --- as folhas desenhadas ---------------------------------------------------------

    def pixels_necessarios(self, indice: int) -> int:
        """Quantos pixels de largura a folha `indice` ocupa de verdade na tela
        (a largura mostrada vezes a escala do Windows)."""
        ret = next((r for i, r in self._ret if i == indice), None)
        if ret is None:
            return 1
        return _em_pixels(ret, self.devicePixelRatioF()).width()

    def pedir(self, indice: int, largura: int, altura: int) -> None:
        """Pede a folha `indice` com `largura` x `altura` pixels (se ainda não
        estiver guardada nem pedida nesse tamanho)."""
        if not self.caminho or not 0 <= indice < len(self.tamanhos):
            return
        if self._pedidas.get(indice) == (largura, altura):
            return
        guardada = self.guardadas.get(indice)
        if guardada is not None and (guardada.width(), guardada.height()) == (largura, altura):
            return
        self._pedidas[indice] = (largura, altura)
        self._pool.start(_Tarefa(self.caminho, indice, largura, altura, self._sinais))

    def _chegou(self, indice: int, img, largura: int = 0, altura: int = 0) -> None:
        """Uma folha desenhada chegou (largura e altura: o tamanho que foi pedido)."""
        if self._pedidas.get(indice) == (largura, altura):
            self._pedidas.pop(indice, None)
        if not self.caminho:
            return
        self.guardadas[indice] = QPixmap.fromImage(numpy_para_qimage(img))
        self.guardadas.move_to_end(indice)
        na_tela = {i for i, _r in self._ret}

        def bytes_guardados() -> int:
            return sum(p.width() * p.height() * 4 for p in self.guardadas.values())

        while len(self.guardadas) > 1 and (len(self.guardadas) > MAXIMO_GUARDADAS
                                           or bytes_guardados() > MAXIMO_DE_BYTES):
            longe = max(self.guardadas, key=lambda i: abs(i - self.atual))
            if longe == indice or (longe in na_tela and abs(longe - self.atual) <= 2):
                break
            self.guardadas.pop(longe)
        self.folhas.update()

    def parar(self) -> None:
        """Interrompe o que falta desenhar (ao voltar para os livros)."""
        self._pool.clear()
        self._pool.waitForDone(2000)
