# Quadrados brancos no Melhorar e no Mágico pro — investigação

**Verificador, 10/11/2026.** Só investigação: nenhuma linha do programa foi mudada. Tudo rodou
sem janela, em cópia, pela mesma conta do programa (a prévia da tela e o PDF final).

Pedido do Samuel (10/11): "anotar erro do filtro melhorar, ele deixa a imagem pixelada, olha esses
quadrados brancos. também acontece no automatico e no magico pro, pode colocar um agente para
investigar isso." · depois: "o erro não aparece só na pagina 13, aparece em varias."

## Em uma frase

**O defeito é real e sai também no PDF, não só na tela.** O último passo do Melhorar e do Mágico pro
("o que não é letra e tem cor de papel vira branco") confunde a água, o céu e as roupas claras das
pinturas com papel, e pinta de branco; os blocos aparecem porque o arquivo do livro guarda a cor em
quadradinhos, e a resposta "é papel / não é papel" muda de um quadradinho para o outro.

Opinião (atualizada depois da comparação pedida pelo Samuel, seção 8): **a melhor saída é a C**
(procurar a gravura no Melhorar e no Mágico pro à mão, como a D-659 faz no Preto e branco, com a regra
"em volta é papel" como rede de segurança). Na prática a C sai igual à B quando "Respeitar" está
marcada. A regra sozinha (A) tira os quadrados grandes, mas deixa furos nas partes claras perto da
margem e não conserta as letras quebradas. Tudo isso é mudança de filtro: precisa do "sim" do Samuel.

Imagens (no modelo de print, resumo primeiro):

- `imagens/1-resumo-pagina-13.png` — página 13: Original, como sai hoje (Melhorar e Mágico pro) e como sairia consertado.
- `imagens/2-previa-igual-ao-pdf.png` — a prévia da tela e o PDF têm os mesmos quadrados.
- `imagens/3-livro-escola-melhorar.png` e `imagens/4-livro-escola-magico-pro.png` — oito páginas do livro, nas três situações.
- `imagens/5-outro-livro-horas-47.png` — outro livro do acervo (Livro de Horas, página 47).
- `imagens/6-comparacao-abc-melhorar.png` e `imagens/7-comparacao-abc-magico-pro.png` — a comparação A, B e C (seção 8).

## 1. Reprodução na página 13 (Jonas e a baleia)

Livro novo, aberto como a tela abre (sem o Automático), página 13, desenhada pelos dois caminhos do
programa: a prévia da tela (`core.pipeline.renderizar_com_filtro`, 150 DPI) e o PDF
(`core.pipeline._pagina_pronta`, 300 DPI). Conferido por **máquina** (medida) e por **olho** (imagens).

| como | quadrados? | quanto da gravura vira branco puro (PDF) |
|---|---|---|
| Original | não | — |
| Melhorar "bem forte", "Respeitar" marcada (print 09) | **sim, na tela e no PDF** | 25% |
| Melhorar "bem forte", "Respeitar" desmarcada | **sim** — imagem idêntica ponto a ponto à de cima | 25% |
| Mágico pro "bem fraco", "Respeitar" desmarcada, no painel | **sim** | 26% |
| Mágico pro "bem fraco", "Respeitar" desmarcada, com "Limpar a folha" do Automático (print 10) | **sim** — idêntica ponto a ponto à do painel | 26% |
| Melhorar ou Mágico pro com o Automático, "Respeitar" marcada e a gravura achada | não | 0,6% |
| Melhorar e Mágico pro no ajuste do meio ("normal") | **sim** — o ajuste não muda nada | 25% |

- **Sai no PDF final**, não só na prévia (imagem 2). Na prévia 25,7% da gravura, no PDF 25,0%.
- **O ajuste ("bem forte", "bem fraco", "normal") não importa**: o passo que pinta de branco não usa o ajuste.
- **Na página 13 a caixinha "Respeitar as gravuras achadas" não muda nada** no Melhorar e no Mágico pro
  escolhidos à mão sem o Automático: o programa não procura a gravura nesse caso (a D-659 vale só no
  Preto e branco: `core/etapas.py`, `respeitar_procura`, "Melhorar e Magico pro a mao nao procuram: a
  decisao fala do Preto e branco"). Sem gravura achada, não há o que respeitar.
- No print 10 a caixinha está desmarcada: pela D-586, "o filtro vale na página inteira", e cai no mesmo caminho.
- Quando a gravura é achada e respeitada, os quadrados somem: o conserto de 28/09 (bug 202, "quadradinhos
  na roupa do anjo") funciona **dentro da gravura marcada**. O defeito de hoje é o mesmo bug, voltando
  pelo caminho **sem marcação**.

## 2. A causa

**Arquivo e função:** `core/filtros.py`, `_limpar_o_papel_de_verdade` — o último passo de
`filtro_melhorar` e de `filtro_magico_pro` (e por isso do Automático com esses filtros).

Ele pinta de branco puro todo ponto que responde "sim" a três perguntas:

1. está longe de letra (o Sauvola não achou tinta perto)?
2. não é escuro (mais claro que 45% da luz do papel)?
3. tem cor de papel (pouca cor, saturação até 25, ou o tom amarelado do papel)?

A água e o céu da pintura são cinza-azulados, sem letra perto, nem claros nem escuros: passam nas três.
O passo foi feito para a mancha do verso numa página de texto, e numa página de texto isso está certo;
numa pintura sem marcação, não.

**Por que em quadrados:** o livro guarda cada página como JPEG, e o JPEG guarda a COR em quadradinhos de
16 por 16 pontos (24 por 24 no PDF a 300 DPI). Na pergunta 3 ("tem cor de papel?"), um quadradinho
passa e o vizinho não, inteiro. Já estava escrito no código em 28/09 ("decidir ponto a ponto sobre a cor
crua era o que fazia os quadradinhos"), mas a correção só entrou no caminho de dentro da gravura.

**As provas (medidas na página 13, PDF):**

- **Tirando só esse passo, os quadrados somem:** 25% da gravura vira branco hoje; sem o passo, 0,5%.
- **O que vira branco não é papel:** os pontos pintados dentro da gravura têm luz entre 49% e 66% do
  papel (metade dos casos); o papel de verdade da página, entre 94% e 101%.
- **As bordas caem na grade do JPEG:** a borda da pergunta "tem cor de papel?" cai na grade de 24 pontos
  em 34% das vezes; ao acaso seria 12,5%. A pergunta "não é escuro" (que não depende da cor) cai em 14,6%,
  perto do acaso. Na imagem pronta, 25,6% das bordas do branco estão na grade (o dobro do acaso), e há
  37 blocos brancos grandes (mais de meio quadrado de 24×24) dentro da gravura.
- **A miniatura de 400 pontos (a pista do CLAUDE.md §7) não é a causa:** o fundo estimado nela é liso
  por construção; com ele intacto e só o último passo desligado, os quadrados somem.

## 3. O livro inteiro e outro livro

### *Na escola de Jesus*, 199 páginas, livro novo, filtro escolhido à mão

Medida: pontos que viraram branco onde o original era pintura de tom médio (fora a beirada do scan),
sobre a página pronta. Calibrei olhando as 199 páginas em folhas de contato: a partir de 1% os buracos
se veem de longe; de 0,25% a 1% se veem ao olhar a pintura; de 0,1% a 0,25% são poucos pontos.

**Melhorar "bem forte": 110 páginas com quadrados (79 bem visíveis).**

- muito (32): 8, 13, 18, 24, 27, 29, 30, 36, 50, 51, 52, 53, 55, 65, 66, 67, 73, 74, 77, 78, 79, 101, 110, 119, 120, 121, 131, 143, 147, 153, 160, 175
- visível (47): 9, 10, 23, 25, 32, 33, 39, 40, 42, 46, 56, 57, 58, 60, 61, 68, 69, 84, 88, 96, 97, 98, 99, 103, 106, 112, 116, 118, 126, 128, 132, 134, 136, 144, 145, 146, 148, 151, 165, 174, 177, 179, 181, 186, 192, 194, 196
- poucos pontos (31): 11, 16, 19, 26, 37, 43, 45, 47, 49, 54, 64, 70, 72, 80, 86, 93, 95, 100, 102, 109, 122, 125, 140, 142, 158, 159, 168, 170, 172, 182, 184
- nada (89): as páginas só de texto, as capas e as páginas com pintura escura ou grande demais, em que a limpeza não roda (trava "tinta demais").

**Mágico pro "bem fraco": 112 páginas com quadrados (84 bem visíveis)** — praticamente as mesmas
(muito 34, visível 50, poucos 28, nada 87; a mais: 146 e 179 sobem para "muito", 16, 26, 72, 100, 125 e 142 para "visível"; a 42 desce para "poucos pontos").

### Outro livro: Livro de Horas (Luís XIV)

Páginas do gabarito 11, 13, 14, 26, 27 e 47, Melhorar e Mágico pro. **O defeito aparece na página 47**
(a pintura das bodas de Caná, com colunas e prédio claros atrás das figuras): o prédio, o céu e riscos
nas colunas e roupas claras viram branco puro (imagem 5). Nas outras, quase nada: são tabelas e
calendários dentro de moldura dourada.

## 4. O que consertaria (não aplicado)

**Proposta:** no último passo (`_limpar_o_papel_de_verdade`, só no caminho da página, o de fora da
gravura marcada), acrescentar uma quarta pergunta: **"em volta deste ponto é papel?"**. O ponto só vai a
branco se a luz do meio da vizinhança (mediana numa janela de uns 2% da página, medida na miniatura de
400 pontos, como o fundo dos filtros) passa de 80% do nível do papel **ou** se a área é de traço sobre
papel (a medida da tentativa 20, `_peso_de_traco`: xilogravura, tabela, letra). Na mancha do verso e no
vão entre as letras, a vizinhança é papel: continua indo a branco como hoje. No meio de uma pintura, a
vizinhança é a própria pintura: fica como o Melhorar a deixou.

Resultado da simulação (o mesmo programa, só com esse passo trocado, num processo à parte):

- **Página 13:** 25% da gravura em branco → 0,9% (o que sobra é a espuma, que já é branca no original).
- **Livro inteiro, Melhorar e Mágico pro:** pela primeira medida, de 110 e 112 páginas com quadrados → nenhuma. **Correção (seção 8):** essa medida só olhava a pintura de tom médio; com uma segunda medida, que olha também as partes claras (céu, nuvens), o A ainda deixa furos em 48 páginas no Melhorar e 92 no Mágico pro (hoje: 113 e 136). Os furos que sobram ficam no céu claro perto da margem (páginas 97, 99, 119).
- **Páginas sem quadrados hoje:** mudam pouco, e para melhor: roupas e lençóis brancos das pinturas (páginas 163, 71) passam a guardar a sombra em vez de virar branco chapado.
- **Boécio (mancha do verso, páginas 3, 7, 8, 22 e 33):** muda de 0% a 0,4% da página; a mancha do verso some igual. A primeira versão do conserto (sem o "ou traço") deixava a xilogravura da página 3 mais cinza; a versão com o "ou traço" não.
- **Livro de Horas 47:** melhora mas não resolve: o prédio volta, ficam riscos brancos nas colunas e na roupa clara da esquerda (a miniatura tem traço fino, e o "ou traço" deixa limpar ali).
- **Velocidade:** o último passo ficou uns 0,05 s mais lento por página a 300 DPI (Melhorar inteiro ≈ 0,9 s). Medido de forma simples no PC; precisa do filtro de velocidade do GitHub.

**O que isso mexe do que já foi aprovado:**

- A correção do "magic color" (CLAUDE.md §9: fundo relativo ao papel, peso, curva de ombro) **não é tocada**: a mudança é só no último passo.
- A limpeza da mancha do verso e do "fundo meio amarelado" (o motivo desse passo existir) continua; nas páginas de texto medidas não muda nada no miolo.
- Pela D-605, é uma mudança que altera resultado já visto (as pinturas sem marcação deixam de ir a branco): **pergunta para o Samuel antes**.

**Outra saída (decisão dele, não substitui a de cima):** estender a D-659 ao Melhorar e ao Mágico pro —
com "Respeitar" marcada, o programa procuraria a gravura também nesses filtros escolhidos à mão. Resolveria
o print 09, mas **não o print 10** (lá a caixinha está desmarcada e, pela D-586, o filtro vale na página
inteira) nem a página com a gravura que o programa não acha.

**Risco do conserto proposto:** (a) a beirada da pintura que encosta na margem branca ainda pode ganhar
manchas brancas numa faixa de uns 2 a 3 mm (visto nas páginas 27 e 74); (b) na faixa escura de scanner
na beirada da página, um pouco menos de branco (até 0,8% da página, só nos 6% da beirada); (c) pinturas com
traço fino (Livro de Horas) continuam com riscos brancos; (d) os números 80% e 2% são meus, escolhidos
nesta investigação, sem rodar as 32 páginas do gabarito.

## 5. Ressalvas

1. **O conserto é simulação**: trocado só dentro de um processo de teste (`scripts/candidato.py`), sem teste em `tests/`, sem rodada do GitHub, sem o gabarito inteiro. Antes de entrar no programa: teste de reversão (página 13: falha hoje, passa com o conserto), as provas das decisões (`tests/test_decisoes*.py`), o gabarito e o filtro de velocidade.
2. **Livro de Horas 47 fica pela metade** com o conserto proposto (ver acima).
3. **A medida do livro inteiro é feita na miniatura da página pronta (75 DPI)**: serve para separar páginas com e sem buracos (calibrada olhando as 199 páginas), não para comparar números finos.
4. **Achado à parte, não investigado:** no Livro de Horas, Melhorar "bem forte", a margem de fora da moldura sai com manchas cinza e brancas misturadas (imagem 5, página inteira à esquerda). Parece da mesma família (a limpeza decidindo por pedaços), mas o defeito é o contrário: papel que fica cinza. O conserto proposto não muda isso.
5. Não abri o programa na tela do Samuel: tudo pela conta do programa, sem janela (`QT_QPA_PLATFORM=offscreen`), com dados num `LOCALAPPDATA` à parte. O que a tela mostra é desenhado por essa mesma conta (`renderizar_com_filtro`), mas não pilotei a janela.
6. Os scripts em `scripts/` gravam os dados de teste numa pasta `dados/` ao lado deles; foram rodados de uma cópia fora do projeto.

## 6. Para a Lista de bugs

- **10/11/2026 — Quadrados brancos nas pinturas no Melhorar e no Mágico pro sem gravura marcada** (livro
  novo com filtro à mão, ou "Respeitar" desmarcada). Sai também no PDF. *Na escola de Jesus*: 110 de 199
  páginas; Livro de Horas: página 47. Causa: `core/filtros.py`, `_limpar_o_papel_de_verdade` (cor
  decidida sobre a cor crua do JPEG, em blocos de 16×16). Mesmo bug do 202 (28/09), pelo caminho sem
  marcação. Prints: `relatorios/testes-guiados/2026-11-10-sessao-5/prints/09-...` e `10-...`; imagens
  deste relatório.

## 7. Como medir de novo

`scripts/reproduzir.py` (página e variantes, prévia e PDF), `scripts/medir.py` (blocos e grade),
`scripts/partes.py` (as três perguntas), `scripts/varrer.py` (livro inteiro), `scripts/medir_miniaturas.py`
(a medida por página), `scripts/candidato.py` (o conserto simulado; `CANDIDATO=1`), `scripts/montar.py`
(as imagens). As medidas por página estão em `medidas/`.

## 8. Comparação A, B e C (pedido do Samuel, 10/11: "faça um teste com os dois para ver qual se sai melhor")

As três saídas foram simuladas em script, pela mesma conta do programa (o corpo do PDF,
`core.pipeline._pagina_pronta`, 300 DPI). Livro novo, filtro escolhido à mão e "Respeitar" marcada.
Nenhuma linha do programa mudou.

- **A** — a regra "em volta é papel" no último passo (seção 4), sem procurar a gravura.
- **B** — o Melhorar e o Mágico pro à mão procuram a gravura como a D-659 faz no Preto e branco
  (`core/etapas.py`, `respeitar_procura` valendo também nesses dois filtros), e a gravura achada fica
  protegida. A regra de hoje não muda. A procura é a de sempre do programa (`garantir_selecao`).
- **C** — os dois juntos.

### Em uma frase

**O B (e o C, que sai igual a ele) se sai muito melhor que o A.** Some com os quadrados, deixa o céu claro
inteiro e ainda conserta as letras que o Melhorar de hoje quebra. O preço é tempo: cerca de 4 s a mais
na primeira vez que cada página é desenhada. Minha escolha é a **C**: é o B, mais a regra como rede de
segurança para quando a caixinha está desmarcada (o print 10) ou quando a procura não acha a pintura.

### 1. *Na escola de Jesus* inteiro (199 páginas)

Primeira medida: pintura de tom médio que virou branco, a mesma das seções 3 e 4.

| | Melhorar "bem forte" | Mágico pro "bem fraco" |
|---|---|---|
| hoje | 110 páginas (32 muito, 47 visível, 31 poucos pontos) | 112 (34, 50, 28) |
| A | 0 | 0 |
| B | 2 (119 visível, 68 poucos pontos) | 2 (as mesmas) |
| C | 2 (as mesmas) | 2 (as mesmas) |

Segunda medida, que também vê as partes claras da pintura (céu, nuvens): dentro da caixa da pintura,
os pontos que viraram branco puro onde o original não era branco de papel. A primeira medida não via
isso: é a correção da seção 4.

| páginas com furo de 2% ou mais (de 0,5% ou mais) | Melhorar | Mágico pro |
|---|---|---|
| hoje | 113 (154) | 136 (169) |
| A | 48 (100) | 92 (139) |
| B | 16 (68) | 16 (67) |
| C | 16 (68) | 16 (67) |

As 16 do B e do C, olhadas uma a uma, são quase todas brilhos que já são brancos no original e o papel
de dentro de desenho de traço (a basílica da página 43), que deve mesmo ficar branco. A pior de verdade é
a 173 (o céu em volta dos anjos). O A deixa furos no céu claro perto da margem: páginas 97, 99, 119.

**As letras:** o Melhorar e o Mágico pro de hoje quebram o "i" e o "t" finos, e o A não muda isso (é o
mesmo passo; em volta da letra é papel). O B e o C não quebram, porque a letra achada recebe o
tratamento de letra. Tinta da letra que virou branco:

- página 13: hoje 1,2%, A 1,2%, B e C 0,0%
- página 97: hoje 4,1%, A 4,1%, B e C 0,4%
- página 119: hoje 1,1%, A 1,1%, B e C 0,0%

Na miniatura, "Assim" vira "Ass m".

**B e C, um contra o outro:** nas 199 páginas, nenhuma difere em mais de 0,05% dos pontos. Com a
gravura achada em 197 páginas (só as páginas 4 e 197, de texto, ficam sem), a regra do C quase não
tem onde agir.

### 2. Livro de Horas, página 47

| | hoje | A | B | C |
|---|---|---|---|---|
| branco na pintura (medida 1) | 1,10% (113 blocos) | 0,51% (55) | 0,04% (3) | 0,04% (3) |

Olhado: hoje e A deixam riscos brancos nas colunas e no prédio; **B e C deixam a pintura inteira**,
com o céu e o prédio de trás.

### 3. Páginas do gabarito com gravura (Melhorar; o Mágico pro dá os mesmos números)

| página | hoje | A | B | C | olhado |
|---|---|---|---|---|---|
| Escola 7 | 1,37 | 0,20 | 0,01 | 0,01 | B/C inteiros |
| Escola 35 | 1,25 | 0,25 | 0,02 | 0,02 | B/C inteiros |
| Palatino 5 (retrato) | 1,27 | 1,26 | 5,17 | 5,16 | hoje e A: pontinhos brancos no retrato; B/C: papel branco entre os traços, como pede a regra da Fase 1 (o número sobe porque esse papel vai a branco) |
| Palatino 9 | 1,82 | 1,77 | 1,57 | 1,53 | parecidos |
| Horas 11 / 13 | 0 / 0,10 | 0 / 0,08 | 0,01 / 0,07 | 0,01 / 0,06 | parecidos |
| Rhetorica 73 | 0,10 | 0,06 | 13,99 | 13,97 | hoje e A: papel continua bege (a limpeza não roda nessa página); B/C: papel branco, mas com **contorno bege em volta das letras** |
| Opus 3 / 165 / 256 | 0,17 / 0,18 / 0,88 | igual a hoje | 0,17 / 0 / 0,13 | igual ao B | parecidos |
| Opus 20 (foto) | 0 | 0 | 0,04 | 0,04 | parecidos |

### 4. Boécio (mancha do verso)

Páginas 3, 7, 8, 22 (gabarito) e 33. No B e no C a limpeza **não piora**: vai a branco um pouco mais do
que hoje (página 33: 4,5% → 5,4% da página), e a mancha do verso some igual, olhado. No A, quase igual a
hoje (0% a 0,4% da página muda).

### 5. Tempo por página a 300 DPI

Medido alternado, girando a ordem: páginas 13, 8, 27, 119 e 6. Melhorar com duas rodadas (10 medidas
cada); Mágico pro com uma (5 medidas cada). Nenhum outro processo meu rodando, mas o Samuel estava
usando o PC.

| | hoje | A | B | C |
|---|---|---|---|---|
| Melhorar | 1,51 s | 1,68 s | 5,95 s | 5,83 s |
| Mágico pro | 1,91 s | 1,73 s | 6,25 s | 6,20 s |

O A fica dentro do ruído. O B e o C custam uns **4,4 s a mais por página**, que é a procura da gravura,
feita aqui do zero em cada medida. No programa a marcação achada fica guardada na página, então os
desenhos seguintes não deveriam pagar de novo (não medi isso). O teste de velocidade que vale é o do GitHub.

### 6. O caso do print 10 (caixinha desmarcada)

No **B**, com "Respeitar" desmarcada, nada é procurado (D-586: "Desligada, o filtro vale na página
inteira"): a página sai **igual a hoje, com os quadrados**. Medido na página 13, Mágico pro: 5,95%,
o mesmo de hoje. No **C**, a regra segura: sai como o A (0,21%).

### Opinião e ressalvas

- **Melhor: C** (na prática B + rede de segurança). Conserta os quadrados, o céu claro, as letras
  quebradas, a página 47 das Horas e o papel de dentro do retrato do Palatino.
- **O B e o C mudam a cara de toda página com Melhorar ou Mágico pro à mão e "Respeitar" marcada,
  não só a das pinturas.** As letras ficam com o tom do original, menos "escurecidas"; o papel em volta
  da letra vai a branco; a gravura fica com o tratamento da gravura. É o mesmo resultado que esses
  filtros já dão depois do Automático com a gravura achada. Nas 199 páginas, C e A diferem em 11,6% dos
  pontos em média no Melhorar e 6% no Mágico pro. Pela D-605 isso é pergunta para o Samuel.
- Rhetorica 73 no B/C: papel branco com contorno bege nas letras. Hoje o papel fica todo bege.
- O B só vale com "Respeitar" marcada. É a D-659 estendida a dois filtros novos: decisão do Samuel.
- Tudo é simulação (`scripts/reproduzir.py`, `instalar_b`; `scripts/candidato.py`; `scripts/comparar_paginas.py`;
  `scripts/tempo.py`; `scripts/medir_pintura.py`), sem teste em `tests/` nem rodada do GitHub.
- As letras quebradas do Melhorar de hoje são um **achado novo** desta comparação: vêm do mesmo passo
  (`_limpar_o_papel_de_verdade`). Sem esse passo, a página 13 sai com as letras inteiras. Vale também
  como bug para a Lista.
