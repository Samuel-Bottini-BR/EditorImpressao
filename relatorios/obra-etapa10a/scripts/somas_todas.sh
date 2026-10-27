#!/bin/bash
# Prova "Desligado de fábrica" (obra etapa 1, 26/10/2026): as 32 páginas do gabarito
# x Original / Preto e branco / Melhorar, cada uma como livro novo pelo
# core.pipeline.processar (script da junção: relatorios/fase2-novas/scripts/rodada_processar.py),
# uma página por processo, esperando 2,5 GB livres antes de cada uma.
# Uso (da pasta da worktree obra-etapa10a):
#   bash relatorios/obra-etapa10a/scripts/somas_todas.sh <raiz do código> <saida.json>
# TEMP fica em relatorios/conferir/obra-etapa10a/tmp (fora do git).
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
RAIZ="$1"; SAIDA="$2"
export TEMP="$(pwd)/relatorios/conferir/obra-etapa10a/tmp"; export TMP="$TEMP"; mkdir -p "$TEMP"
PIDS=$($PY -c "import json;print(' '.join(sorted(json.load(open('gabarito/lista.json',encoding='utf-8'))['paginas'])))")
for pid in $PIDS; do
  until [ "$($PY -c 'import psutil;print(int(psutil.virtual_memory().available>2.5*2**30))')" = "1" ]; do sleep 20; done
  $PY relatorios/fase2-novas/scripts/rodada_processar.py --raiz "$RAIZ" somas --saida "$SAIDA" "$pid" > /dev/null 2> "$TEMP/ultimo-erro-$(basename $SAIDA).txt" || { echo "FALHOU $pid"; tail -3 "$TEMP/ultimo-erro-$(basename $SAIDA).txt"; }
done
echo "fim $(date +%H:%M:%S)"
