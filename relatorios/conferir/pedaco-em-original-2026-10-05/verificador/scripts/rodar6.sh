#!/usr/bin/env bash
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
S="C:/Users/fotog/AppData/Local/Temp/claude/d--programas/35d489db-9216-4d07-a049-6468d4552ad0/scratchpad/v"
IDS=escola_p007,opusmajus_p020,horas_p011,palatino_p057,graduale_p221,siebmacher_p007
mkdir -p $S/rodadas
for f in original preto_e_branco melhorar magico_pro; do
  for lado in antes agora; do
    $PY $S/rodar_32.py $S/$lado $f $S/rodadas/$lado-$f $IDS > $S/rodadas/$lado-$f.log 2>&1
    echo "$lado $f exit=$?"
  done
done
echo FIM
