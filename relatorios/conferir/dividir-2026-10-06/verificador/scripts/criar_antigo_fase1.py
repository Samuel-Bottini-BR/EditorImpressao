"""Verificador 2.1: monta, com o codigo do FASE-1 (<raiz>), um projeto como o
programa de antes gravava (livro novo dividia de fabrica), com algumas mudancas
de quem confere, e grava o projeto.json. Uso: <raiz> <livro.pdf> <de> <ate> <saida.json>"""
import json, sys
from pathlib import Path
raiz, livro, de, ate, saida = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
sys.path.insert(0, raiz)
import fitz
from core import pipeline
from modelos import Projeto
pedaco = Path(saida).with_suffix(".pdf")
o = fitz.open(livro); n = fitz.open(); n.insert_pdf(o, from_page=de - 1, to_page=ate - 1); n.save(str(pedaco)); n.close(); o.close()
p = Projeto(caminho_entrada=str(pedaco.resolve()), nome=Path(saida).stem)
print("fase-1 dividir de fabrica:", p.dividir_folhas)
pipeline.analisar_projeto(p)
# mudancas de quem confere (como a tela do fase-1 faz):
p.folhas[2].dividir = False; p.folhas[2].revisada = True          # "nao dividir esta" (fase-1)
pp = [x for x in p.paginas if x.folha == 4]
pp[0].apagada = True                                                # apagou a pagina da esquerda da folha 5
p.folhas[6].posicao_corte = 0.5; p.folhas[6].revisada = True       # arrastou a linha da folha 7
for x in p.paginas[:6]:
    x.filtro = "preto_e_branco"
Path(saida).write_text(json.dumps(p.para_dicionario(), ensure_ascii=False, indent=1), encoding="utf-8")
print(len(p.folhas), len(p.paginas), sum(f.dividir for f in p.folhas))
