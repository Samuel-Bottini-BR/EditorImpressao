# Programa de prova (sem janela): so anota com que argumentos o Velopack o abriu, e sai.
import datetime, os, pathlib, sys
log = pathlib.Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo\saida_teste\qtq3\volta-recusada\aberturas.log")
pasta = pathlib.Path(sys.executable).resolve().parent
v = (pasta / "versao.txt").read_text(encoding="utf-8").strip() if (pasta / "versao.txt").exists() else "?"
with log.open("a", encoding="utf-8") as f:
    f.write(f"{datetime.datetime.now().isoformat(timespec='milliseconds')} | versao {v} | pasta {pasta.name} | args {sys.argv[1:]} | VELOPACK_RESTART={os.environ.get('VELOPACK_RESTART')}\n")
