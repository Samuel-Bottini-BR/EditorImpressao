"""Prototipo (so para medir; nao e o codigo do programa): variantes de "guardar
o desenho claro" no jeito "Guardar a tinta forte", rodadas nos dados gravados
por rodar_base.py, sem o leitor de texto.

Para cada pagina: quantos pontos de tinta cada variante devolve (que o Misto de
hoje apagava), em quantas regioes, e uma imagem de olhar com o que volta em
azul por cima do Misto de hoje.

Uso: python prototipo.py variante [pid,...]
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np

import comum

BASE = comum.TRABALHO / "base"
OLHAR = comum.TRABALHO / "prototipo"


def rede_de_hoje(binaria, cinza, linhas, h, imagem):
    tinta = binaria == 0
    fora = tinta & ~linhas & ~imagem
    dentro = tinta & linhas
    if not (dentro.any() and fora.any()):
        return fora, np.zeros_like(fora), None
    escuro = float(np.median(cinza[dentro]))
    n, rot, st, _ = cv2.connectedComponentsWithStats(fora.view(np.uint8), connectivity=8)
    fica = np.zeros(n, bool)
    fica[np.unique(rot[fora & (cinza <= escuro)])] = True
    fica &= st[:, cv2.CC_STAT_AREA] >= (max(h, 1.0) / 6.0) ** 2
    fica[0] = False
    return fora, fica[rot], escuro


def desenho(fora, forte, h, raio_f=0.08, minimo_h2=1.0, lado_h=1.0, total_h2=0.0):
    """Regioes = tinta de fora alargada `raio`; uma regiao com tinta forte
    (semente) e com bastante tinta apagada (>= minimo_h2 * h^2) e que mede
    pelo menos lado_h * h nos dois lados: toda a tinta dela fica."""
    raio = max(1, int(round(raio_f * h)))
    elem = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    junto = cv2.dilate(fora.view(np.uint8), elem)
    n, rot, st, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    tem_semente = np.zeros(n, bool)
    tem_semente[np.unique(rot[forte])] = True
    apagada = np.bincount(rot[fora & ~forte], minlength=n)
    toda = np.bincount(rot[fora], minlength=n)
    ok = tem_semente & (apagada >= minimo_h2 * h * h) & (toda >= total_h2 * h * h)
    ok &= (st[:, cv2.CC_STAT_WIDTH] >= lado_h * h) & (st[:, cv2.CC_STAT_HEIGHT] >= lado_h * h)
    ok[0] = False
    return fora & ok[rot], int(ok.sum())


VARIANTES = {
    "v1": dict(raio_f=0.08, minimo_h2=1.0, lado_h=1.0),
    "v2": dict(raio_f=0.05, minimo_h2=1.0, lado_h=1.0),
    "v3": dict(raio_f=0.12, minimo_h2=1.0, lado_h=1.0),
    "v0": dict(raio_f=0.08, minimo_h2=0.0, lado_h=0.0),
    "v4": dict(raio_f=0.08, minimo_h2=0.0, lado_h=0.0, total_h2=1.0),
    "v5": dict(raio_f=0.08, minimo_h2=0.0, lado_h=0.0, total_h2=2.0),
    "v6": dict(raio_f=0.05, minimo_h2=0.0, lado_h=0.0, total_h2=2.0),
    "v7": dict(raio_f=0.08, minimo_h2=0.0, lado_h=0.0, total_h2=0.3),
}


def main():
    var = sys.argv[1]
    params = VARIANTES[var]
    so = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    destino = OLHAR / var
    destino.mkdir(parents=True, exist_ok=True)
    tabela = {}
    for js in sorted(BASE.glob("*.json")):
        d = json.loads(js.read_text(encoding="utf-8"))
        if so and d["pid"] not in so:
            continue
        z = np.load(BASE / f"{js.stem}.npz")
        h = d["altura_linha"]
        if not d["tem_linhas"] or h <= 0:
            tabela[js.stem] = {"sem_linhas": True}
            continue
        fora, forte, escuro = rede_de_hoje(z["binaria"], z["cinza"], z["linhas"], h, z["imagem"])
        if escuro is None:
            tabela[js.stem] = {"sem_tinta": True}
            continue
        volta, regioes = desenho(fora, forte, h, **params)
        volta &= ~forte
        total = int((z["binaria"] == 0).sum()) or 1
        apagada = int((fora & ~forte).sum())
        tabela[js.stem] = {"volta": int(volta.sum()), "volta_frac": round(volta.sum() / total, 4),
                           "apagada_hoje": apagada,
                           "volta_da_apagada": round(volta.sum() / max(apagada, 1), 3),
                           "regioes": regioes}
        print(js.stem, tabela[js.stem], flush=True)
        if volta.any():
            a = z["a"]
            a3 = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR) if a.ndim == 2 else a.copy()
            a3[volta] = (255, 120, 0)
            ori = z["img"]
            partes = [comum.reduzir(x, 1300) for x in (ori, a3)]
            cv2.imwrite(str(destino / f"{js.stem}.jpg"), np.hstack(partes),
                        [cv2.IMWRITE_JPEG_QUALITY, 85])
    (destino / "tabela.json").write_text(json.dumps(tabela, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
