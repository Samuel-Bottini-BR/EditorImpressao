"""Provas da D-731 e dos defeitos B2, B3, B4 dos testes à distância (17/11/2026).

D-731 (Samuel, 16/11/2026), "ok" a: "se um dia o programa for desinstalado do notebook do Kaique, o comando de
longe e a conta de testes saem junto? Assim o notebook fica como era antes de instalar."
D-733 (17/11/2026), "1- sim": alternativa B do plano `relatorios/frente-kaique-2026-11-16/d731-desinstalar/
plano-d732.md`. Para a D-731: o `ligar` cria uma tarefa "desfazer" (roda como o sistema; a conta comum pode mandar
rodar). O gancho de desinstalar do Velopack roda SEM administrador e tem 30 s: ele só manda a tarefa rodar.

Defeitos do plano.md (seção 9), achados lendo o código em 16/11/2026:
  B2  as linhas que o `ligar` põe no fim do sshd_config caem dentro do bloco "Match Group administrators";
  B3  ligar de novo depois de desligar falha (tenta criar a conta que já existe) e repete as linhas;
  B4  desligar desativa um OpenSSH que já era do dono antes.

COMO SE PROVA SEM TOCAR O WINDOWS. Dois jeitos:
  1. o executor de mentira (como em test_decisoes_testes_a_distancia.py), que só anota;
  2. o "Windows de mentira" do PowerShell: o comando de um passo roda num powershell.exe em que cada comando do
     Windows que muda alguma coisa (Stop-Service, Remove-LocalUser, icacls...) foi TROCADO por uma função que só
     escreve "CHAMOU <nome> <argumentos>". No PowerShell, uma função com o mesmo nome ganha do comando de verdade.
     Os caminhos (sshd_config, pasta ssh, pasta dos testes) apontam para a pasta temporária do teste.
     PROTEÇÃO: antes de rodar, `rodar_no_windows_de_mentira` confere o texto do comando e se RECUSA a rodar se
     houver um comando do Windows sem a troca, um caminho do disco C:, ou uma escrita no registro sem troca.

Cada prova de defeito falha no código de antes (commit 997a3085); ver o relatório em
relatorios/frente-kaique-2026-11-16/d731-construcao/.
"""

from __future__ import annotations

import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import atualizacao
from core import testes_a_distancia as td

POWERSHELL = shutil.which("powershell")
precisa_do_powershell = pytest.mark.skipif(
    sys.platform != "win32" or not POWERSHELL, reason="o Windows de mentira usa o powershell.exe")

DESCRICAO_NOSSA = "Conta so para os testes a distancia"  # a que o ligar dá à conta (etapa 4)

# Uma cópia do fim do sshd_config de fábrica do OpenSSH do Windows (sshd_config_default): tem a linha comentada
# "#PasswordAuthentication yes" e termina com o bloco "Match Group administrators".
SSHD_CONFIG_DE_FABRICA = (
    "# This is the sshd server system-wide configuration file.\n"
    "#Port 22\n"
    "#PubkeyAuthentication yes\n"
    "AuthorizedKeysFile\t.ssh/authorized_keys\n"
    "# To disable tunneled clear text passwords, change to no here!\n"
    "#PasswordAuthentication yes\n"
    "#PermitEmptyPasswords no\n"
    "# override default of no subsystems\n"
    "Subsystem\tsftp\tsftp-server.exe\n"
    "\n"
    "Match Group administrators\n"
    "       AuthorizedKeysFile __PROGRAMDATA__/ssh/administrators_authorized_keys\n"
)


# ---------------------------------------------------------------------------------------------------------------
# O executor de mentira
# ---------------------------------------------------------------------------------------------------------------

class ExecutorDeMentira(td.Executor):
    """Anota o que seria feito. `aplicar` (a pergunta de administrador que espera) não pode ser chamada no gancho."""

    def __init__(self, aplicar_proibido: bool = False) -> None:
        self.chamadas: list[tuple[list[td.Passo], str]] = []
        self.tarefas: list[str] = []
        self._aplicar_proibido = aplicar_proibido

    def aplicar(self, passos, senha):
        if self._aplicar_proibido:
            pytest.fail("o gancho de desinstalar não pode pedir licença de administrador nem esperar (30 s)")
        self.chamadas.append((list(passos), senha))
        return td.Resultado(True, passos=passos)

    def rodar_a_tarefa(self, nome):
        self.tarefas.append(nome)
        return td.Resultado(True)


@pytest.fixture
def dados(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.delenv("APPDATA", raising=False)
    return tmp_path


# ---------------------------------------------------------------------------------------------------------------
# O Windows de mentira do PowerShell
# ---------------------------------------------------------------------------------------------------------------

# Comandos que só leem ou só mexem no texto: podem rodar de verdade.
SO_LEEM = {"Test-Path", "Get-Content", "ConvertFrom-Json", "ConvertTo-Json", "Where-Object", "ForEach-Object",
           "Select-Object", "Sort-Object", "Write-Output", "Out-Null", "New-Object", "Get-Date", "Join-Path",
           "Get-ChildItem", "Get-Item"}
# Comandos que escrevem em arquivo: só rodam de verdade se o comando não citar o disco C: nem o registro.
ESCREVEM_ARQUIVO = {"Set-Content", "Add-Content", "New-Item", "Remove-Item"}
# Programas de fora que mudam o Windows: sempre trocados.
PROGRAMAS_DE_FORA = ("icacls", "schtasks", "reg", "net", "sc", "cmd", "takeown", "msiexec", "powershell")


def _mentira_que_anota(nome: str) -> str:
    return (f"function {nome} {{ $a = @($input); Write-Host ('CHAMOU {nome} ' + ($args -join ' '));"
            f" foreach ($i in $a) {{ Write-Host ('CHAMOU {nome} <- ' + $i) }} }}")


def rodar_no_windows_de_mentira(comando: str, pasta: Path, trocas: dict[str, str] | None = None,
                                anotar: tuple[str, ...] = ()) -> tuple[int, list[str], str]:
    """Roda `comando` num powershell.exe com os comandos do Windows trocados. Devolve (código, linhas, erro).

    `trocas`: nome -> corpo da função (para devolver objetos, ex.: Get-LocalUser). `anotar`: nomes que só anotam.
    Recusa-se a rodar (o teste falha) se algo de verdade do Windows ficasse sem troca.
    """
    trocas = dict(trocas or {})
    for nome in anotar:
        trocas.setdefault(nome, _mentira_que_anota(nome))
    trocas.setdefault("Anotar", "function Anotar($t) { Write-Host ('ANOTOU ' + $t) }")

    # --- a proteção: nada de verdade do Windows sem troca ---
    texto = comando.replace(td.REGRA_LARGA_DO_OPENSSH, "").replace(td.NOME_DA_REGRA, "")  # nomes, não comandos
    assert "C:\\" not in comando and "c:\\" not in comando, "o comando cita o disco C: (caminho não trocado)"
    assert "ComObject" not in comando, "o comando fala com um serviço do Windows (COM): não roda aqui"
    for nome in set(re.findall(r"\b[A-Z][a-z]+-[A-Z][A-Za-z]+\b", texto)):
        if nome in trocas or nome in SO_LEEM:
            continue
        assert nome in ESCREVEM_ARQUIVO, f"'{nome}' mudaria o Windows de verdade e não tem troca"
        assert "HKLM" not in comando and "HKCU" not in comando, f"'{nome}' poderia escrever no registro"
    for programa in PROGRAMAS_DE_FORA:
        if re.search(rf"(?<![\w$-]){programa}(\.exe)?(?![\w-])", comando, re.IGNORECASE):
            assert programa in trocas, f"o programa '{programa}' mudaria o Windows e não tem troca"

    script = pasta / "windows_de_mentira.ps1"
    script.write_text("\n".join(["$ErrorActionPreference = 'Stop'", "$SenhaDosTestes = 'senha-de-mentira'",
                                 *trocas.values(), comando]), encoding="utf-8-sig")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                            "-File", str(script)], capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
    return feito.returncode, feito.stdout.splitlines(), feito.stderr


def chamou(linhas: list[str], nome: str) -> list[str]:
    return [l for l in linhas if l.startswith(f"CHAMOU {nome} ")]


@pytest.fixture
def maquina(tmp_path, monkeypatch, dados):
    """Os caminhos do Windows que os passos usam, trocados por pastas do teste."""
    ssh = tmp_path / "ssh"
    ssh.mkdir()
    testes = tmp_path / "testes-a-distancia"
    testes.mkdir()
    monkeypatch.setattr(td, "SSHD_CONFIG", str(ssh / "sshd_config"))
    monkeypatch.setattr(td, "PASTA_SSH", str(ssh), raising=False)
    monkeypatch.setattr(td, "PASTA_DOS_TESTES", str(testes), raising=False)
    # o registro do Windows vira um caminho de arquivo que não existe: Test-Path só diz "não há"
    monkeypatch.setattr(td, "CHAVE_USERLIST", str(tmp_path / "UserList-de-mentira"))
    return tmp_path


def gravar_o_antes(maquina: Path, **campos) -> Path:
    """Grava o caderninho do antes (como o ligar gravaria) na pasta do teste."""
    antes = {"openssh_ja_existia": False, "sshd_inicio": "", "sshd_rodando": False,
             "regra_larga_existia": False, "regra_larga_ligada": False, "conta_de_outro_existia": False,
             "userlist_existia": True, "pasta_ssh_existia": True, "pasta_ssh_itens": []}
    antes.update(campos)
    arquivo = maquina / "testes-a-distancia" / "antes.json"
    arquivo.write_text(json.dumps(antes), encoding="utf-8")
    return arquivo


def o_passo(passos: list[td.Passo], *pedacos: str, sem: tuple[str, ...] = ()) -> td.Passo:
    """O único passo cujo comando tem todos os `pedacos` e nenhum de `sem`."""
    achados = [p for p in passos if all(x in p.comando for x in pedacos) and not any(x in p.comando for x in sem)]
    assert len(achados) == 1, f"esperava um passo com {pedacos} (sem {sem}); achei {[p.nome for p in achados]}"
    return achados[0]


def get_local_user(descricao: str | None, sid: str = "S-1-5-21-111-1001") -> str:
    """Troca do Get-LocalUser: devolve a conta EditorTestes com a descrição dada (None = não existe)."""
    if descricao is None:
        return "function Get-LocalUser { $null }"
    return ("function Get-LocalUser { [pscustomobject]@{ Name = 'EditorTestes'; Description = '"
            + descricao + "'; SID = [pscustomobject]@{ Value = '" + sid + "' } } }")


# ---------------------------------------------------------------------------------------------------------------
# D-731: desinstalar manda rodar a tarefa "desfazer" e volta logo
# ---------------------------------------------------------------------------------------------------------------

def test_d731_desinstalar_manda_rodar_a_tarefa_desfazer(dados, monkeypatch):
    """D-731 (17/11/2026): ao desinstalar (instalação de verdade), o gancho manda rodar a tarefa "desfazer" dos
    testes à distância, sem pedir licença de administrador e sem esperar. A tarefa da atualização continua sendo
    apagada como antes. Falha no código de antes: o gancho só apagava a tarefa da atualização."""
    falso = ExecutorDeMentira(aplicar_proibido=True)
    monkeypatch.setattr(td, "_executor", falso)
    apagadas = []
    monkeypatch.setattr(atualizacao, "apagar_tarefa", lambda *a, **k: apagadas.append(1) or True)

    atualizacao.ao_desinstalar("1.2.0", portatil=lambda: False)

    assert falso.tarefas, "o gancho de desinstalar não mandou rodar a tarefa desfazer (D-731)"
    assert falso.tarefas == [td.nome_da_tarefa_do_desfazer()]
    assert falso.chamadas == [], "nenhuma pergunta de administrador no gancho"
    assert apagadas == [1], "a tarefa da atualização continua sendo apagada (D-714)"


def test_d731_desinstalar_o_portatil_nao_manda_nada(dados, monkeypatch):
    """D-723 e D-731 (17/11/2026): o pacote portátil do ensaio nunca mexe no Windows, nem ao desinstalar."""
    falso = ExecutorDeMentira(aplicar_proibido=True)
    monkeypatch.setattr(td, "_executor", falso)
    monkeypatch.setattr(atualizacao, "apagar_tarefa", lambda *a, **k: pytest.fail("apagou a tarefa"))
    atualizacao.ao_desinstalar("1.2.0", portatil=lambda: True)
    assert falso.tarefas == [] and falso.chamadas == []


def test_d731_desinstalar_sem_a_tarefa_nao_quebra(dados, monkeypatch):
    """D-731 (17/11/2026): se os testes à distância nunca foram ligados, a tarefa não existe: o gancho anota e
    segue (apaga a tarefa da atualização mesmo assim), sem erro."""
    class SemTarefa(ExecutorDeMentira):
        def rodar_a_tarefa(self, nome):
            raise OSError("ERRO: O sistema não pode encontrar o arquivo especificado.")

    monkeypatch.setattr(td, "_executor", SemTarefa(aplicar_proibido=True))
    apagadas = []
    monkeypatch.setattr(atualizacao, "apagar_tarefa", lambda *a, **k: apagadas.append(1) or True)
    atualizacao.ao_desinstalar("1.2.0", portatil=lambda: False)
    assert apagadas == [1]
    assert "desfazer" in atualizacao.caminho_do_registro().read_text(encoding="utf-8")


def test_d731_o_executor_de_verdade_nao_manda_rodar_sob_o_pytest():
    """D-731 (17/11/2026): a peça de verdade se recusa a mandar rodar a tarefa durante os testes."""
    with pytest.raises(RuntimeError):
        td.ExecutorWindows().rodar_a_tarefa(td.nome_da_tarefa_do_desfazer())
    assert td.TEMPO_MAXIMO_NO_GANCHO < 30, "o gancho de desinstalar tem 30 s (documentação do Velopack)"


# ---------------------------------------------------------------------------------------------------------------
# D-731: o ligar prepara a tarefa "desfazer" com o MESMO plano de desfazer da etapa 5 (uma regra só, §11.12)
# ---------------------------------------------------------------------------------------------------------------

def test_d731_ligar_cria_a_tarefa_desfazer_com_o_mesmo_plano(dados):
    """D-731/D-722 (17/11/2026): o ligar grava o script da tarefa desfazer, e ele é exatamente o
    `plano_de_desfazer` montado (o mesmo da etapa 5). A tarefa roda como o sistema. Falha no código de antes: o
    ligar não criava tarefa nenhuma."""
    passos = td.plano_de_ligar()
    passo = o_passo(passos, "FromBase64String")
    codificado = re.search(r"FromBase64String\('([A-Za-z0-9+/=]+)'\)", passo.comando).group(1)
    script = base64.b64decode(codificado).decode("utf-8")
    assert script == td.montar_script(td.plano_de_desfazer(), td.caminho_do_registro_do_desfazer(),
                                      continuar_depois_de_erro=True)
    assert td.caminho_do_script_do_desfazer() in passo.comando
    assert "Register-ScheduledTask" in passo.comando
    assert "<UserId>S-1-5-18</UserId>" in passo.comando, "a tarefa roda como o sistema"
    assert td.NOME_DA_TAREFA_DO_DESFAZER in passo.comando
    # a tarefa só nasce depois da conta (a licença nega a conta de testes pelo SID dela)
    nomes = [p.comando for p in passos]
    assert nomes.index(passo.comando) > nomes.index(o_passo(passos, "New-LocalUser").comando)


def test_d731_a_conta_comum_manda_rodar_e_a_conta_de_testes_nao(dados):
    """D-731 e D-717 (17/11/2026): a licença da tarefa deixa qualquer conta que entrou no Windows mandá-la rodar
    (o gancho roda na conta do Kaique, sem administrador), menos a conta de testes ("um teste não [...] consegue
    mudar o Windows"). O sistema e os administradores mandam em tudo."""
    passo = o_passo(td.plano_de_ligar(), "FromBase64String")
    assert "SetSecurityDescriptor" in passo.comando
    sddl = re.search(r'"(D:[^"]+)"', passo.comando).group(1)
    assert sddl.startswith("D:(D;;FA;;;$sid)"), "a conta de testes é negada primeiro"
    assert "(A;;FA;;;SY)" in sddl and "(A;;FA;;;BA)" in sddl
    assert "(A;;GRGX;;;AU)" in sddl, "quem entrou no Windows pode ler e mandar rodar"
    assert f"Get-LocalUser -Name {td.NOME_DA_CONTA}" in passo.comando and ".SID.Value" in passo.comando


def test_d731_o_caderninho_fica_onde_o_plano_diz(dados):
    """D-731 (17/11/2026): o caderninho do antes fica na pasta do ProgramData que só o administrador grava."""
    assert td.caminho_do_antes() == r"C:\ProgramData\EditorImpressao\testes-a-distancia\antes.json"
    assert td.caminho_do_script_do_desfazer().startswith(r"C:\ProgramData\EditorImpressao\testes-a-distancia")


@precisa_do_powershell
def test_d731_ligar_anota_o_antes_primeiro_e_so_na_primeira_vez(maquina):
    """D-731 (17/11/2026): o primeiro passo do ligar, antes de instalar o OpenSSH, anota o que já havia no
    computador. Só na primeira vez: um ligar depois de desligar não acha que o OpenSSH "já estava lá" quando foi o
    programa que o pôs. Um caderninho que não foi gravado pelo administrador não vale (é gravado de novo). Falha no
    código de antes: não havia caderninho."""
    passos = td.plano_de_ligar()
    primeiro = passos[0]
    assert td.caminho_do_antes() in primeiro.comando, "o primeiro passo anota o antes"
    assert "Add-WindowsCapability" not in primeiro.comando
    arquivo = maquina / "testes-a-distancia" / "antes.json"

    def rodar(estado_openssh: str, dono: str = "S-1-5-32-544"):
        trocas = {
            "Get-WindowsCapability": "function Get-WindowsCapability { [pscustomobject]@{ State = '"
                                     + estado_openssh + "' } }",
            "Get-Service": "function Get-Service { [pscustomobject]@{ StartType = 'Manual'; Status = 'Running' } }",
            "Get-NetFirewallRule": "function Get-NetFirewallRule { [pscustomobject]@{ Enabled = 'True' } }",
            "Get-LocalUser": get_local_user(None),
            "Get-Acl": ("function Get-Acl { $o = New-Object psobject; $o | Add-Member -MemberType ScriptMethod"
                        " -Name GetOwner -Value { param($t) [pscustomobject]@{ Value = '" + dono + "' } }; $o }"),
        }
        return rodar_no_windows_de_mentira(primeiro.comando, maquina, trocas, anotar=("icacls",))

    codigo, linhas, erro = rodar("Installed")
    assert codigo == 0, erro
    antes = json.loads(arquivo.read_text(encoding="utf-8-sig"))
    assert antes["openssh_ja_existia"] is True
    assert antes["sshd_inicio"] == "Manual" and antes["sshd_rodando"] is True
    assert antes["regra_larga_existia"] is True and antes["regra_larga_ligada"] is True
    assert antes["conta_de_outro_existia"] is False
    icacls = " ".join(chamou(linhas, "icacls"))
    assert "/inheritance:r" in icacls and "/setowner" in icacls, "a pasta fica só de leitura para os comuns"

    # ligar de novo (o OpenSSH agora é o nosso, instalado): o caderninho não muda
    codigo, _, erro = rodar("NotPresent")
    assert codigo == 0, erro
    assert json.loads(arquivo.read_text(encoding="utf-8-sig"))["openssh_ja_existia"] is True

    # um caderninho posto por uma conta comum (dono não é o sistema nem os administradores) não vale
    gravar_o_antes(maquina, openssh_ja_existia=False)
    codigo, _, erro = rodar("Installed", dono="S-1-5-21-999-1001")
    assert codigo == 0, erro
    assert json.loads(arquivo.read_text(encoding="utf-8-sig"))["openssh_ja_existia"] is True


# ---------------------------------------------------------------------------------------------------------------
# B2 e B3: as linhas do sshd_config
# ---------------------------------------------------------------------------------------------------------------

def _passo_do_sshd_no_ligar() -> td.Passo:
    return o_passo(td.plano_de_ligar(), td.SSHD_CONFIG)


@precisa_do_powershell
def test_b2_as_linhas_do_ligar_vao_antes_do_match(maquina):
    """B2 (16/11/2026, plano.md seção 9; consertado em 17/11/2026): o sshd_config de fábrica termina com o bloco
    "Match Group administrators". As linhas do ligar (AllowUsers, PasswordAuthentication, MaxAuthTries) têm de ir
    ANTES do primeiro Match; no fim, valeriam só para os administradores. Falha no código de antes."""
    config = Path(td.SSHD_CONFIG)
    config.write_text(SSHD_CONFIG_DE_FABRICA, encoding="utf-8", newline="")
    codigo, linhas, erro = rodar_no_windows_de_mentira(_passo_do_sshd_no_ligar().comando, maquina,
                                                       anotar=("Restart-Service",))
    assert codigo == 0, erro
    texto = config.read_text(encoding="utf-8").splitlines()
    allow = texto.index(f"AllowUsers {td.NOME_DA_CONTA}")
    match = texto.index("Match Group administrators")
    assert allow < match, "B2: as linhas caíram dentro do bloco Match Group administrators"
    assert texto.index("PasswordAuthentication yes") < match and texto.index("MaxAuthTries 3") < match
    assert chamou(linhas, "Restart-Service"), "o sshd é reiniciado para ler as linhas"


@precisa_do_powershell
def test_b3_ligar_de_novo_nao_repete_as_linhas(maquina):
    """B3 (16/11/2026; consertado em 17/11/2026): ligar duas vezes não repete as linhas do sshd_config. Falha no
    código de antes (cada ligar acrescentava outra cópia)."""
    config = Path(td.SSHD_CONFIG)
    config.write_text(SSHD_CONFIG_DE_FABRICA, encoding="utf-8", newline="")
    for _ in range(2):
        codigo, _, erro = rodar_no_windows_de_mentira(_passo_do_sshd_no_ligar().comando, maquina,
                                                      anotar=("Restart-Service",))
        assert codigo == 0, erro
    texto = config.read_text(encoding="utf-8").splitlines()
    assert texto.count(f"AllowUsers {td.NOME_DA_CONTA}") == 1


@precisa_do_powershell
def test_d731_sshd_config_sai_pelas_marcas_e_a_linha_de_fabrica_fica(maquina):
    """D-731 (17/11/2026): o desfazer tira só o que o ligar pôs no sshd_config. A linha de fábrica
    "#PasswordAuthentication yes" fica: o arquivo volta igual, letra por letra. Falha no código de antes (o
    desfazer apagava toda linha com "PasswordAuthentication yes", inclusive a de fábrica)."""
    config = Path(td.SSHD_CONFIG)
    config.write_text(SSHD_CONFIG_DE_FABRICA, encoding="utf-8", newline="")
    codigo, _, erro = rodar_no_windows_de_mentira(_passo_do_sshd_no_ligar().comando, maquina,
                                                  anotar=("Restart-Service",))
    assert codigo == 0, erro
    desfazer = o_passo(td.plano_de_desfazer(), td.SSHD_CONFIG, sem=("Service",))
    assert "PasswordAuthentication yes" not in desfazer.comando, "o desfazer não procura a linha solta"
    codigo, _, erro = rodar_no_windows_de_mentira(desfazer.comando, maquina)
    assert codigo == 0, erro
    assert config.read_bytes() == SSHD_CONFIG_DE_FABRICA.encode("utf-8")


# ---------------------------------------------------------------------------------------------------------------
# B3: ligar depois de desligar
# ---------------------------------------------------------------------------------------------------------------

NEW_LOCAL_USER_QUE_JA_EXISTE = ("function New-LocalUser { throw 'A conta EditorTestes ja existe.' }")


@precisa_do_powershell
def test_b3_ligar_depois_de_desligar_reativa_a_conta(maquina):
    """B3 (16/11/2026; consertado em 17/11/2026): depois de desligar, a conta de testes existe (desativada).
    Ligar de novo reativa a conta e troca a senha, em vez de tentar criá-la e parar no erro. Falha no código de
    antes (o New-LocalUser dava "já existe")."""
    passo = o_passo(td.plano_de_ligar(), "New-LocalUser")
    trocas = {"Get-LocalUser": get_local_user(DESCRICAO_NOSSA), "New-LocalUser": NEW_LOCAL_USER_QUE_JA_EXISTE}
    codigo, linhas, erro = rodar_no_windows_de_mentira(
        passo.comando, maquina, trocas, anotar=("Enable-LocalUser", "Set-LocalUser", "Add-LocalGroupMember"))
    assert codigo == 0, f"B3: ligar de novo parou no erro: {erro}"
    assert chamou(linhas, "Enable-LocalUser"), "a conta desativada é reativada"
    assert "-Password" in " ".join(chamou(linhas, "Set-LocalUser")), "a senha nova entra"
    assert "$SenhaDosTestes" in passo.comando, "a senha entra pela variável, nunca pelo texto"


@precisa_do_powershell
def test_b3_ligar_numa_conta_que_nao_e_nossa_para(maquina):
    """B3 (17/11/2026): se já existe uma conta EditorTestes que o programa não criou, o ligar para, sem mexer
    nela (nada do dono muda)."""
    passo = o_passo(td.plano_de_ligar(), "New-LocalUser")
    trocas = {"Get-LocalUser": get_local_user("Conta do Kaique"), "New-LocalUser": NEW_LOCAL_USER_QUE_JA_EXISTE}
    codigo, linhas, _ = rodar_no_windows_de_mentira(
        passo.comando, maquina, trocas, anotar=("Enable-LocalUser", "Set-LocalUser", "Add-LocalGroupMember"))
    assert codigo != 0
    assert not chamou(linhas, "Enable-LocalUser") and not chamou(linhas, "Set-LocalUser")


@precisa_do_powershell
def test_b3_conta_nova_continua_sem_administrador(maquina):
    """D-717 (17/11/2026, não muda com o B3): sem conta, o ligar cria e põe só no grupo Usuários."""
    passo = o_passo(td.plano_de_ligar(), "New-LocalUser")
    codigo, linhas, erro = rodar_no_windows_de_mentira(
        passo.comando, maquina, {"Get-LocalUser": get_local_user(None)},
        anotar=("New-LocalUser", "Enable-LocalUser", "Set-LocalUser", "Add-LocalGroupMember"))
    assert codigo == 0, erro
    assert chamou(linhas, "New-LocalUser") and not chamou(linhas, "Enable-LocalUser")
    assert td.SID_USUARIOS in " ".join(chamou(linhas, "Add-LocalGroupMember"))


@precisa_do_powershell
def test_b3_ligar_de_novo_refaz_a_regra_do_firewall(maquina):
    """B3 (17/11/2026): ligar de novo sem ter desligado (ex.: pôr a senha outra vez) não para na regra do firewall
    que já existe: ela é apagada e feita de novo, igual. Falha no código de antes."""
    passo = o_passo(td.plano_de_ligar(), "New-NetFirewallRule")
    codigo, linhas, erro = rodar_no_windows_de_mentira(
        passo.comando, maquina, anotar=("Remove-NetFirewallRule", "New-NetFirewallRule"))
    assert codigo == 0, erro
    ordem = [l.split()[1] for l in linhas if l.startswith("CHAMOU ")]
    assert ordem == ["Remove-NetFirewallRule", "New-NetFirewallRule"]


# ---------------------------------------------------------------------------------------------------------------
# B4: desligar devolve o OpenSSH do dono como estava
# ---------------------------------------------------------------------------------------------------------------

SERVICOS = ("Stop-Service", "Set-Service", "Start-Service", "Restart-Service", "Enable-NetFirewallRule")


@precisa_do_powershell
def test_b4_desligar_devolve_o_openssh_que_ja_era_do_dono(maquina):
    """B4 (16/11/2026; consertado em 17/11/2026): se o OpenSSH já era do dono antes do ligar, desligar não o
    desativa: devolve o início e o estado do serviço como estavam, religa a regra larga se estava ligada e tira as
    nossas linhas do sshd_config. Falha no código de antes (Set-Service -StartupType Disabled sempre)."""
    gravar_o_antes(maquina, openssh_ja_existia=True, sshd_inicio="Automatic", sshd_rodando=True,
                   regra_larga_existia=True, regra_larga_ligada=True)
    config = Path(td.SSHD_CONFIG)
    config.write_text(SSHD_CONFIG_DE_FABRICA, encoding="utf-8", newline="")
    rodar_no_windows_de_mentira(_passo_do_sshd_no_ligar().comando, maquina, anotar=("Restart-Service",))

    passo = td.plano_de_desligar()[0]
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=SERVICOS)
    assert codigo == 0, erro
    set_service = " ".join(chamou(linhas, "Set-Service"))
    assert "Disabled" not in set_service, "B4: desligou o OpenSSH que era do dono"
    assert "-StartupType Automatic" in set_service, "o início volta a ser o de antes"
    assert chamou(linhas, "Restart-Service") or chamou(linhas, "Start-Service"), "estava rodando: continua"
    assert chamou(linhas, "Enable-NetFirewallRule"), "a regra larga do dono volta a ficar ligada"
    assert config.read_bytes() == SSHD_CONFIG_DE_FABRICA.encode("utf-8"), "as nossas linhas saem"


@precisa_do_powershell
@pytest.mark.parametrize("com_caderninho", [True, False])
def test_b4_desligar_o_openssh_que_o_programa_pos_continua_parando(maquina, com_caderninho):
    """D-705 e B4 (17/11/2026): se o OpenSSH foi o programa que pôs (ou não há caderninho), desligar continua
    como antes: para o serviço e o tira do arranque do Windows."""
    if com_caderninho:
        gravar_o_antes(maquina, openssh_ja_existia=False)
    codigo, linhas, erro = rodar_no_windows_de_mentira(td.plano_de_desligar()[0].comando, maquina, anotar=SERVICOS)
    assert codigo == 0, erro
    assert chamou(linhas, "Stop-Service")
    assert "-StartupType Disabled" in " ".join(chamou(linhas, "Set-Service"))


# ---------------------------------------------------------------------------------------------------------------
# D-731: o desfazer só tira o que foi nosso
# ---------------------------------------------------------------------------------------------------------------

@precisa_do_powershell
@pytest.mark.parametrize("caderninho, tira", [
    ({"openssh_ja_existia": True}, False),   # o OpenSSH era do dono: fica
    (None, False),                          # sem caderninho: o OpenSSH nunca é tirado
    ({"openssh_ja_existia": False}, True),  # foi o programa que pôs: sai
])
def test_d731_openssh_so_sai_se_foi_o_programa_que_pos(maquina, caderninho, tira):
    """D-731 (17/11/2026): "o comando de longe (Servidor OpenSSH, se foi o programa que instalou)". O desfazer só
    tira o OpenSSH se o caderninho do antes diz que ele não existia. Sem caderninho, nunca. Falha no código de
    antes (o Remove-WindowsCapability era sempre)."""
    if caderninho is not None:
        gravar_o_antes(maquina, **caderninho)
    passo = o_passo(td.plano_de_desfazer(), "Remove-WindowsCapability")
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=("Remove-WindowsCapability",))
    assert codigo == 0, erro
    assert bool(chamou(linhas, "Remove-WindowsCapability")) is tira


@precisa_do_powershell
@pytest.mark.parametrize("regra_existia, apaga", [(True, False), (False, True)])
def test_d731_a_regra_larga_so_sai_se_veio_com_o_nosso_openssh(maquina, regra_existia, apaga):
    """D-731 (17/11/2026): a regra larga do OpenSSH só é apagada se veio com o OpenSSH que o programa pôs."""
    gravar_o_antes(maquina, openssh_ja_existia=False, regra_larga_existia=regra_existia)
    passo = o_passo(td.plano_de_desfazer(), f"Remove-NetFirewallRule -Name {td.REGRA_LARGA_DO_OPENSSH}")
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=("Remove-NetFirewallRule",))
    assert codigo == 0, erro
    assert bool(chamou(linhas, "Remove-NetFirewallRule")) is apaga


@precisa_do_powershell
@pytest.mark.parametrize("descricao, apaga", [(DESCRICAO_NOSSA, True), ("Conta do Kaique", False), (None, False)])
def test_d731_a_conta_so_sai_se_for_a_nossa(maquina, descricao, apaga):
    """D-731 (17/11/2026): a conta EditorTestes só é apagada se for a nossa (a descrição do ligar e o caderninho).
    Falha no código de antes (o Remove-LocalUser era sempre)."""
    gravar_o_antes(maquina)
    passo = o_passo(td.plano_de_desfazer(), "Remove-LocalUser")
    codigo, linhas, erro = rodar_no_windows_de_mentira(
        passo.comando, maquina, {"Get-LocalUser": get_local_user(descricao)}, anotar=("Remove-LocalUser",))
    assert codigo == 0, erro
    assert bool(chamou(linhas, "Remove-LocalUser")) is apaga


@precisa_do_powershell
def test_d731_a_conta_de_outro_que_existia_antes_fica(maquina):
    """D-731 (17/11/2026): se o caderninho anotou que já havia uma conta EditorTestes de outro, ela fica."""
    gravar_o_antes(maquina, conta_de_outro_existia=True)
    passo = o_passo(td.plano_de_desfazer(), "Remove-LocalUser")
    codigo, linhas, erro = rodar_no_windows_de_mentira(
        passo.comando, maquina, {"Get-LocalUser": get_local_user(DESCRICAO_NOSSA)}, anotar=("Remove-LocalUser",))
    assert codigo == 0, erro
    assert not chamou(linhas, "Remove-LocalUser")


@precisa_do_powershell
def test_d731_o_perfil_e_achado_pelo_sid(maquina):
    """D-731 (17/11/2026): o perfil apagado é o da conta de testes, achado pelo número de identidade dela (SID), e
    não pelo nome da pasta: uma pasta C:\\Users\\EditorTestes de outra conta fica. Falha no código de antes
    (procurava por LocalPath -like '*\\EditorTestes')."""
    gravar_o_antes(maquina)
    passo = o_passo(td.plano_de_desfazer(), "Win32_UserProfile")
    trocas = {
        "Get-LocalUser": get_local_user(DESCRICAO_NOSSA, sid="S-1-5-21-111-1001"),
        "Get-CimInstance": ("function Get-CimInstance {"
                            " [pscustomobject]@{ SID = 'S-1-5-21-111-1001'; LocalPath = 'X:\\Users\\EditorTestes.PC' };"
                            " [pscustomobject]@{ SID = 'S-1-5-21-222-1002'; LocalPath = 'X:\\Users\\EditorTestes' } }"),
        "Remove-CimInstance": ("function Remove-CimInstance { foreach ($i in $input) {"
                               " Write-Host ('CHAMOU Remove-CimInstance ' + $i.SID) } }"),
    }
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, trocas)
    assert codigo == 0, erro
    assert chamou(linhas, "Remove-CimInstance") == ["CHAMOU Remove-CimInstance S-1-5-21-111-1001"]


@precisa_do_powershell
@pytest.mark.parametrize("pasta_existia", [True, False])
def test_d731_da_pasta_ssh_so_sai_o_que_nasceu_depois(maquina, pasta_existia):
    """D-731 (17/11/2026): com o OpenSSH nosso, da pasta C:\\ProgramData\\ssh sai só o que não estava lá antes; a
    pasta só sai se não existia (no PC do Samuel ela já existe). Falha no código de antes (não havia o passo)."""
    ssh = maquina / "ssh"
    (ssh / "do-dono.txt").write_text("do dono", encoding="utf-8")
    gravar_o_antes(maquina, openssh_ja_existia=False, pasta_ssh_existia=pasta_existia,
                   pasta_ssh_itens=["do-dono.txt"] if pasta_existia else [])
    (ssh / "ssh_host_ed25519_key").write_text("chave", encoding="utf-8")
    (ssh / "logs").mkdir()
    (ssh / "logs" / "sshd.log").write_text("registro", encoding="utf-8")
    passo = o_passo(td.plano_de_desfazer(), td.PASTA_SSH, "Remove-Item")
    codigo, _, erro = rodar_no_windows_de_mentira(passo.comando, maquina)
    assert codigo == 0, erro
    if pasta_existia:
        assert sorted(p.name for p in ssh.iterdir()) == ["do-dono.txt"]
    else:
        assert not ssh.exists()


# ---------------------------------------------------------------------------------------------------------------
# D-731: o script do desfazer continua depois de um erro e se apaga só se tudo deu certo
# ---------------------------------------------------------------------------------------------------------------

@precisa_do_powershell
def test_d731_o_desfazer_continua_depois_de_um_erro(maquina):
    """D-731 (17/11/2026): no desfazer, um passo que falha não impede os outros; a tarefa e o caderninho só se
    apagam se tudo deu certo (para dar para rodar de novo). Falha no código de antes (o montador parava no
    primeiro erro e não estava em core/testes_a_distancia)."""
    registro = maquina / "o-que-foi-desfeito.txt"
    passos = [td.Passo("um", "throw 'falhou'"), td.Passo("dois", "Write-Output 'dois'"),
              td.Passo("fim", "Write-Output 'FIM'", so_se_tudo_certo=True)]
    script = maquina / "desfazer.ps1"
    script.write_text(td.montar_script(passos, str(registro), continuar_depois_de_erro=True), encoding="utf-8")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
                            str(script)], capture_output=True, text=True, timeout=120)
    linhas = registro.read_text(encoding="utf-8-sig", errors="replace").splitlines()
    assert any(l.startswith("ERRO | um") for l in linhas)
    assert "OK   | dois" in linhas, "o passo seguinte rodou"
    assert any(l.startswith("PULADO | fim") for l in linhas) and "FIM" not in feito.stdout
    assert feito.returncode != 0


@precisa_do_powershell
def test_script_sem_senha_nao_procura_o_arquivo_da_senha(maquina):
    """Achado de 17/11/2026 (impedia a tarefa desfazer, que roda sem senha): o script montado lia sempre o
    arquivo da senha, que só existe quando um passo precisa dela. Sem ele, a primeira linha dava erro e nada rodava
    (o desligar e o desfazer, que não têm senha). Falha no código de antes."""
    registro = maquina / "registro.txt"
    script = maquina / "sem-senha.ps1"
    script.write_text(td.montar_script([td.Passo("um", "Write-Output 1")], str(registro)), encoding="utf-8")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File",
                            str(script)], capture_output=True, text=True, timeout=120)
    assert feito.returncode == 0, feito.stderr
    assert "OK   | um" in registro.read_text(encoding="utf-8-sig").splitlines()


# ---------------------------------------------------------------------------------------------------------------
# D-731: nunca os projetos do Kaique; tudo em ASCII
# ---------------------------------------------------------------------------------------------------------------

def _todos_os_comandos() -> list[str]:
    comandos = [p.comando for p in td.plano_de_ligar() + td.plano_de_desligar() + td.plano_de_desfazer()]
    comandos.append(td.montar_script(td.plano_de_desfazer(), td.caminho_do_registro_do_desfazer(),
                                     continuar_depois_de_erro=True))
    return comandos


def test_d731_nunca_toca_os_projetos_do_kaique(dados):
    """D-731 (17/11/2026): "Os projetos do Kaique (%LOCALAPPDATA%\\EditorImpressao) continuam lá". Nenhum comando
    de ligar, desligar ou desfazer cita a pasta dele, nem C:\\Users (o perfil é achado pelo SID)."""
    for comando in _todos_os_comandos():
        for proibido in ("LOCALAPPDATA", "AppData", "C:\\Users", "LocalPath"):
            assert proibido.lower() not in comando.lower(), f"um comando cita {proibido}"


def test_os_comandos_sao_ascii(dados):
    """17/11/2026: o PowerShell do Windows lê o script sem marca de UTF-8 como ANSI; os comandos ficam em ASCII."""
    for comando in _todos_os_comandos():
        assert comando.isascii()


@precisa_do_powershell
def test_os_scripts_montados_sao_powershell_sem_erro_de_escrita(tmp_path, dados):
    """17/11/2026: os scripts do ligar, do desligar e do desfazer (e o do desfazer de dentro do ligar) passam
    pelo leitor do PowerShell sem erro de escrita. Só LÊ o texto (Parser.ParseFile): nada é executado."""
    scripts = {
        "ligar": td.montar_script(td.plano_de_ligar(), str(tmp_path / "r.txt"), str(tmp_path / "s.dpapi")),
        "desligar": td.montar_script(td.plano_de_desligar(), str(tmp_path / "r.txt")),
        "desfazer": td.montar_script(td.plano_de_desfazer(), td.caminho_do_registro_do_desfazer(),
                                     continuar_depois_de_erro=True),
    }
    for nome, texto in scripts.items():
        arquivo = tmp_path / f"{nome}.ps1"
        arquivo.write_text(texto, encoding="utf-8-sig")
        ler = ("$e = $null; [System.Management.Automation.Language.Parser]::ParseFile('" + str(arquivo)
               + "', [ref]$null, [ref]$e) | Out-Null; $e | ForEach-Object { $_.Message }")
        feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", ler],
                               capture_output=True, text=True, timeout=120)
        assert feito.returncode == 0 and not feito.stdout.strip(), f"{nome}: {feito.stdout} {feito.stderr}"


@precisa_do_powershell
@pytest.mark.parametrize("chave_existe", [True, False])
def test_b5_esconder_a_conta_nao_recria_a_chave_userlist(maquina, monkeypatch, chave_existe):
    """B5 (achado 17/11/2026, consertado em 17/11/2026): o passo que esconde a conta fazia
    `New-Item -Path ...UserList -Force`; numa chave que já existe, isso pode recriá-la e apagar as outras contas
    escondidas do dono. Agora a chave só é criada se não existe; o valor EditorTestes entra do mesmo jeito.
    Falha no código de antes (o New-Item era sempre)."""
    chave = maquina / "UserList-do-dono"
    if chave_existe:
        chave.mkdir()  # o Test-Path de verdade diz "existe"
    monkeypatch.setattr(td, "CHAVE_USERLIST", str(chave))
    passo = o_passo(td.plano_de_ligar(), "New-ItemProperty")
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=("New-Item", "New-ItemProperty"))
    assert codigo == 0, erro
    assert bool(chamou(linhas, "New-Item")) is (not chave_existe), "B5: a chave do dono não pode ser recriada"
    assert f"-Name {td.NOME_DA_CONTA} -Value 0" in " ".join(chamou(linhas, "New-ItemProperty"))


# ---------------------------------------------------------------------------------------------------------------
# D-731, pergunta (a) do relatório da construção (pedido da gerente, 17/11/2026): a tarefa "desfazer" existe
# SEMPRE (nasce na pergunta do Windows da primeira abertura) e apaga também a tarefa da atualização e a si mesma.
# ---------------------------------------------------------------------------------------------------------------

class ExecutorDaPrimeiraAbertura(ExecutorDeMentira):
    """Anota também o que o --preparar-o-computador (já como administrador) mandaria aplicar."""

    def __init__(self) -> None:
        super().__init__(aplicar_proibido=True)
        self.ja_como_administrador: list[list[td.Passo]] = []

    def aplicar_ja_como_administrador(self, passos):
        self.ja_como_administrador.append(list(passos))
        return td.Resultado(True, passos=passos)


class _GerenteInstalado:
    def get_is_portable(self):
        return False


def _script_gravado(passo: td.Passo) -> str:
    codificado = re.search(r"FromBase64String\('([A-Za-z0-9+/=]+)'\)", passo.comando).group(1)
    return base64.b64decode(codificado).decode("utf-8")


def _tarefa_da_atualizacao() -> tuple[str, str]:
    pasta, nome = atualizacao.NOME_DA_TAREFA.rsplit("\\", 1)
    return nome, f"\\{pasta}\\"


@precisa_do_powershell
def test_d731a_sem_os_testes_ligados_desinstalar_apaga_a_tarefa_da_atualizacao(maquina, monkeypatch):
    """D-731 ("o notebook fica como era antes de instalar"), pergunta (a) do relatório da construção (17/11/2026).
    Defeito: a tarefa "desfazer" só nascia quando os testes à distância eram ligados, e o gancho de desinstalar,
    sem administrador, não consegue apagar a tarefa da atualização ("Procurar versao nova"): ela ficava no
    Windows. Agora a pergunta do Windows da primeira abertura (--preparar-o-computador) cria SEMPRE a tarefa
    "desfazer", com o plano curto; desinstalar manda rodá-la, e ela apaga a tarefa da atualização e a si mesma.
    Falha no código de antes: a primeira abertura não criava a tarefa "desfazer"."""
    falso = ExecutorDaPrimeiraAbertura()
    monkeypatch.setattr(td, "_executor", falso)
    criadas = []
    monkeypatch.setattr(atualizacao, "criar_tarefa", lambda *a, **k: criadas.append("ajudante") or True)

    # 1. a primeira abertura, dentro da pergunta do Windows, sem a senha dos testes
    assert atualizacao.preparar_como_administrador(_GerenteInstalado(), preparar=lambda g: None) == 0
    assert criadas == ["ajudante"]
    assert falso.ja_como_administrador, "a primeira abertura não criou a tarefa desfazer (D-731, pergunta (a))"
    assert falso.chamadas == [], "nenhuma pergunta do Windows a mais: já roda como administrador"
    passos = falso.ja_como_administrador[0]
    script = _script_gravado(o_passo(passos, "FromBase64String"))
    assert script == td.montar_script(td.plano_de_desfazer(testes_ligados=False),
                                      td.caminho_do_registro_do_desfazer(), continuar_depois_de_erro=True)

    # 2. desinstalar: o gancho só manda rodar a tarefa desfazer
    monkeypatch.setattr(atualizacao, "apagar_tarefa", lambda *a, **k: False)  # sem administrador, falha
    atualizacao.ao_desinstalar("1.2.0", portatil=lambda: False)
    assert falso.tarefas == [td.nome_da_tarefa_do_desfazer()]

    # 3. a tarefa roda o script gravado: apaga a tarefa da atualização e a si mesma, e nada dos testes
    codigo, linhas, erro = rodar_no_windows_de_mentira(script, maquina, anotar=("Unregister-ScheduledTask",))
    assert codigo == 0, erro
    apagadas = " | ".join(chamou(linhas, "Unregister-ScheduledTask"))
    nome, pasta = _tarefa_da_atualizacao()
    assert f"-TaskName {nome} -TaskPath {pasta}" in apagadas, "a tarefa da atualização tem de sair"
    assert f"-TaskName {td.NOME_DA_TAREFA_DO_DESFAZER} -TaskPath {pasta}" in apagadas, "e o desfazer, a si mesmo"
    for dos_testes in ("Set-Service", "Stop-Service", "Remove-LocalUser", "Remove-WindowsCapability",
                       "NetFirewallRule", td.SSHD_CONFIG):
        assert dos_testes not in script, f"sem os testes ligados, o desfazer não mexe em {dos_testes}"


@precisa_do_powershell
def test_d731a_com_os_testes_ligados_o_desfazer_inteiro_apaga_tambem_a_tarefa_da_atualizacao(maquina):
    """D-731, pergunta (a) (17/11/2026): o desfazer inteiro (o que o ligar grava) também apaga a tarefa da
    atualização, mesmo se um passo dos testes falhou; e só se apaga a si mesmo se tudo deu certo."""
    plano = td.plano_de_desfazer()
    nome, pasta = _tarefa_da_atualizacao()
    passo = o_passo(plano, f"-TaskName '{nome}'")
    assert not passo.so_se_tudo_certo, "a tarefa da atualização sai sempre"
    fim = o_passo(plano, f"-TaskName '{td.NOME_DA_TAREFA_DO_DESFAZER}'")
    assert fim.so_se_tudo_certo and plano[-1] is fim
    # o que o plano curto faz é exatamente o fim do plano inteiro (uma regra só)
    curto = td.plano_de_desfazer(testes_ligados=False)
    assert [p.comando for p in plano[-len(curto):]] == [p.comando for p in curto]
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=("Unregister-ScheduledTask",))
    assert codigo == 0, erro
    assert f"-TaskName {nome} -TaskPath {pasta}" in " ".join(chamou(linhas, "Unregister-ScheduledTask"))


@precisa_do_powershell
@pytest.mark.parametrize("ja_ligados", [False, True])
def test_d731a_a_primeira_abertura_nao_troca_o_desfazer_inteiro_pelo_curto(maquina, monkeypatch, ja_ligados):
    """D-731, pergunta (a) (17/11/2026): se os testes já foram ligados (há o caderninho do antes), a pergunta da
    primeira abertura (que volta depois de um "Não", D-741) deixa a tarefa desfazer como está: gravar o plano
    curto por cima deixaria a conta de testes e o OpenSSH para trás ao desinstalar."""
    monkeypatch.setattr(td, "_comando_preparar_o_desfazer", lambda testes_ligados=True: "Write-Output 'CRIOU'")
    if ja_ligados:
        gravar_o_antes(maquina)
    passo = o_passo(td.plano_de_preparar_o_desfazer(), "CRIOU")
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina)
    assert codigo == 0, erro
    assert ("CRIOU" in linhas) is (not ja_ligados)


@precisa_do_powershell
def test_d731a_a_pasta_do_desfazer_fica_protegida(maquina):
    """D-731, pergunta (a) (17/11/2026): o script do desfazer roda como o sistema; a pasta dele é criada pela
    primeira abertura com dono "administradores" e só de leitura para as contas comuns (o mesmo icacls do ligar)."""
    (maquina / "testes-a-distancia").rmdir()  # a pasta vazia que a fixture criou: a primeira abertura a cria
    passo = td.plano_de_preparar_o_desfazer()[0]
    codigo, linhas, erro = rodar_no_windows_de_mentira(passo.comando, maquina, anotar=("icacls",))
    assert codigo == 0, erro
    assert (maquina / "testes-a-distancia").is_dir()
    icacls = " ".join(chamou(linhas, "icacls"))
    assert "/setowner" in icacls and "/inheritance:r" in icacls and f"*{td.SID_USUARIOS}:(OI)(CI)RX" in icacls
    assert td.plano_de_ligar()[0].comando.endswith(td._comando_proteger_a_pasta()), "o mesmo icacls do ligar"


def test_d731a_a_licenca_nega_a_conta_de_testes_so_quando_ela_existe(dados):
    """D-717 e D-731 (17/11/2026): na primeira abertura a conta de testes ainda não existe; a tarefa nasce sem a
    negação e o ligar a refaz já negando a conta. Quem entrou no Windows continua podendo mandar rodar."""
    passo = o_passo(td.plano_de_preparar_o_desfazer(), "FromBase64String")
    assert "if ($u) { $sid = $u.SID.Value; $licenca = \"D:(D;;FA;;;$sid)" in passo.comando
    assert "else { $licenca = 'D:(A;;FA;;;SY)(A;;FA;;;BA)(A;;GRGX;;;AU)' }" in passo.comando
    assert o_passo(td.plano_de_ligar(), "FromBase64String").comando.count("SetSecurityDescriptor($licenca, 0)") == 1


def test_d731a_o_executor_de_verdade_nao_aplica_sob_o_pytest():
    """D-731, pergunta (a) (17/11/2026): a peça de verdade se recusa a rodar durante os testes."""
    with pytest.raises(RuntimeError):
        td.ExecutorWindows().aplicar_ja_como_administrador(td.plano_de_preparar_o_desfazer())


def test_d731a_nunca_toca_os_projetos_do_kaique_e_tudo_em_ascii(dados):
    """D-731 (17/11/2026): o que a primeira abertura grava também nunca cita a pasta do Kaique, e é ASCII."""
    comandos = [p.comando for p in td.plano_de_preparar_o_desfazer()]
    comandos.append(td.montar_script(td.plano_de_desfazer(testes_ligados=False),
                                     td.caminho_do_registro_do_desfazer(), continuar_depois_de_erro=True))
    for comando in comandos:
        assert comando.isascii()
        for proibido in ("LOCALAPPDATA", "AppData", "C:\\Users", "LocalPath"):
            assert proibido.lower() not in comando.lower()


@precisa_do_powershell
def test_d731a_os_scripts_novos_sao_powershell_sem_erro_de_escrita(tmp_path, dados):
    """17/11/2026: o script da primeira abertura e o desfazer curto passam pelo leitor do PowerShell (só lê)."""
    scripts = {
        "preparar": td.montar_script(td.plano_de_preparar_o_desfazer(), str(tmp_path / "r.txt")),
        "curto": td.montar_script(td.plano_de_desfazer(testes_ligados=False), td.caminho_do_registro_do_desfazer(),
                                  continuar_depois_de_erro=True),
    }
    for nome, texto in scripts.items():
        arquivo = tmp_path / f"{nome}.ps1"
        arquivo.write_text(texto, encoding="utf-8-sig")
        ler = ("$e = $null; [System.Management.Automation.Language.Parser]::ParseFile('" + str(arquivo)
               + "', [ref]$null, [ref]$e) | Out-Null; $e | ForEach-Object { $_.Message }")
        feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", ler],
                               capture_output=True, text=True, timeout=120)
        assert feito.returncode == 0 and not feito.stdout.strip(), f"{nome}: {feito.stdout} {feito.stderr}"
