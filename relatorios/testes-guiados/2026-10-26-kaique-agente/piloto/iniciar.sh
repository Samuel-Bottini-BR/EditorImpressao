#!/bin/bash
cd "D:/programas/EditorImpressao/.claude/worktrees/teste-kaique"
T="C:/Users/fotog/AppData/Local/Temp/claude/C--Users-fotog/56a8699a-7d20-418a-a239-ac3228d49249/scratchpad/kaique-trabalho"
export LOCALAPPDATA="$T/dados" TEMP="$T" TMP="$T"
rm -f "$T/fila/cmd.json" "$T/fila/res.json"
"D:/programas/EditorImpressao/.venv/Scripts/python.exe" "relatorios/testes-guiados/2026-10-26-kaique-agente/piloto/piloto.py" "$T" "D:/programas/EditorImpressao/.claude/worktrees/teste-kaique" >> "$T/saida.txt" 2>&1
