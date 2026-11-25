"""A vigia da prova à vista do atualizador novo: anota, com a hora (milésimos), cada janela e cada processo do programa
instalado que aparece e some. NÃO é parte do programa. SÓ LÊ: não clica, não fecha, não abre nada, não mostra janela.

PARA QUÊ
    - As medidas do passo 12 (quanto tempo a abertura leva; quantos segundos sem nada na tela depois da troca): a
      diferença entre as horas anotadas, lidas depois no registro.
    - A prova escrita do que apareceu em cada passo (a pergunta do Windows não aparece aqui: ela fica numa área de
      trabalho protegida do Windows, que nenhum programa lê; o print dela é do Samuel ou da gerente).

O QUE ANOTA
    - processo que começa ou termina, se o programa dele está em `C:\\Program Files\\EditorImpressaoPrograma\\` (o nosso,
      o `Update.exe` do Velopack, o atalho), ou se é o `msiexec.exe`: o número, o caminho e a linha de comando (é onde
      se vê `--teste-rapido`, `--conferir-a-versao-nova 1.9.0 1.9.1`, `--sem-janela`, `apply`);
    - janela visível de primeiro nível que aparece, muda de título ou some, de um desses processos: o título e a
      classe (`#32770` é uma caixa de mensagem).
    Nada de outros programas do Samuel é anotado (nem o título).

COMO RODAR (por trás, durante a prova; para parar, criar o arquivo <BASE>\\registros\\parar-a-vigia)
    python vigiar_janelas.py [segundos, padrão 7200]
    O registro vai para <BASE>\\registros\\vigia-<data>-<hora>.txt (e para a tela).

A lista de janelas é pedida ao Windows aqui mesmo (EnumWindows, pelo ctypes), porque a peça do programa
(`core/windows.py`) não tem essa leitura e esta preparação não muda o programa (ver o ONDE-PAREI, ressalvas). Os
processos vêm do `psutil` (só leitura).

Seguro mexer: o intervalo, os textos. Arriscado: anotar janelas de qualquer processo (os títulos das janelas do Samuel
iriam para o registro).
"""
from __future__ import annotations

import ctypes
import os
import sys
import time
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

import psutil

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import prova_comum as comum  # noqa: E402

PARAR = comum.REGISTROS / "parar-a-vigia"
INTERVALO_S = 0.2
OUTROS_QUE_CONTAM = {"msiexec.exe"}


def e_nosso(caminho: str | None, nome: str | None) -> bool:
    """O processo conta? O programa dele está na pasta do programa instalado, ou é o msiexec (o .msi)."""
    if caminho and os.path.normcase(caminho).startswith(os.path.normcase(str(comum.PROGRAMA)) + os.sep):
        return True
    return (nome or "").lower() in OUTROS_QUE_CONTAM


def _processos() -> dict[int, tuple[str, str, float]]:
    """{número: (caminho, linha de comando, hora em que nasceu)} dos processos que contam."""
    saida = {}
    for p in psutil.process_iter(["pid", "name", "exe", "cmdline", "create_time"]):
        info = p.info
        try:
            if e_nosso(info.get("exe"), info.get("name")):
                linha = " ".join(info.get("cmdline") or [])
                saida[info["pid"]] = (info.get("exe") or info.get("name") or "?", linha, info.get("create_time") or 0)
        except (psutil.Error, TypeError):
            continue
    return saida


_user32 = ctypes.WinDLL("user32", use_last_error=True)
_EnumWindows = _user32.EnumWindows
_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


def _janelas(pids: set[int]) -> dict[int, tuple[int, str, str]]:
    """{janela: (número do processo, título, classe)} das janelas visíveis de primeiro nível desses processos."""
    achadas: dict[int, tuple[int, str, str]] = {}

    def uma(hwnd, _lparam):
        if not _user32.IsWindowVisible(hwnd):
            return True
        pid = wintypes.DWORD()
        _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value not in pids:
            return True
        tamanho = _user32.GetWindowTextLengthW(hwnd)
        titulo = ctypes.create_unicode_buffer(tamanho + 1)
        _user32.GetWindowTextW(hwnd, titulo, tamanho + 1)
        classe = ctypes.create_unicode_buffer(256)
        _user32.GetClassNameW(hwnd, classe, 256)
        achadas[int(hwnd)] = (pid.value, titulo.value, classe.value)
        return True

    _EnumWindows(_PROC(uma), 0)
    return achadas


def _hora(t: float | None = None) -> str:
    """HH:MM:SS.mmm"""
    return datetime.fromtimestamp(t if t is not None else time.time()).strftime("%H:%M:%S.%f")[:-3]


def vigiar(segundos: float, registro: Path) -> int:
    """O laço da vigia (ver o topo)."""
    registro.parent.mkdir(parents=True, exist_ok=True)
    PARAR.unlink(missing_ok=True)
    fim = time.time() + segundos
    procs: dict[int, tuple[str, str, float]] = {}
    janelas: dict[int, tuple[int, str, str]] = {}
    with registro.open("a", encoding="utf-8") as saida:
        def anotar(texto: str, t: float | None = None) -> None:
            linha = f"{_hora(t)}  {texto}"
            print(linha, flush=True)
            saida.write(linha + "\n")
            saida.flush()

        anotar(f"a vigia começou (pasta do programa: {comum.PROGRAMA})")
        while time.time() < fim and not PARAR.exists():
            agora = _processos()
            for pid in agora.keys() - procs.keys():
                caminho, linha, nasceu = agora[pid]
                anotar(f"PROCESSO COMEÇOU (nasceu {_hora(nasceu)}) {pid} {caminho} | {linha}")
            for pid in procs.keys() - agora.keys():
                anotar(f"PROCESSO TERMINOU {pid} {procs[pid][0]}")
            procs = agora
            novas = _janelas(set(procs))
            for h in novas.keys() - janelas.keys():
                pid, titulo, classe = novas[h]
                anotar(f"JANELA APARECEU '{titulo}' [{classe}] do processo {pid} {os.path.basename(procs[pid][0])}")
            for h in novas.keys() & janelas.keys():
                if novas[h][1] != janelas[h][1]:
                    anotar(f"JANELA MUDOU DE TÍTULO '{janelas[h][1]}' -> '{novas[h][1]}' do processo {novas[h][0]}")
            for h in janelas.keys() - novas.keys():
                pid, titulo, classe = janelas[h]
                anotar(f"JANELA SUMIU '{titulo}' [{classe}] do processo {pid}")
            janelas = novas
            time.sleep(INTERVALO_S)
        anotar("a vigia parou")
    PARAR.unlink(missing_ok=True)
    return 0


def main(argumentos: list[str]) -> int:
    """python vigiar_janelas.py [segundos]"""
    segundos = float(argumentos[0]) if argumentos else 7200
    registro = comum.REGISTROS / f"vigia-{datetime.now():%Y%m%d-%H%M%S}.txt"
    return vigiar(segundos, registro)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
