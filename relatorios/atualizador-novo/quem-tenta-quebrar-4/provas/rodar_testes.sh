#!/bin/bash
# Roda os testes um arquivo por vez (regra de 19/10), pasta temporaria no D:.
cd /d/programas/EditorImpressao/.claude/worktrees/atualizador-novo
OUT=saida_teste/qtq4/testes-resultado.txt
: > $OUT
LISTA="tests/test_atualizador_volta4.py tests/test_fases_da_atualizacao.py tests/test_atualizador_d851.py tests/test_atualizador_novo.py tests/test_atualizador_volta2.py tests/test_atualizador_volta3.py tests/test_atualizador_volta3_de_verdade.py tests/test_decisoes_atualizacao.py tests/test_decisoes_ajudante_da_atualizacao.py tests/test_velopack_de_verdade.py tests/test_windows_preparo_do_computador.py tests/test_porteiro_licenca_que_acrescenta.py tests/test_trava_windows.py tests/test_assinatura.py tests/test_windows_peca.py tests/test_windows_janela_de_prova.py tests/test_conferencias_pacote.py tests/test_conferencias_codigo.py tests/test_conferencias_excecoes.py tests/test_publicar_versao.py tests/test_pasta_das_ferramentas.py $(ls tests/test_decisoes*.py | grep -v -e test_decisoes_atualizacao.py -e test_decisoes_ajudante_da_atualizacao.py)"
for f in $LISTA; do
  n=$(basename $f .py)
  r=$(/d/programas/EditorImpressao/.venv/Scripts/python.exe -m pytest $f -q -p no:cacheprovider --basetemp=saida_teste/qtq4/pytest/$n 2>&1 | tail -1)
  echo "$f | $r" >> $OUT
done
echo FIM >> $OUT
