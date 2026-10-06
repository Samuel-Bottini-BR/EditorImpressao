r"""Pecas comuns dos scripts da conferencia 12 (05/10/2026, formulario conferir-aqui-12.html).

PROTOTIPO, NAO E O PROGRAMA: reaproveita os scripts da conferencia 11
(relatorios/conferencia-11-2026-10-05/scripts/comum11.py e simular.py), que importam o codigo do
programa (ramo fase2-misto) sem mudar nenhum arquivo dele, e grava as imagens AQUI
(relatorios/conferencia-12-2026-10-05/). Paginas do gabarito: somente leitura. Pasta de dados do
programa e cache: a de teste da conferencia 11 (%TEMP%\conf11_dados), nunca a do Samuel.
"""
from __future__ import annotations

import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
CONF11 = AQUI.parent / "conferencia-11-2026-10-05" / "scripts"
if str(CONF11) not in sys.path:
    sys.path.insert(0, str(CONF11))

import comum11  # noqa: E402

comum11.AQUI = AQUI          # simular.gravar escreve em comum11.AQUI
import simular as S  # noqa: E402,F401
