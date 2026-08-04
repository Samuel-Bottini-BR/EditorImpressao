# Linha de base do Editor de Impressao

Medido em 04/08/2026 as 01:06.

Este relatorio e uma **regua**: ele nao diz se o programa esta bonito, diz em numeros como ele esta hoje. Serve para que, depois de qualquer mudanca, se possa medir de novo e saber se melhorou de verdade ou se foi so impressao.

## O essencial, em quatro linhas

- Foram medidos **1 livros**, 191 folhas, 191 paginas de saida.
- A qualidade de imagem foi medida a fundo em **7 paginas**, as mesmas em toda rodada.
- **Nenhuma pagina saiu pior que o original.** E o que se espera.
- O programa nunca passou de **1182 MB** de memoria, contra o teto de 2048 MB.

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
| Original | 32.99 | 5814 | 219.5 | 1.51 | 1.87 | 401 | 0.01s |
| Preto e branco | 21.54 | 7550 | 244.0 | 1.13 | 1.23 | 4913 | 6.01s |
| Melhorar | 23.26 | 19963 | 241.3 | 1.17 | 1.63 | 938 | 9.50s |
| Mágico pro | 23.13 | 20443 | 241.8 | 1.13 | 1.58 | 995 | 10.58s |

> Leitura rapida: na coluna **Fundo**, quanto mais perto de 255 melhor - e o amarelado indo embora. Na coluna **Transicao**, o alvo e entre 1 e 2; valor muito baixo e o serrilhado que aparece nas letras.

## Velocidade e memoria

| O que | Medido | Meta | Passou? |
|---|---|---|---|
| Abrir o programa | 0.46 s | 10 s | sim |
| Primeiras miniaturas | 0.57 s | 5 s | sim |
| Analisar 500 folhas (projecao) | 166 s | 180 s | sim |
| Exportar 500 paginas a 300 DPI (projecao) | 524 s | 1200 s | sim |
| Pico de memoria | 1182 MB | 2048 MB | sim |

> As duas linhas marcadas como **projecao** foram calculadas a partir do custo real por folha e por pagina medido nos nove livros, multiplicado por 500. Nenhum livro do acervo tem 500 paginas.

## Livro a livro

| Livro | Tamanho | Folhas | Paginas | Analise | Paginas piores |
|---|---|---|---|---|---|
| Livro de Horas - Luís XIV | 106 MB | 191 | 191 | 63.3s | 0 |

## Paginas que sairam piores que o original

Nenhuma. E o resultado esperado.

## Paginas marcadas em laranja, e por que

Laranja quer dizer *o programa nao teve certeza*. Nao e erro: e um pedido de conferida.

| Aviso | Quantas paginas | O que o programa diz |
|---|---|---|
| Alinhamento duvidoso | 152 | Não consegui achar o alinhamento do texto direito. |
| Tamanho diferente | 8 | Esta folha tem tamanho diferente das outras. |
| Corte encostou no texto | 5 | O corte da borda pode ter pegado parte do texto. |
| Muito torta | 2 | Esta página estava bem torta. Veja se ficou certa. |

## Geometria: as paginas saem todas do mesmo tamanho?

Paginas do mesmo livro precisam sair identicas, senao o caderno nao fecha direito na hora de imprimir. A coluna de variacao deveria ser zero.

| Livro | Menor pagina (px) | Variacao largura | Variacao altura | Inclinacao media | Inclinacao maxima |
|---|---|---|---|---|---|
| Livro de Horas - Luís XIV | 2952x5527 | 111.3 mm | 563.9 mm | 0.086 | 0.100 |

## Em que maquina isto foi medido

- Windows 11, Python 3.14.3, 16 nucleos, 15 GB de memoria
- OpenCV 5.0.0, DoxaPy disponivel: sim
- Todas as imagens medidas a 300 DPI

> A maquina onde isto rodou e mais forte que a do Kaique. Os tempos numa maquina modesta serao maiores; a Etapa 4 preve a conferencia num computador de verdade.
