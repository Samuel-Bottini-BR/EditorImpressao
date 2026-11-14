"""Imagens novas da Parte 1 (perguntas que destravam consertos). Ver montar.py.

    python montar_parte1.py [pdf] [pares] [mover] [abas]
"""
from __future__ import annotations

import sys

from montar import (ANTIGAS, AZUL, CRU, LARANJA, VERDE, abrir, cabeca, empilhar, gravar_legendas,
                    lado_a_lado, salvar, tela, texto, topo)


def pdf_desatualizado(leg: dict) -> None:
    """b-pdf-desatualizado: os prints de 28/10 (versão de teste, Palatino cópia), recortados só na
    parte que importa (a barra de cima do livro aberto e o cartão), sem as páginas carregando."""
    p = ANTIGAS / "vt28" / "perguntas"
    um = abrir(p / "b-pdf-desatualizado-1.jpg")
    dois = abrir(p / "b-pdf-desatualizado-2.jpg")
    tres = abrir(p / "b-pdf-desatualizado-3.jpg")
    img = empilhar([
        topo("O livro depois de gerar o PDF",
             "Palatino (cópia), versão de teste. No alto do livro aberto (clique no cartão do livro, na tela dos "
             "livros) e no cartão, o programa diz em que pé o livro está. O contorno vermelho mostra onde olhar."),
        cabeca("1. Logo depois de gerar o PDF", AZUL,
               "No alto do livro aberto: \"pronto, PDF gerado\"."),
        tela(um, caixa=(0, 0, 1280, 108)),
        cabeca("2. Depois de mudar uma página (como é hoje)", LARANJA,
               "Mexi em duas páginas e voltei: agora diz \"32 de 134 conferidas\" e \"Continuar\". "
               "Nada diz que o PDF que você já gerou ficou velho."),
        tela(dois, caixa=(0, 0, 1280, 108)),
        texto("O cartão do livro na tela dos livros, depois de mexer: o mesmo \"32 de 134 conferidas\".",
              tamanho=24, negrito=False),
        tela(tres, caixa=(222, 214, 436, 308), largura=520),
        cabeca("3. A outra opção (ainda não existe)", VERDE,
               "Diria \"PDF desatualizado: gere de novo\", com \"continuar\" e \"abrir a pasta\". "
               "Não há print porque essa frase não está no programa."),
    ])
    salvar(img, "b-pdf-desatualizado-resumo.png", leg,
           "Palatino (cópia). Azul: logo depois de gerar o PDF, o livro diz \"pronto, PDF gerado\". "
           "Laranja (como é hoje): depois de mudar uma página, diz \"32 de 134 conferidas\" e nada fala "
           "do PDF velho. Verde: a outra opção, que ainda não existe.")


def pares(leg: dict) -> None:
    c = CRU / "p1"
    hoje = abrir(c / "hoje-indice-05.png")
    depois = abrir(c / "depois-indice-06.png")
    menu = abrir(c / "menu-miniatura-1.png")
    caixa = (430, 60, 1180, 575)
    img = empilhar([
        topo("Pares trocados: como acertar hoje",
             "La vida eterna (cópia), dividido pelo Automático, \"Duas lado a lado\" na área de trabalho. "
             "Olhe o número impresso no pé de cada página."),
        cabeca("Como é hoje", AZUL,
               "A página com número ímpar impresso (7) fica à ESQUERDA. Num livro aberto, ela fica à direita."),
        tela(hoje, circulos=[(580, 448, 652, 492)], caixa=caixa, largura=1100),
        cabeca("O que já dá para fazer hoje, à mão", VERDE,
               "Botão direito na miniatura da capa, \"adicionar página em branco depois\". Os pares andam uma "
               "página e a ímpar impressa (7) passa para a DIREITA. A página em branco entra também no PDF e "
               "nos cadernos."),
        lado_a_lado([tela(menu, largura=min(560, menu.width * 2))]),
        texto("Depois do clique, os mesmos pares:", tamanho=24, negrito=False),
        tela(depois, circulos=[(917, 448, 989, 492)], caixa=caixa, largura=1100),
    ])
    salvar(img, "v-capa-aviso-resumo.png", leg,
           "La vida eterna (cópia), dividido, \"Duas lado a lado\". Azul (como é hoje): a página de número "
           "impresso ímpar fica à esquerda. Verde: botão direito na miniatura da capa, \"adicionar página em "
           "branco depois\": a ímpar passa para a direita, como no livro.")


def mover(leg: dict) -> None:
    c = CRU / "p2"
    a = abrir(c / "a-mover-antes-depois.png")
    b = abrir(c / "b-mover-uma-pagina.png")
    caixa = (380, 50, 860, 585)
    img = empilhar([
        topo("Ferramenta Mover com o \"antes / depois\"",
             "Gradus Primus (cópia), dividido, página 11. Ferramenta Mover (barra da esquerda). "
             "O botão \"antes / depois\" fica na barra de baixo."),
        cabeca("Como é hoje: \"antes / depois\" ligado", AZUL,
               "Com o Mover, a tela mostra as duas: o \"antes\" à esquerda (só para olhar) e o \"depois\" à "
               "direita, que é onde o Mover mexe. O rótulo \"antes: Original\" fica no canto de cima."),
        tela(a, circulos=[(432, 64, 580, 106)], caixa=caixa, largura=640),
        cabeca("A outra opção: com o Mover, só a página", VERDE,
               "É como a tela fica com o \"antes / depois\" desligado: só a página que você está mexendo."),
        tela(b, caixa=caixa, largura=640),
    ])
    salvar(img, "mover-rotulo-antes-resumo.png", leg,
           "Gradus (cópia), dividido, página 11, ferramenta Mover. Azul (como é hoje): com o \"antes / depois\" "
           "ligado aparecem as duas, o antes e o depois. Verde: só a página que o Mover mexe.")


def abas(leg: dict) -> None:
    fab = abrir(CRU / "p3" / "1-fabrica.png")                       # 1600 x 821 (125%)
    menu = abrir(CRU / "p3" / "2-menu-lado-direito.png")
    abas_img = abrir(ANTIGAS / "vt28" / "perguntas" / "b-abas-nomes-1.jpg")   # 1280 x 657, 28/10
    img = empilhar([
        topo("O lado direito da área de trabalho",
             "São os painéis da direita: Para revisar, Automático, Propriedades, Filtro da página e Histórico. "
             "Já existem quatro jeitos de mostrá-los, no menu Ver > Lado direito."),
        texto("O menu Ver > Lado direito, hoje (versão de teste):", tamanho=24),
        lado_a_lado([tela(menu, largura=min(560, menu.width * 2))]),
        cabeca("De fábrica: \"Ícones na borda\"", AZUL,
               "Gradus (cópia). Os painéis aparecem como desenhos na borda direita, sem nome (círculo vermelho)."),
        tela(fab, circulos=[(1540, 45, 1600, 330)], caixa=(1000, 0, 1600, 520), largura=760),
        cabeca("Jeito \"Abas no alto\" (é dele que a pergunta trata)", VERDE,
               "Palatino (cópia), print de 28/10. Os mesmos painéis viram abas com um nome curto: Revisar, "
               "Automático, Propriedades, Filtro, Histórico. Embaixo, o nome inteiro do painel aberto."),
        tela(abas_img, caixa=(760, 0, 1280, 420), largura=760),
    ])
    salvar(img, "b-abas-nomes-resumo.png", leg,
           "O menu Ver > Lado direito já tem quatro jeitos. Azul: o de fábrica, ícones na borda, sem nome "
           "(Gradus, cópia). Verde: \"Abas no alto\", com os nomes curtos das abas (Palatino, cópia, 28/10).")


if __name__ == "__main__":
    leg: dict = {}
    pedidos = sys.argv[1:] or ["pdf", "pares", "mover", "abas"]
    for p in pedidos:
        {"pdf": pdf_desatualizado, "pares": pares, "mover": mover, "abas": abas}[p](leg)
    gravar_legendas(leg)
