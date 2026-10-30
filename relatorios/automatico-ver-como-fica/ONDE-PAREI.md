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
- [ ] core: prévia de uma página pelo mesmo caminho do rodar (core/automatico.py)
- [ ] tarefa de fundo (ui/tarefas.py)
- [ ] coluna da direita da janela grande (ui/automatico.py)
- [ ] provas (tests/test_decisoes_automatico_ver_como_fica.py)
- [ ] testes que já tocam ui/automatico.py, um por vez
- [ ] prints offscreen

## Perguntas para o Samuel

(nenhuma ainda)
