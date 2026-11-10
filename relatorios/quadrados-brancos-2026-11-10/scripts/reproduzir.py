"""Quadrados brancos (Samuel, 10/11/2026): reproduz pela conta do programa.

Livro novo (core.automatico.livro_leve, como a tela abre), pagina escolhida, filtro
escolhido a mao (marca FILTRO), e desenha:
  - a previa (core.pipeline.renderizar_com_filtro, DPI_PREVIA)
  - o PDF (core.pipeline._pagina_pronta, qualidade_dpi)
Uso: python reproduzir.py <saida> <livro.pdf> <pagina1based> [variantes...]
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = Path(r"D:\programas\EditorImpressao\.claude\worktrees\obra-juncao")
sys.path.insert(0, str(RAIZ))
(AQUI / "dados").mkdir(exist_ok=True)
(AQUI / "temp").mkdir(exist_ok=True)
os.environ["LOCALAPPDATA"] = str(AQUI / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(AQUI / "temp")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import automatico, etapas, pipeline  # noqa: E402
from core import filtros as F  # noqa: E402
from core.pdf_io import DPI_PREVIA, abrir_pdf, info_paginas  # noqa: E402
from modelos import Projeto  # noqa: E402

VARIANTES = {
    # nome: (filtro, ajuste, respeitar, limpar_no_livro)
    "original": ("original", 50, True, False),
    "melhorar_forte_respeitar": ("melhorar", 100, True, False),
    "melhorar_forte_sem_respeitar": ("melhorar", 100, False, False),
    "magico_fraco_sem_respeitar": ("magico_pro", 0, False, False),
    "magico_fraco_sem_respeitar_auto": ("magico_pro", 0, False, True),
    "melhorar_forte_respeitar_auto": ("melhorar", 100, True, True),
    "magico_fraco_respeitar_auto": ("magico_pro", 0, True, True),
    "melhorar_normal": ("melhorar", 50, True, False),
    "magico_normal": ("magico_pro", 50, True, False),
}


def livro_novo(pdf: str) -> Projeto:
    projeto = Projeto(caminho_entrada=pdf, nome=Path(pdf).stem)
    doc = abrir_pdf(pdf)
    try:
        tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
    finally:
        doc.close()
    automatico.livro_leve(projeto, tamanhos)
    return projeto


def preparar(projeto: Projeto, indice: int, variante: str):
    filtro, ajuste, respeitar, limpar = VARIANTES[variante]
    p = copy.deepcopy(projeto)
    pag = p.paginas[indice]
    pag.filtro = filtro
    pag.clareza_melhorar = ajuste if filtro == "melhorar" else pag.clareza_melhorar
    pag.intensidade_magico = ajuste if filtro == "magico_pro" else pag.intensidade_magico
    pag.respeitar_gravuras_achadas = respeitar
    if limpar:
        p.limpar = True                     # "Limpar a folha" (o Automatico) ligado no livro
    else:
        etapas.marcar_mexida_a_mao(pag, etapas.FILTRO)   # escolhido a mao no painel
    return p, pag


def desenhar(projeto: Projeto, pag, pdf_final: bool):
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        if pdf_final:
            folha = projeto.folhas[pag.folha]
            img, _ = pipeline._pagina_pronta(projeto, doc, folha, pag, pipeline._FolhaDaVez(), 0)
        else:
            img, _ = pipeline.renderizar_com_filtro(doc, projeto, pag, pag.filtro, dpi=DPI_PREVIA)
    finally:
        doc.close()
    return img


def main() -> None:
    saida = Path(sys.argv[1])
    saida.mkdir(parents=True, exist_ok=True)
    pdf = sys.argv[2]
    indice = int(sys.argv[3]) - 1
    nomes = sys.argv[4:] or list(VARIANTES)
    sem_limpeza = os.environ.get("SEM_LIMPEZA") == "1"
    if sem_limpeza:     # prova da causa: tira so o ultimo passo dos dois filtros
        F._limpar_o_papel_de_verdade = lambda original, saida, dentro_da_gravura=False: saida
    if os.environ.get("CANDIDATO") == "1":   # o conserto candidato (so neste processo)
        sys.path.insert(0, str(AQUI))
        import candidato
        candidato.instalar()
    projeto = livro_novo(pdf)
    info = {}
    for nome in nomes:
        p, pag = preparar(projeto, indice, nome)
        for pdf_final in (False, True):
            img = desenhar(p, pag, pdf_final)
            rot = f"{nome}_{'pdf' if pdf_final else 'previa'}"
            cv2.imwrite(str(saida / f"{rot}.png"), img)
            sel = pag.selecao or []
            info[rot] = {"forma": list(img.shape), "regioes": [
                (r.get("tipo"), r.get("origem")) for r in sel] if isinstance(sel, list) else str(sel)}
            print(rot, img.shape, info[rot]["regioes"], flush=True)
    (saida / "info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
