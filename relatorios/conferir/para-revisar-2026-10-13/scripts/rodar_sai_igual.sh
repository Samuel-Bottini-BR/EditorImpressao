#!/bin/sh
# Verificador, 20/10/2026: refaz a prova "sai igual" do implementador por conta propria, em pasta minha
# (analise com o fase-1 b6fd091; processa com o fase-1 e com o ramo adf4e69), uma etapa por vez.
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
S=$W/verif-para-revisar/relatorios/conferir/para-revisar-2026-10-13/scripts/sai_igual_copia_do_implementador.py
P=$W/verif-para-revisar/relatorios/conferir/para-revisar-2026-10-13/trabalho/sai-igual
export PYTHONIOENCODING=utf-8
for i in 1 2 3; do $PY $S analisar $W/fase1-b6fd091 $P; done
for i in 1 2 3; do $PY $S processar $W/fase1-b6fd091 $P fase1; done
for i in 1 2 3; do $PY $S processar $W/verif-para-revisar $P ramo; done
echo TUDO-FIM
