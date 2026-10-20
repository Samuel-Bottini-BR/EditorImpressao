# Palatino — página 5 do PDF

- Livro: [palatino](../livros/palatino.md) · gabarito: sim (`palatino_p005`) · imagem: `gabarito/paginas/palatino_p005.png` (fora do git).
- **Retrato** gravado (com barba) e letras; papel bem amarelado. PDF do Internet Archive com camadas: fundo em resolução cheia + camada de cima com máscara, 400 DPI. Gira 0,50°.

## O que ela tem de difícil

- R1: papel branco, letras e gravura (retrato) intactas — inclusive o papel **dentro** da gravura (o fundo do retrato) tem de ficar branco (regra de 28/09).
- O detector antigo marcava 100% da página como gravura.
- O "tirar o fundo" (1.1) deixa a página intacta e amarela (regra do 1.1 certa, regra da Fase 1 não).
- Endireitar automático numa folha girada para deitada achava inclinação falsa (0,4° → 4,3°).

## Itens que a usam

- Gabarito do item `fase1` ([lista.json](../../gabarito/lista.json)); obrigatória da Fase 1 (28/09: "fundo do retrato branco").
- [1.1](../itens/1.1.md), [1.2](../itens/1.2.md), [1.3](../itens/1.3.md) (Z1), [1.5](../itens/1.5.md); "Só as letras" (Fase 2).

## O que já se viu nela, rodada a rodada

- 24/09/2026 → teste do ScanTailor de 24/09 (PNG idêntico ao do gabarito).
- 28/09/2026 → prévia × PDF: cortes diferentes até 8% (consertado: mesmo corte). Detector antigo: 100% gravura (resolve-se com o 1.2).
- 29/09/2026 → 1.1: fica intacta e amarela (vai para o 1.5).
- 30/09/2026 → B2 fundo do retrato e barba "BOM"; Z1 "BOM".
- 01/10/2026 → páginas endireitadas com menos de 1 mm nos cantos (Palatino 5 esquerda 0,76 mm).
- 02/10/2026 → N1/N2 sem piora "BOM".
- 05/10/2026 → conferência 10, EX2 (o retrato no Misto): "entendi".
- 06/10/2026 → estudo: certa nos dois jeitos.

## O que o Samuel disse

- 30/09/2026, B2 "Palatino 5 - fundo do retrato e barba: BOM"; Z1 "BOM" ([conferência 30/09](../../relatorios/conferencia-samuel-2026-09-30.md)).
- 02/10/2026, N1 e N2: "BOM" ([conferência 6](../../relatorios/conferencia-samuel-2026-10-02.md)).
- 05/10/2026, EX2: "entendi - Se eu quiser preto eu escolho o preto e branco, simples." ([conferência 10](../../relatorios/conferencia-samuel-2026-10-05-b.md))

## De onde veio (fontes)

- "Vamos recapitular..." (12/09/2026) e teste do ScanTailor de 24/09/2026 ([gabarito/LEIA-ME.md](../../gabarito/LEIA-ME.md); [ESTADO-ATUAL, tabela R1](../../docs/plano/ESTADO-ATUAL.md)).
- [plano, Lista de bugs 28/09–01/10](../../docs/plano/PLANO-DEFINITIVO.md); [histórico, PARTE -11 §4](../../historico/Editor%20de%20Impressao%20-%20resumo%20para%20o%20Claude.md) (inclinação falsa).
