"""Imagens novas da Parte 2 (aba nomes-28-10). Ver montar.py."""
from __future__ import annotations

from PIL import Image

from montar import (ANTIGAS, AZUL, CINZA, CRU, VERDE, abrir, cabeca, empilhar, gravar_legendas,
                    lado_a_lado, salvar, tela, texto, topo)

V28 = ANTIGAS / "vt28" / "perguntas"


def desligar(leg: dict) -> None:
    a = abrir(CRU / "p4" / "a1-depois-do-dividir.png")      # 1600 x 821
    b = abrir(CRU / "p4" / "a2-depois-de-desligar.png")
    circ = [(1185, 278, 1505, 345), (1262, 776, 1452, 810), (60, 668, 870, 772)]
    img = empilhar([
        topo("O que o botão \"desligar as marcadas\" faz",
             "Gradus Primus (cópia), versão de teste. Painel Automático aberto à direita. No círculo vermelho: a "
             "etapa marcada, o botão (embaixo à direita) e a tira das páginas."),
        cabeca("1. Depois de rodar o Automático com \"Dividir folhas ao meio\"", AZUL,
               "A etapa 1 está marcada (\"ligada no livro todo\"). As 70 folhas viraram 140 páginas: a tira mostra "
               "uma página em cada miniatura."),
        tela(a, circulos=circ),
        cabeca("2. Depois de clicar \"desligar as marcadas\"", VERDE,
               "Com a etapa 1 marcada e \"Rodar: no livro todo\", o botão DESFEZ o dividir: cada folha voltou a ser "
               "uma página só (as duas páginas juntas), e a caixinha da etapa 1 ficou desmarcada. Na tira, a metade "
               "que sobrou aparece como \"apagada\". O Ctrl+Z traz o dividir de volta."),
        tela(b, circulos=circ),
    ])
    salvar(img, "nm-desligar-marcadas-resumo.png", leg,
           "Gradus (cópia). Azul: depois do Automático só com \"Dividir folhas ao meio\", 140 páginas. Verde: com a "
           "etapa marcada, \"desligar as marcadas\" desfaz o dividir e as folhas voltam inteiras.")


def jeito_pb(leg: dict) -> None:
    lista = abrir(V28 / "nm-jeito-pb-1.jpg")                # 1280 x 657, 28/10
    caixa = (420, 440, 700, 600)
    nomes = [("sauvola", "\"Sauvola (padrão)\"", "proposta: \"letra fina\""),
             ("otsu", "\"Otsu (letra grossa/gótica)\"", "proposta: \"letra grossa ou gótica\""),
             ("wolf", "\"Wolf (scan de baixo contraste)\"", "proposta: \"scan apagado\"")]
    pedacos = []
    for chave, hoje, proposta in nomes:
        p = Image.open(CRU / "p4" / f"b-pagina-9-{chave}.png").convert("RGB").crop(caixa)
        p = p.resize((470, round(p.height * 470 / p.width)), Image.NEAREST)
        pedacos.append(empilhar([texto(hoje, largura=470, tamanho=22), texto(proposta, largura=470, tamanho=22,
                                                                                negrito=False), p],
                                espaco=6, largura=470))
    img = empilhar([
        topo("A lista \"Jeito do preto e branco\"",
             "Painel \"Filtro da página\" (à direita), numa página em Preto e branco, parte \"Mais ajustes\". Print "
             "de 28/10, Palatino (cópia), página 9."),
        tela(lista, circulos=[], caixa=(940, 40, 1230, 520), largura=560),
        cabeca("O que cada um faz, na mesma página", CINZA,
               "Palatino (cópia), página 9, Preto e branco, desenhada pela mesma conta do PDF, só trocando o jeito. "
               "O mesmo pedaço, aumentado. Nesta página a diferença é pequena: olhe a moldura da direita e a "
               "grossura das letras. O \"Automático\" escolheu o Sauvola para esta página."),
        lado_a_lado(pedacos),
    ])
    salvar(img, "nm-jeito-pb-resumo.png", leg,
           "Palatino (cópia), página 9, Preto e branco: a lista \"Jeito do preto e branco\" e o mesmo pedaço da "
           "página com Sauvola, Otsu e Wolf. A diferença está na moldura da direita e na grossura das letras.")


def tela_livros(leg: dict) -> None:
    menu = abrir(V28 / "nm-tela-livros-1.jpg")
    janela = abrir(V28 / "nm-tela-livros-2.jpg")
    cartoes = abrir(V28 / "nm-tela-livros-3.jpg")
    busca = abrir(V28 / "nm-tela-livros-4.jpg")
    img = empilhar([
        topo("Tela dos livros: três coisas com dois nomes",
             "Prints de 28/10 (versão de teste, cópias dos livros). O contorno vermelho mostra onde olhar."),
        cabeca("1. Tirar o livro da lista", AZUL,
               "No menu \"Mais...\" o item é \"remover da lista\"; a janela que ele abre diz \"Tirar da lista\"."),
        lado_a_lado([tela(menu, largura=360), tela(janela, largura=620)], espaco=40),
        cabeca("2. Achar o PDF que mudou de pasta", AZUL,
               "No cartão: \"o PDF saiu do lugar\" e o botão \"procurar de novo\". No menu \"Mais...\" o mesmo se "
               "chama \"procurar o livro\"."),
        tela(cartoes, circulos=[(322, 180, 424, 210), (236, 262, 420, 288)], caixa=(225, 55, 640, 310), largura=760),
        cabeca("3. \"projeto\" no lugar de \"livro\"", AZUL,
               "Procurando \"Horas\" na busca: \"Nenhum projeto com 'horas' no nome.\""),
        tela(busca, caixa=(0, 0, 1280, 320), largura=1100),
    ])
    salvar(img, "nm-tela-livros-resumo.png", leg,
           "Tela dos livros (prints de 28/10). 1: \"remover da lista\" no menu e \"Tirar da lista\" na janela. 2: "
           "\"procurar de novo\" no cartão e \"procurar o livro\" no menu. 3: \"projeto\" na busca.")


if __name__ == "__main__":
    leg: dict = {}
    desligar(leg)
    jeito_pb(leg)
    tela_livros(leg)
    gravar_legendas(leg)
