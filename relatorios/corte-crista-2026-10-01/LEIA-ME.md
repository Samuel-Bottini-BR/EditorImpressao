# O "A" de "CRISTÃ" (cartão B6 da conferência 2) — 01/10/2026

Pedido: "mostram, mas foi cortado o A de Crista" (Samuel, conferência 2, cartão B6).
A página é a **Escola 7** (título "PRINCIPAIS VERDADES DA RELIGIÃO CRISTÃ").

## Conclusão

**O corte de bordas não come o "A".** Quem cobriu a perna do "A" foi a **moldura
cor-de-rosa desenhada por cima da imagem do cartão**. O corte deixa só uns 0,6 mm
de papel depois do "A", e o retângulo "margem de cima" foi desenhado justamente
nos últimos pontos do painel. Por baixo do retângulo, o "A" está inteiro.

- `prova-cartao-b6.jpg`: o mesmo canto do painel "AGORA: o que a TELA mostra",
  ampliado 4 vezes: à esquerda **sem** o retângulo (o "A" inteiro), à direita
  **com** o retângulo (como saiu no cartão: a perna do "A" some). Script:
  `prova_cartao_b6.py`.
- Com o código de hoje (ramo `fase-1`), pelo caminho de verdade do programa
  (`renderizar_pagina` a 110 DPI e `processar` gravando o PDF a 300 DPI, filtro
  Original): a última tinta do título fica a 7 pontos da borda direita no PDF
  (0,6 mm) e a 2 pontos na prévia. Nada cortado.
- O corte das 32 páginas do gabarito, medido na resolução cheia (300 DPI):
  `medida-corte-2026-10-01.json` (script `medir_corte_gabarito.py`). Na Escola 7,
  nenhuma peça de tinta partida.

## O que a medida achou nas outras páginas (já conhecido, não mexido)

Peças de tinta que a borda do corte atravessa, na resolução cheia
(`medida-corte-2026-10-01-recortes/`):

| Página | O quê | Quanto passa |
|---|---|---|
| Graduale 221 | o número da folha "Cvii", no alto à direita: o corte passa no meio do primeiro "i" e deixa o último "i" de fora (ele fica a ~8 pontos da beirada do scan e, na imagem reduzida do corte, gruda nela, então não conta como peça) | 16 pontos (1,4 mm) |
| Palatino 67 | a ponta do fio da moldura, embaixo à direita | 7 pontos |
| Escola 35 | três pedaços do endereço do site, no pé (vai ser apagado no item 6.4) | 2 pontos |
| Graduale 223 | um pontinho na beirada esquerda | 1 ponto |

O número da folha do Graduale 221 e 223 está na Lista de bugs (28/09) como
"sobra do não partir peça", decidido pela gerente para o corte do ScanTailor
(2.5/2.13).
