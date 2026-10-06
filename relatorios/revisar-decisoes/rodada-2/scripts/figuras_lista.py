"""As imagens da rodada 2. "tipo": "lado" = quadros soltos lado a lado
(figuras.lado_a_lado); sem tipo = o quadro grande da rodada 1 (figuras.figura).
caixa = a parte ampliada (x0, y0, x1, y1, em fracao da pagina)."""

from comum import TRABALHO

M = str(TRABALHO / "marcar")

FIGURAS = [
    # --- respostas as perguntas do Samuel ------------------------------------
    dict(tipo="lado", arquivo="resp-graduale222", quadros=[
        ("graduale_p222__inteira", "original", (0, 0, 1, 0.42), ["sumiu"],
         "Graduale 222: o que o jeito de fábrica apagou"),
        ("palatino_p076__inteira", "original", (0.06, 0.12, 0.50, 0.42), ["sumiu"],
         "Palatino 76: o que o jeito de fábrica apagou"),
    ], legendas=[
        "Em vermelho, o que o jeito de fábrica apagou e o Preto e branco de sempre imprime.",
        "No Graduale quase não há vermelho (a música ficou). No Palatino, o desenho da letra S inteiro.",
        "O critério novo olha isso: só vai para a lista a página em que o programa apagou um desenho.",
    ]),
    dict(tipo="lado", arquivo="resp-palatino010-so-texto", quadros=[
        ("palatino_p010__inteira", "original", (0.0, 0.0, 0.52, 0.36), [], "Original"),
        ("palatino_p010__inteira", "a", (0.0, 0.0, 0.52, 0.36), [], "Jeito de fábrica"),
        ("palatino_p010__inteira", "c", (0.0, 0.0, 0.52, 0.36), [], "Só o texto achado"),
    ], legendas=[
        "No jeito de fábrica a moldura fica (preta). No 'Só o texto achado' ela some inteira.",
    ]),
    dict(tipo="lado", arquivo="resp-matematica032", quadros=[
        ("matematica_p032__inteira", "original", (0.0, 0.55, 1.0, 1.0), [], "Original"),
        ("matematica_p032__inteira", "a", (0.0, 0.55, 1.0, 1.0), [], "Jeito de fábrica"),
        ("matematica_p032__inteira", "pb", (0.0, 0.55, 1.0, 1.0), [], "Preto e branco de sempre"),
    ], legendas=[
        "A faixa escura embaixo é o fundo do scanner, fora da folha. Sai igual nos dois jeitos.",
        "Quem deve tirá-la é o corte das bordas (item 2.13 do plano), não o Misto.",
    ]),
    dict(tipo="lado", arquivo="resp-horas014", quadros=[
        ("horas_p014__inteira", "original", (0.18, 0.07, 0.62, 0.36), [], "Original"),
        ("horas_p014__inteira", "pb", (0.18, 0.07, 0.62, 0.36), [], "Preto e branco (sem 'Só as letras')"),
        ("horas_p014__inteira", "a", (0.18, 0.07, 0.62, 0.36), [], "Com 'Só as letras' (jeito de fábrica)"),
    ], legendas=[
        "O aviso só existe com a caixinha 'Só as letras' marcada. Sem ela, a página nunca vai por este motivo.",
    ]),
    dict(tipo="lado", arquivo="resp-graduale588-marcar", quadros=[
        ("graduale_p588__inteira", "original", (0.0, 0.26, 0.42, 0.56), [], "Original"),
        ("graduale_p588__inteira", "a", (0.0, 0.26, 0.42, 0.56), [], "Hoje (Só as letras)"),
        ("graduale_p588__inteira", M + r"\graduale588-S-gravura__a__marcado.jpg",
         (0.0, 0.26, 0.42, 0.56), [], "Marcada como 'gravura ou foto'"),
    ], legendas=[
        "Na aba Marcar: 'gravura ou foto' e um retângulo em volta da letra. Com 'Só as letras', a letra fica colorida.",
        "Mas tudo o que está dentro do retângulo fica como no original, inclusive o papel amarelado e as pautas vermelhas.",
    ]),
    dict(tipo="lado", arquivo="resp-marial454-marcar", quadros=[
        ("marial_p454__inteira", "original", (0.0, 0.18, 0.5, 0.74), [], "Original"),
        ("marial_p454__inteira", "a", (0.0, 0.18, 0.5, 0.74), [], "Hoje (Só as letras)"),
        ("marial_p454__inteira", M + r"\marial454-remendo-tirar__a__marcado.jpg",
         (0.0, 0.18, 0.5, 0.74), [], "Remendo 'tirado' da gravura"),
    ], legendas=[
        "Já dá hoje, à mão: aba Marcar, 'gravura ou foto', botão 'tirar', e um retângulo sobre o remendo: ele vai para o branco.",
        "(Marcar como 'papel' não resolve no 'Só as letras': testei, o remendo continua marrom.)",
    ]),
    dict(arquivo="fecho-palatino010", base="palatino_p010__inteira", jeito="c",
         caixa=(0.0, 0.0, 0.52, 0.36), camadas=["sumiu"],
         legenda="em vermelho, o que o 'Só o texto achado' apagou: a moldura."),
    # --- o livro novo: Righetti, Historia de la Liturgia (girado e dividido) ---
    dict(arquivo="righetti052d", base="righetti_p052__direita", jeito="a",
         caixa=(0.05, 0.33, 0.95, 0.63), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou do mosaico (o Preto e branco de sempre imprime)."),
    dict(arquivo="righetti050d", base="righetti_p050__direita", jeito="a",
         caixa=(0.05, 0.37, 0.95, 0.70), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou do mosaico."),
    dict(arquivo="righetti006d", base="righetti_p006__direita", jeito="a",
         caixa=(0.0, 0.36, 0.9, 0.60), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou da foto do manuscrito (fundo e pedaços dos traços)."),
    dict(arquivo="righetti094d", base="righetti_p094__direita", jeito="a",
         caixa=(0.03, 0.28, 0.80, 0.75), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou: quase nada (o cálice fica inteiro)."),
    dict(arquivo="righetti054e", base="righetti_p054__esquerda", jeito="a",
         caixa=(0.25, 0.22, 1.0, 0.88), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou: pouca coisa, espalhada."),
    dict(arquivo="righetti062e", base="righetti_p062__esquerda", jeito="a",
         caixa=(0.25, 0.28, 1.0, 0.72), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou: pontinhos claros do fundo da foto."),
    dict(arquivo="righetti030e", base="righetti_p030__esquerda", jeito="a",
         caixa=(0.45, 0.24, 1.0, 0.80), camadas=["sumiu"],
         legenda="em vermelho, o que o jeito de fábrica apagou: pouca coisa."),
    dict(arquivo="righetti041e", base="righetti_p041__esquerda", jeito="a",
         caixa=(0.0, 0.0, 0.75, 0.62), camadas=[], cor_caixas="contou",
         caixas_olhar=[(0.0, 0.0, 1.0, 0.105), (0.0, 0.0, 0.29, 1.0)],
         legenda="em laranja, a faixa escura do scanner (em cima e à esquerda); o texto saiu bem."),
]
