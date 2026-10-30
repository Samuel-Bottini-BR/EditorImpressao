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

## Perguntas para o Samuel

(nenhuma; as ressalvas vão na entrega à gerente)
