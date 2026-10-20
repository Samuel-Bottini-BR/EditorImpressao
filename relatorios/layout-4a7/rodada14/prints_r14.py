"""Prints da janela DE VERDADE (ramo fase-1 + este ramo) para a rodada 14 de perguntas do layout.

Abre o programa de verdade numa CÓPIA do Boécio (montagem de prints_layout.py: dados e projetos em
saida_teste/, janela fora da tela, sem roubar o foco, 1280 x 657). Cada foto é a janela renderizada
em alta resolução (ESC vezes) - assim o pedaço ampliado sai nítido - e as peças que o Qt abre em
janela própria (menu, lista aberta) são renderizadas e coladas no lugar onde aparecem.

Onde uma opção ainda não existe no programa, a foto é do programa com a peça trocada AQUI, no
roteiro (o texto de um botão, um item de menu a mais), nunca no código do programa. As duas telas
que ainda não existem (Todas as páginas e Configurações em partes) são montadas aqui com as peças e
as cores do programa; a pergunta diz isso.

Uso: python prints_r14.py <pasta_de_saida>
(arquivo descartável do agente de layout, dentro de saida_teste/, que o git ignora)."""
import os
import sys
from pathlib import Path

# A janela inteira desenhada em 2 x a escala da tela (125% neste PC = 2,5 pontos por ponto): o
# ampliado sai nítido e com o desenho de verdade do Qt (o render() para QImage trocava as cores da
# página: o vermelho e o azul saíam invertidos).
sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_layout import LIVRO, abrir_o_livro, app, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, QRect, QRectF, QSize, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap  # noqa: E402
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QFrame, QGridLayout,  # noqa: E402
                               QHBoxLayout, QLabel, QListWidget, QMenu, QPushButton,
                               QRadioButton, QScrollArea, QVBoxLayout, QWidget)

ESC = 2.4               # quantas vezes a foto é renderizada (o ampliado sai daqui, nítido)
AMARELO = QColor("#F5D90A")
SAIDA: Path = Path(".")


# ---------------------------------------------------------------------------
# a foto
# ---------------------------------------------------------------------------

def render_alto(widget, escala: float = ESC) -> QImage:
    """O widget (com os filhos) desenhado em `escala` vezes, num QPixmap (desenhar direto num
    QImage trocava o vermelho e o azul da página)."""
    pix = QPixmap(round(widget.width() * escala), round(widget.height() * escala))
    pix.setDevicePixelRatio(escala)
    pix.fill(Qt.transparent)
    widget.render(pix)
    img = pix.toImage()
    img.setDevicePixelRatio(1)
    return img


class Cena:
    """A janela em alta resolução, com as peças soltas coladas por cima."""

    def __init__(self, janela) -> None:
        self.janela = janela
        self.img = render_alto(janela)

    def colar(self, peca, onde: QPoint) -> None:
        """Cola a peça solta (menu, lista aberta) com o canto em `onde` (pontos da janela)."""
        foto = render_alto(peca)
        x = min(max(0, round(onde.x() * ESC)), self.img.width() - foto.width())
        y = min(max(0, round(onde.y() * ESC)), self.img.height() - foto.height())
        p = QPainter(self.img)
        p.drawImage(QPoint(x, y), foto)
        # sombra fininha, para a peça solta não se misturar ao fundo
        p.setPen(QPen(QColor(0, 0, 0, 120), 2))
        p.drawRect(QRect(x, y, foto.width() - 1, foto.height() - 1))
        p.end()

    def inteira(self, nome: str, contornos: list[QRect] = ()) -> None:
        """Grava a tela inteira (1600 x 821, o tamanho de um print deste PC a 125%), com o contorno
        amarelo tracejado em volta do que muda."""
        img = self.img.copy()
        if contornos:
            p = QPainter(img)
            p.setRenderHint(QPainter.Antialiasing)
            caneta = QPen(AMARELO, 3.2 * ESC / 1.25 * 0.6, Qt.DashLine)
            p.setPen(caneta)
            for r in contornos:
                p.drawRoundedRect(QRectF(r.x() * ESC - 4 * ESC, r.y() * ESC - 4 * ESC,
                                         r.width() * ESC + 8 * ESC, r.height() * ESC + 8 * ESC), 6 * ESC, 6 * ESC)
            p.end()
        pequena = img.scaled(round(self.janela.width() * 1.25), round(self.janela.height() * 1.25),
                             Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        pequena.save(str(SAIDA / f"{nome}.png"))
        print(f"  {nome}.png  (tela inteira)", flush=True)

    def ampliado(self, nome: str, ret: QRect, titulo: str) -> None:
        """Grava só o pedaço `ret` (pontos da janela), em ESC vezes, com o título em cima."""
        recorte = self.img.copy(QRect(round(ret.x() * ESC), round(ret.y() * ESC),
                                      round(ret.width() * ESC), round(ret.height() * ESC)))
        com_titulo(recorte, titulo).save(str(SAIDA / f"{nome}.png"))
        print(f"  {nome}.png  (ampliado: {titulo})", flush=True)


def com_titulo(img: QImage, titulo: str) -> QImage:
    """Põe uma faixa escura com o título em cima da imagem (como nos ampliados da rodada 13)."""
    from PySide6.QtGui import QFontMetrics
    fonte = QFont("Segoe UI")
    fonte.setPixelSize(30)
    fonte.setBold(True)
    caixa = QFontMetrics(fonte).boundingRect(QRect(0, 0, img.width() - 44, 2000),
                                             Qt.TextWordWrap | Qt.AlignLeft, titulo)
    altura = max(64, caixa.height() + 26)
    final = QImage(img.width(), img.height() + altura, QImage.Format_ARGB32)
    final.fill(QColor("#151515"))
    p = QPainter(final)
    p.setRenderHint(QPainter.TextAntialiasing)
    p.setFont(fonte)
    p.setPen(QColor("#FFFFFF"))
    p.drawText(QRect(22, 0, img.width() - 44, altura), Qt.AlignVCenter | Qt.AlignLeft | Qt.TextWordWrap, titulo)
    p.drawImage(QPoint(0, altura), img)
    p.end()
    return final


def no_janela(widget, janela) -> QRect:
    """O retângulo do widget, em pontos da janela."""
    return QRect(widget.mapTo(janela, QPoint(0, 0)), widget.size())


def juntar(r1: QRect, r2: QRect) -> QRect:
    return r1.united(r2)


def com_folga(r: QRect, folga: int, janela) -> QRect:
    """O retângulo com `folga` pontos a mais em volta, sem sair da janela."""
    return r.adjusted(-folga, -folga, folga, folga).intersected(QRect(0, 0, janela.width(), janela.height()))


def botao_com_texto(widget, texto: str):
    for b in widget.findChildren(QAbstractButton):
        if b.text() == texto:
            return b
    raise LookupError(texto)


def menu_do_titulo(janela, titulo: str) -> QMenu:
    return janela.menu.menus[titulo]


def abrir_menu(janela, menu: QMenu) -> QPoint:
    """Abre o menu fora da tela (para ele se montar) e devolve onde ele apareceria na janela:
    logo embaixo do título dele na barra de menus."""
    barra = janela.menu
    geo = barra.actionGeometry(menu.menuAction())
    onde = barra.mapTo(janela, geo.bottomLeft())
    menu.popup(QPoint(-31000, -31000))
    esperar(0.5)
    return onde


# ---------------------------------------------------------------------------
# as perguntas
# ---------------------------------------------------------------------------

def base(janela, tela) -> None:
    """A tela de trabalho de hoje, para o exemplo de cada pergunta."""
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(4)
    Cena(janela).inteira("22-rodada14-hoje-tela-de-trabalho")


def q_mesmo_da_pagina(janela, tela) -> None:
    """905: o nome "o mesmo da página" no "só neste pedaço" do painel Filtro."""
    print("\n905 o mesmo da página")
    tela.trilha.escolher("cortar")
    tela.paineis.abrir("filtro")
    esperar(3)
    painel = tela.paineis.filtro_da_pagina
    botao = botao_com_texto(painel, "o mesmo da página")
    rotulo = next(l for l in painel.findChildren(QLabel) if l.text() == "só neste pedaço")
    pedaco = com_folga(juntar(no_janela(rotulo, janela),
                              no_janela(botao_com_texto(painel, "Mágico pro"), janela)), 10, janela)
    pedaco.setTop(pedaco.top() - 34)
    for letra, texto, titulo in (("hoje", "o mesmo da página", "Hoje: “o mesmo da página”"),
                                 ("a", "o mesmo da página", "A: fica “o mesmo da página”"),
                                 ("b", "igual ao resto da página", "B: “igual ao resto da página”"),
                                 ("c", "nenhum: fica o filtro da página", "C: “nenhum: fica o filtro da página”")):
        botao.setText(texto)
        esperar(0.5)
        cena = Cena(janela)
        cena.ampliado(f"22-rodada14-pedaco-{letra}-ampliado", pedaco, titulo)
        if letra != "hoje":
            cena.inteira(f"22-rodada14-pedaco-{letra}", [no_janela(botao, janela)])
        else:
            cena.inteira("22-rodada14-pedaco-hoje", [pedaco])
    botao.setText("o mesmo da página")
    tela.paineis.fechar()


def q_aviso_marcar(janela, tela) -> None:
    """906: a frase do aviso "Desenho ou escrita?"."""
    print("\n906 aviso Desenho ou escrita")
    from dataclasses import replace

    from core import analise
    projeto = janela.projeto
    i = tela.indice_pagina
    original = analise.ALERTAS[analise.DESENHO_OU_ESCRITA]
    projeto.paginas[i].alertas = [analise.DESENHO_OU_ESCRITA]
    projeto.paginas[i].revisada = False
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    frases = {
        "hoje": original.mensagem,
        "a": "Não tenho certeza se esta página é desenho ou escrita. Se for escrita, marque a área "
             "com uma ferramenta de marcar e escolha “letra e traço”.",
        "b": "Não tenho certeza se esta página é desenho ou escrita. Se for escrita, marque como "
             "“letra e traço”.",
        "c": "Não tenho certeza se esta página é desenho ou escrita. Confira: se for escrita, "
             "marque a área e escolha “letra e traço” no painel Propriedades.",
    }
    titulos = {"hoje": "Hoje (a aba Marcar não existe mais)", "a": "A: diz o caminho",
               "b": "B: curta", "c": "C: diz onde fica o “letra e traço”"}
    for letra, frase in frases.items():
        analise.ALERTAS[analise.DESENHO_OU_ESCRITA] = replace(original, mensagem=frase)
        tela.ir_para_pagina(i)
        esperar(3)
        print("     faixa:", repr(tela.texto_faixa.text()))
        cena = Cena(janela)
        faixa = no_janela(tela.faixa, janela)
        cena.ampliado(f"22-rodada14-aviso-{letra}-ampliado", com_folga(faixa, 6, janela), titulos[letra])
        cena.inteira(f"22-rodada14-aviso-{letra}", [faixa])
    analise.ALERTAS[analise.DESENHO_OU_ESCRITA] = original


def q_dividir_palavra(janela, tela) -> None:
    """907: a lista "jeito:" do Dividir ("o do programa / o do ScanTailor")."""
    print("\n907 palavra do Dividir")
    tela.trilha.escolher("dividir")
    tela.paineis.abrir("props")
    esperar(4)
    combo = tela.combo_jeito_da_folha
    print("     lista habilitada:", combo.isEnabled(), [combo.itemText(k) for k in range(combo.count())])
    originais = [combo.itemText(k) for k in range(combo.count())]
    # o Boécio não tem folha dupla: a lista fica apagada; acesa só para a foto ficar legível
    combo.setEnabled(True)
    tela.rotulo_jeito_da_folha.setEnabled(True)
    endireitar_na_lista = None
    for letra, troca, titulo in (("hoje", None, "Hoje: “o do programa”"),
                                 ("a", None, "A: fica “o do programa”"),
                                 ("b", "o do Editor", "B: “o do Editor”, como na conta do Endireitar")):
        for k, texto in enumerate(originais):
            combo.setItemText(k, troca if (troca and "programa" in texto) else texto)
        esperar(0.3)
        combo.showPopup()
        esperar(0.8)
        caixa = combo.view().window()
        onde = combo.mapTo(janela, QPoint(0, combo.height()))
        cena = Cena(janela)
        cena.colar(caixa, onde)
        ret = com_folga(juntar(no_janela(tela.rotulo_jeito_da_folha, janela),
                               QRect(onde, caixa.size())), 12, janela)
        ret.setTop(no_janela(tela.rotulo_jeito_da_folha, janela).top() - 40)
        cena.ampliado(f"22-rodada14-dividir-{letra}-ampliado", ret, titulo)
        cena.inteira(f"22-rodada14-dividir-{letra}", [juntar(no_janela(combo, janela), QRect(onde, caixa.size()))])
        combo.hidePopup()
        esperar(0.4)
    for k, texto in enumerate(originais):
        combo.setItemText(k, texto)
    # o Endireitar, para comparar (a conta já diz "a do Editor")
    tela.trilha.escolher("endireitar")
    esperar(4)
    combo2 = tela.combo_conta_do_endireitar
    combo2.showPopup()
    esperar(0.8)
    caixa = combo2.view().window()
    onde = combo2.mapTo(janela, QPoint(0, combo2.height()))
    cena = Cena(janela)
    cena.colar(caixa, onde)
    ret = com_folga(juntar(no_janela(tela.rotulo_conta_do_endireitar, janela),
                           QRect(onde, caixa.size())), 12, janela)
    cena.ampliado("22-rodada14-dividir-endireitar-ja-diz-editor-ampliado", ret,
                  "Já decidido no Endireitar: “a do Editor”")
    combo2.hidePopup()
    esperar(0.4)
    del endireitar_na_lista


def q_endireitar_a_mao(janela, tela) -> None:
    """908: a conta do Endireitar quando o ângulo foi posto à mão."""
    print("\n908 conta com o ângulo à mão")
    tela.trilha.escolher("endireitar")
    tela.paineis.abrir("props")
    esperar(4)
    rolagem = tela.paineis.propriedades.rolagem.verticalScrollBar()
    rolagem.setValue(rolagem.maximum())
    esperar(0.5)
    conta = tela.combo_conta_do_endireitar
    titulo_conta = tela.rotulo_conta_do_endireitar
    linha = tela.rotulo_angulos_medidos

    def pedaco() -> QRect:
        botao_volta = botao_com_texto(tela.paineis.propriedades, "usar o ângulo do programa")
        return com_folga(juntar(no_janela(botao_volta, janela),
                                juntar(no_janela(conta, janela), no_janela(linha, janela))), 14, janela)

    cena = Cena(janela)
    print("     automático: linha =", repr(linha.text()))
    cena.ampliado("22-rodada14-mao-antes-ampliado", pedaco(), "Com o ângulo do programa: a lista acesa e os dois ângulos")
    cena.inteira("22-rodada14-mao-antes", [pedaco()])
    tela.botao_angulo_horario.click()
    esperar(4)
    rolagem.setValue(rolagem.maximum())
    esperar(0.5)
    print("     à mão: linha =", repr(linha.text()), "· lista acesa:", conta.isEnabled())
    cena = Cena(janela)
    cena.ampliado("22-rodada14-mao-hoje-ampliado", pedaco(), "Hoje, depois de girar à mão: a lista apagada e a linha some")
    cena.inteira("22-rodada14-mao-a", [pedaco()])
    # B: uma frase no lugar da linha vazia
    linha.setText("Você pôs o ângulo à mão, por isso a conta não vale. Para voltar a ela: "
                  "“usar o ângulo do programa”.")
    esperar(0.5)
    cena = Cena(janela)
    cena.ampliado("22-rodada14-mao-b-ampliado", pedaco(), "B: uma frase diz por quê")
    cena.inteira("22-rodada14-mao-b", [pedaco()])
    # C: a lista some, fica só a frase
    conta.setVisible(False)
    linha.setText("Ângulo posto à mão: a conta não vale nesta página. Para voltar a ela: "
                  "“usar o ângulo do programa”.")
    esperar(0.5)
    cena = Cena(janela)
    cena.ampliado("22-rodada14-mao-c-ampliado", pedaco(), "C: a lista some e fica só a frase")
    cena.inteira("22-rodada14-mao-c", [pedaco()])
    conta.setVisible(True)
    tela.botao_angulo_anti_horario.click()
    esperar(3)


def _menu_ver_hoje(janela) -> list:
    """Os itens do menu Ver de hoje (para devolver depois de mexer)."""
    return list(menu_do_titulo(janela, "Ver").actions())


def _foto_do_menu(janela, menu: QMenu, nome: str, titulo: str, submenu: QMenu | None = None,
                  inteira: bool = True) -> None:
    onde = abrir_menu(janela, menu)
    cena = Cena(janela)
    cena.colar(menu, onde)
    ret = QRect(onde, menu.size())
    if submenu is not None:
        acao = submenu.menuAction()
        geo = menu.actionGeometry(acao)
        onde_sub = QPoint(onde.x() + menu.width() - 4, onde.y() + geo.top())
        submenu.popup(QPoint(-30000, -31000))
        esperar(0.5)
        cena.colar(submenu, onde_sub)
        ret = ret.united(QRect(onde_sub, submenu.size()))
        submenu.close()
    menu.close()
    esperar(0.3)
    barra = no_janela(janela.menu, janela)
    pedaco = com_folga(ret.united(QRect(barra.left(), barra.top(), ret.right() - barra.left(), 1)), 10, janela)
    cena.ampliado(f"{nome}-ampliado", pedaco, titulo)
    if inteira:
        cena.inteira(nome, [ret])


def q_menus(janela, tela) -> None:
    """902 (lugar da troca do lado direito, opção do menu Ver), 903 (os painéis nos menus) e
    904 (as coisas novas nos menus)."""
    print("\n903 painéis nos menus · 904 coisas novas · 902 lado direito no menu Ver")
    from PySide6.QtGui import QAction, QActionGroup
    tela.trilha.escolher("cortar")
    tela.paineis.fechar()
    esperar(2)
    ver = menu_do_titulo(janela, "Ver")
    hoje = list(ver.actions())
    _foto_do_menu(janela, ver, "22-rodada14-paineis-hoje", "Hoje: quatro nomes de painel que não fazem nada")

    itens_paineis = [a for a in hoje if a.text().startswith("Painel:")]
    nomes = [("Propriedades", True), ("Filtro da página", False), ("Para revisar", False),
             ("Automático", False), ("Histórico", False)]

    def acoes_dos_paineis(pai) -> list:
        lista = []
        for nome, marcado in nomes:
            a = QAction(nome, pai)
            a.setCheckable(True)
            a.setChecked(marcado)
            lista.append(a)
        return lista

    # A: no menu Ver, os cinco
    novos = acoes_dos_paineis(ver)
    antes_de = itens_paineis[0]
    for a in itens_paineis:
        ver.removeAction(a)
    titulo_a = None
    sep_depois = [a for a in ver.actions() if a.isSeparator()]
    ponto = sep_depois[1] if len(sep_depois) > 1 else None
    for a in novos:
        ver.insertAction(ponto, a)
    _foto_do_menu(janela, ver, "22-rodada14-paineis-a", "A: no menu Ver, os cinco painéis")
    # devolve
    for a in novos:
        ver.removeAction(a)

    # B: menu novo "Painéis"
    for a in itens_paineis:
        ver.removeAction(a)
    menu_p = QMenu("Painéis", janela.menu)
    for a in acoes_dos_paineis(menu_p):
        menu_p.addAction(a)
    menu_p.addSeparator()
    menu_p.addAction(QAction("Fechar o painel", menu_p))
    menu_p.addAction(QAction("Esconder os ícones da direita", menu_p))
    janela.menu.insertMenu(menu_do_titulo(janela, "Ajuda").menuAction(), menu_p)
    esperar(0.5)
    _foto_do_menu(janela, menu_p, "22-rodada14-paineis-b", "B: um menu novo, “Painéis”")
    _foto_do_menu(janela, ver, "22-rodada14-paineis-b-ver", "B: o menu Ver fica sem os painéis", inteira=False)
    janela.menu.removeAction(menu_p.menuAction())

    # C: nenhum (só pelos ícones)
    _foto_do_menu(janela, ver, "22-rodada14-paineis-c", "C: os painéis saem dos menus (só pelos ícones)")

    # 904 A: as coisas novas da tela no menu Ver (com os cinco painéis da A da 903)
    novos = acoes_dos_paineis(ver)
    sep = [a for a in ver.actions() if a.isSeparator()]
    for a in novos:
        ver.insertAction(sep[1] if len(sep) > 1 else None, a)
    extra = []
    ponto = [a for a in ver.actions() if a.isSeparator()][-1]
    for texto in ("Miniaturas", "Ícones da direita", "Ver lado a lado", "Todas as páginas",
                  "Filtros em tela cheia"):
        a = QAction(texto, ver)
        if texto in ("Miniaturas", "Ícones da direita"):
            a.setCheckable(True)
            a.setChecked(True)
        ver.insertAction(ponto, a)
        extra.append(a)
    s = ver.insertSeparator(ponto)
    extra.append(s)
    _foto_do_menu(janela, ver, "22-rodada14-novas-a", "A: as peças novas da tela também no menu Ver")
    for a in extra + novos:
        ver.removeAction(a)
    _foto_do_menu(janela, ver, "22-rodada14-novas-b", "B: o menu Ver não ganha nada (só os botões da tela)")

    # 902 A: a troca do lado direito no menu Ver (o menu Ver de hoje, com o item a mais)
    for a in list(ver.actions()):
        ver.removeAction(a)
    for a in hoje:
        ver.addAction(a)
    tema = next(m for m in ver.findChildren(QMenu) if m.title() == "Tema")
    lado = QMenu("Lado direito", ver)
    grupo = QActionGroup(lado)
    for texto, marcado in (("Ícones na borda (de fábrica)", True), ("Sanfona (a área de trabalho 1)", False),
                           ("Abas no alto", False), ("Painel solto", False)):
        a = QAction(texto, lado)
        a.setCheckable(True)
        a.setChecked(marcado)
        grupo.addAction(a)
        lado.addAction(a)
    ver.insertMenu(tema.menuAction(), lado)
    _foto_do_menu(janela, ver, "22-rodada14-lado-a", "A: no menu Ver, ao lado do Tema", submenu=lado)
    ver.removeAction(lado.menuAction())

    # devolve os quatro de hoje no lugar
    for a in list(ver.actions()):
        ver.removeAction(a)
    for a in hoje:
        ver.addAction(a)


def montar_configuracoes(parte: str = "aparencia") -> QWidget:
    """A tela de Configurações como foi decidida (807 B: a lista das partes à esquerda), montada AQUI
    com as peças e as cores do programa, com a parte Aparência à vista (tema e, na opção B da 902,
    o lado direito). Esta tela ainda não existe no programa."""
    from ui import estilo
    tela = QWidget()
    tela.setObjectName("cfgTela")
    tela.setStyleSheet(f"#cfgTela {{ background: {estilo.cor('app')}; }}")
    fora = QVBoxLayout(tela)
    fora.setContentsMargins(0, 0, 0, 0)
    fora.setSpacing(0)
    alto = QFrame()
    alto.setStyleSheet(f"background: {estilo.cor('bar')}; border-bottom: 1px solid {estilo.cor('linha')};")
    la = QHBoxLayout(alto)
    la.setContentsMargins(16, 10, 16, 10)
    t = QLabel("Configurações")
    t.setStyleSheet(f"color: {estilo.cor('forte')}; font-size: 16px; font-weight: 600; border: none;")
    la.addWidget(t)
    la.addStretch()
    voltar = QPushButton("voltar")
    la.addWidget(voltar)
    fora.addWidget(alto)
    corpo = QHBoxLayout()
    corpo.setContentsMargins(0, 0, 0, 0)
    corpo.setSpacing(0)
    lista = QListWidget()
    lista.setFixedWidth(220)
    for nome in ("Aparência", "Para todos os livros", "Atalhos de teclado"):
        lista.addItem(nome)
    lista.setCurrentRow(0)
    lista.setStyleSheet(f"QListWidget {{ background: {estilo.cor('painel')}; border: none; "
                        f"border-right: 1px solid {estilo.cor('linha')}; padding: 8px; font-size: 13px; "
                        f"color: {estilo.cor('texto')}; }} QListWidget::item {{ padding: 9px 10px; "
                        f"border-radius: 4px; }} QListWidget::item:selected {{ background: {estilo.cor('sel')}; "
                        f"color: {estilo.cor('forte')}; }}")
    corpo.addWidget(lista)
    direita = QWidget()
    ld = QVBoxLayout(direita)
    ld.setContentsMargins(28, 22, 28, 22)
    ld.setSpacing(8)

    def titulo(texto):
        r = QLabel(texto)
        r.setStyleSheet(f"color: {estilo.cor('forte')}; font-size: 14px; font-weight: 600;")
        return r

    def frase(texto):
        r = QLabel(texto)
        r.setWordWrap(True)
        r.setStyleSheet(f"color: {estilo.cor('fraco')}; font-size: 12px;")
        return r

    ld.addWidget(titulo("Tema"))
    ld.addWidget(frase("As cores do programa."))
    linha = QHBoxLayout()
    for nome, marcado in (("Escuro", False), ("Cinza (de fábrica)", True), ("Claro", False)):
        b = QRadioButton(nome)
        b.setChecked(marcado)
        linha.addWidget(b)
    linha.addStretch()
    ld.addLayout(linha)
    caixa_lado = QWidget()
    ll = QVBoxLayout(caixa_lado)
    ll.setContentsMargins(0, 18, 0, 0)
    ll.setSpacing(8)
    ll.addWidget(titulo("Lado direito"))
    ll.addWidget(frase("Como os painéis (Propriedades, Filtro, Para revisar, Automático, Histórico) "
                       "aparecem à direita da página."))
    grade = QVBoxLayout()
    for nome, marcado in (("Ícones na borda (de fábrica)", True), ("Sanfona (a área de trabalho 1)", False),
                          ("Abas no alto", False), ("Painel solto", False)):
        b = QRadioButton(nome)
        b.setChecked(marcado)
        grade.addWidget(b)
    ll.addLayout(grade)
    ld.addWidget(caixa_lado)
    ld.addStretch()
    corpo.addWidget(direita, 1)
    fora.addLayout(corpo, 1)
    tela.caixa_lado = caixa_lado
    return tela


def q_lado_configuracoes(janela) -> None:
    """902 B: a troca do lado direito nas Configurações (a tela decidida na 807 B, montada aqui)."""
    print("\n902 lado direito nas Configurações")
    cfg = montar_configuracoes()
    cfg.setAttribute(Qt.WA_ShowWithoutActivating)
    cfg.resize(janela.size())
    cfg.move(-32000, -32000)
    cfg.show()
    cfg.move(-32000, -32000)
    esperar(1.5)
    cena = Cena(cfg)
    lado = no_janela(cfg.caixa_lado, cfg)
    cena.ampliado("22-rodada14-lado-b-ampliado", com_folga(lado.adjusted(-240, -110, 0, 0), 4, cfg),
                  "B: nas Configurações, na parte Aparência")
    cena.inteira("22-rodada14-lado-b", [lado])
    cfg.close()
    esperar(0.5)


def montar_todas_as_paginas(janela, tela, vista: str) -> QWidget:
    """A tela "Todas as páginas" (rodadas 1 e 2: "uma a uma / em pares", "todas / só as que precisam
    de atenção"; clique num par abre as duas lado a lado), montada AQUI com as cores do programa e as
    páginas de verdade do livro (a metade certa de cada folha, como a tira de miniaturas corta).
    Esta tela ainda não existe no programa."""
    import numpy as np
    from core.pdf_io import abrir_pdf, pagina_para_array
    from ui import estilo
    from ui.widgets.visualizador import numpy_para_qimage

    tira = tela.tira
    projeto = janela.projeto
    total = len(projeto.paginas)
    mostrar = list(range(0, 24))
    em_alerta = {i for i in mostrar if projeto.paginas[i].alertas and not projeto.paginas[i].revisada}
    motivos = {}
    from core import analise
    for i in em_alerta:
        cod = projeto.paginas[i].alertas[0]
        motivos[i] = analise.ALERTAS[cod].titulo if cod in analise.ALERTAS else "confira"

    doc = abrir_pdf(str(LIVRO))
    folhas = {}

    def imagem(indice: int) -> QPixmap:
        folha = next(f for f, idx in tira._mapa_folha.items() if indice in idx)
        if folha not in folhas:
            folhas[folha] = pagina_para_array(doc, folha, dpi=40)
        img = tira._metade(indice, folhas[folha])
        return QPixmap.fromImage(numpy_para_qimage(np.ascontiguousarray(img)))

    tela_t = QWidget()
    tela_t.setObjectName("todasTela")
    tela_t.setStyleSheet(f"#todasTela {{ background: {estilo.cor('tela')}; }}")
    fora = QVBoxLayout(tela_t)
    fora.setContentsMargins(0, 0, 0, 0)
    fora.setSpacing(0)
    alto = QFrame()
    alto.setObjectName("todasAlto")
    alto.setStyleSheet(f"#todasAlto {{ background: {estilo.cor('bar')}; border-bottom: 1px solid {estilo.cor('linha')}; }}")
    la = QHBoxLayout(alto)
    la.setContentsMargins(14, 8, 14, 8)
    la.setSpacing(6)
    t = QLabel("Todas as páginas")
    t.setStyleSheet(f"color: {estilo.cor('forte')}; font-size: 15px; font-weight: 600;")
    la.addWidget(t)
    la.addSpacing(14)

    def chave(texto, ligado):
        b = QPushButton(texto)
        b.setCheckable(True)
        b.setChecked(ligado)
        if ligado:
            b.setStyleSheet(f"QPushButton {{ background: {estilo.cor('sel')}; border: 1px solid {estilo.cor('azul')}; "
                            f"color: {estilo.cor('forte')}; padding: 4px 12px; }}")
        else:
            b.setStyleSheet(f"QPushButton {{ background: {estilo.cor('botao')}; border: 1px solid {estilo.cor('sep')}; "
                            f"color: {estilo.cor('texto')}; padding: 4px 12px; }}")
        return b

    tela_t.chave_uma = chave("uma a uma", vista == "uma")
    tela_t.chave_pares = chave("em pares", vista == "pares")
    la.addWidget(tela_t.chave_uma)
    la.addWidget(tela_t.chave_pares)
    la.addSpacing(14)
    la.addWidget(chave("todas", True))
    la.addWidget(chave(f"só as que precisam de atenção ({len(em_alerta)})", False))
    la.addStretch()
    la.addWidget(QPushButton("voltar ao trabalho"))
    fora.addWidget(alto)

    rolagem = QScrollArea()
    rolagem.setWidgetResizable(True)
    rolagem.setStyleSheet(f"QScrollArea {{ background: {estilo.cor('tela')}; border: none; }}")
    dentro = QWidget()
    dentro.setObjectName("todasDentro")
    dentro.setStyleSheet(f"#todasDentro {{ background: {estilo.cor('tela')}; }}")
    grade = QGridLayout(dentro)
    grade.setContentsMargins(18, 16, 18, 16)
    grade.setHorizontalSpacing(14)
    grade.setVerticalSpacing(10)
    altura = 150
    largura_do_quadro = 140 if vista == "uma" else 232

    def quadro(pixes, legenda, alerta, atual):
        q = QWidget()
        q.setFixedWidth(largura_do_quadro)
        lq = QVBoxLayout(q)
        lq.setContentsMargins(0, 0, 0, 0)
        lq.setSpacing(3)
        lbl = QLabel()
        largura_total = sum(round(p.width() * altura / p.height()) for p in pixes)
        junta = QPixmap(largura_total, altura)
        junta.fill(QColor("#FFFFFF"))
        pp = QPainter(junta)
        x = 0
        for p in pixes:
            w = round(p.width() * altura / p.height())
            pp.drawPixmap(QRect(x, 0, w, altura), p)
            x += w
        pp.end()
        lbl.setPixmap(junta)
        cor_borda = estilo.cor("aviso") if alerta else (estilo.cor("azul") if atual else estilo.cor("sep"))
        grossura = 3 if (alerta or atual) else 1
        lbl.setStyleSheet(f"border: {grossura}px solid {cor_borda}; padding: 2px; background: {estilo.cor('painel')};")
        lq.addWidget(lbl, 0, Qt.AlignHCenter)
        leg = QLabel(legenda)
        leg.setWordWrap(True)
        leg.setFixedWidth(largura_do_quadro)
        leg.setAlignment(Qt.AlignHCenter)
        leg.setStyleSheet(f"color: {estilo.cor('aviso') if alerta else estilo.cor('fraco')}; font-size: 12px;"
                          + (" font-weight: 600;" if alerta else ""))
        lq.addWidget(leg)
        return q

    atual = tela.indice_pagina
    if vista == "uma":
        colunas = 8
        for n, i in enumerate(mostrar):
            leg = f"{i + 1}" + (f" · {motivos[i].lower()}" if i in motivos else "")
            grade.addWidget(quadro([imagem(i)], leg, i in em_alerta, i == atual), n // colunas, n % colunas)
    else:
        colunas = 5
        # como num livro: a página 1 sozinha, à direita; depois 2-3, 4-5...
        pares = [[0]] + [[i, i + 1] for i in range(1, mostrar[-1], 2)]
        for n, par in enumerate(pares):
            alerta = any(i in em_alerta for i in par)
            nomes = " e ".join(str(i + 1) for i in par)
            leg = nomes + (" · " + motivos[next(i for i in par if i in motivos)].lower() if alerta else "")
            pixes = [imagem(i) for i in par]
            if len(par) == 1:
                branco = QPixmap(pixes[0].size())
                branco.fill(QColor(estilo.cor("tela")))
                pixes = [branco] + pixes
            grade.addWidget(quadro(pixes, leg, alerta, atual in par), n // colunas, n % colunas)
    grade.setRowStretch(grade.rowCount(), 1)
    grade.setColumnStretch(colunas, 1)
    rolagem.setWidget(dentro)
    fora.addWidget(rolagem, 1)
    pe = QLabel(("Uma a uma: cada página do livro num quadro. Clique numa página para ir até ela."
                 if vista == "uma" else
                 "Em pares: as duas páginas lado a lado, como vão ser impressas. Clique num par para ver as duas grandes.")
                + f"   ·   {total} páginas")
    pe.setStyleSheet(f"background: {estilo.cor('bar')}; color: {estilo.cor('fraco')}; padding: 7px 14px; "
                     f"border-top: 1px solid {estilo.cor('linha')}; font-size: 12px;")
    fora.addWidget(pe)
    tela_t.alto = alto
    tela_t.grade_dentro = dentro
    return tela_t


def q_todas(janela, tela) -> None:
    """901: a vista de fábrica de "Todas as páginas"."""
    print("\n901 Todas as páginas")
    from core import analise
    projeto = janela.projeto
    # avisos postos À MÃO em três páginas, só para a grade ter o que mostrar (como na etapa 3)
    for indice, codigo in ((6, analise.ANGULO_SUSPEITO_), (11, analise.LOMBADA_INCERTA), (19, analise.COR)):
        projeto.paginas[indice].alertas = [codigo]
        projeto.paginas[indice].revisada = False
    for vista, letra in (("uma", "a"), ("pares", "b")):
        t = montar_todas_as_paginas(janela, tela, vista)
        t.setAttribute(Qt.WA_ShowWithoutActivating)
        t.resize(janela.size())
        t.move(-32000, -32000)
        t.show()
        t.move(-32000, -32000)
        esperar(1.5)
        cena = Cena(t)
        alto = no_janela(t.alto, t)
        chaves = juntar(no_janela(t.chave_uma, t), no_janela(t.chave_pares, t))
        pedaco = QRect(0, 0, 640, 300)
        cena.ampliado(f"22-rodada14-todas-{letra}-ampliado", pedaco,
                      "A: abre “uma a uma”" if letra == "a" else "B: abre “em pares”")
        cena.inteira(f"22-rodada14-todas-{letra}", [chaves])
        del alto
        t.close()
        esperar(0.5)


def principal(destino: Path) -> None:
    global SAIDA
    SAIDA = destino
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    print("escala da tela:", janela.devicePixelRatioF())
    tela.ir_para_pagina(4)
    esperar(6)
    pedido = sys.argv[2:] or ["base", "pedaco", "aviso", "dividir", "mao", "menus", "lado", "todas"]
    if "base" in pedido:
        base(janela, tela)
    if "pedaco" in pedido:
        q_mesmo_da_pagina(janela, tela)
    if "aviso" in pedido:
        q_aviso_marcar(janela, tela)
    if "dividir" in pedido:
        q_dividir_palavra(janela, tela)
    if "mao" in pedido:
        q_endireitar_a_mao(janela, tela)
    if "menus" in pedido:
        q_menus(janela, tela)
    if "lado" in pedido:
        q_lado_configuracoes(janela)
    if "todas" in pedido:
        tela.ir_para_pagina(4)
        esperar(3)
        q_todas(janela, tela)
    janela.close()
    esperar(1)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
