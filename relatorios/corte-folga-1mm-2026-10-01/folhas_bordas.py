r"""Folhas de "antes x depois" da folga do corte, ampliadas, para o Samuel ver (01/10/2026).

Para cada pagina e cada lado em que a folga mudou: a beirada da pagina pronta
(resultado\<id>.png da conferencia, filtro Original, PDF a 300 DPI) perto da
tinta mais proxima da borda, ANTES (esquerda) e DEPOIS (direita), ampliada 2x.
Nada e desenhado em cima da pagina: o texto fica numa faixa branca acima de
cada quadro, e a regua de 1 mm, numa faixa abaixo.

Uso: .venv\Scripts\python.exe folhas_bordas.py PASTA_ANTES PASTA_DEPOIS DESTINO
(PASTA_* = a pasta de uma conferencia: usa resultado\<id>.png)
"""
import sys
from pathlib import Path

import cv2
import numpy as np

MM = 300 / 25.4
FUNDO = 142             # quanto entra na pagina a partir da beirada (12 mm)
COMPRIDO = 300          # comprimento do trecho ao longo da beirada (pontos)
ZOOM = 2


def tinta_mais_perto(img, lado):
    """(distancia, centro ao longo da beirada) da peca de tinta mais perto do lado."""
    h, w = img.shape[:2]
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    papel = float(np.percentile(cinza[::4, ::4], 90))
    n, _, cx, _ = cv2.connectedComponentsWithStats((cinza < 0.6 * papel).astype(np.uint8), 8)
    melhor = None
    for i in range(1, n):
        a, b, cw, ch, ar = (int(v) for v in cx[i])
        if ar < 30 or a <= 0 or b <= 0 or a + cw >= w or b + ch >= h:
            continue
        d = {"esq": a, "dir": w - a - cw, "topo": b, "pe": h - b - ch}[lado]
        centro = b + ch // 2 if lado in ("esq", "dir") else a + cw // 2
        if melhor is None or d < melhor[0]:
            melhor = (d, centro)
    return melhor


def trecho(img, lado, centro):
    """O pedaco da beirada `lado` em volta de `centro`, ampliado ZOOM vezes."""
    h, w = img.shape[:2]
    if lado in ("esq", "dir"):
        c0 = int(np.clip(centro - COMPRIDO // 2, 0, max(0, h - COMPRIDO)))
        pedaco = img[c0:c0 + COMPRIDO, :FUNDO] if lado == "esq" else img[c0:c0 + COMPRIDO, w - FUNDO:]
    else:
        c0 = int(np.clip(centro - COMPRIDO // 2, 0, max(0, w - COMPRIDO)))
        pedaco = img[:FUNDO, c0:c0 + COMPRIDO] if lado == "topo" else img[h - FUNDO:, c0:c0 + COMPRIDO]
    return cv2.resize(pedaco, None, fx=ZOOM, fy=ZOOM, interpolation=cv2.INTER_NEAREST)


def com_legenda(quadro, texto, lado):
    """Faixa branca com o texto acima, a regua de 1 mm abaixo (fora da pagina)."""
    h, w = quadro.shape[:2]
    topo = np.full((34, w, 3), 255, np.uint8)
    cv2.putText(topo, texto, (6, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 1, cv2.LINE_AA)
    base = np.full((26, w, 3), 255, np.uint8)
    um = int(round(MM * ZOOM))
    if lado == "dir":
        x0 = w - um
    elif lado == "esq":
        x0 = 0
    else:
        x0 = 6
    if lado in ("esq", "dir"):
        cv2.rectangle(base, (x0, 6), (x0 + um - 1, 12), (0, 0, 200), -1)
        cv2.putText(base, "1 mm", (min(max(0, x0 - 50), w - 50) if lado == "dir" else um + 4, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1, cv2.LINE_AA)
    borda = np.full((h + 60, 8, 3), 255, np.uint8)
    return np.vstack([topo, cv2.copyMakeBorder(quadro, 0, 0, 0, 0, cv2.BORDER_CONSTANT), base]), borda


def main():
    antes, depois, destino = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    destino.mkdir(parents=True, exist_ok=True)
    for arq in sorted((depois / "resultado").glob("*.png")):
        pid = arq.stem
        a = cv2.imread(str(antes / "resultado" / arq.name))
        d = cv2.imread(str(arq))
        linhas = []
        for lado in ("esq", "dir", "topo", "pe"):
            ma, md = tinta_mais_perto(a, lado), tinta_mais_perto(d, lado)
            if ma is None or md is None:
                continue
            qa, qd = trecho(a, lado, ma[1]), trecho(d, lado, md[1])
            if abs(ma[0] - md[0]) <= 1:
                continue          # o lado nao mudou
            nomes = {"esq": "esquerda", "dir": "direita", "topo": "em cima", "pe": "embaixo"}
            la, sep = com_legenda(qa, f"{nomes[lado]} ANTES: {ma[0] / MM:.1f} mm", lado)
            ld, _ = com_legenda(qd, f"DEPOIS: {md[0] / MM:.1f} mm", lado)
            altura = max(la.shape[0], ld.shape[0])
            la = cv2.copyMakeBorder(la, 0, altura - la.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
            ld = cv2.copyMakeBorder(ld, 0, altura - ld.shape[0], 0, 0, cv2.BORDER_CONSTANT, value=(255, 255, 255))
            meio = np.full((altura, 24, 3), 255, np.uint8)
            linha = np.hstack([la, meio, ld])
            linhas.append(linha)
        if not linhas:
            print(pid, "- nenhum lado mudou")
            continue
        largura = max(l.shape[1] for l in linhas)
        titulo = np.full((40, largura, 3), 255, np.uint8)
        cv2.putText(titulo, f"{pid}: papel depois da ultima tinta, ANTES x DEPOIS (2x)", (6, 27),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2, cv2.LINE_AA)
        linhas.insert(0, titulo)
        linhas = [cv2.copyMakeBorder(l, 0, 16, 0, largura - l.shape[1], cv2.BORDER_CONSTANT,
                                     value=(255, 255, 255)) for l in linhas]
        cv2.imwrite(str(destino / f"bordas-{pid}.jpg"), np.vstack(linhas), [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(destino / f"bordas-{pid}.jpg")


if __name__ == "__main__":
    main()
