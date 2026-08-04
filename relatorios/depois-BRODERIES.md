# Linha de base do Editor de Impressao

Medido em 04/08/2026 as 01:16.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **1 livros**, 92 folhas, 92 paginas de saida.
- A qualidade de imagem foi medida a fundo em **7 paginas**, as mesmas em toda rodada.
- **5 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **667 MB** de memoria, contra o teto de 2048 MB.

## O que cada numero quer dizer

| Numero | O que e, na pratica |
|---|---|
| Espessura do traco | Grossura media da linha da letra, em pontinhos de tela (pixels). Se afina demais, some na impressao. |
| Vazios internos | Buraquinhos fechados dentro das letras: o miolo do **o**, do **e**, do **a**. Se o filtro engrossa demais, eles entopem e a letra vira bolha. Quanto mais sobrarem, melhor. |
| Nivel do fundo | Quao claro esta o papel, de 0 (preto) a 255 (branco). O alvo e 255: papel branco de verdade, sem o amarelado. |
| Ruido do fundo | O quanto o papel varia onde deveria ser liso. Quanto menor, mais limpo. |
| Transicao da borda | Largura da rampa entre a tinta e o papel, em pixels. **Este e o numero da queixa de letra pixelada.** De 1 a 2 e o certo; perto de zero a borda vira degrau de escada; acima de 3 a letra borra. |
| Nitidez | O quanto a imagem tem detalhe definido. Maior e mais nitido, mas exagero vira ruido. |

## Como cada filtro se comporta, na media do acervo

| Filtro | Espessura | Vazios | Fundo (255=branco) | Ruido | Transicao (px) | Nitidez | Tempo/pagina |
|---|---|---|---|---|---|---|---|
| Original | 218.92 | 1160 | 163.8 | 1.84 | 0.82 | 740 | 0.00s |
| Preto e branco | 11.42 | 3988 | 236.6 | 1.28 | 0.33 | 3837 | 1.04s |
| Melhorar | 16.67 | 4028 | 190.8 | 1.93 | 1.39 | 3097 | 1.52s |
| Mágico pro | 169.74 | 3994 | 187.4 | 2.10 | 0.81 | 3086 | 1.71s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.44 s | 10 s | sim |
| Primeiras miniaturas | 8.00 s | 5 s | NAO |
| Analisar 500 folhas (projecao) | 426 s | 180 s | NAO |
| Exportar 500 paginas a 300 DPI (projecao) | 550 s | 1200 s | sim |
| Pico de memoria | 667 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 12 MB | 92 | 92 | 78.4s | 5 |

## Paginas que sairam piores que o original

Sao **5** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Melhorar | o fundo escureceu: passou de 142 para 138 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Mágico pro | o fundo escureceu: passou de 142 para 127 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Melhorar | a borda das letras borrou: a rampa subiu de 0.91 para 3.55 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Mágico pro | o fundo escureceu: passou de 154 para 147 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Mágico pro | o fundo escureceu: passou de 156 para 148 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.5 |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Alinhamento duvidoso | 3 | Não consegui achar o alinhamento do texto direito. |
| Corte encostou no texto | 1 | O corte da borda pode ter pegado parte do texto. |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| POINTS d´ANCIENNES BRODERIES ANGLAISES | 1018x2591 | 69.8 mm | 16.0 mm | 0.014 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
