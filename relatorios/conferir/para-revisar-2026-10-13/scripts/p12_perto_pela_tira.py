import time, v
P = v.P
x, y, vis, ativo = v.g.geo("tc.tira._miniaturas[45]")
P.clicar_em(P.principal(), int(x), int(y), duplo=True); time.sleep(4)
print([x[1] for x in P.janelas()])
print(v.s("[a.descricao for a in tc.acoes.feitas]"))
print(v.estado_da_pagina())
print(v.foto_da_caixa("03g-antiphonal-46-ver-de-perto-com-aviso", "Ver de perto"))
