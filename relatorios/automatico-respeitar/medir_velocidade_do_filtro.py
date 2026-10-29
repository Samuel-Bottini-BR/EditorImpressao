"""D-586, velocidade da única conta nova do core (core.pipeline.marcacao_que_o_filtro_usa).

Desenha a capa e a página 9 do "Na escola de Jesus" (cópia em <worktree>/_tmp/dados, depois do
Automático) em Preto e branco e Mágico pro, 110 DPI, N vezes, com o código da pasta argv[1], e
imprime a mediana em segundos. Rodar alternado: antigo, novo, antigo, novo...
Uso: python medir_velocidade_do_filtro.py <pasta do código> [vezes]
"""
import copy
import json
import os
import statistics
import sys
import time
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"
CODIGO = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(CODIGO))
VEZES = int(sys.argv[2]) if len(sys.argv) > 2 else 5
PROJETO = (Path(__file__).resolve().parents[2] / "_tmp" / "dados" / "EditorImpressao" / "projetos"
           / "Na escola de Jesus - Catecismo explicado com imagens" / "projeto.json")


def main() -> int:
    from core.pdf_io import abrir_pdf
    from core.pipeline import renderizar_pagina
    from modelos import Projeto

    projeto = Projeto.de_dicionario(json.loads(PROJETO.read_text(encoding="utf-8")))
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for indice in (0, 8):
            for filtro in ("preto_e_branco", "magico_pro"):
                pagina = copy.deepcopy(projeto.paginas[indice])
                pagina.filtro = filtro
                renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=110)
                tempos = []
                for _ in range(VEZES):
                    inicio = time.perf_counter()
                    renderizar_pagina(doc, copy.deepcopy(projeto), copy.deepcopy(pagina), dpi=110)
                    tempos.append(time.perf_counter() - inicio)
                print(f"{CODIGO.name:15s} pagina {indice + 1:2d} {filtro:15s} "
                      f"mediana {statistics.median(tempos):.3f} s")
    finally:
        doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
