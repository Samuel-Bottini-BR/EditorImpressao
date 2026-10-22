"""Verificador, 22/10/2026: janela de verdade (codigo 49d1ed3), mensagens nativas do Windows, janela fora da
tela. Abre um livro NOVO, liga "Cortar seguindo o conteudo" e "Achar a pagina dentro da borda preta" (ate a
moldura, de fabrica) com cliques nativos, Original, confere, espera o programa parar, e tira o print das paginas
pedidas (com a lista de avisos de cada uma). Uso: python janela.py <pdf> <rotulo> <paginas 1-based, virgula>"""
import sys
import time

import v

P = v.P
pdf, rot, quais = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3].split(",")]
print("abrir", v.abrir(maximizada=True))
(P.CANAL / "resposta_abrir.txt").write_text(pdf, encoding="utf-8")
v.g.clicar_w("jp.tela_inicio.area", espera=2)
for _ in range(180):
    if any(x[2] == "Conferir" for x in v.itens(classes=("QPushButton",))):
        break
    time.sleep(1)
time.sleep(2)
if P.janela("Fundo separado"):
    v.g.responder("Não, deixar como está"); time.sleep(1)
q = ('(lambda d: [(sb.mapTo(jp, sb.rect().topLeft()).x()*d, sb.mapTo(jp, sb.rect().topLeft()).y()*d, sb.width()*d, sb.height()*d, '
     'sb.value(), sb.maximum(), sb.pageStep()) for sb in jp.findChildren(QtWidgets.QScrollBar) if sb.isVisible() and '
     'sb.orientation()==__import__("PySide6.QtCore").QtCore.Qt.Vertical])(jp.devicePixelRatioF())')
barras = eval(v.s(q))
if barras:
    x, y, w, h, val, mx, pg = barras[0]
    comp = max(h * pg / (mx + pg), 20)
    P.arrastar_em(P.principal(), int(x + w / 2), int(y + comp / 2), int(x + w / 2), int(y + h - comp / 2 - 2), passos=20)
    time.sleep(1.5)
for nome in ("Cortar seguindo o conteúdo", "Achar a página dentro"):
    it = [i for i in v.itens(classes=("QCheckBox",)) if i[2].startswith(nome)][0]
    if not it[4]:
        P.clicar_em(P.principal(), it[5] + 12, it[6] + it[8] // 2); time.sleep(1.5)
print("opcoes:", v.s("(jp.projeto.cortar_pelo_conteudo, jp.projeto.borda_preta, jp.projeto.borda_preta_ate, jp.projeto.borda_preta_fazer, jp.projeto.filtro_padrao)"))
print("frase:", [i[2] for i in v.itens(classes=("QLabel",)) if i[2] and i[2].startswith("Vou")])
print(v.foto(f"{rot}-o-que-fazer"))
t0 = time.time()
v.clicar("Conferir", classe="QPushButton", espera=2)
print("abriu conferir", v.esperar("tc.projeto is not None and tc._pronta() and tc.isVisible()", limite=1500, passo=2),
      round(time.time() - t0))
time.sleep(5)
print("ocioso", v.esperar_ocioso(1500), round(time.time() - t0))
print("avisos:", v.s("[(p.indice+1, list(p.alertas)) for p in tc.projeto.paginas if p.alertas]"))
EST = ("(lambda p: dict(pagina=tc.indice_pagina+1, alertas=list(p.alertas), "
       "pendentes=list(getattr(p, 'alertas_pendentes', [])), contador=tc.botao_alertas.text()))"
       "(tc.projeto.paginas[tc.indice_pagina])")
print("contador:", v.s("tc.botao_alertas.text()"))
print(v.foto(f"{rot}-depois-de-abrir"))
for n in quais:
    print("pagina", v.ir_pagina(n), "ocioso", v.esperar_ocioso(600))
    time.sleep(3)
    print(n, v.s(EST))
    print("  caixa do livro na janela:", v.s("(lambda pl, p: (lambda a: None if a is None else (tuple(round(x) for x in a[1]), a[0].medida.largura, a[0].medida.altura))(pl._caixa_do_livro(tc.projeto.folhas[p.folha], p, tc.projeto)))(__import__('core.pipeline').pipeline, tc.projeto.paginas[tc.indice_pagina])"))
    print(v.foto(f"{rot}-p{n:03d}"))
print("avisos no fim:", v.s("[(p.indice+1, list(p.alertas)) for p in tc.projeto.paginas if p.alertas]"))
print("contador no fim:", v.s("tc.botao_alertas.text()"))
print("erros.log:", repr(v.erros_log()[-400:]))
print(v.fechar())
