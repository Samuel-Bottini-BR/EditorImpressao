"""Segura um arquivo aberto (como um leitor de PDF faria) por N segundos.

open() do Python no Windows abre sem FILE_SHARE_DELETE: ninguem consegue
apagar nem trocar o arquivo enquanto ele estiver aberto aqui.
"""
import sys
import time

caminho, segundos = sys.argv[1], float(sys.argv[2])
with open(caminho, "rb") as f:
    f.read(1024)
    print("segurando", caminho, flush=True)
    time.sleep(segundos)
print("soltei", flush=True)
