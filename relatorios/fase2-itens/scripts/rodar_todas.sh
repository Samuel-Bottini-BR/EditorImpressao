#!/bin/bash
# Roda rodada_gabarito.py nas 32 paginas do gabarito, uma por processo, esperando
# ter pelo menos 2,5 GB livres antes de cada uma (regra da gerente, 20/10/2026).
# Uso (da pasta da worktree):
#   bash relatorios/fase2-itens/scripts/rodar_todas.sh --hashes relatorios/fase2-itens/2.8/somas-novo.json
#   bash relatorios/fase2-itens/scripts/rodar_todas.sh --item 2.8 --pasta relatorios/fase2-itens/2.8/imagens
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
PIDS=$($PY -c "import json;print(' '.join(sorted(json.load(open('gabarito/lista.json',encoding='utf-8'))['paginas'])))")
for pid in $PIDS; do
  until [ "$($PY -c 'import psutil;print(int(psutil.virtual_memory().available>2.5*2**30))')" = "1" ]; do sleep 20; done
  echo "== $pid $(date +%H:%M:%S)"
  $PY relatorios/fase2-itens/scripts/rodada_gabarito.py "$pid" "$@" > /dev/null 2> "relatorios/fase2-itens/ultimo-erro.txt" || { echo "FALHOU $pid"; cat relatorios/fase2-itens/ultimo-erro.txt | tail -3; }
done
echo "fim $(date +%H:%M:%S)"
