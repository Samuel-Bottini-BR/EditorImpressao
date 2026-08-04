# Rhetorica Christiana -  Fray Diego Valadés

- Arquivo de 40 MB
- 446 folhas no PDF, que viram 446 paginas de saida
- 7 paginas medidas a fundo
- 246 segundos para analisar o livro inteiro (551 milissegundos por folha)

## Paginas que sairam piores que o original

Sao 3 ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era.

| Pagina | Filtro | O que piorou |
|---|---|---|
| 1 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 4.08 para 0.52 pixels |
| 446 | Melhorar | o fundo escureceu: passou de 208 para 182 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 0.4 para 4.5 |
| 446 | Mágico pro | o fundo escureceu: passou de 208 para 201 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 4.59 para 0.0 |

## Paginas marcadas em laranja

Laranja quer dizer *o programa nao teve certeza*. Nao e erro:
e um pedido de conferida.

| Aviso | Quantas | O que significa |
|---|---|---|
| Tem cor | 93 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 13 | Não consegui achar o alinhamento do texto direito. |
| Corte encostou no texto | 10 | O corte da borda pode ter pegado parte do texto. |
| Muito torta | 2 | Esta página estava bem torta. Veja se ficou certa. |
| Tamanho diferente | 2 | Esta folha tem tamanho diferente das outras. |

## Observacoes do livro inteiro

- este livro tem uma página por folha, não duas

## As paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno
nao fecha direito na impressao.

- Menor pagina: 1534 x 2236 pontinhos
- Variacao de largura: 32.1 mm
- Variacao de altura: 49.5 mm
- Inclinacao que sobrou depois de endireitar: 0.029 grau na media, 0.100 no pior caso

## Como cada filtro se comportou

| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |
|---|---|---|---|---|---|
| Original | 24.38 | 1157 | 210.4 | 0.88 | 1.52 |
| Preto e branco | 5.67 | 932 | 251.8 | 0.26 | 0.11 |
| Melhorar | 11.24 | 914 | 239.4 | 0.95 | 1.20 |
| Mágico pro | 7.94 | 1330 | 244.1 | 0.36 | 0.32 |

> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os
> buraquinhos dentro das letras: quanto mais sobrarem, melhor.
> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e
> serrilhado.
