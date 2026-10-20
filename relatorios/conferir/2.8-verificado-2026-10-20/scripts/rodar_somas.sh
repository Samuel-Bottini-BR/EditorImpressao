#!/bin/bash
# uma pagina por processo, primeiro o codigo antigo e depois o novo (verificador, 20/10)
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
cd "$(dirname "$0")/.."
for pdf in /d/programas/EditorImpressao/gabarito/paginas/*.pdf; do
  pid=$(basename "$pdf" .pdf)
  for v in antes:b8e9af7 novo:34b3d0e; do
    $PY scripts/somas.py --raiz $W/v28-${v%%:*} --saida trabalho/somas-${v##*:}.json --pid $pid >/dev/null 2>trabalho/erro-$pid-${v##*:}.txt || echo "FALHOU $pid ${v##*:}"
  done
  echo "$pid ok"
done
echo FIM
