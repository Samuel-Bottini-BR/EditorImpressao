# Opus Majus — página 20 do PDF

- Livro: [opusmajus](../livros/opusmajus.md) · gabarito: sim (`opusmajus_p020`) · imagem: `gabarito/paginas/opusmajus_p020.png` (fora do git).
- **Foto** da estátua de Roger Bacon, com legenda. PDF do Internet Archive com camadas: os tons da foto estão só no fundo, em baixa resolução (166 DPI); a camada de cima (500 DPI) tem os pontinhos pretos da foto e a legenda. Gira 0,31°.

## O que ela tem de difícil

- Jogando o fundo fora, a foto vira um pontilhado duro: o programa precisa perceber que é foto.
- A estátua tende a sair mais clara, com halo, degrau no alto e rosto lavado; nas formas do detector, a "livre" estraga e a "retangular"/"Este livro tem fotos" acerta.
- As contas de endireitar discordam mais de 0,3° (aviso C1).

## Itens que a usam

- Gabarito do item `fase1` ([lista.json](../../gabarito/lista.json)); página obrigatória da Fase 1 (28/09: "Opus Majus 20 (foto da estátua)").
- [1.1 Tirar o fundo](../itens/1.1.md): "A foto do Opus Majus 20 tem de ficar igual ao original".
- [1.2 Detector de gravura](../itens/1.2.md): forma livre × retangular; "Este livro tem fotos".
- [1.5](../itens/1.5.md): halo, estátua clara. "Só neste pedaço" no Preto e branco (Fase 2).

## O que já se viu nela, rodada a rodada

- 28/09/2026 → a limpeza dos quadradinhos lavou a foto (consertado); ficam halo, estátua clara e degrau no alto (Lista de bugs, 1.2/1.5).
- 29/09/2026 → 1.1: foto mais clara que o original (cinza 184 → 228) → consertado (`06f747e`); beirada de baixo perde até 0,35 mm.
- 30/09/2026 → F2 "BOM" no "tirar o fundo"; 1.2 ligado: forma livre piora, retangular perfeita; G5 "RUIM"; O2 "Este livro tem fotos" "BOM".
- 01/10/2026 → F1 (Preto e branco) "RUIM" → consertado; A3 "RUIM" ("Este livro tem fotos é a melhor escolha").
- 02/10/2026 → F1 "BOM"; X2 Mágico pro, forma livre: "muito ruim" → consertado (`6748949`).
- 05/10/2026 → X2 "BOM", aprovado por enquanto; X2b "Quero mais escuro" (Lista de espera). Conferência 13: S2 "só neste pedaço" "BOM".
- 08/10/2026 → endireitar do ScanTailor: aviso C1 (as contas discordam). 12/10 G6: "Está bom".
- 13/10/2026 → "Para revisar" no livro novo: decide diferente do estudo (uma das 5). 20/10/2026 → o verificador tem esta página para reabrir na janela.

## O que o Samuel disse

- 29/09/2026 (decisão do 1.1): "A foto do Opus Majus 20 não pode sair mais clara: tem que ficar igual ao original." ([plano, Lista de bugs 29/09](../../docs/plano/PLANO-DEFINITIVO.md))
- 30/09/2026, F2 "BOM"; G5: "RUIM - está ruim, nas duas ultimas duas fotos da direita as fotos pioraram bastante." ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md))
- 01/10/2026, F1: "RUIM - não gostei de como ficou esbranquiçada, não da mais para ver o rosto direito da imagem."; A3: "RUIM - ESTE LIVRO TEM FOTOS É A MELHOR ESCOLHA ATÉ AGORA, espero ter a escolha de conseguir deixar a foto em original, caso precise." ([conferência 5](../../relatorios/conferencia-samuel-2026-10-01.md))
- 02/10/2026, X2: "não sei porque, agora ficou muito ruim, não consigo ver o rosto mais, esses pontos estão horriveis atras da estatua." ([conferência 6](../../relatorios/conferencia-samuel-2026-10-02.md)); O3: "Manter - Mas precisa ser melhorado" ([decisões 02/10](../../relatorios/decisoes-samuel-2026-10-02.md)).
- 05/10/2026, X2: "BOM - mas ainda temos algumas partes que ficaram muito esbranquiçadas, mas estamos quase chegando no ponto. Mas está aprovado por enquanto."; X2b: "Quero mais escuro" ([conferência 7](../../relatorios/conferencia-samuel-2026-10-05.md)).
- 05/10/2026, S2: "BOM - Mas se eu quiser deixar todas as fotos no original, eu vou conseguir né?" ([conferência 13](../../relatorios/conferencia-samuel-2026-10-05-e.md)).
- 12/10/2026, G6: "Está bom" ([conferência 12/10/2026](../../relatorios/conferencia-samuel-2026-10-12.md)).

## De onde veio (fontes)

- Candidata escolhida pelo implementador olhando o livro inteiro; aprovada pelo Samuel em 25/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md), pendência 5).
