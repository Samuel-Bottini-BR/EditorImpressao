# Horas — página 13 do PDF

- Livro: [horas](../livros/horas.md) · gabarito: sim (`horas_p013`) · imagem: `gabarito/paginas/horas_p013.png` (fora do git).
- "TABLE / CONTENU EN CE LIVRE.": títulos vermelhos e azuis dentro de uma **moldura dourada** fechada (o documento do Samuel chama de "borda prata"); "pag. 54" no canto de baixo da moldura. 72 DPI declarado (138 DPI para as ferramentas do ScanTailor), sem camadas. Gira 0,62°.

## O que ela tem de difícil

- R6: manter o texto, as cores (vermelho e azul) e a borda dourada; centralizar; papel branco.
- A moldura dourada sai escurecida, furada, preta ou falhada conforme o filtro e o detector; o detector marca um triângulo sobre "pag. 54".
- Títulos vermelhos fora da gravura sumiam no Preto e branco; letras com a perna cortada no Preto e branco (o "E" de "Exercisse").
- A caixa do conteúdo do ScanTailor, com o DPI do programa, fica por dentro da moldura.

## Itens que a usam

- Gabarito dos itens `fase1` e `6.3` ([lista.json](../../gabarito/lista.json)); obrigatória da Fase 1 (28/09: "moldura da TABLE").
- [1.2 Detector de gravura](../itens/1.2.md) ("consertar agora ... a moldura da Horas 13", 30/09), [1.3 OCR](../itens/1.3.md) (zonas Z9), [1.5](../itens/1.5.md), [6.3](../itens/6.3.md), [2.5 Caixa da página](../itens/2.5.md).

## O que já se viu nela, rodada a rodada

- 24/09/2026 → ScanTailor: "ruim na cor (vermelho e azul viraram preto, moldura dourada sumiu)".
- 30/09/2026 → zonas Z9 "RUIM" → "BOM"; moldura preta no Preto e branco na forma livre (consertado `47cabac`); títulos vermelhos somem no Preto e branco (consertado `8c29a7d`); N4 "RUIM"; O4 "BOM" (falta um quadradinho).
- 01/10/2026 → V1 títulos "BOM"; M1 moldura perto de "pag. 54" "RUIM" → consertado; MP1 dourado "BOM"; A4 "RUIM".
- 02/10/2026 → M1 "BOM".
- 05/10/2026 → Misto: "A", com letras cortadas (Lista de bugs, conferência 8, H13). Falta de memória na detecção vira "página sem gravura" (visto na Horas 13).
- 13/10/2026 → G6: melhorou (somem as cunhas brancas); caixa do conteúdo com DPI 138 fica por dentro da moldura (`ramo fase2-geometria-perguntas: relatorios/conferir/geometria-g7-g10-2026-10-12/pesquisa.md`).

## O que o Samuel disse

- 30/09/2026, Z9: "RUIM - na parte do subtitulo, parece estar apagando uma parte "contenu en ce livre" e também apaga um pouco da moldura dourada, não pega tudo na segunda imagem." ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md))
- 30/09/2026, Z9: "BOM - O resultado está bom, mas a borda dourada deveria sair sem alteração, ela ainda está saindo meio escurecido"; N4: "RUIM - A moldura em preto e branco sai toda falhada, nem sai totalmente preenchida e nem só as linhas dela."; O4: "BOM - pega inteira quase inteira, porque tem um quadradinho bem pequeno que falta pegar, além de que seleciona uma parte que não é moldura." ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 01/10/2026, M1: "RUIM - ela apaga um pedaço da moldura dourada, ali perto do escrito pag. 54."; V1 e MP1: "BOM" ([conferência 5](../../relatorios/conferencia-samuel-2026-10-01.md)). 02/10/2026, M1: "BOM" ([conferência 6](../../relatorios/conferencia-samuel-2026-10-02.md)).
- 05/10/2026, H13: "A - Guardar a tinta forte - mas ainda tem que melhora, ainda fica cortando algumas letras como o E de Exercisse a primeira perna do E a perna de cima é cortada, e tem outras letras assim que o programa está comendo tinta." ([conferência 8](../../relatorios/conferencia-samuel-2026-10-05-f.md))

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026) e teste do ScanTailor de 24/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md)).
- [plano, Lista de bugs 28/09–05/10 e Registro](../../docs/plano/PLANO-DEFINITIVO.md).
