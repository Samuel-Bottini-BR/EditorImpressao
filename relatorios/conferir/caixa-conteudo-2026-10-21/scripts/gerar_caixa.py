"""Verificador, 21/10: abre o Egenloff 1-14 como livro novo, liga as opcoes do corte pedidas (cliques nativos na tela
"O que fazer"), confere, processa ate "Ficou pronto!" e devolve o caminho do PDF. Uso: python gerar_caixa.py <as_duas: 0|1>"""
import sys
import time

import n
import v

P = v.P
as_duas = sys.argv[1] == "1"
L = P.BASE / "trabalho" / "livros" / "egenloff_1a14.pdf"
(P.CANAL / "resposta_abrir.txt").write_text(str(L), encoding="utf-8")
v.g.clicar_w("jp.tela_inicio.area", espera=2)
for _ in range(120):
    if any(x[2] == "Conferir" for x in v.itens(classes=("QPushButton",))):
        break
    time.sleep(1)
time.sleep(2)
if P.janela("Fundo separado"):
    v.g.responder("Não, deixar como está"); time.sleep(1)
q = ('(lambda d: [(sb.mapTo(jp, sb.rect().topLeft()).x()*d, sb.mapTo(jp, sb.rect().topLeft()).y()*d, sb.width()*d, sb.height()*d, '
     'sb.value(), sb.maximum(), sb.pageStep()) for sb in jp.findChildren(QtWidgets.QScrollBar) if sb.isVisible() and '
     'sb.orientation()==__import__("PySide6.QtCore").QtCore.Qt.Vertical])(jp.devicePixelRatioF())')
x, y, w, h, val, mx, pg = eval(v.s(q))[0]
comp = max(h * pg / (mx + pg), 20)
P.arrastar_em(P.principal(), int(x + w / 2), int(y + comp / 2), int(x + w / 2), int(y + h - comp / 2 - 2), passos=20)
time.sleep(1.5)
nomes = ["Cortar seguindo o conteúdo"] + (["Achar a página dentro"] if as_duas else [])
for nome in nomes:
    it = [i for i in v.itens(classes=("QCheckBox",)) if i[2].startswith(nome)][0]
    P.clicar_em(P.principal(), it[5] + 12, it[6] + it[8] // 2); time.sleep(1.5)
print("opcoes:", v.s("(jp.projeto.cortar_pelo_conteudo, jp.projeto.borda_preta, jp.projeto.borda_preta_ate)"))
print("frase:", [i[2] for i in v.itens(classes=("QLabel",)) if i[2] and i[2].startswith("Vou")])
print(v.foto("X-o-que-fazer-" + ("duas" if as_duas else "so25")))
v.clicar("Conferir", classe="QPushButton", espera=2)
v.esperar("tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=900, passo=2)
time.sleep(5)
print("ocioso", v.esperar_ocioso(900))
print("avisos:", v.s("[(p.indice+1, list(p.alertas)) for p in tc.projeto.paginas if p.alertas]"))
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
for _ in range(3):
    c = v.caixas()
    if not c or c[0][0] == "Confirmar e processar":
        break
    for b in ("continuar assim mesmo", "processar assim mesmo"):
        if b in c[0][1]:
            v.botao_da_caixa(c[0][0], b, espera=3)
v.botao_da_caixa("Confirmar e processar", "Processar", espera=2)
t0 = time.time()
while time.time() - t0 < 1200 and "Final" not in v.s("type(jp.telas.currentWidget()).__name__"):
    time.sleep(2)
print("processou em", round(time.time() - t0), v.s("type(jp.telas.currentWidget()).__name__"), "erros.log:", repr(v.erros_log()[-300:]))
print(v.fechar())
