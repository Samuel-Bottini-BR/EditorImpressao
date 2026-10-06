"""Monta ../rodada-1-perguntas.json (rodada 1 das decisoes do "Para revisar").

hoje / opcao1 / veredito_agente: tirados de
relatorios/revisar-criterios-2026-10-06/dados/sinais-e-vereditos.json
(opcao1 = apagado_junto >= 2% ou apagado_a >= 2,5% ou vazou_da_gravura >= 10%,
como no gerar_relatorio.py do estudo). A pagina do claude.ai nao mostra esses
tres campos: servem para comparar depois com as respostas do Samuel.
A rodada de 06/10 (rodar.py desta pasta) deu a mesma "tinta forte fora do texto"
e o mesmo aviso de hoje do estudo nas 17 paginas rodadas.

Uso: python perguntas.py
"""
import json
from pathlib import Path

PASTA = Path(__file__).resolve().parents[1]
ESTUDO = PASTA.parents[1] / "revisar-criterios-2026-10-06" / "dados" / "sinais-e-vereditos.json"
SINAIS = json.loads(ESTUDO.read_text(encoding="utf-8"))
PARTE = "Rodada 1 · página por página"
VERED = {"ok": "certa", "leve": "leve", "errada": "errada"}

OPCOES = [
    {"id": "sim", "nome": "Sim, deveria ir",
     "texto": "Quero que esta página apareça na lista 'Para revisar', para alguém olhar antes de imprimir.",
     "imgs": []},
    {"id": "nao", "nome": "Não precisa",
     "texto": "Do jeito que saiu, pode imprimir; não precisa ir para a lista.", "imgs": []},
    {"id": "marca", "nome": "Só uma marca discreta",
     "texto": "Não vai para a lista, mas a página ganha um aviso pequeno, para quem quiser olhar.",
     "imgs": []},
]

# (id, base no estudo, livro e pagina, imagem, legenda da imagem, explicacao)
PAGINAS = [
    ("palatino076", "palatino_p076__inteira", "Palatino, p. 76", "palatino076",
     "A letra S grande do alto da página.",
     "Olhe a letra S grande no alto, à esquerda. No jeito de fábrica sobraram só a moldura dela e "
     "um arco; no Preto e branco de sempre o desenho fica."),
    ("graduale222", "graduale_p222__inteira", "Graduale, p. 222", "graduale222",
     "A música do alto da página.",
     "Olhe as notas e as pautas. No jeito de fábrica a música sai preta, como no Preto e branco de "
     "sempre; ela conta como 'tinta fora do texto', e é isso que manda a página para a lista hoje."),
    ("marial454", "marial_p454__inteira", "Marial, p. 454", "marial454",
     "O meio da página, com as duas manchas.",
     "Olhe a mancha marrom à esquerda (um remendo de papel) e a faixa marrom à direita (a mancha do "
     "verso). O programa achou que eram gravuras e elas saem impressas em cor; no Preto e branco de "
     "sempre o remendo também sai, em cinza."),
    ("horas014", "horas_p014__inteira", "Livro de Horas, p. 14", "horas014",
     "O canto de cima da tabela.",
     "Olhe a moldura dourada da tabela. O programa não a reconheceu como desenho: ela sai preta e "
     "grossa, igual ao Preto e branco de sempre."),
    ("palatino067", "palatino_p067__inteira", "Palatino, p. 67", "palatino067",
     "A letra M grande no meio da página.",
     "Olhe dentro do quadrado da letra M. No jeito de fábrica o fundo desenhado (folhas e figuras) "
     "sumiu quase todo; no Preto e branco de sempre ele fica."),
    ("matematica032", "matematica_p032__inteira", "Matemática para vencer, p. 32", "matematica032",
     "A parte de baixo da página.",
     "Olhe a faixa escura embaixo: é a beirada do scanner, e sai igual no Preto e branco de sempre. "
     "O texto saiu bem; é a faixa que manda a página para a lista hoje."),
    ("siebmacher007", "siebmacher_p007__esquerda", "Siebmacher, folha 7 (página da esquerda)",
     "siebmacher007", "O canto de baixo da moldura de ornamentos.",
     "Olhe a moldura de ornamentos, principalmente a faixa de baixo. Ela sai em preto e branco, mas "
     "o jeito de fábrica apagou pedaços que o Preto e branco de sempre guarda."),
    ("antiphon260", "antiphon_p260__inteira", "Antiphonarium, p. 260", "antiphon260",
     "A música à direita da iluminura.",
     "Olhe as notas à direita da iluminura. As que ficam na zona que o programa achou como gravura "
     "saem marrons e desbotadas, como no original; as de fora saem pretas. No Preto e branco de "
     "sempre acontece o mesmo."),
    ("boecio007", "boecio_p007__inteira", "Boécio, p. 7", "boecio007",
     "O alto da página, com a letra Q.",
     "Olhe a letra Q grande e os sinais pequenos (- - v v) em cima do poema. No jeito de fábrica "
     "eles ficaram, como no Preto e branco de sempre."),
    ("palatino066", "palatino_p066__inteira", "Palatino, p. 66", "palatino066",
     "As letras enfeitadas do pé da página.",
     "Olhe a letra enfeitada 'M.' no pé da página. No jeito de fábrica ela ficou pela metade; no "
     "Preto e branco de sempre fica inteira."),
    ("graduale588", "graduale_p588__inteira", "Graduale, p. 588", "graduale588",
     "A letra S azul grande.",
     "Olhe a letra S azul grande. O programa não a reconheceu como desenho: ela sai preta, igual ao "
     "Preto e branco de sempre; a música e o texto saem bem."),
    ("pesel021", "pesel_p021__inteira", "Points (Pesel), p. 21", "pesel021",
     "A parte de baixo, com a legenda.",
     "Olhe a legenda miúda embaixo, impressa no papel escuro. Ela vira duas tarjas pretas, no jeito "
     "de fábrica e também no Preto e branco de sempre; no jeito de fábrica o papel escuro em volta "
     "ainda sai marrom."),
    ("palatino010", "palatino_p010__inteira", "Palatino, p. 10", "palatino010",
     "O canto de cima, com a moldura.",
     "Olhe a moldura de fios em volta do texto. No jeito de fábrica ela sai preta, igual ao Preto e "
     "branco de sempre; é ela que manda a página para a lista hoje."),
    ("ljs47-103", "ljs47_p103__inteira", "Manuscrito ljs47, p. 103", "ljs47-103",
     "O desenho de linhas e arcos.",
     "Olhe o desenho de linhas e arcos vermelhos embaixo. No jeito de fábrica as linhas compridas "
     "ficaram picotadas; no Preto e branco de sempre ficam mais inteiras, mas também falhadas, "
     "porque o traço é muito claro."),
    ("horas175", "horas_p175__inteira", "Livro de Horas, p. 175", "horas175",
     "A letra S colorida do começo do parágrafo.",
     "Olhe a letra S colorida (azul e vermelha) no começo do parágrafo. O programa não a reconheceu "
     "como desenho e ela sai como um bloco preto, igual ao Preto e branco de sempre."),
    ("rhetorica034", "rhetorica_p034__inteira", "Rhetorica Christiana, p. 34", "rhetorica034",
     "A gravura do anjo.",
     "Olhe a gravura do anjo. O programa a reconheceu como gravura e ela fica como no original, "
     "enquanto o Preto e branco de sempre a deixa manchada."),
]


def main() -> None:
    saida = []
    for ordem, (pid, base, nome, img, leg, expl) in enumerate(PAGINAS, start=1):
        s = SINAIS[base]
        opcao1 = bool(s["apagado_junto"] >= 0.02 or s["apagado_a"] >= 0.025
                      or s["vazou_da_gravura"] >= 0.10)
        hoje = bool(s["aviso_hoje"])
        expl = expl + (" (Hoje: vai para a lista.)" if hoje else " (Hoje: não vai para a lista.)")
        saida.append({
            "id": f"rv1-{pid}", "ordem": ordem, "parte": PARTE,
            "pergunta": f"{nome}: esta página deveria ir para 'Para revisar'?",
            "explicacao": expl,
            "exemplos": [{"src": f"img/{img}.jpg", "legenda": f"{nome}. {leg}"}],
            "opcoes": OPCOES,
            "hoje": hoje, "opcao1": opcao1, "veredito_agente": VERED[s["veredito_a"]],
        })
    saida.append({
        "id": "rv1-fecho-so-texto", "ordem": len(saida) + 1,
        "parte": "Rodada 1 · fechamento: o jeito 'Só o texto achado'",
        "pergunta": "No jeito 'Só o texto achado', toda página com algo além de texto corrido deve "
                    "ir para 'Para revisar'?",
        "explicacao": "Esse jeito apaga tudo o que não é linha de texto. Nos exemplos, olhe o "
                      "vermelho: a música do Graduale some, a letra Q do Boécio some, os números da "
                      "margem da Escola somem (nas 59 páginas testadas, ele estragou 43).",
        "exemplos": [
            {"src": "img/fecho-graduale222.jpg", "legenda": "Graduale, p. 222: a música some."},
            {"src": "img/fecho-boecio007.jpg",
             "legenda": "Boécio, p. 7: a letra Q e os sinais de métrica somem."},
            {"src": "img/fecho-escola197.jpg",
             "legenda": "Na escola de Jesus, p. 197: os números da margem somem."},
        ],
        "opcoes": [
            {"id": "todas", "nome": "Sim, todas",
             "texto": "Toda página em que esse jeito apagar alguma coisa vai para a lista.", "imgs": []},
            {"id": "grande", "nome": "Só quando sumir algo grande",
             "texto": "Vai para a lista quando some capitular, música, moldura ou desenho; pedacinho "
                      "pequeno, não.", "imgs": []},
            {"id": "livro", "nome": "Avisar uma vez no livro, não página por página",
             "texto": "Ao escolher esse jeito, o programa avisa uma vez que ele apaga o que não é "
                      "texto; as páginas não vão uma a uma para a lista.", "imgs": []},
        ],
        "hoje": None, "opcao1": None, "veredito_agente": "errada",
    })
    destino = PASTA / "rodada-1-perguntas.json"
    destino.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    for q in saida:
        print(q["ordem"], q["id"], q["hoje"], q["opcao1"], q["veredito_agente"])


if __name__ == "__main__":
    main()
