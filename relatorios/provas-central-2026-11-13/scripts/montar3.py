"""Imagens do item 3 (n0411-caderno-pagina-em-branco; D-604)."""
from __future__ import annotations

from montar import (CRU, ESCURO, LARANJA, LARGURA, VERDE, abrir, cabeca, circular, com_moldura,
                    empilhar, largura, retangulo, salvar, titulo)


def gradus():
    tela = abrir(CRU / "p3" / "02-ultima-folha.png")
    tela = retangulo(tela, (1110, 116, 1590, 146), grossura=5)
    tela = retangulo(tela, (1110, 371, 1590, 401), grossura=5)
    tela = circular(tela, (24, 708, 590, 738), folga=10, grossura=5)
    img = empilhar([
        cabeca("GRADUS DIVIDIDO: nenhum lugar sem página", LARANJA,
               "Gradus Primus (cópia), aberto do zero, Automático só com \"Dividir folhas ao meio\" "
               "(fábrica): 70 folhas viram 140 páginas. Etapa 7 \"Montar cadernos\", 20 páginas por "
               "caderno (fábrica): 140 = 7 cadernos cheios, 35 folhas de papel. A última folha (35 de "
               "35) diz \"frente: páginas 132 e 129\" e \"verso: páginas 130 e 131\" (quadros "
               "vermelhos). Nenhuma folha do livro dividido tem lugar sem página; por isso a folha "
               "com lugar vazio vem do Righetti, na próxima imagem."),
        com_moldura(largura(tela, LARGURA - 40)),
    ])
    salvar(img, "3-caderno-a-gradus-dividido-sem-lugar-vazio.png",
           "Gradus dividido pelo Automático: 140 páginas = 7 cadernos de 20 cheios; a última folha "
           "(35 de 35) é \"frente: páginas 132 e 129 / verso: páginas 130 e 131\". Não há lugar sem "
           "página nesse livro.")


def righetti():
    tela = abrir(CRU / "p3-righetti" / "03-folha-com-lugar-sem-pagina.png")
    tela = retangulo(tela, (1110, 116, 1590, 146), grossura=5)
    tela = retangulo(tela, (1110, 371, 1590, 401), grossura=5)
    tela = circular(tela, (1150, 150, 1350, 364), folga=6, grossura=6)     # o lugar vazio da frente
    tela = circular(tela, (1352, 405, 1552, 619), folga=6, grossura=6)     # o lugar vazio do verso
    img = empilhar([
        cabeca("LIVRO DIVIDIDO COM LUGAR SEM PÁGINA", VERDE,
               "Righetti (cópia inteira), aberto do zero, folhas giradas ¼ à esquerda, Automático só "
               "com \"Dividir folhas ao meio\" (fábrica): 135 folhas viram 270 páginas. Etapa 7, 20 "
               "páginas por caderno: o último caderno tem 10 páginas em 12 lugares. Na folha 66 de 68: "
               "\"frente: páginas em branco e 261\" e \"verso: páginas 262 e em branco\" (quadros "
               "vermelhos). Os lugares sem página saem brancos (círculos)."),
        com_moldura(largura(tela, LARGURA - 40)),
        titulo("As outras folhas desse último caderno: folha 67 de 68 — frente: páginas 270 e 263 · "
               "verso: páginas 264 e 269. Folha 68 de 68 — frente: páginas 268 e 265 · verso: "
               "páginas 266 e 267.", tamanho=24),
    ])
    salvar(img, "3-caderno-b-righetti-folha-com-lugar-sem-pagina.png",
           "Righetti dividido (270 páginas), etapa 7, folha 66 de 68: \"frente: páginas em branco e "
           "261\" e \"verso: páginas 262 e em branco\"; os dois lugares sem página saem brancos.")


if __name__ == "__main__":
    gradus()
    righetti()
