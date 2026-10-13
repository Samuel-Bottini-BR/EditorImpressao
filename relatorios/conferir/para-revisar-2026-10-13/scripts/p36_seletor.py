import time, v
P = v.P
JA = "[w for w in QtWidgets.QApplication.topLevelWidgets() if type(w).__name__=='JanelaDosAvisos' and w.isVisible()][0]"
def linha_xy(i):
    return eval(v.s(f"(lambda ja, d: (lambda r: ((ja.lista.viewport().mapTo(ja, r.topLeft()).x() + 14)*d, (ja.lista.viewport().mapTo(ja, r.center()).y())*d))(ja.lista.visualItemRect(ja.lista.item({i}))))({JA}, jp.devicePixelRatioF())"))
v.clicar_no_painel("ver a lista…")
j = P.janela("Para revisar")
linhas = v.linhas_da_lista()
print("lista: %d linhas; primeiras:" % len(linhas), linhas[:4], "... ultimas:", linhas[-6:])
print("combo:", v.s(f"[{JA}.combo_motivo.itemText(i) for i in range({JA}.combo_motivo.count())]"))
print("foto:", v.foto("24a-seletor-para-revisar", j["hwnd"])[0][-36:])
# marca duas linhas (cliques nativos na caixinha): a da pagina 3 'Texto falhado' e a da pagina 12
alvos = [i for i, t in enumerate(linhas) if t.startswith("Página 3 ") and "Texto falhado" in t] + [i for i, t in enumerate(linhas) if t.startswith("Página 12 ") and "sem conte" in t]
print("alvos:", alvos, [linhas[i] for i in alvos])
for i in alvos:
    v.s(f"{JA}.lista.scrollToItem({JA}.lista.item({i}))") if False else None
    x, y = linha_xy(i)
    P.clicar_em(j["hwnd"], int(x), int(y)); time.sleep(0.8)
print("marcadas:", v.s(f"[a.onde + ' - ' + a.titulo for a in {JA}.avisos_marcados()]"))
print("foto:", v.foto("24b-seletor-duas-marcadas", j["hwnd"])[0][-36:])
v.botao_da_caixa("Para revisar", "está bom nas marcadas", espera=2.5)
print("depois:", v.contagem()); print("hist:", v.historico())
print("caixas abertas:", [c[0] for c in v.caixas()], "linhas agora:", len(v.linhas_da_lista()))
j = P.janela("Para revisar"); print("foto:", v.foto("24c-seletor-depois-do-esta-bom", j["hwnd"])[0][-40:])
v.botao_da_caixa("Para revisar", "fechar", espera=2)
print("fechou:", [c[0] for c in v.caixas()])
v.ctrl_z(); print("Ctrl+Z:", v.contagem(), v.historico())
