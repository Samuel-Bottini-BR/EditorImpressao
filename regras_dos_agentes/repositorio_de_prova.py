"""Um repositório git de verdade numa pasta, para as provas do porteiro e para quem tenta quebrar experimentar.

As conferências das mudanças (K09 a K18) e a conferência antes do commit leem commits, o índice e o "GitHub" (um
remoto). Testá-las com um git de mentira não provaria nada (D-767): aqui o git é o de verdade, numa pasta temporária,
com um remoto que é outra pasta (o papel do GitHub). Nada toca o repositório do projeto.

Uso:
    r = RepositorioDeProva.novo(pasta)
    r.escrever("core/a.py", "X = 1\n")
    base = r.commit("partida")
    ...
Seguro mexer: acrescentar ajudas. Arriscado: escrever fora de `pasta`.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import conversa_com_o_git as git


@dataclass
class RepositorioDeProva:
    """Um repositório de prova: a pasta da cópia e a do remoto (o "GitHub")."""

    raiz: Path
    remoto: Path

    @classmethod
    def novo(cls, pasta: Path | str) -> "RepositorioDeProva":
        """Cria a cópia (`pasta/copia`) e o remoto (`pasta/github`)."""
        pasta = Path(pasta)
        r = cls(pasta / "copia", pasta / "github")
        git.criar_repositorio(r.raiz)
        git.criar_repositorio(r.remoto, sem_pasta_de_trabalho=True)
        git.configurar(r.raiz, "core.autocrlf", "false")
        return r

    def escrever(self, caminho: str, texto: str) -> Path:
        """Escreve um arquivo da cópia (cria as pastas), em UTF-8 com quebra de linha "\n"."""
        destino = self.raiz / caminho
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8", newline="\n")
        return destino

    def apagar(self, caminho: str) -> None:
        """Apaga um arquivo da cópia de prova."""
        (self.raiz / caminho).unlink()

    def commit(self, mensagem: str) -> str:
        """Commit de tudo; devolve o código do commit. Levanta `GitFalhou` se o commit não acontecer."""
        r = git.commit_de_tudo(self.raiz, mensagem)
        if r.returncode != 0:
            raise git.GitFalhou(f"o commit de prova não aconteceu: {r.stdout}{r.stderr}")
        return git.commit_completo(self.raiz, "HEAD")

    def adicionar(self, caminho: str) -> None:
        """Põe o arquivo no índice (o que vai no próximo commit), sem fazer o commit."""
        git.adicionar(self.raiz, caminho)

    def commit_do_indice(self, mensagem: str):
        """Tenta o commit só do que está no índice e devolve o resultado (o gancho pode barrar)."""
        return git.commit_do_indice(self.raiz, mensagem)

    def tentar_commit(self, mensagem: str):
        """Tenta o commit e devolve o resultado (código, saída): o gancho pode barrar."""
        return git.commit_de_tudo(self.raiz, mensagem)

    def enviar(self) -> None:
        """Envia o ramo ao remoto de prova (o "push")."""
        git.enviar(self.raiz, self.remoto)
