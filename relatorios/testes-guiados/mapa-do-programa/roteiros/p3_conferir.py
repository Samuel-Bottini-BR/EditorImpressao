"""Mapa do programa, parte 3 (verificador, 23/10/2026): a tela de conferir, num livro novo com
Dividir + Limpar + Endireitar + Cortar (o caminho de fábrica mais o Dividir, porque o livro
tem folhas duplas). Os menus do alto, a coluna da esquerda (cada ferramenta), a coluna de
ícones da direita (cada painel), a faixa ("está certo", "próxima dúvida"), a barra de espaço,
as miniaturas, o rodapé, "ver todas", os filtros em tela cheia, a folha 5 (achado 0-5).
Cliques do Windows onde o Samuel clica; o resto por chamada direta (dito no texto).
Uso: python p3_conferir.py <worktree> <saida_prints> <trabalho>"""
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
base.preparar(WT, TRAB)
from PySide6.QtCore import QPoint  # noqa: E402

TXT = SAIDA / "textos-p3.txt"
if TXT.exists():
    TXT.unlink()


def anota(texto):
    print("  · " + texto, flush=True)
    with open(TXT, "a", encoding="utf-8") as f:
        f.write(texto + "\n")


ORIGINAL = Path(r"D:\Livros para editar\2 - TEOLOGIA\Escatologia\La vida eterna y La profundidad del alma.pdf")
LIVRO = base.TRAB / ORIGINAL.name
shutil.copy2(ORIGINAL, LIVRO)
j = base.nova_janela(1536, 800)
j.abrir_livro(str(LIVRO))
base.esperar(3)
op = j.tela_opcoes
for cx in (op.cx_dividir, op.cx_limpar, op.cx_endireitar, op.cx_cortar):
    if not cx.isChecked():
        op.rolagem.ensureWidgetVisible(cx, 50, 50); base.esperar(0.4)
        base.clique(j, cx, cx.rect().topLeft() + QPoint(9, 10))
anota("resumo da tela de opções: " + op.resumo.text())
base.clique(j, op.botao_conferir)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(8)
tc = j.tela_conferir
base.print_window(j, SAIDA / "p3-01-conferir.png")
base.gravar_textos(j, TXT, "conferir, folha 1, Dividir a folha")
anota(f"abas: {tc._abas_ativas}")

# --- menus do alto ---------------------------------------------------------------------
barra = j.menu
for acao in barra.actions():
    menu = acao.menu()
    if menu is None or not acao.isVisible():
        continue
    nome = acao.text().replace("&", "")
    base.print_do_menu_que_abrir(f"p3-menu-{nome}", SAIDA, TXT)
    menu.popup(QPoint(-30000, -30000))
    base.esperar(1.5)
    if menu.isVisible():
        menu.close()

# --- coluna da esquerda: o balão de cada botão e cada ferramenta de página ---------------
tr = tc.trilha
from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR, FERRAMENTA_DIVIDIR, FERRAMENTA_ENDIREITAR, FERRAMENTA_FILTROS, GRUPOS  # noqa: E402,E501
for indice, ret in sorted(tr.retangulos().items(), key=lambda x: x[1].y()):
    anota(f"esquerda, {ret.y()} px: {tr.texto_da_dica(indice)}")
for ferramenta, nome in ((FERRAMENTA_CORTAR, "cortar"), (FERRAMENTA_ENDIREITAR, "endireitar"),
                         (FERRAMENTA_FILTROS, "filtros"), (FERRAMENTA_DIVIDIR, "dividir")):
    indice = next(i for i, g in enumerate(GRUPOS) if g != "-" and ferramenta in g)
    ret = tr.retangulos()[indice]
    base.clique(j, tr, ret.center())          # clique do Windows no ícone
    base.esperar(3)
    anota(f"clique em {nome}: aba {tc.aba_atual}; painel aberto {tc.paineis.aberto}; faixa '{tc.texto_faixa.text()}'")
    base.print_window(j, SAIDA / f"p3-02-ferramenta-{nome}.png")
    base.gravar_textos(j, TXT, f"ferramenta {nome}")

# --- coluna da direita: cada ícone ---------------------------------------------------------
tc.paineis.fechar(); base.esperar(1)
ic = tc.paineis.icones
for chave, ret in ic.retangulos().items():
    anota(f"direita, {ret.y()} px: '{chave}' balão: {ic.texto_da_dica(chave)}")
for chave, ret in ic.retangulos().items():
    if chave == "seta":
        continue
    base.clique(j, ic, ret.center())          # clique do Windows no ícone
    base.esperar(2.5)
    anota(f"clique no ícone '{chave}': painel aberto = {tc.paineis.aberto}")
    base.print_window(j, SAIDA / f"p3-03-painel-{chave}.png")
    base.gravar_textos(j, TXT, f"painel {chave}")
    base.clique(j, ic, ret.center())          # de novo fecha?
    base.esperar(1)
    anota(f"segundo clique no mesmo ícone: painel aberto = {tc.paineis.aberto}")
tc.paineis.fechar(); base.esperar(1)

# --- faixa: "está certo", "próxima dúvida" e a barra de espaço ------------------------------
def estado(rotulo):
    anota(f"{rotulo}: folha {tc.indice_folha + 1}, página {tc.indice_pagina + 1}; faixa '{tc.texto_faixa.text()}'; "
          f"rodapé '{tc.rotulo_da_pagina.text()}' / '{tc.rotulo_do_livro.text()}'")


tc._ferramenta_da_trilha(FERRAMENTA_DIVIDIR); tc.paineis.fechar(); tc.ir_para_pagina(0); base.esperar(3)
estado("antes do 'está certo'")
base.print_window(j, SAIDA / "p3-04-antes-do-esta-certo.png")
base.clique(j, tc.botao_esta_certo)
base.esperar(2)
estado("depois do 'está certo' (clique do Windows)")
base.print_window(j, SAIDA / "p3-05-depois-do-esta-certo.png")
base.clique(j, tc.botao_proxima_duvida)
base.esperar(3)
estado("depois do 'próxima dúvida' (clique do Windows)")
base.print_window(j, SAIDA / "p3-06-depois-da-proxima-duvida.png")
tc.ir_para_pagina(0); base.esperar(2)
tc.setFocus(); j.activateWindow(); base.esperar(0.5)
base.tecla(j, 0x20)                          # barra de espaço
base.esperar(2)
estado("depois da barra de espaço na folha 1")
base.print_window(j, SAIDA / "p3-07-depois-da-barra-de-espaco.png")
base.tecla(j, 0x09)                          # Tab
base.esperar(2)
estado("depois do Tab")

# --- folha 5 no Dividir (achado 0-5) ---------------------------------------------------------
tc._ferramenta_da_trilha(FERRAMENTA_DIVIDIR); tc.paineis.fechar()
from ui.widgets.trilha_agrupada import FERRAMENTA_DIVIDIR as _D  # noqa: E402,F401
alvo = next(i for i, p in enumerate(tc.projeto.paginas) if p.folha == 4)
tc.ir_para_pagina(alvo); base.esperar(4)
estado("folha 5")
base.print_window(j, SAIDA / "p3-08-folha-5-dividir.png")

# --- miniaturas e rodapé ----------------------------------------------------------------------
tc.ir_para_pagina(0); base.esperar(2)
base.gravar_textos(tc.miniaturas, TXT, "miniaturas (cabeçalho)")
from PySide6.QtWidgets import QAbstractButton  # noqa: E402
for b in tc.miniaturas.findChildren(QAbstractButton):
    if b.isVisible():
        anota(f"miniaturas, botão '{b.text()}' balão '{b.toolTip()}'")
pontinhos = [b for b in tc.miniaturas.findChildren(QAbstractButton) if b.isVisible() and "•" in b.text()]
if pontinhos:
    base.print_do_menu_que_abrir("p3-09-menu-das-miniaturas", SAIDA, TXT)
    base.clique(j, pontinhos[0]); base.esperar(2)
todas = [b for b in tc.miniaturas.findChildren(QAbstractButton) if b.isVisible() and "ver todas" in b.text()]
if todas:
    base.clique(j, todas[0]); base.esperar(4)
    base.print_window(j, SAIDA / "p3-10-ver-todas.png")
    base.gravar_textos(j, TXT, "ver todas (na conferência)")
    base.tecla(j, 0x1B); base.esperar(2)
    anota(f"Esc depois do 'ver todas': na grade ainda? {tc.pilha_da_tela.currentWidget() is tc.todas}")
    if tc.pilha_da_tela.currentWidget() is tc.todas:
        tc._voltar_das_todas(None); base.esperar(1)
base.gravar_textos(j, TXT, "barra de baixo")

# --- filtros em tela cheia (Ver > Filtros em tela cheia) ---------------------------------------
tc._ferramenta_da_trilha(FERRAMENTA_FILTROS); base.esperar(3)
base.print_window(j, SAIDA / "p3-11-os-quatro-filtros.png")
from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia  # noqa: E402
base.quando_abrir_janela(FiltrosEmTelaCheia, "p3-12-filtros-tela-cheia", SAIDA, TXT, espera_ms=6000)
j.menu.acoes["filtros_tela_cheia"].trigger(); base.esperar(2)

# --- atalhos ---------------------------------------------------------------------------------------
import atalhos  # noqa: E402
for a in atalhos.todas():
    anota(f"atalho: {a.nome} = {atalhos.tecla_atual(a.chave)}")
anota("atalhos do menu (Ajuda): " + j.menu.texto_dos_atalhos().replace("\n", " | "))

base.fechar(j)
base.gravar_resultados(SAIDA / "p3")
