#!/bin/sh
# Quadrados brancos, origem (10/11/2026): o livro "Na escola de Jesus" inteiro (199 paginas),
# Melhorar "bem forte" e Magico pro "bem fraco", em tres situacoes, uma depois da outra
# (prioridade baixa): antes (ddd4d74a), hoje (d9f80eb4) e hoje com so a mudanca desfeita.
#   sh rodar_livro.sh <pasta de trabalho>
T=$1
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
AQUI=$(cd "$(dirname "$0")" && pwd)
WT=/d/programas/EditorImpressao/.claude/worktrees
for v in "hoje $WT/quadrados-origem X=1" "desfeita $WT/quadrados-origem DESFAZER=1" "antes $WT/qo-antes-etapa1 X=1"; do
  set -- $v
  env $3 $PY "$AQUI/rodar_versao.py" $2 "$T/livros/escola.pdf" todas ambos "$T/livro/$1" > "$T/livro-$1.log" 2>&1
done
echo FIM
