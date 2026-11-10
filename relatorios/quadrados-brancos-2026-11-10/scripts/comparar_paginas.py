"""Hoje x A x B x C em paginas soltas (gabarito, Horas 47, Boecio), pelo corpo do PDF
(core.pipeline._pagina_pronta, 300 DPI), livro novo, filtro escolhido a mao, "Respeitar" marcada.
Grava a pagina pronta em JPG (qualidade 92, tamanho cheio) e a medida de manchas brancas.
Uso: python comparar_paginas.py <saida> <lista.json: [[pdf, pagina, nome], ...]>"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reproduzir as R  # noqa: E402

import cv2  # noqa: E402

from core import etapas, pipeline  # noqa: E402
from core import filtros as F  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
import candidato  # noqa: E402
import varrer  # noqa: E402

limpar_real = F._limpar_o_papel_de_verdade
procura_real = etapas.respeitar_procura
R.instalar_b()
procura_b = etapas.respeitar_procura


def ligar(saida: str) -> None:
    F._limpar_o_papel_de_verdade = candidato.candidato if saida in ("A", "C") else limpar_real
    etapas.respeitar_procura = procura_b if saida in ("B", "C") else procura_real


saida = Path(sys.argv[1])
saida.mkdir(parents=True, exist_ok=True)
lista = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
res = {}
for pdf, numero, nome in lista:
    projeto = R.livro_novo(pdf)
    doc = abrir_pdf(pdf)
    try:
        orig = None
        for variante in ("melhorar_forte_respeitar", "magico_fraco_respeitar"):
            for s in ("hoje", "A", "B", "C"):
                ligar(s)
                p, pag = R.preparar(projeto, numero - 1, variante)
                img, _ = pipeline._pagina_pronta(p, doc, p.folhas[pag.folha], pag, pipeline._FolhaDaVez(), 0)
                if orig is None:
                    orig = pagina_para_array(doc, p.folhas[pag.folha].indice, dpi=p.qualidade_dpi)
                    if orig.shape[:2] != img.shape[:2]:
                        orig = cv2.resize(orig, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_AREA)
                    cv2.imwrite(str(saida / f"{nome}_original.jpg"), orig, [cv2.IMWRITE_JPEG_QUALITY, 92])
                cv2.imwrite(str(saida / f"{nome}_{variante}_{s}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 92])
                pct, blocos, _np = varrer.medir(orig, img)
                sel = pag.selecao or []
                g = sum(1 for r in sel if isinstance(r, dict) and r.get("tipo") == "gravura")
                res[f"{nome}|{variante}|{s}"] = {"branco_em_pintura_pct": pct, "blocos": blocos, "gravuras": g}
                print(nome, variante, s, res[f"{nome}|{variante}|{s}"], flush=True)
                (saida / "medidas.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    finally:
        doc.close()
