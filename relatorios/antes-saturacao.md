# Linha de base antes de mexer na saturacao

Medido em 04/08/2026 as 15:14.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **9 livros**, 2903 folhas, 3037 paginas de saida.
- A qualidade de imagem foi medida a fundo em **63 paginas**, as mesmas em toda rodada.
- **25 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **1418 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 32.58 | 1763 | 189.0 | 2.42 | 1.17 | 733 | 0.00s |
| Preto e branco | 12.30 | 2386 | 237.3 | 0.89 | 0.57 | 6704 | 1.57s |
| Melhorar | 26.86 | 4187 | 220.1 | 1.52 | 1.13 | 1724 | 3.14s |
| Mágico pro | 34.09 | 3974 | 219.0 | 1.48 | 1.04 | 1794 | 3.50s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 2.45 s | 10 s | sim |
| Primeiras miniaturas | 0.38 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 170 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 307 s | 1200 s | sim |
| Pico de memoria | 1418 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino romano | 9 MB | 134 | 134 | 45.6s | 1 |
| Graduale - Saeculum XIV | 271 MB | 750 | 750 | 216.2s | 6 |
| Livro de Horas - Luís XIV | 106 MB | 191 | 191 | 58.9s | 0 |
| Marial de sermoens - Frei Balthasar Paez. (1 | 205 MB | 907 | 907 | 142.9s | 0 |
| Na escola de Jesus - Catecismo explicado com | 48 MB | 199 | 199 | 31.1s | 3 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 12 MB | 92 | 92 | 72.0s | 4 |
| Rhetorica Christiana -  Fray Diego Valadés | 40 MB | 446 | 446 | 230.4s | 1 |
| Schön Neues Modell Buch - Johann Siebmacher | 11 MB | 134 | 268 | 59.9s | 0 |
| Sobre a Consolação da Filosofia - Severino B | 4 MB | 50 | 50 | 2.7s | 10 |

## Paginas que sairam piores que o original

Sao **25** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Giovambattista Palatino cittadino  | 1 | Mágico pro | o fundo escureceu: passou de 81 para 76 numa escala em que 255 e branco |
| Graduale - Saeculum XIV | 1 | Melhorar | o fundo escureceu: passou de 47 para 44 numa escala em que 255 e branco |
| Graduale - Saeculum XIV | 1 | Mágico pro | o fundo escureceu: passou de 47 para 42 numa escala em que 255 e branco |
| Graduale - Saeculum XIV | 126 | Preto e branco | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| Graduale - Saeculum XIV | 126 | Melhorar | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| Graduale - Saeculum XIV | 126 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| Graduale - Saeculum XIV | 750 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.9 para 7.2 |
| Na escola de Jesus - Catecismo exp | 199 | Preto e branco | as letras entupiram: sobraram 142 vazios internos de 243 (42% a menos) |
| Na escola de Jesus - Catecismo exp | 199 | Melhorar | as letras entupiram: sobraram 142 vazios internos de 243 (42% a menos) |
| Na escola de Jesus - Catecismo exp | 199 | Mágico pro | as letras entupiram: sobraram 146 vazios internos de 243 (40% a menos) |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Mágico pro | o fundo escureceu: passou de 91 para 82 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.91 para 0.66 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Mágico pro | o fundo escureceu: passou de 154 para 147 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.91 para 0.6 |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Mágico pro | o fundo escureceu: passou de 156 para 148 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.5 |
| Rhetorica Christiana -  Fray Diego | 446 | Mágico pro | o fundo escureceu: passou de 202 para 199 numa escala em que 255 e branco |
| Sobre a Consolação da Filosofia -  | 1 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.5 para 14.8 |
| Sobre a Consolação da Filosofia -  | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.5 para 14.0 |
| Sobre a Consolação da Filosofia -  | 9 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.65 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.56 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.50 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.55 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.48 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.55 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.49 pixels |
| Sobre a Consolação da Filosofia -  | 50 | Mágico pro | o fundo escureceu: passou de 146 para 138 numa escala em que 255 e branco |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Tem cor | 392 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 349 | Não consegui achar o alinhamento do texto direito. |
| Corte encostou no texto | 43 | O corte da borda pode ter pegado parte do texto. |
| Tamanho diferente | 22 | Esta folha tem tamanho diferente das outras. |
| Muito torta | 4 | Esta página estava bem torta. Veja se ficou certa. |
| Parece em branco | 1 | Esta página parece estar em branco. Quer apagar? |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino roma | 1229x1805 | 34.4 mm | 55.3 mm | 0.057 | 0.100 |
| Graduale - Saeculum XIV | 2630x4537 | 265.6 mm | 250.9 mm | 0.071 | 0.200 |
| Livro de Horas - Luís XIV | 2952x5527 | 111.3 mm | 563.9 mm | 0.086 | 0.100 |
| Marial de sermoens - Frei Balthasar Pa | 1046x3802 | 183.0 mm | 8.7 mm | 0.071 | 0.100 |
| Na escola de Jesus - Catecismo explica | 1894x2896 | 26.2 mm | 18.5 mm | 0.100 | 0.300 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES | 1018x2591 | 69.8 mm | 16.0 mm | 0.014 | 0.100 |
| Rhetorica Christiana -  Fray Diego Val | 1534x2236 | 32.1 mm | 49.5 mm | 0.029 | 0.100 |
| Schön Neues Modell Buch - Johann Siebm | 594x1179 | 39.3 mm | 12.8 mm | 0.043 | 0.100 |
| Sobre a Consolação da Filosofia - Seve | 833x1399 | 20.1 mm | 12.9 mm | 0.071 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
