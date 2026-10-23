#!/bin/bash
# Roda rodada_processar.py somas nas 32 páginas do gabarito, uma por processo,
# esperando ter pelo menos 2,5 GB livres antes de cada uma (regra de 20/10/2026).
# Uso (da pasta da worktree):
#   bash relatorios/fase2-novas/scripts/somas_todas.sh <raiz do código> <saida.json>
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
RAIZ="$1"; SAIDA="$2"
export TEMP="$(pwd)/.tmp"; export TMP="$TEMP"; mkdir -p "$TEMP"
PIDS=$($PY -c "import json;print(' '.join(sorted(json.load(open('gabarito/lista.json',encoding='utf-8'))['paginas'])))")
for pid in $PIDS; do
  until [ "$($PY -c 'import psutil;print(int(psutil.virtual_memory().available>2.5*2**30))')" = "1" ]; do sleep 20; done
  $PY relatorios/fase2-novas/scripts/rodada_processar.py --raiz "$RAIZ" somas --saida "$SAIDA" "$pid" > /dev/null 2> "$TEMP/ultimo-erro.txt" || { echo "FALHOU $pid"; tail -3 "$TEMP/ultimo-erro.txt"; }
done
echo "fim $(date +%H:%M:%S)"
