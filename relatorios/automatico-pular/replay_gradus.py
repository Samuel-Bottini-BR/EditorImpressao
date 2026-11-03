import sys, json, copy
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\automatico-pular")
from modelos import Projeto, folhas_da_lista, paginas_da_lista
from core import automatico as A
P = r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free"
dados = json.load(open(P + r"\projeto.json", encoding="utf-8"))
acoes = [json.loads(l) for l in open(P + r"\acoes.jsonl", encoding="utf-8") if l.strip()]
antes = acoes[22]["antes"]
proj = Projeto.de_dicionario(copy.deepcopy(dados))
proj.folhas = folhas_da_lista(antes["livro.folhas"]); proj.paginas = paginas_da_lista(antes["livro.paginas"])
proj.dividir_folhas = antes["livro.dividir_folhas"]; proj.ordem_do_automatico = antes["livro.ordem_do_automatico"]
proj.margens_iguais = False
print("paginas antes:", len(proj.paginas))
ped = A.Pedido(etapas=["dividir"])
foto = A.fotografar(proj, ped)
print("redividir:", [(f.indice, f.redividir) for f in foto.folhas[:10]])
print("mexidas:", A.paginas_mexidas(proj, ped))
med = A.medir(foto)
for i in range(10): print(i, med[i])
res = A.aplicar(proj, ped, med)
print("paginas depois:", len(proj.paginas))
print([(f.indice, f.dividir, f.confianca_corte) for f in proj.folhas[:10]])
inteiras = [f.indice for f in proj.folhas if sum(1 for p in proj.paginas if p.folha == f.indice) < 2]
print("folhas que ficaram com uma pagina so (indice):", inteiras)
print("motor achou duas paginas e ficou inteira:", [i for i in inteiras if med.get(i) and med[i].dividir])
print("indices seguidos:", [p.indice for p in proj.paginas] == list(range(len(proj.paginas))))
