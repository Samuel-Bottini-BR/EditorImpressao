"""Tempo de abrir o livro e de processar, antes e depois do item 2.1.

Uso:
    python tempo.py <raiz do codigo> <livro.pdf> <jeito> <saida.json> [folhas]

<raiz do codigo>: a pasta do programa a medir (a copia "antes", tirada com
git archive do commit de antes, ou a de agora). <jeito>: "antigo" (o projeto
como o programa de antes fazia: dividir marcado, sem os campos novos),
"nao", "programa", "scantailor" ou "scantailor_sobra". Mede pelas MESMAS
funcoes que a janela usa: core.pipeline.analisar_projeto (abrir o livro,
150 DPI) e core.pipeline.processar (10 paginas, Original, 300 DPI, sem
cadernos). Grava os segundos em <saida.json>. Rodar com LOCALAPPDATA
apontando para uma pasta de rascunho (nunca a do Samuel).
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path


def main() -> int:
    raiz, livro, jeito, saida = sys.argv[1:5]
    folhas = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    sys.path.insert(0, raiz)
    from core import pipeline
    from modelos import Projeto

    campos = dict(caminho_entrada=livro, nome="tempo", detectar_regioes=False)
    if jeito == "antigo":
        campos["dividir_folhas"] = True
    elif jeito == "nao":
        campos["dividir_folhas"] = False
    else:
        campos["dividir_folhas"] = True
        campos["dividir_como"] = "scantailor" if jeito.startswith("scantailor") else "programa"
        campos["cortar_sobra"] = jeito.endswith("_sobra")
    projeto = Projeto(**campos)

    if folhas:
        # um pedaco do livro: as primeiras `folhas` folhas, copiadas como estao
        import fitz
        origem = fitz.open(livro)
        pedaco = fitz.open()
        pedaco.insert_pdf(origem, from_page=0, to_page=min(folhas, origem.page_count) - 1)
        caminho = Path(tempfile.gettempdir()) / f"tempo_{os.getpid()}.pdf"
        pedaco.save(str(caminho))
        pedaco.close()
        origem.close()
        projeto.caminho_entrada = str(caminho)

    inicio = time.perf_counter()
    pipeline.analisar_projeto(projeto)
    abrir = time.perf_counter() - inicio

    projeto.paginas = projeto.paginas[:10]
    projeto.caminho_saida = str(Path(tempfile.gettempdir()) / f"tempo_saida_{os.getpid()}.pdf")
    inicio = time.perf_counter()
    pipeline.processar(projeto)
    processar = time.perf_counter() - inicio
    Path(projeto.caminho_saida).unlink(missing_ok=True)
    if folhas:
        Path(projeto.caminho_entrada).unlink(missing_ok=True)

    resultado = {"jeito": jeito, "folhas": len(projeto.folhas), "abrir_s": round(abrir, 2),
                 "processar_10_s": round(processar, 2),
                 "divididas": sum(1 for f in projeto.folhas if f.dividir)}
    Path(saida).write_text(json.dumps(resultado), encoding="utf-8")
    print(json.dumps(resultado))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
