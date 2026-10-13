import time, v
P = v.P
print(v.abrir())
print("abriu em", v.novo_livro(str(P.BASE / "trabalho" / "livros" / "antiphonal_44a49.pdf")), "s")
print(v.s("(len(tc.projeto.paginas), tc.projeto.ordem_do_preparo, tc.projeto.reforcar_texto_falhado, tc.projeto.misto_so_as_letras)"))
print("p1", v.esperar_medida(120), v.estado_da_pagina())
print("fui para", v.ir_pagina(3)); print("medida", v.esperar_medida(120)); print(v.estado_da_pagina())
print(v.foto("10a-pedaco-pagina3-aviso"))
print(v.s("[(p.indice+1, list(p.alertas_pendentes)) for p in tc.projeto.paginas]"))
print("erros.log:", repr(v.erros_log()[-600:]))
