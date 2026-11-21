"""Desliga cada proteção nova (D-809, D-811, D-812, D-814) e roda o arquivo de teste dela: algum teste tem de falhar.

Uso: python mutacoes.py <pasta da cópia>. Cada mutação roda num processo à parte (o código dos arquivos não muda: a
troca é feita na memória, antes do pytest rodar). Saída: uma linha por mutação, ACUSADA ou PASSOU (a ruim).
"""
import ast
import subprocess
import sys

COPIA = sys.argv[1]
PY = sys.executable

MUTACOES = {
    "M1 K25 sem a lista do git": ("from regras_dos_agentes import porteiro; porteiro._GIT_QUE_MUDA[:] = []",
                                  "tests/test_conferencias_codigo.py", "k25"),
    "M2 K25 sem conferir o atalho antes": (
        "import re; from regras_dos_agentes import porteiro; porteiro._CONFERE_SE_E_ATALHO = re.compile('(?!)')",
        "tests/test_conferencias_codigo.py", "k25"),
    "M3 K25 sem a exceção das duas peças": ("from regras_dos_agentes import porteiro; porteiro.PECAS_DO_GIT = ()",
                                            "tests/test_conferencias_codigo.py", "k25"),
    "M4 K25 lê texto solto como comando": (
        "import ast; from regras_dos_agentes import porteiro; porteiro.leitura.comandos = lambda raiz: "
        "[(n.lineno, n.value) for n in ast.walk(raiz) if isinstance(n, ast.Constant) and isinstance(n.value, str)]",
        "tests/test_conferencias_codigo.py", "k25"),
    "M5 K25 sem tirar o comentário do terminal": (
        "from regras_dos_agentes import porteiro; porteiro._sem_comentario_do_terminal = lambda c, l: l",
        "tests/test_conferencias_codigo.py", "k25"),
    "M6 F21 sem conferir o teste de cada proteção": (
        "from regras_dos_agentes import formulario; formulario._conferir_protecoes = lambda campos, r: None",
        "tests/test_conferencias_formulario.py", "d811"),
    "M7 F22 sem as etiquetas do trabalho que confere": (
        "from regras_dos_agentes import formulario; formulario.CAMPOS[:] = [c for c in formulario.CAMPOS "
        "if c[0] != 'F22']", "tests/test_conferencias_formulario.py", "d812"),
    "M8 F23 sem conferir as decisões procuradas": (
        "from regras_dos_agentes import formulario; formulario._conferir_procuradas = lambda s, t, l, r: None",
        "tests/test_conferencias_formulario.py", "d814"),
    "M9 vale_para sempre sim": (
        "from regras_dos_agentes import formulario; formulario.vale_para = lambda quem, tags: True",
        "tests/test_conferencias_formulario.py", "novas or formulario_certo"),
    "M10 F23 aceita decisão que não existe no Livro": (
        "from regras_dos_agentes import formulario; formulario.Livro.existe = lambda self, n: True",
        "tests/test_conferencias_formulario.py", "d814"),
    "M11 pacote escolhe os campos com conta própria": (
        "from regras_dos_agentes import montar_pacote; v = montar_pacote.formulario.vale_para; "
        "montar_pacote.formulario = type('F', (), dict(vars(montar_pacote.formulario), vale_para=staticmethod("
        "lambda quem, tags: quem == '*' or (isinstance(quem, str) and quem in tags))))",
        "tests/test_conferencias_pacote.py", "em_branco or perguntas_novas"),
    "M12 D-813 sem o acréscimo no sempre": (
        "from regras_dos_agentes import catalogo; s = next(x for x in catalogo.SEMPRE if 'R118' in x['cobre']); "
        "s['texto'] = s['texto'].replace(catalogo.ACRESCIMO_D813, '')", "tests/test_conferencias_pacote.py", "d813"),
}

for nome, (troca, arquivo, filtro) in MUTACOES.items():
    codigo = (f"import sys; {troca}\nimport pytest\n"
              f"sys.exit(pytest.main(['{arquivo}', '-q', '-p', 'no:cacheprovider', '-k', '{filtro}']))")
    ast.parse(codigo)
    r = subprocess.run([PY, "-c", codigo], cwd=COPIA, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env={**__import__("os").environ, "QT_QPA_PLATFORM": "offscreen"})
    fim = (r.stdout.strip().splitlines() or ["?"])[-1]
    print(f"{'ACUSADA' if r.returncode == 1 else 'PASSOU (ruim)' if r.returncode == 0 else 'ERRO'}: {nome} -> {fim}")
