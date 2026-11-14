#!/bin/sh
# Perguntas B1 e B3 (14/11/2026): a capa do Gradus (CÓPIA) desenhada pela conta do PDF, com a versão de
# teste, sem janela. Uma coisa por vez, prioridade baixa (capa_b.py baixa a dela).
#   sh rodar_capa.sh
AQUI=$(cd "$(dirname "$0")" && pwd)
R=$(dirname "$AQUI")
W=$(cd "$R/../.." && pwd)                      # a raiz da cópia do programa (perguntas-prints)
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
L=$R/_livros/gradus.pdf
C=$R/_cru/capa
$PY "$AQUI/capa_b.py" "$W" "$L" 1 "$C/hoje" original pb+resp1 pb+samuel+resp0 pb+samuel+resp0+letras1
# os retângulos brancos tirados (só neste processo): como a capa sai depois do conserto parado
SEM_QUADROS=1 $PY "$AQUI/capa_b.py" "$W" "$L" 1 "$C/sem_quadros" pb+resp1 pb+samuel+resp0 pb+samuel+resp0+letras1
# opção (a) da B3: o nome achado em cima da capa não recorta a capa (só neste processo)
SEM_LETRA_NA_GRAVURA=1 $PY "$AQUI/capa_b.py" "$W" "$L" 1 "$C/sem_letra" pb+resp1 pb+samuel+resp0+letras1
echo FIM
