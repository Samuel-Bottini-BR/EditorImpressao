#!/bin/bash
# Roda os 9 livros com o código NOVO, um por vez, do maior para o menor (04/11/2026).
# Uso: bash rodar_novo.sh   (da pasta medidas-9-livros)
A="/d/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE"
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
rodar() {  # curto, arquivo, folhas (0 = inteiro), guardar
  g=""; [ "$4" = "sim" ] && g="--guardar"
  $PY medir_livro.py --raiz ../../.. --livro "$A/$2" --folhas $3 --pasta "trabalho/$1-novo" --saida "medidas/$1-novo.json" $g > /dev/null 2> "trabalho/$1-novo.err"
  echo "$1 terminou: $(tail -1 medidas/$1-novo.log)"
}
mkdir -p medidas trabalho
rodar marial "Marial de sermoens - Frei Balthasar Paez. (1).pdf" 500 nao
rodar graduale "Graduale - Saeculum XIV.pdf" 300 nao
rodar rhetorica "Rhetorica Christiana -  Fray Diego Valadés.pdf" 0 nao
rodar escola "Na escola de Jesus - Catecismo explicado com imagens..pdf" 0 sim
rodar horas "Livro de Horas - Luís XIV.pdf" 0 sim
rodar palatino "Giovambattista Palatino cittadino romano.pdf" 0 sim
rodar siebmacher "Schön Neues Modell Buch - Johann Siebmacher.pdf" 0 sim
rodar pesel "POINTS d´ANCIENNES BRODERIES ANGLAISES - Louisa F. Pesel.pdf" 0 sim
rodar boecio "Sobre a Consolação da Filosofia - Severino Boécio.pdf" 0 sim
echo TUDO PRONTO
