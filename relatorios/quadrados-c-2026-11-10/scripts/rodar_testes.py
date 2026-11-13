"""Roda arquivos de teste um por vez, sem janela, prioridade baixa (como rodar_suite_por_arquivo.py do fase-1).
Uso: python rodar_testes.py <raiz> <saida> arq1 arq2 ..."""
import os, subprocess, sys, time
from pathlib import Path
RAIZ, SAIDA = Path(sys.argv[1]), Path(sys.argv[2])
PY = r"D:\programas\EditorImpressao\.venv\Scripts\python.exe"
env = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONUTF8="1")
SAIDA.mkdir(parents=True, exist_ok=True)
resumo = SAIDA / "resumo.txt"
for arq in sys.argv[3:]:
    t = time.time(); nome = Path(arq).stem
    log = SAIDA / f"{nome}.txt"
    with log.open("w", encoding="utf-8") as f:
        cod = subprocess.call([PY, "-m", "pytest", arq, "-q", "-p", "no:cacheprovider"], cwd=RAIZ, env=env,
                              stdout=f, stderr=subprocess.STDOUT, creationflags=0x4000)
    ult = [l for l in log.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()][-1:]
    with resumo.open("a", encoding="utf-8") as r:
        r.write(f"{'OK   ' if cod in (0, 5) else 'FALHA'} {nome} ({time.time()-t:.0f}s) {ult[0] if ult else ''}\n")
