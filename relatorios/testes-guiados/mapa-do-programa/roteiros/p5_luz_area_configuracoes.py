"""Mapa do programa, parte 5 (verificador, 23/10/2026): onde ficaram a Luz ("Mais ajustes" do
painel Filtro da página) e a "Área" (painel Propriedades com uma ferramenta de marcar), as
Configurações (cada parte) e a Ajuda. Usa o trabalho da parte 3 (continuado pelo cartão).
Uso: python p5_luz_area_configuracoes.py <worktree> <saida_prints> <trabalho_da_parte_3>"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
base.preparar(WT, TRAB, limpar=False)
TXT = SAIDA / "textos-p5.txt"
if TXT.exists():
    TXT.unlink()


def anota(texto):
    print("  · " + texto, flush=True)
    with open(TXT, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


j = base.nova_janela(1536, 800)
base.esperar(2)

# --- Configurações, pelo botão da tela dos livros (clique do Windows) -----------------------
from ui.tela_configuracoes import PARTES, TelaConfiguracoes  # noqa: E402


def nas_configuracoes(w):
    for i, nome in enumerate(PARTES):
        r = w.lista.visualItemRect(w.lista.item(i))
        base.clique(w, w.lista.viewport(), r.center())     # clique do Windows na parte
        base.esperar(1)
        anota(f"Configurações, parte '{nome}': aberta = {w.lista.currentRow() == i}")
        base.print_window(w, SAIDA / f"p5-01-configuracoes-{i + 1}.png", so_cliente=False)
        base.gravar_textos(w.pilha.currentWidget(), TXT, f"Configurações > {nome}")


base.quando_abrir_janela(TelaConfiguracoes, "p5-01-configuracoes-0", SAIDA, TXT, depois=nas_configuracoes)
base.clique(j, j.tela_inicio.botao_configuracoes)
base.esperar(3)

# --- Ajuda (tela dos livros) --------------------------------------------------------------------
from PySide6.QtWidgets import QDialog, QMessageBox  # noqa: E402
base.quando_abrir_janela(QDialog, "p5-02-ajuda", SAIDA, TXT)
base.clique(j, j.tela_inicio.botao_ajuda)
base.esperar(3)
_ = QMessageBox

# --- o trabalho da parte 3 ------------------------------------------------------------------------
from ui.tela_inicio import CartaoDeProjeto  # noqa: E402
cartao = [c for c in j.tela_inicio.findChildren(CartaoDeProjeto) if c.isVisible()][0]
j.tela_inicio.pedir_para_continuar(cartao.resumo)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(6)
tc = j.tela_conferir
from ui.widgets.paineis import PAINEL_FILTRO, PAINEL_PROPRIEDADES  # noqa: E402
from ui.widgets.trilha_agrupada import FERRAMENTA_FILTROS  # noqa: E402
tc._ferramenta_da_trilha(FERRAMENTA_FILTROS); base.esperar(2)
tc.paineis.abrir(PAINEL_FILTRO); base.esperar(3)
pf = tc.paineis.filtro_da_pagina
anota(f"painel Filtro, filtro Original: partes à vista = {[k for k, p in pf.partes.items() if p.isVisibleTo(pf)]}")
base.print_window(j, SAIDA / "p5-03-filtro-original.png")
base.gravar_textos(pf, TXT, "painel Filtro da página (Original)")
from core.filtros import PRETO_E_BRANCO  # noqa: E402
base.clique(j, pf.cartoes[PRETO_E_BRANCO])          # clique do Windows no cartãozinho do Preto e branco
base.esperar(4)
anota(f"painel Filtro, Preto e branco: partes à vista = {[k for k, p in pf.partes.items() if p.isVisibleTo(pf)]}")
mais = pf.partes["mais"]
mais.abrir(True); base.esperar(1.5)
pf_rolagem = mais
base.print_window(j, SAIDA / "p5-04-filtro-pb-mais-ajustes.png")
base.gravar_textos(pf, TXT, "painel Filtro da página (Preto e branco, Mais ajustes aberto)")
# o pedaço do painel inteiro (com rolagem), pelo grab do Qt
pf.grab().save(str(SAIDA / "p5-04b-painel-filtro-inteiro.png"))
mais.grab().save(str(SAIDA / "p5-04c-mais-ajustes.png"))

# --- a "Área": ferramenta Retângulo e o painel Propriedades -------------------------------------
from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO  # noqa: E402
tc._ferramenta_da_trilha(FERRAMENTA_RETANGULO); base.esperar(2)
tc.paineis.abrir(PAINEL_PROPRIEDADES); base.esperar(3)
base.print_window(j, SAIDA / "p5-05-propriedades-marcar.png")
base.gravar_textos(tc.paineis.propriedades, TXT, "painel Propriedades com o Retângulo")
tc.paineis.propriedades.grab().save(str(SAIDA / "p5-05b-propriedades-inteiro.png"))
base.fechar(j)
base.gravar_resultados(SAIDA / "p5")
