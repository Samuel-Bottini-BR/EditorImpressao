# Consertos de 05/10 (2): página em Original com "só neste pedaço", o "(2)" que virava erro, e o aviso e o botão do pedaço na aba Marcar

Ramo `pedaco-e-salvo-2-2026-10-05` (criado do `fase-1` em `19c1ba7`). Três itens, um commit cada. O implementador não junta nada ao `fase-1`.

| Item | Commit | Tipo de teste |
|---|---|---|
| 1. Página em Original obedece ao "só neste pedaço" | `294cb91` | máquina + olho (Escola 7) |
| 2. O "(2)" com o PDF antigo aberto vira "Ficou pronto!" | `f058452` | máquina + print da tela |
| 3. Aviso e botão "Ajustar o pedaço à figura" na aba Marcar | `30fc7c0` | máquina + prints da aba Marcar |

## 1. Página em Original obedece ao "só neste pedaço" (commit `294cb91`)

**O que estava errado:** numa página em Original, um pedaço marcado na aba Marcar com Preto e branco, Melhorar ou Mágico pro era ignorado, sem aviso. A página saía toda como veio.

**O que mudou (Samuel, conferência 13: "Sim, do mesmo jeito"):** do mesmo jeito do conserto do Preto e branco (`60d8c58`). O pedaço obedece inteiro ao filtro escolhido para ele, inclusive o papel pego junto, com a borda que foi desenhada. O resto da página fica Original, ponto por ponto. Página em Original sem pedaço: sai exatamente como antes.

**O que não mudou, de propósito:**

- **"Tirar o fundo":** continua sem obedecer ao pedaço. A gerente ainda está perguntando ao Samuel. Há um comentário no código dizendo isso.
- **"Limpar a folha" desligado:** o pedaço continua sem valer. **Não é a mesma causa.** Desligar "Limpar a folha" é a escolha do livro de não passar filtro em página nenhuma. Com ela desligada, a tela de conferir nem monta as abas Marcar e Filtro. O pedaço ficaria invisível, sem como ver nem tirar, e mesmo assim mudaria o PDF. Está explicado em `core/pipeline.py::_filtrar`. Se o Samuel quiser o contrário, a mudança é ali, e na tela, para o pedaço aparecer.

**O antes e depois (abrir para conferir):** a Escola de Jesus 7 com a página em Original e o bloco de texto de cima marcado com "só neste pedaço: Preto e branco". O livro foi processado de verdade e a página foi lida de volta do PDF.

- `escola7-pagina.jpg`: Original (o pedaço em laranja) | antes (o pedaço é ignorado) | depois (o bloco de texto em preto e branco; o resto, incluindo a pintura, como veio).
- `escola7-pedaco.jpg`: o bloco de texto de perto.
- `escola7-detalhe1.jpg`: o título e as primeiras linhas, perto do tamanho real.
- `escola7-detalhe2.jpg`: a beirada de baixo do pedaço. O preto e branco acaba numa linha reta, e o papel creme do Original começa logo abaixo.

Números (`medidas.json`): antes, a página saía igual ao Original em todos os pontos. Depois, dentro do pedaço só há dois tons (preto e branco). Fora do pedaço há 0 pontos diferentes do Original. Processar a página levou 1,9 e 1,9 s antes, e 1,8 e 2,0 s depois. O PDF dessa página caiu de 6,6 para 5,3 MB, porque o branco comprime melhor que o papel creme.

**Prova de que as páginas sem pedaço não mudaram:** as 32 páginas do gabarito em Original, Preto e branco, Melhorar e Mágico pro, pelo mesmo caminho do botão "Confirmar e processar", comparadas ponto a ponto com uma cópia inteira do `19c1ba7`: **128 de 128 imagens idênticas** (32 em cada filtro). O tempo de processar as 32 páginas ficou dentro do ruído: Original 145,2 → 151,0 s, Preto e branco 142,6 → 134,5 s, Melhorar 246,9 → 227,5 s, Mágico pro 260,5 → 230,2 s. O caminho dessas páginas é o mesmo de antes (`comparacao-32-paginas.json`).

## 2. PDF antigo aberto em outro programa: o "(2)" passa a ser "Ficou pronto!" (commit `f058452`)

**O que estava errado (achado do verificador):** com "substituir o antigo" e o PDF antigo aberto no leitor de PDF, o programa gravava o novo como "nome (2).pdf", o que estava certo. Mas a tela tratava o caso como erro. Aparecia a caixa "Um momento", e a tela voltava para Conferir em vez de "Ficou pronto!". O cartão não virava "PDF gerado", o destino guardado continuava com o nome antigo e o `erros.log` ganhava o rastro técnico.

**O que mudou (exceção da gerente para mexer em `ui/`):** o caso agora conta como sucesso.

- Aparece a tela "Ficou pronto!", com o nome "(2)". Embaixo de "Salvo em" vem uma frase: *"O arquivo antigo, "X.pdf", estava aberto em outro programa (o leitor de PDF, por exemplo) e não pôde ser substituído. Ele ficou como estava, e o PDF novo foi salvo ao lado dele com o nome acima."* "Abrir a pasta" e "imprimir agora" usam o "(2)".
- Nenhuma caixa de erro aparece. O cartão vira "PDF gerado", e o destino guardado, no projeto e no cartão, passa a ser o "(2)".
- Nada vai para o `erros.log`.
- Sem o antigo preso, a tela fica como sempre, sem frase nenhuma. A frase de um livro anterior também não sobra.

Prints (tela sozinha, sem janela à vista, 1280 × 657): `pronto-com-2.png` (com a frase) e `pronto-normal.png` (como sempre).

## 3. Aba Marcar: aviso de papel em volta do pedaço e o botão "Ajustar o pedaço à figura" (commit `30fc7c0`)

**O pedido (Samuel, conferência 13):** "(b) e (c) juntas - Mas caso ele não queira mudar, fica do jeito que está."

**O que aparece na tela:** só numa página que tem um pedaço em retângulo com "só neste pedaço" num filtro diferente do da página, surge uma linha nova na aba Marcar, embaixo de "Foto:":

`Pedaço:  [ícone] Ajustar o pedaço à figura   Sobrou papel em volta da figura (17% do pedaço): pode sair uma faixa.`

- **(c) O botão** encolhe o retângulo até a figura. Ele só encolhe: nunca cresce, nunca anda, e não mexe em tipo, filtro nem no resto da marcação. O ajuste entra no Histórico ("Página N: pedaço ajustado à figura"), e o Desfazer devolve o retângulo de antes. O ícone é desenhado (um retângulo tracejado com um menor cheio dentro e quatro setinhas para dentro), sem emoji. A dica do mouse explica o que o botão faz e que dá para desfazer.
- **(b) O aviso** é uma frase discreta, em cinza, que aparece só quando sobra muito papel. A dica do mouse traz a explicação inteira e diz que, se o Kaique não quiser mudar, pode deixar como está. Com o pedaço já justo, a frase é "O pedaço já está justo na figura." e o botão fica apagado.
- Nada muda sozinho. O cálculo fica em `core/ajustar_pedaco.py`, sem nenhum `import` de `ui/`.

**Como o programa acha "a figura", em palavras simples:** a cor do papel é tirada das partes claras da página fora do retângulo. Dentro dele, o que tem cor bem diferente do papel é tinta. Pontinhos soltos de sujeira são ignorados. A tinta que está perto uma da outra forma um grupo, e a figura é o maior grupo. Legenda e linha de texto soltas, bem menores, ficam de fora. A conta é feita na página **sem filtro**, reduzida a 1000 pontos no lado maior, e leva uns 0,05 s.

**O "muito", calibrado na Escola 7 e na Opus 20 (`calibracao.json`, `cal-*.jpg`):** a medida é a parte do retângulo que é papel em volta da figura. O aviso aparece a partir de **5%**, que numa figura do tamanho da da Escola 7 é uma faixa de uns 2 mm em volta toda.

| Página e retângulo | Papel em volta | Avisa? |
|---|---|---|
| Escola 7, retângulo da conferência 13 | 2,2% (faixa de ~1,5 mm em cima e à esquerda) | não, mas o botão tira a faixa |
| Escola 7, o do verificador | 2,1% | não |
| Escola 7, folga larga (pega a linha de texto de cima e a legenda) | 17,8% | sim; o ajuste fica justo na pintura, sem o texto nem a legenda |
| Escola 7, retângulo por dentro da pintura | 0% | não; nada a ajustar |
| Opus 20, retângulo da conferência 13 | 0,6% | não |
| Opus 20, retângulo da página quase inteira | 1,2% na prévia, 8,1% no PDF | ver ressalva |

**Prints da aba Marcar** (a tela de conferir de verdade com a Escola 7 em Preto e branco e a pintura em "só neste pedaço: Original", com folga larga; sem janela à vista, 1280 × 760):

- `marcar-1-aviso.png`: a linha "Pedaço:" com o aviso de 17%. O retângulo marcado pega o papel e o texto em volta da pintura.
- `marcar-2-ajustado.png`: depois de clicar. O retângulo ficou justo na pintura, a faixa sumiu da prévia e a frase diz "O pedaço já está justo na figura."
- `marcar-3-desfeito.png`: depois do Desfazer. O retângulo voltou como estava.

## Testes de máquina

- Novos: `tests/test_so_neste_pedaco_no_original.py` (16), `tests/test_antigo_aberto_vira_pronto.py` (5), `tests/test_ajustar_pedaco.py` (13) e `tests/test_ajustar_pedaco_na_aba_marcar.py` (4). Os 10 dos itens 1 e 2 que cobram o conserto **falham no `19c1ba7`**; os outros cobram o que não pode mudar.
- `pytest tests` inteiro: **1449 passaram, 7 pularam, 0 falhas** (7 min 32 s). Os 7 que pularam: 6 do Kraken ("motor do Kraken não montado": o motor fica fora do git e não existe nesta cópia) e 1 que só roda com `OCR_22=1` (roda o Kraken, ~5 min). Nenhum é destes itens.
- `teste_botoes.py`: **132 ações, 0 falhas**. Rodou por um embrulho que troca a pasta de trabalho dele (`saida_teste\botoes`, que nesta cópia é atalho para a pasta original e que o script apaga e recria) por uma pasta no scratchpad. O código do script não mudou. Ele não clica no botão novo da aba Marcar, porque a linha só aparece com um pedaço com outro filtro. Quem cobre o botão é `tests/test_ajustar_pedaco_na_aba_marcar.py`.

## Opinião do implementador

Os três fazem o que foi pedido. Na Escola 7 em Original, o bloco de texto sai em preto e branco e a pintura fica como veio. O "(2)" deixa de assustar: o Kaique vê "Ficou pronto!" e lê por que o nome mudou. O botão da aba Marcar acerta a pintura da Escola 7 mesmo com folga larga, deixando de fora o texto e a legenda. O ponto que mais merece a decisão do Samuel é o limiar do aviso. Com 5%, o retângulo da conferência 13 (a faixa fina que ele viu) não avisa, embora o botão a tire. Se ele quiser o aviso também aí, é baixar para 2%, mas então quase todo retângulo desenhado à mão vai avisar. PRONTO PARA CONFERIR, a decidir pelo Samuel.

## Ressalvas

- **Nada foi pilotado na janela de verdade com mouse nativo.** Os prints são da tela sozinha (TelaFinal, TelaConferir), sem janela à vista. O "(2)" foi testado com a troca do arquivo simulada (`os.replace` recusando o antigo) e o processamento de verdade, mas não com um leitor de PDF de verdade segurando o arquivo. Fica para o verificador.
- **Item 1, o pedaço em Preto e branco numa página em Original** usa a força do preto guardada na página (50 se ninguém mexeu) e as opções de fábrica do Preto e branco (escolha automática do jeito, "limpar poeirinha" ligado). O pedaço não tem medidor próprio, e no Melhorar e no Mágico pro sempre foi assim também.
- **Item 1, faixa branca:** com o pedaço em Preto e branco numa página em Original, o papel de dentro do retângulo sai branco ao lado do creme. É o inverso da faixa creme (`escola7-detalhe2.jpg`). O botão "Ajustar o pedaço à figura" também vale aí: ele encolhe até o bloco de texto.
- **Item 1:** no Preto e branco do pedaço, a pintinha laranja perto de "antes" (linha 2) vira um ponto preto (`escola7-detalhe1.jpg`). É o próprio Preto e branco, igual ao da página inteira nesse filtro.
- **Item 3, o limiar do aviso (5%) é uma decisão a confirmar.** Ele foi calibrado em duas páginas só (Escola 7 e Opus 20). Com 5%, a faixa fina do retângulo da conferência 13 não avisa (o botão a tira).
- **Item 3, a conta pode errar para os dois lados**, e por isso só sugere. (a) Um pedaço da figura de verdade que esteja longe do resto (mais de ~1,5 mm) e seja pequeno (menos de 1/4 do maior) fica de fora do retângulo. O Kaique vê na hora e desfaz. (b) Uma mancha grande colada na figura, ou a borda escura da página encostando na figura e na legenda, segura o ajuste e ele encolhe menos. Foi o caso da Opus 20 com o retângulo pegando a página quase inteira: na prévia a legenda ficou dentro (1,2%, sem aviso); a 300 DPI ela saiu (8,1%). A aba Marcar faz a conta na página reduzida a 1000 pontos.
- **Item 3, só retângulos:** pedaço feito com oval, laço, polígono ou pincel não ganha aviso nem botão. Ajustar mudaria a forma escolhida.
- **Item 3, céu muito claro:** uma figura com a beira quase da cor do papel (céu desbotado sem moldura) pode perder essa beira no ajuste. Na Escola 7 isso não aconteceu.
- **Item 3, altura da aba Marcar:** quando aparece, a linha "Pedaço:" ocupa mais uma linha numa aba que já é apertada. No print de 760 de altura, os textos dos botões já aparecem um pouco cortados, inclusive os que já existiam.
- **Item 3, desfazer:** o ajuste entra no Histórico, mas desenhar o retângulo continua fora dele (antigo, achado do verificador). Desfazer depois do ajuste devolve o retângulo de antes do ajuste. Um segundo Desfazer não apaga o retângulo desenhado: ele desfaz a ação registrada anterior.
- **Velocidade:** o teste oficial (`teste_velocidade.py`) não foi rodado. A indicação está nas 32 páginas acima, iguais e sem lentidão. Na aba Marcar, a conta custa ~0,05 s por mudança na marcação, e só em página com pedaço de outro filtro.
- **Pasta `saida_teste` (atalho para a original):** o `pytest` grava ali pastas próprias de cada rodada (com data e número) e as apaga no fim, como sempre fez. Ele não apaga nada que não tenha criado. O `teste_botoes.py` foi desviado para o scratchpad (ver acima).
- As imagens do antes e depois do item 1 foram geradas com o filtro do `19c1ba7` posto no lugar do de hoje, dentro do programa de hoje. A prova das 32 páginas, essa sim, usou uma cópia inteira do `19c1ba7`.

## Bugs para a Lista de bugs (05/10/2026)

- Nenhum novo de verdade. Lembrete do que se viu: os textos dos botões da aba Marcar aparecem cortados em altura com a janela baixa (print `marcar-1-aviso.png`, 1280 × 760, nas linhas "Marcação:" e "Foto:", que já existiam).

## Ideias para a Lista de espera

- Pôr o "desenhar um pedaço" no Histórico, para o Desfazer valer igual para tudo na aba Marcar.
- Aviso e botão também para pedaço feito com laço ou polígono (ajustar sem mudar a forma, só cortando o papel da beira).
