import time, v
P = v.P; g = v.g
print("caixa:", g.responder("Não, deixar como está"))
time.sleep(1)
v.clicar("Preto e branco", classe="QRadioButton", espera=1.5)
for linha in v.itens(classes=("QCheckBox", "QRadioButton", "QComboBox", "QPushButton")):
    print(linha)
print(v.foto("01-o-que-fazer-pb"))
