#!/bin/bash
# Roda os arquivos de teste dados, UM POR VEZ (regra de 19/10: no PC, um
# arquivo por vez), com TEMP e --basetemp dentro da worktree (fora do git).
# Uso (da pasta da worktree): bash relatorios/obra-etapa10a/scripts/rodar_testes.sh saida.txt tests/a.py tests/b.py ...
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
SAIDA="$1"; shift
BASE="$(pwd)/relatorios/conferir/obra-etapa10a/tmp"
export TEMP="$BASE" TMP="$BASE"; mkdir -p "$BASE"
: > "$SAIDA"
for f in "$@"; do
  nome=$(basename "$f" .py)
  r=$($PY -m pytest "$f" -q -p no:cacheprovider --basetemp="$BASE/pt-$nome" 2>&1 | tail -15)
  echo "== $f: $(echo "$r" | tail -1)" >> "$SAIDA"
  echo "$r" | grep -E "^FAILED|^ERROR" >> "$SAIDA"
done
echo "fim $(date +%H:%M:%S)" >> "$SAIDA"
