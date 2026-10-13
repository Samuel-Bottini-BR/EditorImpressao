import time, v
P = v.P
HIST = "[a.descricao for a in tc.acoes.feitas]"
for _ in range(4):
    if v.s(HIST) == "[]": break
    P.tecla("Z", mods=("ctrl",)); time.sleep(1.5)
print("historico:", v.s(HIST))
v.ir_pagina(3); time.sleep(1)
print("Egenloff 3:"); v.passo("22a-egenloff-3-forca-sozinha", 180); time.sleep(6); print(" ", v.curto())
print("  faixa:", v.faixa()); print("  medidor:", v.s("tc.medidor.valor"), "historico:", v.s(HIST))
v.passo("22a-egenloff-3-forca-sozinha")
v.ir_pagina(47); time.sleep(1)
print("Egenloff 47:"); v.passo("22b-egenloff-47", 180); print("  faixa:", v.faixa())
print("observacoes do livro:", v.s("tc.projeto.observacoes"))
print("faixa na beirada por pagina medida:", v.s("[(p.indice+1, p.faixa_na_beirada) for p in tc.projeto.paginas if p.faixa_na_beirada is not None]"))
print("painel:", [x if isinstance(x, str) else x[0] for x in v.painel()])
