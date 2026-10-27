#!/bin/bash
# somas de fabrica: 32 paginas do gabarito x 3 filtros, uma pagina por processo
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
RAIZ="$1"; SAIDA="$2"
W=/d/programas/EditorImpressao/.claude/worktrees/obra-etapa5
export TEMP="$W/_tmp/somas"; export TMP="$TEMP"; mkdir -p "$TEMP"
cd $W; PIDS=$($PY -c "import json;print(' '.join(sorted(json.load(open('gabarito/lista.json',encoding='utf-8'))['paginas'])))")
for pid in $PIDS; do
  $PY $W/relatorios/obra-etapa5/scripts/rodada_processar.py --raiz "$RAIZ" somas --saida "$SAIDA" "$pid" > /dev/null 2> "$TEMP/erro-$(basename $SAIDA).txt" || { echo "FALHOU $pid"; tail -3 "$TEMP/erro-$(basename $SAIDA).txt"; }
done
echo "fim $(date +%H:%M:%S)"
