# Onde parei: conferência das 3 melhorias de tela do layout (22/10/2026)

- Ramo `verif-layout-melhorias-2026-10-22` (parte de `a3f7240`), worktree `.claude/worktrees/vlm22`.
- Worktrees de apoio (HEAD solta, todas com junções `modelos` e `gabarito\paginas`: nunca `Remove-Item -Recurse`;
  desfazer com `(Get-Item <junção>).Delete()` e depois `git worktree remove --force`): `vlm22-antes` (`7843503`, com
  os testes novos copiados por cima), `vlm22-av` (`138e425`), `vlm22-av-antes` (`f54428e`, com o teste novo copiado).
- Itens: 1 quadro azul em "Duas lado a lado" (`eae91cb`); 2 "Antes de processar" (`138e425`); 3 miniaturas
  lembradas (`edc6143`). Rodadas do GitHub do agente (lidas, código igual ao conferido, não disparei outra):
  39843764387 (`edc6143`; a ponta `a3f7240` só muda o ONDE-PAREI): 2196 passaram, 0 falharam, botões 216 ações
  0 falhas; 39843769308 (`138e425`): 2188 passaram, 0 falharam, botões 228 ações 0 falhas.

## Andamento: TERMINADO, PRONTO PARA CONFERIR (com ressalvas)
- Testes de reversão: item 1 falha no `7843503` ("foi à 21 e a página da vez virou a 20") e passa no novo
  (`test_livro_aberto.py` 14 de 14). Item 3: o teste do agente falha no antigo só por ImportError; uma variante só de
  comportamento (`roteiros/`, não commitada em tests/) falha no antigo e passa no novo; `test_miniaturas_novas.py`
  5 de 5. Item 2: `test_para_revisar_na_tela.py` 26 de 26 no `138e425`; no `f54428e` o teste novo falha por
  ImportError (mudança de tela, não conserto de bug).
- Item 1, janela de verdade (Graduale, página digitada na pílula com teclas do Windows): depois 14 de 14; antes
  12 de 14 (a 301 em 1280x657 marcava a 300; maximizada acertava por acaso).
- Item 2, janela de verdade (Palatino, 25 avisos): 16 de 16 nos dois códigos; nomes e controles iguais; janela
  522x400 (61% da altura) contra 560x520 (79%). DEFEITO: o "Mostrar" corta "Endireitar: as contas discordam (12)"
  (220 pontos para 219 de texto + seta). 7 linhas à vista em vez de 10.
- Item 3, janela de verdade, cada fase um processo novo: depois todas certas; antes não guardava nada. Valores
  estranhos (dicionário sem sentido, texto, arquivo quebrado): volta ao de fábrica.
- Achado à parte (já existia no `7843503`): ao montar a janela, 4 botões viram janelas soltas por um instante
  (`ui/widgets/escolhas_do_misto.py:169` "Guardar a tinta forte/tudo/só o texto"; `ui/widgets/miniaturas.py:219`
  "ver todas"). Para a Lista de bugs; não vi se pisca na tela.
- Cuidado aprendido: `QMenu.popup` e os diálogos do Qt puxam a janela para dentro da tela do Samuel mesmo com o
  programa em -32000. Os roteiros (`roteiros/base.py`) põem toda janela nova fora da tela no evento Show, antes de
  aparecer.
- Entrega: `conferencia.json` (id `lm22`), `relatorio-lm22.html/.pdf/.md`, `img/` (30 fotos).

## Perguntas para o Samuel
(nenhuma)
