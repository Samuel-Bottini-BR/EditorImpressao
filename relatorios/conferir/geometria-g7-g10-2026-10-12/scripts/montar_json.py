"""Monta escolhas-g7-g10.json: as seis perguntas G7 a G10 no formato dos documentos
da colecao `decisoes` da pagina "Escolhas do Editor de Impressao".

Cada item da lista e um documento (o `id` e o nome do documento no banco). As
imagens ficam em img/g7g10/ (passo2_imagens.py); na pagina, publicar com o mesmo
caminho. A gerente e quem publica: este script so grava o arquivo.

Regras do texto (pedido da gerente, 12/10): a explicacao comeca com "O que voce
esta escolhendo:", no maximo 3 paragrafos curtos depois, sem jargao; cada opcao
com imagem (primeiro o pedaco que muda, ampliado; depois a pagina inteira),
"Bom: ... Ruim: ...", a sugestao marcada, e sempre "Ainda nao entendi".

Uso: python montar_json.py   (confere tambem se todas as imagens citadas existem)
"""
from __future__ import annotations

import json

import comum

IMG = "img/g7g10/"
NAO_ENTENDI = {"id": "nao-entendi", "nome": "Ainda não entendi",
               "texto": "Diga no comentário o que ficou confuso, e eu explico de outro jeito.", "imgs": []}


def i(nome: str, legenda: str) -> dict:
    return {"src": IMG + nome + ".jpg", "legenda": legenda}


def ex(nome: str, legenda: str) -> dict:
    return {"src": IMG + nome + ".jpg", "legenda": legenda, "largo": True}


def numeros() -> dict:
    """Numeros medidos pelo passo 2, usados nos textos."""
    arquivo = comum.DADOS / "ajustar-horas.json"
    d = json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else {}
    maior = round((d.get("fator_so_da_pequena", 1) / d.get("fator_do_livro", 1) - 1) * 100) if d else 0
    return {"maior": maior}


def perguntas() -> list[dict]:
    n = numeros()
    return [
        # ------------------------------------------------------------------ G7 (item 2.13)
        {
            "id": "g7-borda-ate-onde", "ordem": 121, "status": "aberta", "quando": "12/10",
            "parte": "Borda preta do scanner",
            "pergunta": "Página com borda preta: até onde vai o corte que o programa sugere?",
            "explicacao": (
                "O que você está escolhendo: onde para o corte que o programa sugere quando a folha vem com o fundo "
                "preto do scanner aparecendo.\n\n"
                "Você já decidiu que o programa sugere esse corte e o Kaique aceita, muda ou manda para todas as "
                "páginas. Falta dizer até onde a sugestão vai. As imagens são das duas páginas em que você perguntou, "
                "hoje, se o certo não seria cortar as bordas pretas.\n\n"
                "Hoje o corte do programa deixa o preto dentro da página. A busca de página do ScanTailor, sozinha, "
                "também quase não corta aqui: ela só tira faixa preta que vai reta de ponta a ponta, e esta folha é "
                "torta. Num livro com preto em volta toda ela funciona (último exemplo)."),
            "exemplos": [
                ex("g7-hoje-siebmacher7", "Como sai hoje, primeira página. Em laranja, o corte do programa: o preto da direita e de baixo fica dentro."),
                ex("g7-hoje-siebmacher9", "Como sai hoje, segunda página. O mesmo defeito."),
                ex("g7-scantailor-siebmacher7", "A busca de página do ScanTailor (código original), sozinha: em azul, o que ela achou. O preto da direita continua dentro."),
                ex("g7-scantailor-cantos-siebmacher7", "A mesma busca com a opção \"ajustar os cantos\" do ScanTailor: fica pior, porque corta o enfeite de cima da moldura."),
                ex("g7-as-duas-na-outra-pagina", "As duas opções abaixo, na segunda página. Nesta, \"até a moldura\" parou um pouco abaixo da moldura, nos pontinhos de sujeira do papel."),
                ex("g7-scantailor-borda-larga", "A busca de página do ScanTailor num livro com preto em volta toda: aqui ela acha a página."),
            ],
            "opcoes": [
                {"id": "so-o-preto", "nome": "Tira só o preto",
                 "texto": "O corte para onde o preto acaba, no meio de cada lado. Bom: não tira nada que é do livro, nem o "
                          "papel vazio em volta. Ruim: continuam a beirada das outras folhas, a sombra da lombada e uma ponta "
                          "de preto no canto, porque a folha não é reta.",
                 "imgs": [i("g7-a-so-o-preto-canto", "O canto de baixo, ampliado: o que sai está escurecido. A beirada das outras folhas e a ponta preta do canto ficam. Simulação com uma conta simples minha."),
                          i("g7-a-so-o-preto-inteira", "A página inteira: antes, o corte e depois.")]},
                {"id": "ate-a-moldura", "nome": "Vai até a moldura (o que está impresso)",
                 "texto": "Bom: somem o preto, a beirada das outras folhas e a lombada; as margens novas, iguais em todas as "
                          "páginas, vêm depois. Ruim: o papel vazio em volta some junto e, se o programa errar onde o impresso "
                          "acaba, o Kaique tem de puxar o corte. Sugestão: esta. É o que você descreveu em 05/10 para esta "
                          "página: respeitar a moldura e tirar a lombada.",
                 "imgs": [i("g7-b-ate-a-moldura-canto", "O canto de baixo, ampliado: sai tudo o que está fora da moldura. É a busca de conteúdo do ScanTailor, de verdade."),
                          i("g7-b-ate-a-moldura-inteira", "A página inteira: antes, o corte e depois. As margens brancas entram depois.")]},
                NAO_ENTENDI,
            ],
        },
        # ------------------------------------------------------------------ G8 (item 2.5)
        {
            "id": "g8-moldura-tinta-fora", "ordem": 122, "status": "aberta", "quando": "12/10",
            "parte": "Corte que segue a moldura",
            "pergunta": "Quando o corte que segue a moldura deixa de fora algo impresso, o que o programa faz?",
            "explicacao": (
                "O que você está escolhendo: o que o programa faz quando o corte \"seguir a moldura / o papel\" (que você "
                "pediu como opção, desligada) deixa de fora um pedaço do que está impresso.\n\n"
                "Esse corte é o do ScanTailor. Em muitas páginas ele acerta e abraça a moldura (primeiro exemplo). Mas ele "
                "erra de dois jeitos. Trata barra comprida e reta como sombra de scanner: nesta página do Livro de Horas, "
                "a barra dourada da esquerda ficou de fora. E não pega o número da página quando ele está sozinho, longe "
                "do texto (segundo exemplo).\n\n"
                "Você já pediu que o programa avise onde o corte pode ter ficado ruim. A pergunta é o que ele faz junto "
                "com o aviso."),
            "exemplos": [
                ex("g8-exemplo-acerta", "Outra página do mesmo livro, em que o corte do ScanTailor (azul) acerta. À direita, o corte comum do programa (laranja) na mesma página: sobra muito mais papel."),
                ex("g8-exemplo-numero-da-pagina", "Página que termina no meio, de outro livro. O corte do ScanTailor deixa de fora o número da página, que está sozinho no pé. Alargado (simulação minha), o número entra."),
            ],
            "opcoes": [
                {"id": "avisa", "nome": "Só avisa",
                 "texto": "O corte fica como o ScanTailor achou, e a página vai para a lista de conferir. Bom: o Kaique vê "
                          "exatamente o que o ScanTailor fez. Ruim: se ele não olhar, a página sai sem a barra da moldura ou "
                          "sem o número.",
                 "imgs": [i("g8-a-avisa-canto", "O canto de cima da moldura, ampliado: a barra dourada da esquerda fica de fora (escurecida). Resultado de verdade do ScanTailor."),
                          i("g8-a-avisa-inteira", "A página inteira: antes, o corte e depois.")]},
                {"id": "alarga", "nome": "Alarga sozinho e avisa",
                 "texto": "O programa abre o corte até caber inteiro o que ficou cortado ou sozinho do lado de fora. Bom: "
                          "moldura e número de página não se perdem, mesmo que o Kaique não olhe. Ruim: é uma conta nossa por "
                          "cima do ScanTailor, e às vezes vai trazer uma sujeira junto. Sugestão: esta. Perder a moldura ou "
                          "o número da página é pior do que sobrar um pouco de papel.",
                 "imgs": [i("g8-b-alarga-canto", "O mesmo canto: a moldura fica inteira dentro do corte. Simulação com uma conta simples minha."),
                          i("g8-b-alarga-inteira", "A página inteira: antes, o corte e depois.")]},
                {"id": "volta", "nome": "Nessa página, volta para o corte comum e avisa",
                 "texto": "Bom: usa o corte que já está aprovado, que não perde a moldura nem o número. Ruim: nesta página o "
                          "corte comum deixa quase a folha inteira, e a moldura fica longe da beirada.",
                 "imgs": [i("g8-c-volta-canto", "O mesmo canto com o corte comum do programa (de verdade): quase nada sai."),
                          i("g8-c-volta-inteira", "A página inteira: antes, o corte e depois.")]},
                NAO_ENTENDI,
            ],
        },
        {
            "id": "g8-guias", "ordem": 123, "status": "aberta", "quando": "12/10",
            "parte": "Linhas de apoio",
            "pergunta": "Linhas de apoio para alinhar as páginas: quais o programa deve ter?",
            "explicacao": (
                "O que você está escolhendo: que linhas de apoio aparecem quando o Kaique arruma o lugar do conteúdo na "
                "folha.\n\n"
                "Hoje o programa tem linhas automáticas: quando o Kaique arrasta o conteúdo, ele gruda no meio e nas "
                "beiradas da folha. O ScanTailor tem outro tipo: a pessoa põe uma linha onde quiser (por exemplo, onde o "
                "texto começa), a linha aparece em todas as páginas, e o conteúdo de cada página encosta nela.\n\n"
                "As imagens são desenhos por cima de páginas de verdade, para mostrar a ideia. Não são a tela do programa."),
            "exemplos": [],
            "opcoes": [
                {"id": "do-kaique", "nome": "Só linhas que o Kaique põe, valendo no livro todo (como no ScanTailor)",
                 "texto": "Bom: todas as páginas ficam alinhadas pelo mesmo lugar, mesmo quando o tamanho do texto muda. "
                          "Ruim: é mais uma coisa para o Kaique aprender, e as linhas automáticas de hoje deixam de existir.",
                 "imgs": [i("g8-guias-a-canto", "O canto de cima, ampliado: o conteúdo encostado nas duas linhas azuis. Desenho."),
                          i("g8-guias-a-paginas", "Duas páginas do livro com as mesmas linhas. Desenho.")]},
                {"id": "automaticas", "nome": "Só as automáticas de hoje",
                 "texto": "Bom: nada novo para aprender. Ruim: só alinha pelo meio e pelas beiradas da folha.",
                 "imgs": [i("g8-guias-b-meio", "O meio da folha, ampliado: as linhas do meio. Desenho."),
                          i("g8-guias-b-pagina", "A página inteira com as linhas automáticas. Desenho.")]},
                {"id": "as-duas", "nome": "As duas",
                 "texto": "As automáticas continuam, e as linhas do Kaique entram como opção. Bom: ele usa a que servir em "
                          "cada livro. Ruim: dá mais trabalho para fazer. Sugestão: esta. Você pediu que o programa dê "
                          "opções, e uma não atrapalha a outra.",
                 "imgs": [i("g8-guias-a-paginas", "As linhas do Kaique, valendo no livro todo. Desenho."),
                          i("g8-guias-b-pagina", "As linhas automáticas de hoje. Desenho.")]},
                NAO_ENTENDI,
            ],
        },
        # ------------------------------------------------------------------ G9 (item 2.4)
        {
            "id": "g9-pagina-muito-maior", "ordem": 124, "status": "aberta", "quando": "12/10",
            "parte": "Margens iguais",
            "pergunta": "Uma folha muito maior que as outras (tabela dobrável): ela entra na conta do tamanho?",
            "explicacao": (
                "O que você está escolhendo: se uma folha muito maior que as outras muda o tamanho de todas as páginas do "
                "livro.\n\n"
                "Você decidiu que todas as páginas saem do tamanho da maior. Neste livro há uma tabela dobrável, deitada, "
                "bem mais larga que as páginas comuns. Se ela entrar na conta, todas as páginas ficam com a largura dela "
                "e o texto fica no meio de uma folha larga demais.\n\n"
                "No ScanTailor ela entra na conta, e é a pessoa que tira, página por página."),
            "exemplos": [
                ex("g9-maior-as-duas-paginas", "Uma página comum do livro e a tabela dobrável, como vieram do scanner."),
            ],
            "opcoes": [
                {"id": "fica-de-fora", "nome": "O programa deixa essa folha de fora sozinho, e avisa",
                 "texto": "A folha muito diferente sai no tamanho dela, e as outras ficam iguais entre si. Bom: uma folha "
                          "dobrável não estraga o livro inteiro. Ruim: o programa pode separar uma folha que você queria "
                          "igual às outras; o aviso mostra qual foi, e dá para pôr de volta. Sugestão: esta. É o que quase "
                          "sempre se quer, e o aviso deixa desfazer.",
                 "imgs": [i("g9-maior-a-fica-de-fora-pagina-comum", "Uma página comum: fica do tamanho das outras páginas comuns. Simulação com as contas do ScanTailor."),
                          i("g9-maior-a-fica-de-fora-o-livro", "Duas páginas comuns e a tabela dobrável, na mesma escala.")]},
                {"id": "entra", "nome": "Ela entra na conta, até o Kaique tirar",
                 "texto": "É como no ScanTailor. Bom: o programa não decide nada sozinho. Ruim: se o Kaique não notar, o "
                          "livro inteiro sai em folha larga, com o texto perdido no meio.",
                 "imgs": [i("g9-maior-b-entra-na-conta-pagina-comum", "Uma página comum: fica com a largura da tabela dobrável. Simulação com as contas do ScanTailor."),
                          i("g9-maior-b-entra-na-conta-o-livro", "Duas páginas comuns e a tabela dobrável, na mesma escala.")]},
                NAO_ENTENDI,
            ],
        },
        # ----------------------------------------------------------------- G10 (item 2.6)
        {
            "id": "g10-papel-ou-pagina", "ordem": 125, "status": "aberta", "quando": "12/10",
            "parte": "Tamanho final",
            "pergunta": "Quando o Kaique escolhe \"A4\", isso é o papel da impressora ou a página do livro?",
            "explicacao": (
                "O que você está escolhendo: o que o programa entende quando o Kaique escolhe um tamanho de papel, como "
                "A4.\n\n"
                "Quando o programa monta os cadernos, cada lado da folha leva duas páginas do livro, uma ao lado da "
                "outra. Então o papel que entra na impressora tem o dobro da largura de uma página.\n\n"
                "Hoje o tamanho escolhido vale para a página. Se o Kaique escolher A4, a folha do caderno fica do tamanho "
                "de duas A4, e numa impressora A4 tudo sai reduzido, inclusive as margens que ele mediu. É palpite meu "
                "que ele imprime em papel A4 dobrado ao meio; se não for assim, diga no comentário."),
            "exemplos": [],
            "opcoes": [
                {"id": "papel", "nome": "É o papel da impressora",
                 "texto": "O Kaique diz o papel que usa, e cada página do livro fica com metade dele. Bom: o que ele mede na "
                          "tela é o que sai no papel, sem redução escondida. Ruim: em livro que não vai virar caderno ele "
                          "precisa avisar, para a página ocupar o papel inteiro. Sugestão: esta. A margem da costura só fica "
                          "certa se o programa souber o tamanho de verdade do papel.",
                 "imgs": [i("g10-papel-a-pagina", "Uma página do livro, no tamanho de verdade. Desenho em escala."),
                          i("g10-papel-a-folha", "A folha A4 impressa, com duas páginas. Desenho em escala.")]},
                {"id": "pagina", "nome": "É a página do livro (como hoje)",
                 "texto": "Cada página fica do tamanho escolhido, e a folha do caderno fica com o dobro. Bom: é simples e é "
                          "como já funciona. Ruim: num caderno em papel A4 a impressora reduz tudo para 71%, e uma margem de "
                          "10 mm vira 7 mm.",
                 "imgs": [i("g10-papel-b-pagina", "A mesma página depois que a impressora reduz para caber: letra e margens menores. Desenho em escala."),
                          i("g10-papel-b-folha", "A folha do caderno com duas páginas A4, e o tamanho do papel A4 em tracejado rosa. Desenho em escala.")]},
                NAO_ENTENDI,
            ],
        },
        {
            "id": "g10-ajustar-todas", "ordem": 126, "status": "aberta", "quando": "12/10",
            "parte": "Tamanho final",
            "pergunta": "Reduzir o conteúdo para caber na folha e passar para todas as páginas: todas na mesma medida, ou cada uma até encher a folha?",
            "explicacao": (
                "O que você está escolhendo: como o programa passa para o livro todo a redução (ou o aumento) que o Kaique "
                "fez numa página.\n\n"
                "Você já decidiu que, quando o conteúdo não cabe na folha, o programa avisa, o Kaique reduz à mão e pode "
                "passar isso para todas as folhas. Falta dizer o que \"passar para todas\" quer dizer quando as páginas "
                "têm tamanhos diferentes, como estas duas do Livro de Horas: uma cheia e uma com uma tabela pequena.\n\n"
                "Neste arquivo as páginas dizem ter 36 cm de largura; para caber numa folha A4 é preciso reduzir bastante."),
            "exemplos": [
                ex("g10-ajustar-as-duas-paginas", "As duas páginas como vieram do scanner: a cheia e a pequena. No livro, a moldura da pequena é menor que a pintura da cheia."),
            ],
            "opcoes": [
                {"id": "mesma-medida", "nome": "Todas na mesma medida",
                 "texto": "A redução que faz a maior página caber vale para o livro todo. Bom: as páginas guardam entre si o "
                          "tamanho que têm no livro, e a letra não muda de uma página para outra. Ruim: a página pequena "
                          "continua pequena, com mais branco em volta. Sugestão: esta. Uma página crescer mais que as outras "
                          "parece defeito.",
                 "imgs": [i("g10-ajustar-a-mesma-medida-letra", "Um pedaço da página pequena, no tamanho em que sai no papel. Simulação."),
                          i("g10-ajustar-a-mesma-medida-folhas", "As duas folhas A4, lado a lado.")]},
                {"id": "cada-uma", "nome": "Cada página até encher a folha",
                 "texto": "Bom: nenhuma página fica com muito branco em volta. Ruim: a página pequena cresce mais que as "
                          f"outras (aqui, tudo nela sai uns {n['maior']}% maior do que na outra opção).",
                 "imgs": [i("g10-ajustar-b-cada-uma-letra", "O mesmo pedaço da página pequena: tudo sai maior. Simulação."),
                          i("g10-ajustar-b-cada-uma-folhas", "As duas folhas A4, lado a lado.")]},
                NAO_ENTENDI,
            ],
        },
    ]


def main() -> None:
    lista = perguntas()
    faltando, usadas = [], set()
    for p in lista:
        for im in p["exemplos"] + [x for o in p["opcoes"] for x in o["imgs"]]:
            usadas.add(im["src"])
            if not (comum.PASTA / im["src"]).exists():
                faltando.append(im["src"])
    sobrando = sorted(f"{IMG}{a.name}" for a in comum.IMG.glob("*.jpg") if f"{IMG}{a.name}" not in usadas)
    destino = comum.PASTA / "escolhas-g7-g10.json"
    destino.write_text(json.dumps({
        "sobre": "Seis perguntas dos itens 2.13, 2.5, 2.4 e 2.6 (G7 a G10), preparadas pelo pesquisador em 12/10/2026 "
                 "para a página 'Escolhas do Editor de Impressão'. Cada item de 'decisoes' é um documento da coleção "
                 "'decisoes' (o 'id' é o nome do documento). Imagens em img/g7g10/. Ainda NÃO publicadas.",
        "decisoes": lista}, indent=1, ensure_ascii=False), encoding="utf-8")
    print("gravou", destino.name, len(lista), "perguntas,", len(usadas), "imagens citadas")
    print("imagens faltando:", sorted(set(faltando)) or "nenhuma")
    print("imagens na pasta que nenhuma pergunta usa:", sobrando or "nenhuma")


if __name__ == "__main__":
    main()
