# Melhorias tentadas

Uma entrada por mudança, aceita ou revertida. As revertidas ficam registradas
de propósito: saber o que não funcionou vale tanto quanto saber o que funcionou.

Cada entrada diz qual número a mudança queria melhorar, o que aconteceu com
todos os outros, e a decisão.

---

## Tentativa 1 — o contraste local deixa de agir no papel

**Data:** 30/07/2026
**Situação:** aguardando decisão do Samuel
**Número atacado:** ruído de fundo do Mágico pro, o pior da linha de base
(2,25 no original contra 8,04 depois do filtro)

### O que estava acontecendo

O Mágico pro aplica realce de contraste local (CLAHE) na folha inteira. Onde a
folha é só papel não há o que realçar, então ele pega o grão do escâner e o
amplia. De quebra, puxa o papel para baixo — no filtro que deveria justamente
embranquecê-lo.

Foi medido desligando um passo por vez, em cinco páginas:

| Variante | Ruído | Fundo (255 = branco) |
|---|---|---|
| Como estava | 13,57 | 196,8 |
| **Sem o contraste local** | **6,35** | **219,3** |
| Sem a nitidez | 10,10 | 196,8 |
| Sem a saturação | 13,46 | 201,4 |
| Sem o empurrão para o branco | 13,10 | 195,5 |

O contraste local responde por mais da metade do ruído e por todo o
escurecimento. A saturação e o empurrão para o branco não têm nada a ver.

### O que foi mudado

O realce de contraste local passou a ser pesado em vez de aplicado por igual:
cheio no conteúdo escuro, nenhum no papel. A rampa começa em 80% do nível do
papel. Esse valor foi escolhido medindo: abaixo dele não há mais ganho, só
perda de contraste nas gravuras.

Nada mudou na tela. Nenhum controle novo, nenhum nome diferente.

### O que aconteceu no acervo inteiro

| Número (Mágico pro) | Antes | Depois | |
|---|---|---|---|
| Ruído do fundo | 8,04 | **3,68** | melhorou 54% |
| Nível do fundo | 209,9 | **215,4** | melhorou |
| Nitidez | 3044 | 3144 | melhorou |
| Vazios internos | 5218 | 3263 | ver observação |
| Transição da borda | 2,24 | 1,39 | **piorou** |

Ocorrências de defeito, no acervo todo:

| Defeito | Antes | Depois |
|---|---|---|
| O fundo ficou mais sujo | 57 | **32** |
| O fundo escureceu | 15 | 13 |
| O traço afinou demais | 3 | **1** |
| A borda das letras borrou | 2 | **0** |
| As letras entupiram | 5 | 5 |
| A borda virou degrau (serrilhado) | 5 | **13** |
| **Total** | **68** | **51** |

### Observação sobre os vazios internos

A queda de 5218 para 3263 parece perda, mas não é. O filtro antigo inventava
buracos a partir do grão amplificado. Em toda página de texto o número novo se
aproxima do original, em vez de se afastar dele:

| Página | Original | Antes | Depois |
|---|---|---|---|
| Marial p1 | 229 | 7491 | 645 |
| Graduale p251 | 88 | 771 | 177 |
| Marial p605 | 1216 | 5282 | 2386 |

E o critério que olha página por página, "as letras entupiram", ficou em 5
antes e 5 depois. Nenhuma página perdeu miolo de letra de verdade.

### A piora é real

O serrilhado subiu de 5 para 13 páginas. Foi verificado se não era vício da
medida — a régua contava como rampa qualquer pixel de tom intermediário da
página, e papel ruidoso enche isso. Medindo só junto do contorno da letra, a
contaminação some, **mas a piora continua**: a rampa cai de 0,86 para 0,49
pixel. Segurar o contraste local deixa o papel liso ao redor da letra, e a
borda fica mais dura.

Também foi testado se a causa era o empurrão para o branco. Não é: tirá-lo
piora ainda mais a rampa.

### Decisão

**Aceita.** O Samuel viu as imagens do antes e do depois, inclusive da página
que o número acusou de ter piorado, e nela o resultado a olho é melhor: o
fundo sai limpo e as letras ficam iguais. A "escadinha" medida vai de 1,20 para
0,65 pixel — os dois valores já são menores que um pixel, e a 300 DPI isso não
se enxerga. O limite de 0,7 que eu havia escolhido para a régua está severo
demais para escaneamento que já vem com a borda dura de origem.

---

## Tentativa 2 — o ponto de preto deixa de arrastar o papel

**Data:** 30/07/2026
**Situação:** medindo no acervo
**Número atacado:** o fundo escurecendo no filtro Melhorar, o pior estrago
isolado da linha de base — na Rhetorica p446 o papel caía de 208 para 64 numa
escala em que 255 é branco

### O que estava acontecendo

O último passo do Melhorar aprofunda os pretos. Ele pegava o tom mais escuro da
página, mandava para 0, e reescalava tudo tomando o branco absoluto como
âncora. Numa página cujo papel já é escuro — uma gravura, uma folha muito
envelhecida — essa conta arrasta o meio da escala inteiro para baixo junto.

Medido desligando um passo por vez:

| Página | Original | Filtro completo | Sem aprofundar pretos |
|---|---|---|---|
| Rhetorica p446 | 208,1 | **64,5** | 210,9 |
| Boécio p50 | 159,9 | **89,5** | 164,1 |
| POINTS p16 | 141,5 | **96,7** | 138,0 |

Era ele sozinho. O balanço de branco, que eu suspeitava, nem chega a rodar
nessas páginas: ele desiste por não achar papel branco à vista.

### O que foi mudado

A âncora passou a ser o nível do papel, e não o branco absoluto. O preto vai
para 0 e o papel fica exatamente onde estava; só a parte de baixo da escala é
esticada.

### Resultado imediato

| Página | Original | Antes | Depois |
|---|---|---|---|
| Rhetorica p446 | 208,1 | 64,5 | **181,6** |
| Boécio p50 | 159,9 | 89,5 | **157,4** |
| POINTS p16 | 141,5 | 96,7 | **138,2** |
| Boécio p26 (texto) | 204,0 | 221,9 | **222,9** |

Os 68 testes existentes continuam passando. A medição no acervo inteiro está
em andamento.

---

## Investigação — os 18 binarizadores do DoxaPy

**Data:** 30/07/2026
**Situação:** medido; nenhuma troca feita ainda
**Motivo:** o Kaique reclamou de uma página em que o preto e branco ficou menos
legível que o original. O DoxaPy já instalado traz dezessete alternativas ao
Sauvola, várias feitas para documento histórico degradado.

Medidos 17 algoritmos em 36 páginas do acervo, com a mesma régua.

| Algoritmo | Vazios | Fundo | Tinta | Piorou |
|---|---|---|---|---|
| OTSU | 2540 | 255,0 | 0,3495 | 0 |
| PHANSALKAR | 5096 | 251,4 | 0,2464 | 2 |
| WELLNER | 2086 | 253,7 | 0,1744 | 2 |
| BATAINEH | 1834 | 252,7 | 0,1975 | 2 |
| **SAUVOLA (hoje)** | 1327 | 254,0 | 0,1662 | 3 |
| ISAUVOLA | 1320 | 254,6 | 0,1604 | 3 |
| NICK | 1175 | 254,6 | 0,1423 | 3 |
| GATOS | 778 | 254,6 | 0,1438 | 5 |
| NIBLACK | 6385 | 183,1 | 0,5120 | 24 |

### Por que não troquei nada

**Os números sozinhos enganam aqui, e a régua tem um ponto cego.** O OTSU marca
zero piora, mas guarda o dobro de tinta do Sauvola. Em papel envelhecido isso
quer dizer manter a mancha como se fosse letra, e nenhum dos critérios atuais
pega isso. Falta um número para "guardou a sujeira".

Olhando as imagens, o resultado se inverte conforme a página:

**No Palatino** (manual de caligrafia, letra gótica pesada) o OTSU sai sólido e
limpo, enquanto Sauvola, Phansalkar, Wellner e Bradley **quebram o traço** — as
letras ficam salpicadas de branco por dentro. A janela local, dimensionada para
linha de texto corrente, fragmenta letra de corpo grande.

Isso confirma o que a literatura diz: Sauvola é melhor em ruído de fundo
uniforme, Wolf em baixo contraste. Não existe um vencedor único — **a escolha
certa depende da página**, não do livro.

### Um defeito grave descoberto de passagem

No **Graduale**, manuscrito do século XIV com pautas em vermelho e neumas
pretos, **os dezessete algoritmos transformaram as linhas vermelhas em barras
pretas grossas**. O Wellner chegou a apagá-las, mas levou junto metade das
notas.

Para um instituto de preservação isso é perda de informação: a rubricação
vermelha é parte do documento. A causa é a conversão para cinza, que trata
vermelho como escuro. O DoxaPy oferece oito métodos de conversão
(LABDIST, LUSTER, MINAVG, VALUE, LIGHTNESS, BT601, BT709, BT2100) e algum deles
deve tratar o vermelho de outra forma. A investigar.

---

## Pendência da régua

A medida de transição conta pixels de tom intermediário em toda a página, e
papel ruidoso infla o número. Deve passar a contar só junto do contorno da
letra. Não muda o veredito da Tentativa 1, mas muda a magnitude
(1,32 → 0,60 pela medida atual; 0,86 → 0,49 pela medida limpa) e vai
contaminar comparações futuras.

---

## Tentativa 7 — o realce de cor do Mágico pro escurece o papel

**Data:** 04/08/2026
**Situação:** medido, três variantes; **nada trocado**, e o porquê está abaixo
**Motivo:** oito das vinte e sete reprovações da régua eram "o fundo escureceu",
espalhadas por quatro livros. Sete delas no Mágico pro.

### A causa, medida passo a passo

Reproduzidas as páginas reprovadas e medido o fundo **depois de cada passo** do
filtro, a causa é uma só: `_realcar_saturacao`. Todos os outros passos são
neutros ou clareiam — no Boécio o achatamento da iluminação sobe o fundo de
145,5 para 154,4, e a saturação joga para 138,4. O filtro Melhorar, que não tem
esse passo, passa nas seis páginas.

| Página | Fundo original | Queda causada pelo passo |
|---|---|---|
| BRODERIES 16 | 91,5 | 13,4 |
| BRODERIES 46 | 153,8 | 6,3 |
| BRODERIES 76 | 156,4 | 6,5 |
| Palatino 1 | 81,2 | 10,0 |
| Rhetorica 446 | 201,9 | 11,0 |
| Boécio 50 | 145,5 | 15,9 |

O passo multiplica o S do HSV mantendo o V. Isso preserva o brilho, mas não a
luminância: o cinza é 0,299 R + 0,587 G + 0,114 B, e numa cor quente subir a
saturação empurra verde e azul para baixo. Papel envelhecido é sempre
amarelo-pardo, então isso acontece em todo o acervo.

**E o número escondia metade do estrago.** Olhadas as imagens, a folha vazia do
Boécio e a 446 da Rhetorica saem de um creme pálido para um **amarelo forte** —
exatamente o amarelado que o Kaique pediu para tirar. A régua não pega isso: ela
mede quão CLARO está o papel, e uma folha mais amarela pode estar mais clara.

### As três variantes medidas

| | fundo | rubricação do Graduale 376 | teste |
|---|---|---|---|
| **Hoje (HSV)** | escurece em 8 páginas | vazios −18% | passa |
| **Cor em LAB** | conserta 6 | vazios **−30%** (entope) | passa |
| **Cor em YCrCb** | conserta 8 | vazios **−28%** (entope) | passa |
| **Não rodar em folha sem tinta** | conserta 4 | vazios −18% | **falha** |

**LAB e YCrCb foram revertidos.** Os dois consertam o papel e fazem o mesmo
estrago do outro lado: na página 376 do Graduale, de rubricação vermelha, a
letra engrossa e os vazios internos caem abaixo do limite de 25%. Entupimento de
letra é o defeito mais grave que existe neste projeto. Preservar a luminância
não basta — quem binariza a letra é a conversão para cinza por VALUE, o maior
canal, e essa não vê o Y.

**O guarda de folha vazia** é o único sem regressão na régua: 27 motivos passam
a 23, quatro reprovações somem e nenhuma nasce. Mas derruba
`test_intensidade_do_magico_muda_a_saturacao`: numa página colorida **sem
tinta**, o medidor de intensidade deixa de mexer na cor. O medidor foi um pedido
explícito, então isto não é detalhe de teste. Fica para decisão.

### O caminho que sobra

Deixar a **tinta** de fora do realce, e não só o papel claro. O peso de hoje
separa papel de conteúdo pelo par claro-e-sem-cor; falta uma terceira condição
que reconheça tinta colorida — a rubricação — e a preserve. Com ela, dá para
trocar o espaço de cor sem engrossar letra nenhuma, e aí LAB ou YCrCb passam a
valer.

---

## Tentativa 8 — a rampa da borda media papel, não letra

**Data:** 05/08/2026
**Situação:** **trocada a medida da régua**; nenhum filtro tocado

Dez dos vinte e quatro motivos de reprovação eram "a borda das letras virou
degrau". Quatro deles no Boécio, que é um scan de baixa resolução.

Medido passo a passo, o padrão era sempre o mesmo:

| Página | Ruído do papel | Rampa "de hoje" |
|---|---|---|
| Boécio 33 | 8,14 → **0,00** | 0,86 → 0,55 |
| Boécio 41 | 7,57 → **0,00** | 0,70 → 0,55 |
| Boécio 17 | 6,77 → **0,00** | 0,75 → 0,56 |

O papel saía **perfeitamente limpo** e a "rampa" caía junto. Não é coincidência:
a medida contava pixels de tom intermediário até quatro pixels do contorno da
letra, e o grão do papel ali ao lado entra nessa conta. Papel sujo inflava o
número; limpar o papel — que é o certo — aparecia como estrago na letra.

### A medida nova

Rampa é contraste dividido por inclinação, medida **em cima do contorno**. Sai
em pixels de verdade, e o grão do papel não entra. Validada contra casos
extremos na mesma página:

| Caso | Medida antiga | Medida nova |
|---|---|---|
| Imagem binarizada (degrau mais duro possível) | 0,00 | **1,00** |
| Original | 0,86 | 1,20 |
| Desfocado sigma 1 | 1,02 | 1,37 |
| Desfocado sigma 2 | 1,35 | 1,81 |
| Desfocado sigma 4 | 2,27 | 3,19 |

Por ela, as letras do Boécio nunca saíram da faixa saudável: **1,20 antes do
filtro, 1,14 depois**. Bate com a imagem — ampliadas quatro vezes, elas estão
redondas. O piso do critério passou de 0,7 para 1,05, porque um degrau puro dá
exatamente 1,00 nesta escala.

---

## Pendência — o ruído da capa

**Data:** 05/08/2026
**Situação:** diagnosticado, **não consertado**

Sobram seis motivos de "o fundo ficou mais sujo". O maior salto é a página 1 do
Boécio, de 5,5 para 14,8. Aberta a imagem, ela é a **capa** do livro: pergaminho
mosqueado com a etiqueta da biblioteca. Não é papel de texto.

Medido passo a passo, o ruído sobe em dois lugares:

| Passo | Ruído |
|---|---|
| original | 5,52 |
| achatar iluminação | 5,94 |
| **balanço de branco** | **13,34** |
| **aprofundar pretos** | **17,54** |
| alisar o papel | 14,78 |

São os dois passos que levam o papel ao branco. Numa capa não há papel a
branquear: o que eles esticam é o mosqueado do couro.

O `_aprofundar_pretos` já tem guarda de folha sem tinta, mas ela não pega esta
página — a etiqueta é escura de verdade. O `_balanco_de_branco` não tem guarda
nenhuma.

Existe pronto um teste que acerta o caso: `_pagina_sem_conteudo`, usado pelo
recorte de bordas. Medido nas páginas do acervo, ele dá verdadeiro exatamente
para capas e folhas vazias — Boécio 1 e 50, Palatino 1, Graduale 1, BRODERIES
16/46/76, Rhetorica 446 — e falso para página de texto e para ilustração. É por
aí que o conserto deve vir, e ele precisa ser medido antes de entrar.

---

## Onde a régua deixou de cobrar letra — e o limite disso

**Data:** 05/08/2026

Treze das 63 páginas medidas passaram a não ter os critérios de letra cobrados.
**Abri as treze.** Doze estão certas: capas do Boécio, Palatino, Graduale, Horas
e as duas do Pesel; guarda em branco do Palatino e da Rhetorica; três folhas
pardas sem tinta do Pesel; folha vazia do Boécio; e a foto do corte do Graduale,
que é o livro fechado visto de lado.

**Uma é discutível:** a página 1 do Livro de Horas é o cartão de rosto que a
Gallica acrescentou à digitalização — "Heures de Louis XIV. Ms. déposé au
Louvre." em tipo cinza-claro sobre branco. Tem texto, e mesmo assim passou no
teste, porque nada nela é escuro o bastante. Não é conteúdo do livro, então o
estrago é pequeno; fica registrado como limite conhecido do teste.

### A regra foi apertada no meio do caminho

A primeira versão aceitava a palavra do detector de regiões: folha marcada
inteira como gravura, nada como letra. Com ela, **30 das 63 páginas** deixavam
de ser cobradas — e entre elas estava a **página 126 do Graduale, uma partitura
manuscrita cheia de texto**, que o detector marcou como 100% gravura. É o erro
que a regra do projeto cita pelo nome: partitura tratada como uma grande
ilustração.

Nenhuma medida de pixel separa aquela partitura de uma prancha de padrão do
Siebmacher — fração de tinta 0,276 contra 0,307 e 0,341. Então a régua passou a
tratar as duas perguntas com pesos diferentes:

| Pergunta | Quem responde |
|---|---|
| Vale medir **forma** de letra? (vazios, espessura) | o detector basta — esses números já não valem para ilustração |
| Vale medir **borda** de letra? | só o teste por imagem: nada mais escuro que a própria folha |

Com isso a partitura voltou a ser cobrada, e as páginas afrouxadas caíram de 30
para 13.
