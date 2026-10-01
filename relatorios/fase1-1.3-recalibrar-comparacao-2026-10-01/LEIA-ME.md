# Comparação automática dos OCRs com as zonas aprovadas — 01/10/2026

Pedido: recalibrar a comparação automática (`core/ocr_comparar.py`, commit `23665fb`)
depois que o Samuel aprovou as zonas do OCR (conferência 2), já com a decisão D5
(as letrinhas dos diagramas do Opus 165 são texto).

## Conclusão

**Os números da comparação ficam como estão: nenhuma combinação acerta mais páginas
sem mandar página boa para revisar.** Pela régua nova a decisão bate em **18 das 22**
páginas, **nenhuma** vai para revisar à toa, e **4 erros passam** (Horas 27, Graduale
221, 222 e 223). Os 4 são erros que os dois OCRs cometem quase igual, então comparar
um com o outro não os enxerga:

- **Graduale 222 e 223:** nenhuma discordância na página. Os dois perdem pedaços nos
  mesmos lugares: palavras vermelhas no começo da linha (223: "Et", "qui"), o alto de
  algumas letras e o pedaço da pauta vermelha que ficou dentro das caixas de texto
  alargadas em 30/09 (este último é mais da régua que do OCR: ver ressalva abaixo).

**Ressalva:** no Graduale, parte do "texto perdido" é fio da pauta que entrou nas
caixas de texto quando elas foram alargadas para pegar as hastes (30/09). Pela D7 a
pauta fica de fora; os OCRs fazem certo em não cobri-la, mas a régua conta como texto
perdido. Não medido quanto isso pesa.
- **Graduale 221:** a maior discordância (0,94) é menor que as de duas páginas boas
  (Opus 11: 1,13; Horas 26: 1,11).
- **Horas 27:** a caixa do docTR encosta na moldura dourada no fim de duas linhas
  compridas (1,28% de figura); a diferença para o contorno do Kraken é uma lasca
  fina (0,47), menor que a de qualquer página boa.

Na grade de 8 × 7 × 57 combinações (folga, espessura, área), o melhor resultado é
19 de 22, **com** uma página boa para revisar (Opus 11), e só numa faixa estreita
(folga 0,15, espessura 0,10, área 1,60–1,70, quando a maior zona de página boa é
1,73): isso é calibrar demais nas mesmas 22 páginas. Sem nenhum revisar à toa, o
máximo é 18, que é o de hoje.

**Folga dos limites de hoje** (área mínima 1,4): a maior discordância numa página
boa é 1,13 (Opus 11), o limite está 24% acima dela; a menor discordância num erro
pego é 1,64 (Opus 3), 17% acima do limite. São os mesmos números de 29/09: as zonas
novas não mudam a decisão, só o que conta como erro.

## Arquivos

- `scripts/recalibrar.py`: régua, decisão, busca na grade e folga (não roda OCR; lê
  `saida_teste/ocr-comparar/`).
- `resultados.json`: tudo o que o script imprime, página por página.
