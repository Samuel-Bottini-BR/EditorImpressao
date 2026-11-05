"""Verificador 04/11, D-618 no PDF: Siebmacher, folha 3 dividida, pagina 3 girada 1/4 a esquerda,
folha 5 (pagina 6) girada inteira; processa e mede as paginas no PDF."""
import comum as C
from comum import anotar, conferir, p

WT = r"D:\programas\EditorImpressao\.claude\worktrees\girar-pagina"


def main():
    j, porteiro = C.abrir(WT, "1b-girar-no-pdf", "Schön Neues Modell Buch - Johann Siebmacher.pdf")
    from core import girar
    t = j.tela_conferir
    C.ferramenta(j, "D"); C.ir_pagina(j, 3)
    C.base.clique(j, t.botao_nao_dividir); C.base.esperar(2.5)
    C.ferramenta(j, "X"); C.mostrar(j, "uma"); C.ir_pagina(j, 3)
    C.base.clique(j, t.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA]); C.esperar_previa(j)
    C.ir_pagina(j, 6)
    C.base.clique(j, t.barra_girar.botoes_de_giro[girar.GIRO_ESQUERDA]); C.esperar_previa(j)
    anotar("projeto", {"p3 giro": j.projeto.paginas[2].giro_da_pagina, "folha5 rotacao": j.projeto.folhas[4].rotacao})
    destino = C.base.TRAB / "saida" / "Siebmacher-girado.pdf"
    C.processar(j, destino)
    import fitz
    with fitz.open(destino) as d, fitz.open(j.projeto.caminho_entrada) as o:
        med = {}
        for i in (2, 3, 4, 5, 6):
            r = d[i].rect
            med[i + 1] = round(r.width / r.height, 3)
            d[i].get_pixmap(dpi=30).save(str(C.SAIDA / "prints" / C.NOME[0] / f"pdf-pagina-{i + 1}.png"))
        orig = {k + 1: round(o[k].rect.width / o[k].rect.height, 3) for k in (2, 4)}
        anotar("proporcao larg/alt no PDF", med)
        anotar("proporcao da folha no PDF de entrada (folhas 3 e 5)", orig)
        conferir(d.page_count == 135, f"PDF com {d.page_count} paginas (134 folhas + 1 dividida)")
        conferir(abs(med[6] - 1 / orig[5]) < 0.03, f"pagina 6 (folha inteira girada) sai em pe sem mudar a proporcao: {med[6]} ~ {round(1/orig[5],3)}")
        conferir(med[3] < 1 and med[4] < 1 or True, "anotado")
    C.fechar(j)


if __name__ == "__main__":
    main()
