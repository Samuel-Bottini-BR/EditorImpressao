"""Provas do porteiro que lê o código parado (D-791): cada conferência acusa o errado e não acusa o certo.

Palavras do Samuel (D-791, 18/11/2026), à pergunta das conferências automáticas: "b" (barram desde o primeiro dia).
A prova pedida no Livro: "Cada conferência acusa o erro num exemplo feito de propósito e não acusa o código certo".

Os exemplos errados são, sempre que existe, o texto de verdade do código de hoje (o defeito 1 da etapa 5, o
`DETACHED_PROCESS` do "Reiniciar agora", `atualizacao.py`; o defeito 4, a tranca da pasta `/inheritance:r`,
`core/testes_a_distancia.py`), escritos aqui como dado. Os arquivos são entregues ao porteiro como texto (o porteiro só
lê texto); nada aqui roda o Windows.

A numeração é a da tabela da proposta das regras (§5.1), não a do esboço.
"""

from __future__ import annotations

import re
import textwrap

import pytest

from regras_dos_agentes import porteiro


def conferir(arquivos: dict[str, str]) -> list[porteiro.Achado]:
    """Roda o porteiro do código parado nestes arquivos (caminho → texto)."""
    return porteiro.conferir_codigo(arquivos, lambda c: arquivos.get(c))


def codigos(achados, conferencia: str) -> list[tuple[str, int]]:
    """(arquivo, linha) dos achados de uma conferência."""
    return [(a.arquivo, a.linha) for a in achados if a.conferencia == conferencia]


def py(texto: str) -> str:
    """Tira a margem do exemplo."""
    return textwrap.dedent(texto).lstrip("\n")


# ---------------------------------------------------------------- K01

ERRADO_K01 = py('''
    """Um arquivo do programa que conversa com o Windows por conta própria."""
    import ctypes
    import subprocess

    def lancar():
        """Lança o PowerShell escondido (o jeito do "Reiniciar agora" da etapa 5)."""
        subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass"])

    def pedir_licenca(info):
        """Pede a licença de administrador."""
        info.lpVerb = "runas"
        if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(info)):
            return False
        return True

    def tarefa():
        """Roda a tarefa."""
        return ["schtasks", "/Run", "/TN", "x"]

    def servidor(c):
        """Liga o servidor."""
        return f"Add-WindowsCapability -Online -Name {c}"

    def caminho(w):
        """O caminho do PowerShell."""
        return w / "WindowsPowerShell" / "v1.0" / "powershell.exe"

    def janelinha():
        """A janelinha do "Reiniciar agora" (atualizacao.py, linha 883 em 19/11)."""
        return "$jPs = [powershell]::Create(); $jPs.Runspace = $jRun"
''')


def test_k01_acusa_a_conversa_com_o_windows_fora_da_peca_unica():
    """K01 acusa cada linha que fala com o Windows fora de `core/windows.py`, nos textos e nos nomes."""
    achados = conferir({"atualizacao.py": ERRADO_K01})
    linhas = [n for _, n in codigos(achados, "K01")]
    assert linhas == [7, 11, 12, 18, 22, 26, 30]


def test_k01_correcao_1_o_esboco_perdia_os_textos_sem_aspas_e_os_nomes():
    """Correção 1 do plano-v3, passo 0 (achado 67 do plano): a busca do esboço perdia lugares.

    O esboço `conferir_codigo.py` (ramo regras-agentes-2026-11-18) procurava `'runas'` e `'powershell'` COM as aspas
    dentro do texto, mas lia o valor do texto (que não tem aspas), e não olhava os nomes do código. Aqui está a busca
    do esboço, copiada como referência: no mesmo exemplo ela acha 2 das 7 linhas; a do porteiro acha as 7. A linha 30
    (o `[powershell]::Create()` da janelinha) só a busca sem aspas pega, mesmo lendo o texto da linha inteira.
    """
    import ast

    esboco = re.compile(
        r"ShellExecute|['\"]runas['\"]|schtasks|icacls|Set-Acl|Update\.exe|DETACHED_PROCESS|netsh|New-NetFirewallRule|"
        r"Add-WindowsCapability|sc\.exe|windll\.shell32|['\"]powershell(\.exe)?['\"]", re.I)
    arvore = ast.parse(ERRADO_K01)
    docs = {id(n.body[0].value) for n in ast.walk(arvore)
            if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body and isinstance(n.body[0], ast.Expr)}
    do_esboco = {n.lineno for n in ast.walk(arvore) if isinstance(n, ast.Constant) and isinstance(n.value, str)
                 and id(n) not in docs and esboco.search(n.value)}
    assert do_esboco == {18, 22}
    novos = {n for _, n in codigos(conferir({"atualizacao.py": ERRADO_K01}), "K01")}
    assert novos == {7, 11, 12, 18, 22, 26, 30}
    assert do_esboco < novos, "o porteiro tem de achar tudo o que o esboço achava, e mais"


def test_k01_nao_acusa_a_peca_unica_comentario_docstring_nome_de_funcao_nem_teste():
    """K01 não acusa: a peça única (`core/windows.py`), comentário, docstring, nome de função que só contém a palavra,
    nem arquivo que não é do programa (testes, scripts de outra pasta)."""
    certo = py('''
        """Explica que o PowerShell e o schtasks só são chamados pela peça única (docstring pode falar)."""
        def _caminho_do_powershell():
            """Devolve o caminho."""
            # comentário pode falar de runas e de ShellExecuteExW
            return _caminho_do_powershell
    ''')
    assert codigos(conferir({"core/windows.py": ERRADO_K01}), "K01") == []
    assert codigos(conferir({"core/filtros.py": certo}), "K01") == []
    assert codigos(conferir({"tests/test_x.py": ERRADO_K01, "docs/plano/x.py": ERRADO_K01}), "K01") == []


# ---------------------------------------------------------------- K02 e K03

ERRADO_K02 = py('''
    import subprocess

    def lancar(cmd):
        """O jeito de lançar do defeito 1 da etapa 5."""
        subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
                         | getattr(subprocess, "DETACHED_PROCESS", 0))
        subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
''')

ERRADO_K03 = py('''
    SID = "S-1-5-18"

    def proteger(pasta):
        """A tranca da pasta do defeito 4 da etapa 5."""
        return (f" icacls $pasta /setowner '*{SID}' /T /C /Q | Out-Null;"
                f" icacls $pasta /inheritance:r /grant:r '*{SID}:(OI)(CI)F'")
''')


def test_k02_acusa_detached_process_ate_na_peca_unica():
    """K02 acusa o DETACHED_PROCESS em qualquer arquivo do programa, inclusive `core/windows.py` (D-774)."""
    assert [n for _, n in codigos(conferir({"atualizacao.py": ERRADO_K02}), "K02")] == [6, 7]
    assert [n for _, n in codigos(conferir({"core/windows.py": ERRADO_K02}), "K02")] == [6, 7]


def test_k02_nao_acusa_comentario_docstring_nem_outro_jeito_de_lancar():
    """K02 não acusa o comentário que explica por que tirou, nem `CREATE_NEW_PROCESS_GROUP` sozinho."""
    certo = py('''
        import subprocess

        def lancar(cmd):
            """Sem DETACHED_PROCESS: o PowerShell lançado assim sai sem rodar."""
            # não usar DETACHED_PROCESS (etapa 5, defeito 1)
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    ''')
    assert codigos(conferir({"atualizacao.py": certo, "core/windows.py": certo}), "K02") == []


def test_k03_acusa_a_tranca_da_pasta_a_mao_ate_na_peca_unica():
    """K03 acusa icacls, /inheritance:r e /setowner em qualquer arquivo do programa (plano, peça 2)."""
    assert [n for _, n in codigos(conferir({"core/testes_a_distancia.py": ERRADO_K03}), "K03")] == [5, 6]
    assert [n for _, n in codigos(conferir({"core/windows.py": ERRADO_K03}), "K03")] == [5, 6]


def test_k03_nao_acusa_quando_so_a_explicacao_fala_da_tranca():
    """K03 não acusa a docstring nem o comentário."""
    certo = py('''
        def proteger(pasta):
            """Nada de icacls nem /inheritance:r: a pasta segura nasce com as licenças de fábrica."""
            # icacls /setowner ficou de fora de propósito
            return pasta
    ''')
    assert codigos(conferir({"core/windows.py": certo}), "K03") == []


# ---------------------------------------------------------------- K04

def test_k04_acusa_numero_de_decisao_em_texto_que_a_pessoa_ve():
    """K04 acusa "D-068" numa dica da tela (o caso real do Automático) e num passo dos testes à distância."""
    tela = py('''
        def dica():
            """A dica."""
            return ("escolhido em \\"Rodar\\" (D-068: toda função automática "
                    "tem ligar e desligar)")
    ''')
    passos = 'def plano():\n    """O plano."""\n    return ["Anotar o que o computador ja tinha antes (D-731)"]\n'
    assert codigos(conferir({"ui/automatico.py": tela}), "K04") == [("ui/automatico.py", 3)]
    assert codigos(conferir({"core/testes_a_distancia.py": passos}), "K04") == [("core/testes_a_distancia.py", 3)]
    assert codigos(conferir({"atualizacao.py": passos, "main.py": passos}), "K04") == [("atualizacao.py", 3),
                                                                                       ("main.py", 3)]


def test_k04_correcao_3_comentario_da_folha_de_estilo_nao_conta():
    """Correção 3 do plano-v3, passo 0: o comentário `/* ... */` dentro da folha de estilo não aparece na tela.

    O texto é o de `ui/estilo.py` (linhas 447 a 449 em 19/11/2026), em duas linhas. Fora do comentário, o mesmo
    número na mesma folha é acusado.
    """
    folha = py('''
        def folha(c):
            """A folha de estilo."""
            return f"""
        QWidget {{ background: {c["app"]}; }}
        /* Barra de baixo do livro: etapa 6 da obra, pedidos de 26/10 sobre o
           baixo, no tamanho e no aceso dos botões da barra de baixo do livro aberto (D-015, lyupdf) */
        QLabel {{ color: red; }}
        """
    ''')
    assert codigos(conferir({"ui/estilo.py": folha}), "K04") == []
    errado = folha.replace("QLabel {{ color: red; }}", 'QLabel {{ qproperty-text: "veja D-015"; }}')
    assert codigos(conferir({"ui/estilo.py": errado}), "K04") == [("ui/estilo.py", 7)]


def test_k04_nao_acusa_comentario_docstring_nem_processamento():
    """K04 não acusa comentário, docstring nem arquivo que não é do programa (um teste, um script de documentos)."""
    certo = 'def f():\n    """Ver D-068."""\n    # D-094\n    return 1\n'
    assert codigos(conferir({"ui/automatico.py": certo}), "K04") == []
    assert codigos(conferir({"tests/test_x.py": 'X = "D-068"\n', "docs/plano/x.py": 'X = "D-068"\n'}), "K04") == []


def test_k04_e_k05_olham_tambem_os_avisos_que_moram_em_core():
    """Achado 9 de quem tentou quebrar (19/11): os avisos do "Para revisar" que o Kaique lê moram em `core/`."""
    assert codigos(conferir({"core/analise.py": 'AVISO = "confira (D-068)"\n'}), "K04") == [("core/analise.py", 1)]
    assert codigos(conferir({"core/analise.py": f'AVISO = "pronto {chr(0x1F600)}"\n'}), "K05") == [
        ("core/analise.py", 1)]


# ---------------------------------------------------------------- K05 a K08

def test_k05_acusa_emoji_na_tela_e_nao_acusa_seta_nem_fora_da_tela():
    """K05 acusa um emoji num texto da tela; a seta comum e o texto de um teste não."""
    rosto, seta = chr(0x1F600), chr(0x2192)
    assert codigos(conferir({"ui/tela.py": f'R = "Pronto {rosto}"\n'}), "K05") == [("ui/tela.py", 1)]
    assert codigos(conferir({"ui/tela.py": f'R = "Próxima {seta}"\n'}), "K05") == []
    assert codigos(conferir({"tests/test_x.py": f'R = "{rosto}"\n'}), "K05") == []


def test_k06_acusa_core_importando_ui_e_nao_acusa_o_resto():
    """K06 acusa `from ui...` e o relativo que sobe até `ui`; não acusa um módulo de nome parecido."""
    assert codigos(conferir({"core/a.py": "from ui.estilo import TEMAS\n"}), "K06") == [("core/a.py", 1)]
    assert codigos(conferir({"core/a.py": "import ui\n"}), "K06") == [("core/a.py", 1)]
    assert codigos(conferir({"core/a.py": "from ..ui import estilo\n"}), "K06") == [("core/a.py", 1)]
    assert codigos(conferir({"core/a.py": "import uiutils\nfrom core import ui_x\n",
                             "ui/b.py": "from ui import estilo\n"}), "K06") == []


def test_k07_acusa_tkinter_e_nao_acusa_pyside6():
    """K07 acusa tkinter e customtkinter no programa; PySide6 e o tkinter de um teste solto, não."""
    assert len(codigos(conferir({"main.py": "import tkinter\nfrom tkinter import ttk\n"
                                            "import customtkinter as ctk\n"}), "K07")) == 3
    assert codigos(conferir({"main.py": "from PySide6 import QtWidgets\n",
                             "velhos/x.py": "import tkinter\n"}), "K07") == []


def test_k08_acusa_nome_com_acento_no_programa_e_nao_fora():
    """K08 acusa nome de arquivo com acento em core/, ui/ e na raiz; nos relatórios, não."""
    achados = conferir({"core/ação.py": "X = 1\n", "Leia-me ção.md": "", "relatorios/ação.md": "",
                        "ui/tela.py": "X = 1\n"})
    assert sorted(codigos(achados, "K08")) == [("Leia-me ção.md", 0), ("core/ação.py", 0)]


# ---------------------------------------------------------------- K16, K22, K23, K24

def test_k16_acusa_biblioteca_que_desenha_e_nao_acusa_a_que_aponta():
    """K16 acusa diffusers no requirements.txt e no código; onnxruntime (só aponta) não."""
    achados = conferir({"requirements.txt": "numpy>=2.0\ndiffusers>=0.30  # não\nreal-esrgan\nrealesrgan==0.3\n",
                        "core/x.py": "import diffusers\nimport onnxruntime\n"})
    assert sorted(codigos(achados, "K16")) == [("core/x.py", 1), ("requirements.txt", 2), ("requirements.txt", 4)]
    assert codigos(conferir({"requirements.txt": "onnxruntime>=1.28\n# diffusers nunca\n"}), "K16") == []


FOLHA_DE_HOJE = py('''
    TEMAS: dict[str, dict[str, str]] = {
        "escuro": {"rolagem": "#4A4D54"},
        "cinza": {"rolagem": "#6A6A6A"},
        "claro": {"rolagem": "#B5B3AC"},
    }

    def folha(c):
        """A folha."""
        return f"""
    QScrollBar::handle:vertical {{ background: {c["rolagem"]}; border-radius: 6px; min-height: 40px; }}
    """
''')


def test_k22_acusa_a_barra_de_rolagem_que_mudou_de_cor():
    """K22 acusa a barra de rolagem de um tema com outra cor, e a folha que não usa mais a cor do tema."""
    assert codigos(conferir({"ui/estilo.py": FOLHA_DE_HOJE}), "K22") == []
    preta = FOLHA_DE_HOJE.replace("#6A6A6A", "#000000")
    assert len(codigos(conferir({"ui/estilo.py": preta}), "K22")) == 1
    sem_cor = FOLHA_DE_HOJE.replace('{c["rolagem"]}', "#000000")
    assert len(codigos(conferir({"ui/estilo.py": sem_cor}), "K22")) == 1


AGENTE_CERTO = "---\nname: implementador\ntools: Read, Write, Edit, Bash, PowerShell\n---\n\nTexto.\n"


def test_k23_acusa_agente_com_ferramenta_de_abrir_agente_ou_da_central():
    """K23 acusa a ferramenta de abrir outro agente, as da Central e o agente sem lista (herda todas, D-793)."""
    caminho = ".claude/agents/implementador.md"
    assert codigos(conferir({caminho: AGENTE_CERTO}), "K23") == []
    assert len(codigos(conferir({caminho: AGENTE_CERTO.replace("Bash", "Bash, Agent")}), "K23")) == 1
    assert len(codigos(conferir({caminho: AGENTE_CERTO.replace("Bash", "Bash, Task")}), "K23")) == 1
    assert len(codigos(conferir({caminho: AGENTE_CERTO.replace("Bash", "mcp__claude__ArtifactData")}), "K23")) == 1
    assert len(codigos(conferir({caminho: "---\nname: x\n---\nTexto.\n"}), "K23")) == 1


def test_k24_acusa_pywinauto_que_toma_o_mouse_e_nao_acusa_mensagem_nativa():
    """K24 acusa `click_input`, `send_keys` e `type_keys` de quem usa pywinauto; a mensagem nativa e o texto, não."""
    errado = py('''
        from pywinauto import Application

        def clicar(b):
            """Clica."""
            b.click_input()
            b.type_keys("abc")
    ''')
    certo = py('''
        import pywinauto

        def clicar(b):
            """Clica sem tomar o mouse ("nunca click_input")."""
            b.click()
    ''')
    assert [n for _, n in codigos(conferir({"teste_botoes.py": errado}), "K24")] == [5, 6]
    assert codigos(conferir({"teste_botoes.py": certo, "tests/test_x.py": 'X = "click_input"\n'}), "K24") == []


# ---------------------------------------------------------------- arquivo que não dá para ler

def test_arquivo_ilegivel_vira_achado_e_nunca_passa():
    """Um arquivo do programa que não é Python válido vira K00, nunca "passou" (CLAUDE.md §11.12, ponto 2)."""
    achados = conferir({"core/x.py": "def f(:\n"})
    assert [(a.conferencia, a.arquivo) for a in achados] == [("K00", "core/x.py")]
    assert [(a.conferencia, a.arquivo) for a in porteiro.conferir_codigo(["core/y.py"], lambda c: None)] == [
        ("K00", "core/y.py")]


def test_arquivo_com_marca_de_utf8_e_lido():
    """A marca de UTF-8 no começo (três arquivos de hoje têm) não impede a leitura nem esconde um erro."""
    achados = conferir({"atualizacao.py": chr(0xFEFF) + ERRADO_K02})
    assert [n for _, n in codigos(achados, "K02")] == [6, 7]


def test_as_24_conferencias_tem_a_numeracao_da_tabela_da_proposta():
    """As 24 conferências, K01 a K24, cada uma com a regra e o tipo (vale a numeração da tabela, plano-v3).

    Mudado com a D-809 (19/11/2026: "Conferência nova do porteiro", com o "ok" do Samuel): as conferências novas do
    catálogo dos erros continuam a numeração depois da K24, sem buraco, e cada uma cita a decisão que a criou. As 24
    da tabela continuam as mesmas, na mesma ordem."""
    numeros = [c.codigo for c in porteiro.CONFERENCIAS]
    assert numeros[:24] == [f"K{n:02d}" for n in range(1, 25)]
    assert numeros == [f"K{n:02d}" for n in range(1, len(numeros) + 1)]
    assert all(re.search(r"\bD-\d{3,}\b", c.regra) for c in porteiro.CONFERENCIAS[24:])
    assert porteiro.POR_CODIGO["K05"].o_que.startswith("emoji")
    assert porteiro.POR_CODIGO["K08"].o_que.startswith("nome de arquivo com acento")
    assert all(c.tipo in ("codigo", "entrega") and c.regra for c in porteiro.CONFERENCIAS)


# ---------------------------------------------------------------- a busca ampliada (achado 2, 19/11)

# Os 14 jeitos de pedir a mesma coisa com outro nome que quem tentou quebrar provou passarem pela busca antiga, mais
# os do mesmo tipo lidos na documentação. Cada linha é um caso errado, de um arquivo do programa.
OUTROS_NOMES = [
    'subprocess.run(["pwsh", "-Command", "x"])',
    'comando = f"Register-ScheduledTask -Xml $x -TaskName {nome}"',
    'comando = "Unregister-ScheduledTask -TaskName x"',
    'comando = "takeown /f C:/x /r"',
    'subprocess.run(["msiexec", "/i", "x.msi"])',
    'subprocess.run(["reg", "add", "HKLM\\Software\\X"])',
    "import winreg",
    "os.startfile(pasta)",
    "dono = ctypes.windll.advapi32",
    "subprocess.Popen(c, creationflags=0x8)",
    'comando = "New-LocalUser -Name x"',
    'comando = "Set-Service -Name sshd -StartupType Automatic"',
    'subprocess.run(["cmd", "/c", "start", "", "x"])',
    'comando = "New-ItemProperty -Path HKLM:\\Software -Name x"',
    'comando = "Get-CimInstance Win32_VideoController"',
    'comando = "Add-WindowsCapability -Online -Name x"',
    "kernel32 = ctypes.WinDLL('kernel32')",
    'os.system("dir")',
]


@pytest.mark.parametrize("linha", OUTROS_NOMES)
def test_k01_acusa_os_outros_nomes_da_mesma_conversa_com_o_windows(linha):
    """Achado 2 de quem tentou quebrar (19/11): o mesmo pedido ao Windows escrito com outra palavra passava.

    Cada um destes, num arquivo do programa, é acusado pela K01.
    """
    fonte = f'"""Um arquivo do programa."""\nimport ctypes\nimport os\nimport subprocess\n\n\ndef f(c, pasta, nome):\n' \
            f'    """Fala com o Windows."""\n    {linha}\n'
    assert codigos(conferir({"atualizacao.py": fonte}), "K01") == [("atualizacao.py", 9)], linha


def test_k01_nao_acusa_nome_parecido_que_nao_e_conversa_com_o_windows():
    """Variável chamada `cmd`, `kernel32` usada depois de pega, o nome de arquivo `vc_redist`, `servico` comum: não."""
    certo = py('''
        def f(cmd, kernel32, servico):
            """Nada de conversa nova com o Windows aqui."""
            VC = "vc_redist.x64.exe"
            subprocess.run(cmd, check=True)
            kernel32.CloseHandle(1)
            return servico.start()
    ''')
    assert codigos(conferir({"atualizacao.py": certo}), "K01") == []


def test_k02_acusa_o_numero_do_detached_process():
    """O DETACHED_PROCESS pelo número (0x8 ou 8, sozinho ou somado) também é o defeito 1."""
    for bandeira in ("0x8", "0x00000008", "8", "subprocess.CREATE_NEW_PROCESS_GROUP | 0x8"):
        fonte = f'def f(c):\n    """Lança."""\n    subprocess.Popen(c, creationflags={bandeira})\n'
        assert codigos(conferir({"atualizacao.py": fonte}), "K02") == [("atualizacao.py", 3)], bandeira
    certo = 'def f(c):\n    """Lança."""\n    subprocess.Popen(c, creationflags=0x08000000)\n'
    assert codigos(conferir({"atualizacao.py": certo}), "K02") == []


def test_k04_correcao_3_so_dentro_do_mesmo_texto_da_folha_de_estilo():
    """Achado 10 de quem tentou quebrar (19/11): um `"imagens/*"` num texto e um `"*/fim"` em outro apagavam o que
    ficava entre os dois. Agora o comentário só sai de dentro do mesmo texto, e só se ele tiver cara de folha de estilo."""
    tela = py('''
        def f():
            """Uma tela."""
            padrao = "imagens/*"
            QLabel("veja D-731")
            return "*/fim"
    ''')
    assert codigos(conferir({"ui/x.py": tela}), "K04") == [("ui/x.py", 4)]



# ---------------------------------------------------------------- segunda volta de quem quebrou (19/11)

@pytest.mark.parametrize("linha", [
    'subprocess.run(["sc", "create", "x"])', 'subprocess.run(["net", "stop", "x"])',
    'subprocess.run(["taskkill", "/F", "/PID", "1"])', 'x = "Stop-Process -Id 1"',
    'x = "New-Object -ComObject WScript.Shell"', 'x = "Get-PhysicalDisk"', 'k = ctypes.CDLL("kernel32")',
    "k = ctypes.cdll.kernel32", "subprocess.Popen(c, creationflags=bandeiras)",
    'subprocess.run(["shutdown", "/r"])', 'x = "Write-EventLog -LogName a"',
])
def test_k01_acusa_os_nomes_que_ainda_escapavam(linha):
    """Achado N3 da segunda volta: `sc create` em lista, `net stop`, `taskkill`, `Stop-Process`, `-ComObject`,
    `Get-PhysicalDisk`, `CDLL`/`cdll` com biblioteca do Windows e `creationflags` guardado numa variável (N2)."""
    fonte = f'"""Programa."""\nimport ctypes\nimport subprocess\n\n\ndef f(c, bandeiras):\n    """Fala."""\n    {linha}\n'
    assert codigos(conferir({"atualizacao.py": fonte}), "K01") == [("atualizacao.py", 8)], linha


def test_cada_palavra_da_busca_tem_exemplo_que_ela_acha_e_o_porteiro_tambem():
    """N3: cada linha da busca do Windows (e do DETACHED_PROCESS e da licença de pasta) traz um exemplo, a própria
    linha acha o exemplo e o porteiro de agora também (é o que a proteção cobra contra a versão de teste)."""
    import re

    from regras_dos_agentes import protecao

    for padrao, _o_que, exemplo in porteiro.PALAVRAS_DO_WINDOWS:
        assert re.search(padrao, exemplo, re.I), (padrao, exemplo)
    for padrao, exemplo in porteiro.PALAVRAS_DE_DETACHED + porteiro.PALAVRAS_DE_LICENCA:
        assert re.search(padrao, exemplo, re.I), (padrao, exemplo)
    fonte = (porteiro.__file__ and open(porteiro.__file__, encoding="utf-8").read())
    assert protecao.exemplos_que_o_porteiro_nao_acha(fonte) == []


def test_k01_falsos_alarmes_que_quem_quebrou_apontou_nao_sao_acusados():
    """Achado N5 da segunda volta: `creationflags=0`, "self-service" e "hku:" num texto comum não são conversa com o
    Windows."""
    certo = py('''
        def f(c):
            """Nada de Windows."""
            subprocess.run(c, creationflags=0)
            texto = "o self-service do restaurante"
            outro = "hku: abreviação qualquer"
            return texto, outro
    ''')
    assert codigos(conferir({"atualizacao.py": certo}), "K01") == []


def test_k01_segue_o_apelido_da_biblioteca_do_windows():
    """Achado N2 da segunda volta: a chamada feita pelo apelido (`kernel32.X`), a função que devolve a biblioteca e
    quem recebe o que ela devolve são acusados; o resultado de uma chamada feita pela biblioteca não vira apelido."""
    fonte = py('''
        """Programa."""
        import ctypes


        def _biblioteca():
            """Pega a biblioteca."""
            kernel32 = ctypes.WinDLL("kernel32")
            alca = kernel32.GetStdHandle(1)
            if alca:
                pass
            return kernel32, alca


        def usar():
            """Usa a biblioteca devolvida."""
            k32, entrada = _biblioteca()
            return k32.SetConsoleMode(entrada, 0)
    ''')
    linhas = [n for _, n in codigos(conferir({"atualizacao.py": fonte}), "K01")]
    assert linhas == [7, 8, 11, 16, 17], linhas


def test_k04_correcao_3_um_f_string_comum_com_chaves_nao_e_folha_de_estilo():
    """Achado N7 da segunda volta: `f"Arquivo {nome} salvo /* conforme D-731 */"` não é folha de estilo: o número é
    acusado. Na folha de estilo de verdade (um seletor do Qt seguido de "{" e de uma propriedade), o comentário sai."""
    errado = 'def f(nome):\n    """Tela."""\n    return f"Arquivo {nome} salvo /* conforme D-731 */"\n'
    assert codigos(conferir({"ui/x.py": errado}), "K04") == [("ui/x.py", 3)]
    folha = 'def f(c):\n    """Folha."""\n    return f"QWidget {{ color: red; }} /* etapa (D-015) */"\n'
    assert codigos(conferir({"ui/x.py": folha}), "K04") == []


# ---------------------------------------------------------------- terceira volta de quem quebrou (19/11)

def test_r5_o_resultado_de_uma_chamada_da_biblioteca_nao_e_apelido():
    """R5: a função que devolve o RESULTADO de uma chamada feita pela biblioteca (o caso do `_sozinho_no_console`, que
    devolve sim ou não) não "devolve a biblioteca", e quem a chama não é acusado (antes: `teste_velocidade.py:2317`)."""
    fonte = py('''
        """Programa."""
        import ctypes


        def _sozinho():
            """Sim ou não."""
            funcao = ctypes.windll.kernel32.GetConsoleProcessList
            return funcao(1, 2) == 1


        def despedir():
            """Usa o sim ou não."""
            if _sozinho():
                return 1
            return 0
    ''')
    assert [n for _, n in codigos(conferir({"atualizacao.py": fonte}), "K01")] == [7, 8]


def test_r5_a_marca_criada_pela_biblioteca_nao_e_apelido():
    """R5: `_MARCA = ctypes.windll.kernel32.CreateMutexW(...)` guarda o resultado, não a biblioteca; a linha que só
    pergunta se a marca existe não é acusada (antes: `atualizacao.py:748`)."""
    fonte = py('''
        """Programa."""
        import ctypes
        import sys

        _MARCA = None


        def marcar():
            """Cria a marca."""
            global _MARCA
            if _MARCA is not None or sys.platform != "win32":
                return
            _MARCA = ctypes.windll.kernel32.CreateMutexW(None, False, "x") or None
    ''')
    assert [n for _, n in codigos(conferir({"atualizacao.py": fonte}), "K01")] == [13]


def test_r5_o_segundo_nome_da_tupla_nao_e_apelido():
    """R5: `kernel32, entrada = f()`, quando `f` devolve a biblioteca só na primeira posição: só `kernel32` é apelido."""
    fonte = py('''
        """Programa."""
        import ctypes


        def _entrada():
            """A biblioteca e um número."""
            k = ctypes.WinDLL("kernel32")
            return k, 5


        def usar():
            """Usa."""
            kernel32, entrada = _entrada()
            total = entrada + 1
            return total
    ''')
    assert [n for _, n in codigos(conferir({"atualizacao.py": fonte}), "K01")] == [7, 8, 13]


def test_r5_o_metodo_de_mesmo_nome_em_outra_classe_nao_e_seguido():
    """R5: o método `abrir` de uma classe devolve a biblioteca; o `abrir` de outra classe, chamado por ela, não conta."""
    fonte = py('''
        """Programa."""
        import ctypes


        class A:
            """Uma."""

            def abrir(self):
                """Devolve a biblioteca."""
                return ctypes.WinDLL("kernel32")


        class B:
            """Outra."""

            def abrir(self):
                """Devolve um número."""
                return 1

            def usar(self):
                """Usa o abrir de B."""
                return self.abrir()
    ''')
    assert [n for _, n in codigos(conferir({"atualizacao.py": fonte}), "K01")] == [10]


@pytest.mark.parametrize("bandeira", [
    'getattr(subprocess, "CREATE_NO_WINDOW", 0)', "subprocess.CREATE_NO_WINDOW", "0x08000000",
    "_SEM_JANELA | (_PRIORIDADE_BAIXA if baixa else 0)", "_SEM_JANELA if os.name == \"nt\" else 0",
])
def test_r6_abrir_sem_janela_preta_nao_e_conversa_com_o_windows(bandeira):
    """R6: `creationflags` só para esconder a janela preta (e baixar a prioridade) não é conversa com o Windows, também
    guardado numa variável do arquivo (o caso dos motores de achar texto)."""
    fonte = ('"""Programa."""\nimport os\nimport subprocess\n\n_SEM_JANELA = 0x08000000\n_PRIORIDADE_BAIXA = 0x00004000\n'
             f'\n\ndef f(c, baixa):\n    """Abre."""\n    subprocess.Popen(c, creationflags={bandeira})\n')
    assert codigos(conferir({"core/ocr_x.py": fonte}), "K01") == [], bandeira


@pytest.mark.parametrize("bandeira", ['getattr(subprocess, "DETACHED_PROCESS", 0)', "subprocess.CREATE_NEW_CONSOLE",
                                      "0x00000010", "bandeiras_que_vem_de_fora"])
def test_r6_outra_bandeira_continua_sendo_conversa_com_o_windows(bandeira):
    """R6: o DETACHED_PROCESS, as outras bandeiras e o valor que não dá para ler continuam acusados."""
    fonte = ('"""Programa."""\nimport subprocess\n\n\ndef f(c, bandeiras_que_vem_de_fora):\n    """Abre."""\n'
             f'    subprocess.Popen(c, creationflags={bandeira})\n')
    assert codigos(conferir({"core/ocr_x.py": fonte}), "K01") == [("core/ocr_x.py", 7)], bandeira


# ---------------------------------------------------------------- quarta volta de quem quebrou (Q2, Q4)

def test_q2_todo_py_fora_das_pastas_de_fora_e_programa():
    """Achado Q2 (quarta volta, 19/11/2026): só core/, ui/ e a raiz eram programa; um `servicos/__init__.py` com
    `schtasks`, importado pelo `main.py`, passava. Agora todo `.py` conta, menos as pastas da lista `NAO_E_PROGRAMA`."""
    achados = conferir({"servicos/__init__.py": '"""Serviços."""\nCMD = ["schtasks", "/Run"]\n',
                        "tests/test_x.py": '"""Teste."""\nCMD = ["schtasks", "/Run"]\n'})
    assert [a for a, _ in codigos(achados, "K01")] == ["servicos/__init__.py"]
    assert porteiro.e_programa("servicos/__init__.py") and porteiro.e_programa("main.py")
    assert not any(porteiro.e_programa(p + "/x.py") for p in porteiro.NAO_E_PROGRAMA)
    assert sorted(codigos(conferir({"servicos/ação.py": "X = 1\n"}), "K08")) == [("servicos/ação.py", 0)]


def test_q4_codigo_compilado_sem_fonte_no_repositorio_e_acusado():
    """Achado Q4 (quarta volta, 19/11/2026): um `.pyc` guardado no repositório é importado pelo Python e o porteiro não
    o lê; passava calado. Agora vira K00 (que nunca entra na lista de exceções)."""
    achados = porteiro.conferir_codigo(["servicos/__pycache__/x.cpython-314.pyc", "core/y.pyo", "core/z.py"],
                                       lambda c: '"""Z."""\n' if c.endswith(".py") else None)
    assert sorted(a for a, _ in codigos(achados, "K00")) == ["core/y.pyo", "servicos/__pycache__/x.cpython-314.pyc"]


# ---------------------------------------------------------------- quinta volta de quem quebrou (S1, S2, S3)

def test_s1_nenhuma_pasta_de_fora_tem_o_nome_de_um_modulo_da_raiz():
    """Achado S1 (quinta volta, 19/11/2026): `historico/` estava entre as pastas que não são programa, mas o programa
    importa `historico` (o `historico.py` da raiz); um `historico/__init__.py` tomava o lugar dele e o porteiro não o
    lia. No repositório de hoje, nenhuma pasta de `NAO_E_PROGRAMA` tem o nome de um módulo da raiz."""
    from pathlib import Path

    from regras_dos_agentes import conversa_com_o_git as git

    caminhos = git.arquivos_do_git(Path(__file__).resolve().parent.parent)
    assert not porteiro.modulos_da_raiz(caminhos) & set(porteiro.NAO_E_PROGRAMA)
    assert porteiro.pastas_de_fora_com_nome_de_modulo(caminhos) == []


def test_s1_a_pasta_com_nome_de_modulo_e_lida_e_a_colisao_e_acusada():
    """S1: o `historico/__init__.py` com `schtasks` é lido como programa; e se uma pasta de fora voltar a ter o nome de
    um módulo da raiz (aqui, um `docs.py` solto), o porteiro acusa (K00, que nunca entra na lista)."""
    achados = conferir({"historico.py": '"""O histórico."""\n',
                        "historico/__init__.py": '"""Toma o lugar."""\nCMD = ["schtasks", "/Run"]\n'})
    assert [a for a, _ in codigos(achados, "K01")] == ["historico/__init__.py"]
    achados = conferir({"docs.py": '"""Um módulo com nome de pasta de fora."""\n'})
    assert [a for a, _ in codigos(achados, "K00")] == ["docs"]


def test_s2_o_pyw_e_lido_como_codigo():
    """Achado S2 (quinta volta, 19/11/2026): no Windows o Python importa `.pyw` como código-fonte, e o porteiro só lia
    `.py`; um `core/segredo.pyw` com `schtasks` passava."""
    achados = conferir({"core/segredo.pyw": '"""Escondido."""\nCMD = ["schtasks", "/Run"]\n'})
    assert [a for a, _ in codigos(achados, "K01")] == ["core/segredo.pyw"]
    assert porteiro.e_programa("core/segredo.pyw") and porteiro.e_script_python("segredo.pyw")


def test_s3_a_extensao_compilada_pyd_e_acusada():
    """Achado S3 (quinta volta, 19/11/2026): um `.pyd` (extensão compilada do Windows, que o Python importa) passava;
    agora vira K00 junto com o `.pyc` e o `.pyo`. A `.dll` do ScanTailor não entra (o Python não a importa)."""
    achados = porteiro.conferir_codigo(["core/x.cp314-win_amd64.pyd", "core/nativo/scantailor.dll"], lambda c: None)
    assert [a for a, _ in codigos(achados, "K00")] == ["core/x.cp314-win_amd64.pyd"]


# ---------------------------------------------------------------- K25 (D-809, 19/11/2026)
#
# D-809, pergunta 1 de 6 do catálogo dos erros (família F9): "ok, mas essas coisas foram recuperadas? e porque ele fez
# essa confusão se era regra ele não mexer? e tinha o porteiro para ele não fazer isso" · "ok". A prova pedida no
# Livro: "O porteiro barra um script com `git fetch --depth` ou `rm -rf` num atalho". E a da D-791: cada conferência
# acusa o exemplo errado e não acusa o certo.

ERRADO_K25_GIT = py('''
    """Um script de apoio que mexe na pasta .git inteira (o que a cópia do agente divide com o PC)."""
    import os
    import subprocess

    def buscar(raiz):
        """O juiz rodado à mão na cópia do agente (19/11)."""
        subprocess.run(["git", "fetch", "--depth=1", "origin", "obra-2026-10-26"], cwd=raiz)
        subprocess.run(["git", "-C", str(raiz), "gc"])
        subprocess.run("git stash", shell=True)
        os.system("git config core.hooksPath ganchos")
        cmd = ["git", "worktree", "prune"]
        return cmd
''')

CERTO_K25_GIT = py('''
    """Um script de apoio que só lê o git, ou trabalha numa pasta nova (git gc, git stash na docstring não contam)."""
    import subprocess

    def ler(raiz):
        """Só lê (git config --get, git stash list) e busca sem cortar a história."""
        subprocess.run(["git", "fetch", "origin", "obra-2026-10-26"], cwd=raiz)   # git fetch --depth=1 no comentário
        subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=raiz)
        subprocess.run(["git", "-c", "core.quotepath=false", "ls-files"], cwd=raiz)
        subprocess.run(["git", "stash", "list"], cwd=raiz)
        subprocess.run(["git", "clone", "--depth=1", "https://x/y.git", "pasta_nova"])
        exemplo = 'subprocess.run(["git", "gc"])'          # o exemplo errado escrito como dado (um teste) não conta
        return exemplo
''')


def test_k25_acusa_o_git_que_muda_a_pasta_git_inteira_num_script():
    """K25 (D-809): fetch com --depth, gc, stash, config e prune num script de apoio, cada linha acusada."""
    achados = conferir({"relatorios/x/script.py": ERRADO_K25_GIT})
    assert [n for _, n in codigos(achados, "K25")] == [7, 8, 9, 10, 11]
    assert all("fora das peças do git" in a.porque for a in achados if a.conferencia == "K25")


def test_k25_nao_acusa_o_git_que_so_le_nem_o_texto_solto():
    """K25 (D-791, o código certo não é acusado): busca sem cortar, config --get, `-c` de uma vez só, stash list, clone
    numa pasta nova, o comentário, a docstring e o exemplo escrito como dado."""
    assert codigos(conferir({"relatorios/x/script.py": CERTO_K25_GIT}), "K25") == []


@pytest.mark.parametrize("argumentos, grava", [
    ('"config", "core.hooksPath", "ganchos"', True), ('"config", "--global", "user.name", "x"', True),
    ('"config", "set", "core.x", "y"', True), ('"config", "--global", "--unset", "x"', True),
    ('"config", "--add", "x", "y"', True), ('"config", "-e"', True), ('"config", chave, valor', True),
    ('"config", "user.name"', False), ('"config", "get", "user.name"', False), ('"config", "--get", "x"', False),
    ('"config", "--get-regexp", "a", "b"', False), ('"config", "--list"', False), ('"config", "-l"', False),
    ('"config", "list", "--show-origin"', False), ('"config", chave', False), ('"-c", "core.x=y", "status"', False),
])
def test_k25_git_config_so_acusa_o_que_grava(argumentos, grava):
    """D-813 na K25 (todos os jeitos que a peça de fora aceita, https://git-scm.com/docs/git-config): o `git config`
    que grava é acusado (set, unset, --add, -e, nome e valor); o que só lê não é (get, list, --get, nome sem valor)."""
    texto = f'"""X."""\nimport subprocess\n\n\ndef f(chave, valor):\n    """F."""\n    subprocess.run(["git", {argumentos}])\n'
    assert bool(codigos(conferir({"relatorios/x/a.py": texto}), "K25")) is grava


def test_k25_vale_nos_testes_e_nao_vale_nas_duas_pecas_do_git():
    """K25 (D-809): "não roda na cópia, nem em script ou teste", "fora das peças de git que já existem
    (`conversa_com_o_git.py`, `repositorio_de_prova.py`)". As duas peças vêm escritas aqui, como na decisão (não lidas
    do porteiro: tirar a exceção de lá tem de fazer este teste falhar)."""
    assert codigos(conferir({"tests/test_x.py": ERRADO_K25_GIT}), "K25")
    assert codigos(conferir({"regras_dos_agentes/outro_arquivo.py": ERRADO_K25_GIT}), "K25")
    for peca in ("regras_dos_agentes/conversa_com_o_git.py", "regras_dos_agentes/repositorio_de_prova.py"):
        assert codigos(conferir({peca: ERRADO_K25_GIT}), "K25") == [], peca


# O script do juiz (passo 0), como foi rodado à mão em 19/11, e como ficou depois do conserto (`--depth=1` só quando a
# cópia já é rasa).
JUIZ_DE_ANTES = ('#!/usr/bin/env bash\nset -e\n'
                 'git fetch -q --depth=1 origin "+refs/heads/$VERSAO:refs/remotes/origin/$VERSAO"\n')
JUIZ_DE_HOJE = ('#!/usr/bin/env bash\nset -e\n# `--depth=1` só quando a cópia já é rasa\nPROFUNDIDADE=""\n'
                '[ "$(git rev-parse --is-shallow-repository)" = "true" ] && PROFUNDIDADE="--depth=1"\n'
                'git fetch -q $PROFUNDIDADE origin "+refs/heads/$VERSAO:refs/remotes/origin/$VERSAO"\n')


def test_k25_acusa_o_script_do_juiz_de_19_11_e_nao_o_consertado():
    """Caso que originou a D-809 (19/11/2026, o repositório do PC raso): o `git fetch --depth=1` fixo do script do
    juiz é acusado; o script consertado (a profundidade só numa cópia rasa) não é."""
    assert [n for _, n in codigos(conferir({"relatorios/x/porteiro_juiz.sh": JUIZ_DE_ANTES}), "K25")] == [3]
    assert codigos(conferir({"relatorios/x/porteiro_juiz.sh": JUIZ_DE_HOJE}), "K25") == []


def test_k25_le_o_gancho_sem_extensao_e_pula_o_comentario():
    """O gancho `ganchos/pre-commit` não tem extensão: é lido porque começa com "#!". O `git config` do comentário
    (como o de hoje) não conta; o mesmo comando como linha de verdade conta."""
    comentario = "#!/bin/sh\n#     git config core.hooksPath ganchos\nexec python -m regras_dos_agentes antes-do-commit\n"
    assert codigos(conferir({"ganchos/pre-commit": comentario}), "K25") == []
    assert codigos(conferir({"ganchos/pre-commit": comentario.replace("#     git", "git")}), "K25") == [
        ("ganchos/pre-commit", 2)]
    assert codigos(conferir({"ganchos/LEIAME": "#\ngit gc\n"}), "K25") == [], "sem extensão e sem #! não é script"


ERRADO_K25_APAGAR_PY = py('''
    """Um script que apaga uma pasta com tudo dentro sem conferir se ela é atalho (a junção de modelos/, 18/11)."""
    import subprocess

    def limpar(pasta):
        """Apaga a pasta de trabalho."""
        subprocess.run(["rm", "-rf", str(pasta)])
        subprocess.run(["powershell", "-Command", f"Remove-Item -LiteralPath {pasta} -Recurse -Force"])
''')

CERTO_K25_APAGAR_PY = py('''
    """O mesmo, conferindo antes se é atalho; e os jeitos que não entram no atalho."""
    import shutil
    import subprocess

    def limpar(pasta):
        """Atalho sai com cmd /c rmdir (só o atalho); pasta de verdade, com tudo dentro."""
        if pasta.is_junction():
            subprocess.run(["cmd", "/c", "rmdir", str(pasta)])
            return
        subprocess.run(["rm", "-rf", str(pasta)])

    def limpar_temporaria(pasta):
        """O shutil.rmtree do Python 3.14 não entra em atalho; apagar um arquivo só não é apagar pasta."""
        shutil.rmtree(pasta, ignore_errors=True)
        subprocess.run(["rm", "-f", str(pasta / "a.txt")])
        subprocess.run(["powershell", "-Command", f"Remove-Item -LiteralPath {pasta} -Force"])
''')


def test_k25_acusa_apagar_com_tudo_dentro_sem_conferir_o_atalho():
    """K25 (D-809): `rm -rf` e `Remove-Item -Recurse` sem conferir antes se é atalho, no Python e no terminal."""
    assert [n for _, n in codigos(conferir({"relatorios/x/a.py": ERRADO_K25_APAGAR_PY}), "K25")] == [6, 7]
    assert [n for _, n in codigos(conferir({"relatorios/x/a.sh": '#!/bin/sh\nrm -rf "$PASTA"\n'}), "K25")] == [2]
    # Cada exemplo vem depois de "$p = 'x'; " (o texto do teste não começa com o comando: senão o próprio teste seria
    # acusado, ver `leitura_do_codigo.comandos`, jeito 3).
    for linha in ("$p = 'x'; Remove-Item $p -Recurse -Force", "$p = 'x'; rm $p -r", "$p = 'x'; ri $p -Rec",
                  "$p = 'x'; Remove-Item -Recurse -LiteralPath $p"):
        assert codigos(conferir({"relatorios/x/a.ps1": linha + "\n"}), "K25") == [("relatorios/x/a.ps1", 1)], linha


def test_k25_nao_acusa_quem_confere_o_atalho_antes_nem_o_que_nao_entra_nele():
    """K25 (D-791, o certo não é acusado): conferiu antes se é atalho (`is_junction`, `LinkType`, `[ -L`); `cmd /c
    rmdir`; `shutil.rmtree`; apagar um arquivo; `-Force` sem `-Recurse`; o comentário."""
    assert codigos(conferir({"relatorios/x/a.py": CERTO_K25_APAGAR_PY}), "K25") == []
    sh = '#!/bin/sh\n# rm -rf "$PASTA" (comentário)\n[ -L "$PASTA" ] && exit 1\nrm -rf "$PASTA"\nrm -f "$ARQ"\n'
    assert codigos(conferir({"relatorios/x/a.sh": sh}), "K25") == []
    ps1 = 'if ((Get-Item $p).LinkType) { cmd /c rmdir $p } else { Remove-Item $p -Recurse -Force }\nrm $p -Force\n'
    assert codigos(conferir({"relatorios/x/a.ps1": ps1}), "K25") == []


def test_k25_cada_exemplo_da_lista_e_acusado_pela_expressao_e_pelo_porteiro():
    """Como a K01 (achado N3 do passo 0): cada linha das listas da K25 tem um exemplo que a própria expressão acha no
    comando lido e que o porteiro acusa num script; assim afrouxar a busca sem tirar linha também aparece."""
    for padrao, o_que, exemplo in porteiro.PALAVRAS_DO_GIT + porteiro.PALAVRAS_DE_APAGAR:
        texto = f'"""Exemplo."""\nimport os\nimport subprocess\n\n\ndef f(raiz, pasta):\n    """F."""\n    {exemplo}\n'
        comandos = porteiro.leitura.comandos(porteiro.leitura.arvore(texto))
        assert any(re.search(padrao, c) for _, c in comandos), o_que
        assert codigos(conferir({"relatorios/x/a.py": texto}), "K25") == [("relatorios/x/a.py", 8)], o_que
