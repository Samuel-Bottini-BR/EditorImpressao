import time, v
P = v.P
v.clicar("Confirmar e processar", classe="QPushButton", espera=2.5)
j = P.janela("Antes de processar")
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "continuar assim mesmo":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
time.sleep(3)
print([(x[1], x[3]) for x in P.janelas()])
for jj in P.mapa():
    if jj["classe"] != "JanelaPrincipal":
        print("JANELA", jj["titulo"], jj["classe"])
        for it in jj["itens"]:
            print("  ", it["classe"], repr(it["texto"][:100]), it.get("ativo"), it.get("marcado"), int(it["x"]), int(it["y"]), int(it["w"]), int(it["h"]))
        print(v.foto("10d-janela-confirmar", jj["hwnd"]))
