"""SEGUNDA CONFERENCIA (ramo em ce2b835): os consertos 1, 2, 3, 4, 6, 7 e 8 na janela de verdade.
Pasta de dados NOVA (trabalho/dados_teste2): todo livro aqui e livro novo.
Uso: q1_consertos.py <parte>   parte = graduale | antiphonal | egenloff | avulsas
Prints com o prefixo r2- em trabalho/prints."""
import sys, time, v
P = v.P
L = P.BASE / "trabalho" / "livros"
PAG = __import__("pathlib").Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
GAB = __import__("pathlib").Path(r"D:\programas\EditorImpressao\gabarito\paginas")
FOCO = "(lambda w: (type(w).__name__, (w.text() if hasattr(w,'text') else '')[:26]) if w is not None else None)(jp.focusWidget())"


def reabrir(pdf, **k):
    v.fechar()
    v.abrir()
    return v.novo_livro(str(pdf), **k)


def rotulo_marcado():
    return [x[2] for x in v.itens("Marcado:")][:1]


parte = sys.argv[1]
if parte == "graduale":
    # ponto 8 primeiro (pagina nunca acertada): aba Marcar, antes e depois, e o tempo
    print("Graduale 219-225 abriu em", reabrir(L / "graduale_219a225.pdf"), "s")
    v.aba("Marcar"); time.sleep(1)
    t0 = time.time(); v.ir_pagina(3, espera=0.3)
    while time.time() - t0 < 60:                       # espera a previa (a marcacao provisoria) aparecer
        if eval(v.marcado())[0] > 0:
            break
        time.sleep(0.2)
    t_prev = time.time() - t0
    print("p3 (Graduale 221) na aba Marcar: provisoria em %.1f s:" % t_prev, v.marcado(), rotulo_marcado())
    print("  foto:", v.foto("r2-marcar-1-antes")[0][-34:])
    while time.time() - t0 < 180:
        if eval(v.marcado())[2] is False:
            break
        time.sleep(0.25)
    t_def = time.time() - t0
    time.sleep(2.5)
    print("  acertou sozinha %.1f s depois de chegar (%.1f s depois da provisoria):" % (t_def, t_def - t_prev), v.marcado(), rotulo_marcado())
    print("  foto:", v.foto("r2-marcar-2-depois")[0][-34:])
    # area marcada a mao no intervalo: pagina 5, arrasto nativo logo que a provisoria aparece
    t0 = time.time(); v.ir_pagina(5, espera=0.3)
    while time.time() - t0 < 60:
        if eval(v.marcado())[0] > 0:
            break
        time.sleep(0.2)
    antes = v.marcado()
    x, y, vis, ativo = v.g.geo("tc.editor_selecao")
    P.arrastar_em(P.principal(), int(x) - 60, int(y) + 40, int(x) + 60, int(y) + 130, passos=10); time.sleep(0.8)
    com_mao = v.marcado(); t_mao = time.time() - t0
    print("p5: provisoria:", antes, "| depois do meu retangulo (%.1f s):" % t_mao, com_mao, "| historico:", v.historico())
    v.foto("r2-marcar-3-a-mao-antes")
    while time.time() - t0 < 180:
        if eval(v.marcado())[2] is False:
            break
        time.sleep(0.25)
    time.sleep(2.5)
    print("  depois de acertar sozinha (%.1f s):" % (time.time() - t0), v.marcado(), rotulo_marcado())
    print("  foto:", v.foto("r2-marcar-4-a-mao-depois")[0][-40:])
    # ponto 1: Graduale 221 na aba Filtro, com tudo medido
    v.aba("Filtro"); time.sleep(1); v.ir_pagina(3); print("  medida:", v.esperar_medida(120), "ocioso:", v.esperar_ocioso(120))
    print("PONTO 1, Graduale 221 (p3):", v.curto()); print("  faixa:", v.faixa())
    print("  foto:", v.foto("r2-graduale-221")[0][-30:])
    for n in (1, 2, 4):
        v.ir_pagina(n); v.esperar_medida(120); v.esperar_ocioso(120); print("  ", v.curto())
    print("erros.log:", repr(v.erros_log()[-300:]))
elif parte == "antiphonal":
    print("Antiphonal 44-49 abriu em", reabrir(L / "antiphonal_44a49.pdf"), "s")
    v.ir_pagina(3); print("medida:", v.esperar_medida(120), v.esperar_ocioso(120)); print(v.curto())
    # ponto 2: dois cliques no cartao do Preto e branco
    x, y, vis, ativo = v.g.geo("tc.cartoes['preto_e_branco']")
    P.clicar_em(P.principal(), int(x), int(y) - 40, duplo=True); time.sleep(4)
    print("PONTO 2, depois do duplo clique no cartao: janelas", [j[1] for j in P.janelas()], "| historico:", v.historico())
    print("  ", v.curto())
    j = P.janela("Ver de perto")
    if j:
        print("  foto:", v.foto("r2-duplo-clique-ver-de-perto", j["hwnd"])[0][-44:]); v.botao_da_caixa("Ver de perto", "X")
    print("  foto:", v.foto("r2-duplo-clique-aviso-continua")[0][-46:])
    print("erros.log:", repr(v.erros_log()[-300:]))
elif parte == "egenloff":
    print("Egenloff 1-14 abriu em", reabrir(L / "egenloff_1a14.pdf"), "s")
    v.ir_pagina(12); print("medida:", v.esperar_medida(120), v.esperar_ocioso(120))
    print("PONTO 3, Egenloff 12:", v.curto()); print("  faixa:", v.faixa()); print("  foto:", v.foto("r2-egenloff-12-tres-botoes")[0][-42:])
    v.g.clicar_w("tc.botoes_de_sugestao_3['filtro']", espera=2)
    print("  depois do 'está bom assim':", v.curto(), v.historico()); v.foto("r2-egenloff-12-esta-bom-assim")
    v.ctrl_z(); print("  Ctrl+Z:", v.curto())
    # ponto 4: teclado depois de clicar num botao do aviso
    v.clicar("Deixar em branco", classe="QPushButton", espera=2)
    print("PONTO 4: cliquei 'Deixar em branco'; foco:", v.s(FOCO), "|", v.curto())
    P.tecla(0x27); time.sleep(2)
    print("  seta direita -> pagina", v.s("tc.indice_pagina+1"), "foco:", v.s(FOCO))
    P.tecla(0x25); time.sleep(2)
    print("  seta esquerda -> pagina", v.s("tc.indice_pagina+1"))
    h0 = v.historico(); P.tecla(0x20); time.sleep(2)
    print("  espaco -> pagina", v.s("tc.indice_pagina+1"), "| historico:", v.historico(), "foco:", v.s(FOCO))
    v.foto("r2-teclado-depois-do-clique")
    v.ctrl_z(2); v.ir_pagina(12); time.sleep(1)
    v.clicar("Tirar do livro", classe="QPushButton", espera=2)
    print("  cliquei 'Tirar do livro'; foco:", v.s(FOCO), "|", v.s("(len(tc.projeto.paginas_ativas), tc.projeto.total_apagadas)"))
    P.tecla(0x20); time.sleep(2)
    print("  espaco -> pagina", v.s("tc.indice_pagina+1"), "| historico:", v.historico(), "|", v.s("(len(tc.projeto.paginas_ativas), tc.projeto.total_apagadas)"))
    vistos = set()
    for _ in range(40):
        P.tecla(0x09); time.sleep(0.3); vistos.add((v.s(FOCO), v.s("tc.indice_pagina+1")))
    print("  Tab 40 vezes: paginas", sorted({x[1] for x in vistos}, key=int), "| botoes do aviso com foco:", [x for x in vistos if "Deixar" in x[0] or "Tirar" in x[0] or "bom assim" in x[0] or "voltar a" in x[0]])
    for _ in range(4):
        if v.historico() == "[]":
            break
        v.ctrl_z()
    # pontos 6 e 7: Egenloff 3
    v.ir_pagina(3); print("medida:", v.esperar_medida(180), v.esperar_ocioso(180)); time.sleep(3)
    print("PONTOS 6 e 7, Egenloff 3:", v.curto()); print("  faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"))
    print("  foto:", v.foto("r2-egenloff-3")[0][-30:])
    print("erros.log:", repr(v.erros_log()[-300:]))
elif parte == "avulsas":
    for nome, pdf in (("gladstone-18", PAG / "gladstone_p018.pdf"), ("rariora-8", PAG / "rariora_p008.pdf"),
                      ("palatino-66", GAB / "palatino_p066.pdf")):
        print(nome, "abriu em", reabrir(pdf), "s"); print("  medida:", v.esperar_medida(180), v.esperar_ocioso(180)); time.sleep(3)
        e = eval(v.estado_da_pagina())
        print("  ", v.curto()); print("   faixa:", v.faixa(), "medidor:", v.s("tc.medidor.valor"))
        # passa pelos avisos da pagina ate o que interessa (so leitura do que aparece; 'está bom assim' nativo nos outros)
        for _ in range(3):
            e = eval(v.estado_da_pagina())
            if not e["pendentes"] or e["pendentes"][0] in ("em_branco", "pagina_sem_conteudo", "texto_falhado", "forca_reforcada"):
                break
            botao = "tc.botoes_de_sugestao_3['filtro']" if e.get("b3") else ("tc.botoes_de_sugestao_2['filtro']" if e["b2"] else "tc.botoes_de_sugestao['filtro']")
            v.g.clicar_w(botao, espera=2)
        print("   no aviso que interessa:", v.curto()); print("   faixa:", v.faixa())
        print("   foto:", v.foto(f"r2-{nome}")[0][-34:])
    print("erros.log:", repr(v.erros_log()[-300:]))
    v.fechar()
