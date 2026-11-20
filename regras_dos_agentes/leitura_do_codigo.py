"""A peça única de leitura de código Python para o porteiro: o que é código, o que é comentário, o que é docstring.

O porteiro procura palavras nas linhas de código (inclusive dentro dos textos entre aspas, sem exigir as aspas) e nos
nomes do código (`ctypes.windll.shell32.ShellExecuteExW`), mas nunca nos comentários `#` nem nas docstrings: ali se pode
falar de tudo (explicar por que um `DETACHED_PROCESS` foi tirado, por exemplo). Esta é a correção 1 do plano-v3,
passo 0: o esboço só olhava textos com as aspas dentro e não via os nomes.

Como funciona: o `tokenize` do Python acha os comentários (sabe que um `#` dentro de um texto não é comentário) e o
`ast` acha as docstrings; as duas coisas são apagadas (trocadas por espaços, para as colunas não andarem) e o resto,
linha por linha, é o "código" que o porteiro lê. As linhas são as do Python (`\\n`, `\\r\\n` ou `\\r`), as mesmas que o
`ast` numera.

A K25 (D-809) lê outra coisa: os comandos de terminal que o arquivo manda rodar (`comandos`), pela estrutura do
código (a chamada do `subprocess`, a lista que começa com `git`, o texto que começa com o comando), nunca o texto
solto: assim o exemplo errado escrito dentro de um teste não conta como comando do teste.

Seguro mexer: acrescentar uma leitura nova (ex.: as funções de um arquivo). Arriscado: deixar passar comentário ou
docstring para a busca (vira alarme falso) ou apagar código de verdade (o porteiro fica cego àquele trecho); em
`comandos`, ler texto solto como comando (o exemplo de cada teste vira alarme falso).
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


FOLHA_DE_ESTILO = re.compile(r"\bQ[A-Z]\w*(?:::?[\w-]+)*\s*\{\{?\s*[\w-]+\s*:")


def sem_comentarios_de_folha_de_estilo(codigo: list[str], raiz: ast.Module, fonte: str) -> list[str]:
    """Tira os comentários `/* ... */` de dentro dos textos de folha de estilo do Qt (que ninguém vê na tela).

    Correção 3 do plano-v3, passo 0: o comentário de `ui/estilo.py` ("etapa 6 da obra... (D-015, lyupdf)") estava
    dentro do texto da folha de estilo e o esboço o contava como número de decisão na tela.

    Só dentro do MESMO texto (um nó de texto do código, inclusive um f-string em várias linhas) que tem cara de folha
    de estilo (tem "{" e "}"): um `"imagens/*"` num texto e um `"*/fim"` em outro não apagam o que fica entre os
    dois (achado 10 de quem tentou quebrar, 19/11). `codigo` são as linhas já sem comentário `#` nem docstring.
    """
    texto = [list(l) for l in codigo]
    originais = linhas(fonte)
    for no in ast.walk(raiz):
        if not isinstance(no, (ast.Constant, ast.JoinedStr)) or not getattr(no, "end_lineno", None):
            continue
        if isinstance(no, ast.Constant) and not isinstance(no.value, str):
            continue
        l1, l2 = no.lineno, no.end_lineno
        c1 = _coluna_em_letras(originais[l1 - 1], no.col_offset)
        c2 = _coluna_em_letras(originais[l2 - 1], no.end_col_offset or 0)
        posicoes = [(n, c) for n in range(l1, l2 + 1) for c in range(c1 if n == l1 else 0,
                                                                     c2 if n == l2 else len(texto[n - 1]))
                    if c < len(texto[n - 1])]
        trecho = "".join(texto[n - 1][c] for n, c in posicoes)
        # Cara de folha de estilo do Qt: um seletor (QWidget, QScrollBar::handle:vertical...) seguido de "{" e de uma
        # propriedade com ":" (achado N7 da segunda volta: um f-string comum com "{nome}" e "/* */" não é folha).
        if "/*" not in trecho or not FOLHA_DE_ESTILO.search(trecho):
            continue
        for m in re.finditer(r"/\*.*?\*/", trecho, flags=re.S):
            for k in range(m.start(), m.end()):
                n, c = posicoes[k]
                texto[n - 1][c] = " "
    return ["".join(l) for l in texto]


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
        """Desce na árvore guardando o nome de fora (classe ou função) de cada função achada."""
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


# ----------------------------------------------------------------------------------------------------------------
# Os comandos que o código roda (K25, D-809): o texto de cada comando de terminal que um arquivo Python manda rodar.
# ----------------------------------------------------------------------------------------------------------------

# As funções da biblioteca do Python que rodam um programa ou um comando do terminal (fontes:
# https://docs.python.org/3/library/subprocess.html, https://docs.python.org/3/library/os.html#os.system,
# https://docs.python.org/3/library/asyncio-subprocess.html). `os.exec*` e `os.spawn*` não entram: ninguém no projeto os
# usa, e o nome do programa vem num argumento separado (ficam no "não pega" da K25).
RODAM_COMANDO = {"subprocess": {"run", "Popen", "call", "check_call", "check_output", "getoutput", "getstatusoutput"},
                 "os": {"system", "popen"},
                 "asyncio": {"create_subprocess_exec", "create_subprocess_shell"}}
# Os programas cujo comando guardado numa lista (`["git", "gc"]`) já conta como comando, mesmo antes de ir para uma
# daquelas funções (o comando costuma ser montado numa variável e rodado depois).
PROGRAMAS_DA_LISTA = {"git", "git.exe", "rm", "rm.exe"}
# O texto que fica no lugar do que não é texto escrito no código (um nome, uma conta): um "pedaço que não dá para ler".
NAO_DA_PARA_LER = "<?>"
# O texto que começa com o nome de um comando (o jeito 3 de `comandos`): uma linha de comando guardada num texto.
COMECA_COM_COMANDO = re.compile(r"^\s*(?:git(?:\.exe)?|rm(?:\.exe)?|Remove-Item)\s", re.I)


def _como_texto(no: ast.AST) -> str:
    """O texto de um pedaço do comando: o texto escrito, o f-string com `<?>` no lugar das contas, a lista juntada com
    espaços e a soma de textos; o resto vira `<?>`."""
    if isinstance(no, ast.Constant) and isinstance(no.value, str):
        return no.value
    if isinstance(no, ast.JoinedStr):
        return "".join(v.value if isinstance(v, ast.Constant) else NAO_DA_PARA_LER for v in no.values)
    if isinstance(no, (ast.List, ast.Tuple)):
        return " ".join(_como_texto(e) for e in no.elts)
    if isinstance(no, ast.BinOp) and isinstance(no.op, ast.Add):
        return _como_texto(no.left) + _como_texto(no.right)
    return NAO_DA_PARA_LER


def _quem_roda(raiz: ast.Module) -> tuple[dict[str, str], dict[str, str]]:
    """(apelido do módulo → módulo, nome importado → módulo) para `subprocess`, `os` e `asyncio` neste arquivo."""
    modulos = {m: m for m in RODAM_COMANDO}
    nomes: dict[str, str] = {}
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            for a in no.names:
                if a.name in RODAM_COMANDO:
                    modulos[a.asname or a.name] = a.name
        elif isinstance(no, ast.ImportFrom) and no.module in RODAM_COMANDO and not no.level:
            for a in no.names:
                if a.name in RODAM_COMANDO[no.module]:
                    nomes[a.asname or a.name] = no.module
    return modulos, nomes


def comandos(raiz: ast.Module) -> list[tuple[int, str]]:
    """(linha, o comando como texto) de cada comando de terminal que o arquivo manda rodar (K25, D-809).

    Três jeitos, lidos pela estrutura do código (nunca dentro de um texto qualquer, como o exemplo de um teste):
    1. a chamada de uma função que roda comando (`RODAM_COMANDO`, também pelo apelido do módulo ou importada pelo nome):
       o primeiro argumento (ou `args=`), e no `create_subprocess_exec` todos os argumentos;
    2. a lista ou tupla de textos que começa com um programa de `PROGRAMAS_DA_LISTA` (o comando guardado);
    3. o texto (ou f-string) que começa com o nome de um comando (`git `, `rm `, `Remove-Item `): a linha de comando
       guardada num texto. As docstrings não contam.
    O que não é texto escrito vira `<?>`. Não segue o comando que vai para outra função ou outro arquivo.

    Cuidado nos testes (o jeito 3): um texto de exemplo que COMEÇA com o comando (`"git gc"`, `"rm -rf x"`) conta como
    comando guardado, e o próprio teste é acusado. O exemplo vai dentro de um script maior (com outra linha ou outro
    comando antes) ou numa linha de código (`'subprocess.run(["git", "gc"])'`).
    """
    modulos, nomes = _quem_roda(raiz)
    lidos = {id(d) for d in _docstrings(raiz)}     # o que já foi lido (ou não conta): não se lê duas vezes
    saida: list[tuple[int, str]] = []

    def guardar(linha: int, pedacos: list[ast.AST]) -> None:
        """Guarda o comando feito destes pedaços e marca tudo o que está dentro deles como já lido."""
        saida.append((linha, " ".join(_como_texto(p) for p in pedacos)))
        lidos.update(id(n) for p in pedacos for n in ast.walk(p))

    # 1. As chamadas que rodam comando (primeiro, para o texto delas não ser lido de novo pelos jeitos 2 e 3).
    for no in ast.walk(raiz):
        if not isinstance(no, ast.Call):
            continue
        f = no.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id in modulos:
            nome = f.attr if f.attr in RODAM_COMANDO[modulos[f.value.id]] else None
        else:
            nome = f.id if isinstance(f, ast.Name) and f.id in nomes else None
        if nome is None:
            continue
        partes = list(no.args) if nome == "create_subprocess_exec" else (
            no.args[:1] or [k.value for k in no.keywords if k.arg == "args"])
        if partes:
            guardar(no.lineno, partes)
    # 2 e 3. A lista que começa com o programa e o texto que começa com o comando.
    for no in ast.walk(raiz):
        if id(no) in lidos:
            continue
        if isinstance(no, (ast.List, ast.Tuple)) and no.elts:
            primeiro = no.elts[0]
            if (isinstance(primeiro, ast.Constant) and isinstance(primeiro.value, str)
                    and primeiro.value.replace("\\", "/").rsplit("/", 1)[-1].lower() in PROGRAMAS_DA_LISTA):
                guardar(no.lineno, [no])
        elif isinstance(no, ast.JoinedStr) or (isinstance(no, ast.Constant) and isinstance(no.value, str)):
            if COMECA_COM_COMANDO.match(_como_texto(no)):
                guardar(no.lineno, [no])
            elif isinstance(no, ast.JoinedStr):
                lidos.update(id(n) for n in ast.walk(no))   # os pedaços de um f-string não são textos soltos
    return sorted(saida)
