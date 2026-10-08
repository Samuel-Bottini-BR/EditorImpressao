"""Monta ../rodada-4-perguntas.json (rodada 4 das decisoes do "Para revisar").

Mesmo formato da rodada 3 (colecao `decisoes` da pagina "Quando revisar uma
pagina"), com o campo novo `historico` (pedido do Samuel de 07/10: o comentario
anterior fica fixado no alto da pergunta que responde a ele): lista de
{"quem": "samuel", "em": "", "texto": <comentario literal da rodada 3>}. O "em"
fica vazio: o respostas-samuel.md da rodada 3 so tem o intervalo (15:57 a
18:41); a gerente completa pelo banco, se quiser.

Campos que a pagina nao mostra (para a analise): hoje, regra4, gabarito.
As respostas a comentarios comecam a explicacao com "RESPOSTA AO SEU COMENTARIO:".

Uso: python perguntas4.py
"""
import json
from pathlib import Path

import comum

PASTA = Path(__file__).resolve().parents[1]
REGRA = json.loads((comum.TRABALHO / "regra4.json").read_text(encoding="utf-8"))
R = "RESPOSTA AO SEU COMENTÁRIO: "
P = "Rodada 4"

# Comentarios literais da rodada 3 (relatorios/revisar-decisoes/rodada-3/respostas-samuel.md)
COMENT = {
    "aviso-so-texto": "entendi, mas quando a pessoa querer mesmo apagar as coisas, ela pode ter um jeito de simplismente apagar todos os avisos.",
    "conserto-desenho": "Quero mais opções de como vai ser concertado esses erros, na verdade, temos que pensar em cada hipotese que pode acontecer dentro do arquivo que o programa vá pedir para fazer revisão, como resolver da forma mais rapida possivel, e qual seria a forma manual de resolver.",
    "conserto-faixa": "o programa consegue identificar essas bordas pretas sobrando hoje? para que seja cortado automaticamente, no caso o programa avisa e o kaique diz se vai ou não aceitar? o scantailor faz isso hoje? ou o nosso programa, se não faz deveriamos poder fazer.",
    "conserto-gravura": "Entendi, mas o que eu quero, é que apareça um delineado em volta, como um selecionar em volta da parte que vai ser escolhida se vai ser apagada ou não para eu decidir, ai nesse caso, certamente é um erro, e seria apagado, precisamos fazer testes para entender melhor isso e com varios livros diferentes e casos diferentes.",
    "antiphonal1547-006": "porque o jeito de fabrica apagou?",
    "camoes-027": "tanto no jeito de fabrica quanto no petro e branco, estamos lendo de maneira melhor no original, basicamente os dois filtros estragaram o conteúdo.",
    "camoes-066": "(Não concordo, sem comentário)",
    "camoes-104": "por apagar o titulo do altor embaixo, mas imagem em si, não está tão ruim",
    "egenloff-003": "Ele apaga o titulo em vermelho em baixo.",
    "egenloff-012": "é uma pagina que deveria ir para revisar, porque não tem nada nela, deve ser trocada por uma pagina branca",
    "egenloff-047": "(Não concordo, sem comentário)",
    "rariora-008": "Essa pagina deveria se tornar branca, porque unica coisa que ela tem é mancha de outra folha, devia ter um aviso de folhas de rostos, que as vezes tem tanto no final quanto no começo, alguns livros tem até 4 folhas de rosto. o programa está errado, pois não é uma gravura. ele vai para revisão, mas não pelo motivo da gravura, mas porque errou o que tinha uma gravura.",
    "rariora-169": "(Não concordo, sem comentário)",
}


def hist(chave):
    """O comentario anterior, fixado no alto (formato pedido pela gerente em 07/10).
    Nos "Nao concordo" sem comentario, o texto diz isso entre parenteses."""
    return [{"quem": "samuel", "em": "", "texto": COMENT[chave]}]


def op(i, nome, texto):
    return {"id": i, "nome": nome, "texto": texto, "imgs": []}


CONCORDO = lambda frase: [op("concordo", "Concordo", f"Está certo: ela {frase} para 'Para revisar'."),  # noqa: E731
                          op("nao-concordo", "Não concordo", "Diga no comentário por quê."),
                          op("nao-sei", "Não sei", "Preciso ver de outro jeito.")]


def main() -> None:
    q: list = []

    def cartao(id_, parte, pergunta, explicacao, imgs, opcoes, historico=None, **extra):
        c = {"id": f"rv4-{id_}", "ordem": len(q) + 1, "parte": parte, "pergunta": pergunta,
             "explicacao": explicacao,
             "exemplos": [{"src": f"img/{a}.jpg", "legenda": l} for a, l in imgs], "opcoes": opcoes}
        if historico:
            c["historico"] = historico
        c.update(extra)
        q.append(c)

    def pag(base):
        r = REGRA[base]
        return {"hoje": r["hoje"], "regra4": r["regra4"], "gabarito": r["gabarito"], "motivos4": r["motivos4"]}

    # ------------------------------------------------------------------ resumo
    A = f"{P} · a regra ajustada"
    cartao("resumo", A,
           "A regra ajustada pelas suas respostas da rodada 3: fica assim?",
           "Refiz tudo com o programa de hoje, que já tem o conserto do desenho claro (entrou em 06/10). Mudanças na regra: "
           "(1) 'desenho apagado' agora é medido no resultado de verdade, e pega também uma letra grande que some inteira "
           "(a T vermelha do Antiphonal 46); (4) NOVO: texto que sai falhado nos dois jeitos (Camões 27, Camões 104, Egenloff 3); "
           "(5) NOVO: página sem conteúdo, em branco ou só com a mancha do verso (Egenloff 12, Rariora 8). "
           "Nas 89 páginas (as 59 do estudo e as 30 da rodada 3): hoje o programa manda 55 e acerta 52; a regra da rodada 3 manda 15 "
           "e acerta 72; a regra ajustada manda 21 e acerta 78. Nas 30 da rodada 3: de 19 para 25 certas. "
           "Ainda escapam 5: Antiphonal 6 e 31 (pautas vermelhas com falhas pequenas), Camões 9 (a letra A enfeitada sai "
           "lavada nos dois jeitos), Camões 66 e Egenloff 47 (não sei o motivo do seu 'Não concordo': perguntas abaixo). "
           "Vão sem precisar 6, todas de leve (beirada escura, figura que passa um pouco da gravura). "
           "Ressalva: as contas novas foram acertadas em poucas páginas; o texto falhado pega, no Egenloff 3, uma linha vermelha "
           "e um carimbo da biblioteca.",
           [("resumo-regra4", "A regra ajustada e as contas nas 89 páginas.")],
           [op("fica", "Fica assim", "Pode seguir com a regra ajustada."),
            op("quase", "Quase: quero mudar", "Diga no comentário o que muda."),
            op("nao", "Não", "Diga no comentário por quê.")])

    # ------------------------------------------------- cada tipo de erro
    E = f"{P} · cada erro: o jeito mais rápido e o manual"
    cartao("conserto-desenho", E,
           "Para cada erro que manda uma página para 'Para revisar': o jeito mais rápido e o manual. Como você quer o 'mais rápido'?",
           R + "Fiz um cartão para cada tipo de erro (os 6 cartões seguintes), cada um com o jeito mais rápido de resolver, "
           "o jeito manual e uma imagem. Em quase todos o mais rápido é UM clique numa escolha que já existe (trocar o jeito "
           "do 'Só as letras', a força do preto, o corte). A pergunta aqui é onde fica esse clique: "
           "(a) um botão dentro do próprio aviso do 'Para revisar' (ex.: 'Guardar tudo nesta página'), o Kaique olha e clica; "
           "(b) o programa já faz o jeito rápido sozinho e só avisa o que fez (o Kaique desfaz se não gostar); "
           "(c) sem botão novo: o aviso diz o que fazer e o Kaique faz na aba certa.",
           [("c1-desenho-antiphonal046", "Exemplo do jeito rápido: Antiphonal 46 com 'Guardar tudo'.")],
           [op("botao", "(a) Botão no aviso", "O aviso traz o botão do jeito rápido; o Kaique decide."),
            op("sozinho", "(b) O programa faz sozinho", "Faz o jeito rápido e avisa; dá para desfazer."),
            op("so-aviso", "(c) Só o aviso", "O aviso diz o que fazer; o Kaique faz na aba."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("conserto-desenho"))

    cartao("erro-1-desenho", E,
           "Erro 1, o jeito de fábrica apagou parte de um desenho (letra grande, desenho claro): o rápido e o manual.",
           "Quando acontece: um desenho que o programa não achou como gravura e que é mais claro que as letras (a letra T "
           "vermelha do Antiphonal 46). O conserto de 06/10 já trouxe de volta os desenhos colados em tinta escura (Palatino 76, "
           "Siebmacher 7, Rariora 169); sobra o desenho solto, como a T. "
           "JEITO MAIS RÁPIDO: trocar a página para 'Guardar tudo' (aba Filtro, um clique): tudo que não é gravura sai como no "
           "Preto e branco de sempre, e a letra volta. "
           "JEITO MANUAL: aba Marcar, 'gravura ou foto' (fica como no original) ou 'letra e traço' (fica em preto), "
           "num retângulo em volta da letra.",
           [("c1-desenho-antiphonal046", "Antiphonal 46: o jeito de fábrica, 'Guardar tudo' e o Preto e branco.")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("guardar-tudo-sozinho", "Trocar sozinho", "Quando o programa perceber que apagou desenho, ele mesmo troca a página para 'Guardar tudo' e avisa."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    cartao("erro-2-gravura", E,
           "Erro 2, mancha que virou 'gravura' ou figura que passou da gravura achada: o rápido e o manual.",
           "Quando acontece: o programa marca como gravura um remendo ou a mancha do verso (Marial 454, Rariora 8), ou a "
           "gravura achada é menor ou maior que a figura (Camões 104, Antiphon 260). "
           "JEITO MAIS RÁPIDO (planejado, item 2.18 do plano, com o seu pedido do 'delineado'): o programa desenha um contorno em "
           "volta de cada área achada, e o Kaique clica nela para manter, apagar (deixar branco) ou tratar como texto. "
           "Ver a pergunta do delineado, mais abaixo. "
           "JEITO MANUAL (já existe hoje): aba Marcar, 'gravura ou foto', botão 'tirar', e um retângulo sobre a mancha: ela vai "
           "para o branco. Para a figura maior que a área: 'somar' em volta do pedaço que faltou.",
           [("marial454-tirar", "Marial 454: o jeito manual que já existe (remendo 'tirado' da gravura)."),
            ("gravura-delineado-1", "Como ficaria o delineado (jeito rápido planejado).")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    cartao("erro-3-faixa", E,
           "Erro 3, faixa escura na beirada (fundo do scanner, sombra da beirada): o rápido e o manual.",
           "Quando acontece: sobra a borda preta do scanner ou a sombra da beirada da folha (Matemática 32, Egenloff, Camões). "
           "Se ela está em quase todas as páginas do livro (70% ou mais), vira um aviso só, no livro. "
           "JEITO MAIS RÁPIDO (a decidir na pergunta da faixa, mais abaixo): o programa sugere um corte e o Kaique aceita com "
           "um clique, nesta página ou em todas. "
           "JEITO MANUAL (já existe): aba Bordas, arrastar a linha do corte; ou aba Marcar, 'papel', um retângulo sobre a faixa, "
           "que fica branca.",
           [("faixa-cortes", "Onde o nosso corte e o do ScanTailor cortam, e como sai hoje.")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    cartao("erro-4-texto-falhado", E,
           "Erro 4 (NOVO), texto que sai falhado nos dois jeitos (letra clara, gasta ou vermelha): o rápido e o manual.",
           "Quando acontece: a letra é clara demais e o preto e branco perde os traços finos ('que' vira 'qne', 'DE' vira 'DI'). "
           "Acontece igual no jeito de fábrica e no Preto e branco de sempre (Camões 27, Camões 104, Egenloff 3). "
           "JEITO MAIS RÁPIDO: puxar a 'Força do preto' para o lado do escuro (aba Filtro). Testei: no Camões 27 e no Camões 104 "
           "as letras se fecham (85 em vez de 50). No Egenloff 3 (texto vermelho) NÃO resolve, nem a 85. "
           "JEITO MANUAL: para o texto colorido, marcar a linha na aba Marcar e pôr nela o 'Melhorar' ou o 'Mágico pro' "
           "('só neste pedaço'), que guardam a cor; ou a zona 'Tinta com a cor original, papel branco' (P11, decidida, ainda não feita).",
           [("c4-texto-camoes027", "Camões 27: o texto nos dois jeitos e com a força do preto mais forte."),
            ("p-egenloff-003", "Egenloff 3: o texto vermelho, que a força do preto não conserta.")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("forca-sozinho", "Força sozinha", "Quando o programa perceber texto falhado, ele mesmo escurece a força nessa página e avisa."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    cartao("erro-5-sem-conteudo", E,
           "Erro 5 (NOVO), página sem conteúdo (em branco, ou só a mancha do verso): o rápido e o manual.",
           "Quando acontece: folha de guarda, verso em branco de uma prancha, folha de rosto vista por trás (Egenloff 12, "
           "Rariora 8). JEITO MAIS RÁPIDO (depende da sua decisão sobre a página branca, que está na página de escolhas): "
           "um botão 'trocar por página branca', que mantém a página no lugar e não estraga a encadernação. "
           "JEITO MANUAL (já existe hoje): aba Marcar, 'papel', e um retângulo na folha inteira: a página sai branca. "
           "Cuidado com o que existe hoje: o aviso 'Parece em branco' oferece APAGAR a página, e ele errou na Gladstone 18, que "
           "tem um título (pergunta própria, mais abaixo).",
           [("c5-sem-conteudo", "Egenloff 12, Rariora 8 e Gladstone 18: original, como sai e o que cada regra faz.")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    cartao("erro-6-so-texto", E,
           "Erro 6, o que some no 'Só o texto achado' (Guardar só o texto): o rápido e o manual.",
           "Quando acontece: nesse jeito, tudo que não é linha de texto vai para o branco, e às vezes vai junto o que você "
           "queria (a música do Graduale 222). JEITO MAIS RÁPIDO: trocar a página para 'Guardar a tinta forte' ou 'Guardar tudo' "
           "(aba Filtro, um clique). JEITO MANUAL: aba Marcar, 'gravura ou foto' ou 'letra e traço' em volta do que deve ficar.",
           [("so-texto-graduale222", "Graduale 222: no 'Só o texto achado' a música some.")],
           [op("ok", "Os dois jeitos estão bons", "Pode seguir assim."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    # ------------------------------------------------- delineado
    G = f"{P} · respostas aos seus comentários"
    cartao("conserto-gravura", G,
           "O delineado em volta das áreas achadas como gravura: onde ele deve aparecer?",
           R + "Fiz como ficaria: uma linha tracejada em volta de cada área que o programa achou como gravura, com um número. "
           "Clicando no número, o Kaique escolhe: manter, apagar (deixar branco) ou tratar como texto. Pintei de LARANJA as "
           "áreas suspeitas (só mancha, sem desenho dentro; ou tiras finas na beirada) e de VERDE as que parecem gravura. "
           "TESTE em 8 livros (as 89 páginas): o programa achou gravura em 29 páginas (39 áreas). A conta de 'suspeita' "
           "marcou 6 páginas: acertou 4 (o remendo e a mancha do Marial 454, a beirada do Camões 104, a sombra da Matemática 72, "
           "a página só de mancha da Rariora 8) e errou 2 (a moldura dourada da Horas 16 e 27, que é certa). Não pega as áreas "
           "que engolem pautas de música (Antiphon 260, Graduale 269) nem a legenda do Pesel 21: o contorno mostra, mas fica "
           "verde. Por isso o delineado ajuda o Kaique a VER; a decisão continua sendo dele.",
           [("gravura-delineado-1", "Marial 454, Camões 104, Antiphon 260 e Rariora 8: como ficaria o delineado."),
            ("gravura-delineado-2", "Pesel 21, Graduale 269, Rariora 155 e Opus Majus 20: mais casos.")],
           [op("todas", "Em todas as áreas", "Contorno em toda área achada, laranja nas suspeitas."),
            op("suspeitas", "Só nas suspeitas", "Contorno só nas áreas laranja."),
            op("para-revisar", "Só nas páginas do 'Para revisar'", "Contorno só quando a página foi para a lista por causa da gravura."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("conserto-gravura"))

    # ------------------------------------------------- faixa
    cartao("conserto-faixa", G,
           "A borda preta do scanner: como o programa deve cortar?",
           R + "Hoje: o NOSSO programa já tem um corte de bordas ligado de fábrica ('Cortar bordas'). Ele corta pela tinta e para "
           "no escuro do scanner; tira a borda preta quando ela está separada do conteúdo (na Matemática 32 tirou o lado "
           "direito), mas NÃO tira a moldura preta do Egenloff nem as linhas pretas da beirada do Camões. O ScanTailor tem "
           "uma 'caixa da página' que procura a página dentro da borda preta (é o item 2.13 do plano, a sua decisão G7: uma opção, "
           "desligada de fábrica). Ela ainda NÃO está no programa; rodei o código dele num programa de teste: na Matemática 32 "
           "tira também a faixa de baixo, mas no Egenloff e no Camões também não tira a moldura. Então: hoje nenhum dos dois "
           "resolve sozinho esses livros; dá para fazer, juntando a caixa do ScanTailor com o aviso. A proposta: quando sobra "
           "faixa, o programa mostra o corte que sugere e o Kaique aceita ou não, nesta página ou em todas.",
           [("faixa-cortes", "Egenloff 3, Matemática 32 e Camões 66: onde cada um corta, e como sai hoje.")],
           [op("sugere", "O programa sugere, o Kaique aceita", "Mostra o corte sugerido; botão 'aceitar o corte' nesta página ou em todas."),
            op("sozinho", "Corta sozinho e avisa", "Corta sem perguntar; o aviso diz onde cortou e dá para desfazer."),
            op("pintar", "Pintar de branco, sem cortar", "A faixa fica branca (item 2.14), o tamanho da página não muda."),
            op("manual", "Deixar como hoje", "O Kaique corta à mão na aba Bordas."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("conserto-faixa"))

    # ------------------------------------------------- apagar todos os avisos
    cartao("aviso-so-texto", G,
           "Um jeito de apagar todos os avisos de uma vez: qual?",
           R + "Sim. Proposta: no painel 'Para revisar', na aba 'Por motivo' (que você já escolheu no layout), um botão "
           "'está bom assim: todas' que marca como vistas, de uma vez, todas as páginas daquele motivo (A) ou todas da lista (B). "
           "O botão não muda nada nas páginas: só tira da lista. Outra forma (C): uma caixinha 'não avisar mais isso neste livro', "
           "que além de limpar a lista não deixa o aviso voltar quando o Kaique mexe nas páginas. A imagem é um desenho da proposta, "
           "não a tela de verdade.",
           [("aviso-todos", "Desenho da proposta: um botão por motivo (A) ou um botão para tudo (B).")],
           [op("a", "(A) Um botão por motivo", "Marca como vistas todas as páginas daquele motivo."),
            op("b", "(B) Um botão para tudo", "Marca como vistas todas as páginas da lista."),
            op("a-b", "Os dois", "Um por motivo e um para tudo."),
            op("c", "(C) Caixinha 'não avisar mais neste livro'", "Limpa e não deixa voltar."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("aviso-so-texto"))

    # ------------------------------------------------- Antiphonal 6
    b = "antiphonal1547_p006__inteira"
    cartao("pag-antiphonal1547-006", G,
           "Antiphonal 6: por que o jeito de fábrica apagou as pautas vermelhas? E o que fazer?",
           R + "O programa decide tudo no cinza. A tinta vermelha vira um cinza CLARO, mais claro que as letras pretas. Fora "
           "das linhas de texto, o jeito de fábrica ('Guardar a tinta forte') só guarda o que é tão escuro quanto as letras, ou "
           "o que está colado nelas. Os pedaços de pauta vermelha que ficam soltos entre as notas pretas não são escuros o "
           "bastante e vão para o branco; os pedaços que encostam numa nota ficam (por isso a pauta sai em pedaços). A gravura "
           "de baixo à esquerda também perde pedaços, porque o programa não a achou como gravura. Com o programa de hoje sobra "
           "pouca falha, e pela regra ajustada esta página NÃO iria mais para 'Para revisar'. O conserto rápido é 'Guardar tudo': "
           "as pautas saem inteiras.",
           [("p-antiphonal1547-006", "Antiphonal 6: original, como o programa vê (cinza), jeito de fábrica e 'Guardar tudo'.")],
           [op("entendi", "Entendi; a página não precisa ir", "Pouca falha: o Kaique usa 'Guardar tudo' se quiser."),
            op("deve-ir", "Entendi, mas deve ir", "Pauta com falha, mesmo pequena, deve ir para 'Para revisar'."),
            op("cor-forte", "A tinta colorida deve contar como forte", "Estudar: no jeito de fábrica, tinta vermelha (ou de outra cor) fica, como a preta."),
            op("nao-entendi", "Não entendi", "Explique de outro jeito.")],
           historico=hist("antiphonal1547-006"), **pag(b))

    # ------------------------------------------------- Rariora 8 / folhas sem conteudo
    b = "rariora_p008__inteira"
    cartao("pag-rariora-008", G,
           "Rariora 8 e as folhas sem conteúdo (rosto, guardas): o que o programa deve fazer com elas?",
           R + "Você tem razão: não é gravura. A regra ajustada tem um motivo novo, 'página sem conteúdo': quase nenhuma tinta "
           "forte e só escrita fraca (a mancha do verso). Ela pega a Rariora 8 e o Egenloff 12, e nenhuma outra das 89 páginas; "
           "não pega a Gladstone 18 (que tem um título). Agora a página vai para 'Para revisar' por esse motivo, não pela gravura. "
           "O que fazer com ela depende da sua decisão sobre a página branca (na página de escolhas); estas opções não decidem "
           "aquela, só dizem como avisar.",
           [("p-rariora-008", "Rariora 8: só a mancha do verso."),
            ("c5-sem-conteudo", "As três páginas quase vazias e o que cada regra faz.")],
           [op("lista-botao", "Vai para a lista, com botão", "Motivo 'página sem conteúdo' e o botão 'trocar por página branca'."),
            op("sozinho", "Troca sozinho e avisa no livro", "Vira página branca e o aviso do livro lista quais (ex.: 'folhas de rosto e guardas: 1, 2, 211, 212')."),
            op("aviso-livro", "Só um aviso no livro", "Lista as folhas sem conteúdo; o Kaique decide cada uma."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rariora-008"), **pag(b))

    b = "egenloff_p012__inteira"
    cartao("pag-egenloff-012", G,
           "Egenloff 12 (verso em branco): pela regra ajustada, esta página VAI para 'Para revisar'. Você concorda?",
           R + "Agora vai, com o motivo 'página sem conteúdo' (o mesmo da Rariora 8), para o Kaique trocar por página branca. "
           "Antes ela não ia porque a moldura preta do scanner está em todas as páginas do livro e vira um aviso só, no livro. "
           "(Hoje o programa a manda para a lista, mas pelo motivo errado: a moldura conta como 'tinta forte fora do texto'.)",
           [("p-egenloff-012", "Egenloff 12: original e como sai.")],
           CONCORDO("vai"), historico=hist("egenloff-012"), **pag(b))

    cartao("em-branco", G,
           "O aviso de hoje 'Parece em branco. Quer apagar?': o que fazer com ele?",
           "Achado nesta rodada. O programa já tem um aviso 'Parece em branco', com o botão 'apagar esta página'. Nas 89 páginas "
           "ele apareceu só na Gladstone 18, que NÃO está em branco: tem o título 'DA ORAÇÃO' (com o botão, o Kaique apagaria o "
           "título da parte). E ele não apareceu no Egenloff 12 nem na Rariora 8, que não têm conteúdo (a moldura e a mancha "
           "enganam a conta). Além disso, apagar tira a página da fila e troca frente e verso das seguintes na encadernação "
           "(o que você levantou em 07/10). As opções não decidem a página branca, que está na página de escolhas.",
           [("c5-sem-conteudo", "Gladstone 18 (à direita): o aviso 'Parece em branco' numa página com título.")],
           [op("juntar", "Juntar ao 'página sem conteúdo'", "Um aviso só, com a conta nova (que não pega a Gladstone 18)."),
            op("trocar-botao", "Manter, mas trocar o botão", "O botão passa a ser 'trocar por página branca' em vez de 'apagar'."),
            op("esperar", "Esperar a decisão da página branca", "Fica como está até lá."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")])

    # ------------------------------------------------- os "Nao concordo"
    N = f"{P} · os seus 'Não concordo' da rodada 3"
    b = "camoes_p027__inteira"
    cartao("pag-camoes-027", N,
           "Camões 27: pela regra ajustada, esta página VAI para 'Para revisar'. Você concorda?",
           R + "Você tem razão: os dois jeitos estragam a letra. O papel é escuro e a letra é clara; o preto e branco perde os "
           "traços finos ('que' vira 'qne', 'e' vira 'c'), mais ainda na nota de rodapé. A regra da rodada 3 só olhava o que o "
           "jeito de fábrica apaga A MAIS que o Preto e branco, e aqui os dois falham igual. Ajuste: motivo novo 'texto falhado "
           "nos dois jeitos' (duas ou mais linhas em que o preto e branco guarda menos de 62% da tinta clara da letra). Com ele "
           "a página vai. Conserto rápido: a força do preto mais forte (ver o cartão do erro 4).",
           [("p-camoes-027", "Camões 27: a nota de rodapé nos dois jeitos e as linhas que mandam a página."),
            ("c4-texto-camoes027", "O texto de cima e a força do preto mais forte.")],
           CONCORDO("vai"), historico=hist("camoes-027"), **pag(b))

    b = "camoes_p066__inteira"
    cartao("pag-camoes-066", N,
           "Camões 66: você não concordou, sem comentário. O que está errado nela?",
           R + "No meu olho, com o programa de hoje: o texto sai legível (com os traços finos um pouco mais fracos, como no "
           "Camões 27, mas a regra não acha falha suficiente); o que destoa são as linhas pretas da beirada (à direita, em cima "
           "e nos cantos de baixo) e um borrão no canto de baixo à esquerda. Essas linhas estão nas 6 páginas do Camões; pela "
           "regra, faixa que está no livro inteiro vira um aviso só, no livro, e não manda cada página. Por isso ela não vai. "
           "Escolha o que acontece:",
           [("p-camoes-066", "Camões 66: a página inteira, original e os dois jeitos.")],
           [op("beirada-pagina", "São as linhas pretas: deve ir", "Mesmo estando no livro todo, cada página com linha preta vai para a lista."),
            op("beirada-livro", "São as linhas pretas: aviso no livro basta", "Desde que o corte (pergunta da faixa) resolva."),
            op("letra", "É a letra fraca", "Deve ir pelo texto falhado, mesmo sendo pouco."),
            op("agora-ok", "Agora está bom", "Com o programa de hoje, não precisa ir."),
            op("outro", "Outra coisa", "Diga no comentário.")],
           historico=hist("camoes-066"), **pag(b))

    b = "camoes_p104__inteira"
    cartao("pag-camoes-104", N,
           "Camões 104 (contracapa): pela regra ajustada, esta página VAI, agora pelo título falhado. Você concorda?",
           R + "Entendi assim: ela deve ir, mas pelo título, não pela imagem. O título 'LUIZ DE CAMÕES' sai 'LUIZ DI CAMÕUS' "
           "nos dois jeitos. A regra ajustada agora dá os dois motivos: 'texto falhado nos dois jeitos' (o título) e 'figura "
           "além da gravura achada' (a área de gravura escorre pela beirada; o retrato em si sai bem, como você disse). "
           "Conserto rápido do título: força do preto mais forte (com 85 o 'DE' volta). Se você preferir que a beirada NÃO conte "
           "como motivo aqui, diga no comentário.",
           [("p-camoes-104", "Camões 104: o título nos quatro jeitos e a gravura achada.")],
           CONCORDO("vai"), historico=hist("camoes-104"), **pag(b))

    b = "egenloff_p003__inteira"
    cartao("pag-egenloff-003", N,
           "Egenloff 3 (folha de rosto): pela regra ajustada, esta página VAI para 'Para revisar'. Você concorda?",
           R + "Sim: as duas linhas vermelhas do pé ('1880 neu aufgelegt von / George Gilbers, Königl. Hofbuchhändler zu "
           "Dresden') saem falhadas nos dois jeitos: o vermelho vira um cinza claro e o preto e branco o quebra. A regra da "
           "rodada 3 não via isso; com o motivo novo 'texto falhado nos dois jeitos' a página vai. A força do preto mais forte "
           "NÃO conserta este caso; o conserto é marcar a linha com o 'Melhorar' ou o 'Mágico pro' ('só neste pedaço'), que "
           "guardam a cor. Ressalva: das duas linhas que a regra conta aqui, uma é a vermelha e a outra é o carimbo da biblioteca.",
           [("p-egenloff-003", "Egenloff 3: as linhas vermelhas do pé nos dois jeitos.")],
           CONCORDO("vai"), historico=hist("egenloff-003"), **pag(b))

    b = "egenloff_p047__inteira"
    cartao("pag-egenloff-047", N,
           "Egenloff 47: você não concordou, sem comentário. O que está errado nela?",
           R + "No meu olho, com o programa de hoje: o ornamento sai inteiro nos dois jeitos (o jeito de fábrica apaga só "
           "pontinhos). O que sobra é da página inteira: a moldura preta do scanner e a tarja da biblioteca embaixo (SLUB), "
           "que estão em todas as páginas do livro e viram um aviso só, no livro; e restos dos carimbos e da anotação a lápis. "
           "Por isso ela não vai. Escolha o que acontece:",
           [("p-egenloff-047", "Egenloff 47: como sai inteira, e o ornamento ampliado.")],
           [op("moldura", "É a moldura preta / a tarja", "A página deve ir mesmo que o livro inteiro tenha."),
            op("carimbos", "São os carimbos e anotações", "O que sobra deles deve mandar a página."),
            op("ornamento", "É o ornamento", "Os traços finos falham; deve ir."),
            op("agora-ok", "Agora está bom", "Com o programa de hoje, não precisa ir."),
            op("outro", "Outra coisa", "Diga no comentário.")],
           historico=hist("egenloff-047"), **pag(b))

    b = "rariora_p169__inteira"
    cartao("pag-rariora-169", N,
           "Rariora 169: com o programa de hoje, esta página NÃO VAI, porque agora sai certa. Você concorda?",
           R + "Você tinha razão: na rodada 3 o pontilhado da concha (Fig. 8) sumia e a regra não pegava (ficou logo abaixo do "
           "limite). Desde 06/10 o programa tem o conserto do desenho claro, e a concha sai inteira, como no Preto e branco. "
           "Agora não há o que revisar, e ela não vai.",
           [("p-rariora-169", "Rariora 169: rodada 3 (sem o conserto) e hoje (com o conserto).")],
           CONCORDO("não vai"), historico=hist("rariora-169"), **pag(b))

    (PASTA / "rodada-4-perguntas.json").write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
    print("perguntas", len(q))
    for c in q:
        imgs = [e["src"] for e in c["exemplos"]]
        falta = [s for s in imgs if not (PASTA / s).exists()]
        print(c["ordem"], c["id"], "historico" if "historico" in c else "", "FALTA " + str(falta) if falta else "")


if __name__ == "__main__":
    main()
