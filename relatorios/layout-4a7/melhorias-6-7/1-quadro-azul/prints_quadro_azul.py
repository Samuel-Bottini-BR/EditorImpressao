"""Prints da janela DE VERDADE: o quadro azul de "Todas as páginas" em "Duas lado a lado"
(melhoria do layout 6 e 7, 22/10/2026). Abre uma CÓPIA do Graduale, clica no cartão, em
"Duas lado a lado" e em "Ver todas as páginas" com mensagens do Windows, vai à folha 301
(a da direita do par 300-301) e fotografa a grade em 1280 x 657 (print de 1600 x 821 a 125%)
e "maximizada" (1536 x 816). Diz qual quadro ficou azul.
Serve para o código antigo e o novo. Uso: python prints_quadro_azul.py <pasta>
(arquivo descartável do agente de layout, em saida_teste/, que o git ignora)."""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from prints_etapa3 import RESULTADOS, clique_nativo, conferir  # noqa: E402
from prints_layout import ACERVO, TRAB, esperar, nova_janela  # noqa: E402

from PySide6.QtCore import QPoint  # noqa: E402

GRADUALE = TRAB / "Graduale (copia).pdf"
shutil.copy2(ACERVO / "Graduale - Saeculum XIV.pdf", GRADUALE)   # o original nunca é aberto
DESTINO = Path(".")


def principal() -> None:
    from ui.tela_inicio import CartaoDeProjeto

    janela = nova_janela()
    inicio = janela.tela_inicio
    janela.abrir_livro(str(GRADUALE))
    esperar(6)
    janela._voltar_das_opcoes()
    esperar(4)
    cartoes = [c for c in inicio.findChildren(CartaoDeProjeto) if c.parent() is not None]
    clique_nativo(janela, cartoes[0], QPoint(20, 200))
    esperar(5)
    aberto = inicio.livro_aberto
    conferir(inicio.pilha.currentWidget() is aberto, "clique nativo no cartão: o livro aberto")
    clique_nativo(janela, aberto.botoes_mostrar["duas"])
    esperar(2)
    for tamanho, sufixo in (((1280, 657), "1600x821"), ((1536, 816), "maximizada")):
        janela.resize(*tamanho)
        janela.move(-32000, -32000)
        esperar(2)
        aberto.campo_ir.setValue(301)            # o "ir para" da pílula, como o Kaique digita
        aberto.campo_ir.editingFinished.emit()
        esperar(8)
        conferir(aberto.paginas.lado_a_lado, f"{sufixo}: duas lado a lado ligado")
        janela.grab().save(str(DESTINO / f"{sufixo}-1-livro-na-301.png"))
        pilula = aberto.rotulo_pagina.text()
        clique_nativo(janela, aberto.botao_todas)
        esperar(20)
        q = next(q for q in aberto.todas.quadros if q.itens[0].indice == 300)
        aberto.todas.rolagem.ensureWidgetVisible(q)
        esperar(3)
        janela.grab().save(str(DESTINO / f"{sufixo}-2-todas-as-paginas.png"))
        azuis = [q.itens[0].indice + 1 for q in aberto.todas.quadros if q.atual]
        print(f"  {sufixo}: pílula '{pilula}', quadro azul na {azuis}", flush=True)
        conferir(azuis == [301], f"{sufixo}: pílula '{pilula}'; o quadro azul está na {azuis} (tem de ser 301)")
        aberto._voltar_da_grade(None)
        esperar(2)
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
