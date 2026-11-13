#!/bin/sh
# Quadrados na capa (13/11/2026): todas as escolhas em cada capa, com a versao de teste (hoje) e
# com o conserto C (quadrados-c). Uma coisa pesada por vez, prioridade baixa (rodar_capa.py baixa
# a prioridade dele). Sem janela.
#   sh rodar_matriz.sh
W=/d/programas/EditorImpressao/.claude/worktrees
AQUI=$(cd "$(dirname "$0")" && pwd)
R=$(dirname "$AQUI")
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
L=$W/quadrados-capa/_tmp/livros
MAO="original pb+resp1 pb+resp0 pb+resp1+cinza1 pb+resp0+cinza1 pb+letras1 pb+letras_tudo pb+samuel+resp0 pb+samuel+resp0+letras1 melhorar+resp1 melhorar+resp0 magico+resp1 magico+resp0 fundo"
AUTO="auto+pb+resp1 auto+pb+resp0 auto+pb+letras1 auto+pb+resp0+cinza1 auto+melhorar+resp1 auto+melhorar+resp0 auto+magico+resp1 auto+magico+resp0"
for versao in quadrados-capa quadrados-c; do
  for caso in "gradus 1" "escola 1" "matematica 1" "pesel 1" "destino 1"; do
    set -- $caso
    livro=$1; pag=$2
    saida=$R/_trabalho/matriz/$versao/$livro
    $PY "$AQUI/rodar_capa.py" $W/$versao $L/$livro.pdf $pag $saida $MAO 2>&1 | grep -v -i warning | sed "s/^/$versao $livro mao: /"
    $PY "$AQUI/rodar_capa.py" $W/$versao $L/$livro.pdf $pag $saida $AUTO 2>&1 | grep -v -i warning | sed "s/^/$versao $livro auto: /"
    $PY "$AQUI/medir_quadros.py" $saida > /dev/null 2>&1
  done
done
echo FIM
