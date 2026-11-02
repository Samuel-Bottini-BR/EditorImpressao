"""D-600 (02/11/2026): prints de antes e depois do Shift + roda em cada tela com página e zoom.

Sem janela na tela (offscreen), com as letras do Windows, no "Na escola de Jesus" (a pasta de
dados de teste), página 2. Em cada tela: (1) com zoom, a página mais larga que o espaço; (2) depois
de três dentes de Shift + roda para baixo com o ponteiro no meio (a cruz vermelha é o ponteiro).
  shift-automatico-*        a janela grande do Automático, "A página, antes e depois" (zoom 2)
  shift-automatico-tela-cheia-*   a tela cheia dela (zoom 2)
  shift-automatico-comparar-*     o "comparar" da tela cheia (zoom 3, as duas telas juntas)
  shift-ver-de-perto-*      o "Ver de perto" da área de trabalho (zoom 3)
  shift-livro-aberto-*      o livro aberto, "Duas lado a lado" em "Tamanho real" (sem zoom: o par
                            é mais largo que a tela)
Uso: QT_QPA_FONTDIR=C:/Windows/Fonts python relatorios/zoom-mouse/fazer_prints_shift.py antes|depois
Os dados do programa (projetos) ficam em <worktree>/_tmp/dados_prints_shift. Nada é gravado fora
de _tmp e desta pasta."""
import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]   # a raiz da worktree
sys.path.insert(0, str(RAIZ))
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados_prints_shift")
SAIDA = Path(__file__).resolve().parent
LIVRO = (r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
         r"Na escola de Jesus - Catecismo explicado com imagens..pdf")
TAMANHO = (1280, 657)


def main() -> int:
    quando = sys.argv[1] if len(sys.argv) > 1 else "depois"
    from PySide6.QtCore import QPoint, QPointF, Qt, QTimer
    from PySide6.QtGui import QColor, QPainter, QPen, QWheelEvent
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    app = QApplication(sys.argv)
    QDialog.exec = lambda self, *a, **k: 0          # nenhuma caixa fica esperando clique
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(900000, lambda: (print("tempo esgotado"), app.exit(3)))

    def assentar(segundos: float = 0.3) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim:
            app.processEvents()
            time.sleep(0.02)

    def esperar(condicao, segundos: float = 240.0) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim and not condicao():
            assentar(0.1)

    def shift_roda(vista, ponto: QPoint, vezes: int = 3) -> None:
        for _ in range(vezes):
            evento = QWheelEvent(QPointF(ponto), QPointF(vista.mapToGlobal(ponto)), QPoint(0, 0),
                                 QPoint(0, -120), Qt.NoButton, Qt.ShiftModifier, Qt.NoScrollPhase, False)
            QApplication.sendEvent(vista, evento)
            assentar(0.15)

    def print_(janela, vista, ponto: QPoint, nome: str) -> None:
        """A janela inteira, com uma cruz vermelha onde está o ponteiro."""
        assentar(0.5)
        foto = janela.grab()
        no_print = vista.mapTo(janela, ponto)
        pintor = QPainter(foto)
        pintor.setPen(QPen(QColor(220, 0, 0), 3))
        pintor.drawLine(no_print.x() - 14, no_print.y(), no_print.x() + 14, no_print.y())
        pintor.drawLine(no_print.x(), no_print.y() - 14, no_print.x(), no_print.y() + 14)
        pintor.end()
        caminho = SAIDA / f"{nome}-{quando}.png"
        foto.save(str(caminho))
        print("gravado", caminho.name)

    def no_meio_da_barra(rolagem) -> None:
        barra = rolagem.horizontalScrollBar()
        barra.setValue(barra.maximum() // 2)

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(*TAMANHO)
    janela.show()
    janela.abrir_livro(LIVRO)
    assentar(3)
    janela.tela_conferir.ir_para_pagina(1)
    assentar(1)

    # 1. o Automático: "A página, antes e depois"
    grande = janela.abrir_o_automatico()
    grande.resize(*TAMANHO)
    grande.show()
    painel = grande.antes_e_depois
    esperar(lambda: not painel.calculando() and painel.visor.depois is not None)
    vista = painel.visor
    vista.definir_zoom(2.0)
    assentar()
    no_meio_da_barra(vista.rolagem)
    porta = vista.rolagem.viewport()
    ponto = vista.mapFrom(porta, porta.rect().center())
    print_(grande, vista, ponto, "shift-automatico-1-com-zoom")
    shift_roda(vista, ponto)
    print_(grande, vista, vista.mapFrom(porta, porta.rect().center()), "shift-automatico-2-shift-roda-3-vezes")

    # 2. a tela cheia dela
    vista.ajustar_a_tela()
    painel.botao_tela_cheia.click()
    assentar(1)
    tela = painel.tela_cheia
    tela.setWindowState(Qt.WindowNoState)
    tela.resize(*TAMANHO)
    assentar(1)
    vista = tela.visor
    vista.definir_zoom(2.0)
    assentar()
    no_meio_da_barra(vista.rolagem)
    porta = vista.rolagem.viewport()
    ponto = vista.mapFrom(porta, porta.rect().center())
    print_(tela, vista, ponto, "shift-automatico-tela-cheia-1-com-zoom")
    shift_roda(vista, ponto)
    print_(tela, vista, vista.mapFrom(porta, porta.rect().center()),
           "shift-automatico-tela-cheia-2-shift-roda-3-vezes")

    # 3. o "comparar" da tela cheia
    vista.ajustar_a_tela()
    tela.botao_comparar.click()
    esperar(lambda: not painel.calculando() and tela.vista_a._pixmap is not None
            and tela.vista_b._pixmap is not None)
    assentar(1)
    a = tela.vista_a
    a.definir_zoom(3.0)
    assentar()
    ponto = a.rect().center()
    print_(tela, a, ponto, "shift-automatico-comparar-1-com-zoom")
    shift_roda(a, ponto)
    print_(tela, a, ponto, "shift-automatico-comparar-2-shift-roda-3-vezes")
    tela.accept()
    grande.close()
    assentar(1)

    # 4. o "Ver de perto"
    from ui.tela_ampliada import MODO_FILTRO, TelaAmpliada

    ampliada = TelaAmpliada(janela.tela_conferir, modo=MODO_FILTRO, parent=janela)
    ampliada.resize(*TAMANHO)
    ampliada.show()
    esperar(lambda: ampliada.vista._pixmap is not None, 120)
    assentar(1)
    vista = ampliada.vista
    vista.definir_zoom(3.0)
    assentar()
    ponto = vista.rect().center()
    print_(ampliada, vista, ponto, "shift-ver-de-perto-1-com-zoom")
    shift_roda(vista, ponto)
    print_(ampliada, vista, ponto, "shift-ver-de-perto-2-shift-roda-3-vezes")
    ampliada.close()

    # 5. o livro aberto: "Duas lado a lado", "Tamanho real" (o par mais largo que a tela)
    from ui.widgets import paginas_rolando as pr

    livro = pr.PaginasRolando()
    livro.resize(*TAMANHO)
    livro.show()
    livro.abrir(LIVRO)
    livro.definir_jeito(mostrar=pr.DUAS, caber=pr.TAMANHO_REAL, continuo=True)
    livro.ir_para(2)
    esperar(lambda: 2 in livro.guardadas and 1 in livro.guardadas, 120)
    assentar(1)
    no_meio_da_barra(livro)
    porta = livro.viewport()
    ponto = porta.rect().center()
    print_(livro, porta, ponto, "shift-livro-aberto-1-par-mais-largo")
    shift_roda(porta, ponto)
    esperar(lambda: not livro._pedidas, 30)
    print_(livro, porta, ponto, "shift-livro-aberto-2-shift-roda-3-vezes")
    livro.parar()
    livro.close()

    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
