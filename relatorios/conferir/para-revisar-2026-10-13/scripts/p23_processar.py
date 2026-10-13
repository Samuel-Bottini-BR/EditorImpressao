import time, v
P = v.P
j = P.janela("Confirmar e processar")
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "Processar":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
t0 = time.time()
time.sleep(1.5)
print("logo depois:", [x[1] for x in P.janelas()], v.s("jp.telas.currentIndex()"))
print(v.foto("10e-processando"))
ultimo = None
while time.time() - t0 < 900:
    idx = v.s("(jp.telas.currentIndex(), type(jp.telas.currentWidget()).__name__)")
    if idx != ultimo:
        print("%.0f s" % (time.time() - t0), idx); ultimo = idx
    if "Final" in idx:
        break
    extra = [x[1] for x in P.janelas() if x[1] != "Editor de Impressão"]
    if extra:
        print("janela extra:", extra); break
    time.sleep(1)
print("tempo ate a tela final: %.0f s" % (time.time() - t0))
time.sleep(1.5)
print(v.foto("10f-ficou-pronto"))
for linha in v.itens(classes=("QLabel", "QPushButton")):
    if linha[5] > -1000: print(linha)
print("erros.log:", repr(v.erros_log()[-1500:]))
