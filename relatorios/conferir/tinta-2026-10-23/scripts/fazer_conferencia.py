"""Gera o conferencia.json do tc23 (formato da Central) e confere que toda imagem citada existe."""
import json
import os
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
os.chdir(AQUI)


def i(f, legenda):
    return {"src": "tc23/img/" + f, "legenda": legenda}


CAM = ("Caminho: livro novo, ajustes de fábrica (girar 0°, dividir não, endireitar sim, cortar as bordas sim), "
       "o filtro, e a área marcada à mão como \"tinta com a cor, papel branco\".")
DECISAO = "\"As duas: A e B como opções separadas\" (b-8, 22/10)"

d = {
    "id": "tc23",
    "nome": "\"Tinta com a cor original\" em dois jeitos: \"cor como no livro\" (A) e \"cor escurecida\" (B)",
    "trabalho": "fase2-ferramentas-2026-10-22 (8226f33, 41fa7bc; ponta 639136a)",
    "origem": "verif-tinta-2026-10-23 (antes = f26407c)",
    "resumo": {
        "titulo": "Os dois jeitos da \"tinta com a cor\" funcionam: o A sai igual ao de antes e o B escurece a tinta só dentro da área",
        "paragrafos": [
            "Sua resposta: \"As duas: A e B como opções separadas\". Conferi nas páginas Horas 13, Escola 7, Opus Majus 3, Horas 11 (folha de rosto) e Graduale 221, pelo caminho inteiro do livro novo.",
            "A, \"cor como no livro\" (o de fábrica): saiu igual ao de antes, ponto por ponto, em 25 de 25 PDFs (Preto e branco, Original e Melhorar). Um projeto começado antes, sem o campo novo, abre como A e sai igual.",
            "B, \"cor escurecida\": o vermelho vira vermelho-escuro, o azul vira azul-marinho, a tinta desbotada fica marrom-escura. Fora da área, nada muda (0 pontos diferentes).",
            "Na janela de verdade: escolhendo \"tinta com a cor, papel branco\" no \"Marcar como\", aparecem os dois botões; cada área guarda o seu jeito, também fechando e abrindo o programa (38 de 38 conferências).",
            "Testes no GitHub: 2185 passaram, 0 falharam (rodada 39850503362). Velocidade: igual (rodada 39849559789).",
        ],
        "veredito": "PRONTO PARA CONFERIR, com ressalvas (a principal: a B escurece também o dourado e a moldura que caem dentro da área).",
    },
    "ressalvas": [
        "A B escurece tudo o que for tinta dentro da área, não só a letra: na Horas 11, os cantos da moldura laranja e o dourado das letras de \"LOUIS\" ficam escuros. Já estava na pergunta 8.",
        "A cor fica de 10 a 23 % mais forte no PDF pronto, não 25 %: a cor muito escura não cabe toda e é cortada. O brilho cai para 52 a 65 % do A.",
        "No Original, a área vira um retângulo branco no meio do papel creme (com A e com B; já era assim antes). Virou pergunta.",
        "Graduale 221 em Preto e branco: com qualquer área por cima, a faixa escura da beirada esquerda sai um pouco diferente de sem área. Já era assim no código de antes; não é desta mudança.",
        "Defeito antigo da tela: ao escolher um tipo no \"Marcar como\", os botões do painel aparecem por um instante como janelinhas soltas. Acontece igual no código de antes (mesmo achado de 22/10). Para a Lista de bugs.",
        "Não testei a roda do mouse nem o Melhorar e o Mágico pro na janela (o Melhorar foi conferido nas somas).",
    ],
    "quadros": [
        {
            "id": "tc23-janela",
            "nome": "1. Os dois botões na janela do programa",
            "explicacao": [
                "O que você está olhando: o Livro de Horas 13 aberto no programa, a ferramenta Retângulo e o painel Propriedades. Cliquei em \"tinta com a cor, papel branco\" (clique do Windows).",
                "Depois: \"cor escurecida\" e um retângulo no título; \"cor como no livro\" e outro retângulo. Por fim, a página em Original e o programa fechado e aberto de novo.",
            ],
            "olhar": "Se os dois botões aparecem e se o título sai escuro na área B e claro na área A.",
            "texto": "Os dois botões aparecem logo abaixo de \"tinta com a cor, papel branco\", com \"cor como no livro\" escolhido de fábrica. A área desenhada com \"cor escurecida\" saiu B, e a seguinte, com \"cor como no livro\", saiu A, sem mudar a primeira. No \"Ver de perto\" o mesmo título mostra as duas: \"TABLE / CE QUI EST\" escuro (B) e \"TENU EN CE LIVRE\" claro (A). Escolhendo outro tipo, os botões somem. Fechando e abrindo o programa, as duas áreas voltam com o jeito delas. No código de antes, só existe o botão \"tinta com a cor\".",
            "selo": "Bom",
            "ressalva": "Os botões aparecem também no Original (pergunta 9, aberta): os prints mostram Preto e branco e Original.",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("jan_00_antes_sem_os_dois_botoes.jpg", "Antes: só o \"tinta com a cor\", sem os dois jeitos"),
                i("jan_01_marcar_como_de_fabrica.jpg", "Depois: o \"Marcar como\" antes de escolher"),
                i("jan_02_pb_dois_botoes_A_de_fabrica.jpg", "Preto e branco: os dois botões, A de fábrica"),
                i("jan_03_pb_B_escolhida.jpg", "\"cor escurecida\" escolhida"),
                i("jan_04_pb_area_B_e_area_A.jpg", "Duas áreas marcadas: a de cima B, a de baixo A"),
                i("jan_05_ver_de_perto_pb.jpg", "\"Ver de perto\" em Preto e branco: B escuro em cima, A claro embaixo"),
                i("jan_06_ver_de_perto_original.jpg", "\"Ver de perto\" em Original: as mesmas áreas"),
                i("jan_07_original_dois_botoes.jpg", "Original: os dois botões também aparecem"),
                i("jan_08_original_letra_sem_botoes.jpg", "Escolhendo \"letra e traço\", os botões somem"),
                i("jan_09_reaberto_areas_guardadas.jpg", "Programa aberto de novo: as áreas B e A voltam"),
            ],
        },
        {
            "id": "tc23-pb",
            "nome": "2. Nas páginas, em Preto e branco",
            "explicacao": [
                "O que você está olhando: cada página em quatro: o livro (Original), Preto e branco sem área, A e B. " + CAM,
                "Cada foto escreve por onde a página passou.",
            ],
            "olhar": "Se a B fica mais escura e legível e se fora da área está igual.",
            "texto": "A traz a cor do livro, clara; B a mesma cor mais escura: vermelho-escuro, azul-marinho, marrom-escuro. Fora da área, A e B são iguais ponto por ponto, nas cinco páginas. Na Horas 11, os cantos da moldura e o dourado das letras que caem na área também escurecem na B.",
            "selo": "Bom, com ressalva",
            "ressalva": "A B escurece também o dourado e a moldura dentro da área (Horas 11).",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("horas_p013-pb-ampliado.jpg", "Horas 13: o título ampliado"),
                i("horas_p013-pb-pagina.jpg", "Horas 13: a página"),
                i("escola_p007-pb-ampliado.jpg", "Escola 7: o título ampliado"),
                i("escola_p007-pb-pagina.jpg", "Escola 7: a página"),
                i("opusmajus_p003-pb-ampliado.jpg", "Opus Majus 3: a parte de baixo ampliada"),
                i("opusmajus_p003-pb-pagina.jpg", "Opus Majus 3: a página"),
                i("horas_p011-pb-ampliado.jpg", "Horas 11: o título ampliado (moldura nos cantos)"),
                i("horas_p011-pb-pagina.jpg", "Horas 11: a página"),
                i("graduale_p221-pb-ampliado.jpg", "Graduale 221: as rubricas ampliadas"),
                i("graduale_p221-pb-pagina.jpg", "Graduale 221: a página"),
            ],
        },
        {
            "id": "tc23-original",
            "nome": "3. Nas páginas, em Original",
            "explicacao": ["O que você está olhando: as mesmas páginas em Original: sem área, A e B. " + CAM],
            "olhar": "Se a B escurece a tinta como no Preto e branco, e o retângulo branco que a área faz no papel creme.",
            "texto": "Dentro da área, A e B saem iguais ao Preto e branco (a área manda por cima do filtro). Fora da área, nada muda. O papel da área fica branco e aparece como um retângulo no papel creme, com A e com B; já era assim antes.",
            "selo": "Bom, com ressalva",
            "ressalva": "O retângulo branco no Original: é a pergunta nova (tc23-1).",
            "decisao_do_samuel": DECISAO,
            "bate_com_a_decisao": "sim",
            "imgs": [
                i("horas_p013-original-ampliado.jpg", "Horas 13: o título ampliado"),
                i("horas_p013-original-pagina.jpg", "Horas 13: a página"),
                i("escola_p007-original-ampliado.jpg", "Escola 7: o título"),
                i("escola_p007-original-pagina.jpg", "Escola 7: a página"),
                i("opusmajus_p003-original-ampliado.jpg", "Opus Majus 3: a parte de baixo"),
                i("opusmajus_p003-original-pagina.jpg", "Opus Majus 3: a página"),
                i("horas_p011-original-ampliado.jpg", "Horas 11: o título"),
                i("horas_p011-original-pagina.jpg", "Horas 11: a página"),
                i("graduale_p221-original-ampliado.jpg", "Graduale 221: as rubricas"),
                i("graduale_p221-original-pagina.jpg", "Graduale 221: a página, com o retângulo branco"),
            ],
        },
    ],
    "pergunta": {
        "id": "tc23",
        "titulo": "A \"tinta com a cor\" em dois jeitos: o que você decide?",
        "explicacao": [
            "O que você está escolhendo: se os dois jeitos entram no programa como estão.",
            "O que mais pesa: a B escurece também o dourado e a moldura que caem dentro da área.",
        ],
        "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"],
    },
    "perguntas": [
        {
            "id": "tc23-1",
            "titulo": "No Original, o papel da área vira um retângulo branco. Fica assim?",
            "explicacao": [
                "O que é: com a página em Original (ou Melhorar), a área \"tinta com a cor, papel branco\" sai como um retângulo branco no meio do papel creme. Vale para A e para B, e já era assim antes. No Preto e branco não aparece, porque a página toda já é branca.",
                "Pergunto agora porque a pergunta 9 (os botões só no Preto e branco ou em qualquer filtro?) depende disto: no Original, o resultado é este retângulo.",
            ],
            "imgs": [
                i("graduale_p221-original-pagina.jpg", "Graduale 221 em Original: o retângulo branco com A e com B"),
                i("horas_p013-original-pagina.jpg", "Horas 13 em Original"),
                i("jan_06_ver_de_perto_original.jpg", "O mesmo na janela do programa"),
                i("graduale_p221-pb-pagina.jpg", "Para comparar: no Preto e branco não se vê retângulo"),
            ],
            "opcoes": [
                "Fica assim: o papel da área sai branco em qualquer filtro",
                "No Original (e no Melhorar), o papel da área fica como o resto da página; só a tinta muda",
                "Ainda não entendi",
            ],
        }
    ],
}

(AQUI / "conferencia.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
todas = [x["src"] for q in d["quadros"] for x in q["imgs"]] + [x["src"] for p in d["perguntas"] for x in p["imgs"]]
falta = [s for s in todas if not (AQUI / s.replace("tc23/", "")).is_file()]
print(len(todas), "imagens citadas; faltam:", falta)
