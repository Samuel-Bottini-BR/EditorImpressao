# Onde parei: conferência das 3 melhorias de tela do layout (22/10/2026)

- Ramo `verif-layout-melhorias-2026-10-22` (parte de `a3f7240`), worktree `.claude/worktrees/vlm22`.
- Worktrees de apoio (HEAD solta, todas com junções `modelos` e `gabarito\paginas`: nunca `Remove-Item -Recurse`):
  `vlm22-antes` (`7843503`), `vlm22-av` (`138e425`), `vlm22-av-antes` (`f54428e`).
- Itens: 1 quadro azul em "Duas lado a lado" (`eae91cb`); 2 "Antes de processar" (`138e425`); 3 miniaturas
  lembradas (`edc6143`). Rodadas do GitHub do agente: 39843764387 e 39843769308.

## Andamento
- [x] ler as diferenças do código
- [x] testes de reversão no código antigo: item 1 falha no `7843503` ("foi à 21 e a página da vez virou a 20") e
  passa no novo (14 de 14); item 3: o teste do agente falha no antigo só por ImportError; uma variante só de
  comportamento (minha) falha no antigo e passa no novo; `test_miniaturas_novas.py` 5 de 5. Item 2: 26 de 26 no
  `138e425`; no `f54428e` o teste novo falha por ImportError (é mudança de tela, não conserto).
- [x] item 1 na janela de verdade: depois 14 de 14 (301 e 300 em "Duas lado a lado", 301 em "Uma página", nos dois
  tamanhos, página digitada na pílula com teclas do Windows); antes 12 de 14 (a 301 em 1280x657 marcava a 300).
- [x] item 3 na janela de verdade, cada fase um processo novo: depois todas certas (direita + em pares guardados,
  outro livro igual, seta fecha e fica fechada, 3 valores estranhos voltam ao de fábrica); antes não guardava nada.
- [ ] item 2 na janela de verdade
- [ ] conferencia.json

## Perguntas para o Samuel
(nenhuma ainda)
