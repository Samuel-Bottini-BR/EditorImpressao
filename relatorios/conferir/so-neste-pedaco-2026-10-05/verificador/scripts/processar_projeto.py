r"""Processa um projeto.json gravado pela janela, com o codigo de RAIZ (sem janela).

Uso: python processar_projeto.py RAIZ PROJETO_JSON SAIDA_PDF

LOCALAPPDATA e TEMP descartaveis ao lado da saida. Os modelos vem da pasta
original (so lidos) quando a copia nao tem modelos\ (git archive).
"""
import json
import os
import shutil
import sys
import time
from pathlib import Path

raiz, proj, saida = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), Path(sys.argv[3]).resolve()
tmp = saida.parent / ("_tmp_" + saida.stem)
(tmp / "local").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(tmp / "local")
os.environ["TEMP"] = os.environ["TMP"] = str(tmp)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.chdir(raiz)
sys.path.insert(0, str(raiz))
import tempfile  # noqa: E402
tempfile.tempdir = str(tmp)

MODELOS = Path(r"D:\programas\EditorImpressao\modelos")
if not (raiz / "modelos").is_dir():
    import core.detectar_regioes as _dr
    import core.rede_selecao as _rede
    _dr.CAMINHO_MODELO = MODELOS / "doclayout.onnx"
    _dr._detector.caminho = _dr.CAMINHO_MODELO
    _rede.PASTA = MODELOS / "mobile_sam"
    _rede.CODIFICADOR = _rede.PASTA / _rede.CODIFICADOR.name
    _rede.DECODIFICADOR = _rede.PASTA / _rede.DECODIFICADOR.name
    print("modelos da pasta original", flush=True)

from core import pipeline  # noqa: E402
from modelos import Projeto  # noqa: E402

projeto = Projeto.de_dicionario(json.loads(proj.read_text(encoding="utf-8")))
projeto.caminho_saida = str(saida)
t0 = time.perf_counter()
pipeline.processar(projeto)
print("ok", round(time.perf_counter() - t0, 1), "s", saida, flush=True)
shutil.rmtree(tmp, ignore_errors=True)
