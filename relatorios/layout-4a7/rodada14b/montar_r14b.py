"""Monta o rodada14b-escolhas.json (as duas perguntas da rodada 14 refeitas: 909 e 910)."""
import json
import sys
from pathlib import Path

PASTA = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])
ANTIGAS = Path(r"D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\imagens")
P = "23-rodada14b-"
SUG = " Sugestão do agente de layout: esta."


def img(nome, legenda):
    return {"src": f"img/{nome}.png", "legenda": legenda}


def nao_entendi():
    return {"id": "z", "nome": "Ainda não entendi",
            "texto": "Escreva no comentário o que ficou confuso. A pergunta volta explicada de outro jeito.",
            "imgs": [img("18-rodada12-ainda-nao-entendi", "Ainda não entendi")]}


perguntas = [
    {
        "id": "r14b-mesmo-da-pagina", "ordem": 909, "parte": "Filtro da página",
        "pergunta": "Na lista “Só neste pedaço”, o primeiro botão sai? E com que filtro o pedaço marcado começa?",
        "explicacao": (
            "O que você está escolhendo: como fica a lista “Só neste pedaço”, que dá a um pedaço marcado da "
            "página um filtro diferente do resto. Você achou confuso o primeiro botão (“o mesmo da página”) e "
            "perguntou se não seria mais fácil usar o Original.\n\n"
            "Exemplo: a página 5 sai em Preto e branco e tem uma gravura colorida. O Kaique marca a gravura "
            "com o Retângulo. Se na lista estiver “Original”, só a gravura sai colorida, e o texto continua "
            "em Preto e branco. O botão de cima de hoje quer dizer o contrário: o pedaço não ganha filtro "
            "dele e sai igual ao resto da página.\n\n"
            "Atenção: a lista vale para tudo o que for marcado depois, inclusive “letra e traço” e “papel”."),
        "exemplos": [img(P + "pedaco-hoje-ampliado", "Hoje no programa (painel Filtro novo)"),
                     img(P + "pedaco-hoje", "Hoje, a tela inteira")],
        "opcoes": [
            {"id": "a", "nome": "A — Usar o Original: o pedaço começa no Original",
             "texto": "O botão de cima sai, e todo pedaço marcado sai em Original, a não ser que se escolha "
                      "outro. Bom: a gravura marcada já sai colorida, sem clicar em nada. Ruim: uma letra ou "
                      "um papel marcado também sai em Original (com o amarelado do livro), e aí é preciso "
                      "escolher o filtro da página na lista.",
             "imgs": [img(P + "pedaco-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Sem o botão de cima, nenhum aceso",
             "texto": "O botão de cima sai, e nenhum filtro vem aceso: o pedaço só ganha filtro dele se o "
                      "Kaique clicar num dos quatro. Bom: some o botão que confundiu, e nada muda sem ele "
                      "querer. Ruim: para a gravura sair colorida, continua sendo preciso clicar em “Original”."
                      + SUG,
             "imgs": [img(P + "pedaco-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-b", "A tela inteira")]},
            {"id": "c", "nome": "C — Fica o botão, com o nome “igual ao resto da página”",
             "texto": "Tudo como hoje, só o nome muda. Bom: o nome diz o que acontece. Ruim: continua um "
                      "botão a mais na lista.",
             "imgs": [img(P + "pedaco-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14b-endireitar-a-mao", "ordem": 910, "parte": "Endireitar",
        "pergunta": "Depois de girar a página à mão, como os ângulos continuam aparecendo na parte “Conta”?",
        "explicacao": (
            "O que você está escolhendo: o que a parte “Conta” do Endireitar mostra depois que o Kaique gira "
            "a página à mão. Você pediu: “mesmo que coloque a mão tem que continuar aparecendo o ângulo”. Nas "
            "três opções os ângulos continuam à vista.\n\n"
            "Hoje, ao girar à mão, a linha “ScanTailor −0,6° · Editor −0,7°” some. O número do giro à mão "
            "aparece no campo de cima (“−0,72 graus”). A lista “Conta” fica apagada porque, com o ângulo à "
            "mão, ela não muda nada até o “usar o ângulo do programa”.\n\n"
            "O contorno amarelo só mostra a parte que muda."),
        "exemplos": [img(P + "mao-antes-ampliado", "Antes de girar à mão"),
                     img(P + "mao-hoje-ampliado", "Hoje, depois de girar à mão")],
        "opcoes": [
            {"id": "a", "nome": "A — Os dois ângulos e, embaixo, o seu",
             "texto": "A linha dos dois ângulos continua, e outra embaixo diz o giro à mão e como voltar às "
                      "contas. Bom: mostra tudo e explica. Ruim: duas linhas a mais de texto.",
             "imgs": [img(P + "mao-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Os três ângulos numa linha, com o que vale",
             "texto": "“ScanTailor −0,6° · Editor −0,7° · à mão −0,7° (vale)”. Bom: uma linha só, e diz qual "
                      "vale. Ruim: a linha fica comprida.",
             "imgs": [img(P + "mao-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-b", "A tela inteira")]},
            {"id": "c", "nome": "C — A linha continua igual à de antes de girar",
             "texto": "Só deixa de sumir: os dois ângulos ficam como estavam, e o giro à mão continua no "
                      "campo de cima. Bom: a menor mudança, e é o que você pediu. Ruim: nada diz que a "
                      "lista está apagada por causa do giro à mão." + SUG,
             "imgs": [img(P + "mao-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
]

faltam = []
for q in perguntas:
    for i in q["exemplos"] + [x for o in q["opcoes"] for x in o["imgs"]]:
        nome = i["src"][4:]
        if not (PASTA / nome).exists() and not (ANTIGAS / nome).exists():
            faltam.append(nome)
    assert q["explicacao"].startswith("O que você está escolhendo:")
    assert q["explicacao"].count("\n\n") <= 2
    assert sum(SUG.strip() in o["texto"] for o in q["opcoes"]) == 1
SAIDA.write_text(json.dumps(perguntas, ensure_ascii=False, indent=1), encoding="utf-8")
json.loads(SAIDA.read_text(encoding="utf-8"))
print(len(perguntas), "perguntas;", sum(len(q["opcoes"]) for q in perguntas), "opções; faltam:", faltam)
