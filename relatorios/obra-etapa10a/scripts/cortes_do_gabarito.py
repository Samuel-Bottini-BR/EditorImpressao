"""O corte (recorte, ângulo) de fábrica de cada página do gabarito, livro novo.

Para comparar dois códigos (antes/depois) sem gerar o PDF: só a geometria
(core.pipeline._geometria), na resolução do PDF (300 DPI), como o processar.
USO: python cortes_do_gabarito.py <raiz do código> <saida.json> [pid ...]
"""
import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RAIZ))
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "etapa10a_localappdata")
GAB = Path(r"D:\programas\EditorImpressao\gabarito")


def main():
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import Projeto

    pids = sys.argv[3:] or sorted(json.loads((GAB / "lista.json").read_text(encoding="utf-8"))["paginas"])
    saida = {}
    for pid in pids:
        pdf = GAB / "paginas" / f"{pid}.pdf"
        projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=pid))
        doc = abrir_pdf(str(pdf))
        for pagina in projeto.paginas_ativas:
            folha = projeto.folhas[pagina.folha]
            img = pagina_para_array(doc, folha.indice, dpi=projeto.qualidade_dpi)
            base = pipeline.preparar_para_recorte(img, folha, pagina, projeto)
            rec, ang = pipeline._geometria(base, pagina, projeto, dpi=projeto.qualidade_dpi)
            chave = f"{pid}|{pagina.metade}"
            saida[chave] = [None if rec is None else [round(float(v), 5) for v in rec], round(float(ang), 4)]
            print(chave, saida[chave], flush=True)
        doc.close()
    Path(sys.argv[2]).write_text(json.dumps(saida, indent=1), encoding="utf-8")


main()
