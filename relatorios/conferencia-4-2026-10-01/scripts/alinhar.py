"""Poe a pagina ORIGINAL no mesmo enquadramento do RESULTADO (quarta conferencia, 01/10/2026).

Nao faz parte do programa e nao processa pagina nenhuma: so le imagens prontas
(gabarito/paginas/*.png e os resultados da rodada
relatorios/conferir/pb-mp-decoracao-2026-10-01/) e calcula a semelhanca
(escala, giro, deslocamento) entre elas.

Por que: o programa corta e endireita a pagina, entao o resultado tem outro
tamanho e outra posicao que o original. Para mostrar ORIGINAL, ANTES e AGORA
lado a lado com o MESMO recorte, o original e desenhado por cima da moldura do
resultado. ANTES e AGORA saem do mesmo programa com o mesmo corte (conferido:
mesmo tamanho nas quatro pastas), entao nao precisam de alinhamento.

Como: pontos em comum (ORB + RANSAC) entre o original e o resultado do Magico
pro (que ainda tem as cores, e por isso casa melhor que o Preto e branco), e
refino com ECC em miniatura (o ORB sozinho deixa ~1% de erro). Mesma conta de
relatorios/conferencia-2-2026-09-30/scripts/montar_imagens.py
(resultado_alinhado), so que no sentido contrario.

Seguro mudar: tamanhos das miniaturas, numero de pontos.
Arriscado: nada (so leitura e desenho).
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def ler_rgb(caminho: Path) -> np.ndarray:
    bgr = cv2.imread(str(caminho), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(caminho)
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def matriz_resultado_para_original(orig: np.ndarray, res: np.ndarray, nome: str = "") -> np.ndarray:
    """M (2x3) que leva um ponto do RESULTADO ao ponto do ORIGINAL."""
    h, w = orig.shape[:2]
    esc_o, esc_r = 1200 / w, 1200 / res.shape[1]
    go = cv2.cvtColor(cv2.resize(orig, None, fx=esc_o, fy=esc_o, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    gr = cv2.cvtColor(cv2.resize(res, None, fx=esc_r, fy=esc_r, interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    orb = cv2.ORB_create(8000)
    ko, do = orb.detectAndCompute(go, None)
    kr, dr = orb.detectAndCompute(gr, None)
    pares = sorted(cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(dr, do), key=lambda m: m.distance)[:1500]
    src = np.float32([kr[m.queryIdx].pt for m in pares]) / esc_r
    dst = np.float32([ko[m.trainIdx].pt for m in pares]) / esc_o
    M, dentro = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4.0, maxIters=5000)
    n_bons = int(dentro.sum()) if dentro is not None else 0
    if M is None or n_bons < 25:
        raise RuntimeError(f"{nome}: nao alinhou ({n_bons} pontos)")
    try:
        e = 800 / w
        er = e / float(np.hypot(M[0, 0], M[0, 1]))
        go2 = cv2.cvtColor(cv2.resize(orig, None, fx=e, fy=e, interpolation=cv2.INTER_AREA),
                           cv2.COLOR_RGB2GRAY).astype(np.float32)
        gr2 = cv2.cvtColor(cv2.resize(res, None, fx=er, fy=er, interpolation=cv2.INTER_AREA),
                           cv2.COLOR_RGB2GRAY).astype(np.float32)
        Se, Sr = np.diag([e, e, 1.0]), np.diag([er, er, 1.0])
        A = np.vstack([M, [0, 0, 1]])
        W0 = (Sr @ np.linalg.inv(A) @ np.linalg.inv(Se))[:2].astype(np.float32)
        _, W = cv2.findTransformECC(go2, gr2, W0, cv2.MOTION_AFFINE,
                                    (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        W3 = np.vstack([W.astype(np.float64), [0, 0, 1]])
        M = (np.linalg.inv(Se) @ np.linalg.inv(W3) @ Sr)[:2]
    except cv2.error as erro:
        print(f"  {nome}: ECC nao convergiu ({str(erro)[:60]}); fica o ORB")
    print(f"  {nome}: alinhado com {n_bons} pontos, escala {np.hypot(M[0, 0], M[0, 1]):.3f}")
    return M


def original_no_quadro_do_resultado(orig: np.ndarray, res: np.ndarray, nome: str = "") -> np.ndarray:
    """O original redesenhado no tamanho e posicao do resultado (fora da pagina: cinza claro)."""
    M = matriz_resultado_para_original(orig, res, nome)
    inv = cv2.invertAffineTransform(M)
    return cv2.warpAffine(orig, inv, (res.shape[1], res.shape[0]), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_CONSTANT, borderValue=(215, 215, 215))
