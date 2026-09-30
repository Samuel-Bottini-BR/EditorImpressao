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

---

## Tentativa 38 — o caminho da cópia não deixa mais "D:" sozinho numa linha (29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, print p23): na mensagem
do recomeço, o caminho da cópia quebrava a linha logo depois de "D:".

**Por quê:** na regra de quebra de linha do Qt, as barras `\` de um caminho
não são lugar de quebra; o único lugar antes do primeiro espaço é depois de
"D:". Quando o caminho não cabe na largura da caixa, o "D:" fica sozinho.

**O que mudou:** `_frase_do_recomeco` põe um WORD JOINER (U+2060, invisível)
entre a letra da unidade e o resto do caminho. A caixa se alarga para o
caminho caber (conferido com a caixa de verdade: 716 → 728 pontos no exemplo
do print) e, se o caminho tiver espaço, quebra no espaço.

**Ressalvas:** quem copiar o texto da caixa (Ctrl+C) leva o sinal invisível
junto no caminho. Um caminho sem espaço nenhum e mais largo que a caixa
máxima do Qt (cerca de 1000 pontos) continua cortado, como antes.

**Teste:** `tests/test_trabalho_nao_se_perde.py`,
`test_caminho_da_copia_nao_deixa_a_letra_da_unidade_sozinha`: mostra a caixa
de verdade, com a folha de estilo do programa, e confere as linhas em que o
Qt quebra o texto (falhava antes: uma linha "D:").


---

## Tentativa 39 — os três detectores de texto no instalador, com o Visual C++ oficial (item 1.3, 29/09/2026)

**Pedido (Samuel, 29/09, Registro de mudanças):**
- "O instalador roda o instalador oficial da Microsoft, e pula se já estiver
  instalado": as DLLs do Visual C++ deixam de ir dentro do motor do Kraken.
- O Tesseract vai com os seis idiomas da comparação.
- Todos os OCRs vão instalados, com o Tesseract desligado de fábrica.

**O que ficou:**

- `montar_motor_kraken.py` (commit separado):
  - não copia mais as seis DLLs do Visual C++;
  - tira o `vcruntime140.dll` e o `vcruntime140_1.dll` que vêm no zip do
    Python, que são mais velhos e misturariam versões;
  - tira os 23 atalhos `Lib\site-packages\bin\*.exe`;
  - `--levar-dlls-do-visual-c` faz como antes, só para teste;
  - no teste do fim, a DLL do Visual C++ tem de vir do motor ou do System32.
- Motor novo em `saida_teste\motor-kraken` (1143 MB). Com o Visual C++ 14.50
  do Windows, deu as mesmas linhas do Kraken do WSL em 6 páginas, inclusive
  as 8 perdidas do Opus 256. O motor antigo em `ferramentas\motor-kraken` não
  foi tocado; o empacotador o recusa.
- `empacotar.py`: a versão em pasta (e, por ela, o instalador) leva:
  - o motor do Kraken, em `motor-kraken\`;
  - o Tesseract, em `tesseract\`: os 27 arquivos, `LICENSE`, `AUTHORS`,
    `LEIA-ME-TESSERACT.txt` e `tessdata\` com lat, ita, por, fra, eng e
    script/Fraktur;
  - o modelo do docTR, em `_internal\modelos\doctr\`;
  - o OnnxTR, pelas importações escondidas do PyInstaller.
- O `vc_redist.x64.exe` oficial:
  - é baixado de `https://aka.ms/vs/17/release/vc_redist.x64.exe` para
    `ferramentas\downloads`;
  - é conferido pela assinatura digital, porque não há soma publicada fixa;
  - vai só no instalador.
- **A trava vale para tudo:** se faltar peça ou o motor for do jeito velho, o
  empacotamento para antes do PyInstaller. Depois, cada peça é conferida na
  pasta e no registro do Inno.
- `instalador.iss`:
  - `#error` para cada peça que faltar;
  - `[Code]`: lê a chave oficial `...\VisualStudio\14.0\VC\Runtimes\x64` nas
    duas vistas do registro e roda o vc_redist em silêncio só se faltar ou
    for mais velho;
  - trata os resultados 0, 1638 e 3010, e para qualquer outro mostra um aviso
    em português.
- `core/ocr_diagnostico.py` e `main.py --conferir-ocr`: rodam os três
  detectores numa imagem, sem janela, e gravam onde cada um achou o seu
  motor. É o que prova que o programa **empacotado** funciona.
- `core/ocr_tesseract.py`: no programa instalado, procura os idiomas em
  `{app}\tesseract\tessdata`.

**Resultado:**

- Instalador de 561 MB (o de 28/09 tinha 209 MB), com 35.086 arquivos:
  - motor do Kraken: 34.521 arquivos, 1091 MB;
  - Tesseract: 36 arquivos, 177 MB;
  - Visual C++: 24 MB.
- O Inno levou 14 min para comprimir; o empacotamento inteiro, 21 min.
- O programa empacotado, rodado de `dist\` com `--conferir-ocr`, achou os três
  detectores. Deu as mesmas linhas que no código em 4 páginas: Opus 20
  (2/2/2), Palatino 57 (24/16/17), Graduale 222 (20/0/13), Horas 11 (12/0/16).
- O Kraken empacotado carregou o Visual C++ só do System32.

**O que deu errado no caminho (não repetir):**

1. **O motor do Kraken, aberto pelo programa empacotado, carregava o Visual
   C++ da pasta `_internal\` do programa.**
   - Causa: o PyInstaller marca `_internal` com `SetDllDirectoryW`, e o
     Windows passa essa marca ao processo filho.
   - Reproduzido fora do empacotado.
   - Conserto: `ocr_comum.abrir_processo` tira a marca só durante o `Popen` e
     a devolve em seguida; também tira `_internal` do PATH do filho. Vale para
     o Kraken e o Tesseract.
2. **Caminho relativo** da imagem ou da pasta do motor era lido de dentro da
   pasta do motor, que roda com `cwd` = a pasta dele. Agora vai absoluto
   (commit do motor).
3. **O Inno põe a versão no fim da linha "Compressing:"** de um `.exe` sem
   `ignoreversion` ("... vc_redist.x64.exe   (14.44.35211.0)"). A conferência
   não reconhecia o vc_redist, e a trava apagou o primeiro instalador bom:
   14 min perdidos. Consertado em `_comprimidos`, com teste.
4. **A ferramenta Bash desta sessão corta pela metade as barras invertidas**
   dentro de heredoc. Vários trechos com `\\` saíram errados; use a
   ferramenta de edição para código com barra invertida.

**Não testado:**
- instalar;
- rodar o vc_redist;
- uma máquina sem o Visual C++;
- o notebook do Kaique.

Nada foi instalado neste PC.

---

## Tentativa 40 — "cancelar" a análise não desliga mais o salvamento (bug grave, 29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, 2ª rodada, prints q21
a q23): nascido do conserto `4c01fa6` (Tentativa 36). Livro com trabalho, na
conferência → "Voltar para as opções" → "Conferir" → "cancelar" em "Olhando o
livro...": a janela voltava para a conferência, mas o marcador
`trabalho_carregado` ficava falso e nada mais era gravado até fechar, sem
aviso.

**O que mudou (`ui/janela_principal.py`, `ui/tarefas.py`):**
- `analisar` guarda o valor do marcador e analisa uma **cópia rasa** do
  projeto (`copy.copy`): `analisar_projeto` só atribui listas novas
  (`folhas`, `paginas`, `observacoes`, `tem_camadas`), então o projeto da
  tela, com o trabalho, fica intacto até `_analise_pronta`. Antes, um cancelar
  no instante em que a análise terminava podia deixar as páginas novas (em
  branco) no projeto da tela.
- `cancelar` e `_falhou_na_analise` devolvem o marcador ao valor de antes
  (`_parar_a_analise`). Livro recém-aberto com trabalho salvo continua sem
  gravar por cima; livro que veio da conferência volta a gravar.
- `_analise_pronta` ignora resultado de análise cancelada ou que não é mais a
  da vez (`TarefaAnalise.foi_cancelada`, remetente do sinal): antes, um
  resultado que chegava depois do "cancelar" entrava mesmo assim.
- `abrir_livro` marca como cancelada a análise do livro de antes (trocar de
  livro no meio): o resultado dela não entra mais no livro novo.

**Outros caminhos em que o marcador poderia ficar falso, conferidos:** erro na
análise (coberto); trocar de livro no meio (coberto: o livro novo começa com
o marcador falso e só o liga a análise dele); "voltar" do "O que fazer" para
a tela inicial (não grava nada nesse intervalo, e o próximo livro reinicia o
marcador); processar (não mexe no marcador); "começar de novo" (apaga o salvo
antes, então grava).

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 5 (3 falhavam antes):
cancelar com a análise de verdade volta à conferência e continua gravando
(pelo relógio e ao fechar); cancelar quando a análise já tinha acabado não põe
páginas em branco; erro na análise não desliga o salvamento; cancelar num
livro recém-aberto continua sem gravar por cima; trocar de livro no meio da
análise não mistura os livros. A sonda do verificador (parte P1, numa cópia
com pasta própria) agora mostra as mudanças no disco depois de trabalhar e de
fechar.

---

## Tentativa 41 — os testes nunca gravam na pasta de dados real (29/09/2026)

**Data:** 29/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, 2ª rodada): "Testes
gravam na pasta de dados real quando rodados sem `LOCALAPPDATA` próprio"
(`erros.log` a cada rodada; e, antes do `7bb3905`, as pastas-sombra
`projetos\camadas` e `projetos\comum`).

**O que mudou:** `tests/conftest.py` (novo). Antes de coletar os testes
(`pytest_configure`), `LOCALAPPDATA` passa a apontar para
`saida_teste\pytest_dados\<data-hora>-<processo>`, apagada no fim da rodada
(`pytest_unconfigure`). Tudo o que o programa grava lê a variável na hora
(`historico.pasta_de_dados`: projetos, `historico.json`,
`configuracoes.json`, `erros.log`), então nada precisa ser trocado módulo por
módulo. O valor verdadeiro fica em `EDITOR_IMPRESSAO_LOCALAPPDATA_REAL`.

**Conferido:** lista de todos os arquivos da pasta de dados real
(`%LOCALAPPDATA%\EditorImpressao`, 58 entradas, inclusive o `erros.log`), com
tamanho e data em nanossegundos, antes e depois da bateria inteira (1131
passaram, 1 pulado): **iguais**. A pasta da rodada em `saida_teste\` foi
apagada no fim. Nada da pasta real foi apagado (as pastas `camadas` e
`comum` continuam lá, para a gerente decidir com o Samuel).

**Teste:** `tests/test_pasta_de_dados_dos_testes.py` (3): a pasta de dados é
a dos testes; `erros.log`, projetos, `historico.json` e `configuracoes.json`
ficam fora da pasta real; um erro registrado vai para o log de mentira.

**Fica de fora:** a pasta Documentos\Editor de Impressão (saída padrão) não é
trocada; nenhum teste grava nela hoje (conferido na mesma comparação: a lista
não mudou). O TEMP do Windows continua sendo usado pelo `tmp_path` do pytest.

---

## Tentativa 42 — o "continuar" de um cartão abre exatamente aquele projeto (29/09/2026)

**Data:** 29/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 29/09 (parecer do verificador, 2ª rodada, prints q24
e q25): com dois projetos do mesmo PDF, o "continuar" do cartão mais antigo
abria o mais recente. O trabalho do antigo ficava no disco, mas inalcançável
pelo cartão.

**Por quê:** o cartão chamava `_continuar_projeto(resumo)`, que chamava
`abrir_livro(caminho)`, que achava o projeto pela assinatura do arquivo
(`achar_por_assinatura`: o mais recente) e esquecia o cartão.

**O que mudou:** `abrir_livro(caminho, resumo=None)`: com `resumo`, abre
**esse** projeto. O "continuar" e o "começar de novo" do cartão passam o
resumo do cartão. Sem ele ("Abrir", arrastar, Windows), continua achando pela
assinatura (o mais recente), como sempre.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 4 (1 falhava antes; o
do "começar de novo" passava por acaso, porque apagar o trabalho regravava o
resumo e tornava aquele cartão o mais recente): "continuar" do cartão mais
antigo abre ele, grava nele e não toca no outro; "continuar" do mais recente
abre ele; "começar de novo" limpa e abre aquele projeto; o "Abrir" continua
achando o mais recente.

---

## Tentativa 43 — a pergunta do fundo: uma vez por livro, inclusive nos que já existem (item 1.1, 29/09/2026)

**Data:** 29/09/2026
**Situação:** feito, a conferir (teste de máquina; a pergunta é de tela)
**Pedido (Samuel, 29/09, Registro de mudanças):** a pergunta "Este livro tem
fundo separado. Quer tirar o fundo?" aparece "uma vez por livro, inclusive
nos que ele já tem: na próxima vez que abrir, e depois não pergunta mais"
(substitui a decisão da gerente de perguntar só em projeto novo).

**O que mudou:**
- `modelos.Projeto.perguntou_fundo` (campo novo, autorizado pela decisão):
  projeto antigo sem o campo volta com `False` (= ainda não perguntou).
- `abrir_livro` (por qualquer caminho: "Abrir", arrastar, Windows,
  "continuar") pergunta se o PDF tem camadas e o projeto salvo ainda não
  perguntou. Livro sem camadas: nunca.
- Qualquer resposta (Sim, Não, Esc, X) grava "já perguntou". Com trabalho
  salvo, grava **só esse campo** no `projeto.json`
  (`projetos.anotar_no_estado`), sem tocar no trabalho (nessa hora
  `_salvar_agora` não grava por cima, Tentativa 36). Livro novo grava o projeto
  (só as opções).
- **Sim** num livro novo: como antes (o filtro do livro vira "Tirar o fundo" e
  as páginas nascem nele). **Sim** num projeto que já tem páginas: quando o
  trabalho carrega, o livro inteiro vai para "Tirar o fundo" numa ação só do
  Histórico ("Tirar o fundo em N páginas (resposta à pergunta do fundo)"), que
  se desfaz; o resto do trabalho (corte, conferidas, alertas) fica. Vale também
  para o "Sim" respondido durante a análise do "continuar".
- **Não/Esc/X:** nada muda; projeto antigo nunca vem com o fundo tirado sem o
  "Sim".

**Decisão minha, a conferir:** depois do "começar de novo" (que apaga o
projeto salvo) a pergunta aparece de novo, como num livro novo.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 10 (8 falhavam
antes): livro novo pergunta uma vez só (e não de novo pelo "Abrir"); projeto
antigo pergunta na próxima abertura e não mais; pelo "continuar" também;
Não, Esc e X não mudam o trabalho e contam como perguntado; Sim num projeto
antigo põe o livro inteiro no filtro e se desfaz pelo Histórico; Sim durante a
análise do "continuar" vale; livro sem camadas nunca pergunta, nem o antigo;
o campo vai e volta do disco. Os testes antigos do aviso
(`tests/test_tirar_fundo_no_programa.py`) continuam passando.

---

## Tentativa 44 — a pergunta do fundo: o "Sim" troca só as páginas em Original, e a resposta vale a qualquer momento (item 1.1, 30/09/2026)

**Data:** 30/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bugs:** Lista de bugs, 30/09 (parecer do verificador, 3ª rodada, prints s15 a
s23), e decisão do Samuel de 29/09 (commit `f94f69b`): o "Sim" num livro
antigo troca **só as páginas que estão em "Original"**.

**O que acontecia:**
- O "Sim" trocava todas as páginas, inclusive as que o Samuel tinha posto em
  outro filtro de propósito; e o desfazer não devolvia o filtro do livro (s17).
- Pelo "continuar", a resposta dada **depois** do fim da análise era jogada
  fora: a janela reconhecia o livro pelo objeto do projeto, e a análise troca
  esse objeto (s19 a s21). Nada ficava anotado e a pergunta voltava sempre.
- "Sim" e fechar (ou voltar, ou cancelar) antes de "Conferir": o "Sim" ficava
  só na memória e se perdia, mas a pergunta já estava anotada como respondida
  e não voltava (s23).

**O que mudou (`ui/janela_principal.py`, `historico_acoes.py`):**
- O livro que perguntou é reconhecido pela **pasta do projeto**, não pelo
  objeto: a resposta vale antes, durante ou depois da análise.
- **"Sim"** com o trabalho na tela: aplica na hora. Livro sem trabalho salvo
  (novo): o filtro do livro vira "Tirar o fundo" e é gravado com as opções,
  junto com o "já perguntou" (fechar antes de "Conferir" não perde nada).
  Projeto com trabalho salvo ainda não carregado: o "Sim" espera o trabalho
  carregar e **só então** conta como respondido; se o programa fechar, a
  pessoa voltar ou cancelar antes, nada foi aplicado e nada fica anotado, e a
  pergunta volta na próxima abertura.
- **Por que assim:** é o mais simples e seguro. A alternativa, gravar o "Sim"
  direto no `projeto.json` do trabalho sem carregá-lo, pularia o Histórico
  (não daria para desfazer) e a trava que não grava por cima do trabalho antes
  da análise (Tentativa 36).
- **"Não", Esc e X:** anotados na hora (só o campo), a qualquer momento.
- O "Sim" num projeto com páginas troca **só as páginas em "Original"** e o
  filtro do livro, numa ação só do Histórico. O desfazer devolve os dois: a
  ação ganhou o campo `livro.filtro_padrao`, que `historico_acoes.aplicar`
  aplica no projeto e não nas páginas (arquivo de ações antigo não tem o
  campo: nada muda para ele).

**Testes:** `tests/test_trabalho_nao_se_perde.py`: o teste do "Sim" em
projeto antigo foi refeito (só as de Original; o desfazer devolve o filtro do
livro) e ganhou 8 casos (6 falhavam antes): desfazer numa sessão seguinte;
resposta depois do fim da análise do "continuar", com "Sim" e com "Não" (vale
e fica anotada); "Sim" e fechar, voltar ou cancelar antes de "Conferir" (a
pergunta volta e o trabalho fica igual); "Sim", cancelar e "Conferir" de novo
aplica o "Sim"; livro novo, "Sim" e fechar guarda o "Sim".

---

## Tentativa 45 — "cancelar" devolve as opções de antes da análise (30/09/2026)

**Data:** 30/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 30/09 (parecer do verificador, 3ª rodada, prints s34 a
s36; sonda `sonda3_opcao_e_cancelar.py`).

**O que acontecia:** a tela "O que fazer" muda as opções direto no projeto
aberto. Mudar uma opção (ex.: desmarcar "Dividir folhas ao meio"), clicar
"Conferir" e "cancelar" devolvia a conferência com as páginas de antes, mas a
opção nova ficava no projeto e era gravada com elas. Na abertura seguinte a
opção salva mandava recomeçar a conferência (com cópia e aviso, mas sem jeito
de trazer o trabalho de volta pela tela).

**O que mudou:**
- `ui/janela_principal.py`: `_sair_da_conferencia` guarda as opções do
  trabalho carregado (dividir, limpar, filtro do livro, endireitar, cortar,
  cadernos). Quando a análise é cancelada ou dá erro e a conferência de antes
  volta (`_parar_a_analise`), essas opções voltam para o projeto e para a tela
  "O que fazer".
- `ui/tela_opcoes.py`: `mostrar_opcoes()` acerta as caixinhas pelo projeto da
  tela sem abrir o folhear (o `carregar` passou a usá-la).
- Livro recém-aberto (sem trabalho na tela): a opção nova fica, como antes
  (não há páginas de antes para combinar).

**Fica como estava (a conferir se é o desejado):** mudar uma opção em "O que
fazer" e **fechar** o programa (ou voltar para o início) sem clicar
"Conferir" grava a opção nova com as páginas de antes, e a conferência
recomeça na abertura seguinte (com cópia e aviso). Não foi pedido; relatado.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 3 (2 falhavam antes):
cancelar depois de mudar "Dividir" volta com a opção de antes (no projeto e
na tela), grava assim e a abertura seguinte não recomeça; erro na análise
também devolve; mudar e conferir até o fim continua valendo (recomeço com
aviso). A sonda do verificador, numa cópia com pasta própria, agora mostra
"dividir na memória: True" depois do cancelar e 13 páginas sem aviso na
abertura seguinte.

---

## Tentativa 46 — item 1.2, segunda etapa: o detector de gravura do ScanTailor ligado ao processamento (29/09/2026)

**Data:** 29/09/2026
**Situação:** ligado, a conferir (teste de máquina + teste de olho do Samuel)
**Pedido:** decisão do Samuel (29/09): o 1.2 "em duas etapas: primeiro o
detector (já entregue como núcleo), depois a ligação ao programa".

**O que mudou:** a zona GRAVURA de cada página passa a vir do seletor do
ScanTailor Advanced (`core/gravura_scantailor.py` + `core/nativo/st_gravura.dll`),
chamado por `core/detectar_regioes.detectar(detector_de_gravura="scantailor")`,
pedido por `core/pipeline.garantir_selecao` na prévia e no PDF (depois do corte
e do endireitamento, na imagem da página). A letra e o papel continuam do
detector de antes, agora em volta da gravura nova. Escolha como parâmetro no
`core/` (sem campo nem botão ainda): `DETECTOR_DE_GRAVURA_PADRAO = "scantailor"`,
`FORMA_DA_GRAVURA_PADRAO = "livre"`; `pipeline.escolha_da_gravura` lê os campos
`detector_de_gravura`/`forma_da_gravura` do projeto quando existirem. DLL
faltando ou falhando: cai no detector antigo, motivo no log e em
`selecao.aviso_gravura`.

**Tentado e medido no caminho (o que ficou e o que não):**

1. *DPI da imagem que vai à DLL.* Dar a página no DPI em que foi desenhada:
   no Marial 150 (escaneado a 72 DPI) a mesma página de texto saía 98%
   "gravura" desenhada a 110 DPI e 3-5% a 72, 150, 200 ou 300. **Ficou:** a
   página vai à DLL no DPI do escaneamento (nunca mais pontos que o scan
   tem; teto 300). Assim a prévia e o PDF dão quase a mesma entrada.
2. *Tempo.* Primeira versão: prévia do Marial 0,6 a 1,3 s mais lenta. Duas
   coisas: (a) a DLL roda numa linha a parte, ao mesmo tempo que o modelo de
   layout e a tinta (solta o GIL; 72 chamadas em 4 linhas deram a mesma
   máscara que em série); (b) teto de trabalho da DLL: páginas que o PDF diz
   ter 72 DPI (Marial, Horas, Graduale) viram folhas de 24 x 33 a 36 x 51 cm
   e a DLL trabalhava em 11 a 26 milhões de pontos. **Ficou** um teto de 7
   milhões (`PONTOS_MAXIMOS_DA_GRAVURA`): acima dele se diz à DLL um DPI
   maior. Testado 6 milhões (a Escola, 6,9, entraria; e uma gravura
   sintética numa folha Carta a 150 DPI deixou de ser achada: prova de que
   dizer outro DPI muda o resultado) e 9 milhões (a detecção do Marial ficava
   0,3-0,6 s mais lenta).
3. *O que o ScanTailor marca e não é gravura.* Na página inteira, sem a caixa
   do conteúdo que o ScanTailor de verdade usa, ele marca: a faixa escura do
   scanner que o corte deixou (Marial 150 e 153; sem limpar, o Preto e branco
   do Marial 150 levava 12,8 s em vez de 2,3 s), a sombra da lombada (Horas
   27, tira de 1 cm na beirada), e borrões de tinta no meio do texto (palavras
   soltas, 0,06% a 0,15% da página). **Ficou:** `_limpar_gravura_do_scantailor`
   tira pedaço menor que 0,2% da página, pedaço que encosta na beirada e vive
   80% na faixa de 5% da beirada, e tira fina e comprida encostada na beirada.
   Uma mancha escura de canto que avança para dentro (Marial 151, canto de
   cima à esquerda) continua como gravura.
4. *Texto dentro da gravura do ScanTailor.* Onde o modelo de layout viu texto
   com letra miúda embaixo, o texto ganha (a mesma regra da legenda do
   Pesel): **ficou ligado** (`ESCRITA_GANHA_DO_SCANTAILOR = True`). Na Horas
   26, a forma livre enche o miolo da moldura; com a regra, o bloco do
   calendário volta a ser letra e sobra como gravura o papel liso em volta.

**Resultado da rodada** (`relatorios/conferir/fase1-1.2-ligacao-2026-09-30/`,
Mágico pro e Preto e branco, 21 páginas): melhorou a Horas 11 (iluminura
inteira), a moldura dourada da Horas 26 e 27, o Palatino 5 (só o retrato é
gravura), o título corrido do Marial, a tabela do Opus 256. **Piorou** o Opus
Majus 20 na forma livre (estátua lavada; na retangular sai perfeita) e o
Graduale 222 (pedaços da pauta viram gravura: blocos cinza e +11 a +17 s no
processar). A "retangular" como padrão não serve: 100% do Graduale 222, 31%
do Marial 153 (texto).

**Tempo (medida isolada, máquina dividida):** Marial, primeira prévia +0,5 s
(mediana 2,82 → 3,33 s); processar 10 páginas igual (Mágico pro 126 → 120 s;
Preto e branco 57 → 58 s).

**Riscos que continuam (para a conferência):** forma livre deixa a estátua
branca do Opus Majus 20 fora da gravura; o Graduale 222 tem pedaços da pauta
marcados como gravura (14% da página); a Horas 11 inteira vira gravura
(inclusive o centro claro com o texto); a Horas 13 mantém o triângulo sobre
"pag. 54". A aba Marcar ("detectar automaticamente") e o item 1.1
(`core/camadas.py`) continuam com o detector antigo.

---

## Tentativa 47 — "Conferir" logo depois do "cancelar" não derruba mais o programa (30/09/2026)

**Data:** 30/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 30/09 (parecer do verificador, 3ª rodada, print s33,
sonda `sonda3_thread.py`), antigo: "Conferir" menos de 0,1 s depois do
"cancelar" fazia o programa sumir, sem mensagem e sem nada no `erros.log`.

**Causa:** a análise cancelada termina a página em que está antes de parar.
Se nesse intervalo começava outra análise, a janela trocava `self.tarefa`, e
a análise antiga perdia a última referência do Python; o Qt destruía o
`QThread` ainda rodando e derrubava o processo ("QThread: Destroyed while
thread is still running", queda nativa com código 0xC0000409). Não é exceção
Python: o `sys.excepthook` não vê, por isso nada no log.

**O que mudou (`ui/janela_principal.py`):** `_trocar_tarefa` põe a tarefa nova
em `self.tarefa` e guarda a antiga, se ainda roda, em `_tarefas_saindo` até
ela acabar (as que acabaram saem da lista a cada troca). Vale para a análise
e para o processamento. Ao fechar o programa, espera também essas (até 3 s
cada). O resultado da antiga não entra (Tentativa 40).

**Teste:** `tests/test_cancelar_e_conferir_rapido.py`: roda num processo à
parte (a queda mata o processo) um livro de 12 folhas grandes, três vezes
"voltar", "Conferir", "cancelar", "Conferir" e "cancelar" em seguida. Antes:
o processo caía (código 3221226505). Depois: termina normalmente (3 rodadas
seguidas).

---

## Tentativa 48 — "Tirar da lista" não apaga mais as cópias de segurança (30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Pedido (Samuel, 29/09, Registro de mudanças, `f94f69b`):** "'Tirar da lista'
não deve apagar as cópias de segurança (`projeto.antigo-*`), ou pelo menos deve
avisar antes."

**Antes:** o "Tirar da lista" apagava a pasta inteira do projeto, com as
cópias `projeto.antigo-*` (e `acoes.antigo-*`, `posicao.antigo-*`) dentro.

**Escolha (a que não apaga nada das cópias):** antes de apagar a pasta do
projeto, `projetos.remover_da_lista` copia as cópias de segurança, o
`resumo.json` (diz de que livro são) e um `LEIA-ME.txt` para
`%LOCALAPPDATA%\EditorImpressao\copias-de-seguranca\<pasta do projeto> (tirado da lista em AAAA-MM-DD-HHMM)`.
- **Fora da pasta de projetos** de propósito: lá dentro, com o `resumo.json`
  copiado, viraria um cartão falso na tela inicial, e ocuparia o nome de um
  projeto novo do mesmo livro.
- Nunca por cima de outra (no mesmo minuto ganha "-2", "-3"...).
- **Se as cópias não puderem ser guardadas** (disco cheio, sem permissão),
  **nada é apagado** e o cartão continua na lista.
- Projeto sem cópias: nada é criado; a pasta sai como antes.
- A pergunta "Tirar da lista?" diz quantas cópias há e onde vão ficar, e tem
  os botões em português ("Tirar da lista" / "Não, deixar"), com o "não" no
  Enter (`ui/perguntas.py`, novo: pergunta e aviso com botões escritos por
  nós).

**O que continua se perdendo no "Tirar da lista":** o trabalho atual
(`projeto.json`, `acoes.jsonl`), como a pergunta já dizia ("a conferência
feita nele se perde"). Não foi pedido guardar; fica como ideia.

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 5 (falhavam antes):
as cópias vão para a pasta à parte, iguais byte a byte, com o resumo e o
LEIA-ME, e não viram cartão; sem cópias não cria pasta; duas vezes no mesmo
minuto não sobrescreve; se as cópias não puderem ser guardadas nada é
apagado; a pergunta avisa das cópias, em português, com o "não" no Enter.

---

## Tentativa 49 — sem cópia vazia em livro novo, e todos os botões em português (30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Bugs:** Lista de bugs, 30/09 (parecer do verificador, 3ª rodada): "Livro novo
com camadas ganha um `projeto.antigo-*.json` vazio" e "'Começar de novo?' com
botões em inglês" (print s25).

**Cópia vazia:** a resposta à pergunta do fundo grava um `projeto.json` só com
as opções (0 páginas); o fim da análise o via como "trabalho que não combina"
e guardava uma cópia inútil. Agora `_analise_pronta` só guarda cópia quando
havia trabalho (`projetos.tem_trabalho_salvo`: páginas, ou um `projeto.json`
que não dá para ler).

**Botões em inglês:** o programa não carrega a tradução do Qt, então toda
função pronta do Qt com botões padrão saía em inglês. Procurei em `ui/` e no
`main.py` e troquei todas:
- "Começar de novo?" ("Yes"/"No" → "Começar de novo" / "Não, deixar", com o
  "não" no Enter);
- os dois avisos "Este não é o mesmo livro" da tela inicial ("OK" →
  "entendi");
- "Renomear" (tela inicial), "Nome do arquivo..." e "Ir para a página..."
  (menu): "Cancel" → "Cancelar";
- "Tamanho da folha" (aba Bordas): "Cancel" → "Cancelar";
- o aviso do erro inesperado (`main.py`, `sys.excepthook`): "OK" → "entendi".

Tudo passa por `ui/perguntas.py` (`perguntar`, `avisar`, `pedir_texto`,
`pedir_numero`). As caixas de arquivo e pasta ("Abrir", "Escolher pasta") são
as do próprio Windows, já em português. O `teste_botoes.py` ganhou respostas
fixas para `pedir_texto`/`pedir_numero` (senão travaria esperando digitar).

**Testes:** `tests/test_botoes_em_portugues.py` (novo, 5): varre `ui/` e
`main.py` atrás das funções prontas do Qt com botões padrão (falhava antes:
achava as 9); confere os botões das caixas de `ui/perguntas.py` e do diálogo
do tamanho da folha. `tests/test_trabalho_nao_se_perde.py`, mais 3: livro
novo com camadas, com "Sim" e com "Não", não ganha cópia (falhavam antes); a
pergunta de "Começar de novo" em português com o "não" no Enter.
`tests/test_tela_inicio.py`: os dois testes que trocavam as funções prontas
do Qt passaram a trocar as de `ui/perguntas.py`.

---

## Tentativa 50 — nenhuma rodada de testes abre janela na tela (30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Pedido da gerente (30/09, plano no commit `4a30026`):** depois de uma caixa
"Tirar da lista?" de um teste meu ficar minutos na tela do Samuel esperando
clique, nenhuma rodada de pytest pode abrir janela na tela, e caixa sem
resposta tem de falhar rápido em vez de travar. O mesmo no `teste_botoes.py`,
por padrão.

**O que mudou:**
- `tests/conftest.py`, antes de qualquer teste: `QT_QPA_PLATFORM=offscreen`
  (o Qt desenha na memória; vale para os processos filhos). Só com
  `EDITOR_TESTES_COM_TELA=1` as janelas aparecem, de propósito.
- Vigia nas caixas modais: `QDialog.exec`, `QMessageBox.exec` e `QMenu.exec`
  fecham a caixa depois de 20 s sem resposta e o teste **falha** dizendo qual
  caixa foi (em vez de a bateria ficar parada para sempre). Teste que responde
  a caixa a tempo não é afetado.
- As funções prontas do Qt que abrem caixa por dentro do C++
  (`QMessageBox.question/warning/...`, `QInputDialog.getText/getInt/...`,
  `QFileDialog.getOpenFileName/...`) levantam erro **na hora** se um teste as
  chamar sem trocá-las por uma resposta. A caixa de arquivo do Windows
  apareceria na tela mesmo com o offscreen.
- `teste_botoes.py`: offscreen por padrão (`--com-tela` para ver) e pasta de
  dados própria (`saida_teste\botoes\dados`), para não criar projetos na
  pasta real.

**Fontes:** nenhum teste precisa de fontes de verdade: a bateria inteira passa
com o offscreen (inclusive o teste da quebra de linha do caminho da cópia,
que mede o texto).

**Conferido (como):** um vigia de janelas (script à parte, com a API do
Windows: `EnumWindows` + `IsWindowVisible` + o processo dono de cada janela)
olhou a cada 0,1 s todas as janelas visíveis do processo do pytest e dos
filhos. Primeiro provei que o vigia enxerga: uma janela de 50×50 pontos posta
**fora** da tela (x = −20000), por 1,5 s, sem pegar o foco, foi vista. Depois:
- bateria inteira, rodada **sem** `QT_QPA_PLATFORM` no ambiente (para provar
  que o conftest põe sozinho): 1215 passaram, 1 pulado; **0 janelas visíveis**
  em 2648 olhadas;
- `teste_botoes.py` sem `QT_QPA_PLATFORM` nem `LOCALAPPDATA` trocados: 129
  ações, 0 falhas; **0 janelas visíveis** em 618 olhadas; a pasta de dados real
  ficou igual (lista de arquivos, tamanhos e datas, antes e depois).

**Testes:** `tests/test_sem_janela_na_tela.py` (novo, 8): o Qt dos testes é o
offscreen; as funções prontas de caixa sem resposta falham na hora (5
casos); a caixa modal sem resposta é fechada pelo vigia e marcada; a caixa
respondida a tempo não é afetada.

---

## Tentativa 51 — opção mudada em "O que fazer" sem "Conferir" não vai para o disco (30/09/2026)

**Data:** 30/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** achado pelo implementador em 30/09 (relatório da Tentativa 45);
decisão da gerente: consertar agora (plano no commit `4a30026`).

**O que acontecia:** num livro com trabalho, sair da conferência para "O que
fazer", mudar uma opção (ex.: desmarcar "Dividir folhas ao meio") e **fechar**
o programa, ou **voltar** para o início, sem clicar "Conferir": a opção nova
era gravada com as páginas de antes (pelo fechamento ou pelo relógio de
salvar), e a abertura seguinte recomeçava a conferência (com cópia e aviso).

**O que mudou (`ui/janela_principal.py`):** `_salvar_agora` grava
`_o_que_gravar()`: enquanto houver opções do trabalho guardadas (desde
`_sair_da_conferencia` até o "Conferir" terminar, em `_analise_pronta`), vai
para o disco uma cópia rasa do projeto com **as opções do trabalho** e as
páginas de sempre. O trabalho das páginas continua sendo gravado; só as
opções não conferidas ficam fora. A opção nova passa a valer quando o
"Conferir" termina (ou volta à de antes no "cancelar", Tentativa 45).

**Conferido, os outros caminhos:**
- livro **recém-aberto** com trabalho salvo, opção mudada e "voltar" ou
  fechar: já não gravava (a trava da Tentativa 36); o teste confirma, byte a
  byte;
- **"voltar"** (tela "O que fazer" → início) não grava nada por si; o
  relógio de salvar, se disparar depois, grava as opções do trabalho;
- **livro novo** (sem trabalho): as opções continuam indo para o disco, como
  antes (o "continuar" as traz de volta; não há páginas com que brigar).

**Testes:** `tests/test_trabalho_nao_se_perde.py`, mais 6 (4 falhavam antes):
opção mudada e fechar, voltar e fechar, voltar e o relógio disparar (o disco
fica com as opções do trabalho, e a abertura seguinte não recomeça); livro
recém-aberto com trabalho, opção mudada e voltar não grava nada; o trabalho
feito antes de sair para "O que fazer" continua gravado; livro novo guarda a
opção como antes.

---

## Tentativa 52 — a regra nova do Preto e branco: a gravura vira desenho (30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina + teste de olho do Samuel)
**Pedido (Samuel, 30/09):** "No Preto e branco, tudo sai em preto e branco,
inclusive moldura dourada, título colorido e iluminura. A moldura não deve sair
dourada (como no detector antigo) nem preta chapada (como no novo): deve sair
como desenho em preto e branco, com os traços e detalhes em preto e o fundo da
faixa em branco, sem perder o desenho. O título 'NOVEMBRE.' da Horas 26 sai
preto no Preto e branco. Nos outros filtros (Mágico pro, Melhorar, Original),
sai com a cor original."

**O que mudou (`core/filtros.py`, `_preto_e_branco_com_gravura`):** no Preto e
branco, cada zona de gravura da marcação vira **desenho de 1 bit**: preto é o
ponto bem mais escuro que o fundo em volta dele (o fundo é o fechamento
morfológico, a mesma operação consagrada de `_peso_de_traco`; elemento de 1/120
do menor lado da página; limiar 0,80 do fundo). A faixa pintada, mais larga que
o elemento, é fundo dela mesma e sai branca; o contorno, o detalhe e a letra
saem pretos. Mancha escura pequena e sem cor (nota quadrada, letra grossa de
tinta preta) volta cheia. Sem foto na página, ela sai inteira em 1 bit e o
Melhorar não roda mais no Preto e branco. **Foto e pintura de tom contínuo
ficam como estavam** (pouco traço, `GRAVURA_DE_TRACO_MINIMA`, e zona "grossa",
`FOTO_ESPESSURA_MINIMA` = 12% do menor lado), até o Samuel decidir. Melhorar,
Mágico pro e Original: sem mudança.

**Tentado e descartado (protótipos em `saida_teste/pb_30_09/proto/`):**

1. *Sauvola da página dentro da gravura* (o que o detector antigo fazia): a
   faixa dourada mais estreita que a janela sai preta; a iluminura da Horas 11
   vira borrão preto. É o defeito que a regra proíbe.
2. *Normalizar pelo fundo e passar Sauvola por cima*: faixa da Horas 13 cheia de
   ruído, hachura do Palatino 5 partida. Trocado pelo limiar fixo sobre o fundo.
3. *Elemento de 1/200 da página*: o título "NOVEMBRE." sai oco (só contorno).
   1/90 a 1/120 enchem a letra; 1/120 ainda cabe nas faixas das molduras.
4. *Contraste 0,15 / 0,22 / 0,30*: 0,15 enche a faixa da Horas 13 de pontinhos;
   0,30 apaga a hachura do retrato do Palatino 5 e o contorno da Horas 27. 0,20.
5. *Canal verde, ou os três canais*, no lugar do brilho: o verde não mudou nada
   à vista; os três canais enchem a faixa dourada de ruído. Fica o brilho.
6. *Encher toda mancha escura pequena* (para a nota do Graduale não sair oca):
   pedaços da moldura dourada da Horas 13 viram blocos pretos, e a hachura
   fechada do Palatino 5 vira manchas. Encher só a mancha **sem cor** (tinta):
   as notas voltam cheias e o dourado não. Encher pela "lisura" do miolo: a
   nota do Graduale tem textura e não enche. Descartado.
7. *Somar o Sauvola da página onde não há cor* (para a tinta preta larga): a
   iluminura da Horas 11 e as cenas da Horas 47 ganham grandes manchas pretas.
   Descartado.
8. *Pedaço fino de moldura contado como foto*: a medida de traço sozinha dá 0%
   nos pedaços da moldura das Horas 13 e 27 (o recorte só tem faixa) e eles
   ficariam em cor. Por isso a foto precisa também ser "grossa".

**Resultado da rodada** (`relatorios/conferir/pb-regra-30-09/antes/1.2-2026-09-30-1004`
e `.../depois/1.2-2026-09-30-1031`, Preto e branco, 15 páginas, com a coluna
"rodada anterior"): mudam só as 6 páginas com gravura que não é foto (Horas 11,
13, 26, 27, Palatino 5, Graduale 222), e todas saem só com preto e branco; as
outras 9 (inclusive Opus 20 e Escola 35, fotos) ficam idênticas ponto a ponto.

**Tempo** (só o filtro, nas mesmas entradas, antes e depois alternados, máquina
dividida com outro agente): Horas 11 23,8 → 12,0 s; Horas 13 17,9 → 4,0 s;
Horas 26 13,4 → 3,0 s; Horas 27 12,8 → 2,5 s; Graduale 222 13,3 → 3,5 s;
Palatino 5 1,6 → 0,4 s; páginas de texto iguais; Marial, 10 páginas do teste de
velocidade, 25,2 → 24,5 s. **Página com foto: Opus 20 5,4 → 5,7 s (+0,3 s, a
conta de "foto ou não")**; Escola 35 5,8 → 5,0 s (dentro do ruído).

**O que continua:** o que a gravura não pega continua no Preto e branco da
página (o lado direito e o pé da moldura da Horas 13 seguem pretos: o detector
não os marca); o título vermelho fora da gravura some no Preto e branco da
página ("TABLE" e "CONTENU EN CE LIVRE." da Horas 13), pela conversão para
cinza pelo maior canal (`_cinza_para_binarizar`, a escolha feita para a pauta
vermelha do Graduale). Fotos: exemplos para o Samuel escolher em
`relatorios/conferir/fotos-no-preto-e-branco-2026-09-30/`.

**Testes:** `tests/test_preto_e_branco_regra_30_09.py` (8, novos). Mudados
para a regra nova: `test_a_gravura_fica_com_o_papel_branco_sem_perder_o_traco`
(`tests/test_filtro_com_selecao.py`, agora no Melhorar) e
`test_gravura_pequena_nao_roda_o_melhorar_na_folha_inteira`
(`tests/test_melhorar_em_volta_da_gravura.py`, agora no Mágico pro).

---

## Tentativa 53 — item 1.2: as opções do ScanTailor na tela, por livro e por página; pauta do Graduale e moldura da Horas 13 (30/09/2026)

**Data:** 30/09/2026
**Situação:** a conferir (teste de máquina + teste de olho do Samuel)
**Pedidos:** Samuel, 30/09: "o programa tem que ter essas opções para o
usuário conseguir usar"; "Todo livro começa no contorno 'livre', com a
caixinha 'Este livro tem fotos' para trocar para 'retangular'. Quero poder
trocar também só numa página (ex.: só a página da estátua do Opus Majus), sem
mudar o livro inteiro."; consertar agora a pauta do Graduale 222 e a moldura
da Horas 13; o título da Horas 26 vai para o 1.5.

**O que mudou (commits a5ec20b, ee1f6d6, fc25d72, 2c6cb15, 47cabac):**
- `Projeto.gravura_forma` / `gravura_sensibilidade` / `gravura_mais_sensivel`
  / `gravura_normalizar` (padrões do ScanTailor) e `ConfigPagina.gravura_forma`
  (só a página) + `gravura_feita_com` (assinatura das opções que fizeram a
  parte automática). Não há campo "detector": o "não procurar" (forma
  "desligada") é o desligar da regra 8; o detector antigo só entra sozinho,
  quando a DLL falha.
- Tela "O que fazer": grupo "Gravuras e fotos" (frases ao lado de cada
  caixinha: com elas embaixo, a tela não cabia em 880 pontos de altura e as
  caixinhas eram espremidas — visto na foto da tela).
- Mudar as opções num livro com trabalho: só ao clicar "Conferir"; cópia do
  trabalho antes; a parte que a máquina marcou é refeita quando a página é
  desenhada; a marcação à mão (e o filtro por pedaço) volta por cima, na ordem;
  aviso na tela.
- Aba Marcar: "detectar automaticamente" passa pelo mesmo caminho da prévia e
  do PDF (antes chamava o detector antigo na prévia já filtrada);
  "Esta página tem foto" com "usar em todas", "só nas próximas" e desfazer.
- Falha da DLL: erros.log (uma vez por motivo) e uma frase na tela (uma vez).

**Tentado no detector (Graduale 222 e Horas 13):**
1. *"Tira de escrita" pela medida de pedaços de letra em cada peça da
   gravura* — **descartado**: a medida não separa (moldura da Horas 26 dá 1,0,
   retrato do Palatino 5 dá 0,7), e a pauta do Graduale era uma peça só com a
   faixa escura da beirada.
2. *Caixa "figure" do modelo julgada escrita tira a gravura* — **ficou**: no
   Graduale 222 o modelo desenha uma caixa "figure" em volta da partitura que
   o detector antigo julga escrita (46% de pedaços de letra); ali a escrita
   ganha, e a peça que é mais da metade de dentro da caixa sai inteira.
   Barras finas encostadas na beirada (até 10% do outro lado) saem mesmo
   presas a outra peça. Graduale 222: 14% → 0% (em todas as combinações).
3. *A gravura cresce pelo que não é papel* (até 2% do menor lado) —
   **ficou**: a Horas 13 tinha só a beirada de dentro da moldura (37% do
   dourado coberto); agora 88%. Feito na linha a parte do ScanTailor.
   As outras páginas mudam no máximo a beirada.

**Rodada das opções** (`relatorios/conferir/fase1-1.2-opcoes-2026-09-30/`, 9
páginas × 10 combinações × 2 filtros): a de fábrica (contorno livre, sem
imagens claras, luz igualada) é a melhor ou empata em 8 de 9; o Opus 20 fica
bom com "tem foto" (retângulo); "imagens claras" resolve o Opus 20 mas põe
gravura no texto (Marial 153, Palatino 9 e 67) — **não recomendada de
fábrica**. O título da Horas 26 nenhuma opção resolve (1.5, depende do OCR).
Visto de passagem: no Preto e branco (regra nova do filtro, outro
implementador) o título vermelho da Horas 13 some em todas as combinações.

---

## Tentativa 54 — a tela do 1.2 legível em qualquer janela; o desfazer na tela "O que fazer"; o aviso certo (30/09/2026)

**Data:** 30/09/2026
**Situação:** a conferir (teste de máquina + prints da janela real)
**Pedido:** parecer do verificador da rodada geral (30/09, r01, r02, r04, r06,
r09, r15).

**O que estava errado, e por quê:** a foto "sem janela" (plataforma
offscreen) de 29/09 dizia que o grupo cabia em 1440 × 880. Não servia de
prova: este PC tem escala de 125% no Windows, e a janela de 1440 × 880 do
verificador tem uns 1150 × 680 pontos; a foto não tinha barra de título nem
menu. Na janela real, o Qt espremia as linhas até 2 pontos. **Lição:** conferir
tela na janela real (fora da tela), com a escala do Windows (`QT_SCALE_FACTOR`
para simular 100% e 150% num monitor a 125%).

**O que mudou (commits f9ab43a, 6400b5d, 749d70f, a20257c):**
- o cartão da tela "O que fazer" vai numa área com rolagem (a altura dela para
  no cartão quando cabe, para o resumo ficar logo embaixo);
- no grupo, frase embaixo de cada caixinha, quebrando a linha; "Mais opções"
  guarda sensibilidade, imagens claras e igualar a luz (abre sozinho se alguma
  não está no padrão); as frases dos filtros também quebram;
- caixinha com quadrado (`ui/estilo.estilo_da_caixinha_com_quadrado`): na
  janela real, a desmarcada saía sem quadrado nenhum. Só no grupo e na aba
  Marcar; as outras caixinhas do programa têm o mesmo defeito (a decidir);
- a tela "O que fazer" se reacerta pelo projeto ao aparecer e depois de
  desfazer/refazer (r15);
- `pipeline.aviso_das_opcoes_da_gravura`: título "Gravuras e fotos" e frase
  certa no "não procurar" (r09) — falta ligar em `ui/janela_principal.py`;
- aba Marcar: linhas "Marcação:" e "Foto:", dicas nos botões (r06).

---

## Tentativa 55 — a janela não congela mais: as páginas do PDF são desenhadas num processo à parte (30/09/2026)

**Data:** 30/09/2026
**Situação:** consertado, a conferir (teste de máquina)
**Bug:** Lista de bugs, 30/09 (parecer do verificador, rodada geral,
`reproducoes/sonda4_congela.py`): a janela ficava ~16 s sem responder ao
terminar a análise de um livro de 40 folhas / 80 páginas. Regra técnica do
`CLAUDE.md`: "Interface nunca congela".

**Causa (medida, diferente da suposta):** o desenho das páginas já estava em
segundo plano (QThread e QThreadPool). O problema é que o **PyMuPDF não solta
o GIL do Python enquanto desenha**: numa thread de fundo, desenhar uma página
do livro de teste (imagem JPEG 2000 de 3325 × 2568, como os do Internet
Archive) segurou a thread principal parada 0,72 s. Com a análise, a tira de
miniaturas e as prévias desenhando ao mesmo tempo, a thread da janela (e até
uma thread de medição que só precisava do GIL) ficava sem vez por 2 a 9 s. O
perfil do verificador (cProfile) apontava `paineis._botao → get_pixmap`
porque, no Python 3.14, o cProfile mistura as threads: o `_botao` só estava na
pilha da janela enquanto outra thread desenhava. O próprio PyMuPDF manda usar
processos para trabalhar em paralelo (`pymupdf/_apply_pages.py`).

**O que mudou:**
- `core/paginas_em_outro_processo.py` (novo): dois "servidores de páginas"
  (processos auxiliares). `pdf_io.pagina_para_array` pede a página a um deles e
  espera pela resposta com o GIL solto; o servidor roda **a mesma função**
  (com a delegação desligada), então a imagem é **igual ponto por ponto**
  (conferido a 50, 150 e 300 DPI em três livros). A imagem volta por memória
  compartilhada (pelo cano custava 25 ms por página a 300 DPI).
- **Adiantamento:** quando se pede a página N, o outro servidor já desenha a
  N+1 (a análise e o PDF final pedem em ordem). É o que deixou a análise mais
  rápida que antes.
- **Arquivo nunca preso:** o servidor fecha o PDF depois de meio segundo sem
  pedido e na hora em que o livro é fechado ou trocado
  (`GerenciadorPrevias.parar`, `TiraMiniaturas.parar` chamam `soltar_livro`).
  A tira de miniaturas passou a abrir o PDF a cada folha (antes o deixava
  aberto o tempo todo da tira). Achado pelo outro implementador: numa
  primeira versão o servidor guardava o livro aberto e 5 testes quebraram
  (arquivo preso).
- **Robustez:** servidor que cai é trocado por outro e a página é pedida de
  novo; se não subir outro, a página é desenhada aqui, como antes (anotado no
  `erros.log`). Antes, uma queda do MuPDF derrubava o programa inteiro; agora
  derruba só o servidor. `EDITOR_PAGINAS_AQUI=1` desliga tudo.
- `main.py`: o programa empacotado atende `--servidor-de-paginas` antes de
  abrir qualquer janela (o servidor é o próprio `.exe`), e sobe os servidores
  quando a janela abre. Em desenvolvimento: `python -m
  core.paginas_em_outro_processo`. Sem janela de console (`CREATE_NO_WINDOW`).

**Medido (sonda sem janela, a mesma máquina, "antes" = `EDITOR_PAGINAS_AQUI=1`,
que é o comportamento de antes; relógio de 20 ms na thread da janela):**

| Livro | Maior tempo sem resposta | Análise até a conferência abrir | Primeira página, depois de a conferência abrir |
|---|---|---|---|
| 40 folhas / 80 páginas (JPEG 2000, a sonda do verificador) | 9,19 s → **0,07 s** | 28,3 s → **17,6 s** | 1,86 s → **0,51 s** |
| Marial, 300 páginas (`gabarito/velocidade/marial_300.pdf`) | 0,41 a 0,67 s → **0,44 a 0,46 s** | 47,0 e 52,2 s → **42,6 e 43,5 s** | 0,05 s → **0,02 s** |

No Marial, o que sobra (0,45 s, uma vez, quando a conferência abre) **não é
desenho de página**: é o próprio `_analise_pronta` na thread da janela (0,42 s
medidos, quase tudo dentro do `_salvar_agora`, enquanto as prévias começam a
ser processadas; gravar sozinho leva 10 a 30 ms). Fica como ressalva.

PDF final (`pipeline.processar`, melhor de 3, máquina dividida com outros
agentes, variação de ±30% entre rodadas iguais): Marial 10 páginas 14,6 s →
15,0 s; livro JPEG 2000 8 páginas 2,7 s → 2,0 s. Custo puro por página
(medido isolado): +2 ms a 150 DPI, +8 ms a 300 DPI.

**Testes:** `tests/test_paginas_em_outro_processo.py` (novo, 11): a página do
servidor é igual à desenhada aqui (50, 150 e 300 DPI) e se pode alterar;
**desenhar não prende as outras threads** (a thread principal fica no máximo
0,15 s parada; antes do conserto, 0,33 s nesse teste); erro de PDF chega como
`ErroPDF`; servidor que cai é trocado; desligado desenha aqui; documento sem
arquivo desenha aqui; o PDF fica livre depois de meio segundo e na hora com
`soltar_livro`; livro mudado no disco é relido. `tests/test_folhear_pdf.py`: o
teste que espia o esvaziamento do armazém do MuPDF passou a desenhar aqui (é
no servidor que ele acontece agora, com a mesma função).
`tests/test_mesmo_livro_outro_caminho.py`: o ajudante que "fecha o livro" para
também a tira, como o fechamento do programa.

---

## Tentativa 56 — o aviso das opções de gravura com o título e o texto de cada caso (item 1.2, 30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina)
**Pedido da gerente (30/09):** ligar à janela o aviso novo que o outro
implementador fez em `core.pipeline.aviso_das_opcoes_da_gravura` (parecer do
verificador, rodada geral, r09: mudar as opções de "Gravuras e fotos" num
livro conferido dizia "serão procuradas de novo" até no "não procurar", numa
caixa de título "Um momento").

**O que mudou:** `ui/janela_principal.py` (`_analise_pronta`) mostra
`self.avisar(frase, titulo)` com o `(titulo, frase)` de
`aviso_das_opcoes_da_gravura`; o texto antigo (`_frase_das_gravuras_refeitas`)
saiu. O `avisar` já aceitava o título.

**Teste:** `tests/test_trabalho_nao_se_perde.py`,
`test_aviso_das_opcoes_de_gravura_usa_o_titulo_e_o_texto_certos` (falhava
antes: o título era "Um momento"): livro conferido com uma gravura achada pelo
programa, "não procurar" e "Conferir" → caixa "Gravuras e fotos", texto "não
vai mais procurar", com o caminho da cópia.

---

## Tentativa 57 — a janela cabe no notebook do Kaique a 150% (30/09/2026)

**Data:** 30/09/2026
**Situação:** feito, a conferir (teste de máquina; o Samuel confere na tela)
**Pedido da gerente (30/09):** a janela principal não cabia no notebook do
Kaique a 150% de escala: altura mínima de 680 pontos, e a área útil é de ~657.

**O que mudou (`ui/janela_principal.py`):** mínimo 1000 × 600 pontos (antes
1000 × 680); o tamanho inicial (1220 × 800) passa a ser reduzido à área útil
da tela, tirando ~40 pontos para o título e a moldura
(`JanelaPrincipal.tamanho_que_cabe`); nunca abaixo do mínimo.

**Conferido (como):** com as fontes de verdade, a janela desenhada sem ir para
a tela (`WA_DontShowOnScreen`, e o vigia de janelas confirmou nenhuma janela
visível), `QT_SCALE_FACTOR=1.5`, a 1280 × 600: início, "O que fazer",
conferência (abas Onde cortar, Bordas, Endireitar e Filtro), progresso e
final cabem sem se sobrepor (olhei as imagens). O que os layouts exigem é no
máximo 463 pontos de altura (a do "O que fazer" com o menu). A lista de opções
do "O que fazer" e os painéis da direita da conferência já tinham rolagem e a
usam. Observação: o monitor do Samuel é 1920 × 1080 a 125%; com o fator 1,5
por cima, a tela lógica ficou 1024 × 576 (menor que a do Kaique), então a
conferência foi feita pelo tamanho da janela, não pela tela.

**Teste:** `tests/test_janela_cabe_na_tela.py` (novo, 2; os 2 falhavam antes):
a altura mínima (e a que os layouts exigem) cabe em 657; o tamanho inicial
não passa da área útil de 1280 × 688, e numa tela grande continua 1220 × 800.
