"""Prova EXECUTADA (quem tenta quebrar, volta 2): a função ÚNICA da licença (`windows.dar_licenca_aos_usuarios`, o
`icacls /grant *S-1-5-32-545:(OI)(CI)M /T` de verdade) numa pasta MINHA no D: que imita a raiz da instalação, nos
casos que a volta 1 não rodou:
  a. um arquivo de dentro aberto por outro processo sem compartilhar nada (repete a volta 1, agora com a leitura de
     volta nova, a que recusa linha a mais);
  b. um atalho de pasta (junção) DENTRO da raiz apontando para uma pasta de fora (aqui, outra pasta minha): o `/T` passa
     pela junção e muda a licença da pasta de fora? (depois do "Sim", qualquer conta do computador pode criar uma
     junção na raiz; o preparo roda de novo com a licença de administrador quando o teste de gravar falha).
No fim, as licenças das minhas pastas voltam ao normal (`icacls /reset /T`).
"""
import _winapi
import json
import subprocess
import sys
import time
from pathlib import Path

RAMO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\atualizador-novo")
R = Path(r"D:\programas\EditorImpressao\rascunho-qtq2\licenca")
sys.path.insert(0, str(RAMO))
from core import windows  # noqa: E402

SEM_JANELA = 0x08000000


def usuarios_modificam(p):
    return windows.usuarios_modificam(windows.ler_licencas(p))


raiz, fora = R / "raiz", R / "fora-da-raiz"
for p in (raiz / "current", fora):
    p.mkdir(parents=True, exist_ok=True)
(raiz / "current" / "sq.version").write_text("x", encoding="utf-8")
(raiz / "current" / "preso.dll").write_bytes(b"x" * 10)
(fora / "arquivo-de-fora.txt").write_text("x", encoding="utf-8")
juncao = raiz / "atalho-para-fora"
if not juncao.exists():
    _winapi.CreateJunction(str(fora), str(juncao))
segura = subprocess.Popen([sys.executable, "-c",
                           "import ctypes,time;k=ctypes.windll.kernel32;"
                           f"h=k.CreateFileW(r'{raiz / 'current' / 'preso.dll'}',0x80000000,0,None,3,0x80,None);"
                           "print(h,flush=True);time.sleep(30)"], stdout=subprocess.PIPE, text=True,
                          creationflags=SEM_JANELA)
alca = segura.stdout.readline().strip()
time.sleep(0.5)
saida = {"arquivo de dentro preso (alça)": alca,
         "antes": {"raiz": usuarios_modificam(raiz), "fora (pela junção)": usuarios_modificam(fora)}}
try:
    r = windows.dar_licenca_aos_usuarios(raiz)
    saida["resposta"] = {"desfecho": r.desfecho, "motivo": r.motivo, "detalhe": r.detalhe[-500:]}
    saida["depois"] = {"raiz": usuarios_modificam(raiz), "current\\preso.dll (aberto sem compartilhar)":
                       usuarios_modificam(raiz / "current" / "preso.dll"),
                       "fora-da-raiz (o alvo da junção, FORA da raiz)": usuarios_modificam(fora),
                       "fora-da-raiz\\arquivo-de-fora.txt": usuarios_modificam(fora / "arquivo-de-fora.txt")}
finally:
    segura.kill()
    segura.wait()
    reset = subprocess.run(["icacls", str(R), "/reset", "/T", "/C"], capture_output=True, text=True, encoding="oem",
                           errors="replace")
    saida["licencas devolvidas"] = (reset.stdout.strip().splitlines() or [""])[-1]
    saida["depois de devolver: fora"] = usuarios_modificam(fora)
texto = json.dumps(saida, ensure_ascii=False, indent=1)
Path(__file__).with_name("prova_licenca_de_verdade-resultado.txt").write_text(texto, encoding="utf-8")
print(texto)
