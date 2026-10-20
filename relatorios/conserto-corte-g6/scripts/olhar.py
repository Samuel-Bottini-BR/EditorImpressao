"""Apoio da experiencia (so leitura): escreve, para uma pagina e uma variante,
a cobertura de tinta das linhas ou colunas de uma ponta da mascara do corte
(a "bruta", antes de apagar a borda solida, e a "limpa", a que o corte usa) e
quanto de cada uma e imagem de verdade (nao e cunha do giro). E recorta um
pedaco ampliado do desenho da mascara, para abrir e olhar.

USO  python olhar.py base variante lado [quantas]     lado = esq, dir, topo, pe
     python olhar.py --recorte arquivo.png x0 y0 x1 y1 saida.png   (fracoes 0..1)
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np


def recorte() -> int:
    _, _, arquivo, x0, y0, x1, y1, saida = sys.argv
    img = cv2.imread(arquivo)
    a, l = img.shape[:2]
    p = img[int(float(y0) * a):int(float(y1) * a), int(float(x0) * l):int(float(x1) * l)]
    f = min(4.0, 1800 / max(p.shape[:2]))
    cv2.imwrite(saida, cv2.resize(p, None, fx=f, fy=f, interpolation=cv2.INTER_NEAREST))
    return 0


def main() -> int:
    if sys.argv[1] == "--recorte":
        return recorte()
    import experiencia as E

    base, variante, lado = sys.argv[1:4]
    quantas = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    dados = json.loads((E.PASTA / "dados-verificador.json").read_text(encoding="utf-8"))
    inteira = cv2.imread(str(E.FINAIS / f"{base}__inteira.jpg"))
    cinza = cv2.cvtColor(inteira, cv2.COLOR_BGR2GRAY)
    angulo = dados[base]["C"]["angulo"]
    E.CTX.clear()
    E.CTX.update(angulo=angulo, variante=variante, base=base, margem=1)
    reta = E.girar(cinza, angulo, variante[0])
    rec = E.R.detectar_bordas(reta, dpi=300).tupla
    bruta, limpa, fora = E.CTX["bruta"], E.CTX["limpa"], E.CTX["fora"]
    eixo = 0 if lado in ("esq", "dir") else 1
    b, l, v = bruta.mean(axis=eixo), limpa.mean(axis=eixo), (~fora).mean(axis=eixo)
    n = len(b)
    idx = range(quantas) if lado in ("esq", "topo") else range(n - 1, n - 1 - quantas, -1)
    print(base, variante, "angulo", angulo, "mascara", bruta.shape[::-1], "recorte", [round(float(x), 4) for x in rec])
    print("  i  bruta limpa valido")
    for i in idx:
        print(f"{i:4d} {b[i]:5.2f} {l[i]:5.2f} {v[i]:5.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
