# Rhetorica Christiana -  Fray Diego Valadés

- Arquivo de 40 MB
- 446 folhas no PDF, que viram 446 paginas de saida
- 7 paginas medidas a fundo
- 192 segundos para analisar o livro inteiro (430 milissegundos por folha)

## Paginas que sairam piores que o original

Sao 3 ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era.

| Pagina | Filtro | O que piorou |
|---|---|---|
| 1 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 4.08 para 0.55 pixels |
| 446 | Melhorar | o fundo escureceu: passou de 205 para 176 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 0.4 para 4.8 |
| 446 | Mágico pro | o fundo escureceu: passou de 205 para 198 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 4.43 para 0.0 |

## Paginas marcadas em laranja

Laranja quer dizer *o programa nao teve certeza*. Nao e erro:
e um pedido de conferida.

| Aviso | Quantas | O que significa |
|---|---|---|
| Tem cor | 93 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 13 | Não consegui achar o alinhamento do texto direito. |
| Muito torta | 2 | Esta página estava bem torta. Veja se ficou certa. |
| Tamanho diferente | 2 | Esta folha tem tamanho diferente das outras. |

## Observacoes do livro inteiro

- este livro tem uma página por folha, não duas

## As paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno
nao fecha direito na impressao.

- Menor pagina: 1427 x 2348 pontinhos
- Variacao de largura: 41.1 mm
- Variacao de altura: 40.0 mm
- Inclinacao que sobrou depois de endireitar: 0.071 grau na media, 0.100 no pior caso

## Como cada filtro se comportou

| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |
|---|---|---|---|---|---|
| Original | 24.94 | 1133 | 210.5 | 0.82 | 1.51 |
| Preto e branco | 5.27 | 1245 | 254.9 | 0.00 | 0.00 |
| Melhorar | 11.75 | 962 | 232.9 | 1.51 | 1.28 |
| Mágico pro | 8.26 | 1652 | 241.6 | 0.23 | 0.33 |

> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os
> buraquinhos dentro das letras: quanto mais sobrarem, melhor.
> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e
> serrilhado.
