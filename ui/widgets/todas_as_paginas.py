"""A tela "Todas as páginas": o livro inteiro em grade (etapa 5 do layout, 21/10/2026).

O QUE O SAMUEL DECIDIU
    Rodadas 1 e 2 (aprovado): ter "uma a uma" e "em pares" ("na opção 2 (pares), clicar abre as
    duas páginas lado a lado, como vai ser impresso"), e "todas / só as que precisam de atenção".
    Rodada 13, 808 A: abre pelo botão "ver todas" do cabeçalho das miniaturas. Rodada 14, 901
    ("A — Uma a uma"): abre sempre "uma a uma". Rodada 14, 904 A: também pelo menu Ver.

O QUE FAZ
    A grade das páginas pequenas, com o número e, nas que têm aviso, a borda laranja e o motivo.
    Clicar numa página volta ao trabalho NELA. "Em pares" junta as páginas como no livro aberto
    (a 1 sozinha à direita, depois 2 e 3...); clicar num par vai para a primeira página dele. O
    "abrir as duas lado a lado" de quando se clica num par depende do "Ver lado a lado", que
    ainda não existe no programa: não foi inventado aqui.

    As páginas pequenas são desenhadas em segundo plano (uma folha por vez, a 30 DPI, abrindo e
    fechando o PDF a cada folha, como a tira) e guardadas enquanto o livro está aberto: cada uma
    tem uns 60 KB, umas 18 MB num livro de 300 folhas. A tela nunca espera por elas (quadro cinza
    até chegar).

Seguro mudar: tamanhos e textos. Arriscado: desenhar as páginas no fio da tela (trava a janela
num livro grande).
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass

import numpy as np
from PySide6.QtCore import QObject, QPointF, QRect, QRunnable, QSize, Qt, QThreadPool, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from registro import registrar_erro
from ui import estilo
from ui.widgets.visualizador import numpy_para_qimage

UMA_A_UMA, EM_PARES = "uma", "pares"
ALTURA_DA_PAGINA = 150        # o desenho de cada página na grade
# A folha guardada: maior que o quadro (150 pontos são ~375 pixels numa tela a
# 250%), senão a página sai borrada (verificador, 21/10/2026). No máximo
# MAXIMO_GUARDADAS folhas ficam guardadas (as mais longe da página da vez saem):
# ~0,25 MB cada, uns 40 MB no máximo, num livro de qualquer tamanho.
ALTURA_GUARDADA = 340          # (fica para quem importava o nome; a altura vem da tela)
DPI_MAXIMO_DA_GRADE = 160
MAXIMO_GUARDADAS = 120
FOLGA_NA_MARGEM = 3            # pontos que a folha pode avançar na margem do quadro (ver _pintar)


@dataclass
class ItemDaGrade:
    """Uma página do livro, como a grade precisa dela."""

    indice: int
    folha: int
    motivo: str = ""              # o título do aviso, se houver ("Lombada incerta")
    apagada: bool = False


class _Sinais(QObject):
    pronta = Signal(int, object)          # índice da folha, imagem (numpy)


class _TarefaDasFolhas(QRunnable):
    """Desenha as folhas pedidas, uma por vez, em segundo plano."""

    def __init__(self, caminho_pdf: str, folhas: list[int], sinais: _Sinais,
                 altura_px: int = ALTURA_GUARDADA) -> None:
        """altura_px: a altura, em pixels de verdade, de que o quadro precisa
        (150 pontos vezes a escala do Windows, com folga): cada folha é
        desenhada no DPI que dá essa altura (verificador, 21/10/2026: com um
        DPI fixo a grade saía mole)."""
        super().__init__()
        self.altura_px = altura_px
        self.caminho_pdf = caminho_pdf
        self.folhas = folhas
        self.sinais = sinais
        self.parar = False

    def run(self) -> None:
        from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array
        try:
            for folha in self.folhas:
                if self.parar:
                    return
                doc = abrir_pdf(self.caminho_pdf)
                try:
                    altura_pt = max(1.0, doc[folha].rect.height)
                    dpi = min(DPI_MAXIMO_DA_GRADE, 72.0 * self.altura_px / altura_pt)
                    img = pagina_para_array(doc, folha, dpi=dpi)
                finally:
                    doc.close()
                img = limitar_altura(img, self.altura_px)
                # a altura EXATA do quadro em pixels (cortando ou completando 1 ou
                # 2 pixels do arredondamento, sem reamostrar): assim ela é pintada
                # 1 para 1 (22/10/2026)
                from ui.widgets.paginas_rolando import no_tamanho
                if 0 < self.altura_px - img.shape[0] <= 2 or img.shape[0] == self.altura_px:
                    img = no_tamanho(img, img.shape[1], self.altura_px)
                self.sinais.pronta.emit(folha, img)
        except Exception:  # noqa: BLE001 - a grade nunca derruba a janela
            registrar_erro("todas as páginas", traceback.format_exc())


def razao_do_pintor(pintor: QPainter) -> float:
    """Quantos pixels de verdade por ponto o pintor está pintando: o do
    aparelho de verdade por trás (a tela, ou a imagem de um grab/render), e não
    o do widget, que num grab pode ser outro."""
    motor = pintor.paintEngine()
    aparelho = motor.paintDevice() if motor is not None else None
    aparelho = aparelho or pintor.device()
    return aparelho.devicePixelRatioF() if aparelho is not None else 1.0


def _reduzir_para_a_tela(pix: QPixmap, tamanho: QSize, pintor: QPainter) -> QPixmap:
    """A imagem reduzida para caber em `tamanho` (pontos), nos pixels de verdade
    do que está sendo pintado (a razão de pixels do dispositivo do pintor),
    marcada com essa razão para o Qt não aumentá-la de novo. Se ela já cabe
    exatamente (um dos lados igual ao lugar, o outro menor), volta igual: nada
    de reamostrar o que já tem o tamanho certo (22/10/2026)."""
    razao = razao_do_pintor(pintor)
    alvo_w, alvo_h = round(tamanho.width() * razao), round(tamanho.height() * razao)
    escala = min(alvo_w / max(1, pix.width()), alvo_h / max(1, pix.height()))
    if abs(escala - 1.0) < 1e-6:
        escalado = QPixmap(pix)
    else:
        escalado = pix.scaled(QSize(max(1, round(pix.width() * escala)), max(1, round(pix.height() * escala))),
                              Qt.KeepAspectRatio, Qt.SmoothTransformation)
    escalado.setDevicePixelRatio(razao)
    return escalado


class _Quadro(QFrame):
    """Uma página (ou um par) na grade: o desenho e a legenda."""

    clicado = Signal(int)

    def __init__(self, itens: list[ItemDaGrade], atual: bool, em_pares: bool = False,
                 parent=None) -> None:
        super().__init__(parent)
        self.itens = itens
        self.pixmaps: list[QPixmap | None] = [None] * len(itens)
        self.atual = atual
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("quadroDasTodas")
        self.setStyleSheet("QFrame#quadroDasTodas { background: transparent; border: none; }")
        self.motivo = next((i.motivo for i in itens if i.motivo), "")
        largura_de_uma = int(ALTURA_DA_PAGINA * 0.70)
        # em pares o quadro tem lugar para duas (a página 1, sozinha, fica do
        # lado direito, como no livro aberto)
        self.lugares = 2 if em_pares else 1
        self.largura_do_desenho = largura_de_uma * self.lugares
        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(3)
        self.desenho = QWidget()
        self.desenho.setFixedSize(QSize(self.largura_do_desenho + 8, ALTURA_DA_PAGINA + 8))
        self.desenho.paintEvent = self._pintar          # noqa: E731 - desenho simples
        fora.addWidget(self.desenho, 0, Qt.AlignHCenter)
        numeros = " e ".join(str(i.indice + 1) for i in itens)
        legenda = QLabel(numeros + (f" · {self.motivo.lower()}" if self.motivo else ""))
        legenda.setWordWrap(True)
        legenda.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        legenda.setFixedWidth(self.largura_do_desenho + 40)
        cor = estilo.cor("aviso") if self.motivo else estilo.cor("fraco")
        legenda.setStyleSheet(f"color: {cor}; font-size: 12px; background: transparent;"
                              + (" font-weight: 600;" if self.motivo else ""))
        fora.addWidget(legenda, 0, Qt.AlignHCenter)
        fora.addStretch()
        self.setToolTip("Clique para ir a esta página")

    def definir_pixmap(self, posicao: int, pixmap: QPixmap) -> None:
        self.pixmaps[posicao] = pixmap
        self.desenho.update()

    def _pintar(self, _evento) -> None:
        pintor = QPainter(self.desenho)
        pintor.setRenderHint(QPainter.SmoothPixmapTransform)
        largura = self.largura_do_desenho // self.lugares
        # só a página 1, sozinha, fica do lado direito (como no livro aberto);
        # a última, se sobrar sozinha, fica do lado esquerdo
        primeira = 1 if (self.lugares == 2 and len(self.itens) == 1
                         and self.itens[0].indice == 0) else 0
        for n, (item, pix) in enumerate(zip(self.itens, self.pixmaps)):
            lugar = primeira + n
            alvo = QRect(4 + lugar * largura, 4, largura, ALTURA_DA_PAGINA)
            if pix is None or pix.isNull():
                pintor.fillRect(alvo.adjusted(2, 2, -2, -2), QColor(estilo.cor("cabeca")))
            else:
                # reduzida nos pixels DE VERDADE do lugar onde é pintada (a
                # escala do Windows: 1,25 a 125%), e não no tamanho em pontos:
                # reduzir a 150 pontos e o Qt aumentar 1,25x deixava a grade
                # mole (verificador, 21/10/2026). Seguro mudar: nada aqui.
                #
                # E posta num PIXEL INTEIRO da tela, 1 para 1, sem o "suavizar" do
                # Qt: a 125% um ponto não cai em pixel inteiro e o Qt reamostrava a
                # imagem meio pixel para o lado, borrando (medido em 22/10/2026:
                # nitidez 0,60 do desenho direto do PDF). Seguro mudar: nada aqui.
                razao = razao_do_pintor(pintor)
                # a folha pode avançar até FOLGA_NA_MARGEM pontos na margem do quadro: uma
                # folha só um pouco mais larga que o lugar (o Graduale: 134 pixels para 131)
                # era reduzida a 97,7% inteira e amolecia (medido em 22/10/2026: 0,65)
                cabe = QSize(alvo.width() + (2 if self.lugares == 1 else 1) * FOLGA_NA_MARGEM, alvo.height())
                escalado = _reduzir_para_a_tela(pix, cabe, pintor)
                w, h = escalado.width(), escalado.height()          # pixels de verdade
                ax0, ay0 = round(alvo.left() * razao), round(alvo.top() * razao)
                ax1, ay1 = round((alvo.right() + 1) * razao), round((alvo.bottom() + 1) * razao)
                if self.lugares == 1:
                    x = ax0 + (ax1 - ax0 - w) // 2
                else:                    # o par encosta no meio, como o livro aberto
                    x = ax1 - w if lugar == 0 else ax0
                y = ay0 + (ay1 - ay0 - h) // 2
                pintor.setRenderHint(QPainter.SmoothPixmapTransform, False)
                pintor.drawPixmap(QPointF(x / razao, y / razao), escalado)
            if item.apagada:
                pintor.fillRect(alvo, QColor(255, 255, 255, 170))
                pintor.setPen(QColor("#B91C1C"))
                pintor.drawText(alvo, Qt.AlignCenter, "apagada")
        if self.motivo:
            cor, grossura = QColor(estilo.cor("aviso")), 3
        elif self.atual:
            cor, grossura = QColor(estilo.cor("azul")), 3
        else:
            cor, grossura = QColor(estilo.cor("sep")), 1
        caneta = pintor.pen()
        caneta.setColor(cor)
        caneta.setWidth(grossura)
        pintor.setPen(caneta)
        pintor.drawRect(self.desenho.rect().adjusted(1, 1, -2, -2))
        pintor.end()

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        if evento.button() == Qt.LeftButton:
            self.clicado.emit(self.itens[0].indice)


class TodasAsPaginas(QWidget):
    """A tela "Todas as páginas" (ver o começo do arquivo)."""

    ir_para = Signal(int)          # o índice da página clicada
    voltar = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("todasAsPaginas")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.vista = UMA_A_UMA
        self.so_atencao = False
        self.itens: list[ItemDaGrade] = []
        self.atual = 0
        self.metade = None            # função (indice, img) -> img: a metade da folha (a da tira)
        self._folhas: dict[int, np.ndarray] = {}
        self._caminho = ""
        self._tarefa: _TarefaDasFolhas | None = None
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._folha_chegou)
        self.quadros: list[_Quadro] = []

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(0)
        alto = QFrame()
        alto.setObjectName("altoDasTodas")
        alto.setAttribute(Qt.WA_StyledBackground, True)
        linha = QHBoxLayout(alto)
        linha.setContentsMargins(14, 8, 14, 8)
        linha.setSpacing(6)
        titulo = QLabel("Todas as páginas")
        titulo.setObjectName("tituloDasTodas")
        linha.addWidget(titulo)
        linha.addSpacing(14)
        self.botao_uma = self._chave("uma a uma", lambda: self.definir_vista(UMA_A_UMA))
        self.botao_pares = self._chave("em pares", lambda: self.definir_vista(EM_PARES))
        linha.addWidget(self.botao_uma)
        linha.addWidget(self.botao_pares)
        linha.addSpacing(14)
        self.botao_todas = self._chave("todas", lambda: self.definir_so_atencao(False))
        self.botao_atencao = self._chave("só as que precisam de atenção",
                                         lambda: self.definir_so_atencao(True))
        linha.addWidget(self.botao_todas)
        linha.addWidget(self.botao_atencao)
        linha.addStretch()
        self.botao_voltar = QPushButton("voltar ao trabalho")
        self.botao_voltar.setCursor(Qt.PointingHandCursor)
        self.botao_voltar.clicked.connect(lambda: self.voltar.emit())
        linha.addWidget(self.botao_voltar)
        fora.addWidget(alto)

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        self.dentro = QWidget()
        self.dentro.setObjectName("dentroDasTodas")
        self.grade = QGridLayout(self.dentro)
        self.grade.setContentsMargins(18, 16, 18, 16)
        self.grade.setHorizontalSpacing(14)
        self.grade.setVerticalSpacing(10)
        self.rolagem.setWidget(self.dentro)
        fora.addWidget(self.rolagem, 1)
        self.vazio = QLabel("Nenhuma página precisa de atenção.")
        self.vazio.setAlignment(Qt.AlignCenter)
        self.vazio.setVisible(False)
        fora.addWidget(self.vazio)
        self.pe = QLabel("")
        self.pe.setObjectName("peDasTodas")
        fora.addWidget(self.pe)
        estilo.estilizar(self, self._folha)
        self._colunas = 0
        self._acertar_as_chaves()

    # --- desenho -------------------------------------------------------------

    def _folha(self) -> str:
        c = estilo.cor
        return (f"QWidget#todasAsPaginas, QWidget#dentroDasTodas {{ background: {c('tela')}; }}"
                f"QFrame#altoDasTodas {{ background: {c('bar')}; border-bottom: 1px solid {c('linha')}; }}"
                f"QLabel#tituloDasTodas {{ color: {c('forte')}; font-size: 15px; font-weight: 600; }}"
                f"QLabel#peDasTodas {{ background: {c('bar')}; color: {c('fraco')}; padding: 6px 14px;"
                f" border-top: 1px solid {c('linha')}; font-size: 12px; }}"
                f"QPushButton#chaveDasTodas {{ padding: 4px 12px; }}"
                f"QPushButton#chaveDasTodas:checked {{ background: {c('sel')}; border: 1px solid {c('azul')};"
                f" color: {c('forte')}; }}")

    def _chave(self, texto: str, acao) -> QPushButton:
        botao = QPushButton(texto)
        botao.setObjectName("chaveDasTodas")
        botao.setCheckable(True)
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(lambda _c=False: acao())
        return botao

    def _acertar_as_chaves(self) -> None:
        self.botao_uma.setChecked(self.vista == UMA_A_UMA)
        self.botao_pares.setChecked(self.vista == EM_PARES)
        self.botao_todas.setChecked(not self.so_atencao)
        self.botao_atencao.setChecked(self.so_atencao)
        quantas = sum(1 for i in self.itens if i.motivo)
        self.botao_atencao.setText(f"só as que precisam de atenção ({quantas})")
        # a largura acompanha o texto novo (a negrita do escolhido é mais larga)
        largura = self.botao_atencao.fontMetrics().horizontalAdvance(self.botao_atencao.text())
        self.botao_atencao.setMinimumWidth(int(largura * 1.12) + 30)
        self.pe.setText(
            ("Uma a uma: cada página do livro num quadro. Clique numa página para ir até ela."
             if self.vista == UMA_A_UMA else
             "Em pares: as duas páginas lado a lado, como no livro aberto. Clique num par para ir até ele.")
            + f"   ·   {len(self.itens)} páginas")

    # --- uso -------------------------------------------------------------------

    def mostrar(self, itens: list[ItemDaGrade], atual: int, caminho_pdf: str, metade) -> None:
        """Abre com as páginas do livro, sempre "uma a uma" (rodada 14, 901 A).
        `metade(indice, img_da_folha)` dá a página de dentro da folha (a da
        tira, com o giro). As folhas que ainda não foram desenhadas são pedidas
        em segundo plano."""
        if caminho_pdf != self._caminho:
            self.esquecer()
            self._caminho = caminho_pdf
        self.itens = list(itens)
        self.atual = atual
        self.metade = metade
        self.vista = UMA_A_UMA
        self.so_atencao = False
        self._montar()
        # primeiro as folhas perto da página da vez (num livro de 750 folhas, as de
        # perto da 300 esperavam as 299 de antes, 22/10/2026), depois as outras
        perto = next((i.folha for i in self.itens if i.indice == atual), 0)
        faltam = sorted({i.folha for i in self.itens} - set(self._folhas), key=lambda f: (abs(f - perto), f))
        if faltam and self._caminho:
            self._parar_a_tarefa()
            self._tarefa = _TarefaDasFolhas(self._caminho, faltam, self._sinais,
                                            self.altura_necessaria())
            self._pool.start(self._tarefa)

    def altura_necessaria(self) -> int:
        """A altura, em pixels de verdade, de uma página no quadro (exata: ela é
        pintada 1 para 1; com folga ela tinha de ser reduzida ao pintar)."""
        return int(round(ALTURA_DA_PAGINA * self.devicePixelRatioF()))

    def definir_vista(self, vista: str) -> None:
        self.vista = vista
        self._montar()

    def definir_so_atencao(self, so: bool) -> None:
        self.so_atencao = bool(so)
        self._montar()

    def esquecer(self) -> None:
        """Joga fora as páginas guardadas (outro livro, ou a tela fechou o livro)."""
        self._parar_a_tarefa()
        self._folhas.clear()
        self._caminho = ""

    def _parar_a_tarefa(self) -> None:
        if self._tarefa is not None:
            self._tarefa.parar = True
            self._tarefa = None
            self._pool.waitForDone(2000)

    # --- a grade ----------------------------------------------------------------

    def _grupos(self) -> list[list[ItemDaGrade]]:
        itens = self.itens
        if self.vista == EM_PARES:
            grupos = [itens[:1]] + [itens[i:i + 2] for i in range(1, len(itens), 2)]
        else:
            grupos = [[i] for i in itens]
        if self.so_atencao:
            grupos = [g for g in grupos if any(i.motivo for i in g)]
        return [g for g in grupos if g]

    def _montar(self) -> None:
        for quadro in self.quadros:
            quadro.setParent(None)
            quadro.deleteLater()
        self.quadros = []
        for grupo in self._grupos():
            quadro = _Quadro(grupo, any(i.indice == self.atual for i in grupo),
                             em_pares=self.vista == EM_PARES)
            quadro.clicado.connect(self.ir_para)
            self.quadros.append(quadro)
            for n, item in enumerate(grupo):
                pix = self._pixmap_da_pagina(item)
                if pix is not None:
                    quadro.pixmaps[n] = pix
        self.vazio.setVisible(not self.quadros)
        self._colunas = 0
        self._arrumar()
        self._acertar_as_chaves()

    def _arrumar(self) -> None:
        """Põe os quadros na grade, com quantas colunas couberem na largura."""
        if not self.quadros:
            return
        largura_do_quadro = self.quadros[0].sizeHint().width() + self.grade.horizontalSpacing()
        colunas = max(1, (self.rolagem.viewport().width() - 36) // max(1, largura_do_quadro))
        if colunas == self._colunas:
            return
        self._colunas = colunas
        while self.grade.count():
            self.grade.takeAt(0)
        for n, quadro in enumerate(self.quadros):
            self.grade.addWidget(quadro, n // colunas, n % colunas, Qt.AlignTop | Qt.AlignHCenter)
        for c in range(self.grade.columnCount()):
            self.grade.setColumnStretch(c, 0)
        self.grade.setColumnStretch(colunas, 1)
        self.grade.setRowStretch(len(self.quadros) // colunas + 1, 1)

    def resizeEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().resizeEvent(evento)
        self._arrumar()

    def showEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        super().showEvent(evento)
        self._colunas = 0
        self._arrumar()

    def _pixmap_da_pagina(self, item: ItemDaGrade) -> QPixmap | None:
        img = self._folhas.get(item.folha)
        if img is None:
            return None
        if self.metade is not None:
            try:
                img = self.metade(item.indice, img)
            except Exception:  # noqa: BLE001 - a página fica cinza, a tela segue
                registrar_erro("todas as páginas (metade)", traceback.format_exc())
                return None
        return QPixmap.fromImage(numpy_para_qimage(np.ascontiguousarray(img)))

    def _folha_chegou(self, folha: int, img) -> None:
        self._folhas[folha] = img
        if len(self._folhas) > MAXIMO_GUARDADAS:
            atual = next((i.folha for i in self.itens if i.indice == self.atual), 0)
            longe = max(self._folhas, key=lambda f: abs(f - atual))
            self._folhas.pop(longe)
        for quadro in self.quadros:
            for n, item in enumerate(quadro.itens):
                if item.folha == folha:
                    pix = self._pixmap_da_pagina(item)
                    if pix is not None:
                        quadro.definir_pixmap(n, pix)
