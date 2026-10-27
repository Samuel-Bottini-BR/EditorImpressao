# Obra 26/10, etapa 9c — consertos de núcleo (ONDE-PAREI)

Ramo `obra-etapa9c-2026-10-26` (base `obra-2026-10-26` = 39b7d8a). Worktree `.claude/worktrees/obra-etapa9c`.

## Decisões que esta tarefa precisa cumprir

- **D-027** (30/09/2026): "essa é uma página que eu poderia simplesmente escolher a opção para virar uma folha branca,
  pois não tem nenhum conteúdo." — promessa P-078.
- **D-227** (05/10/2026): "[...] eu poderia ir lá e apagar ou botar branco por cima" · prova do Livro: "Clicar numa área
  laranja e 'pintar de branco' → no PDF sai branca" — promessa P-075.
- **D-134** (29/09/2026): "Página sempre abre em 'Original', sem mexer. [...] sem mudança escondida." (o Original continua
  sendo a página como veio: só o papel marcado à mão vai a branco).
- **D-342** (05/10/2026): "o programa quando estiver pronto, ele vai ter que ser capaz de abrir arquivos de versões
  anteriores." (item 3: projeto ilegível não pode sumir calado).
- **D-271 / D-288 / D-254 / D-474** ("Parece em branco"): "Tem que ter um tipo de aviso para cada coisa [...]" ·
  Gladstone 18 "Está bom" (página com título não recebe "Parece em branco") · "menos de 10% das páginas são marcadas
  para revisão — o alerta não vira ruído" (item 4).
- **D-082** (05/10/2026): "O do ScanTailor de fábrica; quando os dois discordarem mais de 0,3 grau, a página fica marcada
  'conferir'" (item 5: página reta não avisa).
- **D-365** (18/07/2026): "Corrija TODOS os textos da interface para português correto" (item 6).
- **D-479** (26/10/2026): "o do Editor" / "a do Editor" em todo lugar onde aparece o jeito ou a conta do próprio
  programa (item 6).

## Andamento

| Item | Situação | Commit |
|---|---|---|
| 1. folha em branco / pintar de branco no Original | feito | (ver git log) |
| 2. nome de saída sem acento | a fazer | |
| 3. projeto.json ilegível | a fazer | |
| 4. "Parece em branco" falso | a fazer | |
| 5. "contas discordam" em página reta | a fazer | |
| 6. textos do núcleo | a fazer | |
| 7. "Menor que o corte" com números iguais | a fazer | |

## Item 1 — "Deixar a folha em branco" e "pintar de branco" no Original

**Causa.** `core/filtros.aplicar_filtro_com_selecao`, ramo do Original/Tirar o fundo: devolvia a página como veio com só
os pedaços de "só neste pedaço" por cima (`aplicar_so_os_pedacos`). O papel marcado à mão (a folha inteira do menu Marcar,
`ui/tela_conferir._folha_em_branco`, e a área de "pintar de branco", `core/editar_zonas.pintada_de_branco`) é uma região
`tipo=papel, origem=mao, filtro=""`, que nos outros filtros ia a branco, mas no Original era ignorada. Vale com e sem
"Limpar a folha" (sem ela, `pipeline._so_a_marcacao_a_mao` chama o mesmo ramo).

**Conserto.** `core/filtros._papel_a_mao_em_branco`: depois dos pedaços, o papel marcado À MÃO e sem filtro próprio vai a
branco. O papel que a máquina marcou continua sem mudar o Original (D-134). Sem esse papel, devolve o mesmo objeto
(página sem marcação sai idêntica, sem conta a mais).

**Provas.**
- `tests/test_decisoes_nucleo.py`: `test_d027_folha_em_branco_no_original_sai_branca[com/sem limpar]`,
  `test_d227_pintar_de_branco_no_original_sai_branco_so_na_area[com/sem limpar]`,
  `test_papel_que_a_maquina_marcou_nao_branqueia_o_original`. No código antigo: 4 falham, 1 passa (a de "máquina" é a
  guarda do lado de lá). No novo: 5 passam.
- Promessas: `pytest tests/test_promessas.py -k "p075 or p078 or p073"` → 4 passed (2 vezes). No código antigo P-075 e
  P-078 falham. Tirei o campo "defeito" das duas em `tests/promessas/promessas.md`.
- A prova P-075 tinha uma falta própria, escondida pelo defeito do PDF: o terceiro clique ("apagar a área") vinha antes
  de a página chegar ao editor e não escolhia nada. Pus a mesma espera do clique de cima
  (`aj.esperar(lambda: editor._pixmap is not None ...)`), em `tests/test_promessas.py`. Não é defeito do programa (o
  clique de verdade só existe com a página na tela).

**Ressalva.** A página em "Tirar o fundo" de que o fundo FOI tirado vai por `pipeline._pedacos_na_pagina_sem_fundo`, que
não passa por este ramo: ali "Deixar a folha em branco" ainda não branqueia a tinta. Não pedido; anotado como bug.
