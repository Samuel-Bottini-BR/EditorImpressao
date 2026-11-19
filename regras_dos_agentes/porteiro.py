"""O porteiro (D-791): as 24 conferências automáticas e as que leem o código parado.

As 24 conferências são as da proposta das regras dos agentes (ramo `regras-agentes-2026-11-18`, `proposta.md` §5.1),
**com a numeração da tabela de lá** (o esboço `conferir_codigo.py` numerava diferente; vale a tabela, plano-v3 passo 0).
A lista `CONFERENCIAS` abaixo é o lugar único dessa numeração: os testes, a lista de exceções e o formulário leem daqui.

Dois tipos:
- **as que leem o código parado** (este arquivo): K01 a K08, K16, K22, K23, K24. Rodam no GitHub em toda entrega
  (`tests/test_conferencias_codigo.py`) e antes do commit, só nos arquivos mudados
  (`python -m regras_dos_agentes antes-do-commit`, chamado por `ganchos/pre-commit`).
- **as que olham o que a entrega mudou** (`porteiro_mudancas.py` e `formulario.py`): K09 a K15, K17 a K21. Precisam do
  commit de partida e do papel do agente, que vêm do pedido; rodam quando a entrega é conferida.

O que já está errado hoje no código fica na lista de exceções (`excecoes.py`), um item por lugar, e só ali.
Nenhuma conferência tem exceção própria escrita no código: nem por arquivo, nem por caso.

Onde cada busca olha (o "programa"): os `.py` de `core/`, de `ui/` e da raiz. O pacote `regras_dos_agentes/`, os
testes e os scripts de outras pastas não são programa (o próprio porteiro tem as palavras que procura escritas como
dado). A K16 e a K24 olham também os scripts de teste e de apoio, e leem a estrutura do código (a importação e a
chamada de verdade), não o texto.

Seguro mexer: o texto de `porque`; acrescentar uma palavra a uma busca **com** o exemplo errado e o certo no teste.
Arriscado: tirar palavra de uma busca, mudar o que conta como "programa" (`e_programa`), ou mudar o que conta como
"texto achado" (`_texto_do_lugar`): a lista de exceções guarda esse texto, e mudá-lo invalida a lista inteira.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Callable, Iterable

from . import conversa_com_o_git as git
from . import leitura_do_codigo as leitura


@dataclass(frozen=True)
class Conferencia:
    """Uma das 24 conferências: o número da tabela da proposta, a regra que ela cobra e o que ela confere."""

    codigo: str
    regra: str
    o_que: str
    tipo: str            # "codigo" (lê o código parado) | "entrega" (olha o que a entrega mudou)
    nao_pega: str


CONFERENCIAS: list[Conferencia] = [
    Conferencia("K01", "R113", "conversa com o Windows fora da peça única (ShellExecute, runas, schtasks, icacls, "
                "powershell, Update.exe, netsh...), nos textos e nos nomes do código", "codigo",
                "chamada disfarçada (texto montado em pedaços); uma segunda peça com outro nome"),
    Conferencia("K02", "R113, D-774", "DETACHED_PROCESS em qualquer lugar do programa (o PowerShell lançado assim sai "
                "sem rodar: defeito 1 da etapa 5)", "codigo", "outro jeito de lançar que também falha"),
    Conferencia("K03", "R113, plano peça 2", "comando de licença de pasta à mão (icacls, /inheritance:r, /setowner, "
                "Set-Acl: defeito 4 da etapa 5)", "codigo", "licença mudada por outra função do Windows"),
    Conferencia("K04", "R120, Lista de bugs 17/11", "número de decisão (D-123) em texto que a pessoa vê (tela, avisos, "
                "passos e registro dos testes à distância e do atualizador)", "codigo",
                "número escrito de outro jeito (\"decisão 731\")"),
    Conferencia("K05", "R019", "emoji em texto de tela", "codigo", "emoji que chega por arquivo de dados"),
    Conferencia("K06", "R049", "core/ importa ui/", "codigo", "importação feita por texto (importlib)"),
    Conferencia("K07", "R015", "tkinter ou customtkinter", "codigo", "—"),
    Conferencia("K08", "R020", "nome de arquivo com acento no programa (core/, ui/, raiz)", "codigo",
                "caminho com acento que o programa monta ao rodar"),
    Conferencia("K09", "R014", "relatório só em .md (falta o .html ou o .pdf ao lado)", "entrega",
                "relatório gravado fora da pasta do trabalho"),
    Conferencia("K10", "R031, D-798", "\"APROVADO\" escrito por agente; [x] posto no plano ou no Livro; o rótulo "
                "\"PRONTO PARA CONFERIR\" escrito no ramo de quem construiu", "entrega",
                "aprovação dita com outras palavras"),
    Conferencia("K11", "R102, D-605", "teste antigo mudado ou apagado (sem o commit citar a decisão que autoriza)",
                "entrega", "teste antigo enfraquecido por fora (uma ajuda que ele usa mudou)"),
    Conferencia("K12", "R076", "função ou arquivo tocado sem docstring (só as funções mudadas)", "entrega",
                "docstring vazia de sentido"),
    Conferencia("K13", "R071, D-796", "mexeu fora do papel: implementador em ui/, agente de tela em core/, verificador "
                "ou pesquisador no programa, fora da lista de arquivos do pedido", "entrega", "—"),
    Conferencia("K14", "camada 2", "mexeu em arquivo fora da lista do pedido (avisa, não barra)", "entrega", "—"),
    Conferencia("K15", "R048", "requirements.txt mudou sem o \"sim\" citado no commit", "entrega",
                "biblioteca instalada à mão no .venv"),
    Conferencia("K16", "R022", "biblioteca que desenha ou inventa (diffusers, realesrgan, gfpgan...)", "codigo",
                "biblioteca nova que não está na lista"),
    Conferencia("K17", "R056, R094", "agente mexeu no CLAUDE.md, nos agentes, no Livro, no plano, no handoff ou "
                "acrescentou item na lista de exceções", "entrega", "—"),
    Conferencia("K18", "R136", "terminar com mudança sem commit ou sem push", "entrega", "—"),
    Conferencia("K19", "R096, R104, R115, R118", "o formulário da entrega", "entrega", "se a resposta é verdadeira"),
    Conferencia("K20", "R013, R096", "as palavras do Samuel citadas batem com o Livro, letra por letra", "entrega",
                "palavras certas na decisão errada"),
    Conferencia("K21", "R034", "a rodada do GitHub existe, é do último commit do ramo e passou", "entrega", "—"),
    Conferencia("K22", "R069", "a barra de rolagem continua cinza (os valores de hoje de ui/estilo.py)", "codigo", "—"),
    Conferencia("K23", "R106, R090, D-793", "agente não abre agente nem grava na Central (a lista de ferramentas de "
                "cada arquivo em .claude/agents/)", "codigo", "—"),
    Conferencia("K24", "R142", "pywinauto com click_input ou send_keys (tomam o mouse e o teclado do Samuel)",
                "codigo", "—"),
]
POR_CODIGO = {c.codigo: c for c in CONFERENCIAS}


@dataclass(frozen=True)
class Achado:
    """Um lugar que o porteiro acusou.

    `texto` é o texto do lugar (a linha de código sem comentário, sem espaço sobrando): é a chave da lista de
    exceções, junto com o arquivo e a conferência. O número da linha só serve para achar o lugar (muda quando se
    escreve acima dele; o texto não).
    """

    conferencia: str
    arquivo: str
    linha: int
    texto: str
    porque: str
    funcao: str = ""
    barra: bool = True     # False = só avisa (K14)


# ----------------------------------------------------------------------------------------------------------------
# Onde cada busca olha
# ----------------------------------------------------------------------------------------------------------------

PECA_UNICA_DO_WINDOWS = "core/windows.py"   # o único lugar onde a conversa com o Windows é permitida (plano, peça 1)


def e_programa(caminho: str) -> bool:
    """Um `.py` do programa: de `core/`, de `ui/` (com as subpastas) ou da raiz."""
    if not caminho.endswith(".py"):
        return False
    partes = caminho.split("/")
    return len(partes) == 1 or partes[0] in ("core", "ui")


def e_texto_que_a_pessoa_ve(caminho: str) -> bool:
    """Arquivo cujos textos o Kaique vê: a tela, o processamento (os avisos do "Para revisar" moram em `core/`, achado
    9 de quem tentou quebrar), o começo do programa e o atualizador."""
    return e_programa(caminho) and (caminho.startswith(("ui/", "core/")) or caminho in ("main.py", "atualizacao.py"))


def e_tela(caminho: str) -> bool:
    """Arquivo com texto de tela: `ui/`, o `main.py` e `core/` (os avisos que a tela mostra moram lá, achado 9)."""
    return e_programa(caminho) and (caminho.startswith(("ui/", "core/")) or caminho == "main.py")


# As pastas que não são do projeto para o porteiro: o código de fora e o guardado. Lugar único (achado 13).
FORA_DO_PROJETO = ("terceiros", "velhos")


def e_script_python(caminho: str) -> bool:
    """Todo `.py` do projeto, menos o código de fora (`terceiros/`) e o guardado (`velhos/`)."""
    return caminho.endswith(".py") and caminho.split("/")[0] not in FORA_DO_PROJETO


# ----------------------------------------------------------------------------------------------------------------
# As buscas
# ----------------------------------------------------------------------------------------------------------------

# K01 (correção 1 do plano-v3, ampliada em 19/11 com as duas voltas de quem tentou quebrar): as palavras sem exigir
# aspas, e os nomes do código. `\b` evita pegar nome de função que só contém a palavra (`_caminho_do_powershell` não é
# conversa com o Windows; `"powershell.exe"` é). É a lista única do que é "conversa com o Windows" no pacote: a tabela
# de etiquetas (`tabela_arquivos.py`) usa a mesma.
# Cada linha é (expressão, o que é, uma linha de código de exemplo que ela tem de achar). O exemplo existe para a
# proteção (achado N3 da segunda volta): o teste do GitHub pega o exemplo de cada linha da lista da versão de teste e
# cobra que o porteiro do ramo ainda o acha. Assim afrouxar a busca pelo jeito de juntar as palavras, sem tirar
# palavra nenhuma, também é pego. Um teste cobra que cada exemplo é achado pela própria expressão.
# PROTEGIDA: nenhuma linha sai e nenhum exemplo deixa de ser achado sem a gerente. Acrescentar linha é seguro.
# Fontes: os módulos do PowerShell (ScheduledTasks, NetSecurity, LocalAccounts, Storage, Microsoft.PowerShell.Security,
# Microsoft.PowerShell.Management), https://learn.microsoft.com/powershell/module/scheduledtasks/ e
# https://learn.microsoft.com/powershell/module/microsoft.powershell.management/; o `winreg` e o `os.startfile` da
# biblioteca do Python (https://docs.python.org/3/library/winreg.html,
# https://docs.python.org/3/library/os.html#os.startfile); o `ctypes` (https://docs.python.org/3/library/ctypes.html,
# `windll`, `WinDLL`, `oledll`, `cdll`, `CDLL`); os programas do Windows de linha de comando (sc, net, taskkill, reg,
# msiexec, shutdown), https://learn.microsoft.com/windows-server/administration/windows-commands/windows-commands.
_SEP = r"""\b["']?(?:\s*,\s*["']|\s+)"""      # "programa subcomando" ou ["programa", "subcomando"]
_DLL_DO_WINDOWS = r"(?:kernel32|advapi32|shell32|user32|psapi|ntdll|ole32|oleaut32|netapi32|wtsapi32|userenv|secur32)"
PALAVRAS_DO_WINDOWS: list[tuple[str, str, str]] = [
    # O PowerShell, com qualquer nome.
    (r"\bpowershell\b", "o PowerShell", 'subprocess.run(["powershell.exe", "-Command", "x"])'),
    (r"\bpwsh\b", "o PowerShell 7", 'subprocess.run(["pwsh", "-Command", "x"])'),
    (r"-ExecutionPolicy\b", "a permissão de rodar scripts do PowerShell", 'x = "-ExecutionPolicy Bypass"'),
    # Abrir programa ou arquivo pelo Windows.
    (r"ShellExecute", "abrir programa pelo ShellExecute", "ctypes.windll.shell32.ShellExecuteExW(info)"),
    (r"\bos\.startfile\b", "abrir arquivo ou programa pelo ShellExecute (os.startfile)", "os.startfile(pasta)"),
    (r"\bos\.system\b", "rodar um comando pelo cmd (os.system)", 'os.system("dir")'),
    (r"\bos\.popen\b", "rodar um comando pelo cmd (os.popen)", 'os.popen("dir")'),
    (r"\bcmd(?:\.exe)?" + _SEP + r"/[cCkK]\b", "rodar um comando pelo cmd", 'subprocess.run(["cmd", "/c", "start", "x"])'),
    (r"\brunas\b", "pedir licença de administrador", 'info.lpVerb = "runas"'),
    (r"\b(?:Start|Stop|Wait|Debug)-Process\b", "abrir ou fechar programa pelo PowerShell", 'x = "Start-Process -FilePath a"'),
    (r"\btaskkill\b", "fechar programa à força", 'subprocess.run(["taskkill", "/F", "/PID", "1"])'),
    # Tarefas do Windows, por qualquer meio.
    (r"\bschtasks\b", "tarefas do Windows", 'subprocess.run(["schtasks", "/Run", "/TN", "x"])'),
    (r"-(?:Clustered)?ScheduledTask\w*\b", "tarefas do Windows pelo PowerShell", 'x = "Register-ScheduledTask -Xml a"'),
    (r"Schedule\.Service", "tarefas do Windows pelo COM", 'x = "New-Object -ComObject Schedule.Service"'),
    (r"-ComObject\b", "um programa do Windows pelo COM", 'x = "New-Object -ComObject WScript.Shell"'),
    # Licença e dono de pastas e arquivos.
    (r"\bicacls\b", "licença de pasta (icacls)", 'x = "icacls C:/a /grant x"'),
    (r"\bcacls\b", "licença de pasta (cacls)", 'x = "cacls C:/a"'),
    (r"\btakeown\b", "tomar o dono de pasta", 'x = "takeown /f C:/a"'),
    (r"\b(?:Get|Set)-Acl\b", "licença de pasta pelo PowerShell", 'x = "Set-Acl -Path a"'),
    (r"/inheritance", "licença de pasta (herança)", 'x = "/inheritance:r"'),
    (r"/setowner", "dono de pasta", 'x = "/setowner a"'),
    (r"Set(?:Named)?SecurityInfo|SetFileSecurity", "licença de pasta pelo ctypes", "advapi32.SetNamedSecurityInfoW(a)"),
    # O registro do Windows.
    (r"\bwinreg\b|\b_winreg\b", "o registro do Windows (winreg)", "import winreg"),
    (r"\breg(?:\.exe)?" + _SEP + r"(?:add|delete|query|import|export|copy)\b", "o registro do Windows (reg)",
     'subprocess.run(["reg", "add", "x"])'),
    (r"(?-i:\bHK(?:LM|CU|CR|U|CC)(?::|\\))|(?-i:\bHKEY_[A-Z_]+)|Registry::", "o registro do Windows (o caminho)",
     r'x = "HKLM:\Software\X"'),
    (r"-ItemProperty\b", "o registro do Windows pelo PowerShell", 'x = "New-ItemProperty -Path a -Name b"'),
    (r"\bregedit\b", "o registro do Windows (regedit)", 'x = "regedit /s a.reg"'),
    # Instaladores.
    (r"\bmsiexec\b", "o instalador do Windows", 'subprocess.run(["msiexec", "/i", "a.msi"])'),
    (r"\bUpdate\.exe\b", "o atualizador do Velopack", 'x = pasta / "Update.exe"'),
    # O firewall e a rede.
    (r"\bnetsh\b", "o firewall e a rede (netsh)", 'x = "netsh advfirewall set"'),
    (r"-NetFirewall\w*\b", "o firewall pelo PowerShell", 'x = "New-NetFirewallRule -Name a"'),
    # Serviços.
    (r"\bsc(?:\.exe)?" + _SEP + r"(?:create|delete|config|start|stop|query|failure)\b", "serviços do Windows (sc)",
     'subprocess.run(["sc", "create", "x"])'),
    (r"\bsc\.exe\b", "serviços do Windows (sc.exe)", 'x = "sc.exe"'),
    (r"\b(?:Get|Set|Start|Stop|Restart|New|Remove|Suspend|Resume)-Service\b", "serviços do Windows pelo PowerShell",
     'x = "Set-Service -Name sshd"'),
    # Contas e o computador.
    (r"-Local(?:User|Group\w*)\b", "contas do Windows pelo PowerShell", 'x = "New-LocalUser -Name a"'),
    (r"\bnet(?:\.exe)?" + _SEP + r"(?:user|localgroup|stop|start|share|use|accounts)\b", "contas e serviços (net)",
     'subprocess.run(["net", "stop", "x"])'),
    (r"\b(?:Restart|Stop)-Computer\b|\bshutdown(?:\.exe)?" + _SEP + r"/", "desligar ou reiniciar o computador",
     'subprocess.run(["shutdown", "/r"])'),
    # Recursos, discos e o que o Windows sabe.
    (r"-WindowsCapability\b|-WindowsOptionalFeature\b|\bdism(?:\.exe)?\b", "recursos do Windows",
     'x = "Add-WindowsCapability -Online -Name a"'),
    (r"-(?:PhysicalDisk|Disk|Volume|Partition)\b", "os discos pelo PowerShell", 'x = "Get-PhysicalDisk"'),
    (r"-CimInstance\b|Invoke-CimMethod|-WmiObject\b|\bwmic\b", "ler ou mudar o Windows pelo WMI",
     'x = "Get-CimInstance Win32_VideoController"'),
    (r"\bwin32com\b|\bcomtypes\b|\bpythoncom\b", "o COM pelo Python", "import win32com.client"),
    (r"\bwin32api\b|\bwin32con\b|\bwin32process\b|\bwin32security\b|\bwin32service\b|\bpywintypes\b",
     "o pywin32", "import win32api"),
    (r"-WinEvent\b|-EventLog\b|\bwevtutil\b|\beventcreate\b", "o registro de eventos do Windows",
     'x = "Write-EventLog -LogName a"'),
    (r"-MpPreference\b|\bbcdedit\b|\brundll32\b|\bmshta\b", "outras configurações do Windows",
     'subprocess.run(["rundll32", "a.dll"])'),
    # As bibliotecas do Windows pelo ctypes (o lugar onde a biblioteca é pega; o uso dela pelo apelido é seguido
    # pela K01 também, ver `_apelidos_do_windows`).
    (r"\bwindll\b|\bWinDLL\b|\boledll\b", "funções do Windows pelo ctypes", "k = ctypes.windll.kernel32"),
    (r"\bcdll\." + _DLL_DO_WINDOWS + r"\b|\bCDLL\(\s*[\"']" + _DLL_DO_WINDOWS, "funções do Windows pelo ctypes (CDLL)",
     'k = ctypes.CDLL("kernel32")'),
    # Lançar processo com bandeira do Windows (qualquer valor que não seja o 0 literal: guardada numa variável
    # também conta, achado N2).
    (r"\bDETACHED_PROCESS\b", "lançar processo solto do Windows", "f = subprocess.DETACHED_PROCESS"),
    (r"\bcreationflags\s*=\s*(?!0(?![\w.x]))[\w(]", "lançar processo com bandeira do Windows",
     "subprocess.Popen(c, creationflags=bandeiras)"),
]
CONVERSA_COM_O_WINDOWS = re.compile("|".join(f"(?:{p})" for p, _, _ in PALAVRAS_DO_WINDOWS), re.I)

# K02: o DETACHED_PROCESS pelo nome ou pelo número (0x8 = 8), na bandeira de lançar processo. PROTEGIDA.
# (padrão, exemplo que ele tem de achar).
PALAVRAS_DE_DETACHED: list[tuple[str, str]] = [
    (r"\bDETACHED_PROCESS\b", "f = subprocess.DETACHED_PROCESS"),
    (r"\bcreationflags\s*=\s*[^,)\n]*?(?<![\w.])(?:0x0*8|8)(?![\w.])", "subprocess.Popen(c, creationflags=0x8)"),
]
DETACHED = re.compile("|".join(f"(?:{p})" for p, _ in PALAVRAS_DE_DETACHED))
# K03: licença de pasta mudada à mão. PROTEGIDA. (padrão, exemplo que ele tem de achar).
PALAVRAS_DE_LICENCA: list[tuple[str, str]] = [
    (r"\bicacls\b", 'x = "icacls a /grant b"'), (r"\bcacls\b", 'x = "cacls a"'), (r"\btakeown\b", 'x = "takeown /f a"'),
    (r"/inheritance:r", 'x = "/inheritance:r"'), (r"/setowner", 'x = "/setowner a"'),
    (r"\bSet-Acl\b", 'x = "Set-Acl -Path a"'), (r"Set(?:Named)?SecurityInfo", "advapi32.SetNamedSecurityInfoW(a)"),
    (r"SetFileSecurity", "advapi32.SetFileSecurityW(a)"),
]
LICENCA_A_MAO = re.compile("|".join(f"(?:{p})" for p, _ in PALAVRAS_DE_LICENCA), re.I)
# K04 e K05: PROTEGIDAS.
PADRAO_DO_NUMERO_DE_DECISAO = r"\bD-\d{3,}\b"
NUMERO_DE_DECISAO = re.compile(PADRAO_DO_NUMERO_DE_DECISAO)
PADRAO_DO_EMOJI = "[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF\u2600-\u27BF\u2B00-\u2BFF\uFE0F]"
EMOJI = re.compile(PADRAO_DO_EMOJI)
# K16 e K23: PROTEGIDAS (nada sai sem a gerente).
GERADORES = {"diffusers", "realesrgan", "gfpgan", "basicsr", "codeformer", "facexlib", "lama_cleaner", "iopaint",
             "invokeai", "stable_diffusion", "controlnet_aux", "kandinsky"}
PADRAO_DAS_FERRAMENTAS_PROIBIDAS = r"^(Agent|Task)$|Artifact"
FERRAMENTAS_PROIBIDAS_AOS_AGENTES = re.compile(PADRAO_DAS_FERRAMENTAS_PROIBIDAS, re.I)

# K22: os valores de hoje da barra de rolagem, um por tema (ui/estilo.py, 19/11/2026). São cinza; o #a8a49e do
# CLAUDE.md §9 é de antes dos temas. Mudar exige decisão do Samuel (CLAUDE.md §9): então muda aqui junto.
BARRA_DE_ROLAGEM = {"escuro": "#4A4D54", "cinza": "#6A6A6A", "claro": "#B5B3AC"}

# Os dados das buscas que agente nenhum afrouxa: o teste do GitHub (`tests/test_conferencias_protecao.py`, pela
# `protecao.py`) compara cada um com o da versão de teste; nenhum item pode sumir nem mudar (achado 6 de quem tentou
# quebrar, 19/11). Só acrescentar é livre. Cada nome aqui é uma atribuição de valor literal neste arquivo.
PROTEGIDAS = ("PALAVRAS_DO_WINDOWS", "PALAVRAS_DE_DETACHED", "PALAVRAS_DE_LICENCA", "PADRAO_DO_NUMERO_DE_DECISAO",
              "PADRAO_DO_EMOJI", "GERADORES", "PADRAO_DAS_FERRAMENTAS_PROIBIDAS", "BARRA_DE_ROLAGEM",
              "PECA_UNICA_DO_WINDOWS", "FORA_DO_PROJETO")


def _texto_do_lugar(linha_de_codigo: str) -> str:
    """O texto que identifica o lugar: a linha de código sem comentário, com os espaços juntados."""
    return " ".join(linha_de_codigo.split())


@dataclass
class _Arquivo:
    """Um arquivo lido uma vez só para todas as buscas (o texto, as linhas de código e a árvore)."""

    caminho: str
    fonte: str
    _codigo: list[str] | None = None
    _arvore: ast.Module | None = None
    erro: str = ""
    _lido: bool = False
    _funcoes: list | None = None

    def ler(self) -> bool:
        """Lê o código uma vez; devolve False (e guarda o erro) se não for Python válido."""
        if not self._lido:
            self._lido = True
            try:
                self._arvore = leitura.arvore(self.fonte)
                self._codigo = leitura.linhas_de_codigo(self.fonte)
            except leitura.CodigoIlegivel as e:
                self.erro = str(e)
        return not self.erro

    @property
    def codigo(self) -> list[str]:
        """As linhas de código (sem comentário nem docstring); vazio se o arquivo não foi lido."""
        return self._codigo or []

    @property
    def raiz(self) -> ast.Module:
        """A árvore do código (só depois de `ler()` dar certo)."""
        return self._arvore  # type: ignore[return-value]

    def funcao(self, linha: int) -> str:
        """O nome da função mais de dentro que contém a linha ("" fora de função), calculado uma vez por arquivo."""
        if self._funcoes is None:
            self._funcoes = sorted(leitura.funcoes(self.raiz), key=lambda f: f.fim - f.inicio)
        return next((f.nome for f in self._funcoes if f.inicio <= linha <= f.fim), "")


def _por_linha(arq: _Arquivo, k: str, padrao: re.Pattern, porque: str, linhas: list[str] | None = None) -> list[Achado]:
    """Um achado por linha de código onde a busca acha alguma coisa (no máximo um por linha e por conferência)."""
    saida = []
    for n, linha in enumerate(linhas if linhas is not None else arq.codigo, 1):
        m = padrao.search(linha)
        if m:
            saida.append(Achado(k, arq.caminho, n, _texto_do_lugar(arq.codigo[n - 1]),
                                f"{porque}: {m.group(0)}", arq.funcao(n)))
    return saida


# Onde a biblioteca do Windows é pega pelo ctypes: as duas linhas de PALAVRAS_DO_WINDOWS que tratam disso.
PEGA_A_BIBLIOTECA = re.compile("|".join(f"(?:{p})" for p, o_que, _ in PALAVRAS_DO_WINDOWS
                                        if o_que.startswith("funções do Windows pelo ctypes")), re.I)


def _escopos(nome_da_funcao: str) -> list[str]:
    """A função e as de fora dela, até o arquivo ("a.b.c" → ["a.b.c", "a.b", "a", ""])."""
    partes = nome_da_funcao.split(".") if nome_da_funcao else []
    return [".".join(partes[:n]) for n in range(len(partes), -1, -1)]


def _apelidos_do_windows(arq: _Arquivo) -> dict[int, str]:
    """As linhas que usam a biblioteca do Windows por um apelido (achado N2 da segunda volta de quem quebrou).

    Segue o apelido dentro do arquivo: (1) o nome que recebe a biblioteca (`kernel32 = ctypes.WinDLL("kernel32")`,
    `funcao = ctypes.windll.kernel32.SetThreadExecutionState`); (2) a função que devolve um apelido (`return kernel32,
    ...`, inclusive dentro de um `lambda`) e o nome que recebe o que ela devolve (`kernel32, entrada =
    _entrada_da_janela_preta()`: os dois nomes, por cautela), até não mudar mais; (3) toda linha que usa um desses
    nomes, na mesma função ou dentro dela, e toda chamada de uma função que devolve a biblioteca. O resultado de uma
    chamada feita PELA biblioteca (`alca = kernel32.OpenProcess(...)`) não vira apelido. Devolve linha → o nome usado.
    Não segue: o apelido que vai para outro arquivo (importado), nem o que passa por um dicionário ou um atributo
    (`self.k = ...`); isso fica nas ressalvas.
    """
    if not PEGA_A_BIBLIOTECA.search("\n".join(arq.codigo)):
        return {}
    apelidos: dict[str, set[str]] = {}            # escopo (função) → nomes
    devolve: set[str] = set()                     # funções que devolvem a biblioteca

    def e_apelido(nome: str, linha: int) -> bool:
        return any(nome in apelidos.get(e, set()) for e in _escopos(arq.funcao(linha)))

    def e_a_biblioteca(valor: ast.AST, linha: int) -> bool:
        """O valor É a biblioteca (ou uma função dela), e não o resultado de uma chamada feita por ela: um apelido, um
        atributo de um apelido (`kernel32.SetThreadExecutionState`), a chamada de uma função que devolve a biblioteca,
        ou uma tupla com um desses."""
        if isinstance(valor, ast.Name):
            return e_apelido(valor.id, linha)
        if isinstance(valor, ast.Attribute):
            return e_a_biblioteca(valor.value, linha)
        if isinstance(valor, ast.Call):
            f = valor.func
            return (f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else "") in devolve
        if isinstance(valor, (ast.Tuple, ast.List)):
            return any(e_a_biblioteca(e, linha) for e in valor.elts)
        return False

    def alvos(no: ast.AST) -> list[str]:
        nos = [no.target] if isinstance(no, ast.AnnAssign) else list(no.targets)
        return [n.id for alvo in nos for n in ast.walk(alvo) if isinstance(n, ast.Name)]

    atribuicoes = [n for n in ast.walk(arq.raiz) if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None]
    funcoes = [n for n in ast.walk(arq.raiz) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    mudou = True
    while mudou:
        mudou = False
        for no in atribuicoes:
            linhas = arq.codigo[no.lineno - 1:(no.end_lineno or no.lineno)]
            if PEGA_A_BIBLIOTECA.search(" ".join(linhas)) or e_a_biblioteca(no.value, no.lineno):
                escopo = arq.funcao(no.lineno)
                novos = set(alvos(no)) - apelidos.get(escopo, set())
                if novos:
                    apelidos.setdefault(escopo, set()).update(novos)
                    mudou = True
        for f in funcoes:
            if f.name in devolve:
                continue
            for r in ast.walk(f):
                if isinstance(r, ast.Return) and r.value is not None and any(
                        isinstance(n, ast.Name) and e_apelido(n.id, r.lineno) for n in ast.walk(r.value)):
                    devolve.add(f.name)
                    mudou = True
                    break
    usadas: dict[int, str] = {}
    for n in ast.walk(arq.raiz):
        if isinstance(n, ast.Name) and e_apelido(n.id, n.lineno):
            usadas.setdefault(n.lineno, n.id)
        elif isinstance(n, ast.Call):
            nome = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else ""
            if nome in devolve:
                usadas.setdefault(n.lineno, nome)
    return usadas


def k01(arq: _Arquivo) -> list[Achado]:
    """K01: conversa com o Windows fora da peça única: as palavras da lista e o uso da biblioteca do Windows pelo apelido."""
    if not e_programa(arq.caminho) or arq.caminho == PECA_UNICA_DO_WINDOWS:
        return []
    achados = _por_linha(arq, "K01", CONVERSA_COM_O_WINDOWS, "fala com o Windows fora da peça única")
    ja = {a.linha for a in achados}
    for linha, nome in sorted(_apelidos_do_windows(arq).items()):
        if linha not in ja and arq.codigo[linha - 1].strip():
            achados.append(Achado("K01", arq.caminho, linha, _texto_do_lugar(arq.codigo[linha - 1]),
                                  f"usa a biblioteca do Windows pelo apelido {nome}", arq.funcao(linha)))
    return sorted(achados, key=lambda a: a.linha)


def k02(arq: _Arquivo) -> list[Achado]:
    """K02: DETACHED_PROCESS, em qualquer arquivo do programa (até na peça única)."""
    if not e_programa(arq.caminho):
        return []
    return _por_linha(arq, "K02", DETACHED, "o processo lançado assim sai sem rodar (etapa 5, defeito 1)")


def k03(arq: _Arquivo) -> list[Achado]:
    """K03: comando de licença de pasta à mão, em qualquer arquivo do programa (até na peça única)."""
    if not e_programa(arq.caminho):
        return []
    return _por_linha(arq, "K03", LICENCA_A_MAO, "licença de pasta mudada à mão (etapa 5, defeito 4)")


def k04(arq: _Arquivo) -> list[Achado]:
    """K04: número de decisão num texto que a pessoa vê (sem comentário, docstring e comentário de folha de estilo)."""
    if not e_texto_que_a_pessoa_ve(arq.caminho):
        return []
    visivel = leitura.sem_comentarios_de_folha_de_estilo(arq.codigo, arq.raiz, arq.fonte)
    return _por_linha(arq, "K04", NUMERO_DE_DECISAO, "número de decisão num texto que a pessoa vê", visivel)


def k05(arq: _Arquivo) -> list[Achado]:
    """K05: emoji num texto da tela."""
    if not e_tela(arq.caminho):
        return []
    return _por_linha(arq, "K05", EMOJI, "emoji num texto da tela")


def k06(arq: _Arquivo) -> list[Achado]:
    """K06: um arquivo de core/ importa ui/."""
    if not (e_programa(arq.caminho) and arq.caminho.startswith("core/")):
        return []
    pacote = ".".join(arq.caminho.split("/")[:-1])
    saida = []
    for n, nome in leitura.importacoes(arq.raiz, pacote):
        if nome == "ui" or nome.startswith("ui."):
            saida.append(Achado("K06", arq.caminho, n, _texto_do_lugar(arq.codigo[n - 1]), f"core/ importa {nome}",
                                arq.funcao(n)))
    return saida


def k07(arq: _Arquivo) -> list[Achado]:
    """K07: tkinter ou customtkinter no programa."""
    if not e_programa(arq.caminho):
        return []
    saida = []
    for n, nome in leitura.importacoes(arq.raiz):
        if nome.split(".")[0] in ("tkinter", "customtkinter", "_tkinter"):
            saida.append(Achado("K07", arq.caminho, n, _texto_do_lugar(arq.codigo[n - 1]), f"importa {nome}",
                                arq.funcao(n)))
    return saida


def k16_codigo(arq: _Arquivo) -> list[Achado]:
    """K16 (parte do código): importa uma biblioteca que desenha ou inventa."""
    if not e_script_python(arq.caminho):
        return []
    saida = []
    for n, nome in leitura.importacoes(arq.raiz):
        if nome.split(".")[0].lower() in GERADORES:
            saida.append(Achado("K16", arq.caminho, n, _texto_do_lugar(arq.codigo[n - 1]),
                                f"importa {nome}, que desenha ou inventa pixel", arq.funcao(n)))
    return saida


def k24(arq: _Arquivo) -> list[Achado]:
    """K24: chamada de `click_input` ou `send_keys` num arquivo que usa o pywinauto (lê a chamada, não o texto)."""
    if not e_script_python(arq.caminho):
        return []
    if not any(nome.split(".")[0] == "pywinauto" for _, nome in leitura.importacoes(arq.raiz)):
        return []
    saida = []
    for no in ast.walk(arq.raiz):
        if isinstance(no, ast.Call):
            alvo = no.func
            nome = alvo.attr if isinstance(alvo, ast.Attribute) else alvo.id if isinstance(alvo, ast.Name) else ""
            if nome in ("click_input", "send_keys", "type_keys"):
                saida.append(Achado("K24", arq.caminho, no.lineno, _texto_do_lugar(arq.codigo[no.lineno - 1]),
                                    f"pywinauto {nome} toma o mouse e o teclado do Samuel",
                                    arq.funcao(no.lineno)))
    return saida


def k22(arq: _Arquivo) -> list[Achado]:
    """K22: a barra de rolagem de cada tema continua com o cinza de hoje e a folha de estilo usa essa cor."""
    if arq.caminho != "ui/estilo.py":
        return []
    temas = None
    for no in ast.walk(arq.raiz):
        alvos = [no.target] if isinstance(no, ast.AnnAssign) else no.targets if isinstance(no, ast.Assign) else []
        if any(isinstance(a, ast.Name) and a.id == "TEMAS" for a in alvos):
            try:
                temas = ast.literal_eval(no.value)
            except ValueError:
                temas = None
    if not isinstance(temas, dict):
        return [Achado("K22", arq.caminho, 0, "TEMAS", "não achei a tabela TEMAS das cores em ui/estilo.py")]
    saida = []
    for tema, cor in BARRA_DE_ROLAGEM.items():
        atual = (temas.get(tema) or {}).get("rolagem")
        if str(atual).upper() != cor.upper():
            saida.append(Achado("K22", arq.caminho, 0, f"TEMAS[{tema!r}]['rolagem'] = {atual!r}",
                                f"a barra de rolagem do tema {tema} mudou de {cor} para {atual} sem decisão do Samuel"))
    if not re.search(r"QScrollBar::handle:vertical\s*\{\{[^}]*background:\s*\{c\[\"rolagem\"\]\}", arq.fonte):
        saida.append(Achado("K22", arq.caminho, 0, "QScrollBar::handle:vertical",
                            "a barra de rolagem não usa mais a cor \"rolagem\" do tema"))
    return saida


def k23(caminho: str, fonte: str) -> list[Achado]:
    """K23: o arquivo do agente diz quais ferramentas ele tem, sem a de abrir agente e sem as da Central."""
    if not fnmatch(caminho, ".claude/agents/*.md"):
        return []
    cabeca = re.match(r"\A---\s*\n(.*?)\n---", fonte.replace("\r\n", "\n"), re.S)
    linha = re.search(r"^tools:\s*(.*)$", cabeca.group(1), re.M) if cabeca else None
    if not linha or not linha.group(1).strip():
        return [Achado("K23", caminho, 0, "tools:", "o agente não diz quais ferramentas tem: herda todas, inclusive "
                       "a de abrir outro agente e as da Central")]
    proibidas = [f.strip() for f in linha.group(1).split(",") if FERRAMENTAS_PROIBIDAS_AOS_AGENTES.search(f.strip())]
    if proibidas:
        return [Achado("K23", caminho, 0, _texto_do_lugar(linha.group(0)),
                       f"o agente tem ferramenta proibida: {', '.join(proibidas)}")]
    return []


def k16_requisitos(caminho: str, fonte: str) -> list[Achado]:
    """K16 (parte das bibliotecas): o requirements.txt pede uma biblioteca que desenha ou inventa."""
    if caminho != "requirements.txt":
        return []
    saida = []
    for n, linha in enumerate(leitura.linhas(fonte), 1):
        nome = re.split(r"[\s\[<>=~!;@]", linha.split("#", 1)[0].strip(), maxsplit=1)[0]
        if nome and nome.lower().replace("-", "_") in GERADORES:
            saida.append(Achado("K16", caminho, n, _texto_do_lugar(linha), f"{nome} desenha ou inventa pixel"))
    return saida


def k08(caminhos: Iterable[str]) -> list[Achado]:
    """K08: nome de arquivo ou pasta com acento (ou outra letra fora do ASCII) em core/, ui/ ou na raiz."""
    saida = []
    for c in caminhos:
        partes = c.split("/")
        if len(partes) > 1 and partes[0] not in ("core", "ui"):
            continue
        if any(ord(letra) > 127 for letra in c):
            saida.append(Achado("K08", c, 0, c, "nome de arquivo com acento"))
    return saida


_DO_CODIGO_PYTHON: list[Callable[[_Arquivo], list[Achado]]] = [k01, k02, k03, k04, k05, k06, k07, k16_codigo, k22, k24]


def conferir_codigo(caminhos: Iterable[str], ler: Callable[[str], str | None]) -> list[Achado]:
    """Roda as conferências do código parado nos `caminhos` (os do git, ou só os do próximo commit).

    `ler(caminho)` devolve o texto do arquivo (da pasta ou do índice) ou `None` se não deu para ler; arquivo que o
    porteiro deveria ler e não conseguiu vira achado (K00), nunca "passou".
    """
    caminhos = sorted(set(caminhos))
    achados: list[Achado] = k08(caminhos)
    for c in caminhos:
        precisa = e_script_python(c) or c == "requirements.txt" or fnmatch(c, ".claude/agents/*.md")
        if not precisa:
            continue
        fonte = ler(c)
        if fonte is None:
            achados.append(Achado("K00", c, 0, c, "não deu para ler o arquivo"))
            continue
        if c.endswith(".py"):
            arq = _Arquivo(c, fonte)
            if not arq.ler():
                achados.append(Achado("K00", c, 0, c, f"o porteiro não conseguiu ler o código: {arq.erro}"))
                continue
            for conferencia in _DO_CODIGO_PYTHON:
                achados += conferencia(arq)
        else:
            achados += k16_requisitos(c, fonte) + k23(c, fonte)
    return achados


def obrigatorios_numa_leitura_completa(caminhos: Iterable[str]) -> list[Achado]:
    """Na leitura do repositório inteiro, o que tem de existir para as conferências K22 e K23 terem o que ler."""
    caminhos = set(caminhos)
    saida = []
    if "ui/estilo.py" not in caminhos:
        saida.append(Achado("K22", "ui/estilo.py", 0, "ui/estilo.py", "não achei a folha de estilo para conferir"))
    if not any(fnmatch(c, ".claude/agents/*.md") for c in caminhos):
        saida.append(Achado("K23", ".claude/agents/", 0, ".claude/agents/", "não achei os arquivos dos agentes"))
    return saida


# ----------------------------------------------------------------------------------------------------------------
# De onde vêm os arquivos: o repositório inteiro (no GitHub) ou só o próximo commit (antes do commit)
# ----------------------------------------------------------------------------------------------------------------

def achados_do_repositorio(raiz) -> tuple[list[str], list[Achado]]:
    """Lê todos os arquivos que o git conhece, como estão na pasta, e devolve (os caminhos, os achados).

    É o que o teste do GitHub roda. Arquivo que o git conhece e não está na pasta vira K00 (não deu para ler).
    `GitFalhou` sobe para quem chamou: sem a lista do git não há conferência.
    """
    raiz = Path(raiz)
    caminhos = git.arquivos_do_git(raiz)

    def ler(c: str) -> str | None:
        """O texto do arquivo na pasta, ou None se não deu para ler (vira K00)."""
        try:
            return (raiz / c).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    return caminhos, conferir_codigo(caminhos, ler) + obrigatorios_numa_leitura_completa(caminhos)


def achados_do_proximo_commit(raiz) -> tuple[list[str], list[Achado]]:
    """Lê só os arquivos que vão no próximo commit, como estão no índice (não na pasta), e devolve (caminhos, achados).

    É o que a conferência antes do commit roda.
    """
    caminhos = git.arquivos_no_indice_mudados(raiz)

    def ler(c: str) -> str | None:
        """O texto do arquivo como vai no commit, ou None se o git não deu (vira K00)."""
        try:
            return git.conteudo_no_indice(raiz, c)
        except git.GitFalhou:
            return None

    return caminhos, conferir_codigo(caminhos, ler)
