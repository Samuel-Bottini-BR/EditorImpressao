# Causas dos erros do Lusíadas e plano de cada conserto (implementador, 17/11/2026) — onde parei

Tarefa de **investigação**: achar a causa de cada erro e escrever o plano do conserto. **Nenhuma linha do programa
muda.** Quem pediu: a gerente, com as 13 respostas do Samuel de 17/11 na Central (`agente-causas.json`).

- Cópia: `.claude/worktrees/causas-lusiadas`, ramo `causas-lusiadas-2026-11-17`, a partir de `obra-2026-10-26`
  (`a9d81030`). Junção `modelos` (PowerShell `New-Item -ItemType Junction`).
- Base do estudo: ramo `lusiadas-provas-2026-11-14` (`0bd75b41`), relatório e ONDE-PAREI em
  `relatorios/lusiadas-provas-2026-11-14/`. Investigações vizinhas: `quadrados-capa-2026-11-13` (capa do Gradus),
  `quadrados-origem-2026-11-10` / `quadrados-c-2026-11-10` (quadrados do Melhorar e do Mágico pro, D-668).
- Prints do Lusíadas: `prints/` desta pasta, **fora do git** (direito autoral).
- Nada na tela do Samuel: só conta sem janela ou `QT_QPA_PLATFORM=offscreen`. Pasta de dados própria.

## Decisões que esta tarefa precisa cumprir (palavras dele)

- D-691: "eu quero ver esses erros, as provas dele e uma explicação de como acontece, explique de forma simples. quero
  antes de dar inicio."
- D-678 (p. 14, remendos): "tem que verificar o que aconteu". Comentário de 17/11: "Quero entender porque isso
  aconteceu. porque esses pedaços brancos estavam aparecendo também no melhorar e no magico pro e também apareceram em
  outros livros, como no Gradus primus que ele apaga um quadrado da parte superior da capa azul do livro."
- D-679 (números): 17/11: "Mudou sozinho porque ele procurou e achou mais defeitos? numero está errado por causa de
  alguma confusão que o programa está fazendo, provavelmente uma gambiarra o motor de contagem deveria valer para todo o
  programa e não fazer uma conta em cada lugar um motor para paginas e um para folhas( lembrando que eu não lembro a
  diferença entre as duas), Quero entender também o porque desse erro."
- D-680 (miniatura em branco): 17/11: "Quero saber porque isso acontece."
- D-681 (barra cortada): "não é urgente."
- D-682 (página deitada): 17/11: "Quero saber porque saiu deitado? o programa aplicou o girar? é um defeito do
  programa ou do agente que fez esses testes?"
- D-684 (laranja com a Mão): 17/11, opção 2 ("o botão "marcações" manda também no laranja") · "Quero entender porque
  este bug está acontecendo. Segundo, onde aparece essas marcações, vemos claramente alguns defeitos nas gravuras,
  vemos manchas brancas."
- D-685 (aviso de salvar): 17/11: "Quero saber porque esse problema acontece."
- D-686 (frase depois de tirar): 17/11: "Depois que tira uma pagina do livro, ela tem que sumir das miniaturas, ela só
  continuaria existindo se tivessemos deixado ela em branco ou simplismente excluido o conteudo dela."
- D-687 (código na tela): "Não se deve usar código na nomeação de coisas." · 17/11: "além disso tem que rever as regras
  dos agentes para que eles não cometam mais esse erro."
- D-688 (lista volta ao topo): 17/11: "pode consertar, mas quero saber o motivo desse erro, pois isso é um gambiarra né."
- D-528 (marcações ao dividir): 17/11, "Concordo, fica assim" · "Mas tem que ver se não tem gambiarra nessa decisão, e
  nessa função."
- D-689 (p. 22): 17/11, só comentário: "Gostaria de saber como seria esse conserto, por enquanto poderia ter só um
  aviso né? Seria possivel criar uma IA só para parte de avisos do programa?"
- D-690 (p. 8): 17/11, só comentário: "explique melhor como vai funcionar a opção 3."
- Regras: CLAUDE.md §11.12 (sem gambiarra: causa, regra da ferramenta, todos os caminhos), §11.13 (como escrever para
  ele), §10 (modelo de print do girar), §4.10 (caminho inteiro), §3 (rede neural só aponta, nunca desenha), §11.7 (só o
  que ele mandou), D-605 (o novo não estraga o testado).

## O que já está escolhido e testado aqui

Nada é mexido (só leitura). Ao propor cada conserto, cito as decisões e provas que ele não pode mudar (na seção de cada
item, "não pode mudar").

## Como fica para quem usa e no livro

Nada muda nesta tarefa: não há código. Em cada plano de conserto digo o que muda para o Kaique e no PDF.

## Plano da investigação

1. [x] Ler regras, Central, estudo de 14/11, Livro (feito ao começar).
2. [x] Remendos e pedaços brancos (lu-1, lu-7 parte 2): decompor a marcação da p. 14 e da p. 8 (de onde vem cada
   pedaço: leitor de texto, ScanTailor, sobra de tinta, papel); rodar Melhorar e Mágico pro na p. 14 pelo caminho
   inteiro; ligar com o Gradus (estudo de 13/11) e com a D-668.
3. [x] Números (lu-2): todas as contas de "páginas" e "folhas" do programa; o sino.
4. [x] Miniatura em branco (lu-3), frase (lu-9), barra (lu-4), aviso de salvar (lu-8), lista (lu-11), códigos (lu-10).
5. [x] Página deitada (lu-5): de onde vem o giro na montagem.
6. [x] D-528: ler a função de dividir com as marcações.
7. [x] lu-12 e lu-13: explicar o conserto e a opção 3 com o caso real.
8. [x] Prints novos no modelo do girar onde a resposta pede imagem.
9. [x] "Respostas para a Central", uma por item.

## Andamento

(abaixo, a cada passo)

### Passo 2 (lu-1, lu-7): feito — o que achei
- `scripts/decompor_marcacao.py` (procura a marcação de novo, espiando por dentro) → `decompor_marcacao.json`; imagens
  em `prints/decompor/` (fora do git).
- P. 14: o leitor de texto NÃO viu texto na página (só uma caixa "figure"). Os dois pedaços azuis ("letra") são
  buracos da pintura do ScanTailor (ele deixou de fora as partes escuras e lisas: a nuca do homem da frente e o casaco
  do da direita). A regra `letra = (letra_layout | blocos_de_tinta(sobrou)) & ~gravura` (core/detectar_regioes.detectar)
  chama de "letra" toda tinta que sobrou fora da gravura, sem conferir se parece escrita. O mesmo pedaço sai remendo
  nos três filtros: Preto e branco (1 bit), Melhorar e Mágico pro (cinza chapado, com pontinhos brancos na beirada).
- P. 8: igual, mais os pedaços do céu e do mar que sobraram viram "papel" (branco).
- `scripts/pedacos_de_letra.py` → `pedacos_de_letra.json`: os pedaços remendo (p. 14 e o mar da p. 8) dão
  "não parece escrita" na régua que o detector já tem (`_parece_escrita`) e encostam na gravura; os blocos de texto da
  p. 2 dão "parece escrita" e não encostam. Medida em poucas páginas: o conserto precisa medir no gabarito.
- Ligação com o Gradus (estudo de 13/11, ramo quadrados-capa): lá o pedaço "ÓNAI" veio de outra porta (caixa de texto do
  leitor, regra "a escrita ganha", `ESCRITA_GANHA_DO_SCANTAILOR`) e o branco do passo da sombra em quadros do Preto e
  branco (D-700, suspensa). Os quadrados do Melhorar e do Mágico pro na Escola eram a limpeza do papel (D-668, consertado
  13/11, testado por ele: "funcionando").

### Passos 3 a 8: feitos (detalhe em "Causas e planos", abaixo)
- Sonda da D-528 (rodada e apagada; era um teste temporário em `tests/_sonda_d528_causas.py`, só para usar o conftest):
  livro sintético de uma folha dupla → "dividir esta" → "não dividir esta" → "pintar de branco" na metade direita da
  página juntada → "dividir esta" de novo (o caminho das metades guardadas, como a tela chama). Resultado:
  `selecao esquerda = [] | direita = []` — a marcação feita na página juntada some. (1 passed, 4,3 s, offscreen,
  `--basetemp=D:/agente_temp_testes/causas-lusiadas`.)
- Varredura dos textos de `ui/` com o script do estudo (`codigos_na_tela.py`) na versão de hoje (`a9d81030`, 94 commits
  depois da versão do estudo): continuam os mesmos três (G2, D-068, D-094), todos em `ui/automatico.py`. Fora de
  `ui/`, `atualizacao.py` tem D-731, D-733, D-741, D-749 em textos de passo e de registro (pelo que li, vão para o
  registro e para o script do PowerShell, não para a tela; a conferir no conserto).
- Prints novos (fora do git): `prints/lu1-remendos-nos-tres-filtros.jpg`, `prints/lu7-laranja-mostra-o-defeito.jpg`,
  `prints/lu13-opcao-3-passo-1.jpg` (montados por `scripts/montar_prints.py`; abertos e conferidos um por um).

---

## Causas e planos (para a gerente; tem palavra de dentro)

Versão lida: `obra-2026-10-26` em `a9d81030`. "Visto rodando" = medido ou reproduzido por mim hoje (ou no estudo de
14/11, dito assim); "lido no código" = dedução pela leitura.

### lu-1 (D-678) — remendos na p. 14, e os pedaços brancos no Melhorar, no Mágico pro e no Gradus
- **Causa (visto rodando):** a marcação é feita uma vez por página em `core/detectar_regioes.detectar` (chamada por
  `core/pipeline.garantir_selecao`). A gravura vem do ScanTailor; ele deixou de fora a nuca e o casaco (partes escuras
  e lisas da pintura). Depois, `letra = (letra_layout | blocos_de_tinta(sobrou)) & ~gravura` transforma em LETRA toda
  tinta que sobrou fora da gravura, sem perguntar se parece escrita, e `papel = ~ocupado` transforma em PAPEL o resto
  (céu e mar claros da p. 8). O leitor de texto nem viu texto na p. 14 (só uma caixa "figure").
- **Por que nos três filtros:** os três usam a mesma marcação (`core/filtros.aplicar_filtro_com_selecao`). Preto e
  branco: fora da gravura vale o 1 bit da página. Melhorar e Mágico pro: a LETRA recebe só nitidez e o "papel do
  bloco" (`refinar_para_tinta`) vai a 255 → cinza chapado com pontinhos brancos. Visto: `prints/decompor/p14-e-*.png`.
- **Gradus (estudo de 13/11, não refeito):** outra porta para o mesmo erro — a caixa de texto do leitor ("ÓNAI") ganha
  da gravura (`gravura &= ~escrita_certa`, `ESCRITA_GANHA_DO_SCANTAILOR`, regra de 30/09 para as legendas da Pesel); o
  branco por cima é o passo "sombra em quadros" do Preto e branco (`_sombra_em_quadros`, 27/10; D-700 suspensa). Os
  quadrados da Escola no Melhorar e no Mágico pro eram outra causa (limpeza do papel sem procurar a gravura, D-668), já
  consertada e testada por ele em 13/11.
- **Remendo ou conta repetida?** Não é remendo no filtro (os filtros são coerentes). É uma **regra que falta no lugar
  único da marcação**: "o que fica dentro da pintura é pintura, a não ser que pareça escrita". Achado vizinho (§11.12):
  o detector antigo tem `_tapar_buracos_da_iluminura` e o caminho do ScanTailor não tem — dois caminhos para achar a
  gravura, com regras diferentes.
- **Caminhos que chegam na função:** prévia (110), desenho do tamanho do PDF por trás, PDF (`processar`), figurinhas do
  Filtro e "comparar" (`renderizar_com_filtro`), tela cheia, "antes / depois", miniaturas compostas, medida do "Para
  revisar", Automático ("Gravuras e fotos") e o filtro escolhido à mão com "Respeitar" (D-659/D-668). Todos passam por
  `garantir_selecao` → `detectar`. Marcação à mão: não muda.
- **Plano, numa regra só:** em `detectar`, depois de achar a gravura e antes de montar LETRA e PAPEL: pedaço de tinta
  que sobrou, encosta na gravura e **não** parece escrita (`_parece_escrita`, régua que o detector já tem) passa a ser
  gravura; o papel cercado por essa gravura também. Medido hoje: os dois remendos da p. 14 e o mar da p. 8 dão "não
  parece escrita" e encostam; os blocos de texto da p. 2 dão "parece escrita" e não encostam
  (`scripts/pedacos_de_letra.json`). Medir no gabarito antes (Pesel: legenda sobre cartão; Graduale 222: pauta;
  Marial 150: palavras borradas). A porta do Gradus ("ÓNAI") depende da pergunta 3 do estudo de 13/11 (título escrito
  na capa colorida), sem resposta: não mexer nela sem ele.
- **Não pode mudar:** D-147/D-148, D-588, D-659/D-668, D-605. Provas: `tests/test_decisoes_quadrados_brancos.py`,
  `test_decisoes_gravura_a_mao.py`, `test_detectar_regioes.py`, `test_gravura_scantailor.py`.
- **Teste de reversão:** a p. 14 tem direito autoral (fora do git): página sintética (pintura com miolo escuro liso que
  o ScanTailor não pega) ou do gabarito; medida = fração de 1 bit dentro do contorno da pintura.

### lu-7 (D-684) — o laranja com a Mão, e as manchas onde ele aparece
- **Causa (lido no código, visto no estudo):** `ui/tela_conferir._mostrar_as_achadas` liga
  `editor_selecao.mostrar_achadas` em toda página com aviso (`pagina.precisa_revisao`, D-237), com qualquer
  ferramenta. O botão "marcações" (D-580/D-584) só manda em `mostrar_marcacao` (as cores). Dois interruptores para a
  mesma coisa ("mostrar o que o programa marcou").
- **As manchas:** o laranja é o contorno das áreas que a máquina achou; dentro da figura ele cerca os pedaços que
  viraram LETRA/PAPEL (print `lu7-laranja-mostra-o-defeito.jpg`). É a causa do lu-1, não do laranja.
- **Plano (opção 2, escolhida por ele):** uma função só, "as marcações estão à vista?", lida pelas cores e pelo
  laranja; o botão "marcações" é o único interruptor; a D-584 continua (liga sozinho nas de marcar, desliga no Zoom e na
  Mão). A caixinha "Mostrar as áreas achadas" e o laranja do "Para revisar" (D-237) obedecem ao mesmo botão — muda a
  D-237 só no que ele escolheu. Caminhos: Mão, Zoom, ferramentas de marcar, "Duas lado a lado", "antes / depois"
  (D-612), tela cheia, troca de página, reabrir. Prova: `tests/test_decisoes_marcacoes.py` continua + uma nova
  cobrando o laranja nos mesmos caminhos.

### lu-2 (D-679) — os números
- **"de 134" (lido no código, visto no estudo):** "quantas páginas tem o livro" é contado com duas contas:
  `len(projeto.paginas)` (lista inteira, com a tirada) na barra de baixo (`_atualizar_barra_de_baixo`), no Automático
  (`EstadoDoAutomatico.total_paginas`, `_numero_e_total` sem o Dividir) e no cartão da tela inicial (`projetos.py`,
  `resumo.total_paginas`); `Projeto.paginas_ativas` na janela de salvar (`_frase_do_livro`), no PDF e no Automático
  com o Dividir (`paginas_do_pdf_depois`). O comentário do Automático diz que contar pela lista é de propósito. Conta
  repetida: a mesma pergunta respondida por duas contas.
- **O sino (visto no estudo, fase d):** o número de avisos já é um motor só (`core/avisos.quantas_com_duvida`, etapa
  7). O que muda é o aviso "as contas do endireitar discordam": medido na análise (150 DPI) e de novo quando a página
  é desenhada no tamanho do PDF (`pipeline._guardar_geometria` → `_anotar_contas_discordam`), por trás, ao passar pelas
  páginas. Duas medidas da mesma coisa em resoluções diferentes; a segunda põe ou tira o aviso.
- **Plano:** (1) uma função em `core` para a numeração do livro (ex.: `core/numeracao.py`): "quantas vão para o PDF"
  (= `paginas_ativas`) e "que número esta página tem no livro que sai" (ou "fora do livro"); barra de baixo,
  Automático (resumo e contador), janela de salvar, tela inicial, "Ficou pronto" e montar para imprimir usam essa
  função. Com a D-595 (ver lu-9) a página tirada deixa de ter número. (2) O aviso das contas do endireitar é decidido
  por uma medida só, a do tamanho do PDF; enquanto ela não foi feita, o sino diz que ainda está medindo em vez de mudar
  calado (tela nova: mostrar a ele antes). Não pode mudar: D-285 e o motor dos avisos; D-617.

### lu-3 (D-680) — miniatura da página "deixada em branco"
- **Causa (lido no código, visto no estudo):** `ui/tela_conferir._acertar_as_miniaturas_movidas` pinta branca só a
  `inserida` (D-623) e compõe só a `_pagina_sai_movida`; a grade (`_pagina_dentro_da_folha` → `miniatura_como_sai`)
  igual. O PDF (`core/pipeline._filtrar`, l. 3429) testa `em_branco or inserida`. Conta repetida: "a página sai em
  branco?" respondida em três lugares; a da tela esqueceu o caso comum (a inserida já é `em_branco=True`).
- **Plano:** `core/paginas_em_branco.sai_em_branco(pagina)`, usada por `_filtrar`, pela tira e pela grade. Caminhos:
  Delete, menu Página, Propriedades > Esta página, botão direito (D-598), grade com várias, aviso "Parece em branco",
  Ctrl+Z/Ctrl+Y, reabrir. Prova: miniatura e grade brancas em todos, e o desfazer devolve a de antes.

### lu-9 (D-686) — a faixa depois de "tirar do livro", e "tem que sumir das miniaturas"
- **Causa (lido no código, visto no estudo):** `_atualizar_faixa` tem ramo para `em_branco` e para a conferida, não
  para `apagada`. Cada parte da tela decide sozinha a situação da página (tira: "apagada"; botões: "trazer de volta";
  faixa: frase da ferramenta).
- **O pedido dele já é decisão:** D-595 (31/10): "Somem da tira; um botão "4 tiradas do livro" no começo da tira" —
  "não construída" no Livro.
- **Plano:** uma função em `core` com a situação da página (tirada / em branco / com aviso / conferida / normal), usada
  pela faixa, tira, grade, botões e "Antes de processar"; com ela, construir a D-595 e a frase da faixa. D-650 e o
  "trazer de volta" continuam. Junta com lu-2 e lu-3.

### lu-4 (D-681) — barra de baixo cortada (não é urgente)
- **Causa (lido no código, visto no estudo):** fila só (`QHBoxLayout`) de botões com texto fixo; a janela não pode
  ficar mais larga que a tela (de propósito); com o painel aberto a 1280 × 657 sobra menos lugar que a soma dos textos,
  e o Qt corta. Falta a regra "o que encolhe primeiro". Vizinho: a tela inicial já tem o jeito estreito ("1 de 134",
  `ui/tela_inicio.py:976`); a barra de baixo não.
- **Plano:** uma regra de encolher para a barra inteira (textos curtos), num lugar só. Mudança de tela: mostrar antes.

### lu-5 (D-682) — a página deitada no arquivo para imprimir
- **Causa, duas peças (visto no estudo):** (1) folha com só uma página impressa: o Dividir do ScanTailor corta fora do
  meio (folha 2 em 0,239; folha 7 em 0,732); `core/pipeline.achar_divisao` guarda a linha e só avisa "Lombada
  incerta". (2) Na janela "Montar para imprimir", a caixinha "Rotação automática" (nome do UPDF, marcada de fábrica)
  gira toda página mais larga que alta (`core/impressao._gira`). O aviso existe (`_avisos_de_giro`) mas só é mostrado
  depois de gravar (`ui/dialogo_impressao._terminou`); a prévia da janela (`previa_da_folha`) não calcula avisos.
- **Não foi a ferramenta Girar nem escolha do agente:** o agente do estudo fez o caminho do Kaique ("continuar assim
  mesmo" na "Antes de processar", `scripts/piloto.py` do estudo, l. 277-299; montar com as opções de fábrica), e o
  teste do Kaique de 06/11 deu o mesmo na folha 7.
- **Plano:** (1) os avisos da montagem saem da mesma função para a prévia e para o gravar (o giro só precisa do
  tamanho das páginas), à vista antes de gravar. (2) O corte da folha com "Lombada incerta": pergunta para ele (linha
  das vizinhas? só avisar mais forte?) — não decidir sem ele.

### lu-8 (D-685) — aviso "será substituído"
- **Causa (lido no código, visto no estudo):** `ui/widgets/destino.py`: o campo do nome (`textEdited`) só chama
  `_conferir`; `alterado` só sai em `escolher_pasta`; a faixa (`JanelaConfirmar._reavaliar`) só escuta `alterado`. Duas
  conferências do mesmo fato, com textos diferentes ("eu pergunto antes de substituir" × "Se continuar, ele será
  substituído"). O teste antigo chama `_reavaliar()` por dentro.
- **Plano:** o seletor emite `alterado` sempre que o destino muda; uma função responde "já existe?" e um aviso só fica
  (qual texto: perguntar a ele). Prova que digita no campo. Caminhos: escolher pasta, digitar, abrir a janela, menu
  Arquivo > "Nome do arquivo...".

### lu-10 (D-687) — códigos na tela, e a regra para os agentes
- **Causa (git, visto no estudo):** os três entraram juntos em `e2321b16` (26/10, etapa 3). O agente pôs o número da
  decisão dentro do texto da tela, em vez do comentário. Nenhuma prova varre os textos da tela; a regra "nenhuma
  palavra de dentro" (§11.13) fala do que se escreve PARA ele, não dos textos do programa.
- **Plano:** tirar os três; prova nova que varre os textos de `ui/` (strings que não são docstring nem comentário) e
  falha com D-123, G2, rv4-..., "item 2.11", "etapa 3", "obra".
- **Texto proposto (para `implementador.md`, `layout.md`, `verificador.md` e uma linha no §11.13; NÃO mudei nenhum
  arquivo de regra):**
  > **Textos da tela sem código (Samuel, 17/11/2026: "tem que rever as regras dos agentes para que eles não cometam
  > mais esse erro").** Todo texto que o Kaique pode ver — botão, rótulo, balão, aviso, título de janela, mensagem —
  > usa só palavras da tela, do livro e da página. Nunca leva número de decisão (D-123), nome de pergunta (G2,
  > rv4-..., k0611-...), item ou etapa do plano ("item 2.11", "etapa 3", "obra"), nome de agente, de arquivo ou de
  > função. O número da decisão vai no comentário do código, na linha de cima, nunca dentro das aspas do texto. Antes
  > de entregar, rode a prova que varre os textos da tela; se ela acusar, troque o texto, nunca a prova. O verificador
  > lê os textos novos e procura código de propósito.

### lu-11 (D-688) — a lista do Automático volta ao topo
- **Causa (lido no código, visto no estudo):** `ui/automatico.ListaDeEtapas.refazer` (ligada a `estado.mudou`) apaga e
  recria todas as linhas a cada mudança; a rolagem volta a 0 (guarda a linha escolhida, não a rolagem).
- **É gambiarra?** Não é regra repetida (uma classe, usada pelo painel e pela janela). É o atalho "refazer tudo" em
  vez de "mudar só o que mudou". Seria remendo guardar e devolver a rolagem; o certo é `refazer` atualizar texto e
  caixinha das linhas que existem e só recriar quando a ordem muda (arrastar), mantendo a rolagem.
- **Caminhos:** caixinhas, opções de dentro das etapas, receita, arrastar, painel compacto e janela grande.

### au-d-528 — conferência da função "marcações ao dividir"
- **Certo (lido + provas existentes):** uma função (`core/dividir_a_mao.metades_da_pagina` →
  `core/zonas_na_folha.repartir_nas_metades`) serve o "dividir esta" e o Automático; a marcação da máquina não passa
  (é procurada de novo); provas `tests/test_decisoes_nucleo2.py::test_*d528*` (à mão e Automático).
- **Achado 1 (visto rodando, sonda):** depois de "não dividir esta", a marcação feita na página juntada **some** ao
  "dividir esta" de novo: o caminho das metades guardadas (`campos_para_dividir`, `metades_guardadas`, l. 242-250)
  devolve as metades de antes e só leva `apagada` e `em_branco`. Duas listas do que passa da página inteira para as
  metades. Trabalho à mão perdido sem aviso.
- **Achado 2 (lido):** sem a geometria anotada, `repartir_nas_metades` usa conta própria aproximada (só o x); o
  comentário diz que não acontece com zona feita na tela. Caminho reserva com conta própria.
- **Achado 3 (lido; já no §11.12 pela revisão de 10/11):** o Automático deixa a folha inteira marcando a da direita
  "apagada" (`core/automatico`, ramo `len(pags) >= 2`); o "não dividir esta" junta numa página (D-498). Dois jeitos.
- **Zona que atravessa a linha:** o centro decide o lado; escolha documentada, não remendo.
- **Plano:** uma lista só do que passa da página inteira para as metades, nos dois caminhos, com a marcação à mão; a
  sonda vira teste de reversão.

### lu-12 (D-689) — página 22
- **Causa (visto no estudo, medida):** `core/filtros.escolher_algoritmo_automatico` mede a espessura do traço sem
  conferir se há tinta; p. 22 (cinza 249 a 255) → Otsu, 10,7% preto; Sauvola 0%. Função única (tela, cartões, PDF).
- **Plano:** antes de medir o traço, página sem contraste de tinta (limite a medir no gabarito) fica no Sauvola. Teste
  de reversão com página sintética. Não pode mudar: Graduale/Palatino (gótica grossa continua em Otsu): medir.
- **Aviso:** já existe ("Parece em branco", D-271) e acertou. **IA para avisos:** possível dentro do §3 (rede que só
  classifica); o programa já usa o leitor de layout; precisa de páginas ensinadas (as escolhas gravadas no histórico de
  ações dão um começo), treino e medida; tamanho da Fase 7. Sugestão: Lista de espera.

### lu-13 (D-690) — opção 3
- **Passo 1:** o aviso nasce na conta que decide pintura × traço (`core/filtros._tipos_das_zonas`), quando a zona foi
  tratada como traço e a decisão ficou perto da linha (muito cinza médio que o 1 bit apaga). Entra no motor dos avisos
  (sino, faixa, "Para revisar", "Antes de processar") com o botão "Gravuras em tons de cinza" (marca a caixinha da
  D-588 na página ou nas do "Aplicar em"). Nada muda sozinho.
- **Passo 2:** consertar `_tipos_das_zonas` para a pintura clara de pincel cair em "pintura"; medir nas gravuras de traço
  (Valadés, Siebmacher, Escola). Quando entrar, o aviso aparece menos.
- **Visto no print:** mesmo com a caixinha, pedaços do céu e do mar da p. 8 saem brancos — causa do lu-1.

---

## Respostas para a Central

Uma por item, no formato do §11.13. Prints: "novo" = desta tarefa (pasta
`D:\programas\EditorImpressao\.claude\worktrees\causas-lusiadas\relatorios\causas-lusiadas-2026-11-17\prints\`);
"do estudo" = de 14/11 (pasta
`D:\programas\EditorImpressao\.claude\worktrees\lusiadas-provas\relatorios\lusiadas-provas-2026-11-14\prints\`).

### lu-1 — Remendos na pintura (página 14)
**Do que se trata.** É a página 14 do Lusíadas, a pintura dos homens de chapéu. No PDF, a nuca do homem da frente e o
casaco do da direita saem diferentes do resto da pintura.

**O que acontece hoje.** Antes de passar o filtro, o programa separa a página em três: pintura, letra e papel. Quem
acha a pintura é a parte que veio do ScanTailor. Nesta página ela deixou de fora as partes mais escuras e lisas: a
nuca e o casaco. Depois disso, o programa chama de "letra" toda tinta que sobrou fora da pintura, sem conferir se
aquilo parece escrita. E cada filtro trata a "letra" do jeito da letra.

**Sua dúvida: "porque esses pedaços brancos estavam aparecendo também no melhorar e no magico pro".** Porque os três
filtros usam a mesma separação. No Preto e branco, o pedaço vira preto e branco duro. No Melhorar e no Mágico pro, vira
um cinza desbotado, com pontinhos brancos na beirada: o filtro acha que entre as "letras" é papel e pinta de branco.
Vi isso rodando nos três filtros, na mesma página (print novo `lu1-remendos-nos-tres-filtros.jpg`).

**Sua dúvida: "e também apareceram em outros livros, como no Gradus primus".** No Gradus é a mesma família, por outra
porta. Lá o programa leu "ÓNAI" (de "PAULO RÓNAI") como texto, e o texto ganhou da capa: abriu uma caixa. O branco
dentro da caixa vem de um passo do Preto e branco feito para tirar a sombra da mão em foto de celular, que confunde o
azul liso com sombra. Isso foi estudado em 13/11 (print
`D:\programas\EditorImpressao\.claude\worktrees\quadrados-capa\relatorios\quadrados-capa-2026-11-13\imagens\3-de-onde-vem-o-buraco.png`).
Os quadrados brancos do Melhorar e do Mágico pro no *Na escola de Jesus* eram outra causa, já consertada e testada por
você em 13/11 ("funcionando").

**Defeito ou escolha.** Defeito do programa. Não é escolha sua nem do Kaique.

**O que vem agora.** O conserto fica num lugar só, na separação: o pedaço de tinta que encosta na pintura e não tem
cara de escrita passa a ser pintura. Medi hoje: os dois pedaços da página 14 e o mar da página 8 não têm cara de
escrita; os parágrafos da página 2 têm. Antes de entrar, isso é medido nos outros livros (legendas da Pesel, pauta do
Graduale). Vale sozinho na tela, nas figurinhas e no PDF, nos três filtros, no Automático e à mão. O que você marca à
mão não muda. A caixa do "ÓNAI" no Gradus espera a sua resposta à pergunta do título escrito na capa colorida, de
13/11. Situação: você já disse "pode consertar"; espera a vez na fila.

(D-678, D-700)

### lu-2 — Números que não batem ("de 134" e o sino)
**Do que se trata.** O "página 132 de 134" do Automático e da barra de baixo, e o sino (o número de páginas com aviso,
no alto da coluna da direita).

**O que acontece hoje.** O programa conta "quantas páginas tem o livro" em vários lugares, com duas contas diferentes.
A barra de baixo, o Automático e o cartão da tela inicial contam a lista inteira, com a página tirada do livro. A
janela de salvar e o PDF contam só as que vão sair.

**Sua dúvida: "lembrando que eu não lembro a diferença entre as duas".** Folha é cada imagem do PDF que entra, como o
scanner viu (muitas vezes o livro aberto, com duas páginas). Página é cada página do livro que sai: uma folha dividida
vira duas páginas.

**Sua dúvida: "o motor de contagem deveria valer para todo o programa e não fazer uma conta em cada lugar".** Você tem
razão: é conta repetida. Para os avisos isso já foi feito (um número só, desde 27/10). Para as páginas, não: são duas
contas para a mesma pergunta. O conserto cria uma conta só, "quantas páginas o livro vai ter e que número cada uma
tem", e todas as telas passam a usá-la.

**Sua dúvida: "Mudou sozinho porque ele procurou e achou mais defeitos?"** Quase isso. Um dos avisos ("as contas do
endireitar discordam") é medido duas vezes: na abertura, numa imagem pequena, e de novo, por trás, quando você passa
pela página e ela é desenhada no tamanho do PDF. Às vezes a segunda medida discorda da primeira, e o aviso aparece ou
some. Não é defeito novo na página: é a mesma coisa medida de dois jeitos. Visto no teste de 14/11: 25 parado por dois
minutos, 26 depois de andar pelas páginas (print do estudo `erro2-numeros.jpg`).

**Defeito ou escolha.** Defeito do programa.

**O que vem agora.** A conta de páginas vira uma só. O aviso do endireitar passa a valer só pela medida do tamanho do
PDF; enquanto ela não terminou, o sino diz que ainda está medindo, em vez de mudar calado. Esse "ainda medindo" é
coisa nova na tela: vem com print para você ver antes. Nada do que já funciona muda. Situação: na fila.

(D-679, D-285)

### lu-3 — A miniatura não fica branca depois de "deixar em branco"
**Do que se trata.** A tira de miniaturas embaixo da área de trabalho e o botão "deixar em branco" (painel
Propriedades, em "Esta página"; também no Delete e no menu Página).

**O que acontece hoje.** A página grande fica branca; a miniatura continua com o título (print do estudo
`erro3-miniatura-branco.jpg`).

**Sua dúvida: "Quero saber porque isso acontece."** A pergunta "esta página sai em branco?" está escrita em três
lugares do programa, cada um do seu jeito. A do PDF olha a página "deixada em branco" e a página branca acrescentada à
mão. A da miniatura e a da grade "Todas as páginas" olham só a acrescentada à mão. Quem fez a página acrescentada (em
04/11) ensinou a miniatura só para ela, e a "deixada em branco", mais antiga, ficou de fora.

**Defeito ou escolha.** Defeito do programa.

**O que vem agora.** Uma pergunta só, num lugar só, que o PDF, a miniatura e a grade usam. Vale para todos os jeitos de
deixar em branco (botão, Delete, menu, botão direito, grade, aviso "Parece em branco") e para o Ctrl+Z. Nada do que já
funciona muda. Situação: na fila.

(D-680, D-649)

### lu-4 — Textos cortados na barra de baixo (não é urgente)
**Do que se trata.** A barra do pé da área de trabalho ("página N de M", "Uma página", "Duas lado a lado", "antes /
depois", "marcações", zoom).

**O que acontece hoje.** Na janela do tamanho do notebook do Kaique, com o painel Propriedades aberto, sai "uas lado a
lad" (print do estudo `erro4-barra-cortada.jpg`).

**Por que acontece.** A barra é uma fila só de botões, com o texto de cada um fixo. A janela não pode ficar mais larga
que a tela (isso é de propósito). Com o painel aberto sobra menos lugar que a soma dos textos, e o Windows corta. Falta
uma regra de "o que encolhe primeiro". A tela inicial já tem esse jeito ("1 de 134" em vez de "página 1 de 134"); a
barra de baixo não.

**Defeito ou escolha.** Defeito de tela. Os botões funcionam e o PDF não muda.

**O que vem agora.** Uma regra só para a barra inteira: com pouco lugar, os textos ficam curtos. Os textos curtos vêm
com print para você escolher antes. Situação: fim da fila, como você disse.

(D-681)

### lu-5 — A página que sai deitada no arquivo para imprimir
**Do que se trata.** O arquivo de "montar para imprimir em A4" (na tela "Ficou pronto!"), com duas páginas de cada
lado da folha.

**O que acontece hoje.** A página 3 saiu deitada (print do estudo `erro5-pagina-deitada.jpg`).

**Sua dúvida: "Quero saber porque saiu deitado? o programa aplicou o girar?"** Não foi a ferramenta Girar. Foi a
caixinha "Rotação automática" da janela "Montar para imprimir", que vem marcada (o nome é o do UPDF). Ela gira toda
página mais larga que alta para caber na metade da folha. A página 3 ficou larga porque o Dividir cortou a folha 2
fora do meio: numa folha com só uma página impressa, ele não acha a dobra. O programa escreve o aviso "Página 3: era
deitada e foi girada", mas só depois de gravar, lá embaixo.

**Sua dúvida: "é um defeito do programa ou do agente que fez esses testes?"** Do programa. O agente fez o caminho do
Kaique: na janela "Antes de processar" apertou "continuar assim mesmo", e montou com tudo de fábrica. Não tocou no
Girar. O teste do Kaique de 06/11 deu o mesmo, na folha 7.

**Defeito ou escolha.** Defeito, em duas partes: o corte fora do meio (o programa avisa "Não tenho certeza de onde
cortar", mas segue) e o giro escondido.

**O que vem agora.** O aviso do giro passa a aparecer antes de gravar, junto da folha na prévia da janela, pela mesma
conta do gravar. O que fazer com o corte da folha em dúvida (usar a linha das folhas vizinhas, ou só avisar mais
forte) é pergunta para você, separada. A caixinha "Rotação automática" continua, e você pode desmarcar. Situação: na
fila.

(D-682)

### lu-7 — Os contornos laranja com a Mão, e as manchas na pintura
**Do que se trata.** Os contornos laranja em volta do texto e da pintura, com a ferramenta Mão (a mãozinha, a última da
coluna da esquerda).

**O que acontece hoje.** Você escolheu a opção 2: o botão "marcações" passa a mandar também no laranja.

**Sua dúvida: "Quero entender porque este bug está acontecendo."** Existem dois interruptores para a mesma coisa. O
botão "marcações" manda nas cores. O laranja tem outro, que liga sozinho em toda página com aviso, seja qual for a
ferramenta. Logo depois do Automático quase toda página tem aviso, então quase toda fica com laranja.

**Sua dúvida: "onde aparece essas marcações, vemos claramente alguns defeitos nas gravuras, vemos manchas brancas".**
É isso mesmo. O laranja desenha onde o programa separou a pintura do resto. Dentro da figura, ele cerca justamente os
pedaços que o programa não tomou por pintura, e esses pedaços saem remendados no PDF (print novo
`lu7-laranja-mostra-o-defeito.jpg`). O laranja não cria a mancha: mostra onde ela está. A causa é a do erro da página
14, e o conserto é o mesmo.

**Defeito ou escolha.** Os dois interruptores são defeito de tela. As manchas são defeito do programa (o da página 14).

**O que vem agora.** Um botão só para tudo o que é marcação: desligado, nenhuma cor e nenhum contorno. Ele continua
acendendo sozinho nas ferramentas de marcar e apagando no Zoom e na Mão, como você decidiu em 29/10. Situação: na fila.

(D-684, D-237, D-584)

### lu-8 — O aviso "será substituído" na janela de salvar
**Do que se trata.** A janela "Onde salvar o livro pronto", que abre em "Confirmar e processar".

**O que acontece hoje.** Trocando o nome para um que não existe, a faixa continua dizendo que o arquivo antigo será
substituído (print do estudo `erro8-aviso-velho-salvar.jpg`).

**Sua dúvida: "Quero saber porque esse problema acontece."** A janela confere "esse arquivo já existe?" em dois
lugares, cada um com o seu texto. O aviso pequeno, embaixo do nome, é refeito a cada letra. A faixa grande só fica
sabendo quando a pasta muda, porque o campo do nome nunca avisa a janela que mudou. E o teste dessa faixa não digita o
nome: manda a janela se conferir por dentro, por isso passou.

**Defeito ou escolha.** Defeito do programa. Nada é apagado sem perguntar.

**O que vem agora.** O campo do nome passa a avisar a janela, como a pasta já avisa. A conferência fica num lugar só,
com um aviso só. Hoje os dois dizem coisas diferentes ("eu pergunto antes de substituir" e "se continuar, ele será
substituído"); qual texto fica vem como pergunta, com print. A prova nova digita no campo, como o Kaique. Situação: na
fila.

(D-685)

### lu-9 — Depois de "tirar do livro", a faixa diz "vai sair em Preto e branco"
**Do que se trata.** A faixa acima da tira de miniaturas, numa página tirada do livro.

**O que acontece hoje.** A miniatura diz "apagada" e a faixa diz "Esta página vai sair em Preto e branco" (print do
estudo `erro9-frase-depois-de-tirar.jpg`).

**Seu comentário: "Depois que tira uma pagina do livro, ela tem que sumir das miniaturas".** Você já decidiu isso em
31/10: "Somem da tira; um botão "4 tiradas do livro" no começo da tira". Essa decisão ainda não foi construída; por
isso a página tirada continua na tira. A frase errada é a mesma falta: cada parte da tela decide sozinha em que
situação a página está, e a faixa não aprendeu a "tirada".

**Defeito ou escolha.** Defeito: falta construir o que você já decidiu.

**O que vem agora.** Uma conta só diz a situação da página (tirada, em branco, com aviso, conferida); a tira, a faixa,
a grade e os botões usam a mesma. Com ela vem a sua decisão de 31/10: a página tirada some da tira, e um botão no
começo da tira ("1 tirada do livro") a traz de volta, com o conteúdo dela. O arquivo original nunca muda. Isso também
acerta o "de 134". Situação: na fila, junto com o erro dos números e o da miniatura em branco.

(D-686, D-595, D-650)

### lu-10 — Códigos como "(G2)" na tela
**Do que se trata.** Na janela do Automático, etapa Dividir: "só quando esta etapa roda (G2)"; e mais dois códigos em
balões do mouse, na mesma janela (print do estudo `erro10-codigo-g2.jpg`).

**Por que aconteceu.** Os três entraram juntos em 26/10. O agente pôs o número da sua decisão dentro do texto da tela,
quando devia pôr no comentário do código, que só o programador vê. Nenhuma prova lê os textos da tela, e a regra
"nenhuma palavra de dentro" (13/11) fala do que se escreve para você, não do que o programa mostra. Conferi hoje: são
só esses três.

**Sua dúvida: "tem que rever as regras dos agentes para que eles não cometam mais esse erro".** Proposta de regra, para
os agentes que escrevem código e para quem confere: "Todo texto que o Kaique pode ver (botão, rótulo, balão, aviso,
título de janela, mensagem) usa só palavras da tela, do livro e da página. Nunca leva número de decisão, nome de
pergunta, item ou etapa do plano, nome de agente, de arquivo ou de função. O número da decisão vai no comentário do
código, nunca dentro do texto. Antes de entregar, rode a prova que lê todos os textos da tela; se ela acusar, troque o
texto, nunca a prova. Quem confere procura código de propósito."

**Defeito ou escolha.** Defeito.

**O que você escolhe.** Se essa regra pode entrar como está. Sugestão: sim. A prova automática entra junto com o
conserto, que está na fila.

(D-687)

### lu-11 — A lista de etapas do Automático volta para o topo
**Do que se trata.** A lista "Etapas, na ordem" do Automático (1 Dividir ... 7 Montar cadernos), na janela grande e no
painel da direita.

**O que acontece hoje.** Marcando "6 Margens iguais" com a lista rolada, ela pula para o topo (print do estudo
`erro11-lista-volta-ao-topo.jpg`).

**Sua dúvida: "quero saber o motivo desse erro, pois isso é um gambiarra né."** Não é gambiarra no sentido de regra
repetida: a lista é uma só, e o painel e a janela usam a mesma. É um atalho de quem escreveu: a cada mudança, a lista
inteira é apagada e montada de novo, porque é mais fácil do que mudar só a linha que mudou. Montada de novo, volta
para o alto. Remendo seria guardar a posição e devolver depois; o certo é mudar só a linha que mudou.

**Defeito ou escolha.** Defeito.

**O que vem agora.** A lista passa a mudar só a caixinha e o texto da linha mexida, e fica onde estava. Vale no painel e
na janela, em todas as caixinhas e opções. Situação: na fila.

(D-688)

### au-d-528 — As marcações ao dividir uma folha
**Do que se trata.** Na ferramenta Dividir e no Automático: ao dividir uma folha, o que você marcou à mão na folha
inteira vai para a página onde está.

**O que conferi.** A regra está num lugar só: o "dividir esta" e o Automático usam a mesma conta, e as provas cobram os
dois. Nisso não há gambiarra.

**O que achei.**
- Um caminho esquecido, visto rodando: se a folha foi dividida, depois juntada ("não dividir esta"), e você marca na
  folha juntada, ao dividir de novo essa marcação some, sem aviso. O programa tem duas listas do que passa da folha
  inteira para as páginas: uma na primeira divisão, outra quando divide de novo. A segunda não leva as marcações.
- Uma conta de reserva: quando a página nunca foi desenhada, o programa reparte a marcação por uma conta aproximada,
  diferente da normal. Pela tela isso não deve acontecer, mas é uma segunda conta para a mesma coisa.
- Na mesma família, já conhecido desde 10/11: o Automático deixa a folha inteira de um jeito, e o "não dividir esta",
  de outro.
- Uma regra para você saber, não é defeito: a marcação que atravessa a linha do meio vai inteira para o lado onde está
  o centro dela.

**O que você escolhe.** Se o conserto do caminho esquecido entra na fila: uma lista só do que passa para as páginas,
nos dois jeitos de dividir. Sugestão: sim. Nada do que já funciona muda. Sem print: é conferência do código, e o
caminho esquecido foi provado por um teste rodado hoje.

(D-528, D-498)

### lu-12 — A página 22, quase em branco, sai suja
**Do que se trata.** A página 22, o verso sem nada impresso, que sai no PDF com tracinhos pretos (print do estudo
`erro12-pagina-suja-p22.jpg`).

**Sua dúvida: "Gostaria de saber como seria esse conserto".** O Preto e branco escolhe sozinho, página por página, um
jeito de decidir o que é tinta. Para escolher, mede a grossura das letras. Numa página sem letra, ele mede as
manchinhas do papel e escolhe o jeito de letra grossa, que sempre acha "tinta". O conserto é uma conferência antes
disso: se a página não tem tinta de verdade (quase nenhuma diferença entre o mais claro e o mais escuro), fica no jeito
de letra fina, que a deixa branca. É uma conta só, usada na tela, nos cartões e no PDF. Nas páginas com letra nada
muda; isso é medido nos livros de letra grossa (Graduale, Palatino) antes de entrar.

**Sua dúvida: "por enquanto poderia ter só um aviso né?"** O aviso já existe e acertou: o programa marcou essa página
com "Parece em branco", com o botão "deixar em branco". O problema é que, se o Kaique não apertar, ela sai suja. Por
isso a sugestão é o conserto, e o aviso continua.

**Sua dúvida: "Seria possivel criar uma IA só para parte de avisos do programa?"** Sim, dentro da regra do programa:
uma rede que só aponta, nunca desenha. Ela olharia cada página e diria "em branco", "texto", "pintura" ou "desenho de
traço", e o programa poria o aviso. O programa já usa uma rede assim para achar onde está o texto. Para ensinar,
servem as escolhas que você e o Kaique já fazem (o "está certo", o "deixar em branco"), que o programa guarda. É um
trabalho do tamanho do treino dos leitores de texto (a última fase do plano). Sugestão: anotar como ideia, para depois.

**Defeito ou escolha.** Defeito do programa.

**O que você escolhe.** Pode consertar como descrito? Sugestão: sim. E a ideia da IA dos avisos vai para a lista de
ideias? Sugestão: sim.

(D-689, D-271)

### lu-13 — A opção 3 da página 8 (a pintura das bandeiras)
**Do que se trata.** A página 8: o programa achou a pintura, mas a tratou como desenho de traço, e no PDF só sobram
riscos (print do estudo `erro13-pintura-p8.jpg`).

**Sua dúvida: "explique melhor como vai funcionar a opção 3."** São dois passos, um depois do outro (print novo
`lu13-opcao-3-passo-1.jpg`).
- **Passo 1, o aviso.** Quando o programa trata uma pintura como desenho de traço e estava em dúvida, a página ganha um
  aviso, como os outros: aparece no sino, na faixa da página e no "Antes de processar". O aviso diz que a pintura vai
  sair só com as linhas e tem o botão "Gravuras em tons de cinza". Um clique do Kaique e a página sai com a pintura em
  cinza (faixa verde do print). Com o "Aplicar em", vale também para outras páginas. Nada muda sozinho, e as outras
  páginas ficam como estão. A caixinha já existe hoje; o que é novo é o aviso na hora certa.
- **Passo 2, a conta.** Depois, o programa aprende a separar melhor pintura de pincel de desenho de traço, para a página
  8 sair em cinza sem clique. Isso é medido antes nas gravuras de traço dos livros antigos, que devem continuar em preto
  e branco. Quando entrar, o aviso do passo 1 aparece menos.

Um ponto que o print mostra: mesmo com a caixinha, pedaços do céu e do mar saem brancos. É a mesma causa dos remendos
da página 14, e o conserto de lá resolve isso também.

**O que você escolhe.** Opção 3 assim, começando pelo aviso? Sugestão: sim. No passo 1, nada do que já funciona muda;
no passo 2, as gravuras de traço são conferidas de novo.

(D-690, D-588)

---

## Visto rodando × lido no código
- **Visto rodando hoje:** lu-1 (decomposição da p. 14 e da p. 8, os três filtros), lu-7 (o laranja cerca os remendos:
  print da tela do estudo + PDF), au-d-528 achado 1 (sonda), códigos na tela (varredura na versão de hoje).
- **Visto rodando no estudo de 14/11 (não refeito):** lu-2, lu-3, lu-4, lu-5, lu-8, lu-9, lu-11, lu-12 (medida), lu-13
  (com a caixinha); Gradus (estudo de 13/11).
- **Lido no código (dedução):** as funções e os caminhos de cada item, au-d-528 achados 2 e 3, os planos.

## Ressalvas
- Nenhum plano foi testado como conserto (tarefa só de causa). As medidas do lu-1 são de poucas páginas de um livro.
- Os prints novos usam a conta do programa sem janela (a mesma da tela e do PDF, D-649) e, no lu-7, a tela de verdade do
  estudo de 14/11 (versão `c7e34fd8`; a de hoje é `a9d81030`). Não rodei a janela hoje.
- Criei `D:\agente_temp_testes\causas-lusiadas` (pasta de teste da sonda, fora do projeto): não apaguei (regra).
- Testes do programa: só a sonda temporária (apagada). Sem rodada no GitHub: nenhuma linha do programa mudou.

## Ideias para a Lista de espera
- "IA só para avisos" (rede que só classifica a página), com as palavras dele de 17/11.

## Bugs para a Lista de bugs
- 17/11/2026, Dividir: a marcação feita na página juntada some ao "dividir esta" de novo (sonda acima).
- 17/11/2026, `atualizacao.py`: números de decisão em textos de passos e de registro (conferir se algum chega à tela).
