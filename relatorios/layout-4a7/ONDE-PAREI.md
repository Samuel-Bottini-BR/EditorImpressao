# Onde parei: rodada 14 e etapas 4 a 7 do layout (começado em 20/10/2026)

- Ramo: `layout-etapas4a7-2026-10-19`, a partir do `origin/fase-1` (`b8e9af7`).
- Worktree: `.claude/worktrees/layout-4a7` (junções: `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`;
  nunca `Remove-Item -Recurse` nelas).
- Só mexo em `ui/` (e nos testes de tela). Outro agente (Fase 2, ramo `fase2-scantailor-itens-2026-10-19`) pode pôr
  controles mínimos nos painéis Filtro e Propriedades e listá-los em `layout\Botoes e funcoes para o layout.md`: ler a
  lista quando ele publicar e não desfazer.
- Fontes: `Plano de layout (rascunho).md` e `prototipo\21-rodada13-base.html` (pasta
  `D:\programas\EditorImpressao-arquivos\plano-24-09-2026\layout\`); a lista do que falta é o `ONDE-PAREI.md` do ramo
  `layout-impl-2026-10-08`.

## Tarefa 1: rodada 14 de perguntas

Situação: **pronta para a gerente publicar** (20/10).
- `rodada14-escolhas.json` + 53 imagens `22-rodada14-*.png` em `relatorios/layout-4a7/rodada14/` e também na pasta
  do HD (`...\plano-24-09-2026\layout\` e `\imagens\`, só arquivos novos). Seção "Rodada 14" acrescentada no fim do
  `Plano de layout (rascunho).md` (cópia de antes: `...antes-2026-10-20.md`).
- 8 perguntas (901 a 908): Todas as páginas de fábrica; onde troca o lado direito; painéis nos menus; peças novas
  no menu Ver; "o mesmo da página"; frase do aviso "desenho ou escrita"; "o do Editor" no Dividir; a "Conta" com o
  ângulo à mão.
- Fotos: programa de verdade (`saida_teste/prints_r14.py`, cópia em `rodada14/`), renderizado num QPixmap a 2,4 x
  (num QImage as cores da página saíam trocadas; com QT_SCALE_FACTOR=2 o Windows encolhia a janela para 1000 x 600).
- Falta na página (fora de `ui/`): grupo "22" em `docs/plano/para_a_pagina_de_layout.py`.

## Tarefa 2: etapas 4 a 7

Situação: não começada.
