"""Fotos para refazer a pergunta 8 (2.18, "Tinta com a cor original, papel branco"), 22/10/2026.

Cada página passa pelo caminho inteiro do programa (dividir → endireitar → cortar
→ filtro, de fábrica) com core.pipeline.processar; a área marcada à mão vai POR
CIMA da marcação que o programa acha sozinho (como na tela).

Painéis: Original · Preto e branco (hoje) · Preto e branco + "Tinta com a cor"
(A, o que o programa faz) · Preto e branco + "tinta com a cor, escurecida" (B,
SIMULADO só nesta foto: a mesma tinta, com o brilho reduzido à metade e a cor
mantida - não existe no programa).
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve()
sys.path.insert(0, str(AQUI.parent))
import antes_depois as ad  # noqa: E402
import rodada_processar as rp  # noqa: E402

SAIDA = AQUI.parents[3] / "relatorios" / "conferir" / "fase2-novas" / "pergunta-8"

CASOS = [
    ("horas_p013", "título vermelho e azul (Livro de Horas 13)", (0.10, 0.11, 0.80, 0.27)),
    ("escola_p007", "título (Na Escola de Jesus 7)", (0.0, 0.0, 1.0, 0.065)),
]


def _escurecida(original, pb, area_px):
    """A opção B, simulada: dentro da área, a tinta (o preto do Preto e branco)
    com a cor do original e o brilho reduzido à metade; o resto branco."""
    from core.editar_zonas import _tinta_na_area

    saida = pb if pb.ndim == 3 else cv2.cvtColor(pb, cv2.COLOR_GRAY2BGR)
    saida = saida.copy()
    x0, y0, x1, y1 = area_px
    mascara = np.zeros(original.shape[:2], bool)
    mascara[y0:y1, x0:x1] = True
    tinta = _tinta_na_area(original, mascara, 50, "auto")
    lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[..., 0] *= 0.5
    lab[..., 1:] = (lab[..., 1:] - 128) * 1.25 + 128
    escura = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    saida[mascara & tinta] = escura[mascara & tinta]
    saida[mascara & ~tinta] = 255
    return saida


def main() -> int:
    raiz = Path(sys.argv[1]) if len(sys.argv) > 1 else rp.RAIZ_PADRAO
    rp._preparar(raiz.resolve())
    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.selecao import MAO, TINTA_COR, Regiao, Selecao

    SAIDA.mkdir(parents=True, exist_ok=True)
    tmp = SAIDA / "_pdfs"
    tmp.mkdir(exist_ok=True)
    for pid, nome, area in CASOS:
        regiao = Regiao(tipo=TINTA_COR, pontos=[area[:2], area[2:]], origem=MAO)
        orig, f_o, _ = ad._processar_pagina(raiz, pid, tmp, "original", {"filtro_padrao": ORIGINAL},
                                            {"filtro": ORIGINAL}, selecao=Selecao())
        pb, f_p, _ = ad._processar_pagina(raiz, pid, tmp, "pb", {"filtro_padrao": PRETO_E_BRANCO},
                                          {"filtro": PRETO_E_BRANCO}, selecao=Selecao())
        cor, f_c, _ = ad._processar_pagina(raiz, pid, tmp, "cor", {"filtro_padrao": PRETO_E_BRANCO},
                                           {"filtro": PRETO_E_BRANCO}, selecao=Selecao([regiao]))
        h, w = orig.shape[:2]
        px = (int(area[0] * w), int(area[1] * h), int(area[2] * w), int(area[3] * h))
        b = _escurecida(orig, pb, px)
        marcado = f" → área marcada à mão no título: {area}"
        paineis = [
            ("Original", orig, f_o),
            ("Preto e branco (hoje): a cor vira preto", pb, f_p),
            ("A: + \"Tinta com a cor\" (o programa)", cor, f_c + marcado),
            ("B: + tinta com a cor, escurecida (SIMULADO)", b, f_p + marcado + " → simulação, não existe no programa"),
        ]
        cv2.imwrite(str(SAIDA / f"{pid}-pagina.jpg"), ad._lado_a_lado(paineis, altura=1000),
                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        x0, y0, x1, y1 = px
        recortes = [(t, im[y0:y1, x0:x1], "") for t, im, _f in paineis]
        altura = max(160, min(320, (y1 - y0)))
        cv2.imwrite(str(SAIDA / f"{pid}-titulo-ampliado.jpg"),
                    np.vstack([ad._faixa(cv2.resize(im, (min(1400, im.shape[1]),
                                                         int(im.shape[0] * min(1400, im.shape[1]) / im.shape[1]))),
                                         [t]) for t, im, _ in recortes]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(pid, "ok", altura)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
