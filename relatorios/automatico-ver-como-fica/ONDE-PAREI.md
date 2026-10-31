# ONDE PAREI — Automático: ver como fica (D-577)

Ramo `automatico-ver-como-fica-2026-10-29` (saiu de `obra-2026-10-26`), cópia
`.claude/worktrees/auto-ver`. Construtor; entrega à gerente.

## Decisões que esta tarefa precisa cumprir

- **D-577** (29/10/2026). Samuel, sessão 2 dos testes, 2-11 (28/10): "eu queria poder nessa etapa do automatico
  poder ver como iria ficar conforme as opções que eu fosse escolhendo." Pergunta: "A página da direita passa a
  mostrar o antes e depois, com a linha que você arrasta. O lado do "depois" muda a cada opção que você marca ou
  desmarca. [...] Pode ser assim?" → "sim, mas coloca uma bolinha de carregamento como fez na area de trabalho,
  porque as vezes vai demorar para processar né?" Só mostra: não muda o projeto nem o histórico. Substitui a D-486.
- **D-486** (27/10, escolha da gerente): a página da direita era a original (folhear, com zoom). Sai; o folhear e o
  zoom ficam (pedido da gerente, item 4).
- **D-002**, rodada 2 nº 5: "Na janela, ver a página ao lado, folhear e dar zoom." (continua valendo).
- **D-064** (a bolinha de carregamento, `ui/widgets/bolinha.py`).
- CLAUDE.md §3: uma página por vez na memória; interface nunca congela.

## Andamento

- [x] Li CLAUDE.md (§3, §10, §11), implementador.md, memoria/INDICE.md, D-577/D-486.
- [x] core: prévia de uma página pelo mesmo caminho do rodar (core/automatico.py: copia_para_a_previa,
      antes_da_pagina, depois_da_pagina, paginas_depois, como_sai_na_tela)
- [x] tarefa de fundo (ui/tarefas.py: TarefaPreviaDoAutomatico)
- [x] coluna da direita da janela grande (ui/automatico.py: PaginaAntesEDepois, VistaAntesDepoisComZoom)
- [x] provas (tests/test_decisoes_automatico_ver_como_fica.py, 10 testes; commit 55a816d)
- [x] testes que já tocam ui/automatico.py, um por vez
- [x] prints offscreen (prints_d577.py nesta pasta; livro copiado em _tmp/livro)

## Como cumpri cada uma

- **D-577, antes e depois com a linha:** a coluna da direita é `PaginaAntesEDepois` (ui/automatico.py), com a
  `VistaAntesDepois` da área de trabalho (a linha que se arrasta). Prova: `test_d577_a_pagina_da_direita_mostra_o_antes_e_depois_com_a_linha`;
  prints 1, 3 e 4.
- **D-577, o depois muda a cada opção:** `test_d577_marcar_uma_opcao_muda_o_depois_e_desmarcar_volta`,
  `test_d577_cortar_e_dividir_mudam_o_tamanho_do_depois`, `test_d577_sem_etapa_marcada_o_depois_e_o_antes`.
- **D-577, a bolinha:** `BolinhaDeCarregamento` ao lado do título; `test_d577_a_bolinha_gira_enquanto_calcula_e_some_no_fim`; print 2.
- **D-577, só mostra:** cópia do projeto; `test_d577_mexer_e_fechar_deixa_o_livro_o_desfazer_e_o_disco_iguais`,
  `test_d577_core_a_previa_nao_toca_no_projeto` (as duas falham se a prévia usar o projeto aberto: conferido).
- **Mesmo caminho do rodar:** `test_d577_o_depois_bate_com_o_rodar_de_verdade` (torta P&B 0,08% dos pontos; dividir 0%).
- **Só o último pedido vale:** `test_d577_resultado_velho_nunca_cobre_o_novo` (falha sem a conferência da chave: conferido).
- **D-486 saiu / D-002 folhear e zoom:** mesmo teste da linha (sem FolhearPDF) e `test_d577_folhear_e_zoom_continuam`; P-187.

---

# Conserto depois do teste do Samuel (30/10/2026)

Ramo atualizado com `obra-2026-10-26` (20a07c7). Livro de teste: cópia do projeto *Na escola de Jesus*
(`_tmp/localapp_30`, refeita a cada rodada pelo `prints_d577_30-10.py`), capa = página 1, mexida à mão no filtro.

## Decisões que esta tarefa precisa cumprir

- **D-577, 30/10** (Livro, linha D-577): "na previa ali, ele mostra a mudança em todas as paginas mas só muda as que
  nós autorizarmos ( no caso as que foram mexidas a mão), segundo tem que dar para ver na previa em tela grande e poder
  dar zoom na previa em tela grande" · "quarta coisa, quando você mexe no antes e depois, ele começa a mostrar o antes
  de qual pagina, parece que ele troca o antes conforme se troca os perfis dos filtros." No Livro: "a prévia mostra a
  mudança também nas páginas mexidas à mão (quem decide pular é a pergunta da D-004 ao "Rodar"); o "tela cheia" mostra
  o mesmo antes e depois, grande, com zoom."
- **D-004**: "Automático em livro já mexido à mão: o programa pergunta se quer pular as páginas mexidas." (o "Rodar"
  não muda).
- **D-002**, rodada 2 nº 5: "Na janela, ver a página ao lado, folhear e dar zoom." (o tela cheia continua folheando).
- **CLAUDE.md §11 regra 7**: só o que ele mandou.

## Andamento (30/10)

- [x] Coisa 1: a prévia não pula as mexidas (`PaginaAntesEDepois._calcular_agora` usa `estado.pedido(pular_mexidas=False)`)
- [x] Coisa 2: `TelaCheiaDoAntesEDepois` (ui/automatico.py) no lugar da `TelaCheiaDoPDF`
- [x] Coisa 3: investigada; não se reproduziu (abaixo)
- [x] Quadro laranja do a-08: procurado (abaixo)
- [x] 3 provas novas (commit d301673); as 3 falharam no código de antes
- [x] prints (`prints_d577_30-10.py antes|depois`)
- [x] testes que tocam ui/automatico.py, um por vez no PC: 18 arquivos, todos passaram (o da D-577: 14 de 14)
- [x] GitHub, rodada 41086238065: passou. Na 1ª vez, a parte 2 falhou num teste de tempo
      (`test_d148_desfazer_o_automatico_devolve_o_so_as_letras_do_livro`: "o projeto.json com o 'Só as letras'
      desfeito" não chegou em 15 s); a mesma parte rodada de novo passou, e no PC ele passou 4 de 4 vezes. Esse teste
      não abre página mexida nem o tela cheia.

## Como cumpri cada uma

- **Coisa 1, a prévia mostra a mudança na página mexida à mão:** `test_d577_a_previa_mostra_a_mudanca_tambem_na_pagina_mexida_a_mao`
  (no código de antes: papel do depois 170, igual ao antes). Na capa do livro de teste: antes do conserto o depois era o
  mesmo nos 5 filtros (md5 48c74928); depois, cada filtro dá um depois diferente. Prints `1-antes-do-conserto-*` e
  `1-depois-do-conserto-*`.
- **D-004 não mudou:** o mesmo teste confere que `estado.pedido()` continua pulando de fábrica e que o "Rodar" pergunta.
- **Coisa 2, tela cheia com o antes e depois e zoom:** `test_d577_tela_cheia_mostra_o_antes_e_depois_da_previa_com_zoom_e_folhear`
  (as mesmas imagens da janela, –/+/ajustar à tela, < > e setas, Esc; a TelaCheiaDoPDF não abre mais). Prints
  `2-antes-do-conserto-tela-cheia-folha-crua.png`, `2-depois-do-conserto-tela-cheia-antes-e-depois.png`,
  `2-depois-do-conserto-tela-cheia-com-zoom.png`, `2-depois-do-conserto-tela-cheia-folheou-pagina-2.png`.
  Reaproveitado: a `VistaAntesDepoisComZoom` (a vista da página da direita; a tela cheia dos filtros e o "antes / depois"
  da área de trabalho não têm zoom) e o jeito da `TelaCheiaDoPDF` (maximizada, < >, fechar).
- **Coisa 3, o antes não muda:** `test_d577_o_antes_nao_muda_ao_trocar_o_filtro_nem_na_pagina_mexida` (guarda; a parte
  do antes passa também no código de antes). Print `3-depois-do-conserto-o-antes-fica-o-mesmo-magico-pro.png`.

## Coisa 3: o que foi tentado (não reproduziu)

- Capa do livro de teste, só "Limpar a folha", Preto e branco + "Só as letras", trocando Preto e branco, Mágico pro,
  Melhorar, Original e de novo Preto e branco, e trocas rápidas sem esperar; com o código de antes (pulando) e com o
  conserto: o antes guardado é o mesmo ponto por ponto (md5 c890e86b) e a vista mostra sempre ele.
- Hipóteses da gerente: (a) a vista trocar os lados ou mostrar o depois velho: não; a vista só mostra o antes sozinho
  (sem a linha) enquanto o depois não chegou. (b) o antes recalculado na cópia já mexida: não; ele é desenhado numa cópia
  à parte, antes de aplicar o pedido, e uma vez só por página. (c) tamanhos diferentes: na capa, só com o Limpar, os
  dois têm 1800 x 1317.
- Único achado: ao folhear e voltar para a capa, o antes é desenhado de novo e sai 0,8% dos pontos diferente (não se
  vê; a primeira vez a página é desenhada na resolução do PDF e reduzida, as outras direto na da prévia). Não depende
  do filtro escolhido.
- O que pode ter parecido: no código de antes, na capa, o antes e o depois eram a MESMA imagem em 1 bit (a prévia pulava
  a capa), e o "tela cheia" mostrava a folha colorida crua e, se ele folheasse lá, a janela voltava em outra página. As
  duas coisas saíram com os consertos 1 e 2.

## Quadro laranja e preto do a-08

- Não veio do nosso código, pelo que dá para ver: com o tela cheia de antes aberto, as únicas janelas do programa são a
  janela grande e a "Folhear o livro" (lista em `prints_d577_30-10.py antes`); o programa não cria janela solta com
  imagem (nenhuma dica com imagem, nenhuma janela sem moldura). O livro não tem página laranja e preta (procurado nas
  199). Pela forma (cantos redondos, sombra, por cima da barra de título), parece janela de outro programa. Ressalva: o
  modo sem tela do teste não mostra janelas de outros programas.

## Perguntas para o Samuel

1. **(coisa 3)** Depois destes consertos, o "antes" ainda muda quando você troca o filtro? Se mudar, mande um print e
   diga o que fez antes (folheou? abriu o tela cheia? fechou e abriu a janela? rodou?). Não consegui fazer acontecer.
2. **(capa do teste)** Na capa, "Preto e branco + Só as letras" vai continuar mostrando a capa toda em preto e branco
   duro: a capa tem as opções dela mesma do teste da D-588 ("Só as letras" desligado nela, Otsu, força 0), e o "Rodar"
   (com "Rodar nelas também") troca só o filtro e mantém essas opções da página. A prévia mostra o mesmo que o Rodar
   faria. Está certo assim, ou o "Rodar nelas também" deve devolver a página às opções do livro?

---

# 2ª rodada: depois do 2º teste do Samuel (30/10, 13:33)

Ramo atualizado com `obra-2026-10-26` (3f169d7). Pedido da gerente (A e B), com a correção do Samuel para a A.

## Decisões que esta rodada precisa cumprir

- **D-577, 30/10, depois do 2º teste** (prints a-12, a-13 e a-14): "está bem confuso, na verdade, porque eu já tinha
  colocado um filtro antes, eu acho que o antes deveria ser sempre o original e o filtro depois o que escolhemos, ai se
  quiser comparar faz isso na tela cheia." · "na tela cheia vai ter um botão de comparação , ai vão aparecer duas telas
  para comparar" · "nessa vai ter o filtro que estava antes, seja ele original ou que foi aplicado e o filtro que está
  selecionado no momento" · e, no lugar de "mostra já cortada e endireitada se tiver sido feito isso.": "o antes é sem
  filtro e sem cortar sem nada, o depois na tela de atualizar que aplica os filtros de endireitar cortar ou fazer
  qualquer outra coisa para ver como iria ficar."
- Os rótulos "antes" e "depois" do visor não mudam (ele não respondeu a essa sugestão).
- CLAUDE.md §11 regra 7: só o que ele mandou (sem seletor de filtro no comparar).

## Andamento

- [x] A: o antes é a folha crua, como veio do PDF (`core/automatico.antes_da_pagina` = `pdf_io.pagina_para_array`).
      A página como está no livro, com o filtro dela, virou `pagina_como_esta` (usada só no comparar).
- [x] B: botão "comparar" na tela cheia (`TelaCheiaDoAntesEDepois`): duas telas (`Visualizador`, como o "Ver de perto"),
      à esquerda "como está no livro: <filtro>", à direita "depois: <filtro>"; zoom e posição juntos (botões, roda e
      arrastar); folhear continua; apertar de novo volta à linha. A página como está no livro só é desenhada com o
      comparar ligado (um desenho a mais por página só aí; o folhear de sempre não fica mais lento).
- [x] Provas novas: `test_d577_o_antes_e_a_folha_crua_sem_nada`, `test_d577_comparar_na_tela_cheia_mostra_o_livro_e_o_depois_lado_a_lado`
      (as duas falharam no código de antes, 3f169d7: "o antes não é a folha crua (tamanho (655, 471), crua (1008, 720, 3))"
      e "a tela cheia não tem o botão \"comparar\""). Arquivo da D-577: 16 de 16.
- [x] Prints: `4-antes-cru-depois-preto-e-branco.png`, `5-tela-cheia-antes-cru-depois-preto-e-branco.png`,
      `5-tela-cheia-comparar-preto-e-branco.png`, `5-tela-cheia-comparar-magico-pro.png`,
      `5-tela-cheia-comparar-magico-pro-com-zoom.png` (script `prints_d577_30-10b.py`).

## Provas antigas que mudaram (e por quê)

Nenhuma prova antiga falhou: o livro sintético das provas está todo em Original, sem corte, então a folha crua é igual
à "página como está". Mudei só o texto que dizia "o antes é a página como está no livro":
- `test_d577_sem_etapa_marcada_o_depois_e_o_antes`: docstring diz que ali o antes sem nada é a própria página.
- `test_d577_marcar_uma_opcao_muda_o_depois_e_desmarcar_volta`: a mensagem "no Original o depois tinha de ser a página
  como está" virou "... tinha de ser o antes".
- `test_d577_o_antes_nao_muda_ao_trocar_o_filtro_nem_na_pagina_mexida`: docstring diz o que o antes é agora.
- A dica (tooltip) do visor dizia "a página como está agora"; agora "a página como veio, sem nada".

## Perguntas para o Samuel (2ª rodada)

3. ~~Página de folha dividida~~ **respondida** (30/10, "pode", pela gerente): (1) "A folha já foi dividida: o antes
   mostra só a metade dela, crua, sem filtro e sem endireitar. O depois mostra essa mesma metade pronta." (2) "A folha
   ainda não foi dividida e 'Dividir folhas ao meio' está marcada: o antes mostra a folha inteira, crua. O depois mostra
   as duas metades prontas, uma ao lado da outra, como já faz hoje." (3) "[...] O antes continua sendo a folha inteira
   crua, porque é dela que as duas metades vão sair. Se ela desmarcar 'Dividir', o depois volta a ser a folha inteira
   pronta. Se a folha já tinha sido dividida antes, o antes mostra só a metade crua, com 'Dividir' marcado ou não."
   Feito em `core/automatico.antes_da_pagina`: a metade sai da folha crua pelo giro de 90 da folha (para saber para que
   lado ela fica de pé) e pela linha da divisão, mais nada. Provas: `test_d577_folha_ja_dividida_o_antes_e_so_a_metade_crua`
   (falhou no 1b5f947: o antes era a folha inteira, 1008 x 1440 em vez de 1008 x 720),
   `test_d577_folha_inteira_com_dividir_marcado_antes_inteiro_depois_duas_metades` e
   `test_d577_marcar_e_desmarcar_dividir_muda_so_o_depois` (estas duas já passavam: guardam o que já era assim).
   Ressalva: a folha inteira que veio deitada continua deitada no antes (sem giro); a metade usa o giro, senão a linha
   da divisão cairia no lugar errado.
4. (continua a pergunta 2 da rodada anterior) Na capa, "Preto e branco + Só as letras" ainda mostra a capa toda em preto e
   branco duro, porque a capa guarda opções dela mesma do teste da D-588; o Rodar faz o mesmo. Print
   `4-antes-cru-depois-preto-e-branco.png`.

## Testes da 2ª rodada

- PC, um arquivo por vez: os 18 arquivos que tocam o Automático passaram (no 2669603); depois da metade crua (72fbdc0),
  de novo `test_decisoes_automatico_ver_como_fica.py` (19 de 19), `test_decisoes_automatico.py`, `test_decisoes_dividir.py`
  e `test_dividir_na_tela.py`: todos passaram.
- GitHub: 41104087681 (2669603) e 41109208060 (72fbdc0) passaram, as duas depois de rodar de novo a parte 1. Nas duas, a
  1ª vez caiu no mesmo erro de tempo do `test_promessas.py`: `test_p083_jeitos_do_so_as_letras[rede]` (e, numa delas,
  o teste seguinte) acha no erros.log uma prévia da ÁREA DE TRABALHO (`ui/tarefas.py` linha 832, categoria "previa")
  que não achou o PDF do teste. Esse teste não abre o Automático; o `janela` do test_promessas espera as tarefas de fundo
  só 15 s. No PC o arquivo passou inteiro (262). Fica como ressalva: teste instável no GitHub, não do código da D-577.

---

# 3ª rodada: depois do 3º teste do Samuel (30/10, 16:30)

Ramo atualizado com a obra (db0a661). Prints dele a-15 a a-18.

## Decisões que esta rodada precisa cumprir

- **D-577, 3º teste:** "1- não consigo dar zoom com o mouse, usando o scrool" · "eu quero que a faixa seja de acordo com
  a direção do antes e depois, se ela está embaixo do depois ela está aparecendo o depois se está embaixo do antes ela
  está no antes." · "sim" a: "Linha toda à direita, embaixo de 'depois': a página inteira mostra o depois. Linha toda à
  esquerda, embaixo de 'antes': a página inteira mostra o antes. Linha no meio: à esquerda dela aparece o depois, e à
  direita aparece o antes. Hoje é o contrário." · "sim" a valer também no "antes / depois" da área de trabalho.
- Os rótulos não mudam de lugar; a linha abre onde abria (no meio). A 3ª coisa dele (opções de cada lado no comparar)
  NÃO foi começada (ainda em conversa).

## Como cumpri

- **Roda do mouse:** `VistaAntesDepoisComZoom.wheelEvent` (ui/automatico.py), com o `PASSO_DA_RODA` do Visualizador e o
  ponto debaixo do ponteiro parado; vale na página da direita e na tela cheia. As duas telas do "comparar" já eram
  `Visualizador` (já tinham a roda e andam juntas). Prova: `test_d577_a_roda_do_mouse_da_zoom_ancorado_no_ponteiro`
  (no db0a661: "página da direita: a roda não deu zoom (1.0)").
- **Lado da linha:** `VistaAntesDepois.paintEvent` (ui/widgets/filtros_tela_cheia.py): o antes por baixo, a página toda, e
  o depois por cima, da beirada esquerda até a linha. Prova: `test_d577_a_linha_mostra_o_lado_para_onde_vai` (no db0a661:
  "área de trabalho: linha toda à direita não mostra o depois inteiro"); `test_d577_o_antes_depois_da_area_de_trabalho_e_a_mesma_vista`
  confere que a área de trabalho e o Automático usam a mesma vista.
- **Textos que diziam o lado** (ficariam falsos): a dica do visor do Automático e a dica do botão "antes / depois" da
  área de trabalho agora dizem "para o lado do "antes" ... para o lado do "depois" ..."; docstrings acertadas.
- **Provas antigas:** nenhuma dependia do lado desenhado (as da área de trabalho, P-xxx e D-577 conferem as imagens
  guardadas, `vista.antes` / `vista.depois`, não o lado pintado). Nenhuma mudou.
- **Prints** (`prints_d577_30-10c.py`): `6-area-de-trabalho-linha-toda-a-esquerda.png`, `6-area-de-trabalho-linha-no-meio.png`,
  `6-area-de-trabalho-linha-toda-a-direita.png`, `7-automatico-linha-toda-a-esquerda.png`, `7-automatico-linha-no-meio.png`,
  `7-automatico-linha-toda-a-direita.png`.

- **Testes no PC, um arquivo por vez:** 25 arquivos (os do Automático e os da `VistaAntesDepois`: test_filtros_tela_cheia,
  test_decisoes_ver, _filtro_automatico, _respeitar_gravuras, _marcacoes, _9b1, test_promessas...): todos passaram (o da
  D-577: 22 de 22).

## Pergunta / ressalva da 3ª rodada

5. A mesma vista também é o "Comparar com o Original" da **tela cheia dos filtros** (`FiltrosEmTelaCheia`, rótulos
   "antes: Original" e "depois: <filtro>"). Lá também passou a valer o lado novo. Não foi perguntado ao Samuel; se lá
   for para continuar como era, dizer (dá para separar, mas a mesma vista ficaria com dois jeitos).
- **GitHub 41129841728 (3050494):** passou depois de rodar de novo a parte 1. Na 1ª vez, de novo o erro de tempo do
  `test_promessas.py` (p083 [rede], p083 no Automático [Guardar tudo] e p107 [aviso/forca:mais_escuro]): prévia da área
  de trabalho (`ui/tarefas.py` linha 832) sem o PDF do teste já apagado. Nas rodadas deste ramo, a parte 1 (ou a 2)
  falhou na 1ª vez em 4 de 4 e passou ao rodar de novo; o ramo `automatico-cadernos` (mesma obra) passou de primeira
  (41131159641). Bug para a Lista de bugs (não consertado; não é desta tarefa): o `janela` do test_promessas espera só
  as tarefas do QThreadPool (15 s), e não as contas da prévia do Automático (QThread no `_Guardiao`), que podem seguir
  rodando no teste seguinte; dá para chamar `ui.automatico.parar_as_previas()` ali.

---

# 4ª rodada (31/10): D-594 (todas as opções do painel Filtro no Automático) + D-577 (opções nos dois lados do "comparar")

Ramo atualizado com `obra-2026-10-26` (2822470). Pedido da gerente: uma tarefa só (Samuel: "mas já faça com as
opções que faltam do automatico" · "Sim, podemos fazer isso junto com a tarefa 1").

## Decisões que esta tarefa precisa cumprir

- **D-594** (31/10): "Outra coisa, no automatico não tem opções que encontramos nos filtros da aba da area de
  trabalho." · print do "Mais ajustes": "os tipos de preto." · "mas isso era uma coisa obvia que deveria ter". No
  Livro: **a etapa "Limpar a folha" do Automático tem todas as opções do painel Filtro da área de trabalho, com os
  mesmos nomes**: o "Jeito do preto e branco", "Letra clara em fundo escuro", "Letras com a cor delas", "Reduzir
  cores", "Igualar a luz da página", "Suavizar as letras", "Tirar o chuvisco" e "Respeitar as gravuras achadas".
  Prova pedida: abrir o Automático, etapa "Limpar a folha" → cada opção do "Mais ajustes" do painel Filtro aparece,
  e rodar com ela dá o mesmo resultado que escolhê-la no painel. Pedido da gerente: conferir se falta mais alguma
  (os ajustes de Melhorar/Mágico pro); a prévia antes/depois (D-577) mostra a mudança; receita leva as opções novas.
- **D-577** (o que falta): "seria bom se pudessemos ver as opções e mudar simutaneamente nesse comparar, tivesse uma
  aba de cada lado que abrisse e fechasse para mudar as opções no comparar, ao em vez de ser só o antes e depois." ·
  "não, eu quero poder mudar dos dois lados, todas as opções." · "usar este" em cada lado → "ok, não gostei do nome,
  mas vamos ficar com esse por enquanto." No Livro: **no "comparar": cada lado com uma aba que abre e fecha com
  todas as opções do Automático, mudando à parte; cada lado com "usar este" (nome provisório), que passa as opções
  daquele lado para a janela; o "Rodar" usa as da janela.** Tentado e descartado: rótulos colados na linha.
  Continua valendo da D-577: o comparar mostra à esquerda o filtro que a página já tinha e à direita o escolhido.
- **D-583/D-586/D-587**: "Respeitar as gravuras achadas", ligada de fábrica; cinza com "Só as letras" no Preto e
  branco (como a caixinha das molduras, D-168).
- **D-004**: o "Rodar" pergunta se pula as páginas mexidas à mão (não muda).
- **CLAUDE.md §11 regra 7**: só o que ele mandou (o painel Filtro não muda; o defeito dos nomes cortados lá não é
  desta tarefa). §3: interface nunca congela, uma página por vez na memória.

## Andamento (4ª rodada)

- [x] A: opções novas no core (campos da página, gravadas pelo "Limpar a folha") e na receita
- [x] A: as opções na janela (com os mesmos nomes do painel)
- [x] B: o painel de opções separado da janela (o mesmo nos dois lados do comparar)
- [x] B: comparar com opções nos dois lados e "usar este"
- [x] provas (18), prints (8-*, 9-*), testes um por um
- [x] GitHub 41252917494 (14d8a3c): passou de primeira, tudo verde

## Perguntas para o Samuel (4ª rodada)

6. **(opções novas do "Limpar a folha")** As opções novas ("Força do preto", "Jeito do preto e branco", "Tirar o
   chuvisco"...) são de cada página, no painel Filtro. Na janela do Automático elas começam **com os valores da página
   em que você está** (como o painel Filtro mostra os dela), e o "Rodar" leva esses valores para as páginas onde o
   "Limpar a folha" roda (as mexidas à mão continuam com a pergunta de pular). Sugestão: fica assim. Sim ou não?
7. **(nomes no "comparar")** Cada lado ganhou o botão **"opções"**, que abre e fecha a aba, e o **"usar este"**.
   Enquanto você não mexe no lado esquerdo, ele continua dizendo "como está no livro: <filtro>"; depois que você muda
   uma opção nele, passa a dizer "depois: <filtro>", como o lado direito, porque também mostra como a página vai sair.
   Sugestão: fica assim. Sim ou não?

## Como cumpri cada uma (4ª rodada)

- **D-594, todas as opções do painel Filtro, com os mesmos nomes.** Conferido no código do painel
  (`ui/tela_conferir._montar_aba_filtro`) o que faltava no "Limpar a folha": o "Ajuste" (a barra "Força do preto" /
  "Clareza do fundo" / "Intensidade", um valor por filtro: estava faltando também, não só os da lista), o "Jeito do
  preto e branco" (Automático, os três de sempre e os dez do ScanTailor), "Letra clara em fundo escuro", "Letras com a
  cor delas", "Reduzir cores", "Igualar a luz da página", "Suavizar as letras", "Tirar o chuvisco" (com os avisos de
  luz do painel) e "Respeitar as gravuras achadas". "Limpar a sujeira" e "Só as letras" já estavam. Fora do painel
  Filtro (não entram): "Aplicar em", "deixar em branco", "tirar do livro" (são ações, não opções). Onde:
  `ui/automatico.PainelDeOpcoes._opcoes_do_painel_filtro`; aparecem com as regras do painel (só no Preto e branco o
  jeito, as letras com a cor e o suavizar; o "Mais ajustes" e o "Ajuste" só nos filtros com ajuste; "Respeitar" em
  todos e cinza com "Só as letras", D-587). Provas: `test_d594_cada_opcao_do_painel_filtro_esta_no_limpar_a_folha_com_o_mesmo_nome`
  (lê os nomes da tela de conferir de verdade e compara; a lista dos jeitos é igual item por item),
  `test_d594_aparecem_como_no_painel_conforme_o_filtro`. Prints `8-automatico-limpar-preto-e-branco-mais-ajustes.png`,
  `8-automatico-jeito-do-preto-e-branco.png`, `8-automatico-limpar-magico-pro-chuvisco-30.png`.
- **D-594, o mesmo resultado que escolher no painel (mesmos campos, nada de conta nova).** As opções são os campos da
  página (`core/automatico.CAMPOS_DA_PAGINA`); o "Rodar" grava, em cada página onde o "Limpar a folha" roda (as
  puladas pela pergunta D-004 ficam), as que o painel mostra com aquele filtro (`campos_da_pagina_no_filtro`), na
  mesma ação do desfazer. A "Força do preto" escurecida sozinha pelo programa não é desfeita se o valor pedido é o
  de antes do reforço (`_valor_da_pagina`). Prova: `test_d594_rodar_com_a_opcao_da_o_mesmo_que_escolher_no_painel`,
  11 casos (uma por opção, inclusive os três ajustes): os campos da página e a página desenhada saem iguais pelos dois
  caminhos; o Ctrl+Z desfaz o Automático com a opção junto.
- **D-577 + D-594, a prévia mostra a mudança.** `test_d594_a_previa_mostra_a_mudanca_da_opcao` ("Tirar o chuvisco" 60
  muda o depois; 0 volta ao mesmo).
- **Receitas.** As chaves novas entram em `core/perfis.CAMPOS` (a receita do Automático as guarda como as outras).
  Receita antiga não tem as chaves: posta, as opções novas ficam como estavam (nada quebra; não precisou mudar o
  formato de um jeito que quebre). "De fábrica" põe as de uma página nova. A caixa da receita diz as novas que não
  estão de fábrica, com os nomes do painel. Prova: `test_d594_a_receita_leva_as_opcoes_novas_e_a_antiga_continua_valendo`.
- **D-577, comparar: aba com todas as opções em cada lado, mudando à parte.** O miolo da janela virou
  `PainelDeOpcoes` (a lista das etapas e as opções de cada etapa); a janela grande e cada lado do comparar usam o
  MESMO (sem cópia de código). Cada lado (`LadoDoComparar`) tem um estado só dele, o botão "opções" (abre e fecha a
  aba) e o "usar este". A esquerda começa das opções do livro como está e mostra a página como está no livro (como
  era); a direita começa das opções da janela e mostra o depois da janela (e acompanha a janela enquanto não é
  mexida). Mexido, o lado mostra como a página sai com as opções dele (a mesma conta da prévia, numa cópia; só o
  depois; bolinha girando). Provas: `test_d577_cada_lado_do_comparar_tem_a_aba_com_todas_as_opcoes_e_o_usar_este`,
  `test_d577_lado_direito_nao_mexido_acompanha_a_janela`. Prints `9-comparar-abas-fechadas.png`,
  `9-comparar-abas-abertas-direita-magico-pro.png`.
- **D-577, "usar este" passa as opções para a janela; o "Rodar" usa as da janela; nada muda no livro.**
  `test_d577_mudar_um_lado_nao_muda_a_janela_e_usar_este_passa_para_ela` (os dois lados; o pedido do "Rodar" sai com
  as opções passadas; o livro e o desfazer iguais). Prints `9-comparar-depois-de-usar-este-da-direita.png`,
  `9-janela-depois-de-usar-este-magico-pro.png`.
- **Reversão (§11 regra 4):** as provas novas rodadas no código de antes (2822470) falham: "\"Letra clara em fundo
  escuro\" (painel Filtro) não está no \"Limpar a folha\" do Automático", "no attribute 'CAMPOS_DA_PAGINA'",
  "cannot import name 'PainelDeOpcoes'".
- **O painel Filtro não mudou** (nenhuma linha de `ui/tela_conferir.py`; os nomes cortados de lá não são desta tarefa).

## Ressalvas (4ª rodada)

- Mexi em `core/` (`core/automatico.py`: o "Limpar a folha" grava os campos da página; `core/perfis.py`: as chaves da
  receita). Nada do desenho da página (`core/pipeline`) mudou; o rodar faz uma volta a mais pelas páginas comparando
  11 campos. O filtro de velocidade do GitHub não foi rodado.
- No lado do comparar, a aba tem 400 pontos de largura: as frases ao lado dos filtros ficam cortadas e a aba rola de
  lado (como a coluna estreita). Em tela pequena as duas abas abertas deixam pouca página à vista.
- Bug que já existia (não consertei, não é desta tarefa): no "Limpar a folha", fora do Preto e branco, a caixinha
  "Escurecer sozinho a força do preto..." some mas a frase de baixo dela fica ("com "Só as letras": escurece só na
  página falhada..."); aparece no print `9-comparar-abas-abertas-direita-magico-pro.png`. Para a Lista de bugs.

## Testes da 4ª rodada

- PC, um arquivo por vez (offscreen): 29 arquivos que tocam o Automático, as receitas e o painel Filtro. Todos
  passaram (o novo `test_decisoes_automatico_opcoes_do_filtro.py`: 18 de 18; o da D-577: 22 de 22;
  `test_promessas.py`: 262 + 1 xfail). Um falhou na 1ª vez: `test_unidades_e_perfis.py::test_de_fabrica_existe_e_e_o_livro_novo`
  (eu tinha posto as opções da página na receita "De fábrica" do `core/perfis`); consertado pondo-as pela janela
  (`EstadoDoAutomatico.por_receita`), e o arquivo passou (9 de 9), com o do Automático e o novo de novo.
- `teste_botoes.py` no PC (offscreen): 366 ações, 0 falhas.
- GitHub 41249268892 (ac6e4c9): as conferências passaram; o `teste_botoes.py` deu 4 falhas ("o icone 'automatico' /
  'props' / 'filtro' / 'historico' nao abriu o painel dele"). Causa: nessa rodada o aviso "Qualidade baixa" da
  página 3 já tinha chegado quando o roteiro abriu o painel "Para revisar", e ele clicou "ver as 1 em tela cheia" e
  "ver a lista…", que abrem janelas por cima e não são fechadas pelo roteiro; os ícones seguintes não recebem o
  clique. Nas rodadas que passaram (este ramo 41129841728, livreto 41217021857) o aviso ainda não tinha chegado e
  esses dois botões nem aparecem. Rodada de novo, a parte falhou igual (2 de 2); a base (`obra-2026-10-26`,
  2822470, rodada 41251418890) passou no `teste_botoes.py` (sem o aviso nesse ponto; a parte 1 dela caiu num teste
  das conferências, não olhei). O que muda o tempo: o roteiro clica cada controle da janela do Automático, e agora
  são 15 trocas a mais (os jeitos do preto e branco e as caixinhas novas), uns 5 segundos.
- Achado (31/10): o que falhava era o roteiro, não o programa. "ver as N em tela cheia" troca a página pela grade
  "Todas as páginas"; com a grade na frente, o painel abre mas fica escondido (conferido num roteiro à parte: sem
  grade o painel aparece; com a grade, não; voltando da grade, aparece). Conserto no `teste_botoes.py`: depois de
  cada botão do painel, se a grade abriu, volta (o "voltar" da grade, como a pessoa faria). No PC, numa rodada em que
  o aviso já tinha chegado ("ver as 1 em tela cheia"): 371 ações, 0 falhas (commit 14d8a3c).
- **GitHub 41252917494 (14d8a3c): passou** (as 5 partes das conferências e o `teste_botoes.py`, de primeira).

PRONTO PARA O VERIFICADOR (4ª rodada).
