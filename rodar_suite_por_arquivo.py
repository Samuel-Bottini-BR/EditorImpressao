r"""Roda a suíte inteira um arquivo de teste por vez (um processo por arquivo, como o GitHub).

Uso: .venv\Scripts\python.exe rodar_suite_por_arquivo.py <raiz da cópia> <pasta de saída>

Por que existe (10/11/2026): num processo só, a suíte trava em test_p147_tema (o tema é
reaplicado em milhares de widgets que sobram dos testes anteriores) e pesa o PC do Samuel.
Aqui cada arquivo roda sozinho, sem janela (QT_QPA_PLATFORM=offscreen) e com prioridade
baixa; no fim roda o teste_botoes.py. O resumo fica em <saída>\resumo.txt, uma linha por
arquivo ("OK" ou "FALHA"), e a saída de cada arquivo em <saída>\<nome>.txt.

Seguro mudar: a prioridade (BAIXA) e a ordem. Arriscado: tirar o offscreen (abriria janelas
na tela do Samuel, o que ele proibiu em 09/11).
"""
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])
PY = str(Path(__file__).resolve().parent / ".venv" / "Scripts" / "python.exe")
BAIXA = 0x00004000  # BELOW_NORMAL_PRIORITY_CLASS

env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONUTF8="1")
SAIDA.mkdir(parents=True, exist_ok=True)
arquivos = sorted((RAIZ / "tests").glob("test_*.py"))
resumo = SAIDA / "resumo.txt"
with resumo.open("w", encoding="utf-8") as r:
    r.write(f"{len(arquivos)} arquivos, comeco {time.strftime('%H:%M')}\n")
for i, arq in enumerate(arquivos, 1):
    t = time.time()
    log = SAIDA / f"{arq.stem}.txt"
    with log.open("w", encoding="utf-8") as f:
        cod = subprocess.call([PY, "-m", "pytest", str(arq.relative_to(RAIZ)), "-q", "-p", "no:cacheprovider"],
                              cwd=RAIZ, env=env, stdout=f, stderr=subprocess.STDOUT, creationflags=BAIXA)
    ultima = [l for l in log.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()][-1:]
    with resumo.open("a", encoding="utf-8") as r:
        r.write(f"{i:3}/{len(arquivos)} {'OK ' if cod in (0, 5) else 'FALHA'} {arq.name} ({time.time()-t:.0f}s) {ultima[0] if ultima else ''}\n")
log = SAIDA / "teste_botoes.txt"
with log.open("w", encoding="utf-8") as f:
    cod = subprocess.call([PY, "teste_botoes.py"], cwd=RAIZ, env=env, stdout=f, stderr=subprocess.STDOUT, creationflags=BAIXA)
with resumo.open("a", encoding="utf-8") as r:
    r.write(f"teste_botoes: {'OK' if cod == 0 else 'FALHA'} (codigo {cod})\nfim {time.strftime('%H:%M')}\n")
