"""Imagens do item 4 (n0411-o-que-vai-sair): o quadro "O que vai sair" do "Montar para imprimir"."""
from __future__ import annotations

import json

from montar import (AZUL, CRU, LARGURA, VERDE, abrir, cabeca, circular, com_moldura, empilhar,
                    largura, retangulo, salvar, titulo)

P = CRU / "p4"
E = 1.25          # o print tem 125% (janela 1000 x 617 = 1250 x 771 pontos)


def px(caixa):
    x, y, l, a = caixa
    return (round(x * E), round(y * E), round((x + l) * E), round((y + a) * E))


def main():
    n = json.loads((P / "notas.json").read_text(encoding="utf-8"))
    a = abrir(P / "a-como-abre.png")
    lado = px(n["a: lado direito (x,y,l,a)"])
    # o pé do lado direito (onde o quadro fica, fora da vista) e a barra de rolagem
    a = retangulo(a, (lado[0] - 6, lado[3] - 70, lado[2] + 40, lado[3] + 10), grossura=6)
    a = circular(a, (1208, 90, 1228, 680), folga=10, grossura=5)
    b = abrir(P / "b-rolado.png")
    t, q = px(n["b: titulo (x,y,l,a)"]), px(n["b: quadro (x,y,l,a)"])
    b = retangulo(b, (t[0] - 10, t[1] - 10, q[2] + 10, q[3] + 8), grossura=6)   # sem riscar o texto
    texto = n["texto do quadro"].replace("\n\n", " ")
    img_a = empilhar([
        cabeca("COMO ABRE", AZUL,
               "\"Montar para imprimir\" (a janela que \"Ficou pronto!\" abre), tamanho de fábrica "
               "(1000 x 617), Palatino processado (134 páginas), opções de fábrica. O quadro \"O que "
               "vai sair\" fica no pé do lado direito, FORA da vista: nem o título dele aparece "
               "(quadro vermelho, onde ele está escondido). Só a barra de rolagem da direita (círculo) "
               "mostra que tem mais coisa embaixo."),
        com_moldura(largura(a, LARGURA - 40)),
    ])
    salvar(img_a, "4-o-que-vai-sair-a-como-abre.png",
           "Como abre o \"Montar para imprimir\" (tamanho de fábrica): o quadro \"O que vai sair\" fica "
           "fora da vista, no pé do lado direito; nem o título aparece, só a barra de rolagem indica.")
    img_b = empilhar([
        cabeca("ROLADO ATÉ O FIM", VERDE,
               "O lado direito rolado até embaixo: o quadro \"O que vai sair\" aparece inteiro "
               "(quadro vermelho). É o resumo, em palavras, do arquivo que vai ser gravado com as escolhas da "
               "esquerda. Neste exemplo diz: \"" + texto + "\""),
        com_moldura(largura(b, LARGURA - 40)),
    ])
    salvar(img_b, "4-o-que-vai-sair-b-rolado.png",
           "O lado direito rolado até embaixo: o quadro \"O que vai sair\" inteiro. Exemplo do Palatino: "
           + texto)


if __name__ == "__main__":
    main()
