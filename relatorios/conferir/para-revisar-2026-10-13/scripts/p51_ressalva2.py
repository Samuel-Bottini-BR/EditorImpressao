import time, v
P = v.P
P.fechar(); print(v.abrir(True))
print("Antiphonal 1547 reabriu em", v.continuar_projeto("1547"), "s; pagina", v.s("tc.indice_pagina+1"), v.s("(tc.projeto.nome, len(tc.projeto.paginas), tc.projeto.reforcar_texto_falhado)"))
v.aba("Filtro"); time.sleep(2)
REGRA = "sorted((p.indice+1, a) for p in tc.projeto.paginas for a in p.alertas_pendentes if a not in ('contas_do_endireitar_discordam','em_branco'))"
print("avisos da regra ja no livro (so paginas visitadas):", v.s(REGRA))
v.ir_pagina(46); v.esperar_medida(120); time.sleep(4); print(v.curto())
print("foto maximizada:", v.foto("70a-antiphonal-46-aviso-maximizada")[0][-48:], v.s("(jp.width(), jp.height())"))
def lista(nome):
    v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
    j = P.janela("Antes de processar"); linhas = v.linhas_da_lista()
    print("  frase:", [it["texto"] for it in j["itens"] if it["classe"] == "QLabel"][0], "| linhas:", len(linhas))
    print("  motivos:", dict(__import__("collections").Counter(l.split("  -  ")[1] for l in linhas)))
    v.foto(nome + "-todos", j["hwnd"])
    print("  mostrar:", v.escolher_motivo_na_lista("Desenho apagado"), v.linhas_da_lista())
    j = P.janela("Antes de processar"); print("  foto:", v.foto(nome + "-desenho-apagado", j["hwnd"])[0][-52:])
    P.u32.PostMessageW(j["hwnd"], 0x10, 0, 0); time.sleep(2)
print("LISTA 1 (visitadas: 1 e 46):"); lista("70b-lista-poucas-visitadas")
for n in (76, 252, 6, 31):
    v.ir_pagina(n); t = v.esperar_medida(180); time.sleep(3); print(f"visitei {n}: medida {t} s |", v.curto())
print("LISTA 2 (visitadas: 1, 46, 76, 252, 6, 31):"); lista("70c-lista-mais-visitadas")
print("avisos da regra no livro agora:", v.s(REGRA))
print("erros.log:", repr(v.erros_log()[-300:]))
