"""20/10/2026: o Opus Majus 20 sai com a foto inteira no PDF? (codigo ce2b835, janela de verdade)
Reabre o projeto feito pelo r3_quatro_paginas.py (pasta dados_teste3), processa ate "Ficou pronto!"
com "continuar assim mesmo" e guarda a pagina do PDF em trabalho/desenhos/r3-opus-pdf.png.
Rodar com VERIF_DADOS=...trabalho/dados_teste3. So cliques nativos; nao muda o programa."""
import time

import fitz

import v

P = v.P
v.fechar()
v.abrir()
print("reabriu o Opus Majus 20 em", v.continuar_projeto("opusmajus"), "s")
v.aba("Filtro"); time.sleep(2)
v.esperar_medida(120); v.esperar_ocioso(120)
print(v.curto())
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
if P.janela("Antes de processar"):
    print("lista:", v.linhas_da_lista())
    v.botao_da_caixa("Antes de processar", "continuar assim mesmo", espera=3)
v.botao_da_caixa("Confirmar e processar", "Processar", espera=1)
t0 = time.time()
while time.time() - t0 < 300:
    if v.caixas():
        print("caixa:", v.caixas()[0][0]); v.botao_da_caixa("", "salvar como", parte=True); continue
    if "Final" in v.s("type(jp.telas.currentWidget()).__name__"):
        break
    time.sleep(0.5)
print("tela final em", round(time.time() - t0), "s")
v.foto("r3-opus-ficou-pronto")
pasta = P.DADOS / "home" / "Editor de Impressão"
pdf = sorted(pasta.glob("*.pdf"), key=lambda p: p.stat().st_mtime)[-1]
d = fitz.open(pdf)
pix = d[0].get_pixmap(dpi=150)
destino = P.BASE / "trabalho" / "desenhos" / "r3-opus-pdf.png"
pix.save(destino)
print("PDF:", pdf.name, len(d), "pagina(s) ->", destino.name, pix.width, pix.height)
print("erros.log:", repr(v.erros_log()[-200:]))
v.fechar()
