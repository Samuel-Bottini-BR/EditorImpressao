"""Refaz os prints da tela que tinham saido com a imagem velha (Cursus 3, Opus Majus 20,
Antiphon 260, Rariora 8) e tenta o print no tamanho de janela maximizada (Antiphonal 46)."""
import time, v
P = v.P
def um(busca, rotulo, pagina, nome, maximizada=False):
    try: P.fechar()
    except Exception: pass
    v.abrir()
    r = v.continuar_projeto(busca, rotulo=rotulo)
    v.aba("Filtro"); time.sleep(2)
    v.ir_pagina(pagina); t = v.esperar_medida(300); time.sleep(4)
    print(f"{rotulo} p{pagina}: reabriu em {r} s, medida {t} s |", v.curto()); print("   faixa:", v.faixa())
    print("   painel:", [x if isinstance(x, str) else x[0] for x in v.painel()][:9])
    print("   foto:", v.foto(nome)[0][-40:])
    if maximizada:
        print("   tamanho maximizada:", v.tamanho(True)); time.sleep(6)
        d, w, h = v.foto(nome + "-maximizada"); print("   foto maximizada:", d[-52:], w, h)
um("Cursus", "Cursus", 3, "62-cursus-p3-tela")
um("opusmajus", "opusmajus", 1, "61-opusmajus-p1-tela")
um("Rariora", "Rariora", 8, "51-rariora-p8-tela")
um("Antiphon", "Antiphon_25", 260, "63-antiphon-p260-tela")
um("1547", "1547", 46, "70d-antiphonal-46", maximizada=True)
P.fechar()
