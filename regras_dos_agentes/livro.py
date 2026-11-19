"""A leitura única do Livro de decisões (`docs/plano/DECISOES.md`) para o pacote e o formulário.

Cada decisão é uma linha de tabela que começa com `| D-nnn |`; as colunas são: número, data, palavras do Samuel (com a
origem), o que quer dizer na prática, onde toca, a prova, a situação, o dono, a fonte. O montador do pacote copia daqui
as palavras e o "na prática"; o formulário confere aqui se as palavras citadas pelo agente estão no Livro, letra por
letra (K20). Nenhum outro arquivo do pacote lê o Livro.

Seguro mexer: o tamanho do resumo. Arriscado: o jeito de achar a linha (`linha`) ou de cortar as colunas: o Livro tem
"|" dentro do texto às vezes, e o corte é por " | ", como o esboço da proposta fazia.
"""

from __future__ import annotations

import re
from pathlib import Path

from . import conversa_com_o_git as git

CAMINHO = "docs/plano/DECISOES.md"
NUMERO = re.compile(r"\bD-\d{3,}\b")
VERSAO_DE_TESTE = "obra-2026-10-26"     # D-797: a versão de teste, onde só a gerente junta (e escreve o Livro)


class Livro:
    """O Livro lido uma vez: as linhas de cada decisão."""

    def __init__(self, texto: str):
        """Guarda a linha de cada decisão (a primeira, se o número aparecer duas vezes)."""
        self.linhas: dict[str, str] = {}
        for l in texto.splitlines():
            m = re.match(r"^\|\s*(D-\d{3,})\s*\|", l)
            if m:
                self.linhas.setdefault(m.group(1), l)

    @classmethod
    def da_versao_de_teste(cls, raiz: Path | str) -> "Livro":
        """O Livro da versão de teste no GitHub (`origin/obra-2026-10-26`), que só a gerente escreve.

        É o Livro que vale para conferir o "sim" do Samuel e as palavras citadas (achado N1 da segunda volta de quem
        quebrou): o Livro da pasta ou do ramo do agente o próprio agente pode mudar. Busca no GitHub pela peça única do
        git; sem internet, `GitFalhou` (quem chama diz que não deu para conferir, nunca "passou").
        """
        base = git.buscar_ramo(raiz, VERSAO_DE_TESTE)
        return cls(git.conteudo_no_commit(raiz, base, CAMINHO) or "")

    @classmethod
    def do_repositorio(cls, raiz: Path | str) -> "Livro":
        """O Livro desta cópia; vazio (sem decisão nenhuma) se o arquivo não existir."""
        caminho = Path(raiz) / CAMINHO
        return cls(caminho.read_text(encoding="utf-8") if caminho.exists() else "")

    def existe(self, numero: str) -> bool:
        """A decisão existe no Livro?"""
        return numero in self.linhas

    def colunas(self, numero: str) -> list[str]:
        """As colunas da linha da decisão (vazia se não existe)."""
        linha = self.linhas.get(numero)
        return [c.strip() for c in linha.split(" | ")] if linha else []

    def tem_as_palavras(self, numero: str, citacao: str) -> bool:
        """A citação está na linha da decisão, letra por letra (os espaços contam como um só)?"""
        linha = self.linhas.get(numero, "")
        junta = lambda s: " ".join(s.split())  # noqa: E731
        return bool(citacao.strip()) and junta(citacao) in junta(linha)

    def palavras_do_samuel(self, numero: str) -> str:
        """A coluna das palavras do Samuel (com a origem) da decisão, ou "" se ela não existe."""
        col = self.colunas(numero)
        return col[2] if len(col) > 2 else ""

    def trata_da_lista_de_excecoes(self, numero: str) -> bool:
        """A decisão fala da lista de exceções do porteiro (como a D-791 e a D-800)?"""
        return "lista de exceç" in self.linhas.get(numero, "").lower()

    def resumo(self, numero: str, limite: int = 700) -> str:
        """A decisão para o pacote: a data, as palavras dele e o "na prática", copiados da linha."""
        col = self.colunas(numero)
        if len(col) < 4:
            return f"- **{numero}**: NÃO ACHADA NO LIVRO (a gerente confere antes de mandar)"
        pratica = col[3].replace("**", "")
        if len(pratica) > limite:
            pratica = pratica[:limite].rsplit(" ", 1)[0] + " [...]"
        return f"- **{numero}** ({col[1]}): {col[2]}\n  Na prática: {pratica}"
