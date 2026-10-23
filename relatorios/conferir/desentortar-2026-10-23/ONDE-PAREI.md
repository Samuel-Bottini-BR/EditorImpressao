# Onde parei: verificador d212, item 2.12 (desentortar perto da lombada)

Pedido da gerente em 23/10/2026. Ramo `verif-2.12-2026-10-23` (da ponta `c3b66fb` do
`fase2-scantailor-itens-2026-10-19`), worktree `.claude/worktrees/v212`. "Antes": worktrees destacadas
`.claude/worktrees/v212-antes` (`b8e9af7`) e `.claude/worktrees/v212-p5` (`2a42cfb`), criadas por mim, só para rodar.
Junções `modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09` nas três (desfazer só com
`(Get-Item <junção>).Delete()`, nunca apagar a pasta).

## Situação (23/10/2026): FEITO — PRONTO PARA CONFERIR, com ressalvas

Entrega para a gerente publicar (NÃO publiquei na Central): `conferencia.json` (id `d212`, fotos `d212/img/<nome>.jpg`,
guardadas em `img/`, fora do git), relatório `relatorio-d212.html` (.md/.pdf).

- [x] (1) Desligado de fábrica: 96 de 96 PDFs de saída iguais ao `b8e9af7` (`maquina/somas-comparacao.txt`; meu
      roteiro usa `processar`, o PDF de verdade, não o `renderizar_pagina` do implementador). Projeto antigo abre
      "desligado" (`maquina/reabrir/reabrir.json`).
- [x] (2) Ligado: página curva limpa (Righetti 96 encurvada por mim) sai reta, sem perder letra. Páginas de verdade:
      a proteção segura onde estragaria; nenhuma perdeu texto. RESSALVA: com a moldura escura do scanner (Marial
      encurvada) não acha a curva — causa: `caixa_do_conteudo` pega a moldura (`img/causa-curvada2-moldura.jpg`,
      `scripts/exp2.py`).
- [x] (3) Prévia Rápida = PDF reduzido, 6 de 6 (diferença 0) (`previa/previa.json`).
- [x] (4) Janela de verdade: 31/31 (Destino 18 com Desfazer/Manter assim/Desfazer(Ctrl+Z)/abrir de novo, Righetti
      96) + 7/7 (página curva) (`maquina/janela*.log`, `maquina/janela-*conferencias.txt`).
- [x] (5) Tela não trava: maior parada 23 a 37 ms durante a medida.
- [x] (6) GitHub lido: suíte 39902142935 (código 6be1dbe = c3b66fb) 2204/0, botões 221/0; velocidade 39902159919
      igual (`maquina/github.txt`). Testes do desentortar com os livros no PC: 80 passaram (`maquina/testes-novo.txt`);
      reversão da P6 falha no `2a42cfb` (proporção 0,318) (`maquina/reversao-p6-no-2a42cfb.txt`).

## Perguntas para o Samuel

Fotos e opções em `conferencia.json` (`perguntas`) e no relatório.

1. **d212-1** — Página curva com a moldura escura do scanner: o desentortar não acha a curva (a caixa do texto pega a
   moldura). A (recomendo) esperar o 2.5 e refazer esta página; B voltar ao implementador agora; C deixar.
   Fotos: `img/ligado-curvada2-pagina.jpg`, `img/causa-curvada2-moldura.jpg`.
2. **d212-2** — Righetti 96 com o botão: página um pouco deformada (linhas de cima maiores, margem esquerda ondulada)
   sem a pergunta. A está bom assim; B também deveria perguntar. Fotos: `img/ligado-righetti96-pagina.jpg` (coluna 3),
   `img/previa-righetti96-botao-previa.jpg`.

## Ressalvas

Ver `relatorio-d212.md` (9 ressalvas).

## Rascunhos fora do projeto (criados por mim; não apaguei)

- `C:\Users\fotog\AppData\Local\Temp\v212_localappdata\` (PDFs das páginas, páginas de teste encurvadas, PNGs).
- Pastas de trabalho da janela no scratchpad da sessão.
