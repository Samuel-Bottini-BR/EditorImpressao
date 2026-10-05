"""Caixa "Ja existe" aberta -> escolhe "substituir o antigo" e cancela (ou nao).

  substituir.py PREFIXO cancelar PAGINA   -> cancela quando a tela mostrar "Pagina >= PAGINA"
  substituir.py PREFIXO terminar

Vigia a pasta de saida a cada 50 ms (anota todo arquivo que aparece, inclusive
~*.parcial), tira prints da caixa, da tela de progresso e do depois.
"""
import hashlib
import json
import re
import sys
import threading
import time
from pathlib import Path

import piloto as P

PASTA = P.DADOS / "saida"
prefixo, modo = sys.argv[1], sys.argv[2]
pagina_alvo = int(sys.argv[3]) if len(sys.argv) > 3 else 0
PR = P.BASE / "prints"


def foto():
    out = {}
    for f in sorted(PASTA.iterdir()):
        try:
            st = f.stat()
            h = hashlib.sha256(f.read_bytes()).hexdigest()[:16] if f.suffix == ".pdf" else "-"
            out[f.name] = (st.st_size, time.strftime("%H:%M:%S", time.localtime(st.st_mtime)), h)
        except OSError as e:
            out[f.name] = ("ERRO", repr(e))
    return out


vistos = {}
parar = False


def vigia():
    while not parar:
        try:
            for f in PASTA.iterdir():
                vistos.setdefault(f.name, time.strftime("%H:%M:%S"))
        except OSError:
            pass
        time.sleep(0.05)


print("ANTES:", json.dumps(foto(), ensure_ascii=False))
threading.Thread(target=vigia, daemon=True).start()
cx = P.janela("Já existe", contem=True)
P.printar(f"{prefixo}-a-caixa", cx["hwnd"], pasta=PR)
P.clicar("substituir o antigo", titulo=cx["titulo"], espera=0.05)
t0 = time.time()
cancelou = False
ultima = ""
while time.time() - t0 < 120:
    try:
        textos = [it["texto"] for j in P.mapa() for it in j["itens"] if it["texto"]]
    except RuntimeError:
        continue
    prog = [t for t in textos if t.startswith("Página ") and " de " in t]
    if prog:
        ultima = prog[0]
    if "Ficou pronto!" in textos:
        print("PRONTO depois de", round(time.time() - t0, 1), "s")
        break
    if modo == "cancelar" and prog and not cancelou:
        m = re.match(r"Página (\d+) de", prog[0])
        if m and int(m.group(1)) >= pagina_alvo:
            P.printar(f"{prefixo}-b-processando", pasta=PR)
            P.clicar("cancelar", titulo="Editor de Impressão", espera=0.05)
            print("CANCELEI em:", prog[0], "aos", round(time.time() - t0, 1), "s")
            cancelou = True
            time.sleep(2.5)
            break
    time.sleep(0.05)
time.sleep(1.0)
parar = True
print("ultima tela de progresso:", ultima)
P.printar(f"{prefixo}-c-depois", pasta=PR)
for j in P.mapa():
    if j["classe"] != "JanelaPrincipal":
        print("JANELA ABERTA:", j["titulo"], [it["texto"] for it in j["itens"] if it["texto"]])
        P.printar(f"{prefixo}-d-{j['classe']}", j["hwnd"], pasta=PR)
print("arquivos vistos na pasta durante a rodada:", json.dumps(vistos, ensure_ascii=False))
print("DEPOIS:", json.dumps(foto(), ensure_ascii=False))
