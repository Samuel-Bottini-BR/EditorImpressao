"""Prints na janela de VERDADE da D-609 (04/11/2026; ramo dividir-arrastar-2026-11-04), no
Gradus Primus: folha 2 ainda inteira, a linha azul arrastada com o mouse do Windows para outro
lugar; "dividir esta" corta nesse lugar; Ctrl+Z volta. Também "Duas lado a lado" na folha 4.

Usa as funções do piloto dos ajustes de 03/11 (relatorios/dividir-ajustes/piloto.py): janela
fora da tela, cliques/arrastos/teclas por mensagens do Windows ao hwnd, prints por PrintWindow,
pasta de dados própria no scratchpad (nunca a pasta de dados do Samuel); o PDF do Gradus é
COPIADO (o original só é lido). Janela 1536 x 824.

Rodar (na cópia dividir-arrastar):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe relatorios\\dividir-arrastar\\piloto.py
"""
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "dividir-ajustes"))
import piloto as P  # noqa: E402

P.AQUI = AQUI
P.SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\C--Users-fotog"
                 r"\05fa28dc-c2f5-4152-b355-e6ab76bb386f\scratchpad\arrastar\dados-piloto")
P.LOG = open(AQUI / "anotacoes.txt", "w", encoding="utf-8")


def estado(j):
    from ui.tela_conferir import ABA_CORTE
    t = j.tela_conferir
    folha = j.projeto.folhas[t.indice_folha]
    vis = t.visualizadores[ABA_CORTE]
    return {**P.estado(j), "linha_arrasta": vis.corte_arrastavel,
            "linha_a_mao": folha.linha_a_mao, "acoes": len(j.acoes.feitas),
            "metades": [p.metade for p in j.projeto.paginas if p.folha == t.indice_folha]}


def arrastar_a_linha(j, para):
    """Aperta em cima da linha azul, leva até `para` (fração da folha) e solta (mouse do Windows)."""
    from PySide6.QtCore import QPoint
    from ui.tela_conferir import ABA_CORTE
    vis = j.tela_conferir.visualizadores[ABA_CORTE]
    a = vis._area
    y = int(a.top() + a.height() * 0.6)
    de = QPoint(int(a.left() + a.width() * vis.posicao_corte), y)
    ate = QPoint(int(a.left() + a.width() * para), y)
    P.base.arrastar(j, vis, de, ate)
    P.base.esperar(1.5)


def main():
    b = P.base
    b.preparar(str(AQUI.parents[1]), str(P.SCRATCH))
    destino = b.TRAB / "livros" / P.GRADUS.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(P.GRADUS, destino)
    j = b.nova_janela(1536, 824)
    j.abrir_livro(str(destino))
    P.esperar_tela(j)
    t = j.tela_conferir
    P.ferramenta_dividir(j)

    # --- folha 2 ainda inteira, "Uma página" (o a-54) ---------------------------------------
    P.ir_folha(j, 2)
    P.anotar("folha 2 inteira, a linha do motor", estado(j))
    P.p(j, "folha2-inteira-linha-do-motor")
    from ui.tela_conferir import ABA_CORTE
    motor = t.visualizadores[ABA_CORTE].posicao_corte
    arrastar_a_linha(j, 0.40)
    P.anotar("folha 2 depois de arrastar para 40%", estado(j))
    P.p(j, "folha2-inteira-linha-arrastada-para-40")
    b.clique(j, t.botao_nao_dividir); b.esperar(2)                 # dividir esta
    P.anotar("folha 2 depois do dividir esta", {**estado(j), "linha_do_motor_era": round(motor, 4)})
    P.p(j, "folha2-dividida-uma-pagina-metade-esquerda")
    P.mostrar(j, "duas")
    P.anotar("folha 2 dividida, Duas lado a lado", estado(j))
    P.p(j, "folha2-dividida-duas-lado-a-lado-corte-em-40")
    P.ctrl(j, ord("Z")); P.esperar_linha(j)
    P.anotar("Ctrl+Z (do corte)", estado(j))
    P.ctrl(j, ord("Z")); P.esperar_linha(j)
    P.anotar("Ctrl+Z (do arrasto): a linha do motor", estado(j))
    P.p(j, "folha2-depois-dos-dois-ctrl-z-linha-do-motor")
    P.ctrl(j, ord("Y")); P.esperar_linha(j)
    P.anotar("Ctrl+Y (o arrasto de novo)", estado(j))

    # --- folha 4 inteira em "Duas lado a lado" -----------------------------------------------
    P.ir_folha(j, 4)
    P.anotar("folha 4 inteira, Duas lado a lado", estado(j))
    arrastar_a_linha(j, 0.55)
    P.anotar("folha 4 depois de arrastar para 55%", estado(j))
    P.p(j, "folha4-duas-lado-a-lado-linha-arrastada-para-55")
    b.tecla(j, 0x27); P.esperar_linha(j)                           # seta → (D-608)
    P.anotar("seta direita depois de arrastar (D-608)", estado(j))
    j.close(); b.esperar(2)
    P.LOG.close()


if __name__ == "__main__":
    main()
