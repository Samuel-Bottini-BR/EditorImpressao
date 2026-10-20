"""20/10/2026: monta a conferencia do Samuel para a ABA 4 da pagina de conferencia ("Para revisar").

Entrada: o conferencia.json da segunda conferencia (18 quadros pr-* e as tres perguntas) e o que o
verificador conferiu em 20/10 (as imagens contra as decisoes das rodadas 4 e 5, as quatro paginas
reabertas na janela). Saida: conferencia-aba4.json (para a gerente montar a aba; nao publica nada)
e conferencia-aba4.md/.html/.pdf (o mesmo, para ler).

Formato de cada quadro: o mesmo das abas 2 e 3 (id, nome, olhar, texto, ressalva, tipo, selo, imgs),
mais: explicacao (ate 3 paragrafos, o primeiro comeca por "O que voce esta escolhendo:"), opcoes
(sempre com "Ainda nao entendi"), decisao_do_samuel (literal, de onde veio), bate_com_a_decisao,
e em cada imagem a "situacao" (vale / tela antiga / desatualizada)."""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
RAIZ = BASE.parents[2]
sys.path.insert(0, str(RAIZ))

ANTIGA = "tela antiga: refazer depois de juntar o fase-1 no ramo"
DESATUALIZADA = "desatualizada: mostra o que o programa já não faz; trocar antes de publicar"
VALE = "vale"
OPCOES_QUADRO = ["Está bom", "Melhorar", "Está pior", "Ainda não entendi"]


def im(src, legenda, situacao=VALE):
    if not (BASE / src).exists():
        raise FileNotFoundError(src)
    return {"src": src, "legenda": legenda, "situacao": situacao}


R3 = json.loads((BASE / "trabalho" / "r3-quatro-paginas.json").read_text(encoding="utf-8")) \
    if (BASE / "trabalho" / "r3-quatro-paginas.json").exists() else {}

QUADROS = [
    {
        "id": "pr-letra-t", "nome": "Antiphonal 46: a letra grande que some",
        "explicacao": [
            "O que você está escolhendo: se o aviso da letra grande que some ficou como você pediu na rodada 5.",
            "Caso real: no Antiphonal 46 o Preto e branco apaga a letra T vermelha. O programa avisa, desenha um quadrado laranja em volta do T e mostra o botão \"Trazer de volta nesta página\". Um clique e a página guarda tudo de novo; o Ctrl+Z desfaz.",
            "O que ficou diferente do que você pediu: você escreveu \"onde sumiu, tem que aparecer selecionado automaticamente, como na opção 3\". O quadrado laranja mostra o lugar, mas é só um desenho por cima, como um post-it: não é uma marcação da aba Marcar que dá para aumentar ou diminuir, e o botão traz de volta a página inteira, não só o T.",
        ],
        "olhar": "O quadrado laranja em volta do T, nos dois cartões, e o botão \"Trazer de volta nesta página\".",
        "texto": "O aviso aparece sozinho uns 8 segundos depois de chegar na página. O botão troca só essa página para \"Guardar tudo\", o aviso some e a página sai da lista. O Ctrl+Z desfaz.",
        "ressalva": "A marca laranja não entra na marcação (está escrito no código: \"são só um desenho\"). Em 1280 x 657 os cartões são pequenos e a marca quase não se vê. No cartão a letra T continua lá: é o defeito do quadro seguinte.",
        "tipo": "misto", "selo": "funciona; a marca é só desenho",
        "decisao_do_samuel": "rv5-erro-1-desenho (09/10): \"Botão 'Trazer de volta nesta página'\" + \"eu acho que pode ser a opção 1, mas onde sumiu, tem que aparecer selecionado automaticamente, como na opção 3\" (a opção 3 era o retângulo 'letra e traço' da aba Marcar).",
        "bate_com_a_decisao": "em parte: o botão sim; o lugar aparece marcado, mas não como uma seleção que se ajusta",
        "imgs": [
            im("img/a4-letra-t.jpg", "Ampliado: o T no Original (vermelho) e no Preto e branco, com o quadrado laranja", ANTIGA),
            im("img/letra-t-1-aviso-recorte.jpg", "Os cartões, o aviso e os dois botões", ANTIGA),
            im("img/letra-t-3-trazer-de-volta-recorte.jpg", "Depois de \"Trazer de volta nesta página\": \"Guardar tudo\" ligado, aviso e marca sumiram", ANTIGA),
        ],
    },
    {
        "id": "pr-tela-engana", "nome": "Antiphonal 46: a tela mostra a letra T, o PDF sai sem ela",
        "explicacao": [
            "O que você está escolhendo: se este defeito é grave. A escolha do conserto está na pergunta \"A tela igual ao PDF\", no fim da aba.",
            "Caso real: na tela, a página 46 aparece com a letra T. No PDF que o programa gerou, a letra sumiu. É como uma prova de gráfica que mostra uma coisa e a impressão sai outra.",
            "O aviso \"Desenho apagado\" diz a verdade; a imagem da tela é que engana, porque é desenhada pequena para ser rápida.",
        ],
        "olhar": "A letra T grande à esquerda: na tela ela aparece; na página do PDF, não.",
        "texto": "Processei o livro na janela: no PDF a letra T sumiu mesmo. O \"Ver de perto\" continua mostrando a letra T.",
        "ressalva": "Não foi mexido de propósito: depende da sua resposta à pergunta \"A tela igual ao PDF\".",
        "tipo": "pior", "selo": "defeito grave, já existia",
        "decisao_do_samuel": "Sem decisão ainda (pergunta nova desta aba).",
        "bate_com_a_decisao": "não se aplica",
        "imgs": [
            im("img/tela-engana-1-comparacao.jpg", "Ampliado: o mesmo pedaço da página 46, na tela (com o T) e no PDF (sem o T)"),
            im("img/tela-engana-3-pagina-do-pdf.jpg", "A página inteira tirada do PDF: no lugar do T sobrou um tracinho"),
        ],
    },
    {
        "id": "pr-so-o-texto", "nome": "Graduale 222: \"Guardar só o texto\" apaga a música",
        "explicacao": [
            "O que você está escolhendo: se o aviso do \"Guardar só o texto\" ficou como você pediu na rodada 5.",
            "Caso real: no Graduale 222, quem escolhe \"Guardar só o texto\" perde as pautas. O programa avisa, marca de laranja e mostra \"Trazer de volta nesta página\": um clique e só essa página volta a guardar a música.",
            "O que ficou diferente: você pediu \"aparece marcado como apareceu na segunda opção\", que era um retângulo em volta de uma pauta. Aqui o laranja é um contorno em volta da página inteira, porque o botão traz de volta a página toda.",
        ],
        "olhar": "O cartão do Preto e branco sem as pautas, o contorno laranja e o botão \"Trazer de volta nesta página\".",
        "texto": "No jeito de fábrica (\"Guardar a tinta forte\") a página 222 não tem aviso. Trocando para \"Guardar só o texto\", o aviso aparece; o botão devolve só essa página para \"Guardar a tinta forte\". As outras páginas não mudam.",
        "ressalva": "Conferido num pedaço de 7 páginas do Graduale (219 a 225); na janela a página se chama 4.",
        "tipo": "misto", "selo": "funciona; a marca é a página toda",
        "decisao_do_samuel": "rv5-erro-6-so-texto (09/10): \"Botão 'Trazer de volta nesta página'\" + \"opção 1, mas aparece marcado como apareceu na segunda opção.\" (a segunda opção mostrava um retângulo em volta de uma pauta).",
        "bate_com_a_decisao": "em parte: o botão sim; a marca é a página inteira, não as pautas",
        "imgs": [
            im("img/a4-so-o-texto.jpg", "Ampliado: Original e Preto e branco sem a música, o contorno laranja, o aviso e os botões", ANTIGA),
            im("img/so-o-texto-3-trazer-de-volta-recorte.jpg", "Depois do botão: a música voltou e o aviso sumiu", ANTIGA),
        ],
    },
    {
        "id": "pr-sem-conteudo", "nome": "Egenloff 12 e Rariora 8: página sem conteúdo",
        "explicacao": [
            "O que você está escolhendo: se o aviso da página sem conteúdo ficou como você pediu (os dois botões, \"Deixar em branco\" e \"Tirar do livro\").",
            "Caso real: o verso do Egenloff 12 só tem a mancha da página de trás. \"Deixar em branco\" põe uma folha branca no lugar (o livro fica com o mesmo número de páginas); \"Tirar do livro\" apaga a página.",
            "Há um terceiro botão, \"está bom assim\", que não estava na sua escolha: ele tira só o aviso e deixa a página como está. Foi posto porque o aviso às vezes erra (quadro da Gladstone 18).",
        ],
        "olhar": "Os três botões: \"Deixar em branco\", \"Tirar do livro\" e \"está bom assim\".",
        "texto": "Os três voltam com Ctrl+Z.",
        "ressalva": "",
        "tipo": "melhor", "selo": "funciona",
        "decisao_do_samuel": "rv5-erro-5-sem-conteudo (09/10): \"Os dois botões: 'Deixar em branco' e 'Tirar do livro'\"; rv4-pag-rariora-008: \"Vai para a lista, com botão\"; rv4-pag-egenloff-012: \"Concordo\".",
        "bate_com_a_decisao": "sim (com um botão a mais, \"está bom assim\")",
        "imgs": [
            im("img/a4-sem-conteudo.jpg", "Ampliado: Egenloff 12, o aviso e os três botões", ANTIGA),
            im("img/sem-conteudo-3-deixar-em-branco-recorte.jpg", "Depois de \"Deixar em branco\": folha branca no lugar e o botão \"voltar a página\"", ANTIGA),
            im("img/sem-conteudo-4-tirar-do-livro-recorte.jpg", "Depois de \"Tirar do livro\": a página 12 fica apagada na tira e o botão vira \"restaurar página\"", ANTIGA),
            im("img/sem-conteudo-5-rariora-recorte.jpg", "Rariora 8: o mesmo aviso, com os três botões", ANTIGA),
        ],
    },
    {
        "id": "pr-parece-em-branco", "nome": "Gladstone 18: \"Parece em branco\" numa página com título",
        "explicacao": [
            "O que você está escolhendo: se os dois avisos separados (\"Parece em branco\" e \"Página sem conteúdo\") ficaram como você pediu.",
            "Caso real, e é um erro: a Gladstone 18 tem o título \"DA ORAÇÃO\", e o programa diz que ela parece em branco, oferecendo \"Tirar do livro\". O erro já estava na Lista de bugs.",
            "O que mudou: agora o aviso tem também \"está bom assim\", que deixa a página como está.",
        ],
        "olhar": "A página tem o título \"DA ORAÇÃO\" e mesmo assim vem o aviso \"Parece em branco\".",
        "texto": "O aviso errado continua; com o terceiro botão há uma saída certa.",
        "ressalva": "O conserto do aviso em si fica para a Lista de bugs (não era deste trabalho).",
        "tipo": "misto", "selo": "erro conhecido, com saída",
        "decisao_do_samuel": "rv4-em-branco: \"Tem que ter um tipo de aviso para cada coisa, e um botão de apagar folha e outro realmente de só mudar para um folha branca.\"; rv5-em-branco (08/10): \"Fica assim\".",
        "bate_com_a_decisao": "sim (o aviso errado na Gladstone 18 é bug à parte)",
        "imgs": [
            im("img/a4-parece-em-branco.jpg", "Ampliado: o aviso \"Parece em branco\" e os três botões", ANTIGA),
            im("img/parece-em-branco-3-a-pagina.jpg", "A página: tem o título \"DA ORAÇÃO\""),
        ],
    },
    {
        "id": "pr-forca-sozinha", "nome": "Camões 27: a força do preto sozinha",
        "explicacao": [
            "O que você está escolhendo: se a força do preto sozinha ficou como você pediu (\"Força sozinha\", até o reconhecimento de tintas do item 1.4).",
            "Caso real: no Camões 27 várias linhas saíam falhadas. O programa escureceu a força só nessa página (de \"normal\" para \"bem forte\"), avisou e deixou o botão \"Desfazer\".",
            "Uma regra a mais, decidida pela gerente para não estragar página boa: a força só muda sozinha quando 4 linhas ou mais saem falhadas, e só fica se as falhas diminuírem. Nas 89 páginas do estudo ela agiu em duas (Camões 27 e 104); nas outras com texto falhado fica só o aviso, com o botão \"usar mais escuro\".",
        ],
        "olhar": "O medidor em \"bem forte\", o aviso \"escureci a força do preto só nela\" e o botão \"Desfazer\".",
        "texto": "Com a força já em 85, o botão \"usar mais escuro\" não aparece. Há uma caixinha na tela \"O que fazer\" para desligar a força sozinha no livro.",
        "ressalva": "A caixinha só aparece rolando a lista de opções. Com a força em 85, a frase do aviso \"Texto falhado\" ainda diz \"tente a força do preto mais escura\" (Lista de bugs).",
        "tipo": "melhor", "selo": "funciona",
        "decisao_do_samuel": "rv4-erro-4-texto-falhado: \"Força sozinha\" + \"mas temos que melhorar o reconhecimento de tintas, para não sair falhado assim, não precisar usar sempre o reforço.\"; rv5-erro-4-tintas (09/10): \"Fica no plano; até lá, a força sozinha\".",
        "bate_com_a_decisao": "sim, com o limite de 4 linhas (decisão técnica da gerente, a confirmar com você)",
        "imgs": [
            im("img/a4-forca-sozinha.jpg", "Ampliado: o aviso, o medidor em \"bem forte\" e os botões \"Desfazer\" e \"está bom assim\"", ANTIGA),
            im("img/forca-3-desfazer-recorte.jpg", "Depois do \"Desfazer\": força normal e o aviso \"Texto falhado\" com \"usar mais escuro\"", ANTIGA),
            im("img/forca-7-egenloff-3-forca-85-recorte.jpg", "Egenloff 3 depois de \"usar mais escuro\": o botão sumiu, fica \"está bom assim\"", ANTIGA),
            im("img/forca-5-caixinha-recorte.jpg", "A caixinha \"Escurecer sozinho a força do preto quando o texto sair falhado\""),
        ],
    },
    {
        "id": "pr-palatino-66", "nome": "Palatino 66: a força não mexe mais; fica o aviso",
        "explicacao": [
            "O que você está escolhendo: se está bom a página de caligrafia ficar só com o aviso, sem a força mudar sozinha.",
            "Caso real: na primeira versão, o programa escurecia sozinho a força nesta página e sujava a moldura. Agora ele não mexe: mostra \"Texto falhado\" e o botão \"usar mais escuro\", e quem decide é o Kaique.",
            "A página continua indo para a lista sem precisar: é uma das cinco que decidem diferente do estudo que você aprovou.",
        ],
        "olhar": "O medidor em \"normal\" e o aviso \"Texto falhado\" com \"usar mais escuro\".",
        "texto": "Agora não estraga nada; o aviso fica.",
        "ressalva": "",
        "tipo": "melhor", "selo": "melhorou",
        "decisao_do_samuel": "rv4-erro-4-texto-falhado: \"Força sozinha\" (o limite de 4 linhas é da gerente).",
        "bate_com_a_decisao": "sim",
        "imgs": [
            im("img/a4-palatino-66.jpg", "Ampliado: o aviso \"Texto falhado\", a força em \"normal\" e os botões", ANTIGA),
            im("img/palatino-66-1-pagina-recorte.jpg", "Como saía na primeira versão, com a força escurecida sozinha (moldura suja)"),
        ],
    },
    {
        "id": "pr-antes-de-processar", "nome": "A janela \"Antes de processar\"",
        "explicacao": [
            "O que você está escolhendo: se a janela que aparece ao processar com avisos ficou como você pediu (\"Lista as páginas e os motivos\").",
            "Caso real: no Camões, ao clicar em \"Confirmar e processar\", a janela lista \"Página N - motivo\" e \"Folha N - motivo\", com \"ver\" (vai para a página e não processa) e \"continuar assim mesmo\" (segue até \"Ficou pronto!\").",
            "A frase de cima diz quantas páginas e quantos avisos: \"75 páginas (104 avisos na lista)\". Os números de três telas não batem: é a pergunta \"As contagens\", no fim da aba.",
        ],
        "olhar": "As linhas \"Página N - motivo\" e os botões \"ver\" e \"continuar assim mesmo\".",
        "texto": "Fechar no X não processa.",
        "ressalva": "A lista junta os avisos novos com os de sempre, e mistura \"Folha N\" com \"Página N\" (no Camões: 104 linhas, 4 da regra nova). Só mostra as páginas já visitadas: é a pergunta \"Quando medir\".",
        "tipo": "misto", "selo": "funciona; contagens em pergunta",
        "decisao_do_samuel": "rv5-aviso-so-texto (08/10): \"Lista as páginas e os motivos\"; rv4-aviso-so-texto: \"quando alguém tentar imprimir sem ver os alertas o programa para e mostra os alertas e a pessoa diz se quer ver ou continuar\".",
        "bate_com_a_decisao": "sim",
        "imgs": [
            im("img/a4-antes-de-processar.jpg", "Ampliado: a frase nova e as linhas da lista (Camões)"),
            im("img/antes-5-ficou-pronto-tela.jpg", "Depois de \"continuar assim mesmo\": \"Ficou pronto!\""),
        ],
    },
    {
        "id": "pr-esta-bom", "nome": "\"Está bom\" numa página, num motivo, em todas e em tudo",
        "explicacao": [
            "O que você está escolhendo: se dar \"está bom\" nos avisos ficou como você pediu na rodada 4.",
            "Caso real (Egenloff): \"está bom assim\" tira um aviso de uma página; \"está bom: todas\" tira um motivo do livro inteiro; \"está bom em tudo\" limpa a lista; na lista grande dá para marcar várias linhas e dar \"está bom nas marcadas\". O Ctrl+Z desfaz cada um.",
            "Quando o problema é resolvido (por exemplo, \"Guardar tudo\" na página da letra que sumiu), o aviso some sozinho.",
        ],
        "olhar": "O número do painel \"Para revisar\" descendo em cada nível.",
        "texto": "Um motivo de uma página: de 31 para 30 avisos. Um motivo em todas: de 31 para 6. Em tudo: \"tudo certo\". Na lista grande, duas linhas marcadas: de 31 para 29.",
        "ressalva": "Os botões \"ver a lista…\" e \"está bom em tudo\" ficam no fim do painel e só aparecem rolando a coluna da direita.",
        "tipo": "melhor", "selo": "funciona; FOTOS A TROCAR",
        "decisao_do_samuel": "rv4-aviso-so-texto: \"Eu tenho que conseguir fazer isso com uma pagina individual, com um motivo individual de uma pagina e com todas as paginas ou com todos os motivos de todas as paginas, e eu devo conseguir abrir um selecionador em aba grande [...] quando eu resolver aquele problema, o programa já vai automaticamente ver que eu resolvi?\"",
        "bate_com_a_decisao": "sim",
        "imgs": [
            im("img/esta-bom-4-seletor.jpg", "A lista grande com duas linhas marcadas", DESATUALIZADA),
            im("img/esta-bom-2-motivo-em-todas-tela.jpg", "Depois de \"está bom: todas\" no motivo do endireitar", DESATUALIZADA),
            im("img/esta-bom-3-em-tudo-tela.jpg", "Depois de \"está bom em tudo\": nenhuma página marcada na tira", DESATUALIZADA),
        ],
        "nota_para_a_gerente": "As quatro fotos deste quadro são da primeira conferência e mostram o Egenloff 3 com a força escurecida sozinha (\"bem forte\", \"Força do preto escurecida\" na lista) e, na esta-bom-1, o botão \"usar mais escuro\" com a força já em \"bem forte\". Os dois mudaram no ce2b835: o Egenloff 3 fica só com o aviso. Refazer no programa juntado.",
    },
    {
        "id": "pr-janela-diferente", "nome": "Graduale 221: as 89 páginas decidem igual na tela e na conta",
        "explicacao": [
            "O que você está escolhendo: se aceita o resultado da regra como está, um pouco abaixo do que você aprovou.",
            "Você aprovou a regra com 21 páginas indo para a lista e 78 decididas certo, das 89 do estudo. Com o preparo do livro novo (endireitar antes de cortar), dá 22 e 75: três páginas certas a menos.",
            "As cinco que decidem diferente do estudo: Antiphon 260, Cursus 3, Matemática 72, Opus Majus 20 e Palatino 66. O erro desta página, o Graduale 221 com aviso na tela e sem aviso na conta, foi consertado.",
        ],
        "olhar": "Não há mais aviso nem marca laranja nesta página.",
        "texto": "A medida usa sempre as áreas achadas na página do tamanho do PDF. Na janela e na conta direta as 89 páginas dão o mesmo resultado.",
        "ressalva": "O Opus Majus 20, reaberto em 20/10, vai para a lista e devia ir (quadro do Opus Majus 20).",
        "tipo": "melhor", "selo": "consertado; 22 e 75",
        "decisao_do_samuel": "rv4-resumo: \"Fica assim\" (a regra ajustada: 21 vão, 78 certas).",
        "bate_com_a_decisao": "em parte: 22 vão e 75 certas, contra 21 e 78 aprovados",
        "imgs": [
            im("img/a4-janela-diferente.jpg", "Ampliado: Graduale 221 na janela, sem aviso", ANTIGA),
        ],
    },
]

# os tres quadros das paginas reabertas em 20/10 (Opus, Cursus, Antiphon e Camoes) e os de maquina
QUADROS += json.loads((AQUI / "aba4_quadros_reabertos.json").read_text(encoding="utf-8"))

QUADROS += [
    {
        "id": "pr-marcar-sozinha", "nome": "Aba Marcar: as áreas se acertam sozinhas",
        "explicacao": [
            "O que você está escolhendo: se está bom as áreas da aba Marcar mudarem sozinhas alguns segundos depois de chegar numa página.",
            "Caso real: no Graduale 221 a aba Marcar mostra 9 áreas ao chegar; uns 10 segundos depois, o programa troca por 18, achadas na página do tamanho do PDF. É como um rascunho que é passado a limpo sem ninguém pedir.",
            "Uma área marcada à mão nesse intervalo continuou lá depois da troca. Nada avisa que o programa ainda está procurando.",
        ],
        "olhar": "As áreas azuis (letra) e verdes (papel) antes e depois.",
        "texto": "Só acontece uma vez por página.",
        "ressalva": "Não testei apagar ou mexer numa área do programa nesse intervalo, só marcar uma nova.",
        "tipo": "misto", "selo": "novo, para saber",
        "decisao_do_samuel": "Não foi pedido por você: veio do conserto da medida (decisão técnica da gerente).",
        "bate_com_a_decisao": "não se aplica",
        "imgs": [
            im("img/marcar-1-antes-e-depois.jpg", "Ampliado: Graduale 221 na aba Marcar, ao chegar e 10,7 segundos depois"),
            im("img/marcar-4-a-mao-recorte.jpg", "Página 5: o retângulo marcado à mão continuou depois do acerto", ANTIGA),
        ],
    },
    {
        "id": "pr-duplo-clique", "nome": "Dois cliques no cartão não tiram mais o aviso",
        "explicacao": [
            "O que você está escolhendo: se o conserto está bom.",
            "Na primeira versão, dois cliques no cartão do filtro gravavam uma ação vazia e o aviso sumia. Agora os dois cliques só abrem o \"Ver de perto\" e o aviso continua.",
        ],
        "olhar": "Depois dos dois cliques, o aviso e os botões laranja continuam na tela.",
        "texto": "Nada foi gravado no histórico.",
        "ressalva": "",
        "tipo": "melhor", "selo": "consertado",
        "decisao_do_samuel": "Conserto de um defeito achado na primeira conferência.",
        "bate_com_a_decisao": "não se aplica",
        "imgs": [
            im("img/a4-duplo-clique.jpg", "Ampliado: depois dos dois cliques, o aviso e os botões continuam", ANTIGA),
            im("img/duplo-clique-2-ver-de-perto.jpg", "O \"Ver de perto\" que os dois cliques abrem"),
        ],
    },
    {
        "id": "pr-teclado", "nome": "O teclado depois de clicar num botão do aviso",
        "explicacao": [
            "O que você está escolhendo: se o conserto do teclado está bom.",
            "Na primeira versão, depois de clicar num botão do aviso, a barra de espaço apertava o botão de novo. Agora o botão não fica com o teclado, e a barra de espaço faz \"está certo e avança\".",
            "A seta para a direita só troca de página quando o teclado não está na tira de miniaturas nem no medidor da força: esses dois usam a seta (a tira rola; o medidor muda a força do preto daquela página). Isso já era assim no programa de hoje.",
        ],
        "olhar": "Depois de \"Deixar em branco\" e da barra de espaço, o programa passou para a página 13.",
        "texto": "Com Tab, 40 vezes, o foco nunca parou num botão do aviso.",
        "ressalva": "A seta foi conferida na janela de teste, que nunca fica ativa, e pelo código (a tecla vai primeiro para quem está com o teclado). A conclusão não depende da janela estar ativa, mas não testei com o teclado de verdade.",
        "tipo": "misto", "selo": "espaço sim; seta como antes",
        "decisao_do_samuel": "Conserto de um defeito achado na primeira conferência.",
        "bate_com_a_decisao": "não se aplica",
        "imgs": [
            im("img/a4-teclado.jpg", "Ampliado: depois da barra de espaço, a página 13 escolhida na tira", ANTIGA),
        ],
    },
    {
        "id": "pr-projeto-antigo", "nome": "Projeto feito antes desta mudança",
        "explicacao": [
            "O que você está escolhendo: se está bom o que acontece com um livro começado antes desta mudança.",
            "Caso real: um projeto do programa de hoje, com o aviso antigo \"Tinta forte fora do texto\" em 8 páginas, aberto no programa novo. Abriu em 7 segundos, o aviso antigo sumiu sozinho e os avisos novos vieram ao visitar cada página. A força sozinha vem desligada nesses livros.",
        ],
        "olhar": "No programa novo, a página 3 mostra \"Texto falhado\" com a força em \"normal\".",
        "texto": "O erros.log ficou vazio.",
        "ressalva": "O projeto salvo ganhou campos novos, todos com valor padrão. Projeto de antes de 09/10 não foi conferido (só existe na sua pasta de dados).",
        "tipo": "igual", "selo": "abre igual",
        "decisao_do_samuel": "Não se aplica.",
        "bate_com_a_decisao": "não se aplica",
        "imgs": [
            im("img/a4-projeto-antigo.jpg", "Ampliado: no programa novo, \"Texto falhado\" e a força em \"normal\"", ANTIGA),
            im("img/antigo-1-no-programa-de-hoje-recorte.jpg", "O mesmo projeto no programa de hoje: o aviso antigo \"Tinta forte fora do texto\"", ANTIGA),
        ],
    },
]


def explicar_pergunta(p, explicacao, primeira=None):
    p = dict(p)
    p["explicacao"] = explicacao
    if primeira:
        p["primeira_imagem"] = primeira
    assert any(o["id"] == "nao-entendi" for o in p["opcoes"])
    return p


CONF = json.loads((BASE / "conferencia.json").read_text(encoding="utf-8"))
PERGUNTAS = [
    explicar_pergunta(CONF["pergunta_medir"], [
        "O que você está escolhendo: em que hora o programa confere as páginas que ninguém abriu.",
        "Hoje ele só confere a página que está na tela, como um revisor que só lê as páginas que você abre. As outras ele só lê na hora de gerar o PDF, quando já não dá para parar. Por isso a lista \"Antes de processar\" só traz as páginas visitadas: no Antiphonal, com 2 páginas visitadas a lista tinha 2 avisos; visitei mais 4 e ela passou a 4.",
        "Conferir custa tempo: de 4 a 15 segundos por página nos livros comuns e de 20 a 26 no Antiphon. Num livro de 300 páginas, de 13 a 15 minutos (pela conta do implementador).",
    ], im("img/medir-1-listas.jpg", "As duas listas: 2 páginas visitadas, 2 avisos; mais 4 visitadas, 4 avisos", ANTIGA)),
    explicar_pergunta(CONF["pergunta_contagens"], [
        "O que você está escolhendo: qual número cada tela mostra, para não haver três placares diferentes do mesmo jogo.",
        "No Camões (106 páginas): o painel \"Para revisar\" diz 39 (só avisos de página); a lista \"Antes de processar\" diz 75 páginas e 104 avisos (junta os de folha: qualidade baixa, tamanho diferente); a janela de salvar diz 106 (toda página em que ninguém clicou \"está certo\").",
        "Quem dá \"continuar assim mesmo\" para 75 páginas lê, na janela seguinte, que ainda há 106 sem conferir.",
    ], im("img/contagens-1-lado-a-lado.jpg", "Os três números no Camões: 39, 75 (104 avisos) e 106", ANTIGA)),
    explicar_pergunta(CONF["pergunta_tela_igual_ao_pdf"], [
        "O que você está escolhendo: se a página que aparece na tela, no \"Só as letras\", passa a ser a mesma que vai para o PDF, como uma prova de gráfica fiel.",
        "Hoje a tela usa uma imagem menor, para ser rápida. No Antiphonal 46 essa imagem mostra a letra T grande; no PDF a letra some. O aviso está certo, mas quem olha a tela vê a letra no lugar.",
        "O programa já desenha por trás a página do tamanho do PDF, para medir os avisos. Ela chega de 4 a 15 segundos depois de abrir a página (20 a 26 em folha grande). Dá para mostrá-la na tela quase sem custo.",
    ], im("img/tela-engana-1-comparacao.jpg", "A mesma página 46: a tela (com a letra T) e o PDF que saiu (sem ela)")),
]

ANTES_DE_PUBLICAR = [
    "NÃO publicar esta aba como está. Todas as fotos da janela são da tela de antes do layout que o Samuel aprovou e que está no fase-1 desde 14/10 (sem abas, painel \"Para revisar\" na coluna da direita com \"Por página | Por motivo\", \"daqui em diante\" no lugar de \"só nas próximas\"). É o mesmo erro de 09 e 12/10.",
    "O ramo fase2-para-revisar (ce2b835) não se junta ao fase-1 (b8e9af7) sem conflito: `git merge-tree` dá conflito em ui/tela_conferir.py e ui/widgets/paineis.py, exatamente onde ficam os avisos e o painel. Quem resolve é o implementador (o verificador não mexe em ui/).",
    "Depois da junção: os textos novos dos avisos ainda dizem \"aba Marcar\" e \"aba Bordas\" (core/analise.py do ramo); o layout já trocou \"aba Endireitar\" por \"ferramenta Endireitar\" e \"programa\" por \"Editor\". Acertar as palavras novas antes das fotos.",
    "Depois da junção, o verificador refaz na janela as fotos marcadas \"tela antiga\" e troca as \"desatualizadas\" (quadro pr-esta-bom), com os mesmos recortes (scripts/a4_recortes.py), e confere de novo as 89 páginas (a junção mexe na tela que pede a medida).",
    "O Cursus 3 e o Antiphon 260 dependem do conserto do corte com borda preta (outro ramo, decisão cg6 ainda aberta): se ele entrar antes, as fotos desses dois quadros mudam.",
    "Podem ir já, se a gerente quiser separar: as três perguntas (\"Quando medir\", \"As contagens\", \"A tela igual ao PDF\") falam de comportamento, não de aparência. Só a foto do painel na pergunta das contagens é da tela antiga (o painel novo pode contar diferente: conferir depois da junção).",
    "Cada quadro precisa da opção \"Ainda não entendi\" ao lado de \"Está bom / Melhorar / Está pior\" (as abas 2 e 3 só têm as três).",
]

RESUMO = {
    "titulo": "O que aconteceu e o que eu achei",
    "paragrafos": [
        "O programa passa a avisar, página por página, quando o \"Só as letras\" do Preto e branco pode ter estragado alguma coisa: uma letra grande que sumiu, texto falhado, página sem nada do livro. Cada aviso traz o botão do conserto que você escolheu: \"Trazer de volta nesta página\", \"Deixar em branco\", \"Tirar do livro\", \"Desfazer\".",
        "Quando 4 linhas ou mais saem falhadas, o programa escurece sozinho a força do preto só naquela página e avisa. Ao processar com avisos sem olhar, aparece a lista \"Página N - motivo\", com \"ver\" e \"continuar assim mesmo\". O Kaique dá \"está bom\" numa página, num motivo, em todas ou em tudo, e o Ctrl+Z desfaz.",
        "Ficaram três perguntas para você, no fim da aba: quando medir as páginas não visitadas, as três contagens que não batem e se a tela deve mostrar o mesmo que o PDF.",
    ],
    "veredito": ("PRONTO PARA CONFERIR no que faz: os seis pedaços e os consertos funcionam na janela de verdade. "
                 "Duas escolhas suas ficaram em parte (a marca laranja é só desenho; no \"Guardar só o texto\" ela contorna a página toda) "
                 "e a regra dá 22 vão e 75 certas, contra 21 e 78 aprovados."),
    "velocidade": "O Mágico pro saiu 1,1% mais lento (0,06 s por página); você mandou deixar para a Fase 5, de desempenho (19/10).",
}

SAIDA = {
    "aba": 4, "id_da_decisao": "pr", "titulo_da_aba": "4. Para revisar: os avisos com botão",
    "ramo": "fase2-para-revisar", "commit": "ce2b835", "montado_em": "20/10/2026",
    "pode_publicar": False, "antes_de_publicar": ANTES_DE_PUBLICAR,
    "resumo": RESUMO,
    "quadros": QUADROS, "opcoes_de_cada_quadro": OPCOES_QUADRO,
    "perguntas": PERGUNTAS,
    "pergunta": {"id": "pr", "titulo": "\"Para revisar\": o que você decide?",
                 "opcoes": ["Aprovado", "Melhorar", "Ainda não entendi"]},
}

for q in QUADROS:
    assert q["explicacao"][0].startswith("O que você está escolhendo:"), q["id"]
    assert len(q["explicacao"]) <= 3, q["id"]
    assert q["imgs"], q["id"]
for p in PERGUNTAS:
    assert p["explicacao"][0].startswith("O que você está escolhendo:"), p["id"]
ids = [q["id"] for q in QUADROS]
assert len(ids) == len(set(ids)) == 18, (len(ids), ids)
(BASE / "conferencia-aba4.json").write_text(json.dumps(SAIDA, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------------ o mesmo, para ler (md/html/pdf)
def md():
    m = ["# Aba 4 da página de conferência: \"Para revisar\" (preparada pelo verificador, 20/10/2026)", "",
         "Ramo `fase2-para-revisar`, `ce2b835`. Arquivo para a gerente montar a aba: `conferencia-aba4.json`. "
         "**Não marco nada como aprovado.**", "",
         "## Antes de publicar (para a gerente)", ""] + [f"- {x}" for x in ANTES_DE_PUBLICAR] + [""]
    m += ["## Resumo para o Samuel", ""] + [p + "\n" for p in RESUMO["paragrafos"]] + [f"**{RESUMO['veredito']}**", "", RESUMO["velocidade"], ""]
    m += ["## As fotos contra as decisões dele", "", "| Quadro | Decisão dele | Bate? | Fotos |", "|---|---|---|---|"]
    for q in QUADROS:
        sit = sorted({i["situacao"].split(":")[0] for i in q["imgs"]})
        m.append(f"| {q['nome']} | {q['decisao_do_samuel']} | {q['bate_com_a_decisao']} | {', '.join(sit)} |")
    m.append("")
    for n_, q in enumerate(QUADROS, 1):
        m += [f"## {n_}. {q['nome']} ({q['selo']})", ""] + [p + "\n" for p in q["explicacao"]]
        m += [f"**O que olhar:** {q['olhar']}", "", q["texto"], ""]
        if q.get("ressalva"):
            m += [f"**Ressalva:** {q['ressalva']}", ""]
        if q.get("nota_para_a_gerente"):
            m += [f"**Para a gerente:** {q['nota_para_a_gerente']}", ""]
        m += [f"Opções: {' · '.join(OPCOES_QUADRO)} · e um comentário.", ""]
        for i in q["imgs"]:
            m += [f"![{i['legenda']}]({i['src']})", "", f"*{i['legenda']}* ({i['situacao']})", ""]
    for p in PERGUNTAS:
        m += [f"## Pergunta: {p['titulo']}", ""] + [e + "\n" for e in p["explicacao"]]
        for o in p["opcoes"]:
            m.append(f"- **{o['nome']}**{' (sugestão do verificador)' if o.get('sugestao_do_verificador') else ''}. {o['texto']}")
        m += ["", p["sugestao"], ""]
        pi = p.get("primeira_imagem")
        if pi:
            m += [f"![{pi['legenda']}]({pi['src']})", "", f"*{pi['legenda']}* ({pi['situacao']})", ""]
    return "\n".join(m)


import relatorio  # noqa: E402

print(relatorio.gravar(md(), BASE / "conferencia-aba4.md"))
print("quadros:", len(QUADROS), "| perguntas:", len(PERGUNTAS),
      "| fotos:", sum(len(q["imgs"]) for q in QUADROS),
      "| tela antiga:", sum(i["situacao"] == ANTIGA for q in QUADROS for i in q["imgs"]),
      "| desatualizadas:", sum(i["situacao"] == DESATUALIZADA for q in QUADROS for i in q["imgs"]))
