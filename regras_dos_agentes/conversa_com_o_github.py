"""A peça única de conversa com o GitHub (CLAUDE.md §11.12, ponto 1), pela ferramenta `gh` do Samuel.

Usada só pela K21 do formulário: "a rodada do GitHub existe, é do último commit do ramo e passou".

O que se lê de verdade (conferido em 19/11/2026 na rodada 44202459161):
- `gh run view <id> --json status,conclusion,displayTitle,jobs` dá a situação ("completed") e o resultado ("success",
  "failure"...) da rodada, e os trabalhos dela (cada um com `databaseId` e `name`, ex.: "Suite (parte 1 de 5)").
- A rodada disparada com `-f ramo=<ramo>` roda no commit do ramo dos testes (`headSha` não é o do agente): o commit
  testado de verdade só aparece no registro do passo "Trocar o codigo" (`.github/scripts/trocar_codigo.sh`), na linha
  "codigo trocado pelo de <ramo> (<commit>)" ou, sem ramo pedido, "testando o proprio commit <commit>". Esse registro
  sai por `gh run view <id> --log --job <databaseId>` (o `gh api .../jobs/<id>/logs` recusa por causa das cores do
  registro: "the response contains terminal escape sequences").

Três jeitos de sair: a resposta lida; `GitHubFalhou` com o motivo (sem `gh`, sem internet, rodada que não existe,
registro sem a linha do commit). Nunca "passou" sem ter lido.

Seguro mexer: o caminho do `gh`. Arriscado: a linha procurada no registro (muda se o `trocar_codigo.sh` mudar a frase).
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

LUGAR_DO_GH = Path(r"C:\Program Files\GitHub CLI\gh.exe")
LINHA_DO_COMMIT = re.compile(r"codigo trocado pelo de \S+ \(([0-9a-f]{40})\)|testando o proprio commit ([0-9a-f]{40})")


class GitHubFalhou(RuntimeError):
    """Não deu para ler a rodada no GitHub; a mensagem diz por quê, em português."""


def _gh() -> str:
    """O caminho do `gh` (no PATH ou no lugar onde o instalador do GitHub CLI põe)."""
    achado = shutil.which("gh")
    if achado:
        return achado
    if LUGAR_DO_GH.exists():
        return str(LUGAR_DO_GH)
    raise GitHubFalhou("a ferramenta gh do GitHub não está instalada (C:\\Program Files\\GitHub CLI)")


def _rodar(*args: str) -> str:
    """Roda o `gh` e devolve a saída; qualquer falha vira `GitHubFalhou`."""
    try:
        r = subprocess.run([_gh(), *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300)
    except (OSError, subprocess.TimeoutExpired) as erro:
        raise GitHubFalhou(f"não deu para rodar o gh: {erro}") from erro
    if r.returncode != 0:
        raise GitHubFalhou(f"o gh recusou `gh {' '.join(args[:3])}`: {r.stderr.strip()[:300]}")
    return r.stdout


@dataclass(frozen=True)
class Rodada:
    """O que se leu de uma rodada dos testes no GitHub."""

    numero: str
    terminada: bool
    passou: bool
    titulo: str
    commit_testado: str


def commit_do_registro(registro: str) -> str | None:
    """O commit testado, tirado do registro do passo "Trocar o codigo" (ou None se a linha não está lá)."""
    m = LINHA_DO_COMMIT.search(registro)
    return (m.group(1) or m.group(2)) if m else None


def ler_rodada(numero: str, repositorio: str) -> Rodada:
    """Lê a rodada `numero` no repositório `dono/nome`: se terminou, se passou e qual commit ela testou de verdade."""
    dados = json.loads(_rodar("run", "view", numero, "-R", repositorio, "--json", "status,conclusion,displayTitle,jobs"))
    commit = None
    for job in dados.get("jobs", []):
        if job.get("conclusion") == "skipped":
            continue
        commit = commit_do_registro(_rodar("run", "view", numero, "-R", repositorio, "--log", "--job",
                                           str(job["databaseId"])))
        if commit:
            break
    if commit is None:
        raise GitHubFalhou(f"o registro da rodada {numero} não diz qual commit foi testado")
    return Rodada(numero, dados.get("status") == "completed", dados.get("conclusion") == "success",
                  dados.get("displayTitle", ""), commit)
