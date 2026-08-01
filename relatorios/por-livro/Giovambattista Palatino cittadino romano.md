# Giovambattista Palatino cittadino romano

- Arquivo de 9 MB
- 134 folhas no PDF, que viram 134 paginas de saida
- 7 paginas medidas a fundo
- 45 segundos para analisar o livro inteiro (333 milissegundos por folha)

## Paginas que sairam piores que o original

Sao 5 ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era.

| Pagina | Filtro | O que piorou |
|---|---|---|
| 1 | Mágico pro | o fundo escureceu: passou de 88 para 83 numa escala em que 255 e branco |
| 27 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.79 para 0.48 pixels |
| 53 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.90 para 0.62 pixels |
| 132 | Melhorar | o fundo escureceu: passou de 255 para 230 numa escala em que 255 e branco |
| 134 | Melhorar | o fundo ficou mais sujo: ruido subiu de 6.6 para 8.1 |

## Paginas marcadas em laranja

Laranja quer dizer *o programa nao teve certeza*. Nao e erro:
e um pedido de conferida.

| Aviso | Quantas | O que significa |
|---|---|---|
| Tem cor | 20 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 10 | Não consegui achar o alinhamento do texto direito. |
| Tamanho diferente | 2 | Esta folha tem tamanho diferente das outras. |
| Parece em branco | 1 | Esta página parece estar em branco. Quer apagar? |

## Observacoes do livro inteiro

- este livro tem uma página por folha, não duas

## As paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno
nao fecha direito na impressao.

- Menor pagina: 1074 x 1698 pontinhos
- Variacao de largura: 22.3 mm
- Variacao de altura: 64.3 mm
- Inclinacao que sobrou depois de endireitar: 0.071 grau na media, 0.100 no pior caso

## Como cada filtro se comportou

| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |
|---|---|---|---|---|---|
| Original | 127.04 | 1023 | 184.8 | 2.51 | 0.78 |
| Preto e branco | 6.12 | 458 | 254.5 | 0.00 | 0.00 |
| Melhorar | 7.14 | 1008 | 201.7 | 2.95 | 0.86 |
| Mágico pro | 5.47 | 617 | 205.8 | 1.96 | 0.56 |

> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os
> buraquinhos dentro das letras: quanto mais sobrarem, melhor.
> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e
> serrilhado.
