# Onde parei: melhorias do layout 6 e 7 (começado em 22/10/2026)

- Ramo `layout-etapas4a7-2026-10-19`, worktree `.claude/worktrees/layout-4a7` (junções `modelos`,
  `gabarito\paginas`: nunca `Remove-Item -Recurse` nelas). Só `ui/` e os testes de tela.
- O histórico das etapas 4 a 7 continua em `relatorios/layout-4a7/ONDE-PAREI.md`.
- Pedido (Central, 22/10): layout 6 e 7 "Aprovado", ordem "continuar" com as melhorias: quadro azul certo no "Duas
  lado a lado"; "Antes de processar" ("ficou meio embolado, deve ficar mais claro e não tão grande."); lembrar as
  miniaturas ("Sim, lembrar para todos os livros", 21/10). Fora: bolinhas de carregamento; letra mais grossa da tela
  cheia (processamento).
- Prints: `relatorios/layout-4a7/melhorias-6-7/<item>/antes|depois`, janela de verdade (1280 x 657 = print 1600 x
  821 a 125%, e "maximizada" 1536 x 816). Código antigo para os "antes": worktree `saida_teste/antigo` (`7843503`,
  sem junções; apagar com `git worktree remove` no fim).

## Item 1: quadro azul de "Todas as páginas" em "Duas lado a lado": FEITO, PRONTO PARA CONFERIR
- Causa: rolando até o par, o "acompanhar da rolagem" (`ui/widgets/paginas_rolando._acompanhar`) trocava a página da
  vez pela primeira do par (a 300); a pílula dizia 301 porque era escrita depois. Agora, se a página da vez já está
  no par que aparece, ela continua a da vez.
- Teste de reversão `tests/test_livro_aberto.py::test_duas_lado_a_lado_guarda_a_pagina_da_vez`: falhou no código de
  antes ("foi à 21 e a página da vez virou a 20"), passa no novo (14 de 14 no arquivo).
- Janela de verdade (Graduale, ir para 301 pela pílula, "Ver todas as páginas" por clique do Windows): antes o azul na
  300 em 1600 x 821 (maximizada já acertava por acaso); depois na 301 nos dois tamanhos (5 de 5).

## Item 2: "Antes de processar": FEITO NUM RAMO À PARTE, PRONTO PARA CONFERIR
- A janela (`ui/janela_dos_avisos.py`) só existe no ramo do "Para revisar" (`fase2-para-revisar`, aprovado, ainda não
  juntado), não neste ramo nem no `fase-1`. Para não juntar o "Para revisar" inteiro aqui (é trabalho da gerente),
  fiz a mudança num ramo novo, `layout-antes-de-processar-2026-10-22`, que parte do `f54428e` (ponta do
  `fase2-para-revisar`) e só mexe em `ui/janela_dos_avisos.py` e num teste. Worktree `.claude/worktrees/layout-avisos`
  (junção `modelos`). Commit `138e425`.
- O que mudou: abre com 500 x 400 (era 560 x 520; na janela de verdade 522 x 400 contra 560 x 520, a 1280 x 657 ela
  passou de 80% para 61% da altura); a frase em duas linhas (o que aconteceu, forte; "Quer ver antes ou continuar
  assim mesmo?", mais fraca); "Selecionar todas" e "Nenhuma" pequenos na mesma linha do "Mostrar"; uma fila só
  embaixo ("está bom nas marcadas" à esquerda, "ver" em azul e "continuar assim mesmo" à direita); linhas da lista
  mais baixas. Nenhum controle saiu, nenhum nome mudou.
- Testes: `tests/test_para_revisar_na_tela.py` 26 passaram (teste novo `test_antes_de_processar_menor_e_em_duas_filas`);
  `tests/test_reversao_para_revisar.py` 6 passaram.
- Prints (janela de verdade, Palatino, clique do Windows em "Confirmar e processar" e em "ver"): no ramo novo,
  `relatorios/layout-antes-de-processar/antes|depois` (4 de 4 nas duas rodadas).
- Ressalva: a página que tem dois motivos aparece em duas linhas ("Página 69 - Alinhamento duvidoso" e "Página 69 -
  Endireitar..."). Juntar numa linha mudaria as caixinhas (uma por motivo): não mexi.
## Item 3: lembrar as miniaturas para todos os livros: FEITO, PRONTO PARA CONFERIR
- O lugar (embaixo, esquerda, direita), abertas ou fechadas e "Ver em pares" ficam em `configuracoes.json`, chave
  nova "miniaturas" (`configuracoes.PADROES`, fora de `ui/`, só a preferência, como o "livro_aberto"). A tela de
  trabalho (`ui/tela_conferir.py`: `miniaturas_guardadas`, `_guardar_as_miniaturas`) lê ao montar e grava a cada
  mudança (arrastar a alça, "Lugar", seta, "Ver em pares", menu Ver). Valor estranho volta ao de fábrica. O menu Ver
  > "Miniaturas" acompanha quando elas abrem fechadas (`ui/janela_principal.py`).
- Teste `tests/test_miniaturas_novas.py::test_as_miniaturas_ficam_para_o_proximo_livro` (5 de 5 no arquivo; também
  `test_barra_de_menu` 20, `test_paineis_na_tela` 22, `test_menus_que_nao_faziam_nada` 5, `test_livro_aberto` 14).
- Janela de verdade (Boécio: alça arrastada para a esquerda com o Windows, "Ver em pares"; programa fechado e aberto
  de novo no Palatino; seta fechada com o Windows; aberto de novo): antes 3 de 5 (o outro livro voltava embaixo,
  uma a uma, abertas); depois 5 de 5. `relatorios/layout-4a7/melhorias-6-7/3-miniaturas-lembradas/antes|depois`.

## Perguntas para o Samuel
(nenhuma ainda)

## GitHub (22/10)
- 39843764387 (este ramo, `edc6143`): success; teste_botoes 216 ações, 0 falhas; erros.log vazio.
- 39843769308 (`layout-antes-de-processar-2026-10-22`, `138e425`): success; teste_botoes 228 ações, 0 falhas; erros.log vazio.
- **Parado aqui.** Os três itens PRONTOS PARA CONFERIR. Nenhuma pergunta aberta para o Samuel.
