import time, v
P = v.P
FOCO = "(lambda w: (type(w).__name__, getattr(w,'text',lambda:'')() if hasattr(w,'text') else '', w.isVisible()) if w is not None else None)(jp.focusWidget())"
HIST = "[a.descricao for a in tc.acoes.feitas]"
ATIVAS = "(len(tc.projeto.paginas_ativas), tc.projeto.total_apagadas)"
print("0", v.s(ATIVAS), "foco:", v.s(FOCO))
v.clicar("Deixar em branco", classe="QPushButton", espera=2.5)
print("1 Deixar em branco:"); v.passo("21a-egenloff-12-deixar-em-branco")
print("  faixa:", v.faixa(), v.s(ATIVAS), "foco:", v.s(FOCO), v.s(HIST))
# teclado com o foco onde o clique deixou: Enter e depois Espaco (nativos)
P.tecla(0x0D); time.sleep(1.5)
print("2 depois do Enter:", v.curto(), v.s(HIST), "foco:", v.s(FOCO))
P.tecla("Z", mods=("ctrl",)); time.sleep(2); P.tecla("Z", mods=("ctrl",)); time.sleep(2)
print("3 depois de 2 Ctrl+Z:"); v.passo("21b-egenloff-12-ctrlz", 60); print("  ", v.s(HIST))
