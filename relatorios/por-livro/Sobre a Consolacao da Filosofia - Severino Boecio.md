# Sobre a Consolação da Filosofia - Severino Boécio

- Arquivo de 4 MB
- 50 folhas no PDF, que viram 50 paginas de saida
- 7 paginas medidas a fundo
- 3 segundos para analisar o livro inteiro (62 milissegundos por folha)

## Paginas que sairam piores que o original

Sao 12 ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era.

| Pagina | Filtro | O que piorou |
|---|---|---|
| 1 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.5 |
| 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.6 |
| 9 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.45 pixels |
| 9 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.43 pixels |
| 17 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.39 pixels |
| 17 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.38 pixels |
| 33 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.41 pixels |
| 33 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.38 pixels |
| 41 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.40 pixels |
| 41 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.38 pixels |
| 50 | Melhorar | o fundo escureceu: passou de 161 para 159 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 3.8 para 9.1 |
| 50 | Mágico pro | o fundo escureceu: passou de 161 para 150 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.6 |

## Paginas marcadas em laranja

Laranja quer dizer *o programa nao teve certeza*. Nao e erro:
e um pedido de conferida.

| Aviso | Quantas | O que significa |
|---|---|---|
| Corte encostou no texto | 3 | O corte da borda pode ter pegado parte do texto. |
| Alinhamento duvidoso | 2 | Não consegui achar o alinhamento do texto direito. |
| Tem cor | 1 | Esta página tem cor - o preto e branco vai perder a ilustração. |

## Observacoes do livro inteiro

- este livro tem uma página por folha, não duas

## As paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno
nao fecha direito na impressao.

- Menor pagina: 833 x 1399 pontinhos
- Variacao de largura: 20.1 mm
- Variacao de altura: 12.9 mm
- Inclinacao que sobrou depois de endireitar: 0.071 grau na media, 0.100 no pior caso

## Como cada filtro se comportou

| Filtro | Espessura | Vazios | Fundo | Ruido | Transicao |
|---|---|---|---|---|---|
| Original | 4.98 | 722 | 190.7 | 6.33 | 0.86 |
| Preto e branco | 4.71 | 175 | 254.3 | 0.00 | 0.01 |
| Melhorar | 4.66 | 941 | 230.3 | 3.81 | 0.51 |
| Mágico pro | 4.43 | 1080 | 228.7 | 3.21 | 0.49 |

> **Fundo** perto de 255 e papel branco de verdade. **Vazios** sao os
> buraquinhos dentro das letras: quanto mais sobrarem, melhor.
> **Transicao** entre 1 e 2 e borda saudavel; perto de zero e
> serrilhado.
