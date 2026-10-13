import time, v
from livros import LIVROS
P = v.P
v.clicar("fazer outro", classe="QPushButton", espera=2.5)
print("Egenloff abriu em", v.novo_livro(LIVROS["egenloff"]), "s")
print(v.s("(tc.projeto.nome, len(tc.projeto.paginas), tc.projeto.misto_so_as_letras, tc.projeto.reforcar_texto_falhado, tc.projeto.ordem_do_preparo, tc.indice_pagina+1)"))
print(v.s("__import__('collections').Counter(a for p in tc.projeto.paginas for a in p.alertas_pendentes)"))
v.passo("20a-egenloff-p1", 120)
print("fui para", v.ir_pagina(12)); v.passo("20b-egenloff-12-pagina-sem-conteudo", 120)
print("faixa:", v.faixa())
print("painel:", v.painel())
