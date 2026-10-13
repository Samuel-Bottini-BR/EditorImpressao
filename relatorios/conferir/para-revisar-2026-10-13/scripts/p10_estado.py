import time, v
P = v.P
print(v.estado_da_pagina())
print("medida pronta:", v.medida_pronta(), v.s("tc.previas.chave_da_medida(tc.indice_pagina)"))
print(v.s("[k for k in tc.previas._cache if ':medida:' in k]"))
print(v.s("(lambda p: (len(p.zonas) if hasattr(p,'zonas') else None, [ (z.tipo if hasattr(z,'tipo') else z) for z in getattr(p,'zonas',[])][:12]))(tc.projeto.paginas[45])"))
time.sleep(10)
print(v.estado_da_pagina())
print(v.foto("03e-antiphonal-46-filtro-depois-do-marcar"))
