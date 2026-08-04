# Giovambattista Palatino cittadino romano

- Arquivo de 9 MB
- 134 folhas no PDF, que viram 134 paginas de saida
- 7 paginas medidas a fundo
- 84 segundos para analisar o livro inteiro (627 milissegundos por folha)

## Paginas que sairam piores que o original

Sao 6 ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era.

| Pagina | Filtro | O que piorou |
|---|---|---|
| 1 | Mágico pro | o fundo escureceu: passou de 81 para 76 numa escala em que 255 e branco |
| 27 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.76 para 0.42 pixels |
| 27 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.76 para 0.42 pixels |
| 53 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.87 para 0.48 pixels |
| 53 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.87 para 0.48 pixels |
| 132 | Melhorar | o fundo escureceu: passou de 255 para 225 numa escala em que 255 e branco |

## Paginas marcadas em laranja

Laranja quer dizer *o programa nao teve certeza*. Nao e erro:
e um pedido de conferida.

| Aviso | Quantas | O que significa |
|---|---|---|
| Tem cor | 20 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 10 | Não consegui achar o alinhamento do texto direito. |
| Tamanho diferente | 2 | Esta folha tem tamanho diferente das outras. |
| Corte encostou no texto | 1 | O corte da borda pode ter pegado parte do texto. |
| Parece em branco | 1 | Esta página parece estar em branco. Quer apagar? |

## Observacoes do livro inteiro

- este livro tem uma página por folha, não duas

## As paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno
nao fecha direito na impressao.

- Menor pagina: 1229 x 1805 pontinhos
- Variacao de largura: 34.4 mm
- Variacao de altura: 55.3 mm
- Inclinacao que sobrou depois de endireitar: 0.057 grau na media, 0.100 no pior caso

## Como cada filtro se comportou

| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |
|---|---|---|---|---|---|
| Original | 167.35 | 1086 | 183.0 | 2.64 | 0.79 |
| Preto e branco | 6.66 | 821 | 232.6 | 1.11 | 0.19 |
| Melhorar | 7.08 | 1160 | 204.7 | 2.10 | 0.68 |
| Mágico pro | 6.27 | 862 | 207.6 | 1.90 | 0.61 |

> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os
> buraquinhos dentro das letras: quanto mais sobrarem, melhor.
> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e
> serrilhado.
