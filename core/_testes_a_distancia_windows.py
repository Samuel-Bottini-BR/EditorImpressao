"""A peca que fala de verdade com o Windows, para os testes a distancia.

Fica separada de core/testes_a_distancia.py de proposito: so este arquivo toca
o Windows, e so na producao. Os testes nunca o importam (o ExecutorWindows se
recusa a rodar sob o pytest, e os testes trocam o executor por um de mentira).

O QUE FAZ (D-705, D-711, D-717; estudo 2.3):
  - monta um script PowerShell com todos os passos (um lugar so, vindos de
    core/testes_a_distancia.plano_de_ligar);
  - entrega a senha por dentro, cifrada pelo proprio Windows (DPAPI da conta do
    usuario), NUNCA na linha de comando (outros programas enxergam a linha de
    comando). O texto da senha nao vai para disco em claro nem para argv;
  - roda o script elevado com UMA pergunta de administrador so (runas);
  - anota num registro o que fez (para a lista do D-722).

RESSALVA (etapa 5, D-722): esta ligacao - o runas, a passagem da senha por
DPAPI, a tarefa rodar sem perguntar - so e PROVADA no PC do Samuel. Aqui ela e
escrita com cuidado, mas nao foi rodada; os testes cobrem o plano de comandos e
a fiacao da tela, nao este arquivo.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from ctypes import wintypes
from pathlib import Path

from core.testes_a_distancia import Passo, Resultado, VARIAVEL_DA_SENHA
from registro import registrar_erro

_CANCELADO = 1223  # o Windows devolve isto quando a pessoa clica "Nao" no runas


def _senha_cifrada_pelo_windows(senha: str) -> str:
    """Devolve a senha cifrada pela DPAPI da conta do usuario (uma string que
    so esta maquina e este usuario decifram), sem a senha passar por argv.

    A senha vai pela ENTRADA PADRAO do powershell (nao pela linha de comando).
    """
    script = ("$s = [Console]::In.ReadLine();"
              " $seg = ConvertTo-SecureString $s -AsPlainText -Force;"
              " [Console]::Out.Write((ConvertFrom-SecureString $seg))")
    saida = subprocess.run(
        ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
        input=senha, capture_output=True, text=True, check=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return saida.stdout.strip()


def _montar_script(passos: list[Passo], blob_cifrado: Path, registro: Path) -> str:
    """O texto do script PowerShell que roda elevado: le a senha cifrada,
    roda cada passo, para no primeiro erro, anota o que fez e apaga o blob."""
    linhas = [
        "$ErrorActionPreference = 'Stop'",
        f"$blob = Get-Content -Raw '{blob_cifrado}'",
        # $SenhaDosTestes (o nome que os passos usam) vem da DPAPI, so na memoria.
        f"{VARIAVEL_DA_SENHA} = ConvertTo-SecureString $blob",
        f"Remove-Item -Path '{blob_cifrado}' -Force -ErrorAction SilentlyContinue",
        f"function Anotar($t) {{ Add-Content -Path '{registro}' -Value $t }}",
    ]
    for passo in passos:
        linhas.append("try {")
        linhas.append(f"  {passo.comando}")
        linhas.append(f"  Anotar 'OK   | {passo.nome}'")
        linhas.append("} catch {")
        linhas.append(f"  Anotar ('ERRO | {passo.nome} | ' + $_.Exception.Message)")
        linhas.append("  throw")
        linhas.append("}")
    return "\n".join(linhas)


class _SHELLEXECUTEINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("fMask", ctypes.c_ulong),
        ("hwnd", wintypes.HWND),
        ("lpVerb", wintypes.LPCWSTR),
        ("lpFile", wintypes.LPCWSTR),
        ("lpParameters", wintypes.LPCWSTR),
        ("lpDirectory", wintypes.LPCWSTR),
        ("nShow", ctypes.c_int),
        ("hInstApp", wintypes.HINSTANCE),
        ("lpIDList", ctypes.c_void_p),
        ("lpClass", wintypes.LPCWSTR),
        ("hkeyClass", wintypes.HKEY),
        ("dwHotKey", wintypes.DWORD),
        ("hIcon", wintypes.HANDLE),
        ("hProcess", wintypes.HANDLE),
    ]


def _rodar_elevado(caminho_script: Path) -> int:
    """Roda o script com UMA pergunta de administrador (runas) e devolve o
    codigo de saida. 1223 = a pessoa clicou "Nao"."""
    SEE_MASK_NOCLOSEPROCESS = 0x00000040
    SEE_MASK_NO_CONSOLE = 0x00008000
    info = _SHELLEXECUTEINFO()
    info.cbSize = ctypes.sizeof(info)
    info.fMask = SEE_MASK_NOCLOSEPROCESS | SEE_MASK_NO_CONSOLE
    info.lpVerb = "runas"
    info.lpFile = "powershell.exe"
    info.lpParameters = (f"-NoProfile -NonInteractive -ExecutionPolicy Bypass "
                         f"-WindowStyle Hidden -File \"{caminho_script}\"")
    info.nShow = 0  # SW_HIDE
    if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(info)):
        return ctypes.get_last_error()
    ctypes.windll.kernel32.WaitForSingleObject(info.hProcess, 0xFFFFFFFF)
    codigo = wintypes.DWORD()
    ctypes.windll.kernel32.GetExitCodeProcess(info.hProcess, ctypes.byref(codigo))
    ctypes.windll.kernel32.CloseHandle(info.hProcess)
    return codigo.value


def aplicar_no_windows(passos: list[Passo], senha: str) -> Resultado:
    """Aplica os passos no Windows, numa pergunta de administrador so."""
    pasta = Path(tempfile.mkdtemp(prefix="editor-testes-"))
    script = pasta / "ligar.ps1"
    registro = pasta / "o-que-fiz.txt"
    blob = pasta / "senha.dpapi"
    try:
        if any(p.precisa_senha for p in passos):
            blob.write_text(_senha_cifrada_pelo_windows(senha), encoding="ascii")
        script.write_text(_montar_script(passos, blob, registro), encoding="utf-8")
        codigo = _rodar_elevado(script)
        if codigo == _CANCELADO:
            return Resultado(False, cancelado=True, passos=passos)
        if codigo != 0:
            registrar_erro("testes a distancia",
                           f"codigo {codigo}; registro: {registro.read_text(encoding='utf-8', errors='replace') if registro.exists() else '(vazio)'}")
            return Resultado(False, mensagem="Não consegui preparar os testes à distância agora. "
                                             "O programa continua funcionando.", passos=passos)
        return Resultado(True, passos=passos)
    except Exception as erro:  # noqa: BLE001 - nenhum erro pode fechar a janela
        registrar_erro("testes a distancia", repr(erro))
        return Resultado(False, mensagem="Não consegui preparar os testes à distância agora. "
                                         "O programa continua funcionando.", passos=passos)
    finally:
        # Nada da senha fica para tras: apaga o blob e o script.
        for arquivo in (blob, script):
            try:
                arquivo.unlink(missing_ok=True)
            except OSError:
                pass
        os.environ.pop("EDITOR_SENHA_TESTES", None)
