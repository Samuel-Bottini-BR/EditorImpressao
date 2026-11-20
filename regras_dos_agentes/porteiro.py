"""O porteiro (D-791): as 25 conferências automáticas e as que leem o código parado.

As 24 primeiras conferências são as da proposta das regras dos agentes (ramo `regras-agentes-2026-11-18`, `proposta.md`
§5.1), **com a numeração da tabela de lá** (o esboço `conferir_codigo.py` numerava diferente; vale a tabela, plano-v3
passo 0). As novas continuam a numeração: a K25 (D-809, 19/11/2026) veio do catálogo dos erros (família F9).
A lista `CONFERENCIAS` abaixo é o lugar único dessa numeração: os testes, a lista de exceções e o formulário leem daqui.

Dois tipos:
- **as que leem o código parado** (este arquivo): K01 a K08, K16, K22, K23, K24, K25. Rodam no GitHub em toda entrega
  (`tests/test_conferencias_codigo.py`) e antes do commit, só nos arquivos mudados
  (`python -m regras_dos_agentes antes-do-commit`, chamado por `ganchos/pre-commit`).
- **as que olham o que a entrega mudou** (`porteiro_mudancas.py` e `formulario.py`): K09 a K15, K17 a K21. Precisam do
  commit de partida e do papel do agente, que vêm do pedido; rodam quando a entrega é conferida.

O que já está errado hoje no código fica na lista de exceções (`excecoes.py`), um item por lugar, e só ali.
Nenhuma conferência tem exceção própria escrita no código: nem por arquivo, nem por caso.

Onde cada busca olha (o "programa"): todo `.py` e `.pyw` do repositório, menos as pastas de `NAO_E_PROGRAMA` (os testes, os
relatórios, a documentação, o próprio porteiro, que tem as palavras que procura escritas como dado, e o código de fora). A K16, a K24 e a K25 olham também os scripts de teste e de apoio, e leem a estrutura do código (a importação, a
chamada de verdade e o comando que o código roda), não o texto; a K25 lê também os arquivos de comandos do terminal
(`.sh`, `.ps1`, `.bat`...).

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
    Conferencia("K19", "R096, R104, R115, R118, D-811, D-812, D-814", "o formulário da entrega", "entrega",
                "se a resposta é verdadeira"),
    Conferencia("K20", "R013, R096", "as palavras do Samuel citadas batem com o Livro, letra por letra", "entrega",
                "palavras certas na decisão errada"),
    Conferencia("K21", "R034", "a rodada do GitHub existe, é do último commit do ramo e passou", "entrega", "—"),
    Conferencia("K22", "R069", "a barra de rolagem continua cinza (os valores de hoje de ui/estilo.py)", "codigo", "—"),
    Conferencia("K23", "R106, R090, D-793", "agente não abre agente nem grava na Central (a lista de ferramentas de "
                "cada arquivo em .claude/agents/)", "codigo", "—"),
    Conferencia("K24", "R142", "pywinauto com click_input ou send_keys (tomam o mouse e o teclado do Samuel)",
                "codigo", "—"),
    # Conferência nova do catálogo dos erros (D-809, 19/11/2026; família F9). Não é da tabela da proposta: continua a
    # numeração dela.
    Conferencia("K25", "R156, D-809", "comando que muda a pasta .git inteira (fetch com --depth, gc, prune, stash, "
                "config) ou que apaga pasta com tudo dentro (rm -r, Remove-Item -Recurse) sem conferir antes se ela é "
                "atalho, em scripts e testes, fora das duas peças do git", "codigo",
                "comando montado em outra função ou guardado num texto que não começa com ele; os.exec e os.spawn; "
                "rd /s do cmd e robocopy; apagar DENTRO de um atalho (modelos/x); mexer em ramo que não é o seu; "
                "shutil.rmtree (o do Python 3.14 não entra no atalho, ver PALAVRAS_DE_APAGAR)"),
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


# As pastas do repositório que NÃO são programa (achado Q2 da quarta volta de quem quebrou: um `servicos/__init__.py`
# com `schtasks`, importado pelo `main.py`, passava). Todo o resto conta como programa, inclusive pasta nova. Lugar
# único: o porteiro, a K08 e a tabela leem daqui. PROTEGIDA ("igual"): pôr uma pasta aqui afrouxa o porteiro.
# Nenhuma delas pode ter o nome de um módulo da raiz (achado S1 da quinta volta): uma pasta `historico/` com
# `__init__.py` toma o lugar do `historico.py` no `import historico`, e o porteiro não a lia. Por isso `historico`
# saiu daqui (a pasta continua no git; não tem `.py`, então o porteiro passa a lê-la sem achar nada), e
# `pastas_de_fora_com_nome_de_modulo` acusa a colisão se ela voltar.
NAO_E_PROGRAMA = ("tests", "relatorios", ".github", ".claude", "docs", "memoria", "gabarito",
                  "regras_dos_agentes", "ganchos", "terceiros", "velhos")

# O que o Python carrega como código (achados S2 e S3 da quinta volta). Lugar único: toda conferência que olha código
# Python pergunta a `e_fonte_python`, e o código compilado vira K00.
# - Fonte: o `.py` e o `.pyw` (no Windows, `importlib.machinery.SOURCE_SUFFIXES` é `['.py', '.pyw']`).
# - Compilado, que o porteiro não consegue ler: o `.pyc`/`.pyo` (bytecode) e o `.pyd` (extensão do Windows,
#   `EXTENSION_SUFFIXES`). As `.dll` do ScanTailor não entram: o Python não as importa como módulo.
FONTE_PYTHON = (".py", ".pyw")
COMPILADO_PYTHON = (".pyc", ".pyo", ".pyd")


def e_fonte_python(caminho: str) -> bool:
    """O arquivo é código-fonte que o Python importa (`.py` ou `.pyw`)?"""
    return caminho.endswith(FONTE_PYTHON)


def _no_programa(caminho: str) -> bool:
    """O arquivo está numa parte do repositório que é programa (a raiz ou uma pasta fora de `NAO_E_PROGRAMA`)?"""
    partes = caminho.split("/")
    return len(partes) == 1 or partes[0] not in NAO_E_PROGRAMA


def e_programa(caminho: str) -> bool:
    """Código-fonte do programa: qualquer `.py`/`.pyw` do repositório fora das pastas de `NAO_E_PROGRAMA`."""
    return e_fonte_python(caminho) and _no_programa(caminho)


def modulos_da_raiz(caminhos: Iterable[str]) -> set[str]:
    """Os nomes que um `import` acha na raiz: cada arquivo de código ou compilado solto na raiz (`historico.py` →
    `historico`; `x.cp314-win_amd64.pyd` → `x`)."""
    return {c.split(".", 1)[0] for c in caminhos if "/" not in c and c.endswith(FONTE_PYTHON + COMPILADO_PYTHON)}


def pastas_de_fora_com_nome_de_modulo(caminhos: Iterable[str]) -> list[Achado]:
    """Achado S1: uma pasta de `NAO_E_PROGRAMA` com o nome de um módulo da raiz pode tomar o lugar dele no import (com
    um `__init__.py`), fora da vista do porteiro. Vira K00, que nunca entra na lista de exceções."""
    return [Achado("K00", nome, 0, nome, f"a pasta {nome}/ está fora da vista do porteiro e tem o nome de um módulo "
                   f"da raiz ({nome}): ela pode tomar o lugar dele no import")
            for nome in sorted(modulos_da_raiz(caminhos) & set(NAO_E_PROGRAMA))]


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
    """Todo `.py`/`.pyw` do projeto, menos o código de fora (`terceiros/`) e o guardado (`velhos/`)."""
    return e_fonte_python(caminho) and caminho.split("/")[0] not in FORA_DO_PROJETO


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
    # Lançar processo solto do Windows. As outras bandeiras de lançar processo são lidas pela estrutura do código
    # (`_bandeiras_do_windows`): só esconder a janela e baixar a prioridade não contam (achado R6).
    (r"\bDETACHED_PROCESS\b", "lançar processo solto do Windows", "f = subprocess.DETACHED_PROCESS"),
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

# K25 (D-809, 19/11/2026, família F9 do catálogo dos erros): a cópia do agente (worktree) divide a pasta .git com o
# repositório do Samuel; o `git fetch --depth=1` do juiz rodado na cópia deixou o repositório do PC raso (19/11), e um
# atalho de pasta (junção) tirado com um comando que entra nele esvaziou a pasta modelos/ (18/11).
# As duas peças do git (D-809): só elas falam com o git; o repositório de prova cria o seu .git numa pasta temporária.
PECAS_DO_GIT = ("regras_dos_agentes/conversa_com_o_git.py", "regras_dos_agentes/repositorio_de_prova.py")
# Os arquivos de comandos do terminal que a K25 lê, além do Python: o Git Bash (.sh, .bash), o PowerShell (.ps1,
# .psm1) e o cmd (.bat, .cmd). Arquivo sem extensão que começa com "#!" (o gancho `ganchos/pre-commit`) também.
COMANDOS_DE_TERMINAL = (".sh", ".bash", ".ps1", ".psm1", ".bat", ".cmd")
# O começo de um comando do git: o programa (com ou sem `.exe`, com o caminho na frente) e as opções gerais que vêm
# antes do subcomando (https://git-scm.com/docs/git#_options: -C, -c, --git-dir, --work-tree, --namespace,
# --exec-path, --config-env, que levam um valor, e as que não levam, como --no-pager e -P). `<?>` é o pedaço que não é
# texto escrito (um nome do código), lido por `leitura_do_codigo.comandos`.
_GIT = (r"(?i:(?<![\w.-])git(?:\.exe)?)(?:\s+(?:-C|-c|--git-dir|--work-tree|--namespace|--exec-path|--config-env)"
        r"(?:=|\s+)\S+|\s+--?[A-Za-z][\w-]*)*\s+")
# O `git config` que grava (https://git-scm.com/docs/git-config, lido em 19/11): os subcomandos set, unset,
# rename-section, remove-section e edit; as opções antigas --add, --unset, --unset-all, --rename-section,
# --remove-section, -e e --edit; e o jeito antigo "git config <nome> <valor>" (nome e valor). Só lê, e não conta: get,
# list, --get, --get-all, --get-regexp, --get-urlmatch, --get-color, --get-colorbool, -l, --list, e "git config <nome>"
# sem valor. Sem --worktree, o que se grava vai para o .git/config que todas as cópias dividem.
_GIT_CONFIG_QUE_GRAVA = (
    r"(?![^;&|\n]*\s(?:--get(?:-all|-regexp|-urlmatch|-color|-colorbool)?|-l|--list)(?:[\s=]|$))"
    r"(?:\s+(?:set|unset|rename-section|remove-section|edit)\b"
    r"|[^;&|\n]*\s(?:--add|--unset(?:-all)?|--rename-section|--remove-section|-e|--edit)(?:\s|$)"
    r"|(?:\s+(?:--file|-f|--blob|--type|--default|--comment)(?:=|\s+)\S+|\s+--?[A-Za-z][\w-]*(?:=\S+)?)*"
    r"\s+(?!(?:get|list)\b)[^\s;&|-]\S*\s+[^\s;&|])")
# Os subcomandos que mudam a pasta .git inteira (D-809: "fetch --depth, gc, prune, stash, config"). Cada linha é
# (expressão, o que é, uma linha de código que a K25 tem de acusar): um teste cobra que cada exemplo é acusado.
# Fontes: https://git-scm.com/docs/git-fetch (--depth, --deepen, --shallow-since, --shallow-exclude, --prune),
# https://git-scm.com/docs/git-gc, https://git-scm.com/docs/git-prune, https://git-scm.com/docs/git-worktree (prune),
# https://git-scm.com/docs/git-remote (prune), https://git-scm.com/docs/git-stash (list e show só leem),
# https://git-scm.com/docs/git-config (--get, --get-all, --get-regexp, --get-urlmatch, -l, --list, "get" e "list"
# só leem; `git -c chave=valor` vale só para aquele comando e não grava nada).
PALAVRAS_DO_GIT: list[tuple[str, str, str]] = [
    (_GIT + r"(?:fetch|pull)\b[^;&|\n]*\s--(?:depth|deepen|shallow-since|shallow-exclude)\b",
     "busca cortando a história (deixa o repositório inteiro raso)",
     'subprocess.run(["git", "fetch", "--depth=1", "origin", "obra-2026-10-26"])'),
    (_GIT + r"(?:fetch|pull|remote\s+update)\b[^;&|\n]*\s(?:--prune(?:-tags)?|-p)\b",
     "busca apagando os ramos que sumiram no GitHub", 'subprocess.run(["git", "fetch", "--prune", "origin"])'),
    (_GIT + r"gc\b", "reorganiza a pasta .git inteira (git gc)", 'subprocess.run(["git", "-C", str(raiz), "gc"])'),
    (_GIT + r"(?:(?:worktree|remote)\s+)?prune\b", "apaga coisas da pasta .git (prune)",
     'subprocess.run(["git", "worktree", "prune"])'),
    (_GIT + r"stash\b(?!\s+(?:list|show)\b)", "guarda e tira mudanças de todas as cópias (git stash)",
     'os.system("git stash")'),
    (_GIT + r"config\b" + _GIT_CONFIG_QUE_GRAVA,
     "muda a configuração do git do repositório ou do computador (git config)",
     'subprocess.run(["git", "config", "core.hooksPath", "ganchos"])'),
    # git clean (pedido da gerente, 20/11; achado 15 de quem quebrou): apaga os arquivos que o git não conhece, o
    # trabalho sem commit de quem rodou. Só lista, e não conta: -n e --dry-run (https://git-scm.com/docs/git-clean).
    (_GIT + r"clean\b(?![^;&|\n]*\s(?:-[a-zA-Z]*n[a-zA-Z]*|--dry-run)(?:\s|$))",
     "apaga os arquivos que o git não conhece (git clean)", 'subprocess.run(["git", "clean", "-fdq"])'),
]
# Apagar uma pasta com tudo dentro. Num atalho de pasta (junção), o comando que entra no atalho apaga o conteúdo da
# pasta de verdade. Fontes: o `rm` do Git Bash (coreutils, https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html:
# -r, -R, --recursive, juntas com outras letras: -rf, -fr); o Remove-Item do PowerShell
# (https://learn.microsoft.com/powershell/module/microsoft.powershell.management/remove-item: -Recurse, que o
# PowerShell aceita abreviado, -r a -Recurse; os apelidos ri, rm, rmdir, rd, del, erase,
# https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_aliases).
# O `shutil.rmtree` NÃO entra, de propósito (aceito pela gerente em 20/11, pela leitura abaixo). Lido no Python 3.14.3
# instalado (C:/Users/fotog/AppData/Local/Python/pythoncore-3.14-64/Lib), em 19/11:
#   - shutil.py, linhas 660-663: `_rmtree_islink` diz que a junção (IO_REPARSE_TAG_MOUNT_POINT) é um link;
#   - shutil.py, linhas 679-680: com a pasta pedida sendo link ou junção, ele recusa ("Cannot call rmtree on a symbolic
#     link") e não apaga nada (com ignore_errors=True, sai calado, também sem apagar);
#   - shutil.py, linha 688 (`followlinks=os._walk_symlinks_as_files`), e os.py, linha 381: dentro da pasta, a junção
#     conta como arquivo
#     (`entry.is_dir(follow_symlinks=False) and not entry.is_junction()`): é tirada sem entrar nela.
#   (No Windows ele usa `_rmtree_unsafe`, shutil.py linhas 669-707: `_use_fd_functions` é falso, linhas 804-808.)
# Os dois jeitos certos de tirar um atalho de pasta tiram só o atalho e NÃO são acusados (D-809 e a gerente, 20/11):
# `cmd /c rmdir <atalho>` (sem /s) e `(Get-Item <atalho>).Delete()` (sem $true).
PALAVRAS_DE_APAGAR: list[tuple[str, str, str]] = [
    (r"(?<![\w.-])rm(?:\.exe)?(?:\s+-[\w-]+)*?\s+(?:-(?=[A-Za-z]{0,3}[rR])[A-Za-z]{1,4}|--recursive)(?![\w-])",
     "apaga a pasta com tudo dentro (rm -r)", 'subprocess.run(["rm", "-rf", pasta])'),
    (r"(?i:(?<![\w.-])(?:Remove-Item|ri|rm|rmdir|rd|del|erase)\b[^;|\n]*?\s-r(?:e(?:c(?:u(?:r(?:se?)?)?)?)?)?(?![\w-]))",
     "apaga a pasta com tudo dentro (Remove-Item -Recurse)",
     'subprocess.run(["powershell", "-Command", "Remove-Item -LiteralPath x -Recurse -Force"])'),
]
# O que conta como "conferir antes se é atalho" (no mesmo arquivo de terminal antes da linha, ou na mesma função do
# Python antes da linha): o Python (`is_junction`, `isjunction`, `islink`, `is_symlink`, `st_reparse_tag`), o
# PowerShell (`LinkType`, `ReparsePoint`), o cmd (`fsutil reparsepoint`) e o Git Bash (`[ -L`, `[ -h`, `test -L`).
CONFERE_SE_E_ATALHO = (r"is_junction|isjunction|islink|is_symlink|st_reparse_tag|REPARSE_POINT|ReparsePoint|LinkType|"
                       r"fsutil\s+reparsepoint|\[\[?\s+-[Lh]\s|\btest\s+-[Lh]\s")
# O comando do git que muda o .git pode rodar quando a MESMA linha só deixa rodar no GitHub (onde a cópia é jogada fora
# no fim da rodada): `[ "${GITHUB_ACTIONS:-}" = "true" ] && git clean ...` no terminal, ou
# `if os.environ.get("GITHUB_ACTIONS") == "true": ...` no Python (pedido da gerente, 20/11, para o `git clean` do
# `trocar_codigo.sh`). Só na mesma linha, de propósito: uma conferência no começo do arquivo não libera o resto.
SO_NO_GITHUB = (r"\[\[?\s*\"?\$\{?GITHUB_ACTIONS(?::-)?\}?\"?\s*==?\s*\"?true\"?\s*\]\]?\s*&&"
                r"|os\.environ(?:\.get\(\s*|\[\s*)[\"']GITHUB_ACTIONS[\"']\s*[)\]]\s*==\s*[\"']true[\"']")
# O `git rm` tira arquivos do índice do git (`--cached`) ou da pasta, mas é o `rm` do git, não o do terminal: não é
# "apagar pasta com tudo dentro" (falso alarme do achado 1 de quem quebrou, 20/11: `git rm -rq --cached` do
# `trocar_codigo.sh`). Antes de procurar o `rm`, o `rm` que vem logo depois do `git` (e das opções dele) é trocado.
_O_RM_DO_GIT = re.compile(_GIT + r"rm\b")
_GIT_QUE_MUDA = [(re.compile(p), o_que) for p, o_que, _ in PALAVRAS_DO_GIT]
_APAGAR_TUDO = [(re.compile(p), o_que) for p, o_que, _ in PALAVRAS_DE_APAGAR]
_CONFERE_SE_E_ATALHO = re.compile(CONFERE_SE_E_ATALHO, re.I)
_SO_NO_GITHUB = re.compile(SO_NO_GITHUB)

# Um exemplo de cada jeito que a K25 lê um comando (achado 4 de quem quebrou, 20/11): a proteção do GitHub
# (`protecao.exemplos_que_o_porteiro_nao_acha`) passa cada exemplo da versão de teste pelo porteiro do ramo e cobra o
# achado na linha dita. Assim, desligar um jeito (o terminal, a lista guardada, o texto guardado) aparece.
# (arquivo, texto, linha que tem de ser acusada, o jeito). PROTEGIDA: nenhum sai.
EXEMPLOS_DA_K25: list[tuple[str, str, int, str]] = [
    ("relatorios/x/chamada.py", '"""Exemplo."""\nimport subprocess\n\n\ndef f():\n    """F."""\n'
     '    subprocess.run(["git", "gc"])\n', 7, "a chamada do subprocess"),
    ("relatorios/x/lista.py", '"""Exemplo."""\n\n\ndef f():\n    """F."""\n    return ["git", "stash"]\n', 6,
     "a lista guardada"),
    ("relatorios/x/texto.py", '"""Exemplo."""\nCOMANDO = "git fetch --depth=1 origin x"\n', 2, "o texto guardado"),
    ("relatorios/x/terminal.sh", '#!/bin/sh\nrm -rf "$PASTA"\n', 2, "o Git Bash"),
    ("relatorios/x/terminal.ps1", "$p = 'x'; Remove-Item $p -Recurse\n", 1, "o PowerShell"),
    ("relatorios/x/terminal.bat", "@echo off\ngit clean -fdq\n", 2, "o cmd"),
]

# Os dados das buscas que agente nenhum afrouxa: o teste do GitHub (`tests/test_conferencias_protecao.py`, pela
# `protecao.py`) compara cada um com o da versão de teste; nenhum item pode sumir nem mudar (achado 6 de quem tentou
# quebrar, 19/11). Só acrescentar é livre. Cada nome aqui é uma atribuição de valor literal neste arquivo.
PROTEGIDAS = ("PALAVRAS_DO_WINDOWS", "PALAVRAS_DE_DETACHED", "PALAVRAS_DE_LICENCA", "PADRAO_DO_NUMERO_DE_DECISAO",
              "PADRAO_DO_EMOJI", "GERADORES", "PADRAO_DAS_FERRAMENTAS_PROIBIDAS", "BARRA_DE_ROLAGEM",
              "PECA_UNICA_DO_WINDOWS", "FORA_DO_PROJETO", "NAO_E_PROGRAMA",
              "FONTE_PYTHON", "COMPILADO_PYTHON",
              # K25 (D-809), também em `protecao.PROTEGIDOS`.
              "PECAS_DO_GIT", "COMANDOS_DE_TERMINAL", "PALAVRAS_DO_GIT", "PALAVRAS_DE_APAGAR", "CONFERE_SE_E_ATALHO",
              "SO_NO_GITHUB", "EXEMPLOS_DA_K25")


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
        return self._funcao_em_volta(linha)[0]

    def inicio_da_funcao(self, linha: int) -> int:
        """A primeira linha da função mais de dentro que contém a linha (1 fora de função): o "antes" da K25."""
        return self._funcao_em_volta(linha)[1]

    def _funcao_em_volta(self, linha: int) -> tuple[str, int]:
        """(nome, primeira linha) da função mais de dentro que contém a linha; ("", 1) fora de função."""
        if self._funcoes is None:
            self._funcoes = sorted(leitura.funcoes(self.raiz), key=lambda f: f.fim - f.inicio)
        return next(((f.nome, f.inicio) for f in self._funcoes if f.inicio <= linha <= f.fim), ("", 1))


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


# Os construtores e atributos do ctypes que dão uma biblioteca do Windows (a mesma conta das duas linhas da lista).
_CONSTRUTORES_DO_WINDOWS = {"WinDLL", "OleDLL"}
_ATRIBUTOS_DO_WINDOWS = {"windll", "oledll"}
_DLL_DO_WINDOWS_NOMES = set(_DLL_DO_WINDOWS.strip("(?:)").split("|"))


def _pega_a_biblioteca(valor: ast.AST) -> bool:
    """O valor pega uma biblioteca do Windows: `ctypes.WinDLL("x")`, `ctypes.CDLL("kernel32")`, `ctypes.windll.kernel32`,
    `ctypes.cdll.kernel32` ou uma função dela sem chamar (`ctypes.windll.kernel32.SetThreadExecutionState`)."""
    if isinstance(valor, ast.Call):
        nome = valor.func.attr if isinstance(valor.func, ast.Attribute) else getattr(valor.func, "id", "")
        if nome in _CONSTRUTORES_DO_WINDOWS:
            return True
        primeiro = valor.args[0] if valor.args else None
        return (nome == "CDLL" and isinstance(primeiro, ast.Constant) and isinstance(primeiro.value, str)
                and primeiro.value.lower().removesuffix(".dll") in _DLL_DO_WINDOWS_NOMES)
    no = valor
    while isinstance(no, ast.Attribute):
        if no.attr in _ATRIBUTOS_DO_WINDOWS or (no.attr in _DLL_DO_WINDOWS_NOMES and isinstance(no.value, ast.Attribute)
                                                and no.value.attr == "cdll"):
            return True
        no = no.value
    return isinstance(no, ast.Name) and no.id in _ATRIBUTOS_DO_WINDOWS


def _apelidos_do_windows(arq: _Arquivo) -> dict[int, str]:
    """As linhas que usam a biblioteca do Windows por um apelido (achados N2 e R5 de quem quebrou).

    Segue o apelido dentro do arquivo:
    (1) o nome que recebe a biblioteca (`kernel32 = ctypes.WinDLL("kernel32")`) ou uma função dela sem chamar
        (`funcao = ctypes.windll.kernel32.SetThreadExecutionState`);
    (2) a função que devolve a biblioteca EM SI (`return kernel32, ...`; um `lambda` que usa a biblioteca conta como
        função dela), na posição em que ela devolve; quem recebe o que essa função devolve vira apelido só naquela
        posição (`kernel32, entrada = _entrada_da_janela_preta()`: só o `kernel32`);
    (3) toda linha que usa um desses nomes, na mesma função ou dentro dela, e toda chamada de uma função que devolve a
        biblioteca (pelo nome da função no mesmo arquivo, ou `self.metodo()` dentro da mesma classe).
    O resultado de uma chamada feita pela biblioteca (`alca = kernel32.OpenProcess(...)`,
    `_MARCA = ctypes.windll.kernel32.CreateMutexW(...)`, `return funcao(...) == 1`) não vira apelido (achado R5).
    Não segue: o apelido que vai para outro arquivo, nem o que passa por um dicionário ou um atributo (`self.k = ...`).
    """
    if not PEGA_A_BIBLIOTECA.search("\n".join(arq.codigo)):
        return {}
    apelidos: dict[str, set[str]] = {}            # escopo (função) → nomes
    devolve: dict[str, set[int | None]] = {}      # função (nome completo) → posições devolvidas (None = o valor inteiro)

    def e_apelido(nome: str, linha: int) -> bool:
        """O nome é um apelido da biblioteca no lugar desta linha?"""
        return any(nome in apelidos.get(e, set()) for e in _escopos(arq.funcao(linha)))

    def funcao_chamada(chamada: ast.Call, linha: int) -> str | None:
        """O nome completo da função deste arquivo que a chamada chama, se ela devolve a biblioteca."""
        escopo = arq.funcao(linha)
        if isinstance(chamada.func, ast.Name):
            candidatos = [f"{e}.{chamada.func.id}" if e else chamada.func.id for e in _escopos(escopo)]
        elif (isinstance(chamada.func, ast.Attribute) and isinstance(chamada.func.value, ast.Name)
              and chamada.func.value.id == "self" and "." in escopo):
            candidatos = [f"{escopo.rsplit('.', 1)[0]}.{chamada.func.attr}"]
        else:
            return None
        return next((c for c in candidatos if c in devolve), None)

    def e_a_biblioteca(valor: ast.AST, linha: int) -> bool:
        """O valor É a biblioteca (ou uma função dela), não o resultado de uma chamada feita por ela."""
        if _pega_a_biblioteca(valor):
            return True
        if isinstance(valor, ast.Name):
            return e_apelido(valor.id, linha)
        if isinstance(valor, ast.Attribute):
            return e_a_biblioteca(valor.value, linha)
        if isinstance(valor, ast.Lambda):
            return any(isinstance(n, ast.Name) and e_apelido(n.id, linha) for n in ast.walk(valor.body))
        if isinstance(valor, ast.Call):
            f = funcao_chamada(valor, linha)
            return f is not None and None in devolve[f]
        return False

    def posicoes(valor: ast.AST, linha: int) -> set[int | None]:
        """As posições do valor que são a biblioteca (None = o valor inteiro)."""
        if isinstance(valor, (ast.Tuple, ast.List)):
            return {i for i, e in enumerate(valor.elts) if e_a_biblioteca(e, linha)}
        if _pega_a_biblioteca(valor):
            return {None}
        if isinstance(valor, ast.Call):
            f = funcao_chamada(valor, linha)
            return set(devolve[f]) if f else set()
        return {None} if e_a_biblioteca(valor, linha) else set()

    atribuicoes = [n for n in ast.walk(arq.raiz) if isinstance(n, (ast.Assign, ast.AnnAssign)) and n.value is not None]
    funcoes = [n for n in ast.walk(arq.raiz) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    mudou = True
    while mudou:
        mudou = False
        for no in atribuicoes:
            escopo = arq.funcao(no.lineno)
            alvos = [no.target] if isinstance(no, ast.AnnAssign) else list(no.targets)
            pos = posicoes(no.value, no.lineno)
            novos: set[str] = set()
            for alvo in alvos:
                if isinstance(alvo, ast.Name) and None in pos:
                    novos.add(alvo.id)
                elif isinstance(alvo, (ast.Tuple, ast.List)):
                    novos |= {e.id for i, e in enumerate(alvo.elts) if isinstance(e, ast.Name) and (i in pos or None in pos)}
            novos -= apelidos.get(escopo, set())
            if novos:
                apelidos.setdefault(escopo, set()).update(novos)
                mudou = True
        for f in funcoes:
            nome = arq.funcao(f.lineno) if arq.funcao(f.lineno).endswith(f.name) else f.name
            pos: set[int | None] = set()
            for r in ast.walk(f):
                if isinstance(r, ast.Return) and r.value is not None and arq.funcao(r.lineno) == nome:
                    pos |= posicoes(r.value, r.lineno)
            if pos - devolve.get(nome, set()):
                devolve.setdefault(nome, set()).update(pos)
                mudou = True
    usadas: dict[int, str] = {}
    for n in ast.walk(arq.raiz):
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and e_apelido(n.id, n.lineno):
            usadas.setdefault(n.lineno, n.id)
        elif isinstance(n, ast.Call) and funcao_chamada(n, n.lineno):
            usadas.setdefault(n.lineno, funcao_chamada(n, n.lineno))
    return usadas


# As bandeiras de lançar processo que não mudam nada no Windows: só esconder a janela preta e baixar a prioridade
# (achado R6 da terceira volta; escolha técnica da gerente). Qualquer outra (DETACHED_PROCESS, CREATE_NEW_CONSOLE,
# CREATE_BREAKAWAY_FROM_JOB...) ou um valor que não se consegue ler é conversa com o Windows.
BANDEIRAS_QUE_SO_ESCONDEM = {"CREATE_NO_WINDOW": 0x08000000, "BELOW_NORMAL_PRIORITY_CLASS": 0x00004000,
                             "IDLE_PRIORITY_CLASS": 0x00000040}


def _bandeiras_do_windows(arq: _Arquivo) -> dict[int, str]:
    """As linhas com `creationflags=` que usam uma bandeira além de esconder a janela ou baixar a prioridade.

    Lê a estrutura do código: o número escrito, `subprocess.NOME`, `getattr(subprocess, "NOME", ...)`, `a | b`,
    `x if c else y`, e o nome guardado numa variável do mesmo arquivo (segue as atribuições dela). O que não se consegue
    ler conta como bandeira desconhecida (acusa). Devolve linha → o que foi achado.
    """
    permitidos = set(BANDEIRAS_QUE_SO_ESCONDEM.values())
    atribuicoes: dict[str, list[ast.AST]] = {}
    for no in ast.walk(arq.raiz):
        if isinstance(no, ast.Assign):
            for alvo in no.targets:
                if isinstance(alvo, ast.Name):
                    atribuicoes.setdefault(alvo.id, []).append(no.value)

    def ruins(valor: ast.AST, vistos: frozenset) -> set[str]:
        """As bandeiras do valor que não só escondem (vazio = tudo bem)."""
        if isinstance(valor, ast.Constant) and isinstance(valor.value, int):
            sobra = valor.value & ~sum(permitidos)
            return {hex(sobra)} if sobra else set()
        nome = (valor.attr if isinstance(valor, ast.Attribute) else valor.id if isinstance(valor, ast.Name) else None)
        if isinstance(valor, ast.Call) and getattr(valor.func, "id", "") == "getattr" and len(valor.args) >= 2 \
                and isinstance(valor.args[1], ast.Constant):
            nome = str(valor.args[1].value)
        if nome is not None:
            if nome in BANDEIRAS_QUE_SO_ESCONDEM:
                return set()
            if isinstance(valor, ast.Name) and nome in atribuicoes and nome not in vistos:
                return set().union(*(ruins(v, vistos | {nome}) for v in atribuicoes[nome]))
            return {nome}
        if isinstance(valor, ast.BinOp) and isinstance(valor.op, ast.BitOr):
            return ruins(valor.left, vistos) | ruins(valor.right, vistos)
        if isinstance(valor, ast.IfExp):
            return ruins(valor.body, vistos) | ruins(valor.orelse, vistos)
        return {"valor que não dá para ler"}

    achadas: dict[int, str] = {}
    for no in ast.walk(arq.raiz):
        if isinstance(no, ast.keyword) and no.arg == "creationflags":
            sobra = ruins(no.value, frozenset())
            if sobra:
                achadas[no.value.lineno] = ", ".join(sorted(sobra))
    return achadas


def k01(arq: _Arquivo) -> list[Achado]:
    """K01: conversa com o Windows fora da peça única: as palavras da lista, o uso da biblioteca do Windows pelo
    apelido e a bandeira de lançar processo que vai além de esconder a janela."""
    if not e_programa(arq.caminho) or arq.caminho == PECA_UNICA_DO_WINDOWS:
        return []
    achados = _por_linha(arq, "K01", CONVERSA_COM_O_WINDOWS, "fala com o Windows fora da peça única")
    ja = {a.linha for a in achados}
    extras = [(linha, f"usa a biblioteca do Windows pelo apelido {nome}")
              for linha, nome in _apelidos_do_windows(arq).items()]
    extras += [(linha, f"lança processo com bandeira do Windows ({quais})")
               for linha, quais in _bandeiras_do_windows(arq).items()]
    for linha, porque in sorted(extras):
        if linha not in ja and arq.codigo[linha - 1].strip():
            ja.add(linha)
            achados.append(Achado("K01", arq.caminho, linha, _texto_do_lugar(arq.codigo[linha - 1]), porque,
                                  arq.funcao(linha)))
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


def _o_que_o_comando_muda(comando: str, antes: str, linha: str = "") -> str | None:
    """K25: o que este comando de terminal faz de perigoso (None = nada).

    `antes` é o código que vem antes dele (na mesma função do Python, ou no arquivo de terminal até a linha): o apagar
    com tudo dentro só é acusado se ali não houver conferência de atalho (`CONFERE_SE_E_ATALHO`). `linha` é a linha de
    código onde o comando está: o comando do git que muda a pasta .git só passa se ESSA linha deixa rodar só no
    GitHub (`SO_NO_GITHUB`); conferir antes, noutra linha, não o torna seguro. O `rm` do git (`git rm`) não é o `rm`
    do terminal (`_O_RM_DO_GIT`).
    """
    for padrao, o_que in _GIT_QUE_MUDA:
        m = padrao.search(comando)
        if m and not _SO_NO_GITHUB.search(linha):
            return f"{o_que}, fora das peças do git: {m.group(0).strip()}"
    comando = _O_RM_DO_GIT.sub(lambda m: m.group(0)[:-2] + "git_rm", comando)
    for padrao, o_que in _APAGAR_TUDO:
        m = padrao.search(comando)
        if m and not _CONFERE_SE_E_ATALHO.search(antes):
            return f"{o_que} sem conferir antes se é atalho de pasta: {m.group(0).strip()}"
    return None


def k25(arq: _Arquivo) -> list[Achado]:
    """K25 (D-809): no Python, o comando de terminal que muda a pasta .git inteira ou apaga pasta com tudo dentro sem
    conferir se é atalho. Lê os comandos pela estrutura (`leitura_do_codigo.comandos`), nunca o texto solto."""
    if not e_script_python(arq.caminho) or arq.caminho in PECAS_DO_GIT:
        return []
    saida, ja = [], set()
    for linha, comando in leitura.comandos(arq.raiz):
        antes = "\n".join(arq.codigo[arq.inicio_da_funcao(linha) - 1:linha])
        porque = _o_que_o_comando_muda(comando, antes, arq.codigo[linha - 1])
        if porque and linha not in ja:
            ja.add(linha)
            saida.append(Achado("K25", arq.caminho, linha, _texto_do_lugar(arq.codigo[linha - 1]), porque,
                                arq.funcao(linha)))
    return saida


def e_comandos_de_terminal(caminho: str, fonte: str | None = None) -> bool:
    """Arquivo de comandos do terminal do projeto (`COMANDOS_DE_TERMINAL`), ou sem extensão começando com "#!"."""
    if caminho.split("/")[0] in FORA_DO_PROJETO:
        return False
    if caminho.lower().endswith(COMANDOS_DE_TERMINAL):
        return True
    return "." not in caminho.rsplit("/", 1)[-1] and fonte is not None and fonte.lstrip("﻿").startswith("#!")


def _sem_comentario_do_terminal(caminho: str, linha: str) -> str:
    """A linha sem o comentário: `#` no Git Bash e no PowerShell; `rem` e `::` no cmd."""
    if caminho.lower().endswith((".bat", ".cmd")):
        return "" if re.match(r"^\s*@?(?:rem\b|::)", linha, re.I) else linha
    return re.sub(r"(?:^|\s)#.*$", "", linha)


def k25_terminal(caminho: str, fonte: str) -> list[Achado]:
    """K25 (D-809) nos arquivos de comandos do terminal: cada linha (sem comentário) é um comando."""
    if not e_comandos_de_terminal(caminho, fonte):
        return []
    codigo = [_sem_comentario_do_terminal(caminho, l) for l in leitura.linhas(fonte)]
    saida = []
    for n, linha in enumerate(codigo, 1):
        porque = _o_que_o_comando_muda(linha, "\n".join(codigo[:n]), linha) if linha.strip() else None
        if porque:
            saida.append(Achado("K25", caminho, n, _texto_do_lugar(linha), porque))
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
    """K08: nome de arquivo ou pasta com acento (ou outra letra fora do ASCII) no programa (fora de `NAO_E_PROGRAMA`)."""
    return [Achado("K08", c, 0, c, "nome de arquivo com acento") for c in caminhos
            if _no_programa(c) and any(ord(letra) > 127 for letra in c)]


def k00_compilado_sem_fonte(caminhos: Iterable[str]) -> list[Achado]:
    """Código compilado guardado no repositório (`COMPILADO_PYTHON`: `.pyc`, `.pyo`, `.pyd`): o Python o importa, e o
    porteiro não consegue lê-lo (achados Q4 da quarta volta e S3 da quinta). Vira K00, que nunca entra na lista."""
    return [Achado("K00", c, 0, c, "código compilado no repositório: o porteiro não consegue ler e o Python "
                   "importa") for c in caminhos if c.endswith(COMPILADO_PYTHON)]


_DO_CODIGO_PYTHON: list[Callable[[_Arquivo], list[Achado]]] = [k01, k02, k03, k04, k05, k06, k07, k16_codigo, k22, k24,
                                                                k25]


def _talvez_sem_extensao(caminho: str) -> bool:
    """Arquivo do projeto sem extensão: pode ser um script com "#!" (só se sabe lendo)."""
    return "." not in caminho.rsplit("/", 1)[-1] and caminho.split("/")[0] not in FORA_DO_PROJETO


def conferir_codigo(caminhos: Iterable[str], ler: Callable[[str], str | None]) -> list[Achado]:
    """Roda as conferências do código parado nos `caminhos` (os do git, ou só os do próximo commit).

    `ler(caminho)` devolve o texto do arquivo (da pasta ou do índice) ou `None` se não deu para ler; arquivo que o
    porteiro deveria ler e não conseguiu vira achado (K00), nunca "passou".
    """
    caminhos = sorted(set(caminhos))
    achados: list[Achado] = (k08(caminhos) + k00_compilado_sem_fonte(caminhos)
                             + pastas_de_fora_com_nome_de_modulo(caminhos))
    for c in caminhos:
        terminal = e_comandos_de_terminal(c)
        sem_extensao = _talvez_sem_extensao(c)
        precisa = (e_script_python(c) or c == "requirements.txt" or fnmatch(c, ".claude/agents/*.md") or terminal
                   or sem_extensao)
        if not precisa:
            continue
        fonte = ler(c)
        if fonte is None and sem_extensao:
            continue          # sem extensão e sem texto legível: não é script (só o "#!" diria que é)
        if fonte is None:
            achados.append(Achado("K00", c, 0, c, "não deu para ler o arquivo"))
            continue
        if e_fonte_python(c):
            arq = _Arquivo(c, fonte)
            if not arq.ler():
                achados.append(Achado("K00", c, 0, c, f"o porteiro não conseguiu ler o código: {arq.erro}"))
                continue
            for conferencia in _DO_CODIGO_PYTHON:
                achados += conferencia(arq)
        else:
            achados += k16_requisitos(c, fonte) + k23(c, fonte) + k25_terminal(c, fonte)
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
