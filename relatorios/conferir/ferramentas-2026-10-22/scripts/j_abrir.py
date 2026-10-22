"""Verificador 22/10: abre um livro novo como a pessoa (clique nativo na área, a caixa Abrir responde o PDF)."""
import sys, time
import v
P = v.P
(P.CANAL / "resposta_abrir.txt").write_text(sys.argv[1], encoding="utf-8")
v.g.clicar_w("jp.tela_inicio.area", espera=2)
for _ in range(180):
    if any(x[2] == "Conferir" for x in v.itens(classes=("QPushButton",))):
        break
    time.sleep(1)
time.sleep(2)
if P.janela("Fundo separado"):
    v.g.responder("Não, deixar como está"); time.sleep(1)
print(v.foto(sys.argv[2]))
print([i[2] for i in v.itens(classes=("QCheckBox", "QLabel", "QPushButton", "QComboBox")) if i[2]][:80])
