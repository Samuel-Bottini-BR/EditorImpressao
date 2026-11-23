"""A trava dos donos: cada capacidade perigosa tem um dono, um arquivo só (D-830, 23/11/2026; segunda volta).

De onde veio. O Samuel decidiu refazer o atualizador ("refazer", 23/11/2026, 18:50) e colou no chat da gerente a
mensagem do Fable: "ela pode mandar escrever a primeira trava (o teste que diz 'só core/windows.py fala com o
Windows'). Esse teste vai falhar hoje de propósito — a lista do que falha é a lista de trabalho do atualizador novo".
Na segunda volta (resposta do Fable aos 7 pontos da primeira, colada pelo Samuel), o desenho mudou: "a trava não
pergunta 'este import é permitido?', pergunta 'quem é o dono desta capacidade?'".

O desenho (o mapa `DONOS`, escrito uma vez só, aqui):
- falar com o Windows (licença, tarefas, registro, mutex, memória, janela, SetDllDirectoryW): `core/windows.py`, que pode
  `ctypes` (tudo), `winreg` e `os.startfile`;
- carregar e chamar as nossas DLLs do ScanTailor: `core/nativo_dll.py` (ainda não existe), que pode `ctypes`, e é o
  único que pode chamar `CDLL`;
- abrir e falar com os nossos processos (OCR, Kraken, servidor de páginas, brasão): `core/processos.py` (ainda não
  existe), que pode `subprocess`.
Fora do dono, cada capacidade é proibida sem exceção. As capacidades (`CAPACIDADES`): `ctypes` (o módulo inteiro,
inclusive só para os tipos), carregar DLL (`CDLL`, `cdll`, `PyDLL`, `pydll`), `subprocess`, `winreg`, `os.startfile` e
rodar programa pelo `os` (`os.system`, `os.popen`, `os.spawn*`, `os.exec*`). Esta última o desenho põe na lista do
proibido, mas não a dá a dono nenhum: aqui ela fica sem dono (proibida em todo lugar). Isso é um ponto que o desenho não
fecha; está no ONDE-PAREI, para decidir.

O que é "o programa" nesta trava: o fechamento das importações a partir do `main.py`, o que o `.exe` carrega. Não é
uma lista: é tirado lendo o código (`fechamento`). Parte do `main.py`, lê cada `import` e `from ... import` do
arquivo, resolve para os arquivos do repositório e repete em cada arquivo achado. O que não é do repositório (a
biblioteca do Python, o PySide6, o numpy) não entra. Conta **toda** importação escrita no arquivo: a de cima, a de
dentro de função, a de dentro de `if` e a de dentro de `try`. É o que o PyInstaller põe no `.exe`: ele lista os quatro
tipos ("top-level", "conditional: imported within an if-statement", "delayed: imported within a function",
"optional: imported within a try-except-statement"; PyInstaller 6.21.0, `PyInstaller/building/build_main.py`,
`WARNFILE_HEADER`). A importação pelo nome escrito num texto (`__import__("x")`, `importlib.import_module("x")`) também
entra quando o nome está escrito por inteiro. O PyInstaller não a segue ("Analysis can detect nothing",
https://pyinstaller.org/en/stable/when-things-go-wrong.html), mas o programa a carrega quando roda. O porteiro continua
com a definição dele (`porteiro.e_programa`); esta trava não a usa.

Por que é um teste à parte, e não uma conferência dentro do porteiro (escolha da primeira volta, no
`relatorios/atualizador-novo/ONDE-PAREI.md`): a lista de exceções do porteiro está "valendo" e só ganha item com o
"sim" do Samuel. Uma conferência nova no porteiro, neste ramo, faria o teste antigo
`test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` falhar (D-605), e o juiz do GitHub nem a veria. Quando for
juntada, esta trava deve substituir a parte da K01 que procura essas mesmas coisas por palavras.

A trava está marcada `xfail(strict=True)` (pedido da gerente, segunda volta): enquanto houver lugar na lista, a rodada
não fica vermelha por ela. No dia em que a lista zerar, o `strict` faz o teste falhar, avisando para tirar a marca. As
provas deste arquivo (os exemplos feitos de propósito) não têm marca: elas passam e provam que a trava acusa o errado e
não acusa o certo.

O que ela NÃO pega (escrito para ninguém achar que pega): `multiprocessing` e `asyncio.create_subprocess_*` (outros
jeitos de abrir processo, fora do desenho); `sys.modules["ctypes"]`; o nome montado em pedaços
(`__import__("ct" + "ypes")`); os módulos `nt` e `posix` (onde o `os` busca o `system`); um módulo nosso que guarda o
`subprocess` com outro nome e o entrega por uma função; a importação feita com o nome numa variável; e o código que o
`.exe` leva sem o `main.py` importar (os `--hidden-import` do `empacotar.py`; ver ONDE-PAREI).

Seguro mexer: o texto das frases. Arriscado: tirar uma capacidade ou um nome de `CAPACIDADES`, dar uma capacidade a mais
um dono em `DONOS` (cada dono novo é uma porta), ou deixar de seguir algum tipo de importação em `fechamento`. Qualquer
um desses afrouxa a trava calado. Proibido, pela própria decisão: acrescentar lista de exceções.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes import leitura_do_codigo as leitura

RAIZ = Path(__file__).resolve().parent.parent

# Onde o programa começa (o PyInstaller monta o .exe a partir dele: `empacotar.py`, `comando.append(RAIZ / "main.py")`).
ENTRADA = "main.py"

# As capacidades: nome → o que é. Fontes: https://docs.python.org/3/library/ctypes.html,
# https://docs.python.org/3/library/subprocess.html, https://docs.python.org/3/library/winreg.html,
# https://docs.python.org/3/library/os.html#os.startfile e #process-management.
CAPACIDADES = {
    "ctypes": "o módulo ctypes (chamar funções em DLL, inclusive só os tipos)",
    "carregar DLL": "carregar uma DLL pelo ctypes (CDLL, cdll, PyDLL, pydll)",
    "subprocess": "o módulo subprocess (abrir outro programa)",
    "winreg": "o registro do Windows (winreg)",
    "os.startfile": "abrir arquivo ou programa pelo Windows (os.startfile)",
    "rodar programa pelo os": "rodar programa pelo os (os.system, os.popen, os.spawn*, os.exec*)",
}

# O mapa dos donos: arquivo → as capacidades que só ele pode usar. Lugar único. Capacidade que não aparece aqui não
# tem dono: é proibida em todo arquivo do programa ("rodar programa pelo os").
DONOS: dict[str, frozenset[str]] = {
    "core/windows.py": frozenset({"ctypes", "winreg", "os.startfile"}),       # falar com o Windows
    "core/nativo_dll.py": frozenset({"ctypes", "carregar DLL"}),             # as nossas DLLs (ainda não existe)
    "core/processos.py": frozenset({"subprocess"}),                          # os nossos processos (ainda não existe)
}

# Os nomes dos módulos de cada capacidade de módulo (o `_winreg` é o nome antigo do `winreg`).
_MODULOS = {"ctypes": "ctypes", "subprocess": "subprocess", "winreg": "winreg", "_winreg": "winreg"}
_CARREGAR_DLL = frozenset({"CDLL", "cdll", "PyDLL", "pydll"})
_IMPORTA_POR_TEXTO = frozenset({"__import__", "import_module"})


def _rodar_programa_pelo_os(nome: str) -> bool:
    """O nome é uma função do `os` que roda outro programa (`system`, `popen`, `spawnl`..., `execv`...)."""
    return nome in ("system", "popen") or nome.startswith(("spawn", "exec"))


# ---------------------------------------------------------------- o fechamento das importações

def _nome_do_modulo(caminho: str) -> str:
    """O nome com que o Python importa o arquivo (`core/filtros.py` → `core.filtros`; `core/__init__.py` → `core`)."""
    partes = caminho.rsplit(".", 1)[0].split("/")
    if partes[-1] == "__init__":
        partes = partes[:-1]
    return ".".join(partes)


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
    (pode ser um módulo `a.x`). O relativo vira absoluto. Os que não são do repositório são filtrados por quem chama."""
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


def fechamento(caminhos, ler, entrada: str = ENTRADA) -> tuple[list[str], list[str]]:
    """(os arquivos do programa, as falhas da leitura): o fechamento das importações a partir de `entrada`.

    `caminhos` são os arquivos do repositório; `ler(caminho)` devolve o texto ou None. Arquivo do fechamento que não
    abre ou que não é Python válido vira falha (nunca some calado). Sem a entrada, a falha diz isso.
    """
    por_nome: dict[str, str] = {}
    for c in caminhos:
        if c.endswith((".py", ".pyw")):
            por_nome.setdefault(_nome_do_modulo(c), c)
    if entrada not in set(caminhos):
        return [], [f"{entrada}:0: o começo do programa não está no repositório"]
    vistos, falhas, fila = {entrada}, [], [entrada]
    while fila:
        caminho = fila.pop()
        fonte = ler(caminho)
        if fonte is None:
            falhas.append(f"{caminho}:0: não deu para ler o arquivo")
            continue
        try:
            raiz = leitura.arvore(fonte)
        except leitura.CodigoIlegivel as erro:
            falhas.append(f"{caminho}:0: o código não pôde ser lido ({erro})")
            continue
        for nome in modulos_pedidos(raiz, caminho):
            achado = por_nome.get(nome)
            if achado and achado not in vistos:
                vistos.add(achado)
                fila.append(achado)
    return sorted(vistos), falhas


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


def capacidades_usadas(fonte: str) -> list[tuple[int, str, str]]:
    """(linha, capacidade, o que foi achado) de cada uso de uma capacidade de `CAPACIDADES` no arquivo.

    Lê só a árvore (`ast`): comentário e docstring nunca contam. Levanta `leitura.CodigoIlegivel` se o texto não for
    Python válido (quem chama trata como falha).
    """
    raiz = leitura.arvore(fonte)
    importados, do_os = _nomes_importados(raiz), _nomes_do_os(raiz)
    achados: set[tuple[int, str, str]] = set()
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            for a in no.names:
                cap = _MODULOS.get(a.name.split(".")[0])
                if cap:
                    achados.add((no.lineno, cap, f"import {a.name}"))
        elif isinstance(no, ast.ImportFrom):
            modulo = no.module or ""
            cap = None if no.level else _MODULOS.get(modulo.split(".")[0])
            if cap:
                achados.add((no.lineno, cap, f"from {modulo} import ..."))
            for a in no.names:
                if cap == "ctypes" and a.name in _CARREGAR_DLL:
                    achados.add((no.lineno, "carregar DLL", f"from {modulo} import {a.name}"))
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
        elif isinstance(no, ast.Attribute):
            comeco = _raiz_do_atributo(no)
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
        elif isinstance(no, ast.Name) and isinstance(no.ctx, ast.Load) and no.id in _CARREGAR_DLL \
                and no.id in importados:
            achados.add((no.lineno, "carregar DLL", f"usa {no.id}"))
    return sorted(achados)


def falhas_da_trava(caminhos, ler, entrada: str = ENTRADA) -> list[str]:
    """As falhas da trava, "arquivo:linha: capacidade (o que)", em todo arquivo do fechamento a partir de `entrada`.

    O dono da capacidade (`DONOS`) não é acusado por ela; é acusado pelas outras. Arquivo que não se lê vira falha.
    """
    arquivos, falhas = fechamento(caminhos, ler, entrada)
    for caminho in arquivos:
        fonte = ler(caminho)
        if fonte is None:
            continue                                  # já está nas falhas do fechamento
        try:
            usos = capacidades_usadas(fonte)
        except leitura.CodigoIlegivel:
            continue                                  # já está nas falhas do fechamento
        pode = DONOS.get(caminho, frozenset())
        falhas += [f"{caminho}:{linha}: {cap} ({o_que})" for linha, cap, o_que in usos if cap not in pode]
    return falhas


def _ler_da_pasta(caminho: str) -> str | None:
    """O texto do arquivo nesta cópia, ou None se não deu para ler."""
    try:
        return (RAIZ / caminho).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def falhas_do_repositorio() -> list[str]:
    """As falhas da trava no repositório inteiro (os arquivos que o git conhece, como estão na pasta)."""
    return falhas_da_trava(git.arquivos_do_git(RAIZ), _ler_da_pasta)


# ---------------------------------------------------------------- a trava

@pytest.mark.xfail(strict=True, reason="D-830: lista de trabalho do atualizador novo")
def test_cada_capacidade_so_no_seu_dono():
    """A trava (D-830, segunda volta): no programa que o `.exe` carrega, cada capacidade só no seu dono. Binária.

    Falha hoje de propósito, e está marcada `xfail(strict=True)`: a lista que ela mostra é a lista de trabalho do
    atualizador novo. Quando a lista zerar, o `strict` acusa: é hora de tirar a marca.
    """
    falhas = falhas_do_repositorio()
    assert not falhas, f"{len(falhas)} lugares usam uma capacidade fora do dono:\n" + "\n".join(falhas)


def test_pendencia_o_dono_das_dlls_so_carrega_dll_de_core_nativo():
    """PENDÊNCIA (D-830, segunda volta, ponto 3): o teste de execução "todo caminho que o dono das DLLs carrega está
    sob `core/nativo/`". A trava de estrutura só diz QUEM pode chamar `CDLL` (o dono); o caminho vem de uma variável e
    só se confere rodando. A peça (`core/nativo_dll.py`) ainda não existe, e esta prova não a inventa: fica parada
    enquanto ela não existir, e falha no dia em que ela existir sem esta prova escrita."""
    if "core/nativo_dll.py" not in git.arquivos_do_git(RAIZ):
        pytest.skip("pendência: core/nativo_dll.py ainda não existe (D-830); a prova de execução é escrita com ela")
    pytest.fail("core/nativo_dll.py existe: escreva aqui a prova de execução (todo caminho carregado sob core/nativo/)")


# ---------------------------------------------------------------- as provas de que a trava funciona

def _py(texto: str) -> str:
    """Tira a margem do exemplo."""
    return textwrap.dedent(texto).lstrip("\n")


def _conferir(arquivos: dict[str, str], entrada: str = ENTRADA) -> list[str]:
    """Roda a trava nestes arquivos de exemplo (caminho → texto), sem ler o disco."""
    return falhas_da_trava(list(arquivos), arquivos.get, entrada)


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
    """Os donos: `core/windows.py` pode ctypes, winreg e startfile, mas não subprocess nem CDLL; `core/nativo_dll.py`
    pode ctypes e CDLL, mas não subprocess; `core/processos.py` pode subprocess, mas não ctypes."""
    windows = '"""W."""\nimport ctypes\nimport winreg\nimport os\nimport subprocess\nx = ctypes.CDLL("a")\nos.startfile("a")\n'
    nativo = '"""N."""\nimport ctypes\nd = ctypes.CDLL("core/nativo/a.dll")\nimport subprocess\n'
    processos = '"""P."""\nimport subprocess\nimport ctypes\n'
    arquivos = {"main.py": '"""M."""\nimport core.windows\nimport core.nativo_dll\nimport core.processos\n',
                "core/windows.py": windows, "core/nativo_dll.py": nativo, "core/processos.py": processos}
    assert _conferir(arquivos) == [
        "core/nativo_dll.py:4: subprocess (import subprocess)",
        "core/processos.py:3: ctypes (import ctypes)",
        "core/windows.py:5: subprocess (import subprocess)",
        "core/windows.py:6: carregar DLL (usa ctypes...CDLL)",
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
    assert achados == [(2, "ctypes"), (3, "subprocess"), (4, "carregar DLL"), (4, "ctypes"), (5, "winreg"),
                       (6, "os.startfile"), (7, "subprocess"), (15, "os.startfile"), (16, "winreg"), (17, "ctypes"),
                       (18, "os.startfile"), (19, "ctypes"), (20, "rodar programa pelo os"),
                       (21, "rodar programa pelo os"), (22, "rodar programa pelo os"), (23, "rodar programa pelo os"),
                       (24, "subprocess")]


def test_rodar_programa_pelo_os_nao_tem_dono():
    """`os.system` é proibido até nos três donos (o desenho não dá essa capacidade a nenhum)."""
    texto = '"""D."""\nimport os\nos.system("dir")\n'
    arquivos = {"main.py": '"""M."""\nimport core.windows\nimport core.nativo_dll\nimport core.processos\n',
                "core/windows.py": texto, "core/nativo_dll.py": texto, "core/processos.py": texto}
    assert [f.split(":")[0] for f in _conferir(arquivos)] == ["core/nativo_dll.py", "core/processos.py",
                                                               "core/windows.py"]


CERTO = _py('''
    """Fala de ctypes, subprocess, winreg, os.startfile e os.system só no comentário e na docstring.

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
        return os.path.join(caminho, json.dumps(nome_do_subprocess), TEXTO, sistema)
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
    """Todo dono só tem capacidades de `CAPACIDADES`, e o ctypes tem dois donos (o Windows e as nossas DLLs), como no
    desenho; o `subprocess` e o carregar DLL, um só."""
    assert all(caps <= set(CAPACIDADES) for caps in DONOS.values())
    donos_de = {cap: sorted(a for a, caps in DONOS.items() if cap in caps) for cap in CAPACIDADES}
    assert donos_de == {"ctypes": ["core/nativo_dll.py", "core/windows.py"], "carregar DLL": ["core/nativo_dll.py"],
                        "subprocess": ["core/processos.py"], "winreg": ["core/windows.py"],
                        "os.startfile": ["core/windows.py"], "rodar programa pelo os": []}
