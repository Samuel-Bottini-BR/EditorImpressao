"""Prints e conferência da janela DE VERDADE: a tela cheia dos filtros com todas as opções
(22/10/2026, quadro l67-tela-cheia) e as caixinhas da Fase 2 no painel Filtro (Mais ajustes).
Cliques por mensagens nativas do Windows. Uso: python prints_tela_cheia_opcoes.py <pasta>
(arquivo descartável do agente de layout, em saida_teste/, que o git ignora)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_etapa3 import RESULTADOS, clicar_no_icone, clique_nativo, conferir  # noqa: E402
from prints_layout import abrir_o_livro, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint, Qt  # noqa: E402

ABERTAS = []
DESTINO = Path(".")


def foto(widget, nome):
    pix = widget.grab()
    pix.save(str(DESTINO / f"{nome}.png"))
    print(f"  {nome}.png ({pix.width()} x {pix.height()})", flush=True)


def principal() -> None:
    from core.filtros import MELHORAR, PRETO_E_BRANCO
    from core import preto_e_branco_scantailor
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    def exec_sem_travar(self):
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.move(-32000, -32000)
        self.show()
        self.move(-32000, -32000)
        ABERTAS.append(self)
        return 0

    FiltrosEmTelaCheia.exec = exec_sem_travar
    janela = nova_janela()
    tela = abrir_o_livro(janela, dividir=True)
    tela.ir_para_pagina(6)                       # do miolo
    esperar(6)
    clicar_no_icone(janela, tela, "filtro")
    esperar(5)
    painel = tela.paineis.filtro_da_pagina
    tela._escolher_filtro(PRETO_E_BRANCO)
    esperar(6)
    parte = painel.partes["mais"]
    if not parte.corpo.isVisible():
        parte.alternar()
    esperar(2)
    conferir(tela.caixa_claro_no_escuro.isVisible() and tela.caixa_reduzir_cores.isVisible()
             and tela.caixa_letras_com_a_cor.isVisible() and tela.seletor_algoritmo_pb.isVisible(),
             "painel Filtro, Preto e branco: o jeito do preto e branco e as três caixinhas em Mais ajustes")
    foto(janela, "1-painel-filtro-mais-ajustes")
    pagina = janela.projeto.paginas[tela.indice_pagina]
    clique_nativo(janela, painel.botao_tela_cheia)
    esperar(10)
    conferir(len(ABERTAS) == 1, "clique nativo no ícone do título abriu a tela cheia")
    d = ABERTAS[0]
    d.resize(1280, 657)
    d.move(-32000, -32000)
    esperar(10)
    conferir(all(not d.partes_das_opcoes[t].isHidden() for t in ("Só as letras", "Limpar a sujeira",
                                                                 "Mais ajustes")),
             "tela cheia no Preto e branco: Só as letras, Limpar a sujeira e Mais ajustes à direita")
    foto(d, "2-tela-cheia-preto-e-branco")
    d.partes_das_opcoes["Mais ajustes"].parentWidget().parentWidget().parentWidget().ensureWidgetVisible(
        d.caixas["reduzir_cores"])
    esperar(1)
    clique_nativo(d, d.caixas["reduzir_cores"], QPoint(8, d.caixas["reduzir_cores"].height() // 2))
    esperar(1)
    conferir(d.opcoes.get("reduzir_cores") is True and not pagina.reduzir_cores,
             "clique nativo em 'Reduzir cores' na tela cheia: guardado, a página não mudou")
    jeito = preto_e_branco_scantailor.CODIGOS[1]
    d.seletor_algoritmo_pb.setCurrentIndex(d.seletor_algoritmo_pb.findData(jeito))
    esperar(15)
    conferir(d.vista.depois is not None and "Mexido aqui" in d.frase_do_ajuste.text(),
             "com opções mexidas, a página grande refeita e a frase do 'Mexido aqui'")
    foto(d, "3-tela-cheia-opcoes-mexidas")
    clique_nativo(d, d.botao_usar)
    esperar(6)
    conferir(pagina.reduzir_cores and pagina.algoritmo_preto_branco == jeito,
             "clique nativo em 'Usar Preto e branco': as opções gravadas na página")
    for _ in range(4):
        tela.desfazer()
    esperar(3)
    conferir(not pagina.reduzir_cores, "desfazer volta as opções")
    janela.menu.acoes["filtros_tela_cheia"].trigger()
    esperar(6)
    d2 = ABERTAS[-1]
    d2.resize(1280, 657)
    d2.move(-32000, -32000)
    clique_nativo(d2, d2.cartoes[MELHORAR])
    esperar(10)
    conferir(d2.escolhido == MELHORAR and d2.partes_das_opcoes["Só as letras"].isHidden()
             and not d2.caixas["claro_no_escuro"].isHidden(),
             "no Melhorar: só o ajuste, Letra clara em fundo escuro e Reduzir cores")
    foto(d2, "4-tela-cheia-melhorar")
    d2.resize(1000, 600)
    d2.move(-32000, -32000)
    clique_nativo(d2, d2.cartoes[PRETO_E_BRANCO])
    esperar(8)
    foto(d2, "5-tela-cheia-janela-minima")
    d2.reject()
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    for f in falhas:
        print("  FALHOU:", f)
    (DESTINO / "conferencias.txt").write_text("\n".join(
        ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


if __name__ == "__main__":
    DESTINO = Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    principal()
    print("FIM", flush=True)
