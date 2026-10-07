#!/bin/bash
# Roda o Python do projeto SEMPRE com a pasta de dados e o TEMP do verificador-2 (nunca a do Samuel).
V=/d/programas/EditorImpressao/.claude/worktrees/geometria/relatorios/conferir/dividir-2026-10-06/verificador-2
W="$(cd $V; pwd -W)"
export LOCALAPPDATA="$W/dados_teste/x" USERPROFILE="$W/dados_teste/home" TEMP="$W/trabalho/tmp" TMP="$W/trabalho/tmp"
exec /d/programas/EditorImpressao/.venv/Scripts/python.exe "$@"
