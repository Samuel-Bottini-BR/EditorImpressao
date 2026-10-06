"""Mede os sinais candidatos a "Para revisar" em cada pagina rodada por rodar.py
e monta as imagens de olhar (original | jeito A | mapa).

Sinais (todos so FORA das gravuras achadas; "tinta" = o preto e branco de base
do Misto; "linha" = as caixas do leitor de texto, alargadas como no programa;
h = altura mediana das linhas):

  forte_fora      o de hoje: tinta forte fora das linhas / toda a tinta
  apagado_a       tinta fora das linhas que o jeito A manda para o branco
  apagado_a_grande  so os pedacos apagados do tamanho de uma letra ou maiores
  apagado_a_colado  pedacos apagados no A encostados (ate h/4) em tinta que ficou
                  (um desenho comido pela metade, a pauta, a hachura)
  cortado_a / cortado_c  pedacos inteiros de tinta que a caixa de uma linha
                  corta ao meio (um pedaco dentro e um pedaco grande fora) e cuja
                  parte de fora some naquele jeito
  linhas_atravessadas  quantas linhas do leitor sao atravessadas por um traco
                  comprido (pedaco com altura > 2,5 h): o leitor pegou um pedaco
                  de moldura, capitular ou desenho como se fosse texto
  linhas_altas    quantas linhas tem mais de 2 vezes a altura mediana
  linhas_na_gravura  quantas linhas encostam na gravura achada
  vazou_da_gravura  tinta de pedacos grandes (>= 1,5 h) encostados na gravura
                  achada, do lado de fora: a figura passou da beirada
  n_linhas        quantas linhas o leitor achou

Uso: python medir.py   (grava <TRABALHO>/sinais.json e <TRABALHO>/olhar/*.jpg)
"""

from __future__ import annotations

import json
import sys

import cv2
import numpy as np

import comum


def _componentes(mascara):
    n, rot, stats, _c = cv2.connectedComponentsWithStats(mascara.view(np.uint8), connectivity=8)
    return n, rot, stats


def sinais(dados: dict, z) -> tuple[dict, dict]:
    cinza = z["cinza"]
    T = z["base_tinta"]
    L = z["linhas"]
    IMG = z["imagem"]
    h = max(float(dados["altura_linha"]), 1.0)
    total = max(int(T.sum()), 1)
    fora = T & ~L & ~IMG
    dentro = T & L
    s: dict = {"n_linhas": dados["n_linhas"], "altura_linha": round(h, 1),
               "tinta_total": total, "tinta_fora": float(fora.sum()) / total}
    mapas: dict = {}

    # a rede (a mesma conta de core.misto._fora_do_texto)
    forte = np.zeros_like(fora)
    n, rot, st = _componentes(fora)
    if dentro.any() and fora.any() and n > 1:
        escuro = float(np.median(cinza[dentro]))
        fica = np.zeros(n, bool)
        fica[np.unique(rot[fora & (cinza <= escuro)])] = True
        fica &= st[:, cv2.CC_STAT_AREA] >= (h / 6.0) ** 2
        fica[0] = False
        forte = fica[rot]
    apagado_a = fora & ~forte
    s["forte_fora"] = float(forte.sum()) / total
    s["apagado_a"] = float(apagado_a.sum()) / total

    # pedacos apagados no A: grandes, e colados em tinta que ficou
    grande = np.zeros(n, bool)
    if n > 1:
        tam = np.maximum(st[:, cv2.CC_STAT_WIDTH], st[:, cv2.CC_STAT_HEIGHT])
        grande = tam >= h
        grande[0] = False
    # pecas fortes fora das linhas (o que o C apaga): quantas do tamanho de
    # meia letra ou mais, e quantas maiores que uma letra e meia
    if n > 1 and forte.any():
        ids_f = np.unique(rot[forte])
        ids_f = ids_f[ids_f > 0]
        tam_f = np.maximum(st[ids_f, cv2.CC_STAT_WIDTH], st[ids_f, cv2.CC_STAT_HEIGHT])
        s["fortes_meia_letra"] = int((tam_f >= 0.5 * h).sum())
        s["fortes_grandes"] = int((tam_f >= 1.5 * h).sum())
        s["maior_forte_h"] = round(float(tam_f.max()) / h, 2) if len(tam_f) else 0.0
    else:
        s["fortes_meia_letra"] = s["fortes_grandes"] = 0
        s["maior_forte_h"] = 0.0
    apag_grande = apagado_a & grande[rot]
    s["apagado_a_grande"] = float(apag_grande.sum()) / total
    raio = max(2, int(round(h / 4)))
    elem = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * raio + 1, 2 * raio + 1))
    ficou_a = (forte | dentro)
    perto = cv2.dilate(ficou_a.view(np.uint8), elem) > 0
    colado = np.zeros(n, bool)
    if n > 1:
        ids = np.unique(rot[apagado_a & perto])
        colado[ids] = True
        colado[0] = False
    apag_colado = apagado_a & colado[rot]
    s["apagado_a_colado"] = float(apag_colado.sum()) / total
    # o mesmo, so com pedacos colados que sejam do tamanho de letra ou maiores
    s["apagado_a_colado_grande"] = float((apagado_a & (colado & grande)[rot]).sum()) / total

    # pedacos inteiros cortados pela caixa de uma linha
    inteiro = T & ~IMG
    n2, rot2, st2 = _componentes(inteiro)
    cort_a = np.zeros_like(fora)
    cort_c = np.zeros_like(fora)
    atravessados = np.zeros(n2, bool)
    if n2 > 1:
        dentro_px = np.bincount(rot2[inteiro & L], minlength=n2)
        fora_px = np.bincount(rot2[inteiro & ~L], minlength=n2)
        cortado = (dentro_px >= 1) & (fora_px >= (h / 2.0) ** 2)
        cortado[0] = False
        cort_c = fora & cortado[rot2]
        cort_a = apagado_a & cortado[rot2]
        atravessados = st2[:, cv2.CC_STAT_HEIGHT] > 2.5 * h
        atravessados[0] = False
    s["cortado_a"] = float(cort_a.sum()) / total
    s["cortado_c"] = float(cort_c.sum()) / total

    # as linhas uma a uma
    alt, larg = T.shape
    altas = na_grav = atrav = 0
    alturas = []
    caixas = []
    for p in dados["poligonos"]:
        pts = np.asarray(p)
        x0, y0 = max(0, pts[:, 0].min()), max(0, pts[:, 1].min())
        x1, y1 = min(larg, pts[:, 0].max() + 1), min(alt, pts[:, 1].max() + 1)
        if x1 <= x0 or y1 <= y0:
            continue
        caixas.append((x0, y0, x1, y1))
        alturas.append(y1 - y0)
    med = float(np.median(alturas)) if alturas else h
    suspeitas = np.zeros((alt, larg), bool)
    folga = int(round(0.3 * h))
    for (x0, y0, x1, y1) in caixas:
        motivo = False
        if (y1 - y0) > 2.0 * med:
            altas += 1
            motivo = True
        ya, yb = max(0, y0 - folga), min(alt, y1 + folga)
        xa, xb = max(0, x0 - folga), min(larg, x1 + folga)
        if IMG[ya:yb, xa:xb].any():
            na_grav += 1
            motivo = True
        ids = np.unique(rot2[y0:y1, x0:x1])
        ids = ids[ids > 0]
        passa = False
        if len(ids):
            ex = st2[ids, cv2.CC_STAT_LEFT]
            ey = st2[ids, cv2.CC_STAT_TOP]
            ex1 = ex + st2[ids, cv2.CC_STAT_WIDTH]
            ey1 = ey + st2[ids, cv2.CC_STAT_HEIGHT]
            alem = np.maximum.reduce([x0 - ex, ex1 - x1, y0 - ey, ey1 - y1])
            passa = bool((alem > h).any())
        if passa or atravessados[ids].any():
            atrav += 1
            motivo = True
        if motivo:
            suspeitas[y0:y1, x0:x1] = True
    s["linhas_altas"] = altas
    s["linhas_na_gravura"] = na_grav
    s["linhas_atravessadas"] = atrav
    s["n_caixas"] = len(caixas)

    # a figura que passou da beirada da gravura
    vazou = np.zeros_like(fora)
    if IMG.any() and n2 > 1:
        borda = cv2.dilate(IMG.view(np.uint8), np.ones((5, 5), np.uint8)) > 0
        toca = np.zeros(n2, bool)
        toca[np.unique(rot2[inteiro & borda])] = True
        tam2 = np.maximum(st2[:, cv2.CC_STAT_WIDTH], st2[:, cv2.CC_STAT_HEIGHT])
        toca &= tam2 >= 1.5 * h
        toca[0] = False
        vazou = inteiro & toca[rot2]
    s["vazou_da_gravura"] = float(vazou.sum()) / total
    s["imagem_frac"] = float(IMG.mean())

    mapas.update(forte=forte, apagado_a=apagado_a, apag_colado=apag_colado,
                 cort_c=cort_c, suspeitas=suspeitas, vazou=vazou)
    return s, mapas


def mapa(z, m) -> np.ndarray:
    """O mapa de olhar: tinta que fica em cinza escuro; vermelho = some no A;
    laranja = some so no C (a tinta forte fora das linhas); azul claro = linhas
    do leitor; verde claro = gravura; roxo claro = linha suspeita."""
    T = z["base_tinta"]
    alt, larg = T.shape
    tela = np.full((alt, larg, 3), 255, np.uint8)
    tela[z["linhas"]] = (255, 228, 200)
    tela[z["imagem"]] = (200, 245, 200)
    tela[m["suspeitas"] & ~T] = (255, 190, 235)
    tela[T] = (90, 90, 90)
    tela[z["imagem"] & T] = (60, 130, 60)
    tela[m["forte"]] = (0, 140, 255)          # laranja: some so no C
    tela[m["apagado_a"]] = (0, 0, 230)        # vermelho: some no A e no C
    return tela


def main() -> None:
    destino = comum.TRABALHO / "olhar"
    destino.mkdir(parents=True, exist_ok=True)
    todos = {}
    so = sys.argv[1].split(",") if len(sys.argv) > 1 else None
    for js in sorted(comum.DADOS.glob("*.json")):
        dados = json.loads(js.read_text(encoding="utf-8"))
        base = js.stem
        if so and dados["pid"] not in so:
            continue
        z = dict(np.load(comum.DADOS / f"{base}.npz"))
        s, m = sinais(dados, z)
        for modo, info in dados["modos"].items():
            s[f"aviso_{modo}"] = info["para_revisar"]
        s["forte_fora_programa"] = dados["modos"]["rede"]["medidas"].get("forte_fora")
        s["alertas_da_analise"] = dados["alertas_da_analise"]
        s["em_duvida"] = dados["em_duvida"]
        todos[base] = s
        tela = mapa(z, m)
        lado = 1100
        ori = cv2.imread(str(comum.DADOS / f"{base}__original.jpg"))
        a = cv2.imread(str(comum.DADOS / f"{base}__a.jpg"))
        c = cv2.imread(str(comum.DADOS / f"{base}__c.jpg"))
        partes = [comum.reduzir(x, lado) for x in (ori, a, c, tela)]
        hh = max(p.shape[0] for p in partes)
        partes = [cv2.copyMakeBorder(p, 0, hh - p.shape[0], 0, 8, cv2.BORDER_CONSTANT,
                                     value=(255, 255, 255)) for p in partes]
        cv2.imwrite(str(destino / f"{base}.jpg"), np.hstack(partes), [cv2.IMWRITE_JPEG_QUALITY, 82])
        cv2.imwrite(str(comum.DADOS / f"{base}__mapa.png"), comum.reduzir(tela, 2400))
        print(base, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()
                     if k not in ("alertas_da_analise",)}, flush=True)
    saida = comum.TRABALHO / "sinais.json"
    antigo = json.loads(saida.read_text(encoding="utf-8")) if (so and saida.exists()) else {}
    antigo.update(todos)
    saida.write_text(json.dumps(antigo, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
