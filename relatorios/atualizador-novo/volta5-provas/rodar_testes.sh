#!/bin/bash
# Volta 5: roda os testes do atualizador um arquivo por vez (regra de 19/10), pasta temporaria no D:.
# Uso: rodar_testes.sh <nome da saida> [arquivos...]  (sem arquivos: a lista do atualizador e os test_decisoes*)
cd /d/programas/EditorImpressao/.claude/worktrees/atualizador-novo
NOME=$1; shift
OUT=saida_teste/v5/$NOME.txt
: > $OUT
if [ $# -gt 0 ]; then LISTA="$*"; else
LISTA="tests/test_atualizador_volta5.py tests/test_decisoes_atualizacao_volta5.py tests/test_atualizador_volta4.py tests/test_fases_da_atualizacao.py tests/test_atualizador_d851.py tests/test_atualizador_novo.py tests/test_atualizador_volta2.py tests/test_atualizador_volta3.py tests/test_atualizador_volta3_de_verdade.py tests/test_decisoes_atualizacao.py tests/test_decisoes_ajudante_da_atualizacao.py tests/test_velopack_de_verdade.py tests/test_windows_preparo_do_computador.py tests/test_porteiro_licenca_que_acrescenta.py tests/test_trava_windows.py tests/test_assinatura.py tests/test_windows_peca.py tests/test_windows_janela_de_prova.py $(ls tests/test_decisoes*.py | grep -v -e test_decisoes_atualizacao.py -e test_decisoes_ajudante_da_atualizacao.py -e test_decisoes_atualizacao_volta5.py)"
fi
for f in $LISTA; do
  [ -f "$f" ] || { echo "$f | (não existe neste código)" >> $OUT; continue; }
  n=$(basename $f .py); mkdir -p saida_teste/v5/pytest/$NOME
  r=$(/d/programas/EditorImpressao/.venv/Scripts/python.exe -m pytest $f -q -p no:cacheprovider --basetemp=saida_teste/v5/pytest/$NOME/$n 2>&1 | tail -1)
  echo "$f | $r" >> $OUT
done
echo FIM >> $OUT
