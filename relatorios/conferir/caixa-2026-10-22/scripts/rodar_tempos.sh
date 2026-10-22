#!/bin/bash
# verificador 22/10: passada + geracao, antes (c66f28d) x depois (49d1ed3), alternado, um processo por vez
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W='D:/programas/EditorImpressao/.claude/worktrees'
T="$W/vcx22-novo/relatorios/conferir/caixa-2026-10-22"
for livro in egenloff_1a14 marial_300_100; do
  for rep in 1 2; do
    for lado in antes novo; do
      $PY "$T/scripts/tempo_total.py" "$W/vcx22-$lado" "$T/trabalho/$livro.pdf" "$T/trabalho/saida_${livro}_$lado.pdf" "$T/trabalho/tempo_${livro}_${lado}_$rep.json" 2>"$T/trabalho/erro_${livro}_${lado}_$rep.txt" || echo "FALHOU $livro $lado $rep"
      echo "$livro $lado $rep $(date +%H:%M:%S)"
    done
  done
done
echo FIM
