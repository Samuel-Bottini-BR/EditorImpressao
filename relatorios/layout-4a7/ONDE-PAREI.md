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

Situação: não começada (a rodada 14 foi entregue primeiro, para o Samuel responder enquanto a obra anda).

### Plano da etapa 4 (o que não depende da rodada 14)
1. **Propriedades das ferramentas de marcar** (protótipo `21-rodada13-base.html`, `propsMarcarA`): sob o "Marcar
   como", as partes "Marcação desta página" (detectar automaticamente · usar em todas · daqui em diante), "Foto"
   ("Esta página tem foto" · usar em todas · daqui em diante) e "Pedaço" (Ajustar o pedaço à figura + o aviso);
   saem as filas de baixo da página (`_montar_aba_marcar`, `linhas_de_botoes[ABA_MARCAR]`). O "Na área marcada"
   (pintar por cima, copiar, colar, mover) não existe no programa: não inventar.
2. **Painel Filtro decidido** (R9 403 B, R10 nomes do conjunto 2 e menus com amostra, R11 ícone da tela cheia no
   título): fila dos filtros com tecla, partes que abrem e fecham (Ajuste · Só as letras · Limpar a sujeira · Mais
   ajustes · Só neste pedaço), "apagar página" depois de um risco, pé "Aplicar em: só nesta · todas · daqui em
   diante". **Atenção:** o agente da Fase 2 (ramo `fase2-scantailor-itens-2026-10-19`, `34b3d0e`) pôs os dez
   jeitos do ScanTailor na lista `seletor_algoritmo_pb` ("Algoritmo:"); no painel novo essa lista vira "Jeito do
   preto e branco" em "Mais ajustes" e tem de levar os itens dele (juntar o ramo dele antes, ou manter a mesma
   lista `seletor_algoritmo_pb`).
3. **Itens de menu mortos** (conserto, com teste de reversão): Aproximar, Afastar, Ajustar à tela, Mostrar o
   histórico, Restaurar página apagada, Modo comparar, Livros recentes. Os quatro "Painel: …" esperam a 903.
4. Depois de cada passo: prints da janela real (`saida_teste/prints_etapa3.py` como base), `teste_botoes.py` no
   GitHub (`-f so_janela=true`) e a lista do que ficou antigo.
