#!/bin/bash
# Roda livros com o código ANTIGO (f06e0c15, antes do conserto) e compara com o PDF do novo (04-05/11/2026).
# Uso: bash rodar_antigo.sh   (da pasta medidas-9-livros; o novo já rodou com --guardar)
A="/d/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE"
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
ANTIGO=../../../../memoria-pdf-antes
rodar() {  # curto, arquivo
  $PY medir_livro.py --raiz $ANTIGO --livro "$A/$2" --folhas 0 --pasta "trabalho/$1-antigo" --saida "medidas/$1-antigo.json" --guardar > /dev/null 2> "trabalho/$1-antigo.err"
  echo "$1 antigo terminou: $(tail -1 medidas/$1-antigo.log)"
  if [ -f "trabalho/$1-antigo/saida.pdf" ]; then
    $PY comparar_pdfs.py "trabalho/$1-antigo/saida.pdf" "trabalho/$1-novo/saida.pdf" "medidas/$1-comparacao.json" > "trabalho/$1-comparacao.out" 2>&1
    echo "$1 comparacao: $(head -1 trabalho/$1-comparacao.out | grep -o '"tudo_igual": [a-z]*')"
  fi
}
rodar boecio "Sobre a Consolação da Filosofia - Severino Boécio.pdf"
rodar pesel "POINTS d´ANCIENNES BRODERIES ANGLAISES - Louisa F. Pesel.pdf"
rodar siebmacher "Schön Neues Modell Buch - Johann Siebmacher.pdf"
rodar palatino "Giovambattista Palatino cittadino romano.pdf"
echo TUDO PRONTO
