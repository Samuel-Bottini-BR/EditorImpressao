"""Quem tenta quebrar 5: quais testes antigos mudaram de aba7b844 para 0d9cac4e (corpo da função comparado pelo ast),
para conferir contra a lista da D-836. Só lê o git."""
import ast, subprocess, sys
A, B = "aba7b844", "0d9cac4e"
arqs = subprocess.run(["git", "diff", "--name-only", f"{A}..{B}", "--", "tests/"], capture_output=True, text=True).stdout.split()
def funcs(ref, arq):
    r = subprocess.run(["git", "show", f"{ref}:{arq}"], capture_output=True, text=True, encoding="utf-8")
    if r.returncode: return None
    t = ast.parse(r.stdout); d = {}
    for n in ast.walk(t):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            d[n.name] = ast.dump(n, include_attributes=False)
    mod = [ast.dump(n) for n in t.body if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    return d, mod
for arq in arqs:
    a, b = funcs(A, arq), funcs(B, arq)
    if a is None: print(f"{arq}: NOVO"); continue
    (fa, ma), (fb, mb) = a, b
    for n in sorted(fa):
        if n not in fb: print(f"{arq}::{n}: SAIU")
        elif fa[n] != fb[n]: print(f"{arq}::{n}: MUDOU")
    for n in sorted(fb):
        if n not in fa: print(f"{arq}::{n}: ENTROU")
    if ma != mb: print(f"{arq}: o topo do módulo (constantes/imports/tabelas) MUDOU")
