# Central de decisões: perguntas reescritas para o Samuel (13/11/2026)

Trabalho do verificador, só de texto: **nenhuma linha do programa mudou**. As perguntas foram reescritas no formato
das dez regras de "Como perguntar e responder ao Samuel" (CLAUDE.md §11.13). Os ids das perguntas e das opções
continuam os mesmos; nenhuma opção que ele já escolheu saiu. A página da Central acrescenta sozinha a opção "Só
comentário"; a opção "Ainda não entendi" ficou só onde ela já existia.

- **Arquivos prontos para publicar** (documento inteiro de cada aba, para `set`): `novas/<aba>.json`.
- **Imagens novas:** `novas/imagens/`. O `src` delas é `imagens/<arquivo>.png`; a gerente sobe e troca pelo endereço
  da Central. As legendas estão também em `novas/imagens/legendas.json`.
- **Como os prints novos foram tirados:** programa da versão de teste (ramo `obra-2026-10-26`, commit `4c48e899`), numa
  worktree própria (`.claude/worktrees/central-reescrita`), sem janela na tela (modo sem tela do Qt, janela de 1280 x
  657 a 125%), prioridade baixa, cópias dos livros e pasta de dados à parte. Scripts em `scripts/`.


## Parte 1: as perguntas que destravam consertos (8 perguntas mudaram)

Arquivos: `novas/perg-revisao-codigo.json` (4), `novas/acrescentei-27-10.json` (3 das 37; as outras 34 iguais),
`novas/perg-mover-rotulo.json` (1).

Em todas: a primeira frase diz o que é e onde fica, com o caminho de clique; saíram os números de decisão do meio do
texto (ficam só no fim, entre parênteses, "para consulta"), "motor", "escolha da gerente" e as citações longas do
Livro; entrou "O que muda no que já funciona", "Situação" e "O que você escolhe"; cada opção diz o que acontece.

### rev-usar-em-todas ("usar em todas" deixa de fora as páginas mexidas à mão?)
- **Mudou:** título e texto; o nome do botão em cada ferramenta ("usar em todas" / "aplicar em: todas"); o caso real
  numa frase por ferramenta; **acrescentei o que muda no que já funciona**: com "Sim", no Girar a página virada à mão
  deixa de acompanhar as outras (muda em parte a decisão de 06/10, "Todas ficam viradas como a folha da vez"). Isso
  não estava dito e é regra 6 / D-605.
- **Por quê:** ele ainda não respondeu; o texto antigo tinha um parágrafo só de citações com números (D-090, D-091,
  D-545, D-035, D-667), o padrão de "Não sei de que obra está falando" e "Não se deve usar código na nomeação".
- **Prints:** os de 10/11 continuam valendo (conferi: nenhuma mudança no código do "usar em todas" desde então). Já
  estão no modelo do girar (azul antes, laranja como é hoje, verde a outra opção).

### rev-letra-clara-todas ("Letra clara em fundo escuro" vai junto no "Aplicar em: todas"?)
- **Mudou:** título e texto; onde fica a caixinha ("Mais ajustes" do painel "Filtro da página"); "é defeito";
  **acrescentei**: com "Sim", a caixinha vai como está na página da vez, então também DESMARCA nas outras se nela
  estiver desmarcada (é como o Automático já faz: conferido em `core/automatico.py`, que grava o valor em todas as
  páginas em que roda).
- **Conferido no programa hoje:** a lista do "Aplicar em" (`ui/tela_conferir._campos_do_aplicar_em`, juntada em 13/11)
  ainda não tem a caixinha. O fato da pergunta continua verdadeiro.

### rev-dividir-grade-linha (o "dividir" da grade corta onde você deixou a linha?)
- **Mudou:** título e texto; "linha do motor" virou "onde o programa acha a lombada" (também nas legendas); tirei a
  afirmação de que o "dividir todas" também corta na linha arrastada (não conferi); acrescentei que na folha sem linha
  arrastada nada muda.

### rev-girar-grade (o girar da grade deixa todas viradas do mesmo jeito?)
- **Mudou:** título ("como a página da vez" na grade é ambíguo: na grade não há página da vez; troquei por "todas
  viradas do mesmo jeito"); acrescentei a perda: quem usa a grade para girar cada página ¼ a partir de onde está perde
  esse jeito com "Sim".

### b-abas-nomes (os nomes curtos das abas do "Abas no alto")
- **Motivo:** "Ainda não entendi" + "No caso, isso é uma opção a mais do que a que temos hoje?" (06/11). A gerente
  respondeu no chat da pergunta em 07/11, mas a pergunta continuou igual (com o código de rodada
  `7-paineis-da-direita-opcao-1`, "402 C" e "D-033" no texto).
- **Mudou:** responde primeiro a dúvida dele ("Não: já existe hoje; é um dos quatro jeitos que você pediu em 05/10");
  diz onde fica (menu Ver > Lado direito) e que o de fábrica é outro ("Ícones na borda"); diz com todas as letras que
  os nomes curtos foram escolhidos por um agente sem perguntar a ele (regra 9).
- **Opção nova:** `nomes-inteiros` ("As abas com o nome inteiro do painel"), como segunda sugestão de nome (regra 6:
  duas ou três opções de nome). Avisa que precisa conferir se cabe em 1280 de largura.
- **Print novo:** `b-abas-nomes-resumo.png`: o menu Ver > Lado direito (versão de teste, hoje), o lado de fábrica
  (Gradus, cópia, hoje) e o "Abas no alto" (print de 28/10, Palatino).
- **Achado ao tirar o print (não confirmado em janela de verdade):** no programa de hoje, sem janela na tela, ao
  trocar para "Abas no alto" a barra de menu (Arquivo, Editar...) some: `menuBar().isVisible()` = falso, nas duas
  vezes que tentei (`cru/p2/e-abas-no-alto.png`, `cru/p3/4-abas-depois-de-redimensionar.png`). No print de 28/10 ela
  aparecia. Pode ser só do modo sem tela; precisa conferir na janela de verdade. Por isso usei o print de 28/10 nessa
  faixa.

### b-pdf-desatualizado (o cartão deve dizer "PDF desatualizado"?)
- **Motivo:** "Ainda não entendi" + "Isso se aplica só se eu fizer alterações né?" (06/11).
- **Mudou:** responde primeiro ("Sim, só quando você muda alguma página; folhear não conta", conferido na regra do
  programa `ui/janela_principal._ver_se_o_pdf_ficou_velho`); diz que não é defeito, de onde veio (o conserto que ele
  mandou em 05/10), que "PDF desatualizado" é coisa nova e o que muda em cada opção. Tirei o "etapa 9b-1", "Lista de
  bugs 332" e "D-309" do meio do texto.
- **Print novo:** `b-pdf-desatualizado-resumo.png`, montado com os prints de 28/10 (a regra do programa não mudou
  desde então), cortados só na barra do alto e no cartão, para tirar as páginas cinzas ainda carregando e o botão
  cortado "ontinua" que distraíam.

### v-capa-aviso (pares trocados: quando o programa avisa?)
- **Motivo:** comentário de 13/11: "mas vai ter um botão para fazer isso antes do imprimir livros?"
- **Mudou:** responde primeiro: sim, o botão que ele mandou fazer em 09/11 vai ficar no "Duas lado a lado" e ele usa
  quando quiser, antes de "Montar para imprimir"; ainda não está feito. **Acrescentei que já hoje dá para acertar à
  mão**: botão direito na miniatura da capa, "adicionar página em branco depois" (função que ele testou em 09/11:
  "pagina em branco funciona"). Disse como o Acrobat faz (a escolha de mostrar a capa sozinha no modo de duas páginas).
- **Print novo:** `v-capa-aviso-resumo.png` (La vida eterna, cópia, dividido pelo Automático, "Duas lado a lado"):
  azul, a página 7 impressa à esquerda; verde, o menu do botão direito e, depois do clique, a 7 à direita.
- **Não conferido:** que a página em branco anda também os cadernos do "Montar para imprimir". Está escrito no
  Livro (D-623: "entra no livro, no PDF e nos cadernos") e ele testou a página em branco, mas não montei os cadernos
  deste livro.

### mover-rotulo-antes (o Mover com o "antes / depois")
- **Motivo:** "Ainda não entendi" + "Isso ficou bem estranho né, acho que não deveria dar para ver o antes/depois
  enquanto se mexe na folha, no caso do mover." (07/11). A pergunta antiga era sobre o lugar do rótulo; o comentário
  dele pede outra coisa.
- **Mudou:** título, texto e opções. Diz o que é o "antes / depois" e o Mover, como é hoje (o que ele aprovou em
  04/11) e que as opções novas mudam essa decisão só no Mover.
- **Opções novas:** `so-a-pagina` ("Com o Mover, só a página", sugestão) e `some-ao-arrastar` (a proposta da
  gerente de 07/11). As antigas `fica` e `mudar` continuam, com texto mais claro.
- **Print novo:** `mover-rotulo-antes-resumo.png` (Gradus, cópia, dividido, página 11, ferramenta Mover): azul, com
  "antes / depois" ligado; verde, só a página.

### Fatos que não consegui confirmar no programa (Parte 1)
1. Cadernos com a página em branco posta à mão (v-capa-aviso): não montei os cadernos; vale o Livro e o teste dele.
2. "dividir todas" com a linha arrastada (rev-dividir-grade-linha): não conferi; tirei a frase.
3. Se as abas com o nome inteiro cabem na coluna da direita em 1280 de largura (b-abas-nomes): escrito como algo a
   conferir antes de fazer.
4. A barra de menu que some no "Abas no alto" sem tela: não conferi na janela de verdade.


## Parte 2: a aba "Revisão dos nomes" (20 perguntas mudaram)

Arquivo: `novas/nomes-28-10.json` (as 20; o resumo da aba também, que tinha "D-374", "D-365"
e caminhos de arquivo).

**Em todas:**
- A primeira frase diz onde o botão fica e o que ele faz ("Do que se trata").
- Depois, por que o nome confunde, com o caso real e as palavras do Kaique.
- Depois, de onde veio, com data e palavras dele. Saíram os números de decisão, os códigos de rodada (`pr-esta-bom`,
  `b-11-nome`, `fr-26`...), "etapa 9a/9b-1" e "escolha da gerente" (agora: "escolhido pela gerente, sem perguntar a
  você", regra 9).
- No fim, a mesma frase de situação: nada mudou; o que o botão faz não muda; o nome escolhido entra junto com a
  arrumação nova do layout, como ele pediu em 04/11 ("Isso deveria ser feito junto com a repaginação do layout [...]
  o agente não vai escolher os nomes ele pode sugerir opções"). Isso não estava dito e é regra 10.
- Cada pergunta tem duas sugestões de nome, "Deixar como está" e "Ainda não entendi" (ids mantidos). A sugestão
  passou para o campo "sugestão", com o porquê em uma frase.
- **Conferido no programa de hoje** (busca dos textos de tela em `ui/` e `core/`): todos os nomes citados continuam
  lá. Únicas diferenças: o subtítulo da etapa agora é "tira o amarelado" (minúsculo); o "Show Details..." da Lista de
  atalhos é o botão que o próprio Qt põe (vem do `setDetailedText`), não um texto escrito no código.

### As três que voltaram com "não entendi"

**nm-desligar-marcadas** — ele: "Eu não entendi o que você quis dizer." (13/11)
- O texto antigo dizia o que o botão faz só em palavras ("o programa deixa de fazer sozinho..."). Agora diz que ele
  **desfaz** o que o Automático fez nas etapas marcadas, e mostra.
- **Print novo** `nm-desligar-marcadas-resumo.png` (Gradus, cópia, hoje): azul, depois do Automático só com
  "Dividir folhas ao meio" (140 páginas); verde, depois de "desligar as marcadas" (as folhas voltam inteiras; a
  caixinha da etapa fica desmarcada; na tira, a metade que sobrou aparece como "apagada"). Conferido pelo Histórico:
  "Automático desligado: dividir folhas ao meio".
- As opções viraram "desfazer estas etapas" e "tirar o automático das etapas marcadas" (ids `estas-etapas` e
  `nao-fazer` mantidos; ele não tinha escolhido nenhuma).
- **Achado no print (não é desta pergunta):** depois de desligar o Dividir, a barra de baixo continua "página 11 de
  140" e a tira mostra "apagada" no lugar das metades. Pode confundir o Kaique; não investiguei.

**nm-jeito-pb** — ele: "Ainda não entendi" (13/11), sem comentário.
- Agora explica primeiro o que é a lista (maneiras de decidir o que vira preto e o que vira branco) e por que
  "Sauvola", "Otsu" e "Wolf" não dizem nada (são sobrenomes dos inventores).
- **Print novo** `nm-jeito-pb-resumo.png`: a lista (print de 28/10) e a mesma página do Palatino (cópia, página 9),
  desenhada pela conta do PDF com cada jeito, o mesmo pedaço aumentado. Aviso honesto na imagem: nesta página a
  diferença é pequena (a moldura da direita e a grossura das letras). O "Automático" escolheu o Sauvola nela.
- Segunda opção (`so-padrao`) ganhou o texto que faltava.

**nm-tela-livros** — ele: "Suas respostas ainda não são claras, tem que rever isso, não consegui entender, tem que
ser de fácil entendimento." (13/11)
- O texto antigo juntava três assuntos num parágrafo só. Agora são três itens numerados (1. tirar da lista;
  2. achar o PDF que mudou de pasta; 3. "projeto" no lugar de "livro"), e a imagem tem uma faixa para cada um.
- **Imagem nova** `nm-tela-livros-resumo.png`, montada com os quatro prints de 28/10 (os textos continuam iguais no
  programa de hoje).
- A opção `so-botoes` ganhou o texto que faltava.

### As outras 17 (reescritas no mesmo formato, sem print novo; os prints de 28/10 continuam)
- **nm-codigos:** ele já decidiu em 09/11 ("Não se deve usar código na nomeação de coisas"; mandou consertar). A
  pergunta agora diz isso, diz que está na fila, e pergunta só o que falta (tirar só o código ou a frase da regra). A
  opção "Deixar como está" ficou (o id não sai), mas avisa que é contra o que ele decidiu. Conferi hoje: os três
  códigos ainda estão na tela.
- **nm-montar-nomes:** tirei das opções o "Folhas de (0 = todas)" e o "Páginas do livro de (0 = todas)", porque ele
  já decidiu em 08/11 a caixinha "Imprimir só algumas folhas" (regra 10: não perguntar de novo).
- **nm-montar-frases:** diz com todas as letras que as frases foram escolha de agente, sem pedido dele.
- **nm-dois-mover, nm-desligar-marcadas:** dizem que o nome foi escolhido pela gerente, sem perguntar.
- Opções que estavam sem texto ganharam texto: `aumentar` (nm-dois-mover), `nao-fazer`, `so-padrao`, `so-botoes`.
- **nm-esta-bom, nm-antes-de-processar, nm-folha-pagina, nm-nao-esta, nm-limpar-a-folha, nm-scantailor, nm-tirada,
  nm-frase-salvar, nm-historico, nm-menu-marcar, nm-manter-cor-tinta, nm-montar-dois, nm-atalhos:** mesmo conteúdo,
  no formato novo; nomes de decisão e de rodada tirados do meio do texto.

### Fatos que não consegui confirmar (Parte 2)
1. Os números dos exemplos (54 avisos, 8 páginas, "6 páginas", "12 das 50") são dos prints e testes de 26-28/10;
   não refiz as contas hoje.
2. Se o Kaique ainda vê "Show Details..." em inglês: depende do Qt instalado no notebook dele; no PC, conferi só no
   código que a lista vem pelo "detalhe" da caixa de mensagem.


## Parte 3: as abas de auditoria (141 perguntas mudaram)

Arquivos: `novas/auditoria-3-com-ressalva.json` (31 das 32), `novas/auditoria-4-funciona.json` (88 das 92),
`novas/auditoria-5-escolhas-da-gerente.json` (16 das 19), `novas/auditoria-6-para-depois.json` (6 das 13). As que
ele já respondeu (15) ficaram iguais, letra por letra (conferido por script). O resumo de cada aba foi reescrito.

**Motivo (para todas):** as fichas "Situação / Você pediu / O que isso quer dizer / Solução na versão de teste / Parte
do programa / Ressalva" são, nas palavras da regra nova, as que mais voltaram com "Ainda não entendi" (CLAUDE.md
§11.13, regra 7: "Nada de ficha com campos"). Os comentários dele que motivaram a regra: "Um monte de texto e não
consigo saber o que era para saber realmente" · "os relatorios continuam muito ruins e dificeis de entender" · "nos
para responder, não tem explicações sobre o que precisa ser respondido".

**O que mudou em cada uma (o mesmo molde para as 141):**
1. **Onde fica e o que é**, numa frase só ("Onde fica: Dividir as folhas. O que é: ...").
2. **O que ele pediu, com a data e as palavras dele.** Quando a ficha dizia "Você pediu" mas era "(escolha da
   gerente, D-014)", agora diz com todas as letras: "ninguém perguntou a você; a gerente escolheu sozinha em 27/10"
   (regra 9). Isso acontecia em várias da aba 4 e da aba 6, não só na aba 5.
3. **Como está hoje** na versão de teste e, quando havia ressalva, "O que ainda não está bom".
4. **Se ele já testou depois da auditoria de 29/10**, procurado no Livro de decisões (ver a lista abaixo).
5. **O que ele escolhe**, com as mesmas opções (ids iguais), e o texto de cada opção dizendo o que acontece.
6. O número da decisão só no fim, "(Para consulta: D-xxx)".

**Palavras de dentro tiradas** (por script, `scripts/parte3.py`, função `limpar`, e conferidas por busca no
resultado): números de decisão no meio do texto (viraram "a decisão de 05/10"), códigos de pergunta e de rodada
("G2:", "P6:", "F5", "R7 203 D", "904 A", "rv4-...", "dv-..."), números de item do plano ("2.13", "1.6/2.10",
"item 7.3"), "etapa 9b-2", "obra", "junção", nomes de arquivo e de função, "escolha da gerente" como rótulo. Os
títulos que vinham cortados com "…" foram refeitos (à mão; os outros pela primeira frase do "o que é"). A busca
final não acha mais nenhum desses códigos nos textos reescritos ("A4" é o papel e ficou).

**O que não mudou:** as imagens (são as que já existiam, prints de quando o assunto foi decidido; a tarefa não pedia
print novo aqui); as palavras dele entre aspas (só tirei os códigos que vinham grudados nelas).

**Ressalva desta parte:** o texto é montado por script a partir das fichas antigas e do Livro, com 32 títulos e 22
explicações ou pedidos reescritos à mão. Li as 141 por amostra e por busca de padrões estranhos, não uma por uma com o mesmo
cuidado das Partes 1 e 2. Algumas explicações continuam compridas porque a decisão é comprida (ex.: a ferramenta
Mover). A gerente pode querer encurtar essas antes de publicar.

### Já testado ou já respondido por ele depois da auditoria (o que achei no Livro)
- **Testado em parte (ficam na lista, com a frase "Já testado por você" dizendo o que falta):** au-d-021 (setas,
  10/11 "sim"), au-d-334 e au-d-487 (o "inserir" virou "adicionar página em branco", 09/11 "pagina em branco
  funciona"), au-d-568 (Ctrl + roda 01/11 "1- funcionando"; Shift + roda 02/11 "shift funcionando"), au-d-373 e
  au-d-007 e au-d-090 (Dividir testado em 10/11, "ok"), au-d-168 (caixinha irmã testada em 29/10), au-d-095 (cantinho
  do giro, 10/11: "a cor é diferente da cor do papel").
- **Não achei teste dele no Livro** para as outras 124. O Livro pode não ter anotado algum teste feito no chat;
  quando é assim, a pergunta diz "Você ainda não testou isto depois da auditoria de 29/10 (não há teste seu no Livro
  de decisões)".


## Pode sair da lista (já resolvida ou já testada por ele)

Oito perguntas das abas de auditoria. Em cada uma o texto novo já diz por quê, e a sugestão é "Pode sair da lista".
A gerente decide se tira; nada foi gravado na Central.

| Pergunta | Aba | Por que pode sair | Prova |
|---|---|---|---|
| au-d-004 (o Automático pergunta antes de mexer nas páginas mexidas à mão) | Auditoria 4 | Ele usou e testou esse aviso duas vezes depois da auditoria. | Livro, D-607: "04/11: testada pelo Samuel: '7- ok'"; D-661: "testada pelo Samuel em 10/11, funciona" ("fiz os dois testes que você pediu e estão funcionando.") |
| au-d-486 (página da direita da janela grande do Automático = a original) | Auditoria 5 | A escolha da gerente foi trocada por um pedido dele, já testado. | Livro, D-577: "Substitui a D-486 (escolha da gerente)" · "testada pelo Samuel em 01/11: 'está funcionando'" |
| au-d-547 (todas as telas mostram a página já movida) | Auditoria 5 | Ele pediu de novo e testou. | Livro, D-649: "Reforça a D-547" · "Testada pelo Samuel em 13/11: 'funcionando'" |
| au-d-483 (a medida por trás só roda no livro novo) | Auditoria 4 | Resolvida junto com outra que ele já respondeu. | Central, resposta `au-d-284` (29/10): "Está certo assim" |
| au-d-490 (o "Sim" do aviso do fundo vale na hora) | Auditoria 4 | Resolvida junto com duas que ele já respondeu. | Central, respostas `au-d-135` e `au-d-069` (29/10): "Está certo assim" · "Eu consigo usar essa opção sem ter que começar de novo." |
| au-d-476 ("Marcar como" iluminura e moldura, para depois) | Auditoria 6 | A pergunta irmã já foi respondida. | Central, resposta `au-d-566` (09/11): "Fica para depois"; Livro, D-695 |
| au-d-478 (espaços "Limpo / Completo" viram arranjos salvos) | Auditoria 6 | A pergunta irmã já foi respondida. | Central, resposta `au-d-565` (13/11): "Fica para depois" |
| au-d-480 (manuscritos na leitura do texto, Fase 7) | Auditoria 6 | A pergunta irmã já foi respondida. | Central, resposta `au-d-557` (09/11): "Fica para depois" · "Vai entrar sim."; Livro, D-677 |

**Também vale olhar (não tirei):** a Parte 2, `nm-codigos`, já foi decidida por ele em 09/11 (D-687, "Consertar").
A pergunta ficou só para o resto da frase; se a gerente achar que "tirar só o código" é detalhe técnico do que ele
mandou, ela pode sair também.

## O que ficou criado e o que foi apagado

- **Fica** nesta pasta: `novas/` (a entrega), `relatorio.*`, `ONDE-PAREI.md`, `scripts/` (para refazer as imagens e
  os textos), `cru/` (as fotos cruas dos prints novos, os textos de conferência e as anotações dos scripts),
  `partes/` (as seções deste relatório) e os registros `cru-p*.log`.
- Os scripts de montagem das imagens leem os prints antigos da Central que baixei para a pasta de rascunho desta
  sessão (`ANTIGAS` em `scripts/montar.py`); para refazer depois, é preciso baixá-los de novo.
- **Apagado no fim:** a worktree `.claude/worktrees/central-reescrita` (junções `modelos` e `gabarito\paginas`
  tiradas antes, e conferido que as pastas originais continuam inteiras), com as cópias dos livros e as pastas de
  dados dos scripts que estavam dentro dela.
