"""Verificador 04/11: D-612, D-622, D-611 (mover-lado). Palatino do acervo (paginas simples) para as
ferramentas nos pares e no antes/depois; Siebmacher do acervo para o Dividir (tira pela folha)."""
import shutil

import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\mover-lado"


def ret_de(t, indice):
    from PySide6.QtCore import QRect
    pares = t.lado_a_lado
    pares.grab()
    for pos, r in pares.retangulos():
        if pares.indices[pos] == indice:
            vista = t.vista_da_pagina.currentWidget()
            topo = pares.folhas.mapTo(vista, r.topLeft())
            return QRect(topo, r.size())
    return None


def ponto(r, fx, fy):
    from PySide6.QtCore import QPoint
    return QPoint(r.left() + int(fx * r.width()), r.top() + int(fy * r.height()))


def arrastar(j, de, dx, dy=0):
    from PySide6.QtCore import QPoint
    vista = j.tela_conferir.vista_da_pagina.currentWidget()
    C.base.arrastar(j, vista, de, QPoint(de.x() + dx, de.y() + dy)); C.base.esperar(1.0)


def clicar(j, pt):
    vista = j.tela_conferir.vista_da_pagina.currentWidget()
    C.base.clique(j, vista, pt); C.base.esperar(0.8)


def main():
    j, porteiro = C.abrir(WT, "2-mover-lado", "Giovambattista Palatino cittadino romano.pdf")
    from ui.tela_conferir import DUAS
    t = j.tela_conferir
    pg = j.projeto.paginas

    # 1. Mover (F), pagina 4, botao "Duas lado a lado" (a vista nao muda sozinha)
    C.ir_pagina(j, 4); C.ferramenta(j, "F"); C.mostrar(j, "duas")
    anotar("estado", C.estado(j))
    conferir(t.mostrar == DUAS and t.vista_da_pagina.currentWidget() is t.lado_a_lado,
             "Mover + Duas lado a lado: a vista fica nos pares")
    p(j, "mover-nos-pares")

    # 2. um aperto na OUTRA pagina do par (5) escolhe e ja arrasta (a-75/a-76)
    r5 = ret_de(t, 4); r4 = ret_de(t, 3)
    anotar("retangulos 4 e 5", [str(r4), str(r5)])
    arrastar(j, ponto(r5, 0.5, 0.45), 60)
    anotar("depois de arrastar a 5", {"da vez": t.indice_pagina + 1, "desloc 5": pg[4].conteudo_deslocamento,
                                      "desloc 4": pg[3].conteudo_deslocamento})
    conferir(t.indice_pagina == 4, "o aperto na pagina 5 escolheu a 5")
    conferir(pg[4].conteudo_deslocamento[0] > 0.02, "e no mesmo aperto a 5 andou para a direita")
    conferir(tuple(pg[3].conteudo_deslocamento) == (0.0, 0.0), "a 4 nao andou")
    p(j, "mover-arrastou-a-5")

    # 3. D-622: clicar no cinza tira a selecao; clicar na pagina escolhe de novo
    r4 = ret_de(t, 3)
    from PySide6.QtCore import QPoint
    fora = QPoint(max(4, r4.left() // 2), r4.center().y())
    clicar(j, fora)
    anotar("depois do clique no cinza", {"sem_escolha": t.lado_a_lado.sem_escolha, "da vez": t.indice_pagina + 1})
    conferir(t.lado_a_lado.sem_escolha, "D-622: clique no cinza tirou a selecao")
    p(j, "d622-clicou-no-cinza")
    clicar(j, ponto(ret_de(t, 4), 0.5, 0.5))
    conferir(not t.lado_a_lado.sem_escolha, "D-622: clique na pagina escolheu de novo")
    p(j, "d622-clicou-na-pagina")
    # o Ctrl+Z desfaz o arrasto
    C.ctrl(j, ord("Z"))
    conferir(tuple(pg[4].conteudo_deslocamento) == (0.0, 0.0), "Ctrl+Z desfez o arrasto da 5")

    # 4. Cortar (X) nos pares: puxar a beirada da direita da pagina 5 para dentro
    C.ferramenta(j, "X")
    conferir(t.mostrar == DUAS, "Cortar: continua em Duas lado a lado")
    C.ir_pagina(j, 5); C.ir_pagina(j, 4); C.base.esperar(2)
    antes = tuple(pg[4].recorte or (0, 0, 1, 1))
    r5 = ret_de(t, 4)
    de = ponto(r5, 1.0, 0.5) - QPoint(2, 0)
    arrastar(j, de, -50)
    depois = tuple(pg[4].recorte or (0, 0, 1, 1))
    anotar("cortar nos pares", {"da vez": t.indice_pagina + 1, "recorte antes": antes, "depois": depois})
    conferir(t.indice_pagina == 4 and depois[2] < antes[2] - 0.02, "Cortar: puxar a beirada da 5 nos pares cortou a 5")
    p(j, "cortar-nos-pares")

    # 5. Retangulo (R) nos pares: marcar na pagina 4
    C.ferramenta(j, "R")
    r4 = ret_de(t, 3)
    n0 = len(pg[3].selecao or [])
    arrastar(j, ponto(r4, 0.3, 0.3), 60, 60)
    n1 = len(pg[3].selecao or [])
    anotar("retangulo nos pares", {"aba": t.aba_atual, "da vez": t.indice_pagina + 1, "regioes antes/depois": [n0, n1]})
    conferir(n1 == n0 + 1 and t.indice_pagina == 3, "Retangulo: marcou na pagina 4 nos pares")
    p(j, "retangulo-nos-pares")

    # 6. Endireitar (I) nos pares
    C.ferramenta(j, "I")
    conferir(t.mostrar == DUAS, "Endireitar: continua em Duas lado a lado")
    p(j, "endireitar-nos-pares")

    # 7. antes / depois com o Mover (Uma pagina): o depois mostra o que o Mover fez
    C.ferramenta(j, "F"); C.mostrar(j, "uma"); C.ir_pagina(j, 6)
    C.base.clique(j, t.botao_antes_depois); C.base.esperar(4)
    vista = t.vista_antes_depois
    anotar("antes/depois ligado", {"comparando": t.comparando, "aviso": getattr(vista, "aviso", None),
                                   "na tela": type(t.vista_da_pagina.currentWidget()).__name__})
    p(j, "antes-depois-mover")
    d0 = vista.depois.cacheKey() if vista.depois is not None else None
    w = t.vista_da_pagina.currentWidget()
    arrastar(j, QPoint(int(w.width() * 0.6), int(w.height() * 0.5)), 70)
    C.base.esperar(4)
    anotar("antes/depois depois do arrasto", {"desloc 6": pg[5].conteudo_deslocamento, "comparando": t.comparando,
                                              "depois mudou": (vista.depois.cacheKey() if vista.depois is not None else None) != d0})
    conferir(pg[5].conteudo_deslocamento[0] > 0.02, "antes/depois: o arrasto moveu a pagina 6 (agiu no depois)")
    conferir(t.comparando, "antes/depois continua ligado")
    p(j, "antes-depois-mover-arrastado")
    C.base.clique(j, t.botao_antes_depois); C.base.esperar(1.5)

    # 8. Ao redor: Uma pagina, Mover, arrastar ainda funciona; Mao nos pares: clique no cinza nao tira a escolha
    C.ir_pagina(j, 8)
    v = C.visualizador(j)
    vista = t.vista_da_pagina.currentWidget()
    c = v.mapTo(vista, v.rect().center())
    arrastar(j, c, -40)
    conferir(pg[7].conteudo_deslocamento[0] < -0.01, "Uma pagina: o Mover arrasta como antes")
    p(j, "uma-pagina-mover")
    C.ferramenta(j, "E"); C.mostrar(j, "duas")
    r = ret_de(t, t.indice_pagina)
    if r is not None:
        clicar(j, QPoint(max(4, r.left() // 2), r.center().y()))
        conferir(not t.lado_a_lado.sem_escolha, "Mao nos pares: clique no cinza nao tira a pagina da vez (como antes)")
    p(j, "mao-nos-pares")
    C.mostrar(j, "uma")

    # 9. D-611 no Dividir: Siebmacher, dividir a mao as folhas 2, 3 e 4
    import comum
    trab = C.base.TRAB / "livros"
    pdf2 = trab / "Siebmacher.pdf"
    shutil.copy2(C.ACERVO / "Schön Neues Modell Buch - Johann Siebmacher.pdf", pdf2)
    j.abrir_livro(str(pdf2)); anotar("abriu Siebmacher", C.esperar_tela(j))
    t = j.tela_conferir
    C.ferramenta(j, "D"); C.mostrar(j, "uma")
    for folha in (2, 3, 4):
        i = next(q.indice for q in j.projeto.paginas if q.folha == folha - 1)
        C.ir_pagina(j, i + 1)
        C.base.clique(j, t.botao_nao_dividir); C.base.esperar(2.5)
    anotar("paginas", [(q.indice + 1, q.folha + 1, q.metade) for q in j.projeto.paginas[:9]])
    C.mostrar(j, "duas")
    tira = t.tira
    rotulos = [getattr(m, "rotulo_numero", None) or m.numero for m in tira._miniaturas]
    blocos = {}
    for i in range(min(12, len(tira._miniaturas))):
        lin, col = tira.posicao(i)
        blocos.setdefault((lin, col // 3), []).append(i + 1)
    anotar("tira no Dividir, Duas lado a lado", {"rotulos (12)": rotulos[:12], "pares": sorted(blocos.values())})
    conferir(rotulos == list(range(1, len(j.projeto.paginas) + 1)), "a miniatura tem o numero real da pagina")
    pares_folha = sorted(blocos.values())
    conferir([2, 3] in pares_folha and [4, 5] in pares_folha and [6, 7] in pares_folha,
             "no Dividir a tira junta pela folha (2-3, 4-5, 6-7 = folhas 2, 3, 4)")
    p(j, "d611-dividir-duas-tira-pela-folha")
    # clicar na miniatura 5 leva a pagina 5
    mini = tira._miniaturas[4]
    tira.rolagem.ensureWidgetVisible(mini, 60, 0); C.base.esperar(0.4)
    C.base.clique(j, mini); C.esperar_previa(j)
    conferir(t.indice_pagina == 4 and t.rotulo_da_pagina.text().startswith("página 5"),
             f"clique na miniatura 5 -> {t.rotulo_da_pagina.text()}")
    p(j, "d611-clicou-miniatura-5")
    # fora do Dividir: os pares do livro aberto (como antes)
    C.ferramenta(j, "X")
    blocos = {}
    for i in range(min(12, len(tira._miniaturas))):
        lin, col = tira.posicao(i)
        blocos.setdefault((lin, col // 3), []).append(i + 1)
    anotar("tira no Cortar, Duas lado a lado", sorted(blocos.values()))
    p(j, "d611-cortar-duas-tira")
    C.fechar(j)


if __name__ == "__main__":
    main()
