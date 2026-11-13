"""Print 5, continuação: reabre o projeto do La vida eterna já dividido (a mesma pasta de dados do
p5_pares.py) e tira os pares 8-9 e 10-11 em "Duas lado a lado"."""
import sys
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum

comum.preparar(str(AQUI.parent), "p5", limpar=False)
from ui.widgets.paginas_rolando import DUAS
j = comum.nova_janela()
j.abrir_livro(str(AQUI / "livros" / "vida_eterna.pdf"))
print("abrir", comum.esperar_tela(j), flush=True)
tela, projeto = j.tela_conferir, j.projeto
print("paginas", len(projeto.paginas_ativas), flush=True)
tela.definir_mostrar(DUAS)
comum.esperar(1.0)
for i in (8, 10):
    tela.ir_para_pagina(i)
    comum.esperar(3.0)
    comum.ate(lambda: all(tela.previas.ja_pronta(k, tela._dpi_atual) is not None for k in (i - 1, i)), 240)
    comum.esperar(4.0)
    comum.foto(j, AQUI / "cru" / "p5" / f"tela-duas-pagina-{i + 1}.png")
comum.fechar(j)
