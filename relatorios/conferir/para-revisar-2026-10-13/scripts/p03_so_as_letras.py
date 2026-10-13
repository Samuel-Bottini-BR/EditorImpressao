import time, v
P = v.P; g = v.g
v.clicar("Só as letras", classe="QCheckBox", espera=1.5)
P.arrastar_em(P.principal(), 924, 215, 924, 262); time.sleep(1.0)
for linha in v.itens(classes=("QCheckBox", "QRadioButton", "QComboBox")):
    print(linha)
for linha in v.itens("guardar"): print(linha)
for linha in v.itens("falhad"): print(linha)
print(v.foto("01-o-que-fazer-so-as-letras"))
