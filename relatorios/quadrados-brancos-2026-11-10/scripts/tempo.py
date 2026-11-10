"""Tempo por pagina a 300 DPI (o corpo do PDF, core.pipeline._pagina_pronta), hoje x A x B x C,
ALTERNADO: em cada rodada, cada pagina passa pelas quatro saidas, numa ordem que gira.
B e C procuram a gravura do zero em cada medida (projeto copiado de novo), que e o custo da
primeira vez numa pagina (depois a marcacao fica guardada no projeto).
Uso: python tempo.py <livro.pdf> <paginas> <variante_melhorar> <rodadas>"""
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import reproduzir as R  # noqa: E402

from core import etapas, pipeline  # noqa: E402
from core import filtros as F  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
import candidato  # noqa: E402

limpar_real = F._limpar_o_papel_de_verdade
procura_real = etapas.respeitar_procura
R.instalar_b()
procura_b = etapas.respeitar_procura


def ligar(saida: str) -> None:
    F._limpar_o_papel_de_verdade = candidato.candidato if saida in ("A", "C") else limpar_real
    etapas.respeitar_procura = procura_b if saida in ("B", "C") else procura_real


pdf, paginas, variante, rodadas = sys.argv[1], [int(v) for v in sys.argv[2].split(",")], sys.argv[3], int(sys.argv[4])
projeto = R.livro_novo(pdf)
doc = abrir_pdf(pdf)
tempos = {s: [] for s in ("hoje", "A", "B", "C")}
ordem = ["hoje", "A", "B", "C"]
try:
    # aquece (bibliotecas, rede neural carregada)
    for s in ordem:
        ligar(s)
        p, pag = R.preparar(projeto, paginas[0] - 1, variante)
        pipeline._pagina_pronta(p, doc, p.folhas[pag.folha], pag, pipeline._FolhaDaVez(), 0)
    for r in range(rodadas):
        for n in paginas:
            giro = ordem[r % 4:] + ordem[:r % 4]
            for s in giro:
                ligar(s)
                p, pag = R.preparar(projeto, n - 1, variante)
                t = time.perf_counter()
                pipeline._pagina_pronta(p, doc, p.folhas[pag.folha], pag, pipeline._FolhaDaVez(), 0)
                tempos[s].append(time.perf_counter() - t)
finally:
    doc.close()
res = {s: {"media_s": round(sum(v) / len(v), 2), "n": len(v)} for s, v in tempos.items()}
print(json.dumps(res))
(AQUI / f"tempo_{variante}.json").write_text(json.dumps({"paginas": paginas, "rodadas": rodadas, "res": res,
                                                         "cru": tempos}, indent=1), encoding="utf-8")
