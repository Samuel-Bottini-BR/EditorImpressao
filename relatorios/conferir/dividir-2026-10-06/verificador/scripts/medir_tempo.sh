#!/bin/bash
# Verificador 2.1: tempo de abrir (analisar_projeto) e processar 10 paginas, alternando antes/depois.
V=/d/programas/EditorImpressao/.claude/worktrees/geometria/relatorios/conferir/dividir-2026-10-06/verificador
cd $V
W=$(pwd -W)
export LOCALAPPDATA="$W\dados_teste\tempo_local"; export TEMP="$W\trabalho\tmp"; export TMP="$TEMP"
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
T=/d/programas/EditorImpressao/.claude/worktrees/geometria/relatorios/conferir/dividir-2026-10-06/scripts/tempo.py
H="D:\Livros para editar\Tractatus Dogmatici (vol. 3)_  - Hugon, Édouard, O.P._7207.pdf"
E="D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE\Na escola de Jesus - Catecismo explicado com imagens..pdf"
for r in 1 2 3; do
  $PY $T trabalho/misto "$H" antigo trabalho/tempos/hugon_antes_antigo_$r.json
  $PY $T trabalho/novo "$H" scantailor trabalho/tempos/hugon_novo_scantailor_$r.json
  $PY $T trabalho/novo "$H" programa trabalho/tempos/hugon_novo_programa_$r.json
  $PY $T trabalho/novo "$H" nao trabalho/tempos/hugon_novo_nao_$r.json
done
for r in 1 2; do
  $PY $T trabalho/misto "$E" antigo trabalho/tempos/escola_antes_antigo_$r.json
  $PY $T trabalho/novo "$E" scantailor_sobra trabalho/tempos/escola_novo_scantailor_sobra_$r.json
  $PY $T trabalho/novo "$E" programa trabalho/tempos/escola_novo_programa_$r.json
done
echo FIM
