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
# O trabalho da rodada que roda o juiz (o nome vem do workflow, no ramo dos testes, que o agente não controla). A marca
# só vale lida ali (achado Q1 da quarta volta de quem quebrou: os trabalhos da suíte e dos botões rodam o código do
# agente, que pode escrever uma marca falsa antes).
TRABALHO_DO_JUIZ = "Porteiro (juiz da versao de teste)"
MARCA_DO_PORTEIRO = re.compile(r"^PORTEIRO: (CONFERIDO|BARROU|NAO CONFERIDO[^\r\n]*)$")
CARIMBO_DE_HORA = re.compile(r"^\d{4}-\d{2}-\d{2}T[\d:.]+Z ")
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
    porteiro: str | None = None     # a marca do juiz (`juiz.py`) no registro; None = a rodada não tem o juiz


def commit_do_registro(registro: str) -> str | None:
    """O commit testado, tirado do registro do passo "Trocar o codigo" (ou None se a linha não está lá)."""
    m = LINHA_DO_COMMIT.search(registro)
    return (m.group(1) or m.group(2)) if m else None


def ler_rodada(numero: str, repositorio: str) -> Rodada:
    """Lê a rodada `numero` no repositório `dono/nome`: se terminou, se passou e qual commit ela testou de verdade."""
    dados = json.loads(_rodar("run", "view", numero, "-R", repositorio, "--json", "status,conclusion,displayTitle,jobs"))
    commit = None
    for job in dados.get("jobs", []):
        if job.get("conclusion") == "skipped" or job.get("name") == TRABALHO_DO_JUIZ:
            continue
        commit = commit_do_registro(_rodar("run", "view", numero, "-R", repositorio, "--log", "--job",
                                           str(job["databaseId"])))
        if commit:
            break
    porteiro = marca_do_juiz(dados.get("jobs", []), lambda job: _rodar("run", "view", numero, "-R", repositorio,
                                                                       "--log", "--job", str(job["databaseId"])))
    if commit is None:
        raise GitHubFalhou(f"o registro da rodada {numero} não diz qual commit foi testado")
    return Rodada(numero, dados.get("status") == "completed", dados.get("conclusion") == "success",
                  dados.get("displayTitle", ""), commit, porteiro)


def marca_do_porteiro(registro: str) -> str | None:
    """A ÚLTIMA marca que o juiz deixou no registro de um trabalho ("CONFERIDO", "BARROU" ou "NAO CONFERIDO (motivo)").

    Só conta a linha que É a marca (depois do nome do trabalho, do passo e da hora que o GitHub põe na frente), não um
    texto que a contenha no meio; e vale a última, que o juiz escreve no fim.
    """
    achada = None
    for linha in registro.splitlines():
        texto = CARIMBO_DE_HORA.sub("", linha.rsplit("\t", 1)[-1]).strip()
        m = MARCA_DO_PORTEIRO.match(texto)
        if m:
            achada = m.group(1).strip()
    return achada


def marca_do_juiz(jobs: list[dict], registro_de) -> str | None:
    """A marca do juiz, lida só no trabalho de nome `TRABALHO_DO_JUIZ` (None se a rodada não tem esse trabalho ou ele
    não deixou marca). `registro_de(job)` devolve o registro de um trabalho."""
    juiz = next((j for j in jobs if j.get("name") == TRABALHO_DO_JUIZ and j.get("conclusion") != "skipped"), None)
    return marca_do_porteiro(registro_de(juiz)) if juiz else None
