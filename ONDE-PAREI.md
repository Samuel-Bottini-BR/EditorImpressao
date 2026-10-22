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

## Item 2: "Antes de processar": a fazer
## Item 3: lembrar as miniaturas: a fazer

## Perguntas para o Samuel
(nenhuma ainda)
