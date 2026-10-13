# Onde parei — conferência do corte depois do G6 (13/10/2026)

Tarefa: comparar o corte na ordem antiga (cortar e depois endireitar) e na ordem nova
(endireitar e depois cortar, G6, commit `4a7f288`) nas 89 páginas do estudo do "Para revisar"
(as 32 do gabarito estão todas dentro delas) e achar onde piorou, como no Cursus 3.

Ramo: `verif-corte-g6-2026-10-13` (worktree `.claude/worktrees/verif-corte-g6`, saída do `fase-1` em `85ed189`).

## Como rodar de novo

```
cd D:\programas\EditorImpressao\.claude\worktrees\verif-corte-g6
$env:TEMP="$PWD\_tmp"; $env:TMP="$PWD\_tmp"
D:\programas\EditorImpressao\.venv\Scripts\python.exe relatorios\conferir\corte-g6-2026-10-13\scripts\medir.py
```

O `medir.py` pula as páginas que já estão em `dados.json` e grava a cada página. As páginas prontas
(JPEG, 300 DPI) ficam em `_tmp\finais\` (fora do git).

## Feito

- [x] Worktree, junções (`modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`).
- [x] `scripts/medir.py` pronto e testado no Cursus 3: reproduz o achado (faixa na beirada 0,5% na
      ordem antiga, 7,4% na nova).

## Falta

- [ ] Rodar o `medir.py` nas 87 folhas (89 páginas).
- [ ] Separar em melhorou / igual / piorou (`scripts/classificar.py`).
- [ ] Imagens lado a lado das que pioraram e das 5 que mais melhoraram; abrir todas.
- [ ] Causa no código (Cursus 3 e mais duas).
- [ ] Projeto antigo: o defeito aparece?
- [ ] Relatório nos três formatos (`corte-g6.md`, `.html`, `.pdf`).
