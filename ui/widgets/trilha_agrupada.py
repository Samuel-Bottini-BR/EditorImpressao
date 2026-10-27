"""A trilha de ferramentas AGRUPADA, como no Photoshop (layout, etapa 2).

Decisões do Samuel que esta peça segue:
  - rodada 8 (302 C, 06/10/2026): "Agrupadas, como no Photoshop", com o
    comentário "mas quando eu passar em cima da agrupada tem que mostrar a
    letra dela de atalho." Ao passar o mouse, o balão diz o nome, a letra e as
    outras ferramentas do mesmo botão, cada uma com a letra;
  - 25/09: estilo Photoshop, sem abas, uma tela só. As abas de antes (Onde
    cortar, Bordas, Endireitar, Marcar, Filtro) viraram ferramentas desta
    trilha: Dividir, Cortar e Endireitar no alto, as de marcar agrupadas no
    meio, Zoom e Mão embaixo.

Os grupos (os mesmos do protótipo da rodada 8): Formas (Retângulo, Oval),
Contornar (Laço, Ponto a ponto), Pegar pela cor (Varinha mágica, Pegar tudo
desta cor). O botão de um grupo mostra a última ferramenta usada dele e tem
um triângulo no canto; segurando o botão (ou clicando com o direito) abre a
lista do grupo. Laço magnético e Seleção rápida, que o protótipo mostrava
apagados ("ainda não existe"), não entram: botão que não faz nada não vai
para o programa.

"Os quatro filtros" (o botão provisório que abria a tela dos quatro filtros
da página, a antiga aba Filtro) SAIU da trilha na etapa 2 da obra de
26/10/2026: o painel "Filtro da página" (R9 403 B, "Filtros numa fila + partes
que abrem e fecham", com a tela cheia dos filtros) faz o mesmo e mais, e as
duas portas com o mesmo desenho confundiam (lista única 5.13). O nome
FERRAMENTA_FILTROS continua existindo por dentro (a tela ainda tem a "aba"
dos cartões, de onde o painel tira as amostras), mas nenhum botão leva a ela.

D-001 (25/09: "Uma única tela com todas as ferramentas"): desde a etapa 2 da
obra a tela mostra SEMPRE todos os botões (definir_disponiveis(None)); o
"disponíveis" continua aqui só para quem quiser esconder um de propósito.

Os ícones são desenhados à mão (nada de emoji em rótulo, regra do projeto) e
pintados com as cores do tema da vez (ui/estilo.py), lidas na hora.

Seguro mudar: a ordem dos grupos, os nomes, os desenhos. Arriscado: tirar um
botão (todo botão que existia continua existindo, só muda de lugar).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QMenu, QToolTip, QWidget

import atalhos
from ui import estilo
from ui.widgets.editor_selecao import (
    FERRAMENTA_AJUSTAR,
    FERRAMENTA_COR,
    FERRAMENTA_ELIPSE,
    FERRAMENTA_LACO,
    FERRAMENTA_MAO,
    FERRAMENTA_PINCEL,
    FERRAMENTA_POLIGONO,
    FERRAMENTA_RETANGULO,
    FERRAMENTA_VARINHA,
    FERRAMENTA_ZOOM,
    NOMES_DAS_FERRAMENTAS,
    tecla_da_ferramenta,
)

# As ferramentas que eram abas. Os nomes dizem o que fazem (o nome da aba
# "Onde cortar" confundia: ela divide a folha na lombada).
FERRAMENTA_DIVIDIR = "dividir"
FERRAMENTA_CORTAR = "cortar"
FERRAMENTA_ENDIREITAR = "endireitar"
FERRAMENTA_FILTROS = "filtros"          # provisório até a etapa 4
# Etapa 5 da obra de 26/10/2026 (D-008, Samuel na sessão 1: "a ferramenta de
# mover não deveria estar vinculada ao corte de bordas, deveriam ser duas
# coisas independentes"; "como é no photoshope, que você arrasta a hora que
# quiser e aumenta a hora que quiser"): mover e redimensionar o conteúdo na
# área branca é uma ferramenta própria, sempre na trilha, logo depois do
# Endireitar. Antes era a caixinha "Mover conteúdo" dentro do Cortar, cinza
# até escolher um tamanho de folha.
FERRAMENTA_MOVER = "mover"
FERRAMENTAS_DA_PAGINA = (FERRAMENTA_DIVIDIR, FERRAMENTA_CORTAR,
                         FERRAMENTA_ENDIREITAR, FERRAMENTA_MOVER, FERRAMENTA_FILTROS)

NOMES = dict(NOMES_DAS_FERRAMENTAS)
NOMES.update({
    FERRAMENTA_DIVIDIR: "Dividir a folha",
    FERRAMENTA_CORTAR: "Cortar as bordas",
    FERRAMENTA_ENDIREITAR: "Endireitar",
    FERRAMENTA_MOVER: "Mover e redimensionar",
    FERRAMENTA_FILTROS: "Os quatro filtros",
})

# O que cada uma faz, numa frase curta (o balão do mouse). Desde a rodada 12
# do layout (702 C, 12/10/2026: "Mostrar só o nome da ferramenta" na linha dos
# menus) este balão é o ÚNICO lugar onde a frase do que fazer aparece; por
# isso as dicas que a barra de opções mostrava (a roda do mouse) vieram
# para cá.
USOS = {
    FERRAMENTA_DIVIDIR: "Arraste a linha azul para mudar onde a folha divide.",
    FERRAMENTA_CORTAR: "Arraste o retângulo para mudar o corte da borda.",
    # Desde o G5 (item 2.2, 07/10/2026) o giro à mão é pela bolinha azul
    # (alça) ou pela linha laranja (linha-guia), no visualizador.
    FERRAMENTA_ENDIREITAR: ("Gire pela bolinha azul, ou desenhe a linha laranja em "
                            "cima de uma linha do texto."),
    FERRAMENTA_MOVER: ("Arraste a página para mover dentro da área branca. Puxe um canto "
                       "para aumentar ou diminuir."),
    FERRAMENTA_FILTROS: "A mesma página nos quatro filtros: clique no que preferir.",
    FERRAMENTA_RETANGULO: "Arraste de um canto ao outro.",
    FERRAMENTA_ELIPSE: "Arraste para desenhar um oval.",
    FERRAMENTA_LACO: "Contorne a área com o botão apertado.",
    FERRAMENTA_POLIGONO: "Clique ponto a ponto. Duplo clique fecha.",
    FERRAMENTA_PINCEL: "Pinte por cima. A roda do mouse muda a espessura.",
    FERRAMENTA_VARINHA: ("Clique numa cor e ela pega a mancha inteira. "
                         "A roda do mouse muda a tolerância."),
    FERRAMENTA_COR: ("Clique numa cor e ela pega tudo daquela cor na página. "
                     "A roda do mouse muda a variação."),
    # item 2.18: mover e mudar o tamanho das areas (controle minimo; o
    # lugar e o desenho do icone sao do agente de layout)
    FERRAMENTA_AJUSTAR: ("Clique numa área para escolher. Arraste para mover; os "
                         "quadradinhos mudam o tamanho."),
    FERRAMENTA_ZOOM: "Clique para aproximar. Com Alt, afasta.",
    FERRAMENTA_MAO: "Arraste para andar pela página aproximada.",
}

# "-" é o traço que separa os blocos.
GRUPOS = (
    (FERRAMENTA_DIVIDIR,), (FERRAMENTA_CORTAR,), (FERRAMENTA_ENDIREITAR,),
    (FERRAMENTA_MOVER,), "-",
    (FERRAMENTA_RETANGULO, FERRAMENTA_ELIPSE), (FERRAMENTA_LACO, FERRAMENTA_POLIGONO),
    (FERRAMENTA_PINCEL,), (FERRAMENTA_VARINHA, FERRAMENTA_COR), (FERRAMENTA_AJUSTAR,), "-",
    (FERRAMENTA_ZOOM,), (FERRAMENTA_MAO,),
)
NOMES_DOS_GRUPOS = {FERRAMENTA_RETANGULO: "Formas", FERRAMENTA_LACO: "Contornar",
                    FERRAMENTA_VARINHA: "Pegar pela cor"}

LARGURA = 44                 # a do protótipo da rodada 8
LADO_DO_BOTAO = (34, 30)
ALTURA_DO_ITEM = 32          # o botão e um respiro de 2 px
ALTURA_MINIMA_DO_ITEM = 26
ALTURA_DO_TRACO = 11
TEMPO_PARA_ABRIR_O_GRUPO_MS = 450


# Obra de 26/10/2026, etapa 3 (pergunta da etapa 2: "Letras para Dividir, Cortar e
# Endireitar?"; o Samuel quer atalhos "como o Photoshop"). Escolha da gerente
# (D-014), anotada no Livro de decisoes: D = Dividir, X = Cortar (o X de
# "recortar", como o Ctrl+X; o C do Photoshop ja e "Pegar tudo desta cor"),
# I = Endireitar (o I da regua de endireitar do Photoshop, e de "inclinação").
# Livres em todo o programa: R O L P B V C A Z E (marcar), M e T (recorte
# espelhado e proporção), 1 a 4 (filtros). Remapeaveis nas Configuracoes
# (atalhos.py, chaves "ferramenta_dividir/cortar/endireitar").
# Etapa 5 da obra (escolha da gerente, D-014; anotada no Livro, D-540): F =
# Mover e redimensionar ("F de folha": põe o conteúdo no lugar da folha). O V
# do Photoshop já é a Varinha mágica aqui, e o M é o "Recorte: espelhado";
# as letras livres eram F G H J K N Q S U W Y.
ATALHOS_DA_PAGINA = {FERRAMENTA_DIVIDIR: "D", FERRAMENTA_CORTAR: "X", FERRAMENTA_ENDIREITAR: "I",
                     FERRAMENTA_MOVER: "F"}
for _ferramenta, _letra in ATALHOS_DA_PAGINA.items():
    atalhos.registrar(f"ferramenta_{_ferramenta}", NOMES[_ferramenta], _letra)


def tecla_de(ferramenta: str) -> str:
    """A letra do atalho de hoje (remapeavel). "Os quatro filtros" nao tem.
    Dividir, Cortar, Endireitar e (desde a etapa 5) Mover: ATALHOS_DA_PAGINA."""
    if ferramenta in ATALHOS_DA_PAGINA:
        return atalhos.tecla_atual(f"ferramenta_{ferramenta}") or ATALHOS_DA_PAGINA[ferramenta]
    if ferramenta in FERRAMENTAS_DA_PAGINA:
        return ""
    return tecla_da_ferramenta(ferramenta)


def ferramenta_da_pagina_da_tecla(tecla: str) -> str | None:
    """Dividir, Cortar ou Endireitar pela letra de hoje, ou None (etapa 3)."""
    for ferramenta in ATALHOS_DA_PAGINA:
        if tecla and tecla_de(ferramenta) == tecla:
            return ferramenta
    return None


def grupo_de(ferramenta: str) -> int:
    """Em qual grupo (índice em GRUPOS) a ferramenta mora, ou -1."""
    for indice, grupo in enumerate(GRUPOS):
        if grupo != "-" and ferramenta in grupo:
            return indice
    return -1


def desenhar_icone(pintor: QPainter, ferramenta: str, x: int, y: int, lado: int) -> None:
    """O ícone de uma ferramenta, desenhado à mão no quadrado (x, y, lado).
    A caneta já vem escolhida por quem chama."""
    meio = QPoint(x + lado // 2, y + lado // 2)
    if ferramenta == FERRAMENTA_DIVIDIR:
        pintor.drawRect(QRect(x + 1, y + 3, lado - 2, lado - 6))
        pintor.drawLine(meio.x(), y + 3, meio.x(), y + lado - 3)
    elif ferramenta == FERRAMENTA_CORTAR:
        a, b = x + lado // 4, y + lado // 4
        pintor.drawLine(a, y, a, y + lado - lado // 4)
        pintor.drawLine(a, y + lado - lado // 4, x + lado, y + lado - lado // 4)
        pintor.drawLine(x, b, x + lado - lado // 4, b)
        pintor.drawLine(x + lado - lado // 4, b, x + lado - lado // 4, y + lado)
    elif ferramenta == FERRAMENTA_ENDIREITAR:
        caminho = QPainterPath()
        caminho.moveTo(x + lado * 0.27, y + lado * 0.80)
        caminho.lineTo(x + lado * 0.35, y + lado * 0.20)
        caminho.lineTo(x + lado * 0.77, y + lado * 0.27)
        caminho.lineTo(x + lado * 0.69, y + lado * 0.87)
        caminho.closeSubpath()
        pintor.drawPath(caminho)
    elif ferramenta == FERRAMENTA_MOVER:
        # etapa 5: a cruz de quatro setas do "mover" (como no Photoshop)
        pintor.drawLine(meio.x(), y + 1, meio.x(), y + lado - 1)
        pintor.drawLine(x + 1, meio.y(), x + lado - 1, meio.y())
        ponta = max(3, lado // 6)
        for (px, py), (ax, ay), (bx, by) in (
                ((meio.x(), y + 1), (-ponta, ponta), (ponta, ponta)),
                ((meio.x(), y + lado - 1), (-ponta, -ponta), (ponta, -ponta)),
                ((x + 1, meio.y()), (ponta, -ponta), (ponta, ponta)),
                ((x + lado - 1, meio.y()), (-ponta, -ponta), (-ponta, ponta))):
            pintor.drawLine(px, py, px + ax, py + ay)
            pintor.drawLine(px, py, px + bx, py + by)
    elif ferramenta == FERRAMENTA_FILTROS:
        raio = lado // 2 - 1
        pintor.drawEllipse(meio, raio, raio)
        metade = QPainterPath()
        metade.moveTo(meio.x(), meio.y() - raio)
        metade.arcTo(QRect(meio.x() - raio, meio.y() - raio, 2 * raio, 2 * raio), 90, -180)
        metade.closeSubpath()
        pintor.fillPath(metade, pintor.pen().color())
    elif ferramenta == FERRAMENTA_RETANGULO:
        caneta = QPen(pintor.pen())
        caneta.setStyle(Qt.DashLine)
        pintor.save()
        pintor.setPen(caneta)
        pintor.drawRect(QRect(x + 1, y + 4, lado - 2, lado - 8))
        pintor.restore()
    elif ferramenta == FERRAMENTA_ELIPSE:
        caneta = QPen(pintor.pen())
        caneta.setStyle(Qt.DashLine)
        pintor.save()
        pintor.setPen(caneta)
        pintor.drawEllipse(QRect(x + 1, y + 4, lado - 2, lado - 8))
        pintor.restore()
    elif ferramenta == FERRAMENTA_LACO:
        pintor.drawEllipse(QRect(x + 1, y + 2, lado - 2, lado - 9))
        pintor.drawLine(x + 5, y + lado - 8, x + 3, y + lado - 1)
    elif ferramenta == FERRAMENTA_POLIGONO:
        caminho = QPainterPath()
        caminho.moveTo(x + lado * 0.2, y + lado * 0.75)
        caminho.lineTo(x + lado * 0.33, y + lado * 0.25)
        caminho.lineTo(x + lado * 0.71, y + lado * 0.33)
        caminho.lineTo(x + lado * 0.79, y + lado * 0.71)
        caminho.closeSubpath()
        pintor.drawPath(caminho)
    elif ferramenta == FERRAMENTA_PINCEL:
        pintor.drawLine(x + 3, y + lado - 3, x + lado - 5, y + 4)
        pintor.drawLine(x + 6, y + lado - 1, x + lado - 2, y + 7)
        pintor.drawLine(x + 3, y + lado - 3, x + 6, y + lado - 1)
    elif ferramenta == FERRAMENTA_VARINHA:
        pintor.drawLine(x + 2, y + lado - 2, x + lado - 7, y + 7)
        for dx, dy in ((0, -5), (5, 0), (4, -4)):
            pintor.drawLine(x + lado - 5 + dx, y + 5 + dy, x + lado - 3 + dx, y + 7 + dy)
    elif ferramenta == FERRAMENTA_COR:
        pintor.drawLine(x + 3, y + lado - 3, x + lado - 9, y + 8)
        pintor.save()
        pintor.setBrush(QColor(estilo.cor("azul")))
        pintor.drawEllipse(QPoint(x + lado - 6, y + 6), 4, 4)
        pintor.restore()
    elif ferramenta == FERRAMENTA_AJUSTAR:
        # item 2.18: uma caixa tracejada com quadradinhos nos cantos
        pintor.save()
        caneta = pintor.pen()
        caneta.setStyle(Qt.DashLine)
        pintor.setPen(caneta)
        pintor.drawRect(QRect(x + 4, y + 4, lado - 8, lado - 8))
        pintor.restore()
        for cx, cy in ((x + 4, y + 4), (x + lado - 4, y + 4), (x + 4, y + lado - 4),
                       (x + lado - 4, y + lado - 4)):
            pintor.drawRect(QRect(cx - 2, cy - 2, 4, 4))
    elif ferramenta == FERRAMENTA_ZOOM:
        raio = lado // 2 - 4
        pintor.drawEllipse(QPoint(meio.x() - 2, meio.y() - 2), raio, raio)
        pintor.drawLine(meio.x() + raio - 3, meio.y() + raio - 3, x + lado - 1, y + lado - 1)
    elif ferramenta == FERRAMENTA_MAO:
        caminho = QPainterPath()
        caminho.moveTo(x + lado * 0.25, y + lado * 0.85)
        caminho.lineTo(x + lado * 0.25, y + lado * 0.40)
        caminho.lineTo(x + lado * 0.40, y + lado * 0.40)
        caminho.lineTo(x + lado * 0.40, y + lado * 0.15)
        caminho.lineTo(x + lado * 0.55, y + lado * 0.15)
        caminho.lineTo(x + lado * 0.55, y + lado * 0.38)
        caminho.lineTo(x + lado * 0.70, y + lado * 0.38)
        caminho.lineTo(x + lado * 0.70, y + lado * 0.25)
        caminho.lineTo(x + lado * 0.85, y + lado * 0.25)
        caminho.lineTo(x + lado * 0.85, y + lado * 0.85)
        pintor.drawPath(caminho)


def icone(ferramenta: str, lado: int = 18) -> QIcon:
    """O ícone como QIcon (para a lista do grupo), na cor do texto do tema."""
    escala = 3
    imagem = QPixmap(lado * escala, lado * escala)
    imagem.fill(Qt.transparent)
    pintor = QPainter(imagem)
    pintor.setRenderHint(QPainter.Antialiasing)
    pintor.scale(escala, escala)
    pintor.setPen(QPen(QColor(estilo.cor("texto")), 1.4))
    desenhar_icone(pintor, ferramenta, 1, 1, lado - 2)
    pintor.end()
    imagem.setDevicePixelRatio(escala)
    return QIcon(imagem)


class TrilhaAgrupada(QWidget):
    """A coluna de ferramentas à esquerda da página. Só avisa quem foi
    escolhida (sinal `escolhida`); quem troca de modo é a tela."""

    escolhida = Signal(str)
    # a ferramenta marcada mudou, por clique ou por fora (o menu Ferramentas
    # da janela acompanha; etapa 2 da obra). Leva "" quando nenhuma.
    ferramenta_mudou = Signal(str)

    def __init__(self, parent=None) -> None:
        """Começa com o Retângulo à vista no grupo Formas e tudo disponível."""
        super().__init__(parent)
        self.setFixedWidth(LARGURA)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover, True)
        self.ferramenta: str | None = None
        # a ferramenta à vista em cada grupo (a última usada dele)
        self._a_vista = {i: g[0] for i, g in enumerate(GRUPOS) if g != "-"}
        self._disponiveis: set[str] | None = None     # None = todas
        self._sob_o_mouse: int | None = None
        self._apertado: int | None = None
        self._abriu_o_grupo = False
        self._relogio = QTimer(self)
        self._relogio.setSingleShot(True)
        self._relogio.setInterval(TEMPO_PARA_ABRIR_O_GRUPO_MS)
        self._relogio.timeout.connect(self._segurou)
        self.menu_do_grupo: QMenu | None = None      # guardado para os testes

    # --- estado -----------------------------------------------------------

    def definir_disponiveis(self, ferramentas) -> None:
        """Quais ferramentas valem neste livro (as de uma etapa desligada na
        tela "O que fazer" somem da trilha). None = todas."""
        self._disponiveis = None if ferramentas is None else set(ferramentas)
        for indice, grupo in enumerate(GRUPOS):
            if grupo == "-":
                continue
            if self._a_vista[indice] not in self._ferramentas_vivas(grupo) and self._ferramentas_vivas(grupo):
                self._a_vista[indice] = self._ferramentas_vivas(grupo)[0]
        self.update()

    def disponivel(self, ferramenta: str) -> bool:
        """A ferramenta aparece na trilha deste livro?"""
        return self._disponiveis is None or ferramenta in self._disponiveis

    def _ferramentas_vivas(self, grupo) -> list[str]:
        return [f for f in grupo if self.disponivel(f)]

    def definir_ferramenta(self, ferramenta: str | None) -> None:
        """Marca a ferramenta escolhida (por fora: tecla, menu, troca de modo)
        e põe ela à vista no grupo dela. Não avisa a tela (não emite
        `escolhida`); só `ferramenta_mudou`, para a marca do menu acompanhar."""
        indice = grupo_de(ferramenta) if ferramenta else -1
        if indice >= 0:
            self._a_vista[indice] = ferramenta
        mudou = ferramenta != self.ferramenta
        self.ferramenta = ferramenta
        self.update()
        if mudou:
            self.ferramenta_mudou.emit(ferramenta or "")

    def a_vista(self, indice: int) -> str:
        """A ferramenta que o botão do grupo mostra agora."""
        return self._a_vista[indice]

    # --- geometria --------------------------------------------------------

    def _blocos(self) -> list[tuple[str, int]]:
        """O que aparece, em ordem: ("grupo", índice) ou ("traco", -1), sem
        grupo vazio e sem traço dobrado, no começo ou no fim."""
        saida: list[tuple[str, int]] = []
        for indice, grupo in enumerate(GRUPOS):
            if grupo == "-":
                if saida and saida[-1][0] != "traco":
                    saida.append(("traco", -1))
            elif self._ferramentas_vivas(grupo):
                saida.append(("grupo", indice))
        while saida and saida[-1][0] == "traco":
            saida.pop()
        return saida

    def _altura_do_item(self) -> int:
        """Quanto cabe por botão: aperta até ALTURA_MINIMA_DO_ITEM em janela baixa."""
        blocos = self._blocos()
        grupos = sum(1 for b in blocos if b[0] == "grupo")
        tracos = len(blocos) - grupos
        util = self.height() - 14 - tracos * ALTURA_DO_TRACO
        cabe = util // grupos if grupos else ALTURA_DO_ITEM
        return int(max(ALTURA_MINIMA_DO_ITEM, min(ALTURA_DO_ITEM, cabe)))

    def retangulos(self) -> dict[int, QRect]:
        """O retângulo de cada botão de grupo à vista (para pintar e clicar)."""
        altura = self._altura_do_item()
        lado_x, lado_y = LADO_DO_BOTAO[0], min(LADO_DO_BOTAO[1], altura - 2)
        y = 7
        saida: dict[int, QRect] = {}
        for tipo, indice in self._blocos():
            if tipo == "traco":
                y += ALTURA_DO_TRACO
                continue
            saida[indice] = QRect((LARGURA - lado_x) // 2, y, lado_x, lado_y)
            y += altura
        return saida

    def _grupo_em(self, ponto: QPoint) -> int | None:
        for indice, ret in self.retangulos().items():
            if ret.adjusted(-4, -1, 4, 1).contains(ponto):
                return indice
        return None

    def sizeHint(self) -> QSize:  # noqa: N802 - nome do Qt
        return QSize(LARGURA, 400)

    # --- desenho ----------------------------------------------------------

    def paintEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Fundo, risco da direita, os traços entre blocos e cada botão (azul
        o escolhido, com o ícone branco; triângulo no canto dos grupos)."""
        pintor = QPainter(self)
        pintor.setRenderHint(QPainter.Antialiasing)
        pintor.fillRect(self.rect(), QColor(estilo.cor("bar")))
        pintor.setPen(QPen(QColor(estilo.cor("linha")), 1))
        pintor.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        retangulos = self.retangulos()
        y_anterior = None
        for tipo, indice in self._blocos():
            if tipo == "traco":
                if y_anterior is not None:
                    pintor.setPen(QPen(QColor(estilo.cor("sep")), 1))
                    meio = y_anterior + (ALTURA_DO_TRACO + self._altura_do_item()) // 2 - 1
                    pintor.drawLine(10, meio, LARGURA - 10, meio)
                continue
            ret = retangulos[indice]
            y_anterior = ret.top()
            self._desenhar_botao(pintor, indice, ret)

    def _desenhar_botao(self, pintor: QPainter, indice: int, ret: QRect) -> None:
        grupo = GRUPOS[indice]
        escolhido = self.ferramenta in grupo
        if escolhido:
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(estilo.cor("azul")))
            pintor.drawRoundedRect(ret, 6, 6)
        elif indice == self._sob_o_mouse:
            pintor.setPen(Qt.NoPen)
            pintor.setBrush(QColor(estilo.cor("botao_h")))
            pintor.drawRoundedRect(ret, 6, 6)
        cor = QColor("#FFFFFF" if escolhido else estilo.cor("icone"))
        lado = min(18, ret.height() - 6)
        pintor.setBrush(Qt.NoBrush)
        pintor.setPen(QPen(cor, 1.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        desenhar_icone(pintor, self._a_vista[indice],
                       ret.center().x() - lado // 2, ret.center().y() - lado // 2, lado)
        if len(self._ferramentas_vivas(grupo)) > 1:
            triangulo = QPainterPath()
            triangulo.moveTo(ret.right() - 2, ret.bottom() - 7)
            triangulo.lineTo(ret.right() - 2, ret.bottom() - 2)
            triangulo.lineTo(ret.right() - 7, ret.bottom() - 2)
            triangulo.closeSubpath()
            pintor.fillPath(triangulo, cor)

    # --- interação --------------------------------------------------------

    def mousePressEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Botão esquerdo: escolhe ao soltar; segurando, abre o grupo.
        Botão direito: abre o grupo na hora."""
        indice = self._grupo_em(evento.position().toPoint())
        if indice is None:
            return
        if evento.button() == Qt.RightButton:
            self.abrir_o_grupo(indice)
            return
        if evento.button() == Qt.LeftButton:
            self._apertado = indice
            self._abriu_o_grupo = False
            if len(self._ferramentas_vivas(GRUPOS[indice])) > 1:
                self._relogio.start()

    def mouseReleaseEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        """Soltou sem segurar: escolhe a ferramenta à vista do grupo."""
        self._relogio.stop()
        indice, self._apertado = self._apertado, None
        if evento.button() != Qt.LeftButton or indice is None or self._abriu_o_grupo:
            return
        if self._grupo_em(evento.position().toPoint()) == indice:
            self.escolher(self._a_vista[indice])

    def _segurou(self) -> None:
        if self._apertado is not None:
            self._abriu_o_grupo = True
            self.abrir_o_grupo(self._apertado)

    def escolher(self, ferramenta: str) -> None:
        """Escolhe a ferramenta (como um clique) e avisa a tela."""
        self.definir_ferramenta(ferramenta)
        self.escolhida.emit(ferramenta)

    def abrir_o_grupo(self, indice: int) -> None:
        """A lista do grupo, ao lado do botão: ícone, nome e a letra de cada
        ferramenta (a letra fica na coluna da direita do menu)."""
        grupo = self._ferramentas_vivas(GRUPOS[indice])
        if len(grupo) < 2:
            return
        menu = QMenu(self)
        menu.setToolTipsVisible(True)
        titulo = menu.addAction(f"{NOMES_DOS_GRUPOS.get(GRUPOS[indice][0], '')}"
                                " · segure o botão ou clique com o direito")
        titulo.setEnabled(False)
        menu.addSeparator()
        for ferramenta in grupo:
            letra = tecla_de(ferramenta)
            acao = QAction(icone(ferramenta), NOMES[ferramenta] + (f"\t{letra}" if letra else ""), menu)
            acao.setCheckable(True)
            acao.setChecked(ferramenta == self.ferramenta)
            acao.setToolTip(USOS.get(ferramenta, ""))
            acao.triggered.connect(lambda _marcado=False, f=ferramenta: self.escolher(f))
            menu.addAction(acao)
        self.menu_do_grupo = menu
        ret = self.retangulos()[indice]
        menu.popup(self.mapToGlobal(QPoint(ret.right() + 6, ret.top() - 4)))

    def texto_da_dica(self, indice: int) -> str:
        """O balão do botão: nome e letra da ferramenta à vista, o que ela faz
        e, nos grupos, as outras do mesmo botão com a letra de cada uma."""
        ferramenta = self._a_vista[indice]
        letra = tecla_de(ferramenta)
        texto = f"<b>{NOMES[ferramenta]}</b>" + (f"&nbsp;&nbsp;<b>[{letra}]</b>" if letra else "")
        texto += f"<br>{USOS.get(ferramenta, '')}"
        outras = [f for f in self._ferramentas_vivas(GRUPOS[indice]) if f != ferramenta]
        if outras:
            nomes = " &nbsp;·&nbsp; ".join(
                NOMES[f] + (f" [{tecla_de(f)}]" if tecla_de(f) else "") for f in outras)
            texto += (f"<br>No mesmo botão: {nomes}"
                      "<br><i>segure o botão ou clique com o direito para trocar</i>")
        return texto

    def event(self, evento) -> bool:  # noqa: D401 - nome do Qt
        """O balão do mouse com a letra do atalho (pedido do Samuel na rodada 8)."""
        if evento.type() == QEvent.ToolTip:
            indice = self._grupo_em(evento.pos())
            if indice is None:
                QToolTip.hideText()
            else:
                QToolTip.showText(evento.globalPos(), self.texto_da_dica(indice), self)
            return True
        return super().event(evento)

    def mouseMoveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        sob = self._grupo_em(evento.position().toPoint())
        if sob != self._sob_o_mouse:
            self._sob_o_mouse = sob
            self.update()

    def leaveEvent(self, evento) -> None:  # noqa: N802 - nome do Qt
        self._sob_o_mouse = None
        self._relogio.stop()
        self.update()
