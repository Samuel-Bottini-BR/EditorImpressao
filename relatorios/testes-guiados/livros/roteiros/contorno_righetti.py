"""Righetti (verificador, 23/10/2026): o livro escaneado de lado só pôde ser girado DEPOIS do
"Conferir", e aí as folhas não se dividem. Contorno que o Kaique tentaria: continuar o trabalho,
Arquivo > "Voltar para as opções" e "Conferir" de novo, agora com as folhas já de pé. Divide?
Usa a pasta de trabalho do percurso do Righetti (não limpa). Uso: python contorno_righetti.py <worktree>"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import base  # noqa: E402

WT = sys.argv[1]
RAIZ = Path(r"D:\programas\EditorImpressao-arquivos\testes-livros-saida\righetti")
base.preparar(WT, str(RAIZ / "trab"), limpar=False)
SAIDA = RAIZ / "contorno"
SAIDA.mkdir(exist_ok=True)
j = base.nova_janela(1536, 800)
base.esperar(2)
from ui.tela_inicio import CartaoDeProjeto  # noqa: E402
cartao = [c for c in j.tela_inicio.findChildren(CartaoDeProjeto) if c.isVisible()][0]
j.tela_inicio.pedir_para_continuar(cartao.resumo)        # o "continuar" do cartão (direto)
t0 = time.time()
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 300:
    base.esperar(1)
base.esperar(6)
P = j.tela_conferir.projeto
print(f"continuar: {len(P.folhas)} folhas, {len(P.paginas)} páginas, giro folha 1 = {P.folhas[0].rotacao}", flush=True)
base.print_window(j, SAIDA / "1-continuar.png")
tc = j.tela_conferir
from core import girar as G  # noqa: E402
tc.paineis.abrir("props"); base.esperar(2)
tc.barra_girar.definir_alcance(G.ALCANCE_TODAS); base.esperar(0.5)
base.clique(j, tc.barra_girar.botoes_de_giro[G.GIRO_ESQUERDA]); base.esperar(8)
print(f"girei todas: giro folha 1 = {P.folhas[0].rotacao}, última = {P.folhas[-1].rotacao}", flush=True)
base.print_window(j, SAIDA / "1b-girado.png")
j.menu.acoes["voltar"].trigger()                        # Arquivo > Voltar para as opções
base.esperar(3)
op = j.tela_opcoes
print(f"opções: frase '{op.resumo.text()}'", flush=True)
base.print_window(j, SAIDA / "2-opcoes.png")
base.clique(j, op.botao_conferir)
t0 = time.time()
base.esperar(3)
while j.telas.currentWidget() is not j.tela_conferir and time.time() - t0 < 600:
    base.esperar(1)
base.esperar(8)
P = j.tela_conferir.projeto
print(f"depois de conferir de novo ({time.time() - t0:.0f} s): {len(P.folhas)} folhas, {len(P.paginas)} páginas, "
      f"giro folha 1 = {P.folhas[0].rotacao}, dividir folha 1 = {P.folhas[0].dividir}", flush=True)
base.print_window(j, SAIDA / "3-conferir-de-novo.png")
base.fechar(j)
