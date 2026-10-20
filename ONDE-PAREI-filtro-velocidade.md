# Onde parei: filtro de velocidade no GitHub (antes x depois na mesma máquina)

Pedido da gerente em 20/10/2026 (CLAUDE.md §4.6, "opção 2" de 19/10). Ramo: `claude/list-server-files-gkos8v`
(worktree `D:\programas\EditorImpressao\.claude\worktrees\filtro-velocidade`). Só mexo no workflow e nos scripts
de apoio em `.github/`.

## Passos

- [x] 1. Worktree criada, leitura feita (workflow, `teste_velocidade.py`, medida do PC de 14/10).
- [x] 2. Script `.github/scripts/velocidade_ab.py` (roda alternando e junta a tabela) + `preparar_versao.sh`.
- [x] 3. Conferir a parte que junta com os números do PC de 14/10 (tem de dar "igual").
- [x] 4. Novo modo no workflow (`velocidade_ab`), sem mudar os modos que já existem.
- [x] 5. Rodada curta (`rapido`) para ver que funciona: rodada 39394176019, success (preparo ~3 min, 4 rodadas --rapido de 1 min).
- [x] 6. Validação 1: antes = `1d37f8f`, depois = `3bdbab3`: rodada 39395142921 -> igual (1h50).
- [x] 7. Validação 2: a mesma coisa de novo: rodada 39395156472 -> igual.
- [x] 8. Controle: antes = depois = mesmo commit (`1d37f8f`): rodada 39395169127 -> igual.
- [x] 9. Entrega à gerente (20/10).

## Anotações

- Commits deste trabalho levam `[skip ci]` na mensagem: sem isso cada push neste ramo dispara a suíte inteira
  e grava prints no `prints-testes`.
- 3: `--so-juntar` nas pastas do PC de 14/10 deu "igual" nas quatro medidas (Magico pro -3,0% com vai-e-vem 3,6%).
- A regra do veredito (diferenca das medianas > maior vai-e-vem entre rodadas da mesma versao), simulada com
  ruido puro e 3 rodadas: ~3% de "falso lento" por medida (~12% em alguma das 4). Ver se a validacao confirma;
  se acusar lentidao, repetir antes de devolver ao agente.
- Na rodada curta a maquina do GitHub foi MUITO estavel dentro do job (vai-e-vem 0,1% a 2,5%); com isso a regra
  "maior que o vai-e-vem" chamou de "mais rapido" uma diferenca de -0,7% no Magico pro. Pensar num piso minimo
  depois de ver as rodadas de verdade (a conta pode ser refeita sem medir de novo: `--so-juntar` no artifact).
- Rodadas de 20/10: a 1a rodada de cada versao as vezes sai ate ~18% lenta (processador 28-30% ocupado no fundo,
  primeiros ~40 min da maquina). Commit 7e3a006: espera o processador quieto antes de cada rodada + piso de 2% no
  veredito. Refeita a conta nas 4 rodadas e no PC: continua "igual". Rodada curta de conferencia: 39470587102 (success, igual).
- Rodada inteira de conferencia do 7e3a006: 39471738696 (disparada 18:05 UTC; resultado no resumo da rodada).
- Alguem ja usou o filtro: rodada 39396712441 (fase-1 -> conserto-corte-g6-2026-10-13) -> igual.
