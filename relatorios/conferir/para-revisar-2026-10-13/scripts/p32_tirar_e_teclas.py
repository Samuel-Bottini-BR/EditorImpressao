import time, v
P = v.P
FOCO = "(lambda w: (type(w).__name__, w.text() if hasattr(w,'text') else '', w.isVisible()) if w is not None else None)(jp.focusWidget())"
HIST = "[a.descricao for a in tc.acoes.feitas]"
ATIVAS = "(len(tc.projeto.paginas_ativas), tc.projeto.total_apagadas)"
v.clicar("Tirar do livro", classe="QPushButton", espera=2.5)
print("1 Tirar do livro:"); v.passo("21c-egenloff-12-tirar-do-livro")
print("  faixa:", v.faixa(), v.s(ATIVAS), "foco:", v.s(FOCO), v.s(HIST))
P.tecla(0x20); time.sleep(2)   # Espaco, com o foco onde o clique deixou
print("2 depois do Espaco:", v.curto(), v.s(ATIVAS), v.s(HIST), "foco:", v.s(FOCO))
# volta tudo
for _ in range(4):
    if v.s(HIST) == "[]": break
    P.tecla("Z", mods=("ctrl",)); time.sleep(1.5)
v.ir_pagina(12); time.sleep(1)
print("3 de volta:", v.curto(), v.s(ATIVAS), v.s(HIST))
# foco num botao do aviso, depois uma pagina SEM aviso (os botoes ficam escondidos), e as teclas
v.clicar("Deixar em branco", classe="QPushButton", espera=2)
print("4 foco depois do Deixar em branco:", v.s(FOCO))
v.ir_pagina(11); time.sleep(2)
print("5 na pagina 11 (sem aviso):", v.curto(), "foco:", v.s(FOCO), "b1 visivel:", v.s("(tc.botoes_de_sugestao['filtro'].isVisible(), tc.botoes_de_sugestao_2['filtro'].isVisible(), tc.botoes_de_sugestao['filtro'].hasFocus(), tc.botoes_de_sugestao_2['filtro'].hasFocus())"))
for nome, vk in (("Enter", 0x0D), ("Espaco", 0x20)):
    antes = v.s(HIST)
    P.tecla(vk); time.sleep(2)
    print("6 tecla", nome, "->", v.curto(), "| novo no historico:", v.s(HIST)[len(antes) - 1:], "foco:", v.s(FOCO))
print(v.s("[(p.indice+1, p.em_branco, p.apagada, p.revisada) for p in tc.projeto.paginas[9:13]]"), v.s(ATIVAS))
v.passo("21d-egenloff-teclas-com-botoes-escondidos")
