"""So INDICATIVO: como ficariam alguns pares de detectores juntos (pergunta do criterio 3).

NAO e o item 1.5 (juntar os detectores de verdade): aqui so se somam ou se
cruzam as mascaras de caixas ja medidas, para ver se os erros de um cobrem os
do outro. Duas contas por par:
- "os dois concordam" (intersecao): so e texto onde os dois poem caixa;
- "qualquer um" (uniao): e texto onde pelo menos um poe caixa.

Uso (ambiente de teste): .venv-ocr\\Scripts\\python.exe pares.py
Grava relatorios\\...\\pares.json.
"""

from __future__ import annotations

import json
import statistics as st

import comum as C
from medir import DETECTORES, linhas_de

PARES = [("K1", "D2"), ("K1", "P3"), ("D2", "P3"), ("T1", "D2"), ("K1", "T1")]


def main() -> None:
    zonas = C.carregar_zonas()
    todos = dict(DETECTORES)
    res = {f"{a}+{b}": {"e": {}, "ou": {}} for a, b in PARES}
    for pagina in C.PAGINAS:
        img = C.ler_imagem(pagina)
        h, w = img.shape[:2]
        zm = C.mascaras_zonas(zonas[pagina], (h, w))
        tinta = C.tinta(img, C.dpi_trabalho(pagina))
        mascaras = {}
        for d in {x for par in PARES for x in par}:
            linhas, _, _ = linhas_de(d, pagina, todos)
            mascaras[d] = C.mascara_linhas(linhas or [], (h, w))
        for a, b in PARES:
            chave = f"{a}+{b}"
            res[chave]["e"][pagina] = C.medir(tinta, zm, mascaras[a] & mascaras[b])
            res[chave]["ou"][pagina] = C.medir(tinta, zm, mascaras[a] | mascaras[b])
        print(pagina, flush=True)
    (C.RELATORIO / "pares.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for chave, modos in res.items():
        for modo, pags in modos.items():
            txt = [v["texto_achado"] for p, v in pags.items() if p in C.PAGINAS_19 and v["texto_achado"] is not None]
            obrig = [v["figura_tomada"] for p, v in pags.items() if p in C.OBRIGATORIAS and v["figura_tomada"] is not None]
            todas = [(p, v["figura_tomada"]) for p, v in pags.items() if v["figura_tomada"] is not None]
            grad = [pags[p]["texto_achado"] for p in C.PAGINAS_MANUSCRITO_EXTRA]
            acima = [p for p, f in todas if f > 0.01]
            print(f"{chave:6s} {modo:2s} texto medio {100*st.mean(txt):5.1f}  >=98%: {sum(t >= .98 for t in txt):2d}/19  "
                  f"pior obrig {100*max(obrig):5.2f}%  figura>1% em {len(acima)} ({', '.join(acima)})  "
                  f"graduale {' '.join(f'{100*g:.1f}' for g in grad)}")


if __name__ == "__main__":
    main()
