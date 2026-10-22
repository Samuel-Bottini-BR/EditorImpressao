"""Prints da janela DE VERDADE: as miniaturas lembradas de um livro para o outro (22/10/2026).
No primeiro livro (cópia do Boécio), arrasta a alça das miniaturas para a esquerda com mensagens
do Windows, liga "Ver em pares" (menu dos três pontinhos) e fecha o programa. Abre o programa de
novo e outro livro (cópia do Palatino) e fotografa a tela de trabalho em 1280 x 657 (print de
1600 x 821 a 125%) e 1536 x 816 ("maximizada"). Depois fecha as miniaturas pela seta (clique do
Windows), abre o programa de novo e fotografa outra vez.
Serve para o código antigo e o novo. Uso: python prints_miniaturas_lembradas.py <pasta>
(arquivo descartável do agente de layout, em saida_teste/, que o git ignora)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_etapa3 import RESULTADOS, arrasto_nativo, clique_nativo, conferir  # noqa: E402
from prints_layout import ACERVO, LIVRO, TRAB, esperar, nova_janela  # noqa: E402

from PySide6.QtWidgets import QApplication  # noqa: E402

PALATINO = TRAB / "Palatino (copia).pdf"
shutil.copy2(ACERVO / "Giovambattista Palatino cittadino romano.pdf", PALATINO)
DESTINO = Path(".")


def abrir(janela, livro):
    janela.abrir_livro(str(livro))
    esperar(3)
    janela.analisar()
    tela = janela.tela_conferir
    for _ in range(300):
        if tela.projeto is not None:
            break
        esperar(1)
    esperar(6)
    while QApplication.activeModalWidget() is not None:    # "Este livro tem fundo separado..."
        QApplication.activeModalWidget().reject()
        esperar(1)
    tela.ir_para_pagina(4)
    esperar(6)
    return tela


def estado(tela):
    m = tela.miniaturas
    return f"lugar {m.lugar}, {'abertas' if m.aberta else 'fechadas'}, {'em pares' if m.em_pares else 'uma a uma'}"


def fotos(janela, tela, nome):
    for tamanho, sufixo in (((1280, 657), "1600x821"), ((1536, 816), "maximizada")):
        janela.resize(*tamanho)
        janela.move(-32000, -32000)
        esperar(3)
        janela.grab().save(str(DESTINO / f"{sufixo}-{nome}.png"))
        print(f"  {sufixo}-{nome}.png: {estado(tela)}", flush=True)


def principal() -> None:
    from ui.widgets.miniaturas import ESQUERDA

    janela = nova_janela()
    tela = abrir(janela, LIVRO)
    m = tela.miniaturas
    alvo = tela._retangulos_de_encaixe()[ESQUERDA].center()
    arrasto_nativo(janela, m.alca, m.alca.rect().center(), m.alca.mapFrom(tela, alvo))
    esperar(2)
    conferir(m.lugar == ESQUERDA, f"arrastar a alça (Windows) põe as miniaturas à esquerda ({m.lugar})")
    m.acao_em_pares.trigger()
    esperar(2)
    conferir(m.em_pares, "'Ver em pares' ligado")
    fotos(janela, tela, "1-primeiro-livro-arrumado")
    janela.close()
    esperar(2)

    janela = nova_janela()                       # o programa aberto de novo
    tela = abrir(janela, PALATINO)
    m = tela.miniaturas
    fotos(janela, tela, "2-outro-livro-depois-de-fechar-o-programa")
    conferir((m.lugar, m.em_pares) == (ESQUERDA, True),
             f"o outro livro abre com as miniaturas como ficaram: {estado(tela)}")
    clique_nativo(janela, m.seta)
    esperar(2)
    conferir(not m.aberta, "a seta (clique do Windows) fechou as miniaturas")
    janela.close()
    esperar(2)

    janela = nova_janela()
    tela = abrir(janela, LIVRO)
    fotos(janela, tela, "3-de-novo-fechadas")
    conferir(not tela.miniaturas.aberta and tela.miniaturas.lugar == ESQUERDA,
             f"abre de novo fechadas, à esquerda: {estado(tela)}")
    janela.close()
    esperar(1)
    falhas = [f for ok, f in RESULTADOS if not ok]
    print(f"\nconferências: {len(RESULTADOS) - len(falhas)} de {len(RESULTADOS)} certas")
    (DESTINO / "conferencias.txt").write_text("\n".join(
        ("ok   " if ok else "FALHOU ") + f for ok, f in RESULTADOS), encoding="utf-8")


if __name__ == "__main__":
    DESTINO = Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    principal()
    print("FIM", flush=True)
