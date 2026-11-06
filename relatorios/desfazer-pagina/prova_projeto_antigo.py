"""D-623: prova de que um projeto de VERDADE gravado antes abre igual (05/11/2026).

D-623: "Muda o modelo de dados (página que não vem do PDF [...]): projeto antigo abre igual."

O projeto do Gradus Primus da pasta `dados-teste-rodada-de-consertos` (gravado antes da D-623, sem
o campo "inserida") é COPIADO para uma pasta de trabalho (a pasta de origem só é lida) e aberto
pelo código da vez. O script grava num .json o que o programa tira dele:

- o projeto gravado de novo (Projeto.para_dicionario), sem o campo novo "inserida" (que tem de vir
  0 em todas as páginas: isso é conferido e anotado à parte);
- as páginas que vão para o PDF, o "caminho rápido" dos cadernos e a lista do caderno da etapa 7
  (core/automatico.paginas_do_pdf_depois, com o Dividir marcado);
- o desenho final (core/pipeline.renderizar_pagina, 100 dpi) de todas as páginas do livro, como
  impressão digital (sha256 dos pontos).

Rodar o MESMO script no código de antes e no de depois e comparar os dois .json:
    python prova_projeto_antigo.py <saida.json> <pasta de trabalho>
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

GRADUS = Path(r"C:\Users\fotog\Desktop\Estudos\Latim\pdfcoffee.com_gradus-primus-pdf-pdf-free.pdf")
PROJ_ORIGEM = Path(r"D:\programas\EditorImpressao-arquivos\dados-teste-rodada-de-consertos\EditorImpressao"
                   r"\projetos\pdfcoffee-com_gradus-primus-pdf-pdf-free")
PAGINAS_DESENHADAS = None      # todas


def main(saida: Path, trabalho: Path) -> None:
    trabalho.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(trabalho / "dados")
    os.environ["TEMP"] = os.environ["TMP"] = str(trabalho)
    copia = trabalho / "projeto.json"
    shutil.copy2(PROJ_ORIGEM / "projeto.json", copia)          # a origem só é lida
    dados = json.loads(copia.read_text(encoding="utf-8"))
    assert all("inserida" not in p for p in dados["paginas"]), "o projeto não é de antes"
    dados["caminho_entrada"] = str(GRADUS)                      # o PDF só é lido

    import fitz

    from core.automatico import Pedido, paginas_do_pdf_depois
    from core.pipeline import renderizar_pagina
    from modelos import Projeto

    projeto = Projeto.de_dicionario(json.loads(json.dumps(dados)))
    regravado = projeto.para_dicionario()
    inseridas = [p.pop("inserida", "falta") for p in regravado["paginas"]]
    resultado = {
        "paginas": len(projeto.paginas),
        "inserida_de_cada_pagina": sorted(set(map(str, inseridas))),
        "projeto_regravado": regravado,
        "paginas_ativas": [p.indice for p in projeto.paginas_ativas],
        "so_cadernos": bool(projeto.so_cadernos),
        "caderno_etapa7": paginas_do_pdf_depois(projeto, Pedido(etapas=["dividir"])),
        "desenhos": {},
    }
    doc = fitz.open(str(GRADUS))
    try:
        for pagina in projeto.paginas_ativas[:PAGINAS_DESENHADAS]:
            img, mono = renderizar_pagina(doc, projeto, pagina, dpi=100)
            resultado["desenhos"][str(pagina.indice)] = [
                list(img.shape), bool(mono), hashlib.sha256(img.tobytes()).hexdigest()]
    finally:
        doc.close()
    saida.write_text(json.dumps(resultado, ensure_ascii=False, indent=1, default=str),
                     encoding="utf-8")
    print("ok", saida)


if __name__ == "__main__":
    sys.path.insert(0, os.getcwd())
    main(Path(sys.argv[1]), Path(sys.argv[2]))
