#!/bin/bash
# Roda cada arquivo de teste sozinho. Verificador do item 2.1 (dividir), 06/10.
cd /d/programas/EditorImpressao/.claude/worktrees/geometria
V=relatorios/conferir/dividir-2026-10-06/verificador
W='D:\programas\EditorImpressao\.claude\worktrees\geometria\relatorios\conferir\dividir-2026-10-06\verificador'
export TEMP="$W\trabalho\tmp"
export TMP="$TEMP"
export LOCALAPPDATA="$W\dados_teste\pytest_local"
export USERPROFILE="$W\dados_teste\pytest_home"
mkdir -p "$V/dados_teste/pytest_local" "$V/dados_teste/pytest_home"
LOG=$V/trabalho/pytest_partes.log
: > $LOG
echo "HEAD $(git rev-parse --short HEAD) $(date +%H:%M:%S)" >> $LOG
for f in ${@:-tests/test_*.py}; do
  ini=$(date +%s)
  r=$(/d/programas/EditorImpressao/.venv/Scripts/python.exe -m pytest "$f" -q -p no:cacheprovider 2>&1 | tail -1)
  echo "$f | $(( $(date +%s) - ini ))s | $r" >> $LOG
done
echo "FIM $(date +%H:%M:%S)" >> $LOG
