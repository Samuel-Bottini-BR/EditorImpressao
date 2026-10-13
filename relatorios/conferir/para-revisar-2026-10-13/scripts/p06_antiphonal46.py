import time, v
P = v.P
v.aba("Filtro"); time.sleep(2)
print("pag 1:", v.estado_da_pagina())
t0 = time.time()
print("fui para:", v.ir_pagina(46))
print("medida em", v.esperar_medida(240), "s; total %.0f s" % (time.time() - t0))
print(v.estado_da_pagina())
print(v.foto("03-antiphonal-46-aviso"))
for linha in v.itens(classes=("QPushButton",)): print(linha)
for linha in v.itens(classes=("QLabel",)): print(linha)
