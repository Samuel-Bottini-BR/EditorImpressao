# Teste do ScanTailor Advanced — modo Misto (24/09/2026)

Teste feito no PC do Samuel, com o ScanTailor Advanced **de verdade** (não uma recriação), configuração padrão, modo de saída "Misto". Objetivo: ver se o seletor automático de gravuras dele funciona nos livros do acervo antes de decidir trazê-lo.

Arquivos: `D:\programas\Scan Tailor\Testes de ajuste\teste-gravuras-varios\` (páginas de entrada em PNG, saída em `out\`, comparações lado a lado em `comparacoes\`).

## Resultado por página

| Página | Resultado |
|---|---|
| Na escola de Jesus p. 7 | **Ótimo.** A gravura colorida ficou intacta, o texto preto e o papel branco. O endereço de site sumiu (ficou fora do corte). |
| Palatino p. 5 | **Ótimo.** O retrato foi preservado e o papel ficou branco. O papel **dentro** do oval continua amarelado, porque entrou como parte da gravura. |
| Palatino p. 9 | **Bom.** O papel ficou branco e a mancha do verso sumiu. A capitular xilográfica **não** foi reconhecida como gravura e virou preto e branco: ficou legível, mas perdeu detalhe. |
| Livro de Horas p. 47 | **Muito bom.** A iluminura foi mantida, o texto continuou colorido e o papel ficou branco. Um borrão preto no canto inferior direito. |
| Livro de Horas p. 13 | **Ruim na cor.** O texto ficou limpo e o papel branco, mas o vermelho e o azul do texto viraram preto, e quase toda a moldura dourada sumiu. |
| Livro de Horas p. 11 (frontispício todo iluminado) | **Ruim.** Grandes áreas da iluminura viraram preto sólido. |

## Conclusão

- O detector **verdadeiro** do ScanTailor funciona muito melhor que as duas recriações anteriores (31/07 e 16/09) nos livros impressos com gravura separada do texto.
- Ele falha em duas situações:
  - **página inteira iluminada**;
  - **texto colorido** (a cor da tinta vira preto, porque o modo Misto binariza o texto).
- O texto colorido se resolve com a ideia das camadas do Internet Archive: a camada de cima guarda a cor original da tinta.
- **Decisão do Samuel (24/09): caminho (a)** — usar o código original do ScanTailor, compilado e ligado ao nosso programa, e não uma tradução para Python.

## Achado extra

O PDF do **Palatino** também é do Internet Archive e já vem com duas camadas:
- nas páginas de gravura (5, 7, 9, 10), o Archive deixou a página inteira na camada de baixo;
- nas páginas só de texto (ex.: 57), a camada de baixo é o fundo em baixa resolução.

Então o "tirar o fundo" automático já funciona nas páginas de texto desse livro.

## Como o Internet Archive separa as camadas

Programa aberto `internetarchive/archive-pdf-tools` (AGPL-3.0; cabe na decisão de licença de 17/09), arquivo `internetarchivepdf/mrc.py`:
1. OCR (Tesseract) marca onde está cada linha de texto (hOCR).
2. Dentro de cada linha, binarização Sauvola (janela = DPI/4, k = 0,1), testando a linha normal e invertida e ficando com a mais limpa; depois limpeza de pontinhos.
3. Camada de cima: a cor original da tinta só onde a máscara diz "é tinta".
4. Camada de baixo: a página com as letras apagadas e preenchidas com o papel em volta, em baixa resolução. Gravuras e fotos ficam nela.

O segredo é o passo 1: mancha fora das linhas de texto nunca entra na máscara.

## Observação sobre o tamanho das páginas no teste

As páginas de saída ficaram pequenas dentro de uma folha grande porque a etapa "Margens" do ScanTailor iguala o tamanho de todas as páginas do projeto ("Match size with other pages"). O projeto misturou livros de tamanhos diferentes, e todos foram para o tamanho do maior (Livro de Horas). Isso não afeta a qualidade. Com um livro por projeto, isso não acontece.
