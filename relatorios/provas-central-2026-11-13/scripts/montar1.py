"""Imagens do item 1 (ac-tampa): a faixa preta da tampa do scanner some pelo Automático."""
from __future__ import annotations

import json

from montar import (marcar_o_alto, AZUL, CRU, ESCURO, LARANJA, LARGURA, VERDE, abrir, caber, cabeca, caixa_da_pagina,
                    circular, com_moldura, empilhar, faixa_preta_em_cima, lado_a_lado, largura,
                    legenda_em_cima, retangulo, salvar, titulo)

P = CRU / "p1"
CAMINHO = ("Righetti, folha 96 (páginas impressas 452 e 453). Caminho: girada ¼ à esquerda, "
           "Automático com 1 Dividir + 2 Endireitar + 3 Cortar as bordas, opções de fábrica.")


def a_onde_fica():
    tela = abrir(P / "automatico-cortar-cortar.png")
    # a linha "O que fica fora da página: cortar fora" (x 385-825, y 352-400 no print de 1600)
    tela = circular(tela, (380, 350, 830, 402), folga=16)
    tela = retangulo(tela, (16, 282, 349, 352), grossura=5)          # a etapa 3 escolhida
    tela = com_moldura(largura(tela, LARGURA - 40))
    pintar = abrir(P / "automatico-cortar-pintar.png").crop((370, 340, 1100, 412))
    cortar = abrir(P / "automatico-cortar-cortar.png").crop((370, 340, 1100, 412))
    duas = lado_a_lado([legenda_em_cima(com_moldura(cortar), "1ª rodada: cortar fora (de fábrica)"),
                        legenda_em_cima(com_moldura(pintar), "2ª rodada: pintar de branco")])
    duas = caber(duas, LARGURA - 40, 400)
    img = empilhar([
        cabeca("ONDE FICA A ESCOLHA", ESCURO,
               "Janela do Automático (\"O que o automático vai fazer\"), etapa 3 \"Cortar as bordas\" "
               "(quadro vermelho). Em vermelho, a escolha \"O que fica fora da página\": \"cortar fora\" "
               "(de fábrica) ou \"pintar de branco\". A explicação dela diz que vale para a borda preta "
               "e para a faixa preta da tampa do scanner. Programa de hoje, janela 1280 x 657."),
        tela,
        titulo("As duas escolhas, como ficaram nas duas rodadas deste teste:"),
        duas,
    ])
    salvar(img, "1-tampa-a-onde-fica-a-escolha.png",
           "Onde fica a escolha: Automático, etapa 3 \"Cortar as bordas\", \"O que fica fora da página: "
           "cortar fora / pintar de branco\" (vale para a borda preta e para a faixa da tampa).")


def _pagina_da_tela(nome: str, alto: int = 520):
    img = abrir(P / nome)
    cx = caixa_da_pagina(img, area=(55, 48, 1545, 588))
    pg = caber(img.crop(cx), 640, alto)
    return marcar_o_alto(com_moldura(pg), texto="sem faixa preta")


def b_na_tela():
    antes = abrir(P / "tela-antes-girada.png")
    cx = caixa_da_pagina(antes, area=(55, 48, 1545, 525))   # acima da faixa "Livro novo"
    pg = antes.crop(cx)
    faixa = faixa_preta_em_cima(pg)
    pg = caber(pg, 1000, 560)
    esc = pg.height / (cx[3] - cx[1])
    if faixa:
        pg = circular(pg, (8, int(faixa[0] * esc), pg.width - 8, int(faixa[1] * esc)), folga=10)
    img = empilhar([
        cabeca("ANTES do Automático", AZUL,
               "Na tela (área de trabalho), a folha 96 já girada, antes de rodar o Automático. Em "
               "vermelho, a faixa preta da tampa do scanner em cima das duas páginas."),
        com_moldura(pg),
        cabeca("DEPOIS — \"cortar fora\"", VERDE,
               "Na tela, depois do Automático com \"cortar fora\": a página 452 (esquerda) e a 453 "
               "(direita). Em vermelho, o alto da página: a faixa preta sumiu nas duas."),
        lado_a_lado([legenda_em_cima(_pagina_da_tela("tela-depois-cortar-esq.png"), "página 452"),
                     legenda_em_cima(_pagina_da_tela("tela-depois-cortar-dir.png"), "página 453")]),
        cabeca("DEPOIS — \"pintar de branco\"", VERDE,
               "O mesmo livro, do zero, com \"pintar de branco\". Em vermelho, o alto da página: a "
               "faixa preta sumiu nas duas."),
        lado_a_lado([legenda_em_cima(_pagina_da_tela("tela-depois-pintar-esq.png"), "página 452"),
                     legenda_em_cima(_pagina_da_tela("tela-depois-pintar-dir.png"), "página 453")]),
    ])
    salvar(img, "1-tampa-b-na-tela.png",
           "Na tela: antes (azul) a faixa preta da tampa em cima da folha 96; depois do Automático, com "
           "\"cortar fora\" e com \"pintar de branco\" (verde), a faixa sumiu nas páginas 452 e 453.")


def _pagina_do_pdf(nome: str, alto: int = 560):
    pg = caber(abrir(P / nome), 640, alto)
    return marcar_o_alto(com_moldura(pg), texto="sem faixa preta")


def c_no_pdf():
    notas = {}
    for m in ("cortar", "pintar"):
        notas.update(json.loads((P / f"notas-{m}.json").read_text(encoding="utf-8")))
    antes = abrir(P / "pdf-antes-folha96.png")
    faixa = faixa_preta_em_cima(antes)
    pg = caber(antes, 1100, 560)
    esc = pg.height / antes.height
    if faixa:
        pg = circular(pg, (8, int(faixa[0] * esc), pg.width - 8, int(faixa[1] * esc)), folga=10)
    img = empilhar([
        cabeca("ANTES do Automático", AZUL,
               "No PDF, a folha 96 girada, sem passar pelo Automático (sai inteira, sem dividir). Em "
               "vermelho, a faixa preta da tampa do scanner."),
        com_moldura(pg),
        cabeca("DEPOIS — \"cortar fora\"", VERDE,
               "No PDF, depois do Automático com \"cortar fora\": páginas 452 e 453. Em vermelho, o "
               "alto da página: sem faixa preta. (O preto do lado esquerdo da 452 é outra coisa: "
               "ver a imagem 1-tampa-d.)"),
        lado_a_lado([legenda_em_cima(_pagina_do_pdf("pdf-cortar-esq.png"), "página 452"),
                     legenda_em_cima(_pagina_do_pdf("pdf-cortar-dir.png"), "página 453")]),
        cabeca("DEPOIS — \"pintar de branco\"", VERDE,
               "No PDF, o mesmo livro do zero com \"pintar de branco\": páginas 452 e 453. Em "
               "vermelho, o alto da página: sem faixa preta."),
        lado_a_lado([legenda_em_cima(_pagina_do_pdf("pdf-pintar-esq.png"), "página 452"),
                     legenda_em_cima(_pagina_do_pdf("pdf-pintar-dir.png"), "página 453")]),
    ])
    salvar(img, "1-tampa-c-no-pdf.png",
           "No PDF: antes (azul) a faixa preta da tampa em cima da folha 96; depois do Automático, com "
           "\"cortar fora\" e com \"pintar de branco\" (verde), as páginas 452 e 453 saem sem a faixa.")


def d_preto_do_lado():
    sem = caber(abrir(P / "pdf-cortar-esq.png"), 640, 600)
    sem = circular(sem, (4, int(sem.height * 0.05), int(sem.width * 0.27), sem.height - 4), folga=4)
    com = caber(abrir(P / "pdf-cortar_borda-esq.png"), 640, 600)
    img = empilhar([
        cabeca("O QUE CONTINUA: o preto do lado", LARANJA,
               "Página 452 no PDF, \"cortar fora\". A faixa da tampa (em cima) sumiu, mas o preto do "
               "LADO esquerdo (o fundo do scanner, em vermelho) continua. Ele não é a tampa: é a "
               "\"borda preta do scanner\", que só sai com a caixinha \"Achar a página dentro da borda "
               "preta do scanner\", desligada de fábrica (decisão G7)."),
        lado_a_lado([
            legenda_em_cima(com_moldura(sem), "caixinha da borda preta desligada (fábrica)"),
            legenda_em_cima(com_moldura(com), "caixinha da borda preta ligada"),
        ]),
        titulo("À direita, a mesma página com a caixinha \"Achar a página dentro da borda preta do "
               "scanner\" ligada no Automático (etapa 3), também \"cortar fora\": sai sem a faixa "
               "de cima e sem o preto do lado.", tamanho=24),
    ])
    salvar(img, "1-tampa-d-preto-do-lado.png",
           "Página 452: a faixa da tampa sumiu, mas o preto do lado (fundo do scanner) continua com a "
           "caixinha da borda preta desligada (fábrica); com ela ligada, sai também.")


if __name__ == "__main__":
    a_onde_fica()
    b_na_tela()
    c_no_pdf()
    d_preto_do_lado()
