#!/bin/bash
# Roda os antes/depois dos itens, um processo por item, esperando ter memória
# livre (2,5 GB) antes de cada um. Uso (da worktree):
#   bash relatorios/fase2-novas/scripts/antes_depois_todos.sh <raiz do código>
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
RAIZ="$1"
export TEMP="$(pwd)/.tmp"; export TMP="$TEMP"; mkdir -p "$TEMP"
for item in 2.4 2.17 2.10 2.18 2.6; do
  until [ "$($PY -c 'import psutil;print(int(psutil.virtual_memory().available>2.5*2**30))')" = "1" ]; do sleep 20; done
  echo "== $item $(date +%H:%M:%S)"
  $PY relatorios/fase2-novas/scripts/antes_depois.py --raiz "$RAIZ" "$item" > "$TEMP/ad-$item.txt" 2>&1 || { echo "FALHOU $item"; tail -5 "$TEMP/ad-$item.txt"; }
done
echo "fim $(date +%H:%M:%S)"
