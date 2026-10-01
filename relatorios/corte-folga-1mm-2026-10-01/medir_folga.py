r"""Mede a folga de papel que o corte de bordas deixa depois da ultima tinta (01/10/2026).

Pedido: conferencia 5 do Samuel, P2 ("Sim, 1 mm"): o corte deixava ~0,6 mm
de papel depois da ultima letra (relatorios/corte-crista-2026-10-01/LEIA-ME.md).
Este script mede, nas 32 paginas do gabarito, ANTES e DEPOIS da mudanca em
core/recortar.py (rodar uma vez com cada codigo, gravando JSONs diferentes).

Para cada pagina, desenhada a 300 DPI (a resolucao do PDF, a mesma em que o
programa calcula o corte desde 28/09):

1. o (recorte, angulo) do programa, por core/pipeline._geometria (o mesmo que
   _guardar_geometria usa para a previa e para o PDF);
2. as pecas de tinta PARTIDAS pela borda do corte, na resolucao cheia (o
   medidor de 01/10, relatorios/corte-crista-2026-10-01/medir_corte_gabarito.py,
   copiado aqui sem mudar a regra);
3. a imagem FINAL da pagina (preparar_metade: cortar -> endireitar, como sai no
   PDF), e nela, de cada lado:
   - `folga_px`: a distancia, em pontos a 300 DPI, da beirada da imagem ate a
     peca de tinta mais perto (tinta: cinza abaixo de 60% do papel; peca com
     6 pontos ou mais, que NAO encosta na beirada). 11,8 pontos = 1 mm.
   - `na_beirada`: as pecas de tinta que encostam naquele lado (peca cortada
     ou borda escura entrando);
   - `escuro`: a media do cinza da faixa de 1 mm colada naquele lado, em
     fracao do papel (abaixo de 0,6 = faixa escura, borda do scanner).
   - `beirada_do_scan`: o corte ja esta na beirada da imagem desse lado (nao
     ha papel para dar folga).
Tambem mede o tempo de detectar_bordas (regra 6: o corte nao pode ficar mais
lento).

Uso: .venv\Scripts\python.exe relatorios\corte-folga-1mm-2026-10-01\medir_folga.py SAIDA.json
Isto e so um medidor: quem decide o corte e core/recortar.py.
"""
from __future__ import annotations

import inspect
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

from core import pipeline  # noqa: E402
from core.pdf_io import pagina_para_array  # noqa: E402
from core.recortar import detectar_bordas  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

DPI = 300
MM = DPI / 25.4
PAGINA = SimpleNamespace(recorte=None, angulo_manual=None)
LADOS = ("esq", "dir", "topo", "pe")
# o codigo novo aceita o DPI (folga em milimetros); o antigo nao
COM_DPI = "dpi" in inspect.signature(pipeline._geometria).parameters


def _projeto():
    projeto = Projeto(caminho_entrada="")
    projeto.cortar_bordas = True
    projeto.endireitar = True
    projeto.dividir_folhas = False
    projeto.qualidade_dpi = DPI
    return projeto


def pecas_partidas(img, recorte):
    """Pecas de tinta (resolucao cheia) que a borda do corte atravessa.
    Mesma regra de relatorios/corte-crista-2026-10-01/medir_corte_gabarito.py."""
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


def folgas_da_saida(saida):
    """De cada lado da imagem final: folga ate a tinta, pecas na beirada, escuro."""
    h, w = saida.shape[:2]
    cinza = cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY) if saida.ndim == 3 else saida
    papel = float(np.percentile(cinza[::4, ::4], 90))
    tinta = (cinza < 0.6 * papel).astype(np.uint8)
    n, _, cx, _ = cv2.connectedComponentsWithStats(tinta, connectivity=8)
    a, b, cw, ch, area = (cx[1:, i].astype(np.int64) for i in range(5))
    grande = area >= 6
    toca = {"esq": a <= 0, "dir": a + cw >= w, "topo": b <= 0, "pe": b + ch >= h}
    alguma = toca["esq"] | toca["dir"] | toca["topo"] | toca["pe"]
    livre = grande & ~alguma
    dist = {"esq": a, "dir": w - (a + cw), "topo": b, "pe": h - (b + ch)}
    faixa = max(1, int(round(MM)))
    bandas = {"esq": cinza[:, :faixa], "dir": cinza[:, w - faixa:],
              "topo": cinza[:faixa, :], "pe": cinza[h - faixa:, :]}
    lados = {}
    for lado in LADOS:
        d = dist[lado][livre]
        na_beirada = [[int(a[i]), int(b[i]), int(a[i] + cw[i]), int(b[i] + ch[i]), int(area[i])]
                      for i in np.flatnonzero(grande & toca[lado])]
        lados[lado] = {"folga_px": int(d.min()) if d.size else None,
                       "na_beirada": na_beirada,
                       "escuro": round(float(bandas[lado].mean()) / max(papel, 1.0), 3)}
    return lados, papel


def main():
    destino = Path(sys.argv[1])
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
    projeto = _projeto()
    resultado = {"_com_dpi": COM_DPI}
    tempo_total = 0.0
    for nome, info in lista["paginas"].items():
        doc = fitz.open(RAIZ / "gabarito" / info["pdf"])
        img = pagina_para_array(doc, 0, dpi=DPI)
        doc.close()
        t = time.perf_counter()
        detectar_bordas(img, dpi=DPI) if COM_DPI else detectar_bordas(img)
        tempo = time.perf_counter() - t
        tempo_total += tempo
        if COM_DPI:
            recorte, angulo = pipeline._geometria(img, PAGINA, projeto, dpi=DPI)
        else:
            recorte, angulo = pipeline._geometria(img, PAGINA, projeto)
        recorte = recorte or (0.0, 0.0, 1.0, 1.0)
        partidas, px = pecas_partidas(img, recorte)
        saida = pipeline.preparar_metade(img, ConfigFolha(indice=0), ConfigPagina(indice=0, folha=0),
                                         projeto, geometria=(recorte, angulo))
        lados, papel = folgas_da_saida(saida)
        h, w = img.shape[:2]
        beirada = {"esq": px[0] <= 0, "dir": px[2] >= w, "topo": px[1] <= 0, "pe": px[3] >= h}
        for lado in LADOS:
            lados[lado]["beirada_do_scan"] = bool(beirada[lado])
        resultado[nome] = {"recorte": [round(v, 6) for v in recorte], "angulo": round(angulo, 4),
                           "px": list(px), "tamanho": [w, h], "saida": [saida.shape[1], saida.shape[0]],
                           "partidas": partidas, "lados": lados, "papel": round(papel, 1),
                           "tempo_s": round(tempo, 4)}
        folgas = " ".join(f"{l}={lados[l]['folga_px']}" + ("*" if beirada[l] else "")
                          + (f"!{len(lados[l]['na_beirada'])}" if lados[l]["na_beirada"] else "")
                          for l in LADOS)
        print(f"{nome:16s} ang={angulo:+.2f} partidas={len(partidas)} {folgas} "
              f"escuro_min={min(lados[l]['escuro'] for l in LADOS):.2f} t={tempo:.3f}s", flush=True)
    resultado["_tempo_detectar_bordas_s"] = round(tempo_total, 3)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, indent=1, ensure_ascii=False), encoding="utf-8")
    print("tempo detectar_bordas (32 paginas):", round(tempo_total, 3))


if __name__ == "__main__":
    main()
