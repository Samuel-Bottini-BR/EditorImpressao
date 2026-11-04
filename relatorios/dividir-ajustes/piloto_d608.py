"""Print na janela de VERDADE (Gradus Primus, 1536 x 824, fora da tela, pasta de dados própria),
D-608: "Duas lado a lado", clique em "dividir esta" (mouse do Windows), tecla → (teclado do
Windows): a folha seguinte aparece. Usa as funções de piloto.py. Rodar na cópia dividir-ajustes:
    D:\programas\EditorImpressao\.venv\Scripts\python.exe relatorios\dividir-ajustes\piloto_d608.py"""
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import piloto as P  # noqa: E402

P.SCRATCH = Path(str(P.SCRATCH) + "-d608")
P.LOG = open(P.AQUI / "anotacoes-d608.txt", "w", encoding="utf-8")
P.N[0] = 9


def main():
    from PySide6.QtWidgets import QApplication

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
    P.ir_folha(j, 5)
    P.mostrar(j, "duas")
    b.clique(j, t.botao_nao_dividir); b.esperar(2)          # dividir esta
    P.anotar("depois do clique em dividir esta", {**P.estado(j),
              "teclado_com": type(j.focusWidget()).__name__,
              "texto_de_quem_tem_o_teclado": getattr(j.focusWidget(), "text", lambda: "")()})
    P.p(j, "d608-folha5-depois-de-clicar-dividir-esta")
    b.tecla(j, 0x27); P.esperar_linha(j)                     # →
    P.anotar("depois da seta direita", P.estado(j))
    P.p(j, "d608-seta-direita-foi-para-a-folha-6")
    b.tecla(j, 0x25); P.esperar_linha(j)                     # ←
    P.anotar("depois da seta esquerda", P.estado(j))
    j.close(); b.esperar(2)
    P.LOG.close()


if __name__ == "__main__":
    main()
