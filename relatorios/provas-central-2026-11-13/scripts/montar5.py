"""Imagem do item 5 (v-capa; D-693): pares trocados no "Duas lado a lado" (só o problema)."""
from __future__ import annotations

from montar import (AZUL, CRU, LARGURA, abrir, cabeca, circular, com_moldura, empilhar, lado_a_lado,
                    largura, legenda_em_cima, retangulo, salvar)

P = CRU / "p5"
AREA = (420, 62, 1170, 570)      # as duas páginas na área de trabalho (print de 1600 x 821)


def numero(img, x, y, r=19):
    return circular(img, (x - r, y - r, x + r, y + r), folga=0, grossura=6)


def par(nome, numeros, rotulo):
    img = abrir(P / nome)
    for x, y in numeros:
        img = numero(img, x, y)
    return legenda_em_cima(com_moldura(largura(img.crop(AREA), 715)), rotulo, tamanho=24)


def main():
    janela = abrir(P / "tela-duas-04-paginas-7-8.png")
    janela = numero(janela, 617, 470)
    janela = numero(janela, 1038, 456)
    janela = retangulo(janela, (913, 787, 1048, 819), grossura=5)        # "Duas lado a lado"
    img = empilhar([
        cabeca("COMO É HOJE: a ímpar fica à esquerda", AZUL,
               "La vida eterna (cópia), aberto do zero, Automático só com \"Dividir folhas ao meio\" "
               "(180 folhas = 360 páginas). Área de trabalho em \"Duas lado a lado\" (quadro vermelho "
               "embaixo). Páginas 6 e 7 do PDF: o número impresso 7 (ímpar) aparece à ESQUERDA e o 8 "
               "à direita (círculos). Num livro aberto, a ímpar fica à direita."),
        com_moldura(largura(janela, LARGURA - 40)),
        lado_a_lado([
            par("tela-duas-pagina-9.png", [(634, 442)],
                "PDF 8 e 9: impressa 9 à esquerda; à direita a página em branco (seria a 10)"),
            par("tela-duas-pagina-11.png", [(625, 457), (1004, 540)],
                "PDF 10 e 11: impressa 11 à esquerda, 12 à direita"),
        ], espaco=20),
    ])
    salvar(img, "5-pares-trocados-duas-lado-a-lado.png",
           "La vida eterna dividido, \"Duas lado a lado\": nos pares 6-7, 8-9 e 10-11 do PDF a página "
           "de número impresso ímpar (7, 9, 11) aparece à esquerda; num livro aberto ela fica à direita.")


if __name__ == "__main__":
    main()
