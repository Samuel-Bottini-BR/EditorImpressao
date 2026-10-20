# Opus Majus — página 256 do PDF

- Livro: [opusmajus](../livros/opusmajus.md) · gabarito: sim (`opusmajus_p256`) · imagem: `gabarito/paginas/opusmajus_p256.png` (fora do git).
- **Tabela grande numa folha dobrável deitada** (folha muito maior que as outras: 20,8 × 17,6 cm contra 14,6 × 23,5 cm da página comum), com linhas finas e números pequenos; marca da dobra e "fantasmas" das linhas no fundo. Internet Archive com camadas (500 DPI em cima).

## O que ela tem de difícil

- Folha muito maior: entra na conta das margens iguais e muda o tamanho de todas; precisa ser impressa ("precisamos de alternativa do que fazer com ela").
- O dividir do ScanTailor parte a tabela em duas; o "corte da sobra" forçado corta colunas.
- Os números fracos da última coluna se partem e saem como mancha; o Mágico pro apaga um detalhe embaixo à direita.
- O docTR rodaria melhor em pedaços (tabela grande).

## Itens que a usam

- Gabarito do item `fase1` ([lista.json](../../gabarito/lista.json)): [1.1](../itens/1.1.md), [1.3](../itens/1.3.md) (Z17).
- [2.1 Dividir](../itens/2.1.md), [2.4 Margens](../itens/2.4.md) e [2.6 Tamanho final](../itens/2.6.md) (pergunta `g9-folha-maior-impressao`, aberta).

## O que já se viu nela, rodada a rodada

- 29/09/2026 → Kraken: joga fora 8 linhas e marca a página para revisar.
- 30/09/2026 → Z17 "RUIM" → "BOM" (apaga um pouco um detalhe).
- 01/10/2026 → segundo binarizador para os números fracos: tentado e revertido. X1: "entendi".
- 05–06/10/2026 → dividir: o ScanTailor parte a tabela; o forçado corta colunas (fica de 22% a 84%).
- 13–14/10/2026 → `g9-pagina-muito-maior`: "O programa deixa essa folha de fora sozinho, e avisa"; nasce `g9-folha-maior-impressao`, **ainda sem resposta** em 19/10/2026.

## O que o Samuel disse

- 30/09/2026, Z17: "RUIM - ele apaga uma parte da tabela do lado inferior direito." ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md)); "BOM - Está muito bom, mas ele acaba apagando um pouco esse detalhe." ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 05/10/2026, F3: "CONCORDO - Sim, mas ele cortou na lombada," ([conferência 9](../../relatorios/conferencia-samuel-2026-10-05-g.md))
- 13/10/2026, `g9-pagina-muito-maior`: "precisamos de alternativa do que fazer com ela, porque ela precisa ser impressa." ([conferência 13/10/2026](../../relatorios/conferencia-samuel-2026-10-13.md))
- 14/10/2026: "quando ela foi impressa a primeira vez, ela foi impressa um folha a4 inteira para uma tabela só né?" ([plano, Registro 14/10/2026](../../docs/plano/PLANO-DEFINITIVO.md))

## De onde veio (fontes)

- Candidata do implementador, aprovada em 25/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md)); [relatório do dividir](../../relatorios/conferir/dividir-2026-10-06/relatorio.md); [histórico, PARTE -16 §4 e §6](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md).
