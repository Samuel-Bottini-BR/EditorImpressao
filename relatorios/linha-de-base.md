# Linha de base - 03/08/2026

Medido em 03/08/2026 as 23:57.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **9 livros**, 2903 folhas, 3037 paginas de saida.
- A qualidade de imagem foi medida a fundo em **63 paginas**, as mesmas em toda rodada.
- **53 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **1363 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 60.20 | 2383 | 191.4 | 2.42 | 1.37 | 733 | 0.01s |
| Preto e branco | 14.15 | 1723 | 238.1 | 0.95 | 0.60 | 6447 | 1.39s |
| Melhorar | 25.01 | 2195 | 220.9 | 1.82 | 1.16 | 2066 | 2.64s |
| Mágico pro | 34.27 | 2550 | 220.9 | 1.73 | 0.97 | 2083 | 3.23s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 3.03 s | 10 s | sim |
| Primeiras miniaturas | 0.46 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 220 s | 180 s | NAO |
| Exportar 500 paginas a 300 DPI (projecao) | 404 s | 1200 s | sim |
| Pico de memoria | 1363 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino romano | 9 MB | 134 | 134 | 84.0s | 6 |
| Graduale - Saeculum XIV | 271 MB | 750 | 750 | 354.5s | 13 |
| Livro de Horas - Luís XIV | 106 MB | 191 | 191 | 93.4s | 0 |
| Marial de sermoens - Frei Balthasar Paez. (1 | 205 MB | 907 | 907 | 154.2s | 13 |
| Na escola de Jesus - Catecismo explicado com | 48 MB | 199 | 199 | 34.2s | 0 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 12 MB | 92 | 92 | 82.6s | 6 |
| Rhetorica Christiana -  Fray Diego Valadés | 40 MB | 446 | 446 | 245.6s | 3 |
| Schön Neues Modell Buch - Johann Siebmacher | 11 MB | 134 | 268 | 69.7s | 0 |
| Sobre a Consolação da Filosofia - Severino B | 4 MB | 50 | 50 | 3.1s | 12 |

## Paginas que sairam piores que o original

Sao **53** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Giovambattista Palatino cittadino  | 1 | Mágico pro | o fundo escureceu: passou de 81 para 76 numa escala em que 255 e branco |
| Giovambattista Palatino cittadino  | 27 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.76 para 0.42 pixels |
| Giovambattista Palatino cittadino  | 27 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.76 para 0.42 pixels |
| Giovambattista Palatino cittadino  | 53 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.87 para 0.48 pixels |
| Giovambattista Palatino cittadino  | 53 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.87 para 0.48 pixels |
| Giovambattista Palatino cittadino  | 132 | Melhorar | o fundo escureceu: passou de 255 para 225 numa escala em que 255 e branco |
| Graduale - Saeculum XIV | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.3 para 6.5 |
| Graduale - Saeculum XIV | 126 | Preto e branco | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 126 | Melhorar | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 126 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 251 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 2.38 para 0.68 pixels |
| Graduale - Saeculum XIV | 251 | Mágico pro | as letras entupiram: sobraram 65 vazios internos de 91 (29% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 2.38 para 0.66 pix |
| Graduale - Saeculum XIV | 376 | Melhorar | as letras entupiram: sobraram 102 vazios internos de 142 (28% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 2.21 para 0.54 p |
| Graduale - Saeculum XIV | 376 | Mágico pro | as letras entupiram: sobraram 93 vazios internos de 142 (35% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 2.21 para 0.52 pi |
| Graduale - Saeculum XIV | 501 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 2.12 para 0.62 pixels |
| Graduale - Saeculum XIV | 501 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 2.12 para 0.60 pixels |
| Graduale - Saeculum XIV | 626 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 2.08 para 0.69 pixels |
| Graduale - Saeculum XIV | 626 | Mágico pro | as letras entupiram: sobraram 154 vazios internos de 224 (31% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 2.08 para 0.66 p |
| Graduale - Saeculum XIV | 750 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.9 para 7.8 |
| Marial de sermoens - Frei Balthasa | 1 | Preto e branco | as letras entupiram: sobraram 47 vazios internos de 71 (34% a menos) |
| Marial de sermoens - Frei Balthasa | 1 | Melhorar | as letras entupiram: sobraram 47 vazios internos de 71 (34% a menos) |
| Marial de sermoens - Frei Balthasa | 1 | Mágico pro | as letras entupiram: sobraram 47 vazios internos de 71 (34% a menos) |
| Marial de sermoens - Frei Balthasa | 152 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.49 para 0.61 pixels |
| Marial de sermoens - Frei Balthasa | 152 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.49 para 0.61 pixels |
| Marial de sermoens - Frei Balthasa | 303 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.44 para 0.65 pixels |
| Marial de sermoens - Frei Balthasa | 303 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.44 para 0.65 pixels |
| Marial de sermoens - Frei Balthasa | 454 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.23 para 0.47 pixels |
| Marial de sermoens - Frei Balthasa | 454 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.23 para 0.47 pixels |
| Marial de sermoens - Frei Balthasa | 605 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.49 para 0.58 pixels |
| Marial de sermoens - Frei Balthasa | 605 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 1.49 para 0.57 pixels |
| Marial de sermoens - Frei Balthasa | 756 | Melhorar | as letras entupiram: sobraram 872 vazios internos de 1442 (40% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 1.43 para 0.55  |
| Marial de sermoens - Frei Balthasa | 756 | Mágico pro | as letras entupiram: sobraram 867 vazios internos de 1442 (40% a menos); a borda das letras virou degrau (serrilhado): a rampa caiu de 1.43 para 0.54  |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Melhorar | o fundo escureceu: passou de 142 para 138 numa escala em que 255 e branco; a borda das letras borrou: a rampa subiu de 1.81 para 3.06 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Mágico pro | o fundo escureceu: passou de 142 para 127 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Melhorar | a borda das letras borrou: a rampa subiu de 0.91 para 3.54 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Mágico pro | o fundo escureceu: passou de 154 para 147 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.62 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Mágico pro | o fundo escureceu: passou de 156 para 148 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.5 |
| Rhetorica Christiana -  Fray Diego | 1 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 4.08 para 0.52 pixels |
| Rhetorica Christiana -  Fray Diego | 446 | Melhorar | o fundo escureceu: passou de 208 para 182 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 0.4 para 4.5 |
| Rhetorica Christiana -  Fray Diego | 446 | Mágico pro | o fundo escureceu: passou de 208 para 201 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 4.59 para 0.0 |
| Sobre a Consolação da Filosofia -  | 1 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.5 |
| Sobre a Consolação da Filosofia -  | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.6 |
| Sobre a Consolação da Filosofia -  | 9 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.45 pixels |
| Sobre a Consolação da Filosofia -  | 9 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.43 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.39 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.75 para 0.38 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.41 pixels |
| Sobre a Consolação da Filosofia -  | 33 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.38 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.40 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.38 pixels |
| Sobre a Consolação da Filosofia -  | 50 | Melhorar | o fundo escureceu: passou de 161 para 159 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 3.8 para 9.1 |
| Sobre a Consolação da Filosofia -  | 50 | Mágico pro | o fundo escureceu: passou de 161 para 150 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.86 para 0.6 |

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
