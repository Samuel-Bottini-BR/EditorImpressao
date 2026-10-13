# Onde parei — conferência do conserto do corte do G6 (13/10/2026)

Tarefa: conferir com os olhos e com a velocidade o conserto do implementador
(ramo `origin/conserto-corte-g6-2026-10-13`, commit `d97b937`) e preparar os quadros para o Samuel.
Não mudo código e não marco nada como aprovado.

Ramo desta conferência: `verif-corte-g6-2026-10-13` (worktree `.claude/worktrees/verif-corte-g6`).
Cópia do programa com o conserto, só para rodar: `.claude/worktrees/verif-conserto-corte-g6`
(HEAD solto em `d97b937`, com a junção `modelos`).

## Passos

- [ ] 1. Medir de novo, por minha conta, o livro novo nas 89 páginas com o programa de hoje e com o do
      conserto (`scripts/medir_conserto.py` → `dados-hoje.json`, `dados-conserto.json`; páginas prontas em
      `_tmp/finais-hoje` e `_tmp/finais-conserto`).
- [ ] 2. Imagens das três versões (`scripts/quadros.py` → `img/cg6-*.jpg`) e abrir todas.
- [ ] 3. Velocidade: `velocidade/rodar_uma.ps1`, 2 rodadas de cada, alternadas (antes-1, depois-1, antes-2,
      depois-2), cerca de 13 minutos cada. "Antes" = worktree `velocidade-antes` em `origin/fase-1`.
- [ ] 4. `conferencia.json` (resumo + quadros) e o relatório nos três formatos.

## Para continuar

Ver a lista acima: o que estiver marcado já está no git (commit e push a cada parte).
