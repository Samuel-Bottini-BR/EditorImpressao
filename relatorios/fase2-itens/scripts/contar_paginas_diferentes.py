"""Item 2.15: quantas páginas de cada livro ganham "Inclinação diferente das outras".

Analisa o livro como o programa faz ao abrir (core.pipeline.analisar_projeto,
livro novo: endireitar pela conta do ScanTailor) e grava, em JSON, o ângulo de
cada página e quais foram marcadas. O acervo é só lido.

Uso: python contar_paginas_diferentes.py <livro.pdf> <saida.json>
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))


def main() -> None:
    from core import analise, pipeline
    from modelos import Projeto

    livro, saida = Path(sys.argv[1]), Path(sys.argv[2])
    angulos: list = []
    original = pipeline.marcar_paginas_diferentes

    def guardar(paginas, lista):
        angulos.extend(lista)
        original(paginas, lista)

    pipeline.marcar_paginas_diferentes = guardar
    inicio = time.perf_counter()
    projeto = Projeto(caminho_entrada=str(livro))
    pipeline.analisar_projeto(projeto)
    marcadas = [p.indice + 1 for p in projeto.paginas
                if analise.ANGULO_DIFERENTE_DAS_OUTRAS in p.alertas]
    dados = {
        "livro": livro.name, "paginas": len(projeto.paginas), "marcadas": marcadas,
        "fracao": round(len(marcadas) / max(1, len(projeto.paginas)), 4),
        "angulos": [None if a is None else round(a, 3) for a in angulos],
        "segundos": round(time.perf_counter() - inicio, 1),
    }
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{livro.name}: {len(marcadas)} de {len(projeto.paginas)} ({dados['fracao']:.1%})")


if __name__ == "__main__":
    main()
