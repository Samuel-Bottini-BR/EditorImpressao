import time, v
P = v.P
v.clicar("fazer outro", classe="QPushButton", espera=2.5)
print(v.foto("11a-inicio-com-projetos"))
for linha in v.itens(classes=("QLabel", "QPushButton")): print(linha)
