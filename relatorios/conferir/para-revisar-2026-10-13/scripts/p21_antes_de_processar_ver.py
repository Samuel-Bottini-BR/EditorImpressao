import time, v
P = v.P
v.ir_pagina(1); time.sleep(1)
v.clicar("Confirmar e processar", classe="QPushButton", espera=2.5)
print([ (x[1], x[3]) for x in P.janelas()])
j = P.janela("Antes de processar")
print("itens:", [(it["classe"], it["texto"]) for it in j["itens"]])
print("linhas:", v.s("[w for w in QtWidgets.QApplication.topLevelWidgets() if type(w).__name__=='JanelaDosAvisos'][0].linhas()"))
print(v.foto_da_caixa("10b-antes-de-processar-lista", "Antes de processar"))
# "ver"
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "ver":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
time.sleep(2.5)
print("depois do ver:", [x[1] for x in P.janelas()], v.s("(tc.indice_pagina+1, jp.telas.currentIndex())"))
print(v.foto("10c-depois-do-ver-pagina3"))
