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
    """K04 não acusa comentário, docstring nem arquivo cujo texto o Kaique não vê (`core/filtros.py`)."""
    certo = 'def f():\n    """Ver D-068."""\n    # D-094\n    return 1\n'
    assert codigos(conferir({"ui/automatico.py": certo}), "K04") == []
    assert codigos(conferir({"core/filtros.py": 'X = "D-068"\n'}), "K04") == []


# ---------------------------------------------------------------- K05 a K08

def test_k05_acusa_emoji_na_tela_e_nao_acusa_seta_nem_fora_da_tela():
    """K05 acusa um emoji num texto da tela; a seta comum e o texto de `core/` não."""
    rosto, seta = chr(0x1F600), chr(0x2192)
    assert codigos(conferir({"ui/tela.py": f'R = "Pronto {rosto}"\n'}), "K05") == [("ui/tela.py", 1)]
    assert codigos(conferir({"ui/tela.py": f'R = "Próxima {seta}"\n'}), "K05") == []
    assert codigos(conferir({"core/x.py": f'R = "{rosto}"\n'}), "K05") == []


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
    """As 24 conferências, K01 a K24, cada uma com a regra e o tipo (vale a numeração da tabela, plano-v3)."""
    assert [c.codigo for c in porteiro.CONFERENCIAS] == [f"K{n:02d}" for n in range(1, 25)]
    assert porteiro.POR_CODIGO["K05"].o_que.startswith("emoji")
    assert porteiro.POR_CODIGO["K08"].o_que.startswith("nome de arquivo com acento")
    assert all(c.tipo in ("codigo", "entrega") and c.regra for c in porteiro.CONFERENCIAS)
