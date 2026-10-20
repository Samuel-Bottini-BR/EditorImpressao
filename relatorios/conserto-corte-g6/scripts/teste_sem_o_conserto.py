"""Prova de que o teste novo pega o defeito: roda os testes da borda preta
(tests/test_ordem_do_preparo.py) com o conserto DESLIGADO por fora - a
pipeline chama o detectar_bordas sem dizer o giro, como antes de 13/10/2026.
Nada do programa muda. Tem de FALHAR nos seis casos; com o conserto, passam.

USO  python teste_sem_o_conserto.py <pasta temporaria>
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

import pytest  # noqa: E402

from core import pipeline, recortar  # noqa: E402

_de_verdade = recortar.detectar_bordas
pipeline.detectar_bordas = lambda img, dpi=None, girada=None: _de_verdade(img, dpi=dpi)

if __name__ == "__main__":
    raise SystemExit(pytest.main([str(RAIZ / "tests" / "test_ordem_do_preparo.py"), "-q",
                                  "-k", "nao_deixa_a_borda_preta", "--tb=line", "-p", "no:cacheprovider",
                                  f"--basetemp={sys.argv[1]}"]))
