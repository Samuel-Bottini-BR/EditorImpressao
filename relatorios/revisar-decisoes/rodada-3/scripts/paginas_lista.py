"""As 30 paginas da rodada 3: recorte ampliado, camada do "onde olhar",
legenda, explicacao e o veredito do meu olho no jeito de fabrica
(certa / leve / errada).
"""

# (base, livro e pagina, caixa, camadas, onde olhar, explicacao, veredito)
PAGINAS = [
    # --- Antiphonal 1547 (musica impressa, letras e pautas vermelhas, capitulares) ---
    ("antiphonal1547_p006__inteira", "Antiphonal 1547, p. 6", (0.0, 0.25, 1.0, 0.62), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: pedaços das pautas vermelhas.",
     "Olhe as pautas (linhas da música) que eram vermelhas: no jeito de fábrica saem com falhas; no "
     "Preto e branco de sempre, mais inteiras. A letra E grande ficou.",
     "leve"),
    ("antiphonal1547_p031__inteira", "Antiphonal 1547, p. 31", (0.0, 0.15, 1.0, 0.58), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: pedaços das pautas vermelhas.",
     "Olhe as pautas vermelhas: saem com falhas no jeito de fábrica. A letra O vermelha grande ficou "
     "(preta).",
     "leve"),
    ("antiphonal1547_p046__inteira", "Antiphonal 1547, p. 46", (0.0, 0.0, 1.0, 0.5), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: a letra T vermelha e as pautas vermelhas.",
     "Olhe a letra T vermelha grande à esquerda ('Tunc invoca'): no jeito de fábrica ela sumiu; no "
     "Preto e branco de sempre ela fica.",
     "errada"),
    ("antiphonal1547_p076__inteira", "Antiphonal 1547, p. 76", (0.0, 0.3, 1.0, 0.75), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: a letra L vermelha e pedaços das pautas.",
     "Olhe a letra L vermelha grande ('Loquere'): no jeito de fábrica ela sumiu; no Preto e branco de "
     "sempre ela fica.",
     "errada"),
    ("antiphonal1547_p192__inteira", "Antiphonal 1547, p. 192", (0.0, 0.0, 1.0, 0.5), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: quase nada.",
     "Página escrita à mão, com manchas de umidade: a música e o texto ficam, e as manchas vão para o "
     "branco.",
     "certa"),
    ("antiphonal1547_p252__inteira", "Antiphonal 1547, p. 252", (0.0, 0.4, 1.0, 0.8), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: as pautas vermelhas e letras vermelhas pequenas.",
     "Olhe as pautas vermelhas embaixo e as letras vermelhas do começo do hino: no jeito de fábrica as "
     "pautas saem com falhas.",
     "leve"),
    # --- Rariora Musei Besleriani (gravuras de animais e conchas, texto, quadros) ---
    ("rariora_p008__inteira", "Rariora, p. 8 (folha de rosto)", (0.0, 0.0, 1.0, 0.6), ["gravura"],
     "em verde, o que o programa achou como gravura: a página quase inteira.",
     "Olhe o papel: o programa achou que a página toda era gravura, e ela sai como no original, com o "
     "papel bege e a escrita do verso aparecendo. O Preto e branco de sempre sai cinza escuro. A regra "
     "nova não pega este caso (não há nada 'fora' da gravura).",
     "leve"),
    ("rariora_p099__inteira", "Rariora, p. 99", (0.0, 0.5, 1.0, 1.0), [],
     "nada a marcar: página só de texto.",
     "Página de texto com a letra D grande: tudo sai como no Preto e branco de sempre.",
     "certa"),
    ("rariora_p155__inteira", "Rariora, p. 155", (0.0, 0.0, 1.0, 1.0), ["gravura"],
     "em verde, o que o programa achou como gravura: os caranguejos.",
     "Olhe a gravura dos caranguejos: fica em tons, como no original, com o papel branco.",
     "certa"),
    ("rariora_p169__inteira", "Rariora, p. 169", (0.55, 0.30, 1.0, 0.65), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: o pontilhado da concha (Fig. 8).",
     "Olhe a concha oval à direita (Fig. 8): o programa não a achou como gravura e o jeito de fábrica "
     "apagou boa parte do pontilhado de dentro; o Preto e branco de sempre guarda. As outras figuras "
     "saem bem. Pela regra nova, esta página NÃO vai para 'Para revisar': o apagado ficou logo abaixo "
     "do limite (2,4% da tinta; o limite é 2,5%). Hoje ela vai, por outro motivo.",
     "errada"),
    ("rariora_p211__inteira", "Rariora, p. 211", (0.0, 0.0, 1.0, 1.0), ["gravura"],
     "em verde, o que o programa achou como gravura.",
     "Olhe as pedras e os fósseis: saem em tons, como no original, com o papel branco.",
     "certa"),
    ("rariora_p365__inteira", "Rariora, p. 365", (0.0, 0.15, 1.0, 0.75), ["contou"],
     "em laranja, as chaves do quadro: é a tinta que faz a página ir para 'Para revisar' hoje.",
     "Quadro com chaves: tudo fica, como no Preto e branco de sempre. Hoje esta página vai para "
     "'Para revisar' por causa das chaves.",
     "certa"),
    # --- Egenloff, Modelbuch 1527 (reedicao 1880): ornamentos, fundo do scanner em todas ---
    ("egenloff_p003__inteira", "Egenloff, p. 3 (folha de rosto)", (0.0, 0.0, 1.0, 1.0), ["beirada"],
     "em laranja, a faixa escura do scanner (e a tarja da biblioteca embaixo).",
     "Os ornamentos e o título saem bem. A faixa escura em volta está em TODAS as páginas deste livro, "
     "então vira um aviso só, no livro, e não manda cada página para 'Para revisar'.",
     "certa"),
    ("egenloff_p007__inteira", "Egenloff, p. 7", (0.0, 0.0, 1.0, 1.0), ["beirada"],
     "em laranja, a faixa escura do scanner.",
     "Olhe os dois ornamentos: saem inteiros. A faixa escura em volta vira aviso do livro.",
     "certa"),
    ("egenloff_p012__inteira", "Egenloff, p. 12 (verso em branco)", (0.0, 0.0, 1.0, 1.0), ["beirada"],
     "em laranja, a faixa escura do scanner.",
     "Página em branco (verso de uma prancha): sai branca, com a faixa do scanner em volta.",
     "certa"),
    ("egenloff_p047__inteira", "Egenloff, p. 47", (0.1, 0.1, 0.9, 0.8), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: quase nada.",
     "Olhe o ornamento de traço fino: sai inteiro, como no Preto e branco de sempre.",
     "certa"),
    ("egenloff_p121__inteira", "Egenloff, p. 121", (0.15, 0.1, 0.85, 0.75), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: quase nada.",
     "Olhe as quatro faixas de ornamento (com o grifo): saem inteiras.",
     "certa"),
    ("egenloff_p131__inteira", "Egenloff, p. 131", (0.15, 0.1, 0.85, 0.75), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: quase nada.",
     "Olhe o quadrado escuro de renda e as faixas: saem como no Preto e branco de sempre.",
     "certa"),
    # --- Gladstone Chaves de Melo, Novo Manual de Analise Sintatica (1954): moderno ---
    ("gladstone_p005__inteira", "Gladstone, p. 5", (0.0, 0.0, 1.0, 0.5), [],
     "nada a marcar: página só de texto.",
     "Página só de texto, moderna: sai igual ao Preto e branco de sempre.",
     "certa"),
    ("gladstone_p018__inteira", "Gladstone, p. 18", (0.0, 0.0, 1.0, 1.0), [],
     "nada a marcar: página quase em branco (título de parte).",
     "Página com uma linha só ('DA ORAÇÃO'): sai certa.",
     "certa"),
    ("gladstone_p055__inteira", "Gladstone, p. 55", (0.0, 0.0, 1.0, 0.6), [],
     "nada a marcar: texto com nota de rodapé.",
     "Página de texto com nota: sai igual ao Preto e branco de sempre.",
     "certa"),
    ("gladstone_p096__inteira", "Gladstone, p. 96", (0.0, 0.2, 1.0, 0.8), ["contou"],
     "em laranja, as chaves do quadro (tinta fora das linhas de texto).",
     "Olhe o quadro com chaves: as chaves ficam. Não vai para 'Para revisar', nem hoje nem pela "
     "regra nova.",
     "certa"),
    ("gladstone_p116__inteira", "Gladstone, p. 116", (0.0, 0.0, 1.0, 0.5), [],
     "nada a marcar: página só de texto.",
     "Página de texto: sai certa.",
     "certa"),
    ("gladstone_p136__inteira", "Gladstone, p. 136", (0.0, 0.0, 1.0, 0.5), [],
     "nada a marcar: página só de texto (negrito e itálico).",
     "Página de texto em negrito e itálico: sai certa.",
     "certa"),
    # --- Camoes, Historia de Portugal (seculo XIX): gravuras, capitulares, papel escuro ---
    ("camoes_p006__inteira", "Camões, p. 6", (0.0, 0.0, 1.0, 1.0), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: boa parte da estátua.",
     "Olhe a gravura do monumento: o programa não a reconheceu como gravura e o jeito de fábrica "
     "apagou boa parte dela (a estátua sai pela metade). O Preto e branco de sempre guarda mais.",
     "errada"),
    ("camoes_p009__inteira", "Camões, p. 9", (0.0, 0.1, 1.0, 0.6), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: a letra A ornamentada.",
     "Olhe a letra A grande ornamentada no começo do texto: no jeito de fábrica ela quase sumiu; no "
     "Preto e branco de sempre fica (manchada).",
     "errada"),
    ("camoes_p011__inteira", "Camões, p. 11", (0.0, 0.45, 1.0, 0.85), ["sumiu"],
     "em vermelho, o que o jeito de fábrica apagou: a letra ornamentada.",
     "Olhe a letra grande ornamentada do começo ('Tratando'): no jeito de fábrica ficou só um "
     "contorno; no Preto e branco de sempre fica.",
     "errada"),
    ("camoes_p027__inteira", "Camões, p. 27", (0.0, 0.0, 1.0, 0.5), ["contou"],
     "em laranja, a tinta que faz a página ir para 'Para revisar' hoje.",
     "Página de texto com nota: sai certa. Hoje vai para 'Para revisar' por causa da sombra da beirada "
     "e dos fios.",
     "certa"),
    ("camoes_p066__inteira", "Camões, p. 66", (0.0, 0.0, 1.0, 0.5), ["contou"],
     "em laranja, a tinta que faz a página ir para 'Para revisar' hoje.",
     "Página de versos: sai certa. Hoje vai para 'Para revisar' por causa da sombra da beirada.",
     "certa"),
    ("camoes_p104__inteira", "Camões, p. 104 (contracapa)", (0.0, 0.0, 1.0, 1.0), ["gravura"],
     "em verde, o que o programa achou como gravura: o retrato, e também uma faixa da beirada e da moldura.",
     "Olhe o retrato: fica em tons, com o papel branco. Mas a zona de gravura (verde) escorre pela "
     "beirada esquerda e de baixo, e ali as dobras do papel saem em marrom. É isso que faz a regra nova "
     "mandar a página (sinal 'figura passou da beirada da gravura achada').",
     "leve"),
]

FIGURAS_PAGINAS = [
    dict(arquivo="p-" + b.split("__")[0].replace("_p", "-"), base=b, jeito="a", caixa=cx,
         camadas=cam, legenda=leg)
    for (b, _n, cx, cam, leg, _e, _v) in PAGINAS
]
