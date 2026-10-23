"""Mapa do programa, achado 0-4 (verificador, 23/10/2026): para cada combinação de caixinhas
da tela "Marque o que você quer fazer", clica "Conferir" e conta os ícones da coluna da
esquerda e as páginas com dúvida. Livro novo a cada combinação (pasta de dados própria).
Uso: python p1b_icones_da_esquerda.py <worktree> <saida_prints> <trabalho> <nome> <caixinhas>
  <caixinhas>: letras das que ficam MARCADAS: d=Dividir l=Limpar e=Endireitar c=Cortar as bordas"""
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB, NOME, LETRAS = sys.argv[1], Path(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
base.preparar(WT, TRAB)
from PySide6.QtCore import QPoint  # noqa: E402

ORIGINAL = Path(r"D:\Livros para editar\2 - TEOLOGIA\Escatologia\La vida eterna y La profundidad del alma.pdf")
LIVRO = base.TRAB / ORIGINAL.name
shutil.copy2(ORIGINAL, LIVRO)
j = base.nova_janela(1536, 800)
j.abrir_livro(str(LIVRO))
base.esperar(3)
op = j.tela_opcoes


def marcar(cx, ligar):
    if cx.isChecked() != ligar:
        op.rolagem.ensureWidgetVisible(cx, 50, 50)
        base.esperar(0.4)
        base.clique(j, cx, cx.rect().topLeft() + QPoint(9, 10))
    return cx.isChecked() == ligar


quer = {op.cx_dividir: "d" in LETRAS, op.cx_limpar: "l" in LETRAS,
        op.cx_endireitar: "e" in LETRAS, op.cx_cortar: "c" in LETRAS}
for cx, ligar in quer.items():
    base.conferir(marcar(cx, ligar), f"'{cx.text()}' {'marcada' if ligar else 'desmarcada'}")
op.rolagem.verticalScrollBar().setValue(0); base.esperar(0.5)
base.print_window(j, SAIDA / f"p1b-{NOME}-opcoes.png")
base.clique(j, op.botao_conferir)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(6)
tc = j.tela_conferir
base.print_window(j, SAIDA / f"p1b-{NOME}-conferir.png")
from ui.widgets.trilha_agrupada import GRUPOS  # noqa: E402
vivos = [g[0] for g in GRUPOS if g != "-" and tc.trilha._ferramentas_vivas(g)]
base.conferir(True, f"{NOME}: resumo '{op.resumo.text()}'; abas {tc._abas_ativas}; "
                    f"ícones da esquerda ({len(vivos)}): {vivos}")
base.fechar(j)
base.gravar_resultados(SAIDA / f"p1b-{NOME}")
