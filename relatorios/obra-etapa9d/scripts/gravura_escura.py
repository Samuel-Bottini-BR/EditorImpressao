"""D-532 (etapa 9d): a página no Preto e branco como sai HOJE (a conta da D-532
desligada, a de fábrica) e como sairia com a conta LIGADA
(core.filtros.GRAVURA_ESCURA_EM_CINZA), pelo caminho inteiro do programa
(core.pipeline._pagina_pronta: dividir, endireitar, cortar, filtro).

Páginas: livro novo de fábrica com a página do acervo (só leitura), ou o
projeto salvo do teste dos 14 livros (Righetti, girado e dividido).
USO (da pasta da worktree):
    python relatorios/obra-etapa9d/scripts/gravura_escura.py --saida <pasta> livro:pagina[:projeto] [...]
Grava <pasta>/<livro><pagina>-<metade>-{hoje,ligada}.png e imprime se a página
saiu em 1 bit e quanto da página ficou em tons de cinza.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
spec = importlib.util.spec_from_file_location(
    "rep", RAIZ / "relatorios" / "obra-etapa10b" / "scripts" / "reproduzir.py")
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402


def pronta(projeto, pagina):
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        folha = projeto.folhas[pagina.folha]
        return pipeline._pagina_pronta(projeto, doc, folha, pagina, pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--saida", type=Path, required=True)
    p.add_argument("alvos", nargs="+")
    a = p.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)
    for alvo in a.alvos:
        partes = alvo.split(":")
        livro, n = partes[0], int(partes[1])
        if len(partes) > 2 and partes[2] == "projeto":
            projeto, num = rep.carregar(livro), n
        else:
            projeto, num = rep.carregar_de_fabrica(livro, n)
        for pagina in rep.paginas_da_folha(projeto, num):
            pagina.filtro = F.PRETO_E_BRANCO
            for nome, ligada in (("hoje", False), ("ligada", True)):
                F.GRAVURA_ESCURA_EM_CINZA = ligada
                pipeline._GEOMETRIAS.clear()
                img, mono = pronta(projeto, pagina)
                cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                tons = float(((cinza > 10) & (cinza < 245)).mean())
                print(f"{livro}{n} {pagina.metade:8s} {nome:6s} 1 bit={mono!s:5s} "
                      f"pontos em tons de cinza={tons:.1%}", flush=True)
                cv2.imwrite(str(a.saida / f"{livro}{n}-{pagina.metade}-{nome}.png"), img)
    F.GRAVURA_ESCURA_EM_CINZA = False


if __name__ == "__main__":
    main()
