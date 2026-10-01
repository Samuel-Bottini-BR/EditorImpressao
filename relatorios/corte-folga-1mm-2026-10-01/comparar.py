r"""Tabela antes x depois da folga do corte (01/10/2026), a partir dos JSONs de medir_folga.py.

Uso: .venv\Scripts\python.exe relatorios\corte-folga-1mm-2026-10-01\comparar.py ANTES.json DEPOIS.json
Imprime, por pagina: a folga de cada lado em mm (antes -> depois), quanto o
corte andou em pontos a 300 DPI, as pecas partidas, as pecas na beirada da
imagem final e a faixa escura (1 mm da beirada, em fracao do papel).
`*` = o corte ja esta na beirada do scan desse lado (nao ha papel para folga).
"""
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

MM = 300 / 25.4
LADOS = ("esq", "dir", "topo", "pe")
a = json.load(open(sys.argv[1], encoding="utf-8"))
b = json.load(open(sys.argv[2], encoding="utf-8"))


def mm(v):
    return "-" if v is None else f"{v / MM:.2f}"


print("| Pagina | esq (mm) | dir (mm) | topo (mm) | pe (mm) | corte andou (pt: esq,topo,dir,pe) | partidas | na beirada | escuro <0,6 |")
print("|---|---|---|---|---|---|---|---|---|")
for k in a:
    if k.startswith("_"):
        continue
    la, lb = a[k]["lados"], b[k]["lados"]
    cel = []
    for l in LADOS:
        x, y = la[l]["folga_px"], lb[l]["folga_px"]
        s = f"{mm(x)} → {mm(y)}" + ("*" if lb[l]["beirada_do_scan"] else "")
        cel.append(s)
    pa, pb = a[k]["px"], b[k]["px"]
    andou = [pa[0] - pb[0], pa[1] - pb[1], pb[2] - pa[2], pb[3] - pa[3]]   # + = cresceu
    part = f"{len(a[k]['partidas'])} → {len(b[k]['partidas'])}"
    bei = f"{sum(len(la[l]['na_beirada']) for l in LADOS)} → {sum(len(lb[l]['na_beirada']) for l in LADOS)}"
    esc = ", ".join(f"{l} {la[l]['escuro']:.2f}→{lb[l]['escuro']:.2f}" for l in LADOS
                    if min(la[l]["escuro"], lb[l]["escuro"]) < 0.6) or "-"
    print(f"| {k} | " + " | ".join(cel) + f" | {andou} | {part} | {bei} | {esc} |")
print()
print("tempo detectar_bordas, 32 paginas:", a["_tempo_detectar_bordas_s"], "->", b["_tempo_detectar_bordas_s"], "s")
