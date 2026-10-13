import time, v
P = v.P
pass
print("Gladstone reabriu em", v.continuar_projeto("Gladstone"), "s; pagina", v.s("tc.indice_pagina+1"), v.s("tc.barra_abas.tabText(tc.barra_abas.currentIndex())"))
v.aba("Filtro"); time.sleep(2)
v.ir_pagina(18); time.sleep(3); print(v.curto())
v.g.clicar_w("tc.botoes_de_sugestao['filtro']", espera=2.5)     # "está bom assim" do aviso do endireitar
print("depois de dar 'está bom' no 1o aviso:", v.curto()); print("  faixa:", v.faixa())
print("  foto:", v.foto("50-gladstone-p18-parece-em-branco")[0][-44:])
v.ctrl_z()
print("as outras 'Parece em branco' do livro:", v.s("[p.indice+1 for p in tc.projeto.paginas if 'em_branco' in p.alertas]"))

