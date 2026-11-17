"""D-731 ("o notebook fica como era antes de instalar"), 17/11/2026: a pasta do Agendador sai, so se vazia.

Depois de desinstalar, o desfazer ja apagava a tarefa da atualizacao e a si mesmo, mas a pasta vazia
"EditorImpressao" ficava no Agendador de Tarefas do Windows (pergunta 1 do relatorio
relatorios/frente-kaique-2026-11-16/d731-construcao/). Agora o ultimo passo do desfazer apaga essa pasta, SO se
ela ficou vazia (nenhuma tarefa, nem escondida, e nenhuma subpasta).

COMO SE PROVA SEM TOCAR O WINDOWS:
  1. o executor de mentira (so anota os passos) mostra que o desfazer manda o passo da pasta, no fim;
  2. o comando desse passo roda num powershell.exe em que o servico do Agendador (o objeto COM
     Schedule.Service), o Unregister-ScheduledTask, o Remove-Item e o Anotar foram TROCADOS por funcoes que so
     escrevem "CHAMOU ...". No PowerShell, uma funcao com o mesmo nome ganha do comando de verdade.
     PROTECAO: `_rodar_com_o_agendador_de_mentira` se recusa a rodar se o comando citar o disco C: ou um
     comando do Windows que nao esteja trocado.
Cada prova falha no codigo de antes (fd9f1f58): o desfazer nao tocava na pasta.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from core import testes_a_distancia as td

POWERSHELL = shutil.which("powershell")
precisa_do_powershell = pytest.mark.skipif(
    sys.platform != "win32" or not POWERSHELL, reason="o Agendador de mentira usa o powershell.exe")


class ExecutorDeMentira(td.Executor):
    """So anota os passos (como em tests/test_decisoes_desinstalar.py)."""

    def __init__(self) -> None:
        self.chamadas: list[list[td.Passo]] = []

    def aplicar(self, passos, senha):
        self.chamadas.append(list(passos))
        return td.Resultado(True, passos=passos)

    def rodar_a_tarefa(self, nome):
        return td.Resultado(True)

    def aplicar_ja_como_administrador(self, passos):
        self.chamadas.append(list(passos))
        return td.Resultado(True, passos=passos)


@pytest.fixture
def maquina(tmp_path, monkeypatch):
    """A pasta dos testes (caderninho, script e registro do desfazer) vira uma pasta do teste."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "LocalAppData"))
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    testes = tmp_path / "testes-a-distancia"
    testes.mkdir()
    monkeypatch.setattr(td, "PASTA_DOS_TESTES", str(testes), raising=False)
    return tmp_path


def _o_ultimo_passo(passos: list[td.Passo]) -> td.Passo:
    fim = passos[-1]
    assert f"-TaskName '{td.NOME_DA_TAREFA_DO_DESFAZER}'" in fim.comando, "o ultimo passo e o da tarefa do desfazer"
    return fim


def _agendador_de_mentira(tarefas: int, subpastas: int, existe: bool = True) -> str:
    """O New-Object do teste: para -ComObject devolve um Agendador que so anota (nunca o de verdade)."""
    pasta = ("[pscustomobject]@{}" if existe else "$null")
    return "\n".join([
        "function New-Object { param([string]$TypeName, [switch]$ComObject, [string]$ProgId)",
        "  $agenda = [pscustomobject]@{}",
        "  $agenda | Add-Member -MemberType ScriptMethod -Name Connect -Value { Write-Host 'CHAMOU Connect' }",
        "  $agenda | Add-Member -MemberType ScriptMethod -Name GetFolder -Value { param($p)",
        "    if ($p -eq '\\') { $raiz = [pscustomobject]@{}",
        "      $raiz | Add-Member -MemberType ScriptMethod -Name DeleteFolder -Value { param($n, $f)",
        "        Write-Host ('CHAMOU DeleteFolder ' + $n) }",
        "      return $raiz }",
        f"    $pasta = {pasta}",
        "    if (-not $pasta) { throw 'a pasta nao existe' }",
        "    $pasta | Add-Member -MemberType ScriptMethod -Name GetTasks -Value { param($f)",
        f"      Write-Host ('CHAMOU GetTasks ' + $f); return [pscustomobject]@{{ Count = {tarefas} }} }}",
        "    $pasta | Add-Member -MemberType ScriptMethod -Name GetFolders -Value { param($f)",
        f"      return [pscustomobject]@{{ Count = {subpastas} }} }}",
        "    return $pasta }",
        "  return $agenda }",
    ])


def _rodar_com_o_agendador_de_mentira(comando: str, pasta: Path, tarefas: int, subpastas: int,
                                      existe: bool = True) -> tuple[int, list[str], str]:
    # --- a protecao: nada de verdade do Windows sem troca ---
    assert "C:\\" not in comando and "c:\\" not in comando, "o comando cita o disco C: (caminho nao trocado)"
    trocados = {"New-Object", "Unregister-ScheduledTask", "Remove-Item", "Anotar"}
    for nome in set(re.findall(r"\b[A-Z][a-z]+-[A-Z][A-Za-z]+\b", comando)):
        assert nome in trocados, f"'{nome}' mudaria o Windows de verdade e nao tem troca"
    for programa in ("schtasks", "icacls", "reg", "cmd"):
        assert not re.search(rf"(?<![\w$-]){programa}(\.exe)?(?![\w-])", comando, re.IGNORECASE), programa
    script = pasta / "agendador_de_mentira.ps1"
    script.write_text("\n".join([
        "$ErrorActionPreference = 'Stop'",
        _agendador_de_mentira(tarefas, subpastas, existe),
        "function Unregister-ScheduledTask { Write-Host ('CHAMOU Unregister-ScheduledTask ' + ($args -join ' ')) }",
        "function Remove-Item { Write-Host ('CHAMOU Remove-Item ' + ($args -join ' ')) }",
        "function Anotar($t) { Write-Host ('ANOTOU ' + $t) }",
        comando]), encoding="utf-8-sig")
    feito = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                            "-File", str(script)], capture_output=True, text=True, timeout=120,
                           encoding="utf-8", errors="replace")
    return feito.returncode, feito.stdout.splitlines(), feito.stderr


def test_d731_o_desfazer_pelo_executor_termina_com_a_pasta_do_agendador(maquina, monkeypatch):
    """Pelo executor de mentira: os dois desfazer (com e sem os testes ligados) terminam no mesmo ultimo passo,
    que apaga a tarefa do desfazer e, depois, a pasta das tarefas se ela ficou vazia. Falha antes (fd9f1f58):
    nenhum passo falava da pasta."""
    falso = ExecutorDeMentira()
    monkeypatch.setattr(td, "_executor", falso)
    for ligados in (True, False):
        fim = _o_ultimo_passo(td.plano_de_desfazer(testes_ligados=ligados))
        assert fim.so_se_tudo_certo, "a pasta so sai se tudo deu certo (com a propria tarefa do desfazer)"
        assert f"DeleteFolder('{td.PASTA_DAS_TAREFAS}', 0)" in fim.comando
        assert fim.comando.index("Unregister-ScheduledTask") < fim.comando.index("DeleteFolder"), \
            "a pasta so pode sair depois da ultima tarefa dela"
    falso.aplicar(td.plano_de_desfazer(), "")
    assert "DeleteFolder" in falso.chamadas[0][-1].comando


@precisa_do_powershell
def test_d731_a_pasta_vazia_sai_do_agendador(maquina):
    """D-731: pasta sem tarefas e sem subpastas -> sai. Falha antes (fd9f1f58): ninguem chamava o DeleteFolder."""
    fim = _o_ultimo_passo(td.plano_de_desfazer(testes_ligados=False))
    codigo, linhas, erro = _rodar_com_o_agendador_de_mentira(fim.comando, maquina, tarefas=0, subpastas=0)
    assert codigo == 0, erro
    assert f"CHAMOU DeleteFolder {td.PASTA_DAS_TAREFAS}" in linhas
    assert "CHAMOU GetTasks 1" in linhas, "conta tambem as tarefas escondidas"
    assert any("saiu do Agendador" in l for l in linhas)
    apagou_a_tarefa = next(i for i, l in enumerate(linhas) if l.startswith("CHAMOU Unregister-ScheduledTask"))
    assert apagou_a_tarefa < linhas.index(f"CHAMOU DeleteFolder {td.PASTA_DAS_TAREFAS}")


@precisa_do_powershell
@pytest.mark.parametrize("tarefas, subpastas", [(1, 0), (0, 1), (2, 3)])
def test_d731_a_pasta_com_alguma_coisa_fica(maquina, tarefas, subpastas):
    """D-731: se ficou qualquer tarefa (de outro programa, do dono, ou uma nossa que nao saiu) ou subpasta, a
    pasta fica, e o registro diz por que."""
    fim = _o_ultimo_passo(td.plano_de_desfazer(testes_ligados=False))
    codigo, linhas, erro = _rodar_com_o_agendador_de_mentira(fim.comando, maquina, tarefas, subpastas)
    assert codigo == 0, erro
    assert not any(l.startswith("CHAMOU DeleteFolder") for l in linhas)
    assert any("nao esta vazia" in l for l in linhas)


@precisa_do_powershell
def test_d731_sem_a_pasta_o_desfazer_nao_da_erro(maquina):
    """D-731: se a pasta ja nao existe (alguem apagou), nada acontece e o passo nao vira erro."""
    fim = _o_ultimo_passo(td.plano_de_desfazer(testes_ligados=False))
    codigo, linhas, erro = _rodar_com_o_agendador_de_mentira(fim.comando, maquina, 0, 0, existe=False)
    assert codigo == 0, erro
    assert not any(l.startswith("CHAMOU DeleteFolder") for l in linhas)
