# Linha de base do Editor de Impressao

Medido em 04/08/2026 as 00:58.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **1 livros**, 750 folhas, 750 paginas de saida.
- A qualidade de imagem foi medida a fundo em **7 paginas**, as mesmas em toda rodada.
- **5 vezes um filtro deixou a pagina pior do que ela era.** Cada caso e uma pagina com um filtro; a mesma pagina pode aparecer mais de uma vez, uma por filtro que a estragou. O criterio de aceitacao do projeto exige que esse numero seja zero.
- O programa nunca passou de **1347 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 33.82 | 5268 | 172.5 | 2.58 | 2.10 | 9 | 0.01s |
| Preto e branco | 13.81 | 856 | 249.9 | 0.91 | 0.35 | 4738 | 1.28s |
| Melhorar | 32.41 | 4063 | 206.8 | 2.56 | 1.94 | 92 | 4.35s |
| Mágico pro | 30.95 | 4961 | 203.9 | 3.00 | 1.76 | 96 | 5.31s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.44 s | 10 s | sim |
| Primeiras miniaturas | 0.41 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 162 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 560 s | 1200 s | sim |
| Pico de memoria | 1347 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Graduale - Saeculum XIV | 271 MB | 750 | 750 | 242.7s | 5 |

## Paginas que sairam piores que o original

Sao **5** ocorrencias. Cada linha e uma pagina com um filtro que a deixou pior do que ela era antes de qualquer tratamento.

| Livro | Pagina | Filtro | O que piorou |
|---|---|---|---|
| Graduale - Saeculum XIV | 1 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.3 para 6.8 |
| Graduale - Saeculum XIV | 126 | Preto e branco | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 126 | Melhorar | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 126 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 2.8 para 6.4 |
| Graduale - Saeculum XIV | 750 | Mágico pro | o fundo ficou mais sujo: ruido subiu de 4.9 para 7.9 |

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Tem cor | 211 | Esta página tem cor - o preto e branco vai perder a ilustração. |
| Tamanho diferente | 6 | Esta folha tem tamanho diferente das outras. |
| Corte encostou no texto | 6 | O corte da borda pode ter pegado parte do texto. |
| Alinhamento duvidoso | 1 | Não consegui achar o alinhamento do texto direito. |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Graduale - Saeculum XIV | 2630x4537 | 265.6 mm | 250.9 mm | 0.071 | 0.200 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
