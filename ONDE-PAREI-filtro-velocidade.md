# Onde parei: filtro de velocidade no GitHub (antes x depois na mesma máquina)

Pedido da gerente em 20/10/2026 (CLAUDE.md §4.6, "opção 2" de 19/10). Ramo: `claude/list-server-files-gkos8v`
(worktree `D:\programas\EditorImpressao\.claude\worktrees\filtro-velocidade`). Só mexo no workflow e nos scripts
de apoio em `.github/`.

## Passos

- [x] 1. Worktree criada, leitura feita (workflow, `teste_velocidade.py`, medida do PC de 14/10).
- [ ] 2. Script `.github/scripts/velocidade_ab.py` (roda alternando e junta a tabela) + `preparar_versao.sh`.
- [ ] 3. Conferir a parte que junta com os números do PC de 14/10 (tem de dar "igual").
- [ ] 4. Novo modo no workflow (`velocidade_ab`), sem mudar os modos que já existem.
- [ ] 5. Rodada curta (`rapido`) para ver que funciona.
- [ ] 6. Validação 1: antes = `1d37f8f`, depois = `3bdbab3`.
- [ ] 7. Validação 2: a mesma coisa de novo.
- [ ] 8. Controle: antes = depois = mesmo commit.
- [ ] 9. Entrega à gerente.

## Anotações

- Commits deste trabalho levam `[skip ci]` na mensagem: sem isso cada push neste ramo dispara a suíte inteira
  e grava prints no `prints-testes`.
