"""Verificador, 21/10 (item 2.15): conta, com a analise do programa de verdade (analisar_projeto, livro novo, de
fabrica), as paginas que ganham o aviso de inclinacao diferente, e confere a conta com a formula do ScanTailor
(DeviationProvider) refeita aqui a parte, sobre os mesmos angulos. So le o PDF. Uso: contar_215.py <pdf> <saida.json>"""
import json
import math
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "verif215_dados")
sys.path.insert(0, str(RAIZ))
from core import analise  # noqa: E402
from core import pipeline as P  # noqa: E402
from modelos import Projeto  # noqa: E402

codigo = analise.ANGULO_DIFERENTE_DAS_OUTRAS
pdf = Path(sys.argv[1])
_visto = {}
_orig = P.marcar_paginas_diferentes


def _espia(paginas, angulos):          # so guarda os angulos que o programa usou; nao muda nada
    _visto["angulos"] = list(angulos)
    return _orig(paginas, angulos)


P.marcar_paginas_diferentes = _espia
pr = P.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=pdf.stem))
pags = pr.paginas
marcadas = [p.indice + 1 for p in pags if codigo in p.alertas]
# a conta do ScanTailor, refeita por mim, sobre o angulo que a analise guardou
ang = {i + 1: v for i, v in enumerate(_visto["angulos"])}
nums = [v for v in ang.values() if v is not None and not math.isnan(v)]
media = sum(nums) / len(nums)
desvio = math.sqrt(sum((v - media) ** 2 for v in nums) / (len(nums) - 1))
st = [k for k, v in ang.items() if v is not None and abs(v - media) > max(1.5 * desvio, 0.01 * media)]
longe = [k for k in st if abs(ang[k] - media) >= 1.0]
res = {"livro": pdf.name, "paginas": len(pags), "codigo": codigo, "marcadas_pelo_programa": marcadas,
       "scantailor_puro_minha_conta": st, "com_1_grau_minha_conta": longe, "media": media, "desvio": desvio,
       "angulos": {k: ang[k] for k in marcadas}}
Path(sys.argv[2]).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(res["paginas"], "programa:", marcadas, "| minha conta (ST puro):", st, "| com 1 grau:", longe)
