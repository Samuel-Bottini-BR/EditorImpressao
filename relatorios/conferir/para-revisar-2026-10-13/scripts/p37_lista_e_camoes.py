import time, v
from livros import LIVROS
P = v.P
v.clicar("Confirmar e processar", classe="QPushButton", espera=3)
j = P.janela("Antes de processar")
print("Antes de processar:", [it["texto"] for it in j["itens"] if it["classe"] == "QLabel"][0], "| linhas:", len(v.linhas_da_lista()))
print("foto:", v.foto("25a-antes-de-processar-egenloff", j["hwnd"])[0][-42:])
P.u32.PostMessageW(j["hwnd"], 0x10, 0, 0); time.sleep(2)   # fecha no X
print("depois do X:", [c[0] for c in v.caixas()], v.s("type(jp.telas.currentWidget()).__name__"))
print("erros.log:", repr(v.erros_log()[-400:]))
print("fechou o programa:", P.fechar())
print(v.abrir())
print("Camoes abriu em", v.novo_livro(LIVROS["camoes"]), "s")
print(v.s("(tc.projeto.nome[:30], len(tc.projeto.paginas), tc.projeto.misto_so_as_letras, tc.projeto.reforcar_texto_falhado, tc.projeto.ordem_do_preparo, tc.indice_pagina+1)"))
print(v.contagem())
print("fui para", v.ir_pagina(27)); v.passo("30a-camoes-27-forca-sozinha", 180); time.sleep(8)
v.passo("30a-camoes-27-forca-sozinha"); print("  faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"))
