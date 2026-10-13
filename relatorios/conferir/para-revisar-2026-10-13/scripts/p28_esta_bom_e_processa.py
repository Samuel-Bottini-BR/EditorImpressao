import time, v
P = v.P
def botao(j, texto, parte=False):
    for it in j["itens"]:
        if it["classe"] == "QPushButton" and (texto in it["texto"] if parte else it["texto"] == texto):
            P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); return True
    return False
j = P.janela("Antes de processar")
botao(j, "Selecionar todas"); time.sleep(1)
print(v.foto("12d-antes-de-processar-marcadas", j["hwnd"]))
botao(j, "está bom nas marcadas"); time.sleep(3)
print("janelas:", [x[1] for x in P.janelas()])
print("avisos:", v.s("[(p.indice+1, list(p.alertas), list(p.alertas_pendentes), list(p.alertas_aceitos), p.revisada) for p in tc.projeto.paginas if p.alertas]"))
print("historico:", v.s("[a.descricao for a in tc.acoes.feitas]"))
j = P.janela("Confirmar e processar")
print([it["texto"] for it in j["itens"]])
print(v.foto("12e-confirmar-depois-do-esta-bom", j["hwnd"]))
botao(j, "Processar")
t0 = time.time(); time.sleep(1)
while time.time() - t0 < 300:
    extra = [jj for jj in P.mapa() if jj["classe"] != "JanelaPrincipal"]
    if extra:
        jj = extra[0]; print("caixa:", jj["titulo"], [i["texto"] for i in jj["itens"] if i["classe"] == "QPushButton"])
        botao(jj, "salvar como", parte=True); time.sleep(1); continue
    idx = v.s("type(jp.telas.currentWidget()).__name__")
    if "Final" in idx: break
    time.sleep(0.5)
print("tela final em %.0f s" % (time.time() - t0), idx)
time.sleep(1)
print(v.foto("12f-ficou-pronto"))
print([x[2] for x in v.itens(classes=("QLabel",)) if x[5] > 0])
print("erros.log:", repr(v.erros_log()[-1500:]))
