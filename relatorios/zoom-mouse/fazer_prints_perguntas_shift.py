"""D-600 (02/11/2026): prints das duas perguntas abertas do Shift + roda (ONDE-PAREI, seção de 02/11).

Sem janela na tela (offscreen), com as letras do Windows, no "Na escola de Jesus", página 2.
  pergunta-1-sem-zoom-*  a "A página, antes e depois" do Automático com a página inteira cabendo
                         (100%): antes e depois de UM dente de Shift + roda para baixo (hoje: zoom).
  pergunta-2-pincel-*    a área de trabalho, ferramenta Pincel, com zoom: antes e depois de três
                         dentes de Shift + roda para baixo (hoje: muda a espessura do pincel; a
                         página não anda). Também mede o Retângulo.
A cruz vermelha é o ponteiro. O que cada um fez sai escrito no terminal.
Uso: QT_QPA_FONTDIR=C:/Windows/Fonts python relatorios/zoom-mouse/fazer_prints_perguntas_shift.py
Os dados do programa ficam em <worktree>/_tmp/dados_prints_shift."""
import os
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
os.environ["LOCALAPPDATA"] = str(RAIZ / "_tmp" / "dados_prints_shift")
SAIDA = Path(__file__).resolve().parent
LIVRO = (r"D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/"
         r"Na escola de Jesus - Catecismo explicado com imagens..pdf")
TAMANHO = (1280, 657)


def main() -> int:
    from PySide6.QtCore import QPoint, QPointF, Qt, QTimer
    from PySide6.QtGui import QColor, QPainter, QPen, QWheelEvent
    from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

    app = QApplication(sys.argv)
    QDialog.exec = lambda self, *a, **k: 0
    QMessageBox.exec = lambda self, *a, **k: 0
    QTimer.singleShot(600000, lambda: (print("tempo esgotado"), app.exit(3)))

    def assentar(segundos: float = 0.3) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim:
            app.processEvents()
            time.sleep(0.02)

    def esperar(condicao, segundos: float = 240.0) -> None:
        fim = time.monotonic() + segundos
        while time.monotonic() < fim and not condicao():
            assentar(0.1)

    def shift_roda(vista, ponto: QPoint, vezes: int) -> None:
        for _ in range(vezes):
            evento = QWheelEvent(QPointF(ponto), QPointF(vista.mapToGlobal(ponto)), QPoint(0, 0),
                                 QPoint(0, -120), Qt.NoButton, Qt.ShiftModifier, Qt.NoScrollPhase, False)
            QApplication.sendEvent(vista, evento)
            assentar(0.15)

    def print_(janela, vista, ponto: QPoint, nome: str) -> None:
        assentar(0.5)
        foto = janela.grab()
        no_print = vista.mapTo(janela, ponto)
        pintor = QPainter(foto)
        pintor.setPen(QPen(QColor(220, 0, 0), 3))
        pintor.drawLine(no_print.x() - 14, no_print.y(), no_print.x() + 14, no_print.y())
        pintor.drawLine(no_print.x(), no_print.y() - 14, no_print.x(), no_print.y() + 14)
        pintor.end()
        foto.save(str(SAIDA / f"{nome}.png"))
        print("gravado", f"{nome}.png")

    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(*TAMANHO)
    janela.show()
    janela.abrir_livro(LIVRO)
    assentar(3)
    tela = janela.tela_conferir
    tela.ir_para_pagina(1)
    assentar(1)

    # pergunta 1: o Automático, a página inteira cabendo (100%)
    grande = janela.abrir_o_automatico()
    grande.resize(*TAMANHO)
    grande.show()
    painel = grande.antes_e_depois
    esperar(lambda: not painel.calculando() and painel.visor.depois is not None)
    vista = painel.visor
    vista.ajustar_a_tela()
    assentar()
    porta = vista.rolagem.viewport()
    ponto = vista.mapFrom(porta, porta.rect().center())
    print_(grande, vista, ponto, "pergunta-1-sem-zoom-antes-do-shift-roda")
    zoom = vista.zoom
    shift_roda(vista, ponto, 1)
    print_(grande, vista, vista.mapFrom(porta, porta.rect().center()), "pergunta-1-sem-zoom-depois-de-1-shift-roda")
    print(f"pergunta 1: zoom {zoom:.2f} -> {vista.zoom:.2f}")
    grande.close()
    assentar(1)

    # pergunta 2: a área de trabalho, Pincel (e Retângulo), com zoom
    for ferramenta in ("pincel", "retangulo"):
        tela.escolher_ferramenta(ferramenta)
        assentar(1)
        editor = tela.editor_selecao
        esperar(lambda: getattr(editor, "_imagem", None) is not None or getattr(editor, "_pixmap", None) is not None, 60)
        tela.mudar_o_zoom(None)
        tela.botao_mais_zoom.click()
        tela.botao_mais_zoom.click()
        assentar(1)
        ponto = editor.rect().center()
        desl, espessura, zoom = editor.deslocamento, editor.espessura, editor.zoom
        if ferramenta == "pincel":
            print_(janela, editor, ponto, "pergunta-2-pincel-com-zoom-antes-do-shift-roda")
        shift_roda(editor, ponto, 3)
        if ferramenta == "pincel":
            print_(janela, editor, ponto, "pergunta-2-pincel-depois-de-3-shift-roda")
        print(f"pergunta 2, {ferramenta}: zoom {zoom:.2f} -> {editor.zoom:.2f}; deslocamento {desl.x()},{desl.y()} -> "
              f"{editor.deslocamento.x()},{editor.deslocamento.y()}; espessura {espessura:.4f} -> {editor.espessura:.4f}")
    janela.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
