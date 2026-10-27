#!/bin/bash
# Roda os arquivos de teste dados, UM POR VEZ (regra de 19/10: no PC, um arquivo por vez),
# com TEMP e --basetemp dentro da worktree (_tmp/, fora do git). Obra 26/10, etapa 4.
# Uso (da pasta da worktree): bash relatorios/obra-etapa4/scripts/rodar_testes.sh saida.txt tests/a.py ...
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
SAIDA="$1"; shift
BASE="$(pwd)/_tmp/testes"
export TEMP="$BASE" TMP="$BASE" QT_QPA_PLATFORM=offscreen; mkdir -p "$BASE"
: > "$SAIDA"
for f in "$@"; do
  nome=$(basename "$f" .py)
  r=$($PY -m pytest "$f" -q -p no:cacheprovider --basetemp="$BASE/pt-$nome" 2>&1 | tail -25)
  echo "== $f: $(echo "$r" | tail -1)" >> "$SAIDA"
  echo "$r" | grep -E "^FAILED|^ERROR" >> "$SAIDA"
done
echo "fim $(date +%H:%M:%S)" >> "$SAIDA"
