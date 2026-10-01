"""Prova de onde sumiu o "A" de "CRISTA" no cartao B6 (conferencia 2, 30/09).

Refaz o painel "AGORA: o que a TELA mostra" do cartao exatamente como
relatorios/conferencia-2-2026-09-30/scripts/montar_imagens.py o montou (mesma
fatia da imagem v2 da rodada fase1-2026-09-28-2058-3 e o mesmo retangulo
magenta de U.marcar) e grava, lado a lado e ampliados 4x, o canto de cima a
direita SEM e COM o retangulo. So le imagens; nao mexe no programa.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "relatorios" / "conferencia-2-2026-09-30" / "scripts"))
import util_imagens as U  # noqa: E402

v2 = U.ler_rgb(RAIZ / "relatorios" / "conferir" / "fase1-2026-09-28-2058-3" / "ampliacoes"
               / "v2-escola7-previas-e-pdf.jpg") if hasattr(U, "ler_rgb") else \
    cv2.cvtColor(cv2.imread(str(RAIZ / "relatorios" / "conferir" / "fase1-2026-09-28-2058-3"
                                / "ampliacoes" / "v2-escola7-previas-e-pdf.jpg")), cv2.COLOR_BGR2RGB)
painel = np.ascontiguousarray(v2[30:, 612:1171])
marcado = U.marcar(painel, (4, 4, 555, 120), texto="margem de cima", texto_embaixo=True)
canto = lambda m: cv2.resize(m[40:110, 430:], None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
sep = np.full((70 * 4, 12, 3), 255, np.uint8)
lado = np.hstack([canto(painel), sep, canto(marcado)])
destino = Path(__file__).with_name("prova-cartao-b6.jpg")
cv2.imwrite(str(destino), cv2.cvtColor(lado, cv2.COLOR_RGB2BGR))
print("gravado", destino)
