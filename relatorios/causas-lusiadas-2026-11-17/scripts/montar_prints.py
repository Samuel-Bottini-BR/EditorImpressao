"""Implementador, 17/11/2026: os prints das respostas (modelo do girar, CLAUDE.md §10), a partir de:
  - ../prints/decompor/ (decompor_marcacao.py: a página preparada pelo caminho inteiro, a marcação e a
    página como sai em cada filtro, pela conta do programa no DPI do PDF);
  - os prints e as análises do estudo de 14/11 (ramo lusiadas-provas: tela de verdade fora da tela do
    Samuel, e o PDF que o programa gravou).
Saída em ../prints/ (fora do git: Lusíadas tem direito autoral).
"""
from __future__ import annotations

from pathlib import Path

from modelo import Faixa, Peca, montar

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
DEC = PASTA / "prints" / "decompor"
ESTUDO = PASTA.parents[2] / "lusiadas-provas" / "relatorios" / "lusiadas-provas-2026-11-14" / "prints"
SAI = PASTA / "prints"

CAMINHO = ("Os Lusíadas (cópia), página 14. Caminho da página: Automático com Dividir + \"A 1ª folha é a capa "
           "aberta\", Endireitar, Limpar a folha, Gravuras e fotos (de fábrica), sem Cortar. Versão de teste de hoje.")


def lu1():
    rec = (450, 650, 1700, 2050)          # o mesmo enquadramento em todas as peças
    circ = [(1377, 1160, 430), (845, 1760, 270)]
    montar("Pedaços remendados na pintura - resumo",
           CAMINHO + " Depois, só o filtro da página foi trocado.",
           [Faixa("azul", "O QUE O PROGRAMA ACHOU",
                  "verde = a pintura que o procurador de gravuras achou: ele deixou de fora a nuca do homem "
                  "da frente e o casaco do da direita. Azul = a tinta que sobrou fora da pintura, que o "
                  "programa passou a chamar de \"letra\".",
                  [Peca("página 14 como veio", DEC / "p14-a-preparada.jpg", recorte=rec),
                   Peca("o que o programa achou", DEC / "p14-d-marcacao-final.jpg", recorte=rec,
                        circulos=circ, nome_vermelho=True)]),
            Faixa("laranja", "COMO SAI, NOS TRÊS FILTROS",
                  "os mesmos dois pedaços saem diferentes do resto da pintura nos três: preto e branco duro "
                  "no Preto e branco; cinza desbotado, com pontinhos brancos na beirada, no Melhorar e no "
                  "Mágico pro",
                  [Peca("Preto e branco", DEC / "p14-e-preto_e_branco.png", recorte=rec, circulos=circ,
                        nome_vermelho=True),
                   Peca("Melhorar", DEC / "p14-e-melhorar.png", recorte=rec, circulos=circ, nome_vermelho=True),
                   Peca("Mágico pro", DEC / "p14-e-magico_pro.png", recorte=rec, circulos=circ,
                        nome_vermelho=True)])],
           SAI / "lu1-remendos-nos-tres-filtros.jpg")


def lu7():
    tela = ESTUDO / "crus" / "a-09-mao-uma-pagina-p14.png"
    montar("Os contornos laranja e as manchas na pintura - resumo",
           CAMINHO + " Na tela: ferramenta Mão, vista \"Uma página\", botão \"marcações\" desligado.",
           [Faixa("azul", "NA TELA, COM A MÃO (HOJE)",
                  "os contornos laranja mostram onde o programa separou a pintura do resto. Dentro da figura, "
                  "eles cercam justamente os pedaços que ele não tomou por pintura",
                  [Peca("página 14 na tela", tela, recorte=(700, 80, 1260, 870),
                        circulos=[(940, 600, 110), (1120, 440, 160)], nome_vermelho=True, altura=820)]),
            Faixa("laranja", "NO PDF",
                  "os mesmos pedaços saem remendados: o laranja não cria o defeito, ele mostra onde ele está",
                  [Peca("página 14 no PDF", ESTUDO / "analise" / "p14-4-no-pdf.png",
                        circulos=[(690, 580, 220), (422, 880, 135)], nome_vermelho=True, altura=820)])],
           SAI / "lu7-laranja-mostra-o-defeito.jpg")


def lu13():
    montar("Opção 3, passo a passo - página 8",
           "Os Lusíadas (cópia), página 8 (a pintura das bandeiras). Caminho: Automático com Dividir + capa "
           "aberta, Endireitar, Limpar a folha em Preto e branco, Gravuras e fotos (de fábrica), sem Cortar.",
           [Faixa("azul", "HOJE, NO PDF",
                  "o programa achou a pintura, mas a tratou como desenho de traço: só sobram riscos",
                  [Peca("página 8 no PDF", ESTUDO / "analise" / "p8-4-no-pdf.png", recorte=(70, 0, 913, 1275),
                        circulos=[(450, 520, 380)], nome_vermelho=True, altura=820)]),
            Faixa("verde", "PASSO 1 (O AVISO): UM CLIQUE DO KAIQUE",
                  "o aviso ainda não existe: quando existir, o botão dele marca a caixinha \"Gravuras em tons de "
                  "cinza\" nesta página. Esta é a página com essa caixinha (que já existe hoje), desenhada "
                  "pelo programa de hoje",
                  [Peca("página 8 com \"Gravuras em tons de cinza\"",
                        ESTUDO / "analise" / "p8-5-com-gravuras-em-cinza.png", recorte=(140, 0, 1826, 2550),
                        circulos=[(900, 1040, 760)], nome_vermelho=True, altura=820)])],
           SAI / "lu13-opcao-3-passo-1.jpg")


if __name__ == "__main__":
    lu1()
    lu7()
    lu13()
    print("ok")
