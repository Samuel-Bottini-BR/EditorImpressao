r"""Mede o corte de bordas nas 32 paginas do gabarito (01/10/2026).

Para cada pagina: desenha a 300 DPI (a resolucao do PDF, a mesma que o
programa usa para o corte desde 28/09), calcula o (recorte, angulo) como
core/pipeline._geometria e conta, NA RESOLUCAO CHEIA, as pecas de tinta que a
borda do corte atravessa (parte dentro, parte fora) e quanto cada uma passa
para fora. Grava um JSON com tudo, para comparar antes x depois.

Uso: .venv\Scripts\python.exe relatorios\corte-crista-2026-10-01\medir_corte_gabarito.py SAIDA.json [--recortes]
(--recortes grava, ao lado do JSON, a faixa de cada borda com peca partida.)

Tinta na resolucao cheia: cinza abaixo de 60% do papel (percentil 90 do
cinza dentro do corte). Peca: pedaco ligado (8 vizinhos). Ficam de fora as
pecas que encostam na beirada da imagem (borda do scanner, folha vizinha) e
as maiores que 15% do lado (sombra, risco da beirada): nao sao conteudo que o
corte deva guardar. Isto e so um medidor; quem decide o corte e core/recortar.py.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import cv2
import fitz
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

from core.pdf_io import pagina_para_array  # noqa: E402
from core.pipeline import _geometria  # noqa: E402
from core.recortar import detectar_bordas  # noqa: E402

PROJETO = SimpleNamespace(cortar_bordas=True, endireitar=True)
PAGINA = SimpleNamespace(recorte=None, angulo_manual=None)


def pecas_partidas(img, recorte):
    """Pecas de tinta (resolucao cheia) que a borda do corte atravessa."""
    h, w = img.shape[:2]
    x, y, rw, rh = recorte
    x0, y0, x1, y1 = int(x * w), int(y * h), int((x + rw) * w), int((y + rh) * h)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    papel = float(np.percentile(cinza[y0:y1:8, x0:x1:8], 90))
    tinta = (cinza < 0.6 * papel).astype(np.uint8)
    n, _, cx, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    saida = []
    for i in range(1, n):
        a, b, cw, ch, area = (int(v) for v in cx[i])
        if a <= 1 or b <= 1 or a + cw >= w - 1 or b + ch >= h - 1:
            continue
        if cw > 0.15 * w or ch > 0.15 * h or area < 6:
            continue
        dentro = a >= x0 and b >= y0 and a + cw <= x1 and b + ch <= y1
        fora = a + cw <= x0 or a >= x1 or b + ch <= y0 or b >= y1
        if dentro or fora:
            continue
        passa = max(x0 - a, a + cw - x1, y0 - b, b + ch - y1, 0)
        lado = ("esq" if a < x0 else "dir" if a + cw > x1 else "topo" if b < y0 else "pe")
        saida.append({"caixa": [a, b, a + cw, b + ch], "area": area, "passa_px": passa, "lado": lado})
    return saida, (x0, y0, x1, y1)


def main():
    destino = Path(sys.argv[1])
    recortes = "--recortes" in sys.argv
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
    resultado = {}
    tempo_total = 0.0
    for nome, info in lista["paginas"].items():
        doc = fitz.open(RAIZ / "gabarito" / info["pdf"])
        img = pagina_para_array(doc, 0, dpi=300)
        doc.close()
        t = time.perf_counter()
        detectar_bordas(img)
        tempo = time.perf_counter() - t
        tempo_total += tempo
        recorte, angulo = _geometria(img, PAGINA, PROJETO)
        recorte = recorte or (0.0, 0.0, 1.0, 1.0)
        partidas, px = pecas_partidas(img, recorte)
        resultado[nome] = {"recorte": [round(v, 6) for v in recorte], "angulo": round(angulo, 4),
                           "px": list(px), "tamanho": [img.shape[1], img.shape[0]],
                           "partidas": partidas, "tempo_s": round(tempo, 4)}
        print(f"{nome:18s} {px} ang={angulo:+.2f} partidas={len(partidas)} "
              f"max_passa={max([p['passa_px'] for p in partidas], default=0)} t={tempo:.3f}s")
        if recortes and partidas:
            pasta = destino.parent / (destino.stem + "-recortes")
            pasta.mkdir(exist_ok=True)
            vis = img.copy()
            cv2.rectangle(vis, px[:2], px[2:], (0, 0, 255), 1)
            for k, p in enumerate(partidas):
                a, b, c, d = p["caixa"]
                m = 40
                cv2.imwrite(str(pasta / f"{nome}_{k:02d}_{p['lado']}.png"),
                            cv2.resize(vis[max(0, b - m):d + m, max(0, a - m):c + m], None, fx=3, fy=3,
                                       interpolation=cv2.INTER_NEAREST))
    resultado["_tempo_detectar_bordas_s"] = round(tempo_total, 3)
    destino.write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
    print("tempo detectar_bordas (32 paginas):", round(tempo_total, 3))


if __name__ == "__main__":
    main()
