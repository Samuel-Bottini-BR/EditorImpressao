"""Prova EXECUTADA (quem tenta quebrar, volta 2): o `Update.exe` DE VERDADE do Velopack 1.2.161 (o `Squirrel.exe` tirado,
só lendo, do pacote 1.1.0 do próprio Samuel) numa instalação de prova minha, portátil (`.portable`: o Velopack não mexe
no registro nem em atalhos), com as pastas de dados do Windows desviadas para pastas minhas. Nenhuma janela: o
"programa" é um pythonw (sem janela) que roda a sonda; o `apply` vai com `--silent --norestart` e um pacote que não
existe (ele espera e depois desiste sem mexer em nada).

A. `Update.exe start` (o que o atalho faz): a sonda, aberta por ele, pergunta logo ao começar se o atualizador do
   Velopack está rodando (a conta do conserto do G1). Mede se o `start` ainda está vivo quando o programa pergunta.
B. `Update.exe apply --waitPid` (o que a troca faz): enquanto ele espera, a função do G1 diz "rodando"?
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\vp")
RAIZ = R / "raiz"
BASE = sys.base_prefix  # a instalação do Python por trás da .venv
SEM_JANELA = 0x08000000
sys.path.insert(0, str(RAMO))
from core import windows  # noqa: E402


def ambiente():
    e = dict(os.environ)
    e.update(LOCALAPPDATA=str(R / "env" / "local"), TEMP=str(R / "env" / "temp"), TMP=str(R / "env" / "temp"),
             PROGRAMDATA=str(R / "env" / "pd"), PYTHONHOME=BASE, PYTHONPATH=str(RAMO))
    return e


def parte_a(vezes=8):
    sonda = Path(__file__).with_name("sonda_inicio.py")
    resultados = []
    for i in range(vezes):
        saida = R / f"sonda-{i}.json"
        saida.unlink(missing_ok=True)
        p = subprocess.Popen([str(RAIZ / "Update.exe"), "start", "--", str(sonda), str(RAIZ), str(saida)],
                             env=ambiente(), creationflags=SEM_JANELA)
        p.wait(30)
        fim_do_start = time.perf_counter()
        for _ in range(200):
            if saida.exists():
                break
            time.sleep(0.05)
        time.sleep(0.3)
        lido = json.loads(saida.read_text(encoding="utf-8")) if saida.exists() else None
        resultados.append({"codigo_do_start": p.returncode, "sonda": lido})
    return resultados


def parte_b():
    fora = R / "fora"
    ping = fora / "esperador.exe"
    if not ping.exists():
        ping.write_bytes(Path(r"C:\Windows\System32\PING.EXE").read_bytes())
    esperador = subprocess.Popen([str(ping), "-n", "12", "127.0.0.1"], creationflags=SEM_JANELA,
                                 stdout=subprocess.DEVNULL)
    antes = windows.atualizador_do_velopack_rodando(RAIZ)
    t0 = time.perf_counter()
    apply = subprocess.Popen([str(RAIZ / "Update.exe"), "apply", "--package", str(RAIZ / "packages" / "nao-existe.nupkg"),
                              "--waitPid", str(esperador.pid), "--silent", "--norestart", "--root", str(RAIZ)],
                             env=ambiente(), creationflags=SEM_JANELA)
    amostras = []
    while apply.poll() is None and time.perf_counter() - t0 < 40:
        amostras.append((round(time.perf_counter() - t0, 1), esperador.poll() is None,
                         windows.atualizador_do_velopack_rodando(RAIZ)))
        time.sleep(1)
    depois = windows.atualizador_do_velopack_rodando(RAIZ)
    return {"antes": antes, "amostras (s, esperador vivo, atualizador rodando)": amostras,
            "codigo_do_apply": apply.returncode, "depois": depois}


if __name__ == "__main__":
    a = parte_a()
    b = parte_b()
    texto = json.dumps({"A_start": a, "B_apply": b}, ensure_ascii=False, indent=1)
    Path(__file__).with_name("prova_velopack_start_e_espera-resultado.txt").write_text(texto, encoding="utf-8")
    print(texto)
