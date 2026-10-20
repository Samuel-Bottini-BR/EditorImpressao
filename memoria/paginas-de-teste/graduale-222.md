# Graduale — página 222 do PDF

- Livro: [graduale](../livros/graduale.md) · gabarito: sim (`graduale_p222`) · imagem: `gabarito/paginas/graduale_p222.png` (fora do git).
- Manuscrito do século XIV, partitura com claves e pautas; mancha do verso. 72 DPI declarado, sem camadas. Gira -0,88°.

## O que ela tem de difícil

- R3: "aumentar a margem do lado direito" (página par da dupla 222/223).
- A música é toda "tinta fora do texto": o detector de gravura e o "Só o texto achado" tropeçam nela (no "Só o texto achado" **a música inteira some**).
- Sensível ao enquadramento: mudando o corte, o Mágico pro tratou a página de outro jeito (notas marrons com halo).

## Itens que a usam

- Gabarito do item `2.4` ([lista.json](../../gabarito/lista.json)): [2.4 Margens](../itens/2.4.md).
- [1.2 Detector de gravura](../itens/1.2.md): pauta tomada por gravura (consertado).
- [Para revisar](../itens/para-revisar.md): "'Guardar só o texto' que apaga a música (Graduale 222): botão 'Trazer de volta nesta página'".
- [1.5](../itens/1.5.md) e [1.4](../itens/1.4.md): notas com halo, orla cinza (Lista de bugs).

## O que já se viu nela, rodada a rodada

- 28/09/2026 → corte: a clave foi consertada; sobra a ponta da primeira clave. Mágico pro com halo e notas marrons depois do enquadramento novo (vai para 1.2/1.5).
- 30/09/2026 → 1.2 ligado: 14% da página (pauta) marcada como gravura → consertado (`47cabac`, 0%). Conferência: B5 clave "BOM"; O3 "BOM"; N5 Preto e branco "RUIM" (ver abaixo); fio preto grosso na beirada direita no Preto e branco.
- 02/10/2026 → conferência 6: N5/N6 sem piora, "BOM".
- 05/10/2026 → Misto A/B/C: escolhida "A - Guardar a tinta forte".
- 06/10/2026 → estudo e rodada 1: jeito de fábrica certo; "Só o texto achado" apaga a música. Samuel: "Não precisa" ir para revisar (ver abaixo).
- 09/10/2026 → rodada 5: botão "Trazer de volta nesta página" com o que sumiu já marcado.
- 12/10/2026 → G6: "Está bom". 13/10/2026 → investigação do G6: igual (272 × 446 → 266 × 466 mm); na experiência da cunha (não adotada) mudava muito de largura.
- 20/10/2026 → hoje: o "Trazer de volta" está pronto no ramo `fase2-para-revisar`, não juntado.

## O que o Samuel disse

- 30/09/2026, B5 "Graduale 222 - a clave: BOM"; Z21 "NÃO SEI - precisa melhorar" ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md)).
- 30/09/2026, N5: "RUIM - estamos perdendo alguns detalhes das notas, transformando linha das notas em nada, mas até agora foi um dos melhores resultados, deve continuar nesse caminho, mas queremos conseguir as notas integralmente, diferenciado o que é mancha das notas da folha de trás e o que é nota realmente da pauta." ([conferência 2](../../relatorios/conferencia-samuel-2026-09-30-b.md))
- 05/10/2026, G222: "A - Guardar a tinta forte" ([conferência 8](../../relatorios/conferencia-samuel-2026-10-05-f.md)).
- 06/10/2026, rodada 1, "Não precisa": "não precisa, mas esse é um caso isolado? porque esse é um livro atipico , não costumamos imprimir livros de musica, se isso não ir para revisar pode afetar outros livros?" ([rodada 1](../../relatorios/revisar-decisoes/rodada-1/respostas-samuel.md))
- 09/10/2026, `rv5-erro-6-so-texto`: "opção 1, mas aparece marcado como apareceu na segunda opção." ([rodada 5](../../relatorios/revisar-decisoes/rodada-5/respostas-samuel.md))

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026); [gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md), [lista.json](../../gabarito/lista.json).
- [plano, Lista de bugs 28/09–30/09 e bloco "Para revisar" da Fase 2](../../docs/plano/PLANO-DEFINITIVO.md); [estudo](../../relatorios/revisar-criterios-2026-10-06/revisar-criterios.md).
