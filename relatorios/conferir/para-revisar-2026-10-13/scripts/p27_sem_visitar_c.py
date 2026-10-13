import time, v
P = v.P
print("livro B era:", v.s("(tc.projeto.nome, tc.projeto.caminho_entrada[-40:], tc.projeto.misto_so_as_letras, tc.projeto.reforcar_texto_falhado)"))
v.clicar("fazer outro", classe="QPushButton", espera=2.5)
print("abriu em", v.novo_livro(str(P.BASE / "trabalho" / "livros" / "antiphonal_44a49_c.pdf")), "s")
print("livro C:", v.s("(tc.projeto.nome, tc.projeto.caminho_entrada[-40:], tc.projeto.misto_so_as_letras, tc.projeto.reforcar_texto_falhado, tc.projeto.ordem_do_preparo)"))
print("p1 medida:", v.esperar_medida(60))
time.sleep(8)
print(v.s("[(p.indice+1, list(p.alertas_pendentes)) for p in tc.projeto.paginas]"), v.s("tc.botao_alertas.text()"))
print("medidas guardadas:", v.s("[k.split(':')[0] for k in tc.previas._cache if ':medida:' in k]"))
print(v.foto("12a-sem-visitar-pagina1-tudo-certo"))
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
print("janelas:", [x[1] for x in P.janelas()])
j = P.janela("Confirmar e processar")
print([it["texto"] for it in j["itens"]])
print(v.foto("12b-sem-visitar-confirmar", j["hwnd"]))
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "Processar":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
t0 = time.time(); time.sleep(1)
while time.time() - t0 < 300:
    extra = [jj for jj in P.mapa() if jj["classe"] != "JanelaPrincipal"]
    if extra:
        jj = extra[0]; print("caixa:", jj["titulo"])
        it = [i for i in jj["itens"] if i["classe"] == "QPushButton" and "(2)" in i["texto"] or i["classe"] == "QPushButton" and "(3)" in i["texto"]][0]
        P.clicar_em(jj["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); time.sleep(1); continue
    idx = v.s("type(jp.telas.currentWidget()).__name__")
    if "Final" in idx: break
    time.sleep(0.5)
print("tela final em %.0f s" % (time.time() - t0), idx)
time.sleep(1)
print(v.foto("12c-sem-visitar-ficou-pronto"))
print([x[2] for x in v.itens(classes=("QLabel",)) if x[5] > 0])
print("avisos depois do PDF:", v.s("[(p.indice+1, list(p.alertas), list(p.alertas_pendentes)) for p in tc.projeto.paginas]"))
print("erros.log:", repr(v.erros_log()[-1500:]))
