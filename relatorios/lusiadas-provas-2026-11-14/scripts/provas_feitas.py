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


def erro12():
    montar("Erro 12 - pintura das bandeiras quase some - resumo",
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
           P / "erro12-pintura-p8.jpg")


def erro11():
    montar("Erro 11 - página quase em branco sai suja - resumo",
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
           P / "erro11-pagina-suja-p22.jpg")


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


if __name__ == "__main__":
    for nome in sys.argv[1:]:
        globals()[nome]()
        print("feito", nome)
