# Onde parei — conferência do corte depois do G6 (13/10/2026)

**Terminado.** O relatório está em `corte-g6.html` (e `.pdf`, `.md`) nesta pasta.

Tarefa: comparar o corte na ordem antiga (cortar e depois endireitar) e na ordem nova
(endireitar e depois cortar, G6, commit `4a7f288`) nas 89 páginas do estudo do "Para revisar"
(as 32 do gabarito estão todas dentro delas) e achar onde piorou, como no Cursus 3.

Ramo: `verif-corte-g6-2026-10-13` (worktree `.claude/worktrees/verif-corte-g6`, saída do `fase-1` em `85ed189`).
Nada do programa foi mudado.

## Feito

- [x] Worktree, junções (`modelos`, `gabarito\paginas`, `gabarito\scantailor-24-09`).
- [x] `scripts/medir.py`: as 87 folhas (89 páginas) medidas nos três preparos (`dados.json`).
- [x] `scripts/classificar.py`: melhorou / igual / piorou pela conta (`classificacao.json`).
- [x] Imagens lado a lado (23) e folhas de contato das 43 páginas que giram (11): todas abertas.
- [x] Causa no código (`scripts/causa.py`, `causa.json`): duas causas, descritas no relatório.
- [x] Projeto antigo (`scripts/projeto_antigo.py`, `projeto-antigo.json`): 40 de 40 idênticas.
- [x] Experiência da cunha repetida (`scripts/experiencia_cunha.py`): prova a causa 1, não serve de conserto.
- [x] Relatório nos três formatos (`scripts/relatorio_final.py`).

## Resultado em uma linha

Piorou de verdade em 6 das 89 (Matemática 32, Cursus 3, Antiphon 260, Antiphon 88: faixa preta larga;
Escola 197: números da margem cortados; Camões 104: fio escuro de 2 mm). Projeto antigo não tem o defeito.

## Para rodar de novo

```
cd D:\programas\EditorImpressao\.claude\worktrees\verif-corte-g6
$env:TEMP="$PWD\_tmp"; $env:TMP="$PWD\_tmp"
$py = "D:\programas\EditorImpressao\.venv\Scripts\python.exe"
$s = "relatorios\conferir\corte-g6-2026-10-13\scripts"
& $py $s\medir.py            # pula o que ja esta no dados.json
& $py $s\classificar.py
& $py $s\relatorio_final.py
```

As páginas prontas a 300 DPI ficam em `_tmp\finais\` (fora do git, 460 MB); o `montar.py`, o `causa.py`
e a experiência leem de lá. O programa de antes do G6 (commit `7485e1b`) está em `_tmp\antes-g6\`,
tirado com `git archive`.

## Não feito

Ver "O que não conferi" no relatório: nenhum livro inteiro, não abri a janela, não rodei a suíte.
