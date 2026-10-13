import time, v
P = v.P
j = P.janela("Ver de perto")
if j:
    for it in j["itens"]:
        if it["classe"] == "QPushButton" and it["texto"] == "X":
            P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
    time.sleep(1.5)
print("1 antes:", v.estado_da_pagina())
print(v.foto("04a-antiphonal-46-antes"))
v.clicar("Trazer de volta nesta página", classe="QPushButton", espera=2)
t = v.esperar_medida(120)
time.sleep(3)
print("2 depois do Trazer de volta (medida %s s):" % t, v.estado_da_pagina())
print(v.s("[a.descricao for a in tc.acoes.feitas]"))
print(v.foto("04b-antiphonal-46-depois-do-trazer-de-volta"))
P.tecla("Z", mods=("ctrl",)); time.sleep(2)
t = v.esperar_medida(120); time.sleep(3)
print("3 depois do Ctrl+Z:", v.estado_da_pagina())
print(v.foto("04c-antiphonal-46-ctrlz"))
v.clicar("está bom assim", classe="QPushButton", espera=2)
print("4 depois do 'está bom assim':", v.estado_da_pagina())
print(v.s("[a.descricao for a in tc.acoes.feitas]"))
print(v.foto("04d-antiphonal-46-esta-bom-assim"))
P.tecla("Z", mods=("ctrl",)); time.sleep(2)
print("5 depois do Ctrl+Z:", v.estado_da_pagina())
print(v.foto("04e-antiphonal-46-ctrlz-do-esta-bom"))
