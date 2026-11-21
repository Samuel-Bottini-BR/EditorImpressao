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


# A bandeira do Windows "não abrir janela de console" (a mesma que a peça do Windows usa em core/windows.py); fora do
# Windows não existe e vale 0. Passo 2, volta 9: a peça passou a ser chamada também de dentro da janela do programa
# rodando pelas fontes (core/pasta_das_ferramentas.py), e sem ela cada git piscaria uma janela preta na tela.
_SEM_JANELA = getattr(subprocess, "CREATE_NO_WINDOW", 0)
# As variáveis com que o git aponta para outro repositório (o gancho do commit as põe); quem pergunta "onde está este
# código" (pasta_principal) não pode herdá-las.
_VARIAVEIS_DE_OUTRO_REPOSITORIO = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE")


def _rodar(raiz: Path | str, *args: str, entrada: str | None = None, aceitar: tuple[int, ...] = (0,),
           ambiente_extra: dict[str, str] | None = None, limite_s: float | None = None,
           sem: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
    """Roda `git <args>` na pasta `raiz` e devolve o resultado; código fora de `aceitar` vira `GitFalhou`.

    `GIT_OPTIONAL_LOCKS=0` evita que uma leitura (ex.: `git status`) grave no índice enquanto o gancho do commit roda.
    Sempre sem janela de console (`_SEM_JANELA`). `limite_s`: o tempo máximo (None = sem limite, como sempre foi; o
    `fetch` de um ramo grande pode demorar); passou dele, o git é fechado e vira `GitFalhou`. `sem`: variáveis do
    ambiente que o git não pode herdar.
    """
    ambiente = dict(os.environ, GIT_OPTIONAL_LOCKS="0", LC_ALL="C", **(ambiente_extra or {}))
    for nome in sem:
        ambiente.pop(nome, None)
    try:
        r = subprocess.run(["git", "-c", "core.quotepath=false", *args], cwd=str(raiz), input=entrada,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", env=ambiente,
                           timeout=limite_s, creationflags=_SEM_JANELA)
    except subprocess.TimeoutExpired as erro:
        raise GitFalhou(f"o git não respondeu em {limite_s:g} segundos a `git {' '.join(args)}`") from erro
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


def pasta_principal(pasta: Path | str, limite_s: float | None = 30) -> Path | None:
    """A pasta principal do repositório que contém `pasta` (numa cópia de trabalho, a do repositório de onde ela saiu;
    na própria pasta principal, ela mesma). `None` quando o repositório não tem pasta principal (um repositório só de
    git, sem arquivos, com a pasta comum que não se chama `.git`).

    Lido no git (https://git-scm.com/docs/git-worktree, "DETAILS": numa cópia de trabalho, "$GIT_COMMON_DIR is set to
    point back to the main worktree's $GIT_DIR (e.g. /path/main/.git)"; https://git-scm.com/docs/git-rev-parse,
    `--git-common-dir` e `--path-format=absolute`, o caminho inteiro): a pasta comum, e a de cima dela. Sem as variáveis
    que apontariam para outro repositório (`_VARIAVEIS_DE_OUTRO_REPOSITORIO`), com limite de tempo. Levanta `GitFalhou`
    sem git, fora de um repositório ou se ele não responder. Passo 2, volta 9 (core/pasta_das_ferramentas.py)."""
    comum = Path(_rodar(pasta, "rev-parse", "--path-format=absolute", "--git-common-dir", limite_s=limite_s,
                        sem=_VARIAVEIS_DE_OUTRO_REPOSITORIO).stdout.strip())
    if comum.name != ".git" or not comum.parent.is_dir():
        return None
    return comum.parent


def criar_copia_de_trabalho(raiz: Path | str, pasta: Path | str, ramo: str) -> None:
    """Cria uma cópia de trabalho (`git worktree add -b <ramo> <pasta>`) do repositório `raiz`. Só para os
    repositórios de prova (`repositorio_de_prova.py`): nada aqui toca o repositório do projeto."""
    _rodar(raiz, "worktree", "add", "-q", "-b", ramo, str(pasta))


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


def arquivos_por_commit(raiz: Path | str, base: str) -> list[tuple[str, list[str]]]:
    """(código, arquivos que ele mexeu) de cada commit depois de `base` até o atual."""
    if not existe_commit(raiz, base):
        raise GitFalhou(f"o commit de partida {base} não existe neste repositório")
    saida = _rodar(raiz, "log", "--no-renames", "--format=%x1e%H", "--name-only", f"{base}..HEAD").stdout
    resultado = []
    for bloco in saida.split("\x1e"):
        linhas = [l.strip() for l in bloco.strip().splitlines() if l.strip()]
        if linhas:
            resultado.append((linhas[0], linhas[1:]))
    return resultado


def ramo_atual(raiz: Path | str) -> str:
    """O nome do ramo em que a cópia está (`GitFalhou` se a cópia não está num ramo)."""
    nome = _rodar(raiz, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if not nome or nome == "HEAD":
        raise GitFalhou("a cópia não está num ramo (HEAD solto)")
    return nome


def commit_no_github(raiz: Path | str, ramo: str) -> str | None:
    """O commit que o ramo tem AGORA no GitHub (pergunta ao GitHub, `git ls-remote`), ou None se o ramo não existe lá.

    Não usa a cópia local do que foi buscado da última vez (achado 19 de quem tentou quebrar, 19/11): sem internet,
    `GitFalhou`, e a conferência diz que não conseguiu conferir.
    """
    saida = _rodar(raiz, "ls-remote", "--heads", "origin", f"refs/heads/{ramo}").stdout.strip()
    return saida.split()[0] if saida else None


def e_raso(raiz: Path | str) -> bool:
    """A cópia foi tirada só com o último commit (como no GitHub, `--depth=1`)?"""
    return _rodar(raiz, "rev-parse", "--is-shallow-repository").stdout.strip() == "true"


def buscar_ramo(raiz: Path | str, ramo: str) -> str:
    """Busca o ramo no GitHub e devolve o código do commit dele (`refs/remotes/origin/<ramo>`).

    Numa cópia rasa (a do GitHub), busca só o último commit; numa cópia inteira (a do PC), busca normal: `--depth`
    numa cópia inteira a deixaria rasa, e isso cortaria a história do repositório do Samuel.
    """
    profundidade = ["--depth=1"] if e_raso(raiz) else []
    _rodar(raiz, "fetch", "-q", *profundidade, "origin", f"+refs/heads/{ramo}:refs/remotes/origin/{ramo}")
    return commit_completo(raiz, f"refs/remotes/origin/{ramo}")


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


def adicionar(raiz: Path | str, *caminhos: str) -> None:
    """`git add` destes caminhos (vão para o índice, o que entra no próximo commit)."""
    _rodar(raiz, "add", "--", *caminhos)


def commit_do_indice(raiz: Path | str, mensagem: str) -> subprocess.CompletedProcess:
    """`git commit` só do que já está no índice; devolve o resultado inteiro sem levantar (o gancho pode barrar)."""
    return _rodar_para_escrever(raiz, "commit", "-q", "-m", mensagem, aceitar=tuple(range(256)))


def commit_de_tudo(raiz: Path | str, mensagem: str) -> subprocess.CompletedProcess:
    """`git add -A` e `git commit`; devolve o resultado inteiro (código, saída) sem levantar: o gancho pode barrar."""
    _rodar(raiz, "add", "-A")
    return commit_do_indice(raiz, mensagem)


def criar_e_ir_para_o_ramo(raiz: Path | str, nome: str) -> None:
    """`git switch -C <nome>`: cria (ou refaz) o ramo no commit atual e vai para ele (só nas provas)."""
    _rodar(raiz, "switch", "-q", "-C", nome)


def enviar(raiz: Path | str, remoto: Path | str, ramo_no_remoto: str | None = None) -> None:
    """Liga o repositório a um "origin" (uma pasta) e envia o ramo atual (ou o envia com outro nome lá, sem acompanhar)."""
    if _rodar(raiz, "remote", aceitar=(0,)).stdout.strip() == "":
        _rodar(raiz, "remote", "add", "origin", str(remoto))
    if ramo_no_remoto:
        _rodar_para_escrever(raiz, "push", "-q", "-f", "origin", f"HEAD:refs/heads/{ramo_no_remoto}")
    else:
        _rodar_para_escrever(raiz, "push", "-q", "-u", "origin", "HEAD")
