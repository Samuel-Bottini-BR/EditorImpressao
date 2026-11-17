"""Piloto da tela dos livros (nm-tela-livros, nm-folha-pagina no livro aberto, au-d-489 o recomeço), na
janela de verdade fora da tela. Livros: CÓPIAS do "La vida eterna" (12 folhas) e do Palatino (folhas
20 a 31); o arquivo do Palatino é mudado de nome NA CÓPIA para o cartão dizer "o PDF saiu do lugar".

Janela 1: La vida eterna -> Automático "Dividir" -> página 3 em Preto e branco (o trabalho) ->
          Automático "Endireitar" (mudar uma etapa): o trabalho fica; Histórico. Palatino aberto.
Janela 2 (tela dos livros): cartões; busca "horas"; menu do cartão perdido; menu do La vida ->
          "remover da lista" (janela "Tirar da lista?", fechada sem tirar); "renomear" (janela,
          fechada); um clique no cartão -> o livro aberto (+ SIMULAÇÃO "folha"); "Mais...".
          Recomeço: (a) PDF trocado no mesmo lugar -> "continuar"; (b) "começar de novo" ->
          confirmar; (c) trabalho salvo estragado -> "continuar".
O "procurar de novo" NÃO é clicado: abre a janela do Windows de escolher arquivo, que apareceria na
tela do Samuel.
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum as c  # noqa: E402
from comum import anotar, base  # noqa: E402
import piloto_grade as g  # noqa: E402


def cartao(j, nome):
    from ui.tela_inicio import CartaoDeProjeto
    return next(k for k in j.tela_inicio.findChildren(CartaoDeProjeto)
                if k.isVisible() and k.resumo.nome == nome)


def botao_continuar(j, nome):
    from PySide6.QtWidgets import QPushButton
    k = cartao(j, nome)
    return next(b for b in k.findChildren(QPushButton) if b.text() == "continuar")


def clique_direito(j, widget):
    alvo = widget.mapTo(j, widget.rect().center())
    h, lp = int(j.winId()), base._lp(j, alvo)
    c.normal(j)
    base.user32.PostMessageW(h, base.WM_MOUSEMOVE, 0, lp); base.esperar(0.15)
    base.user32.PostMessageW(h, 0x0204, 2, lp); base.esperar(0.1)
    base.user32.PostMessageW(h, 0x0205, 0, lp); base.esperar(0.3)


def menu_do_cartao(j, pasta, nome_livro, nome_print, acao=None):
    """Botão direito no cartão: print do menu; com `acao`, escolhe esse item (pelo trigger do item,
    o mesmo do clique nele) depois do print."""
    def depois(m):
        if acao:
            item = next(a for a in m.actions() if a.text() == acao)
            m.close()
            item.trigger()
    base.print_do_menu_que_abrir(nome_print, pasta, pasta / "menus.txt", fechar=acao is None,
                                 depois=depois)
    clique_direito(j, cartao(j, nome_livro))
    base.esperar(3.0)


def main():
    pasta = c.preparar("livros")
    from PySide6.QtWidgets import QInputDialog, QMessageBox

    from core.filtros import PRETO_E_BRANCO

    vida = c.copia_da_vida(12)
    palatino = g.copia_do_palatino()

    # --- janela 1: o trabalho -------------------------------------------------------------
    j = base.nova_janela(1280, 657)
    t = c.abrir(j, vida)
    c.clicar_rodar(j, c.rodar_automatico(j, {"dividir"}))
    t = j.tela_conferir
    t.ir_para_pagina(2)
    c.esperar_previa(t)
    t.paineis.abrir("filtro")
    base.esperar(8.0)
    base.clique(j, t.paineis.filtro_da_pagina.cartoes[PRETO_E_BRANCO])
    c.esperar_previa(t)
    pr = j.projeto
    anotar("H0-pagina-3", pr.paginas[2].filtro)
    c.clicar_rodar(j, c.rodar_automatico(j, {"endireitar"}))
    t = j.tela_conferir
    pr = j.projeto
    t.ir_para_pagina(2)
    c.esperar_previa(t)
    t.paineis.abrir("historico")
    base.esperar(1.5)
    anotar("H1-depois-de-mudar-a-etapa", {"pagina_3": pr.paginas[2].filtro, "endireitar": pr.endireitar,
                                         "acoes": [a.descricao for a in j.acoes.feitas]})
    base.conferir(pr.paginas[2].filtro == PRETO_E_BRANCO,
                  "mudar uma etapa no Automático: a página 3 continua em Preto e branco")
    c.p(j, pasta, "H1-mudou-a-etapa-o-trabalho-ficou")
    c.abrir(j, palatino)
    base.fechar(j)
    perdido = palatino.with_name("Palatino-mudou-de-pasta.pdf")
    palatino.rename(perdido)                          # só a CÓPIA, na pasta de trabalho

    # --- janela 2: a tela dos livros -------------------------------------------------------
    j = base.nova_janela(1280, 657)
    ti = j.tela_inicio
    base.esperar(2.0)
    c.p(j, pasta, "L0-tela-dos-livros")
    base.clique(j, ti.busca)
    base.digitar(j, "horas", enter=False)
    base.esperar(1.0)
    c.p(j, pasta, "L1-busca-horas")
    ti.busca.clear()
    base.esperar(1.0)
    menu_do_cartao(j, pasta, "Palatino", "L2-menu-do-livro-perdido")
    base.quando_abrir_janela(QMessageBox, "L4-janela-tirar-da-lista", pasta, pasta / "janelas.txt")
    menu_do_cartao(j, pasta, "La vida eterna", "L3-menu-do-livro", acao="remover da lista")
    base.esperar(3.0)
    base.quando_abrir_janela(QInputDialog, "L5-janela-renomear", pasta, pasta / "janelas.txt")
    menu_do_cartao(j, pasta, "La vida eterna", "L5a-menu-renomear", acao="renomear")
    base.esperar(3.0)
    anotar("livros-na-lista", [r.nome for r in __import__("projetos").listar()])

    # o livro aberto (um clique no cartão)
    base.clique(j, cartao(j, "La vida eterna"))
    base.esperar(4.0)
    la = ti.livro_aberto
    anotar("L6-livro-aberto", {"detalhe": la.detalhe.text(), "pagina": la.rotulo_pagina.text(),
                               "ver_todas_dica": la.botao_todas.toolTip()})
    c.p(j, pasta, "L6-livro-aberto")
    antes = (la.detalhe.text(), la.rotulo_pagina.text())
    la.detalhe.setText(antes[0].replace("24 páginas", "12 folhas, 24 páginas"))
    la.rotulo_pagina.setText(antes[1].replace("página", "folha"))
    base.esperar(0.8)
    c.p(j, pasta, "L7-livro-aberto-SIMULACAO")
    la.detalhe.setText(antes[0])
    la.rotulo_pagina.setText(antes[1])
    base.print_do_menu_que_abrir("L8-menu-mais", pasta, pasta / "menus.txt")
    base.clique(j, la.botao_mais)
    base.esperar(3.0)
    ti.voltar_para_os_livros()
    base.esperar(2.0)

    # recomeço (a): o PDF trocado no mesmo lugar
    guardado = vida.with_name("La vida eterna - guardado.pdf")
    shutil.copy2(vida, guardado)
    import fitz
    with fitz.open(str(c.VIDA)) as livro, fitz.open() as novo:
        novo.insert_pdf(livro, from_page=20, to_page=29)
        novo.save(str(vida))                          # a CÓPIA trocada por outras 10 folhas
    base.quando_abrir_janela(QMessageBox, "R1-pdf-trocado", pasta, pasta / "janelas.txt")
    base.clique(j, botao_continuar(j, "La vida eterna"))
    base.esperar(6.0)
    anotar("R1-tela", j.telas.currentIndex())
    c.p(j, pasta, "R1b-depois-do-pdf-trocado")
    shutil.copy2(guardado, vida)                      # a cópia de volta
    if j.telas.currentIndex() != 0:
        j._sair_da_conferencia()
        base.esperar(2.0)
    ti.voltar_para_os_livros()
    base.esperar(2.0)

    # recomeço (b): "começar de novo" no menu do cartão
    base.quando_abrir_janela(QMessageBox, "R2-comecar-de-novo", pasta, pasta / "janelas.txt",
                             depois=lambda w: w.buttons() and next(
                                 (b for b in w.buttons() if b.text().startswith("Começar")), w.buttons()[0]).click(),
                             fechar=False)
    menu_do_cartao(j, pasta, "La vida eterna", "R2a-menu-comecar-de-novo", acao="começar de novo")
    base.esperar(10.0)
    t = j.tela_conferir
    pr = j.projeto
    if pr is not None and len(pr.paginas) > 2:
        t.ir_para_pagina(2)
        c.esperar_previa(t)
        t.paineis.abrir("historico")
        base.esperar(1.5)
        anotar("R2-depois", {"tela": j.telas.currentIndex(), "paginas": len(pr.paginas),
                             "pagina_3": pr.paginas[2].filtro, "acoes": [a.descricao for a in j.acoes.feitas]})
    c.p(j, pasta, "R2b-depois-de-comecar-de-novo")
    j._sair_da_conferencia()
    base.esperar(2.0)

    # recomeço (c): o trabalho salvo estragado (projeto.json que não dá para ler)
    resumo = next(r for r in __import__("projetos").listar() if r.nome == "La vida eterna")
    arq = Path(resumo.pasta) / "projeto.json"
    anotar("R3-projeto.json", str(arq))
    if arq.exists():
        arq.write_text("{ isto não é um trabalho salvo", encoding="utf-8")
    base.quando_abrir_janela(QMessageBox, "R3-trabalho-estragado", pasta, pasta / "janelas.txt")
    base.clique(j, botao_continuar(j, "La vida eterna"))
    base.esperar(10.0)
    anotar("R3-tela", j.telas.currentIndex())
    c.p(j, pasta, "R3b-depois-do-trabalho-estragado")
    base.fechar(j)
    base.gravar_resultados(pasta)


if __name__ == "__main__":
    main()
