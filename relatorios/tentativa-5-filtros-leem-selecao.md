# Tentativa 5: filtros lendo da selecao (nenhuma pagina marcada)

Medido em 31/07/2026 as 12:07.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **9 livros**, 2903 folhas, 3037 paginas de saida.
- A qualidade de imagem foi medida a fundo em **63 paginas**, as mesmas em toda rodada.
- **52 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **1136 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 53.58 | 2352 | 191.9 | 2.25 | 1.36 | 692 | 0.00s |
| Preto e branco | 8.26 | 1472 | 254.3 | 0.00 | 0.00 | 13955 | 0.12s |
| Melhorar | 23.13 | 2472 | 213.3 | 3.24 | 1.34 | 1405 | 0.63s |
| Mágico pro | 28.22 | 3264 | 215.4 | 3.68 | 0.95 | 3144 | 0.86s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.70 s | 10 s | sim |
| Primeiras miniaturas | 0.38 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 150 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 284 s | 1200 s | sim |
| Pico de memoria | 1136 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino romano | 9 MB | 134 | 134 | 44.6s | 5 |
| Graduale - Saeculum XIV | 271 MB | 750 | 750 | 196.2s | 8 |
| Livro de Horas - Luís XIV | 106 MB | 191 | 191 | 51.1s | 1 |
| Marial de sermoens - Frei Balthasar Paez. (1 | 205 MB | 907 | 907 | 109.1s | 11 |
| Na escola de Jesus - Catecismo explicado com | 48 MB | 199 | 199 | 25.2s | 2 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 12 MB | 92 | 92 | 65.3s | 7 |
| Rhetorica Christiana -  Fray Diego Valadés | 40 MB | 446 | 446 | 191.5s | 3 |
| Schön Neues Modell Buch - Johann Siebmacher | 11 MB | 134 | 268 | 55.9s | 1 |
| Sobre a Consolação da Filosofia - Severino B | 4 MB | 50 | 50 | 2.4s | 14 |

## Paginas que sairam piores que o original

Sao **52** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Giovambattista Palatino cittadino  | 1 | Mágico pro | o fundo escureceu: passou de 88 para 83 numa escala em que 255 e branco |
| Giovambattista Palatino cittadino  | 27 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.79 para 0.48 pixels |
| Giovambattista Palatino cittadino  | 53 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.90 para 0.62 pixels |
| Giovambattista Palatino cittadino  | 132 | Melhorar | o fundo escureceu: passou de 255 para 230 numa escala em que 255 e branco |
| Giovambattista Palatino cittadino  | 134 | Melhorar | o fundo ficou mais sujo: ruido subiu de 6.6 para 8.1 |
| Graduale - Saeculum XIV | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.3 para 7.5 |
| Graduale - Saeculum XIV | 126 | Preto e branco | as letras entupiram: sobraram 448 vazios internos de 1149 (61% a menos) |
| Graduale - Saeculum XIV | 126 | Melhorar | o fundo ficou mais sujo: ruido subiu de 2.0 para 4.1 |
| Graduale - Saeculum XIV | 126 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 2.0 para 4.8 |
| Graduale - Saeculum XIV | 376 | Preto e branco | o traco afinou demais: de 19.06 para 12.16 pixels (36% a menos) |
| Graduale - Saeculum XIV | 376 | Melhorar | as letras entupiram: sobraram 119 vazios internos de 167 (29% a menos) |
| Graduale - Saeculum XIV | 626 | Melhorar | o fundo ficou mais sujo: ruido subiu de 1.6 para 3.1 |
| Graduale - Saeculum XIV | 750 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.9 para 9.0 |
| Livro de Horas - Luís XIV | 191 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.2 para 6.3 |
| Marial de sermoens - Frei Balthasa | 1 | Melhorar | as letras entupiram: sobraram 133 vazios internos de 229 (42% a menos) |
| Marial de sermoens - Frei Balthasa | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.0 para 5.1 |
| Marial de sermoens - Frei Balthasa | 152 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.5 para 9.4 |
| Marial de sermoens - Frei Balthasa | 303 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.0 para 6.8 |
| Marial de sermoens - Frei Balthasa | 454 | Melhorar | o fundo ficou mais sujo: ruido subiu de 3.3 para 7.4 |
| Marial de sermoens - Frei Balthasa | 454 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.3 para 12.0 |
| Marial de sermoens - Frei Balthasa | 605 | Melhorar | o fundo ficou mais sujo: ruido subiu de 3.0 para 4.6 |
| Marial de sermoens - Frei Balthasa | 605 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.0 para 8.1 |
| Marial de sermoens - Frei Balthasa | 756 | Melhorar | o fundo ficou mais sujo: ruido subiu de 3.6 para 6.0 |
| Marial de sermoens - Frei Balthasa | 756 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.6 para 10.1 |
| Marial de sermoens - Frei Balthasa | 907 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 3.3 para 5.7 |
| Na escola de Jesus - Catecismo exp | 199 | Preto e branco | as letras entupiram: sobraram 148 vazios internos de 248 (40% a menos); o traco afinou demais: de 28.57 para 11.01 pixels (61% a menos) |
| Na escola de Jesus - Catecismo exp | 199 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 1.4 para 3.9 |
| POINTS d´ANCIENNES BRODERIES ANGLA | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 6.0 para 9.9 |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Melhorar | o fundo escureceu: passou de 142 para 138 numa escala em que 255 e branco; a borda das letras borrou: a rampa subiu de 1.81 para 3.06 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 16 | Mágico pro | o fundo escureceu: passou de 142 para 127 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Melhorar | a borda das letras borrou: a rampa subiu de 0.91 para 3.54 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 46 | Mágico pro | o fundo escureceu: passou de 154 para 147 numa escala em que 255 e branco |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Melhorar | a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.62 pixels |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Mágico pro | o fundo escureceu: passou de 156 para 148 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.83 para 0.5 |
| Rhetorica Christiana -  Fray Diego | 1 | Mágico pro | a borda das letras virou degrau (serrilhado): a rampa caiu de 4.08 para 0.55 pixels |
| Rhetorica Christiana -  Fray Diego | 446 | Melhorar | o fundo escureceu: passou de 205 para 176 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 0.4 para 4.8 |
| Rhetorica Christiana -  Fray Diego | 446 | Mágico pro | o fundo escureceu: passou de 205 para 198 numa escala em que 255 e branco; a borda das letras virou degrau (serrilhado): a rampa caiu de 4.43 para 0.0 |
| Schön Neues Modell Buch - Johann S | 268 | Mágico pro | o fundo escureceu: passou de 119 para 114 numa escala em que 255 e branco |
| Sobre a Consolação da Filosofia -  | 1 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.5 para 17.5 |
| Sobre a Consolação da Filosofia -  | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.5 para 19.9 |
| Sobre a Consolação da Filosofia -  | 9 | Melhorar | o fundo ficou mais sujo: ruido subiu de 5.0 para 7.1; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.69 pixels |
| Sobre a Consolação da Filosofia -  | 9 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 5.0 para 9.7; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.72 para 0.53 pixels |
| Sobre a Consolação da Filosofia -  | 17 | Melhorar | o fundo ficou mais sujo: ruido subiu de 6.3 para 9.4 |
| Sobre a Consolação da Filosofia -  | 17 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 6.3 para 13.5; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.79 para 0.54 pixels |
| Sobre a Consolação da Filosofia -  | 25 | Melhorar | o fundo ficou mais sujo: ruido subiu de 6.8 para 9.4 |
| Sobre a Consolação da Filosofia -  | 25 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 6.8 para 13.8 |
| Sobre a Consolação da Filosofia -  | 33 | Melhorar | o fundo ficou mais sujo: ruido subiu de 7.2 para 10.6 |
| Sobre a Consolação da Filosofia -  | 33 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 7.2 para 15.3; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.88 para 0.54 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Melhorar | o fundo ficou mais sujo: ruido subiu de 7.4 para 10.1; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.67 pixels |
| Sobre a Consolação da Filosofia -  | 41 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 7.4 para 14.6; a borda das letras virou degrau (serrilhado): a rampa caiu de 0.70 para 0.49 pixels |
| Sobre a Consolação da Filosofia -  | 50 | Melhorar | o fundo escureceu: passou de 161 para 159 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 3.8 para 9.1 |
| Sobre a Consolação da Filosofia -  | 50 | Mágico pro | o fundo escureceu: passou de 161 para 150 numa escala em que 255 e branco; o fundo ficou mais sujo: ruido subiu de 3.8 para 5.6; a borda das letras vi |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Tem cor | 392 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Alinhamento duvidoso | 349 | Não consegui achar o alinhamento do texto direito. |
| Tamanho diferente | 22 | Esta folha tem tamanho diferente das outras. |
| Muito torta | 4 | Esta página estava bem torta. Veja se ficou certa. |
| Parece em branco | 1 | Esta página parece estar em branco. Quer apagar? |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino roma | 1074x1698 | 22.3 mm | 64.3 mm | 0.071 | 0.100 |
| Graduale - Saeculum XIV | 1916x5631 | 304.1 mm | 158.2 mm | 0.071 | 0.100 |
| Livro de Horas - Luís XIV | 3092x5732 | 99.5 mm | 569.0 mm | 0.086 | 0.100 |
| Marial de sermoens - Frei Balthasar Pa | 1070x3855 | 167.3 mm | 8.5 mm | 0.071 | 0.100 |
| Na escola de Jesus - Catecismo explica | 1988x2946 | 20.8 mm | 15.9 mm | 0.086 | 0.100 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES | 993x2759 | 71.9 mm | 7.0 mm | 0.014 | 0.100 |
| Rhetorica Christiana -  Fray Diego Val | 1427x2348 | 41.1 mm | 40.0 mm | 0.071 | 0.100 |
| Schön Neues Modell Buch - Johann Siebm | 558x1274 | 43.1 mm | 4.3 mm | 0.014 | 0.100 |
| Sobre a Consolação da Filosofia - Seve | 940x1514 | 11.0 mm | 3.2 mm | 0.071 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
