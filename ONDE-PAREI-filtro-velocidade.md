# Onde parei: filtro de velocidade no GitHub (antes x depois na mesma máquina)

Pedido da gerente em 20/10/2026 (CLAUDE.md §4.6, "opção 2" de 19/10). Ramo: `claude/list-server-files-gkos8v`
(worktree `D:\programas\EditorImpressao\.claude\worktrees\filtro-velocidade`). Só mexo no workflow e nos scripts
de apoio em `.github/`.

## Passos

- [x] 1. Worktree criada, leitura feita (workflow, `teste_velocidade.py`, medida do PC de 14/10).
- [x] 2. Script `.github/scripts/velocidade_ab.py` (roda alternando e junta a tabela) + `preparar_versao.sh`.
- [x] 3. Conferir a parte que junta com os números do PC de 14/10 (tem de dar "igual").
- [x] 4. Novo modo no workflow (`velocidade_ab`), sem mudar os modos que já existem.
- [ ] 5. Rodada curta (`rapido`) para ver que funciona: rodada 39394176019 (disparada 20/10 08:32 UTC).
- [ ] 6. Validação 1: antes = `1d37f8f`, depois = `3bdbab3`.
- [ ] 7. Validação 2: a mesma coisa de novo.
- [ ] 8. Controle: antes = depois = mesmo commit.
- [ ] 9. Entrega à gerente.

## Anotações

- Commits deste trabalho levam `[skip ci]` na mensagem: sem isso cada push neste ramo dispara a suíte inteira
  e grava prints no `prints-testes`.
- 3: `--so-juntar` nas pastas do PC de 14/10 deu "igual" nas quatro medidas (Magico pro -3,0% com vai-e-vem 3,6%).
- A regra do veredito (diferenca das medianas > maior vai-e-vem entre rodadas da mesma versao), simulada com
  ruido puro e 3 rodadas: ~3% de "falso lento" por medida (~12% em alguma das 4). Ver se a validacao confirma;
  se acusar lentidao, repetir antes de devolver ao agente.
