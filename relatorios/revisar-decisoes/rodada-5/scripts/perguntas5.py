"""Monta ../rodada-5-perguntas.json (rodada 5 das decisoes do "Para revisar").

Mesmo formato das rodadas 3 e 4 (colecao `decisoes` da pagina "Quando revisar uma
pagina"), com `historico` (comentarios anteriores fixados no alto). Novo nesta
rodada: cada opcao das perguntas refeitas leva a sua imagem em `imgs`
([{"src", "legenda"}]); como a pagina, na versao lida em 08/10, nao mostra
`opcoes[].imgs`, as mesmas imagens vao tambem em `exemplos`, na ordem das opcoes
e com o nome da opcao na legenda.

O `historico` traz a cadeia: o comentario da rodada 3 (quando houve) e o da
rodada 4, com a hora de verdade lida do banco (colecao `respostas`, 08/10).

Uso: python perguntas5.py
"""
import json
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
R4 = json.loads((PASTA.parent / "rodada-4" / "rodada-4-perguntas.json").read_text(encoding="utf-8"))
R4 = {c["id"]: c for c in R4}
BANCO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\banco\respostas")
R = "RESPOSTA AO SEU COMENTÁRIO: "


def resp4(id4):
    return json.loads((BANCO / f"{id4}.json").read_text(encoding="utf-8"))


def hist(id4):
    """Os comentarios anteriores da pergunta id4 (rodada 3, se houve) + o da rodada 4."""
    h = [dict(x) for x in R4[id4].get("historico", [])]
    for x in h:   # a hora da rodada 3, que a rodada 4 deixou vazia: lida do banco pelo texto
        if not x.get("em"):
            for f in BANCO.glob("rv3-*.json"):
                d = json.loads(f.read_text(encoding="utf-8"))
                if (d.get("comentario") or "").strip() == x["texto"].strip():
                    x["em"] = d["em"]
            r3 = BANCO / (id4.replace("rv4-", "rv3-") + ".json")
            if not x.get("em") and r3.exists():   # "Nao concordo" sem comentario
                x["em"] = json.loads(r3.read_text(encoding="utf-8"))["em"]
    r = resp4(id4)
    texto = r.get("comentario") or f"(respondeu '{r['opcaoNome']}', sem comentário)"
    h.append({"quem": "samuel", "em": r["em"], "texto": texto, "resposta": r["opcaoNome"]})
    return h


def img(nome, legenda):
    return {"src": f"img/{nome}.jpg", "legenda": legenda}


def op(i, nome, texto, imagens=()):
    return {"id": i, "nome": nome, "texto": texto, "imgs": [img(a, l) for a, l in imagens]}


def main() -> None:
    q: list = []

    def cartao(id_, parte, pergunta, explicacao, exemplos, opcoes, historico=None):
        c = {"id": f"rv5-{id_}", "ordem": len(q) + 1, "parte": parte, "pergunta": pergunta,
             "explicacao": explicacao, "exemplos": exemplos, "opcoes": opcoes}
        # as imagens das opcoes tambem em exemplos (a pagina ainda nao mostra opcoes[].imgs)
        vistos = {e["src"] for e in c["exemplos"]}
        for o in opcoes:
            for im in o["imgs"]:
                if im["src"] in vistos:   # a mesma imagem serve a duas opcoes: aparece uma vez so
                    continue
                vistos.add(im["src"])
                c["exemplos"].append({"src": im["src"], "legenda": f"Opção '{o['nome']}': {im['legenda']}"})
        if historico:
            c["historico"] = historico
        q.append(c)

    # ================================================================ refeitas
    P = "Rodada 5 · as três que ficaram confusas, de novo"
    cartao("erro-1-desenho", P,
           "Quando o programa apaga uma letra grande: o que o aviso do 'Para revisar' oferece?",
           R + "Refiz do zero. O que acontece: no Antiphonal 46, a letra T vermelha grande some no Preto e branco com "
           "'Só as letras' de fábrica, e a página vai para 'Para revisar'. A pergunta é só uma: o que o Kaique vê no aviso "
           "dessa página? Cada opção tem a imagem do que ele veria e faria. Marcar à mão na aba Marcar continua existindo "
           "em qualquer opção.",
           [img("r5-desenho-o-que-acontece", "O que acontece: a letra T vermelha some.")],
           [op("botao", "Botão 'Trazer de volta nesta página'",
               "O aviso tem o botão; um clique e a letra volta (só nesta página).",
               [("r5-desenho-op-botao", "o Kaique clica no botão do aviso e a letra volta.")]),
            op("sozinho", "O programa traz de volta sozinho",
               "A página já sai com a letra; o aviso conta o que foi feito e tem 'Desfazer'.",
               [("r5-desenho-op-sozinho", "a letra já volta; o aviso diz o que foi feito.")]),
            op("mao", "Sem botão: o Kaique marca à mão",
               "O aviso só avisa; ele desenha um retângulo na aba Marcar ('letra e traço').",
               [("r5-desenho-op-mao", "o Kaique desenha o retângulo na aba Marcar.")]),
            op("nao-entendi", "Ainda não entendi", "Diga no comentário o que ficou confuso.")],
           historico=hist("rv4-erro-1-desenho"))

    cartao("erro-5-sem-conteudo", P,
           "Página sem conteúdo (em branco, ou só a mancha da página de trás): que botões o aviso mostra?",
           R + "Refiz do zero. O que você está respondendo: quando o programa acha uma página sem nada do livro (o verso "
           "em branco do Egenloff 12, a Rariora 8 que só tem a mancha da página de trás), ela vai para 'Para revisar' com o "
           "motivo 'página sem conteúdo'. Pergunto só quais botões aparecem nesse aviso. 'Deixar em branco' põe uma folha "
           "branca no lugar (a encadernação não muda); 'Tirar do livro' tira a página de vez (as seguintes andam uma casa). "
           "Você já pediu os dois botões separados no outro cartão ('Parece em branco'); aqui é para esta página.",
           [img("r5-vazia-o-que-acontece", "O que acontece: a página não tem nada do livro.")],
           [op("os-dois", "Os dois botões: 'Deixar em branco' e 'Tirar do livro'",
               "O Kaique escolhe em cada página.",
               [("r5-vazia-op-branco", "'Deixar em branco': folha branca no lugar."),
                ("r5-vazia-op-tirar", "'Tirar do livro': a página sai e as outras andam.")]),
            op("so-branco", "Só 'Deixar em branco'",
               "O aviso só oferece a folha branca; tirar do livro, só pelo menu da página.",
               [("r5-vazia-op-branco", "o único botão: folha branca no lugar.")]),
            op("sozinho", "O programa deixa em branco sozinho e avisa",
               "A página já sai branca; o aviso diz qual foi e tem 'Desfazer'."),
            op("nao-entendi", "Ainda não entendi", "Diga no comentário o que ficou confuso.")],
           historico=hist("rv4-erro-5-sem-conteudo"))

    cartao("erro-6-so-texto", P,
           "Com 'Guardar só o texto', sumiu a música: o que o aviso do 'Para revisar' oferece?",
           R + "Refiz do zero, sem falar em 'dois jeitos'. O que acontece: 'Guardar só o texto' (antes 'Só o texto achado') "
           "é uma escolha que o Kaique faz quando quer só as letras; ela apaga tudo que não é linha de texto. No Graduale 222 "
           "a música inteira some, e a página vai para 'Para revisar'. Pergunto só o que o aviso oferece. Marcar à mão na aba "
           "Marcar continua existindo em qualquer opção.",
           [img("r5-sotexto-o-que-acontece", "O que acontece: a música some.")],
           [op("botao", "Botão 'Trazer de volta nesta página'",
               "Um clique e esta página passa a guardar a tinta forte (a música volta); as outras continuam só com o texto.",
               [("r5-sotexto-op-botao", "o Kaique clica no botão do aviso e a música volta.")]),
            op("mao", "Sem botão: o Kaique marca à mão",
               "O aviso só avisa; ele desenha um retângulo em volta do que quer de volta.",
               [("r5-sotexto-op-mao", "o Kaique marca uma pauta; só ela volta.")]),
            op("nao-entendi", "Ainda não entendi", "Diga no comentário o que ficou confuso.")],
           historico=hist("rv4-erro-6-so-texto"))

    # ================================================================ respostas
    C = "Rodada 5 · respostas aos seus comentários"
    cartao("erro-2-gravura", C,
           "Achar as figuras com mais acerto: quando fazer?",
           R + "Concordo: hoje o programa erra para os dois lados. Nas 89 páginas testadas ele deixou de achar figuras "
           "(a letra T do Antiphonal 46, a letra A do Camões 9, a estátua do Camões 6) e achou 'figura' onde não há "
           "(o remendo do Marial 454, a página de mancha da Rariora 8, as pautas do Antiphon 260). Melhorar o detector "
           "já está no plano: item 1.5 (o filtro por zona automático, Fase 1, adiado) e item 2.18 (editar as áreas à mão, "
           "com o delineado). Entendi 'selecionar coisas que não foram apagadas' como: o programa marcar sozinho, para "
           "o Kaique ver, o que sobrou na página e não devia (mancha, carimbo). Se não for isso, diga no comentário.",
           [img("gravura-delineado-1", "Acertos e erros do detector de hoje (contorno laranja = suspeita).")],
           [op("agora", "Estudar o detector agora", "Um agente mede os erros nos 8 livros e propõe o conserto, antes do 2.18."),
            op("no-plano", "Fica no plano (1.5 e 2.18)", "Segue a ordem do plano; até lá, o delineado e a mão."),
            op("outro", "Entendeu errado / outro jeito", "Diga no comentário.")],
           historico=hist("rv4-erro-2-gravura"))

    cartao("erro-4-tintas", C,
           "Reconhecer melhor a tinta (para a letra clara ou colorida não sair falhada): quando fazer?",
           R + "Fica anotado: a 'força sozinha' é o remendo; o certo é o programa reconhecer a tinta. Isso já está no plano: "
           "item 1.4, 'máscara de tinta como o Internet Archive: achar a tinta dentro das linhas de texto guardando a cor "
           "original', que resolve o texto vermelho do Egenloff 3 (onde a força não adianta). É o mesmo pedido seu de 01/10: "
           "'tem que reconhecer as letras mesmo em outras cores'. O 1.4 está na Fase 1, adiado quando a Fase 2 foi adiantada.",
           [img("p-egenloff-003", "Egenloff 3: o texto vermelho que a força do preto não conserta."),
            img("c4-texto-camoes027", "Camões 27: a letra clara que a força conserta.")],
           [op("adiantar", "Adiantar o 1.4 para agora", "A tinta colorida e clara passa na frente."),
            op("no-plano", "Fica no plano; até lá, a força sozinha", "O programa escurece a força quando acha texto falhado."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-erro-4-texto-falhado"))

    cartao("conserto-gravura", C,
           "O delineado das áreas achadas: como aumentar ou diminuir uma área?",
           R + "Fica assim: um botão (ou aba) 'Mostrar as áreas achadas' desenha o contorno de todas as áreas; nas páginas "
           "do 'Para revisar' elas já aparecem em laranja; e dá para aumentar ou diminuir cada área. Entra no item 2.18 do "
           "plano (edição manual das zonas), junto com o seu pedido de clicar numa área para apagar ou pintar (P11b). A "
           "aparência fica com o agente de layout. Falta só uma escolha: como mudar o tamanho.",
           [],
           [op("alcas", "Puxar pelos quadradinhos", "Cantos e lados da área; bom para retângulo.",
               [("r5-delineado-ajustar", "A, à esquerda: quadradinhos nos cantos e lados.")]),
            op("pincel", "Pincel 'somar' / 'tirar'", "Passa o pincel na beirada; bom para forma solta.",
               [("r5-delineado-ajustar", "B, à direita: o pincel redondo.")]),
            op("os-dois", "Os dois", "Quadradinhos e pincel."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-conserto-gravura"))

    cartao("conserto-faixa", C,
           "O corte da borda preta: o seletor de páginas.",
           R + "Fica assim: o programa sugere o corte (item 2.13); o Kaique pode mudar o corte sugerido; pode aplicar um "
           "corte em todas as páginas e depois mudar só algumas (essas viram exceção e não mexem nas outras); e escolhe as "
           "páginas num seletor grande, com 'Selecionar todas'. O que já existe hoje: na aba Bordas, o corte feito à mão "
           "fica só naquela página, e 'usar em todas' copia para todas, mas apaga as exceções. Muda: as exceções ficam, e "
           "entra o seletor. A aparência fica com o agente de layout. Pergunta: que botões rápidos o seletor tem?",
           [img("faixa-cortes", "Onde o nosso corte e o do ScanTailor cortam hoje.")],
           [op("todas-nenhuma", "'Selecionar todas' e 'Nenhuma'", "Só os dois.",
               [("r5-seletor-2", "o seletor com os dois botões.")]),
            op("pares-impares", "Também 'Só as pares' e 'Só as ímpares'",
               "Útil porque a borda do scanner costuma ficar de um lado nas pares e do outro nas ímpares.",
               [("r5-seletor", "o seletor com os quatro botões.")]),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-conserto-faixa"))

    cartao("aviso-so-texto", C,
           "Os avisos: dar 'está bom' em uma página, num motivo ou em tudo; e o que acontece ao processar.",
           R + "Fica assim, como você pediu: dar 'está bom assim' numa página, num motivo de uma página, em todas as páginas "
           "de um motivo, ou em tudo; e um seletor grande com as páginas daquele problema, para desmarcar ou dar ok em "
           "todas (o mesmo seletor do corte). Sua pergunta: 'quando eu resolver, o programa percebe sozinho?' Sim, na maior "
           "parte: os avisos do 'Só as letras' são refeitos toda vez que a página é desenhada, e somem quando o motivo some "
           "(ex.: trocar a página para 'Guardar tudo'); e quando o Kaique conserta pela própria aba (corte, ângulo, filtro), "
           "a página já fica marcada como conferida. A regra nova vai seguir isso. Ao processar com avisos: o programa JÁ "
           "para e pergunta ('Ainda tem 12 páginas... conferir ou processar assim mesmo?'). Funcionalidade comigo, aparência "
           "com o agente de layout, como você disse. Pergunta: o que essa janela mostra?",
           [img("r5-seletor", "O seletor grande (desenho da proposta).")],
           [op("como-hoje", "Como hoje", "Diz quantas páginas e tem 'conferir' e 'processar assim mesmo'.",
               [("r5-antes-de-processar", "a janela que já existe.")]),
            op("lista", "Lista as páginas e os motivos", "A janela mostra a lista (página e motivo), com 'ver' e 'continuar assim mesmo'."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-aviso-so-texto"))

    cartao("em-branco", C,
           "Um aviso para cada coisa, com os botões 'Deixar em branco' e 'Tirar do livro' separados: fica assim?",
           R + "Fica assim: 'Parece em branco' e 'Página sem conteúdo' viram dois avisos diferentes, e cada um tem os dois "
           "botões separados: 'Deixar em branco' (troca por folha branca, a encadernação não muda) e 'Tirar do livro' "
           "(apaga a página de vez). É o que você decidiu na página de escolhas em 07/10 (dois botões; a tecla Delete deixa "
           "em branco), que está na Lista de espera, Fase 6. Também fica anotado que a conta do 'Parece em branco' precisa "
           "melhorar: na Gladstone 18 ela avisou numa página que tem título. A aparência fica com o agente de layout.",
           [img("r5-avisos-separados", "Os dois avisos, cada um com os dois botões (desenho da proposta).")],
           [op("fica", "Fica assim", "Pode seguir."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-em-branco"))

    cartao("pag-egenloff-047", C,
           "Egenloff 47: a moldura do scanner e a tarja da biblioteca saem do livro. Cortar fora ou pintar de branco?",
           R + "Sim: a moldura preta e a tarja 'SLUB' do pé não são do livro e deveriam sair. Hoje nem o nosso corte nem o "
           "do ScanTailor tiram (rodada 4). Como estão em todas as páginas, vira um aviso só, no livro, com o corte sugerido "
           "para todas as páginas (o seletor do cartão da borda preta). Os dois quadros da direita na imagem são simulações.",
           [img("r5-egenloff047-tarja", "Egenloff 47: o que não é do livro, como sai hoje e as duas simulações.")],
           [op("cortar", "Cortar fora", "A página fica do tamanho do papel do livro (item 2.13)."),
            op("pintar", "Pintar de branco", "A folha mantém o tamanho; o que não é do livro fica branco (item 2.14)."),
            op("escolher", "O Kaique escolhe por livro", "As duas formas, com uma escolha por livro."),
            op("outro", "Quero de outro jeito", "Diga no comentário.")],
           historico=hist("rv4-pag-egenloff-047"))

    (PASTA / "rodada-5-perguntas.json").write_text(json.dumps(q, ensure_ascii=False, indent=1), encoding="utf-8")
    print("perguntas", len(q))
    for c in q:
        srcs = [e["src"] for e in c["exemplos"]] + [i["src"] for o in c["opcoes"] for i in o["imgs"]]
        falta = sorted({s for s in srcs if not (PASTA / s).exists()})
        print(c["ordem"], c["id"], len(c.get("historico", [])), "FALTA " + str(falta) if falta else "")


if __name__ == "__main__":
    main()
