#!/bin/bash
# verificador, 21/10: "Parece em branco" em 4 livros inteiros, codigo antigo (fb9de49) e novo (4c53152)
PY=/d/programas/EditorImpressao/.venv/Scripts/python.exe
W=/d/programas/EditorImpressao/.claude/worktrees
cd "$(dirname "$0")/.."
for pdf in "D:/Livros para editar/Gladstone_Chaves_de_Melo_Novo_Manual_de_Análise_Sintática_1954.pdf" "D:/Livros para editar/Egenloff15271880ModelbuchWHZ_231103_053749.pdf" "D:/programas/EditorImpressao-arquivos/TESTES EDITOR DE IMPRESSAO/LIVROS PARA TESTE/Sobre a Consolação da Filosofia - Severino Boécio.pdf" "D:/Livros para editar/HISTÓRIA/Luiz de Camões levantando o seu monumento ou A Historia de Portugal justificada pelos Lusiadas.pdf"; do
  for v in antes:vcs-novo novo:vcs-c97; do
    PYTHONIOENCODING=utf-8 $PY scripts/contar_em_branco.py --raiz $W/${v##*:} --pdf "$pdf" --saida trabalho/em-branco-${v%%:*}.json 2>>trabalho/erros.txt || echo "FALHOU $pdf ${v%%:*}"
  done
done
echo FIM
