"""Monta o rodada14-escolhas.json (formato das rodadas 12 e 13 da página "Layout do Editor de Impressão")
e confere que toda imagem citada existe. Uso: python montar_r14.py <pasta das imagens> <json de saída>."""
import json
import sys
from pathlib import Path

PASTA = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])
ANTIGAS = Path(r"D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\imagens")


def img(nome, legenda):
    return {"src": f"img/{nome}.png", "legenda": legenda}


def nao_entendi():
    return {"id": "z", "nome": "Ainda não entendi",
            "texto": "Escreva no comentário o que ficou confuso. A pergunta volta explicada de outro jeito.",
            "imgs": [img("18-rodada12-ainda-nao-entendi", "Ainda não entendi")]}


SUG = " Sugestão do agente de layout: esta."
P = "22-rodada14-"

perguntas = [
    {
        "id": "r14-todas-fabrica", "ordem": 901, "parte": "Todas as páginas",
        "pergunta": "A tela “Todas as páginas” abre com uma página em cada quadro, ou com duas páginas lado a lado?",
        "explicacao": (
            "O que você está escolhendo: como a tela com todas as páginas do livro aparece quando o Kaique "
            "abre. Os dois jeitos já estão aprovados e se troca com um clique no alto (“uma a uma” e “em "
            "pares”); falta só qual vem primeiro.\n\n"
            "Exemplo: o Kaique quer achar a página 12, que ficou com dúvida. Uma a uma, cada quadro é uma "
            "página. Em pares, cada quadro é o livro aberto na mesa, com as duas páginas que ficam juntas na "
            "impressão.\n\n"
            "Esta tela ainda não existe no programa: as fotos foram montadas com as cores do programa e as "
            "páginas de verdade do Boécio. O contorno amarelo só mostra a parte que muda."),
        "exemplos": [],
        "opcoes": [
            {"id": "a", "nome": "A — Uma a uma",
             "texto": "Abre com uma página em cada quadro. Bom: cada quadro tem o número de uma página só, igual "
                      "à tira de miniaturas e ao “Para revisar”. Ruim: para ver como fica impresso, é um clique "
                      "em “em pares”." + SUG,
             "imgs": [img(P + "todas-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "todas-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Em pares",
             "texto": "Abre com as duas páginas lado a lado, como o livro aberto. Bom: já mostra como vai sair "
                      "impresso. Ruim: cada quadro tem duas páginas, e o aviso de uma pinta o par inteiro de "
                      "laranja.",
             "imgs": [img(P + "todas-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "todas-b", "A tela inteira")]},
            {"id": "c", "nome": "C — Lembra a última (na primeira vez, uma a uma)",
             "texto": "Abre do jeito que o Kaique deixou da última vez. Bom: ele escolhe uma vez e não troca "
                      "mais. Ruim: quem não lembra que trocou estranha a tela diferente (no “Para revisar” você "
                      "escolheu abrir sempre do mesmo jeito).",
             "imgs": [img(P + "todas-a", "Na primeira vez, uma a uma"),
                      img(P + "todas-b", "Se da última vez ele deixou em pares")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-lado-direito-onde", "ordem": 902, "parte": "Lado direito",
        "pergunta": "Onde o Kaique troca o jeito do lado direito (os ícones na borda, a área de trabalho 1 e os outros)?",
        "explicacao": (
            "O que você está escolhendo: o lugar onde se troca o jeito dos painéis da direita. De fábrica são "
            "os ícones na borda, como o programa está hoje. Você pediu para ter também a área de trabalho 1 "
            "(os painéis um embaixo do outro, abrindo dentro da coluna, como uma sanfona), as abas no alto e "
            "o painel solto.\n\n"
            "É uma escolha que se faz uma vez e fica, como o Tema. No Tema você escolheu os dois lugares.\n\n"
            "Os nomes dos quatro jeitos são sugestão do agente; dá para trocar no comentário. A tela de "
            "Configurações da foto B foi montada como você decidiu na rodada 13 (a lista das partes à "
            "esquerda); ela ainda não existe no programa."),
        "exemplos": [img(P + "hoje-tela-de-trabalho", "Hoje no programa: os ícones na borda (o jeito de fábrica)"),
                     img("13-rodada7-padrao-a-area1-automatico-aberto",
                         "A área de trabalho 1 (desenho da rodada 7): os painéis um embaixo do outro")],
        "opcoes": [
            {"id": "a", "nome": "A — No menu Ver",
             "texto": "Um item “Lado direito” no menu Ver, logo acima do Tema, com os quatro jeitos. Bom: à mão "
                      "na tela de trabalho. Ruim: na tela dos livros não há menu Ver.",
             "imgs": [img(P + "lado-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "lado-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Nas Configurações",
             "texto": "Na parte “Aparência” das Configurações, embaixo do Tema. Bom: fica junto do Tema e de "
                      "todas as outras escolhas. Ruim: para trocar, sai da tela de trabalho.",
             "imgs": [img(P + "lado-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "lado-b", "A tela de Configurações inteira (montada; ainda não existe)")]},
            {"id": "c", "nome": "C — Nos dois lugares",
             "texto": "No menu Ver e nas Configurações, os dois mudando juntos. Bom: é o mesmo que você escolheu "
                      "para o Tema. Ruim: dois lugares para a mesma coisa." + SUG,
             "imgs": [img(P + "lado-a-ampliado", "No menu Ver"),
                      img(P + "lado-b-ampliado", "E nas Configurações")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-menu-paineis", "ordem": 903, "parte": "Menus",
        "pergunta": "Os nomes dos painéis da direita também aparecem num menu do alto?",
        "explicacao": (
            "O que você está escolhendo: se os painéis (Propriedades, Filtro da página, Para revisar, "
            "Automático, Histórico) também abrem por um menu do alto, além dos ícones da direita.\n\n"
            "Hoje o menu Ver tem quatro itens “Painel: …” que não fazem nada quando se clica, e um deles ainda "
            "tem o nome antigo (“Marcar como”). Seja qual for a escolha, eles não ficam assim.\n\n"
            "No Photoshop todo painel tem o nome num menu: quem não acha o ícone acha o nome escrito."),
        "exemplos": [img(P + "paineis-hoje-ampliado", "Hoje no programa: quatro itens que não fazem nada")],
        "opcoes": [
            {"id": "a", "nome": "A — No menu Ver",
             "texto": "Os cinco nomes no menu Ver, com a marca no que está aberto. Clicar abre o painel (e fecha "
                      "o outro, porque abre um por vez). Bom: um lugar a mais para achar, sem menu novo. Ruim: o "
                      "menu Ver fica mais comprido." + SUG,
             "imgs": [img(P + "paineis-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "paineis-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Um menu novo, “Painéis”",
             "texto": "Um menu só para os painéis, entre Ver e Ajuda, como o “Janela” do Photoshop, com “Fechar "
                      "o painel” e “Esconder os ícones da direita”. Bom: fácil de achar e não enche o Ver. Ruim: "
                      "um menu a mais no alto.",
             "imgs": [img(P + "paineis-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "paineis-b", "A tela inteira"),
                      img(P + "paineis-b-ver-ampliado", "O menu Ver, sem os painéis")]},
            {"id": "c", "nome": "C — Em nenhum menu",
             "texto": "Os quatro itens saem do menu Ver; os painéis abrem só pelos ícones. Bom: menu mais curto. "
                      "Ruim: com os ícones escondidos pela seta, o nome escrito não está em lugar nenhum.",
             "imgs": [img(P + "paineis-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "paineis-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-menus-novas", "ordem": 904, "parte": "Menus",
        "pergunta": "As peças novas da tela também ganham um item escrito no menu Ver?",
        "explicacao": (
            "O que você está escolhendo: se o que você decidiu nas rodadas 7 a 13 (mostrar e esconder as "
            "miniaturas e os ícones da direita, “Ver lado a lado”, “Todas as páginas”, os filtros em tela "
            "cheia) também aparece escrito no menu Ver, além do botão na tela.\n\n"
            "Exemplo: o Kaique fechou as miniaturas pela seta e não lembra como abrir de novo. Com o item no "
            "menu, ele acha “Miniaturas” no Ver, como quem procura no índice do livro.\n\n"
            "Nas fotos, os cinco painéis aparecem como na opção A da pergunta anterior, só para mostrar o "
            "tamanho que o menu fica."),
        "exemplos": [],
        "opcoes": [
            {"id": "a", "nome": "A — Sim, no menu Ver",
             "texto": "Cada peça nova ganha um item no Ver. Bom: tudo o que a tela faz fica escrito num lugar "
                      "só, e o menu ensina o que existe. Ruim: o menu Ver fica comprido." + SUG,
             "imgs": [img(P + "novas-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "novas-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Não, só os botões da tela",
             "texto": "O menu Ver fica como está. Bom: menu curto. Ruim: o que foi escondido (miniaturas "
                      "fechadas, ícones escondidos) só volta pelo botão pequeno que ficou na tela.",
             "imgs": [img(P + "novas-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "novas-b", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-mesmo-da-pagina", "ordem": 905, "parte": "Filtro da página",
        "pergunta": "No “só neste pedaço”, que nome fica no lugar de “o mesmo da página”?",
        "explicacao": (
            "O que você está escolhendo: o nome do primeiro botão da lista “só neste pedaço”, no painel Filtro "
            "da página. Você perguntou o que ele quer dizer.\n\n"
            "Exemplo: na página 5, o Kaique marca a gravura e quer que só ela saia em Original, com o texto "
            "em Preto e branco. Ele escolhe “Original” nessa lista. O primeiro botão é o contrário: o pedaço "
            "marcado não tem filtro dele e sai igual ao resto da página.\n\n"
            "Nas fotos o painel Filtro ainda é o antigo por dentro (o novo, com os filtros numa fila e partes "
            "que abrem e fecham, é a próxima etapa da obra). A lista “só neste pedaço” fica igual no novo."),
        "exemplos": [img(P + "pedaco-hoje-ampliado", "Hoje no programa"),
                     img(P + "pedaco-hoje", "Hoje, a tela inteira (o contorno amarelo mostra a lista)")],
        "opcoes": [
            {"id": "a", "nome": "A — Fica “o mesmo da página”",
             "texto": "Nada muda. Bom: nenhum trabalho. Ruim: foi o nome que deixou dúvida.",
             "imgs": [img(P + "pedaco-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-a", "A tela inteira")]},
            {"id": "b", "nome": "B — “igual ao resto da página”",
             "texto": "Bom: diz em palavras de casa o que acontece com o pedaço. Ruim: um pouco mais comprido."
                      + SUG,
             "imgs": [img(P + "pedaco-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-b", "A tela inteira")]},
            {"id": "c", "nome": "C — “nenhum: fica o filtro da página”",
             "texto": "Bom: diz que o pedaço não tem filtro dele. Ruim: o mais comprido, e “nenhum” pode parecer "
                      "“sem filtro nenhum”.",
             "imgs": [img(P + "pedaco-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "pedaco-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-aviso-marcar", "ordem": 906, "parte": "Avisos",
        "pergunta": "Que frase fica no aviso “desenho ou escrita?”, que ainda manda conferir na aba Marcar?",
        "explicacao": (
            "O que você está escolhendo: a frase do aviso que aparece na faixa embaixo da página quando o "
            "programa não sabe se a página é desenho ou escrita. Hoje ela diz “Confira na aba Marcar”, e a "
            "aba Marcar não existe mais: marcar agora é com as ferramentas da trilha da esquerda (Retângulo, "
            "Laço, Pincel, Varinha), e o “letra e traço” fica no painel Propriedades.\n\n"
            "Exemplo: numa página de música com letra grande, o programa fica em dúvida. O Kaique precisa "
            "saber o que fazer se for escrita.\n\n"
            "Só a frase muda; o que o aviso faz continua igual."),
        "exemplos": [img(P + "aviso-hoje-ampliado", "Hoje no programa"),
                     img(P + "aviso-hoje", "Hoje, a tela inteira")],
        "opcoes": [
            {"id": "a", "nome": "A — Diz o caminho",
             "texto": "“…Se for escrita, marque a área com uma ferramenta de marcar e escolha “letra e "
                      "traço”.” Bom: diz o que fazer e com quê. Ruim: não diz onde fica o “letra e traço”.",
             "imgs": [img(P + "aviso-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "aviso-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Curta",
             "texto": "“…Se for escrita, marque como “letra e traço”.” Bom: lê-se num olhar. Ruim: não diz "
                      "como marcar nem onde.",
             "imgs": [img(P + "aviso-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "aviso-b", "A tela inteira")]},
            {"id": "c", "nome": "C — Diz onde fica o “letra e traço”",
             "texto": "“…Confira: se for escrita, marque a área e escolha “letra e traço” no painel "
                      "Propriedades.” Bom: diz onde achar o botão (o Propriedades não abre sozinho com as "
                      "ferramentas de marcar). Ruim: a mais comprida; em 1280 ainda cabe numa linha." + SUG,
             "imgs": [img(P + "aviso-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "aviso-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-dividir-palavra", "ordem": 907, "parte": "Dividir",
        "pergunta": "Na lista “jeito:” do Dividir, “o do programa” passa a se chamar “o do Editor”, como no Endireitar?",
        "explicacao": (
            "O que você está escolhendo: uma palavra. No Endireitar você decidiu que a conta antiga se chama "
            "“Editor” (“a do ScanTailor” e “a do Editor”). No Dividir, a lista de onde dividir a folha ainda "
            "diz “o do programa” e “o do ScanTailor”.\n\n"
            "É a mesma ideia nos dois lugares: o jeito que o Editor já tinha antes de trazer o do ScanTailor. "
            "Só muda o nome; o que a lista faz não muda.\n\n"
            "Nas fotos a lista está aberta. No Boécio ela fica apagada (as folhas dele não são duplas); foi "
            "acesa só para a foto."),
        "exemplos": [img(P + "dividir-endireitar-ja-diz-editor-ampliado", "Já decidido no Endireitar (rodada 13)"),
                     img(P + "dividir-hoje-ampliado", "Hoje no Dividir")],
        "opcoes": [
            {"id": "a", "nome": "A — Fica “o do programa”",
             "texto": "Bom: nada muda. Ruim: o Endireitar diz “Editor” e o Dividir diz “programa” para a mesma "
                      "ideia.",
             "imgs": [img(P + "dividir-a-ampliado", "A parte que muda, ampliada"),
                      img(P + "dividir-a", "A tela inteira")]},
            {"id": "b", "nome": "B — “o do Editor”",
             "texto": "Muda na lista, na parte “Para o livro todo” e na tela “O que fazer”. Bom: a mesma "
                      "palavra em todo lugar. Ruim: nenhum que o agente veja." + SUG,
             "imgs": [img(P + "dividir-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "dividir-b", "A tela inteira")]},
            nao_entendi(),
        ],
    },
    {
        "id": "r14-endireitar-a-mao", "ordem": 908, "parte": "Endireitar",
        "pergunta": "Depois de girar a página à mão, o que o painel do Endireitar mostra embaixo de “Conta”?",
        "explicacao": (
            "O que você está escolhendo: o que aparece na parte “Conta” depois que o Kaique gira a página à "
            "mão (pela bolinha azul ou pelas setas de 0,1°).\n\n"
            "Com o ângulo posto à mão, as duas contas (a do ScanTailor e a do Editor) deixam de valer nesta "
            "página. Hoje a lista fica apagada, quase igual à acesa, e a linha com os dois ângulos some sem "
            "dizer por quê. É como um relógio acertado à mão: o automático para de mandar até alguém pedir "
            "de volta, e o botão para pedir de volta já existe (“usar o ângulo do programa”).\n\n"
            "O contorno amarelo só mostra a parte que muda."),
        "exemplos": [img(P + "mao-antes-ampliado", "Antes de girar à mão: a lista acesa e os dois ângulos"),
                     img(P + "mao-hoje-ampliado", "Hoje, depois de girar à mão")],
        "opcoes": [
            {"id": "a", "nome": "A — Fica como está",
             "texto": "Bom: nada muda. Ruim: não diz por que a linha sumiu, e a lista apagada parece acesa.",
             "imgs": [img(P + "mao-hoje-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-a", "A tela inteira")]},
            {"id": "b", "nome": "B — Uma frase diz por quê",
             "texto": "A lista continua (apagada) e, no lugar da linha dos ângulos, uma frase: “Você pôs o "
                      "ângulo à mão, por isso a conta não vale. Para voltar a ela: “usar o ângulo do "
                      "programa”.” Bom: diz o que aconteceu e como voltar. Ruim: mais texto no painel." + SUG,
             "imgs": [img(P + "mao-b-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-b", "A tela inteira")]},
            {"id": "c", "nome": "C — A lista some, fica só a frase",
             "texto": "Bom: não sobra lista apagada para confundir. Ruim: a parte “Conta” muda de tamanho ao "
                      "girar à mão, e o Kaique não vê qual conta estava valendo.",
             "imgs": [img(P + "mao-c-ampliado", "A parte que muda, ampliada"),
                      img(P + "mao-c", "A tela inteira")]},
            nao_entendi(),
        ],
    },
]

faltam = []
usadas = set()
for q in perguntas:
    for i in q["exemplos"] + [x for o in q["opcoes"] for x in o["imgs"]]:
        nome = i["src"][4:]
        usadas.add(nome)
        if not (PASTA / nome).exists() and not (ANTIGAS / nome).exists():
            faltam.append(nome)
    assert q["explicacao"].startswith("O que você está escolhendo:")
    assert q["explicacao"].count("\n\n") <= 2, q["id"]
    assert sum(SUG.strip() in o["texto"] for o in q["opcoes"]) == 1, q["id"]
    assert q["opcoes"][-1]["nome"] == "Ainda não entendi"
SAIDA.write_text(json.dumps(perguntas, ensure_ascii=False, indent=1), encoding="utf-8")
json.loads(SAIDA.read_text(encoding="utf-8"))
print(len(perguntas), "perguntas;", sum(len(q["opcoes"]) for q in perguntas), "opções;",
      len(usadas), "imagens citadas; faltam:", faltam)
print("novas citadas:", sorted(n for n in usadas if n.startswith(P)))
