# D3: endireitar, girar e dividir — o nosso × o do ScanTailor

**05/10/2026 · implementador (frente de geometria, ramo `fase2-geometria`) · só mostra, nada no programa mudou por causa disto.**

Pedido do Samuel (02/10, D3): *"Não lembro; teste nas páginas de teste e me mostre - mas eu quero usar o do scantailor, pois o nosso não é tão intuitivo de se usar."*

## Em poucas frases

1. **Girar de 90 em 90 graus: nenhum dos dois faz sozinho.** No ScanTailor também é só botão (girar à esquerda, à direita, aplicar em todas / pares / ímpares). Não há o que comparar no automático; a diferença é a tela.
2. **Endireitar: nas 32 páginas, em 24 os dois acham o mesmo ângulo** (diferença de até 0,15 grau). **Nas 7 em que discordam, o ScanTailor acerta 2 que o nosso erra (Horas 11 e Horas 47), o nosso acerta 2 que o ScanTailor erra (Horas 27 e Palatino 57), e 3 ficam quase empatadas** (Horas 14, Siebmacher 9 e Opus 20).
3. **Onde o nosso erra:** nas páginas com muita pintura em volta do texto (Livro de Horas). Na Horas 11 ele **entorta** uma página que estava reta; na Horas 47 ele **deixa torta** uma página que estava torta. O motivo provável (suposição, não conferida no código): a moldura pintada pesa mais que as linhas de texto na conta do nosso; o ScanTailor tira antes as manchas compridas e mede com mais cuidado.
4. **Onde o ScanTailor erra no endireitar:** às vezes acha "quase zero" e não gira página torta (Horas 27); e muda de ideia conforme a resolução da imagem que recebe (na Horas 27, com a imagem no tamanho do escaneamento, ele acha o mesmo ângulo do nosso).
5. **Dividir a folha: os dois erram, cada um de um jeito.** O nosso parte a folha do Siebmacher (uma página só, deitada) **no meio do poema**. O ScanTailor divide a mesma folha **na beirada do livro**: a página de verdade fica inteira, mas sai uma segunda página só com a beirada. E o ScanTailor, sozinho, **corta a tabela dobrável do Opus Majus 256 em duas** e, nas páginas comuns, faz um "corte da sobra" que **passa em cima de letra** (Escola 7, Escola 35) e **leva o número da folha e as guias de fim de pauta** (Graduale 221). O nosso não faz nada disso nessas páginas.
6. **Opinião (de implementador, não é decisão):** trazer o endireitar do ScanTailor resolve as duas páginas do Livro de Horas que o nosso erra, mas piora duas outras; nas páginas comuns dá na mesma. O ganho grande que o Samuel pediu ("mais intuitivo de usar") está na **tela** (girar e corrigir à mão como no ScanTailor) e na **escolha por livro/página** de quantas páginas tem a folha — não na conta automática. Para o dividir, o automático do ScanTailor **não** deveria ser ligado de fábrica sem a pessoa conferir.

## Como foi feito

- **Nosso:** o mesmo caminho do programa para o PDF final, com as opções de fábrica do livro (dividir, cortar e endireitar marcados): a análise decide se divide (a 150 DPI), a folha é desenhada a 300 DPI, e o corte e o ângulo são medidos como o programa mede (`core/pipeline._geometria`).
- **ScanTailor:** a **mesma imagem de 300 DPI** passa pelo código original do ScanTailor Advanced v1.2.1 (o mesmo do item 1.2), compilado num programa de teste fora do projeto (`D:\programas\EditorImpressao-arquivos\ferramentas\geometria-d3-2026-10-05\`). Ele faz o que o ScanTailor faz sozinho, na ordem dele: dividir no modo automático e, em cada página, endireitar com a limpeza das sombras compridas, aceitando o ângulo só com a confiança mínima dele. **Não é a janela do ScanTailor**; é o cálculo dela, copiado sem mudança.
- **Sentido do ângulo:** conferido numa folha de mentira girada 2 graus. Na tabela, os dois estão no mesmo sentido (positivo = gira no sentido anti-horário).
- **Quem acertou:** onde discordam, a página endireitada por cada um foi **esticada 5 vezes na altura** (meio grau de torto vira dois graus e meio e aparece contra as linhas-guia) e olhada; e as linhas de texto foram medidas uma a uma (uma terceira medida, que não é de nenhum dos dois; boa só até uns 0,2 grau).

Legenda das imagens: em cima, a folha com a divisão (azul) e o corte (verde) do nosso, e a divisão/corte do ScanTailor (vermelho). No meio, a página endireitada por cada um, com linhas-guia. Embaixo, a faixa do meio ampliada.

## Página por página

### Livro de Horas 11 (frontispício iluminado)

![Horas 11](imagens/horas_p011.jpg)

![Horas 11 esticada](imagens/esticada_horas_p011.jpg)

- **Números:** nosso −0,50°; ScanTailor 0,00° (com a imagem no tamanho do escaneamento, +0,25°). Divisão: os dois deixam uma página; o ScanTailor corta 2% de sobra de cada lado, sem tocar na iluminura.
- **Onde cada um erra:** **o nosso entorta a página** (na faixa esticada, "LE GRAND" e "DANS L'HOSTEL" descem para a direita); **o ScanTailor deixa reta**, que é como ela já estava.

### Livro de Horas 47 (texto dentro de moldura pintada)

![Horas 47](imagens/horas_p047.jpg)

![Horas 47 esticada](imagens/esticada_horas_p047.jpg)

- **Números:** nosso −0,10°; ScanTailor +0,56° (no tamanho do escaneamento, +0,69°). Divisão: uma página nos dois; o ScanTailor corta 8% da esquerda (só papel e sombra da lombada).
- **Onde cada um erra:** **o nosso deixa a página torta** (as linhas descem para a direita); **o ScanTailor endireita**.

### Siebmacher 7 (uma página só, deitada, com a beirada do livro)

![Siebmacher 7](imagens/siebmacher_p007.jpg)

- **Números:** nosso divide a 57% (confiança baixa, 0,24); ScanTailor divide a 80%. Ângulo 0° nos dois.
- **Onde cada um erra:** **o nosso parte a folha no meio do poema** e da moldura; **o ScanTailor parte na beirada do livro**: a página de verdade fica inteira, mas sobra uma segunda "página" só com a beirada e o fundo preto. O certo seria uma página só.

### Siebmacher 9

![Siebmacher 9](imagens/siebmacher_p009.jpg)

![Siebmacher 9: onde o ScanTailor divide](imagens/corte_st_siebmacher_p009_esq.jpg)

![Siebmacher 9 esticada](imagens/esticada_siebmacher_p009.jpg)

- **Números:** nosso divide a 57% (0,22); ScanTailor a 82%. Ângulo: nosso 0°, ScanTailor −0,25° na página da esquerda.
- **Onde cada um erra:** a divisão, igual à Siebmacher 7 (o nosso no meio do poema, o ScanTailor na beirada do livro). O ângulo é quase empate: a medida das linhas dá o nosso um pouco mais reto (0,2° contra 0,5° de sobra), mas a olho os dois parecem retos.

### Graduale 221 (partitura torta, R5)

![Graduale 221](imagens/graduale_p221.jpg)

![Graduale 221: onde o ScanTailor corta a sobra](imagens/corte_st_graduale_p221_dir.jpg)

- **Números:** nosso +0,70°; ScanTailor +0,75°. Os dois endireitam bem.
- **Onde cada um erra:** no ângulo, nenhum. **O "corte da sobra" do ScanTailor leva o número da folha ("Cvij") e as guias no fim das pautas** (os ganchinhos à direita). O nosso não corta ali.

### Na escola de Jesus 7 (R5)

![Escola 7](imagens/escola_p007.jpg)

![Escola 7: onde o ScanTailor corta a sobra](imagens/corte_st_escola_p007_dir.jpg)

- **Números:** nosso 0,00°; ScanTailor +0,12°. Praticamente igual.
- **Onde cada um erra:** no ângulo, nenhum. **O corte da sobra do ScanTailor passa rente ao fim das linhas** e lasca a última letra ("CRISTÃ", "parece", "existência.").

### Na escola de Jesus 35 (controle: os dois acham o mesmo ângulo)

![Escola 35](imagens/escola_p035.jpg)

![Escola 35: corte da esquerda](imagens/corte_st_escola_p035_esq.jpg)

![Escola 35: corte da direita](imagens/corte_st_escola_p035_dir.jpg)

- **Números:** nosso −0,80°; ScanTailor −0,81°.
- **Onde cada um erra:** no ângulo, nenhum. **O corte da sobra do ScanTailor atravessa o texto dos dois lados** (come o começo e o fim das linhas). O nosso não divide nem corta ali.

### Opus Majus 256 (tabela numa folha dobrável deitada)

![Opus 256](imagens/opusmajus_p256.jpg)

![Opus 256: onde o ScanTailor divide](imagens/corte_st_opusmajus_p256_esq.jpg)

- **Números:** nosso −0,20°; ScanTailor −0,25° e −0,19° (uma para cada metade).
- **Onde cada um erra:** **o ScanTailor divide a tabela em duas páginas**, entre as colunas "Secunda" e "Tertia" (ele divide toda folha mais larga que alta). O nosso deixa a tabela inteira (a folha fica só um pouco abaixo da proporção em que o nosso divide).

### As outras três em que discordam no ângulo

![Horas 27 esticada](imagens/esticada_horas_p027.jpg)

- **Horas 27** (calendário): nosso +0,50°, ScanTailor 0,00°. **O ScanTailor deixa torta** (as linhas descem para a direita); o nosso endireita. Com a imagem no tamanho do escaneamento, o ScanTailor acha +0,50°, igual ao nosso.

![Palatino 57 esticada](imagens/esticada_palatino_p057.jpg)

- **Palatino 57:** nosso −0,10°, ScanTailor −0,50°. **O ScanTailor entorta um pouco**; o nosso fica reto.

![Horas 14 esticada](imagens/esticada_horas_p014.jpg)

- **Horas 14** (tabela): nosso −0,20°, ScanTailor 0,00°. Quase empate: a olho, os dois deixam a tabela praticamente reta.

![Opus 20 esticada](imagens/esticada_opusmajus_p020.jpg)

- **Opus Majus 20** (foto da estátua): nosso −0,40°, ScanTailor +0,25°, para lados opostos. **Não deu para decidir**: a página não tem linha de texto comprida, e esticar na altura não ajuda a ver linha em pé.

## Todas as 32 páginas

Ângulo no mesmo sentido para os dois (positivo = gira no anti-horário). "300 DPI" é a mesma imagem que o nosso usa para o PDF; "DPI do scan" é o PNG do gabarito no tamanho em que foi escaneado (os PDFs do Livro de Horas, do Graduale e do Marial dizem 72 DPI).

| Página | Nosso: dividir | ScanTailor: dividir | Nosso: ângulo | ScanTailor: ângulo (300 DPI) | ScanTailor: ângulo (DPI do scan) |
|---|---|---|---|---|---|
| palatino_p005 | não divide | uma página | +0.40° | +0.50° | +0.38° (400 DPI) |
| palatino_p007 | não divide | uma página + sobra (cortes a 5%, 93%) | +0.00° | +0.00° | +0.00° (400 DPI) |
| palatino_p009 | não divide | uma página + sobra (cortes a 6%, 93%) | -0.10° | +0.00° | +0.00° (400 DPI) |
| palatino_p010 | não divide | uma página + sobra (cortes a 7%, 94%) | -0.10° | -0.12° | -0.12° (400 DPI) |
| palatino_p057 | não divide | uma página + sobra (cortes a 6%, 89%) | -0.10° | -0.50° | -0.50° (400 DPI) |
| palatino_p066 | não divide | uma página + sobra (cortes a 10%, 93%) | -0.10° | +0.00° | +0.00° (400 DPI) |
| palatino_p067 | não divide | uma página + sobra (cortes a 4%, 87%) | -0.10° | +0.00° | +0.00° (400 DPI) |
| marial_p007 | não divide | uma página + sobra (cortes a 4%, 99%) | +1.20° | +1.25° | +1.25° (72 DPI) |
| graduale_p221 | não divide | uma página + sobra (cortes a 2%, 89%) | +0.70° | +0.75° | +0.69° (72 DPI) |
| graduale_p222 | não divide | uma página + sobra (cortes a 0%, 98%) | -1.00° | -0.88° | -1.06° (72 DPI) |
| graduale_p223 | não divide | uma página + sobra (cortes a 3%, 88%) | +0.80° | +0.75° | +0.75° (72 DPI) |
| horas_p011 | não divide | uma página + sobra (cortes a 2%, 97%) | -0.50° | +0.00° | +0.25° (72 DPI) |
| horas_p013 | não divide | uma página + sobra (cortes a 3%, 98%) | +0.70° | +0.62° | +0.62° (72 DPI) |
| horas_p014 | não divide | uma página + sobra (cortes a 2%, 98%) | -0.20° | +0.00° | -0.12° (72 DPI) |
| horas_p026 | não divide | uma página + sobra (cortes a 3%, 98%) | -0.10° | +0.00° | +0.00° (72 DPI) |
| horas_p027 | não divide | uma página + sobra (cortes a 2%, 97%) | +0.50° | +0.00° | +0.50° (72 DPI) |
| horas_p047 | não divide | uma página + sobra (cortes a 8%, 98%) | -0.10° | +0.56° | +0.69° (72 DPI) |
| escola_p007 | não divide | uma página + sobra (cortes a 2%, 94%) | +0.00° | +0.12° | +0.00° (200 DPI) |
| escola_p035 | não divide | uma página + sobra (cortes a 12%, 86%) | -0.80° | -0.81° | -0.81° (200 DPI) |
| siebmacher_p007 | divide a 57% | duas páginas (cortes a 80%) | +0.00° / +0.00° | +0.00° / -0.00° | +0.00° / -0.00° (400 DPI) |
| siebmacher_p009 | divide a 58% | duas páginas (cortes a 82%) | +0.00° / +0.00° | -0.25° / -0.00° | -0.19° / -0.00° (400 DPI) |
| rhetorica_p018 | não divide | uma página + sobra (cortes a 11%, 97%) | -0.10° | +0.00° | +0.00° (400 DPI) |
| rhetorica_p073 | não divide | uma página + sobra (cortes a 14%, 90%) | -0.10° | -0.25° | -0.25° (400 DPI) |
| boecio_p003 | não divide | uma página | +0.60° | +0.75° | +0.50° (150 DPI) |
| boecio_p007 | não divide | uma página | +0.00° | +0.00° | +0.00° (150 DPI) |
| boecio_p008 | não divide | uma página | -1.00° | -1.12° | -1.19° (150 DPI) |
| boecio_p022 | não divide | uma página + sobra (cortes a 0%, 95%) | -0.20° | -0.12° | +0.00° (150 DPI) |
| opusmajus_p011 | não divide | uma página | -0.30° | -0.25° | -0.25° (400 DPI) |
| opusmajus_p003 | não divide | uma página | -0.10° | +0.00° | +0.00° (400 DPI) |
| opusmajus_p020 | não divide | uma página + sobra (cortes a 19%, 89%) | -0.40° | +0.25° | +0.31° (400 DPI) |
| opusmajus_p165 | não divide | uma página | +0.30° | +0.31° | +0.25° (400 DPI) |
| opusmajus_p256 | não divide | duas páginas (cortes a 50%) | -0.20° | -0.25° / -0.19° | -0.19° / -0.12° (400 DPI) |


## Ressalvas

- **Não é a janela do ScanTailor.** É o cálculo dele (o mesmo código da v1.2.1 do item 1.2), rodado na ordem em que ele roda. Na janela de verdade, a pessoa ainda pode mudar o ângulo e a divisão; aqui só o automático foi comparado.
- **O ScanTailor muda de ideia com a resolução.** Nas páginas do Livro de Horas (escaneadas pequenas, desenhadas a 300 DPI pelo programa), o ângulo dele muda até 0,5° conforme a imagem que recebe (tabela, última coluna). Se o 2.2 trouxer o endireitar dele, a imagem e o DPI que ele recebe têm de ser escolhidos e testados.
- **O nosso corte é medido antes do ângulo; o do ScanTailor, não.** O nosso mede o ângulo na página já cortada; o ScanTailor, na página dividida, sem corte (o corte dele é outra etapa, depois). Isso explica parte das diferenças.
- **A medida "linha a linha" é aproximada** (boa até uns 0,2°) e não serve para página sem texto (Opus 20, Horas 14). O que decidiu foi a olho, nas faixas esticadas, que estão aqui para o Samuel conferir.
- **Girar não foi comparado no automático** porque nenhum dos dois tem. A queixa "o nosso não é intuitivo" é da tela, que não foi testada aqui.
- O "corte da sobra" do ScanTailor (dividir no modo "uma página + sobra") é uma etapa que o nosso não tem: o nosso só divide ou não divide. As imagens dos cortes mostram onde a tesoura dele passaria.

## Arquivos

- Imagens: `imagens/` (lado a lado, faixas esticadas, ampliações dos cortes).
- Números: `dados/medidas.json` (as 32 páginas), `dados/torto.json` (a terceira medida), `dados/tabela.md`.
- Scripts: `scripts/comparar_d3.py`, `scripts/medir_torto.py`, `scripts/zoom_cortes.py`.
- O programa de teste do ScanTailor (fora do projeto, 1 pasta nova): `D:\programas\EditorImpressao-arquivos\ferramentas\geometria-d3-2026-10-05\` (`geometria_d3.cpp`, `CMakeLists.txt`, `compilar.bat`, a pasta `build\` e `tmp\` vazia). Fica lá até o Samuel dizer se pode apagar.
