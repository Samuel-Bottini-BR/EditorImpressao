import time, v
P = v.P
t0 = time.time()
P.clicar_em(P.principal(), 700, 215)  # coordenada dentro da area "Arraste o PDF de um livro novo aqui"
time.sleep(4)
for i in range(120):
    its = v.itens()
    nomes = [x[2] for x in its if x[1] == "QPushButton"]
    if "Conferir" in nomes:
        break
    time.sleep(1)
print("tempo ate a tela O que fazer: %.0f s" % (time.time() - t0))
for linha in its:
    print(linha)
print(v.foto("01-o-que-fazer"))

