# Horas — página 47 do PDF

- Livro: [horas](../livros/horas.md) · gabarito: sim (`horas_p047`) · imagem: `gabarito/paginas/horas_p047.png` (fora do git). Saída do ScanTailor de 24/09 (`gabarito/scantailor-24-09/out/horas_p047.tif`, 154 MB) ficou fora do ramo `dados-de-teste` por ser grande demais.
- **Gravura** e texto dentro de moldura pintada; "JESUS" e "C" dourados; letra grossa. 72 DPI declarado (141 DPI para as ferramentas do ScanTailor), sem camadas.

## O que ela tem de difícil

- R6: gravura e texto, papel branco, tirar margem da esquerda, sem perder qualidade.
- Letra grossa no Preto e branco: o Otsu da folha inteira caía no meio do tom da letra e comia a beirada; continuam "pixels apagados no meio das letras".
- Letras coloridas ("JESUS", "C") quase somem no Preto e branco.
- O nosso endireitar deixava a página torta; o do ScanTailor endireita.

## Itens que a usam

- Gabarito dos itens `fase1` e `6.3` ([lista.json](../../gabarito/lista.json)).
- Filtro Preto e branco (Lista de bugs, A1), [1.2](../itens/1.2.md), [1.3](../itens/1.3.md) (zonas Z12), [2.2 Endireitar](../itens/2.2.md), [6.3](../itens/6.3.md).

## O que já se viu nela, rodada a rodada

- 24/09/2026 → ScanTailor: "muito bom (borrão preto no canto inferior direito)".
- 30/09/2026 → Z12 "RUIM" → "BOM" com faixa cinza embaixo de "pitie de nous" → consertado em 01/10 (papel 233–244 → 255).
- 01/10/2026 → I2/A1 "RUIM" (letras coloridas somem) → consertado; MP3 "BOM".
- 02/10/2026 → A1 "RUIM" ("ainda está apagando as letras") → conserto `1b174e4` (Sauvola completa o Otsu) e medidor `bf9680f`.
- 05/10/2026 → A1 e A1b "RUIM" de novo → volta para a Lista de bugs (pontos apagados no meio das letras). D3: o nosso deixa torta, o ScanTailor endireita.
- 20/10/2026 → hoje: A1 continua aberto na Lista de bugs (05/10).

## O que o Samuel disse

- 30/09/2026, Z12: "RUIM - gravura não está sendo pega completamente, mas está muito melhor que as outras iluminarias." ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md)); depois: "BOM - ficou perfeito. mas embaixo do "pitie de nous" e do "propre en amour divin" está cinza, tem uma faixa cinza embaixo, porque ficou essa faixa cinza era para ser totalmente branco né?" ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 01/10/2026, I2: "BOM - O enfeite ficou bom, mas está apagando letras né, isso não pode acontecer, tem que reconhecer as letras mesmo em outras cores"; A1: "RUIM - Eu preciso conseguir enchergar todas as letras da folha" ([conferência 5](../../relatorios/conferencia-samuel-2026-10-01.md))
- 02/10/2026, A1: "RUIM - Ainda está apagando as letras, o original está muito melhor para ler" ([conferência 6](../../relatorios/conferencia-samuel-2026-10-02.md))
- 05/10/2026, A1: "RUIM - ainda pode melhorar, mas está quase perfeito."; A1b: "RUIM - Nenhuma está grossa demais, mas continuam apresentando falhas, pixels apagados no meio das letras." ([conferência 7](../../relatorios/conferencia-samuel-2026-10-05.md)); E2: "CONCORDO" ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md)).

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026) e teste do ScanTailor de 24/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md)).
- [plano, Lista de bugs 05/10 (A1) e Registro 02/10–05/10/2026](../../docs/plano/PLANO-DEFINITIVO.md).
