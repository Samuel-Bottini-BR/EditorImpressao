"""Roda os testes um ARQUIVO por vez (regra do Samuel de 19/10/2026: no PC, um arquivo de teste por
vez), com TEMP e --basetemp dentro da worktree, e grava o resumo de cada arquivo.

Uso (na worktree):
    .venv\\Scripts\\python.exe relatorios\\obra-etapa3\\roteiro\\rodar_por_arquivo.py <saida.txt> [ui|todos] [arquivo ...]

"ui" (padrão): só os arquivos de teste que usam a tela (importam ui/); "todos": todos os
tests/test_*.py; ou a lista de arquivos dada. Pula tests/test_decisoes.py (é da etapa 1, outro
agente). Cada arquivo tem até 30 min.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
PYTHON = Path(r"D:\programas\EditorImpressao\.venv\Scripts\python.exe")


def arquivos(qual: str, nomes: list[str]) -> list[Path]:
    if nomes:
        return [RAIZ / "tests" / (n if n.endswith(".py") else n + ".py") for n in nomes]
    todos = sorted((RAIZ / "tests").glob("test_*.py"))
    todos = [a for a in todos if a.name != "test_decisoes.py"]
    if qual == "todos":
        return todos
    return [a for a in todos
            if re.search(r"^\s*(from ui|import ui)|from tests\.test_mesmo_livro_outro_caminho",
                         a.read_text(encoding="utf-8"), re.M)]


def main() -> None:
    saida = Path(sys.argv[1])
    qual = sys.argv[2] if len(sys.argv) > 2 else "ui"
    lista = arquivos(qual, sys.argv[3:])
    tmp = RAIZ / "saida_teste" / "obra-etapa3" / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    ambiente = dict(os.environ, TEMP=str(tmp), TMP=str(tmp))
    linhas = []
    for arquivo in lista:
        inicio = time.time()
        try:
            r = subprocess.run(
                [str(PYTHON), "-m", "pytest", str(arquivo.relative_to(RAIZ)), "-q",
                 "--basetemp", str(RAIZ / "saida_teste" / "obra-etapa3" / "bt"),
                 "-p", "no:cacheprovider"],
                cwd=RAIZ, env=ambiente, capture_output=True, text=True, encoding="utf-8",
                errors="replace", timeout=1800)
            fim = [l for l in r.stdout.strip().splitlines() if l.strip()]
            resumo = fim[-1] if fim else "(sem saída)"
            falhas = [l for l in r.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
        except subprocess.TimeoutExpired:
            resumo, falhas = "TEMPO ESGOTADO (30 min)", []
        linha = f"{arquivo.name}: {resumo}  [{time.time() - inicio:.0f} s]"
        print(linha, flush=True)
        for f in falhas:
            print("    " + f, flush=True)
        linhas.append(linha)
        linhas.extend("    " + f for f in falhas)
        saida.write_text("\n".join(linhas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
