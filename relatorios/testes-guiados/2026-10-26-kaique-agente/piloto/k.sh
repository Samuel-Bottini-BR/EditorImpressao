#!/bin/bash
T="C:/Users/fotog/AppData/Local/Temp/claude/C--Users-fotog/56a8699a-7d20-418a-a239-ac3228d49249/scratchpad/kaique-trabalho"
cd "$T" && PYTHONIOENCODING=utf-8 "D:/programas/EditorImpressao/.venv/Scripts/python.exe" "D:/programas/EditorImpressao/.claude/worktrees/teste-kaique/relatorios/testes-guiados/2026-10-26-kaique-agente/piloto/kq.py" "$@" | sed 's#^.*kaique-trabalho.telas.#  T/#'
