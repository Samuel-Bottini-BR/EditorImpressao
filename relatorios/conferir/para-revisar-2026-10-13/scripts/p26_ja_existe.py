import time, v
P = v.P
for jj in P.mapa():
    if jj["classe"] != "JanelaPrincipal":
        print("JANELA", repr(jj["titulo"]), jj["classe"], [(it["classe"], it["texto"]) for it in jj["itens"]])
        print(v.foto("11e-ja-existe", jj["hwnd"]))
        alvo = [it for it in jj["itens"] if it["classe"] == "QPushButton" and "(2)" in it["texto"]] or \
               [it for it in jj["itens"] if it["classe"] == "QPushButton" and "salvar como" in it["texto"].lower()]
        it = alvo[0]
        P.clicar_em(jj["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2))
        break
t0 = time.time()
while time.time() - t0 < 300:
    idx = v.s("type(jp.telas.currentWidget()).__name__")
    if "Final" in idx: break
    time.sleep(0.5)
print("tela final em %.0f s" % (time.time() - t0), idx)
time.sleep(1)
print(v.foto("11d-sem-visitar-ficou-pronto"))
print([x[2] for x in v.itens(classes=("QLabel",)) if x[5] > 0])
print("avisos depois do PDF:", v.s("[(p.indice+1, list(p.alertas), list(p.alertas_pendentes)) for p in tc.projeto.paginas]"))
print("erros.log:", repr(v.erros_log()[-1500:]))
