"""Abre um livro NOVO na janela (programa reaberto), visita as paginas pedidas e fotografa
a tela e o "Ver de perto" de cada uma.  Uso: visita.py <livro|caminho.pdf> <prefixo> <pag> [pag...]
Uma pagina com '*' no fim (ex.: 3*) e so visitada (medida), sem foto de perto."""
import sys, time, v
from livros import LIVROS
P = v.P
livro, prefixo, pags = sys.argv[1], sys.argv[2], sys.argv[3:]
caminho = LIVROS.get(livro, livro)
try:
    P.fechar()
except Exception:
    pass
print(v.abrir())
print(livro, "abriu em", v.novo_livro(caminho), "s;", v.s("(len(tc.projeto.paginas), tc.projeto.misto_so_as_letras, tc.projeto.misto_fora_do_texto, tc.projeto.reforcar_texto_falhado, tc.projeto.ordem_do_preparo, tc.indice_pagina+1)"))
print("ao abrir:", v.contagem())
for pg in pags:
    so_medir = pg.endswith("*"); n = int(pg.rstrip("*"))
    if int(v.s("tc.indice_pagina")) + 1 != n:
        v.ir_pagina(n)
    t = v.esperar_medida(300); time.sleep(4)
    print(f"p{n}: medida {t} s |", v.curto())
    if so_medir:
        continue
    print("   faixa:", v.faixa())
    print("   foto:", v.foto(f"{prefixo}-p{n}-tela")[0][-34:])
    x, y, vis, ativo = v.g.geo(f"tc.tira._miniaturas[{n - 1}]")
    P.clicar_em(P.principal(), int(x), int(y), duplo=True); time.sleep(5)
    j = P.janela("Ver de perto")
    if j:
        v.foto(f"{prefixo}-p{n}-perto", j["hwnd"]); v.botao_da_caixa("Ver de perto", "X", espera=1.5)
print("faixa medida:", v.s("[(p.indice+1, p.faixa_na_beirada) for p in tc.projeto.paginas if p.faixa_na_beirada is not None]"), "| obs:", v.s("tc.projeto.observacoes"))
print("no fim:", v.contagem())
print("erros.log:", repr(v.erros_log()[-300:]))
