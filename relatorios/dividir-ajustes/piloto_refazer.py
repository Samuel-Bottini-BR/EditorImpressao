"""Print na janela de VERDADE (Gradus Primus, 1536 x 824, fora da tela, pasta de dados própria):
"dividir todas" → Ctrl+Z → Ctrl+Y (teclas do Windows) → "7 com dúvida" de volta.
Usa as funções de piloto.py. Rodar na cópia dividir-ajustes:
    D:\programas\EditorImpressao\.venv\Scripts\python.exe relatorios\dividir-ajustes\piloto_refazer.py"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import piloto as P  # noqa: E402

P.SCRATCH = Path(str(P.SCRATCH) + "-refazer")
P.LOG = open(P.AQUI / "anotacoes-refazer.txt", "w", encoding="utf-8")
P.N[0] = 8


def main():
    b = P.base
    b.preparar(str(P.RAIZ), str(P.SCRATCH))
    destino = b.TRAB / "livros" / P.GRADUS.name
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(P.GRADUS, destino)
    j = b.nova_janela(1536, 824)
    j.abrir_livro(str(destino))
    P.esperar_tela(j)
    t = j.tela_conferir
    P.ferramenta_dividir(j)
    P.anotar("ao abrir", P.estado(j))
    b.clique(j, t.botao_dividir_todas)
    P.esperar_dividir_todas(j)
    P.anotar("depois do dividir todas", P.estado(j))
    P.ctrl(j, ord("Z"))
    P.esperar_dividir_todas(j)
    P.anotar("depois do Ctrl+Z", P.estado(j))
    P.ctrl(j, ord("Y"))
    P.esperar_dividir_todas(j)
    P.anotar("depois do Ctrl+Y", P.estado(j))
    P.ir_folha(j, 7)
    P.anotar("folha 7 depois do Ctrl+Y", P.estado(j))
    P.p(j, "refazer-depois-do-ctrl-y-7-com-duvida")
    j.close(); b.esperar(2)
    P.LOG.close()


if __name__ == "__main__":
    main()
