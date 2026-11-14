"""Parte 1 da reescrita da Central (13/11/2026): as perguntas que destravam consertos.

Lê o documento atual de cada aba (dados/conferencias/<aba>.json), troca só o TEXTO das perguntas
da Parte 1 (título, explicação, nome e texto das opções, sugestão, legendas; uma opção nova onde
o comentário do Samuel pediu outra coisa) e grava o documento inteiro em novas/<aba>.json.
Os ids das perguntas e das opções ficam os mesmos. As outras perguntas da aba ficam iguais.

Imagens novas: src "imagens/<arquivo>.png" (arquivo em novas/imagens/); a gerente sobe e troca
pelo endereço da Central.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
DADOS = PASTA / "dados" / "conferencias"
NOVAS = PASTA / "novas"


def ler(aba: str) -> dict:
    return json.loads((DADOS / f"{aba}.json").read_text(encoding="utf-8"))


def gravar(aba: str, doc: dict) -> None:
    NOVAS.mkdir(parents=True, exist_ok=True)
    (NOVAS / f"{aba}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")


def pergunta(doc: dict, pid: str) -> dict:
    return next(p for p in doc["perguntas"] if p["id"] == pid)


def opcao(p: dict, oid: str) -> dict:
    return next(o for o in p["opcoes"] if o["id"] == oid)


def trocar_opcoes(p: dict, novas: list[dict]) -> None:
    """Troca nome/texto das opções existentes (pelo id) e acrescenta as novas. Nenhuma opção que
    já existia sai (as respostas dele estão ligadas aos ids)."""
    antigas = {o["id"]: o for o in p["opcoes"]}
    lista = []
    for n in novas:
        if n["id"] in antigas:
            o = antigas.pop(n["id"])
            o["nome"], o["texto"] = n["nome"], n["texto"]
            lista.append(o)
        else:
            lista.append({"id": n["id"], "nome": n["nome"], "texto": n["texto"],
                          **({"imgs": []} if any("imgs" in o for o in p["opcoes"]) else {})})
    assert not antigas, f"{p['id']}: opção antiga ficou de fora: {list(antigas)}"
    p["opcoes"] = lista


def fixar(p: dict, quem: str, em: str, texto: str) -> None:
    """Comentário anterior fixado no alto da pergunta (CLAUDE.md §10.10), sem repetir."""
    hist = p.setdefault("historico", [])
    if not any(h.get("texto") == texto for h in hist):
        hist.append({"quem": quem, "em": em, "texto": texto})


# ---------------------------------------------------------------------------------------------
# Aba perg-revisao-codigo
# ---------------------------------------------------------------------------------------------

def revisao() -> dict:
    doc = ler("perg-revisao-codigo")
    doc["nome"] = "Revisão do código: 4 perguntas (10/11)"
    doc["origem"] = ("Revisão do código que você pediu em 10/11 (\"Eu não quero remendos nesse código\"). "
                     "Os prints são do programa de hoje (versão de teste), em cópias do Gradus e do Siebmacher.")

    p = pergunta(doc, "rev-usar-em-todas")
    p["titulo"] = ("Botão \"usar em todas\": deve deixar de fora as páginas que você mexeu à mão, "
                   "em todas as ferramentas?")
    p["explicacao"] = [
        "Do que se trata: cada ferramenta tem, no painel Propriedades (lado direito), um botão que copia "
        "o que você fez numa página para as outras páginas do livro. No Cortar, no Marcar, no Endireitar e "
        "no Mover ele se chama \"usar em todas\"; no Filtro e no Girar, \"aplicar em: todas\".",
        "O que acontece hoje: no Cortar, no Dividir e no Mover, o botão abre a lista \"Em quais páginas?\" "
        "com as páginas que você mexeu à mão já desmarcadas. Elas ficam como você deixou. No Marcar, no "
        "Filtro, no Endireitar e no Girar, não abre lista: vale em todas e passa por cima do que você fez à mão.",
        "Exemplo de verdade (Gradus Primus, cópia, versão de teste): na página 15 marquei a águia como "
        "gravura e cortei a página à mão. Na página 17 apertei o botão. Pelo Marcar, a águia da 15 sumiu "
        "(faixa laranja). Pelo Cortar, a 15 ficou como eu deixei (faixa verde). Conferi também as outras: o "
        "Filtro trocou o Melhorar que a 15 tinha pelo Preto e branco da 17; o Endireitar trocou os 2 graus "
        "da 15 pelos -1 da 17; o Girar deixou a 15, que eu tinha virado à mão, virada igual à 17.",
        "É defeito ou escolha? É a mesma ferramenta fazendo duas coisas diferentes. Ninguém escolheu assim: "
        "cada ferramenta foi feita numa época. Em 08/10 você pediu: \"quando mudar de um não muda de todas\"; "
        "em 10/11: \"se mudou a ferramenta, muda em todos os lugares\".",
        "O que muda no que já funciona, se for \"Sim\": no Girar, a página que você virou à mão deixa de "
        "acompanhar as outras (hoje ela fica virada igual à página da vez, como você decidiu em 06/10). As "
        "páginas que você não mexeu continuam mudando como hoje. Você continua no controle: na lista dá "
        "para marcar de volta a página mexida à mão.",
        "Situação: só pergunta; nada foi mudado. Se for \"Sim\", entra na fila de consertos e volta para "
        "você testar.",
        "O que você escolhe: se o Marcar, o Filtro, o Endireitar e o Girar passam a deixar de fora as "
        "páginas mexidas à mão, como o Cortar.",
        "(Para consulta: decisões D-090, D-035 e D-667.)",
    ]
    trocar_opcoes(p, [
        {"id": "sim", "nome": "Sim: as quatro fazem como o Cortar (recomendo)",
         "texto": "O botão abre a lista \"Em quais páginas?\" com as páginas mexidas à mão desmarcadas; "
                  "elas ficam como você deixou. É a faixa verde."},
        {"id": "nao", "nome": "Não: fica como hoje",
         "texto": "Nessas quatro, o botão continua valendo em todas e passando por cima do que você fez "
                  "à mão. É a faixa laranja."},
    ])
    p["sugestao"] = "Sim: é o que você pediu em 08/10 e em 10/11."
    p["primeira_imagem"]["legenda"] = (
        "Gradus (cópia), páginas 15 a 18. Azul: antes do clique (a 15 mexida à mão). Laranja (como é hoje): "
        "\"usar em todas\" do Marcar na 17, a águia marcada na 15 some. Verde: \"usar em todas\" do Cortar "
        "na 17, a 15 fica como você deixou.")

    p = pergunta(doc, "rev-letra-clara-todas")
    p["titulo"] = ("Caixinha \"Letra clara em fundo escuro\": deve ir junto quando você aplica o filtro em "
                   "todas as páginas?")
    p["explicacao"] = [
        "Do que se trata: no painel \"Filtro da página\" (lado direito da área de trabalho), em \"Mais "
        "ajustes\", há a caixinha \"Letra clara em fundo escuro\", para página de letra ou desenho claro em "
        "fundo escuro. Embaixo do painel, \"Aplicar em: todas\" leva o filtro desta página para as outras.",
        "O que acontece hoje: o \"Aplicar em: todas\" leva o filtro e as outras caixinhas, mas esta não vai. "
        "Pelo Automático (etapa \"Limpar a folha\"), ela vai para todas as páginas em que ele roda. É defeito: "
        "o painel esqueceu esta caixinha na lista do que vai junto. Conferi no programa hoje (13/11): continua "
        "assim.",
        "Exemplo de verdade (Siebmacher, cópia; as páginas 11, 13, 15 e 17 são desenhos claros em fundo "
        "escuro; o livro já tinha passado pelo Automático em Preto e branco): na página 13 marquei a caixinha "
        "e apertei \"todas\". Só a 13 ficou com ela (faixa laranja). Pelo Automático, com a caixinha marcada, "
        "as quatro ficaram com ela (faixa verde).",
        "De onde veio: a caixinha é pedido seu (05/10: \"Uma caixinha por página, 'Letra clara em fundo "
        "escuro', que o Kaique marca à mão\"). Em 10/11: \"se mudou a ferramenta, muda em todos os lugares\".",
        "O que muda no que já funciona, se for \"Sim\": só o \"Aplicar em\" do painel (\"todas\" e \"daqui "
        "em diante\"). Ele passa a levar a caixinha como ela está nesta página, igual faz com as outras: se "
        "nesta página ela está desmarcada, desmarca nas outras também, como o Automático já faz. O Automático "
        "não muda.",
        "Situação: só pergunta; nada foi mudado. Se for \"Sim\", entra na fila de consertos e volta para "
        "você testar.",
        "O que você escolhe: se a caixinha vai junto no \"Aplicar em\" do painel, como no Automático.",
        "(Para consulta: decisões D-177 e D-667.)",
    ]
    trocar_opcoes(p, [
        {"id": "sim", "nome": "Sim: a caixinha vai junto, como no Automático (recomendo)",
         "texto": "\"todas\" e \"daqui em diante\" levam a caixinha como está nesta página. É a faixa verde."},
        {"id": "nao", "nome": "Não: fica como hoje",
         "texto": "No painel, a caixinha fica só na página em que você marcou. É a faixa laranja."},
    ])
    p["sugestao"] = "Sim: é defeito, e você já mandou a ferramenta fazer igual em todos os lugares (10/11)."
    p["primeira_imagem"]["legenda"] = (
        "Siebmacher (cópia), páginas 11, 13, 15 e 17. Azul: antes (caixinha desmarcada em todas). Laranja "
        "(como é hoje): marcada na 13 e \"Aplicar em: todas\", só a 13 fica com ela. Verde: pelo Automático, "
        "as quatro ficam com ela.")

    p = pergunta(doc, "rev-dividir-grade-linha")
    p["titulo"] = ("Grade \"Todas as páginas\", botão \"dividir\": deve cortar onde você deixou a linha azul?")
    p["explicacao"] = [
        "Do que se trata: na ferramenta Dividir (barra da esquerda), a linha azul mostra onde a folha vai "
        "ser cortada ao meio, e você pode arrastá-la. A grade \"Todas as páginas\" (botão \"ver todas\", em "
        "cima da tira de páginas) também tem um botão \"dividir\", para as páginas que você escolher nela.",
        "O que acontece hoje: o \"dividir esta\" do Dividir corta onde você deixou a linha. O \"dividir\" da "
        "grade mede a folha de novo e corta onde o programa acha a lombada: a linha que você arrastou fica "
        "guardada, mas não é usada. É defeito.",
        "Exemplo de verdade (Gradus Primus, cópia, folha 10 ainda inteira, páginas 18 e 19): arrastei a "
        "linha azul para 40% da largura; o programa tinha posto no meio (50%). Arrastei longe do meio de "
        "propósito, para ficar fácil de ver. Pelo \"dividir esta\", a folha foi cortada nos 40% (faixa "
        "verde). Pela grade, nos 50% (faixa laranja).",
        "De onde veio: em 04/11 você disse \"não consigo mover a linha azul manualmente\" e respondeu \"Sim\" "
        "a \"o 'dividir esta' cortar onde você deixou\". Em 10/11: \"se mudou a ferramenta, muda em todos os "
        "lugares\". O botão da grade é a mesma ferramenta.",
        "O que muda no que já funciona, se for \"Sim\": só o \"dividir\" da grade. Na folha em que você não "
        "arrastou a linha, ele continua cortando onde o programa acha a lombada.",
        "Situação: só pergunta; nada foi mudado. Se for \"Sim\", entra na fila de consertos e volta para "
        "você testar.",
        "O que você escolhe: se o \"dividir\" da grade corta onde você deixou a linha, como o \"dividir esta\".",
        "(Para consulta: decisões D-609 e D-667.)",
    ]
    trocar_opcoes(p, [
        {"id": "sim", "nome": "Sim: a grade corta onde você deixou a linha (recomendo)",
         "texto": "Igual ao \"dividir esta\". É a faixa verde."},
        {"id": "nao", "nome": "Não: fica como hoje",
         "texto": "A grade sempre corta onde o programa acha a lombada. É a faixa laranja."},
    ])
    p["sugestao"] = "Sim: é defeito, e é o que você pediu em 04/11 e em 10/11."
    p["primeira_imagem"]["legenda"] = (
        "Gradus (cópia), folha 10 (páginas 18 e 19). Azul: a linha arrastada para 40%. Laranja (como é "
        "hoje): o \"dividir\" da grade corta no meio, onde o programa acha. Verde: o \"dividir esta\" corta "
        "onde você deixou a linha.")
    for e in p["exemplos"]:
        e["legenda"] = (e["legenda"].replace("na linha do MOTOR", "onde o PROGRAMA acha a lombada")
                        .replace("a do motor estava em 50%", "o programa tinha posto em 50%")
                        .replace("a do motor (em cima)", "a que o programa pôs (em cima)")
                        .replace(" (D-609)", ""))

    p = pergunta(doc, "rev-girar-grade")
    p["titulo"] = ("Grade \"Todas as páginas\", botão \"girar ¼\": deve deixar todas viradas do mesmo jeito, "
                   "como o painel?")
    p["explicacao"] = [
        "Do que se trata: as páginas podem ser giradas em dois lugares. No painel Propriedades (lado "
        "direito), com \"aplicar em: todas as páginas\". E na grade \"Todas as páginas\" (botão \"ver "
        "todas\", em cima da tira de páginas), com os botões \"girar ¼ ←\" e \"girar ¼ →\" para as páginas "
        "escolhidas.",
        "O que acontece hoje: o painel deixa todas viradas como a página da vez (você decidiu assim em 06/10). "
        "A grade gira cada página ¼ a partir de onde ela está. Página que já estava deitada fica de cabeça "
        "para baixo. É defeito: a mesma ferramenta faz duas coisas.",
        "Exemplo de verdade (Gradus Primus, cópia, folhas divididas): a página 19 já estava virada ¼ à "
        "direita, à mão. Pelo painel (página 18, \"todas as páginas\", ¼ à direita), todas deitaram como a "
        "18, inclusive a 19 (faixa verde). Pela grade (todas escolhidas, \"girar ¼ →\"), as outras deitaram "
        "e a 19 ficou de cabeça para baixo (faixa laranja).",
        "De onde veio: 06/10: \"Todas ficam viradas como a folha da vez\"; 05/11 você respondeu \"pode ser\" a "
        "que o mesmo valesse na tela \"ver todas\"; 10/11: \"se mudou a ferramenta, muda em todos os lugares\".",
        "O que muda no que já funciona, se for \"Sim\": na grade, as páginas escolhidas terminam todas na "
        "mesma posição, como no painel. Quem hoje usa a grade para girar cada página ¼ a partir de onde ela "
        "está perde esse jeito.",
        "Situação: só pergunta; nada foi mudado. Se for \"Sim\", entra na fila de consertos e volta para "
        "você testar.",
        "O que você escolhe: se o girar da grade faz como o painel.",
        "(Para consulta: decisões D-035, D-636 e D-667.)",
    ]
    trocar_opcoes(p, [
        {"id": "sim", "nome": "Sim: a grade faz como o painel (recomendo)",
         "texto": "As páginas escolhidas ficam todas viradas do mesmo jeito; a que já estava deitada não "
                  "vira de cabeça para baixo. É a faixa verde."},
        {"id": "nao", "nome": "Não: fica como hoje",
         "texto": "Na grade, cada página gira ¼ a partir de onde está. É a faixa laranja."},
    ])
    p["sugestao"] = "Sim: é defeito, e é o que você decidiu em 06/10, 05/11 e 10/11."
    p["primeira_imagem"]["legenda"] = (
        "Gradus (cópia), páginas divididas; a 19 já estava virada à mão. Azul: antes. Laranja (como é hoje): "
        "a grade gira cada uma ¼ e a 19 fica de cabeça para baixo. Verde: o painel deixa todas viradas como a 18.")
    for e in p["exemplos"]:
        e["legenda"] = e["legenda"].replace(" (D-035)", "")
    return doc


# ---------------------------------------------------------------------------------------------
# Aba acrescentei-27-10 (só três perguntas mudam)
# ---------------------------------------------------------------------------------------------

def acrescentei() -> dict:
    doc = ler("acrescentei-27-10")

    p = pergunta(doc, "b-abas-nomes")
    fixar(p, "samuel", "2026-11-06T21:36:15.177Z", "Ainda não entendi. No caso, isso é uma opção a mais do que a que temos hoje?")
    p["titulo"] = "Lado direito no jeito \"Abas no alto\": os nomes curtos das abas ficam assim?"
    p["explicacao"] = [
        "Do que se trata: o lado direito da área de trabalho tem os painéis Para revisar, Automático, "
        "Propriedades, Filtro da página e Histórico. No menu Ver > Lado direito você escolhe entre quatro "
        "jeitos de mostrá-los. O de fábrica é \"Ícones na borda\": desenhos sem nome. Um dos outros é \"Abas "
        "no alto\": cada painel vira uma aba com um nome curto.",
        "Sua dúvida: \"No caso, isso é uma opção a mais do que a que temos hoje?\" → Não. O jeito \"Abas no "
        "alto\" já existe hoje no programa (print). Os quatro jeitos são pedido seu, de 05/10: \"Quer os quatro "
        "jeitos no app, escolhendo dentro dele\". Nada novo entra. A pergunta é só sobre os nomes escritos nas abas.",
        "Como é hoje: as abas dizem \"Revisar\", \"Automático\", \"Propriedades\", \"Filtro\" e \"Histórico\". "
        "Embaixo delas, o nome inteiro do painel aberto (\"Para revisar\"). Esses nomes curtos foram escolhidos "
        "por um agente, a partir do desenho das abas que você viu no layout, sem perguntar a você.",
        "O que muda: só o que está escrito nas abas, e só para quem escolher \"Abas no alto\". O jeito de "
        "fábrica não muda.",
        "Situação: já está no programa (versão de teste).",
        "O que você escolhe: se os nomes curtos ficam, se as abas mostram o nome inteiro do painel, ou se "
        "vira uma pergunta de nomes com sugestões para cada aba.",
    ]
    trocar_opcoes(p, [
        {"id": "manter", "nome": "Ficam como estão (recomendo)",
         "texto": "Revisar · Automático · Propriedades · Filtro · Histórico, com o nome inteiro do painel embaixo."},
        {"id": "nomes-inteiros", "nome": "As abas com o nome inteiro do painel",
         "texto": "Para revisar · Automático · Propriedades · Filtro da página · Histórico. Antes de fazer, "
                  "o agente confere se cabe na janela do notebook do Kaique (1280 de largura)."},
        {"id": "revisar", "nome": "Levar à revisão dos nomes",
         "texto": "Vira uma pergunta na aba \"Revisão dos nomes\", com duas ou três sugestões para cada aba."},
        {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito."},
    ])
    p["sugestao"] = "Ficam como estão: o jeito de fábrica não usa esses nomes, e o nome inteiro aparece logo embaixo."
    p["primeira_imagem"] = {"src": "imagens/b-abas-nomes-resumo.png",
                            "legenda": "Gradus (cópia), versão de teste. O menu Ver > Lado direito já tem quatro "
                                       "jeitos. Azul: o de fábrica, ícones na borda, sem nome. Verde: \"Abas no "
                                       "alto\", com os nomes curtos (no círculo vermelho)."}
    p["exemplos"] = [{"src": e["src"], "legenda": "Jeito \"Abas no alto\" no Palatino (cópia), página 73: as "
                      "cinco abas com nome curto e, embaixo, \"Para revisar\" com o \"x\". O contorno vermelho "
                      "mostra onde olhar. Print de 28/10, versão de teste."} for e in p.get("exemplos", [])]

    p = pergunta(doc, "b-pdf-desatualizado")
    fixar(p, "samuel", "2026-11-06T21:29:57.774Z", "Ainda não entendi. Isso se aplica só se eu fizer alterações né?")
    p["titulo"] = ("Livro que já virou PDF e depois foi mudado: o programa deve dizer que o PDF ficou velho?")
    p["explicacao"] = [
        "Do que se trata: na tela dos livros (a primeira tela do programa), cada livro tem um cartão. "
        "Clicando nele, abre o livro, com uma barra no alto que diz em que pé ele está. Depois que você "
        "gera o PDF, os dois dizem \"pronto, PDF gerado\".",
        "Sua dúvida: \"Isso se aplica só se eu fizer alterações né?\" → Sim. Só quando você muda alguma "
        "página depois de gerar o PDF (filtro, corte, giro, Automático, desfazer...). Se só olhar as páginas, "
        "continua \"pronto, PDF gerado\".",
        "Como é hoje (Palatino, cópia, versão de teste): depois de mudar, o cartão e a barra voltam a dizer "
        "\"32 de 134 conferidas\" e \"Continuar\", como um livro que ainda está sendo feito. Nada diz que o "
        "PDF que já está na pasta ficou mais velho que o trabalho. Gerar o PDF de novo volta para \"pronto, PDF "
        "gerado\".",
        "É defeito? Não. É o conserto que você mandou fazer em 05/10 (\"pode mandar concertar\": antes, o "
        "cartão dizia \"PDF gerado\" mesmo depois de mudar). O conserto usou as duas frases que o cartão já "
        "tinha. A frase \"PDF desatualizado\" nunca foi pedida nem existe hoje.",
        "O que muda: com \"PDF desatualizado\", só a frase do cartão e da barra muda, e o botão \"abrir a "
        "pasta\" continua à vista. O PDF que sai não muda.",
        "O que você escolhe: o que o cartão diz depois de você mudar um livro que já virou PDF.",
        "(Para consulta: decisão D-309.)",
    ]
    trocar_opcoes(p, [
        {"id": "como-esta", "nome": "Como está: \"32 de 134 conferidas\" (recomendo)",
         "texto": "O livro volta a parecer \"em andamento\". Gerar o PDF de novo devolve o \"pronto, PDF gerado\". "
                  "É a faixa laranja."},
        {"id": "desatualizado", "nome": "Escrever \"PDF desatualizado\"",
         "texto": "O cartão e a barra diriam \"PDF desatualizado: gere de novo\", com \"continuar\" e também "
                  "\"abrir a pasta\". É coisa nova (a faixa verde, sem print porque ainda não existe)."},
        {"id": "nao-entendi", "nome": "Ainda não entendi", "texto": "Explique de outro jeito."},
    ])
    p["sugestao"] = "Como está: já não engana mais (não diz \"pronto\" depois de mudar), e nada novo entra."
    p["primeira_imagem"] = {"src": "imagens/b-pdf-desatualizado-resumo.png",
                            "legenda": "Palatino (cópia), versão de teste. Azul: logo depois de gerar o PDF, "
                                       "\"pronto, PDF gerado\". Laranja (como é hoje): depois de mudar uma página, "
                                       "\"32 de 134 conferidas\" e nada fala do PDF velho. Verde: a outra opção, "
                                       "que ainda não existe."}
    p["exemplos"] = []

    p = pergunta(doc, "v-capa-aviso")
    fixar(p, "samuel", "2026-11-13T23:11:53.827Z", "mas vai ter um botão para fazer isso antes do imprimir livros?")
    p["titulo"] = "Pares trocados (página ímpar à esquerda): quando o programa avisa?"
    p["explicacao"] = [
        "Do que se trata: na área de trabalho, o botão \"Duas lado a lado\" (barra de baixo) mostra as "
        "páginas em pares, como o livro aberto. Num livro de verdade, a página da direita é sempre ímpar. "
        "Alguns PDFs começam no meio da numeração, e aí os pares saem trocados: a ímpar fica à esquerda "
        "(La vida eterna, faixa azul).",
        "Sua dúvida: \"mas vai ter um botão para fazer isso antes do imprimir livros?\" → Sim. Em 09/11 você "
        "mandou fazer o botão de acertar os pares. Ele vai ficar no \"Duas lado a lado\", e você usa quando "
        "quiser, antes de \"Montar para imprimir\". Ainda não está feito: espera esta resposta sobre o aviso.",
        "E já hoje dá para acertar à mão (faixa verde): botão direito na miniatura da capa, na tira de baixo, "
        "\"adicionar página em branco depois\". Os pares andam uma página e a ímpar passa para a direita. Essa "
        "página em branco entra também no PDF e nos cadernos. Você testou essa função em 09/11 (\"pagina em "
        "branco funciona\").",
        "O que falta decidir: quando o programa avisa. Ele não sabe sozinho se os pares estão trocados, "
        "porque não lê o número impresso nas páginas. Por isso o aviso é uma pergunta para você olhar.",
        "Como outros programas fazem: o Acrobat tem, no modo de duas páginas, a escolha \"Mostrar a capa\" "
        "sozinha ou não, que anda os pares uma página. Ele também não avisa sozinho.",
        "O que você escolhe: em que momento o programa pergunta se os pares estão certos.",
        "(Para consulta: decisões D-693 e D-623.)",
    ]
    trocar_opcoes(p, [
        {"id": "montar", "nome": "Na hora de montar os cadernos (recomendo)",
         "texto": "Ao abrir \"Montar para imprimir\", uma vez por livro, só se você nunca olhou o livro no "
                  "\"Duas lado a lado\": o programa mostra os dois primeiros pares e pergunta \"As páginas da "
                  "direita são as ímpares, como no livro?\". Se não forem, o botão de acertar fica ali mesmo."},
        {"id": "abrir", "nome": "Ao abrir o \"Duas lado a lado\" pela primeira vez no livro",
         "texto": "A pergunta aparece antes, mas aparece também quando você só quer olhar as páginas."},
        {"id": "outro", "nome": "Outro jeito", "texto": "Escreva no comentário."},
    ])
    p["sugestao"] = "Na hora de montar os cadernos: é quando o erro faria diferença no livro impresso."
    p["primeira_imagem"] = {"src": "imagens/v-capa-aviso-resumo.png",
                            "legenda": "La vida eterna (cópia), dividido, \"Duas lado a lado\". Azul (como é "
                                       "hoje): a página de número ímpar impresso (7) fica à esquerda. Verde: botão "
                                       "direito na miniatura da capa, \"adicionar página em branco depois\": o 7 "
                                       "passa para a direita, como no livro."}
    p["exemplos"] = [{"src": "/_blob/805737af35e3356b8450dada0c0b097a",
                      "legenda": "O problema em mais pares: La vida eterna dividido, \"Duas lado a lado\". Nos "
                                 "pares 6-7, 8-9 e 10-11 do PDF, a página de número ímpar impresso (7, 9, 11) "
                                 "aparece à esquerda. Print de 13/11, versão de teste, cópia do livro."}]
    return doc


# ---------------------------------------------------------------------------------------------
# Aba perg-mover-rotulo
# ---------------------------------------------------------------------------------------------

def mover() -> dict:
    doc = ler("perg-mover-rotulo")
    doc["nome"] = "Pergunta: o Mover com o \"antes / depois\""
    p = pergunta(doc, "mover-rotulo-antes")
    fixar(p, "samuel", "2026-11-07T15:49:48.704Z",
          "Ainda não entendi. Isso ficou bem estranho né, acho que não deveria dar para ver o antes/depois "
          "enquanto se mexe na folha, no caso do mover.")
    fixar(p, "gerente", "2026-11-07T19:30:00Z",
          "Entendi assim: com o Mover, enquanto você arrasta a página, o \"antes / depois\" some e aparece só "
          "a página. Ao soltar, ele volta. Pode ser assim?")
    p["titulo"] = "Ferramenta Mover com o \"antes / depois\" ligado: o \"antes\" deve sumir?"
    p["explicacao"] = [
        "Do que se trata: o botão \"antes / depois\" (barra de baixo da área de trabalho) mostra a página como "
        "veio, à esquerda, e como vai sair, à direita. A ferramenta Mover (barra da esquerda) arrasta o que "
        "está impresso na folha e muda o tamanho dele.",
        "Como é hoje (Gradus, cópia, versão de teste; faixa azul): com os dois ligados, aparecem o antes e o "
        "depois, e o Mover mexe só no depois. Foi o que você aprovou em 04/11 (\"Ok, pode ser assim o antes e "
        "depois\"). O rótulo \"antes: Original\" fica no canto de cima. Não é defeito: é como foi feito.",
        "Seu comentário: \"acho que não deveria dar para ver o antes/depois enquanto se mexe na folha, no caso "
        "do mover\" → A pergunta antiga era só sobre o lugar do rótulo. O seu comentário pede outra coisa: que, "
        "no Mover, a tela mostre só a página (faixa verde). Por isso as opções mudaram.",
        "O que muda no que já funciona: as duas opções novas mudam o que você aprovou em 04/11, só no Mover. "
        "No Cortar e no Endireitar, o \"antes / depois\" continua como hoje. O botão \"antes / depois\" "
        "continua na barra de baixo e volta a valer ao trocar de ferramenta.",
        "Situação: está como na faixa azul. Nada foi mudado.",
        "O que você escolhe: o que a tela mostra quando o Mover está escolhido e o \"antes / depois\" ligado.",
        "(Para consulta: decisão D-612.)",
    ]
    trocar_opcoes(p, [
        {"id": "so-a-pagina", "nome": "Com o Mover, só a página (recomendo)",
         "texto": "Com o Mover escolhido, a tela mostra só a página que você mexe, mesmo com o \"antes / "
                  "depois\" ligado (faixa verde). Ao trocar de ferramenta, o antes / depois volta."},
        {"id": "some-ao-arrastar", "nome": "O \"antes\" some só enquanto você arrasta",
         "texto": "Enquanto arrasta ou puxa o canto, fica só a página; ao soltar o mouse, o antes volta. "
                  "A tela muda a cada arrasto."},
        {"id": "fica", "nome": "Como hoje",
         "texto": "Antes e depois juntos, o Mover mexe no depois (faixa azul). Nada muda."},
        {"id": "mudar", "nome": "Como hoje, só com o rótulo \"antes: Original\" em outro lugar",
         "texto": "Diga onde no comentário."},
    ])
    p["sugestao"] = "Com o Mover, só a página: é o que o seu comentário pede, e a tela não muda a cada arrasto."
    p["primeira_imagem"] = {"src": "imagens/mover-rotulo-antes-resumo.png",
                            "legenda": "Gradus (cópia), dividido, página 11, ferramenta Mover. Azul (como é "
                                       "hoje): com o \"antes / depois\" ligado, aparecem o antes e o depois. "
                                       "Verde: só a página que o Mover mexe."}
    p["exemplos"] = [{"src": "fotos/mover-lado/mover-antes-depois.png",
                      "legenda": "Print antigo (04/11) da mesma tela, com o conteúdo aumentado para 131%: o "
                                 "rótulo \"antes: Original\" fica em cima da parte da página que o Mover está "
                                 "mexendo (a parte vermelha vai ficar de fora da folha)."}]
    doc["resumo"]["paragrafos"] = [
        "Uma pergunta pequena sobre a ferramenta Mover, refeita a partir do seu comentário de 07/11.",
        "Enquanto você não responde, a tela fica como está hoje.",
    ]
    doc["resumo"]["titulo"] = "O Mover com o \"antes / depois\""
    return doc


if __name__ == "__main__":
    gravar("perg-revisao-codigo", revisao())
    gravar("acrescentei-27-10", acrescentei())
    gravar("perg-mover-rotulo", mover())
    print("ok")
