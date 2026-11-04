"""A tira de miniaturas do rodape da tela de conferir.

As miniaturas são geradas em segundo plano e bem pequenas (~90 px). Enquanto
não chegam, o quadro fica cinza com o número - a tela nunca espera por elas.

Girar a folha (D2 do verificador, 06/10/2026): a tira guarda a folha como
veio no PDF (uma imagem minuscula por folha) e mostra cada uma no giro dela
(definir_giros). Girar uma folha so redesenha os quadros dela, a partir da
imagem guardada - nada e lido do PDF de novo. Arriscado: remontar a tira
(montar) por causa de um giro - refaria a leitura do livro inteiro.

Etapa 5 do layout (21/10/2026; rodadas 7 e 8: as miniaturas embaixo, à
esquerda ou à direita junto da página, e "em pares"): os quadros ficam numa
grade (definir_arranjo): numa fila (embaixo) ou numa coluna (de lado); "em
pares" junta as páginas como no livro aberto - a 1 sozinha à direita, depois
2 e 3, 4 e 5. O número da página fica embaixo do desenho, sem cobri-lo (antes
o número e o "!" do aviso saíam por cima da página e cortados).

D-611 (Samuel, 04/11/2026, print a-56: "quando estiver duas lado a lado
escolhido os icones embaixo tem que estar em duas folhas" → "Sim" a "as
miniaturas embaixo também aparecem de duas em duas, juntas como no livro
aberto?"): com a vista "Duas lado a lado" escolhida, a tela liga os pares da
tira (definir_pares_pela_vista), o mesmo arranjo do "em pares". É separado do
"Ver em pares" do menu (em_pares, a escolha da pessoa, guardada para o
próximo livro): um não mexe no outro, e a tira fica em pares se um dos dois
estiver ligado.

D-611 refeita (04/11/2026; Samuel, testando: "4- não está ok coloquei no
primeiro print", print a-57): a grade já punha 1 | 2-3 | 4-5, mas com as
folhas divididas cada miniatura é uma página em pé, estreita, no meio de um
quadro de largura fixa - o vão entre os dois desenhos do par ficava igual ao de
"Uma página" (22 pontos), e a tira parecia uma a uma. Agora, com os pares da
vista ligados, as duas miniaturas do par ficam ENCOSTADAS como as duas páginas
do livro aberto: a da esquerda encosta o desenho no lado direito do quadro, a
da direita no lado esquerdo (Miniatura.encostar), sem vão entre os quadros do
par, e um vão entre um par e outro (ESPACO_ENTRE_PARES_DA_VISTA). O "Ver em
pares" sozinho (D-032, aprovado "Está bom" em 21/10) e "Uma página" ficam com
o jeito de antes. Arriscado: encostar também no "Ver em pares" do menu (muda
um jeito já aprovado, D-605).

D-615 (Samuel, 04/11/2026, print a-62: "eu quero poder mover folhas para onde eu
quiser dentro do app, quero poder arrastar e mover folhas" → "ok"): arrastar uma
miniatura e soltar noutro vão pede à tela para mudar a página (ou a folha) de
lugar (sinal mover_pedido). Enquanto arrasta, a miniatura fica apagadinha e uma
linha azul mostra o vão onde ela vai cair; perto da beirada a tira rola sozinha.
O clique continua indo para a página no apertar, como antes. Quando a tela
remonta a tira com os mesmos quadros em outra ordem, eles só trocam de lugar
(_reordenar): nada é lido do PDF de novo. Arriscado: trocar o arrastar à mão
pelo do Windows (QDrag: o piloto da janela não o move, e a tira inteira viraria
alvo de soltar arquivo).
"""

from __future__ import annotations

import time
import traceback

import numpy as np
from PySide6.QtCore import QEvent, QObject, QRunnable, QSize, Qt, QThreadPool, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from core.endireitar import girar_90
from core.pdf_io import abrir_pdf, limitar_altura, pagina_para_array
from registro import registrar_erro
from ui import estilo
from ui.widgets.visualizador import numpy_para_qimage

# A tira toda ocupa 58 px no desenho aprovado - contra os 144 de antes. Cada
# linha de altura sai da PAGINA, que e o que precisa ser olhado; a tira serve
# para achar a pagina, e para isso a miniatura nao precisa ser grande.
ALTURA_MINIATURA = 54       # a página desenhada (etapa 5: era 40, pequena demais)
LARGURA_MAXIMA = 62
LARGURA_DO_QUADRO = 50
ALTURA_DO_NUMERO = 16
ESPACO_ENTRE_PARES = 10     # o vão entre um par e outro, "em pares"
ESPACO_ENTRE_OS_QUADROS = 6  # o vão entre um quadro e outro (uma a uma e "Ver em pares")
# D-611 refeita (04/11): com "Duas lado a lado", os quadros do par encostam (vão
# 0) e entre um par e outro fica este vão - o mesmo total de antes (6 + 10 + 6).
ESPACO_ENTRE_PARES_DA_VISTA = 22

# Altura da folha guardada (como veio no PDF). Maior que o quadro de
# proposito: a folha em pe, girada 1/4, fica deitada, e a altura guardada
# vira a largura - com 40 ela ficaria esticada e borrada no quadro. A 20 DPI
# uma folha A4 tem ~230 pontos; aqui fica com 62 (cada uma, ~8 KB).
ALTURA_GUARDADA = LARGURA_MAXIMA


class _Sinais(QObject):
    """Sinal da tarefa de miniaturas - separado porque QRunnable nao e QObject."""

    pronta = Signal(int, object)   # indice_da_folha, imagem numpy


class _TarefaMiniaturas(QRunnable):
    """Gera as miniaturas de todas as folhas, em lote e em segundo plano."""

    def __init__(self, caminho_pdf: str, indices: list[int], sinais: _Sinais) -> None:
        super().__init__()
        self.caminho_pdf = caminho_pdf
        self.indices = indices
        self.sinais = sinais
        self.parar = False

    def run(self) -> None:
        """Le cada FOLHA uma vez (`self.indices` ja vem sem repeticao - ver
        montar()) em resolucao bem baixa (20 DPI) e emite conforme vai pronta.
        `self.parar` permite interromper no meio de um livro grande.

        O PDF e aberto e fechado a CADA folha (1 a 4 ms), e nao uma vez para o
        livro todo: com o desenho num processo a parte (core/
        paginas_em_outro_processo.py, 30/09/2026) a tira de um livro de 300
        folhas leva minutos, e o arquivo ficava preso esse tempo todo - no
        Windows, arquivo aberto nao se move, renomeia nem apaga. Arriscado:
        voltar a abrir uma vez so."""
        try:
            for indice in self.indices:
                if self.parar:
                    return
                doc = abrir_pdf(self.caminho_pdf)
                try:
                    img = pagina_para_array(doc, indice, dpi=20)
                finally:
                    doc.close()
                self.sinais.pronta.emit(indice, limitar_altura(img, ALTURA_GUARDADA))
        except Exception:  # noqa: BLE001
            registrar_erro("miniaturas", traceback.format_exc())


class Miniatura(QFrame):
    """Um quadrinho da tira."""

    def __init__(self, numero: int, parent=None) -> None:
        super().__init__(parent)
        self.numero = numero
        # D-611 atualizada (04/11/2026): o número de verdade da página, que a
        # tela diz (TiraMiniaturas.definir_numeros); None = `numero`. Só o que
        # aparece embaixo muda: o clique continua dizendo a posição (numero - 1).
        self.rotulo_numero: int | None = None
        self.selecionada = False
        self.em_alerta = False
        self.apagada = False
        # etapa 7 da obra (D-010, o exemplo do Samuel: "a folha fica
        # conferida, tique na miniatura"): o "está certo" deixa um tique verde
        self.conferida = False
        # D-611 refeita (04/11/2026): "direita" = a página da esquerda do par,
        # o desenho encosta no lado direito do quadro; "esquerda" = a página da
        # direita, encosta no lado esquerdo; None = no meio, como sempre.
        # Quem põe é a TiraMiniaturas (_arrumar), só com os pares da vista.
        self.encostar: str | None = None
        # D-615: a miniatura que está sendo arrastada fica apagadinha
        self.arrastada = False
        self._pixmap: QPixmap | None = None

        self.setFixedSize(QSize(LARGURA_DO_QUADRO, ALTURA_MINIATURA + ALTURA_DO_NUMERO + 4))
        self.setCursor(Qt.PointingHandCursor)

    def definir_imagem(self, img: np.ndarray) -> None:
        """Guarda a miniatura recebida e pede redesenho."""
        self._pixmap = QPixmap.fromImage(numpy_para_qimage(img))
        self.update()

    def paintEvent(self, evento) -> None:  # noqa: N802
        """Desenha a imagem (ou cinza, se ainda nao chegou), a moldura
        (azul=selecionada, laranja=alerta) e o número/rótulo embaixo.
        Com `encostar` (D-611 refeita, os pares da vista "Duas lado a lado")
        o desenho vai para um lado do quadro, com a moldura na beirada dele,
        e o número fica embaixo do desenho; o tamanho do desenho não muda."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)

        # o desenho em cima; o número embaixo, fora dele
        area = self.rect().adjusted(2, 2, -2, -(ALTURA_DO_NUMERO + 2))
        meio_do_desenho = None          # D-611 refeita: o número embaixo do desenho

        if self._pixmap is not None:
            # nos pixels de verdade (escala do Windows), para não sair mole
            from ui.widgets.todas_as_paginas import razao_do_pintor
            razao = razao_do_pintor(pintor)
            escalado = self._pixmap.scaled(
                round((area.width() - 4) * razao), round((area.height() - 4) * razao),
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            escalado.setDevicePixelRatio(razao)
            largura = round(escalado.width() / razao)
            altura = round(escalado.height() / razao)
            x = area.left() + (area.width() - largura) // 2
            # D-611 refeita: a moldura (2 pontos à esquerda do desenho e 1 à
            # direita, ver o adjusted abaixo) fica na beirada do quadro, e os
            # dois desenhos do par se encostam
            if self.encostar == "direita":
                x = self.width() - 2 - largura
            elif self.encostar == "esquerda":
                x = 2
            if self.encostar is not None:
                meio_do_desenho = x + largura // 2
            y = area.top() + (area.height() - altura) // 2
            pintor.drawPixmap(x, y, escalado)
            area = area.adjusted(x - area.left() - 2, y - area.top() - 2,
                                 -(area.right() - (x + largura) - 1),
                                 -(area.bottom() - (y + altura) - 1))
        else:
            pintor.fillRect(area.adjusted(4, 2, -4, -2), QColor(estilo.cor("cabeca")))

        if self.apagada:
            pintor.fillRect(area, QColor(255, 255, 255, 165))
        if self.conferida and not self.apagada:
            self._pintar_o_tique(pintor, area)

        # moldura: laranja quando ha alerta, azul quando selecionada
        if self.selecionada:
            cor, espessura = QColor(estilo.AZUL), 3
        elif self.em_alerta:
            cor, espessura = QColor(estilo.LARANJA), 2
        else:
            cor, espessura = QColor(estilo.BORDA), 1
        caneta = pintor.pen()
        caneta.setColor(cor)
        caneta.setWidth(espessura)
        pintor.setPen(caneta)
        pintor.drawRect(area)

        rodape = self.rect().adjusted(0, self.height() - ALTURA_DO_NUMERO - 1, 0, -1)
        if meio_do_desenho is not None:
            rodape.translate(meio_do_desenho - rodape.center().x(), 0)
        pintor.setPen(QColor(estilo.LARANJA) if self.em_alerta else QColor(estilo.TEXTO_FRACO))
        rotulo = str(self.rotulo_numero if self.rotulo_numero is not None else self.numero)
        if self.em_alerta:
            rotulo += " !"
        if self.apagada:
            rotulo = "apagada"
        pintor.drawText(rodape, Qt.AlignCenter, rotulo)
        if self.arrastada:
            # D-615: a que anda fica apagadinha (o lugar de onde ela sai)
            fundo = QColor(estilo.cor("bar"))
            fundo.setAlpha(170)
            pintor.fillRect(self.rect(), fundo)

    @staticmethod
    def _pintar_o_tique(pintor: QPainter, area) -> None:
        """O tique de "conferida" no canto de cima, à direita, do desenho:
        uma bolinha verde com o sinal de certo desenhado em traços (sem
        caractere especial: nenhum emoji ou símbolo em rótulo, CLAUDE.md §3)."""
        from PySide6.QtCore import QPointF, QRectF
        from PySide6.QtGui import QPen

        lado = 13.0
        caixa = QRectF(area.right() - lado - 1, area.top() + 1, lado, lado)
        pintor.save()
        pintor.setPen(Qt.NoPen)
        verde = QColor(estilo.cor("ok"))
        pintor.setBrush(verde)
        pintor.drawEllipse(caixa)
        # o traço escuro no verde claro dos temas escuros, branco no verde
        # escuro do tema claro
        caneta = QPen(QColor(20, 20, 20) if verde.lightness() > 128 else QColor(255, 255, 255))
        caneta.setWidthF(1.8)
        caneta.setCapStyle(Qt.RoundCap)
        caneta.setJoinStyle(Qt.RoundJoin)
        pintor.setPen(caneta)
        x, y = caixa.left(), caixa.top()
        pintor.drawPolyline([QPointF(x + 3.2, y + 6.8), QPointF(x + 5.6, y + 9.2),
                             QPointF(x + 9.8, y + 4.0)])
        pintor.restore()

    def _tira(self):
        """Sobe na arvore de widgets ate achar a TiraMiniaturas dona, para
        emitir os sinais dela (a miniatura nao guarda referencia direta)."""
        tira = self.parent()
        while tira is not None and not isinstance(tira, TiraMiniaturas):
            tira = tira.parent()
        return tira

    def mousePressEvent(self, evento) -> None:  # noqa: N802
        """Clique simples seleciona esta página (como sempre: na hora do
        clique). D-615: o botão apertado pode virar um arrastar, se o mouse
        andar (mouseMoveEvent)."""
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira._apertou(self, evento.globalPosition().toPoint())
                tira.selecionada.emit(self.numero - 1)

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802
        """D-615: com o botão apertado, andar o mouse mais que a distância de
        arrastar do Windows começa a mudar a página de lugar (a tira mostra a
        linha azul de onde ela vai cair)."""
        if evento.buttons() & Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira._andou(evento.globalPosition().toPoint())

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802
        """D-615: soltar o botão depois de arrastar muda a página de lugar (a
        tira pede à tela, sinal mover_pedido). Sem arrastar, nada (o clique já
        foi feito no apertar)."""
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira._soltou(evento.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, evento) -> None:  # noqa: N802
        """Duplo clique abre a página em tamanho grande."""
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira.ampliar_pedido.emit(self.numero - 1)


class TiraMiniaturas(QWidget):
    """A tira inteira, com rolagem horizontal."""

    selecionada = Signal(int)
    ampliar_pedido = Signal(int)   # duplo clique numa miniatura
    # D-615: arrastou a miniatura `origem` e soltou no vão `destino` (0 = antes
    # da primeira; quantidade = depois da última). Quem muda o livro é a tela.
    mover_pedido = Signal(int, int)

    def __init__(self, titulo: str, parent=None) -> None:
        """Monta a area de rolagem vazia; os quadros so aparecem em `montar`."""
        super().__init__(parent)
        self._miniaturas: list[Miniatura] = []
        self._tarefa: _TarefaMiniaturas | None = None
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(1)
        self._sinais = _Sinais()
        self._sinais.pronta.connect(self._receber)
        self._mapa_folha: dict[int, list[int]] = {}
        self._cortes: dict[int, tuple[str, float]] = {}
        # D2 (06/10/2026): a folha como veio no PDF, por folha, e o giro com
        # que cada uma esta sendo mostrada (definir_giros)
        self._cruas: dict[int, np.ndarray] = {}
        self._giros: dict[int, int] = {}
        # Etapa 9b-2 da obra (D-547: "Mover uma página → a miniatura [...]
        # mostra igual ao PDF"): a página movida ou posta numa folha escolhida
        # aparece como sai no PDF (a prévia composta, que a tela dá em
        # definir_como_sai), no lugar da folha crua. indice -> (chave, imagem)
        self._como_sai: dict[int, tuple[str, np.ndarray]] = {}
        # Achado do verificador clicando (03/11/2026, print t1-22): depois de
        # remontar (montar), os quadros novos só ficam no lugar quando o Qt
        # arruma a grade (depois deste fio voltar ao laço de eventos); rolar
        # até a escolhida ANTES disso rolava para o começo. montar() liga
        # isto e selecionar() rola de novo quando a grade já está arrumada
        # (_rolar_ate_a_escolhida).
        self._rolar_depois_de_montar = False
        # o PDF dos quadros de agora (D-615: montar com o mesmo PDF e os mesmos
        # quadros em outra ordem só os troca de lugar, _reordenar)
        self._caminho: str | None = None

        fora = QVBoxLayout(self)
        fora.setContentsMargins(0, 0, 0, 0)
        fora.setSpacing(2)

        # O rotulo acima da tira saiu: custava 18 px e dizia o que a propria
        # cor ja diz. A explicacao das cores foi para a dica do mouse.
        self.rotulo = QLabel(titulo)
        self.rotulo.setVisible(False)
        self.setToolTip("A selecionada tem borda grossa. "
                        "As laranjas são as que eu não tive certeza.")

        self.rolagem = QScrollArea()
        self.rolagem.setWidgetResizable(True)
        self.rolagem.setFrameShape(QFrame.NoFrame)
        # Etapa 9b-1 (o foco preso, achado das etapas 5 e 6): a rolagem da tira
        # ficava com o teclado (ao abrir o livro e a cada clique numa
        # miniatura), e o Page Down, as setas, o Home e o End rolavam a tira
        # em vez de trocar a página (D-021). A roda do mouse, a barra e as
        # setinhas da tira continuam rolando; o teclado fica com a página.
        self.rolagem.setFocusPolicy(Qt.NoFocus)

        interno = QWidget()
        interno.setObjectName("dentroDaTira")
        self.linha = QGridLayout(interno)
        self.linha.setContentsMargins(4, 2, 4, 2)
        self.linha.setSpacing(ESPACO_ENTRE_OS_QUADROS)
        self.rolagem.setWidget(interno)
        fora.addWidget(self.rolagem)

        # D-615 (04/11/2026): arrastar uma miniatura muda a página de lugar. A
        # linha azul (fora da grade, por cima dos quadros) mostra o vão onde
        # ela vai cair; a rolagem anda sozinha perto das beiradas.
        self._arrasto: dict | None = None
        self.sinal_do_vao = QFrame(interno)
        self.sinal_do_vao.setObjectName("sinalDoVao")
        self.sinal_do_vao.setStyleSheet(f"QFrame#sinalDoVao {{ background: {estilo.AZUL}; }}")
        self.sinal_do_vao.setVisible(False)
        self._relogio_da_beirada = QTimer(self)
        self._relogio_da_beirada.setInterval(40)
        self._relogio_da_beirada.timeout.connect(self._rolar_na_beirada)
        self.vertical = False
        self.em_pares = False
        self.pares_pela_vista = False      # D-611: "Duas lado a lado" escolhida
        # D-611 atualizada (04/11): os pares da tela grande (definir_grupos)
        self._grupos: list[list[int | None]] | None = None
        self._lugar_no_grupo: dict[int, tuple[int, int, int]] = {}
        self.definir_arranjo(False, False)

    def montar(self, quantidade: int, caminho_pdf: str, folha_de: dict[int, int],
               corte_de: dict[int, tuple[str, float]] | None = None,
               giros: dict[int, int] | None = None) -> None:
        """Cria os quadros e dispara a geracao das imagens.

        folha_de mapeia o indice do item (página ou folha) para a folha do PDF
        de onde ele vem - duas páginas de uma mesma folha reaproveitam a mesma
        leitura, entao o PDF e lido uma vez só por folha.

        corte_de diz, para cada página, qual metade da folha ela e. Sem isso a
        miniatura de uma página mostraria a folha dupla inteira, e o usuario
        veria a mesma imagem em duas páginas seguidas.

        giros: o giro de cada folha (indice da folha -> 0/90/180/270); o
        mesmo de definir_giros.

        D-615 (04/11/2026): se os quadros pedidos são OS MESMOS de agora (mesmo
        PDF, mesma folha e metade de cada um), só em outra ordem - a página
        mudada de lugar, ou o Ctrl+Z disso -, os quadros só trocam de lugar
        (_reordenar): nada é lido do PDF de novo (num livro de 1010 páginas a
        tira inteira ficaria cinza por um bom tempo).
        """
        if self._reordenar(quantidade, caminho_pdf, folha_de, corte_de, giros):
            return
        self.limpar()
        self._caminho = caminho_pdf
        self._cortes = corte_de or {}
        self._giros = {int(k): int(v) % 360 for k, v in (giros or {}).items()}
        self._rolar_depois_de_montar = True

        for i in range(quantidade):
            mini = Miniatura(i + 1)
            self._miniaturas.append(mini)
            self._mapa_folha.setdefault(folha_de.get(i, i), []).append(i)
        self._arrumar()

        indices_de_folha = sorted(self._mapa_folha)
        self._tarefa = _TarefaMiniaturas(caminho_pdf, indices_de_folha, self._sinais)
        self._pool.start(self._tarefa)

    def _reordenar(self, quantidade: int, caminho_pdf: str, folha_de: dict[int, int],
                   corte_de: dict | None, giros: dict | None) -> bool:
        """D-615: os quadros pedidos por `montar` são os de agora em outra ordem?
        Então troca os quadros de lugar (com a imagem, as marcas e o "como sai"
        de cada um), renumera e devolve True. Senão (outro PDF, outra
        quantidade, um quadro novo, ou a mesma ordem) devolve False e `montar`
        faz como sempre. Barato: só reposiciona (nenhum PDF é lido, nenhuma
        imagem é refeita). Arriscado: aceitar quadro que não existia (ficaria
        sem imagem)."""
        from collections import defaultdict, deque

        if (not self._miniaturas or quantidade != len(self._miniaturas)
                or caminho_pdf != getattr(self, "_caminho", None)):
            return False
        corte_de = corte_de or {}
        folha_antiga = {i: f for f, itens in self._mapa_folha.items() for i in itens}

        def quem(folha, corte):
            return (folha, tuple(corte) if corte is not None else None)

        filas: dict = defaultdict(deque)
        for i in range(quantidade):
            filas[quem(folha_antiga.get(i, i), self._cortes.get(i))].append(i)
        nova = []
        for k in range(quantidade):
            fila = filas.get(quem(folha_de.get(k, k), corte_de.get(k)))
            if not fila:
                return False
            nova.append(fila.popleft())
        if nova == list(range(quantidade)):
            return False
        self._miniaturas = [self._miniaturas[i] for i in nova]
        for k, mini in enumerate(self._miniaturas):
            if mini.numero != k + 1:
                mini.numero = k + 1
                mini.update()
        self._mapa_folha = {}
        for k in range(quantidade):
            self._mapa_folha.setdefault(folha_de.get(k, k), []).append(k)
        self._cortes = dict(corte_de)
        self._como_sai = {k: self._como_sai[i] for k, i in enumerate(nova) if i in self._como_sai}
        if giros:
            self.definir_giros({int(f): int(g) for f, g in giros.items()})
        self._rolar_depois_de_montar = True
        self._arrumar()
        return True

    # --- D-615: arrastar uma miniatura para mudar a página de lugar ----------
    # Samuel, 04/11/2026 (print a-62): "eu quero poder mover folhas para onde eu
    # quiser dentro do app, quero poder arrastar e mover folhas" → "ok" a
    # "arrastar a miniatura da tira e soltar onde quiser". O arrastar é feito à
    # mão (apertar, andar, soltar), sem o arrastar-e-soltar do Windows: só dentro
    # da tira, e funciona igual com o mouse de verdade e com o piloto da janela.
    # O clique continua indo para a página NA HORA do apertar, como antes; só
    # andar mais que a distância de arrastar do Windows começa a mudar de lugar.
    # A tira só mostra e avisa (mover_pedido); quem muda o livro é a tela.
    # Arriscado: escolher a página no soltar (o clique mudaria de jeito); mudar o
    # livro aqui (o desfazer não veria).

    def _apertou(self, mini: "Miniatura", ponto) -> None:
        """O botão foi apertado numa miniatura: guarda de onde (ainda não é
        arrastar)."""
        if mini not in self._miniaturas:
            return
        self._arrasto = {"mini": mini, "inicio": ponto, "andando": False, "vao": None}

    def _andou(self, ponto) -> None:
        """O mouse andou com o botão apertado: passou da distância de
        arrastar, começa; arrastando, a linha azul vai para o vão mais perto."""
        from PySide6.QtWidgets import QApplication

        arrasto = self._arrasto
        if arrasto is None:
            return
        if not arrasto["andando"]:
            if (ponto - arrasto["inicio"]).manhattanLength() < QApplication.startDragDistance():
                return
            arrasto["andando"] = True
            arrasto["mini"].arrastada = True
            arrasto["mini"].update()
            arrasto["mini"].setCursor(Qt.ClosedHandCursor)
            self._relogio_da_beirada.start()
        arrasto["ponto"] = ponto
        self._mostrar_o_vao(ponto)

    def _soltou(self, ponto) -> None:
        """O botão foi solto: se estava arrastando e há um vão, pede à tela
        para mudar a página de lugar (depois deste evento, pelo laço do Qt: a
        tela remonta a tira). Soltar fora da tira não muda nada."""
        arrasto, self._arrasto = self._arrasto, None
        if arrasto is None:
            return
        self._relogio_da_beirada.stop()
        self.sinal_do_vao.setVisible(False)
        mini = arrasto["mini"]
        mini.arrastada = False
        mini.setCursor(Qt.PointingHandCursor)
        mini.update()
        if not arrasto["andando"] or mini not in self._miniaturas:
            return
        vao = self.vao_do_ponto(ponto)
        if vao is None:
            return
        origem = self._miniaturas.index(mini)
        if vao in (origem, origem + 1):
            return                                  # soltou no mesmo lugar
        QTimer.singleShot(0, lambda o=origem, v=vao: self.mover_pedido.emit(o, v))

    def arrastando(self) -> bool:
        """Uma miniatura está sendo arrastada agora?"""
        return bool(self._arrasto and self._arrasto.get("andando"))

    def vao_do_ponto(self, ponto) -> int | None:
        """O vão onde a miniatura cai com o mouse em `ponto` (na tela): 0 =
        antes da primeira, N = depois da última. None = fora da tira (longe
        dela, soltar ali não muda nada). Acha o quadro mais perto do mouse e,
        pela metade dele em que o mouse está, o vão antes ou depois dele.
        Passar da beirada no sentido da tira (à esquerda ou à direita da fila)
        vale como estar na beirada (a tira rola até lá); só longe no outro
        sentido (bem acima ou abaixo da fila) é "fora"."""
        from PySide6.QtCore import QPoint

        if not self._miniaturas:
            return None
        janela = self.rolagem.viewport()
        local = janela.mapFromGlobal(ponto)
        folga = 60
        de_lado = self.vertical
        cruzado, comprimento = ((local.x(), janela.width()) if de_lado else (local.y(), janela.height()))
        if cruzado < -folga or cruzado > comprimento + folga:
            return None
        # no sentido da tira, o ponto fica dentro da parte à vista
        if de_lado:
            local = QPoint(local.x(), max(0, min(janela.height() - 1, local.y())))
        else:
            local = QPoint(max(0, min(janela.width() - 1, local.x())), local.y())
        interno = self.rolagem.widget()
        p = interno.mapFrom(janela, local)
        melhor, distancia = 0, None
        for i, mini in enumerate(self._miniaturas):
            g = mini.geometry()
            dx = max(g.left() - p.x(), 0, p.x() - g.right())
            dy = max(g.top() - p.y(), 0, p.y() - g.bottom())
            d = dx * dx + dy * dy
            if distancia is None or d < distancia:
                melhor, distancia = i, d
                if d == 0:
                    break
        g = self._miniaturas[melhor].geometry()
        if self.vertical and not self.em_pares_agora:
            depois = p.y() > g.center().y()
        else:
            depois = p.x() > g.center().x()
        return melhor + 1 if depois else melhor

    def _mostrar_o_vao(self, ponto) -> None:
        """Põe a linha azul no vão do ponto (ou a esconde fora da tira). Na
        fila: uma linha em pé entre os dois quadros; na coluna: deitada."""
        vao = self.vao_do_ponto(ponto)
        if self._arrasto is not None:
            self._arrasto["vao"] = vao
        sinal = self.sinal_do_vao
        if vao is None:
            sinal.setVisible(False)
            return
        n = len(self._miniaturas)
        de_pe = not (self.vertical and not self.em_pares_agora)
        if vao < n:
            g = self._miniaturas[vao].geometry()
            antes = self._miniaturas[vao - 1].geometry() if vao > 0 else None
        else:
            antes = self._miniaturas[n - 1].geometry()
            g = None
        espessura = 4
        if de_pe:
            if g is not None and antes is not None and abs(antes.center().y() - g.center().y()) < 4:
                x = (antes.right() + g.left()) // 2
            elif g is not None:
                x = g.left() - 3
            else:
                x = antes.right() + 3
            ref = g or antes
            sinal.setGeometry(x - espessura // 2, ref.top(), espessura, ref.height())
        else:
            if g is not None and antes is not None:
                y = (antes.bottom() + g.top()) // 2
            elif g is not None:
                y = g.top() - 3
            else:
                y = antes.bottom() + 3
            ref = g or antes
            sinal.setGeometry(ref.left(), y - espessura // 2, ref.width(), espessura)
        sinal.setVisible(True)
        sinal.raise_()

    def _rolar_na_beirada(self) -> None:
        """Arrastando com o mouse perto da beirada da tira, ela rola sozinha
        (para levar a página longe sem soltar). Nunca levanta."""
        try:
            if not self.arrastando() or self._arrasto.get("ponto") is None:
                if not self.arrastando():
                    self._relogio_da_beirada.stop()
                return
            ponto = self._arrasto["ponto"]          # onde o mouse parou por último
            if self._arrasto.get("vao") is None:
                return                              # longe da tira: não rola
            janela = self.rolagem.viewport()
            local = janela.mapFromGlobal(ponto)
            if self.vertical:
                barra, pos, tamanho = self.rolagem.verticalScrollBar(), local.y(), janela.height()
            else:
                barra, pos, tamanho = self.rolagem.horizontalScrollBar(), local.x(), janela.width()
            beirada = 36
            if pos < beirada:
                passo = -min(60, max(6, beirada - pos))
            elif pos > tamanho - beirada:
                passo = min(60, max(6, pos - (tamanho - beirada)))
            else:
                self._arrasto.pop("na_beirada_desde", None)
                return
            # quanto mais tempo parado na beirada, mais depressa (até 4 vezes):
            # num livro de 1010 páginas a tira tem metros
            desde = self._arrasto.setdefault("na_beirada_desde", time.monotonic())
            passo = int(passo * min(4.0, 1.0 + (time.monotonic() - desde)))
            barra.setValue(barra.value() + passo)
            self._mostrar_o_vao(ponto)
        except RuntimeError:
            pass

    # --- o arranjo (etapa 5 do layout) -----------------------------------

    def definir_arranjo(self, vertical: bool, em_pares: bool) -> None:
        """Fila (embaixo) ou coluna (de lado), e "em pares" ou não. Só
        reposiciona os quadros que já existem: nada é lido do PDF de novo."""
        self.vertical = bool(vertical)
        self.em_pares = bool(em_pares)
        rolagem = self.rolagem
        altura_do_quadro = ALTURA_MINIATURA + ALTURA_DO_NUMERO + 4
        if self.vertical:
            rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            rolagem.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            rolagem.setMinimumHeight(0)
            rolagem.setMaximumHeight(16777215)
        else:
            rolagem.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            rolagem.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            rolagem.setFixedHeight(altura_do_quadro + 18)
        self._arrumar()

    def definir_pares_pela_vista(self, ligado: bool) -> None:
        """D-611 (ver o começo do arquivo): a tela liga os pares da tira com a
        vista "Duas lado a lado" e desliga com "Uma página". Só reposiciona os
        quadros que já existem (nada é lido do PDF) e rola até a escolhida de
        novo, com a grade já arrumada. Não toca no "Ver em pares" (em_pares).
        Arriscado: gravar isto como a escolha da pessoa (o próximo livro
        abriria em pares em "Uma página")."""
        if bool(ligado) == self.pares_pela_vista:
            return
        self.pares_pela_vista = bool(ligado)
        self._arrumar()
        QTimer.singleShot(0, self._rolar_ate_a_escolhida)

    # --- o número de verdade e os pares da tela (D-611 atualizada, 04/11/2026) ----------
    #
    # Samuel, à pergunta "no Dividir, a tela grande mostra a folha 6, com as páginas
    # 11 e 12, mas a tira junta a 10 com a 11. Quer que a tira junte igual à tela
    # grande, a 11 com a 12?": "SIm, mas tem que verificar se vai ficar assim em todo
    # os lugares né? a miniatura corresponder com o numero real". A tela diz o número
    # de cada quadro (definir_numeros: o número da página no livro, o mesmo de
    # "página N de M") e, com os pares da vista, como juntar (definir_grupos: os
    # mesmos pares da tela grande). Sem isso, como sempre: o número é a posição
    # do quadro + 1 e os pares são os do livro aberto pela posição.

    def definir_numeros(self, numeros: dict[int, int] | None) -> None:
        """O número embaixo de cada quadro (quadro -> número). None: a posição + 1."""
        numeros = numeros or {}
        for i, mini in enumerate(self._miniaturas):
            numero = numeros.get(i)
            if mini.rotulo_numero != numero:
                mini.rotulo_numero = numero
                mini.update()

    def definir_grupos(self, grupos: list[list[int | None]] | None) -> None:
        """Como os quadros se juntam com os pares da vista: uma lista de pares,
        cada um [esquerda, direita] (None = o lado vazio, como a 1 sozinha à
        direita) ou [sozinho] (no meio do par). None: os pares do livro aberto
        pela posição, como sempre. Só vale com os pares da vista ligados."""
        grupos = [list(g) for g in grupos] if grupos else None
        if grupos == self._grupos:
            return
        self._grupos = grupos
        self._lugar_no_grupo = {}
        for numero, grupo in enumerate(grupos or []):
            for lado, indice in enumerate(grupo):
                if indice is not None:
                    self._lugar_no_grupo[indice] = (numero, lado, len(grupo))
        if self.pares_pela_vista:
            self._arrumar()
            QTimer.singleShot(0, self._rolar_ate_a_escolhida)

    def _lado_para_encostar(self, indice: int) -> str | None:
        """Para que lado o desenho do quadro encosta, com os pares da vista."""
        lugar = self._lugar_no_grupo.get(indice) if self._grupos else None
        if lugar is None:
            return "direita" if (indice + 1) % 2 == 0 else "esquerda"
        _par, lado, tamanho = lugar
        if tamanho < 2:
            return None
        return "direita" if lado == 0 else "esquerda"

    @property
    def em_pares_agora(self) -> bool:
        """A tira está em pares: pelo "Ver em pares" do menu ou pela vista
        "Duas lado a lado" (D-611)."""
        return self.em_pares or self.pares_pela_vista

    def posicao(self, indice: int) -> tuple[int, int]:
        """(linha, coluna) do quadro `indice` na grade. "Em pares", como no
        livro aberto: a página 1 sozinha, do lado direito; depois 2 e 3, 4 e
        5... Na fila, um vão (uma coluna vazia) separa cada par. Em pares pelo
        "Ver em pares" ou pela vista "Duas lado a lado" (D-611)."""
        if not self.em_pares_agora:
            return (indice, 0) if self.vertical else (0, indice)
        lugar = (self._lugar_no_grupo.get(indice)
                 if self._grupos and self.pares_pela_vista else None)
        if lugar is not None:                           # os pares da tela (definir_grupos)
            par, lado, _tamanho = lugar
        else:
            par = (indice + 1) // 2
            lado = 0 if (indice + 1) % 2 == 0 else 1   # página par à esquerda
        if self.vertical:
            return par, lado
        return 0, par * 3 + lado                        # coluna 3*par+2 fica vazia (o vão)

    def _arrumar(self) -> None:
        """Põe cada quadro no lugar da grade (posicao) e o espaço que sobra no fim.

        D-611 refeita (04/11/2026): com os pares da vista ("Duas lado a lado"),
        os dois quadros do par ficam sem vão e com o desenho encostado no
        outro (Miniatura.encostar), e entre um par e outro fica
        ESPACO_ENTRE_PARES_DA_VISTA. Sem eles ("Uma página", ou só o "Ver em
        pares" do menu), o vão e o desenho no meio, como antes."""
        grade = self.linha
        while grade.count():
            grade.takeAt(0)
        for linha in range(grade.rowCount()):
            grade.setRowStretch(linha, 0)
            grade.setRowMinimumHeight(linha, 0)
        for coluna in range(grade.columnCount()):
            grade.setColumnStretch(coluna, 0)
            grade.setColumnMinimumWidth(coluna, 0)
        juntos = self.pares_pela_vista
        grade.setHorizontalSpacing(0 if juntos else ESPACO_ENTRE_OS_QUADROS)
        ultima_linha = ultima_coluna = 0
        for i, mini in enumerate(self._miniaturas):
            linha, coluna = self.posicao(i)
            encostar = None
            if juntos:
                # a página par fica à esquerda do par (posicao): encosta à direita
                # (com os pares da tela, definir_grupos: a da esquerda do par)
                encostar = self._lado_para_encostar(i)
            if mini.encostar != encostar:
                mini.encostar = encostar
                mini.update()
            grade.addWidget(mini, linha, coluna, Qt.AlignCenter)
            ultima_linha, ultima_coluna = max(ultima_linha, linha), max(ultima_coluna, coluna)
        if self.em_pares_agora and not self.vertical:
            vao = ESPACO_ENTRE_PARES_DA_VISTA if juntos else ESPACO_ENTRE_PARES
            for coluna in range(2, ultima_coluna + 1, 3):
                grade.setColumnMinimumWidth(coluna, vao)
        if self.vertical:
            grade.setRowStretch(ultima_linha + 1, 1)
        else:
            grade.setColumnStretch(ultima_coluna + 1, 1)

    def limpar(self) -> None:
        """Interrompe a geracao em andamento e tira todos os quadros - usado
        antes de remontar (livro novo) e em `parar`."""
        if self._tarefa is not None:
            self._tarefa.parar = True
            self._tarefa = None
        # D-615: um arrastar no meio acaba (os quadros vão sair)
        self._arrasto = None
        self._relogio_da_beirada.stop()
        self.sinal_do_vao.setVisible(False)
        for mini in self._miniaturas:
            self.linha.removeWidget(mini)
            mini.setParent(None)
            mini.deleteLater()
        self._miniaturas.clear()
        self._grupos, self._lugar_no_grupo = None, {}      # D-611: a tela diz de novo
        self._mapa_folha.clear()
        self._cruas.clear()
        self._como_sai.clear()

    def _receber(self, indice_folha: int, img: np.ndarray) -> None:
        """Uma folha chegou pronta: guarda como veio e distribui (girada e
        recortada pela metade certa) para TODAS as páginas que vieram dela
        (ver _mapa_folha em montar())."""
        if indice_folha not in self._mapa_folha:
            return                    # de uma tira que ja foi remontada
        self._cruas[indice_folha] = img
        self._mostrar_folha(indice_folha)

    def _mostrar_folha(self, indice_folha: int) -> None:
        """Poe a folha guardada, no giro dela, nos quadros que vem dela. A
        ordem e a do programa (core/pipeline.preparar_metade): girar, depois
        dividir."""
        img = self._cruas.get(indice_folha)
        if img is None:
            return
        giro = self._giros.get(indice_folha, 0)
        if giro:
            img = girar_90(img, giro)
        for indice in self._mapa_folha.get(indice_folha, []):
            if 0 <= indice < len(self._miniaturas) and indice not in self._como_sai:
                self._miniaturas[indice].definir_imagem(self._metade(indice, img))

    def definir_como_sai(self, indice: int, chave: str = "", img: np.ndarray | None = None) -> bool:
        """Etapa 9b-2 (D-547): a miniatura `indice` passa a mostrar `img` (a
        página como sai no PDF, já movida); `img` None volta à folha crua.
        `chave` diz de que estado é a imagem: a mesma chave não redesenha.
        Devolve True se a miniatura mudou."""
        if not 0 <= indice < len(self._miniaturas):
            return False
        if img is None:
            if self._como_sai.pop(indice, None) is None:
                return False
            folha = next((f for f, itens in self._mapa_folha.items() if indice in itens), None)
            if folha is not None:
                self._mostrar_folha(folha)
            return True
        if self._como_sai.get(indice, ("",))[0] == chave and chave:
            return False
        from core.pdf_io import limitar_altura

        pequena = limitar_altura(img, ALTURA_GUARDADA * 2)
        self._como_sai[indice] = (chave, pequena)
        self._miniaturas[indice].definir_imagem(pequena)
        return True

    def definir_giros(self, giros: dict[int, int]) -> int:
        """O giro de cada folha (indice da folha -> 0/90/180/270). Redesenha
        so as folhas cujo giro mudou, a partir da imagem guardada (sem ler o
        PDF, no fio da tela: girar uma imagem de 62 pontos leva microssegundos).
        Devolve quantas folhas foram redesenhadas. Folha que ainda nao chegou
        so anota o giro (sai certa quando chegar)."""
        mudaram = 0
        for indice_folha, giro in giros.items():
            giro = int(giro) % 360
            if self._giros.get(indice_folha, 0) == giro:
                continue
            self._giros[indice_folha] = giro
            if indice_folha in self._cruas:
                self._mostrar_folha(indice_folha)
                mudaram += 1
        return mudaram

    def definir_cortes(self, corte_de: dict[int, tuple[str, float]]) -> int:
        """D-601 (02/11/2026): a metade e a linha de cada miniatura (o mesmo
        corte_de de montar), sem ler o PDF de novo: mover a linha no Dividir
        redesenha só as folhas cujas miniaturas mudaram, a partir da imagem
        guardada (como definir_giros). Devolve quantas folhas foram
        redesenhadas. Seguro mudar: nada; arriscado: remontar a tira aqui (a
        tira inteira seria lida do PDF a cada arrasto da linha)."""
        folhas: set[int] = set()
        for indice, dados in corte_de.items():
            if self._cortes.get(indice) == dados:
                continue
            self._cortes[indice] = dados
            folhas.update(f for f, itens in self._mapa_folha.items() if indice in itens)
        for indice_folha in folhas:
            self._mostrar_folha(indice_folha)
        return len([f for f in folhas if f in self._cruas])

    def _metade(self, indice: int, img: np.ndarray) -> np.ndarray:
        """Recorta a metade que esta página representa."""
        dados = self._cortes.get(indice)
        if not dados:
            return img
        metade, posicao = dados
        largura = img.shape[1]
        corte = max(1, min(largura - 1, int(posicao * largura)))
        if metade == "esquerda":
            return img[:, :corte]
        if metade == "direita":
            return img[:, corte:]
        return img

    # --- estado -----------------------------------------------------------

    def marcar(self, indice: int, em_alerta: bool = False, apagada: bool = False,
               conferida: bool = False) -> None:
        """Liga/desliga a moldura de alerta, a marca de apagada e o tique de
        conferida (etapa 7 da obra) de uma miniatura. Só redesenha se mudou."""
        if 0 <= indice < len(self._miniaturas):
            mini = self._miniaturas[indice]
            novo = (bool(em_alerta), bool(apagada), bool(conferida))
            if (mini.em_alerta, mini.apagada, mini.conferida) == novo:
                return
            mini.em_alerta, mini.apagada, mini.conferida = novo
            mini.update()

    def selecionar(self, indice: int) -> None:
        """Marca a miniatura escolhida (borda grossa) e rola a tira para ela ficar visivel."""
        for i, mini in enumerate(self._miniaturas):
            estava = mini.selecionada
            mini.selecionada = i == indice
            if estava != mini.selecionada:
                mini.update()
        if 0 <= indice < len(self._miniaturas):
            folga = (0, 120) if self.vertical else (200, 0)
            self.rolagem.ensureWidgetVisible(self._miniaturas[indice], *folga)
        if self._rolar_depois_de_montar:
            # a tira acabou de ser remontada (o Ctrl+Z ou o refazer de dividir/
            # juntar, por exemplo): rola de novo quando os quadros estiverem
            # no lugar (achado do verificador clicando, 03/11/2026)
            self._rolar_depois_de_montar = False
            QTimer.singleShot(0, self._rolar_ate_a_escolhida)

    def _rolar_ate_a_escolhida(self) -> None:
        """Rola a tira até a miniatura escolhida, com a grade já arrumada:
        arruma a grade agora (os quadros novos já apareceram) e deixa a
        rolagem acertar o tamanho de dentro antes de rolar. Chamado uma vez
        depois de remontar (selecionar). Nunca levanta: é só a rolagem.
        Arriscado: rolar sem arrumar a grade antes (os quadros novos estão
        todos na posição 0 e a tira vai para o começo)."""
        try:
            from PySide6.QtWidgets import QApplication

            escolhida = next((m for m in self._miniaturas if m.selecionada), None)
            if escolhida is None:
                return
            self.linha.activate()
            QApplication.sendPostedEvents(None, QEvent.LayoutRequest)
            folga = (0, 120) if self.vertical else (200, 0)
            self.rolagem.ensureWidgetVisible(escolhida, *folga)
        except RuntimeError:          # a tira foi apagada no meio (fechar o livro)
            pass

    def definir_titulo(self, texto: str) -> None:
        """Muda o texto do rotulo (hoje invisivel - ver o comentario no __init__)."""
        self.rotulo.setText(texto)

    def parar(self) -> None:
        """Interrompe a geracao e espera a thread atual terminar. Chamar ao
        trocar de livro ou fechar, para nao deixar tarefa orfa escrevendo
        numa tira que ja nao existe mais."""
        self.limpar()
        self._pool.waitForDone(2000)
        # O servidor de paginas fecha o livro na hora (senao, em meio segundo):
        # a pessoa pode mover o PDF logo depois de fechar.
        from core.paginas_em_outro_processo import soltar_livro

        soltar_livro(None)
