"""Antes/depois do 2.12 num TRECHO de livro (para a analise decidir girar/dividir
como no livro inteiro), so nas folhas pedidas. Usa o rodada_gabarito.py sem
mudanca: troca so o `abrir` para apagar (nesta conta) as outras paginas.

Uso: python rodada_trecho.py <pid> <pdf do trecho> <pasta> <folha> [folha ...]
(folha = indice dentro do trecho, a partir de 0)"""
import sys
sys.path.insert(0, "D:/programas/EditorImpressao/.claude/worktrees/fase2-itens/relatorios/fase2-itens/scripts")
from pathlib import Path
import rodada_gabarito as rg

pid, pdf, pasta = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
folhas = {int(x) for x in sys.argv[4:]}
rg.PDF_DE_FORA = pdf
_abrir = rg.abrir


def abrir(p):
    # o Kaique liga "Dividir" no livro de folhas duplas (de fabrica, livro
    # novo nao divide: item 2.1); o resto fica de fabrica
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto
    projeto = Projeto(caminho_entrada=str(pdf), nome=p, dividir_folhas=True)
    projeto = analisar_projeto(projeto)
    doc = abrir_pdf(projeto.caminho_entrada)
    for pagina in projeto.paginas:
        if pagina.folha not in folhas:
            pagina.apagada = True
    print("folhas", [(f.indice, f.rotacao, f.dividir, round(f.posicao_corte, 3)) for f in projeto.folhas
                     if f.indice in folhas], "paginas", [(pg.folha, pg.metade) for pg in projeto.paginas_ativas])
    return projeto, doc


rg.abrir = abrir
rg._registrar_falhas()
r = rg.rodada_do_item(pid, "2.12", pasta)
for k, v in r.items():
    print(k, v["pontos_diferentes_de_hoje"], v["segundos"], v["nao_rodou"])
