"""A trava "só `core/windows.py` fala com o Windows", lendo a estrutura do código (D-830, 23/11/2026).

De onde veio. O Samuel decidiu refazer o atualizador ("refazer", 23/11/2026, 18:50) e colou no chat da gerente a
mensagem do Fable: "ela pode mandar escrever a primeira trava (o teste que diz 'só core/windows.py fala com o
Windows'). Esse teste vai falhar hoje de propósito — a lista do que falha é a lista de trabalho do atualizador novo".
Resposta do Fable (`relatorios/para-o-fable-2026-11-23/resposta-do-fable.md`, "Travas mecânicas"): "Teste de AST em
`tests/`: `ctypes`, `subprocess`, `winreg`, `os.startfile` importados somente em `core/windows.py`. Binário, sem lista
de exceções."

O que confere. Em todo arquivo do programa, fora de `core/windows.py`, lê a árvore do código (o `ast` do Python, não
uma lista de palavras) e acusa cada lugar que:
- importa `ctypes`, `subprocess` ou `winreg` (`import x`, `import x.y`, `import x as z`, `from x import y`, `from x.y
  import z`);
- importa esses nomes ou o `startfile` de outro módulo (`from os import startfile`, `from core.windows import
  subprocess`: o mesmo módulo pego de segunda mão; `from os import *` também, porque traz o `startfile`);
- importa pelo nome escrito num texto (`__import__("ctypes")`, `importlib.import_module("subprocess")`);
- usa `startfile` (`os.startfile(...)`, `o.startfile`, `getattr(os, "startfile")`) ou um desses módulos pego dentro
  de outro módulo importado no arquivo (`from core import windows` e depois `windows.subprocess.run(...)`;
  `getattr(m, "ctypes")`). O `.ctypes` de uma variável (`imagem.ctypes.data_as(...)`, a interface do numpy para
  entregar a imagem a uma DLL) não é o módulo e não conta sozinho; o arquivo que faz isso importa o `ctypes` e é
  acusado na importação.
Comentário e docstring não contam (não são árvore). Código que o Python não consegue ler conta como falha, nunca como
"passou".

O que é "o programa": a mesma definição do porteiro, `regras_dos_agentes.porteiro.e_programa` (todo `.py`/`.pyw` que o
git conhece, fora das pastas de `NAO_E_PROGRAMA`: testes, relatórios, documentação, o próprio porteiro, o código de
fora...). A peça única é `porteiro.PECA_UNICA_DO_WINDOWS`. A lista dos arquivos vem da peça única do git
(`conversa_com_o_git.arquivos_do_git`, que só lê). Nada aqui tem definição própria: mudar uma delas é mudar o porteiro.

Por que é um teste à parte, e não uma conferência dentro do porteiro (escolha e porquê no
`relatorios/atualizador-novo/ONDE-PAREI.md`): a lista de exceções do porteiro está "valendo" e só ganha item com o
"sim" do Samuel; uma conferência nova dentro do porteiro, neste ramo, faria o teste antigo
`test_o_repositorio_so_tem_os_erros_que_a_lista_deixa` falhar (D-605: teste antigo não pode quebrar) e o juiz do GitHub
nem a veria (ele usa o porteiro da versão de teste). Esta trava não tem lista de exceções, de propósito. **Quando for
juntada, ela deve substituir a parte da K01 que procura essas mesmas coisas por palavras**, para não ficarem duas
conferências da mesma regra (§11.12, "uma peça só").

Ela falha hoje de propósito (pedido do Fable, D-830): a lista que ela mostra é a lista de trabalho do atualizador novo.
As outras provas deste arquivo (os exemplos feitos de propósito) passam: elas provam que a trava acusa o errado e não
acusa o certo.

O que ela NÃO pega (escrito para ninguém achar que pega): `os.system`, `os.popen`, `os.spawn*`, `os.exec*`,
`multiprocessing` e `asyncio.create_subprocess_*` (outros jeitos de rodar programa, fora dos quatro pedidos; a K01 do
porteiro pega `os.system` e `os.popen` por palavra); `sys.modules["ctypes"]`; o nome do módulo montado em pedaços
(`__import__("ct" + "ypes")`); um módulo nosso que guarda o `subprocess` com outro nome e o entrega por uma função.

Seguro mexer: o texto das frases. Arriscado: tirar um nome de `MODULOS_PROIBIDOS` ou de `NOMES_PROIBIDOS`, ou trocar
`porteiro.e_programa` por uma definição própria (afrouxa a trava calada). Proibido, pela própria decisão: acrescentar
lista de exceções.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from regras_dos_agentes import conversa_com_o_git as git
from regras_dos_agentes import leitura_do_codigo as leitura
from regras_dos_agentes import porteiro

RAIZ = Path(__file__).resolve().parent.parent

# Os módulos da biblioteca do Python que conversam com o Windows (o pedido do Fable, D-830). `_winreg` é o nome antigo
# do `winreg` (Python 2). Fontes: https://docs.python.org/3/library/ctypes.html,
# https://docs.python.org/3/library/subprocess.html, https://docs.python.org/3/library/winreg.html.
MODULOS_PROIBIDOS = frozenset({"ctypes", "subprocess", "winreg", "_winreg"})
# Os nomes que, pegos de outro módulo ou usados como atributo, são essa mesma conversa: os módulos e o
# `os.startfile` (https://docs.python.org/3/library/os.html#os.startfile).
NOMES_PROIBIDOS = MODULOS_PROIBIDOS | {"startfile"}
# As funções que importam um módulo pelo nome escrito num texto (https://docs.python.org/3/library/functions.html#import__
# e https://docs.python.org/3/library/importlib.html#importlib.import_module).
IMPORTA_POR_TEXTO = frozenset({"__import__", "import_module"})


def _topo(nome: str) -> str:
    """O primeiro pedaço de um nome de módulo (`ctypes.wintypes` → `ctypes`)."""
    return nome.split(".", 1)[0]


def _nome_da_funcao(chamada: ast.Call) -> str:
    """O nome da função chamada (`f(...)` → `f`; `m.f(...)` → `f`); "" se não for um nome."""
    alvo = chamada.func
    return alvo.attr if isinstance(alvo, ast.Attribute) else alvo.id if isinstance(alvo, ast.Name) else ""


def _texto_constante(no: ast.AST | None) -> str | None:
    """O texto, se o nó é um texto escrito no código; senão None."""
    return no.value if isinstance(no, ast.Constant) and isinstance(no.value, str) else None


def lugares_proibidos(fonte: str) -> list[tuple[int, str]]:
    """(linha, o que foi achado) de cada lugar do arquivo que fala com o Windows pela estrutura do código.

    Lê só a árvore (`ast`): comentário e docstring nunca contam. Um achado por linha e por motivo. Levanta
    `leitura.CodigoIlegivel` se o texto não for Python válido (quem chama trata isso como falha).
    """
    achados: set[tuple[int, str]] = set()
    raiz = leitura.arvore(fonte)
    importados = _nomes_importados(raiz)
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            for apelido in no.names:
                if _topo(apelido.name) in MODULOS_PROIBIDOS:
                    achados.add((no.lineno, f"import {apelido.name}"))
        elif isinstance(no, ast.ImportFrom):
            modulo = no.module or ""
            if not no.level and _topo(modulo) in MODULOS_PROIBIDOS:
                achados.add((no.lineno, f"from {modulo} import ..."))
                continue
            for apelido in no.names:
                if apelido.name in NOMES_PROIBIDOS:
                    achados.add((no.lineno, f"from {'.' * no.level}{modulo} import {apelido.name}"))
                elif apelido.name == "*" and not no.level and modulo == "os":
                    achados.add((no.lineno, "from os import * (traz o startfile)"))
        elif isinstance(no, ast.Call):
            nome = _nome_da_funcao(no)
            primeiro = _texto_constante(no.args[0]) if no.args else None
            if nome in IMPORTA_POR_TEXTO and primeiro is not None and _topo(primeiro) in MODULOS_PROIBIDOS:
                achados.add((no.lineno, f"{nome}({primeiro!r})"))
            segundo = _texto_constante(no.args[1]) if len(no.args) >= 2 else None
            if nome == "getattr" and segundo in NOMES_PROIBIDOS:
                achados.add((no.lineno, f"getattr(..., {segundo!r})"))
        elif isinstance(no, ast.Attribute) and no.attr == "startfile":
            achados.add((no.lineno, "usa .startfile"))
        elif (isinstance(no, ast.Attribute) and no.attr in MODULOS_PROIBIDOS
              and _raiz_do_atributo(no) in importados):
            # O módulo pego dentro de outro módulo importado (`windows.subprocess.run`). O `.ctypes` de uma variável
            # (`imagem.ctypes.data_as`, a interface do numpy para passar a imagem à DLL) não é o módulo: não conta
            # aqui; o arquivo que faz isso importa o `ctypes` e é acusado na importação.
            achados.add((no.lineno, f"usa {_raiz_do_atributo(no)}...{no.attr}"))
    return sorted(achados)


def _nomes_importados(raiz: ast.Module) -> set[str]:
    """Os nomes que as importações deste arquivo criam (`import a.b` → `a`; `import a as b` → `b`; `from a import c`
    → `c`): são os módulos (ou coisas de módulos) que o arquivo usa por nome."""
    nomes: set[str] = set()
    for no in ast.walk(raiz):
        if isinstance(no, ast.Import):
            nomes |= {a.asname or _topo(a.name) for a in no.names}
        elif isinstance(no, ast.ImportFrom):
            nomes |= {a.asname or a.name for a in no.names if a.name != "*"}
    return nomes


def _raiz_do_atributo(no: ast.Attribute) -> str:
    """O nome no começo de `a.b.c` (`a`); "" se o começo não for um nome."""
    valor = no.value
    while isinstance(valor, ast.Attribute):
        valor = valor.value
    return valor.id if isinstance(valor, ast.Name) else ""


def falhas_nos_arquivos(caminhos, ler) -> list[str]:
    """As falhas da trava, "arquivo:linha: o que", nos arquivos do programa fora da peça única.

    `ler(caminho)` devolve o texto do arquivo ou None. Arquivo do programa que não se consegue ler ou que não é Python
    válido vira falha (nunca "passou").
    """
    falhas = []
    for caminho in sorted(set(caminhos)):
        if not porteiro.e_programa(caminho) or caminho == porteiro.PECA_UNICA_DO_WINDOWS:
            continue
        fonte = ler(caminho)
        if fonte is None:
            falhas.append(f"{caminho}:0: não deu para ler o arquivo")
            continue
        try:
            lugares = lugares_proibidos(fonte)
        except leitura.CodigoIlegivel as erro:
            falhas.append(f"{caminho}:0: o código não pôde ser lido ({erro})")
            continue
        falhas += [f"{caminho}:{linha}: {o_que}" for linha, o_que in lugares]
    return falhas


def _ler_da_pasta(caminho: str) -> str | None:
    """O texto do arquivo nesta cópia, ou None se não deu para ler."""
    try:
        return (RAIZ / caminho).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def falhas_do_repositorio() -> list[str]:
    """As falhas da trava no repositório inteiro (os arquivos que o git conhece, como estão na pasta)."""
    return falhas_nos_arquivos(git.arquivos_do_git(RAIZ), _ler_da_pasta)


# ---------------------------------------------------------------- a trava

def test_so_core_windows_fala_com_o_windows():
    """A trava (D-830): `ctypes`, `subprocess`, `winreg` e `os.startfile` só em `core/windows.py`. Binária.

    FALHA HOJE DE PROPÓSITO: a lista que ela mostra é a lista de trabalho do atualizador novo (pedido do Fable que o
    Samuel colou, 23/11/2026). Ela passa quando o último lugar for para a peça única ou sair do programa.
    """
    falhas = falhas_do_repositorio()
    assert not falhas, (f"{len(falhas)} lugares do programa falam com o Windows fora de "
                        f"{porteiro.PECA_UNICA_DO_WINDOWS}:\n" + "\n".join(falhas))


# ---------------------------------------------------------------- as provas de que a trava funciona

def _py(texto: str) -> str:
    """Tira a margem do exemplo."""
    return textwrap.dedent(texto).lstrip("\n")


def _conferir(arquivos: dict[str, str]) -> list[str]:
    """Roda a trava nestes arquivos de exemplo (caminho → texto), sem ler o disco."""
    return falhas_nos_arquivos(arquivos, arquivos.get)


def test_acusa_import_ctypes_fora_da_peca_e_nao_acusa_dentro():
    """Um arquivo de exemplo com `import ctypes`: fora da peça é acusado; o mesmo texto em `core/windows.py`, não."""
    exemplo = '"""Exemplo."""\nimport ctypes\n'
    assert _conferir({"atualizacao.py": exemplo}) == ["atualizacao.py:2: import ctypes"]
    assert _conferir({"core/qualquer.py": exemplo}) == ["core/qualquer.py:2: import ctypes"]
    assert _conferir({porteiro.PECA_UNICA_DO_WINDOWS: exemplo}) == []


def test_usa_a_definicao_de_programa_do_porteiro():
    """Fora do programa (testes, relatórios, o próprio porteiro) não é acusado; pasta nova é programa (como no
    porteiro, achado Q2), e o `.pyw` também (achado S2)."""
    exemplo = '"""Exemplo."""\nimport subprocess\n'
    for fora in ("tests/test_x.py", "relatorios/x/script.py", "regras_dos_agentes/x.py", "docs/x.py"):
        assert not porteiro.e_programa(fora)
        assert _conferir({fora: exemplo}) == [], fora
    for dentro in ("servicos/__init__.py", "main.pyw", "publicar.py"):
        assert porteiro.e_programa(dentro)
        assert _conferir({dentro: exemplo}) == [f"{dentro}:2: import subprocess"], dentro


ERRADO = _py('''
    """Cada jeito de falar com o Windows pela estrutura do código."""
    import ctypes.wintypes
    import subprocess as sp
    from ctypes import windll
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
        return windows.subprocess.run(["x"])
''')


def test_acusa_cada_jeito_de_importar_e_de_usar():
    """Cada forma de importar ou usar os quatro, uma linha cada (a estrutura, não a palavra)."""
    linhas = [int(f.split(":")[1]) for f in _conferir({"atualizacao.py": ERRADO})]
    assert linhas == [2, 3, 4, 5, 6, 7, 15, 16, 17, 18, 19, 20]


def test_o_ctypes_de_uma_imagem_do_numpy_nao_e_o_modulo_mas_o_import_e_acusado():
    """`imagem.ctypes.data_as(...)` (o numpy entregando a imagem à DLL do ScanTailor) não é o módulo `ctypes`; o
    `import ctypes` do mesmo arquivo é acusado, então nada fica escondido."""
    exemplo = _py('''
        """E."""
        import ctypes


        def f(imagem, funcao):
            """Chama a DLL com a imagem."""
            return funcao(imagem.ctypes.data_as(ctypes.c_void_p))
    ''')
    assert _conferir({"core/x_scantailor.py": exemplo}) == ["core/x_scantailor.py:2: import ctypes"]


def test_acusa_from_os_import_estrela_que_traz_o_startfile():
    """`from os import *` traz o `startfile` (no Windows ele está em `os.__all__`)."""
    assert _conferir({"x.py": '"""E."""\nfrom os import *\n'}) == ["x.py:2: from os import * (traz o startfile)"]


CERTO = _py('''
    """Fala de ctypes, subprocess, winreg e os.startfile só no comentário e na docstring.

    import ctypes  (isto é docstring, não código)
    """
    # import subprocess  (comentário)
    import os
    import json

    TEXTO = "import ctypes"  # um texto com a palavra não é importação


    def f(caminho):
        """os.startfile(caminho) seria proibido; aqui só se fala dele."""
        nome_do_subprocess = "subprocess"
        return os.path.join(caminho, json.dumps(nome_do_subprocess), TEXTO)
''')


def test_nao_acusa_comentario_docstring_texto_nem_nome_parecido():
    """Comentário, docstring, texto com a palavra e nome que só contém a palavra não são a conversa com o Windows."""
    assert _conferir({"atualizacao.py": CERTO}) == []


def test_codigo_ilegivel_e_arquivo_que_nao_abre_sao_falha_nunca_passou():
    """Python que não se consegue ler e arquivo que não abre viram falha (a trava nunca passa calada)."""
    assert _conferir({"x.py": "def (:\n"})[0].startswith("x.py:0: o código não pôde ser lido")
    assert falhas_nos_arquivos(["y.py"], lambda _c: None) == ["y.py:0: não deu para ler o arquivo"]


@pytest.mark.parametrize("modulo", sorted(MODULOS_PROIBIDOS))
def test_cada_modulo_proibido_e_acusado(modulo):
    """Cada módulo da lista, importado do jeito mais simples, é acusado."""
    assert _conferir({"x.py": f'"""E."""\nimport {modulo}\n'}) == [f"x.py:2: import {modulo}"]
