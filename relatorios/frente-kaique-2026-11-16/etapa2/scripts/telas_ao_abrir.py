"""Prova das telas: o que aparece entre "Seus livros" e a área de trabalho, ao clicar no livro do item 3.

Roda na área escondida (lancar.py), com a pasta de dados própria (cópia da pasta do programa de 28/10).
Serve para o código de 28/10 (python main.py na cópia 3961fbff) e para o empacotado de hoje (o .exe).
Passos: espera "Seus livros" e tira print; clica no nome do livro (clique por mensagem do Windows); tira um
print a cada tela nova; se houver "Continuar", tira print e aperta; para quando aparece o botão exato
"Confirmar e processar" da área de trabalho; fecha com WM_CLOSE.

Uso: python telas_ao_abrir.py <pasta dos prints> <prefixo> <dados> <pasta onde rodar> <comando...>
"""
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import piloto_uia as P
from pywinauto import Desktop

saida, prefixo, dados, onde = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), Path(sys.argv[4])
comando = sys.argv[5:]
P.abrir_log(saida / f"{prefixo}-anotacoes.txt")
amb = dict(os.environ)
amb["LOCALAPPDATA"] = str(dados)
amb["TEMP"] = amb["TMP"] = str(saida / f"{prefixo}-temp")
(saida / f"{prefixo}-temp").mkdir(parents=True, exist_ok=True)
proc = subprocess.Popen(comando, env=amb, cwd=str(onde))
w = None
n = [0]


def foto(nome):
    n[0] += 1
    P.print_janela(w, saida / f"{prefixo}-{n[0]}-{nome}.png")
    P.descrever(w, saida / f"{prefixo}-{n[0]}-{nome}.txt")


try:
    fim = time.time() + 180
    while w is None and time.time() < fim:
        for x in Desktop(backend="uia").windows():
            if "Editor de Impress" in (x.window_text() or ""):
                w = x
        time.sleep(0.5)
    cartao = P.achar(w, "righetti-14-folhas", "Text", limite=120)
    time.sleep(3)
    foto("seus-livros")
    P.clicar(w, cartao)
    vistos = set()
    fim = time.time() + 180
    while time.time() < fim:
        time.sleep(2)
        try:
            P.achar(w, "Confirmar e processar", "Button", limite=1)
            time.sleep(8)
            foto("area-de-trabalho")
            break
        except Exception:
            pass
        try:
            c = P.achar(w, "Continuar", "Button", limite=1)
            if "continuar" not in vistos:
                time.sleep(4)
                foto("tela-com-continuar")
                vistos.add("continuar")
                c.invoke()
                P.anotar("apertei", "Continuar")
            continue
        except Exception:
            pass
        if "outra" not in vistos:
            foto("tela-no-meio")
            vistos.add("outra")
    P.anotar("telas", sorted(vistos))
except Exception:
    P.anotar("ERRO", traceback.format_exc())
finally:
    if w is not None:
        P.fechar(w)
    try:
        proc.wait(60)
    except Exception:
        proc.kill()
        P.anotar("tive de encerrar o processo que eu abri")
    P.anotar("saiu", proc.returncode)
