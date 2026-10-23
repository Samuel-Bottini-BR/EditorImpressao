"""Mapa do programa, parte 4 (verificador, 23/10/2026): "Confirmar e processar" no trabalho da
parte 3 (continuado pelo cartão), a janela "Antes de processar" (as dúvidas), a janela de
confirmar (onde salvar), o processamento e a tela "Ficou pronto!", e a janela "montar para
imprimir em A4". NUNCA clica "imprimir agora" (manda direto para a impressora do Samuel) nem
"abrir a pasta" (abriria o Explorer na tela dele). O PDF sai na pasta de trabalho.
Uso: python p4_processar.py <worktree> <saida_prints> <trabalho_da_parte_3>"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
base.preparar(WT, TRAB, limpar=False)
TXT = SAIDA / "textos-p4.txt"
if TXT.exists():
    TXT.unlink()


def anota(texto):
    print("  · " + texto, flush=True)
    with open(TXT, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


j = base.nova_janela(1536, 800)
base.esperar(2)
from ui.tela_inicio import CartaoDeProjeto  # noqa: E402
cartao = [c for c in j.tela_inicio.findChildren(CartaoDeProjeto) if c.isVisible()][0]
j.tela_inicio.pedir_para_continuar(cartao.resumo)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(6)
tc = j.tela_conferir
anota(f"continuar: tela de conferir ({tc._abas_ativas}); rodapé '{tc.rotulo_do_livro.text()}'")

from ui.janela_confirmar import JanelaConfirmar  # noqa: E402
from ui.janela_dos_avisos import JanelaDosAvisos  # noqa: E402
SAIDA_PDF = base.TRAB / "saida"
SAIDA_PDF.mkdir(exist_ok=True)


def na_confirmar(w):
    anota(f"janela de confirmar: título '{w.windowTitle()}', destino sugerido {w.caminho()}")
    w.destino.definir(SAIDA_PDF, "La vida eterna (pronto).pdf")
    base.esperar(0.8)
    base.print_window(w, SAIDA / "p4-03-confirmar-com-destino.png", so_cliente=False)
    base.clique(w, w.botao_processar)       # clique do Windows em "Processar"


def nos_avisos(w):
    anota(f"antes de processar: '{w.windowTitle()}' com {w.lista.count()} linhas")
    base.quando_abrir_janela(JanelaConfirmar, "p4-02-confirmar", SAIDA, TXT, depois=na_confirmar, fechar=False)
    base.clique(w, w.botao_continuar)        # "continuar assim mesmo"


base.quando_abrir_janela(JanelaDosAvisos, "p4-01-antes-de-processar", SAIDA, TXT, depois=nos_avisos, fechar=False)
base.clique(j, tc.botao_processar)           # clique do Windows em "Confirmar e processar"
base.esperar(5)
base.print_window(j, SAIDA / "p4-04-processando.png")
base.gravar_textos(j, TXT, "processando")
t0 = time.time()
while j.telas.currentWidget() is not j.tela_final and time.time() - t0 < 3000:
    base.esperar(2)
anota(f"processar levou {time.time() - t0:.0f} s; tela final? {j.telas.currentWidget() is j.tela_final}")
base.esperar(3)
base.print_window(j, SAIDA / "p4-05-ficou-pronto.png")
base.gravar_textos(j, TXT, "ficou pronto")
pdfs = list(SAIDA_PDF.glob("*.pdf"))
import fitz  # noqa: E402
for p in pdfs:
    with fitz.open(p) as d:
        anota(f"PDF gerado: {p.name}, {d.page_count} páginas")

# "montar para imprimir em A4 (com margens)..." (abre sem bloquear)
tf = j.tela_final
base.clique(j, tf.botao_montar)
base.esperar(6)
dlg = getattr(tf, "dialogo_impressao", None)
if dlg is not None and dlg.isVisible():
    base.print_window(dlg, SAIDA / "p4-06-montar-para-imprimir.png", so_cliente=False)
    base.gravar_textos(dlg, TXT, f"montar para imprimir ('{dlg.windowTitle()}')")
    dlg.reject() if hasattr(dlg, "reject") else dlg.close()
else:
    anota("a janela 'montar para imprimir' não abriu")
base.esperar(1)
base.fechar(j)
base.gravar_resultados(SAIDA / "p4")
