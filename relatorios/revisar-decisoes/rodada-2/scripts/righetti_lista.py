"""As paginas do livro novo (Righetti, Historia de la Liturgia, vol. 2, parte 2)
que entram na rodada 2, e o veredito do meu olho no jeito de fabrica
(certa / leve / errada, como no estudo). Folha do PDF girada 1/4 a esquerda
e dividida em duas (comum._girar_e_dividir)."""

# (id, base, nome, imagem, legenda, explicacao)
RIGHETTI_PERGUNTAS = [
    ("righetti052d", "righetti_p052__direita", "Righetti, folha 52, página da direita (p. 365)", "righetti052d",
     "O mosaico de Ravena.",
     "Olhe o meio do mosaico (as figuras debaixo do arco). O programa achou só pedaços do mosaico como "
     "gravura; o resto saiu pelo 'Só as letras' e muita parte clara foi apagada: o meio ficou ralo, com buracos "
     "brancos. O Preto e branco de sempre guarda mais."),
    ("righetti050d", "righetti_p050__direita", "Righetti, folha 50, página da direita (p. 361)", "righetti050d",
     "O mosaico de Abel e Melquisedec.",
     "Olhe o céu e as figuras de cima do mosaico: no jeito de fábrica ficaram manchas brancas onde o Preto e "
     "branco de sempre tem desenho."),
    ("righetti006d", "righetti_p006__direita", "Righetti, folha 6, página da direita (p. 273)", "righetti006d",
     "A foto do manuscrito.",
     "Olhe o fundo da foto do manuscrito: o jeito de fábrica apagou o fundo cinza (o que é bom) e alguns "
     "tracinhos claros das letras pequenas de cima; as letras grandes ficam."),
    ("righetti094d", "righetti_p094__direita", "Righetti, folha 94, página da direita (p. 449)", "righetti094d",
     "O cálice de Antioquia.",
     "Olhe o cálice: o desenho fica inteiro, e o fundo pontilhado em volta vai para o branco."),
    ("righetti054e", "righetti_p054__esquerda", "Righetti, folha 54, página da esquerda (p. 368)", "righetti054e",
     "O mosaico da abóbada.",
     "Olhe o mosaico da abóbada: o jeito de fábrica sai parecido com o Preto e branco de sempre; o pouco que "
     "foi apagado está espalhado, em pontinhos."),
    ("righetti062e", "righetti_p062__esquerda", "Righetti, folha 62, página da esquerda (p. 384)", "righetti062e",
     "A pintura das catacumbas.",
     "Olhe o fundo da pintura, entre as duas figuras: o jeito de fábrica tirou os pontinhos claros do fundo e "
     "manteve as figuras em tom de cinza; o Preto e branco de sempre sai mais sujo."),
    ("righetti030e", "righetti_p030__esquerda", "Righetti, folha 30, página da esquerda (p. 320)", "righetti030e",
     "O 'VD' ornamentado do manuscrito.",
     "Olhe o ornamento e as letras do manuscrito: saem como no Preto e branco de sempre, com o fundo mais limpo."),
    ("righetti041e", "righetti_p041__esquerda", "Righetti, folha 41, página da esquerda (p. 342)", "righetti041e",
     "A página de texto, com a faixa do scanner.",
     "Olhe a faixa escura em cima e à esquerda: é o fundo do scanner. Ela aparece em TODAS as páginas deste "
     "livro, então pelo critério novo vira um aviso só, no livro ('este livro tem a borda escura do scanner em "
     "quase todas as páginas'), e não manda cada página para a lista. O texto saiu bem."),
]

RIGHETTI_VEREDITO = {
    "righetti052d": "errada", "righetti050d": "errada", "righetti006d": "leve",
    "righetti094d": "certa", "righetti054e": "certa", "righetti062e": "certa",
    "righetti030e": "certa", "righetti041e": "certa",
}
