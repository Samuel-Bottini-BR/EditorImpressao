"""Verificador 04/11: D-621 (botao direito -> "Desfazer nesta pagina", caixinhas) e D-623 (botao direito
na miniatura -> pagina em branco antes/depois). Livro do acervo: Siebmacher; folha 3 dividida a mao,
depois o Automatico (Endireitar, Cortar, Limpar em Preto e branco) no livro todo."""
import time

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\desfazer-pagina"


def campos(j, i):
    pg = j.projeto.paginas[i]
    return {"pag": i + 1, "folha": pg.folha + 1, "metade": pg.metade, "ang": pg.angulo_manual,
            "recorte": pg.recorte, "filtro": pg.filtro, "escala": pg.conteudo_escala,
            "desloc": tuple(pg.conteudo_deslocamento), "inserida": getattr(pg, "inserida", 0),
            "apagada": pg.apagada}


def abrir_lista(j, nome, marcar, apertar=True):
    from PySide6.QtCore import QPoint
    t = j.tela_conferir
    menu = getattr(t, "_menu_desfazer", None)
    if menu is None or not menu.isVisible():
        anotar(f"{nome}: o menu NAO abriu", [type(m).__name__ for m in C.menus_abertos()])
        return None
    itens = [a.text() for a in menu.actions()]
    anotar(f"{nome}: itens do menu", itens)
    p(menu, f"{nome}-menu")
    acao = next(a for a in menu.actions() if a.menu() is not None)
    C.clique_no_menu(menu, menu.actionGeometry(acao).center())
    sub = acao.menu()
    t0 = time.time()
    while not sub.isVisible() and time.time() - t0 < 5:
        C.base.esperar(0.2)
    lista = sub.lista
    from ui import desfazer_nesta_pagina as D
    anotar(f"{nome}: caixinhas", {D.NOMES[e]: {"acesa": c.isEnabled(), "marcada": c.isChecked()}
                                   for e, c in lista.caixas.items()})
    p(sub, f"{nome}-caixinhas")
    for etapa in marcar:
        caixa = lista.caixas[etapa]
        C.clique_no_menu(sub, caixa.mapTo(sub, QPoint(9, caixa.height() // 2)))
    anotar(f"{nome}: marcadas", lista.marcadas())
    p(sub, f"{nome}-marcadas")
    if apertar:
        C.clique_no_menu(sub, lista.botao.mapTo(sub, lista.botao.rect().center())); C.base.esperar(2)
    else:
        for m in C.menus_abertos():
            m.close()
    return itens


def main():
    j, porteiro = C.abrir(WT, "5-desfazer-pagina", "Schön Neues Modell Buch - Johann Siebmacher.pdf")
    from core import automatico as A
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from ui import desfazer_nesta_pagina as D
    from ui.tela_conferir import ABA_BORDAS
    t = j.tela_conferir

    # folha 3 dividida a mao (pagina 3 e 4)
    C.ferramenta(j, "D"); C.ir_pagina(j, 3)
    C.base.clique(j, t.botao_nao_dividir); C.base.esperar(2.5)
    conferir(j.projeto.folhas[2].dividir, "folha 3 dividida")
    # o Automatico no livro todo (Endireitar, Cortar, Limpar em Preto e branco)
    e = j.estado_do_automatico
    e.marcadas = {A.ENDIREITAR, A.CORTAR, A.LIMPAR}
    e.opcoes["filtro_padrao"] = PRETO_E_BRANCO
    e.alcance = "livro"
    t0 = time.time()
    ok = j.rodar_o_automatico(esperar=True, perguntar=False)
    anotar("Automatico", {"ok": ok, "s": round(time.time() - t0, 1)})
    C.base.esperar(3)
    conferir(j.projeto.folhas[2].dividir, "a folha 3 continua dividida depois do Automatico")
    C.ferramenta(j, "X"); C.mostrar(j, "uma"); C.ir_pagina(j, 3)
    a3, a4 = campos(j, 2), campos(j, 3)
    anotar("antes", [a3, a4])
    p(j, "pagina-3-depois-do-automatico")
    feitas = len(t.acoes.feitas)

    # D-621: botao direito na pagina 3 -> Desfazer nesta pagina -> Corte e Filtro -> desfazer
    C.botao_direito(j, t.visualizadores[ABA_BORDAS])
    abrir_lista(j, "pagina-3", [D.CORTAR, D.FILTRO])
    C.esperar_previa(j)
    d3, d4 = campos(j, 2), campos(j, 3)
    anotar("depois", [d3, d4, {"acoes": [feitas, len(t.acoes.feitas)],
                               "ultima": t.acoes.feitas[-1].descricao if t.acoes.feitas else None}])
    conferir(d3["recorte"] in (None, (0.0, 0.0, 1.0, 1.0), [0.0, 0.0, 1.0, 1.0]), "pagina 3 sem corte")
    conferir(d3["filtro"] == ORIGINAL, "pagina 3 em Original")
    conferir(d3["ang"] == a3["ang"], "pagina 3: o Endireitar (nao marcado) ficou")
    conferir(d4 == a4, "pagina 4 (a outra da folha) nao mudou")
    conferir(j.projeto.folhas[2].dividir, "a folha continua dividida")
    conferir(len(t.acoes.feitas) == feitas + 1, "uma acao so no Historico")
    p(j, "pagina-3-desfeita")
    C.ctrl(j, ord("Z")); C.esperar_previa(j)
    conferir(campos(j, 2) == a3, "Ctrl+Z volta a pagina 3 como estava")
    C.ctrl(j, ord("Y")); C.esperar_previa(j)
    conferir(campos(j, 2) == d3, "Ctrl+Y refaz")
    p(j, "pagina-3-ctrl-y")

    # D-621 na miniatura (pagina 6) e em Duas lado a lado
    mini = t.tira._miniaturas[5]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); C.base.esperar(0.4)
    C.botao_direito(j, mini)
    itens = abrir_lista(j, "miniatura-6", [], apertar=False)
    conferir(itens is not None and D.ANTES_EM_BRANCO in itens and D.DEPOIS_EM_BRANCO in itens,
             "D-623: a miniatura tem 'adicionar pagina em branco antes/depois' no mesmo menu")
    C.mostrar(j, "duas")
    from PySide6.QtCore import QPoint
    pares = t.lado_a_lado; pares.grab()
    vista = t.vista_da_pagina.currentWidget()
    alvo = None
    for pos, r in pares.retangulos():
        if pares.indices[pos] != t.indice_pagina:
            alvo = (pares.indices[pos], pares.folhas.mapTo(vista, r.center())); break
    if alvo:
        C.botao_direito(j, vista, alvo[1])
        menu = getattr(t, "_menu_desfazer", None)
        sub = menu.actions()[0].menu() if menu is not None and menu.actions() else None
        anotar("duas lado a lado: pagina do menu", {"clicada": alvo[0] + 1,
                                                     "menu": getattr(sub, "indice", None)})
        p(j, "duas-lado-a-lado-botao-direito")
        for m in C.menus_abertos():
            m.close()
    C.mostrar(j, "uma")

    # D-623: adicionar pagina em branco depois da 6
    n0 = len(j.projeto.paginas)
    t.tira.rolagem.ensureWidgetVisible(t.tira._miniaturas[5], 60, 0); C.base.esperar(0.4)
    C.botao_direito(j, t.tira._miniaturas[5])
    menu = t._menu_desfazer
    acao = next(a for a in menu.actions() if a.text() == D.DEPOIS_EM_BRANCO)
    C.clique_no_menu(menu, menu.actionGeometry(acao).center()); C.base.esperar(2.5); C.esperar_previa(j)
    n1 = len([q for q in j.projeto.paginas if not q.apagada])
    anotar("pagina em branco", {"antes": n0, "depois": n1, "p7": campos(j, 6), "da vez": t.indice_pagina + 1,
                                "rotulo": t.rotulo_da_pagina.text()})
    conferir(n1 == n0 + 1 and campos(j, 6)["inserida"], "a pagina em branco entrou como a 7")
    p(j, "pagina-em-branco-depois-da-6")
    C.ctrl(j, ord("Z")); C.esperar_previa(j)
    conferir(len([q for q in j.projeto.paginas if not q.apagada]) == n0, "Ctrl+Z tira a pagina em branco")
    p(j, "pagina-em-branco-ctrl-z")

    # Ao redor: o menu do botao direito do Mover (linhas de apoio) continua
    C.ferramenta(j, "F"); C.ir_pagina(j, 8)
    vis = C.visualizador(j)
    C.botao_direito(j, vis)
    abertos = C.menus_abertos()
    anotar("mover: menus", [C.base.acoes_do_menu(m) for m in abertos])
    if abertos:
        p(abertos[0], "mover-menu-do-botao-direito")
    for m in abertos:
        m.close()
    C.fechar(j)


if __name__ == "__main__":
    main()
