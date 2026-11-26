"""Conta as linhas de código dos três arquivos do atualizador (volta 5, 25/11/2026): sem comentário, sem docstring e
sem linha em branco (o mesmo critério da tabela "Tamanho" da volta 4). Lê o arquivo de um commit pelo `git show`.

Como conta: pelo `tokenize` do Python, uma linha conta se tem pelo menos um pedaço que não é comentário, quebra de
linha, recuo ou texto solto que seja só uma docstring (um texto sozinho como instrução: o do módulo, da classe, da
função). Uso: python contar_linhas.py <pasta do ramo> <commit> [<commit> ...]
"""
from __future__ import annotations

import ast
import io
import subprocess
import sys
import tokenize

ARQUIVOS = ("atualizacao.py", "core/fases_da_atualizacao.py", "core/conversa_com_o_velopack.py")


def linhas_de_docstring(fonte: str) -> set[int]:
    """As linhas ocupadas por textos soltos (docstrings e textos que são só uma instrução)."""
    linhas: set[int] = set()
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str):
            linhas |= set(range(no.lineno, no.end_lineno + 1))
    return linhas


def contar(fonte: str) -> int:
    """Quantas linhas têm código de verdade."""
    docs = linhas_de_docstring(fonte)
    com_codigo: set[int] = set()
    ignorar = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
               tokenize.ENDMARKER, tokenize.ENCODING}
    for t in tokenize.generate_tokens(io.StringIO(fonte).readline):
        if t.type in ignorar:
            continue
        for n in range(t.start[0], t.end[0] + 1):
            if n not in docs:
                com_codigo.add(n)
    return len(com_codigo)


def main() -> None:
    pasta, commits = sys.argv[1], sys.argv[2:]
    for commit in commits:
        total = 0
        partes = []
        for arq in ARQUIVOS:
            if commit == "trabalho":
                fonte = open(f"{pasta}/{arq}", encoding="utf-8").read()
            else:
                fonte = subprocess.run(["git", "-C", pasta, "show", f"{commit}:{arq}"], capture_output=True,
                                       text=True, encoding="utf-8", check=True).stdout
            n = contar(fonte)
            total += n
            partes.append(f"{arq} {n}")
        print(f"{commit}: " + " | ".join(partes) + f" | total {total}")


if __name__ == "__main__":
    main()
