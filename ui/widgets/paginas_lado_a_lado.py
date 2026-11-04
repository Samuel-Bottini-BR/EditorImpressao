"""O "Duas lado a lado" da área de trabalho (obra de 26/10/2026, etapa 6).

O QUE O SAMUEL DECIDIU (docs/plano/DECISOES.md)
    D-015 (22/10/2026, a mais recente): o livro aberto como no UPDF aprovado, "Uma página / Duas lado a
    lado" na barra de baixo, e 904 A: "A — Sim, no menu Ver" -> o "Ver lado a lado" da área de trabalho
    fica na barra de baixo e no menu Ver. D-006 (06/10): "eu não quero padrão eu quero como opção um
    botão que eu clique e veja pagina lado a lado" e 202 A: "Pares rolando, um embaixo do outro". D-347
    (`lu-par`, "Está bom"): no par as duas ficam da mesma altura, a 1 sozinha à direita, como num livro.

O QUE FAZ
    É O MESMO folhear do livro aberto (ui/widgets/paginas_rolando.PaginasRolando: os pares, a mesma
    altura no par, a capa sozinha, rolar, só desenhar o que aparece, guardar poucas), com uma troca só:
    as páginas não vêm do PDF como ele está, vêm das PRÉVIAS da área de trabalho (a página como vai
    sair: girada, dividida, endireitada, cortada e com o filtro), pela função `buscar` que a tela dá
    (TelaConferir._previa_do_lado_a_lado: o mesmo GerenciadorPrevias das ferramentas, que desenha em
    segundo plano). Os pares são os do livro que vai sair: só as páginas que vão para o PDF
    (Projeto.paginas_ativas), na ordem dele.

    O tamanho de cada página, antes de a prévia chegar, é uma estimativa (a folha do PDF, girada e
    partida na linha); quando a prévia chega, a página fica com a proporção dela e a arrumação é refeita
    sem a tela pular (a página da vez fica no mesmo lugar).

    A página guardada é reduzida ao tamanho da tela (no_tamanho) antes de ser guardada: pouca memória,
    como no livro aberto (CLAUDE.md §3).

    Clicar numa página faz dela a página da vez (o quadro azul, como no livro aberto).

    ZOOM (etapa 9b-2 da obra, D-570, 27/10/2026, Central `v-zoom-pares`: "Sim, zoom também no lado
    a lado"; D-571, `v-100`: "A página inteira cabendo na tela"): o "– N% +" e o "ajustar à tela" da
    barra de baixo valem aqui também. 100% = o par inteiro cabendo na tela (o "caber a página");
    acima disso as páginas crescem na mesma proporção, a página da vez fica à vista e a roda rola
    (para cima e para baixo; a barra de baixo, para os lados). Ctrl+roda dá zoom (D-568). As
    prévias são aumentadas para o tamanho da tela (no_tamanho); no zoom alto a página fica tão
    nítida quanto a prévia escolhida nas Configurações.

    A FERRAMENTA NO LUGAR DA PÁGINA DA VEZ (D-612, Samuel, 04/11/2026: "1 - ele tem que funcionar com
    paginas lado a lado também"): a tela pode pôr aqui a PEÇA de uma ferramenta (hoje o visualizador
    do Mover; definir_ferramenta). Ela fica por cima da página da vez, exatamente no lugar dela, e
    acompanha a arrumação (zoom, tamanho da janela, proporção que chegou, rolar). O mouse em cima
    dela vai para ela (arrastar, cantos); a outra página do par continua a prévia, e o clique nela
    continua escolhendo a página da vez. Quem tira a peça e a devolve para a casa dela é a tela
    (TelaConferir._acertar_a_ferramenta_no_par).

Seguro mudar: os textos. Arriscado: pedir a prévia aqui no fio da tela de um jeito que espere por ela
(trava a janela); guardar as prévias inteiras (memória).
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, Signal
from PySide6.QtWidgets import QApplication

from ui.widgets.paginas_rolando import CABER_PAGINA, DUAS, MARGEM, PaginasRolando, no_tamanho

# Os mesmos limites do zoom das ferramentas (ui/widgets/visualizador.ZOOM_MIN/MAX)
ZOOM_MIN, ZOOM_MAX = 1.0, 8.0


class PaginasLadoALado(PaginasRolando):
    """As páginas do livro como vão sair, em pares rolando (ver o começo do arquivo)."""

    # a página da vez agora (índice da página no projeto): rolando ou clicando
    pagina_da_vez_mudou = Signal(int)
    # o zoom mudou (pela roda com Ctrl): a barra de baixo mostra o número novo
    zoom_mudou = Signal(float)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.mostrar = DUAS
        self.continuo = True
        self.caber = CABER_PAGINA
        self.indices: list[int] = []          # posição na tela -> índice da página no projeto
        self.zoom = 1.0                       # D-570: 1,0 = o par inteiro cabendo na tela
        self._buscar = None                   # função(indice, da_vez) -> (imagem ou None, chave)
        self._entregues: dict[int, str] = {}  # posição -> chave da prévia que está guardada
        self.ferramenta = None                # D-612: a peça no lugar da página da vez (ou None)
        self._refazer = QTimer(self)
        self._refazer.setSingleShot(True)
        self._refazer.timeout.connect(self._rearrumar)
        # as teclas (Page Down, setas) são da área de trabalho, não do rolar desta peça
        self.setFocusPolicy(Qt.NoFocus)
        self.pagina_mudou.connect(self._posicao_mudou)

    # --- uso --------------------------------------------------------------------

    def definir_fonte(self, buscar) -> None:
        """`buscar(indice, da_vez)` devolve (imagem numpy ou None, chave da prévia).
        None: ainda vem (a tela chama atualizar_imagens quando chegar)."""
        self._buscar = buscar

    def mostrar_paginas(self, indices: list[int], tamanhos: list[tuple[float, float]]) -> bool:
        """As páginas que vão sair (índices no projeto) e o tamanho estimado de
        cada uma (pontos). Só refaz se a lista mudou. Devolve True se mudou."""
        indices = list(indices)
        if indices == self.indices and self.tamanhos:
            return False
        self.indices = indices
        self.tamanhos = list(tamanhos)
        self.caminho = "área de trabalho" if indices else ""
        self.guardadas.clear()
        self._pedidas.clear()
        self._entregues.clear()
        self.atual = min(self.atual, max(0, len(indices) - 1))
        self._arrumar()
        return True

    def posicao_de(self, indice: int) -> int:
        """A posição da página `indice` do projeto; se ela não vai sair (tirada
        do livro), a da próxima que sai (ou a última)."""
        for posicao, i in enumerate(self.indices):
            if i >= indice:
                return posicao
        return max(0, len(self.indices) - 1)

    def ir_para_pagina(self, indice: int) -> None:
        """Mostra a página `indice` do projeto (sem mexer se já é a da vez:
        rolando, a tela não pula para o alto dela)."""
        if not self.indices:
            return
        posicao = self.posicao_de(indice)
        if posicao != self.atual or not self._ret:
            self.ir_para(posicao)

    def indice_da_vez(self) -> int | None:
        if not self.indices:
            return None
        return self.indices[max(0, min(self.atual, len(self.indices) - 1))]

    def atualizar_imagens(self) -> None:
        """Alguma prévia chegou, ou a página mudou: as que estão guardadas com
        uma chave velha saem, e as que estão à vista são pedidas de novo."""
        if self._buscar is not None:
            for posicao in list(self.guardadas):
                if 0 <= posicao < len(self.indices):
                    _img, chave = self._buscar(self.indices[posicao], False, so_olhar=True)
                    if chave != self._entregues.get(posicao):
                        self.guardadas.pop(posicao, None)
                        self._entregues.pop(posicao, None)
        self._pedir_as_visiveis()
        self.folhas.update()

    def limpar(self) -> None:
        self.indices = []
        self._entregues = {}
        super().limpar()

    # --- a ferramenta no lugar da página da vez (D-612) ------------------------------

    def definir_ferramenta(self, peca) -> None:
        """Põe a `peca` (um QWidget: a peça da ferramenta da vez, ver o começo
        do arquivo) por cima da página da vez. Chamar de novo só acerta o
        lugar. Quem a tira é tirar_ferramenta."""
        self.ferramenta = peca
        if peca is None:
            return
        if peca.parentWidget() is not self.folhas:
            peca.setParent(self.folhas)
        self._por_a_ferramenta_no_lugar()

    def tirar_ferramenta(self):
        """Larga a peça, sem a máscara e sem o lugar no par (devolve ela; quem
        chamou a põe de volta na casa dela)."""
        peca, self.ferramenta = self.ferramenta, None
        if peca is not None:
            peca.clearMask()
            if hasattr(peca, "definir_lugar_no_par"):
                peca.definir_lugar_no_par(None)
        return peca

    def _por_a_ferramenta_no_lugar(self) -> None:
        """A peça da ferramenta em cima da página da vez, DO TAMANHO DA PRÉVIA
        (Samuel, 04/11/2026, testando o Mover nos pares: "ela deveria continuar
        o preview das duas do mesmo tamanho"):
          - o Visualizador (Mover, Cortar, Endireitar) cobre o desenho inteiro
            dos pares, sem fundo, e desenha a página no lugar dela
            (definir_lugar_no_par): a área branca do Mover é o lugar da página;
            a parte que passa da beirada e os cantos azuis ficam à vista em
            volta, no espaço entre as páginas;
          - a peça sem esse jeito (o editor de marcar) fica na altura do lugar
            da página (no par as duas têm a mesma altura), no meio dele.
        As OUTRAS páginas ficam por cima (uma máscara as tira da peça): elas
        continuam à vista e o clique nelas continua delas. Sem a página da vez
        arrumada (livro vazio), a peça fica escondida."""
        from PySide6.QtCore import QRect
        from PySide6.QtGui import QRegion

        peca = getattr(self, "ferramenta", None)
        if peca is None:
            return
        ret = next((r for i, r in self._ret if i == self.atual), None)
        if ret is None:
            peca.hide()
            return
        x0, y0 = round(ret.left()), round(ret.top())
        lugar = QRect(x0, y0, max(1, round(ret.right()) - x0), max(1, round(ret.bottom()) - y0))
        if hasattr(peca, "definir_lugar_no_par"):
            geometria = self.folhas.rect()
            peca.setGeometry(geometria)
            peca.definir_lugar_no_par(lugar.translated(-geometria.topLeft()))
        else:
            geometria = QRect(lugar)
            imagem = getattr(peca, "_pixmap", None)
            if imagem is not None and not imagem.isNull() and imagem.height() > 0:
                largura = max(1, round(lugar.height() * imagem.width() / imagem.height()))
                geometria = QRect(lugar.center().x() - largura // 2, lugar.top(), largura, lugar.height())
            peca.setGeometry(geometria)
        regiao = QRegion(peca.rect())
        for indice, outro in self._ret:
            if indice != self.atual:
                regiao = regiao.subtracted(QRegion(outro.toAlignedRect().translated(-geometria.topLeft())))
        # as pegas da ferramenta (cantos azuis, alças) por cima de tudo
        for pega in getattr(peca, "retangulos_das_pegas", lambda: [])():
            regiao = regiao.united(QRegion(pega))
        peca.setMask(regiao)
        peca.show()
        peca.raise_()

    def _arrumar(self) -> None:
        """A arrumação de sempre (PaginasRolando._arrumar) e, depois dela, a
        peça da ferramenta no lugar novo da página da vez (D-612)."""
        super()._arrumar()
        self._por_a_ferramenta_no_lugar()

    def ir_para(self, indice: int) -> None:
        """Como sempre (PaginasRolando.ir_para), e a peça da ferramenta vai
        junto para a página da vez (D-612). Outra página chega escolhida (D-622)."""
        if indice != self.atual:
            self.definir_sem_escolha(False)
        super().ir_para(indice)
        self._por_a_ferramenta_no_lugar()

    # --- o zoom (D-570) --------------------------------------------------------------

    def definir_zoom(self, zoom: float) -> None:
        """Muda o zoom (preso entre ZOOM_MIN e ZOOM_MAX), com a página da vez
        à vista e o par no meio da largura."""
        novo = float(min(max(zoom, ZOOM_MIN), ZOOM_MAX))
        if abs(novo - self.zoom) < 1e-4:
            return
        self.zoom = novo
        atual = self.atual
        self._arrumar()
        self.ir_para(atual)
        barra = self.horizontalScrollBar()
        barra.setValue((barra.maximum() + barra.minimum()) // 2)
        self.zoom_mudou.emit(self.zoom)

    def ajustar_a_tela(self) -> None:
        """100%: o par inteiro cabendo na tela."""
        self.definir_zoom(1.0)

    def _altura_da_linha(self, proporcoes: float, largura: float, altura: float) -> float:
        """A altura da linha do "caber a página" (o par inteiro na tela)
        vezes o zoom (D-570)."""
        # getattr: a arrumação pode rodar ainda dentro do __init__ da classe-mãe
        # (num resize), antes de o zoom existir
        return super()._altura_da_linha(proporcoes, largura, altura) * getattr(self, "zoom", 1.0)

    def zoom_no_ponteiro(self, zoom: float, ponto) -> None:
        """Ctrl+roda (D-568): o zoom vai para onde está o mouse, como nos
        outros lugares do programa (janela do Automático, tela cheia,
        "comparar"): o ponto da página que estava debaixo do ponteiro continua
        debaixo dele (a página mais perto do ponteiro, se ele está no espaço
        entre elas). `ponto`: o ponteiro, na área visível (viewport). Bug de
        31/10/2026 (Samuel: "na area de trabalho o zoom [...] se direciona
        somente para o centro da pagina e não onde o mouse está"); conserto
        de 01/11/2026. Os botões "–", "+" e "ajustar à tela" continuam pelo
        centro (definir_zoom). As barras de rolar não deixam a página sair da
        tela (como na janela do Automático)."""
        novo = float(min(max(zoom, ZOOM_MIN), ZOOM_MAX))
        if abs(novo - self.zoom) < 1e-4:
            return
        no_conteudo = QPointF(self.folhas.mapFrom(self.viewport(), ponto))
        perto = self._pagina_mais_perto(no_conteudo)
        if perto is None:
            self.definir_zoom(novo)
            return
        posicao, ret = perto
        fx = (no_conteudo.x() - ret.left()) / max(1.0, ret.width())
        fy = (no_conteudo.y() - ret.top()) / max(1.0, ret.height())
        self.zoom = novo
        self._arrumar()
        QApplication.sendPostedEvents(self)          # o tamanho novo chega às barras
        ret = next((r for i, r in self._ret if i == posicao), None)
        if ret is not None:
            self.horizontalScrollBar().setValue(int(round(ret.left() + fx * ret.width() - ponto.x())))
            self.verticalScrollBar().setValue(int(round(ret.top() + fy * ret.height() - ponto.y())))
        self._pedir_as_visiveis()
        self.zoom_mudou.emit(self.zoom)

    def _pagina_mais_perto(self, ponto: QPointF):
        """(posição, retângulo) da página arrumada debaixo de `ponto` (no
        conteúdo) ou, se nenhuma, da mais perto dele. None sem páginas."""
        melhor, distancia = None, None
        for posicao, ret in self._ret:
            dx = max(ret.left() - ponto.x(), 0.0, ponto.x() - ret.right())
            dy = max(ret.top() - ponto.y(), 0.0, ponto.y() - ret.bottom())
            d = dx * dx + dy * dy
            if distancia is None or d < distancia:
                melhor, distancia = (posicao, QRectF(ret)), d
        return melhor

    def _largura_do_conteudo(self, largura: float) -> float:
        """Com zoom, o que rola fica pelo menos do tamanho da tela vezes o zoom
        (até o dobro), com o par no meio, como a área de rolar da janela do
        Automático: assim o zoom vai para o mouse também para os lados, mesmo
        quando o par ainda é mais estreito que a tela (01/11/2026, ver
        zoom_no_ponteiro). Com 100%, a largura da tela, como sempre."""
        return largura * min(max(getattr(self, "zoom", 1.0), 1.0), 2.0)

    def wheelEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Ctrl+roda dá zoom (D-568), para onde está o mouse; com zoom, Shift+roda
        anda para os lados; no resto, rola como sempre.

        Shift + roda com zoom: defeito de 01/11/2026 (Samuel: "com shift para os
        lados não funciona ele rola as paginas para pagina, no caso troca de
        pagina"). O rolar padrão do Qt usa o Shift para rolar de página em
        página na barra de pé; aqui, com zoom, ele anda na barra de baixo, o
        mesmo tanto que a roda anda para cima e para baixo (D-568: "com zoom anda
        pela página", Shift para os lados, como na "Uma página"). Sem zoom, como
        sempre (o livro aberto, PaginasRolando.wheelEvent, só anda para os lados se as
        páginas passarem da largura da tela).

        Desde 02/11/2026 (D-600, "o shift tem que funcionar em todas as telas") a conta
        de andar na barra é a peça única ui/widgets/roda_de_lado (a mesma do Automático e
        do livro aberto); o que acontece aqui não mudou."""
        from ui.widgets.roda_de_lado import andar_na_barra, quanto_de_lado

        if evento.modifiers() & Qt.ControlModifier:
            passos = evento.angleDelta().y()
            if passos:
                self.zoom_no_ponteiro(self.zoom * (1.25 if passos > 0 else 1 / 1.25),
                                      evento.position().toPoint())
            evento.accept()
            return
        if self.zoom > 1.0 + 1e-3 and evento.modifiers() & Qt.ShiftModifier:
            de_lado = quanto_de_lado(evento)
            if de_lado:
                andar_na_barra(self.horizontalScrollBar(), de_lado)
            evento.accept()
            return
        super().wheelEvent(evento)

    # --- o desenho das páginas (troca o PDF pelas prévias) ----------------------

    def pedir(self, indice: int, largura: int, altura: int) -> None:
        """A página na posição `indice`, com `largura` x `altura` pixels: vem
        da prévia (na hora, se já está pronta; senão ela é pedida e chega
        depois pelo atualizar_imagens)."""
        if self._buscar is None or not 0 <= indice < len(self.indices):
            return
        img, chave = self._buscar(self.indices[indice], indice == self.atual)
        guardada = self.guardadas.get(indice)
        if (guardada is not None and self._entregues.get(indice) == chave
                and (guardada.width(), guardada.height()) == (largura, altura)):
            return
        if img is None:
            return
        self._entregues[indice] = chave
        self._acertar_a_proporcao(indice, img)
        self._chegou(indice, no_tamanho(img, largura, altura), largura, altura)

    def _acertar_a_proporcao(self, posicao: int, img) -> None:
        """A prévia tem a proporção de verdade da página (cortada, endireitada):
        se a estimativa era outra, a página passa a ter a da prévia e a
        arrumação é refeita logo depois (fora da pintura)."""
        altura, largura = img.shape[:2]
        if not altura or not 0 <= posicao < len(self.tamanhos):
            return
        w, h = self.tamanhos[posicao]
        nova = largura / altura
        if h <= 0 or abs((w / h) - nova) > 0.01 * nova:
            self.tamanhos[posicao] = (h * nova, h)
            self._refazer.start(0)

    def _rearrumar(self) -> None:
        """Refaz a arrumação (a proporção de uma página mudou) com a página da
        vez no mesmo lugar da tela."""
        barra = self.verticalScrollBar()
        antes = next((r.top() for i, r in self._ret if i == self.atual), None)
        distancia = barra.value() - antes if antes is not None else None
        self._arrumar()
        depois = next((r.top() for i, r in self._ret if i == self.atual), None)
        if distancia is not None and depois is not None:
            barra.setValue(max(0, int(depois + distancia)))
        self.folhas.update()

    # --- a página da vez ----------------------------------------------------------

    def _posicao_mudou(self, posicao: int) -> None:
        if 0 <= posicao < len(self.indices):
            self.pagina_da_vez_mudou.emit(self.indices[posicao])

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Clicar numa página faz dela a página da vez (o quadro azul)."""
        if evento.button() == Qt.LeftButton:
            ponto = self.folhas.mapFrom(self.viewport(), evento.position().toPoint())
            for posicao, ret in self._ret:
                if ret.adjusted(-MARGEM / 2, 0, MARGEM / 2, 0).contains(QPointF(ponto)):
                    self.definir_sem_escolha(False, avisar=True)       # D-622
                    if posicao != self.atual:
                        self.atual = posicao
                        self.folhas.update()
                        self.pagina_mudou.emit(posicao)
                        self._passar_o_aperto_a_peca(evento)
                    evento.accept()
                    return
            # D-622: o clique no cinza, fora das páginas, larga a escolha
            if self.desescolher_ao_clicar_fora:
                self.definir_sem_escolha(True, avisar=True)
        super().mousePressEvent(evento)

    # --- D-622: clicar fora larga a escolha ------------------------------------------
    #
    # Samuel, 04/11/2026 (print a-74): "quando eu clicar fora da folha ele
    # desseleciona o que está selecionado, para eu selecionar de novo tenho que
    # clicar de novo na coisa selecionada como no photoshop." Com a tela ligando
    # desescolher_ao_clicar_fora (o Mover), o clique no cinza apaga o quadro azul
    # da página da vez (e a tela apaga os cantos do Mover, escolha_mudou);
    # clicar numa página escolhe de novo. Andar de página escolhe a nova.

    escolha_mudou = Signal(bool)
    desescolher_ao_clicar_fora = False

    def definir_sem_escolha(self, sem: bool, avisar: bool = False) -> None:
        """Apaga (True) ou acende (False) o quadro da página da vez. Com
        `avisar`, conta à tela (escolha_mudou) quando muda."""
        sem = bool(sem)
        if sem == self.sem_escolha:
            return
        self.sem_escolha = sem
        self.folhas.update()
        if avisar:
            self.escolha_mudou.emit(not sem)

    # --- D-612 (a): escolher a outra página do par e já arrastar ---------------------
    #
    # Samuel, 04/11/2026, à pergunta "O mesmo clique na outra página do par já
    # escolhe e arrasta?": "ok". Vale para o Mover, o Cortar e as de marcar (a
    # tela liga arrastar_ao_escolher; no Endireitar não). O aperto na outra
    # página a escolhe (a tela põe a peça da ferramenta em cima dela, na hora,
    # pelo pagina_mudou) e é passado à peça: o arrasto começa no mesmo aperto, e
    # o resto do arrasto (mover, soltar) vai para ela também. Se a imagem da
    # página nova ainda não chegou, a peça não pega o aperto: só escolhe (como
    # antes). Arriscado: passar o aperto quando a peça não está em cima do ponto.

    arrastar_ao_escolher = False
    _peca_no_arrasto = None

    def _passar_o_aperto_a_peca(self, evento) -> None:
        from PySide6.QtCore import QEvent
        from PySide6.QtGui import QMouseEvent

        peca = getattr(self, "ferramenta", None)
        if peca is None or not self.arrastar_ao_escolher or not peca.isVisible():
            return
        ponto = peca.mapFrom(self.viewport(), evento.position().toPoint())
        mascara = peca.mask()
        if not peca.rect().contains(ponto) or (not mascara.isEmpty() and not mascara.contains(ponto)):
            return
        aperto = QMouseEvent(QEvent.MouseButtonPress, QPointF(ponto), evento.globalPosition(),
                             evento.button(), evento.buttons(), evento.modifiers())
        aperto.accept()
        peca.mousePressEvent(aperto)            # direto: o aperto que ela recusa não volta aqui
        if aperto.isAccepted():
            self._peca_no_arrasto = peca

    def _passar_a_peca(self, evento, tipo) -> bool:
        """O resto do arrasto começado na peça (_passar_o_aperto_a_peca)."""
        from PySide6.QtGui import QMouseEvent

        peca = self._peca_no_arrasto
        if peca is None:
            return False
        ponto = peca.mapFrom(self.viewport(), evento.position().toPoint())
        copia = QMouseEvent(tipo, QPointF(ponto), evento.globalPosition(), evento.button(),
                            evento.buttons(), evento.modifiers())
        if tipo == copia.Type.MouseButtonRelease:
            self._peca_no_arrasto = None
            peca.mouseReleaseEvent(copia)
        else:
            peca.mouseMoveEvent(copia)
        evento.accept()
        return True

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        from PySide6.QtCore import QEvent

        if not self._passar_a_peca(evento, QEvent.MouseMove):
            super().mouseMoveEvent(evento)

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        from PySide6.QtCore import QEvent

        if not self._passar_a_peca(evento, QEvent.MouseButtonRelease):
            super().mouseReleaseEvent(evento)
