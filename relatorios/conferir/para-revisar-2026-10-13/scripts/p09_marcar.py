import time, v
P = v.P
j = P.janela("Ver de perto")
# fecha o Ver de perto pelo botao X dele (clique nativo)
for it in j["itens"]:
    if it["classe"] == "QPushButton" and it["texto"] == "X":
        P.clicar_em(j["hwnd"], int(it["x"] + it["w"] / 2), int(it["y"] + it["h"] / 2)); break
time.sleep(1.5)
print("janelas:", [(x[1]) for x in P.janelas()])
v.aba("Marcar"); time.sleep(4)
print(v.foto("03d-antiphonal-46-aba-marcar"))
print(v.s("(tc._dpi_atual, tc.cartoes['preto_e_branco'].amostra._marcas, getattr(tc.editor_selecao, '_marcas_do_aviso', None))"))
v.aba("Filtro"); time.sleep(2)
