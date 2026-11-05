"""Desenha o gráfico do relatório da memória (04/11/2026).

Lê as medidas de relatorios/memoria-pdf/medidas/*.json (gravadas por
medir_memoria.py) e desenha, em grafico.png, a memória do programa (bytes
privados do processo principal) ao longo do processamento do Rhetorica, antes
e depois do conserto, para 30, 90 e 270 folhas. Só OpenCV e numpy (o programa
não tem matplotlib). Texto sem acento no desenho (o OpenCV não desenha
acentos); a explicação em português vai no relatório.

Uso: python relatorios/memoria-pdf/desenhar_grafico.py
Seguro mudar: cores, tamanhos. Nada aqui mexe no programa.
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

PASTA = Path(__file__).resolve().parent
LARGURA, ALTURA = 1400, 700
MARGEM_E, MARGEM_D, MARGEM_C, MARGEM_B = 110, 330, 60, 80
CORES = {30: (60, 160, 60), 90: (200, 120, 30), 270: (40, 40, 200)}   # BGR


def _amostras(nome: str):
    caminho = PASTA / "medidas" / nome
    if not caminho.is_file():
        return None
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    fases_do_processar = {"processar as páginas", "gravar o PDF", "pronto", "caiu"}
    pontos = [(a[0], a[2]) for a in dados["amostras"] if a[1] in fases_do_processar]
    if not pontos:
        return None
    t0 = pontos[0][0]
    return [(t - t0, mb) for t, mb in pontos], dados.get("erro")


def desenhar() -> Path:
    series = []
    for n in (30, 90, 270):
        for quando, tracejado in (("antes", False), ("depois", True)):
            s = _amostras(f"rh-{n}-processar-{quando}.json")
            if s:
                series.append((n, quando, tracejado, s[0], s[1]))
    t_max = max(p[0] for *_x, pts, _e in series for p in pts) or 1
    mb_max = max(3200, max(p[1] for *_x, pts, _e in series for p in pts))
    img = np.full((ALTURA, LARGURA, 3), 255, np.uint8)
    x0, y0, x1, y1 = MARGEM_E, MARGEM_C, LARGURA - MARGEM_D, ALTURA - MARGEM_B

    def ponto(t, mb):
        return (int(x0 + (x1 - x0) * t / t_max), int(y1 - (y1 - y0) * mb / mb_max))

    for mb in range(0, int(mb_max) + 1, 500):
        y = ponto(0, mb)[1]
        cv2.line(img, (x0, y), (x1, y), (225, 225, 225), 1)
        cv2.putText(img, f"{mb} MB", (10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
    cv2.rectangle(img, (x0, y0), (x1, y1), (120, 120, 120), 1)
    for minuto in range(0, int(t_max / 60) + 1, 2):
        x = ponto(minuto * 60, 0)[0]
        cv2.putText(img, f"{minuto} min", (x - 15, y1 + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (90, 90, 90), 1)
    for n, quando, tracejado, pts, erro in series:
        cor = CORES[n]
        caminho = [ponto(t, mb) for t, mb in pts]
        for i, (a, b) in enumerate(zip(caminho, caminho[1:])):
            if tracejado and (i // 4) % 2:
                continue
            cv2.line(img, a, b, cor, 3 if not tracejado else 2, cv2.LINE_AA)
        if erro:
            cv2.drawMarker(img, caminho[-1], (0, 0, 220), cv2.MARKER_TILTED_CROSS, 28, 4)
    y = y0 + 10
    for n in (30, 90, 270):
        for quando, tracejado in (("antes", False), ("depois", True)):
            if not any(s[0] == n and s[1] == quando for s in series):
                continue
            cor = CORES[n]
            if tracejado:
                for k in range(0, 50, 12):
                    cv2.line(img, (x1 + 20 + k, y), (x1 + 26 + k, y), cor, 2)
            else:
                cv2.line(img, (x1 + 20, y), (x1 + 70, y), cor, 3)
            texto = f"{n} folhas - {quando}"
            if quando == "antes" and any(s[0] == n and s[1] == "antes" and s[4] for s in series):
                texto += " (CAIU)"
            cv2.putText(img, texto, (x1 + 80, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (40, 40, 40), 1)
            y += 32
    cv2.putText(img, "Memoria do programa ao processar o Rhetorica (uma pagina por vez)",
                (x0, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (30, 30, 30), 2)
    destino = PASTA / "grafico.png"
    cv2.imwrite(str(destino), img)
    return destino


if __name__ == "__main__":
    print(desenhar())
