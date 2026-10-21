#!/bin/bash
# verificador, 21/10 (item 2.9): somas de fabrica do codigo novo (0f4ee58), uma pagina por processo.
# O lado antigo (b8e9af7) e o mesmo que medi no 2.8 (trabalho/somas-b8e9af7.json, copiado de la).
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
cd "$(dirname "$0")/.."
for pdf in /d/programas/EditorImpressao/gabarito/paginas/*.pdf; do
  pid=$(basename "$pdf" .pdf)
  $PY scripts/somas.py --raiz $W/v29-novo --saida trabalho/somas-0f4ee58.json --pid $pid >/dev/null 2>trabalho/erro-$pid.txt || echo "FALHOU $pid"
  echo "$pid ok"
done
echo FIM
