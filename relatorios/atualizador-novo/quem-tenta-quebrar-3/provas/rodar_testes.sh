#!/bin/bash
# Roda cada arquivo de teste sozinho (um por vez), com a pasta temporaria no D:, e anota o fim de cada um.
cd /d/programas/EditorImpressao/.claude/worktrees/atualizador-novo
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
OUT=saida_teste/qtq3/testes-resultado.txt
mkdir -p saida_teste/qtq3/pt; : > $OUT
export PROGRAMDATA='D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\saida_teste\qtq3\programdata-falso'
for f in tests/test_atualizador_volta3.py tests/test_atualizador_d851.py tests/test_fases_da_atualizacao.py tests/test_atualizador_novo.py tests/test_atualizador_volta2.py tests/test_atualizador_volta3_de_verdade.py tests/test_windows_preparo_do_computador.py tests/test_velopack_de_verdade.py tests/test_porteiro_licenca_que_acrescenta.py tests/test_trava_windows.py tests/test_windows_peca.py tests/test_conferencias_pacote.py tests/test_conferencias_codigo.py tests/test_conferencias_excecoes.py tests/test_decisoes*.py; do
  n=$(basename $f .py)
  s=$(date +%s)
  r=$(timeout 1500 $PY -m pytest $f -q -p no:cacheprovider --basetemp=saida_teste/qtq3/pt/$n 2>&1 | tail -3 | tr '\n' ' ')
  e=$(date +%s)
  echo "$f | $((e-s)) s | $r" >> $OUT
done
echo FIM >> $OUT
