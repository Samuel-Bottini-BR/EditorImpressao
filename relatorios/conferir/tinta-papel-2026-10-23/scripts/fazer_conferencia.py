"""Gera o conferencia.json do tp23 (formato da Central) e confere que toda imagem citada existe."""
import json
import os
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
os.chdir(AQUI)


def i(f, legenda):
    return {"src": "tp23/img/" + f, "legenda": legenda}


CAM = ("Caminho: livro novo, ajustes de fábrica (girar 0°, dividir não, endireitar sim, cortar as bordas sim), "
       "o filtro, e a área marcada à mão como \"manter a cor da tinta\" (o nome antigo era \"tinta com a cor\") em cada um dos quatro jeitos.")
D10 = "\"No Preto e branco, tirar a linha preta: as duas opções de papel saem iguais, com a letra limpa\" (resposta 10, 23/10)"
D11 = "Nome do botão: \"manter a cor da tinta\" (resposta 11, 23/10)"
DECISAO = "\"As duas: escolher o papel em cada área ('papel branco' ou 'papel como o resto da página')\" (tc23-1, 22/10)"

d = {
    "id": "tp23",
    "nome": "O papel da área \"manter a cor da tinta\": \"papel branco\" ou \"papel como o resto da página\" (com os ajustes 10 e 11)",
    "trabalho": "fase2-ferramentas-2026-10-22 (b0af839, 3e95076; ajustes 10 e 11: f8691be, c95ba9e; ponta d4c820b)",
    "origem": "verif-tinta-papel-2026-10-23 (antes = 639136a; antes dos ajustes 10 e 11 = 3e95076)",
    "resumo": {
        "titulo": "\"Papel como o resto da página\" tira o retângulo branco; no Preto e branco as duas opções saem iguais, sem a linha preta; o botão se chama \"manter a cor da tinta\"",
        "paragrafos": [
            "Sua resposta: \"As duas: escolher o papel em cada área\". Conferi nas páginas Horas 13, Escola 7, Opus Majus 3 e Graduale 221, pelo caminho inteiro do livro novo.",
            "\"Papel branco\" (o de fábrica): saiu igual ao de antes, ponto por ponto, em 36 de 36 PDFs (Preto e branco, Original e Melhorar; com A, com B e com várias áreas juntas). Um projeto começado antes abre como \"papel branco\" e sai igual (4 de 4).",
            "\"Papel como o resto da página\": no Original e no Melhorar o retângulo branco some. No Original, com \"cor como no livro\", a página sai igual a sem área. A tinta sai igual à do \"papel branco\", tanto no A quanto no B.",
            "Onde duas áreas se cruzam, vale a de cima, e o pincel \"tirar\" devolve a página como ela era.",
            "Na janela de verdade: os quatro botões aparecem e cada área guarda o seu jeito, também depois de fechar e abrir o programa.",
            "Seus ajustes de 23/10. Resposta 10: no Preto e branco, \"papel como o resto da página\" agora sai igual ao \"papel branco\", ponto por ponto, nas 4 páginas, com \"cor como no livro\" e com \"cor escurecida\" (8 de 8). A linha preta em volta da letra sumiu. No Original e no Melhorar o ajuste não mudou nada (40 de 40 PDFs iguais aos de antes).",
            "Resposta 11: o botão se chama \"manter a cor da tinta\". O aviso \"Área escolhida: ...\" e a linha \"Marcado: ...\" embaixo da página também usam o nome novo e não dizem mais \"papel branco\". Projeto gravado antes abre igual (4 de 4).",
            "De fábrica nada mudou: o \"papel branco\" saiu igual ao de antes do ajuste em 36 de 36 PDFs.",
            "Testes no GitHub: 2206 passaram, 0 falharam (rodada 39889891066). Velocidade: nada ficou mais lento (rodada 39886669584).",
        ],
        "veredito": "PRONTO PARA CONFERIR, com ressalvas pequenas (nenhuma muda o que você decidiu).",
    },
    "ressalvas": [
        "No Preto e branco, com \"papel como o resto da página\", o papel da área agora fica branco puro, igual ao \"papel branco\" (é a sua resposta 10). O resto da página no Preto e branco tem uns pontinhos cinza que o filtro deixa; dentro da área eles somem (na Escola 7, 4,5% do papel da área; nas outras, menos de 2%). Nas fotos não se nota retângulo.",
        "Algumas fotos dos quadros 1 a 4, tiradas antes do ajuste, ainda escrevem \"tinta com a cor\" na legenda; o que elas mostram não mudou. As fotos com o nome novo estão no quadro 0.",
        "No Melhorar, \"cor como no livro\" põe a cor do livro na tinta, e não a cor que o Melhorar daria. Com \"papel como o resto da página\", o papel fica o do Melhorar e a letra fica a do livro (um pouco mais apagada que a de fora da área). É o combinado (\"só a tinta segue o A ou o B\"), mas dá para notar.",
        "A B escurece também as linhas vermelhas da pauta do Graduale e a moldura dourada da Horas 13 que caem na área, com qualquer papel. Já era assim antes (pergunta 8).",
        "Graduale 221 em Preto e branco: com qualquer área por cima, a faixa escura da beirada esquerda sai um pouco diferente de sem área. Acontece igual nos quatro jeitos e já acontecia no código de antes; não é desta mudança.",
        "Defeito antigo da tela: ao escolher um botão do \"Marcar como\", os botões do painel aparecem por um instante como janelinhas soltas (21 vezes no roteiro novo e 7 no antigo, que tem menos cliques). Já estava na conferência anterior e continua igual depois dos ajustes (21 vezes de novo). Vai para a Lista de bugs.",
        "Na rodada de 22/10, uma das minhas conferências da janela falhou por erro do meu roteiro (o programa grava cada área em duas listas e eu contei só uma). Consertei o roteiro: na rodada de agora as duas listas conferem, 8 de 8.",
        "Não testei a roda do mouse, o Mágico pro, nem o pincel \"tirar\" pela janela. O \"tirar\" foi conferido nas contas.",
    ],
    "quadros": [
        {
            "id": "tp23-ajustes",
            "nome": "0. Ajustes das suas respostas 10 e 11 (antes e agora)",
            "explicacao": [
                "O que você está olhando, nas quatro primeiras fotos: a letra de perto, no Preto e branco, em três colunas. Coluna 1: como era ANTES do ajuste, com \"papel como o resto da página\" (tinha a linha preta). Coluna 2: como fica AGORA, com \"papel como o resto da página\". Coluna 3: \"papel branco\", o de fábrica. Em cima, \"cor como no livro\"; embaixo, \"cor escurecida\". Caminho: livro novo, ajustes de fábrica (girar 0°, dividir não, endireitar sim, cortar as bordas sim), filtro Preto e branco, e a área \"manter a cor da tinta\" marcada à mão.",
                "Nas outras fotos: a janela do programa (Livro de Horas 13), antes e agora, com o botão de nome novo, o aviso ao escolher uma área, a linha \"Marcado:\" embaixo da página, o \"Ver de perto\" em Preto e branco e o programa aberto de novo.",
            ],
            "olhar": "Se a linha preta em volta da letra sumiu na coluna 2, e se a coluna 2 ficou igual à 3. Na janela, se o botão diz \"manter a cor da tinta\".",
            "texto": "Resposta 10: nas quatro páginas, com A e com B, a coluna 2 saiu igual à coluna 3 ponto por ponto (8 de 8), e a coluna 3 é a mesma de antes do ajuste. A linha preta da coluna 1 sumiu: os pontos do papel que ficavam escuros eram 7.342 na Horas 13, 5.421 na Escola 7, 784 na Opus Majus e 21.198 no Graduale; agora são 0. No Original e no Melhorar o ajuste não mudou nada (40 de 40 PDFs iguais). Resposta 11: o botão diz \"manter a cor da tinta\"; escolhendo uma área, o aviso diz \"Área escolhida: manter a cor da tinta.\"; a linha embaixo diz \"Marcado: ... 3 de manter a cor da tinta.\", sem \"papel branco\". Fechando e abrindo o programa, as três áreas voltam com o jeito delas.",
            "selo": "Bom",
            "ressalva": "No Preto e branco, dentro da área, somem também os pontinhos cinza que o filtro deixa no papel (ver as ressalvas). Nas fotos não se nota.",
            "decisao_do_samuel": D10 + "; " + D11,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("d4c_escola_p007-pb-letra-antes-e-agora.jpg", "Escola 7, Preto e branco, a letra de perto. Coluna 1: antes (linha preta). Coluna 2: agora. Coluna 3: papel branco. Em cima A, embaixo B"),
                i("d4c_horas_p013-pb-letra-antes-e-agora.jpg", "Horas 13, Preto e branco: as mesmas três colunas (os pontinhos pretos da coluna 1 sumiram)"),
                i("d4c_graduale_p221-pb-letra-antes-e-agora.jpg", "Graduale 221, Preto e branco: a pauta vermelha, nas três colunas"),
                i("d4c_opusmajus_p003-pb-letra-antes-e-agora.jpg", "Opus Majus 3, Preto e branco: as três colunas (aqui a linha já era quase nada)"),
                i("d4c_escola_p007-pb-pagina.jpg", "Escola 7, Preto e branco, agora: da esquerda para a direita, sem área; A + papel branco; A + papel da página; B + papel branco; B + papel da página"),
                i("d4c_horas_p013-pb-pagina.jpg", "Horas 13, Preto e branco, agora: os mesmos cinco jeitos"),
                i("d4c_graduale_p221-pb-pagina.jpg", "Graduale 221, Preto e branco, agora: os mesmos cinco jeitos"),
                i("d4c_opusmajus_p003-pb-pagina.jpg", "Opus Majus 3, Preto e branco, agora: os mesmos cinco jeitos"),
                i("jan_03_papel_da_pagina_escolhido.jpg", "Janela ANTES: o botão dizia \"tinta com a cor, papel branco\""),
                i("d4c_jan_1_botao_manter_a_cor_da_tinta.jpg", "Janela AGORA: o botão diz \"manter a cor da tinta\", com os quatro botões embaixo"),
                i("d4c_jan_2_papel_da_pagina_escolhido.jpg", "AGORA: \"papel como o resto da página\" escolhido"),
                i("jan_05_tres_areas_marcadas.jpg", "Janela ANTES: a linha \"Marcado:\" dizia \"3 de tinta com a cor original, papel branco\""),
                i("d4c_jan_3_tres_areas_linha_marcado.jpg", "AGORA: a linha diz \"Marcado: ... 3 de manter a cor da tinta.\""),
                i("d4c_jan_4_area_escolhida_aviso.jpg", "AGORA: escolhendo a área do título, o aviso diz \"Área escolhida: manter a cor da tinta.\""),
                i("d4c_jan_5_ver_de_perto_pb.jpg", "AGORA: \"Ver de perto\" em Preto e branco, com as três áreas"),
                i("d4c_jan_6_reaberto.jpg", "AGORA: o programa aberto de novo, as três áreas voltam"),
            ],
        },
        {
            "id": "tp23-janela",
            "nome": "1. Os quatro botões na janela do programa (prints de antes do nome novo)",
            "explicacao": [
                "O que você está olhando: o Livro de Horas 13 aberto no programa, a ferramenta Retângulo e o painel Propriedades. Cliquei em \"tinta com a cor, papel branco\" (clique do Windows, janela fora da tela).",
                "Marquei três áreas: a 1 com \"cor como no livro\" + \"papel como o resto da página\", a 2 com \"cor escurecida\" + \"papel como o resto da página\" e a 3 com \"cor como no livro\" + \"papel branco\". Depois vi a página no \"Ver de perto\", fechei o programa e abri de novo.",
            ],
            "olhar": "Se os quatro botões aparecem, e se no \"Ver de perto\" só a área 3 (no começo do texto) faz retângulo branco.",
            "texto": "Embaixo de \"tinta com a cor, papel branco\" aparecem \"cor como no livro\" e \"cor escurecida\" lado a lado e, embaixo, \"papel branco\" e \"papel como o resto da página\", um sob o outro e inteiros. De fábrica vêm \"cor como no livro\" e \"papel branco\". Cada área saiu com o jeito escolhido, e as já marcadas não mudaram. No \"Ver de perto\" em Original, o título não tem retângulo; só a área 3 tem (é a do papel branco). Escolhendo \"letra e traço\", os quatro botões somem. Fechando e abrindo o programa, as três áreas voltam com o jeito delas. No código de antes só existem os dois botões da cor.",
            "selo": "Bom",
            "ressalva": "Estes prints são de antes do ajuste 11 (nome antigo do botão). O nome novo está no quadro 0.",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("jan_00_antes_so_os_botoes_da_cor.jpg", "Antes: só os dois botões da cor, sem os do papel"),
                i("jan_01_antes_retangulo_branco.jpg", "Antes: no Original, a área vira um retângulo branco"),
                i("jan_02_quatro_botoes_de_fabrica.jpg", "Depois: os quatro botões, de fábrica \"cor como no livro\" e \"papel branco\""),
                i("jan_03_papel_da_pagina_escolhido.jpg", "\"papel como o resto da página\" escolhido (o nome do tipo continua \"papel branco\", b-11)"),
                i("jan_04_B_e_papel_da_pagina.jpg", "\"cor escurecida\" + \"papel como o resto da página\""),
                i("jan_05_tres_areas_marcadas.jpg", "Três áreas marcadas (a linha \"Marcado:\" diz \"papel branco\" para as três, b-11)"),
                i("jan_06_ver_de_perto_original.jpg", "\"Ver de perto\" em Original: título sem retângulo; só a área 3 (papel branco) faz retângulo"),
                i("jan_07_ver_de_perto_pb.jpg", "\"Ver de perto\" em Preto e branco: as mesmas áreas"),
                i("jan_08_pb_quatro_botoes.jpg", "Preto e branco: os quatro botões também aparecem"),
                i("jan_09_letra_sem_botoes.jpg", "Escolhendo \"letra e traço\", os quatro botões somem"),
                i("jan_10_reaberto.jpg", "Programa aberto de novo: as três áreas voltam"),
                i("jan_11_reaberto_ver_de_perto_original.jpg", "Aberto de novo, \"Ver de perto\" em Original: igual a antes de fechar"),
            ],
        },
        {
            "id": "tp23-original",
            "nome": "2. Nas páginas, em Original e em Melhorar",
            "explicacao": [
                "O que você está olhando: cada página em cinco: sem área; \"cor como no livro\" + \"papel branco\" (o de fábrica); \"cor como no livro\" + \"papel como o resto da página\"; \"cor escurecida\" + \"papel branco\"; \"cor escurecida\" + \"papel como o resto da página\". " + CAM,
                "Cada foto escreve por onde a página passou e com que jeito.",
            ],
            "olhar": "Se o retângulo branco some com \"papel como o resto da página\" e se só a tinta muda com a \"cor escurecida\".",
            "texto": "Com \"papel branco\", a área faz o retângulo branco de sempre. Com \"papel como o resto da página\", o retângulo some: o papel da área fica o mesmo da página (100% dos pontos do papel iguais, nas 4 páginas, no Original e no Melhorar). No Original, \"cor como no livro\" + \"papel como o resto da página\" sai igual à página sem área. Com \"cor escurecida\", só a letra fica mais escura; o papel continua o da página. Fora da área, nada muda (0 pontos diferentes).",
            "selo": "Bom, com ressalva",
            "ressalva": "No Melhorar, \"cor como no livro\" deixa a letra com a cor do livro, um pouco mais apagada que a de fora da área.",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("horas_p013-original-ampliado.jpg", "Horas 13, Original: o título ampliado"),
                i("horas_p013-original-pagina.jpg", "Horas 13, Original: a página"),
                i("escola_p007-original-ampliado.jpg", "Escola 7, Original: o título"),
                i("escola_p007-original-pagina.jpg", "Escola 7, Original: a página"),
                i("opusmajus_p003-original-ampliado.jpg", "Opus Majus 3, Original: a parte de baixo"),
                i("opusmajus_p003-original-pagina.jpg", "Opus Majus 3, Original: a página"),
                i("graduale_p221-original-ampliado.jpg", "Graduale 221, Original: as rubricas"),
                i("graduale_p221-original-pagina.jpg", "Graduale 221, Original: a página"),
                i("horas_p013-melhorar-ampliado.jpg", "Horas 13, Melhorar: o título"),
                i("horas_p013-melhorar-pagina.jpg", "Horas 13, Melhorar: a página"),
                i("graduale_p221-melhorar-ampliado.jpg", "Graduale 221, Melhorar: as rubricas"),
                i("graduale_p221-melhorar-pagina.jpg", "Graduale 221, Melhorar: a página"),
            ],
        },
        {
            "id": "tp23-pb",
            "nome": "3. Preto e branco ANTES do ajuste 10 (a linha preta que você mandou tirar)",
            "explicacao": [
                "O que você está olhando: as mesmas páginas e os mesmos cinco jeitos, em Preto e branco. " + CAM,
                "Estas fotos são de ANTES do ajuste da sua resposta 10 (código 3e95076). Ficam aqui para comparar; como fica agora está no quadro 0.",
            ],
            "olhar": "O contorno preto fino na beirada da letra, nos jeitos com \"papel como o resto da página\".",
            "texto": "No Preto e branco o papel já é branco, então de longe os jeitos ficam quase iguais. De perto, com \"papel como o resto da página\", a letra colorida ganha um contorno preto: é a beirada que o filtro pintou de preto um pouco além da tinta. Na Escola 7 se vê bem; na Horas 13 e no Graduale são pontinhos pretos; na Opus Majus quase não aparece. Com \"papel branco\" não há contorno.",
            "selo": "Corrigido no quadro 0",
            "ressalva": "A linha preta destas fotos já foi tirada (resposta 10).",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("escola_p007-preto_e_branco-letra-de-perto.jpg", "Escola 7: a letra de perto (contorno preto bem visível)"),
                i("escola_p007-preto_e_branco-ampliado.jpg", "Escola 7: o título"),
                i("escola_p007-preto_e_branco-pagina.jpg", "Escola 7: a página"),
                i("horas_p013-preto_e_branco-letra-de-perto.jpg", "Horas 13: a letra de perto (pontinhos pretos)"),
                i("horas_p013-preto_e_branco-ampliado.jpg", "Horas 13: o título"),
                i("horas_p013-preto_e_branco-pagina.jpg", "Horas 13: a página"),
                i("graduale_p221-preto_e_branco-letra-de-perto.jpg", "Graduale 221: a pauta de perto"),
                i("graduale_p221-preto_e_branco-ampliado.jpg", "Graduale 221: as rubricas"),
                i("graduale_p221-preto_e_branco-pagina.jpg", "Graduale 221: a página"),
                i("opusmajus_p003-preto_e_branco-letra-de-perto.jpg", "Opus Majus 3: a letra de perto (quase sem contorno)"),
                i("opusmajus_p003-preto_e_branco-ampliado.jpg", "Opus Majus 3: a parte de baixo"),
                i("opusmajus_p003-preto_e_branco-pagina.jpg", "Opus Majus 3: a página"),
            ],
        },
        {
            "id": "tp23-cruzadas",
            "nome": "4. Duas áreas que se cruzam, e o pincel \"tirar\"",
            "explicacao": [
                "O que você está olhando: duas áreas, uma à esquerda e outra à direita, que se cruzam no meio, cada uma com um jeito; e uma área com o pincel \"tirar\" passado no meio. Caminho: livro novo, ajustes de fábrica, o filtro escrito na foto.",
            ],
            "olhar": "Se no meio vale a área desenhada por último, e se onde passou o pincel \"tirar\" a página volta a ser a do filtro.",
            "texto": "Nos 12 casos (Horas 13 e Graduale 221 em Original, Horas 13 em Preto e branco), o pedaço em que as duas se cruzam ficou com o jeito da área de cima, ponto por ponto. Onde passou o pincel \"tirar\", a página voltou a ser igual à sem área, e o resto da área ficou como estava (6 de 6).",
            "selo": "Bom",
            "ressalva": "",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("horas_p013-original-cruzadas-e-tirar.jpg", "Horas 13, Original"),
                i("graduale_p221-original-cruzadas-e-tirar.jpg", "Graduale 221, Original"),
                i("horas_p013-preto_e_branco-cruzadas-e-tirar.jpg", "Horas 13, Preto e branco"),
            ],
        },
    ],
    "pergunta": {
        "id": "tp23",
        "titulo": "\"Manter a cor da tinta\" com os dois papéis, e os ajustes 10 e 11: o que você decide?",
        "explicacao": [
            "O que você está escolhendo: se os dois papéis entram no programa como estão.",
            "O que mais pesa: o quadro 0, com a linha preta tirada no Preto e branco e o nome novo do botão.",
        ],
        "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"],
    },
    "perguntas": [],
}

(AQUI / "conferencia.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
todas = [x["src"] for q in d["quadros"] for x in q["imgs"]] + [x["src"] for p in d["perguntas"] for x in p["imgs"]]
falta = [s for s in todas if not (AQUI / s.replace("tp23/", "")).is_file()]
print(len(todas), "imagens citadas; faltam:", falta)
