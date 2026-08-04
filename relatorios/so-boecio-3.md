# Linha de base do Editor de Impressao

Medido em 04/08/2026 as 00:23.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **1 livros**, 50 folhas, 50 paginas de saida.
- A qualidade de imagem foi medida a fundo em **7 paginas**, as mesmas em toda rodada.
- **11 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **467 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 4.98 | 722 | 190.7 | 6.33 | 0.86 | 850 | 0.00s |
| Preto e branco | 4.71 | 175 | 254.3 | 0.00 | 0.01 | 10083 | 0.07s |
| Melhorar | 4.97 | 953 | 230.1 | 3.81 | 0.65 | 2141 | 0.42s |
| Mágico pro | 4.71 | 1092 | 228.5 | 3.22 | 0.60 | 2444 | 0.47s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.47 s | 10 s | sim |
| Primeiras miniaturas | 0.03 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 28 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 56 s | 1200 s | sim |
| Pico de memoria | 467 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Sobre a Consolação da Filosofia - Severino B | 4 MB | 50 | 50 | 2.8s | 11 |

## Paginas que sairam piores que o original

Sao **11** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Sobre a Consolação da Filosofia -  | 1 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.5 |
| Sobre a Consolação da Filosofia -  | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.6 |
| Sobre a Consolação da Filosofia -  | 9 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.65 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.58 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.53 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.57 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.52 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.56 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.51 pixels |
| Sobre a Consolação da Filosofia -  | 50 | Melhorar | o fundo escureceu: passou de 161 para 159 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 3.8 para 9.1 |
| Sobre a Consolação da Filosofia -  | 50 | Mágico pro | o fundo escureceu: passou de 161 para 150 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.6 |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Corte encostou no texto | 3 | O corte da borda pode ter pegado parte do texto. |
| Alinhamento duvidoso | 2 | Não consegui achar o alinhamento do texto direito. |
| Tem cor | 1 | Esta página tem cor - o preto e branco vai perder a ilustração. |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Sobre a Consolação da Filosofia - Seve | 833x1399 | 20.1 mm | 12.9 mm | 0.071 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
