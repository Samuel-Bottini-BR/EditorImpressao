"""Shift + roda do mouse: a imagem da página anda para os lados (D-600, 02/11/2026).

O QUE O SAMUEL DECIDIU
    D-600, testando a D-599 (02/11/2026): "3- shift não funciona no automatico para mover para o
    lado. No duas paginas lado a lado está funcionando" · "e no automatico pode colocar o shift
    tambem, o shift tem que funcionar em todas as telas". No Livro de decisões: "Shift + roda move
    a imagem para os lados em todas as telas do programa que mostram página com zoom (área de
    trabalho, "antes e depois" do Automático e as outras), como já faz no "Duas lado a lado"."

O QUE ESTE ARQUIVO FAZ
    É a peça única que as telas usam para o Shift + roda, para nenhuma copiar a conta da outra.
    Nasceu do conserto `aba8c37` (01/11/2026, "Duas lado a lado"): o rolar padrão do Qt usa o
    Shift para descer de tela em tela na barra de pé, e o Windows manda o Shift + roda como roda
    de cima para baixo (angleDelta em y); por isso cada tela precisa pegar o Shift antes do Qt.
    Há dois tipos de tela:
      - as que ficam numa área de rolar (QScrollArea): a página do Automático e a tela cheia dela
        (ui/automatico.VistaAntesDepoisComZoom), o livro aberto (ui/widgets/paginas_rolando) e o
        "Duas lado a lado" (ui/widgets/paginas_lado_a_lado): `shift_roda_na_rolagem` e
        `andar_na_barra` mexem na barra de baixo;
      - as que andam por um deslocamento (ui/widgets/visualizador.Visualizador): o "Ver de
        perto", o "comparar" da tela cheia do Automático: `shift_roda_no_visualizador`.
    A área de trabalho ("Uma página", ui/tela_conferir._roda_na_pagina) tem a conta dela desde a
    etapa 9b-2 (D-568/D-599) e NÃO passa por aqui: ela fica como está.

O QUE NÃO FAZ (de propósito: CLAUDE.md §11, item 7, "só o que ele mandou")
    - Só age com o Shift apertado e SEM o Ctrl: o Ctrl + roda (zoom) e a roda sozinha continuam
      o que cada tela já fazia.
    - Só age quando há para onde ir de lado: numa área de rolar, quando a barra de baixo tem
      espaço (a imagem mais larga que a tela); no Visualizador, com zoom (acima de 100%, a mesma
      regra da área de trabalho, D-599). Com a página inteira cabendo (sem zoom), a tela
      continua fazendo o mesmo que a roda sozinha dela (Samuel, 02/11/2026, "1- sim":
      relatorios/zoom-mouse/ONDE-PAREI.md, seção de 02/11, pergunta 1).

Seguro mudar: PASSO_NO_VISUALIZADOR e FOLGA_NO_VISUALIZADOR (o quanto anda e a folga na beirada).
Arriscado: agir sem o Shift ou com o Ctrl (mudaria a roda sozinha e o zoom de todas as telas, que
o Samuel não pediu), ou agir com a página inteira cabendo, sem zoom (ele decidiu que aí fica como a roda sozinha)."""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication

# No Visualizador (sem barra de rolar): quanto um dente da roda anda, em fração da altura da
# vista, o mesmo da área de trabalho (ui/tela_conferir.TelaConferir.PASSO_DA_RODA_COM_ZOOM); e a
# folga, em pontos, que a beirada da página pode passar da beirada da vista (a mesma de
# TelaConferir._por_o_deslocamento). Seguro mudar.
PASSO_NO_VISUALIZADOR = 0.12
FOLGA_NO_VISUALIZADOR = 20


def quer_ir_de_lado(evento) -> bool:
    """O Shift está apertado e o Ctrl não (o Ctrl + roda é o zoom, D-568)."""
    teclas = evento.modifiers()
    return bool(teclas & Qt.ShiftModifier) and not bool(teclas & Qt.ControlModifier)


def quanto_de_lado(evento) -> int:
    """Quanto a roda girou (120 por dente). A roda de lado (tilt) manda em x; a roda comum com
    Shift, no Windows, manda em y. Positivo = roda para cima = ver o que está à esquerda."""
    delta = evento.angleDelta()
    return delta.x() or delta.y()


def andar_na_barra(barra, de_lado: int) -> None:
    """Anda a barra de baixo o mesmo tanto que a roda anda de cima para baixo numa área de
    rolar do Qt (as linhas por dente do Windows vezes o passo da barra). Roda para baixo
    (`de_lado` negativo): para a direita. A conta do conserto `aba8c37`."""
    passo = QApplication.wheelScrollLines() * barra.singleStep()
    barra.setValue(barra.value() - int(round(de_lado / 120.0 * passo)))


def shift_roda_na_rolagem(rolagem, evento) -> bool:
    """Numa área de rolar (QScrollArea): com Shift (sem Ctrl) e a imagem mais larga que o
    espaço (a barra de baixo tem para onde ir), anda para os lados, aceita a roda e devolve
    True. Senão não mexe em nada e devolve False (a tela faz o que já fazia)."""
    if not quer_ir_de_lado(evento):
        return False
    barra = rolagem.horizontalScrollBar()
    if barra.maximum() <= barra.minimum():
        return False
    de_lado = quanto_de_lado(evento)
    if de_lado:
        andar_na_barra(barra, de_lado)
    evento.accept()
    return True


def shift_roda_no_visualizador(vista, evento) -> bool:
    """No Visualizador (ui/widgets/visualizador): com Shift (sem Ctrl) e zoom (acima de 100%),
    muda o deslocamento para os lados (o mesmo do arrastar com a Mão), avisa quem acompanha
    (vista_mudou: o "comparar" anda junto), aceita a roda e devolve True. Sem zoom (a página
    inteira cabendo) não mexe em nada e devolve False.

    O quanto a página pode andar é a conta da área de trabalho, aprovada pelo Samuel na D-599
    (01/11/2026, ui/tela_conferir.TelaConferir._por_o_deslocamento): a beirada da página para na
    beirada da vista (com FOLGA_NO_VISUALIZADOR); e, como lá, "Shift + roda move para os lados
    também uma página estreita": com zoom, uma página mais estreita que a vista pode sair do
    meio até (zoom - 1) / 2 da largura da vista, sem o meio dela sair da vista. (Sem isso, no
    "Ver de perto" largo uma página alta ainda estreita com zoom 3 caía no zoom, print de
    02/11.) Se o arrastar já a levou mais longe, a roda não a puxa de volta de uma vez."""
    if not quer_ir_de_lado(evento) or vista._pixmap is None or vista.zoom <= 1.0 + 1e-3:
        return False
    largura = vista._largura_base() * vista.zoom
    de_lado = quanto_de_lado(evento)
    if de_lado:
        atual = vista.deslocamento
        lugar = max(1, vista.width())
        passo = PASSO_NO_VISUALIZADOR * max(1, vista.height())
        x = atual.x() + de_lado / 120.0 * passo
        sobra = (vista.zoom - 1.0) / 2.0
        limite = max(0.0, (largura - lugar) / 2.0 + FOLGA_NO_VISUALIZADOR,
                     min(lugar * sobra, lugar / 2.0), abs(atual.x()))
        x = min(limite, max(-limite, x))
        vista.deslocamento = QPoint(int(round(x)), atual.y())
        vista.vista_mudou.emit(vista.zoom, vista.deslocamento)
        vista.update()
    evento.accept()
    return True
