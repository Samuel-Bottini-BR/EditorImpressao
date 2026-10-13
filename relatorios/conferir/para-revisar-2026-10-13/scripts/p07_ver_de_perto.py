import time, v
P = v.P
print(v.s("__import__('collections').Counter(a for p in tc.projeto.paginas for a in p.alertas_pendentes)"))
print(v.s("__import__('collections').Counter(a for f in tc.projeto.folhas for a in getattr(f,'alertas_pendentes',f.alertas))"))
print(v.s("list(tc.cartoes.keys())"))
# duplo clique nativo no cartao do Preto e branco
x, y, vis, ativo = v.g.geo("tc.cartoes['preto_e_branco']")
P.clicar_em(P.principal(), int(x), int(y) - 40, duplo=True); time.sleep(3)
print([ (j[1], j[2], j[3]) for j in P.janelas()])
print(v.foto("03b-antiphonal-46-duplo-clique"))
for linha in v.itens(classes=("QPushButton",)): print(linha)
