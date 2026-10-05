r"""As 32 paginas do gabarito num filtro, pelo MESMO caminho do botao
"Confirmar e processar" (conferencia.processar_pelo_programa: TarefaAnalise.run
e TarefaProcessar.run, PDF gravado e lido de volta), a partir de uma copia do
codigo. Copia do rodar_verificador.py do verificador (consertos da janela,
05/10), com uma diferenca: a copia ANTES (git archive 044a7c1, sem a pasta
modelos\, que fica fora do git) usa os modelos da pasta original, so lidos.

Uso:
    .venv\Scripts\python.exe rodar_32.py RAIZ_DO_CODIGO FILTRO PASTA_SAIDA [ids]

Nenhuma janela (offscreen); LOCALAPPDATA e TEMP descartaveis, dentro da
PASTA_SAIDA (apagados no fim), nunca os do Samuel. Os PDFs do gabarito sao so
lidos. Grava <pid>.png (a pagina do PDF gerado) e tempos.json.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

raiz, filtro, saida = Path(sys.argv[1]).resolve(), sys.argv[2], Path(sys.argv[3]).resolve()
saida.mkdir(parents=True, exist_ok=True)
dados = saida / "_localappdata"
tmp = saida / "_tmp"
dados.mkdir(exist_ok=True)
tmp.mkdir(exist_ok=True)
os.environ["LOCALAPPDATA"] = str(dados)
os.environ["TEMP"] = os.environ["TMP"] = str(tmp)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(raiz)
sys.path.insert(0, str(raiz))

import tempfile  # noqa: E402
tempfile.tempdir = str(tmp)
import cv2  # noqa: E402

MODELOS = Path(r"D:\programas\EditorImpressao\modelos")     # somente leitura
if not (raiz / "modelos").exists():
    import core.detectar_regioes as _dr
    import core.ocr_doctr as _doctr
    import core.ocr_tesseract as _tess
    import core.rede_selecao as _rede

    _dr.CAMINHO_MODELO = MODELOS / "doclayout.onnx"
    _dr._detector.caminho = _dr.CAMINHO_MODELO          # criado na importacao
    _doctr.CAMINHO_MODELO = MODELOS / "doctr" / _doctr.CAMINHO_MODELO.name
    _tess.PASTA_DOS_MODELOS = MODELOS / "tessdata"
    _rede.PASTA = MODELOS / "mobile_sam"
    _rede.CODIFICADOR = _rede.PASTA / _rede.CODIFICADOR.name
    _rede.DECODIFICADOR = _rede.PASTA / _rede.DECODIFICADOR.name
    print("modelos da pasta original:", MODELOS, flush=True)

import conferencia  # noqa: E402  (o da copia)

GABARITO = Path(r"D:\programas\EditorImpressao\gabarito")
lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
ids = list(lista["paginas"])
if len(sys.argv) > 4:
    ids = sys.argv[4].split(",")

print("codigo:", raiz, "filtro:", filtro, flush=True)
fonte = conferencia.FonteDoPrograma(filtro)
fonte.preparar(lambda t: print(t, flush=True))
tempos = {}
try:
    for pid in ids:
        pdf = GABARITO / lista["paginas"][pid]["pdf"]
        t0 = time.perf_counter()
        depois = fonte.obter(pid, pdf, None)
        total = time.perf_counter() - t0
        if depois.imagem is None:
            print(pid, "FALHOU:", depois.aviso, flush=True)
            tempos[pid] = {"erro": depois.aviso}
            continue
        cv2.imwrite(str(saida / f"{pid}.png"), depois.imagem)
        tempos[pid] = {"processar_s": depois.segundos, "analise_s": depois.segundos_analise,
                       "total_s": total}
        print(f"{pid}: processar {depois.segundos:.1f}s", flush=True)
        (saida / "tempos.json").write_text(json.dumps(tempos, indent=1), encoding="utf-8")
finally:
    fonte.encerrar()
    shutil.rmtree(dados, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
print("FIM", "detector:", fonte.detector, flush=True)
