"""Junta os sinais (medir.py) com o que eu vi (veredito.py) e conta, para cada
criterio: quantas paginas vao para "Para revisar", quantas dessas estavam
erradas de verdade, e quantas erradas ficam de fora.

Acrescenta o sinal "apagado_junto": a tinta que o jeito A manda para o branco
em lugares onde ela se amontoa (uma janela de 2 alturas de linha com mais de
LIMITE_JUNTO dos pontos apagados) - o desenho comido, nao o pontinho solto.

Uso: python tabela.py   (grava <TRABALHO>/tabela.json)
"""

from __future__ import annotations

import json

import cv2
import numpy as np

import comum
import medir
from veredito import VEREDITO

LIMITE_JUNTO = 0.04


def extra(base: str, dados: dict) -> dict:
    z = dict(np.load(comum.DADOS / f"{base}.npz"))
    s, m = medir.sinais(dados, z)
    h = max(float(dados["altura_linha"]), 1.0)
    total = max(int(z["base_tinta"].sum()), 1)
    e = m["apagado_a"].astype(np.float32)
    k = max(3, int(round(2 * h)))
    dens = cv2.boxFilter(e, -1, (k, k), normalize=True)
    junto = m["apagado_a"] & (dens > LIMITE_JUNTO)
    s["dens_max"] = float(dens.max())
    s["apagado_junto"] = float(junto.sum()) / total
    # a mesma conta para o C: a tinta forte que ele apaga, amontoada
    f = m["forte"].astype(np.float32)
    densf = cv2.boxFilter(f, -1, (k, k), normalize=True)
    s["forte_junto"] = float((m["forte"] & (densf > LIMITE_JUNTO)).sum()) / total
    return s


def main() -> None:
    linhas = {}
    for js in sorted(comum.DADOS.glob("*.json")):
        base = js.stem
        dados = json.loads(js.read_text(encoding="utf-8"))
        s = extra(base, dados)
        a, c, nota = VEREDITO[base]
        s.update(veredito_a=a, veredito_c=c, nota=nota,
                 aviso_hoje=dados["modos"]["rede"]["para_revisar"])
        linhas[base] = s
        print(f"{base:28s} A={a:6s} C={c:6s} forte={s['forte_fora']:.3f} apA={s['apagado_a']:.3f} "
              f"junto={s['apagado_junto']:.4f} dens={s['dens_max']:.3f} fjunto={s['forte_junto']:.3f} "
              f"vaz={s['vazou_da_gravura']:.3f} f1.5={s['fortes_grandes']} latr={s['linhas_atravessadas']}",
              flush=True)
    (comum.TRABALHO / "tabela.json").write_text(json.dumps(linhas, indent=1, ensure_ascii=False),
                                                encoding="utf-8")


if __name__ == "__main__":
    main()
