#!/bin/bash
# verificador, 21/10 (caixa do conteudo, partes 1 e 2): somas de fabrica, fase-1 31a9253 x ramo 4120c68, uma pagina por processo
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
cd "$(dirname "$0")/.."
for pdf in /d/programas/EditorImpressao/gabarito/paginas/*.pdf; do
  pid=$(basename "$pdf" .pdf)
  for v in antes:31a9253 novo:4120c68; do
    $PY scripts/somas.py --raiz $W/vcx-${v%%:*} --saida trabalho/somas-${v##*:}.json --pid $pid >/dev/null 2>trabalho/erro-$pid-${v##*:}.txt || echo "FALHOU $pid ${v##*:}"
  done
  echo "$pid ok"
done
echo FIM
