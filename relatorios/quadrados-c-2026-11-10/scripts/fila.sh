#!/bin/bash
# fila de medidas pesadas, uma por vez, prioridade baixa
S="C:/Users/fotog/AppData/Local/Temp/claude/195a7ef9582f81cd/2ec556d3-65e0-44bc-b411-991cf466b9a4/scratchpad"
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
export QT_QPA_PLATFORM=offscreen
ESC="D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/Na escola de Jesus - Catecismo explicado com imagens..pdf"
echo '[["'"$ESC"'", 13, "escola_p013"]]' > "$S/lista13.json"
until grep -q "boecio_p033 magico" "$S/out/soltas_depois.log" 2>/dev/null; do sleep 20; done
cd "$S/sim" && $PY ../baixa.py paginas_soltas.py "$S/out/soltas_hoje" "$S/lista13.json" magico_fraco_sem_respeitar > "$S/out/p10_hoje.log" 2>&1
cd "$S/real" && $PY ../baixa.py paginas_soltas.py "$S/out/soltas_depois" "$S/lista13.json" magico_fraco_sem_respeitar > "$S/out/p10_depois.log" 2>&1
cd "$S/real" && $PY ../baixa.py varrer.py "$S/out/livro_depois" "$ESC" melhorar_forte_respeitar > "$S/out/livro_melhorar.log" 2>&1
cd "$S/real" && $PY ../baixa.py varrer.py "$S/out/livro_depois" "$ESC" magico_fraco_respeitar > "$S/out/livro_magico.log" 2>&1
cd "$S/real" && $PY medir_miniaturas.py "$ESC" "$S/out/livro_depois" melhorar_forte_respeitar > "$S/out/mini_melhorar.txt" 2>&1
cd "$S/real" && $PY medir_miniaturas.py "$ESC" "$S/out/livro_depois" magico_fraco_respeitar > "$S/out/mini_magico.txt" 2>&1
cd "$S/out" && $PY "$S/real/medir_pintura.py" "$ESC" "$S/out/livro_depois:melhorar_forte_respeitar" "$S/out/livro_depois:magico_fraco_respeitar" > "$S/out/pintura.txt" 2>&1
echo FIM > "$S/out/fila_fim.txt"
