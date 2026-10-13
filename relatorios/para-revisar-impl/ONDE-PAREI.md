# O "Para revisar" da Fase 2: onde parei

Implementador, 12 e 13/10/2026. Ramo `fase2-para-revisar` (saiu do `fase-1` em `9c51801`), cópia em
`.claude/worktrees/para-revisar`. Bloco do plano: "Decidido pelo Samuel, a fazer: o 'Para revisar'"
(PLANO-DEFINITIVO, Fase 2). **Nada aqui está aprovado: é para o verificador conferir.**

## O que está feito

**PRONTO PARA CONFERIR** (os seis itens estão no programa e funcionam nos testes de máquina; falta o olho
do verificador na janela e duas decisões, escritas nas ressalvas 1 e 2).

Commits no ramo (todos no GitHub):

| Commit | O que é |
|---|---|
| `7695b46` | Item 1: a regra ajustada (e, nos mesmos arquivos de `core/`, as peças dos itens 2, 4 e 6 ainda sem tela) |
| `90d0708` | Item 6, parte sem tela: a lista dos avisos e o "está bom" por motivo; testes de "Deixar em branco" e da força sozinha |
| `fbe0b7f` | Itens 2 a 6 na tela: botões do aviso, lugar marcado, lista ao processar, "está bom" em cada nível, caixinha da força |
| `2e400c8` | Junção do `fase-1` (G6, `8968704`), pedida pela gerente; dois conflitos de linhas vizinhas |
| `8923370` | A regra só é medida na resolução do PDF; a tela mede por trás (achado da conferência nas 89 páginas) |

### O critério de aceite (89 páginas do estudo)

| Como conferi | Vão | Certas | Decidem diferente do estudo |
|---|---|---|---|
| Aviso de antes (do estudo) | 55 | 52 | |
| Regra ajustada, **a conta do programa sobre as máscaras do estudo** (`conferir_89.py`) | **21** | **78** | nenhuma; os números de cada sinal batem um a um |
| **O programa de verdade**, 300 DPI, página preparada como no dia do estudo (`--programa --preparo-do-estudo`) | **21** | **78** | nenhuma |
| O programa de verdade, 300 DPI, preparo do livro novo de hoje (G6 + conta do ScanTailor) | 20 | 73 | 7 (ressalva 1) |
| O programa de verdade, 110 DPI (a prévia), sem a força sozinha | 39 | 60 | 22 (por isso a prévia não mede mais) |

**Depois do reacerto dos limites (13/10, pedido da gerente; `reacerto-dos-limites.md`):** dois limites mudaram,
os mesmos para os dois preparos: o tamanho do pedaço grande, de 1,5 para **1,2**, e o mínimo da guarda da linha,
de 0,20 para **0,13**. A forma da regra não mudou.

| O programa de verdade, 300 DPI, limites reacertados | Vão | Certas | Decidem diferente do estudo |
|---|---|---|---|
| Preparo do projeto antigo (o do dia do estudo) | **21** | **78** | nenhuma |
| Preparo do livro novo (G6 + conta do ScanTailor) | **22** | **75** | 5: Antiphon 260, Cursus 3, Matemática 72, Opus Majus 20, Palatino 66 |
| A conta do programa sobre as máscaras do estudo | 21 | 78 | nenhuma |

A letra T do Antiphonal 46 e o Egenloff 3 voltaram a ir no livro novo. As 5 que sobram não se resolvem com
limite (o porquê de cada uma, com os números, está em `reacerto-dos-limites.md`); na Matemática 72 o programa
de hoje acerta o gabarito e a regra do estudo errava.

Os resultados página a página estão nos `conferir-89-*.json` desta pasta (os `...-limites-da-rodada-4.json`
são os de antes do reacerto; os `...-completo.json` têm os sinais inteiros que o reacerto leu).

### Tempo de medir uma página na resolução do PDF (para a pergunta da ressalva 2)

Medido nas 89 páginas, o programa de verdade a 300 DPI, uma página por vez, neste PC: desenhar a folha,
preparar, achar gravura e texto (primeira vez da página), filtrar e fazer a conta. Três rodadas de cada preparo:
média de 3,6 a 4,4 s por página, mediana de 2,5 a 3,0 s, 9 em cada 10 páginas em menos de 7 s, a pior de 20 a
31 s (Antiphon 88 e 260, folhas de 38 milhões de pontos). Só a conta da regra: 0,17 a 0,27 s por página em
média (a pior, 1,1 s). Num livro de 300 páginas todo em "Só as letras": de 13 a 15 minutos pela mediana, de 18
a 22 minutos pela média (as 89 páginas misturam livros de folha grande; um livro de folha comum fica perto da
mediana). É tempo de um fio só, com o PC livre; não medi com a tela em uso ao mesmo tempo.

### Testes de máquina

- Novos: `tests/test_revisar.py` (28), `tests/test_avisos.py` (25), `tests/test_para_revisar_na_tela.py` (20);
  refeitos: os do aviso em `tests/test_misto_no_programa.py` (31 no arquivo).
- A suíte inteira, um arquivo de pytest por vez: antes da junção do `fase-1`, 114 arquivos, 2036 passaram,
  nenhum falhou; depois da junção, 115 arquivos, 2080 passaram, nenhum falhou (`test_ordem_do_preparo.py`: 43).
  Depois da última mudança (a medida por trás, `8923370`), a suíte inteira de novo, um arquivo por vez
  (13/10, 01:48 a 02:04): 115 arquivos, 2082 passaram, nenhum falhou.
- `conferir_na_tela.py`: a tela de conferir de verdade (sem aparecer no monitor), com os fios de verdade, em três
  páginas reais: Antiphonal 46 (aviso, marca, "Trazer de volta"), Camões 27 (força sozinha, "Desfazer"),
  Egenloff 12 ("Página sem conteúdo", "Deixar em branco"). Tudo certo.
- Tempo da conta da regra: 268 ms por página em média nas 89 (30 ms por milhão de pontos; a mais lenta 1,09 s),
  só nas páginas em "Só as letras" (jeitos "Guardar a tinta forte" e "Guardar só o texto").
  **O `teste_velocidade.py` não foi rodado** (fica para o verificador).

## Consertos depois da conferência do verificador (13/10)

Relatório dele: `origin/verif-para-revisar-2026-10-13`, `relatorios/conferir/para-revisar-2026-10-13/`.
**Itens 1 a 6 fechados; 7 e 8 investigados (sem conserto, como pedido). Próximo passo: as decisões da gerente
listadas abaixo.**

| Item | O que era | O que foi feito | Commit |
|---|---|---|---|
| 1 | A medida mudava quando a prévia tinha sido desenhada antes (na janela: 24 vão, 73 certas; direto: 22 e 75) | A causa era a marcação de gravura, letra e papel, procurada no primeiro desenho da página (na janela, a prévia de 110 DPI) e guardada; o detector acha áreas diferentes das de 300 DPI. Agora a prévia procura a marcação na página do tamanho do PDF, e as linhas do leitor de texto saem dela também. Nas 89 páginas, direto e na ordem da janela: **22 vão, 75 certas, os mesmos avisos e os mesmos sinais, nenhuma diferença.** **Refeito à tarde, a pedido da gerente: a busca passou para trás (seção "Duas mudanças", A); o resultado nas 89 é o mesmo.** | `027e50d`, `cf04ce7` |
| 2 | Dois cliques no cartão do filtro davam a página por conferida | Escolher o filtro que já está não grava ação nem confere a página | `c19f054` |
| 3 | "Parece em branco" e "Página sem conteúdo" sem "está bom assim" | Terceiro botão, "está bom assim", nos dois | `47a9465`, `c19f054` |
| 4 | Teclado preso no botão do aviso | Os botões do aviso não pegam o foco do teclado (nem escondidos); o mouse funciona igual | `c19f054` |
| 5 | As contagens não batem | Só a frase da janela: conta páginas do livro e diz "N páginas (M avisos na lista)". O resto fica para a gerente (abaixo) | `47a9465` |
| 6 | "usar mais escuro" com a força já em 85 | O botão que não faria nada não aparece | `c19f054` |

Testes depois dos consertos: suíte inteira, um arquivo por vez (13/10, 11:52 a 12:08), 115 arquivos, 2094
passaram; os 2 que falharam eram de `tests/test_gravura_no_processamento.py` e cobravam que a prévia procurasse
a marcação a 110 DPI: ajustei para a resolução do PDF (o comportamento novo) e o arquivo passou (43).
`teste_botoes.py`: 180 ações, 0 falhas.

### Custo do item 1 (para a gerente decidir)

**Decidido pela gerente: não pode ficar. Resolvido na seção "Duas mudanças", A (a busca vai por trás). O texto
abaixo é o registro de como estava.**

A primeira prévia de cada página que ainda não tem marcação ficou mais lenta: em 8 páginas do gabarito, de
1,14 s para 1,92 s em média (+0,8 s; de +0,1 s no Boécio 7 a +2,0 s na Horas 11). Vale em qualquer filtro com
"Achar gravuras" ligado, não só no "Só as letras". Da segunda vez em diante a página não paga nada. **O
`teste_velocidade.py` não foi rodado de novo; o "trocar de página" dele deve subir.** Se for caro demais, dá
para restringir às páginas em "Só as letras" (uma linha em `core/pipeline.renderizar_pagina`), mas aí a página
vista primeiro em outro filtro e depois passada para "Só as letras" volta a medir diferente. Projeto que já tem
a marcação guardada (feita antes, na prévia) continua com ela: não é refeita.

### Item 5: de onde vem cada número (Camões) e o que falta decidir

- **Lista, 105 linhas**: uma linha por motivo pendente de cada folha e de cada página (59 "Qualidade baixa" e
  2 "Tamanho diferente" são avisos de FOLHA; 35 do endireitar e 5 da regra são de PÁGINA).
- **Frase, "100 páginas"**: contava folhas e páginas com aviso como coisas separadas (a folha 5 e a página 5
  eram duas). **Consertado**: agora conta páginas do livro e mostra os dois números com nome.
- **Painel, 40**: só os avisos de PÁGINA (35 + 5); os de folha nunca entraram no painel (já era assim).
- **Janela de salvar, "6 páginas que você não conferiu"**: outra coisa e outro livro (o pedaço de 6 páginas do
  Antiphonal): conta as páginas que não receberam "está certo", com ou sem aviso. Já era assim.

Para os três dizerem a mesma coisa (páginas com aviso pendente) é preciso mudar o que se mostra, então parei:
- (a) o painel passa a listar também os motivos de folha, e o número de cima vira "páginas com aviso";
- (b) a janela de salvar passa a contar "páginas com aviso pendente" em vez de "páginas sem 'está certo'" (hoje
  ela avisa de toda página não olhada, mesmo sem aviso; há teste cobrando isso, `tests/test_barra_de_menu.py`);
- (c) deixar o painel e a janela de salvar como estão.

### Item 6, a caixinha da força sozinha

Hoje fica no grupo dos filtros da tela "O que fazer", depois das escolhas do "Só as letras", e só aparece
rolando. Ficaria melhor colada na linha da caixinha "Só as letras" (ela só age com "Só as letras"), ou na aba
Filtro, ao lado do medidor "força do preto". Não mudei a tela.

### Investigação 7: a tela mostra o que o PDF não tem

No Antiphonal 46 (página pequena: 741 x 1079 pontos a 300 DPI; 272 x 396 na prévia), medido pelo programa:

| Resolução | "Escuro da letra" (o corte do "Guardar a tinta forte") | Tinta na caixa da letra T: preto e branco de base | no resultado |
|---|---|---|---|
| 300 DPI (o PDF) | 45 | 25,2% | 11,8% (mais da metade some) |
| 200 DPI | 56 | 25,8% | 25,5% |
| 150 DPI | 64 | 27,1% | 26,9% |
| 110 DPI (a prévia) | 76 | | 27,9% (a letra fica inteira) |

A causa: o "Guardar a tinta forte" decide pedaço por pedaço de tinta (fica o pedaço que tem algum ponto tão
escuro quanto as letras). Na imagem pequena os pedaços da letra se juntam num só, que tem pontos escuros, e o
corte fica mais frouxo (76 em vez de 45): a letra fica. Na imagem do PDF os pedaços se separam e os claros
somem. Nenhuma resolução menor repete o PDF nesta página (a 200 DPI a letra ainda fica).

O que custaria mostrar na tela o mesmo que o PDF, na página da vez:
- **Em "Só as letras" (onde a medida já roda):** quase nada a mais. O desenho do tamanho do PDF já é feito por
  trás para medir (nesta página, 5,2 s; nas 89, média de 3,6 a 4,4 s, pior 20 a 31 s) e a imagem é jogada fora.
  Basta guardá-la reduzida e trocar a prévia por ela quando chegar: o Kaique veria a prévia de hoje em 1 a 2 s
  e a imagem "como no PDF" de 4 a 11 s depois (20 a 26 s em folha grande, pelos tempos do verificador na
  janela). Memória: uma imagem reduzida por página guardada (1 a 3 MB). O "Ver de perto" precisaria da imagem
  inteira da página da vez (8 a 38 milhões de pontos, só uma por vez).
- **Nos outros filtros** não há medida: seria um desenho do tamanho do PDF a mais por página vista (os mesmos
  3,6 a 4,4 s em média, por trás).
- Não fiz: é mudança de tela e de como a prévia funciona.

### Investigação 8: a força sozinha no Palatino 66

O Palatino 66 não vem do reacerto do limite (0,20 para 0,13): as três linhas dele guardam 50%, 57% e 62% da
tinta, acima dos dois mínimos. Ele passou a ir por causa do preparo do livro novo (no do estudo, uma linha só).

Nas 89 páginas, livro novo, a força sozinha age em **7 páginas com o limite novo e em 6 com o antigo** (a
diferença é o Egenloff 3). Medido com a força 50 e com a 85:

| Página | Linhas falhadas a 50 | a 85 | Tinta fora do texto (% da página) a 50 | a 85 | Precisava? |
|---|---|---|---|---|---|
| Camões 27 | 5 de 28 | 0 | 1,54 | 2,22 | sim |
| Camões 11 | 3 de 22 | 0 | 2,79 | 3,64 | sim |
| Camões 104 | 1 de 1 | 0 | 4,22 | 5,48 | sim (e ganha o aviso "figura além da gravura") |
| ljs47 103 | 3 de 47 | 1 | 9,63 | 10,22 | sim |
| **Palatino 66** | 3 de 12 | 0 | 7,09 | 8,12 | **não** (caligrafia; o verificador viu a moldura suja) |
| Antiphonal 252 | 2 de 14 | 2 | 7,82 | 9,34 | sim, mas a força não resolve |
| Egenloff 3 | 2 de 15 | 5 | 12,49 | 12,60 | sim, mas a força piora a conta (texto vermelho) |

Sem precisar: **1 página (Palatino 66), com o limite novo e com o antigo.** E em 2 (1 com o limite antigo) a
força é escurecida sem resolver. Nenhum número destes separa o Palatino 66 do Camões 11 (os dois têm 3 linhas
falhadas e a força "conserta" os dois). Propostas, para a gerente escolher (não mudei nada):
- **P1: a força sozinha só age com 4 ou mais linhas falhadas, ou com todas** (o aviso continua com 2). Nas 89:
  age só no Camões 27 e no 104, nenhuma sem precisar; Camões 11, ljs47 103 e Palatino 66 ficam só com o aviso
  "Texto falhado" e o botão "usar mais escuro" (um clique).
- **P2: escurece, mede de novo e só mantém se as linhas falhadas caírem**; senão volta a força e deixa o aviso.
  Tira o Egenloff 3 e o Antiphonal 252; o Palatino 66 continua escurecido.
- **P3: as duas juntas** (a minha sugestão: é a mais cuidadosa; apoia-se em poucas páginas).
- P4: desligar a força sozinha de fábrica e deixar só o botão no aviso (muda o que o Samuel escolheu).

**Decidido pela gerente: P3. Feito (`0541236`); a tabela de antes e depois está na seção "Duas mudanças", B.**

## Duas mudanças pedidas pela gerente depois dos consertos (13/10, tarde)

**PRONTO PARA CONFERIR.** Commits `0541236` (B), `a841fd0`, `36a6549`, `bdc8142` e o que fecha (A).

### A. A marcação do tamanho do PDF é procurada por trás (o custo de 0,8 s saiu da frente)

O conserto do item 1 fazia a prévia procurar a marcação (gravura, letra e papel) na página do tamanho do PDF
antes de aparecer. Foi desfeito. Agora:

- A prévia procura na página pequena, como sempre, e aparece no tempo de antes. Essa marcação fica guardada
  como **provisória** (campo novo na página do `projeto.json`: `marcacao_provisoria`).
- Depois que a prévia aparece, a tela pede por trás (`GerenciadorPrevias.pedir_medida`, fio do pool) a procura
  na página do tamanho do PDF (`core.pipeline.acertar_no_tamanho_do_pdf`). Quando chega: a marcação guardada
  passa a ser essa (o que a máquina marcou é trocado; o que a pessoa marcou à mão volta por cima), a prévia é
  desenhada de novo e, nas páginas em "Só as letras", a regra é medida.
- **A regra só mede com a marcação do tamanho do PDF, nunca com a da prévia.** Página que ninguém visitou (ou
  cuja busca não chegou a rodar) é trocada ao gerar o PDF.
- Projeto antigo, com marcação e sem o campo: a marcação dele vale como está, nada é procurado de novo.

**Critério 1, o tempo até a primeira prévia** (as mesmas 8 páginas, filtro de fábrica, página sem marcação;
`tempo_da_primeira_previa.py`, as três versões do código medidas hoje uma atrás da outra, várias rodadas):

| | Média das 8 (rodadas de hoje) | Medido antes |
|---|---|---|
| Antes de tudo (`b5b224f`) | 1,18 a 1,31 s (seis rodadas; a do meio 1,20) | 1,14 s |
| Com o conserto de hoje cedo (`cf04ce7`, busca na frente) | 2,08 e 2,57 s | 1,92 s |
| **Com a busca por trás (agora)** | **1,09 a 1,31 s (seis rodadas; a do meio 1,19)** | |

Por página, o menor tempo de cada uma (segundos): antes de tudo / conserto de hoje / agora. Marial 7:
1,25 / 2,05 / 1,26. Palatino 7: 1,26 / 2,15 / 1,16. Boécio 7: 0,79 / 0,86 / 0,75. Horas 11: 1,34 / 3,12 / 1,27.
Graduale 221: 1,49 / 3,06 / 1,33. Escola 7: 1,04 / 1,76 / 0,95. Opus Majus 20: 1,33 / 2,71 / 1,21. Camões 27:
0,72 / 0,91 / 0,69. As rodadas variam uns 0,1 s entre si (há outros agentes usando o PC); a diferença entre
"antes de tudo" e "agora" fica dentro disso.

**Achado ao medir na tela de verdade** (`tempo_de_trocar_de_pagina.py`: a tela de conferir sem aparecer, fios de
verdade, passando por 12 páginas): o tempo de uma prévia sozinha não mostrava tudo. Com a busca começando logo
depois da prévia, ela disputava os fios e o processador com as prévias adiantadas das páginas seguintes, e num
pedaço do Antiphonal 1547 trocar de página ficava 0,3 s mais lento. Por isso a busca por trás agora espera
numa fila e **só começa com o pool de prévias parado**, uma de cada vez, a mais nova primeiro. Medido depois:

| Livro (pedaço), como folheia | Antes de tudo | Busca por trás começando logo | **Busca por trás, só com o pool parado (agora)** |
|---|---|---|---|
| Antiphonal 1547, parando 1,5 s em cada página | 0,08 a 0,11 s | 0,40 a 0,43 s | **0,09 s** |
| Antiphonal 1547, sem parar | 1,33 a 1,54 s | 1,69 a 1,77 s | **1,53 a 1,54 s** |
| Boécio, parando 1,5 s | 0,01 s | 0,02 s | **0,01 s** |
| Boécio, sem parar | 0,50 a 0,63 s | 0,60 a 0,63 s | **0,51 s** |

O preço: o trabalho de trás leva mais tempo para acabar. Depois da última das 12 páginas, o programa ainda
trabalha por trás uns 22 s no Antiphonal (antes: 3 a 5 s) e 11 s no Boécio folheado sem parar (0,2 s parando
1,5 s por página). Quem folheia sem parar só tem as páginas acertadas quando parar; o PDF acerta todas.

**Critério 2, as 89 páginas** (300 DPI, livro novo): direto, **22 vão e 75 certas**; na ordem da janela (prévia
de 110 DPI, depois a busca por trás, pela mesma função que a tela chama), **22 e 75**. Página a página, os
mesmos avisos, os mesmos sinais, a mesma faixa e as mesmas marcas nas 89 (e os mesmos do conserto de hoje cedo).
Arquivos: `conferir-89-programa-dpi300.json` e `...-ordem-da-janela.json` (os de hoje cedo ficaram com
`-marcacao-na-frente` no nome).

**Critério 3, trocar de página antes de a marcação chegar** (`tests/test_marcacao_por_tras.py`, QThreadPool de
verdade, detector falso e lento cuja resposta depende do tamanho da imagem e de qual página ela mostra):
- passar pelas 4 páginas sem esperar a busca de nenhuma: não trava; cada página termina com a marcação DELA, a
  do tamanho do PDF; cada uma procurada uma vez na pequena e uma na grande; as buscas grandes nunca rodam duas
  ao mesmo tempo; a busca não é pedida de novo;
- a prévia de antes fica no cache até a nova chegar (a tela não pisca nem volta para "preparando...");
- prévia pedida com a busca no meio (a pessoa mexeu na página) não fica guardada com a marcação de antes;
- na tela de verdade, aba Marcar: marcar uma área à mão com a busca no meio, ir e voltar: a área da pessoa
  continua, por cima, e o editor mostra o que a página tem.
E em `tests/test_misto_no_programa.py` (sem fios): a troca em si; a área marcada à mão bem no meio da procura
grande; a folha que a pessoa deixou só com marcação à mão ("Esta folha vai sair em branco") não é procurada de
novo; a cópia velha do editor não é gravada como se fosse a do tamanho do PDF; projeto antigo fica como está;
os cartões de filtro (cópia da página) não mexem na marcação; se a procura grande falha, a página continua
provisória e a regra não mede.

**Critério 4, nada congela**: a procura e o desenho novo rodam no pool; no fio da tela só entra trocar a imagem
e reler a marcação.

**O que o Kaique vê de diferente** (além de a prévia se atualizar sozinha): na aba Marcar, as áreas que o
programa achou se acertam sozinhas uma vez, alguns segundos depois de ele chegar numa página nunca acertada
(no Graduale 221 são 9 áreas na prévia e 18 no tamanho do PDF). É a mesma troca, vista no editor. O "desfazer"
da aba Marcar perde o que tinha anotado nesse momento (pelo código, já perdia quando uma prévia chega; não
conferi na janela). Se a gerente não
quiser isso, a saída é o editor só se acertar ao sair e voltar à página.

### B. A força do preto sozinha (a "P3")

A força só é escurecida sozinha com **4 ou mais linhas falhadas, ou com todas as linhas contadas falhadas**; o
aviso "Texto falhado" continua valendo com 2. Depois de escurecer, a página é medida de novo e o reforço **só
fica se as linhas falhadas caírem**; senão a força volta à de antes, o programa não tenta de novo nessa página,
e ela fica só com o aviso e o botão "usar mais escuro".

As 7 páginas em que a força agia (89 páginas, livro novo, 300 DPI), antes e depois:

| Página | Linhas falhadas (força 50) | Antes da P3 | Depois da P3 |
|---|---|---|---|
| Camões 27 | 5 de 28 | força 85 (0 falhadas) | **força 85** (0 falhadas), aviso "Força do preto escurecida" |
| Camões 104 | 1 de 1 (todas) | força 85 (0 falhadas) | **força 85** (0 falhadas), aviso "Força do preto escurecida" (e "figura além da gravura") |
| Camões 11 | 3 de 22 | força 85 (0 falhadas) | força 50, só o aviso "Texto falhado" |
| ljs47 103 | 3 de 47 | força 85 (1 falhada) | força 50, só o aviso |
| Palatino 66 | 3 de 12 | força 85 (0 falhadas; moldura suja) | **força 50, só o aviso** |
| Antiphonal 252 | 2 de 14 | força 85 (2 falhadas) | força 50, só o aviso |
| Egenloff 3 | 2 de 15 | força 85 (5 falhadas) | força 50, só o aviso |

Nas 89 páginas com a força sozinha ligada (`conferir-89-programa-dpi300-forca-sozinha.json`): ela age só no
Camões 27 e no 104; nenhuma outra página muda de força. Nenhuma foi escurecida e desfeita (a segunda metade da
regra, "só fica se resolver", não chegou a ser usada nestas 89: com 4 linhas ou todas, só entram as duas do
Camões; ela está coberta por teste de máquina, `tests/test_avisos.py`).

### Testes depois de A e B

- A suíte inteira, um arquivo de pytest por vez (13/10, 13:40 a 13:56): **116 arquivos, 2114 passaram, nenhum
  falhou.** Arquivo novo: `tests/test_marcacao_por_tras.py` (4, com os fios de verdade; rodado 4 vezes com o código final,
  sem falhar). Mexidos: `test_misto_no_programa.py` (41), `test_avisos.py` (34), `test_para_revisar_na_tela.py`
  (25), `test_gravura_no_processamento.py` (43; a prévia volta a procurar a 110 DPI).
- `teste_botoes.py`: 180 ações, 0 falhas.
- `conferir_na_tela.py` (a tela de verdade, fios de verdade, Antiphonal 46, Camões 27, Egenloff 12): tudo certo.
- **O `teste_velocidade.py` não foi rodado** (fica para o verificador). O "trocar de página" dele deve dar o
  mesmo de antes; se não der, é para me devolver.

### Ressalvas de A e B

1. **Na aba Marcar a marcação se acerta sozinha uma vez por página** (descrito acima). É consequência direta de
   "a marcação guardada passa a ser a do tamanho do PDF"; não vi como evitar sem o editor mostrar uma marcação
   que não é a que vai para o PDF. A gerente decide se fica.
2. **O trabalho de trás agora existe em toda página visitada**, em qualquer filtro com "Achar gravuras" ligado
   (antes só nas páginas em "Só as letras"): um desenho do tamanho do PDF e uma prévia redesenhada por página,
   sempre depois das prévias. Num PC mais fraco que este pode aparecer de outro jeito: só o `teste_velocidade`
   no PC do Kaique diz.
3. **Quem folheia sem parar** não tem a busca feita na hora (ela espera o pool parar): os avisos da regra e a
   marcação definitiva dessas páginas chegam quando ele parar, da página mais nova para a mais velha, ou ao
   gerar o PDF. Antes (desde `8923370`) as medidas das páginas em "Só as letras" entravam na fila junto com as
   prévias. Não muda quais páginas vão para a lista, só quando.
4. **Página em "Só as letras" já vista na prévia**: o leitor de texto roda duas vezes nela (na prévia, como
   sempre, e por trás na página do tamanho do PDF). O da frente é o de sempre; o segundo é por trás.
5. **Um caso que não fechei**: o "Desfazer" (Ctrl+Z) de "Ajustar o pedaço à figura" devolve a marcação inteira
   de antes do clique. Se a busca por trás trocou a marcação entre o clique e o desfazer, voltam as áreas da
   prévia e a página fica dizendo que são as do tamanho do PDF. É raro (segundos de janela) e o efeito é o de
   antes de hoje (a página sai com as áreas da prévia). Para a Lista de bugs, 13/10/2026.
6. **A segunda metade da P3 ("só fica se resolver") não foi exercida nas 89 páginas**: com 4 linhas ou todas,
   só entram as duas do Camões, onde resolve. Está coberta só por teste de máquina.
7. As cópias de código antigas usadas para medir o tempo ficaram em `saida_teste\codigo-antes-de-tudo` e
   `saida_teste\codigo-conserto-de-hoje` (pasta fora do git); as duas junções `modelos` que criei dentro delas
   já foram desfeitas com `(Get-Item ...).Delete()`.

## O que cada pedido virou no programa

| # | Pedido do Samuel | O que o programa faz agora | Onde |
|---|---|---|---|
| 1 | Regra ajustada (`rv4-resumo`: "Fica assim") | No "Só as letras", a página vai para a lista por: desenho apagado, texto falhado, página sem conteúdo, figura além da gravura achada, faixa escura na beirada. O aviso "Tinta forte fora do texto" não existe mais (sai sozinho do projeto antigo). No "Guardar só o texto" vale a conta de antes (tinta forte apagada acima de 10%), com nome novo. A faixa em 70% ou mais das páginas medidas vira um aviso só, do livro. | `core/revisar.py`, `core/pipeline.py` (`_acertar_avisos_do_misto`, `acertar_faixa_do_livro`), `core/analise.py` |
| 2 | Um aviso para cada coisa, dois botões (`rv5-em-branco`) | "Parece em branco" e "Página sem conteúdo" são dois avisos; cada um com "Deixar em branco" (folha branca no lugar, a página fica no livro) e "Tirar do livro" (o apagar de sempre). | `core/analise.py` (`Alerta.botoes`), `modelos.ConfigPagina.em_branco`, `core/pipeline._filtrar`, `ui/tela_conferir.py` |
| 3 | Conserto rápido como botão do aviso (`rv4-conserto-desenho`, `rv5-erro-1-desenho`, `rv5-erro-6-so-texto`) | "Trazer de volta nesta página": no desenho apagado troca a página para "Guardar tudo"; no "Guardar só o texto" troca para "Guardar a tinta forte". O lugar onde sumiu aparece em retângulo laranja tracejado nos cartões de filtro e na aba Marcar. | `core/revisar.caixas_de`, `core/pipeline.marcas_do_aviso`, `ui/widgets/cartao_filtro.py`, `ui/widgets/editor_selecao.py` |
| 4 | Força do preto sozinha (`rv4-erro-4-texto-falhado`) | Texto falhado: o programa põe a força do preto em 85 só nessa página, filtra de novo e mostra o aviso "Força do preto escurecida", com "Desfazer". Caixinha para ligar e desligar na tela "O que fazer" (regra 8 do plano). Livro novo: ligado; projeto antigo: desligado. | `core/pipeline` (`_reforcar_se_o_texto_falhou`, `acertar_aviso_do_reforco`), `modelos`, `ui/tela_opcoes.py` |
| 5 | "Antes de processar" lista as páginas e os motivos (`rv5-aviso-so-texto`) | A janela mostra uma linha por motivo de cada página, com "ver" e "continuar assim mesmo". | `ui/janela_dos_avisos.py`, `ui/tela_conferir._pedir_processamento` |
| 6 | "Está bom" em cada nível (`rv4-aviso-so-texto`) | Página inteira: "está certo" da aba (como antes). Um motivo de uma página: "está bom assim" do aviso. Um motivo em todas: "está bom: todas" no painel. Tudo: "está bom em tudo" no painel. As que ele escolher: "ver a lista…" (a mesma janela, com caixinhas, "Selecionar todas" e "Nenhuma"). Tudo com Ctrl+Z. O aviso some sozinho quando o problema é resolvido (a conta é refeita a cada desenho). | `core/avisos.py`, `modelos` (`alertas_aceitos`), `ui/widgets/paineis.py`, `ui/tela_conferir.py` |

## O que o verificador precisa conferir na janela

Abrir um livro, tela "O que fazer": Preto e branco, "Só as letras" marcada (de fábrica "Guardar a tinta
forte"). Pasta de dados de teste, nunca a do Samuel.

| O que | Página | O que tem de aparecer |
|---|---|---|
| Letra grande que some | Antiphonal 1547, p. 46 (`D:\Livros para editar\Antiphonal 1547.pdf`) | Aviso "Desenho apagado"; retângulo laranja em volta da letra T nos cartões e na aba Marcar; botão "Trazer de volta nesta página" traz a letra (a página passa a "Guardar tudo") e o aviso some sozinho; Ctrl+Z desfaz. |
| "Guardar só o texto" apaga a música | Graduale p. 222 (gabarito), com "Guardar só o texto" | Aviso "Sumiu algo no 'Guardar só o texto'", pautas marcadas, "Trazer de volta nesta página" troca só essa página para "Guardar a tinta forte". |
| Texto falhado e força sozinha | Camões p. 27 e p. 104; Egenloff p. 3 (`D:\Livros para editar\...`) | A força do preto vai sozinha para 85 só nessas páginas (o medidor mostra), aviso "Força do preto escurecida" com "Desfazer". No Egenloff 3 o aviso "Texto falhado" fica junto (a força não resolve o vermelho). Com a caixinha desligada em "O que fazer": só o aviso "Texto falhado", com "usar mais escuro". |
| Página sem conteúdo | Egenloff p. 12, Rariora p. 8 | Aviso "Página sem conteúdo" com "Deixar em branco" e "Tirar do livro". "Deixar em branco": a prévia fica branca, a página continua na tira e no PDF (mesmo número de páginas). "Tirar do livro": some do PDF. |
| Parece em branco | qualquer folha branca de verdade | Aviso "Parece em branco" com os mesmos dois botões. |
| Não vão mais para a lista | Graduale 221 a 223, Palatino 9, 10, 57 (moldura e música guardadas) | Nenhum aviso (antes: "Tinta forte fora do texto"). |
| "Antes de processar" | qualquer livro com avisos, clicar "Confirmar e processar" | Lista "Página N - motivo"; "ver" leva à página e não processa; "continuar assim mesmo" processa; fechar no X não processa. |
| "Está bom" | livro com vários avisos | Os quatro níveis do item 6, cada um com Ctrl+Z; o contador e o painel acompanham. |
| Faixa do livro | Egenloff ou Matemática, vendo 4 ou mais páginas | A faixa sai das páginas e vira uma frase do livro (ver ressalva sobre onde a frase aparece). |
| Projeto antigo | um projeto salvo antes de 12/10 com "Tinta forte fora do texto" | Abre; o aviso antigo some; nenhuma força muda sozinha. |

## Ressalvas

1. **No preparo do livro novo, 5 das 89 páginas ainda decidem diferente do estudo (22 vão, 75 certas), mesmo
   depois do reacerto dos limites** (antes do reacerto eram 7: 20 vão, 73 certas). A regra foi acertada em
   páginas preparadas como no programa de 07/10; com o G6 e a conta do ScanTailor as máscaras mudam. O
   reacerto (dois limites, um conjunto só para os dois preparos) trouxe de volta a letra T do Antiphonal 46 e
   o Egenloff 3. As 5 que sobram: Antiphon 260 deixa de ir (devia ir); Cursus 3, Opus Majus 20 e Palatino 66
   passam a ir (não precisavam); Matemática 72 deixa de ir (e não precisava: aqui melhorou). Para chegar a
   21 e 78 no livro novo seria preciso mexer em mais do que limite. **O limite mais apertado é o mínimo da
   guarda (0,13): apoia-se numa linha do Egenloff 3.** Não olhei as imagens dessas páginas: é do verificador.
2. **A regra só é medida na resolução do PDF, não na prévia.** A 110 DPI ela erra (39 vão, 60 certas). A tela
   pede, por trás, um desenho na resolução do PDF só para medir a página da vez: custa um desenho desse
   tamanho por página visitada e por mudança de filtro, força ou corte nela (segundos, em fila atrás da
   prévia; nada congela). As páginas vizinhas não são medidas sozinhas (antes o aviso antigo aparecia também
   nas 3 páginas seguintes, que a prévia adianta); as não visitadas só são medidas ao gerar o PDF. Então a
   janela "Antes de processar" só lista o que já foi medido, e a força do preto sozinha pode agir numa página
   nunca vista só na hora do PDF (o aviso fica no livro para depois). Se o Samuel quiser todas medidas antes,
   é uma varredura do livro inteiro na resolução do PDF (pesada): não fiz.
3. **A regra só vale no "Só as letras" com "Guardar a tinta forte" ou "Guardar só o texto"** (é onde o programa
   sabe onde está o texto, e onde o estudo mediu). No "Guardar tudo" e no Preto e branco sem "Só as letras" não
   há aviso nenhum da regra: uma página sem conteúdo ou de texto falhado não é avisada ali. Por isso "Trazer de
   volta nesta página" (que troca para "Guardar tudo") tira todos os avisos da regra daquela página.
4. **"Trazer de volta" troca a página inteira de jeito**, como o Samuel escolheu (opção 1); o retângulo laranja
   só mostra onde sumiu, não é uma zona que se ajusta. Marcar "letra e traço" à mão em volta da letra NÃO a
   traz de volta hoje (o "Guardar a tinta forte" apaga do mesmo jeito): a rodada 5 dizia que trazia. Vai para
   a Lista de bugs (abaixo).
5. **Campos novos no `projeto.json`** (todos com padrão; projeto antigo abre igual): na página `em_branco`,
   `alertas_aceitos`, `forca_antes_do_reforco`, `reforco_desfeito`, `faixa_na_beirada`, `marcacao_provisoria`
   (13/10: a marcação da página veio da prévia e ainda vai ser trocada pela do tamanho do PDF); na folha
   `alertas_aceitos`; no livro `reforcar_texto_falhado` (livro novo ligado; projeto antigo desligado). É
   mudança de formato de dados: entendi que as decisões das rodadas 4 e 5 a autorizam, como nos itens
   anteriores (a gerente avisa o Samuel, 13/10). Projeto antigo, sem os campos, abre e sai igual ponto por
   ponto: `tests/test_avisos.py::test_projeto_antigo_sai_igual_ponto_por_ponto_mesmo_com_texto_falhado` (a
   página sai idêntica ao "Só as letras" de sempre mesmo com texto falhado: a força não muda sozinha) e
   `test_os_campos_novos_vao_e_voltam_do_projeto_salvo`; sem "Só as letras",
   `tests/test_misto_no_programa.py::test_sem_so_as_letras_e_o_preto_e_branco_de_sempre`.
6. **"Deixar em branco" só aparece nos dois avisos** ("Parece em branco" e "Página sem conteúdo"); os dois botões
   em qualquer página são da Lista de espera (Fase 6) e não foram feitos. A tecla Delete continua "apagar".
7. **O aviso "Parece em branco" continua com a conta de antes** (o erro da Gladstone 18, que tem título, está
   na Lista de bugs de 08/10 e não foi consertado aqui; a regra nova, "Página sem conteúdo", não a pega).
8. **Faixa do livro**: a frase "as páginas deste livro têm uma faixa escura na beirada: confira o corte" aparece
   no painel "Para revisar". As outras frases do livro (ex.: "o livro inteiro é colorido") continuam num
   rótulo que está escondido na tela de hoje (ver Lista de bugs).
9. **A força sozinha**: depois de reforçar, a página é medida de novo já com a força nova (um filtro a mais só
   nessas páginas). O reforço é 85, o valor testado na rodada 4. No Egenloff 3 (texto vermelho) ele não
   resolve e o aviso "Texto falhado" fica junto. Se a pessoa mexer no medidor depois do reforço, o "Desfazer"
   some e o programa não reforça de novo aquela página.
10. **Três commits em vez de seis**: escrevi os seis itens enquanto a medição de velocidade ocupava o PC (sem
    poder rodar nada), e os arquivos de `core/` ficaram com mais de um item. As mensagens dizem o que cada um traz.
11. **Não rodei o programa na janela de verdade** nem o `teste_botoes.py` (ele foi ensinado a fechar a janela
    nova, mas não foi rodado). A aparência é provisória, do jeito mais simples: é do agente de layout.
12. Um arquivo vazio meu ficou fora do projeto por engano: `C:\Users\fotog\AppData\Local\Temp\p2.py` (0 bytes,
    12/10 19:22). Não apaguei (regra de 29/09): a gerente decide.

## Bugs para a Lista de bugs (não consertados, não impedem)

| Data | Bug | Onde |
|---|---|---|
| 12/10/2026 | Marcar "letra e traço" à mão não protege a tinta do "Guardar a tinta forte" nem do "Guardar só o texto": a letra grande marcada some do mesmo jeito (a rodada 5 mostrou ao Samuel, em simulação, que voltava). | `core/misto.py` (`_fora_do_texto` só olha as linhas do leitor e a gravura) |
| 12/10/2026 | As observações do livro ("o livro inteiro é colorido", "este livro tem uma página por folha"...) são escritas num rótulo de um cabeçalho escondido: o Kaique não as vê. | `ui/tela_conferir.py` (`rotulo_observacoes`, `_montar_cabecalho`) |
| 12/10/2026 | (consertado, por impedir o botão novo) Os botões "usar mais fraco" / "usar mais escuro" dos avisos "Ficou escura" / "Texto quase sumiu" chamavam um método que não existia (`_escolher_forca`) e davam "Não consegui fazer isso agora". | `ui/tela_conferir.py` |
| 12/10/2026 | Com o preparo do livro novo, o Siebmacher 7 e 9 continua sem ser dividido sozinho (já anotado na rodada 4); nos scripts continua dividido à mão. | divisão do ScanTailor |
| 13/10/2026 | Desfazer (Ctrl+Z) de "Ajustar o pedaço à figura" depois de a busca por trás trocar a marcação da página: voltam as áreas achadas na prévia e a página fica marcada como se fossem as do tamanho do PDF (a regra do "Para revisar" mede com elas). Raro. | `ui/tela_conferir._ajustar_pedaco_a_figura` (grava `selecao` pelo histórico, sem o campo `marcacao_provisoria`) |

## Ideias para a Lista de espera

- Medir o livro inteiro na resolução do PDF por trás, com barra de andamento, para a lista "Para revisar" e a
  janela "Antes de processar" ficarem completas antes de processar (ressalva 2).
- Reacertar os limites da regra no preparo novo (G6), com um livro novo no estudo (ressalva 1).
- Fazer a marcação "letra e traço" à mão valer contra o apagar do "Só as letras" (bug acima), para o
  retângulo laranja poder virar uma zona ajustável, como o Samuel descreveu ("como na opção 3").
