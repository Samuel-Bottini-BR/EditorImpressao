"""Fotografo do Windows para a etapa 5 da frente do Kaique (D-722).

SO LE. Nao instala, nao apaga, nao cria nada no Windows. O unico arquivo que
ele escreve e o .json da fotografia, no caminho dado.

Uso (de qualquer pasta):
    D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe -I fotografo.py <saida.json>

Rodar duas vezes na etapa 5, ANTES de instalar e DEPOIS de desfazer, e
comparar com comparar.py. Se puder, rodar tambem num PowerShell de
administrador: algumas coisas (o recurso OpenSSH.Server do Windows, a pasta
C:\\ProgramData\\ssh, as tarefas criadas como o sistema) so aparecem inteiras
para o administrador. A foto anota se foi tirada com ou sem administrador.

O que a foto guarda:
  - servicos com ssh/OpenSSH/Tailscale no nome (sshd, ssh-agent, Tailscale);
  - o recurso do Windows OpenSSH.Server (e os arquivos sshd.exe/ssh.exe);
  - todas as regras do firewall (nome, ligada, direcao, acao) e o detalhe
    das que falam de ssh, porta 22 ou EditorImpressao;
  - as contas locais, o grupo Administradores e os perfis;
  - a chave UserList (contas escondidas da tela de entrada);
  - o conteudo (nomes, tamanhos, datas) de C:\\ProgramData\\ssh e de
    C:\\ProgramData\\EditorImpressao; o texto do sshd_config e o fim do
    registro da atualizacao (nenhum dos dois e projeto nem segredo; as chaves
    do servidor ssh NAO sao lidas, so os nomes);
  - as tarefas do Windows com EditorImpressao no nome ou na pasta;
  - os programas instalados (as chaves Uninstall, 64 e 32 bits, e do usuario);
  - os atalhos com "Editor" no Menu Iniciar e nas Areas de trabalho;
  - %LOCALAPPDATA%\\EditorImpressao: nomes, tamanhos e datas, SEM abrir
    nenhum arquivo (os projetos nao sao lidos);
  - as pastas de Arquivos de Programas do programa (antiga e nova);
  - os nomes das pastas de primeiro nivel de %LOCALAPPDATA%, %PROGRAMDATA%,
    C:\\Users (para achar o que o Velopack ou a conta de testes criarem);
  - a placa de rede do Tailscale e os enderecos dela;
  - o jeito da pergunta do Windows (UAC) e o antivirus;
  - o espaco livre em C: e D:.
"""

from __future__ import annotations

import ctypes
import getpass
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import winreg
from datetime import datetime
from pathlib import Path

PALAVRAS_DO_ATALHO = ("editor",)
PALAVRA_DA_TAREFA = "editorimpressao"


# ---------------------------------------------------------------------------
# ajudantes de leitura
# ---------------------------------------------------------------------------

def powershell(comando: str, tempo: int = 180):
    """Roda um comando de LEITURA no PowerShell e devolve o JSON dele (ou o erro)."""
    script = ("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'; "
              "[Console]::OutputEncoding=[Text.Encoding]::UTF8; "
              f"try {{ $r = @({comando}); $j = ConvertTo-Json -InputObject $r -Depth 4 -Compress }} "
              "catch { $j = ConvertTo-Json -InputObject @{ __erro = $_.Exception.Message } -Compress }; "
              # em base64 do UTF-8: o PowerShell 5.1 estraga os acentos na saida redirecionada
              "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes([string]$j))")
    try:
        feito = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                               capture_output=True, timeout=tempo,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.SubprocessError) as erro:
        return {"__erro": str(erro)}
    import base64

    bruto = feito.stdout.decode("ascii", errors="replace").strip()
    try:
        texto = base64.b64decode(bruto).decode("utf-8", errors="replace").strip() if bruto else ""
    except ValueError:
        texto = bruto
    if not texto:
        return {"__erro": feito.stderr.decode("utf-8", errors="replace").strip()[:500] or "sem saida"}
    try:
        return json.loads(texto)
    except json.JSONDecodeError:
        return {"__erro": "saida que nao e JSON", "saida": texto[:500]}


def listar_pasta(pasta: Path, ler_texto: tuple[str, ...] = (), cauda: dict[str, int] | None = None) -> dict:
    """Nomes, tamanhos e datas de uma pasta (recursivo). So abre os arquivos de ler_texto/cauda."""
    resultado = {"caminho": str(pasta), "existe": pasta.exists(), "arquivos": {}, "pastas": [],
                 "sem_licenca": [], "textos": {}}
    if not pasta.exists():
        return resultado

    def erro(e: OSError):
        resultado["sem_licenca"].append(f"{getattr(e, 'filename', '')}: {e.strerror}")

    for raiz, pastas, arquivos in os.walk(pasta, onerror=erro):
        for nome in pastas:
            resultado["pastas"].append(os.path.relpath(os.path.join(raiz, nome), pasta))
        for nome in arquivos:
            caminho = os.path.join(raiz, nome)
            relativo = os.path.relpath(caminho, pasta)
            try:
                info = os.stat(caminho)
                resultado["arquivos"][relativo] = {
                    "tamanho": info.st_size,
                    "data": datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds")}
            except OSError as e:
                resultado["sem_licenca"].append(f"{relativo}: {e.strerror}")
    for relativo in ler_texto:
        caminho = pasta / relativo
        try:
            resultado["textos"][relativo] = caminho.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            if caminho.exists():
                resultado["textos"][relativo] = f"(nao deu para ler: {e.strerror})"
    for relativo, linhas in (cauda or {}).items():
        caminho = pasta / relativo
        try:
            texto = caminho.read_text(encoding="utf-8", errors="replace").splitlines()
            resultado["textos"][relativo] = "\n".join(texto[-linhas:])
        except OSError as e:
            if caminho.exists():
                resultado["textos"][relativo] = f"(nao deu para ler: {e.strerror})"
    resultado["pastas"].sort()
    return resultado


def resumo_de_pasta_grande(pasta: Path) -> dict:
    """Quantos arquivos e quanto ocupa (para as pastas do programa, de 1,9 GB). Nao abre arquivo."""
    if not pasta.exists():
        return {"caminho": str(pasta), "existe": False}
    total = quantos = 0
    for raiz, _pastas, arquivos in os.walk(pasta):
        for nome in arquivos:
            try:
                total += os.stat(os.path.join(raiz, nome)).st_size
                quantos += 1
            except OSError:
                pass
    primeiro_nivel = sorted(os.listdir(pasta)) if pasta.is_dir() else []
    return {"caminho": str(pasta), "existe": True, "arquivos": quantos, "bytes": total,
            "primeiro_nivel": primeiro_nivel}


def nomes_de_primeiro_nivel(pasta: Path) -> list[str] | dict:
    try:
        return sorted(os.listdir(pasta))
    except OSError as e:
        return {"__erro": e.strerror}


def ler_chave(raiz, caminho: str, vista: int = 0) -> dict | None:
    """Todos os valores de uma chave do registro (so leitura), ou None se nao existe."""
    try:
        with winreg.OpenKey(raiz, caminho, 0, winreg.KEY_READ | vista) as chave:
            valores = {}
            i = 0
            while True:
                try:
                    nome, valor, _tipo = winreg.EnumValue(chave, i)
                except OSError:
                    break
                valores[nome] = valor if isinstance(valor, (int, str)) else repr(valor)
                i += 1
            return valores
    except OSError:
        return None


def programas_instalados() -> list[dict]:
    lugares = [
        ("HKLM 64", winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY),
        ("HKLM 32", winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY),
        ("HKCU", winreg.HKEY_CURRENT_USER, 0),
    ]
    base = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
    achados = []
    for rotulo, raiz, vista in lugares:
        try:
            chave = winreg.OpenKey(raiz, base, 0, winreg.KEY_READ | vista)
        except OSError:
            continue
        with chave:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(chave, i)
                except OSError:
                    break
                i += 1
                valores = ler_chave(raiz, base + "\\" + sub, vista) or {}
                achados.append({
                    "onde": rotulo, "chave": sub,
                    "nome": valores.get("DisplayName", ""),
                    "versao": valores.get("DisplayVersion", ""),
                    "editor": valores.get("Publisher", ""),
                    "pasta": valores.get("InstallLocation", ""),
                    "data": valores.get("InstallDate", ""),
                    "desinstalar": valores.get("UninstallString", ""),
                })
    return sorted(achados, key=lambda a: (a["onde"], a["chave"]))


def atalhos_com_editor() -> list[dict]:
    # Menu Iniciar: com as subpastas. Areas de trabalho: so o primeiro nivel.
    lugares = [
        (Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Microsoft/Windows/Start Menu/Programs", True),
        (Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs", True),
        (Path(os.environ.get("USERPROFILE", "")) / "Desktop", False),
        (Path(os.environ.get("USERPROFILE", "")) / "OneDrive/Desktop", False),
        (Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Desktop", False),
    ]
    achados = []
    for lugar, com_subpastas in lugares:
        if not lugar.is_dir():
            continue
        for raiz, pastas, arquivos in os.walk(lugar):
            if not com_subpastas:
                pastas[:] = []
            for nome in arquivos:
                if not nome.lower().endswith((".lnk", ".url")):
                    continue
                if any(p in nome.lower() for p in PALAVRAS_DO_ATALHO) or \
                        any(p in raiz.lower() for p in ("editorimpressao", "editor de impressao")):
                    caminho = Path(raiz) / nome
                    info = caminho.stat()
                    achados.append({"caminho": str(caminho), "tamanho": info.st_size,
                                    "data": datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds")})
    # Para onde cada .lnk aponta (CreateShortcut so LE o atalho; nada e gravado sem .Save()).
    lnks = [a["caminho"] for a in achados if a["caminho"].lower().endswith(".lnk")]
    if lnks:
        lista = ",".join("'" + c.replace("'", "''") + "'" for c in lnks)
        alvos = powershell("$s = New-Object -ComObject WScript.Shell; "
                           f"foreach ($c in @({lista})) {{ $l = $s.CreateShortcut($c); "
                           "[pscustomobject]@{caminho=$c; alvo=$l.TargetPath; argumentos=$l.Arguments} }")
        if isinstance(alvos, list):
            por_caminho = {a.get("caminho"): a for a in alvos if isinstance(a, dict)}
            for a in achados:
                if a["caminho"] in por_caminho:
                    a["alvo"] = por_caminho[a["caminho"]].get("alvo", "")
                    a["argumentos"] = por_caminho[a["caminho"]].get("argumentos", "")
    return sorted(achados, key=lambda a: a["caminho"])


def pasta_dos_projetos(pasta: Path) -> dict:
    """%LOCALAPPDATA%\\EditorImpressao: nomes, tamanhos, datas e uma impressao digital da lista.

    NAO abre nenhum arquivo: os projetos nao sao lidos. A impressao digital e
    feita so dos nomes, tamanhos e datas (se ela e igual antes e depois, nada
    ali mudou).
    """
    lista = listar_pasta(pasta)
    linhas = sorted(f"{nome}|{d['tamanho']}|{d['data']}" for nome, d in lista["arquivos"].items())
    lista["quantos_arquivos"] = len(lista["arquivos"])
    lista["bytes"] = sum(d["tamanho"] for d in lista["arquivos"].values())
    lista["impressao_digital"] = hashlib.sha256("\n".join(linhas).encode("utf-8")).hexdigest()
    return lista


def com_administrador() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:  # noqa: BLE001
        return False


# ---------------------------------------------------------------------------
# a fotografia
# ---------------------------------------------------------------------------

def fotografar() -> dict:
    programdata = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
    localappdata = Path(os.environ.get("LOCALAPPDATA", ""))
    foto: dict = {
        "quando": datetime.now().isoformat(timespec="seconds"),
        "computador": platform.node(),
        "usuario": getpass.getuser(),
        "com_administrador": com_administrador(),
        "windows": platform.version(),
    }

    foto["servicos"] = powershell(
        "Get-CimInstance Win32_Service | Where-Object { $_.Name -match 'ssh|tailscale' -or "
        "$_.DisplayName -match 'OpenSSH|Tailscale' } | Sort-Object Name | "
        "Select-Object Name, DisplayName, State, StartMode, StartName, PathName")

    foto["openssh_recurso"] = powershell(
        "Get-WindowsCapability -Online -Name 'OpenSSH*' | Select-Object Name, State")
    sistema = Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "OpenSSH"
    foto["openssh_arquivos"] = {nome: (sistema / nome).is_file() for nome in ("sshd.exe", "ssh.exe")}

    foto["firewall_todas"] = powershell(
        "Get-NetFirewallRule | Sort-Object Name | "
        "Select-Object Name, DisplayName, @{n='Enabled';e={[string]$_.Enabled}}, "
        "@{n='Direction';e={[string]$_.Direction}}, @{n='Action';e={[string]$_.Action}}", tempo=300)
    foto["firewall_detalhe"] = powershell(
        "Get-NetFirewallRule | Where-Object { $_.Name -match 'ssh|EditorImpressao' -or "
        "$_.DisplayName -match 'ssh|Editor de Impressao' } | ForEach-Object { "
        "$p = $_ | Get-NetFirewallPortFilter; $a = $_ | Get-NetFirewallAddressFilter; "
        "$i = $_ | Get-NetFirewallInterfaceFilter; "
        "[pscustomobject]@{ Name=$_.Name; Enabled=[string]$_.Enabled; Direction=[string]$_.Direction; "
        "Action=[string]$_.Action; Profile=[string]$_.Profile; Protocol=$p.Protocol; "
        "LocalPort=[string]$p.LocalPort; RemoteAddress=[string]$a.RemoteAddress; "
        "InterfaceAlias=[string]$i.InterfaceAlias } }", tempo=300)

    foto["contas"] = powershell(
        "Get-LocalUser | Sort-Object Name | Select-Object Name, @{n='Enabled';e={[string]$_.Enabled}}, "
        "Description, FullName, @{n='SID';e={$_.SID.Value}}")
    foto["administradores"] = powershell(
        "Get-LocalGroupMember -SID S-1-5-32-544 | Select-Object Name, @{n='SID';e={$_.SID.Value}}")
    foto["usuarios_grupo"] = powershell(
        "Get-LocalGroupMember -SID S-1-5-32-545 | Select-Object Name, @{n='SID';e={$_.SID.Value}}")
    foto["perfis"] = powershell(
        "Get-CimInstance Win32_UserProfile | Sort-Object LocalPath | "
        "Select-Object LocalPath, SID, Special, Loaded")
    foto["userlist"] = ler_chave(
        winreg.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon\SpecialAccounts\UserList",
        winreg.KEY_WOW64_64KEY)

    foto["programdata_ssh"] = listar_pasta(programdata / "ssh", ler_texto=("sshd_config",))
    foto["programdata_editor"] = listar_pasta(
        programdata / "EditorImpressao",
        cauda={r"atualizacao\atualizacao.log": 80,
               r"testes-a-distancia\o-que-foi-desfeito.txt": 80},
        ler_texto=(r"atualizacao\estado.json", r"testes-a-distancia\antes.json"))

    foto["tarefas"] = powershell(
        "Get-ScheduledTask | Where-Object { $_.TaskName -match 'EditorImpressao' -or "
        "$_.TaskPath -match 'EditorImpressao' } | ForEach-Object { "
        "[pscustomobject]@{ TaskPath=$_.TaskPath; TaskName=$_.TaskName; State=[string]$_.State; "
        "UserId=$_.Principal.UserId; Acoes=(($_.Actions | ForEach-Object { $_.Execute + ' ' + $_.Arguments }) "
        "-join ' | ') } }")

    foto["programas_instalados"] = programas_instalados()
    foto["atalhos"] = atalhos_com_editor()
    foto["pasta_dos_projetos"] = pasta_dos_projetos(localappdata / "EditorImpressao")
    # O Velopack grava aqui o registro dele (velopack_<pacote>.log) e talvez os pacotes baixados.
    foto["localappdata_velopack"] = listar_pasta(localappdata / "velopack")
    foto["perfil_da_conta_de_testes_existe"] = Path(r"C:\Users\EditorTestes").exists()
    foto["programa_antigo"] =resumo_de_pasta_grande(Path(r"C:\Program Files\Editor de Impressao"))
    foto["programa_novo"] = resumo_de_pasta_grande(Path(r"C:\Program Files\EditorImpressao"))

    foto["primeiro_nivel"] = {
        "LOCALAPPDATA": nomes_de_primeiro_nivel(localappdata),
        "PROGRAMDATA": nomes_de_primeiro_nivel(programdata),
        "C:\\Users": nomes_de_primeiro_nivel(Path(r"C:\Users")),
        "C:\\Program Files": nomes_de_primeiro_nivel(Path(r"C:\Program Files")),
    }

    foto["tailscale"] = powershell(
        "Get-NetAdapter -IncludeHidden | Where-Object { $_.Name -match 'Tailscale' -or "
        "$_.InterfaceDescription -match 'Tailscale' } | ForEach-Object { "
        "[pscustomobject]@{ Name=$_.Name; Status=[string]$_.Status; Descricao=$_.InterfaceDescription; "
        "Enderecos=((Get-NetIPAddress -InterfaceIndex $_.ifIndex -ErrorAction SilentlyContinue).IPAddress "
        "-join ', ') } }")

    foto["uac"] = ler_chave(winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System",
                            winreg.KEY_WOW64_64KEY)
    if isinstance(foto["uac"], dict):
        foto["uac"] = {k: v for k, v in foto["uac"].items()
                       if k in ("EnableLUA", "ConsentPromptBehaviorAdmin", "ConsentPromptBehaviorUser",
                                "PromptOnSecureDesktop")}
    foto["antivirus"] = powershell(
        "Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | "
        "Select-Object displayName, productState")

    foto["disco_livre_gb"] = {}
    for letra in ("C:\\", "D:\\"):
        try:
            foto["disco_livre_gb"][letra] = round(shutil.disk_usage(letra).free / 1024 ** 3, 1)
        except OSError:
            foto["disco_livre_gb"][letra] = None
    return foto


def main() -> int:
    if len(sys.argv) != 2:
        print("uso: python -I fotografo.py <saida.json>")
        return 2
    saida = Path(sys.argv[1])
    if saida.exists():
        print(f"PAREI: {saida} ja existe; nao escrevo por cima de uma foto.")
        return 2
    foto = fotografar()
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(foto, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"foto gravada em {saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
