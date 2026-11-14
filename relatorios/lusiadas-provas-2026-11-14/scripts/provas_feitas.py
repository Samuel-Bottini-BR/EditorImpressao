"""Verificador, 14/11/2026: monta as imagens de prova (modelo do girar) a partir dos prints crus.
Uma função por erro; rodar: python scripts/provas_feitas.py <erro...>"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from modelo import Peca, Faixa, montar  # noqa: E402

AQUI = Path(__file__).resolve().parent.parent
C = AQUI / "prints" / "crus"
P = AQUI / "prints"


def erro10():
    montar("Erro 10 - código \"(G2)\" na tela - resumo",
           "Os Lusíadas (cópia), livro novo. Clique em \"Rodar o automático...\" e depois na etapa "
           "\"1 Dividir folhas ao meio\". Versão de teste de hoje.",
           [Faixa("azul", "COMO É HOJE", "embaixo de \"Motor de corte\" está escrito \"só quando esta etapa "
                  "roda (G2)\": G2 é um código de dentro, não quer dizer nada para quem usa",
                  [Peca("janela do Automático, etapa Dividir", C / "a-02-automatico-dividir-g2.png",
                        recorte=(370, 120, 1240, 400), circulos=[(796, 261, 30)], nome_vermelho=True,
                        altura=420)])],
           P / "erro10-codigo-g2.jpg")





A = AQUI / "prints" / "analise"
CAMINHO = ("Caminho da página: Os Lusíadas (cópia), Automático com Dividir + \"A 1ª folha é a capa "
           "aberta\", Endireitar, Limpar em Preto e branco, Gravuras e fotos (de fábrica: \"Respeitar as "
           "gravuras achadas\" ligada), sem Cortar; processado. Versão de teste de hoje.")


def erro1():
    montar("Erro 1 - remendos pretos e brancos nos rostos - resumo",
           "Página 14. " + CAMINHO,
           [Faixa("azul", "COMO É HOJE", "o programa marcou dois pedaços da pintura como \"letra\" (em azul "
                  "no meio): ali ele passa o preto e branco de texto e saem os quadrados duros",
                  [Peca("página 14 como veio", A / "p14-1-preparada.jpg"),
                   Peca("o que o programa marcou", A / "p14-2-marcado.jpg",
                        circulos=[(1400, 1100, 330), (830, 1720, 330)], nome_vermelho=True),
                   Peca("página 14 no PDF", A / "p14-4-no-pdf.png",
                        circulos=[(700, 550, 160), (415, 860, 160)], nome_vermelho=True)]),
            Faixa("laranja", "MESMA PÁGINA COM \"GRAVURAS EM TONS DE CINZA\"",
                  "marcar essa caixinha não resolve: os pedaços marcados como letra continuam fora da pintura",
                  [Peca("página 14 com a caixinha", A / "p14-5-com-gravuras-em-cinza.png",
                        circulos=[(1400, 1100, 330), (830, 1720, 330)])])],
           P / "erro1-remendos-p14.jpg")


def erro13():
    montar("Erro 13 - pintura das bandeiras quase some - resumo",
           "Página 8. " + CAMINHO,
           [Faixa("azul", "COMO É HOJE", "a pintura FOI achada (verde), mas o programa a tomou por desenho de "
                  "traço, não por pintura: o cinza vira branco e só ficam riscos",
                  [Peca("página 8 como veio", A / "p8-1-preparada.jpg"),
                   Peca("o que o programa achou", A / "p8-2-marcado.jpg"),
                   Peca("página 8 no PDF", A / "p8-4-no-pdf.png",
                        circulos=[(430, 560, 260)], nome_vermelho=True)]),
            Faixa("laranja", "MESMA PÁGINA COM \"GRAVURAS EM TONS DE CINZA\"",
                  "com essa caixinha marcada (ela já existe, vem desmarcada), a pintura sai inteira, em cinza",
                  [Peca("página 8 com a caixinha", A / "p8-5-com-gravuras-em-cinza.png",
                        circulos=[(860, 1120, 520)], nome_vermelho=True)])],
           P / "erro13-pintura-p8.jpg")


def erro12():
    montar("Erro 12 - página quase em branco sai suja - resumo",
           "Página 22 (verso em branco, só a sombra fraca da outra face). " + CAMINHO,
           [Faixa("azul", "COMO É HOJE", "no \"jeito de preto\" automático o programa escolhe o jeito para letra "
                  "grossa: ele inventa tinta onde só há papel, e embaixo sai um bloco preto",
                  [Peca("página 22 como veio", A / "p22-1-preparada.jpg"),
                   Peca("página 22 no PDF", A / "p22-4-no-pdf.png",
                        circulos=[(500, 1170, 270)], nome_vermelho=True)]),
            Faixa("laranja", "A MESMA PÁGINA COM O OUTRO JEITO DE PRETO",
                  "com o jeito de preto de sempre para letra fina (o que o automático deixou de escolher), "
                  "a página sai branca",
                  [Peca("página 22, outro jeito de preto", A / "p22-pb-sauvola.png")])],
           P / "erro12-pagina-suja-p22.jpg")


def erro5():
    from PIL import Image, ImageDraw
    def com_linha(arq, pos):
        im = Image.open(arq).convert("RGB"); d = ImageDraw.Draw(im)
        x = round(im.width * pos)
        for k in range(-2, 3):
            d.line((x + k, 0, x + k, im.height), fill=(30, 90, 230))
        return im
    montar("Erro 5 - página deitada no arquivo para imprimir - resumo",
           "Os Lusíadas (cópia): Automático com Dividir + \"A 1ª folha é a capa aberta\" (o resto como a "
           "rodada 1 do Kaique), processado, e \"montar para imprimir em A4\" com o Livreto de fábrica. "
           "Versão de teste de hoje. A linha azul é onde o programa cortou a folha.",
           [Faixa("azul", "COMO É HOJE: FOLHA 2", "o programa cortou a folha muito à esquerda (ele mesmo avisou "
                  "\"Não tenho certeza de onde cortar\"): a página 3 ficou mais larga que alta e, no arquivo "
                  "para imprimir, foi deitada",
                  [Peca("folha 2 como veio", com_linha(A / "original-folha2.png", 0.2391), altura=380,
                        circulos=[(252, 380, 60)]),
                   Peca("face 3 do arquivo para imprimir", A / "imprimir-face3.png", altura=380,
                        circulos=[(790, 370, 260)], nome_vermelho=True)]),
            Faixa("azul", "COMO É HOJE: FOLHA 7 (A DO KAIQUE)", "a linha caiu no meio do título "
                  "\"PERIGOS E TRAIÇÕES\": \"PERIGOS\" ficou numa página e \"E TRAIÇÕES\" na outra; "
                  "nesta rodada a página 12 saiu quase quadrada e não foi deitada, na do Kaique foi",
                  [Peca("folha 7 como veio", com_linha(A / "original-folha7.png", 0.7321), altura=380,
                        circulos=[(770, 365, 120)], nome_vermelho=True),
                   Peca("face 8", A / "imprimir-face8.png", altura=380, circulos=[(780, 300, 150)]),
                   Peca("face 9", A / "imprimir-face9.png", altura=380, circulos=[(440, 350, 110)])]),
            Faixa("azul", "O AVISO EXISTE, MAS FICA ESCONDIDO", "o aviso \"Página 3: era deitada e foi girada "
                  "de pé...\" só aparece depois de gravar, embaixo de \"Como imprimir\", fora da vista "
                  "(é preciso rolar a barra marcada); antes de gravar não há aviso nenhum",
                  [Peca("janela Montar para imprimir, depois de gravar", C / "a-21-montar-depois-de-gravar.png",
                        recorte=(1190, 580, 1560, 960), altura=420, circulos=[(1538, 760, 45)],
                        nome_vermelho=True)])],
           P / "erro5-pagina-deitada.jpg")


def erro7():
    montar("Erro 7 - marcações laranja à vista com a Mão - resumo",
           "Os Lusíadas (cópia), logo depois do Automático (Dividir + capa aberta, Preto e branco, Gravuras). "
           "Ferramenta Mão escolhida (a mãozinha azul, embaixo à esquerda), vista \"Uma página\", botão "
           "\"marcações\" desligado. Versão de teste de hoje.",
           [Faixa("azul", "COMO É HOJE", "com a Mão e o botão \"marcações\" desligado, os contornos laranja "
                  "continuam em volta do texto e da pintura: é o \"Mostrar as áreas achadas\", que liga sozinho "
                  "em toda página que tem aviso",
                  [Peca("página 1", C / "a-05-mao-uma-pagina-p1.png", altura=560,
                        circulos=[(36, 540, 34), (1540, 1075, 50), (730, 420, 120)], nome_vermelho=True),
                   Peca("página 14", C / "a-09-mao-uma-pagina-p14.png", altura=560,
                        circulos=[(36, 540, 34), (1540, 1075, 50), (1120, 450, 140)], nome_vermelho=True)])],
           P / "erro7-laranja-com-a-mao.jpg")


def erro2():
    montar("Erro 2 - números que não batem - resumo",
           "Os Lusíadas (cópia), 134 páginas depois do Dividir com a capa aberta; a página 133 (a contracapa "
           "repetida do scan) foi tirada do livro. Depois, o Automático aberto de novo. Versão de teste de hoje. "
           "Embaixo, o sino, numa rodada com o livro aberto do zero.",
           [Faixa("azul", "COMO É HOJE", "o Automático diz \"de 134\" e \"(134 páginas)\", mas para o PDF vão "
                  "133: ele conta também a página tirada do livro",
                  [Peca("janela do Automático", C / "b-10-automatico-2-contagem.png", altura=520,
                        circulos=[(1525, 795, 95), (840, 918, 75)], nome_vermelho=True),
                   Peca("janela de salvar, logo depois", C / "b-15-salvar-depois-de-trocar-o-nome.png",
                        altura=520, retangulos=[(30, 342, 382, 376)])]),
            Faixa("azul", "O SINO QUE MUDA SOZINHO (OUTRA RODADA, LIVRO NOVO)", "logo depois do Automático, "
                  "\"Qualidade baixa\" + \"Selecionar todas\" + \"está bom nas marcadas\": o sino fica em 25. Sem "
                  "mexer em nada, só andando com a seta para a direita da página 1 à 41, ele passa para 26",
                  [Peca("antes de andar: 25", C / "d-06-sino-logo-depois-do-esta-bom.png",
                        recorte=(1560, 90, 1942, 300), altura=230, circulos=[(1916, 143, 26)], nome_vermelho=True),
                   Peca("depois: 26", C / "d-07-sino-depois-de-andar.png",
                        recorte=(1560, 90, 1942, 300), altura=230, circulos=[(1916, 143, 26)], nome_vermelho=True),
                   Peca("rodapé, depois", C / "d-07-sino-depois-de-andar.png",
                        recorte=(420, 1058, 780, 1092), altura=60)])],
           P / "erro2-numeros.jpg")


def erro3():
    montar("Erro 3 - miniatura não fica branca - resumo",
           "Os Lusíadas (cópia), página 3 (folha de rosto), botão \"deixar em branco\" do painel Propriedades. "
           "Versão de teste de hoje.",
           [Faixa("azul", "COMO É HOJE", "a página grande fica branca (o quadriculado azul é só a régua da ferramenta "
                  "Endireitar), mas a miniatura 3, embaixo, continua mostrando o título",
                  [Peca("página 3 na tela", C / "b-04-p3-em-branco.png", recorte=(400, 110, 1170, 830),
                        altura=440),
                   Peca("a tira de baixo", C / "b-04-p3-em-branco.png", recorte=(60, 935, 560, 1045),
                        altura=200, circulos=[(170, 980, 42)], nome_vermelho=True)])],
           P / "erro3-miniatura-branco.jpg")


def erro4():
    montar("Erro 4 - textos cortados na barra de baixo - resumo",
           "Os Lusíadas (cópia), janela do tamanho do notebook do Kaique (1280 x 657), painel Propriedades "
           "aberto (ícone de controles, na coluna da direita). Versão de teste de hoje.",
           [Faixa("azul", "COMO É HOJE", "com o painel aberto, a barra de baixo não cabe: sai \"uas lado a lad\" "
                  "e \"página 133 de 13\"",
                  [Peca("barra de baixo, painel aberto", C / "b-08-pequena-propriedades-aberto.png",
                        recorte=(60, 818, 1180, 866), altura=120,
                        circulos=[(615, 842, 55), (165, 842, 75)], nome_vermelho=True)]),
            Faixa("laranja", "A MESMA BARRA COM O PAINEL FECHADO (JANELA GRANDE)", "sem o painel, os textos cabem "
                  "inteiros",
                  [Peca("barra de baixo, painel fechado", C / "b-09-grande-propriedades-fechado.png",
                        recorte=(60, 1052, 1900, 1098), altura=90)])],
           P / "erro4-barra-cortada.jpg")


def erro8():
    montar("Erro 8 - aviso velho na janela de salvar - resumo",
           "Os Lusíadas (cópia), já processado uma vez na mesma pasta. \"Confirmar e processar\" -> a janela "
           "\"Onde salvar o livro pronto\"; troquei o nome digitando. Versão de teste de hoje.",
           [Faixa("azul", "ANTES DE TROCAR O NOME", "o nome é o do PDF que já existe: o aviso está certo",
                  [Peca("como abriu", C / "b-14-salvar-como-abriu.png", altura=420)]),
            Faixa("azul", "COMO É HOJE: DEPOIS DE TROCAR O NOME", "o nome agora é \"rodada-2.pdf\", que não existe, "
                  "e o aviso continua dizendo que o outro arquivo será substituído",
                  [Peca("depois de digitar o nome novo", C / "b-15-salvar-depois-de-trocar-o-nome.png", altura=420,
                        circulos=[(275, 203, 60), (410, 272, 120)], nome_vermelho=True)])],
           P / "erro8-aviso-velho-salvar.jpg")


def erro9():
    montar("Erro 9 - página tirada, frase velha - resumo",
           "Os Lusíadas (cópia), página 133 (a contracapa repetida do scan) tirada do livro com o botão \"tirar do "
           "livro\". Ferramenta Mão. Versão de teste de hoje.",
           [Faixa("azul", "COMO É HOJE", "a miniatura diz \"apagada\", mas a faixa em cima dela continua dizendo "
                  "\"Esta página vai sair em Preto e branco.\"",
                  [Peca("página 133, tirada do livro", C / "c-02-mao-p133.png", recorte=(60, 840, 1880, 1045),
                        altura=230, retangulos=[(68, 866, 400, 900)], circulos=[(1471, 1000, 55)], nome_vermelho=True)])],
           P / "erro9-frase-depois-de-tirar.jpg")


def erro11():
    montar("Erro 11 - a lista do Automático volta para o topo - resumo",
           "Os Lusíadas (cópia), janela do Automático do tamanho do notebook do Kaique (1280 x 657). Lista das "
           "etapas rolada até o fim; clique na caixinha de \"6 Margens iguais\". Versão de teste de hoje.",
           [Faixa("azul", "ANTES DO CLIQUE", "a lista está no fim, com \"6 Margens iguais\" à vista",
                  [Peca("lista rolada", C / "c-03-lista-rolada-antes-de-marcar-margens.png", recorte=(10, 120, 370, 730),
                        altura=520, circulos=[(45, 520, 30)], nome_vermelho=True)]),
            Faixa("azul", "COMO É HOJE: DEPOIS DO CLIQUE", "a caixinha foi marcada (a frase de baixo já diz "
                  "\"deixar as margens iguais\"), mas a lista voltou para o topo: \"6 Margens iguais\" ficou escondida lá embaixo (círculo) e o próximo clique cai em outra etapa",
                  [Peca("lista depois do clique", C / "c-04-lista-depois-de-marcar-margens.png", recorte=(10, 120, 370, 730),
                        altura=520, circulos=[(180, 718, 40)], nome_vermelho=True)])],
           P / "erro11-lista-volta-ao-topo.jpg")


def erro6():
    K = Path(r"D:/programas/EditorImpressao/.claude/worktrees/teste-kaique-lusiadas/relatorios/teste-kaique-lusiadas/prints")
    montar("Erro 6 - folha espremida com a Mão - resumo",
           "Os Lusíadas (cópia), logo depois do Automático com Dividir e \"A 1ª folha é a capa aberta\", "
           "ferramenta Mão, vista \"Uma página\", página 1.",
           [Faixa("azul", "NO TESTE DO KAIQUE (06/11)", "a página 1 aparece com a folha inteira (contracapa + capa) "
                  "apertada na largura de uma página",
                  [Peca("página 1, versão de 06/11 (print do Kaique)", K / "20-depois-rodar.png", recorte=(560, 40, 1020, 630),
                        altura=520, circulos=[(790, 330, 230)], nome_vermelho=True)]),
            Faixa("verde", "HOJE (VERSÃO DE TESTE DE 14/11)", "o mesmo caminho mostra só a capa, na forma certa "
                  "(o laranja em volta é o erro 7, outro assunto)",
                  [Peca("página 1, versão de hoje", C / "a-05-mao-uma-pagina-p1.png", recorte=(600, 80, 1340, 860),
                        altura=520)])],
           P / "erro6-folha-espremida.jpg")


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        globals()[nome]()
        print("feito", nome)
