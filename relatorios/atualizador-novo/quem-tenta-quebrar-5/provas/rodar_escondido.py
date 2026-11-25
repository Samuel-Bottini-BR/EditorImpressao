"""Quem tenta quebrar 5: roda uma prova (um script Python) com o processo inteiro NASCIDO numa área de trabalho
separada ("EditorProvaQtq5", `CreateProcessW` com `lpDesktop`), e a guarda da tela normal ligada: se qualquer janela
visível de um processo da prova aparecer na tela do Samuel, a prova inteira é morta na hora. Lição do incidente de
25/11/2026 14:17 (a caixa que saiu de um fio por trás e apareceu na tela dele).
Uso: python rodar_escondido.py [--limite=<segundos>] <script.py> [argumentos...]   (o script grava o próprio resultado num arquivo)
"""
from __future__ import annotations

import ctypes
import importlib.util
import json
import subprocess
import sys
import threading
from ctypes import wintypes
from pathlib import Path

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prova_caixa", AQUI / "prova_caixa.py")
pc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pc)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    limite = 300
    if sys.argv[1].startswith("--limite="):
        limite = int(sys.argv.pop(1).split("=", 1)[1])
    area = pc.u32.CreateDesktopW(pc.NOME_DA_AREA, None, None, 0, pc.GENERIC_ALL, None)
    assert area, ctypes.get_last_error()
    si = pc._STARTUPINFOW()
    si.cb = ctypes.sizeof(si)
    si.lpDesktop = "WinSta0\\" + pc.NOME_DA_AREA
    pi = pc._PROCESS_INFORMATION()
    linha = ctypes.create_unicode_buffer(subprocess.list2cmdline([sys.executable, "-I", *sys.argv[1:]]))
    try:
        assert pc.k32.CreateProcessW(None, linha, None, None, False, 0x08000000, None, str(pc.RAMO), ctypes.byref(si),
                                     ctypes.byref(pi)), ctypes.get_last_error()
        guarda: list = []
        parar = threading.Event()
        g = threading.Thread(target=pc._guarda_da_tela, args=(pi.dwProcessId, guarda, parar), daemon=True)
        g.start()
        pc.k32.WaitForSingleObject(pi.hProcess, limite * 1000)
        codigo = wintypes.DWORD()
        pc.k32.GetExitCodeProcess(pi.hProcess, ctypes.byref(codigo))
        if codigo.value == 259:
            pc._matar(pc._familia(pi.dwProcessId))
        parar.set()
        g.join(5)
        print(json.dumps({"script": sys.argv[1:], "código de saída": codigo.value,
                          "a guarda da tela do Samuel": guarda or "nenhuma janela dos processos da prova na tela normal"},
                         ensure_ascii=False))
    finally:
        pc.u32.CloseDesktop(area)


if __name__ == "__main__":
    main()
