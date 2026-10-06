"""Monta ../rodada-2-perguntas.json (rodada 2 das decisoes do "Para revisar").

Le <TRABALHO>/sinais-rodada2.json (sinais.py) para as paginas do livro novo
(Righetti) e o veredito do meu olho em VEREDITO_RIGHETTI (abaixo).
Campos que a pagina do claude.ai nao mostra: hoje, criterio_novo,
veredito_agente (para a analise depois).

Uso: python perguntas.py
"""
import json
from pathlib import Path

import comum
from criterio import faixa_no_livro, vai_para_a_lista

PASTA = Path(__file__).resolve().parents[1]
SINAIS = json.loads((comum.TRABALHO / "sinais-rodada2.json").read_text(encoding="utf-8"))
P = "Rodada 2"

ENTENDI = [
    {"id": "entendi", "nome": "Entendi", "texto": "Ficou claro.", "imgs": []},
    {"id": "nao-entendi", "nome": "Não entendi", "texto": "Explique de outro jeito (diga no comentário o que ficou confuso).", "imgs": []},
]

# Paginas do livro novo: (id, base, nome, explicacao do que se ve, onde olhar, veredito do meu olho)
from righetti_lista import RIGHETTI_PERGUNTAS  # noqa: E402


def cartao(pid, ordem, parte, pergunta, explicacao, imgs, opcoes, **extra):
    q = {"id": f"rv2-{pid}", "ordem": ordem, "parte": parte, "pergunta": pergunta,
         "explicacao": explicacao, "exemplos": [{"src": f"img/{a}.jpg", "legenda": l} for a, l in imgs],
         "opcoes": opcoes}
    q.update(extra)
    return q


def main() -> None:
    perguntas = []

    def add(*a, **k):
        perguntas.append(cartao(a[0], len(perguntas) + 1, *a[1:], **k))

    # 1. o resumo do criterio
    add("criterio", f"{P} · o critério que saiu das suas respostas",
        "Este é o critério que saiu das suas respostas. Fica assim?",
        "No jeito de fábrica ('Guardar a tinta forte'), a página vai para 'Para revisar' quando: "
        "(1) o programa apagou parte de um desenho que não reconheceu como figura (a letra S do Palatino 76); "
        "(2) uma figura passou da beirada da gravura achada, ou uma mancha virou 'gravura' (Marial 454, Antiphon 260); "
        "(3) sobrou uma faixa escura encostada na beirada da página (o fundo do scanner da Matemática 32); se essa faixa "
        "aparece em quase todas as páginas do livro (70% ou mais), ela vira UM aviso no livro, e não manda cada página. "
        "Moldura, música ou letra grande que sai em preto e branco, igual ao Preto e branco de sempre, NÃO manda "
        "mais a página para a lista. Com esta regra, as 16 páginas da rodada 1 saem exatamente como você respondeu "
        "(tabela na imagem).",
        [("criterio-tabela", "As 16 páginas da rodada 1: o que você respondeu, o que o programa faz hoje e com o critério novo.")],
        [{"id": "sim", "nome": "Sim, fica assim", "texto": "Pode usar este critério como padrão de fábrica.", "imgs": []},
         {"id": "quase", "nome": "Quase: quero mudar", "texto": "Diga no comentário o que mudar.", "imgs": []},
         {"id": "nao", "nome": "Não", "texto": "Não é isso que eu quero (diga no comentário por quê).", "imgs": []}])

    # 2. respostas as perguntas dele
    R = f"{P} · respostas às suas perguntas"
    add("resp-graduale222", R,
        "Graduale 222: é um caso isolado? Não ir para a lista pode afetar outros livros?",
        "Não afeta. O critério novo não olha se a página tem música: olha se o programa APAGOU algum desenho. "
        "No Graduale a música fica inteira (no jeito de fábrica ela sai preta), então nada foi apagado e a página "
        "não precisa ir. Num livro sem música vale a mesma coisa: se o programa apagar a letra grande, a moldura ou "
        "o desenho, a página vai; se não apagar, não vai. Na imagem: em vermelho, o que foi apagado.",
        [("resp-graduale222", "Graduale 222 (quase nada apagado) e Palatino 76 (a letra S apagada).")], ENTENDI)
    add("resp-horas014", R,
        "Horas 14: a página só vai se eu tiver marcado a opção que deixa as figuras fora do preto e branco?",
        "Sim. Este aviso só existe quando a caixinha 'Só as letras' do Preto e branco está marcada (é ela que "
        "deixa gravuras e molduras como no original e passa só as letras para preto e branco). Sem ela, a página "
        "nunca vai para a lista por este motivo. E com o critério novo a Horas 14 também não vai, mesmo com a caixinha "
        "marcada, porque nada foi apagado: a moldura sai preta, igual ao Preto e branco de sempre. (Conferido no "
        "código: core/pipeline.py, o aviso só é posto pelo 'Só as letras'.)",
        [("resp-horas014", "Horas 14: sem 'Só as letras' e com 'Só as letras'.")], ENTENDI)
    add("resp-marial454", R,
        "Marial 454: o programa deveria mostrar onde ele achou 'gravura', para eu clicar e apagar.",
        "Esse pedido já está anotado na Lista de espera do plano (05/10, 'Mostrar as áreas que o programa achou "
        "sozinho', para a Fase 2, item 2.18, junto com o desenho da tela). Hoje já dá para consertar à mão: na aba "
        "Marcar, escolher 'gravura ou foto', o botão 'tirar' e desenhar um retângulo sobre o remendo; ele deixa de "
        "ser gravura e vai para o branco. Testei pelo caminho do programa: a imagem mostra o resultado.",
        [("resp-marial454-marcar", "Marial 454: hoje, e com o remendo 'tirado' da gravura na aba Marcar.")], ENTENDI)
    add("resp-graduale588", R,
        "Graduale 588: se eu quiser deixar a letra S colorida, como figura, consigo?",
        "Consegue, hoje. Na aba Marcar: escolher 'gravura ou foto' e desenhar um retângulo em volta da letra. Com "
        "'Só as letras' marcada, a letra sai colorida como no original. Mas, no teste, tudo o que ficou dentro do "
        "retângulo saiu como no original, inclusive o papel amarelado e as pautas vermelhas em volta da letra; "
        "por isso o retângulo deve ficar bem justo na letra. Sem 'Só as letras', o Preto e branco transforma a "
        "gravura em desenho preto e branco; aí é preciso 'só neste pedaço' com o filtro Original. Testei pelo "
        "caminho do programa: a imagem mostra o resultado.",
        [("resp-graduale588-marcar", "Graduale 588: hoje e com a letra marcada como 'gravura ou foto'.")], ENTENDI)
    add("resp-matematica032", R,
        "Matemática 32: a faixa escura embaixo deveria sair branca.",
        "Concordo, e ela entra no critério novo (item 3: faixa escura encostada na beirada). Mas quem deve tirar a "
        "faixa é o corte das bordas, não o 'Só as letras': ela sai igual no Preto e branco de sempre. Isso é o item "
        "2.13 do plano ('Detectar a página dentro da borda preta do scanner'), e a Matemática já está na lista de "
        "livros de teste da borda preta. Até lá, a página vai para a lista para alguém cortar à mão (ou, se o livro "
        "inteiro tiver a faixa, um aviso só no livro).",
        [("resp-matematica032", "Matemática 32: a faixa sai igual nos dois jeitos.")], ENTENDI)

    # 3. o "So o texto achado"
    S = f"{P} · o jeito 'Só o texto achado'"
    add("so-texto-palatino010", S,
        "Palatino 10: no 'Só o texto achado', a página deveria vir para a lista. E o aviso uma vez no livro?",
        "Na rodada 1 você escolheu 'avisar uma vez no livro, não página por página'. No Palatino 10 você disse que, "
        "pedindo só texto, a página 'teria que vir, pois selecionou algo que não é texto'. As duas coisas podem valer "
        "juntas. Qual você quer?",
        [("resp-palatino010-so-texto", "Palatino 10: a moldura fica no jeito de fábrica e some no 'Só o texto achado'.")],
        [{"id": "os-dois", "nome": "Os dois", "texto": "Aviso uma vez no livro E a página vai para a lista quando some algo grande (moldura, capitular, música, desenho).", "imgs": []},
         {"id": "so-livro", "nome": "Só o aviso no livro", "texto": "Nenhuma página vai sozinha para a lista; o aviso do livro basta.", "imgs": []},
         {"id": "so-paginas", "nome": "Só página por página", "texto": "Sem aviso no livro; cada página em que some algo vai para a lista.", "imgs": []}])
    add("so-texto-aviso", S,
        "O aviso do 'Só o texto achado' pode ser este?",
        "Proposta de texto, mostrado uma vez quando você escolhe 'Só o texto achado' (na tela 'O que fazer' ou na "
        "aba Filtro) e guardado nas observações do livro: \"Neste jeito, só fica o texto que eu achei. Tudo o que não "
        "é texto nem gravura vai para o branco: letra grande, moldura, música, números da margem, tabelas e desenhos "
        "que eu não reconheci. Confira o livro antes de imprimir.\"",
        [("fecho-palatino010", "Exemplo: no Palatino 10 a moldura some.")],
        [{"id": "fica", "nome": "Fica assim", "texto": "O texto está bom.", "imgs": []},
         {"id": "mudar", "nome": "Quero mudar o texto", "texto": "Escreva no comentário como prefere.", "imgs": []},
         {"id": "nao-precisa", "nome": "Não precisa de aviso", "texto": "Quem escolhe esse jeito já sabe o que ele faz.", "imgs": []}])

    # 4. as paginas do livro novo
    L = f"{P} · um livro novo (Righetti, História da Liturgia)"
    fl = faixa_no_livro([v for k, v in SINAIS.items() if k.startswith("righetti")])
    for pid, base, nome, img, leg, expl in RIGHETTI_PERGUNTAS:
        s = SINAIS[base]
        vai = vai_para_a_lista(s, fl)
        frase = "VAI para a lista" if vai else "NÃO vai para a lista"
        add(pid, L,
            f"{nome}: pelo critério novo, esta página {frase.lower()}. Você concorda?",
            expl + f" (Hoje: {'vai' if s['aviso_hoje'] else 'não vai'} para a lista.)",
            [(img, f"{nome}. {leg}")],
            [{"id": "concordo", "nome": "Concordo", "texto": f"Está certo: a página {frase.lower()}.", "imgs": []},
             {"id": "nao-concordo", "nome": "Não concordo", "texto": "Diga no comentário por quê.", "imgs": []}],
            hoje=bool(s["aviso_hoje"]), criterio_novo=bool(vai), veredito_agente=RIGHETTI_VEREDITO[pid])

    destino = PASTA / "rodada-2-perguntas.json"
    destino.write_text(json.dumps(perguntas, ensure_ascii=False, indent=1), encoding="utf-8")
    for q in perguntas:
        print(q["ordem"], q["id"], q.get("hoje"), q.get("criterio_novo"), q.get("veredito_agente"))


from righetti_lista import RIGHETTI_VEREDITO  # noqa: E402

if __name__ == "__main__":
    main()
