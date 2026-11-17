"""Piloto de três perguntas (au-d-492 tique do menu Filtro, au-d-484 Automático nas escolhidas, au-d-487
grade "Todas as páginas"), no Palatino (CÓPIA das folhas 20 a 31 do acervo: páginas de texto, que vão
ser impressas), na janela de verdade fora da tela:

A. menu Filtro (barra do alto): o tique na página 1 (Original); na página 2, Preto e branco escolhido
   no painel Filtro (clique no cartão) -> o tique vai para Preto e branco; página 3 -> Original.
B. Automático, janela grande: "escolher páginas..." -> a grade -> marcar as páginas 5 e 7 (clique) ->
   "usar estas 2 páginas" -> "Rodar em: nas páginas escolhidas (2)" -> só "Limpar a folha" com
   Preto e branco -> "Rodar" -> só as páginas 5 e 7 mudam.
C. A grade "Todas as páginas" (ver todas): "marcar várias", páginas 9 e 11; botão direito numa página
   (nada abre); "rodar o automático nelas..." -> o Automático com as 2 -> "Rodar" -> só 9 e 11 mudam.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum as c  # noqa: E402
from comum import anotar, base  # noqa: E402

PALATINO = "Giovambattista Palatino cittadino romano.pdf"


def copia_do_palatino() -> Path:
    import fitz
    destino = base.TRAB / "livros" / "Palatino.pdf"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not destino.exists():
        with fitz.open(str(base.ACERVO / PALATINO)) as livro, fitz.open() as novo:
            novo.insert_pdf(livro, from_page=19, to_page=30)
            novo.save(str(destino))
    return destino


def filtros(pr):
    return [pg.filtro for pg in pr.paginas]


def abrir_menu(j, pasta, titulo, nome):
    """Clica no título do menu da barra do alto e tira o print do menu aberto."""
    barra = j.menu                       # ui/barra_de_menu.BarraDeMenu (a barra do alto)
    acao = barra.menus[titulo].menuAction()
    base.print_do_menu_que_abrir(nome, pasta, pasta / "menus.txt")
    base.clique(j, barra, barra.actionGeometry(acao).center())
    base.esperar(2.5)


def quadro_da(todas, indice):
    return next(q for q in todas.quadros if any(i.indice == indice for i in q.itens))


def clique_direito(j, widget):
    from PySide6.QtCore import QPoint  # noqa: F401
    alvo = widget.mapTo(j, widget.rect().center())
    h, lp = int(j.winId()), base._lp(j, alvo)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.15)
    base.user32.PostMessageW(h, 0x0204, 2, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, 0x0205, 0, lp); base.esperar(1.0)


def main():
    pasta = c.preparar("grade")
    from PySide6.QtWidgets import QApplication, QMenu

    from core.filtros import PRETO_E_BRANCO
    from ui.automatico import JanelaDoAutomatico
    pdf = copia_do_palatino()
    j = base.nova_janela(1280, 657)
    t = c.abrir(j, pdf)
    pr = j.projeto
    anotar("abriu", {"paginas": len(pr.paginas), "filtros": filtros(pr)})
    c.p(j, pasta, "A0-abriu")

    # A. o tique do menu Filtro
    abrir_menu(j, pasta, "Filtro", "A1-menu-filtro-pagina-1")
    t.ir_para_pagina(1)
    c.esperar_previa(t)
    t.paineis.abrir("filtro")
    base.esperar(8.0)                    # as figurinhas dos filtros chegam por trás
    painel_f = t.paineis.filtro_da_pagina
    cartoes = getattr(painel_f, "cartoes", {}) if painel_f is not None else {}
    anotar("cartoes-do-filtro", list(cartoes))
    if PRETO_E_BRANCO in cartoes:
        base.clique(j, cartoes[PRETO_E_BRANCO])
    c.esperar_previa(t)
    anotar("pagina-2-filtro", pr.paginas[1].filtro)
    c.p(j, pasta, "A2-pagina-2-preto-e-branco-no-painel")
    abrir_menu(j, pasta, "Filtro", "A3-menu-filtro-pagina-2")
    t.ir_para_pagina(2)
    c.esperar_previa(t)
    c.p(j, pasta, "A4-pagina-3")
    abrir_menu(j, pasta, "Filtro", "A5-menu-filtro-pagina-3")

    # B. Automático, janela grande, "escolher páginas..."
    t.paineis.abrir("automatico")
    base.esperar(1.0)
    painel = t.paineis.automatico
    c.p(j, pasta, "B0-painel-automatico")
    base.clique(j, painel.botao_janela)
    base.esperar(2.5)
    jan = next(w for w in QApplication.topLevelWidgets() if isinstance(w, JanelaDoAutomatico) and w.isVisible())
    c.p(jan, pasta, "B1-janela-grande")
    jan.combo_alcance.showPopup()
    base.esperar(1.0)
    c.p(jan.combo_alcance.view().window(), pasta, "B1b-lista-rodar-em")
    jan.combo_alcance.hidePopup()
    base.esperar(0.5)
    base.clique(jan, jan.botao_escolher)
    base.esperar(3.0)
    todas = t.todas
    anotar("grade-para-o-automatico", {"para_o_automatico": todas.para_o_automatico})
    for i in (4, 6):
        base.clique(j, quadro_da(todas, i))
        base.esperar(0.8)
    anotar("escolhidas-na-grade", sorted(todas.escolhidas))
    base.esperar(2.0)
    c.p(j, pasta, "B2-grade-paginas-5-e-7")
    base.clique(j, todas.botao_usar)
    base.esperar(3.0)
    jan = next(w for w in QApplication.topLevelWidgets() if isinstance(w, JanelaDoAutomatico) and w.isVisible())
    est = jan.estado
    from core import automatico as A
    for e in A.ETAPAS:
        est.marcar(e, e == A.LIMPAR)
    est.definir_opcao("filtro_padrao", PRETO_E_BRANCO)
    jan.mostrar_etapa(A.LIMPAR)
    base.esperar(2.0)
    anotar("janela-estado", {"alcance": est.alcance, "escolhidas": sorted(est.escolhidas),
                             "marcadas": sorted(est.marcadas), "rodar": jan.botao_rodar.text(),
                             "combo": jan.combo_alcance.currentText()})
    c.p(jan, pasta, "B3-janela-nas-escolhidas")
    antes = filtros(pr)
    feitas = len(j.acoes.feitas)
    base.clique(jan, jan.botao_rodar)
    c.esperar_ate(lambda: len(j.acoes.feitas) > feitas and t._pronta(), 300)
    base.esperar(3.0)
    pr = j.projeto
    depois = filtros(pr)
    mudaram = [i + 1 for i, (a, b) in enumerate(zip(antes, depois)) if a != b]
    anotar("B-filtros", {"antes": antes, "depois": depois, "paginas_que_mudaram": mudaram,
                         "historico": j.acoes.feitas[-1].descricao})
    base.conferir(mudaram == [5, 7], f"B: só as páginas 5 e 7 mudaram ({mudaram})")
    t.ir_para_pagina(4)
    c.esperar_previa(t)
    c.p(j, pasta, "B4-pagina-5-depois")
    t.ir_para_pagina(5)
    c.esperar_previa(t)
    c.p(j, pasta, "B5-pagina-6-depois")
    c.pdf_das_paginas(pr, [3, 4, 5, 6, 7], pasta, "B")

    # C. a grade "Todas as páginas" (ver todas): marcar várias, botão direito, rodar nelas
    t.abrir_todas_as_paginas()
    base.esperar(3.0)
    todas = t.todas
    c.p(j, pasta, "C0-grade-aberta")
    base.clique(j, todas.botao_marcar_varias)
    base.esperar(0.8)
    for i in (8, 10):
        base.clique(j, quadro_da(todas, i))
        base.esperar(0.8)
    anotar("C-escolhidas", sorted(todas.escolhidas))
    base.esperar(1.5)
    c.p(j, pasta, "C1-grade-paginas-9-e-11")
    base.gravar_textos(todas, pasta / "textos-da-grade.txt", "grade com 2 escolhidas")
    clique_direito(j, quadro_da(todas, 8))
    menus = [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu) and w.isVisible()]
    anotar("C-botao-direito-abriu-menu", len(menus))
    c.p(j, pasta, "C2-depois-do-botao-direito")
    antes = filtros(pr)
    feitas = len(j.acoes.feitas)
    base.clique(j, todas.botoes_da_escolha["automatico"])
    base.esperar(3.0)
    janelas = [w for w in QApplication.topLevelWidgets() if isinstance(w, JanelaDoAutomatico) and w.isVisible()]
    alvo = janelas[0] if janelas else None
    est = j.estado_do_automatico
    anotar("C-automatico", {"janela": bool(alvo), "painel": t.paineis.automatico.isVisible(),
                            "alcance": est.alcance, "escolhidas": sorted(est.escolhidas),
                            "marcadas": sorted(est.marcadas)})
    if alvo is not None:
        c.p(alvo, pasta, "C3-automatico-com-as-escolhidas")
        base.clique(alvo, alvo.botao_rodar)
    else:
        c.p(j, pasta, "C3-automatico-com-as-escolhidas")
        base.clique(j, t.paineis.automatico.botao_rodar)
    c.esperar_ate(lambda: len(j.acoes.feitas) > feitas and t._pronta(), 300)
    base.esperar(3.0)
    pr = j.projeto
    depois = filtros(pr)
    mudaram = [i + 1 for i, (a, b) in enumerate(zip(antes, depois)) if a != b]
    anotar("C-filtros", {"antes": antes, "depois": depois, "paginas_que_mudaram": mudaram,
                         "historico": j.acoes.feitas[-1].descricao})
    base.conferir(mudaram == [9, 11], f"C: só as páginas 9 e 11 mudaram ({mudaram})")
    c.p(j, pasta, "C4-depois")
    c.pdf_das_paginas(pr, [7, 8, 9, 10, 11], pasta, "C")
    base.fechar(j)
    base.gravar_resultados(pasta)


if __name__ == "__main__":
    main()
