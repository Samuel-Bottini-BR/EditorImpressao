r"""Tempo do corte de bordas nas 32 paginas do gabarito (regra 6 do plano), 01/10/2026.

Desenha cada pagina a 300 DPI uma vez e mede pipeline._geometria (detectar_bordas
+ angulo + folga do giro, o que _guardar_geometria faz para a previa e o PDF)
REPETICOES vezes; guarda o MENOR tempo de cada pagina (o menos afetado pelo resto
da maquina) e soma. Rodar com o codigo de antes e com o de depois.

Uso: .venv\Scripts\python.exe tempo_corte.py RAIZ_DO_CODIGO [REPETICOES]
"""
import inspect
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(sys.argv[1]).resolve()
REP = int(sys.argv[2]) if len(sys.argv) > 2 else 5
sys.path.insert(0, str(RAIZ))
import fitz  # noqa: E402

from core import pipeline  # noqa: E402
from core.pdf_io import pagina_para_array  # noqa: E402
from modelos import Projeto  # noqa: E402

projeto = Projeto(caminho_entrada="")
projeto.dividir_folhas = False
PAG = SimpleNamespace(recorte=None, angulo_manual=None)
com_dpi = "dpi" in inspect.signature(pipeline._geometria).parameters
lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
total = 0.0
for nome, info in lista["paginas"].items():
    doc = fitz.open(RAIZ / "gabarito" / info["pdf"])
    img = pagina_para_array(doc, 0, dpi=300)
    doc.close()
    melhor = 1e9
    for _ in range(REP):
        t = time.perf_counter()
        pipeline._geometria(img, PAG, projeto, dpi=300) if com_dpi else pipeline._geometria(img, PAG, projeto)
        melhor = min(melhor, time.perf_counter() - t)
    total += melhor
print(f"{RAIZ.name}: _geometria nas 32 paginas, menor de {REP}: {total:.3f} s")
