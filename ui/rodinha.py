"""A rodinha do mouse só muda número ou lista que a pessoa clicou.

POR QUE EXISTE
    Teste do Kaique (agente leigo, 26/10/2026): "ao rolar a janela 'Montar para
    imprimir' com a rodinha do mouse, o campo 'Páginas da esquerda (pares)'
    passou de 100% para 60% sozinho, porque a rodinha passou por cima dele [...]
    O Kaique pode imprimir um livro com metade das páginas encolhidas."

    Por padrão o Qt deixa a rodinha mudar a caixa de número (QSpinBox,
    QDoubleSpinBox) e a lista (QComboBox) que estiver debaixo do mouse, mesmo sem
    clique; e a caixa de número até "pega o foco" pela rodinha (WheelFocus).
    Numa janela que rola, a rodinha que devia descer a janela muda o número.

O QUE FAZ
    `proteger(raiz)`: em toda caixa de número e lista dentro de `raiz` (as que
    já existem), a rodinha só muda o valor depois que a pessoa clicou na caixa
    (ou chegou nela pelo Tab). Fora disso, a rodinha rola a janela, como a
    pessoa esperava.

    `instalar_no_programa(app)`: o mesmo para o programa inteiro, inclusive o
    que for criado depois (um filtro só, no QApplication). A gerente decide se
    liga em main.py (anotado em relatorios/obra-etapa9a/ONDE-PAREI.md).

COMO
    Filtro de eventos.
    - Foco que a pessoa deu (clique, Tab, atalho) "libera" a rodinha na caixa;
      foco que a janela deu sozinha ao abrir (a primeira caixa da janela ganha
      o foco sem ninguém pedir) não libera. Clicar na caixa libera sempre.
    - A rodinha sobre caixa não liberada não chega a ela: uma cópia vai para a
      área que rola mais próxima (a janela de opções) e a original é dada por
      tratada. Repassar à mão, e não deixar o Qt passar ao pai sozinho, porque
      o Qt só passa adiante a rodinha do mouse de verdade - assim o teste
      automático prova o mesmo que o mouse faz.
    - A política de foco vira StrongFocus (clique e Tab), para a rodinha não
      dar o foco sozinha.

SEGURO MUDAR: a lista TIPOS (por exemplo, pôr o QSlider; hoje fora, porque o
    medidor dos filtros usa a rodinha de propósito e tem outro conserto aberto).
ARRISCADO: devolver False na rodinha de caixa não liberada (a caixa voltaria a
    mudar); deixar a original "não aceita" depois de repassar (o Qt repassaria
    de novo e a janela rolaria em dobro).
"""

from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPointF, Qt
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import (
    QAbstractScrollArea,
    QAbstractSpinBox,
    QApplication,
    QComboBox,
    QWidget,
)

# As peças que mudam de valor com a rodinha e não deviam mudar sem clique.
TIPOS = (QAbstractSpinBox, QComboBox)

# Foco que veio da pessoa: libera a rodinha na caixa.
_FOCO_DA_PESSOA = (Qt.FocusReason.MouseFocusReason, Qt.FocusReason.TabFocusReason,
                   Qt.FocusReason.BacktabFocusReason, Qt.FocusReason.ShortcutFocusReason)
_PROPRIEDADE = "rodinha_liberada"


def _caixa_de(objeto: QObject) -> QWidget | None:
    """A caixa protegida que contém `objeto` (o próprio, ou o campo de digitar
    de dentro de uma caixa de número ou lista editável), ou None."""
    atual = objeto
    for _ in range(3):              # o campo de digitar fica 1 nível abaixo
        if isinstance(atual, TIPOS):
            return atual
        atual = atual.parent() if isinstance(atual, QObject) else None
        if atual is None:
            return None
    return None


def rodinha_liberada(caixa: QWidget) -> bool:
    """A rodinha pode mudar o valor desta caixa agora?"""
    return caixa.hasFocus() and bool(caixa.property(_PROPRIEDADE))


def _area_que_rola(caixa: QWidget) -> QAbstractScrollArea | None:
    """A área com rolagem mais próxima acima da caixa, ou None."""
    pai = caixa.parentWidget()
    while pai is not None:
        if isinstance(pai, QAbstractScrollArea):
            return pai
        pai = pai.parentWidget()
    return None


def _repassar(evento: QWheelEvent, origem: QWidget, caixa: QWidget) -> None:
    """Manda uma cópia da rodinha para a área que rola acima da caixa."""
    area = _area_que_rola(caixa)
    if area is None:
        return
    alvo = area.viewport()
    ponto = QPointF(alvo.mapFromGlobal(origem.mapToGlobal(evento.position().toPoint())))
    copia = QWheelEvent(ponto, evento.globalPosition(), evento.pixelDelta(),
                        evento.angleDelta(), evento.buttons(), evento.modifiers(),
                        evento.phase(), evento.inverted())
    QApplication.sendEvent(alvo, copia)


class FiltroDaRodinha(QObject):
    """Libera a rodinha só na caixa que a pessoa escolheu; nas outras, a
    rodinha rola a janela."""

    def eventFilter(self, objeto, evento) -> bool:  # noqa: N802
        tipo = evento.type()
        if tipo not in (QEvent.Type.Wheel, QEvent.Type.FocusIn, QEvent.Type.MouseButtonPress):
            return False
        caixa = _caixa_de(objeto)
        if caixa is None:
            return False
        if caixa.focusPolicy() == Qt.FocusPolicy.WheelFocus:
            caixa.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        if tipo == QEvent.Type.FocusIn:
            caixa.setProperty(_PROPRIEDADE, evento.reason() in _FOCO_DA_PESSOA)
            return False
        if tipo == QEvent.Type.MouseButtonPress:
            caixa.setProperty(_PROPRIEDADE, True)
            return False
        if rodinha_liberada(caixa):
            return False
        # Repassa uma vez só: aceita a original, e o Qt para de entregá-la
        # (nem a caixa, nem o pai a recebem de novo).
        _repassar(evento, objeto, caixa)
        evento.accept()
        return True


_FILTRO_DO_PROGRAMA: list[FiltroDaRodinha] = []


def proteger(raiz: QWidget) -> FiltroDaRodinha:
    """Protege as caixas de número e as listas que já existem dentro de `raiz`
    (e a própria raiz, se for uma). Devolve o filtro (fica pendurado na raiz)."""
    filtro = FiltroDaRodinha(raiz)
    caixas = [raiz] if isinstance(raiz, TIPOS) else []
    for tipo in TIPOS:
        caixas += raiz.findChildren(tipo)
    for caixa in caixas:
        if caixa.focusPolicy() == Qt.FocusPolicy.WheelFocus:
            caixa.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        caixa.setProperty(_PROPRIEDADE, False)
        caixa.installEventFilter(filtro)
        for de_dentro in caixa.findChildren(QWidget):   # o campo de digitar
            de_dentro.installEventFilter(filtro)
    return filtro


def instalar_no_programa(app: QApplication | None = None) -> FiltroDaRodinha:
    """Liga a proteção no programa inteiro (uma vez só; chamar de novo não
    duplica). Para main.py, depois de criar o QApplication."""
    app = app or QApplication.instance()
    if _FILTRO_DO_PROGRAMA:
        return _FILTRO_DO_PROGRAMA[0]
    filtro = FiltroDaRodinha(app)
    app.installEventFilter(filtro)
    _FILTRO_DO_PROGRAMA.append(filtro)
    return filtro


def desinstalar_do_programa(app: QApplication | None = None) -> None:
    """Desliga o filtro do programa inteiro (para os testes voltarem ao normal)."""
    app = app or QApplication.instance()
    while _FILTRO_DO_PROGRAMA:
        filtro = _FILTRO_DO_PROGRAMA.pop()
        if app is not None:
            app.removeEventFilter(filtro)
