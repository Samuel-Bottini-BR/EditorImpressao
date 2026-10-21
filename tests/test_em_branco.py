"""O aviso "Parece em branco" (core/analise.analisar_pagina).

Bug da Lista de bugs (08/10/2026): "O aviso 'Parece em branco. Quer apagar?'
erra: aparece na Gladstone 18, que tem título, e não aparece no Egenloff 12
nem na Rariora 8." Consertado em 21/10/2026 (ver EM_BRANCO_TINTA_FORTE em
core/analise.py): a página está em branco quando quase não há tinta FORTE
(bem mais escura que o papel) no miolo; antes era a fração de pontos escuros
pelo limiar de Otsu, que numa página branca com um título pequeno fica abaixo
do limite.

Testes de máquina com páginas de mentira (rodam em qualquer lugar) e, se as
páginas do estudo estiverem no PC, com as de verdade.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from core import analise
from core.filtros import ORIGINAL

PAGINAS = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")


def _folha(papel=255):
    return np.full((1754, 1240, 3), papel, np.uint8)       # A4 a 150 DPI


def test_regressao_pagina_branca_com_titulo_nao_e_em_branco():
    """Gladstone 18: página branca só com o título "DA ORAÇÃO" no meio. Antes
    do conserto saía "Parece em branco" (fração de Otsu 0,1% < 0,2%)."""
    img = _folha()
    cv2.putText(img, "DA ORACAO", (470, 870), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 0, 0), 2, cv2.LINE_AA)
    assert analise.EM_BRANCO not in analise.analisar_pagina(img, ORIGINAL)[0]


def test_pagina_so_com_carimbo_claro_e_em_branco():
    """Egenloff 12: verso só com o carimbo violeta da biblioteca (claro) num
    papel creme: é "em branco" (antes não era: o Otsu contava o papel)."""
    img = _folha(papel=216)
    cv2.ellipse(img, (620, 870), (150, 90), 0, 0, 360, (190, 150, 185), 3)
    cv2.putText(img, "Schneeberg", (520, 880), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (190, 150, 185), 2)
    assert analise.EM_BRANCO in analise.analisar_pagina(img, ORIGINAL)[0]


def test_pagina_de_texto_nao_e_em_branco():
    img = _folha()
    for y in range(200, 1500, 40):
        cv2.putText(img, "texto de uma pagina comum", (150, y), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 30, 30), 2)
    assert analise.EM_BRANCO not in analise.analisar_pagina(img, ORIGINAL)[0]


def test_pagina_toda_branca_e_em_branco():
    assert analise.EM_BRANCO in analise.analisar_pagina(_folha(), ORIGINAL)[0]


@pytest.mark.skipif(not PAGINAS.is_dir(), reason="sem as páginas do estudo (fora do git)")
@pytest.mark.parametrize("pid,em_branco", [("gladstone_p018", False), ("egenloff_p012", True)])
def test_paginas_de_verdade(pid, em_branco):
    fitz = pytest.importorskip("fitz")
    with fitz.open(PAGINAS / f"{pid}.pdf") as doc:
        p = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72), alpha=False)
    img = cv2.cvtColor(np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width, 3), cv2.COLOR_RGB2BGR)
    assert (analise.EM_BRANCO in analise.analisar_pagina(img, ORIGINAL)[0]) is em_branco
