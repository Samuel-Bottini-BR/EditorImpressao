"""20/10/2026 (retomada da segunda conferencia): reabre NA JANELA, com o codigo do ramo (ce2b835),
as quatro paginas que a segunda conferencia nao tinha reaberto: Opus Majus 20, Cursus 3, Camoes 66
e Antiphon 260. Livro NOVO, pasta de dados nova (rodar com VERIF_DADOS=...trabalho/dados_teste3).
So le o estado e tira print; os cliques sao nativos (piloto.py), a janela fica fora da tela.

Uso: python r3_quatro_paginas.py opus|cursus|camoes|antiphon
Prints com o prefixo r3- em trabalho/prints."""
import sys
import time
from pathlib import Path

import v
from livros import LIVROS

P = v.P
GAB = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
PEDIDO = {
    "opus": (GAB / "opusmajus_p020.pdf", 1, ()),
    "cursus": (LIVROS["cursus"], 3, ()),
    "camoes": (LIVROS["camoes"], 66, (65, 67, 27, 104)),
    # Antiphon 260: na 1a conferencia o aviso da faixa virou aviso do livro depois de visitar mais 3 paginas
    "antiphon": (LIVROS["antiphon"], 260, (259, 261, 262)),
}


def estado(rotulo, nome):
    print(f"  [{rotulo}]", v.curto())
    print("    faixa:", v.faixa())
    try:
        print("    painel:", [x if isinstance(x, str) else x[0] for x in v.painel()][:12])
    except Exception as e:  # noqa: BLE001 - painel pode nao existir
        print("    painel: (nao li)", repr(e)[:80])
    print("    foto:", Path(v.foto(nome)[0]).name)


qual = sys.argv[1]
pdf, pagina, outras = PEDIDO[qual]
print("codigo:", P.VERIF_RAIZ[-24:], "| dados:", P.DADOS.name, "| livro:", Path(pdf).name)
v.fechar()
v.abrir()
print("abriu como livro novo em", v.novo_livro(str(pdf)), "s")
v.ir_pagina(pagina)
print("  medida da pagina", pagina, "em", v.esperar_medida(300), "s")
time.sleep(4)
estado(f"p{pagina}, primeira visita", f"r3-{qual}-p{pagina}-tela")
for o in outras:
    v.ir_pagina(o)
    print("  medida da pagina", o, "em", v.esperar_medida(300), "s |", v.curto())
if outras:
    v.ir_pagina(pagina)
    time.sleep(5)
    estado(f"p{pagina}, de volta depois de {list(outras)}", f"r3-{qual}-p{pagina}-depois-tela")
print("erros.log:", v.erros_log())
v.fechar()
