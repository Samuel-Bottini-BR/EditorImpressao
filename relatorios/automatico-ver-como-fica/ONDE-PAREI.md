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
- [ ] testes que tocam ui/automatico.py, um por vez (rodando)

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
