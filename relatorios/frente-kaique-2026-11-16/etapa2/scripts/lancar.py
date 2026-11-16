"""Lança um comando numa área de trabalho do Windows escondida (CreateDesktop), que nunca
aparece na tela de quem usa o PC. Uso: python lancar.py <nome_da_area> <saida.log> <comando...>
Espera o comando terminar e devolve o código de saída dele."""
import subprocess
import sys

import win32con
import win32process
import win32service
import win32event

nome, log, *comando = sys.argv[1:]
acesso = (win32con.DESKTOP_CREATEWINDOW | win32con.DESKTOP_ENUMERATE | win32con.DESKTOP_READOBJECTS
          | win32con.DESKTOP_WRITEOBJECTS | win32con.DESKTOP_SWITCHDESKTOP | win32con.DESKTOP_CREATEMENU
          | win32con.DESKTOP_HOOKCONTROL | win32con.DESKTOP_JOURNALPLAYBACK | win32con.DESKTOP_JOURNALRECORD
          | 0x000F0000)
area = win32service.CreateDesktop(nome, 0, acesso, None)
si = win32process.STARTUPINFO()
si.lpDesktop = "WinSta0\\" + nome
linha = subprocess.list2cmdline(comando)
with open(log, "w", encoding="utf-8") as f:
    f.write(f"comando: {linha}\n")
hp, ht, pid, tid = win32process.CreateProcess(None, linha, None, None, False,
                                              win32con.CREATE_NO_WINDOW, None, None, si)
print(f"lancado pid {pid} na area {si.lpDesktop}", flush=True)
win32event.WaitForSingleObject(hp, win32event.INFINITE)
codigo = win32process.GetExitCodeProcess(hp)
print(f"terminou com {codigo}", flush=True)
area.CloseDesktop()
sys.exit(codigo)
