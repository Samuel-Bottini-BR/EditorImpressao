"""Tabela "campo de ConfigPagina / ConfigFolha -> todo lugar que grava nele".

Script de apoio da vistoria de gambiarras de 26/11/2026 (CLAUDE.md §11.12: o
mesmo dado da pagina gravado em lugares diferentes e suspeita obrigatoria; a
regra pede "um dado da pagina e lido e gravado por uma funcao so").

O QUE FAZ
    Le o codigo com `ast` (nunca importa nem roda o programa), nesta ordem:
    1. tira os campos das duas dataclasses de `modelos.py` (as anotacoes do
       corpo da classe; `ClassVar` fica de fora);
    2. junta os atributos de TODAS as outras classes do codigo (core/, ui/,
       modelos.py e os .py da raiz): anotacoes e atribuicoes no corpo da
       classe e `self.X = ...` dentro dos metodos. Serve so para dizer se o
       nome do campo e exclusivo destas duas classes;
    3. percorre todo .py de `core/` e `ui/` (com subpastas) e anota cada
       gravacao de atributo com o nome de um campo;
    4. grava `campos.md` ao lado deste script.

O QUE CONTA COMO GRAVACAO (o que ele pega)
    - `x.campo = ...`, `x.campo: T = ...`, `x.campo += ...` (e todo operador
      composto), atribuicao multipla (`a = x.campo = ...`) e desempacotada
      (`x.campo, y = ...`, inclusive com `*`), `for x.campo in ...`,
      `with ... as x.campo`;
    - `del x.campo`;
    - `setattr(x, "campo", ...)`, `object.__setattr__(x, "campo", ...)` e
      `x.__setattr__("campo", ...)`; quando o nome vem de uma constante de
      texto do proprio modulo (`_NOME = "campo"`), ela e resolvida e dita;
    - `dataclasses.replace(x, campo=...)` (com `import dataclasses`, com
      `from dataclasses import replace` e com apelido);
    - `ConfigPagina(... campo=...)` e `ConfigFolha(...)`, por palavra-chave
      e por posicao (a posicao e traduzida pela ordem dos campos);
    - mutacao no lugar: `x.campo.append/extend/insert/pop/remove/clear/
      update/setdefault/popitem/sort/reverse/add/discard/__setitem__/
      __delitem__(...)`, `x.campo[i] = ...`, `x.campo[i] += ...`,
      `del x.campo[i]`, e o mesmo por dentro de indices
      (`x.campo[0]["tipo"] = ...`, `x.campo[0].append(...)`).
    - `delattr(x, "campo")`.
    Fica numa lista a parte ("nao da para saber o campo"): `setattr`/`delattr`
    com nome que nao e texto fixo, `replace(..., **algo)`,
    `ConfigPagina(**algo)` / `(*algo)`, e escrita por `x.__dict__[...]`,
    `x.__dict__.update(...)`, `vars(x)[...]` e `vars(x).update(...)`. Essa
    lista inclui tambem `historico_acoes.py` (raiz), porque e ali que as
    acoes do desfazer gravam nas paginas e folhas com `setattr(item, campo,
    ...)`: boa parte da tela grava por esse caminho.

O NOME DO CAMPO ESCRITO COMO TEXTO (coluna a parte, NAO conta como gravacao)
    A tela e o Automatico gravam muito por dados: montam `{"filtro": v}` (ou
    `dict(filtro=v)`, ou listas como `("forca_preto", ...)`) e um aplicador
    generico faz `setattr(pagina, campo, v)` (core/automatico._Gravador,
    historico_acoes). Por isso o script tambem lista, por campo, todo lugar
    de `core/` e `ui/` onde o nome aparece como texto: chave de dicionario
    literal, palavra-chave de `dict(...)`, `d["campo"] = ...`, texto passado
    como argumento a uma funcao (menos `getattr`/`hasattr`, que so leem) e
    item de lista/tupla/conjunto literal. Muitas dessas mencoes sao LEITURAS
    ou listas de nomes; servem para achar a gravacao indireta, nao provam
    que ela existe.

O QUE NAO PEGA (ressalvas; repetidas no topo do campos.md)
    - O TIPO de `x`. A AST nao sabe se `x` e uma ConfigPagina. Toda gravacao
      de atributo com o nome do campo entra, de qualquer objeto. A coluna
      "nome exclusivo?" diz se o nome tambem e atributo de outra classe do
      nosso codigo; objetos de biblioteca (Qt, numpy, PyMuPDF) nao sao
      conferidos. Quando o receptor e `self` dentro de uma classe que nao e
      ConfigPagina/ConfigFolha, a linha e marcada "(self de <Classe>)": e
      fato da AST, nao palpite, e quase certamente NAO e o campo.
    - A gravacao indireta (`na_pagina(p, campo, v)` com `campo` vindo de uma
      lista) nao e ligada ao campo: aparece na lista "nao da para saber" e,
      se o nome estiver escrito como texto em algum lugar, na coluna de
      mencoes por texto.
    - Apelido de lista: `lista = pagina.alertas; lista.append(...)` nao e
      visto (so a mutacao escrita direto em `x.campo`).
    - Gravacao dentro de funcao chamada com o objeto (ex.: `json`, `copy`,
      `deepcopy` + troca inteira da pagina na lista do projeto) nao e
      gravacao de campo e nao aparece.
    - Gravacao em dicionario do projeto.json (`d["filtro"] = ...`) nao e
      atributo e nao aparece.
    - `exec`, `eval`, `getattr(x, n).append(...)` e metaprogramacao nao sao
      seguidos.
    - So `core/` e `ui/`. As gravacoes de dentro de `modelos.py` (migracao
      em Projeto.de_dicionario, guardar_selecao) e dos scripts da raiz e de
      `tests/` ficam de fora de proposito (pedido da vistoria).

COMO RODAR
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe campos_que_gravam.py
    (de qualquer pasta; acha a raiz do projeto pelo caminho deste arquivo).

SEGURO MUDAR: o texto do campos.md, a lista MUTADORES. ARRISCADO: tirar o
`ast.walk` das subpastas (core/nativo e ui/widgets sumiriam da tabela) ou
passar a filtrar por "parece ConfigPagina" (seria adivinhar o tipo, e a
vistoria pediu que nao adivinhasse).
"""

from __future__ import annotations

import ast
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

PASTA_DESTE = Path(__file__).resolve().parent
RAIZ = PASTA_DESTE.parents[1]
# Fora de core/ e ui/, mas e o aplicador das acoes do desfazer: entra SO na
# lista "nao da para saber o campo" (os setattr genericos dele).
SO_PARA_A_LISTA_INDEFINIDA = ("historico_acoes.py",)
# Funcoes cujo argumento de texto e LEITURA, nunca mencao para gravar.
SO_LEEM = {"getattr", "hasattr"}
SAIDA = PASTA_DESTE / "campos.md"
CLASSES_ALVO = ("ConfigFolha", "ConfigPagina")
PASTAS_VARRIDAS = ("core", "ui")

# Metodos que mudam no lugar uma lista, um dicionario ou um conjunto.
MUTADORES = {
    "append", "extend", "insert", "pop", "remove", "clear", "update",
    "setdefault", "popitem", "sort", "reverse", "add", "discard",
    "__setitem__", "__delitem__", "__iadd__",
}


@dataclass
class Gravacao:
    """Uma gravacao achada: onde, em que funcao, de que forma e em quem."""

    campo: str
    arquivo: str
    linha: int
    funcao: str
    forma: str
    receptor: str          # o texto do objeto (`pagina`, `self.projeto.paginas[i]`)
    self_de: str | None    # nome da classe quando o receptor e `self` de outra classe
    classe_certa: str | None = None  # quando a forma diz a classe (o construtor)


@dataclass
class Indefinida:
    """Gravacao em que nao da para saber o campo (nome variavel, **algo...)."""

    arquivo: str
    linha: int
    funcao: str
    forma: str


@dataclass
class Mencao:
    """O nome de um campo escrito como texto (possivel gravacao indireta)."""

    campo: str
    arquivo: str
    linha: int
    funcao: str
    forma: str


def _rel(caminho: Path) -> str:
    """Caminho relativo a raiz, com barra normal (para o campos.md)."""
    return caminho.relative_to(RAIZ).as_posix()


def _curto(no: ast.AST, limite: int = 60) -> str:
    """O codigo de um no em uma linha, cortado se for grande."""
    texto = " ".join(ast.unparse(no).split())
    return texto if len(texto) <= limite else texto[: limite - 3] + "..."


def _ler(caminho: Path) -> ast.Module | None:
    """Arvore do arquivo; None (e aviso no terminal) se ele nao compila."""
    try:
        return ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    except (SyntaxError, UnicodeDecodeError) as erro:
        print(f"aviso: nao li {caminho}: {erro}", file=sys.stderr)
        return None


def campos_das_classes(arvore: ast.Module) -> dict[str, list[str]]:
    """{classe: [campos na ordem da dataclass]} para ConfigFolha e ConfigPagina."""
    resultado: dict[str, list[str]] = {}
    for no in arvore.body:
        if isinstance(no, ast.ClassDef) and no.name in CLASSES_ALVO:
            lista = []
            for item in no.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    if "ClassVar" in ast.unparse(item.annotation):
                        continue
                    lista.append(item.target.id)
            resultado[no.name] = lista
    return resultado


def atributos_de_outras_classes(arquivos: list[Path]) -> dict[str, set[str]]:
    """{nome do atributo: {"Classe (arquivo)", ...}} de toda classe que nao e alvo.

    Pega o corpo da classe (anotacao e atribuicao com nome simples) e
    `self.X = / += / :` dentro de qualquer funcao da classe (inclusive
    funcoes internas, que veem o mesmo `self`)."""
    nomes: dict[str, set[str]] = defaultdict(set)
    for caminho in arquivos:
        arvore = _ler(caminho)
        if arvore is None:
            continue
        for classe in ast.walk(arvore):
            if not isinstance(classe, ast.ClassDef) or classe.name in CLASSES_ALVO:
                continue
            dono = f"{classe.name} ({_rel(caminho)})"
            for item in classe.body:
                alvos = []
                if isinstance(item, ast.AnnAssign):
                    alvos = [item.target]
                elif isinstance(item, ast.Assign):
                    alvos = item.targets
                for alvo in alvos:
                    for nome in ast.walk(alvo):
                        if isinstance(nome, ast.Name):
                            nomes[nome.id].add(dono)
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for no in ast.walk(item):
                        alvos2 = []
                        if isinstance(no, ast.Assign):
                            alvos2 = no.targets
                        elif isinstance(no, (ast.AugAssign, ast.AnnAssign)):
                            alvos2 = [no.target]
                        for alvo in alvos2:
                            for at in ast.walk(alvo):
                                if (isinstance(at, ast.Attribute) and isinstance(at.value, ast.Name)
                                        and at.value.id == "self"):
                                    nomes[at.attr].add(dono)
    return nomes


class Varredor(ast.NodeVisitor):
    """Anda por um arquivo e junta as gravacoes nos campos.

    Guarda a pilha de classes e funcoes para dizer "Classe.metodo" e para
    saber de que classe e o `self` de cada linha."""

    def __init__(self, arquivo: str, arvore: ast.Module, campos: set[str],
                 ordem: dict[str, list[str]]):
        self.arquivo = arquivo
        self.campos = campos
        self.ordem = ordem
        self.pilha: list[tuple[str, str]] = []   # ("classe"|"funcao", nome)
        self.achadas: list[Gravacao] = []
        self.indefinidas: list[Indefinida] = []
        self.mencoes: list[Mencao] = []
        self.apelidos_replace: set[str] = set()      # nomes que sao dataclasses.replace
        self.apelidos_dataclasses: set[str] = set()  # nomes que sao o modulo dataclasses
        self.apelidos_classe: dict[str, str] = {}    # nome local -> ConfigPagina/ConfigFolha
        self.constantes: dict[str, str] = {}         # _NOME = "texto" no nivel do modulo
        self._ler_importacoes(arvore)

    # ---- preparo -----------------------------------------------------
    def _ler_importacoes(self, arvore: ast.Module) -> None:
        """Apelidos de dataclasses/replace/ConfigPagina em qualquer ponto do
        arquivo (ha `from dataclasses import replace` dentro de funcao), e as
        constantes de texto do nivel do modulo."""
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                for a in no.names:
                    if a.name == "dataclasses":
                        self.apelidos_dataclasses.add(a.asname or a.name)
            elif isinstance(no, ast.ImportFrom):
                for a in no.names:
                    if no.module == "dataclasses" and a.name == "replace":
                        self.apelidos_replace.add(a.asname or a.name)
                    if a.name in CLASSES_ALVO:
                        self.apelidos_classe[a.asname or a.name] = a.name
        for no in arvore.body:
            if (isinstance(no, ast.Assign) and len(no.targets) == 1
                    and isinstance(no.targets[0], ast.Name)
                    and isinstance(no.value, ast.Constant) and isinstance(no.value.value, str)):
                self.constantes[no.targets[0].id] = no.value.value

    # ---- contexto ----------------------------------------------------
    def _funcao(self) -> str:
        """`Classe.metodo` (com funcoes internas: `Classe.metodo.interna`)."""
        if not self.pilha:
            return "(nivel do modulo)"
        return ".".join(nome for _, nome in self.pilha)

    def _classe_do_self(self) -> str | None:
        """A classe da funcao mais de fora dentro da classe mais de dentro:
        e dela o `self` (metodo, ou funcao interna de um metodo)."""
        for i in range(len(self.pilha) - 1, -1, -1):
            tipo, nome = self.pilha[i]
            if tipo == "classe":
                return nome if i + 1 < len(self.pilha) else None
        return None

    def visit_ClassDef(self, no: ast.ClassDef) -> None:
        self.pilha.append(("classe", no.name))
        self.generic_visit(no)
        self.pilha.pop()

    def visit_FunctionDef(self, no) -> None:
        self.pilha.append(("funcao", no.name))
        self.generic_visit(no)
        self.pilha.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Lambda(self, no: ast.Lambda) -> None:
        self.pilha.append(("funcao", "<lambda>"))
        self.generic_visit(no)
        self.pilha.pop()

    # ---- registro ----------------------------------------------------
    def _anotar(self, campo: str, linha: int, forma: str, receptor: ast.AST | None,
                classe_certa: str | None = None) -> None:
        self_de = None
        texto = "-"
        if receptor is not None:
            texto = _curto(receptor)
            if isinstance(receptor, ast.Name) and receptor.id == "self":
                dono = self._classe_do_self()
                if dono and dono not in CLASSES_ALVO:
                    self_de = dono
        self.achadas.append(Gravacao(campo, self.arquivo, linha, self._funcao(), forma,
                                     texto, self_de, classe_certa))

    def _indefinida(self, linha: int, forma: str) -> None:
        self.indefinidas.append(Indefinida(self.arquivo, linha, self._funcao(), forma))

    def _mencao(self, no: ast.AST, forma: str) -> None:
        """Anota `no` se ele e um texto fixo igual ao nome de um campo."""
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and no.value in self.campos:
            self.mencoes.append(Mencao(no.value, self.arquivo, no.lineno, self._funcao(), forma))

    def visit_Dict(self, no: ast.Dict) -> None:
        for chave in no.keys:
            if chave is not None:
                self._mencao(chave, 'chave de dicionario {"campo": ...}')
        self.generic_visit(no)

    def _itens(self, no) -> None:
        for item in no.elts:
            self._mencao(item, f"item de {type(no).__name__.lower()} literal")
        self.generic_visit(no)

    visit_List = visit_Tuple = visit_Set = _itens

    @staticmethod
    def _tirar_indices(no: ast.AST) -> tuple[ast.AST, bool]:
        """Desce por `a[i][j]` ate `a`; diz se desceu algum indice."""
        desceu = False
        while isinstance(no, ast.Subscript):
            no, desceu = no.value, True
        return no, desceu

    def _alvo(self, alvo: ast.AST, forma: str, linha: int) -> None:
        """Uma coisa do lado esquerdo de uma atribuicao (ou de del/for/with)."""
        if isinstance(alvo, (ast.Tuple, ast.List)):
            for item in alvo.elts:
                self._alvo(item, "desempacotada: " + forma if "desempacotada" not in forma else forma,
                           linha)
            return
        if isinstance(alvo, ast.Starred):
            self._alvo(alvo.value, forma, linha)
            return
        if isinstance(alvo, ast.Attribute) and alvo.attr in self.campos:
            self._anotar(alvo.attr, linha, forma.replace("CAMPO", alvo.attr), alvo.value)
            return
        if isinstance(alvo, ast.Subscript):
            base, _ = self._tirar_indices(alvo)
            if isinstance(base, ast.Attribute) and base.attr in self.campos:
                self._anotar(base.attr, linha,
                             "mutacao no lugar: " + forma.replace("x.CAMPO", f"x.{base.attr}[...]"),
                             base.value)
                return
            if isinstance(alvo.slice, ast.Constant):
                self._mencao(alvo.slice, f'{_curto(alvo.value, 30)}["campo"] = ...')
            # vars(x)[...] = / x.__dict__[...] =
            if (isinstance(base, ast.Call) and isinstance(base.func, ast.Name)
                    and base.func.id == "vars") or (
                    isinstance(base, ast.Attribute) and base.attr == "__dict__"):
                self._indefinida(linha, f"{_curto(alvo)} (escrita por dicionario)")

    # ---- formas ------------------------------------------------------
    def visit_Assign(self, no: ast.Assign) -> None:
        forma = "x.CAMPO = ..." if len(no.targets) == 1 else "atribuicao multipla: x.CAMPO = ... = ..."
        for alvo in no.targets:
            self._alvo(alvo, forma, alvo.lineno)
        self.generic_visit(no)

    def visit_AnnAssign(self, no: ast.AnnAssign) -> None:
        if no.value is not None:
            self._alvo(no.target, "x.CAMPO: T = ...", no.lineno)
        self.generic_visit(no)

    def visit_AugAssign(self, no: ast.AugAssign) -> None:
        simbolo = {ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/", ast.BitOr: "|",
                   ast.BitAnd: "&", ast.FloorDiv: "//", ast.Mod: "%"}.get(type(no.op), "?")
        self._alvo(no.target, f"x.CAMPO {simbolo}= ...", no.lineno)
        self.generic_visit(no)

    def visit_Delete(self, no: ast.Delete) -> None:
        for alvo in no.targets:
            self._alvo(alvo, "del x.CAMPO", alvo.lineno)
        self.generic_visit(no)

    def visit_For(self, no) -> None:
        self._alvo(no.target, "for x.CAMPO in ...", no.lineno)
        self.generic_visit(no)

    visit_AsyncFor = visit_For

    def visit_With(self, no) -> None:
        for item in no.items:
            if item.optional_vars is not None:
                self._alvo(item.optional_vars, "with ... as x.CAMPO", no.lineno)
        self.generic_visit(no)

    visit_AsyncWith = visit_With

    def _nome_fixo(self, arg: ast.AST) -> tuple[str | None, str]:
        """O texto do nome de atributo de um setattr: (nome, de onde veio)."""
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            return arg.value, ""
        if isinstance(arg, ast.Name) and arg.id in self.constantes:
            return self.constantes[arg.id], f" (nome tirado da constante {arg.id})"
        return None, ""

    def visit_Call(self, no: ast.Call) -> None:
        f = no.func
        nome_f = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else None)

        # setattr(x, "campo", v) / object.__setattr__(x, "campo", v)
        eh_setattr = (isinstance(f, ast.Name) and f.id in ("setattr", "delattr")) or (
            isinstance(f, ast.Attribute) and f.attr == "__setattr__"
            and isinstance(f.value, ast.Name) and f.value.id == "object")
        if eh_setattr and len(no.args) >= 2:
            nome, origem = self._nome_fixo(no.args[1])
            if nome is None:
                self._indefinida(no.lineno, f"{_curto(no, 90)} (nome do atributo variavel)")
            elif nome in self.campos:
                quem = f.id if isinstance(f, ast.Name) else "object.__setattr__"
                self._anotar(nome, no.lineno, f'{quem}(x, "{nome}", ...){origem}', no.args[0])
        # x.__setattr__("campo", v)
        elif (isinstance(f, ast.Attribute) and f.attr == "__setattr__" and no.args):
            nome, origem = self._nome_fixo(no.args[0])
            if nome is None:
                self._indefinida(no.lineno, f"{_curto(no, 90)} (nome do atributo variavel)")
            elif nome in self.campos:
                self._anotar(nome, no.lineno, f'x.__setattr__("{nome}", ...){origem}', f.value)

        # dataclasses.replace(x, campo=...)
        eh_replace = (isinstance(f, ast.Name) and f.id in self.apelidos_replace) or (
            isinstance(f, ast.Attribute) and f.attr == "replace"
            and isinstance(f.value, ast.Name) and f.value.id in self.apelidos_dataclasses)
        if eh_replace:
            receptor = no.args[0] if no.args else None
            for kw in no.keywords:
                if kw.arg is None:
                    self._indefinida(no.lineno, f"replace(..., **{_curto(kw.value)})")
                elif kw.arg in self.campos:
                    self._anotar(kw.arg, kw.lineno, f"replace(x, {kw.arg}=...)", receptor)

        # ConfigPagina(...) / ConfigFolha(...)
        classe = None
        if isinstance(f, ast.Name) and f.id in self.apelidos_classe:
            classe = self.apelidos_classe[f.id]
        elif isinstance(f, ast.Attribute) and f.attr in CLASSES_ALVO:
            classe = f.attr
        if classe:
            ordem = self.ordem.get(classe, [])
            for i, arg in enumerate(no.args):
                if isinstance(arg, ast.Starred):
                    self._indefinida(no.lineno, f"{classe}(*{_curto(arg.value)})")
                    break
                if i < len(ordem):
                    self._anotar(ordem[i], arg.lineno, f"{classe}(...) por posicao ({i + 1}o)", None,
                                 classe)
            for kw in no.keywords:
                if kw.arg is None:
                    self._indefinida(no.lineno, f"{classe}(**{_curto(kw.value)})")
                elif kw.arg in self.campos:
                    self._anotar(kw.arg, kw.lineno, f"{classe}({kw.arg}=...)", None, classe)

        # o nome do campo como texto num argumento, ou em dict(campo=...)
        if not eh_setattr and not (isinstance(f, ast.Name) and f.id in SO_LEEM):
            for arg in no.args:
                self._mencao(arg, f"texto passado a {_curto(f, 40)}(...)")
        if isinstance(f, ast.Name) and f.id == "dict":
            for kw in no.keywords:
                if kw.arg in self.campos:
                    self.mencoes.append(Mencao(kw.arg, self.arquivo, kw.lineno, self._funcao(),
                                               f"dict({kw.arg}=...)"))

        # x.campo.append(...) / x.campo[i].update(...)
        if isinstance(f, ast.Attribute) and nome_f in MUTADORES:
            base, desceu = self._tirar_indices(f.value)
            if isinstance(base, ast.Attribute) and base.attr in self.campos:
                texto = f"x.{base.attr}{'[...]' if desceu else ''}.{nome_f}(...)"
                self._anotar(base.attr, no.lineno, "mutacao no lugar: " + texto, base.value)
            elif isinstance(base, ast.Attribute) and base.attr == "__dict__" and nome_f != "get":
                self._indefinida(no.lineno, f"{_curto(no, 90)} (escrita por dicionario)")
            elif (isinstance(base, ast.Call) and isinstance(base.func, ast.Name)
                  and base.func.id == "vars"):
                self._indefinida(no.lineno, f"{_curto(no, 90)} (escrita por dicionario)")
        self.generic_visit(no)


def _arquivos(pastas: tuple[str, ...]) -> list[Path]:
    """Todo .py das pastas, com subpastas, sem __pycache__, em ordem."""
    lista = []
    for pasta in pastas:
        lista += [p for p in (RAIZ / pasta).rglob("*.py") if "__pycache__" not in p.parts]
    return sorted(lista)


def _parte(arquivo: str) -> str:
    return arquivo.split("/", 1)[0]


def montar() -> str:
    """Le tudo e devolve o texto do campos.md."""
    arvore_modelos = _ler(RAIZ / "modelos.py")
    if arvore_modelos is None:
        raise SystemExit("nao consegui ler modelos.py")
    ordem = campos_das_classes(arvore_modelos)
    faltou = [c for c in CLASSES_ALVO if c not in ordem]
    if faltou:
        raise SystemExit(f"nao achei a classe {faltou} em modelos.py")
    dono_do_campo: dict[str, list[str]] = defaultdict(list)
    for classe in CLASSES_ALVO:
        for c in ordem[classe]:
            dono_do_campo[c].append(classe)
    campos = set(dono_do_campo)

    varridos = _arquivos(PASTAS_VARRIDAS)
    outros = atributos_de_outras_classes(
        varridos + [RAIZ / "modelos.py"] + sorted(p for p in RAIZ.glob("*.py") if p.name != "modelos.py"))

    achadas: list[Gravacao] = []
    indefinidas: list[Indefinida] = []
    mencoes: list[Mencao] = []
    for caminho in varridos:
        arvore = _ler(caminho)
        if arvore is None:
            continue
        v = Varredor(_rel(caminho), arvore, campos, ordem)
        v.visit(arvore)
        achadas += v.achadas
        indefinidas += v.indefinidas
        mencoes += v.mencoes
    for nome in SO_PARA_A_LISTA_INDEFINIDA:
        arvore = _ler(RAIZ / nome)
        if arvore is not None:
            v = Varredor(nome, arvore, campos, ordem)
            v.visit(arvore)
            indefinidas += v.indefinidas
    por_mencao: dict[str, list[Mencao]] = defaultdict(list)
    for m in mencoes:
        por_mencao[m.campo].append(m)

    por_campo: dict[str, list[Gravacao]] = defaultdict(list)
    for g in achadas:
        por_campo[g.campo].append(g)

    def exclusivo(campo: str) -> str:
        donos = sorted(outros.get(campo, ()))
        if not donos:
            return "sim, so destas classes"
        # Todos, sem cortar: quem confere precisa ver, por exemplo, que
        # `filtro` tambem e campo de Regiao (core/selecao.py).
        return f"NAO: tambem e atributo de {', '.join(donos)}"

    def contas(lista: list[Gravacao]) -> tuple[int, int, int]:
        return (len(lista), len({(g.arquivo, g.funcao) for g in lista}),
                len({g.arquivo for g in lista}))

    def classes_txt(campo: str) -> str:
        donos = dono_do_campo[campo]
        return " e ".join(donos) + (" (campo nas DUAS)" if len(donos) == 2 else "")

    linhas: list[str] = []
    w = linhas.append
    total_campos = len(campos)
    w("# Campos de ConfigPagina / ConfigFolha: todo lugar de `core/` e `ui/` que grava neles")
    w("")
    w(f"Gerado em {date.today():%d/%m/%Y} por `relatorios/vistoria-gambiarras-2026-11-26/campos_que_gravam.py`, "
      "lendo o codigo com `ast` (sem importar nem rodar o programa). Insumo da vistoria de gambiarras "
      "(CLAUDE.md §11.12: o mesmo campo gravado em lugares diferentes e suspeita obrigatoria).")
    w("")
    w("## Leia antes (ressalvas)")
    w("")
    w("- **A tabela nao sabe o tipo do objeto.** Toda gravacao de atributo com o nome de um campo entra, "
      "de qualquer objeto. Quando o nome tambem e atributo de outra classe do nosso codigo (coluna "
      "\"nome exclusivo?\", ex.: `recorte`, `alertas`, `indice`), a linha PODE NAO SER de ConfigPagina/"
      "ConfigFolha: confira no codigo. Objetos de biblioteca (Qt, numpy, PyMuPDF) nao entram nessa conferencia.")
    w("- **\"(self de Classe)\"** marca a linha cujo receptor e `self` dentro de uma classe que nao e "
      "ConfigPagina/ConfigFolha: e fato lido na AST, e quase certamente NAO e o campo. A coluna "
      "\"sem self de outra\" do resumo conta sem essas linhas.")
    w("- **Nao pega:** apelido de lista (`l = pagina.alertas; l.append(...)`); troca da pagina inteira por "
      "outra (`deepcopy`, `projeto.paginas[i] = nova`); dicionario do projeto.json (`d[\"filtro\"] = ...`); "
      "`exec`/`eval`/`getattr(x, n).append(...)`; e as gravacoes de dentro de `modelos.py` (migracao em "
      "`Projeto.de_dicionario`, `guardar_selecao`), dos scripts da raiz e de `tests/`.")
    w("- **Pega:** `x.campo =`, `+=` e demais compostos, atribuicao multipla e desempacotada, `for`/`with` "
      "com o campo como alvo, `del`, `setattr(x, \"campo\")` (e com o nome numa constante de texto do modulo), "
      "`object.__setattr__`, `dataclasses.replace(x, campo=)`, `ConfigPagina(...)`/`ConfigFolha(...)` por "
      "nome e por posicao, e mutacao no lugar (`.append/.extend/.insert/.pop/.remove/.clear/.update/...`, "
      "`x.campo[i] =`, `del x.campo[i]`, tambem por dentro de indices).")
    w("- **Boa parte da tela e do Automatico grava por dados**: monta `{\"filtro\": v}` e um aplicador "
      "generico faz `setattr(pagina, campo, v)` (`core/automatico._Gravador`, `historico_acoes.py`). Essa "
      "gravacao nao aparece ligada ao campo. Por isso cada campo traz tambem \"nome como texto\": os lugares "
      "onde o nome esta escrito como texto (chave de dicionario, `dict(campo=)`, `d[\"campo\"] =`, argumento "
      "de funcao fora `getattr`/`hasattr`, item de lista/tupla). Isso NAO e contado como gravacao: muitas sao "
      "leituras ou listas de nomes. Campo com zero gravacoes e varias mencoes por texto quase certamente e "
      "gravado por esse caminho indireto.")
    w("- O que nao da para saber o campo (nome variavel, `**algo`, `__dict__`, `vars`) esta numa lista a parte, "
      "no fim do resumo. Ali podem estar gravacoes em QUALQUER campo, inclusive nos que aparecem com zero.")
    w("- \"Funcoes diferentes\" conta pares (arquivo, funcao); funcoes internas e `<lambda>` contam a parte "
      "(`Classe.metodo.interna`).")
    w("")
    n_ui_core = sum(1 for c in por_campo if {_parte(g.arquivo) for g in por_campo[c]} >= {"core", "ui"})
    w(f"**Numeros:** {total_campos} campos ({len(ordem['ConfigFolha'])} de ConfigFolha, "
      f"{len(ordem['ConfigPagina'])} de ConfigPagina, "
      f"{sum(1 for c in campos if len(dono_do_campo[c]) == 2)} nas duas); {len(achadas)} gravacoes achadas em "
      f"{len({g.arquivo for g in achadas})} arquivos; {len(por_campo)} campos com alguma gravacao; "
      f"{len(mencoes)} mencoes do nome como texto; "
      f"{n_ui_core} gravados ao mesmo tempo em `ui/` e em `core/`; {len(indefinidas)} gravacoes sem campo sabido "
      f"(contando `historico_acoes.py`); "
      f"{len(varridos)} arquivos lidos.")
    w("")
    w("## Resumo (os campos com mais lugares primeiro)")
    w("")
    w("Ordem: funcoes diferentes, depois gravacoes, depois arquivos. \"UI+CORE\" = gravado em `ui/` e em `core/`.")
    w("")
    w("| campo | classe | funcoes | gravacoes | arquivos | sem self de outra (func./grav.) | ui e core "
      "| nome como texto (lugares/arquivos) | nome exclusivo? |")
    w("|---|---|---:|---:|---:|---:|---|---:|---|")

    def chave(c: str):
        g, f, a = contas(por_campo.get(c, []))
        return (-f, -g, -a, c)

    for c in sorted(campos, key=chave):
        lista = por_campo.get(c, [])
        g, f, a = contas(lista)
        limpos = [x for x in lista if x.self_de is None]
        g2, f2, _ = contas(limpos)
        partes = {_parte(x.arquivo) for x in lista}
        marca = "**UI+CORE**" if partes >= {"core", "ui"} else ("so ui" if partes == {"ui"} else
                                                                 ("so core" if partes == {"core"} else "-"))
        ms = por_mencao.get(c, [])
        w(f"| `{c}` | {classes_txt(c)} | {f} | {g} | {a} | {f2}/{g2} | {marca} "
          f"| {len(ms)}/{len({m.arquivo for m in ms})} | {exclusivo(c)} |")
    w("")
    w("### Gravacoes em que nao da para saber o campo")
    w("")
    if not indefinidas:
        w("Nenhuma.")
    else:
        w("| onde | funcao | forma |")
        w("|---|---|---|")
        for i in sorted(indefinidas, key=lambda x: (x.arquivo, x.linha)):
            w(f"| `{i.arquivo}:{i.linha}` | `{i.funcao}` | `{i.forma}` |")
    w("")
    w("## Por campo")
    w("")
    for c in sorted(campos, key=chave):
        lista = sorted(por_campo.get(c, []), key=lambda x: (x.arquivo, x.linha))
        g, f, a = contas(lista)
        w(f"### `{c}`")
        w("")
        w(f"{classes_txt(c)} · nome exclusivo? {exclusivo(c)} · **{g} gravacoes, {f} funcoes diferentes, "
          f"{a} arquivos**")
        w("")
        if not lista:
            w("Nenhuma gravacao direta achada em `core/` nem `ui/` (veja a lista \"nao da para saber o campo\" "
              "e o nome como texto, abaixo).")
        for x in lista:
            extra = f" (self de {x.self_de})" if x.self_de else ""
            certa = f" [classe certa: {x.classe_certa}]" if x.classe_certa else ""
            rec = f" · em `{x.receptor}`" if x.receptor != "-" else ""
            w(f"- `{x.arquivo}:{x.linha}` · `{x.funcao}` · {x.forma}{rec}{extra}{certa}")
        ms = sorted(por_mencao.get(c, []), key=lambda m: (m.arquivo, m.linha))
        if ms:
            w("")
            w(f"Nome como texto ({len(ms)}; nao e gravacao, pode ser gravacao indireta ou leitura):")
            w("")
            for m in ms:
                w(f"  - `{m.arquivo}:{m.linha}` · `{m.funcao}` · {m.forma}")
        w("")
    return "\n".join(linhas) + "\n"


if __name__ == "__main__":
    texto = montar()
    SAIDA.write_text(texto, encoding="utf-8")
    print(f"gravado: {SAIDA}")
