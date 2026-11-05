"""Verificador 04/11: D-619 (quadro "Já feito no livro todo") e D-620 (qualidade da previa na barra de
baixo, uma setinha, em todas as ferramentas). Livro do acervo: Rhetorica Christiana."""
import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\painel-livro"


def quadro(j, aba):
    from PySide6.QtWidgets import QAbstractButton, QFrame, QLabel
    painel = j.tela_conferir.propriedades_das_abas[aba]
    q = [q for q in painel.findChildren(QFrame) if q.objectName() == "parteDoLivro"]
    if not q:
        return None
    return [w.text() for w in q[0].findChildren(QLabel) + q[0].findChildren(QAbstractButton)]


def rolar_ao_fim(j, aba):
    from PySide6.QtWidgets import QScrollArea
    pai = j.tela_conferir.propriedades_das_abas[aba].parentWidget()
    while pai is not None and not isinstance(pai, QScrollArea):
        pai = pai.parentWidget()
    if pai is not None:
        pai.verticalScrollBar().setValue(pai.verticalScrollBar().maximum()); C.base.esperar(0.6)


def todos_os_textos(j, aba):
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel
    painel = j.tela_conferir.propriedades_das_abas[aba]
    return ([w.text() for w in painel.findChildren(QLabel)] + [w.text() for w in painel.findChildren(QAbstractButton)]
            + [" / ".join(c.itemText(k) for k in range(c.count())) for c in painel.findChildren(QComboBox)])


def main():
    j, porteiro = C.abrir(WT, "3-painel-livro", "Rhetorica Christiana -  Fray Diego Valadés.pdf")
    from ui.tela_conferir import ABA_ANGULO, ABA_BORDAS, ABA_CORTE
    import configuracoes
    t = j.tela_conferir
    C.ir_pagina(j, 12)

    # D-619 nos tres
    for letra, aba, nome in (("X", ABA_BORDAS, "cortar"), ("D", ABA_CORTE, "dividir"), ("I", ABA_ANGULO, "endireitar")):
        C.ferramenta(j, letra)
        rolar_ao_fim(j, aba)
        q = quadro(j, aba)
        anotar(f"quadro {nome}", q)
        conferir(q is not None and any(s.upper() == "JÁ FEITO NO LIVRO TODO" for s in q),
                 f"{nome}: o quadro se chama 'Já feito no livro todo'")
        conferir(q is not None and not any("PARA O LIVRO TODO" == s.upper() for s in q), f"{nome}: o titulo antigo saiu")
        conferir(q is not None and any("mudar no Automático" in s for s in q), f"{nome}: 'mudar no Automático...' ficou")
        if nome == "cortar":
            conferir(any("Margens iguais" in s for s in q), "cortar: a caixinha 'Margens iguais' (D-554) ficou")
            txt = todos_os_textos(j, aba)
            conferir(not any("Qualidade da prévia" in s for s in txt), "cortar: a 'Qualidade da prévia' saiu do painel")
        p(j, f"d619-quadro-{nome}")

    # D-620: a setinha na barra de baixo em TODAS as ferramentas
    b = t.botao_qualidade
    for letra, nome in (("X", "cortar"), ("D", "dividir"), ("I", "endireitar"), ("F", "mover"),
                        ("R", "retangulo"), ("E", "mao"), ("Z", "zoom")):
        C.ferramenta(j, letra)
        anotar(f"setinha no {nome}", {"aba": t.aba_atual, "visivel": b.isVisible(), "texto": b.text(),
                                      "balao": b.toolTip().splitlines()[0] if b.toolTip() else ""})
        conferir(b.isVisible(), f"D-620: a setinha da qualidade aparece no {nome}")
    # filtros (pelo menu Ferramentas, sem letra conhecida): pelo botao da trilha
    try:
        t.escolher_ferramenta("filtros"); C.esperar_previa(j)
        conferir(b.isVisible(), "D-620: a setinha aparece no Filtro")
    except Exception as erro:  # noqa: BLE001
        anotar("filtros", str(erro))
    C.ferramenta(j, "X")
    p(j, "d620-barra-de-baixo-cortar")

    # abrir a setinha (clique de verdade) e escolher Alta
    C.base.clique(j, b); C.base.esperar(1.2)
    menu = t.menu_da_qualidade
    anotar("menu", {"visivel": menu.isVisible(), "itens": [(a.text(), a.isChecked()) for a in menu.actions()]})
    conferir(menu.isVisible() and [a.text() for a in menu.actions()] == ["Rápida", "Média", "Alta"],
             "a setinha abre Rápida / Média / Alta")
    if menu.isVisible():
        p(menu, "d620-menu-aberto")
        acao = t.acoes_da_qualidade["alta"]
        C.clique_no_menu(menu, menu.actionGeometry(acao).center()); C.base.esperar(3)
        if not acao.isChecked():
            anotar("clique no menu nao pegou: teclado")
            if not menu.isVisible():
                C.base.clique(j, b); C.base.esperar(1.0)
            C.base.tecla(menu, 0x28, vezes=3); C.base.tecla(menu, 0x0D); C.base.esperar(3)
    anotar("depois de Alta", {"gravada": configuracoes.ler("qualidade_previa"), "dpi": t._dpi_normal,
                              "balao": b.toolTip()})
    conferir(configuracoes.ler("qualidade_previa") == "alta", "Alta ficou gravada para o programa todo")
    p(j, "d620-alta-no-cortar")
    for letra, nome in (("I", "endireitar"), ("F", "mover"), ("D", "dividir")):
        C.ferramenta(j, letra)
        anotar(f"alta no {nome}", {"balao": b.toolTip().splitlines()[0], "dpi": t._dpi_normal})
        conferir(b.toolTip().startswith("Qualidade da prévia: Alta"), f"Alta vale no {nome}")
    p(j, "d620-alta-no-dividir")

    # ao redor, na barra: Uma pagina / Duas lado a lado, antes/depois, zoom, ajustar, contador
    C.ferramenta(j, "X")
    C.mostrar(j, "duas"); p(j, "barra-duas-lado-a-lado"); C.mostrar(j, "uma")
    rot = t.rotulo_do_livro
    anotar("contador", {"na tela": rot.text(), "inteiro": rot.texto_inteiro() if hasattr(rot, "texto_inteiro") else None})
    # janela menor (1366) com Propriedades aberto
    j.resize(1366, 705); C.base.esperar(2); j.move(-32000, -32000)
    anotar("1366: contador", {"na tela": rot.text(), "setinha visivel": b.isVisible()})
    p(j, "barra-1366")
    j.resize(C.LARGURA, C.ALTURA); C.base.esperar(1.5)
    t.acoes_da_qualidade["rapida"].trigger(); C.base.esperar(1)
    C.fechar(j)


if __name__ == "__main__":
    main()
