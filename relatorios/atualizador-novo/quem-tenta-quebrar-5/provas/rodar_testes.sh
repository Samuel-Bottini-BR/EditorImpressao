#!/bin/bash
# Quem tenta quebrar 5: os testes do atualizador, da peça do Windows e das decisões, UM ARQUIVO POR VEZ (regra de
# 19/10), no ramo, com a pasta temporária no D:. Fica de fora o test_windows_janela_de_prova.py (ordem da gerente de
# 25/11: nada de janela de verdade; ele não é do atualizador).
cd /d/programas/EditorImpressao/.claude/worktrees/atualizador-novo
OUT=relatorios/atualizador-novo/quem-tenta-quebrar-5/provas/testes-um-por-vez-resultado.txt
: > $OUT
LISTA="tests/test_atualizador_volta5.py tests/test_decisoes_atualizacao_volta5.py tests/test_atualizador_volta4.py tests/test_fases_da_atualizacao.py tests/test_atualizador_d851.py tests/test_atualizador_novo.py tests/test_atualizador_volta2.py tests/test_atualizador_volta3.py tests/test_atualizador_volta3_de_verdade.py tests/test_decisoes_atualizacao.py tests/test_decisoes_ajudante_da_atualizacao.py tests/test_velopack_de_verdade.py tests/test_windows_preparo_do_computador.py tests/test_porteiro_licenca_que_acrescenta.py tests/test_trava_windows.py tests/test_assinatura.py tests/test_windows_peca.py $(ls tests/test_decisoes*.py | grep -v -e test_decisoes_atualizacao.py -e test_decisoes_ajudante_da_atualizacao.py -e test_decisoes_atualizacao_volta5.py)"
for f in $LISTA; do
  n=$(basename $f .py); mkdir -p saida_teste/qtq5/pytest
  r=$(/d/programas/EditorImpressao/.venv/Scripts/python.exe -m pytest $f -q -p no:cacheprovider --basetemp=saida_teste/qtq5/pytest/$n 2>&1 | tail -1)
  echo "$f | $r" >> $OUT
done
echo FIM >> $OUT
