"""Prints e conferência da janela DE VERDADE para a etapa 7 (tela dos livros, livro aberto, Configurações).
Uso: python prints_etapa7.py <pasta>   (arquivo descartável do agente de layout)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import prints_r14 as r  # noqa: E402
from prints_etapa3 import RESULTADOS, clique_nativo, conferir  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, Qt  # noqa: E402


def foto(janela, nome, contornos=()):
    cena = r.Cena(janela)
    pix = janela.grab()
    r.ESC = pix.devicePixelRatio()
    cena.img = pix.toImage()
    cena.img.setDevicePixelRatio(1)
    cena.inteira(nome, list(contornos))


def principal(destino: Path) -> None:
    from ui.janela_principal import CONFERIR, INICIO
    from ui.tela_configuracoes import TelaConfiguracoes
    from ui.tela_inicio import CartaoDeProjeto

    r.SAIDA = destino
    janela = nova_janela()
    inicio = janela.tela_inicio
    esperar(2)
    conferir(janela.telas.currentIndex() == INICIO and not janela.linha_dos_menus.isVisible(),
             "a tela dos livros abre sem a barra de menus")
    conferir(inicio.area.grande, "sem livro nenhum: a página vazia com o + grande")
    foto(janela, "1-sem-livro-nenhum")
    tela = abrir_o_livro(janela, dividir=True)
    conferir(janela.telas.currentIndex() == CONFERIR and janela.linha_dos_menus.isVisible(),
             "na tela de trabalho a barra de menus volta")
    tela.ir_para_pagina(4)
    esperar(3)
    janela._sair_da_conferencia()
    esperar(2)
    janela._voltar_das_opcoes()
    esperar(4)
    cartoes = [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent() is not None]
    conferir(janela.telas.currentIndex() == INICIO and len(cartoes) == 1 and not inicio.area.grande,
             "com um livro: o cartão + e o cartão do livro")
    foto(janela, "2-tela-dos-livros", [r.no_janela(inicio.area, janela)])
    clique_nativo(janela, cartoes[0], QPoint(20, 200))
    esperar(6)
    aberto = inicio.livro_aberto
    conferir(inicio.pilha.currentWidget() is aberto, "clique nativo no cartão: o livro na tela inteira")
    foto(janela, "3-livro-aberto")
    aberto.ir_para(10)
    esperar(4)
    conferir(aberto.paginas.atual == 10 and "11 de" in aberto.rotulo_pagina.text(),
             f"ir para a folha 11 ({aberto.rotulo_pagina.text()})")
    clique_nativo(janela, aberto.botao_lado_a_lado)
    esperar(5)
    conferir(aberto.paginas.lado_a_lado, "clique nativo em 'Ver lado a lado': pares rolando")
    foto(janela, "4-ver-lado-a-lado", [r.no_janela(aberto.botao_lado_a_lado, janela)])
    clique_nativo(janela, aberto.botao_lado_a_lado)
    clique_nativo(janela, aberto.botao_todas)
    esperar(8)
    conferir(aberto.pilha_do_meio.currentWidget() is aberto.todas, "'Ver todas as páginas': a grade")
    foto(janela, "5-ver-todas-as-paginas")
    aberto.todas.quadros[6].clicado.emit(6)
    esperar(3)
    conferir(aberto.pilha_do_meio.currentWidget() is aberto.paginas and aberto.paginas.atual == 6,
             "clique na folha 7 da grade: volta ao folhear nela")
    from PySide6.QtTest import QTest
    QTest.keyClick(aberto, Qt.Key_Escape)
    esperar(3)
    marcados = [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent() is not None and c.marcado]
    conferir(inicio.pilha.currentIndex() == 0 and len(marcados) == 1,
             "Esc volta para os livros, com o último marcado em azul")
    foto(janela, "6-de-volta-com-o-ultimo-marcado")
    # Configurações
    abertas = []
    TelaConfiguracoes.exec = lambda self: (abertas.append(self), self.setAttribute(Qt.WA_ShowWithoutActivating),
                                           self.move(-32000, -32000), self.show(), self.move(-32000, -32000), 0)[-1]
    clique_nativo(janela, inicio.botao_configuracoes)
    esperar(2)
    conferir(len(abertas) == 1, "clique nativo em 'Configurações' abre as Configurações")
    d = abertas[0]
    foto(d, "7-configuracoes-aparencia")
    d.botoes_tema["claro"].click()
    esperar(2)
    conferir(janela.menu.acoes["tema_claro"].isChecked(), "tema claro nas Configurações marcou o menu Ver")
    foto(janela, "8-tela-dos-livros-claro")
    d.lista.setCurrentRow(1)
    esperar(1)
    foto(d, "7-configuracoes-atalhos")
    d.botoes_tema["cinza"].click()
    d.accept()
    janela.resize(1000, 600)
    janela.move(-32000, -32000)
    esperar(2)
    foto(janela, "9-minima-livros")
    inicio.abrir_o_livro(cartoes[0].resumo if cartoes[0].parent() else
                         [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent()][0].resumo)
    esperar(5)
    foto(janela, "9-minima-livro-aberto")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)


if __name__ == "__main__":
    destino = Path(sys.argv[1])
    destino.mkdir(parents=True, exist_ok=True)
    principal(destino)
    print("FIM", flush=True)
