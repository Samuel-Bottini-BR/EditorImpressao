# Linha de base do Editor de Impressao

Medido em 08/08/2026 as 03:41.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **9 livros**, 2903 folhas, 3037 paginas de saida.
- A qualidade de imagem foi medida a fundo em **63 paginas**, as mesmas em toda rodada.
- **4 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **1454 MB** de memoria, contra o teto de 2048 MB.

## O que cada numero quer dizer

| Numero | O que e, na pratica |
|---|---|
| Espessura do traco | Grossura media da linha da letra, em pontinhos de tela (pixels). Se afina demais, some na impressao. |
| Vazios internos | Buraquinhos fechados dentro das letras: o miolo do **o**, do **e**, do **a**. Se o filtro engrossa demais, eles entopem e a letra vira bolha. Quanto mais sobrarem, melhor. |
| Nivel do fundo | Quao claro esta o papel, de 0 (preto) a 255 (branco). O alvo e 255: papel branco de verdade, sem o amarelado. |
| Ruido do fundo | O quanto o papel varia onde deveria ser liso. Quanto menor, mais limpo. |
| Transicao da borda | Largura da rampa entre a tinta e o papel, em pixels. **Este e o numero da queixa de letra pixelada.** De 1,2 a 2 e o certo; em 1,0 cravado a borda e degrau de escada, sem meio-tom nenhum; acima de 3 a letra borra. |
| Nitidez | O quanto a imagem tem detalhe definido. Maior e mais nitido, mas exagero vira ruido. |

## Como cada filtro se comporta, na media do acervo

| Filtro | Espessura | Vazios | Fundo (255=branco) | Ruido | Transicao (px) | Nitidez | Tempo/pagina |
|---|---|---|---|---|---|---|---|
| Original | 32.55 | 1753 | 189.0 | 2.41 | 1.43 | 741 | 0.00s |
| Preto e branco | 14.55 | 2334 | 226.3 | 1.18 | 1.16 | 6135 | 2.17s |
| Melhorar | 27.95 | 2560 | 219.3 | 1.26 | 1.44 | 1795 | 3.97s |
| Mágico pro | 33.56 | 2645 | 219.4 | 1.25 | 1.40 | 1813 | 4.50s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1,2 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.46 s | 10 s | sim |
| Primeiras miniaturas | 0.51 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 170 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 492 s | 1200 s | sim |
| Pico de memoria | 1454 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino romano | 9 MB | 134 | 134 | 46.6s | 0 |
| Graduale - Saeculum XIV | 271 MB | 750 | 750 | 230.8s | 3 |
| Livro de Horas - Luís XIV | 106 MB | 191 | 191 | 61.3s | 0 |
| Marial de sermoens - Frei Balthasar Paez. (1 | 205 MB | 907 | 907 | 135.3s | 0 |
| Na escola de Jesus - Catecismo explicado com | 48 MB | 199 | 199 | 29.5s | 0 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 12 MB | 92 | 92 | 72.3s | 1 |
| Rhetorica Christiana -  Fray Diego Valadés | 40 MB | 446 | 446 | 214.7s | 0 |
| Schön Neues Modell Buch - Johann Siebmacher | 11 MB | 134 | 268 | 62.4s | 0 |
| Sobre a Consolação da Filosofia - Severino B | 4 MB | 50 | 50 | 2.9s | 0 |

## Paginas que sairam piores que o original

Sao **4** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Graduale - Saeculum XIV | 126 | Preto e branco | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| Graduale - Saeculum XIV | 126 | Melhorar | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| Graduale - Saeculum XIV | 126 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.1 |
| POINTS d´ANCIENNES BRODERIES ANGLA | 76 | Mágico pro | o fundo escureceu: passou de 156 para 148 numa escala em que 255 e branco |

## Paginas em que a regua nao cobrou letra

Sao capas, folhas de guarda e versos limpos: nada nelas e mais escuro que a propria folha, entao nao ha letra para medir. Os criterios de letra - vazios internos, espessura e borda - ficam de fora. Os de fundo continuam valendo: sujar ou escurecer uma capa e estrago igual.

**Elas saem nomeadas aqui de proposito.** E onde a regua afrouxa, e se o detector errar - marcar como desenho uma pagina que tem texto - o erro tem de estar a vista, e nao escondido num numero menor.

| Livro | Pagina |
|---|---|
| Giovambattista Palatino cittadino romano | 1 |
| Giovambattista Palatino cittadino romano | 132 |
| Graduale - Saeculum XIV | 1 |
| Graduale - Saeculum XIV | 750 |
| Livro de Horas - Luís XIV | 1 |
| Livro de Horas - Luís XIV | 3 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 16 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 46 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES - Lou | 76 |
| Rhetorica Christiana -  Fray Diego Valadés | 1 |
| Rhetorica Christiana -  Fray Diego Valadés | 446 |
| Sobre a Consolação da Filosofia - Severino B | 1 |
| Sobre a Consolação da Filosofia - Severino B | 50 |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Alinhamento duvidoso | 349 | Não consegui achar o alinhamento do texto direito. |
| Tem cor | 305 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Corte encostou no texto | 33 | O corte da borda pode ter pegado parte do texto. |
| Tamanho diferente | 22 | Esta folha tem tamanho diferente das outras. |
| Muito torta | 4 | Esta página estava bem torta. Veja se ficou certa. |
| Parece em branco | 1 | Esta página parece estar em branco. Quer apagar? |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Giovambattista Palatino cittadino roma | 1229x1805 | 34.4 mm | 55.3 mm | 0.057 | 0.100 |
| Graduale - Saeculum XIV | 2630x4537 | 265.6 mm | 250.9 mm | 0.086 | 0.200 |
| Livro de Horas - Luís XIV | 2983x5461 | 108.7 mm | 566.8 mm | 0.114 | 0.200 |
| Marial de sermoens - Frei Balthasar Pa | 1167x3729 | 175.7 mm | 17.1 mm | 0.071 | 0.100 |
| Na escola de Jesus - Catecismo explica | 1897x2896 | 23.9 mm | 18.9 mm | 0.071 | 0.100 |
| POINTS d´ANCIENNES BRODERIES ANGLAISES | 1035x2595 | 68.3 mm | 15.7 mm | 0.000 | 0.000 |
| Rhetorica Christiana -  Fray Diego Val | 1534x2210 | 32.1 mm | 51.7 mm | 0.014 | 0.100 |
| Schön Neues Modell Buch - Johann Siebm | 594x1206 | 39.3 mm | 10.8 mm | 0.043 | 0.100 |
| Sobre a Consolação da Filosofia - Seve | 833x1396 | 20.1 mm | 13.2 mm | 0.071 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
