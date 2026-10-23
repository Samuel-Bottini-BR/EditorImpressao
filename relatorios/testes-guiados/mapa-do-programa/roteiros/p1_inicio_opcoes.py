"""Mapa do programa, parte 1 (verificador, 23/10/2026): tela inicial vazia, abrir o livro,
a tela "Marque o que você quer fazer" (de fábrica, com o Preto e branco, com Dividir + Limpar),
e o achado 0-4: Conferir só com Dividir + Limpar e contar os ícones da coluna da esquerda.
Janela fora da tela, dados numa pasta própria (nunca a do Samuel). Cliques do Windows nos
botões que o Samuel clica (Conferir); as caixinhas são marcadas pelo clique do Windows também.
Uso: python p1_inicio_opcoes.py <worktree> <saida_prints> <trabalho>"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT, SAIDA, TRAB = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
base.preparar(WT, TRAB)
LIVRO_ORIGINAL = Path(r"D:\Livros para editar\2 - TEOLOGIA\Escatologia\La vida eterna y La profundidad del alma.pdf")
LIVRO = base.TRAB / "La vida eterna y La profundidad del alma.pdf"
shutil.copy2(LIVRO_ORIGINAL, LIVRO)           # só leitura do original: a cópia é a que abre
TXT = SAIDA / "textos-p1.txt"
if TXT.exists():
    TXT.unlink()

j = base.nova_janela(1536, 800)
base.print_window(j, SAIDA / "p1-01-inicio-vazia.png")
base.gravar_textos(j, TXT, "tela inicial vazia")

j.abrir_livro(str(LIVRO))
base.esperar(3)
op = j.tela_opcoes
base.conferir(j.telas.currentWidget() is op, "abrir o PDF leva à tela 'Marque o que você quer fazer'")
base.print_window(j, SAIDA / "p1-02-opcoes-fabrica.png")
base.gravar_textos(j, TXT, "opções de fábrica (janela 1536x800)")
# o cartão inteiro das escolhas (o que só se vê rolando), pelo grab do Qt
def cartao_inteiro(nome):
    op.rolagem.widget().grab().save(str(SAIDA / nome))
    print("  grab", nome, flush=True)


def marcar(cx, ligar=True):
    """Clique do Windows na caixinha, depois de rolar até ela (fora da rolagem o clique cai fora)."""
    if cx.isChecked() != ligar:
        op.rolagem.ensureWidgetVisible(cx, 50, 50)
        base.esperar(0.4)
        base.clique(j, cx, cx.rect().topLeft() + __import__("PySide6.QtCore", fromlist=["QPoint"]).QPoint(9, 10))
        base.esperar(0.4)
    return cx.isChecked() == ligar


cartao_inteiro("p1-03-opcoes-fabrica-inteira.png")

# Preto e branco: aparecem "Só as letras", a força sozinha (cinza e marcada) e a limpeza
from core.filtros import PRETO_E_BRANCO  # noqa: E402
op.rolagem.ensureWidgetVisible(op.radios_de_filtro[PRETO_E_BRANCO]); base.esperar(0.3)
base.clique(j, op.radios_de_filtro[PRETO_E_BRANCO])
base.esperar(1)
base.print_window(j, SAIDA / "p1-04-opcoes-preto-e-branco.png")
cartao_inteiro("p1-04b-opcoes-preto-e-branco-inteira.png")
base.gravar_textos(j, TXT, "opções com o Preto e branco")
base.conferir(op.cx_forca_sozinha.isChecked() and not op.cx_forca_sozinha.isEnabled(),
              "achado 0-2: 'Escurecer sozinho...' aparece MARCADA e CINZA sem 'Só as letras'")
# Só as letras ligada: a força sozinha acende
marcar(op.escolhas_misto.caixa, True); base.esperar(1)
cartao_inteiro("p1-05b-opcoes-so-as-letras-inteira.png")
base.print_window(j, SAIDA / "p1-05-opcoes-so-as-letras.png")
base.gravar_textos(j, TXT, "opções com o Preto e branco + Só as letras")
base.conferir(op.cx_forca_sozinha.isEnabled(), "com 'Só as letras' a caixinha da força acende")
marcar(op.escolhas_misto.caixa, False)
# volta ao filtro de fábrica (o primeiro marcado na abertura era o de fábrica)
from core.filtros import ORIGINAL  # noqa: E402
base.clique(j, op.radios_de_filtro[ORIGINAL]); base.esperar(0.5)

# "Mais opções" das gravuras aberto
op.rolagem.ensureWidgetVisible(op.botao_mais_opcoes, 50, 200); base.esperar(0.4)
base.clique(j, op.botao_mais_opcoes); base.esperar(0.8)
base.print_window(j, SAIDA / "p1-06-opcoes-gravuras-mais.png")
base.gravar_textos(j, TXT, "opções com 'Mais opções' das gravuras aberto")
op.rolagem.ensureWidgetVisible(op.botao_mais_opcoes, 50, 200); base.esperar(0.4)
base.clique(j, op.botao_mais_opcoes); base.esperar(0.5)

# cada caixinha marcada para ver o que ela abre embaixo (borda preta, margens, cadernos)
for cx in (op.cx_borda_preta, op.cx_margens, op.cx_cadernos, op.cx_dividir):
    base.conferir(marcar(cx, True), f"clique do Windows marcou '{cx.text()}'")
cartao_inteiro("p1-07-opcoes-tudo-aberto.png")
base.gravar_textos(j, TXT, "opções com dividir, borda preta, margens e cadernos marcadas")

# --- achado 0-4: só Dividir + Limpar -------------------------------------------------------
for cx in (op.cx_borda_preta, op.cx_margens, op.cx_cadernos, op.cx_endireitar, op.cx_cortar,
           op.cx_cortar_pelo_conteudo, op.cx_cortar_sobra):
    marcar(cx, False)
for cx in (op.cx_dividir, op.cx_limpar):
    marcar(cx, True)
base.esperar(1)
op.rolagem.verticalScrollBar().setValue(0); base.esperar(0.5)
base.print_window(j, SAIDA / "p1-08-opcoes-dividir-e-limpar.png")
cartao_inteiro("p1-08b-opcoes-dividir-e-limpar-inteira.png")
base.gravar_textos(j, TXT, "opções só com Dividir + Limpar")
p = j.projeto
base.conferir(p.dividir_folhas and p.limpar and not p.endireitar and not p.cortar_bordas,
              f"marcadas só Dividir + Limpar (dividir={p.dividir_folhas} limpar={p.limpar} "
              f"endireitar={p.endireitar} cortar={p.cortar_bordas} detectar_regioes={p.detectar_regioes} "
              f"gravura_forma={p.gravura_forma})")

base.clique(j, op.botao_conferir)
base.esperar(2)
base.print_window(j, SAIDA / "p1-09-olhando-o-livro.png")
import time  # noqa: E402
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.conferir(j.telas.currentWidget() is j.tela_conferir, f"a análise acabou em {time.time() - t0:.0f} s")
base.esperar(6)
base.print_window(j, SAIDA / "p1-10-conferir-dividir-e-limpar.png")
base.gravar_textos(j, TXT, "conferir com Dividir + Limpar")
tc = j.tela_conferir
from ui.widgets.trilha_agrupada import GRUPOS  # noqa: E402
vivos = [g for g in GRUPOS if g != "-" and tc.trilha._ferramentas_vivas(g)]
base.conferir(True, f"achado 0-4: abas ativas = {tc._abas_ativas}; grupos à vista na coluna da esquerda = {vivos}")

base.fechar(j)
base.gravar_resultados(SAIDA / "p1")
