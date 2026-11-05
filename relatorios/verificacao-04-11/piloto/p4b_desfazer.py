"""Verificador 04/11, complemento do desfazer-pagina: o botao direito em "Duas lado a lado" (na OUTRA
pagina do par) e a pagina em branco (item do menu pelo mouse em cima + Enter). Siebmacher."""
import time

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\desfazer-pagina"


def escolher_item(menu, texto):
    """Pelo teclado (setas + Enter) na janelinha do menu: o clique por mensagem num item comum,
    com o menu fora da tela, fecha sem escolher (limite do piloto, anotado tambem pelo agente)."""
    itens = [a for a in menu.actions() if not a.isSeparator() and a.isEnabled()]
    acao = next(a for a in itens if a.text() == texto)
    disparou = []
    acao.triggered.connect(lambda *_a: disparou.append(True))
    h = int(menu.winId())
    for _ in range(itens.index(acao) + 1):
        C.base.user32.PostMessageW(h, C.base.WM_KEYDOWN, 0x28, 1); C.base.esperar(0.1)
        C.base.user32.PostMessageW(h, C.base.WM_KEYUP, 0x28, 0xC0000001); C.base.esperar(0.2)
    anotar("item em destaque", menu.activeAction().text() if menu.activeAction() else None)
    p(menu, "menu-item-em-destaque")
    C.base.user32.PostMessageW(h, C.base.WM_KEYDOWN, 0x0D, 1); C.base.esperar(0.05)
    C.base.user32.PostMessageW(h, C.base.WM_KEYUP, 0x0D, 0xC0000001); C.base.esperar(2.5)
    return bool(disparou)


def main():
    j, porteiro = C.abrir(WT, "5b-desfazer-complemento", "Schön Neues Modell Buch - Johann Siebmacher.pdf")
    from ui import desfazer_nesta_pagina as D
    from PySide6.QtCore import QRect
    t = j.tela_conferir
    C.ferramenta(j, "X"); C.mostrar(j, "uma"); C.ir_pagina(j, 5)
    t._escolher_filtro("preto_e_branco"); C.esperar_previa(j)
    C.ir_pagina(j, 4)
    C.mostrar(j, "duas")
    pares = t.lado_a_lado; pares.grab()
    vista = t.vista_da_pagina.currentWidget()
    vis_rect = vista.rect()
    alvo = None
    for pos, r in pares.retangulos():
        idx = pares.indices[pos]
        centro = pares.folhas.mapTo(vista, r.center())
        anotar("retangulo", {"pagina": idx + 1, "centro na vista": [centro.x(), centro.y()]})
        if idx != t.indice_pagina and vis_rect.contains(centro) and abs(idx - t.indice_pagina) == 1:
            alvo = (idx, centro)
    anotar("da vez / alvo", [t.indice_pagina + 1, alvo and alvo[0] + 1])
    t._menu_desfazer = None
    C.botao_direito(j, vista, alvo[1])
    menu = t._menu_desfazer
    sub = menu.actions()[0].menu() if menu is not None and menu.actions() else None
    anotar("menu da pagina clicada", {"abriu": menu is not None and menu.isVisible(),
                                      "pagina do menu": (getattr(sub, "indice", -1) + 1) if sub else None})
    conferir(sub is not None and getattr(sub, "indice", None) == alvo[0],
             f"Duas lado a lado: botao direito na pagina {alvo[0] + 1} abre o menu DELA")
    p(j, "duas-lado-a-lado-menu")
    if menu is not None:
        p(menu, "duas-lado-a-lado-o-menu")
    for m in C.menus_abertos():
        m.close()
    C.mostrar(j, "uma")

    # pagina em branco depois da 5 (miniatura 5)
    n0 = len([q for q in j.projeto.paginas if not q.apagada])
    mini = t.tira._miniaturas[4]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); C.base.esperar(0.4)
    C.botao_direito(j, mini)
    menu = t._menu_desfazer
    ok = escolher_item(menu, D.DEPOIS_EM_BRANCO)
    C.esperar_previa(j)
    n1 = len([q for q in j.projeto.paginas if not q.apagada])
    p6 = j.projeto.paginas[5]
    anotar("depois", {"disparou": ok, "antes": n0, "depois": n1, "p6 inserida": getattr(p6, "inserida", 0),
                      "rotulo": t.rotulo_da_pagina.text(), "ultima": t.acoes.feitas[-1].descricao if t.acoes.feitas else None})
    conferir(n1 == n0 + 1 and getattr(p6, "inserida", 0), "a pagina em branco entrou como a 6")
    C.ir_pagina(j, 6); p(j, "pagina-em-branco-6")
    C.mostrar(j, "duas"); p(j, "pagina-em-branco-6-ao-lado-da-5"); C.mostrar(j, "uma")
    # antes da 1
    mini = t.tira._miniaturas[0]
    t.tira.rolagem.ensureWidgetVisible(mini, 60, 0); C.base.esperar(0.4)
    C.botao_direito(j, mini)
    ok = escolher_item(t._menu_desfazer, D.ANTES_EM_BRANCO); C.esperar_previa(j)
    n2 = len([q for q in j.projeto.paginas if not q.apagada])
    conferir(n2 == n0 + 2 and getattr(j.projeto.paginas[0], "inserida", 0), "pagina em branco antes da 1")
    # Ctrl+Z duas vezes tira as duas
    C.ctrl(j, ord("Z")); C.ctrl(j, ord("Z")); C.esperar_previa(j)
    n3 = len([q for q in j.projeto.paginas if not q.apagada])
    conferir(n3 == n0, f"Ctrl+Z duas vezes tira as duas ({n3})")
    C.ctrl(j, ord("Y")); C.esperar_previa(j)
    conferir(len([q for q in j.projeto.paginas if not q.apagada]) == n0 + 1, "Ctrl+Y poe a primeira de novo")
    # "tirar do livro" na pagina em branco
    C.ir_pagina(j, 6)
    from PySide6.QtWidgets import QPushButton
    tirar = next((b for b in t.findChildren(QPushButton) if b.text() == "tirar do livro" and b.isVisible()), None)
    if tirar is not None:
        C.base.clique(j, tirar); C.base.esperar(2.5)
    n4 = len([q for q in j.projeto.paginas if not q.apagada])
    anotar("tirar do livro", {"achou o botao": tirar is not None, "paginas": n4})
    conferir(n4 == n0, "'tirar do livro' tira a pagina em branco")
    p(j, "depois-de-tirar-do-livro")
    C.fechar(j)


if __name__ == "__main__":
    main()
