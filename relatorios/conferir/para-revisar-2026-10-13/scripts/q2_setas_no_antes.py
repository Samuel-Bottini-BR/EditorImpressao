import time, v, runpy
P = v.P
print("codigo:", P.VERIF_RAIZ[-22:])
v.clicar("Só as letras", classe="QCheckBox", espera=1.5)
v.clicar("Conferir", classe="QPushButton", espera=2)
v.esperar("tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=300, passo=2); time.sleep(3)
v.aba("Filtro"); time.sleep(2)
runpy.run_path("q2_setas.py")
P.fechar()
