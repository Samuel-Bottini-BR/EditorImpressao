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


---

## Tentativa 9 — a partitura marcada como gravura, e os quatro sinais que não a salvam

**Data:** 06/08/2026
**Situação:** **não resolvido**; quatro caminhos medidos e descartados

A página 126 do Graduale é uma partitura manuscrita cheia de texto, e o detector
a marca como **100% gravura**. É o erro que a regra do projeto cita pelo nome —
"uma partitura tratada como uma grande ilustração".

### Por onde ela escapa

Numa caixa que o modelo chamou de `figure`, o detector pergunta três coisas, e
basta uma para virar gravura:

    desenho    pedaços de glifo < 0,30      p126: 0,425  -> não
    foto       papel à vista   < 0,52       p126: 0,066  -> SIM
    meio-tom                                p126: falso

É o `papel à vista` que a condena. E o motivo é o mesmo já corrigido nos
filtros: **papel velho é colorido**. O pergaminho da 126 tem saturação mediana
75, acima do limiar de 60, então o próprio papel deixa de contar como papel —
sobram 7% de "papel à vista" numa página que é quase toda papel.

### Os quatro caminhos medidos

| Caminho | O que faz na 126 | Por que não serve |
|---|---|---|
| Neutralizar a cor do papel antes de medir | 0,07 → 0,64, conserta | Quebra as fotos: Pesel 73 vai a 0,75 e Rhetorica 112 a 0,60 — as duas viram escrita |
| Exigir que `foto` também não pareça escrita | conserta | O bordado do Pesel passa no teste de escrita e vira letra — seria binarizado |
| Usar só os outros dois sinais | — | Nenhum separa: glifo dá 0,425 na escrita e 0,668 numa foto |
| Periodicidade do perfil de linhas | 0,410 | Não separa: a estampa do Catecismo dá 0,931 e a xilogravura 0,601 |

Medidos lado a lado, os números de escrita e de foto **se cruzam em todos os
quatro**. Não é questão de achar o limiar certo.

### O que isso quer dizer

O sinal que falta não é estatística de pixel — é reconhecer escrita antiga como
escrita, e o modelo que temos foi treinado em documento moderno. O conserto de
verdade é trocar ou somar um modelo treinado em documento histórico. A
pesquisa aponta três abertos que fazem exatamente isto: **Eynollah**,
**dhSegment** e o **Kraken/eScriptorium**, e existe dataset anotado pixel a
pixel para validar — o **DIVA-HisDB**, 150 páginas de manuscritos medievais da
competição ICDAR 2017.

Enquanto isso não acontece, o estrago tem conserto na mão: a aba Marcar permite
corrigir a página, e a régua da seleção nomeia quais são.

---

## Tentativa 10 — a capa não é papel, e por isso não se branqueia

**Data:** 06/08/2026
**Situação:** **aplicado**; 10 motivos passam a 4

Depois que o detector passou a marcar capa como gravura, as capas começaram a
passar pelo caminho do `filtro_melhorar` — e é ele que as suja. Medido passo a
passo na capa do Boécio:

| Passo | Ruído |
|---|---|
| original | 5,52 |
| achatar iluminação | 5,94 |
| **balanço de branco** | **13,34** |
| **aprofundar pretos** | **17,54** |

Numa capa não há papel a branquear: o que ali parece papel é o couro. Então o
filtro passou a perguntar se aquilo é capa, e numa capa faz só o alisamento.

Três passos tiveram de sair, e cada um custou uma medição para descobrir:

| Passo retirado | Por quê | Medido |
|---|---|---|
| branqueamento e ponto de preto | não há papel a branquear | ruído do Boécio 5,5 → 17,5 |
| achatamento da iluminação | não há luz torta a corrigir; o que varia é o relevo do objeto | couro verde do Horas 219 → 194 |
| recomposição da rampa | ela devolve a borda da LETRA, e não há letra | couro vermelho do Graduale 47,4 → 43,9 |

Com os três fora, nas três capas medidas o fundo **não anda um décimo**, e o
ruído cai — o do Boécio de 5,52 para 4,48.

A folha de guarda em branco não entra nisso: ela é papel, e continua indo a
branco. É o mesmo teste de objeto-ou-folha que o detector usa, e mantê-lo num
lugar só evita que o filtro e o detector discordem sobre a mesma folha.

### O que sobra

Quatro motivos, e os dois são conhecidos:

- **Graduale 126, três filtros** — é a partitura que o detector marca como
  gravura. O ruído sobe porque ela é tratada como desenho. Mesma raiz da
  Tentativa 9; conserta-se consertando a detecção.
- **Pesel 76** — o fundo escurece 156 → 148 no Mágico pro.

---

## Tentativa 16 — a mancha do verso e o creme, no Melhorar e no Mágico pro

O Samuel apontou nos prints do teste completo:

> "era para tirar a mancha do verso, se era está ruim, não tirou a mancha do
> verso"

> "melhorar e magico pro não estão deixando a pagina totalmente branca, ela
> ainda deixa o fundo meio amarelado (e isso é ruim porque a impressora vai
> entender como cor a ser impressa, mesmo em preto e branco)"

As duas queixas são o mesmo defeito. O Preto e branco já tinha resolvido a
mancha — o Sauvola de `k` adaptativo, da Tentativa 15, a reduziu a chuvisco.
Os outros dois filtros não usam Sauvola: eles empurravam para branco com um
**limiar fixo de 235**. Numa folha amarelada isso não alcança nada:

| na página 33 do Boécio | tom |
|---|---|
| papel já tratado | 225 |
| mancha do verso | 210 |
| limiar do empurrão | **235** |

Nenhum dos dois passa. O fundo continuava creme e a mancha, legível.

### O que separa a mancha da letra não é o tom

Quem sabe separar é o **Sauvola** — ele compara cada pixel com a vizinhança, e
a mancha perde por ser mais fraca que a vizinhança dela. É a mesma conta que o
Preto e branco já faz. Então a pergunta passou a ser feita a ele: o que o Preto
e branco chamaria de papel, aqui vira branco puro.

Só que o Sauvola sozinho ainda pega a parte forte da mancha, e ali ela virava
um fantasma cinza. O que separa esses dois é o **tamanho da peça**:

| página 33 do Boécio | área mediana da peça | peças |
|---|---|---|
| o texto | 66 px | 1012 |
| a mancha do verso | 4 px | 689 |

Corte em 30 px, e peça pequena volta se encostar numa grande — que é o caso de
acento, pingo do i e serifa solta.

### Três travas, e cada uma custou uma medição

| Trava | Por quê | O que estragava sem ela |
|---|---|---|
| não entra em página sem texto | entre os traços de uma estampa está a obra | a estampa do Catecismo perdia o céu azul inteiro |
| só onde a cor é a do papel | mancha é âmbar; céu, rubricação e couro não | mesmo céu, agora manchado |
| pergunta ao ORIGINAL se o pixel é escuro | o realce do Mágico pro escurece a mancha | o próprio realce promovia a mancha a "escura demais para ser mancha" e a protegia |

A primeira saiu de uma contagem no acervo inteiro. Página de texto tem de 264
(Graduale) a 2405 (Rhetorica) peças de letra; estampa e prancha ficam entre 6 e
83. Há um vão de três vezes entre os dois grupos, e o corte cai no meio dele.

A segunda também consertou um erro meu: escrevi a janela de matiz em graus, e
no resto do arquivo ela está na escala do OpenCV. Com a unidade errada a trava
excluía o próprio amarelado do papel, e a mancha voltava inteira.

### Resultado

Aberta imagem por imagem: no Boécio 33 e 17 o fundo é branco puro e a mancha
sumiu nos dois filtros; a Rhetorica 112 mantém a hachura da xilogravura e o
texto ao redor; o Graduale 376 mantém rubricação e pautas vermelhas; as cinco
capas do acervo saem intactas.

### O que a régua diz depois das Tentativas 16 e 17

Nove livros, 63 páginas medidas:

| | antes | agora |
|---|---|---|
| páginas piores que o original | 6 a 8 | **4** |
| régua da seleção | 23 de 26 | **24 de 26** |
| pico de memória | 1402 MB | 1458 MB (teto 2048) |
| abrir o programa | — | 0,44 s (meta 10) |

Os 4 que sobram são os dois casos já documentados, e nenhum é novo:

- **Graduale 126, nos três filtros** — a partitura que o detector marca como
  gravura. O ruído sobe porque ela é tratada como desenho. A página fica
  laranja avisando da dúvida.
- **Pesel 76, no Mágico pro** — o fundo escurece de 156 para 148.

A memória subiu 56 MB, e é o preço da marcação em resolução plena: a máscara de
tinta de uma página de 300 DPI ocupa 10 MB em vez de 1. Continua uma página de
cada vez, e continua bem abaixo do teto.

---

## Tentativa 17 — a marcação em resolução plena

> "as ferramentas de seleção precisam ser mais precisas, precisam conseguir
> selecionar só o texto, precisam conseguir reconhecer desenhos cores padrões"

A máscara de tinta era calculada num reduzido de 1200 px de altura e a resposta
voltava ampliada com vizinho mais próximo. Numa página de 300 DPI isso é um
terço da resolução: a marcação saía com degraus de três pixels em volta de cada
letra. E o `k` era fixo em 0,20, enquanto o filtro já usava o adaptativo — o
detector e o filtro discordavam sobre o que era tinta na **mesma** página.

Régua da seleção: **23 → 24 de 26**. O Pesel 73 passou a separar o título
impresso, o número da página e as quatro legendas da foto do bordado. Aberto e
conferido: a marcação do Boécio 33 segue linha por linha e deixa a mancha do
verso de fora, que é literalmente "selecionar só o texto".

### O gargalo não era o Sauvola

Medido numa página de 3729 px de altura:

| passo | tempo |
|---|---|
| Sauvola (DoxaPy) | 59 ms |
| medir a espessura do traço | **1899 ms** |

A esqueletização é a conta mais cara do programa. Ela passou a ser feita num
reduzido e reconvertida pela escala. Comparado com a medição nativa nas 14
páginas do acervo:

| altura | páginas com `k` fora de 0,01 | custo por página |
|---|---|---|
| 1500 | 4 de 14 | 105 ms |
| 2000 | 2 de 14 | 207 ms |
| **2500** | **1 de 14** | **319 ms** |
| 3000 | 1 de 14 | 435 ms |
| nativo | — | 1900 ms |

Em 2500 a resposta empata em 13 das 14 e o custo cai seis vezes. A que sobra é
a página 454 do Marial, que cai no meio da rampa entre traço fino e grosso.

Sobre isso entrou um cache: a mesma página pergunta o `k` três vezes — o
detector, o filtro e a limpeza do papel. A chave é o **conteúdo** da imagem, e
não o objeto, porque o programa copia a página entre um passo e outro. Medido:
873 ms na primeira vez, 19 ms numa cópia da mesma página.

---

## Tentativa 18 — a capa de trás do Boécio voltava a ser apagada

Achado ao abrir a bateria completa, imagem por imagem: o Preto e branco
devolvia a capa de pergaminho da página 50 do Boécio como uma **folha branca**.
É o bug da capa apagada, voltando por um caminho que ninguém tinha medido.

A capa é protegida por ser marcada como gravura de página inteira, e quem
decide isso é a textura. Contada em todas as páginas sem conteúdo do acervo, os
dois grupos não se encostam:

| | valores |
|---|---|
| folha nua | 0,00 1,31 1,36 1,40 1,49 1,51 1,55 1,91 |
| capa | 5,05 6,19 6,25 7,10 12,48 |

O limiar estava em **5,5 — dentro do grupo das capas**. A de 5,05 ficava de
fora. Agora está em 3,0, no meio do vão, com folga de mais de duas vezes para
cada lado.

### A régua estava errada, e isso escondia o bug

A régua da seleção classificava essa página como "folha de guarda, sem nada
impresso". Não é. Aberta ao lado da página 1, é a **capa de trás do mesmo
pergaminho**: mesma cor, mesmo grão de couro, e as duas trazem a etiqueta
octogonal RESERVADO / B. N. L. da biblioteca — na p1 à esquerda, na p50 à
direita, como é de esperar do verso.

Enquanto o caso dizia "folha nua", a régua **aprovava** a página sair branca. A
classificação errada não era um detalhe: era ela que escondia o defeito.

Corrigi o caso e escrevi o porquê dentro do próprio arquivo, para o Samuel
poder discordar sem ter de reconstituir o raciocínio.

### Resultado

| | antes | depois |
|---|---|---|
| páginas piores que o original | 4 | **4** |
| régua da seleção | 24 de 26 | **24 de 26** |
| pico de memória | 1458 MB | 1454 MB |

Nada piorou, e a capa sai inteira. As folhas nuas continuam indo a branco — a
anotação a lápis no pé do Palatino sobrevive.

---

## Tentativa 19 — folhear o livro, e o vazamento que ele revelou

> "gostaria de poder visualizar o PDF e poder folhear ele enquanto escolho as
> opções que vão ser aplicadas nele nesta parte do programa aqui" — o Samuel,
> sobre a tela "Marque o que você quer fazer"

A tela passou a ter duas colunas: as escolhas à esquerda, o livro à direita,
com `<`, `>`, contador de folhas e botão **tela cheia**. Sem isso a pessoa
marcava "dividir folhas ao meio" sem ter visto se a folha tem mesmo duas
páginas, e só descobria o engano na tela seguinte.

Mostra a folha **como ela é no arquivo**, sem filtro nenhum. O que os filtros
fazem se vê na tela de conferir, com a prévia lado a lado; misturar as duas
coisas aqui faria julgar o filtro por uma imagem pequena.

### O que apareceu ao medir a memória

Medindo o folhear no Marial (907 folhas, 205 MB), a memória subia **uns 2 MB a
cada folha virada**:

| folhas viradas | memória |
|---|---|
| 25 | 157 MB |
| 50 | 209 MB |
| 75 | 262 MB |
| 100 | 314 MB |

Não era do folhear: era do `pagina_para_array`, que **todo o programa usa** — o
pipeline, as prévias, as miniaturas e a régua. Por baixo, o MuPDF guarda
fontes, imagens e a árvore de cada página já aberta, num armazém que ele só
limpa quando o documento fecha. Num livro de 900 folhas isso é o programa
inteiro na memória, e não uma folha.

Uma linha resolve — `fitz.TOOLS.store_shrink(100)` ao fim de cada leitura:

| folhas viradas | antes | depois |
|---|---|---|
| 100 | 314 MB | **105 MB, e para de subir** |

### Sobre o teste dessa correção

Tentei testar medindo a memória do processo, e não dá: o armazém do MuPDF tem
teto próprio, uns 256 MB. Um PDF de teste satura o teto na primeira volta e
para de crescer — **o teste passava com e sem a correção**, e teste que passa
sempre não é teste. Reproduzir de verdade exigiria mais de 256 MB de páginas
diferentes, e uma bateria não pode custar isso.

O teste que ficou verifica o que dá para afirmar sem enganar: **ler uma folha
esvazia o armazém**. Conferido que ele reprova quando a linha sai. O número de
verdade está medido acima, no acervo, à mão.

### O que a correção do vazamento fez no acervo inteiro

A régua sobre os nove livros, com e sem a linha:

| | antes | depois |
|---|---|---|
| pico de memória | 1454 MB | **1148 MB** (teto 2048) |
| páginas piores que o original | 4 | 4 |
| abrir o programa | 0,46 s | 0,56 s |

São 306 MB a menos no programa inteiro, e não só no folhear — porque quem
lia página era o `pagina_para_array`, e ele é o mesmo para o pipeline, as
prévias, as miniaturas e a própria régua. Nada piorou em qualidade.

---

## Tentativa 20 — o papel dentro da gravura (os quadradinhos na roupa do anjo)

**Data:** 28/09/2026
**Situação:** aguardando conferência do Samuel (Lista de bugs do plano, 28/09)
**O que se queria:** a regra do resultado da Fase 1 — todo o papel branco,
inclusive dentro da gravura (fundo do retrato do Palatino 5); só a pintura de
verdade mantém a cor (roupa do anjo da Escola 35, céu, foto da estátua do Opus
Majus 20); sem quadradinhos.

### A causa (investigação de 28/09)

A limpeza do papel da página de texto (`_limpar_o_papel_de_verdade`: "o que não
é letra e tem cor de papel vira branco") rodava também no recorte de cada
gravura, pelo Melhorar dentro de `_limpar_cada_gravura`. O pano quase branco
passava por papel; a cor do JPEG, em quadrados de 16×16, fazia uns quadrados
passarem e outros não. A mesma coisa lavava a foto do Opus 20. Afeta Mágico
pro, Melhorar e a gravura do Preto e branco.

### O que foi medido antes de escolher

- **Pela cor não separa.** O pano do anjo (luz 222 a 233, pouca cor) é mais
  parecido com o papel da página (250) do que o papel de dentro do retrato do
  Palatino 5 é com a margem dele (183 contra 213, saturação 97 contra 56). A
  estátua do Opus 20 tem a cor do papel, só 14 tons mais escura.
- **Pela estrutura separa.** Densidade de traço fino e escuro sobre fundo claro
  (top-hat preto, o fechamento menos a imagem): pinturas da Escola 0,000; foto
  do Opus 20 0,001 (só um pico no livro da mão); retrato do Palatino 5 0,09 a
  0,13; tabela do Opus 256 0,06; Rhetorica 73 0,10. Fração da gravura coberta
  por traço: foto 0,9%, pinturas 0%, gravuras de traço 24% a 88%.
- **Cor relativa ao papel da própria gravura.** Horas 13: papel até 7 de
  distância, moldura dourada a partir de 25. Palatino 5: papel até 13.

### O que foi tentado

1. **Não limpar dentro da gravura** (o conserto simulado da investigação):
   devolve o anjo e a foto, mas o papel do retrato do Palatino 5 fica creme e o
   da tabela do Opus 256 cinza-claro. Fere a regra. Descartado.
2. **Veto por "sombreado"** (densidade de tom médio liso) para a mancha do
   livro da mão da estátua: não funciona — a estátua é lisa e clara, não conta
   como sombreado; e o veto se acendia nas tabelas das Horas. Trocado pela
   fração mínima de traço na gravura (5%).
3. **Na gravura de traço, a pergunta da página de texto ("longe da letra")
   com a cor relativa**: o papel ficou branco, mas **a hachura fraca do retrato
   se partiu** e a barba perdeu detalhe — o Sauvola regulado para letra não vê
   o traço fraco. Descartado.
4. **Adotado:** na gravura de traço, papel é o ponto **no nível do fundo em
   volta** (o próprio fechamento; rampa de 0,78 a 0,90 da luz do fundo), com
   fundo claro, cor do papel da própria gravura (a e b alisados, rampa), e
   **ligado** ao papel entre os traços (componentes ligados a partir de
   sementes). Gravura de tom contínuo (menos de 5% de traço): nada vai a branco
   por aqui. `core/filtros.py`, `_so_o_papel_da_gravura`.

### Resultado (as 32 páginas do gabarito, Mágico pro, conferido de olho)

- Mudam 8 páginas, todas entre as que passam pelas travas da limpeza; as outras
  ficam idênticas ponto a ponto.
- Escola 35 e 7: roupa, céu e nuvens de volta, sem quadrados.
- Opus 20: a foto volta com os cinzas. Sobra uma faixa lavada no alto da foto
  (a caixa da gravura do detector começa 67 pontos abaixo do topo da foto).
- Palatino 5 e Rhetorica 73: papel branco, hachura e letras inteiras, sem o
  contorno creme em volta da letra.
- Opus 256: papel branco, e os números da última coluna (o "16", o "36") que
  a limpeza antiga comia ficam inteiros.
- Horas 13 e 14: só a beirinha vermelha da moldura, a olho igual.
- Tempo só do filtro (antes e depois intercalados no mesmo processo, PC com
  outros agentes rodando): diferença dentro do ruído, de −0,11 a +0,11 s por
  página. A primeira versão, em ponto flutuante e em tamanho cheio, deixava a
  Horas 13 um segundo mais lenta; refeita em 8 bits e com os mapas lisos numa
  cópia reduzida.
- Conferências: `relatorios/conferir/fase1-2026-09-28-1844` (32 páginas,
  Mágico pro) e `-1853`, `-1854`, `-1855` (as 5 em destaque: Mágico pro,
  Melhorar, Preto e branco). Relatório com as provas:
  `relatorios/conserto-anjo-2026-09-28/`.

## Tentativa 21 — tirar o fundo de PDF com camadas do Internet Archive (item 1.1, 28/09/2026)

Módulo novo `core/camadas.py` (ainda não ligado ao programa). Conferência:
`relatorios/conferir/fase1-2026-09-28-1915`. O que foi tentado e descartado:

1. **Manter a zona do detector inteira como o PDF desenha.** Páginas que o
   detector marca inteiras (Opus Majus 256, Rhetorica 73) saíam sem mudança
   nenhuma. Descartado.
2. **"Fundo escuro longe da tinta" para decidir a zona.** O retrato do Palatino
   5 perdia a hachura fina. Trocado por "onde a máscara não cobre".
3. **Papel = percentil 75 do fundo, depois o pico da página inteira.** Na Pesel
   o linho claro virava "papel" e a foto sumia, e a decisão mudava com a
   resolução. Trocado pelo pico na margem.
4. **Análise no DPI de saída.** A prévia e o PDF decidiam diferente (Palatino
   116). Agora é sempre a 150 DPI.
5. **Descartar o que "encosta na borda".** No Siebmacher, 97 de 134 páginas
   ficavam intactas por causa do preto do scanner. Trocado pela regra da faixa
   de 10% junto à borda.
6. **Separar gravura de página inteira de texto com moldura grossa** por
   fração, densidade local e manchas compactas: os números se cruzam entre os
   dois tipos. Virou só o aviso "conferir"; fica para o detector do item 1.2.

## Tentativa 22 — tirar o fundo sem perder a tinta que só existe na camada de baixo (item 1.1, 29/09/2026)

Conserto das perdas achadas pelo verificador (Siebmacher 104 e 105, molduras e
título do Palatino). Conferência: `relatorios/conferir/fase1-2026-09-29-0108`.
Adotado: trazer de volta o traço do fundo que é pelo menos 30% mais escuro que
o papel e fica perto da tinta de cima (o verso, o carimbo e a mancha d'água
ficam abaixo de 20%). Tentado e descartado:

1. **Separar o meio-tom perdido (pontilhado de gravura) do verso** por fração,
   raio de 1 e 2 pixels e densidade local: os números se cruzam (2,0% no
   Palatino 68 contra 2,7% no Palatino 10). Ficou só o aviso "conferir".
2. **Separar o verso da tinta clara pelo escuro:** os dois dão de 0,32 a 0,45.
   A escrita clara que só existe no fundo não volta; a página fica intacta
   quando ela é muita (Siebmacher 103 a 105).
3. **Dividir o papel canal a canal** para branquear dentro das zonas mantidas:
   puxa o cinza da foto para o azul (Opus Majus 20). Trocado pela conta em Lab
   (brilho multiplicado igual para todos os tons, cor do papel tirada).

---

## Tentativa 23 — gravura pequena não roda mais o Melhorar na folha inteira

**Data:** 29/09/2026
**Situação:** aguardando conferência (decisão da gerente pela regra 6)
**Número atacado:** o Preto e branco do teste de velocidade, 8% mais lento
(33,1 → 35,7 s). Causa medida: o detector passou a marcar o título corrido
"de Maria." do Marial 153 como gravura, e qualquer gravura fazia
`_limpar_cada_gravura` rodar o Melhorar na folha inteira (quase 3 s a 300 DPI)
só para usar o resultado na borda suave em volta dela.

1. **Melhorar só numa área em volta da gravura** (o pedido da gerente):
   rápido, mas numa área pequena a limpeza do papel não reconhece mais
   "página de texto" (75 letras no Marial 153; pede 200) e o papel da borda
   parava em 220–229 em vez de 255 — um halo cinza em volta da caixa, visível,
   de 11 a 28 mil pontos por página. Descartado.
2. **Adotado:** com gravura pequena (caixa até 25% da folha) e sem pedacinhos
   de gravura menores que 0,2%, a borda suave usa o próprio filtro da página
   em vez do Melhorar da folha inteira (`GRAVURA_PEQUENA_ATE`,
   `core/filtros.py`). Os recortes das gravuras continuam com o Melhorar
   deles.

**Resultado:** Melhorar idêntico ponto a ponto nas 32 páginas; Mágico pro e
Preto e branco com 27 de 32 idênticas (as 5 em destaque do Samuel idênticas nos
3 filtros); nas 5 que mudam, de 17 a 426 pontos na beirada da caixa, sem
diferença a olho. Marial 146–155: 8 idênticas; 146 e 153 mudam 14 a 152 pontos
na beirada. Etapa Processar em Preto e branco, antes e depois intercalados (PC
com outros agentes): 52,3 → 46,6 s (−5,6 s).

## Tentativa 24 — a foto do Opus Majus 20 fica igual ao original (bug do item 1.1)

**Data:** 29/09/2026
**Situação:** aguardando conferência (Lista de bugs do plano, linha de 29/09 "Bug do 1.1")
**O pedido, nas palavras do Samuel:** "A foto do Opus Majus 20 não pode sair
mais clara: tem que ficar igual ao original."

**A causa.** O conserto da auréola (Tentativa 22, item 3) passou a branquear o
papel de toda zona mantida com `_branquear_papel`: o brilho (L do Lab) era
multiplicado para o papel chegar a branco, **igual para todos os tons**, e a
cor do papel era tirada. Na gravura de traço isso é o papel entre os traços
indo a branco (o pedido da Fase 1). Na foto, é a foto inteira clareando: a
túnica da estátua ia do cinza 183 para 226 e o creme sumia (b do Lab 140 → 129).

**Adotado** (`core/camadas.py`, `_onde_branquear` e `_zona_de_traco`):

1. Zona a zona, a pergunta "é de traço ou de tom contínuo?" é a mesma do Mágico
   pro (`core/filtros.py`, `_peso_de_traco` e `GRAVURA_DE_TRACO_MINIMA`, da
   Tentativa 20). Medido nas zonas mantidas: foto do Opus 20, 0,3% de traço;
   todas as outras (molduras e capitulares do Palatino 9, 10, 57, 66 e 67;
   Palatino 12; Rhetorica 38; ex-libris da Pesel 2), de 29% a 100%.
2. De traço: branqueia como antes (imagem idêntica ponto a ponto).
3. De tom contínuo: o miolo fica **como o PDF desenha**; vai a branco só o
   papel que a zona pegou em volta da foto: o que tem o tom e a cor do papel
   logo fora da zona e se liga ao lado de fora sem atravessar a foto, até
   12 mm da beirada da zona.

**Tentado e descartado:**

- **Curva que só clareia o que está perto do tom do papel** (em vez de
  separar foto de traço): a estátua fica a só uns 25 níveis do papel (e o
  claro dela chega a 11 níveis); qualquer curva que leve o papel a branco
  clareia a estátua. Não cumpre "igual ao original". Não implementado.
- **Referência do papel = papel da página inteira**: no Opus 20 o papel à
  direita da foto é 15 níveis mais escuro que à esquerda (199 a 220 no anel
  em volta); com a tolerância apertada, a folga da direita ficava creme.
  Trocado pelo papel do anel de 3 mm em volta da zona, e tolerância de 20 de
  tom (só para mais escuro; mais claro vale).
- **Limite de 5 mm da beirada da zona** (contra o papel "vazar" para dentro de
  uma parte clara da foto): a zona sintética do teste passa 11 mm da foto e
  sobrava um remendo creme. Subido para 12 mm (a zona do detector de hoje
  passa uns 2 mm da foto).
- **Dilatação de 3 mm para achar o anel** custava 10 ms por página com foto;
  trocada por distância (a mesma coisa).

**Resultado:**

- Opus Majus 20, em resolução cheia: túnica da estátua 183 (original) / 226
  (antes) / **183** (depois); creme (b do Lab) 140 / 129 / **140**; a foto
  inteira, fora a linha de 1 ponto da beirada, **idêntica ao PDF**; o papel
  entre a foto e a legenda continua branco (mínimo 245), sem a auréola.
- As outras 15 páginas do 1.1 no gabarito: **idênticas** ponto a ponto à
  rodada `fase1-2026-09-29-0851`. Também idênticas: Palatino 12, 48, 68, 94;
  Rhetorica 38; Pesel 2; Siebmacher 13, 15, 104, 105, 106, 118, 124.
- Os 5 livros inteiros (1256 páginas, análise a 40 DPI): **nenhuma decisão
  mudou** (fundo tirado / intacta / conferir), contra a conta de 29/09. Só
  duas páginas têm zona "de tom contínuo": o Opus 20 e o Siebmacher 25 (lá a
  zona é o preto do scanner embaixo da folha, 0,3% dos pontos mudam, sem
  diferença a olho).
- **Pesel 2 (ferrugem rosada no ex-libris): não resolvido.** A zona é de
  traço (58%) e continua branqueando como antes; o rosado vem da mesma
  função (`_branquear_papel` tira o amarelo do papel também da ferrugem,
  que tem quase o brilho do papel), mas não deste conserto.
- Tempo (a medida isolada de 6 páginas a 300 DPI, antes e depois
  alternados, 6 rodadas, sem outro agente rodando no momento): antes 8,58 s
  em média (menor 8,47), depois 8,64 s (menor 8,52), dentro do ruído das
  rodadas (8,47 a 8,80). Só a página com foto paga a pergunta nova: Opus 20
  de 1,72 para 1,76 s (cerca de 35 ms).
- Conferência: `relatorios/conferir/fase1-2026-09-29-0956` (as 16 páginas;
  em `acervo\`, Opus 20, Pesel 2 e Siebmacher 25 lado a lado: original,
  antes, depois).

## Tentativa 25 — ligar o "tirar o fundo" (item 1.1) ao programa (29/09/2026)

**Pedido (Samuel, 29/09):** "automático quando o programa detectar camadas,
com botão para desligar por livro; página duvidosa sai marcada 'conferir'."
**Decisão da gerente (a rever pelo Samuel):** com o botão ligado, a página que
`core/camadas.py` deixa sem o fundo usa esse resultado no lugar do filtro
(Preto e branco, Melhorar, Mágico pro); página em "Original" fica como está;
página deixada intacta segue o filtro.

**Como ficou:**

- Detecção ao abrir (`core.camadas.pdf_tem_camadas`, só a estrutura de até 12
  páginas): em `ui/janela_principal.abrir_livro` (para a caixinha) e em
  `core.pipeline.analisar_projeto` (para quem chega sem a tela: conferência,
  teste de velocidade). Campos novos em `Projeto`: `tem_camadas` (fato do PDF)
  e `tirar_fundo_sozinho` (a caixinha, nasce marcada).
- Onde entra na ordem: as camadas são da página do PDF (a folha inteira), então
  o "tirar o fundo" roda **antes** de dividir, no lugar do desenho da folha;
  dividir, cortar e endireitar seguem por cima; o filtro é pulado. O corte e o
  ângulo são **medidos na folha como veio** (os mesmos de sempre, guardados em
  `_GEOMETRIAS`), não na folha sem o fundo: assim o corte não muda com o botão
  e a prévia continua igual ao PDF (teste: igual ponto por ponto).
- O alerta novo `conferir_fundo_tirado` é posto e tirado quando a página é
  desenhada (prévia ou PDF), como o "desenho ou escrita".

**O que deu errado no caminho:**

- A primeira versão só lia a caixinha no projeto: **desmarcar depois da
  primeira conferência não valia**. Causa (já existia, vale para todas as
  caixinhas): depois da análise o projeto salvo volta por cima e a tela "O que
  fazer" continuava mexendo no objeto de antes. Consertado só para o 1.1
  (a tela passa a mexer no projeto de verdade; o salvo não traz de volta a
  caixinha antiga). As outras caixinhas continuam com o problema (Lista de bugs).
- Página deixada intacta (Palatino 5) pagava o "tirar o fundo" (~1,8 s) para
  jogar fora e depois o filtro: prévia de 2,4-3,2 s para 4,6-4,8 s. Agora a
  decisão "fica como está" é guardada por folha, na sessão (não depende do
  DPI): a segunda prévia e o PDF não pagam de novo. A primeira prévia ainda paga.

**Tempo** (medida isolada, 16 páginas do gabarito do 1.1, Mágico pro, código de
antes num worktree do `bbb9861` e o de depois, rodadas alternadas; **máquina
dividida com outro agente**, números com ruído grande):

| | antes | depois |
|---|---|---|
| processar (PDF, 300 DPI), rodada 1 / 2 / 3 | 77,7 / 64,8 / 52,6 s | 55,7 / 55,2 / 45,0 s |
| primeira prévia de cada página, rodada 1 / 2 / 3 | 45,9 / 39,5 / 32,3 s | 46,8 / 46,9 / 39,0 s |
| detectar camadas ao abrir (Palatino, 134 folhas) | — | 0,10 s |
| detectar camadas ao abrir (Escola, sem camadas) | — | 0,002 s |

O PDF sai 14% a 28% mais rápido (pula a marcação de gravura e o filtro). A
**primeira prévia** de cada página de livro com camadas fica **2% a 21% mais
lenta** (~0,5 s): o "tirar o fundo" (~1,8 s) custa mais que marcação + filtro,
e a primeira vista ainda desenha a folha a 300 DPI para medir o corte. Livro
sem camadas: nada muda (a detecção para na primeira página, 2 ms).

## Tentativa 26 — "Tirar o fundo" vira filtro (item 1.1, 29/09/2026)

**Pedido (Samuel, 29/09, depois de ver a primeira ligação):** "Página sempre
abre em 'Original', sem mexer. Em PDF com camadas, 'Tirar o fundo' vira mais
uma opção na lista de filtros (ao lado de Original, Preto e branco, Melhorar e
Mágico pro), com botão para aplicar no livro inteiro. [...] Ao abrir um livro
com camadas, o programa pode avisar: 'Este livro tem fundo separado. Quer
tirar o fundo?'. A caixinha 'Tirar o fundo sozinho' não é mais necessária." E:
"eu quero poder escolher tirar o fundo sem colocar nenhum filtro." E: "nenhum
livro vem marcado, nem novo, nem velho."

**Como ficou:**

- Filtro novo `core.filtros.TIRAR_FUNDO` ("Tirar o fundo", "tira o papel e
  deixa só o que está impresso"). `filtros_do_livro(projeto)` diz onde ele
  aparece: só em livro com camadas (ou, para poder sair dele, quando já está
  escolhido num PDF sem camadas). Aparece no filtro do livro da tela "O que
  fazer", como quinto cartão da aba Filtro e nos botões e no "comparar" da tela
  ampliada. Por página e para o livro inteiro pelos mecanismos de sempre
  (cartão, "todas", "só nas próximas", filtro do livro), com desfazer/refazer
  sem mudança no mecanismo.
- Sai a caixinha e o campo `tirar_fundo_sozinho` (e `tirar_fundo_ligado`).
  Projeto salvo com o campo abre (o campo é ignorado); projeto sem
  `tem_camadas` abre com False. Nenhum projeto vem com o fundo tirado: só a
  página com o filtro escolhido.
- Sem filtro por cima: "fundo tirado" e "conferir" saem como o
  `core/camadas.py` deixa; "intacta", PDF sem camadas ou erro saem **como
  vieram**, igual ao Original (`_filtrar` e `aplicar_filtro*` tratam o nome
  como Original, sem procurar gravura e letra). Palatino 5 pelo programa com
  "Tirar o fundo": idêntico ponto por ponto ao Original.
- O cartão e o "comparar" desenham o resultado de verdade
  (`pipeline.renderizar_com_filtro`, numa cópia da página, pedido ao
  `GerenciadorPrevias` com `pegar_com_filtro`; o cartão só é pedido depois
  que a prévia principal chegou).
- Aviso ao abrir: só quando o livro com camadas é aberto pela primeira vez
  (projeto novo; decisão da gerente, a rever). `QMessageBox.open()` (não
  `exec()`), guardado em `janela.aviso_do_fundo` para os testes clicarem.
  Sim = filtro do livro "Tirar o fundo"; Não, X ou Esc = nada muda.
- Alerta "Conferir o fundo tirado" (defeito 2 do verificador): ao ser posto,
  a página volta a "não conferida" e o alerta vai para a frente da lista; a
  decisão do `core/camadas.py` fica guardada por folha na sessão
  (`_DECISOES_DO_FUNDO`, substitui `_FOLHAS_SEM_TIRAR_FUNDO`), e
  `acertar_alertas_do_fundo` põe/tira o alerta sem desenhar, a cada
  atualização da tela de conferir. O "está bom assim" continua valendo.
- Defeito 1 do verificador (caixinha voltando marcada pelo "Abrir"): some com
  a caixinha; o filtro de cada página volta do salvo igual pelo "Abrir" e pelo
  "continuar" (teste).

**Conferência pelo programa** (`relatorios/conferir/fase1-2026-09-29-1826`,
filtro "Tirar o fundo", comparada com `fase1-2026-09-29-1603`): 15 das 16
páginas **idênticas ponto por ponto** à rodada anterior; o Palatino 5, que o
`core/camadas.py` deixa intacto, antes saía no Mágico pro e agora sai como
veio (papel amarelo, igual ao Original). "Conferir" nas mesmas 4: Palatino 9,
57, 66 e Opus Majus 3.

**Tempo** (medida isolada, 16 páginas do gabarito do 1.1, código da primeira
ligação num worktree do `f4d9a60` com a caixinha e Mágico pro, contra o de
agora com "Tirar o fundo"; duas rodadas alternadas; **máquina dividida com
outros agentes**):

| | antes (caixinha + Mágico pro) | depois ("Tirar o fundo") |
|---|---|---|
| primeira prévia das 16, rodada 1 / 2 | 44,7 / 37,9 s | 44,2 / 36,9 s |
| processar (PDF, 300 DPI), rodada 1 / 2 | 50,0 / 42,1 s | 48,1 / 40,1 s |
| prévia em Original (página nova) | — | 27,2 / 23,1 s |
| cartão "Tirar o fundo" (em segundo plano) | — | 30,7 / 26,4 s |

O ganho vem do Palatino 5 (intacto: prévia 3,4-4,0 s → 2,2 s; PDF 5,6-5,9 s →
2,8-3,0 s, porque não roda mais o Mágico pro). Nas outras, igual dentro do
ruído (o Opus Majus saiu de 0,1 a 0,4 s mais lento nas duas rodadas; não achei
causa no código, que é o mesmo caminho). Página nova em Original num livro com
camadas não paga o "tirar o fundo" na prévia (1,1-2,4 s por página); o cartão
"Tirar o fundo" custa de 1,2 a 2,8 s por página em segundo plano, ao abrir a
aba Filtro.

---

## Tentativa 27 — o motor do Kraken no Windows, sem WSL (item 1.3, etapa do motor, 29/09/2026)

**Pedido (Samuel, 29/09):** "todos os OCRs instalados, com ligar/desligar e
comparação automática entre eles [...] De fábrica, docTR fast_base + Kraken; o
Kraken direto no Windows, sem WSL." Depois da pesquisa
(`docs/pesquisa/fase1-1.3-kraken-windows.md`), escolheu o **motor à parte**:
Python 3.12 embutível + Kraken original + PyTorch para processador, chamado
como outro processo. Esta etapa é só o motor e a ponte até ele; **nada foi
ligado ao programa** (pipeline, tela, empacotador e instalador ficam para a
etapa de ligação, junto com o docTR e a comparação automática).

**O que ficou:**

- `montar_motor_kraken.py` (raiz): monta o motor, do zero, numa pasta fora do
  git (padrão `D:\programas\EditorImpressao-arquivos\ferramentas\motor-kraken`,
  `--destino` para o empacotador). Baixa o Python 3.12.10 embutível oficial
  (conferido pela soma que a python.org publica no `.spdx.json`), roda o pip
  direto do `.whl` (conferido; não fica no motor) e instala as 73 versões de
  `motor_kraken/requisitos-travados.txt` com `--require-hashes --no-deps
  --only-binary`. Nunca apaga pasta: se o destino existir, para e diz.
- `motor_kraken/servidor_kraken.py`: roda dentro do motor; abre o Kraken e o
  modelo uma vez e atende pedidos (uma linha de JSON por pedido) até a entrada
  fechar. Conta os "Polygonizer failed" do Kraken (linhas jogadas fora em
  silêncio).
- `core/ocr_kraken.py`: a ponte, no Python 3.14 do programa. `MotorKraken`
  abre o motor na primeira página, manda cada página por um `.npy`
  temporário (apagado em seguida), devolve `ResultadoKraken` (linhas, falhas,
  `precisa_revisar`), e nunca levanta exceção.
- `tests/test_ocr_kraken.py`: 24 testes com "motores de mentira" (morre ao
  abrir, morre no meio, trava, responde lixo, outra versão, escreve 1,5 MB de
  aviso, cancelar...) e os testes com o motor de verdade contra as linhas do
  Kraken do WSL (4 páginas por padrão; as 22 com `KRAKEN_22=1`).

**Resultado contra o Kraken do WSL (22 páginas do 1.3, duas rodadas):** as
**mesmas linhas em todas**: mesma contagem (862 linhas) e área em comum de
100,00% nas 22. O Opus Majus 256 dá as mesmas 233 linhas e o motor conta as 8
perdidas ("Polygonizer failed"), então a página sai `precisa_revisar`.

**Tempos (PC do Samuel, Ryzen 7 5800H; máquina DIVIDIDA com outro agente
trabalhando ao mesmo tempo, servem para comparar, não como número final):**
abrir o motor 4,6 a 5,1 s (importar 4,1-4,6 s + modelo 0,4 s) com o disco
"quente"; 10,2 s na primeira vez logo depois de montar; e **65 s** na primeira
vez depois de reescrever os 10.644 `.pyc` (o antivírus do Windows está ligado;
causa provável, não provada: ele lê cada arquivo novo uma vez). É o que deve
acontecer na primeira abertura depois de instalar: por isso a ponte espera até
180 s para o motor abrir, e a tela vai precisar dizer "a primeira vez demora". Por página: mediana 9,1-9,4 s,
de 4,9 s (Opus 20) a 19,8 s (Opus 256).

**O que deu errado no caminho (não repetir):**

1. **O coremltools 9.0 não tem pacote pronto para Windows** (só Mac e Linux).
   `--only-binary=:all:` falhou. Solução: uma segunda rodada do pip, só com
   ele, a partir do `.tar.gz` (conferido pela soma), sem isolamento de
   montagem, usando o setuptools travado que a primeira rodada instalou. No
   Windows ele é Python puro.
2. **O `compileall` não trocou nenhum `.pyc`.** O pip já deixa os `.pyc` no
   modo "confere a data", e o `compileall` sem `-f` os acha em dia. Sem o
   modo "não confere" (unchecked-hash), o motor instalado em Arquivos de
   Programas (sem permissão de escrita) poderia recompilar tudo a cada
   arranque se as datas mudassem na instalação. Corrigido com `-f`; o motor
   já montado foi recompilado no lugar.
3. **O Kraken não tem `kraken.__version__`**: a versão vem de
   `importlib.metadata`.
4. **DLLs da Microsoft**: além das duas que a pesquisa achou
   (`msvcp140.dll`, `vcruntime140_threads.dll`), a leitura das importações de
   todas as DLLs do motor pediu `msvcp140_atomic_wait.dll` (PyTorch) e
   `vcomp140.dll` (scikit-learn). O script as copia da pasta de
   redistribuíveis do Visual Studio 2022 (14.44.35112), junto com
   `vcruntime140.dll`/`vcruntime140_1.dll` da mesma versão (o zip do Python
   traz as suas, mais velhas). Conferido pelo próprio motor: as 11 DLLs do
   Visual C++ carregadas são todas de dentro da pasta dele.

**Reprodutível:** montado duas vezes com o mesmo script (a segunda numa pasta
de teste, apagada depois): os 34.550 arquivos batem; fora os `.pyc` e o
LEIA-ME, só diferem os 23 atalhos `bin\*.exe` (que guardam o caminho de quem
montou e não servem ao motor) e os `RECORD` que listam esses atalhos.

**Tamanho:** 1.147 MB no disco (34.550 arquivos); 211 MB comprimido (7-Zip, tar + xz nível 9, sólido: o mais perto do `lzma2/max` sólido do Inno Setup que dá para medir sem gerar o instalador).

---

## Tentativa 28 — o mesmo PDF com o caminho escrito de outro jeito não perde mais o trabalho (bug grave, 29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09, "GRAVE, antigo" (achado pelo verificador;
print `relatorios/conferir/fase1-2026-09-29-1826/verificador/t11-abrir-perdeu-o-trabalho.jpg`).

**O que acontecia:** o mesmo PDF chega com `\` quando se abre pelo Windows
(associação de arquivo) e com `/` pela caixa "Abrir" ou arrastando. O projeto
era achado certo (pela assinatura do arquivo), mas na hora de devolver o
trabalho salvo `projetos.combina_com` comparava o **texto** do caminho: não
batia, o programa dizia "Você mudou as opções desde a última vez..." e
recomeçava a conferência. O Histórico de ações ficava, o trabalho não.

**O que mudou:**

- `projetos.mesmo_arquivo(a, b)`: compara o **arquivo**, não o texto. Primeiro
  a forma comum (absoluto, sem `..`, barra do sistema, minúsculas no Windows:
  `os.path.normcase(os.path.abspath(...))`), que cobre `\`/`/`, maiúsculas,
  letra de unidade, caminho relativo e `..`, mesmo com o arquivo sumido; se não
  bater e os dois existirem, `os.path.samefile` (atalho de pasta, nome curto do
  DOS, unidade mapeada).
- `combina_com` usa `mesmo_arquivo` (a contagem de folhas e páginas continua
  valendo).
- `ui/janela_principal.py` (`_analise_pronta`): quando o salvo volta, fica o
  caminho que acabou de ser aberto (o que existe e funciona agora), não a forma
  antiga gravada.
- `historico.registrar`: uma linha por PDF de saída comparando o arquivo (o
  mesmo PDF escrito de dois jeitos repetia a linha).
- `core/pipeline.py` (`_chave_da_geometria`, `_chave_do_arquivo`): a chave das
  memórias (geometria, decisão do "tirar o fundo") usa a forma comum.

**O formato gravado não mudou:** o caminho continua sendo gravado como veio.
Projeto antigo (gravado com `\`, como o Palatino do Samuel) abre pelo "Abrir"
com o trabalho: coberto por teste (`projeto.json` escrito à mão como o
programa gravava).

**Onde se comparava caminho de livro (todos os lugares vistos):**
`projetos.combina_com` (texto: **era o bug**); `historico.registrar` (texto do
PDF de saída: linha repetida); `core/pipeline.py` (chaves das memórias:
`abspath` já tirava a diferença de barra, faltavam maiúsculas);
`projetos._pastas_conhecidas` (compara `Path`, que no Windows já ignora barra e
maiúsculas: sem mudança); `achar_por_assinatura`, `procurar_o_livro` e a tela
inicial (`pedir_para_continuar`, `procurar_o_livro_a_mao`) comparam a
assinatura do arquivo: já não dependiam da forma do caminho, sem mudança.

**Testes:** `tests/test_mesmo_livro_outro_caminho.py`, 17 casos (15 falhavam
antes do conserto, com a mensagem "Você mudou as opções..."; os 2 que já
passavam são os de "arquivos diferentes não são o mesmo" e "outro tamanho
continua recusado"). Na janela de verdade: salvo com `\` e aberto com `/`, o
contrário, maiúsculas diferentes, "continuar" depois de abrir de outro jeito, e
projeto antigo com `\`: voltam páginas, filtros, corte, alertas, conferidas e
Histórico de ações. Pasta de dados própria em `saida_teste\` (LOCALAPPDATA
trocado), nada criado na pasta de dados real.

**Velocidade:** `mesmo_arquivo` roda uma vez por abertura de livro;
`normcase` na chave das memórias é uma troca de texto. Teste de velocidade não
rodado (pedido da gerente).

---

## Tentativa 29 — "Para revisar" conta o alerta que chega pela prévia (item 1.1, bug pequeno, 29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09, "Item 1.1 (pequeno)" (achado pelo verificador;
print `relatorios/conferir/fase1-2026-09-29-1826/verificador/t03-cinco-cartoes-alerta-mas-para-revisar-vazio.jpg`).

**O que acontecia:** o alerta "Conferir o fundo tirado" só é conhecido quando
a página é desenhada. Quando ele chegava com a prévia, a faixa laranja, a
miniatura e o contador mudavam, mas o quadro "Para revisar" continuava "nada
pendente" até virar a página: `ui/tela_conferir.py` (`_alertas_da_previa`)
não chamava `_atualizar_paineis`.

**O que mudou:** `_alertas_da_previa` chama `_atualizar_paineis` (o mesmo que
`atualizar()` faz a cada mudança), só quando os alertas da página mudaram.

**Teste:** `tests/test_tirar_fundo_no_programa.py`,
`test_alerta_que_chega_pela_previa_entra_no_para_revisar` (falhava antes: o
painel ficava vazio; passa depois).

**Não coberto:** alerta de página VIZINHA que chega pela pré-carga (a página
que não está na tela) só entra no "Para revisar" na próxima atualização da
tela (qualquer clique ou virar a página), como antes.

---

## Tentativa 30 — as pontes do docTR e do Tesseract (item 1.3, etapa das pontes, 29/09/2026)

**Pedido (Samuel, 29/09):** "todos os OCRs instalados, com ligar/desligar e
comparação automática entre eles (onde discordam, a página vai para 'Para
revisar'). De fábrica, docTR fast_base + Kraken [...] Tesseract instalado, mas
desligado na detecção." Esta etapa é só a ponte de cada um (como a do Kraken,
Tentativa 27); **nada foi ligado ao programa** (pipeline, tela, empacotador,
instalador). O número 28 ficou com o outro implementador, que trabalhava ao
mesmo tempo; por isso esta é a 30.

**O que ficou:**

- `core/ocr_comum.py`: o resultado comum (`ResultadoOCR`, `LinhaOCR`,
  `PalavraOCR`), com os mesmos nomes do `ResultadoKraken` (linhas, motivo,
  detalhe_tecnico, segundos, largura, altura, disponivel, precisa_revisar), e
  `de_kraken()`, que converte o resultado do Kraken **sem mudar a ponte dele**.
- `core/ocr_doctr.py`: `DetectorDoctr`, o fast_base pelo OnnxTR 0.9.0 dentro
  do programa (Python 3.14), só detecção. Opções do preditor e limiares
  escritos e fixos (os da comparação "D2"); só processador; modelo local
  `modelos\doctr\rep_fast_base-1b89ebf9.onnx` (42 MB, conferido pela soma
  SHA-256; o OnnxTR nunca recebe endereço de internet). Devolve palavras e
  linhas (as linhas pelo montador do próprio docTR, como na comparação).
- `core/ocr_tesseract.py`: `MotorTesseract`, um `tesseract.exe` por página,
  com o comando que o pytesseract montou na comparação ("T1": modelo do
  idioma em `modelos\tessdata`, `--psm 3`, `--dpi` só de 150 para cima, hOCR).
  Procura o `tesseract.exe` ao lado do programa instalado, na raiz do código,
  em Arquivos de Programas (winget), na instalação só do usuário e no PATH.
- `tests/test_ocr_doctr.py` (41) e `tests/test_ocr_tesseract.py` (36; 52 com
  `OCR_22=1`): sem o OCR, "de mentira" (ausente, danificado, morre, trava,
  lixo, 1,5 MB de aviso, cancelar); com o OCR, as páginas do 1.3.
- `.venv`: `onnxtr==0.9.0` e 20 dependências novas (pyclipper, rapidfuzz,
  pypdfium2, langdetect, huggingface-hub, httpx...), **nenhuma versão já
  instalada mudou** (`pip check` limpo). `requirements.txt`: `onnxtr==0.9.0`
  e `pyclipper==1.4.0` travados.

**Resultado contra a comparação do 1.3 (22 páginas):**

- docTR: as **mesmas palavras e linhas nas 22** (mesma contagem: 3.841
  palavras, 915 linhas; área em comum 100,00%, e 99,99% no Palatino 9, onde
  as caixas diferem em 0,0000000000001 ponto e só o arredondamento do desenho
  muda um pixel). Isso com o onnxruntime 1.28 do programa; a comparação usou
  o 1.30.
- Tesseract: as **mesmas linhas nas 22** (mesma contagem, área 100,00%, e a
  mesma confiança média em cada linha). Horas 11 e Graduale 222 continuam
  sem nenhuma linha, como na comparação.

**Tempos (PC do Samuel, Ryzen 7 5800H; máquina DIVIDIDA com outro agente
trabalhando ao mesmo tempo: servem para comparar, não como número final):**
docTR: carregar o modelo 0,9 s (mais 1 a 3 s para importar o OnnxTR na
primeira vez); por página mediana 0,65 s (0,58 a 1,1 s). Tesseract: por página
mediana 1,3 s (0,2 s no Graduale 222 a 5,2 s no Opus 256), já contando abrir o
programa a cada página.

**O que deu errado no caminho (não repetir):**

1. **O "hocr" do fim do comando não liga o hOCR aqui.** Rodando o
   `tesseract.exe` à mão com `... hocr` e a pasta `modelos\tessdata`, sai só
   texto e o aviso "read_params_file: Can't open hocr": esse arquivo de
   configuração fica em `tessdata\configs\` da instalação, e a
   `modelos\tessdata` não tem essa pasta. Na comparação funcionou porque o
   pytesseract põe `-c tessedit_create_hocr=1` antes. A ponte usa o `-c` (e
   deixa o "hocr" de fora, porque lá ele não fazia nada).
2. Um teste usou `pytest.approx` com lista dentro de lista, que o pytest não
   aceita; trocado por `np.allclose`.

**Ressalvas:** o empacotador e o instalador ainda não levam o modelo do
docTR, o `tesseract.exe` nem os `.traineddata` (vem na ligação); o OnnxTR
empacotado pelo PyInstaller não foi testado; a tela ainda não tem o
ligar/desligar.

---

## Tentativa 31 — rede de segurança: o trabalho antigo é guardado antes de a conferência recomeçar (29/09/2026)

**Data:** 29/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09, "GRAVE, antigo, mesma família: livro que mudou
de pasta [...] perde o trabalho de vez" (decisão da gerente, commit `2856987`:
primeiro a rede de segurança, depois o conserto, depois a mensagem).

**O que acontecia:** quando o trabalho salvo não combinava com o livro
recém-analisado, a conferência recomeçava e o `projeto.json` era regravado na
hora (`_salvar_agora`, no fim de `_analise_pronta`), sem cópia. Qualquer
engano na comparação (como o do livro que mudou de pasta) virava perda de vez.

**O que mudou:** `projetos.guardar_copia_do_trabalho(resumo)` copia, antes de
regravar, o `projeto.json`, o `acoes.jsonl` e o `posicao.json` para
`projeto.antigo-AAAA-MM-DD-HHMM.json`, `acoes.antigo-...jsonl` e
`posicao.antigo-...json`, na pasta do projeto. Nunca sobrescreve: se já há
cópia naquele minuto, a nova ganha `-2`, `-3`..., e cada arquivo é criado em
modo exclusivo. Nada é apagado. Chamada em `_analise_pronta` sempre que o
salvo não volta (inclusive quando o `projeto.json` não dá para ler, que também
seria regravado). O `acoes.jsonl` não é descartado pelo recomeço (as ações
novas vão para o fim dele), mas vai junto para a cópia ficar inteira.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, 8 casos (6 falhavam antes:
a função não existia e o recomeço não deixava cópia): cópia com os três
arquivos, nunca sobrescreve, só o que existe; na janela de verdade, recomeço
guarda o trabalho igualzinho, `projeto.json` ilegível também é guardado,
reabrir sem mudar nada e livro novo não fazem cópia.

**Fica de fora:** o "começar de novo" do cartão da tela inicial continua
apagando o trabalho sem cópia (é pedido pela pessoa, com pergunta de
confirmação).

---

## Tentativa 32 — o livro que mudou de pasta (ou cópia em outra pasta) mantém o trabalho (29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09, "GRAVE, antigo, mesma família: livro que mudou
de pasta (ou cópia do mesmo PDF em outra pasta) perde o trabalho de vez".

**O que acontecia:** o projeto era achado pela assinatura do arquivo
(`achar_por_assinatura`, e a tela inicial "religa sozinha"), mas
`combina_com` só olhava o caminho: o antigo (que não existe mais, ou é outro
lugar) e o novo eram "livros diferentes", e a conferência recomeçava.

**O que mudou:** `combina_com(salvo, recem, assinatura=...)`: além do mesmo
arquivo (`mesmo_arquivo`), aceita o arquivo recém-aberto com a assinatura do
projeto (`resumo.assinatura`). A contagem de folhas e páginas continua
valendo. Assinatura vazia (projeto de antes da assinatura) não vale.
`_analise_pronta` passa a assinatura; o caminho novo já era o gravado (no
`projeto.json` pela Tentativa 28, no resumo pelo `abrir_livro`).

**O risco do caso contrário (dois PDFs diferentes com a mesma assinatura):**
a assinatura é o tamanho do arquivo mais 64 KB do começo, do meio e do fim
(resumo blake2b de 128 bits). Dois PDFs diferentes só a dividem se tiverem o
mesmo tamanho em bytes **e** forem iguais nesses três pedaços; o fim de um PDF
tem a tabela de posições dos objetos, que muda quando qualquer coisa muda de
tamanho. Arquivo de até 192 KB é lido inteiro. O risco existe só para um PDF
editado "no lugar", sem mudar de tamanho, no miolo fora dos três pedaços
(raro). E ele já existia: `achar_por_assinatura` já ligava o projeto ao
arquivo pela assinatura; a comparação do caminho só o escondia quando o livro
estava em outra pasta.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 8 (7 falhavam antes,
4 deles com "Você mudou as opções..."): livro movido aberto pelo "Abrir",
"continuar" depois de religar sozinho, livro apontado à mão ("procurar de
novo"), cópia em outra pasta (em todos voltam páginas, filtros, corte,
alertas, conferidas e Histórico, e o caminho novo fica gravado no resumo e no
projeto); outro PDF com o mesmo nome e o mesmo número de páginas em outra pasta
não recebe o trabalho (e o do primeiro fica intacto); `combina_com` direto
(assinatura igual, diferente, vazia, e igual com outro número de páginas).

---

## Tentativa 33 — a mensagem do recomeço diz o motivo de verdade e onde está a cópia (29/09/2026)

**Data:** 29/09/2026
**Situação:** feito, a conferir (teste de máquina; o texto é para o Samuel ler)
**Bug:** Lista de bugs, 29/09, "A mensagem 'Você mudou as opções...' diz 'outro
número de páginas' para qualquer motivo".

**Antes:** "Você mudou as opções desde a última vez, e o livro ficou com outro
número de páginas. Comecei a conferência de novo - o trabalho antigo não serve
para páginas diferentes." Para qualquer motivo, inclusive o livro que só tinha
mudado de pasta, e sem dizer que havia cópia.

**Agora** (exemplo, livro com a opção "Dividir folhas ao meio" mudada):

> Comecei a conferência deste livro de novo: o trabalho salvo tinha 3 páginas
> e agora o livro tem 4. Isso acontece quando se muda a opção “Dividir folhas
> ao meio”.
>
> O trabalho anterior não foi apagado. Guardei uma cópia dele, que pode ser
> recuperada:
> C:\Users\...\EditorImpressao\projetos\<livro>\projeto.antigo-2026-09-29-1930.json

Os outros motivos: "o arquivo aberto agora não é o mesmo livro do trabalho
salvo" e "o arquivo tinha N folhas quando o trabalho foi salvo e agora tem M:
ele foi trocado ou mudou". Se a cópia falhar: "Não consegui guardar uma cópia
do trabalho anterior." O motivo vem de `projetos.motivo_para_nao_combinar`,
que passou a ser também a regra do `combina_com` (um lugar só decide e
explica). **Quando** a mensagem aparece não mudou.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 7 (falhavam antes): os
três motivos, singular ("1 página"), sem motivo quando combina, a mensagem na
janela de verdade (motivo, "não foi apagado", caminho da cópia, sem "Você
mudou as opções") e sem cópia não promete cópia. Em
`tests/test_mesmo_livro_outro_caminho.py`, a conferência "sem a mensagem"
passou a exigir nenhum aviso (antes procurava o texto velho).

---

## Tentativa 34 — comparação automática entre os OCRs (item 1.3, 29/09/2026)

**Pedido (Samuel, 29/09):** "comparação automática entre eles (onde
discordam, a página vai para 'Para revisar')". De fábrica docTR fast_base +
Kraken; Tesseract instalado mas desligado. **Nada foi ligado ao programa.**

**O que ficou:**

- A ponte do Kraken passou a devolver o tipo comum (`ResultadoOCR`):
  `perdidas = falhas_contorno + linhas_sem_contorno`, `extra` com as regiões
  e as duas contagens. O `ResultadoKraken`, a `LinhaKraken` e o `de_kraken()`
  saíram. `core/ocr_comum.py` ganhou `para_dict`/`de_dict`, para guardar um
  resultado em JSON e ler de volta sem rodar o OCR de novo.
- `core/ocr_comparar.py`: `comparar(resultados)` diz se a página vai para
  revisar e por quê, em português comum. Também devolve as zonas de desacordo
  e a máscara de texto combinado para o 1.4.
  - **Discordar** é: uma área do tamanho de uma palavra ou maior (1,4
    quadrados de altura de linha) que um OCR marca como texto e o outro não,
    com folga de 0,35 altura de linha e sem as lascas mais finas que 0,4; uma
    linha perdida avisada pelo próprio OCR; ou um OCR ligado que falhou.
  - **Máscara**: voto por linha. A linha entra se a maioria dos OCRs a vê.
- `tests/test_ocr_comparar.py`: 16 testes sintéticos e as 22 páginas. Com
  `OCR_22=1`, roda também as pontes de verdade.
- `relatorios/fase1-1.3-comparar-ocr-2026-09-29/`: relatório (três formatos),
  `rodar_pontes.py`, `calibrar.py`, `resultados.json` e as imagens das zonas.

**Resultado (docTR + Kraken, 22 páginas):**

- 10 vão para revisar e todas têm erro conhecido; 0 revisar à toa.
- 1 erro conhecido não pego: no Graduale 223, os dois perdem o mesmo texto.
- No Opus 3, a página vai para revisar certo, mas pelo vão entre "OPUS" e
  "MAJUS", não pelo erro real.
- Com o Tesseract ligado, vão para revisar 19 a 21 de 22.
- Voto por linha: 99,4% do texto achado sem contar o Opus 256; 2 páginas
  acima de 1% de figura (Horas 13 e 47, pelo alargamento de 15% colado na
  moldura). A união dá 7 páginas acima de 1% de figura; a interseção perde
  texto (98,5%).
- Comparar leva 39 ms por página (mediana).

**O que falhou (não repetir):**

1. Comparar linha por linha ("esta linha está coberta pelo outro?") não
   separava as páginas: uma linha do Tesseract que cobre meio parágrafo fica
   "meio coberta". Comparar áreas separou.
2. Número de linhas e "linha partida em duas" não servem para decidir: em
   página boa variam demais (Horas 27: 38 × 74 linhas; 20 linhas partidas).
   Ficam só como medida.
3. Primeira versão das frases: `str.capitalize()` escrevia "O doctr" e
   "o Kraken" com a caixa errada; consertado.

**Ressalva principal:** calibrado nas mesmas 22 páginas em que foi medido, e
a folga é pequena (maior zona em página boa 1,13; menor em página com erro
1,64; limite 1,4).

---

## Tentativa 35 — todo salvamento vai para a pasta do projeto aberto (bug grave, 29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador,
`relatorios/conferir/fase1-2026-09-29-trabalho-salvo/verificador/`, prints
p15 a p17): "fechar o programa com um livro aberto grava o trabalho dele
também na pasta de outro projeto de mesmo nome".

**O que acontecia:** o `closeEvent`, o "Confirmar e processar" e o fim do
processamento chamavam `historico.salvar_projeto`, que escolhia a pasta pelo
**nome** do livro (`historico.pasta_do_projeto`), e não pela pasta do projeto
aberto (`resumo.pasta`). Com dois PDFs diferentes de mesmo nome, fechar com o
segundo aberto gravava o estado dele por cima do trabalho do primeiro, sem
cópia. Depois do `3cfb682`, o primeiro aceitava calado (assinatura bate com o
arquivo, e o estado era do outro livro). E, como esse nome era limpo de outro
jeito que o das pastas dos projetos (`nome_de_arquivo_seguro` × `_sem_acento`),
nasciam pastas-sombra só com `projeto.json`.

**O que mudou:** os três lugares chamam `_salvar_agora` (grava com
`projetos.salvar_estado` na pasta do projeto aberto e atualiza o resumo). O
`closeEvent` já chamava; o segundo salvamento saiu. `historico.salvar_projeto`
e `historico.carregar_projeto` foram tirados (ninguém mais os chamava; um
comentário no lugar explica por quê e pede para não recriar);
`historico.pasta_do_projeto` ficou, com aviso de não usar para gravar.

**A rede de segurança (`guardar_copia_do_trabalho`) não precisa cobrir este
caminho:** agora cada projeto só grava na própria pasta, o estado do próprio
livro; o que sobra de "gravar por cima" é o recomeço (já coberto) e o
fechamento antes da análise (Tentativa 36).

**As duas pastas-sombra da pasta real do Samuel** ("Giovambattista Palatino
cittadino romano" e "Rhetorica Christiana -  Fray Diego Valadés", só com
`projeto.json`): não foram tocadas. Depois do conserto o programa não grava
mais nelas; como não têm `resumo.json`, continuam fora da tela inicial e fora
da busca por assinatura (inertes). O único efeito que sobra: ocupam o nome, e
um projeto novo desses livros ganha "(2)", "(3)" no nome da pasta e do cartão.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 3 (falhavam antes):
fechar com o outro livro de mesmo nome aberto não mexe no primeiro (bytes
iguais) e grava o segundo na pasta dele, sem pasta-sombra; o primeiro,
reaberto, volta com o trabalho; "Confirmar e processar" e o fim do
processamento gravam na pasta do projeto. A reprodução do verificador
(`reproduz_mesmo_nome.py`, rodada numa cópia com pasta própria) agora mostra o
livro 1 intacto.

---

## Tentativa 36 — fechar antes do fim da análise não grava mais por cima do trabalho (bug grave, 29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, prints p18 a p20):
"abrir um livro salvo e fechar o programa antes do fim da análise [...] apaga
o trabalho, sem cópia e sem aviso na próxima vez".

**O que acontecia:** entre abrir o livro (Abrir, arrastar, Windows,
"continuar") e o fim da análise, o projeto em memória está vazio (0 páginas).
O `closeEvent` chamava `_salvar_agora`, que o gravava por cima do trabalho
salvo, e o resumo passava a "0 conferidas".

**O que mudou:** `JanelaPrincipal.trabalho_carregado`: falso ao abrir o livro
e ao disparar uma análise (que refaz as páginas no próprio projeto),
verdadeiro em `_analise_pronta`. Enquanto é falso, `_salvar_agora` não grava
(nem o `projeto.json` nem o resumo) se `projetos.tem_trabalho_salvo(resumo)`:
o `projeto.json` existe e tem páginas, ou existe e não dá para ler. Livro sem
trabalho salvo continua gravando nesse intervalo (só as opções, como antes: é
o que o "continuar" traz de volta).

**O que se perde agora nesse intervalo:** só as mudanças feitas na tela "O que
fazer" de um livro com trabalho salvo, se o programa for fechado antes de
"Conferir" (antes, perdia-se o trabalho inteiro).

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 6 (4 falhavam antes):
fechar no "O que fazer" (trabalho e cartão intactos, e o trabalho volta),
fechar durante a análise do "continuar", fechar no meio de uma nova análise,
`projeto.json` ilegível não é regravado; e os dois que já passavam e continuam:
livro novo fechado no "O que fazer" grava as opções, e depois da análise fechar
grava normalmente. A reprodução do verificador
(`reproduz_fechar_no_o_que_fazer.py`, numa cópia com pasta própria) agora
mostra o trabalho intacto.

---

## Tentativa 37 — reabrir um livro traz as opções salvas na tela "O que fazer" (29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, prints p25 e p26):
"Dividir folhas ao meio" desmarcada num livro conferido voltava marcada ao
reabrir pelo "Abrir", arrastando ou pelo Windows, e a conferência recomeçava
sem a pessoa mudar nada. Resolve também o registrado "reabrindo pelo 'Abrir',
'O que fazer' mostra o filtro do livro em Original" (t10, rodada de 18:26).

**O que acontecia:** só o "continuar" trazia as opções salvas; `abrir_livro`
(por onde passam o "Abrir", o arrastar e o Windows) abria com as de fábrica.

**O que mudou:**
- `abrir_livro`: livro com projeto salvo traz as opções dele (dividir, limpar,
  filtro do livro, endireitar, cortar, cadernos), por
  `_trazer_opcoes_salvas`, que o `_continuar_projeto` também usa agora.
- `ui/tela_opcoes.py` (`carregar`): enquanto as caixinhas são acertadas, o
  projeto fica desligado da tela, e o `_mudou` roda uma vez só no fim. Antes,
  cada caixinha que mudava gravava no projeto o estado das outras ainda com o
  valor do livro anterior (parte do bug "as caixinhas...", Lista de bugs de
  29/09): com o livro anterior sem "Limpar", o livro salvo abria sem ele.

**O que fica do bug "as caixinhas perdem o que se muda na volta":** o que se
muda na tela "O que fazer" **depois** de uma conferência (voltar, mudar, e
"Conferir" de novo) ainda se perde quando o salvo volta por cima em
`_analise_pronta`, nas opções que não mudam o número de páginas (limpar,
filtro do livro, endireitar, cortar, cadernos). Não é deste conserto.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 4 (2 falhavam antes):
reabrir pelo "Abrir" traz "Dividir" desmarcada e o filtro do livro, e não
recomeça; as caixinhas do livro anterior não contaminam as salvas; o
"continuar" continua trazendo; livro novo abre com as de fábrica. A reprodução
do verificador (`reproduz_dividir_desmarcado_abrir.py`, numa cópia com pasta
própria) agora mostra 3 páginas, o trabalho e nenhum aviso.
