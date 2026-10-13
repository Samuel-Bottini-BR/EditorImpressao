import time, v
P = v.P
FOCO = "(lambda w: (type(w).__name__, (w.text() if hasattr(w,'text') else '')[:28], w.isVisible()) if w is not None else None)(jp.focusWidget())"
HIST = "[a.descricao for a in tc.acoes.feitas]"
for _ in range(4):
    if v.s(HIST) == "[]": break
    P.tecla("Z", mods=("ctrl",)); time.sleep(1.5)
v.ir_pagina(11); time.sleep(1.5)
print("T1: pagina 11, sem aviso; foco:", v.s(FOCO))
vistos = []
for i in range(45):
    P.tecla(0x09); time.sleep(0.35)
    vistos.append((v.s(FOCO), v.s("tc.indice_pagina+1")))
escondidos = [x for x in vistos if "False" in x[0]]
print("  focos por Tab:", sorted(set(x[0] for x in vistos)))
print("  paginas por onde passou:", sorted(set(x[1] for x in vistos), key=int))
print("  algum foco em widget escondido?", escondidos[:5])
print("  historico:", v.s(HIST))
v.ir_pagina(12); time.sleep(2)
print("T2:", v.curto())
v.clicar("Deixar em branco", classe="QPushButton", espera=2)
print("  foco:", v.s(FOCO))
P.tecla(0x27); time.sleep(1.5)   # seta para a direita
print("  depois da seta direita: pagina", v.s("tc.indice_pagina+1"), "foco:", v.s(FOCO))
P.tecla(0x20); time.sleep(2)     # espaco
print("  depois do espaco:", v.curto(), "foco:", v.s(FOCO)); print("  historico:", v.s(HIST))
print("  janelas:", [x[1] for x in P.janelas()])
