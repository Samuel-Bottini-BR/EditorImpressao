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
"""

from __future__ import annotations

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
        rotulo = str(self.numero)
        if self.em_alerta:
            rotulo += " !"
        if self.apagada:
            rotulo = "apagada"
        pintor.drawText(rodape, Qt.AlignCenter, rotulo)

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
        """Clique simples seleciona esta página."""
        if evento.button() == Qt.LeftButton:
            tira = self._tira()
            if tira is not None:
                tira.selecionada.emit(self.numero - 1)

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
        # D-618 (04/11/2026): o giro SO da pagina (metade de folha dividida),
        # por quadro (indice da miniatura -> 0/90/180/270), aplicado depois de
        # tirar a metade (definir_giros_das_paginas)
        self._giros_das_paginas: dict[int, int] = {}
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
        self.vertical = False
        self.em_pares = False
        self.pares_pela_vista = False      # D-611: "Duas lado a lado" escolhida
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
        """
        self.limpar()
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
        par = (indice + 1) // 2
        lado = 0 if (indice + 1) % 2 == 0 else 1       # página par à esquerda
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
                encostar = "direita" if (i + 1) % 2 == 0 else "esquerda"
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
        for mini in self._miniaturas:
            self.linha.removeWidget(mini)
            mini.setParent(None)
            mini.deleteLater()
        self._miniaturas.clear()
        self._mapa_folha.clear()
        self._cruas.clear()
        self._como_sai.clear()
        self._giros_das_paginas.clear()

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
                metade = self._metade(indice, img)
                giro = self._giros_das_paginas.get(indice, 0)      # D-618
                if giro:
                    metade = girar_90(metade, giro)
                self._miniaturas[indice].definir_imagem(metade)

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

    def definir_giros_das_paginas(self, giros: dict[int, int]) -> int:
        """D-618 (Samuel, 04/11/2026): o giro SO da pagina de cada quadro
        (indice da miniatura -> 0/90/180/270; quem falta = 0), na metade de uma
        folha dividida. Como definir_giros: redesenha so as folhas cujos
        quadros mudaram, da imagem guardada, sem ler o PDF. Devolve quantas
        folhas foram redesenhadas. Arriscado: por este giro na assinatura da
        tira (remontaria a tira inteira a cada giro)."""
        novos = {int(k): int(v) % 360 for k, v in giros.items() if int(v) % 360}
        mudaram = {i for i in set(novos) | set(self._giros_das_paginas)
                   if novos.get(i, 0) != self._giros_das_paginas.get(i, 0)}
        self._giros_das_paginas = novos
        folhas = {f for f, itens in self._mapa_folha.items() if mudaram & set(itens)}
        for indice_folha in folhas:
            self._mostrar_folha(indice_folha)
        return len([f for f in folhas if f in self._cruas])

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
