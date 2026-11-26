"""Sonda (quem tenta quebrar, volta 2): roda como o "programa" de uma instalação de prova do Velopack, aberto pelo
`Update.exe start` DE VERDADE. Logo ao começar, pergunta à peça do Windows do ramo (a mesma função que a abertura
usa no conserto do G1) se o atualizador do Velopack desta instalação está rodando, várias vezes, e grava o que viu.

Uso: <exe> sonda_inicio.py <raiz> <arquivo de saída>
"""
import json
import sys
import time

t0 = time.perf_counter()
raiz, saida = sys.argv[1], sys.argv[2]
from core import windows  # noqa: E402  (PYTHONPATH aponta para o ramo)

t_import = time.perf_counter() - t0
amostras = []
for _ in range(40):
    amostras.append((round(time.perf_counter() - t0, 3), windows.atualizador_do_velopack_rodando(raiz)))
    time.sleep(0.025)
with open(saida, "w", encoding="utf-8") as f:
    json.dump({"import_s": round(t_import, 3), "amostras": amostras}, f)
