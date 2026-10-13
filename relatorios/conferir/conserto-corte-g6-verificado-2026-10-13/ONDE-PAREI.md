# Onde parei — conferência do conserto do corte do G6 (13/10/2026)

**Terminado.** O relatório está em `conserto-corte-g6-verificado.html` (e `.pdf`, `.md`); o resumo e os
quadros para a página do Samuel estão em `conferencia.json`.

Tarefa: conferir com os olhos e com a velocidade o conserto do implementador
(ramo `origin/conserto-corte-g6-2026-10-13`, commit `d97b937`) e preparar os quadros para o Samuel.
Não mudei código e não marquei nada como aprovado.

Ramo desta conferência: `verif-corte-g6-2026-10-13` (worktree `.claude/worktrees/verif-corte-g6`).
Cópia do programa com o conserto, só para rodar: `.claude/worktrees/verif-conserto-corte-g6`
(HEAD solto em `d97b937`, com a junção `modelos`; fui eu que criei).
A worktree `velocidade-antes` foi levada para `origin/fase-1` (`1d37f8f`), como pedido.

## Passos

- [x] 1. Medida independente do livro novo nas 89 páginas, programa de hoje contra o do conserto
      (`scripts/medir_conserto.py` → `dados-hoje.json`, `dados-conserto.json`): 79 idênticas, 10 mudam.
- [x] 2. Imagens das três versões (`scripts/quadros.py` → `img/cg6-*.jpg`, 33 imagens): todas abertas.
- [x] 3. Velocidade (`velocidade/`): 5 rodadas (a primeira atrapalhada por outro agente, por isso uma terceira
      do programa de hoje), mais a medida direta nas 10 páginas do teste.
- [x] 4. Livro começado antes, com o conserto: 40 de 40 idênticos (`scripts/projeto_antigo_no_conserto.py`).
- [x] 5. Testes de máquina do corte e da ordem do preparo no ramo: 70 passaram.
- [x] 6. `conferencia.json` e o relatório nos três formatos (`scripts/relatorio_conserto.py`).

## Resultado em uma linha

O conserto tira a faixa preta nas cinco páginas sem cortar nada impresso e sem mexer no resto; fica para o
Samuel decidir o Pesel 21 (cartão escuro cortado rente, legenda a 1 ou 2 mm da borda de baixo).

## Para rodar de novo

```
cd D:\programas\EditorImpressao\.claude\worktrees\verif-corte-g6
$env:TEMP="$PWD\_tmp"; $env:TMP="$PWD\_tmp"
$py = "D:\programas\EditorImpressao\.venv\Scripts\python.exe"
$d = "relatorios\conferir\conserto-corte-g6-verificado-2026-10-13"
& $py $d\scripts\medir_conserto.py --raiz D:\programas\EditorImpressao\.claude\worktrees\verif-conserto-corte-g6 --nome conserto
& $py $d\scripts\medir_conserto.py --raiz D:\programas\EditorImpressao\.claude\worktrees\verif-corte-g6 --nome hoje
& $py $d\scripts\quadros.py
powershell -File $d\velocidade\rodar_uma.ps1 -braco antes -nome antes-4     # uma rodada (13 minutos)
& $py $d\velocidade\juntar.py
& $py $d\scripts\relatorio_conserto.py
```

As páginas prontas a 300 DPI ficam em `_tmp\finais`, `_tmp\finais-hoje` e `_tmp\finais-conserto` (fora do git).
