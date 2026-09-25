"""Parte 6: exporta as 5 páginas difíceis para comparar com o CamScanner.

Uso:
    python teste_para_comparar.py "pasta com os livros"

Grava em <pasta>/para_comparar/ os pares ORIGINAL / NOSSO, em alta resolução.
Você processa os ORIGINAL no CamScanner e põe lado a lado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

from core.filtros import MELHORAR, PRETO_E_BRANCO, aplicar_filtro
from core.pdf_io import abrir_pdf, pagina_para_array

DPI = 300

# (rótulo, arquivo, página, filtro que julgamos o certo, por quê)
CASOS = [
    ("01_amarelada", "Marial de sermoens - Frei Balthasar Paez..pdf", 575,
     PRETO_E_BRANCO, "papel bem amarelado, só texto"),
    ("02_bleedthrough", "Marial de sermoens - Frei Balthasar Paez..pdf", 862,
     PRETO_E_BRANCO, "texto do verso aparecendo"),
    ("03_iluminura", "Livro de Horas - Luís XIV.pdf", 61,
     MELHORAR, "iluminura colorida com ouro"),
    ("04_xilogravura", "Rhetorica Christiana -  Fray Diego Valadés.pdf", 73,
     PRETO_E_BRANCO, "gravura de traço fino"),
    ("05_torta", "Sobre a Consolação da Filosofia - Severino Boécio.pdf", 2,
     PRETO_E_BRANCO, "página torta"),
]


def gravar(caminho: Path, img: np.ndarray) -> None:
    """PNG em caminho com acento (cv2.imwrite falha calado nesses casos)."""
    ok, buffer = cv2.imencode(".png", img)
    if ok:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_bytes(buffer.tobytes())


def main(pasta: str) -> int:
    """Para cada CASO, exporta a página ORIGINAL (crua) e NOSSO (com o filtro
    julgado certo) em DPI alto, e escreve um LEIA.txt explicando o que
    comparar e por quê."""
    raiz = Path(pasta)
    destino = raiz / "para_comparar"
    destino.mkdir(parents=True, exist_ok=True)

    linhas = ["PÁGINAS PARA COMPARAR COM O CAMSCANNER", "",
              "Processe os arquivos _ORIGINAL no CamScanner e ponha ao lado do",
              "_NOSSO correspondente.", ""]

    for rotulo, nome, pagina, filtro, motivo in CASOS:
        livro = raiz / nome
        if not livro.exists():
            print(f"  faltando: {nome}")
            continue

        doc = abrir_pdf(livro)
        try:
            indice = min(max(0, pagina - 1), doc.page_count - 1)
            bruta = pagina_para_array(doc, indice, dpi=DPI)
            gravar(destino / f"{rotulo}_ORIGINAL.png", bruta)

            tratada, _ = aplicar_filtro(bruta, filtro)
            if tratada.ndim == 2:
                tratada = cv2.cvtColor(tratada, cv2.COLOR_GRAY2BGR)
            gravar(destino / f"{rotulo}_NOSSO.png", tratada)

            print(f"  {rotulo}: {nome[:38]} pág. {indice + 1}  ({motivo})")
            linhas.append(f"{rotulo}")
            linhas.append(f"    livro: {nome}")
            linhas.append(f"    página: {indice + 1}   ({motivo})")
            linhas.append(f"    nosso filtro: {filtro}")
            linhas.append("")
            del bruta, tratada
        finally:
            doc.close()

    (destino / "LEIA.txt").write_text("\n".join(linhas) + "\n", encoding="utf-8-sig")
    print(f"\nem: {destino}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
