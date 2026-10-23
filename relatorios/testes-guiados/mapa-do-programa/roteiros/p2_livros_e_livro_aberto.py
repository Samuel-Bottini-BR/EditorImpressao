"""Mapa do programa, parte 2 (verificador, 23/10/2026): a tela dos livros com o cartão do livro
(trabalho deixado pela parte 1), o menu do botão direito do cartão, o livro aberto na tela
inteira (clique do Windows no cartão), o "Mais...", "Ver todas as páginas", e o "Rodar o
automático..." (aonde ele leva). Termina marcando Dividir + Limpar + Endireitar + Cortar e
clicando "Conferir" (o trabalho fica para a parte 3).
Uso: python p2_livros_e_livro_aberto.py <worktree> <saida_prints> <trabalho_da_parte_1>"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
base.preparar(WT, TRAB, limpar=False)
from PySide6.QtCore import QPoint, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QMenu  # noqa: E402

TXT = SAIDA / "textos-p2.txt"
if TXT.exists():
    TXT.unlink()


def print_do_menu_que_abrir(nome, fechar=True):
    """Quando um QMenu abrir (exec ou popup), tira o print dele, lista os itens e fecha."""
    def olhar(tentativas=[0]):
        menus = [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu) and w.isVisible()]
        if not menus:
            tentativas[0] += 1
            if tentativas[0] < 40:
                QTimer.singleShot(150, olhar)
            return
        m = menus[-1]
        base.print_window(m, SAIDA / f"{nome}.png", so_cliente=False)
        with open(TXT, "a", encoding="utf-8") as f:
            f.write(f"\n===== menu {nome} =====\n" + "\n".join(base.acoes_do_menu(m)) + "\n")
        if fechar:
            m.close()
    QTimer.singleShot(400, olhar)


j = base.nova_janela(1536, 800)
ti = j.tela_inicio
base.esperar(2)
base.print_window(j, SAIDA / "p2-01-livros-com-cartao.png")
base.gravar_textos(j, TXT, "tela dos livros com um cartão")
from ui.tela_inicio import CartaoDeProjeto  # noqa: E402
cartoes = [c for c in ti.findChildren(CartaoDeProjeto) if c.isVisible()]
base.conferir(len(cartoes) == 1, f"um cartão na tela dos livros ({len(cartoes)})")
cartao = cartoes[0]

# botão direito do cartão: o menu (exec bloqueia; o print sai pelo relógio)
print_do_menu_que_abrir("p2-02-menu-do-cartao")
cartao._abrir_menu(cartao.rect().center())
base.esperar(1)

# um clique do Windows no cartão: o livro aberto na tela inteira
base.clique(j, cartao, QPoint(cartao.width() // 2, 40))
base.esperar(4)
la = ti.livro_aberto
base.conferir(ti.pilha.currentWidget() is la, "um clique no cartão abre o livro na tela inteira")
base.print_window(j, SAIDA / "p2-03-livro-aberto.png")
base.gravar_textos(j, TXT, "livro aberto na tela inteira")

print_do_menu_que_abrir("p2-04-menu-mais")
base.clique(j, la.botao_mais)
base.esperar(2)

base.clique(j, la.botao_todas)
base.esperar(4)
base.print_window(j, SAIDA / "p2-05-ver-todas-as-paginas.png")
base.gravar_textos(j, TXT, "ver todas as páginas (do livro aberto)")
base.tecla(j, 0x1B)      # Esc
base.esperar(2)
if ti.pilha.currentWidget() is not la:
    ti.abrir_o_livro(cartao.resumo); base.esperar(2)

# "Rodar o automático...": aonde leva?
base.clique(j, la.botao_automatico)
base.esperar(4)
qual = type(j.telas.currentWidget()).__name__
base.conferir(j.telas.currentWidget() is j.tela_opcoes,
              f"'Rodar o automático...' leva à tela '{getattr(j.telas.currentWidget(), 'titulo', None) and j.telas.currentWidget().titulo.text()}' ({qual})")
base.print_window(j, SAIDA / "p2-06-depois-do-rodar-o-automatico.png")

# Dividir + Limpar + Endireitar + Cortar (o caminho de fábrica com o Dividir) e Conferir
op = j.tela_opcoes
for cx in (op.cx_dividir, op.cx_limpar, op.cx_endireitar, op.cx_cortar):
    if not cx.isChecked():
        op.rolagem.ensureWidgetVisible(cx, 50, 50); base.esperar(0.4)
        base.clique(j, cx, cx.rect().topLeft() + QPoint(9, 10))
base.conferir(all(c.isChecked() for c in (op.cx_dividir, op.cx_limpar, op.cx_endireitar, op.cx_cortar)),
              f"marcadas as quatro: '{op.resumo.text()}'")
base.clique(j, op.botao_conferir)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(8)
base.print_window(j, SAIDA / "p2-07-conferir-de-fabrica-com-dividir.png")
base.fechar(j)
base.gravar_resultados(SAIDA / "p2")
