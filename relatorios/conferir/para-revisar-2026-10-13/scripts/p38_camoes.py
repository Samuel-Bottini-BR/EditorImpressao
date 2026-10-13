import time, v
P = v.P
def perto(nome):
    x, y, vis, ativo = v.g.geo(f"tc.tira._miniaturas[{int(v.s('tc.indice_pagina'))}]")
    P.clicar_em(P.principal(), int(x), int(y), duplo=True); time.sleep(5)
    j = P.janela("Ver de perto"); r = v.foto(nome, j["hwnd"])
    v.botao_da_caixa("Ver de perto", "X", espera=1.5)
    return r[0][-44:]
print("folhas com aviso:", v.s("dict(__import__('collections').Counter(a for f in tc.projeto.folhas for a in f.alertas_pendentes))"), v.s("tc.projeto.pendentes_de_revisao()"))
print("perto (85):", perto("30b-camoes-27-perto-forca-85"))
v.clicar("Desfazer", classe="QPushButton", espera=2)
print("Desfazer:"); v.passo("30c-camoes-27-desfazer", 120); time.sleep(5); v.passo("30c-camoes-27-desfazer")
print("  faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"), v.historico())
print("perto (50):", perto("30d-camoes-27-perto-forca-50"))
v.ctrl_z(); time.sleep(2)
print("Ctrl+Z:"); v.passo("30e-camoes-27-ctrlz", 120); print("  faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"), v.historico())
print("fui para", v.ir_pagina(66)); v.passo("31a-camoes-66", 180); print("  faixa:", v.faixa())
print("fui para", v.ir_pagina(104)); v.passo("31b-camoes-104", 180); print("  faixa:", v.faixa())
print("fui para", v.ir_pagina(11)); v.passo("31c-camoes-11", 180)
print("faixa na beirada medida:", v.s("[(p.indice+1, p.faixa_na_beirada) for p in tc.projeto.paginas if p.faixa_na_beirada is not None]"))
print("observacoes:", v.s("tc.projeto.observacoes")); print(v.contagem())
