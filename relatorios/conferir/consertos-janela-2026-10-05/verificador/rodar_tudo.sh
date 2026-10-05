#!/usr/bin/env bash
# 32 paginas x 3 filtros, ANTES (aab746f) e AGORA (120e46b), copias limpas, uma de cada vez.
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
V=/d/programas/EditorImpressao/.claude/worktrees/verif-consertos-saida
S=$V/rodadas
mkdir -p $S
for f in preto_e_branco magico_pro melhorar; do
  for lado in antes agora; do
    $PY $V/rodar_verificador.py $V/$lado $f $S/$lado-$f > $S/$lado-$f.log 2>&1
    echo "$lado $f exit=$?"
  done
done
echo FIM
