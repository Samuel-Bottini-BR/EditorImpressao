"""Projeto ANTIGO: cria um projeto no programa de hoje (fase-1, worktree velocidade-antes), fecha,
e abre o mesmo projeto no ramo fase2-para-revisar.  Uso: p52_projeto_antigo.py criar | abrir"""
import sys, time, v
P = v.P
PDF = str(P.BASE / "trabalho" / "livros" / "egenloff_1a14.pdf")
if sys.argv[1] == "criar":
    try:
        P.fechar()
    except Exception:
        pass
    print("codigo:", P.VERIF_RAIZ); print(v.abrir())
    print("abriu em", v.novo_livro(PDF), "s")
    for n in (3, 12, 2):
        v.ir_pagina(n); time.sleep(12)
        print(f"p{n}:", v.s("(lambda p: (list(p.alertas), p.forca_preto, p.revisada))(tc.projeto.paginas[tc.indice_pagina])"), v.s("tc.botao_alertas.text()"))
        print("   faixa:", v.faixa())
        v.foto(f"80a-antigo-no-fase1-p{n}")
    print("campos do projeto:", v.s("(hasattr(tc.projeto,'reforcar_texto_falhado'), tc.projeto.ordem_do_preparo, tc.projeto.misto_so_as_letras)"))
    print("avisos:", v.s("[(p.indice+1, list(p.alertas)) for p in tc.projeto.paginas if p.alertas]"))
    print("fechou:", P.fechar())
else:
    try:
        P.fechar()
    except Exception:
        pass
    print("codigo:", P.VERIF_RAIZ); print(v.abrir())
    print("reabriu em", v.continuar_projeto("1a14"), "s; pagina", v.s("tc.indice_pagina+1"))
    print("projeto:", v.s("(tc.projeto.reforcar_texto_falhado, tc.projeto.ordem_do_preparo, tc.projeto.misto_so_as_letras, tc.projeto.misto_fora_do_texto)"))
    print("avisos ao abrir:", v.s("[(p.indice+1, list(p.alertas), p.forca_preto) for p in tc.projeto.paginas if p.alertas]"))
    v.aba("Filtro"); time.sleep(2)
    print("  foto:", v.foto("80b-antigo-no-ramo-ao-abrir")[0][-40:], "|", v.contagem())
    for n in (3, 12):
        v.ir_pagina(n); t = v.esperar_medida(180); time.sleep(5)
        print(f"p{n}: medida {t} s |", v.curto()); print("   faixa:", v.faixa()); v.foto(f"80c-antigo-no-ramo-p{n}")
    print("erros.log:", repr(v.erros_log()[-600:]))
