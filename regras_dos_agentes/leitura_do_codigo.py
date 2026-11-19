"""A peça única de leitura de código Python para o porteiro: o que é código, o que é comentário, o que é docstring.

O porteiro procura palavras nas linhas de código (inclusive dentro dos textos entre aspas, sem exigir as aspas) e nos
nomes do código (`ctypes.windll.shell32.ShellExecuteExW`), mas nunca nos comentários `#` nem nas docstrings: ali se pode
falar de tudo (explicar por que um `DETACHED_PROCESS` foi tirado, por exemplo). Esta é a correção 1 do plano-v3,
passo 0: o esboço só olhava textos com as aspas dentro e não via os nomes.

Como funciona: o `tokenize` do Python acha os comentários (sabe que um `#` dentro de um texto não é comentário) e o
`ast` acha as docstrings; as duas coisas são apagadas (trocadas por espaços, para as colunas não andarem) e o resto,
linha por linha, é o "código" que o porteiro lê. As linhas são as do Python (`\\n`, `\\r\\n` ou `\\r`), as mesmas que o
`ast` numera.

Seguro mexer: acrescentar uma leitura nova (ex.: as funções de um arquivo). Arriscado: deixar passar comentário ou
docstring para a busca (vira alarme falso) ou apagar código de verdade (o porteiro fica cego àquele trecho).
"""

from __future__ import annotations

import ast
import io
import re
import tokenize
import warnings
from dataclasses import dataclass

_QUEBRA = re.compile(r"\r\n|\r|\n")


class CodigoIlegivel(ValueError):
    """O arquivo não é Python que o Python 3.14 consiga ler (o porteiro acusa isso como achado, nunca como "passou")."""


def sem_marca_de_utf8(fonte: str) -> str:
    """Tira a marca de UTF-8 do começo do arquivo (o Python a aceita; o `ast` recebendo o texto, não)."""
    return fonte.removeprefix("\ufeff")


def linhas(fonte: str) -> list[str]:
    """As linhas do arquivo, cortadas como o Python corta (a linha 1 é o índice 0)."""
    return _QUEBRA.split(sem_marca_de_utf8(fonte))


def _coluna_em_letras(linha: str, coluna_em_bytes: int) -> int:
    """O `ast` conta a coluna em bytes UTF-8; o texto da linha conta em letras. Converte uma na outra."""
    return len(linha.encode("utf-8")[:coluna_em_bytes].decode("utf-8", errors="ignore"))


def arvore(fonte: str) -> ast.Module:
    """A árvore do código; `CodigoIlegivel` se não for Python válido."""
    try:
        with warnings.catch_warnings():
            # Aviso do Python sobre o código lido (ex.: "\p" num texto) não é assunto do porteiro.
            warnings.simplefilter("ignore", SyntaxWarning)
            return ast.parse(sem_marca_de_utf8(fonte))
    except (SyntaxError, ValueError) as erro:
        raise CodigoIlegivel(f"não é Python válido (linha {getattr(erro, 'lineno', '?')}): {erro}") from erro


def _docstrings(raiz: ast.AST) -> list[ast.Constant]:
    """Os nós das docstrings (do módulo, das classes e das funções)."""
    achadas = []
    for no in ast.walk(raiz):
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and no.body:
            primeiro = no.body[0]
            if (isinstance(primeiro, ast.Expr) and isinstance(primeiro.value, ast.Constant)
                    and isinstance(primeiro.value.value, str)):
                achadas.append(primeiro.value)
    return achadas


def linhas_de_codigo(fonte: str) -> list[str]:
    """As linhas do arquivo sem comentários `#` e sem docstrings (trocados por espaços).

    Levanta `CodigoIlegivel` se o arquivo não for Python válido.
    """
    fonte = sem_marca_de_utf8(fonte)
    raiz = arvore(fonte)
    texto = [list(l) for l in linhas(fonte)]

    def apagar(l1: int, c1: int, l2: int, c2: int) -> None:
        """Troca por espaços do (linha l1, coluna c1) até (l2, c2), linhas contadas a partir de 1, colunas em letras."""
        for n in range(l1, l2 + 1):
            if n - 1 >= len(texto):
                break
            linha = texto[n - 1]
            ini = c1 if n == l1 else 0
            fim = c2 if n == l2 else len(linha)
            for i in range(ini, min(fim, len(linha))):
                linha[i] = " "

    try:
        for tok in tokenize.generate_tokens(io.StringIO(fonte).readline):
            if tok.type == tokenize.COMMENT:
                apagar(tok.start[0], tok.start[1], tok.end[0], tok.end[1])
    except (tokenize.TokenError, SyntaxError) as erro:
        raise CodigoIlegivel(f"não deu para separar os comentários: {erro}") from erro
    originais = linhas(fonte)
    for doc in _docstrings(raiz):
        l1, l2 = doc.lineno, doc.end_lineno or doc.lineno
        c1 = _coluna_em_letras(originais[l1 - 1], doc.col_offset)
        c2 = _coluna_em_letras(originais[l2 - 1], doc.end_col_offset or 0)
        apagar(l1, c1, l2, c2)
    return ["".join(l) for l in texto]


def sem_comentarios_de_folha_de_estilo(codigo: list[str]) -> list[str]:
    """Tira os comentários `/* ... */` (os da folha de estilo do Qt, que ninguém vê na tela), mesmo em várias linhas.

    Correção 3 do plano-v3, passo 0: o comentário de `ui/estilo.py` ("etapa 6 da obra... (D-015, lyupdf)") estava
    dentro do texto da folha de estilo e o esboço o contava como número de decisão na tela. Vale para toda folha de
    estilo, não só a do `ui/estilo.py`: um comentário `/* */` nunca aparece para o Kaique.
    """
    junto = "\n".join(codigo)
    limpo = re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), junto, flags=re.S)
    return limpo.split("\n")


@dataclass(frozen=True)
class Funcao:
    """Uma função (ou método) do arquivo: nome com a classe na frente, linhas de começo e fim, e se tem docstring."""

    nome: str
    inicio: int
    fim: int
    tem_docstring: bool
    dentro_de_outra_funcao: bool


def funcoes(raiz: ast.Module) -> list[Funcao]:
    """Todas as funções e métodos, com o nome completo (`Classe.metodo`, `fora.dentro`)."""
    saida: list[Funcao] = []

    def andar(no: ast.AST, prefixo: str, em_funcao: bool) -> None:
        for filho in ast.iter_child_nodes(no):
            if isinstance(filho, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nome = f"{prefixo}{filho.name}"
                # O começo conta os decoradores: mudar um decorador é mexer na função.
                inicio = min([filho.lineno] + [d.lineno for d in filho.decorator_list])
                saida.append(Funcao(nome, inicio, filho.end_lineno or filho.lineno,
                                    bool((ast.get_docstring(filho) or "").strip()), em_funcao))
                andar(filho, nome + ".", True)
            elif isinstance(filho, ast.ClassDef):
                andar(filho, f"{prefixo}{filho.name}.", em_funcao)
            else:
                andar(filho, prefixo, em_funcao)

    andar(raiz, "", False)
    return saida


def funcao_em_volta(raiz: ast.Module, numero_da_linha: int) -> str:
    """O nome da função mais de dentro que contém a linha (ou "" se a linha está fora de qualquer função)."""
    melhor = ""
    tamanho = None
    for f in funcoes(raiz):
        if f.inicio <= numero_da_linha <= f.fim and (tamanho is None or f.fim - f.inicio < tamanho):
            melhor, tamanho = f.nome, f.fim - f.inicio
    return melhor


def importacoes(raiz: ast.Module, pacote_do_arquivo: str = "") -> list[tuple[int, str]]:
    """(linha, nome do módulo importado) de cada `import x` e `from x import y`; o relativo vira absoluto.

    `pacote_do_arquivo` é o pacote onde o arquivo mora (ex.: "core" para `core/filtros.py`), para resolver
    `from ..ui import x`.
    """
    saida = []
    partes = [p for p in pacote_do_arquivo.split(".") if p]
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            saida += [(no.lineno, a.name) for a in no.names]
        elif isinstance(no, ast.ImportFrom):
            if no.level:
                base = partes[: len(partes) - (no.level - 1)] if no.level - 1 <= len(partes) else []
                nome = ".".join(base + ([no.module] if no.module else []))
                if not no.module:
                    saida += [(no.lineno, ".".join(base + [a.name])) for a in no.names]
                    continue
            else:
                nome = no.module or ""
            saida.append((no.lineno, nome))
    return saida
