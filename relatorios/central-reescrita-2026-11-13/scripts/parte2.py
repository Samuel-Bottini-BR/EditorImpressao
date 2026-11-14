"""Parte 2 da reescrita da Central (13/11/2026): a aba nomes-28-10 (20 perguntas de nome).

Mesmo jeito da parte1.py: troca só o texto (título, explicação, nome e texto das opções, sugestão,
legendas), mantém os ids das perguntas e das opções, e grava o documento inteiro em
novas/nomes-28-10.json. Fatos conferidos no código da versão de teste em 13/11 (grep dos textos
de tela em ui/ e core/; ver relatorio, Parte 2).
"""
from __future__ import annotations

from parte1 import fixar, gravar, ler, pergunta, trocar_opcoes

SITUACAO = ("Situação: só pergunta; nada mudou no programa. O que o botão faz não muda em nenhuma opção, só o "
            "nome escrito. O nome escolhido entra na tela junto com a arrumação nova do layout, como você pediu "
            "em 04/11 (\"Isso deveria ser feito junto com a repaginação do layout [...] o agente não vai escolher "
            "os nomes ele pode sugerir opções\").")
DEIXAR = {"id": "deixar", "nome": "Deixar como está", "texto": "O nome de hoje continua (o dos prints)."}
NAO_ENTENDI = {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito."}


def q(doc, pid, titulo, explicacao, opcoes, sugestao, primeira=None, legendas=None):
    p = pergunta(doc, pid)
    p["titulo"] = titulo
    p["explicacao"] = explicacao + [SITUACAO]
    trocar_opcoes(p, opcoes + [DEIXAR, NAO_ENTENDI])
    p["sugestao"] = sugestao
    if primeira:
        p["primeira_imagem"] = primeira
    if legendas:
        for e, leg in zip(p.get("exemplos", []), legendas):
            if leg:
                e["legenda"] = leg
    return p


def montar() -> dict:
    doc = ler("nomes-28-10")
    doc["resumo"] = {
        "titulo": "20 perguntas: os nomes de botão que confundem",
        "paragrafos": [
            "Você pediu em 22/10: \"revisarmos todos os nomes de botão\", e em 04/11: \"o agente não vai escolher os "
            "nomes ele pode sugerir opções\". Aqui estão as sugestões, uma pergunta por grupo de botões.",
            "Cada pergunta diz onde o botão fica, o que ele faz e por que o nome confunde, com print. O que o botão faz "
            "não muda em nenhuma opção: só o nome escrito.",
            "Nada mudou no programa. Os nomes que você escolher entram na tela junto com a arrumação nova do layout.",
            "Os nomes que você já aprovou ficaram de fora (ex.: \"deixar como veio\", \"Limpar a sujeira\", \"daqui em "
            "diante\", \"Deixar em branco\" e \"Tirar do livro\").",
        ],
    }
    doc["origem"] = ("Revisão dos nomes que você pediu em 22/10. Textos de tela conferidos no programa de hoje "
                     "(versão de teste) em 13/11; prints de 28/10 e de 13/11, em cópias dos livros.")

    # ---------------------------------------------------------------------------------------------
    q(doc, "nm-esta-bom",
      "Cinco botões quase iguais: \"está certo\", \"está bom assim\", \"aceitar o corte\", \"está bom: todas\" e \"está bom em tudo\"",
      ["Do que se trata: são os botões que dizem \"já olhei\". Ficam na faixa embaixo da página e no painel \"Para "
       "revisar\" (o triângulo laranja, à direita). Cada um faz uma coisa diferente:",
       "\"está certo\" (faixa): a página toda conta como conferida (a barra de espaço faz o mesmo). \"está bom assim\" "
       "(nos avisos): tira só aquele aviso, a página não muda. \"aceitar o corte\" (só no aviso \"Lombada incerta\"): "
       "faz exatamente o mesmo que \"está bom assim\". \"está bom: todas\" (\"Para revisar\" > \"Por motivo\"): tira "
       "aquele aviso de todas as páginas que o têm. \"está bom em tudo\" (pé do \"Para revisar\"): tira todos os "
       "avisos do livro de uma vez.",
       "Por que confunde (teste do Kaique, 26/10, La vida eterna, página 7): \"'Aceitar o corte' e 'está certo' "
       "parecem a mesma coisa\"; \"'está bom: todas' aparece três vezes, sem dizer de qual motivo é\"; e \"está bom "
       "em tudo\" é fácil de apertar sem querer e aprovar 54 páginas sem olhar.",
       "De onde veio: \"está certo\" e \"próxima dúvida\" você aprovou em 05/10; o \"está bom\" em quatro níveis, em "
       "08/10 e 21/10.",
       "O que você escolhe: os nomes desses cinco botões."],
      [{"id": "onde-vale", "nome": "Ficam \"está certo\" e \"está bom\", e cada um diz onde vale (recomendo)",
        "texto": "\"está certo\" fica. \"aceitar o corte\" vira \"está bom assim\" (faz o mesmo). \"está bom: todas\" vira "
                 "\"está bom nas 8 (Parece em branco)\", com o número e o motivo. \"está bom em tudo\" vira \"está bom "
                 "nos 54 avisos\". Mantém as palavras que você aprovou."},
       {"id": "pelo-que-faz", "nome": "Nomes pelo que fazem: \"página conferida\" e \"tirar este aviso\"",
        "texto": "\"está certo\" vira \"página conferida\" (no Dividir, \"folha conferida\"). \"está bom assim\" e "
                 "\"aceitar o corte\" viram \"tirar este aviso\". \"está bom: todas\" vira \"tirar este aviso das 8\". "
                 "\"está bom em tudo\" vira \"tirar todos os 54 avisos\". Troca palavras que você já tinha aprovado."},
       {"id": "so-aceitar", "nome": "Só trocar \"aceitar o corte\" por \"está bom assim\"",
        "texto": "Os outros quatro ficam como estão."}],
      "Ficam \"está certo\" e \"está bom\", e cada um diz onde vale: muda pouco e tira a confusão.")

    q(doc, "nm-antes-de-processar",
      "Janela \"Antes de processar\": os nomes dos cinco botões",
      ["Do que se trata: é a janela que abre quando você clica em \"Confirmar e processar\" (o botão azul grande, "
       "ou menu Arquivo) e ainda há avisos que ninguém olhou. Ela lista as páginas com aviso.",
       "Os botões hoje (Palatino, cópia): \"Selecionar todas\" e \"Nenhuma\" marcam e desmarcam as linhas; \"está bom "
       "nas marcadas\" tira da lista os avisos das linhas marcadas; \"ver\" fecha a janela e leva até a página da "
       "linha; \"continuar assim mesmo\" processa o livro com os avisos.",
       "De onde veio: a janela é sua (08/10, \"Fica assim\"; 21-22/10, a janela menor). Foi nela que você escreveu, "
       "em 22/10: \"os nomes dos botões são horriveis\". O Kaique, em 26/10: \"Muitos botões\".",
       "O que você escolhe: os nomes dos cinco botões."],
      [{"id": "dizem-o-que", "nome": "Nomes que dizem o que acontece (recomendo)",
        "texto": "\"marcar todas\" · \"desmarcar todas\" · \"está bom nas marcadas\" (segue o que você escolher na "
                 "pergunta dos \"está bom\") · \"ir para a página\" · \"processar assim mesmo\"."},
       {"id": "so-baixo", "nome": "Só os dois de baixo mudam",
        "texto": "\"ver\" vira \"ir para a página\"; \"continuar assim mesmo\" vira \"processar com os avisos\". O resto fica."}],
      "Nomes que dizem o que acontece: \"ver\" e \"continuar\" não dizem para onde vão.")

    q(doc, "nm-folha-pagina",
      "\"Folha\" e \"página\" trocadas em vários lugares",
      ["Do que se trata: no programa, \"folha\" é a foto do scan, que pode ter duas páginas do livro (Dividir, girar); "
       "\"página\" é cada página do livro que sai no PDF. Mas em alguns lugares uma palavra aparece no lugar da outra.",
       "Por que confunde (La vida eterna, cópia, dividido: 180 folhas, 360 páginas): o livro aberto mostra \"360 "
       "páginas\" em cima e \"página 9 de 180\" embaixo (contando folhas); \"Ver todas as páginas\" tem a dica \"Todas "
       "as folhas do livro\"; no Automático, \"Endireitar folhas tortas\" endireita páginas; o botão \"tamanho da "
       "folha...\" do Mover muda o tamanho da página que sai. O Kaique (26/10): \"A conta folha ↔ página não é mostrada.\"",
       "De onde veio: em 12/10 você decidiu que as palavras dizem folha ou página conforme o caso (girar = folha, "
       "endireitar = página); em 14/10, que no \"Montar para imprimir\" a folha é o papel da impressora.",
       "O que você escolhe: onde as palavras são trocadas."],
      [{"id": "sua-regra", "nome": "Seguir a sua regra de 12/10 em todo lugar (recomendo)",
        "texto": "\"folha\" só para a foto do scan e para o papel da impressora. Livro aberto: \"180 folhas, 360 páginas\" "
                 "e \"folha 1 de 180\". \"tamanho da folha...\" vira \"tamanho final da página...\". \"Endireitar folhas "
                 "tortas\" vira \"Endireitar páginas tortas\". No \"Para revisar\": \"Página 9 (folha 5)\"."},
       {"id": "so-numeros", "nome": "Só o livro aberto e o \"Para revisar\"",
        "texto": "Conserta os dois lugares onde o número engana. \"tamanho da folha\" e os nomes das etapas ficam."}],
      "Seguir a sua regra de 12/10 em todo lugar.")

    q(doc, "nm-nao-esta",
      "O botão de \"não mexer nesta\" tem um nome em cada ferramenta",
      ["Do que se trata: cada ferramenta da barra da esquerda tem, no painel Propriedades (à direita), parte \"SÓ "
       "NESTA PÁGINA\", um botão que deixa aquela página sem a ferramenta.",
       "Hoje cada uma tem um nome (La vida eterna, cópia): no Endireitar, \"deixar como veio\" (nome escolhido por "
       "você em 12/10); no Dividir, \"não dividir esta\" (a folha sai inteira); no Cortar, \"não cortar esta\" (a "
       "página sai sem cortar a borda); no Mover, \"voltar como veio\" (desfaz o mover e o tamanho). \"não dividir "
       "esta\" e \"não cortar esta\" aparecem também nos avisos \"Não parece dupla\" e \"Corte encostou no texto\".",
       "Por que confunde: o Kaique aprende no Endireitar que \"deixar como veio\" é \"não mexer nesta\"; no Cortar o "
       "mesmo botão tem outro nome, e no Mover um quase igual (\"voltar\").",
       "O que você escolhe: se os outros três passam a ter o mesmo nome que você escolheu para o Endireitar."],
      [{"id": "deixar-como-veio", "nome": "\"deixar como veio\" nas quatro ferramentas (recomendo)",
        "texto": "Dividir, Cortar, Endireitar e Mover: o mesmo nome. Com a folha ainda sem dividir, o botão do "
                 "Dividir continua \"dividir esta\"."},
       {"id": "completar", "nome": "Completar o nome antigo",
        "texto": "\"não dividir esta folha\", \"não cortar esta página\"; o Mover passa a \"deixar como veio\"."}],
      "\"deixar como veio\" nas quatro: é o nome que você já escolheu.")

    q(doc, "nm-limpar-a-folha",
      "Etapa \"Limpar a folha\" do Automático e painel \"Filtro da página\"",
      ["Do que se trata: o filtro (Original, Preto e branco, Melhorar...) se escolhe em dois lugares. (1) No "
       "Automático (painel Automático > \"abrir em janela grande\"), a etapa \"4 Limpar a folha\", com o subtítulo "
       "\"tira o amarelado\": escolhe o filtro do livro todo. (2) No painel \"Filtro da página\" (ícone da meia-lua, "
       "à direita), que muda esta página e tem embaixo \"só nesta / todas / daqui em diante\".",
       "Por que confunde (Boécio, cópia, livro novo): a etapa diz \"tira o amarelado\", mas vem com \"Original\", que "
       "não mexe na página: o nome promete limpar e nada é limpo. E o painel se chama \"da página\", mas o \"todas\" "
       "dele muda o livro inteiro: o Kaique (26/10) procurou no Automático e não imaginou que era no painel.",
       "De onde veio: \"Limpar a sujeira\" (os pontinhos) é nome seu e fica. \"Limpar a folha\" e \"Filtro da página\" "
       "nunca foram perguntados.",
       "O que você escolhe: o nome da etapa e, se quiser, o do painel."],
      [{"id": "filtro-do-livro", "nome": "A etapa se chama \"Filtro do livro\" e mostra o filtro escolhido (recomendo)",
        "texto": "\"Filtro do livro — hoje: Original (não mexe na página)\"; o subtítulo muda quando o filtro muda. O "
                 "painel continua \"Filtro da página\"."},
       {"id": "os-dois", "nome": "A etapa vira \"Filtro do livro\" e o painel vira só \"Filtro\"",
        "texto": "Sem o \"da página\", porque o painel muda uma página, as próximas ou todas."}],
      "A etapa \"Filtro do livro\": diz o que ela escolhe.")

    q(doc, "nm-scantailor",
      "A palavra \"ScanTailor\" nos nomes das caixinhas e no aviso das contas",
      ["Do que se trata: ScanTailor é o programa de onde vieram várias ferramentas. O nome dele aparece na tela em "
       "quatro lugares: no Automático (janela grande), etapa \"Cortar as bordas\": \"Cortar a beirada da folha "
       "vizinha — o corte da sobra do ScanTailor\" e \"Cortar seguindo o conteúdo (como o ScanTailor)\"; nas "
       "Configurações e no Automático: \"fica no mesmo lugar (como o ScanTailor)\"; e no aviso \"Endireitar: as contas "
       "discordam\": \"A conta do ScanTailor e a do Editor acharam inclinações diferentes nesta página\".",
       "Por que confunde: no teste do Kaique (26/10), \"o Kaique não sabe o que é ScanTailor nem qual 'Editor'\". No "
       "Boécio (cópia), esse aviso apareceu em 12 das 50 páginas.",
       "De onde veio: \"o do ScanTailor / o do Editor\" (Dividir e Endireitar) são nomes seus (12/10 e 20/10) e ficam "
       "fora desta pergunta. \"Fica no mesmo lugar\" você aprovou (09/10) sem o \"(como o ScanTailor)\". Os outros "
       "ninguém aprovou.",
       "O que você escolhe: se \"ScanTailor\" sai desses nomes e do aviso."],
      [{"id": "tirar-dos-nomes", "nome": "Tirar \"ScanTailor\" dos nomes; ele fica só no balão do mouse (recomendo)",
        "texto": "\"Cortar seguindo o conteúdo\", \"Cortar a beirada da folha vizinha\", \"fica no mesmo lugar\". O aviso "
                 "vira \"Endireitar: dois ângulos diferentes\" — \"As duas contas do Endireitar acharam ângulos "
                 "diferentes nesta página. Confira e escolha a que deixou o texto reto.\" Os nomes que você aprovou ficam."},
       {"id": "so-caixinhas", "nome": "Só nos nomes das caixinhas",
        "texto": "O aviso das contas fica como está."}],
      "Tirar dos nomes: quem usa não precisa saber de onde a ferramenta veio.")

    q(doc, "nm-tirada",
      "Página tirada do livro aparece como \"apagada\"",
      ["Do que se trata: o botão \"Tirar do livro\" (painel Propriedades > \"Esta página\", menu Página, ou Shift+Del) "
       "deixa a página fora do PDF. Depois, a mesma página aparece como \"apagada\": na miniatura, na grade, na janela "
       "de salvar (\"126 páginas vão para o PDF, e 8 foram apagadas.\"), no contador de baixo e na mensagem \"Restaure "
       "alguma página apagada.\"",
       "Por que confunde: na sessão de testes (2-2) você escreveu: \"quando eu clico em tirar do livro a pagina fica "
       "como apagada, mas não é tirada do pc\". \"apagada\" parece que sumiu de vez, e não há botão \"apagar\" (o de "
       "voltar se chama \"trazer de volta\").",
       "De onde veio: os botões \"Deixar em branco\" e \"Tirar do livro\" são seus (07/10 e 09/10). A palavra "
       "\"apagada\" não foi perguntada.",
       "O que você escolhe: a palavra que aparece depois de tirar a página."],
      [{"id": "tirada", "nome": "\"tirada do livro\" em todo lugar (recomendo)",
        "texto": "\"359 páginas vão para o PDF; 1 foi tirada do livro\", \"tirada\" na miniatura e no contador, e "
                 "\"Traga de volta alguma página tirada do livro\"."},
       {"id": "fora", "nome": "\"fora do livro\"",
        "texto": "\"359 páginas vão para o PDF; 1 ficou fora do livro\"; a miniatura diz \"fora\"."}],
      "\"tirada do livro\": a mesma palavra do botão.")

    q(doc, "nm-frase-salvar",
      "A frase da janela de salvar: \"Ainda há 6 páginas que você não conferiu\"",
      ["Do que se trata: é a janela \"Onde salvar o livro pronto\", que abre depois do \"Confirmar e processar\". "
       "Embaixo do nome do arquivo ela diz: \"Ainda há N páginas que você não conferiu. Dá para processar assim mesmo, "
       "mas o que não foi olhado sai do jeito que o programa decidiu sozinho.\"",
       "Por que confunde (Palatino, cópia): o livro tem 32 de 134 páginas conferidas, mas a janela diz \"Ainda há 6 "
       "páginas que você não conferiu\". O 6 são as páginas COM AVISO que ninguém olhou; a frase parece falar das 102 "
       "sem \"está certo\". No teste de 26/10 o Kaique não soube se tinha terminado.",
       "De onde veio: em 21/10 você decidiu que a janela conta as páginas com aviso pendente. O número está certo; só "
       "a frase ficou para esta revisão.",
       "O que você escolhe: as palavras da frase."],
      [{"id": "com-aviso", "nome": "\"Ainda há 6 páginas com aviso que você não olhou.\" (recomendo)",
        "texto": "O resto da frase fica. Usa a mesma ideia do painel \"Para revisar\"."},
       {"id": "no-revisar", "nome": "\"Ainda há 6 páginas no 'Para revisar'.\"",
        "texto": "Diz o lugar onde elas estão."}],
      "\"com aviso que você não olhou\": diz que número é esse.")

    q(doc, "nm-historico",
      "O Histórico escreve outros nomes, diferentes dos botões",
      ["Do que se trata: o painel Histórico (ícone do relógio, à direita; ou Editar > \"Mostrar o histórico\") é a "
       "lista do que foi feito. Clicando numa linha, o trabalho volta até ali.",
       "Por que confunde (Palatino, cópia, com as suas linhas de 28/10): o botão é \"está certo\" e a linha diz "
       "\"Conferir a pagina 7\" (sem acento); o botão é \"deixar como veio\" e a linha diz \"Não endireitar a página "
       "9\"; o botão é \"usar o corte do programa\" e a linha diz \"Voltar ao corte automático na página 9\"; na tela "
       "é \"Jeito do preto e branco\" e a linha diz \"Algoritmo do Preto e branco na página 9: Otsu\". O Kaique clica "
       "num botão e o Histórico mostra outro nome; na hora de voltar atrás, não reconhece a linha.",
       "De onde veio: os nomes dos botões são seus (12/10); o acento, você mandou corrigir em 18/07. As linhas do "
       "Histórico não foram perguntadas.",
       "O que você escolhe: como as linhas do Histórico são escritas."],
      [{"id": "nome-do-botao", "nome": "Cada linha repete o nome do botão clicado, com a página (recomendo)",
        "texto": "\"usar o corte do programa — página 5\", \"deixar como veio — página 5\", \"está certo — página 5\", "
                 "\"Jeito do preto e branco da página 5: Otsu\", \"linha de dividir da folha 4\"."},
       {"id": "so-tecnicas", "nome": "Só trocar as palavras técnicas e o acento",
        "texto": "\"Algoritmo\" vira \"Jeito do preto e branco\", \"Conferir a pagina\" vira \"Conferida a página\", "
                 "\"Posição/tamanho\" vira \"Lugar e tamanho\". O resto fica."}],
      "Cada linha repete o nome do botão: o Kaique reconhece o que clicou.")

    q(doc, "nm-dois-mover",
      "Duas ferramentas \"Mover\" na barra da esquerda",
      ["Do que se trata: na barra da esquerda (e no menu Ferramentas) há duas ferramentas com quase o mesmo nome. "
       "\"Mover e redimensionar\" (tecla F) mexe a página inteira dentro da folha e aumenta ou diminui. \"Mover e "
       "mudar o tamanho da área\" (tecla A) mexe uma área marcada (gravura, letra, papel).",
       "Por que confunde: \"redimensionar\" e \"mudar o tamanho\" dizem a mesma coisa, e as duas começam com \"Mover\".",
       "De onde veio: \"quero conseguir redimensionar o conteudo tambem\" é seu (22/09). O NOME \"Mover e "
       "redimensionar\" foi escolhido pela gerente, sem perguntar a você (27/10).",
       "O que você escolhe: os nomes das duas ferramentas."],
      [{"id": "pagina-area", "nome": "\"Mover a página\" (F) e \"Mover a área marcada\" (A) (recomendo)",
        "texto": "O nome diz o que anda: a página inteira ou só a área marcada. O balão do mouse diz que as duas "
                 "também aumentam e diminuem."},
       {"id": "aumentar", "nome": "\"Mover e aumentar a página\" (F) e \"Mover e aumentar a área\" (A)",
        "texto": "O nome diz as duas coisas que cada uma faz."}],
      "\"Mover a página\" e \"Mover a área marcada\": a diferença fica no nome.")

    q(doc, "nm-menu-marcar",
      "Menu \"Marcar\": \"Procurar de novo\", \"Limpar tudo\" e \"Deixar a folha em branco\"",
      ["Do que se trata: são itens do menu Marcar (na linha dos menus) e do painel Propriedades quando uma "
       "ferramenta de marcar está escolhida (ex.: Retângulo).",
       "Por que confunde: \"Procurar de novo\" (menu) e \"detectar automaticamente\" (botão do painel) fazem a mesma "
       "coisa: procuram de novo a gravura, a letra e o papel da página — dois nomes para uma ação; e \"procurar de "
       "novo\" é também o botão do cartão do livro que mudou de lugar (outra coisa). \"Limpar tudo\" tira todas as "
       "marcações da página, mas \"Limpar\" no programa já quer dizer o filtro e os pontinhos. \"Deixar a folha em "
       "branco\" (menu Marcar) marca a página inteira como papel; no menu Página há \"Deixar esta página em branco\" "
       "(tecla Del), quase o mesmo resultado: um diz folha, o outro página.",
       "De onde veio: \"eu quero ter opção de transformar uma capa em branco\" é seu (06/08). Os nomes não foram perguntados.",
       "O que você escolhe: os nomes dos itens do menu Marcar."],
      [{"id": "pelo-que-faz", "nome": "Nomes pelo que fazem (recomendo)",
        "texto": "\"Procurar de novo nesta página\" (no menu e no botão, o mesmo nome) · \"Tirar todas as marcações\" · "
                 "\"Marcar a página inteira como papel\"."},
       {"id": "so-igualar", "nome": "Só igualar o menu e o botão",
        "texto": "Os dois viram \"Procurar de novo nesta página\"; \"Limpar tudo\" e \"Deixar a folha em branco\" ficam."}],
      "Nomes pelo que fazem.")

    q(doc, "nm-manter-cor-tinta",
      "\"manter a cor da tinta\": o nome provisório",
      ["Do que se trata: com uma ferramenta de marcar (ex.: Retângulo), o painel Propriedades tem a parte \"Marcar "
       "como\", com \"gravura ou foto\", \"letra e traço\", \"papel\", \"pintar por cima\", \"tinta preta, fundo "
       "original\" e \"manter a cor da tinta\".",
       "O que ele faz: a área marcada sai com a tinta na cor do livro. Exemplo: no Livro de Horas 13, numa página em "
       "Preto e branco, o título vermelho marcado assim sai vermelho.",
       "De onde veio: em 22/10 você escreveu \"não tem outro nome para recomendar? eu nem entendi para que serve esse "
       "botão.\" e depois \"esse botão ainda é bem confuso, mas por enquanto pode ficar assim.\" \"tinta preta, fundo "
       "original\" é nome seu (05/10).",
       "O que você escolhe: o nome definitivo."],
      [{"id": "tinta-colorida", "nome": "\"tinta colorida\" (recomendo)",
        "texto": "Faz par com \"tinta preta, fundo original\": um deixa a tinta preta, o outro deixa a tinta com a cor."},
       {"id": "letra-colorida", "nome": "\"letra colorida\"",
        "texto": "Diz o uso mais comum (o título vermelho), mas o botão serve também para desenho."}],
      "\"tinta colorida\": faz par com o nome que você já escolheu.")

    q(doc, "nm-montar-dois",
      "Dois \"montar cadernos\" com nomes parecidos",
      ["Do que se trata: há dois jeitos de sair em cadernos. (1) No Automático (janela grande), a etapa \"7 Montar "
       "cadernos\": o próprio PDF do livro sai em cadernos, no tamanho do scan e sem margem. (2) Na tela \"Ficou "
       "pronto!\" (depois de processar), o botão \"montar para imprimir em A4 (com margens)...\": o PDF do livro não "
       "muda e sai outro arquivo, arrumado para a impressora.",
       "Por que confunde: o Kaique quer cadernos para a impressora, vê \"Montar cadernos\" no Automático e liga; o PDF "
       "sai em folhas de dobro de largura, sem margem.",
       "De onde veio: em 22/10 você mandou \"Deixar os dois\". Os dois ficam; só o nome está em pergunta.",
       "O que você escolhe: o nome da etapa e, se quiser, o do botão."],
      [{"id": "pdf-ja-em-cadernos", "nome": "A etapa diz que o PDF já sai em cadernos (recomendo)",
        "texto": "Etapa: \"PDF já em cadernos (tamanho do scan, sem margem)\". O botão da \"Ficou pronto!\" fica "
                 "\"montar para imprimir em A4 (com margens)...\"."},
       {"id": "os-dois", "nome": "Os dois mudam",
        "texto": "Etapa: \"Cadernos sem margem (tamanho do scan)\"; botão: \"cadernos em A4 para a impressora...\"."}],
      "A etapa diz que o PDF já sai em cadernos.")

    q(doc, "nm-montar-nomes",
      "Janela \"Montar para imprimir\": os nomes das opções",
      ["Do que se trata: a janela \"Montar para imprimir\" (tela \"Ficou pronto!\" > \"montar para imprimir em "
       "A4...\") usa os nomes da janela de imprimir do UPDF, porque você pediu \"TODAS essas opções\" (14/10).",
       "Os que mais confundem (Boécio, cópia): \"Ordem de páginas:\" (escolhe frente e verso, só a frente ou só o "
       "verso; na janela \"imprimir agora\" a mesma escolha se chama \"Lados do papel:\"); \"Folhas de (0 = todas):\"; "
       "\"Rotação automática\"; \"Centralizar automático\"; \"Reverter páginas\"; \"Agrupar\"; \"Encadernação: Esquerda / "
       "Direita\". O Kaique (26/10): \"muitas opções técnicas para quem só quer cadernos\".",
       "De onde veio: as opções são suas (14/10); em 22/10: \"Só tem que melhorar esse layout [...] dificil de saber o "
       "que é o que.\" Um agente tinha encurtado os nomes sem perguntar; eles voltaram aos do UPDF em 27/10. Em 08/11 "
       "você já decidiu a caixinha \"Imprimir só algumas folhas\" no lugar do \"0 = todas\".",
       "O que você escolhe: os nomes das outras opções desta janela."],
      [{"id": "nomes-9a", "nome": "Nomes curtos, que dizem o que fazem (recomendo)",
        "texto": "\"Ordem de páginas\" → \"Lados do papel\" (igual ao \"imprimir agora\") · \"Páginas por caderno\" → "
                 "\"Cada caderno\" · \"Esquerda / Direita\" → \"costura à esquerda / à direita\" · \"Rotação automática\" "
                 "→ \"Girar sozinho a página deitada\" · \"Centralizar automático\" → \"Centralizar sozinho\" · \"Reverter "
                 "páginas\" → \"Ordem invertida\" · \"Agrupar\" → \"Agrupar as cópias\"."},
       {"id": "so-tres", "nome": "Só os que mais confundem",
        "texto": "\"Ordem de páginas\" → \"Lados do papel\"; \"Reverter páginas\" → \"Ordem invertida\". O resto fica "
                 "com o nome do UPDF."}],
      "Nomes curtos que dizem o que fazem.")

    q(doc, "nm-montar-frases",
      "Janela \"Montar para imprimir\": as frases pequenas embaixo das opções",
      ["Do que se trata: na janela \"Montar para imprimir\", embaixo das opções, há frases pequenas que um agente pôs "
       "sem você pedir. Exemplos: no alto, \"O PDF do livro não muda: aqui só se arrumam as folhas para a "
       "impressora.\"; embaixo de \"Imprimir como imagem\", \"Ligada de fábrica: sem ela pode sair algo errado.\"; "
       "embaixo de \"Agrupar\", \"Sai o livro inteiro, depois o livro inteiro de novo.\"",
       "De onde veio: escolha de agente, sem pedido seu. Em 27/10 você pediu \"é só para fazer o que eu já tinha "
       "mandado\"; em 22/10, que a janela fosse menos \"dificil de saber o que é o que\".",
       "O que muda: com \"Saem\", ficam só as frases que já estavam entre parênteses no nome (como antes).",
       "O que você escolhe: se as frases novas ficam."],
      [{"id": "ficam-agrupar", "nome": "Ficam, e a do \"Agrupar\" fica mais clara (recomendo)",
        "texto": "\"Sai o livro inteiro, depois o livro inteiro de novo.\" vira \"Com 2 cópias: sai o livro inteiro, e "
                 "depois a segunda cópia inteira.\" As outras ficam."},
       {"id": "saem", "nome": "Saem as frases novas",
        "texto": "Ficam só as que já estavam entre parênteses no nome."}],
      "Ficam: explicam cada opção sem mudar o que ela faz.")

    q(doc, "nm-atalhos",
      "Teclas escritas em inglês nos menus e a lista de atalhos escondida",
      ["Do que se trata: nos menus, à direita de cada item, aparece a tecla que faz o mesmo; e a Ajuda (F1) tem a "
       "\"Lista de atalhos\".",
       "Como é hoje: nos menus as teclas aparecem como o Windows escreve em inglês: \"Ctrl+Return\" (Arquivo > "
       "Confirmar e processar), \"Ctrl+Left\" e \"Ctrl+Right\" (Página > girar ¼), \"Del\" e \"Shift+Del\". Na Ajuda "
       "(F1), a janela mostra só \"O que dá para fazer, e por qual tecla:\"; a lista fica escondida atrás de um botão "
       "em inglês, \"Show Details...\".",
       "De onde veio: em 18/07 você mandou: \"Corrija TODOS os textos da interface para português correto\".",
       "O que você escolhe: o que muda nas teclas e na lista."],
      [{"id": "portugues", "nome": "Teclas em português e a lista à vista (recomendo)",
        "texto": "\"Ctrl+Enter\", \"Ctrl+seta para a esquerda\", \"Ctrl+seta para a direita\", \"Delete\", \"Shift+Delete\"; "
                 "a janela abre já com a lista inteira, sem o botão."},
       {"id": "so-botao", "nome": "Só o botão em português",
        "texto": "\"Show Details...\" vira \"Ver a lista\"; as teclas ficam como o Windows escreve."}],
      "Teclas em português e a lista à vista: é o que você mandou em 18/07.")

    p = q(doc, "nm-codigos",
          "Códigos internos (\"D-068\", \"D-094\", \"G2\") em três textos do Automático",
          ["Do que se trata: três textos do Automático trazem códigos do projeto, que o Kaique não sabe o que são: o "
           "balão do mouse do botão \"desligar as marcadas\" (\"... (D-068: toda função automática liga e desliga) ...\"); "
           "o balão da lista \"Quando o ângulo muda depois do corte à mão, o corte:\" (\"D-094: a mesma escolha existe "
           "nas Configurações...\"); e uma frase escrita na tela, na etapa Dividir: \"Livro novo não divide sozinho: só "
           "quando esta etapa roda (G2).\"",
           "Você já decidiu: em 09/11, \"Não se deve usar código na nomeação de coisas\", e mandou consertar: nenhum "
           "código interno aparece na tela. Isso já está na fila de consertos. Conferi hoje (13/11): os três ainda "
           "estão no programa.",
           "O que falta decidir: tirar só o código e deixar o resto da frase, ou tirar também a parte que fala da regra.",
           "O que você escolhe: como fica a frase sem o código."],
          [{"id": "tirar-codigos", "nome": "Tirar só os códigos e deixar o resto da frase (recomendo)",
            "texto": "Ex.: \"A mesma escolha existe nas Configurações (para todos os livros) e na ferramenta Endireitar "
                     "(só uma página).\""},
           {"id": "tirar-frase", "nome": "Tirar também a parte da frase que fala da regra",
            "texto": "Ex.: \"Tira o automático das etapas marcadas, onde está escolhido em 'Rodar'. O Desfazer traz de volta.\""}],
          "Tirar só os códigos: o resto da frase explica.")
    p["explicacao"][-1] = ("Situação: o conserto (tirar os códigos) já foi decidido por você em 09/11 e está na fila. "
                           "Esta pergunta é só sobre o resto da frase.")
    # "Deixar como está" contraria a decisão de 09/11 (D-687): fica a opção (ids não saem), com o aviso
    for o in p["opcoes"]:
        if o["id"] == "deixar":
            o["nome"] = "Deixar como está (contra o que você decidiu em 09/11)"
            o["texto"] = "Os códigos continuariam na tela. Você mandou tirar em 09/11."

    # ---- as três que voltaram com "não entendi" -------------------------------------------------
    p = q(doc, "nm-tela-livros",
          "Tela dos livros: três coisas com dois nomes cada",
          ["Do que se trata: é a primeira tela do programa, com um cartão para cada livro (da área de trabalho: Arquivo > "
           "\"Voltar para os livros\"). Nela, três coisas aparecem com dois nomes diferentes. O print mostra cada uma.",
           "1. Tirar o livro da lista. No menu \"Mais...\" (ou botão direito no cartão) o item se chama \"remover da "
           "lista\"; a janela que abre pergunta \"Tirar da lista?\" e o botão é \"Tirar da lista\". O livro em PDF não "
           "é apagado. \"Tirar da lista\" é nome seu (29/09).",
           "2. Achar o PDF que mudou de pasta. O cartão mostra \"o PDF saiu do lugar\" e o botão \"procurar de novo\"; no "
           "menu \"Mais...\" o mesmo se chama \"procurar o livro\". E \"Procurar de novo\" é também um item do menu Marcar, "
           "que faz outra coisa.",
           "3. \"Livro\" ou \"projeto\". O programa todo diz \"livro\", mas a busca diz \"Nenhum projeto com 'horas' no "
           "nome.\" e a janela de mudar o nome diz \"Nome deste projeto:\".",
           "O que você escolhe: se cada coisa passa a ter um nome só, e se \"projeto\" vira \"livro\"."],
          [{"id": "um-nome", "nome": "Um nome só para cada coisa, e \"livro\" no lugar de \"projeto\" (recomendo)",
            "texto": "1: \"tirar da lista\" no menu e na janela. 2: \"procurar o livro\" no cartão e no menu. 3: "
                     "\"Nenhum livro com 'horas' no nome\", \"Nome deste livro:\"."},
           {"id": "so-botoes", "nome": "Só os itens 1 e 2; \"projeto\" fica",
            "texto": "\"tirar da lista\" e \"procurar o livro\" nos dois lugares; a busca e o \"Renomear\" continuam "
                     "dizendo \"projeto\"."}],
          "Um nome só para cada coisa: o Kaique vê sempre a mesma palavra.",
          primeira={"src": "imagens/nm-tela-livros-resumo.png",
                    "legenda": "Tela dos livros (cópias, print de 28/10). 1: o menu diz \"remover da lista\" e a janela "
                               "diz \"Tirar da lista\". 2: o cartão diz \"procurar de novo\" e o menu diz \"procurar o "
                               "livro\". 3: a busca diz \"projeto\". O que olhar está no contorno vermelho."})
    fixar(p, "samuel", "2026-11-13T23:19:09.649Z",
          "Suas respostas ainda não são claras, tem que rever isso, não consegui entender, tem que ser de fácil entendimento.")

    p = q(doc, "nm-desligar-marcadas",
          "Automático: o nome do botão \"desligar as marcadas\"",
          ["Do que se trata: no painel Automático (à direita, ícone das linhas com seta), embaixo de tudo, há o botão "
           "\"desligar as marcadas\". Ele DESFAZ o que o Automático fez nas etapas que estão com a caixinha marcada, no "
           "lugar escolhido em \"Rodar\" (livro todo, esta página ou as escolhidas). O Desfazer (Ctrl+Z) traz de volta.",
           "Exemplo de verdade (Gradus, cópia, hoje; print): rodei o Automático só com \"Dividir folhas ao meio\" no "
           "livro todo, e as 70 folhas viraram 140 páginas (faixa azul). Com a etapa Dividir marcada e \"Rodar: no livro "
           "todo\", cliquei \"desligar as marcadas\": cada folha voltou a ser uma página só, com as duas páginas juntas, e a caixinha da etapa ficou desmarcada (faixa verde).",
           "Por que o nome confunde: \"as marcadas\" pode ser lido como as PÁGINAS marcadas na grade \"Todas as "
           "páginas\", mas são as ETAPAS marcadas. E caixinha marcada costuma querer dizer \"ligado\", mas aqui o botão "
           "desfaz justamente o que está marcado.",
           "De onde veio: o botão é pedido seu (24/09: \"Toda função automática tem botão de ligar e desligar.\"). O "
           "NOME foi escolhido pela gerente, sem perguntar a você (27/10).",
           "O que você escolhe: o nome do botão."],
          [{"id": "estas-etapas", "nome": "\"desfazer estas etapas\" (recomendo)",
            "texto": "Diz que desfaz e que é das etapas. Balão do mouse: \"Desfaz o que o automático fez nas etapas "
                     "marcadas, onde está escolhido em Rodar. O Desfazer traz de volta.\""},
           {"id": "nao-fazer", "nome": "\"tirar o automático das etapas marcadas\"",
            "texto": "Mais comprido, mas diz tudo no próprio botão."}],
          "\"desfazer estas etapas\": curto e diz o que acontece.",
          primeira={"src": "imagens/nm-desligar-marcadas-resumo.png",
                    "legenda": "Gradus (cópia), versão de teste. Azul: depois de rodar o Automático só com \"Dividir "
                               "folhas ao meio\", as folhas ficam divididas (140 páginas). Verde: com a etapa Dividir "
                               "marcada, \"desligar as marcadas\": as folhas voltam inteiras."})
    fixar(p, "samuel", "2026-11-13T23:16:24.087Z", "Eu não entendi o que você quis dizer.")

    p = q(doc, "nm-jeito-pb",
          "Preto e branco: os nomes da lista \"Jeito do preto e branco\" (Sauvola, Otsu, Wolf)",
          ["Do que se trata: numa página em Preto e branco, o painel \"Filtro da página\" (à direita) tem, em \"Mais "
           "ajustes\", a lista \"Jeito do preto e branco\". São maneiras diferentes de o programa decidir o que vira "
           "preto e o que vira branco. Uma serve melhor para letra fina, outra para letra grossa, outra para scan "
           "apagado.",
           "O que há hoje na lista: \"Automático\" (de fábrica: o programa escolhe por página), \"Sauvola (padrão)\", "
           "\"Otsu (letra grossa/gótica)\", \"Wolf (scan de baixo contraste)\" e mais dez \"... do ScanTailor\". O print "
           "mostra a mesma página do Palatino (cópia, página 9) com cada um dos quatro primeiros.",
           "Por que o nome confunde: \"Sauvola\", \"Otsu\" e \"Wolf\" são sobrenomes dos inventores dessas contas: não "
           "dizem para que servem. \"Sauvola (padrão)\" diz \"padrão\", mas o de fábrica é o \"Automático\". E "
           "\"Automático\" é também o nome do painel Automático.",
           "De onde veio: os dez \"do ScanTailor\" você mandou pôr como estão (21/10) e ficam fora desta pergunta. Os "
           "quatro primeiros nunca foram perguntados.",
           "O que você escolhe: os nomes dos quatro primeiros da lista."],
          [{"id": "pelo-uso", "nome": "Pelo uso, sem \"(padrão)\" (recomendo)",
            "texto": "\"o programa escolhe\" (de fábrica) · \"letra fina\" · \"letra grossa ou gótica\" · \"scan "
                     "apagado\". O nome técnico fica no balão do mouse."},
           {"id": "so-padrao", "nome": "Só tirar o \"(padrão)\" do Sauvola",
            "texto": "\"Automático\" · \"Sauvola\" · \"Otsu (letra grossa/gótica)\" · \"Wolf (scan de baixo contraste)\"."}],
          "Pelo uso: o Kaique escolhe pelo tipo de letra que está vendo.",
          primeira={"src": "imagens/nm-jeito-pb-resumo.png",
                    "legenda": "Palatino (cópia), página 9, Preto e branco, desenhada pela mesma conta do PDF: o mesmo "
                               "pedaço com cada um dos quatro primeiros da lista. Onde olhar: a grossura e os buracos "
                               "das letras."})
    return doc


if __name__ == "__main__":
    gravar("nomes-28-10", montar())
    print("ok")
