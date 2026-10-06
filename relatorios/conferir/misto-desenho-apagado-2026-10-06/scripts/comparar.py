"""Compara o Misto de hoje com o consertado em cada pagina e monta as imagens
de olhar (06/10/2026, tarefa "Misto: desenho claro apagado").

Le <TRABALHO>/base (rodar_base.py: original, Preto e branco puro), e
<TRABALHO>/antes e <TRABALHO>/depois (rodar_misto.py). Para cada pagina:
  - quantos pontos mudaram (soma da diferenca das imagens; 0 = identica);
  - imagens/<pagina>.jpg (pagina inteira, reduzida) e, se mudou,
    imagens/<pagina>__detalhe.jpg (o pedaco onde mais mudou, ampliado), as
    duas com CINCO quadros lado a lado: Original | Misto de hoje | Misto
    consertado | Preto e branco puro | Onde mudou. O quinto quadro e uma copia
    clareada do original com o que voltou pintado em azul transparente: nada
    e desenhado por cima dos quatro primeiros (pedido do Samuel).

Uso: python comparar.py   (grava <TRABALHO>/comparar.json e <TRABALHO>/imagens/)
"""

from __future__ import annotations

import json

import cv2
import numpy as np

import comum

T = comum.TRABALHO
IMAGENS = T / "imagens"
TITULOS = ("Original", "Misto de hoje", "Misto consertado", "Preto e branco puro", "Onde mudou (azul)")


def _bgr(x):
    return cv2.cvtColor(x, cv2.COLOR_GRAY2BGR) if x.ndim == 2 else x


def _onde_mudou(img, mudou):
    """Copia clareada do original, com os pontos que mudaram em azul
    transparente (o quadro separado, nunca por cima do conteudo)."""
    base = cv2.addWeighted(_bgr(img), 0.35, np.full_like(_bgr(img), 255), 0.65, 0)
    azul = base.copy()
    azul[mudou] = (230, 120, 20)
    return cv2.addWeighted(base, 0.35, azul, 0.65, 0)


def _quadro(x, largura):
    a, l = x.shape[:2]
    f = largura / l
    return cv2.resize(x, (largura, max(1, round(a * f))),
                      interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_NEAREST)


def _montar(partes, largura):
    quadros = [_quadro(_bgr(p), largura) for p in partes]
    alto = max(q.shape[0] for q in quadros)
    linha = []
    for q, t in zip(quadros, TITULOS):
        q = cv2.copyMakeBorder(q, 0, alto - q.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        q = cv2.copyMakeBorder(q, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=(160, 160, 160))
        cab = np.full((34, q.shape[1], 3), 255, np.uint8)
        cv2.putText(cab, t, (4, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (40, 40, 40), 1, cv2.LINE_AA)
        linha.append(np.vstack([cab, q]))
        linha.append(np.full((alto + 36, 10, 3), 255, np.uint8))
    return np.hstack(linha[:-1])


def _detalhe(mudou, h):
    """A caixa (y0, y1, x0, x1) em volta do maior amontoado do que mudou."""
    r = max(3, int(h / 3))
    junto = cv2.dilate(mudou.view(np.uint8), np.ones((r, r), np.uint8))
    n, rot, st, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    soma = np.bincount(rot[mudou], minlength=n)
    soma[0] = 0
    i = int(np.argmax(soma))
    x, y, w, hh = st[i, :4]
    folga = int(1.5 * h)
    a, l = mudou.shape
    lado = max(w, hh) + 2 * folga
    cx, cy = x + w // 2, y + hh // 2
    y0, x0 = max(0, cy - lado // 2), max(0, cx - lado // 2)
    return y0, min(a, y0 + lado), x0, min(l, x0 + lado)


def main() -> None:
    IMAGENS.mkdir(parents=True, exist_ok=True)
    tempos_a = json.loads((T / "antes" / "tempos.json").read_text(encoding="utf-8"))
    tempos_d = json.loads((T / "depois" / "tempos.json").read_text(encoding="utf-8"))
    resultado = {}
    for js in sorted((T / "base").glob("*.json")):
        nome = js.stem
        d = json.loads(js.read_text(encoding="utf-8"))
        z = np.load(T / "base" / f"{nome}.npz")
        antes = cv2.imread(str(T / "antes" / f"{nome}.png"), cv2.IMREAD_UNCHANGED)
        depois = cv2.imread(str(T / "depois" / f"{nome}.png"), cv2.IMREAD_UNCHANGED)
        diferenca = int(np.abs(antes.astype(np.int32) - depois.astype(np.int32)).sum())
        tinta_a = (_bgr(antes).min(axis=2) < 128)
        tinta_d = (_bgr(depois).min(axis=2) < 128)
        voltou = tinta_d & ~tinta_a
        saiu = tinta_a & ~tinta_d
        tinta_total = int(tinta_a.sum()) or 1
        resultado[nome] = {
            "pontos_que_voltaram": int(voltou.sum()),
            "pontos_que_sairam": int(saiu.sum()),
            "voltou_da_tinta": round(float(voltou.sum()) / tinta_total, 4),
            "soma_da_diferenca": diferenca, "identica": diferenca == 0,
            "tempo_antes_s": tempos_a[nome]["mediana_s"], "tempo_depois_s": tempos_d[nome]["mediana_s"],
            "igual_ao_programa": tempos_a[nome]["igual_ao_programa"],
            "desenho_fora": tempos_d[nome]["medidas"].get("desenho_fora"),
            "forte_fora_antes": tempos_a[nome]["medidas"].get("forte_fora"),
            "forte_fora_depois": tempos_d[nome]["medidas"].get("forte_fora"),
        }
        partes = (z["img"], antes, depois, z["pb"], _onde_mudou(z["img"], voltou | saiu))
        cv2.imwrite(str(IMAGENS / f"{nome}.jpg"), _montar(partes, 520), [cv2.IMWRITE_JPEG_QUALITY, 85])
        if diferenca:
            y0, y1, x0, x1 = _detalhe(voltou | saiu, max(d["altura_linha"], 20.0))
            resultado[nome]["detalhe"] = [int(y0), int(y1), int(x0), int(x1)]
            cortes = [p[y0:y1, x0:x1] for p in partes]
            cv2.imwrite(str(IMAGENS / f"{nome}__detalhe.jpg"), _montar(cortes, 420),
                        [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(nome, resultado[nome], flush=True)
    (T / "comparar.json").write_text(json.dumps(resultado, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
