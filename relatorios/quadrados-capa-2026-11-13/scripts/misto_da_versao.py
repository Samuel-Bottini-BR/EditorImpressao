"""Quadrados na capa (13/11/2026): o caso do 13-02 (Preto e branco com "So as letras", gravura
procurada) em UMA versao do programa, para saber desde quando o buraco aparece na capa.

    python misto_da_versao.py <raiz da versao> <livro.pdf> <pagina 1-based> <saida.png>

Livro aberto como naquela versao:
  - com core.automatico.livro_leve (desde a obra, etapa 3): livro novo, "Limpar a folha" e
    "Procurar gravura e letra" LIGADOS no livro (como depois do Automatico), Preto e branco e
    "So as letras" na pagina. Assim a gravura e procurada em qualquer versao (antes de 31/10 o
    "So as letras" sozinho nao procurava).
  - sem ele (antes da obra): o livro novo com as opcoes de fabrica daquela versao ("Limpar a
    folha" e "Procurar gravura e letra" ligadas), Preto e branco e "So as letras" na pagina.
  Dividir, endireitar, cortar, margens e cadernos desligados (o enquadramento e o mesmo).
Escreve uma linha JSON com as regioes achadas (caixas) e grava a pagina (300 pontos)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
SAIDA = Path(sys.argv[4]).resolve()
DADOS = Path(__file__).resolve().parents[1] / "_trabalho" / "dados" / ("misto_" + RAIZ.name)
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)
os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402

from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, info_paginas  # noqa: E402
from modelos import Projeto  # noqa: E402


def main() -> None:
    pdf, numero = sys.argv[2], int(sys.argv[3])
    projeto = Projeto(caminho_entrada=pdf, nome=Path(pdf).stem)
    doc = abrir_pdf(pdf)
    tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
    try:
        from core import automatico
        leve = hasattr(automatico, "livro_leve")
    except ImportError:
        leve = False
    if leve:
        automatico.livro_leve(projeto, tamanhos)
    else:
        from core.filtros import ORIGINAL
        from modelos import METADE_INTEIRA, ConfigFolha, ConfigPagina
        projeto.folhas = [ConfigFolha(indice=i, dividir=False, posicao_corte=0.5)
                          for i in range(len(tamanhos))]
        projeto.paginas = [ConfigPagina(indice=i, folha=i, metade=METADE_INTEIRA, filtro=ORIGINAL)
                           for i in range(len(tamanhos))]
    for campo in ("dividir_folhas", "endireitar", "cortar_bordas", "margens_iguais",
                  "montar_cadernos"):
        if hasattr(projeto, campo):
            setattr(projeto, campo, False)
    projeto.limpar = True
    projeto.detectar_regioes = True
    pag = projeto.paginas[numero - 1]
    pag.filtro = "preto_e_branco"
    pag.misto_so_as_letras = True
    try:
        img, _ = pipeline._pagina_pronta(projeto, doc, projeto.folhas[pag.folha], pag,
                                         pipeline._FolhaDaVez(), 0)
    except (AttributeError, TypeError):
        img, _ = pipeline.renderizar_pagina(doc, projeto, pag, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(SAIDA), img)
    caixas = []
    for r in pag.selecao or []:
        if isinstance(r, dict) and r.get("pontos"):
            xs = [q[0] for q in r["pontos"]]
            ys = [q[1] for q in r["pontos"]]
            caixas.append([r.get("tipo"), r.get("origem"), r.get("operacao"),
                           [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)]])
    print(json.dumps({"raiz": RAIZ.name, "livro_leve": leve, "regioes": caixas}), flush=True)


if __name__ == "__main__":
    main()
