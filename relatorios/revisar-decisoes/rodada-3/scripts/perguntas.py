"""Monta ../rodada-3-perguntas.json (rodada 3 das decisoes do "Para revisar").

Campos que a pagina do claude.ai nao mostra: hoje, regra_nova,
veredito_agente (para a analise depois).

Uso: python perguntas.py
"""
import json
from pathlib import Path

import comum
from criterio import faixa_no_livro, motivos, vai_para_a_lista
from paginas_lista import FIGURAS_PAGINAS, PAGINAS

PASTA = Path(__file__).resolve().parents[1]
SINAIS = json.loads((comum.TRABALHO / "sinais-rodada2.json").read_text(encoding="utf-8"))
P = "Rodada 3"

SEGUIR = [
    {"id": "seguir", "nome": "Entendi, pode seguir", "texto": "Concordo com o caminho.", "imgs": []},
    {"id": "nao-entendi", "nome": "Não entendi", "texto": "Explique de outro jeito (diga no comentário o que ficou confuso).", "imgs": []},
    {"id": "outro-jeito", "nome": "Quero de outro jeito", "texto": "Diga no comentário como prefere.", "imgs": []},
]
MOTIVO = {"desenho apagado": "o programa apagou parte de um desenho",
          "figura além da gravura achada": "uma figura passou da beirada da gravura achada",
          "faixa escura na beirada": "sobrou uma faixa escura na beirada"}


def cartao(perguntas, pid, parte, pergunta, explicacao, imgs, opcoes, **extra):
    q = {"id": f"rv3-{pid}", "ordem": len(perguntas) + 1, "parte": parte, "pergunta": pergunta,
         "explicacao": explicacao,
         "exemplos": [{"src": f"img/{a}.jpg", "legenda": l} for a, l in imgs], "opcoes": opcoes}
    q.update(extra)
    perguntas.append(q)


def main() -> None:
    q: list = []
    C = f"{P} · como o programa vai resolver"

    cartao(q, "para-revisar", C,
           "Antes de tudo: o que é 'Para revisar'?",
           "'Para revisar' é o painel no alto, à direita, da tela de conferir. Nele aparecem as páginas que o "
           "programa acha que alguém deve olhar antes de imprimir, com o motivo; clicar leva até a página. "
           "Quando dissemos 'vai para a lista', era isto: a página aparece em 'Para revisar'. O Kaique olha, "
           "conserta se precisar e marca 'está bom assim'.",
           [("tela-para-revisar", "A tela de conferir; à direita, em laranja, o painel 'Para revisar'.")],
           [{"id": "entendi", "nome": "Entendi", "texto": "Ficou claro.", "imgs": []},
            {"id": "nao-entendi", "nome": "Não entendi", "texto": "Explique de outro jeito.", "imgs": []}])

    cartao(q, "conserto-desenho", C,
           "Erro 1, desenho claro apagado (letra grande, desenho de traço fino): como vai ser resolvido?",
           "O programa vai deixar de apagar. Um conserto já foi feito e está em conferência: quando os traços "
           "claros estão juntos de um traço escuro (a moldura da letra, o contorno do desenho), eles ficam, "
           "como no Preto e branco de sempre. Nas 59 páginas do estudo, 13 melhoraram (Palatino 76, 67, 66, "
           "Siebmacher 7, Rhetorica 129...), 42 saíram idênticas e 2 pioraram de leve (voltaram linhas finas "
           "da beirada). Custa no máximo 0,18 s por página. Depois dele, quase nada mais é apagado nessas "
           "páginas, então elas também deixam de ir para 'Para revisar'. Se ainda sobrar alguma, ela vai para "
           "'Para revisar', e o Kaique pode marcar o desenho à mão na aba Marcar como 'gravura ou foto'.",
           [("conserto-desenho-apagado", "Palatino 76 e Siebmacher 7: como sai hoje e com o conserto.")],
           SEGUIR)

    cartao(q, "conserto-gravura", C,
           "Erro 2, mancha que vira 'gravura' ou figura que passa da gravura achada: como vai ser resolvido?",
           "Hoje já dá à mão: na aba Marcar, 'gravura ou foto', botão 'tirar', e um retângulo sobre a mancha; "
           "ela vai para o branco (foi o que fizemos no Marial 454). Para a figura maior que a zona, o contrário: "
           "'gravura ou foto' com 'somar' em volta do pedaço que faltou. O que está planejado (Lista de espera, "
           "Fase 2, item 2.18, e o seu pedido P11b): o programa MOSTRAR as áreas que achou sozinho, para você "
           "clicar numa delas e apagar, deixar branco ou pintar. Até lá, a página vai para 'Para revisar'.",
           [("marial454-tirar", "Marial 454: hoje, e com o remendo 'tirado' da gravura na aba Marcar.")],
           SEGUIR)

    cartao(q, "conserto-faixa", C,
           "Erro 3, faixa escura do scanner: como vai ser resolvido?",
           "Quem resolve é o corte das bordas, não o 'Só as letras': a faixa sai igual no Preto e branco de "
           "sempre. Está no plano como item 2.13, 'achar a página dentro da borda preta do scanner' (sua "
           "decisão G7: uma opção, desligada de fábrica). Até lá: se a faixa está em quase todas as páginas "
           "(70% ou mais), aparece um aviso só, no livro; se está em poucas, essas páginas vão para "
           "'Para revisar', e o Kaique corta à mão na aba Bordas.",
           [("faixa-matematica032", "Matemática 32: a faixa sai igual nos dois jeitos."),
            ("faixa-righetti041e", "Righetti: a faixa em todas as páginas vira um aviso só, no livro.")],
           SEGUIR)

    cartao(q, "conserto-graduale588", C,
           "Graduale 588 (a letra colorida): o que daria um resultado bom?",
           "Você disse que o resultado de hoje (marcar como 'gravura ou foto') não é bom: o retângulo inteiro "
           "fica como no original, com o papel amarelado. O que daria certo é um tipo de zona que você já "
           "decidiu em 05/10 (P11): 'Tinta com a cor original, papel branco'. A letra fica azul e vermelha e o "
           "papel em volta vai a branco. A imagem da direita é uma SIMULAÇÃO, feita com a conta que o programa "
           "já usa para molduras douradas. Ressalva: as notas dentro do retângulo também ficam com a cor delas "
           "(marrom); o retângulo precisa ficar justo na letra. Esse tipo de zona ainda não existe na aba Marcar: "
           "é trabalho da Fase 2.",
           [("graduale588-proposta", "Graduale 588: original, o que dá hoje e a proposta (simulação).")],
           SEGUIR)

    cartao(q, "conserto-so-texto", C,
           "Erro 4, o que some no 'Só o texto achado': como vai ser resolvido?",
           "Nesse jeito, apagar o que não é texto é o próprio objetivo; o risco é apagar o que você queria "
           "guardar. O conserto, página por página, é do Kaique: trocar a página para 'Guardar a tinta forte' "
           "(aba Filtro) ou marcar na aba Marcar a moldura ou a letra como 'gravura ou foto'. O programa ajuda "
           "com o aviso do livro e mandando para 'Para revisar' as páginas em que sumiu algo grande (próxima "
           "pergunta).",
           [("so-texto-graduale222", "Graduale 222: no 'Só o texto achado' a música some.")],
           SEGUIR)

    A = f"{P} · o aviso do 'Só o texto achado'"
    cartao(q, "aviso-so-texto", A,
           "O aviso do 'Só o texto achado': quando, onde e por quê. Fica assim?",
           "Quando: só quando você escolhe 'Só o texto achado'. Onde: aparece uma vez, numa caixa, na hora em "
           "que você escolhe, e fica escrito nas observações do livro; além disso, as páginas em que sumiu algo "
           "grande vão para 'Para revisar' (você escolheu 'os dois'). Por quê: esse jeito apaga tudo fora das "
           "linhas de texto, e nas 59 páginas testadas estragou 43. O aviso não aparece em cada página.",
           [("aviso-so-texto", "Como vai funcionar (desenho da proposta) e o exemplo do Palatino 10.")],
           SEGUIR)

    # as 30 paginas
    livros = {}
    for (base, *_r) in PAGINAS:
        livros.setdefault(base.split("_p")[0], []).append(SINAIS[base])
    faixa = {l: faixa_no_livro(v) for l, v in livros.items()}
    NOMES = {"antiphonal1547": "Antiphonal 1547 (música impressa, vermelho e preto)",
             "rariora": "Rariora Musei Besleriani (gravuras de animais e conchas)",
             "egenloff": "Egenloff, Modelbuch 1527 (ornamentos; fundo do scanner em todas)",
             "gladstone": "Gladstone, Manual de Análise Sintática 1954 (livro moderno)",
             "camoes": "Camões, A Historia de Portugal (séc. XIX; gravuras e letras ornamentadas)"}
    figs = {f["base"]: f["arquivo"] for f in FIGURAS_PAGINAS}
    for (base, nome, _cx, _cam, leg, expl, vered) in PAGINAS:
        livro = base.split("_p")[0]
        s = SINAIS[base]
        fl = faixa[livro]
        vai = vai_para_a_lista(s, fl)
        frase = "vai" if vai else "não vai"
        por = "; ".join(MOTIVO[m] for m in motivos(s, fl))
        porque = (f" Pela regra nova ela vai porque {por}." if vai else
                  " Pela regra nova ela não vai: nada importante foi apagado e nenhuma figura passou da gravura.")
        if fl and s.get("beirada_a", 0) >= 0.03:
            porque += " (A faixa do scanner vira aviso do livro, não manda a página.)"
        cartao(q, figs[base].replace("p-", "pag-"), f"{P} · 30 páginas de 5 livros novos · {NOMES[livro]}",
               f"{nome}: pela regra nova, esta página {frase.upper()} para 'Para revisar'. Você concorda?",
               expl + porque + (" Hoje ela vai." if s["aviso_hoje"] else " Hoje ela não vai."),
               [(figs[base], f"{nome}. Onde olhar: {leg}")],
               [{"id": "concordo", "nome": "Concordo", "texto": f"Está certo: ela {frase} para 'Para revisar'.", "imgs": []},
                {"id": "nao-concordo", "nome": "Não concordo", "texto": "Diga no comentário por quê.", "imgs": []},
                {"id": "nao-sei", "nome": "Não sei", "texto": "Preciso ver de outro jeito.", "imgs": []}],
               hoje=bool(s["aviso_hoje"]), regra_nova=bool(vai), veredito_agente=vered)

    (PASTA / "rodada-3-perguntas.json").write_text(json.dumps(q, ensure_ascii=False, indent=1),
                                                   encoding="utf-8")
    vai = sum(1 for x in q if x.get("regra_nova"))
    pag = sum(1 for x in q if "regra_nova" in x)
    hoje = sum(1 for x in q if x.get("hoje"))
    print("perguntas", len(q), "paginas", pag, "vao", vai, "nao vao", pag - vai, "hoje vao", hoje)
    for x in q:
        if "regra_nova" in x:
            print(x["ordem"], x["id"], "hoje", int(x["hoje"]), "nova", int(x["regra_nova"]), x["veredito_agente"])


if __name__ == "__main__":
    main()
