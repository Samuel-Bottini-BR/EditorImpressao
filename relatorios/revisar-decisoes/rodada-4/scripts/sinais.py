"""Rodada 2: mede, em cada pagina rodada (rodar.py), os sinais da opcao 1 do
estudo e um sinal novo, a "beirada escura", e grava <TRABALHO>/sinais-rodada2.json.

Opcao 1 do estudo (relatorios/revisar-criterios-2026-10-06, gerar_relatorio.py):
  (1) apagado_junto >= 2%   o jeito de fabrica apagou tinta amontoada (desenho comido)
  (2) vazou_da_gravura >= 10%  um pedaco grande encosta na gravura achada por fora
  (3) apagado_a >= 2,5%     o jeito de fabrica apagou muita tinta fora do texto
  (a conta de apagado_junto e a do tabela.py do estudo, copiada aqui)

Sinal novo (4) "beirada escura": no resultado do jeito de fabrica, mancha
CHEIA de tinta (sobra de uma abertura com um quadrado de 1,5% do lado menor
da pagina: letra, fio e moldura somem; tarja e faixa ficam) que ENCOSTA na
beirada da pagina (ate 1% dela), fora da gravura achada. Medido em fracao
da area da pagina.

Uso: python sinais.py [pid,pid,...]
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np

import comum
import medir

LIMITE_JUNTO = 0.04


def extra(base: str, dados: dict, z) -> dict:
    s, m = medir.sinais(dados, z)
    h = max(float(dados["altura_linha"]), 1.0)
    total = max(int(z["base_tinta"].sum()), 1)
    e = m["apagado_a"].astype(np.float32)
    k = max(3, int(round(2 * h)))
    dens = cv2.boxFilter(e, -1, (k, k), normalize=True)
    junto = m["apagado_a"] & (dens > LIMITE_JUNTO)
    s["dens_max"] = float(dens.max())
    s["apagado_junto"] = float(junto.sum()) / total
    return s


def beirada_escura(tinta: np.ndarray) -> tuple[float, np.ndarray]:
    """Fracao da pagina coberta por mancha cheia de tinta encostada na beirada."""
    alt, larg = tinta.shape
    f = 1000 / max(alt, larg)                      # trabalha pequeno (rapido)
    peq = cv2.resize(tinta.astype(np.uint8) * 255, (max(1, round(larg * f)), max(1, round(alt * f))),
                     interpolation=cv2.INTER_AREA) > 127
    a, l = peq.shape
    lado = max(3, int(round(0.015 * min(a, l))))
    cheia = cv2.morphologyEx(peq.astype(np.uint8), cv2.MORPH_OPEN,
                             np.ones((lado, lado), np.uint8)) > 0
    n, rot, st, _ = cv2.connectedComponentsWithStats(cheia.astype(np.uint8), connectivity=8)
    m = max(1, int(round(0.01 * min(a, l))))
    borda = np.zeros_like(cheia)
    borda[:m, :] = borda[-m:, :] = True
    borda[:, :m] = borda[:, -m:] = True
    ids = np.unique(rot[cheia & borda])
    ids = ids[ids > 0]
    mascara = np.isin(rot, ids)
    return float(mascara.sum()) / (a * l), mascara


def opcao1(s: dict) -> bool:
    return bool(s["apagado_junto"] >= 0.02 or s["apagado_a"] >= 0.025
                or s["vazou_da_gravura"] >= 0.10)


def main() -> None:
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    saida_arq = comum.TRABALHO / "sinais-rodada2.json"
    todos = json.loads(saida_arq.read_text(encoding="utf-8")) if saida_arq.exists() else {}
    for js in sorted(comum.DADOS.glob("*.json")):
        base = js.stem
        dados = json.loads(js.read_text(encoding="utf-8"))
        if so and dados["pid"] not in so:
            continue
        z = dict(np.load(comum.DADOS / f"{base}.npz"))
        s = extra(base, dados, z)
        # so fora da gravura achada (a foto que encosta na beirada, como a do
        # Opus Majus 20, e figura, nao fundo do scanner)
        s["beirada_a"], _ = beirada_escura(z["a_tinta"] & ~z["imagem"])
        s["beirada_pb"], _ = beirada_escura(z["pb_tinta"] & ~z["imagem"])
        s["aviso_hoje"] = bool(dados["modos"]["rede"]["para_revisar"])
        s["opcao1"] = opcao1(s)
        s = {k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()}
        todos[base] = s
        print(f"{base:28s} hoje={int(s['aviso_hoje'])} op1={int(s['opcao1'])} "
              f"junto={s['apagado_junto']:.3f} apag={s['apagado_a']:.3f} vaz={s['vazou_da_gravura']:.3f} "
              f"beirada={s['beirada_a']:.3f}", flush=True)
        del z
    saida_arq.write_text(json.dumps(todos, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
