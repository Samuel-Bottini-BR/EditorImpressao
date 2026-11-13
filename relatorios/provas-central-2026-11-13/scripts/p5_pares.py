"""Print 5 (v-capa; D-693): pares trocados no "Duas lado a lado".

La vida eterna (cópia), aberto do zero, Automático só com "Dividir folhas ao meio" (fábrica), no
livro todo. Área de trabalho em "Duas lado a lado", nos primeiros pares. Prints da janela (grab) e
as páginas como saem no PDF (para achar os números impressos).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

RAIZ = str(AQUI.parent)
CRU = AQUI / "cru" / "p5"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", json.dumps(valor, ensure_ascii=False, default=str), flush=True)
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


def main():
    import faulthandler
    faulthandler.dump_traceback_later(1800, exit=True)
    comum.preparar(RAIZ, "p5")
    from core import automatico as A
    from ui.widgets.paginas_rolando import DUAS

    j = comum.nova_janela()
    j.abrir_livro(str(AQUI / "livros" / "vida_eterna.pdf"))
    nota("abrir (s)", comum.esperar_tela(j))
    projeto, tela = j.projeto, j.tela_conferir
    nota("folhas", len(projeto.folhas))
    estado = j.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    nota("rodou o dividir", j.rodar_o_automatico(esperar=True, perguntar=False))
    comum.esperar(2.0)
    nota("paginas depois de dividir", len(projeto.paginas_ativas))
    nota("primeiras paginas (folha, metade)", [(p.folha, p.metade) for p in projeto.paginas_ativas[:12]])
    tela.definir_mostrar(DUAS)
    comum.esperar(1.0)
    for n, i in enumerate((0, 2, 4, 6)):
        tela.ir_para_pagina(i)
        comum.esperar(3.0)
        comum.ate(lambda: all(tela.previas.ja_pronta(k, tela._dpi_atual) is not None
                              for k in (i, i + 1) if k < len(projeto.paginas_ativas)), 240)
        comum.esperar(4.0)
        comum.foto(j, CRU / f"tela-duas-{n + 1:02d}-paginas-{i + 1}-{i + 2}.png")
    # as primeiras 12 páginas como saem no PDF (para ler os números impressos)
    # as primeiras 12 páginas como o PDF as desenha (core.pipeline.renderizar_pagina, a mesma conta)
    from core import pipeline
    from core.pdf_io import abrir_pdf
    import cv2

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for k, pagina in enumerate(projeto.paginas_ativas[:12]):
            img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=80)
            cv2.imwrite(str(CRU / f"pdf-p{k + 1:02d}.png"), img)
    finally:
        doc.close()
    comum.fechar(j)


if __name__ == "__main__":
    main()
