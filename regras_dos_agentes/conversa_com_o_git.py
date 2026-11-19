"""A peça única de conversa com o git (CLAUDE.md §11.12, ponto 1): todo o pacote pergunta ao git só por aqui.

Cada função roda um comando do git e devolve a resposta já lida. Três jeitos de sair, nunca um quarto:
- deu certo: devolve a resposta;
- o pedido não existe (ex.: um arquivo que não existe naquele commit): devolve `None`, e só nas funções que dizem isso;
- falhou (git ausente, repositório estragado, commit que não existe): levanta `GitFalhou` com o motivo em português.
Nada aqui transforma falha em "passou" (§11.12, ponto 2): quem chama e recebe `GitFalhou` tem de dizer que não
conseguiu conferir.

Os caminhos voltam sempre com "/" (como o git escreve), sem aspas, com acento como está (`core.quotepath=false` e `-z`).

Seguro mexer: acrescentar uma função nova para outro pedido ao git, seguindo o mesmo jeito. Arriscado: tirar o `-z`
(nome com espaço ou acento quebra), trocar `diff base HEAD` por outra forma (muda o que conta como "mexido") ou
engolir o erro do git.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path


class GitFalhou(RuntimeError):
    """O git não respondeu do jeito esperado. A mensagem diz, em português, o que foi pedido e o que ele disse."""


def _rodar(raiz: Path | str, *args: str, entrada: str | None = None, aceitar: tuple[int, ...] = (0,),
           ambiente_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    """Roda `git <args>` na pasta `raiz` e devolve o resultado; código fora de `aceitar` vira `GitFalhou`.

    `GIT_OPTIONAL_LOCKS=0` evita que uma leitura (ex.: `git status`) grave no índice enquanto o gancho do commit roda.
    """
    ambiente = dict(os.environ, GIT_OPTIONAL_LOCKS="0", LC_ALL="C", **(ambiente_extra or {}))
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=str(raiz), input=entrada,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=ambiente)
    except FileNotFoundError as erro:
        raise GitFalhou("o git não está instalado ou não está no caminho do Windows") from erro
    except OSError as erro:
        raise GitFalhou(f"não deu para rodar o git em {raiz}: {erro}") from erro
    if r.returncode not in aceitar:
        raise GitFalhou(f"o git recusou `git {' '.join(args)}` (código {r.returncode}): {r.stderr.strip()[:400]}")
    return r


def _lista_z(texto: str) -> list[str]:
    """Separa uma resposta do git com `-z` (nomes separados por um caractere zero)."""
    return [p for p in texto.split("\0") if p]


def raiz_do_repositorio(pasta: Path | str) -> Path:
    """A pasta de cima da cópia (worktree) que contém `pasta`."""
    return Path(_rodar(pasta, "rev-parse", "--show-toplevel").stdout.strip())


def arquivos_do_git(raiz: Path | str) -> list[str]:
    """Todos os arquivos que o git conhece nesta cópia (o índice), com "/"."""
    return _lista_z(_rodar(raiz, "ls-files", "-z").stdout)


def existe_commit(raiz: Path | str, ref: str) -> bool:
    """O commit (ou ramo) `ref` existe neste repositório?"""
    return _rodar(raiz, "cat-file", "-e", f"{ref}^{{commit}}", aceitar=(0, 1, 128)).returncode == 0


def commit_completo(raiz: Path | str, ref: str) -> str:
    """O código inteiro (40 letras) do commit `ref`; `GitFalhou` se ele não existe."""
    return _rodar(raiz, "rev-parse", "--verify", f"{ref}^{{commit}}").stdout.strip()


def conteudo_no_commit(raiz: Path | str, ref: str, caminho: str) -> str | None:
    """O texto de `caminho` no commit `ref`, ou `None` se o arquivo não existe naquele commit."""
    if _rodar(raiz, "cat-file", "-e", f"{ref}:{caminho}", aceitar=(0, 1, 128)).returncode != 0:
        if not existe_commit(raiz, ref):
            raise GitFalhou(f"o commit {ref} não existe neste repositório")
        return None
    return _rodar(raiz, "show", f"{ref}:{caminho}").stdout


def conteudo_no_indice(raiz: Path | str, caminho: str) -> str:
    """O texto de `caminho` como vai no próximo commit (o índice, não a pasta)."""
    return _rodar(raiz, "show", f":{caminho}").stdout


def arquivos_no_indice_mudados(raiz: Path | str) -> list[str]:
    """Os arquivos acrescentados, mudados ou renomeados que vão no próximo commit (sem os apagados)."""
    return _lista_z(_rodar(raiz, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR").stdout)


def arquivos_mudados(raiz: Path | str, base: str) -> list[str]:
    """Os arquivos diferentes entre o commit `base` e o commit atual (acrescentados, mudados, apagados, renomeados).

    Comparação direta das duas árvores (`git diff base HEAD`). Se o trabalho juntou outro ramo depois de começar, o
    commit de partida do pedido tem de ser atualizado, senão o que veio do outro ramo conta como mexido.
    """
    if not existe_commit(raiz, base):
        raise GitFalhou(f"o commit de partida {base} não existe neste repositório")
    return _lista_z(_rodar(raiz, "diff", "--name-only", "-z", "--no-renames", base, "HEAD").stdout)


_CABECA_DO_TRECHO = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def linhas_novas(raiz: Path | str, base: str) -> dict[str, list[tuple[int, str]]]:
    """Para cada arquivo de texto mudado entre `base` e o commit atual, as linhas acrescentadas: (número, texto).

    Linha trocada conta como acrescentada (o texto novo). Arquivo binário não aparece.
    """
    if not existe_commit(raiz, base):
        raise GitFalhou(f"o commit de partida {base} não existe neste repositório")
    saida = _rodar(raiz, "diff", "-U0", "--no-color", "--no-renames", "--no-ext-diff", base, "HEAD").stdout
    resultado: dict[str, list[tuple[int, str]]] = {}
    atual: str | None = None
    numero = 0
    for linha in saida.split("\n"):
        if linha.startswith("+++ "):
            nome = linha[4:].rstrip("\r")
            atual = None if nome == "/dev/null" else nome.removeprefix("b/")
            if atual is not None:
                resultado.setdefault(atual, [])
            continue
        trecho = _CABECA_DO_TRECHO.match(linha)
        if trecho:
            numero = int(trecho.group(1))
            continue
        if atual is None or linha.startswith(("--- ", "diff ", "index ", "\\")):
            continue
        if linha.startswith("+"):
            resultado[atual].append((numero, linha[1:].rstrip("\r")))
            numero += 1
    return resultado


def mensagens_dos_commits(raiz: Path | str, base: str, caminho: str | None = None) -> list[tuple[str, str]]:
    """(código, mensagem inteira) de cada commit depois de `base` até o atual (só os que mexem em `caminho`, se dado)."""
    if not existe_commit(raiz, base):
        raise GitFalhou(f"o commit de partida {base} não existe neste repositório")
    filtro = ["--", caminho] if caminho else []
    saida = _rodar(raiz, "log", "--format=%H%x1f%B%x1e", f"{base}..HEAD", *filtro).stdout
    resultado = []
    for bloco in saida.split("\x1e"):
        bloco = bloco.strip("\n")
        if "\x1f" in bloco:
            sha, msg = bloco.split("\x1f", 1)
            resultado.append((sha.strip(), msg))
    return resultado


def e_ancestral(raiz: Path | str, ref: str, de: str = "HEAD") -> bool:
    """O commit `ref` vem antes de `de` na história (ou é o mesmo)?"""
    if not existe_commit(raiz, ref):
        raise GitFalhou(f"o commit {ref} não existe neste repositório")
    return _rodar(raiz, "merge-base", "--is-ancestor", ref, de, aceitar=(0, 1)).returncode == 0


def mudados_entre(raiz: Path | str, antes: str, depois: str = "HEAD") -> list[str]:
    """Os arquivos diferentes entre dois commits."""
    return _lista_z(_rodar(raiz, "diff", "--name-only", "-z", "--no-renames", antes, depois).stdout)


def mudancas_sem_commit(raiz: Path | str) -> list[str]:
    """O que está mudado na pasta e não foi para um commit (inclui arquivo novo fora do git e não ignorado)."""
    return _lista_z(_rodar(raiz, "status", "--porcelain", "-z", "--untracked-files=all").stdout)


def commit_do_ramo_remoto(raiz: Path | str) -> str | None:
    """O commit do ramo no GitHub que este ramo acompanha (o último buscado), ou `None` se o ramo não acompanha nenhum."""
    r = _rodar(raiz, "rev-parse", "--verify", "--quiet", "@{upstream}", aceitar=(0, 1, 128))
    if r.returncode != 0:
        return None
    return r.stdout.strip() or None


def repositorio_no_github(raiz: Path | str) -> str:
    """O "dono/nome" do repositório no GitHub, tirado do endereço do `origin` (ex.: Samuel-Bottini-BR/EditorImpressao)."""
    url = _rodar(raiz, "remote", "get-url", "origin").stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not m:
        raise GitFalhou(f"o origin não é um repositório do GitHub: {url}")
    return m.group(1)


# ----------------------------------------------------------------------------------------------------------------
# Escrever num repositório (só para os repositórios de prova: `repositorio_de_prova.py`). O pacote nunca escreve no
# repositório do projeto: quem faz commit e push ali é o agente, com o git dele.
# ----------------------------------------------------------------------------------------------------------------

_QUEM_FAZ_O_COMMIT_DE_PROVA = {"GIT_AUTHOR_NAME": "prova do porteiro", "GIT_AUTHOR_EMAIL": "prova@porteiro.invalid",
                               "GIT_COMMITTER_NAME": "prova do porteiro",
                               "GIT_COMMITTER_EMAIL": "prova@porteiro.invalid"}


def _rodar_para_escrever(raiz: Path | str, *args: str, aceitar: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    """Como `_rodar`, com um nome de autor de prova (o repositório de prova não tem o nome do Samuel configurado)."""
    return _rodar(raiz, *args, aceitar=aceitar, ambiente_extra=_QUEM_FAZ_O_COMMIT_DE_PROVA)


def criar_repositorio(pasta: Path | str, sem_pasta_de_trabalho: bool = False) -> None:
    """`git init` (com o ramo "principal"); `sem_pasta_de_trabalho` cria um repositório só de guardar (o "GitHub")."""
    Path(pasta).mkdir(parents=True, exist_ok=True)
    _rodar(pasta, "init", "-q", "-b", "principal", *(["--bare"] if sem_pasta_de_trabalho else []))


def configurar(raiz: Path | str, chave: str, valor: str) -> None:
    """`git config <chave> <valor>` só neste repositório."""
    _rodar(raiz, "config", chave, valor)


def commit_de_tudo(raiz: Path | str, mensagem: str) -> subprocess.CompletedProcess:
    """`git add -A` e `git commit`; devolve o resultado inteiro (código, saída) sem levantar: o gancho pode barrar."""
    _rodar(raiz, "add", "-A")
    return _rodar_para_escrever(raiz, "commit", "-q", "-m", mensagem, aceitar=tuple(range(256)))


def enviar(raiz: Path | str, remoto: Path | str) -> None:
    """Liga o repositório a um "origin" (uma pasta) e envia o ramo atual, acompanhando-o."""
    if _rodar(raiz, "remote", aceitar=(0,)).stdout.strip() == "":
        _rodar(raiz, "remote", "add", "origin", str(remoto))
    _rodar_para_escrever(raiz, "push", "-q", "-u", "origin", "HEAD")
