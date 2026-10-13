import time, v
P = v.P
print("Graduale 222 em 'Guardar a tinta forte' (de fabrica): sem aviso ->", v.curto())
v.foto("40a-graduale-222-tinta-forte-sem-aviso")
for n in (3, 5):
    v.ir_pagina(n); print(" vizinha:", end=""); v.passo(f"40x-graduale-pagina{n}", 240)
v.ir_pagina(4); time.sleep(2)
v.clicar("Guardar só o texto", classe="QPushButton", espera=3)
print("Guardar so o texto na pagina 4:"); v.passo("40b-graduale-222-so-o-texto", 240); time.sleep(5); v.passo("40b-graduale-222-so-o-texto")
print("  faixa:", v.faixa()); print("  marcas:", v.s("len(tc.cartoes['preto_e_branco'].amostra._marcas)"), v.historico())
v.clicar("Trazer de volta nesta página", classe="QPushButton", espera=3)
print("Trazer de volta:"); v.passo("40c-graduale-222-trazer-de-volta", 240); time.sleep(4); v.passo("40c-graduale-222-trazer-de-volta")
print("  faixa:", v.faixa(), v.historico()); print("  jeito por pagina:", v.s("[(p.indice+1, p.misto_fora_do_texto) for p in tc.projeto.paginas]"), v.s("tc.projeto.misto_fora_do_texto"))
v.ctrl_z(); time.sleep(2); print("Ctrl+Z:"); v.passo("40d-graduale-222-ctrlz", 240)
print(v.contagem())
