#!/bin/bash
# a medida da investigacao da origem (relatorio-completo, quadrados-origem), no programa consertado
S="C:/Users/fotog/AppData/Local/Temp/claude/195a7ef9582f81cd/2ec556d3-65e0-44bc-b411-991cf466b9a4/scratchpad"
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
L="D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE"
ESC="$L/Na escola de Jesus - Catecismo explicado com imagens..pdf"; HOR="$L/Livro de Horas - Luís XIV.pdf"
DEP=/d/programas/EditorImpressao/.claude/worktrees/quadrados-c; ANT=/d/programas/EditorImpressao/.claude/worktrees/obra-juncao
until [ -f "$S/out/fila_fim.txt" ]; do sleep 20; done
cd "$S/origem"
$PY rodar_versao.py $DEP "$ESC" 13,18,29,36,51,66,97,119 ambos "$S/origem/saida/escola/depois" > "$S/origem/log_depois.txt" 2>&1
$PY rodar_versao.py $DEP "$HOR" 47 ambos "$S/origem/saida/horas/depois" >> "$S/origem/log_depois.txt" 2>&1
RESPEITAR=0 $PY rodar_versao.py $DEP "$ESC" 13 magico_pro "$S/origem/saida/escola/depois_p10" >> "$S/origem/log_depois.txt" 2>&1
RESPEITAR=0 LIMPAR=1 $PY rodar_versao.py $DEP "$ESC" 13 magico_pro "$S/origem/saida/escola/depois_p10_auto" >> "$S/origem/log_depois.txt" 2>&1
RESPEITAR=0 $PY rodar_versao.py $ANT "$ESC" 13 magico_pro "$S/origem/saida/escola/antes_p10" >> "$S/origem/log_depois.txt" 2>&1
$PY rodar_versao.py $ANT "$ESC" 13 ambos "$S/origem/saida/escola/antes" >> "$S/origem/log_depois.txt" 2>&1
$PY medir.py "$ESC" "$S/origem/medida_escola.json" "$S/origem/saida/escola/depois:melhorar" "$S/origem/saida/escola/depois:magico_pro" "$S/origem/saida/escola/depois_p10:magico_pro" "$S/origem/saida/escola/depois_p10_auto:magico_pro" "$S/origem/saida/escola/antes_p10:magico_pro" "$S/origem/saida/escola/antes:melhorar" "$S/origem/saida/escola/antes:magico_pro" >> "$S/origem/log_depois.txt" 2>&1
$PY medir.py "$HOR" "$S/origem/medida_horas.json" "$S/origem/saida/horas/depois:melhorar" "$S/origem/saida/horas/depois:magico_pro" >> "$S/origem/log_depois.txt" 2>&1
echo FIM > "$S/origem/fim.txt"
