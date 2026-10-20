"""Verificador, 20/10/2026: mede de novo, por conta propria, as 89 paginas do LIVRO NOVO (endireitar
antes + conta do ScanTailor, 300 DPI, sem filtro) com o codigo de uma pasta dada (--raiz), e guarda o
md5 e o tamanho de cada pagina pronta. Serve para dizer quais paginas mudam entre o d97b937 e o
5a84f7c sem depender da conta do implementador (a lista das 89 vem do dados-pesel21.json dele; o
jeito de montar o projeto e o mesmo do medir.py dele, escrito aqui de novo).

USO  python medir89.py --raiz <pasta do programa> --nome <rotulo>
So le o acervo e o gabarito; pasta de dados do programa isolada em trabalho/; nada do programa muda."""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
args = sys.argv[1:]
RAIZ = Path(args[args.index("--raiz") + 1]).resolve()
NOME = args[args.index("--nome") + 1]
TRAB = PASTA / "trabalho"
os.environ["LOCALAPPDATA"] = str(TRAB / "dados" / "local")
os.environ["USERPROFILE"] = str(TRAB / "dados" / "home")
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402

from core import pipeline as P  # noqa: E402
from core.dividir import detectar_lombada  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from modelos import ENDIREITAR_DO_LIVRO_NOVO, ORDEM_DO_LIVRO_NOVO, ConfigPagina, Projeto  # noqa: E402

assert Path(P.__file__).resolve().is_relative_to(RAIZ), P.__file__
DPI = 300
ESTUDO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
GABARITO = Path(r"D:\programas\EditorImpressao\gabarito\paginas")
LISTA = json.loads((PASTA.parents[1] / "conserto-corte-g6" / "dados-pesel21.json").read_text(encoding="utf-8"))
PIDS = sorted({v["pid"] for v in LISTA.values()})
SAIDA = TRAB / f"finais-{NOME}"
SAIDA.mkdir(parents=True, exist_ok=True)


def pdf(pid):
    p = ESTUDO / f"{pid}.pdf"
    return p if p.exists() else GABARITO / f"{pid}.pdf"


resultado = {}
t0 = time.time()
for pid in PIDS:
    projeto = Projeto(caminho_entrada=str(pdf(pid)), nome=pid)
    projeto.filtro_padrao = ORIGINAL
    projeto.limpar = False
    projeto.qualidade_dpi = DPI
    projeto.ordem_do_preparo = ORDEM_DO_LIVRO_NOVO
    projeto.endireitar_como = ENDIREITAR_DO_LIVRO_NOVO
    projeto = P.analisar_projeto(projeto)
    if pid.startswith("siebmacher") and not projeto.folhas[0].dividir:
        doc = abrir_pdf(projeto.caminho_entrada)
        lombada = detectar_lombada(pagina_para_array(doc, 0, dpi=P.DPI_ANALISE))
        doc.close()
        f = projeto.folhas[0]
        f.dividir, f.posicao_corte, f.confianca_corte = True, lombada.posicao, lombada.confianca
        projeto.paginas = [ConfigPagina(indice=i, folha=0, metade=m, filtro=ORIGINAL)
                           for i, m in enumerate(("esquerda", "direita"))]
    doc = abrir_pdf(projeto.caminho_entrada)
    for pagina in projeto.paginas:
        final, _ = P.renderizar_pagina(doc, projeto, pagina, dpi=DPI)
        base = f"{pid}__{pagina.metade}"
        resultado[base] = {"md5": hashlib.md5(final.tobytes()).hexdigest(),
                           "mm": [round(final.shape[1] * 25.4 / DPI, 1), round(final.shape[0] * 25.4 / DPI, 1)],
                           "ordem": projeto.ordem_do_preparo}
        cv2.imwrite(str(SAIDA / f"{base}.jpg"), final, [cv2.IMWRITE_JPEG_QUALITY, 85])
    doc.close()
    print(pid, len(resultado), round(time.time() - t0), "s", flush=True)
(TRAB / f"medida-{NOME}.json").write_text(json.dumps(resultado, indent=1), encoding="utf-8")
print("paginas:", len(resultado), "em", round(time.time() - t0), "s")
