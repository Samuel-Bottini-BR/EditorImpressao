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

Seguro mudar: os textos. Arriscado: pedir a prévia aqui no fio da tela de um jeito que espere por ela
(trava a janela); guardar as prévias inteiras (memória).
"""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, QTimer, Signal

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

    def wheelEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Ctrl+roda dá zoom (D-568); sem Ctrl, rola como sempre."""
        if evento.modifiers() & Qt.ControlModifier:
            passos = evento.angleDelta().y()
            if passos:
                self.definir_zoom(self.zoom * (1.25 if passos > 0 else 1 / 1.25))
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
                    if posicao != self.atual:
                        self.atual = posicao
                        self.folhas.update()
                        self.pagina_mudou.emit(posicao)
                    evento.accept()
                    return
        super().mousePressEvent(evento)
