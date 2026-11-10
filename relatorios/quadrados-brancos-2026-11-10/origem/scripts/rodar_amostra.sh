#!/bin/sh
# Quadrados brancos, origem (10/11/2026): as mesmas paginas, com as mesmas escolhas, em cada
# versao do programa, uma depois da outra (uma coisa pesada por vez, prioridade baixa).
#   sh rodar_amostra.sh <pasta de trabalho>   (com livros/escola.pdf, horas.pdf, boecio.pdf)
# Versoes: v0928 = 28/09 (a329166d, conserto do bug 202, Fase 1); antes = 26/10 (ddd4d74a, o
# programa de antes da obra, igual ao fase-1); hoje = d9f80eb4; desfeita = hoje com so a mudanca
# da etapa 1 desfeita; conserto_c = hoje com o conserto C do verificador.
T=$1
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
AQUI=$(cd "$(dirname "$0")" && pwd)
WT=/d/programas/EditorImpressao/.claude/worktrees
ESCOLA=13,18,29,36,51,66,97,119
rodar() {   # nome raiz livro paginas [VAR=valor]
  nome=$1; raiz=$2; livro=$3; pags=$4; shift 4
  env "$@" $PY "$AQUI/rodar_versao.py" "$raiz" "$T/livros/$livro.pdf" "$pags" ambos "$T/saida/$livro/$nome" 2>&1 \
    | grep -v Warning | sed "s/^/$livro $nome: /"
}
for v in "v0928 $T/versoes/0928 X=1" "antes $WT/qo-antes-etapa1 X=1" "hoje $WT/quadrados-origem X=1" \
         "desfeita $WT/quadrados-origem DESFAZER=1" "conserto_c $WT/quadrados-origem CONSERTO_C=1"; do
  set -- $v
  rodar $1 $2 escola $ESCOLA $3
  rodar $1 $2 horas 47 $3
  rodar $1 $2 boecio 3,7,8,22,33 $3
done
echo FIM
