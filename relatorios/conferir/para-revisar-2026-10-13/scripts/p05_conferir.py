import time, v
P = v.P
t0 = time.time()
v.clicar("Conferir", classe="QPushButton", espera=2)
ok = v.esperar("jp.pilha.currentWidget() is jp.tela_conferir and tc._pronta()" if False else "tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=600, passo=2)
print("na tela de conferir:", ok, "em %.0f s" % (time.time() - t0))
time.sleep(3)
for linha in v.itens(classes=("QPushButton", "aba", "QCheckBox", "QComboBox", "QScrollBar")):
    print(linha)
print(v.s("(len(tc.projeto.folhas), len(tc.projeto.paginas), tc._abas_ativas, tc.projeto.ordem_do_preparo, tc.projeto.reforcar_texto_falhado, tc.projeto.misto_so_as_letras, tc.projeto.misto_fora_do_texto)"))
print(v.foto("02-conferir-antiphonal-p1"))
