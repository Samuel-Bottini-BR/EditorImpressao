import time, v
P = v.P
print("abriu em", v.novo_livro(str(P.BASE / "trabalho" / "livros" / "antiphonal_44a49_sem_visitar.pdf")), "s")
print("p1 medida:", v.esperar_medida(60))
print(v.s("[(p.indice+1, list(p.alertas_pendentes)) for p in tc.projeto.paginas]"), v.s("tc.botao_alertas.text()"))
print(v.foto("11b-sem-visitar-pagina1-tudo-certo"))
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
print("janelas:", [x[1] for x in P.janelas()])
j = P.janela("Confirmar e processar")
print([it["texto"] for it in j["itens"]])
print(v.foto("11c-sem-visitar-confirmar", j["hwnd"]))
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "Processar":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
t0 = time.time()
while time.time() - t0 < 600:
    idx = v.s("type(jp.telas.currentWidget()).__name__")
    if "Final" in idx: break
    time.sleep(0.5)
print("tela final em %.0f s" % (time.time() - t0), idx)
time.sleep(1)
print(v.foto("11d-sem-visitar-ficou-pronto"))
print([x[2] for x in v.itens(classes=("QLabel",)) if x[5] > 0])
print("avisos depois do PDF:", v.s("[(p.indice+1, list(p.alertas), list(p.alertas_pendentes)) for p in tc.projeto.paginas]"))
print("erros.log:", repr(v.erros_log()[-1500:]))
