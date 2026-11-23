"""A trava dos donos: cada capacidade perigosa tem um dono, um arquivo só (D-830, 23/11/2026; terceira volta).

De onde veio. O Samuel decidiu refazer o atualizador ("refazer", 23/11/2026, 18:50) e colou no chat da gerente a
mensagem do Fable: "ela pode mandar escrever a primeira trava (o teste que diz 'só core/windows.py fala com o
Windows'). Esse teste vai falhar hoje de propósito — a lista do que falha é a lista de trabalho do atualizador novo".
Na segunda volta o desenho mudou: "a trava não pergunta 'este import é permitido?', pergunta 'quem é o dono desta
capacidade?'". Na terceira (o Fable revisou os 5 pontos que não fechavam; o Samuel colou a resposta) vieram a catraca, o
mapa final dos donos, os nomes do Windows proibidos ao dono das DLLs e as raízes do programa.

O desenho (o mapa `DONOS`, escrito uma vez só, aqui):
- falar com o Windows (licença, tarefas, registro, mutex, memória, janela, SetDllDirectoryW, os programas da pasta do
  Windows): `core/windows.py`, que pode `ctypes` (tudo, inclusive "o Windows pelo ctypes"), `winreg`, `os.startfile` e
  `subprocess`;
- carregar e chamar as nossas DLLs do ScanTailor: `core/nativo_dll.py` (ainda não existe), que pode `ctypes` e é o
  único que pode carregar DLL (`CDLL`), mas não pode "o Windows pelo ctypes" (`windll`, `WinDLL`, `oledll`, `OleDLL`,
  `wintypes`, `get_last_error`, `FormatError`, `GetLastError`);
- abrir e falar com os nossos processos (OCR, Kraken, servidor de páginas, brasão): `core/processos.py` (ainda não
  existe), que pode `subprocess`.
O `subprocess` tem dois donos. A separação entre os dois (o Windows só lança programa da pasta do Windows; os processos
recusam programa da pasta do Windows) não se vê pelo import: é feita quando o programa roda. Por isso está escrita aqui
como duas pendências paradas até as peças existirem, como a do `CDLL`. "Rodar programa pelo `os`" (`os.system`,
`os.popen`, `os.spawn*`, `os.exec*`) não tem dono: é proibido em todo lugar, até nos donos.

A catraca (no lugar do `xfail`, que perdoava lugar novo). A lista de hoje está congelada aqui (`LISTA_CONGELADA`), lugar
por lugar, e a trava cobra duas coisas: nenhum lugar novo (lugar acusado que não está na lista falha na hora) e nenhum
lugar perdoado à toa (lugar da lista que deixou de ser acusado falha, pedindo para tirar a linha e abaixar o `TETO`).
A lista nunca passa do `TETO`. A chave do lugar é "arquivo | função onde mora | capacidade | o que foi achado", sem o
número da linha: escrever código acima não muda a chave; mudar o lugar de verdade (outra função, outro jeito de
importar, outra capacidade) muda, e aí a catraca acusa um lugar novo e um que sumiu, que é o certo.

O que é "o programa" nesta trava: o fechamento das importações a partir das raízes (`raizes_do_programa`), o que vai
para o Kaique. Não é uma lista: é tirado lendo o código. As raízes:
- `main.py`, de onde o PyInstaller monta o `.exe` (`empacotar.py`: `comando.append(str(RAIZ / "main.py"))`);
- `motor_kraken/servidor_kraken.py`, o motor do Kraken, programa à parte que vai junto (`montar_motor_kraken.py` o copia;
  roda com `python -I servidor_kraken.py`, então procura os módulos na pasta dele, não na raiz do repositório);
- os módulos do `--hidden-import` do `empacotar.py`, lidos da lista `OCULTOS` pela árvore do código (nunca rodando o
  `empacotar.py`). Se a lista deixar de ser um texto fixo, ou ganhar item por outro caminho, a leitura falha e diz onde.
De cada raiz, lê cada `import` e `from ... import` do arquivo, resolve para os arquivos do repositório e repete em cada
arquivo achado. O que não é do repositório (a biblioteca do Python, o PySide6, o numpy) não entra. Conta **toda**
importação escrita no arquivo: a de cima, a de dentro de função, a de dentro de `if` e a de dentro de `try`. É o que o
PyInstaller põe no `.exe`: ele lista os quatro tipos ("top-level", "conditional: imported within an if-statement",
"delayed: imported within a function", "optional: imported within a try-except-statement"; PyInstaller 6.21.0,
`PyInstaller/building/build_main.py`, `WARNFILE_HEADER`). A importação pelo nome escrito num texto
(`__import__("x")`, `importlib.import_module("x")`) também entra quando o nome está escrito por inteiro. O PyInstaller
não a segue ("Analysis can detect nothing", https://pyinstaller.org/en/stable/when-things-go-wrong.html), mas o
programa a carrega quando roda. O porteiro continua com a definição dele (`porteiro.e_programa`); esta trava não a usa.

Por que é um teste à parte, e não uma conferência dentro do porteiro (escolha da primeira volta, no
`relatorios/atualizador-novo/ONDE-PAREI.md`): a lista de exceções do porteiro está "valendo" e só ganha item com o
"sim" do Samuel. Uma conferência nova no porteiro, neste ramo, faria o teste antigo
`test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` falhar (D-605), e o juiz do GitHub nem a veria. Quando for
juntada, esta trava deve substituir a parte da K01 que procura essas mesmas coisas por palavras.

O que ela NÃO pega (escrito para ninguém achar que pega): `multiprocessing` e `asyncio.create_subprocess_*` (outros
jeitos de abrir processo, fora do desenho); `sys.modules["ctypes"]`; o nome montado em pedaços
(`__import__("ct" + "ypes")`); os módulos `nt` e `posix` (onde o `os` busca o `system`); um módulo nosso que guarda o
`subprocess` com outro nome e o entrega por uma função; a importação feita com o nome numa variável; e qual programa ou
qual DLL cada dono abre de verdade (isso só se confere rodando: são as três pendências).

Seguro mexer: o texto das frases; tirar uma linha de `LISTA_CONGELADA` e abaixar o `TETO` quando o lugar for consertado
(é o que a catraca pede). Arriscado: tirar uma capacidade ou um nome de `CAPACIDADES`, dar uma capacidade a mais um
dono em `DONOS` (cada dono novo é uma porta), deixar de seguir algum tipo de importação em `fechamento`, ou tirar uma
raiz. Qualquer um desses afrouxa a trava calado. Proibido, pela própria decisão: pôr linha nova em `LISTA_CONGELADA` ou
subir o `TETO` (a lista é a de 23/11/2026 e só diminui).
"""

from __future__ import annotations

import ast
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes import leitura_do_codigo as leitura

RAIZ = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Raiz:
    """Um começo do programa: o arquivo e a pasta onde o Python procura os módulos que ele importa ("" = a raiz do
    repositório, que é a `--paths` do PyInstaller no `empacotar.py`)."""

    arquivo: str
    pasta: str = ""


# Os começos fixos. O `main.py`: `empacotar.py`, `comando.append(str(RAIZ / "main.py"))`. O motor do Kraken:
# `montar_motor_kraken.py`, `SERVIDOR = PASTA_FONTES / "servidor_kraken.py"`, rodado como
# `python\python.exe -I -X utf8 servidor_kraken.py` (o `-I` tira a pasta atual e o PYTHONPATH; sobra a pasta do script).
ENTRADA = "main.py"
RAIZES_FIXAS = (Raiz(ENTRADA), Raiz("motor_kraken/servidor_kraken.py", "motor_kraken"))
EMPACOTAR = "empacotar.py"          # onde mora a lista dos `--hidden-import` (`OCULTOS`)
LISTA_DOS_OCULTOS = "OCULTOS"

# As capacidades: nome → o que é. Fontes: https://docs.python.org/3/library/ctypes.html,
# https://docs.python.org/3/library/subprocess.html, https://docs.python.org/3/library/winreg.html,
# https://docs.python.org/3/library/os.html#os.startfile e #process-management.
CAPACIDADES = {
    "ctypes": "o módulo ctypes (chamar funções em DLL, inclusive só os tipos)",
    "carregar DLL": "carregar uma DLL pelo ctypes (CDLL, cdll, PyDLL, pydll)",
    "Windows pelo ctypes": ("as partes do ctypes que são do Windows (windll, WinDLL, oledll, OleDLL, wintypes, "
                            "get_last_error, FormatError, GetLastError)"),
    "subprocess": "o módulo subprocess (abrir outro programa)",
    "winreg": "o registro do Windows (winreg)",
    "os.startfile": "abrir arquivo ou programa pelo Windows (os.startfile)",
    "rodar programa pelo os": "rodar programa pelo os (os.system, os.popen, os.spawn*, os.exec*)",
}

# O mapa dos donos: arquivo → as capacidades que só ele pode usar. Lugar único. Capacidade que não aparece aqui não
# tem dono: é proibida em todo arquivo do programa ("rodar programa pelo os").
DONOS: dict[str, frozenset[str]] = {
    "core/windows.py": frozenset({"ctypes", "Windows pelo ctypes", "winreg", "os.startfile", "subprocess"}),
    "core/nativo_dll.py": frozenset({"ctypes", "carregar DLL"}),             # as nossas DLLs (ainda não existe)
    "core/processos.py": frozenset({"subprocess"}),                          # os nossos processos (ainda não existe)
}

# Os nomes dos módulos de cada capacidade de módulo (o `_winreg` é o nome antigo do `winreg`).
_MODULOS = {"ctypes": "ctypes", "subprocess": "subprocess", "winreg": "winreg", "_winreg": "winreg"}
_CARREGAR_DLL = frozenset({"CDLL", "cdll", "PyDLL", "pydll"})
# As partes do ctypes que só existem para o Windows (https://docs.python.org/3/library/ctypes.html: "windll",
# "oledll", "WinDLL", "OleDLL", "ctypes.wintypes", "get_last_error", "FormatError", "GetLastError"; o último também é o
# nome da função do kernel32, pedida como atributo).
_WINDOWS_PELO_CTYPES = frozenset({"windll", "WinDLL", "oledll", "OleDLL", "wintypes", "get_last_error", "FormatError",
                                  "GetLastError"})
_IMPORTA_POR_TEXTO = frozenset({"__import__", "import_module"})
# Os jeitos de pôr módulo no `.exe` do PyInstaller fora da `OCULTOS`, que esta trava não lê (se aparecerem no
# `empacotar.py`, a leitura das raízes falha em vez de passar calada). Fonte: `pyinstaller --help` 6.21.0.
_OUTROS_JEITOS_DE_POR_MODULO = frozenset({"--collect-submodules", "--collect-all", "--hiddenimport"})


def _rodar_programa_pelo_os(nome: str) -> bool:
    """O nome é uma função do `os` que roda outro programa (`system`, `popen`, `spawnl`..., `execv`...)."""
    return nome in ("system", "popen") or nome.startswith(("spawn", "exec"))


# ---------------------------------------------------------------- as raízes do programa

def ocultos_do_empacotar(fonte: str) -> tuple[list[str], list[str]]:
    """(os módulos da lista `OCULTOS` do `empacotar.py`, as falhas da leitura), lidos pela árvore, sem rodar nada.

    Só aceita o jeito de hoje: uma atribuição `OCULTOS = [...]` no corpo do arquivo, com textos fixos, e o
    `--hidden-import` só dentro de um `for ... in OCULTOS`. Qualquer outro jeito (a lista montada por função,
    `OCULTOS.append`, `OCULTOS += ...`, outra atribuição, um `--hidden-import` fora do laço, `--collect-submodules`)
    vira falha que diz a linha: a trava nunca adivinha o que a lista teria se o `empacotar.py` rodasse."""
    try:
        raiz = leitura.arvore(fonte)
    except leitura.CodigoIlegivel as erro:
        return [], [f"{EMPACOTAR}:0: o código não pôde ser lido ({erro})"]
    falhas: list[str] = []
    no_corpo = [no for no in raiz.body if isinstance(no, ast.Assign)
                and any(isinstance(a, ast.Name) and a.id == LISTA_DOS_OCULTOS for a in no.targets)]
    modulos: list[str] = []
    if len(no_corpo) != 1:
        falhas.append(f"{EMPACOTAR}:0: esperava uma atribuição só de {LISTA_DOS_OCULTOS} no corpo do arquivo, "
                      f"achei {len(no_corpo)}")
    else:
        try:
            valor = ast.literal_eval(no_corpo[0].value)
        except ValueError:
            valor = None
        if isinstance(valor, (list, tuple)) and all(isinstance(m, str) for m in valor):
            modulos = list(valor)
        else:
            falhas.append(f"{EMPACOTAR}:{no_corpo[0].lineno}: {LISTA_DOS_OCULTOS} não é uma lista de textos fixos "
                          "(não dá para ler sem rodar)")
    laços_dos_ocultos = [no for no in ast.walk(raiz) if isinstance(no, ast.For)
                         and isinstance(no.iter, ast.Name) and no.iter.id == LISTA_DOS_OCULTOS]
    dentro_dos_laços = {id(n) for laço in laços_dos_ocultos for n in ast.walk(laço)}
    for no in ast.walk(raiz):
        if isinstance(no, ast.Name) and no.id == LISTA_DOS_OCULTOS and not isinstance(no.ctx, ast.Load) \
                and not any(no is a for a in (no_corpo[0].targets if len(no_corpo) == 1 else [])):
            falhas.append(f"{EMPACOTAR}:{no.lineno}: {LISTA_DOS_OCULTOS} é mudada fora da atribuição de cima")
        elif isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) and no.value.id == LISTA_DOS_OCULTOS:
            falhas.append(f"{EMPACOTAR}:{no.lineno}: {LISTA_DOS_OCULTOS}.{no.attr} (a lista pode ganhar item rodando)")
        elif isinstance(no, ast.AugAssign) and isinstance(no.target, ast.Name) and no.target.id == LISTA_DOS_OCULTOS:
            falhas.append(f"{EMPACOTAR}:{no.lineno}: {LISTA_DOS_OCULTOS} ganha item por +=")
        elif isinstance(no, ast.Constant) and no.value == "--hidden-import" and id(no) not in dentro_dos_laços:
            falhas.append(f"{EMPACOTAR}:{no.lineno}: --hidden-import fora do laço de {LISTA_DOS_OCULTOS}")
        elif isinstance(no, ast.Constant) and isinstance(no.value, str) \
                and no.value.split("=")[0] in _OUTROS_JEITOS_DE_POR_MODULO:
            falhas.append(f"{EMPACOTAR}:{no.lineno}: {no.value.split('=')[0]} põe módulo no .exe e esta trava não o lê")
    return modulos, sorted(set(falhas))


def raizes_do_programa(caminhos, ler) -> tuple[list[Raiz], list[str]]:
    """(as raízes do programa, as falhas da leitura): as fixas (`RAIZES_FIXAS`) e os módulos nossos da `OCULTOS`.

    Módulo da `OCULTOS` que não é do repositório (o `doxapy`, o `onnxtr`) fica de fora. Módulo que parece nosso (o
    começo do nome é um pacote ou arquivo do repositório, como `core.`) e não tem arquivo vira falha."""
    caminhos = list(caminhos)
    raizes, falhas = list(RAIZES_FIXAS), []
    if EMPACOTAR not in set(caminhos):
        return raizes, [f"{EMPACOTAR}:0: não está no repositório (é dele que saem os --hidden-import)"]
    fonte = ler(EMPACOTAR)
    if fonte is None:
        return raizes, [f"{EMPACOTAR}:0: não deu para ler o arquivo"]
    modulos, falhas = ocultos_do_empacotar(fonte)
    por_nome = _indice(caminhos, "")
    nossos_de_cima = {nome.split(".")[0] for nome in por_nome}
    for modulo in modulos:
        if modulo in por_nome:
            raizes.append(Raiz(por_nome[modulo]))
        elif modulo.split(".")[0] in nossos_de_cima:
            falhas.append(f"{EMPACOTAR}:0: {LISTA_DOS_OCULTOS} pede {modulo}, que parece nosso e não tem arquivo")
    return raizes, falhas


# ---------------------------------------------------------------- o fechamento das importações

def _nome_do_modulo(caminho: str) -> str:
    """O nome com que o Python importa o arquivo (`core/filtros.py` → `core.filtros`; `core/__init__.py` → `core`)."""
    partes = caminho.rsplit(".", 1)[0].split("/")
    if partes[-1] == "__init__":
        partes = partes[:-1]
    return ".".join(partes)


def _indice(caminhos, pasta: str) -> dict[str, str]:
    """Nome do módulo → arquivo, para quem procura os módulos em `pasta` ("" = a raiz do repositório)."""
    prefixo = pasta + "/" if pasta else ""
    por_nome: dict[str, str] = {}
    for c in caminhos:
        if c.endswith((".py", ".pyw")) and c.startswith(prefixo):
            por_nome.setdefault(_nome_do_modulo(c[len(prefixo):]), c)
    return por_nome


def _pacote(caminho: str) -> list[str]:
    """O pacote onde o arquivo mora, para resolver o `from . import x` (`core/x.py` e `core/__init__.py` → core)."""
    return caminho.split("/")[:-1]


def _texto(no: ast.AST | None) -> str | None:
    """O texto, se o nó é um texto escrito no código; senão None."""
    return no.value if isinstance(no, ast.Constant) and isinstance(no.value, str) else None


def _nome_da_funcao(chamada: ast.Call) -> str:
    """O nome da função chamada (`f(...)` → `f`; `m.f(...)` → `f`); "" se não for um nome."""
    alvo = chamada.func
    return alvo.attr if isinstance(alvo, ast.Attribute) else alvo.id if isinstance(alvo, ast.Name) else ""


def modulos_pedidos(raiz: ast.Module, caminho: str) -> set[str]:
    """Todos os nomes de módulo que o arquivo pode importar, em qualquer lugar do arquivo (em cima, em função, em `if`,
    em `try`), com os pacotes de cima de cada um (importar `a.b.c` roda `a` e `a.b`) e o `x` de `from a import x`
    (pode ser um módulo `a.x`). O relativo vira absoluto (`caminho` é o do arquivo a partir da pasta de busca). Os que
    não são do repositório são filtrados por quem chama."""
    nomes: set[str] = set()
    pacote = _pacote(caminho)

    def com_os_de_cima(nome: str) -> None:
        """Guarda o nome e os pacotes de cima dele."""
        partes = nome.split(".")
        nomes.update(".".join(partes[:n]) for n in range(1, len(partes) + 1))

    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            for apelido in no.names:
                com_os_de_cima(apelido.name)
        elif isinstance(no, ast.ImportFrom):
            if no.level:
                base = pacote[: len(pacote) - (no.level - 1)] if no.level - 1 <= len(pacote) else []
                modulo = ".".join(base + ([no.module] if no.module else []))
            else:
                modulo = no.module or ""
            if modulo:
                com_os_de_cima(modulo)
            for apelido in no.names:
                if apelido.name != "*":
                    nomes.add(f"{modulo}.{apelido.name}" if modulo else apelido.name)
        elif isinstance(no, ast.Call) and _nome_da_funcao(no) in _IMPORTA_POR_TEXTO and no.args:
            nome = _texto(no.args[0])
            if nome and not nome.startswith("."):
                com_os_de_cima(nome)
    return nomes


def fechamento(caminhos, ler, raizes=(Raiz(ENTRADA),)) -> tuple[list[str], list[str]]:
    """(os arquivos do programa, as falhas da leitura): o fechamento das importações a partir de cada raiz.

    `caminhos` são os arquivos do repositório; `ler(caminho)` devolve o texto ou None. Cada raiz procura os módulos na
    pasta dela (`Raiz.pasta`), e os arquivos que ela alcança procuram na mesma pasta. Arquivo do fechamento que não
    abre ou que não é Python válido vira falha (nunca some calado). Raiz que não está no repositório vira falha.
    """
    caminhos = list(caminhos)
    existentes = set(caminhos)
    indices: dict[str, dict[str, str]] = {}
    vistos: set[tuple[str, str]] = set()
    falhas: list[str] = []
    fila: list[tuple[str, str]] = []
    for r in raizes:
        if r.arquivo not in existentes:
            falhas.append(f"{r.arquivo}:0: o começo do programa não está no repositório")
        elif (r.arquivo, r.pasta) not in vistos:
            vistos.add((r.arquivo, r.pasta))
            fila.append((r.arquivo, r.pasta))
    lidos_com_falha: set[str] = set()
    while fila:
        caminho, pasta = fila.pop()
        por_nome = indices.setdefault(pasta, _indice(caminhos, pasta))
        fonte = ler(caminho)
        if fonte is None:
            if caminho not in lidos_com_falha:
                falhas.append(f"{caminho}:0: não deu para ler o arquivo")
                lidos_com_falha.add(caminho)
            continue
        try:
            raiz = leitura.arvore(fonte)
        except leitura.CodigoIlegivel as erro:
            if caminho not in lidos_com_falha:
                falhas.append(f"{caminho}:0: o código não pôde ser lido ({erro})")
                lidos_com_falha.add(caminho)
            continue
        relativo = caminho[len(pasta) + 1:] if pasta else caminho
        for nome in modulos_pedidos(raiz, relativo):
            achado = por_nome.get(nome)
            if achado and (achado, pasta) not in vistos:
                vistos.add((achado, pasta))
                fila.append((achado, pasta))
    return sorted({c for c, _ in vistos}), falhas


# ---------------------------------------------------------------- as capacidades usadas num arquivo

def _nomes_importados(raiz: ast.Module) -> set[str]:
    """Os nomes que as importações deste arquivo criam (`import a.b` → `a`; `import a as b` → `b`; `from a import c`
    → `c`)."""
    nomes: set[str] = set()
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            nomes |= {a.asname or a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            nomes |= {a.asname or a.name for a in no.names if a.name != "*"}
    return nomes


def _nomes_do_os(raiz: ast.Module) -> set[str]:
    """Os nomes que, neste arquivo, são o módulo `os` (`import os`, `import os as o`)."""
    return {a.asname or "os" for no in ast.walk(raiz) if isinstance(no, ast.Import) for a in no.names if a.name == "os"}


def _raiz_do_atributo(no: ast.Attribute) -> str:
    """O nome no começo de `a.b.c` (`a`); "" se o começo não for um nome."""
    valor = no.value
    while isinstance(valor, ast.Attribute):
        valor = valor.value
    return valor.id if isinstance(valor, ast.Name) else ""


def _usos_na_arvore(raiz: ast.Module) -> list[tuple[int, str, str]]:
    """(linha, capacidade, o que foi achado) de cada uso de uma capacidade de `CAPACIDADES` na árvore."""
    importados, do_os = _nomes_importados(raiz), _nomes_do_os(raiz)
    achados: set[tuple[int, str, str]] = set()
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            for a in no.names:
                cap = _MODULOS.get(a.name.split(".")[0])
                if cap:
                    achados.add((no.lineno, cap, f"import {a.name}"))
                if cap == "ctypes" and _WINDOWS_PELO_CTYPES & set(a.name.split(".")[1:]):
                    achados.add((no.lineno, "Windows pelo ctypes", f"import {a.name}"))
        elif isinstance(no, ast.ImportFrom):
            modulo = no.module or ""
            cap = None if no.level else _MODULOS.get(modulo.split(".")[0])
            if cap:
                achados.add((no.lineno, cap, f"from {modulo} import ..."))
            if cap == "ctypes" and _WINDOWS_PELO_CTYPES & set(modulo.split(".")[1:]):
                achados.add((no.lineno, "Windows pelo ctypes", f"from {modulo} import ..."))
            for a in no.names:
                if cap == "ctypes" and a.name in _CARREGAR_DLL:
                    achados.add((no.lineno, "carregar DLL", f"from {modulo} import {a.name}"))
                if cap == "ctypes" and a.name in _WINDOWS_PELO_CTYPES:
                    achados.add((no.lineno, "Windows pelo ctypes", f"from {modulo} import {a.name}"))
                if not cap and a.name in _MODULOS:
                    achados.add((no.lineno, _MODULOS[a.name], f"from {'.' * no.level}{modulo} import {a.name}"))
                if not no.level and modulo == "os":
                    if a.name == "startfile":
                        achados.add((no.lineno, "os.startfile", "from os import startfile"))
                    elif _rodar_programa_pelo_os(a.name):
                        achados.add((no.lineno, "rodar programa pelo os", f"from os import {a.name}"))
                    elif a.name == "*":
                        achados.add((no.lineno, "os.startfile", "from os import * (traz o startfile e o system)"))
        elif isinstance(no, ast.Call):
            nome = _nome_da_funcao(no)
            primeiro = _texto(no.args[0]) if no.args else None
            if nome in _IMPORTA_POR_TEXTO and primeiro and _MODULOS.get(primeiro.split(".")[0]):
                achados.add((no.lineno, _MODULOS[primeiro.split(".")[0]], f"{nome}({primeiro!r})"))
            segundo = _texto(no.args[1]) if len(no.args) >= 2 else None
            if nome == "getattr" and segundo:
                if segundo == "startfile":
                    achados.add((no.lineno, "os.startfile", "getattr(..., 'startfile')"))
                elif segundo in _MODULOS:
                    achados.add((no.lineno, _MODULOS[segundo], f"getattr(..., {segundo!r})"))
                elif segundo in _CARREGAR_DLL:
                    achados.add((no.lineno, "carregar DLL", f"getattr(..., {segundo!r})"))
                elif segundo in _WINDOWS_PELO_CTYPES:
                    achados.add((no.lineno, "Windows pelo ctypes", f"getattr(..., {segundo!r})"))
        elif isinstance(no, ast.Attribute):
            comeco = _raiz_do_atributo(no)
            if no.attr in _WINDOWS_PELO_CTYPES:
                # Pelo nome, venha de onde vier (`ctypes.windll`, `kernel32.GetLastError`, `wintypes` pego de dentro de
                # outro módulo): nenhum outro objeto do programa tem atributo com esses nomes.
                achados.add((no.lineno, "Windows pelo ctypes", f"usa ...{no.attr}"))
            if no.attr == "startfile":
                achados.add((no.lineno, "os.startfile", "usa .startfile"))
            elif no.attr in _CARREGAR_DLL and comeco in importados:
                achados.add((no.lineno, "carregar DLL", f"usa {comeco}...{no.attr}"))
            elif no.attr in _MODULOS and comeco in importados:
                # O módulo pego de dentro de outro módulo importado (`windows.subprocess.run`). O `.ctypes` de uma
                # variável (`imagem.ctypes.data_as`, o numpy) não é o módulo; o arquivo importa o ctypes e é acusado lá.
                achados.add((no.lineno, _MODULOS[no.attr], f"usa {comeco}...{no.attr}"))
            elif isinstance(no.value, ast.Name) and no.value.id in do_os and _rodar_programa_pelo_os(no.attr):
                achados.add((no.lineno, "rodar programa pelo os", f"usa {no.value.id}.{no.attr}"))
        elif isinstance(no, ast.Name) and isinstance(no.ctx, ast.Load) and no.id in importados:
            if no.id in _CARREGAR_DLL:
                achados.add((no.lineno, "carregar DLL", f"usa {no.id}"))
            elif no.id in _WINDOWS_PELO_CTYPES:
                achados.add((no.lineno, "Windows pelo ctypes", f"usa {no.id}"))
    return sorted(achados)


def capacidades_usadas(fonte: str) -> list[tuple[int, str, str]]:
    """(linha, capacidade, o que foi achado) de cada uso de uma capacidade de `CAPACIDADES` no arquivo.

    Lê só a árvore (`ast`): comentário e docstring nunca contam. Levanta `leitura.CodigoIlegivel` se o texto não for
    Python válido (quem chama trata como falha).
    """
    return _usos_na_arvore(leitura.arvore(fonte))


# ---------------------------------------------------------------- os lugares acusados

FORA_DE_FUNCAO = "(fora de função)"


@dataclass(frozen=True)
class Lugar:
    """Um lugar acusado: o arquivo, a linha, a capacidade, o que foi achado e a função onde mora (com a classe na
    frente, pela peça de leitura: `leitura.funcao_em_volta`; "" se está fora de qualquer função)."""

    arquivo: str
    linha: int
    capacidade: str
    o_que: str
    funcao: str

    @property
    def chave(self) -> str:
        """A chave da catraca, sem a linha: escrever código acima do lugar não a muda."""
        return f"{self.arquivo} | {self.funcao or FORA_DE_FUNCAO} | {self.capacidade} | {self.o_que}"

    @property
    def texto(self) -> str:
        """O lugar como se lê numa falha: "arquivo:linha: capacidade (o que)"."""
        return f"{self.arquivo}:{self.linha}: {self.capacidade} ({self.o_que})"


def lugares_da_trava(caminhos, ler, raizes=(Raiz(ENTRADA),)) -> tuple[list[Lugar], list[str]]:
    """(os lugares acusados, as falhas da leitura) em todo arquivo do fechamento a partir de `raizes`.

    O dono da capacidade (`DONOS`) não é acusado por ela; é acusado pelas outras. Arquivo que não se lê vira falha da
    leitura (essa nunca entra na catraca: sempre falha)."""
    arquivos, falhas = fechamento(caminhos, ler, raizes)
    lugares: list[Lugar] = []
    for caminho in arquivos:
        fonte = ler(caminho)
        if fonte is None:
            continue                                  # já está nas falhas do fechamento
        try:
            raiz = leitura.arvore(fonte)
        except leitura.CodigoIlegivel:
            continue                                  # já está nas falhas do fechamento
        pode = DONOS.get(caminho, frozenset())
        lugares += [Lugar(caminho, linha, cap, o_que, leitura.funcao_em_volta(raiz, linha))
                    for linha, cap, o_que in _usos_na_arvore(raiz) if cap not in pode]
    return sorted(lugares, key=lambda l: (l.arquivo, l.linha, l.capacidade, l.o_que)), falhas


def falhas_da_trava(caminhos, ler, raizes=(Raiz(ENTRADA),)) -> list[str]:
    """As falhas da leitura e os lugares acusados, em texto ("arquivo:linha: capacidade (o que)")."""
    lugares, falhas = lugares_da_trava(caminhos, ler, raizes)
    return falhas + [l.texto for l in lugares]


def _ler_da_pasta(caminho: str) -> str | None:
    """O texto do arquivo nesta cópia, ou None se não deu para ler."""
    try:
        return (RAIZ / caminho).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def lugares_do_repositorio() -> tuple[list[Lugar], list[str]]:
    """Os lugares acusados no repositório inteiro (os arquivos que o git conhece, como estão na pasta), a partir das
    raízes do programa, e as falhas da leitura (das raízes e do fechamento)."""
    caminhos = git.arquivos_do_git(RAIZ)
    raizes, falhas_das_raizes = raizes_do_programa(caminhos, _ler_da_pasta)
    lugares, falhas = lugares_da_trava(caminhos, _ler_da_pasta, raizes)
    return lugares, falhas_das_raizes + falhas


# ---------------------------------------------------------------- a catraca

def conferir_a_catraca(lugares: list[Lugar], congelada, teto: int) -> list[str]:
    """As queixas da catraca (vazia = passou). Um lugar é uma chave (`Lugar.chave`): o mesmo jeito de usar a mesma
    capacidade, na mesma função do mesmo arquivo, é um lugar só, por mais vezes que apareça (doze `wintypes.DWORD` no
    mesmo corpo de arquivo são um lugar). As queixas:
    - a lista congelada passou do teto, ou tem linha repetida;
    - LUGAR NOVO: chave acusada que não está na lista (diz as linhas onde está);
    - lugar da lista que não é mais acusado: pede para tirar a linha e abaixar o teto."""
    queixas: list[str] = []
    congelada = list(congelada)
    if len(congelada) > teto:
        queixas.append(f"a lista congelada tem {len(congelada)} linhas e o TETO é {teto}: a lista só pode diminuir")
    for chave, vezes in sorted(Counter(congelada).items()):
        if vezes > 1:
            queixas.append(f"linha repetida na lista congelada ({vezes} vezes): {chave}")
    achadas, guardadas = {l.chave for l in lugares}, set(congelada)
    for chave in sorted(achadas - guardadas):
        onde = ", ".join(l.texto for l in lugares if l.chave == chave)
        queixas.append(f"LUGAR NOVO (a capacidade vai para o dono, nunca para a lista): {chave}  [{onde}]")
    for chave in sorted(guardadas - achadas):
        queixas.append(f"este lugar não é mais acusado: tire esta linha da lista e abaixe o teto: {chave}")
    return queixas


# A lista de 23/11/2026 (terceira volta), lugar por lugar, pela chave (`Lugar.chave`). Só diminui.
LISTA_CONGELADA = (
    # (a1) O atualizador e os testes à distância (20): a lista de trabalho do atualizador novo.
    "atualizacao.py | (fora de função) | subprocess | import subprocess",
    "atualizacao.py | _dono_do_arquivo | ctypes | import ctypes",
    "atualizacao.py | _dono_do_arquivo | ctypes | from ctypes import ...",
    "atualizacao.py | _dono_do_arquivo | Windows pelo ctypes | from ctypes import wintypes",
    "atualizacao.py | _dono_do_arquivo | Windows pelo ctypes | usa ...windll",
    "atualizacao.py | _dono_do_arquivo | Windows pelo ctypes | usa wintypes",
    "atualizacao.py | marcar_programa_aberto | ctypes | import ctypes",
    "atualizacao.py | marcar_programa_aberto | Windows pelo ctypes | usa ...windll",
    "atualizacao.py | _marca_existe | ctypes | import ctypes",
    "atualizacao.py | _marca_existe | Windows pelo ctypes | usa ...windll",
    "atualizacao.py | _ler_versao_do_visual_c | winreg | import winreg",
    "atualizacao.py | _ler_chave_do_inno | winreg | import winreg",
    "core/_testes_a_distancia_windows.py | (fora de função) | ctypes | import ctypes",
    "core/_testes_a_distancia_windows.py | (fora de função) | ctypes | from ctypes import ...",
    "core/_testes_a_distancia_windows.py | (fora de função) | subprocess | import subprocess",
    "core/_testes_a_distancia_windows.py | (fora de função) | Windows pelo ctypes | from ctypes import wintypes",
    "core/_testes_a_distancia_windows.py | (fora de função) | Windows pelo ctypes | usa wintypes",
    "core/_testes_a_distancia_windows.py | _rodar_elevado | Windows pelo ctypes | usa ...windll",
    "core/_testes_a_distancia_windows.py | _rodar_elevado | Windows pelo ctypes | usa ...get_last_error",
    "core/_testes_a_distancia_windows.py | _rodar_elevado | Windows pelo ctypes | usa wintypes",
    # (a2) O Windows de verdade em outras partes do programa (9). Nada mudado nelas (D-765); vão para core/windows.py
    # depois da entrega (o explorer /select do historico.py vira o mostrar_no_explorer da peça).
    "core/nucleos.py | (fora de função) | ctypes | import ctypes",
    "core/nucleos.py | memoria_livre_mb | Windows pelo ctypes | usa ...windll",
    "core/ocr_comum.py | abrir_processo | ctypes | import ctypes",
    "core/ocr_comum.py | abrir_processo | Windows pelo ctypes | usa ...WinDLL",
    "historico.py | (fora de função) | subprocess | import subprocess",
    "historico.py | abrir_pasta | os.startfile | usa .startfile",
    "historico.py | imprimir | os.startfile | usa .startfile",
    "ui/brasao_girando.py | _programa_vivo | ctypes | import ctypes",
    "ui/brasao_girando.py | _programa_vivo | Windows pelo ctypes | usa ...windll",
    # (b) As nossas DLLs do ScanTailor (12): vão para core/nativo_dll.py.
    "core/caixas_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/cores_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/desentortar_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/dividir_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/endireitar_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/gravura_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/gravura_scantailor.py | DetectorGravuraScanTailor._carregar | carregar DLL | usa ctypes...CDLL",
    "core/luz_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/pontinhos_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/preto_e_branco_scantailor.py | (fora de função) | ctypes | import ctypes",
    "core/st_ferramentas.py | (fora de função) | ctypes | import ctypes",
    "core/st_ferramentas.py | BibliotecaScanTailor._carregar | carregar DLL | usa ctypes...CDLL",
    # (b) Os nossos processos (5): vão para core/processos.py.
    "core/ocr_comum.py | (fora de função) | subprocess | import subprocess",
    "core/ocr_kraken.py | (fora de função) | subprocess | import subprocess",
    "core/ocr_tesseract.py | (fora de função) | subprocess | import subprocess",
    "core/paginas_em_outro_processo.py | (fora de função) | subprocess | import subprocess",
    "ui/tela_de_carregamento.py | (fora de função) | subprocess | import subprocess",
)
TETO = 46       # o tamanho da lista em 23/11/2026 (20 + 9 + 12 + 5); só desce


# ---------------------------------------------------------------- a trava

def test_cada_capacidade_so_no_seu_dono():
    """A trava (D-830, terceira volta): no programa que vai para o Kaique, cada capacidade só no seu dono, com a
    catraca: nenhum lugar novo, nenhum lugar perdoado à toa, e a lista nunca passa do teto. Falha da leitura (raiz,
    `OCULTOS`, arquivo que não abre) nunca é perdoada."""
    lugares, falhas = lugares_do_repositorio()
    assert not falhas, "a trava não conseguiu ler o programa:\n" + "\n".join(falhas)
    assert len(LISTA_CONGELADA) <= TETO
    queixas = conferir_a_catraca(lugares, LISTA_CONGELADA, TETO)
    assert not queixas, f"{len(queixas)} queixas da catraca:\n" + "\n".join(queixas)


def test_pendencia_o_dono_das_dlls_so_carrega_dll_de_core_nativo():
    """PENDÊNCIA (D-830, segunda volta, ponto 3): o teste de execução "todo caminho que o dono das DLLs carrega está
    sob `core/nativo/`". A trava de estrutura só diz QUEM pode chamar `CDLL` (o dono); o caminho vem de uma variável e
    só se confere rodando. A peça (`core/nativo_dll.py`) ainda não existe, e esta prova não a inventa: fica parada
    enquanto ela não existir, e falha no dia em que ela existir sem esta prova escrita."""
    if "core/nativo_dll.py" not in git.arquivos_do_git(RAIZ):
        pytest.skip("pendência: core/nativo_dll.py ainda não existe (D-830); a prova de execução é escrita com ela")
    pytest.fail("core/nativo_dll.py existe: escreva aqui a prova de execução (todo caminho carregado sob core/nativo/)")


def test_pendencia_a_peca_do_windows_so_lanca_programa_da_pasta_do_windows():
    """PENDÊNCIA (D-830, terceira volta, ponto 2): o teste de execução "a peça do Windows (`core/windows.py`) só lança
    programa da pasta do Windows". O `subprocess` tem dois donos, e o import não os separa: a separação é feita quando o
    programa roda.

    Hoje a peça NÃO faz isso (conferido em 23/11/2026, na ponta `d792ebfc`): `_caminho_do_programa` (`core/windows.py`,
    linha 1078) só deixa o caminho como o Windows o completa, para comparar; e a regra do rodar genérico,
    `_por_que_recusa` (linha 1195), faz o contrário: RECUSA o programa da pasta do Windows (linha 1245,
    `if caminho.is_relative_to(pasta_do_windows): return FRASE_TEM_FUNCAO_PROPRIA`) e deixa rodar os de fora (o `vpk`
    e o `gh` do publicar, pelo `rodar_em_grupo`). Esses de fora só têm para onde ir quando a peça dos processos existir.
    Por isso fica parada enquanto `core/processos.py` não existir, e falha no dia em que ela existir sem esta prova."""
    if "core/processos.py" not in git.arquivos_do_git(RAIZ):
        pytest.skip("pendência: core/processos.py ainda não existe (D-830); a regra 'a peça do Windows só lança "
                    "programa da pasta do Windows' é escrita, com a prova de execução, quando ela existir")
    pytest.fail("core/processos.py existe: escreva aqui a prova de execução (core/windows.py só lança programa da "
                "pasta do Windows)")


def test_pendencia_a_peca_dos_processos_recusa_programa_da_pasta_do_windows():
    """PENDÊNCIA (D-830, terceira volta, ponto 2), o espelho da anterior: o teste de execução "a peça dos processos
    (`core/processos.py`) recusa programa da pasta do Windows". A peça ainda não existe, e esta prova não a inventa: fica
    parada enquanto ela não existir, e falha no dia em que ela existir sem esta prova escrita."""
    if "core/processos.py" not in git.arquivos_do_git(RAIZ):
        pytest.skip("pendência: core/processos.py ainda não existe (D-830); a prova de execução é escrita com ela")
    pytest.fail("core/processos.py existe: escreva aqui a prova de execução (recusa programa da pasta do Windows)")


# ---------------------------------------------------------------- as provas de que a trava funciona

def _py(texto: str) -> str:
    """Tira a margem do exemplo."""
    return textwrap.dedent(texto).lstrip("\n")


def _conferir(arquivos: dict[str, str], raizes=(Raiz(ENTRADA),)) -> list[str]:
    """Roda a trava nestes arquivos de exemplo (caminho → texto), sem ler o disco."""
    return falhas_da_trava(list(arquivos), arquivos.get, raizes)


def _lugares(arquivos: dict[str, str], raizes=(Raiz(ENTRADA),)) -> list[Lugar]:
    """Os lugares acusados nestes arquivos de exemplo (sem falha de leitura)."""
    lugares, falhas = lugares_da_trava(list(arquivos), arquivos.get, raizes)
    assert not falhas
    return lugares


def _programa(**mais: str) -> dict[str, str]:
    """Um repositório de exemplo: o `main.py` importa `core.usa`, e os outros arquivos vêm em `mais`
    separados por `_P_` (`core_P_usa` → `core/usa.py`; `pacote_P___init__` → `pacote/__init__.py`)."""
    arquivos = {"main.py": '"""Começo."""\nimport core.usa\n', "core/__init__.py": ""}
    arquivos.update({nome.replace("_P_", "/") + ".py": _py(texto) for nome, texto in mais.items()})
    return arquivos


def test_fechamento_dentro_acusa_e_fora_nao_acusa():
    """O mesmo `import ctypes`: num arquivo que o `main.py` importa é acusado; num arquivo que ninguém do programa
    importa (fora do fechamento), não."""
    arquivos = _programa(core_P_usa='"""Dentro."""\nimport ctypes\n', solto='"""Fora."""\nimport ctypes\n')
    assert _conferir(arquivos) == ["core/usa.py:2: ctypes (import ctypes)"]
    arquivos_ok, _ = fechamento(list(arquivos), arquivos.get)
    assert "solto.py" not in arquivos_ok and "core/usa.py" in arquivos_ok


def test_fechamento_segue_funcao_if_try_relativo_from_e_texto():
    """O fechamento segue a importação dentro de função, de `if`, de `try`, a relativa, o `from pacote import modulo`,
    o `importlib.import_module("x")` escrito por inteiro e os pacotes de cima (`a/__init__.py`). Cada arquivo do fim da
    corrente tem um `import subprocess`, e todos são acusados."""
    sub = '"""E."""\nimport subprocess\n'
    arquivos = _programa(
        core_P_usa=('"""A corrente."""\nimport importlib\n\n\ndef f():\n    """Em função."""\n    import funcao\n\n\n'
                   'if True:\n    import condicional\n\ntry:\n    import tentativa\nexcept ImportError:\n    pass\n'
                   'from . import relativo\nfrom pacote import modulo\nimportlib.import_module("por_texto")\n'),
        funcao=sub, condicional=sub, tentativa=sub, core_P_relativo=sub, pacote_P_modulo=sub, por_texto=sub,
        pacote_P___init__=sub)
    acusados = {f.split(":")[0] for f in _conferir(arquivos)}
    assert acusados == {"funcao.py", "condicional.py", "tentativa.py", "core/relativo.py", "pacote/modulo.py",
                        "por_texto.py", "pacote/__init__.py"}


def test_fechamento_aguenta_ciclo_e_ignora_o_que_nao_e_do_repositorio():
    """Dois arquivos que se importam não travam; `import numpy` e `import json` não são do repositório e não entram."""
    arquivos = _programa(core_P_usa='"""A."""\nimport numpy\nimport json\nimport core.b\n',
                         core_P_b='"""B."""\nimport core.usa\n')
    assert fechamento(list(arquivos), arquivos.get)[0] == ["core/__init__.py", "core/b.py", "core/usa.py", "main.py"]


def test_fechamento_que_nao_le_e_falha_nunca_passou():
    """Arquivo do fechamento que não abre, código ilegível, e falta do `main.py` viram falha."""
    arquivos = _programa(core_P_usa='"""A."""\nimport core.ruim\nimport core.some\n')
    arquivos["core/ruim.py"] = "def (:\n"
    arquivos["core/some.py"] = None  # type: ignore[assignment]
    falhas = _conferir(arquivos)
    assert any(f.startswith("core/ruim.py:0: o código não pôde ser lido") for f in falhas)
    assert "core/some.py:0: não deu para ler o arquivo" in falhas
    assert _conferir({"core/x.py": "import ctypes\n"}) == ["main.py:0: o começo do programa não está no repositório"]


def test_cada_dono_usa_a_sua_capacidade_e_nao_a_dos_outros():
    """Os donos (mapa final, terceira volta): `core/windows.py` pode ctypes, o Windows pelo ctypes, winreg, startfile e
    subprocess, mas não CDLL; `core/nativo_dll.py` pode ctypes e CDLL, mas não subprocess nem o Windows pelo ctypes;
    `core/processos.py` pode subprocess, mas não ctypes."""
    windows = ('"""W."""\nimport ctypes\nimport winreg\nimport os\nimport subprocess\nx = ctypes.CDLL("a")\n'
               'os.startfile("a")\nk = ctypes.windll.kernel32\nsubprocess.run(["schtasks"])\n')
    nativo = '"""N."""\nimport ctypes\nd = ctypes.CDLL("core/nativo/a.dll")\nimport subprocess\n'
    processos = '"""P."""\nimport subprocess\nimport ctypes\n'
    arquivos = {"main.py": '"""M."""\nimport core.windows\nimport core.nativo_dll\nimport core.processos\n',
                "core/windows.py": windows, "core/nativo_dll.py": nativo, "core/processos.py": processos}
    assert _conferir(arquivos) == [
        "core/nativo_dll.py:4: subprocess (import subprocess)",
        "core/processos.py:3: ctypes (import ctypes)",
        "core/windows.py:6: carregar DLL (usa ctypes...CDLL)",
    ]


@pytest.mark.parametrize("nome", sorted(_WINDOWS_PELO_CTYPES))
def test_o_dono_das_dlls_nao_pode_o_windows_pelo_ctypes(nome):
    """Ponto 4 da terceira volta: dentro de `core/nativo_dll.py` (que pode o ctypes e o CDLL) cada nome do Windows é
    acusado, como atributo (`ctypes.<nome>`, `kernel32.<nome>` de uma variável) e como nome (`from ctypes import
    <nome>` e o uso dele). O mesmo arquivo em `core/windows.py` não é acusado; o `CDLL` e os tipos comuns no dono das
    DLLs também não."""
    texto = (f'"""N."""\nimport ctypes\nfrom ctypes import {nome}\nd = ctypes.CDLL("core/nativo/a.dll")\n'
             f'x = ctypes.c_void_p\na = ctypes.{nome}\nb = {nome}\nc = d.{nome}\n')
    for dono, esperado in (("core/nativo_dll.py", [
            f"core/nativo_dll.py:3: Windows pelo ctypes (from ctypes import {nome})",
            f"core/nativo_dll.py:6: Windows pelo ctypes (usa ...{nome})",
            f"core/nativo_dll.py:7: Windows pelo ctypes (usa {nome})",
            f"core/nativo_dll.py:8: Windows pelo ctypes (usa ...{nome})"]), ("core/windows.py", [])):
        arquivos = {"main.py": f'"""M."""\nimport {dono[:-3].replace("/", ".")}\n', dono: texto}
        assert [f for f in _conferir(arquivos) if "carregar DLL" not in f] == esperado


def test_o_dono_das_dlls_nao_pode_importar_o_wintypes_nem_pegar_por_getattr():
    """O `import ctypes.wintypes`, o `from ctypes.wintypes import DWORD` e o `getattr(ctypes, "windll")` no dono das
    DLLs são acusados como o Windows pelo ctypes (o primeiro também é o ctypes, que ele pode)."""
    texto = ('"""N."""\nimport ctypes.wintypes\nfrom ctypes.wintypes import DWORD\n'
             'k = getattr(ctypes, "windll")\n')
    arquivos = {"main.py": '"""M."""\nimport core.nativo_dll\n', "core/nativo_dll.py": texto}
    assert _conferir(arquivos) == [
        "core/nativo_dll.py:2: Windows pelo ctypes (import ctypes.wintypes)",
        "core/nativo_dll.py:3: Windows pelo ctypes (from ctypes.wintypes import ...)",
        "core/nativo_dll.py:4: Windows pelo ctypes (getattr(..., 'windll'))",
    ]


def test_ctypes_so_para_os_tipos_tambem_e_acusado_fora_do_dono():
    """O ctypes é o módulo inteiro: só para os tipos (`c_void_p`), fora do dono, é acusado. O `.ctypes` de uma imagem do
    numpy não é o módulo e não é acusado à parte (o import já é)."""
    arquivos = _programa(core_P_usa=('"""Chama a DLL com a imagem."""\nimport ctypes\n\n\ndef f(imagem, funcao):\n'
                                    '    """F."""\n    return funcao(imagem.ctypes.data_as(ctypes.c_void_p))\n'))
    assert _conferir(arquivos) == ["core/usa.py:2: ctypes (import ctypes)"]


ERRADO = _py('''
    """Cada jeito de usar uma capacidade."""
    import ctypes.wintypes
    import subprocess as sp
    from ctypes import CDLL
    from winreg import OpenKey
    from os import startfile
    from core.windows import subprocess
    import importlib
    import os
    from core import windows


    def f(pasta):
        """Usa cada jeito."""
        os.startfile(pasta)
        m = __import__("winreg")
        n = importlib.import_module("ctypes.util")
        g = getattr(os, "startfile")
        h = windows.ctypes.windll
        os.system("dir")
        o = os.popen("dir")
        os.spawnv(0, "a", [])
        os.execv("a", [])
        return windows.subprocess.run(["x"])
''')


def test_acusa_cada_jeito_de_importar_e_de_usar():
    """Cada forma de importar ou usar as capacidades, com a capacidade certa (a estrutura, não a palavra)."""
    arquivos = _programa(core_P_usa=ERRADO, core_P_windows='"""W."""\n')
    achados = [(int(f.split(":")[1]), f.split(": ", 1)[1].split(" (")[0]) for f in _conferir(arquivos)]
    assert achados == [(2, "Windows pelo ctypes"), (2, "ctypes"), (3, "subprocess"), (4, "carregar DLL"),
                       (4, "ctypes"), (5, "winreg"), (6, "os.startfile"), (7, "subprocess"), (15, "os.startfile"),
                       (16, "winreg"), (17, "ctypes"), (18, "os.startfile"), (19, "Windows pelo ctypes"),
                       (19, "ctypes"), (20, "rodar programa pelo os"), (21, "rodar programa pelo os"),
                       (22, "rodar programa pelo os"), (23, "rodar programa pelo os"), (24, "subprocess")]


def test_rodar_programa_pelo_os_nao_tem_dono():
    """`os.system` é proibido até nos três donos (o desenho não dá essa capacidade a nenhum)."""
    texto = '"""D."""\nimport os\nos.system("dir")\n'
    arquivos = {"main.py": '"""M."""\nimport core.windows\nimport core.nativo_dll\nimport core.processos\n',
                "core/windows.py": texto, "core/nativo_dll.py": texto, "core/processos.py": texto}
    assert [f.split(":")[0] for f in _conferir(arquivos)] == ["core/nativo_dll.py", "core/processos.py",
                                                               "core/windows.py"]


CERTO = _py('''
    """Fala de ctypes, subprocess, winreg, os.startfile, windll e os.system só no comentário e na docstring.

    import ctypes  (isto é docstring, não código)
    """
    # import subprocess  (comentário)
    import os
    import json
    import platform

    TEXTO = "import ctypes"  # um texto com a palavra não é importação


    def f(caminho, motor):
        """os.startfile(caminho) seria proibido; aqui só se fala dele."""
        nome_do_subprocess = "subprocess"
        sistema = platform.system()              # o system de outro módulo não é o do os
        motor.exec("x")                          # exec de outra coisa não é o do os
        return os.path.join(caminho, json.dumps(nome_do_subprocess), TEXTO, sistema, "windll")
''')


def test_nao_acusa_comentario_docstring_texto_nem_nome_parecido():
    """Comentário, docstring, texto com a palavra, `platform.system()` e `x.exec()` não são capacidade."""
    assert _conferir(_programa(core_P_usa=CERTO)) == []


@pytest.mark.parametrize("modulo,capacidade", sorted(_MODULOS.items()))
def test_cada_modulo_proibido_e_acusado(modulo, capacidade):
    """Cada módulo da lista, importado do jeito mais simples fora do dono, é acusado com a sua capacidade."""
    arquivos = _programa(core_P_usa=f'"""E."""\nimport {modulo}\n')
    assert _conferir(arquivos) == [f"core/usa.py:2: {capacidade} (import {modulo})"]


def test_o_mapa_dos_donos_so_usa_capacidades_que_existem():
    """O mapa final (terceira volta): todo dono só tem capacidades de `CAPACIDADES`; o ctypes tem dois donos (o Windows
    e as nossas DLLs), o subprocess dois (o Windows e os nossos processos); o Windows pelo ctypes, o winreg e o
    startfile, só o Windows; carregar DLL, só as DLLs; rodar programa pelo os, nenhum."""
    assert all(caps <= set(CAPACIDADES) for caps in DONOS.values())
    donos_de = {cap: sorted(a for a, caps in DONOS.items() if cap in caps) for cap in CAPACIDADES}
    assert donos_de == {"ctypes": ["core/nativo_dll.py", "core/windows.py"], "carregar DLL": ["core/nativo_dll.py"],
                        "Windows pelo ctypes": ["core/windows.py"],
                        "subprocess": ["core/processos.py", "core/windows.py"], "winreg": ["core/windows.py"],
                        "os.startfile": ["core/windows.py"], "rodar programa pelo os": []}


# ---------------------------------------------------------------- as provas da catraca

def test_catraca_lugar_novo_falha_na_hora():
    """Lugar acusado que não está na lista congelada falha, e diz a linha. Um lugar novo ao lado de um da lista (outra
    função do mesmo arquivo) também falha, e só ele."""
    lugares = _lugares(_programa(core_P_usa='"""A."""\nimport ctypes\n'))
    queixas = conferir_a_catraca(lugares, [], teto=0)
    assert queixas == ["LUGAR NOVO (a capacidade vai para o dono, nunca para a lista): "
                       "core/usa.py | (fora de função) | ctypes | import ctypes  [core/usa.py:2: ctypes (import ctypes)]"]
    ao_lado = _lugares(_programa(core_P_usa='"""A."""\nimport ctypes\n\n\ndef f():\n    """F."""\n    import winreg\n'))
    assert conferir_a_catraca(ao_lado, [lugares[0].chave], teto=1) == [
        "LUGAR NOVO (a capacidade vai para o dono, nunca para a lista): "
        "core/usa.py | f | winreg | import winreg  [core/usa.py:7: winreg (import winreg)]"]


def test_catraca_o_mesmo_jeito_na_mesma_funcao_e_um_lugar_e_linha_repetida_na_lista_falha():
    """O mesmo jeito de usar a mesma capacidade na mesma função é um lugar só (a chave não tem a linha): repetir não é
    lugar novo. E a lista congelada não pode ter a mesma linha duas vezes (seria teto gasto à toa)."""
    um = _lugares(_programa(core_P_usa='"""A."""\nimport ctypes\n'))
    dois = _lugares(_programa(core_P_usa='"""A."""\nimport ctypes\nimport ctypes\n'))
    assert len(dois) == 2 and {l.chave for l in dois} == {um[0].chave}
    assert conferir_a_catraca(dois, [um[0].chave], teto=1) == []
    assert conferir_a_catraca(um, [um[0].chave, um[0].chave], teto=2) == [
        f"linha repetida na lista congelada (2 vezes): {um[0].chave}"]


def test_catraca_lugar_consertado_pede_para_tirar_da_lista():
    """Lugar da lista que deixou de ser acusado (consertado) falha, pedindo para tirar a linha e abaixar o teto."""
    chave = "core/usa.py | (fora de função) | ctypes | import ctypes"
    lugares = _lugares(_programa(core_P_usa='"""Consertado."""\nimport json\n'))
    assert conferir_a_catraca(lugares, [chave], teto=1) == [
        f"este lugar não é mais acusado: tire esta linha da lista e abaixe o teto: {chave}"]


def test_catraca_a_lista_nunca_passa_do_teto():
    """Uma linha a mais na lista sem subir o teto falha, mesmo que o lugar exista."""
    lugares = _lugares(_programa(core_P_usa='"""A."""\nimport ctypes\nimport subprocess\n'))
    chaves = [l.chave for l in lugares]
    assert conferir_a_catraca(lugares, chaves, teto=2) == []
    assert conferir_a_catraca(lugares, chaves, teto=1) == [
        "a lista congelada tem 2 linhas e o TETO é 1: a lista só pode diminuir"]


def test_catraca_a_chave_nao_muda_quando_se_escreve_codigo_acima():
    """A chave é "arquivo | função | capacidade | o que", sem a linha: o mesmo lugar com dez linhas de código novo
    acima dá a mesma chave (e a catraca passa); o mesmo import levado para outra função dá outra chave (e a catraca
    acusa um novo e um que sumiu)."""
    antes = '"""A."""\n\n\ndef ler():\n    """L."""\n    import winreg\n    return winreg\n'
    acima = '"""A."""\nX = 1\n' + "".join(f"Y{n} = {n}\n" for n in range(10)) + antes.split('"""A."""\n', 1)[1]
    outra = antes.replace("def ler", "def gravar")
    l_antes = _lugares(_programa(core_P_usa=antes))
    l_acima = _lugares(_programa(core_P_usa=acima))
    assert [l.chave for l in l_antes] == [l.chave for l in l_acima] == ["core/usa.py | ler | winreg | import winreg"]
    assert l_antes[0].linha != l_acima[0].linha
    assert conferir_a_catraca(l_acima, [l.chave for l in l_antes], teto=1) == []
    queixas = conferir_a_catraca(_lugares(_programa(core_P_usa=outra)), [l.chave for l in l_antes], teto=1)
    assert [q.split(":")[0] for q in queixas] == ["LUGAR NOVO (a capacidade vai para o dono, nunca para a lista)",
                                                  "este lugar não é mais acusado"]


def test_a_lista_congelada_nao_tem_linha_vazia_nem_formato_errado():
    """Cada linha da lista tem as quatro partes da chave, e o TETO não está acima do tamanho da lista no dia em que foi
    congelada (23/11/2026)."""
    assert all(len(chave.split(" | ")) == 4 and all(p.strip() for p in chave.split(" | ")) for chave in LISTA_CONGELADA)
    assert len(LISTA_CONGELADA) <= TETO


# ---------------------------------------------------------------- as provas das raízes

EMPACOTAR_DE_EXEMPLO = _py('''
    """E."""
    OCULTOS = ["doxapy", "core.escondido", "onnxtr.models"]


    def montar():
        """M."""
        comando = []
        for modulo in OCULTOS:
            comando += ["--hidden-import", modulo]
        return comando
''')


def test_raiz_do_hidden_import_entra_no_fechamento():
    """Um módulo nosso que só a `OCULTOS` do `empacotar.py` põe no `.exe` (ninguém o importa) entra e é acusado; os de
    fora (`doxapy`, `onnxtr`) ficam de fora sem falha."""
    arquivos = _programa(core_P_usa='"""A."""\n', core_P_escondido='"""E."""\nimport subprocess\n')
    arquivos["empacotar.py"] = EMPACOTAR_DE_EXEMPLO
    arquivos["motor_kraken/servidor_kraken.py"] = '"""S."""\nimport json\n'
    raizes, falhas = raizes_do_programa(list(arquivos), arquivos.get)
    assert not falhas and Raiz("core/escondido.py") in raizes
    assert _conferir(arquivos, raizes) == ["core/escondido.py:2: subprocess (import subprocess)"]
    assert _conferir(arquivos) == []                       # sem a raiz, escaparia


def test_raiz_do_motor_do_kraken_procura_na_pasta_dele():
    """O motor do Kraken é raiz: o `import ctypes` dele é acusado, e o `import ajudante` dele é o
    `motor_kraken/ajudante.py` (a pasta dele, como o `python -I` procura), não o `ajudante.py` da raiz."""
    arquivos = _programa(core_P_usa='"""A."""\n')
    arquivos.update({"motor_kraken/servidor_kraken.py": '"""S."""\nimport ctypes\nimport ajudante\n',
                     "motor_kraken/ajudante.py": '"""Do motor."""\nimport winreg\n',
                     "ajudante.py": '"""Da raiz."""\nimport subprocess\n'})
    assert _conferir(arquivos, RAIZES_FIXAS) == [
        "motor_kraken/ajudante.py:2: winreg (import winreg)",
        "motor_kraken/servidor_kraken.py:2: ctypes (import ctypes)",
    ]


@pytest.mark.parametrize("trecho,esperado", [
    ('OCULTOS = ["core.a"]\nOCULTOS.append("core.b")\n', "OCULTOS.append (a lista pode ganhar item rodando)"),
    ('OCULTOS = ["core.a"]\nOCULTOS += ["core.b"]\n', "OCULTOS ganha item por +="),
    ('OCULTOS = lista_de_fora()\n', "OCULTOS não é uma lista de textos fixos (não dá para ler sem rodar)"),
    ('X = 1\n', "esperava uma atribuição só de OCULTOS no corpo do arquivo, achei 0"),
    ('OCULTOS = ["core.a"]\nc = ["--hidden-import", "core.b"]\n', "--hidden-import fora do laço de OCULTOS"),
    ('OCULTOS = ["core.a"]\nc = ["--collect-submodules", "core"]\n',
     "--collect-submodules põe módulo no .exe e esta trava não o lê"),
    ('OCULTOS = ["core.nao_existe"]\n', "OCULTOS pede core.nao_existe, que parece nosso e não tem arquivo"),
])
def test_a_lista_dos_ocultos_montada_de_outro_jeito_e_falha(trecho, esperado):
    """A `OCULTOS` só é lida do jeito de hoje (lista de textos fixos, mudada em lugar nenhum, `--hidden-import` só no
    laço dela). Qualquer outro jeito é falha que diz a linha, nunca uma lista adivinhada."""
    arquivos = _programa(core_P_usa='"""A."""\n', core_P_a='"""A."""\n')
    arquivos["empacotar.py"] = '"""E."""\n' + trecho
    _, falhas = raizes_do_programa(list(arquivos), arquivos.get)
    assert any(f.endswith(esperado) for f in falhas), falhas


def test_cada_raiz_de_verdade_entra_no_fechamento():
    """No repositório de verdade: as raízes são o `main.py`, o motor do Kraken e os módulos nossos da `OCULTOS` do
    `empacotar.py` (lida sem falha, e com pelo menos os módulos de hoje), e cada uma está no fechamento."""
    caminhos = git.arquivos_do_git(RAIZ)
    raizes, falhas = raizes_do_programa(caminhos, _ler_da_pasta)
    assert not falhas, falhas
    arquivos, falhas = fechamento(caminhos, _ler_da_pasta, raizes)
    assert not falhas, falhas
    assert {r.arquivo for r in raizes} >= {"main.py", "motor_kraken/servidor_kraken.py", "core/gravura_scantailor.py",
                                          "core/st_ferramentas.py", "core/ocr_comum.py", "core/ocr_kraken.py"}
    assert all(r.arquivo in arquivos for r in raizes)
