"""Verificador, 14/11/2026 (D-687): procura em ui/ textos que vão para a tela com código interno.
Lê cada arquivo .py de ui/ com ast, pega as strings que NÃO são docstring e não estão em
comentário, e acusa as que têm um padrão de código: D-123, G2, B5, P4, (2.11), "etapa 4", "obra",
"D-014". Saída: uma linha por achado (arquivo:linha: texto)."""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1])
PADROES = [
    (re.compile(r"\bD-\d{2,4}\b"), "número de decisão"),
    (re.compile(r"\(([A-Z]{1,2}\d{1,2})\)"), "código entre parênteses"),
    (re.compile(r"\b(?:G|B|P|O|F|V|M|S|C|A|H|N|R|T|Z)\d{1,2}\b"), "letra+número"),
    (re.compile(r"\b\d\.\d{1,2}\b(?![\d,])"), "número de item do plano"),
    (re.compile(r"\betapa \d+\b", re.I), "etapa N"),
    (re.compile(r"\bobra\b", re.I), "obra"),
]


def docstrings(arvore):
    ids = set()
    for n in ast.walk(arvore):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if n.body and isinstance(n.body[0], ast.Expr) and isinstance(getattr(n.body[0], "value", None), ast.Constant) \
                    and isinstance(n.body[0].value.value, str):
                ids.add(id(n.body[0].value))
    return ids


for arq in sorted(RAIZ.rglob("*.py")):
    try:
        arvore = ast.parse(arq.read_text(encoding="utf-8"))
    except SyntaxError:
        continue
    doc = docstrings(arvore)
    # strings soltas como instrução (Expr) também são comentário
    soltas = {id(n.value) for n in ast.walk(arvore) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)}
    for n in ast.walk(arvore):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc and id(n) not in soltas:
            s = n.value
            if len(s) < 3 or " " not in s:      # chaves, nomes de campo, caminhos
                continue
            for rx, tipo in PADROES:
                m = rx.search(s)
                if m:
                    print(f"{arq.relative_to(RAIZ.parent)}:{n.lineno}: [{tipo}: {m.group(0)}] {s[:160]!r}")
                    break
