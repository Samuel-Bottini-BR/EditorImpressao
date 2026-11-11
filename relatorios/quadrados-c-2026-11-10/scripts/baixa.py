"""Roda um script com prioridade baixa (o PC do Samuel trava facil). Uso: python baixa.py script.py args..."""
import ctypes, runpy, sys
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
