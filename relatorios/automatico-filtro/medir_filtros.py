"""D-582 (a): a capa do "Na escola de Jesus" (copia em _tmp/dados) desenhada em cada filtro,
com a marcacao que o Automatico deixou e sem nenhuma marcacao. Mede a diferenca entre os
filtros (media do |a-b| em 0..255), dentro e fora da maior gravura."""
import copy
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parents[2] / "_tmp"   # a copia do projeto mora em <worktree>/_tmp/dados
sys.path.insert(0, str(AQUI.parent))
os.environ["LOCALAPPDATA"] = str(AQUI / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(AQUI / "temp")

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

import projetos  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_com_filtro  # noqa: E402
from modelos import Projeto  # noqa: E402

PASTA = AQUI / "dados/EditorImpressao/projetos/Na escola de Jesus - Catecismo explicado com imagens"
import json
projeto = Projeto.de_dicionario(json.loads((PASTA / "projeto.json").read_text(encoding="utf-8")))
IDX = int(os.environ.get("PAG", "0"))
DPI = int(os.environ.get("DPI", "110"))
FILTROS = ["original", "preto_e_branco", "melhorar", "magico_pro"]


def cinza(a):
    a = a.astype(np.float32)
    return a if a.ndim == 2 else a.mean(axis=2)


def desenhar(proj, sem_marcacao=False):
    doc = abrir_pdf(proj.caminho_entrada)
    saidas = {}
    try:
        for f in FILTROS:
            p = copy.deepcopy(proj)
            pag = p.paginas[IDX]
            if sem_marcacao:
                p.detectar_regioes = False
                pag.selecao = []
                pag.zonas_na_folha = []
            img, _ = renderizar_com_filtro(doc, p, pag, f, dpi=DPI)
            saidas[f] = img
    finally:
        doc.close()
    return saidas


for rotulo, sem in (("com a marcacao do Automatico", False), ("sem marcacao nenhuma", True)):
    s = desenhar(projeto, sem)
    print(f"--- pagina {IDX + 1}, {rotulo}")
    for f, img in s.items():
        cor = img.ndim == 3 and float(np.abs(img[..., 0].astype(int) - img[..., 2].astype(int)).mean())
        print(f"  {f:15s} forma {img.shape} media {cinza(img).mean():6.1f} cor(|R-B|) {cor}")
        Image.fromarray(img if img.ndim == 2 else img[..., ::-1]).save(
            AQUI / f"filtro_{IDX}_{'sem' if sem else 'com'}_{f}.png")
    for a in FILTROS:
        for b in FILTROS:
            if a < b:
                ia, ib = cinza(s[a]), cinza(s[b])
                if ia.shape == ib.shape:
                    print(f"  |{a} - {b}| = {np.abs(ia - ib).mean():6.2f}")
