"""Passo 0: desenha as paginas que nao estao no gabarito e sao usadas nas perguntas.

  - paginas de livros com borda preta larga (copiados para os testes em 05/10), a 150 DPI;
  - uma pagina do Opus Majus que termina no meio da folha (fim de capitulo, com o numero
    da pagina sozinho no pe), para mostrar o que o corte do ScanTailor faz com o numero:
    `procurar` lista as candidatas (desenhando o livro bem pequeno, uma pagina por vez);
    a escolhida fica em PAGINAS, a 400 DPI como as do gabarito.
Grava os PNG em saida_teste/geometria-perguntas/paginas/ (fora do git) e
dados/paginas-extras.json (de que livro e pagina veio cada uma).

Os livros sao somente leitura. Uso: python passo0_paginas_extras.py [procurar]
"""
from __future__ import annotations

import json
import sys

import numpy as np

import comum

OPUS = r"C:\Users\fotog\Desktop\opusmajustransla01baco.pdf"   # o mesmo caminho da gabarito/lista.json

# nome -> (livro, pagina do PDF comecando em 1, DPI do desenho)
PAGINAS = {
    "ljs47_p046": (str(comum.LIVROS / "ljs47.pdf"), 46, 150),
    "ljs47_p068": (str(comum.LIVROS / "ljs47.pdf"), 68, 150),
    "righetti_p055": (str(comum.LIVROS / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf"), 55, 150),
    "antiphon_p123": (str(comum.LIVROS / "Antiphon_25.pdf"), 123, 150),
    # pagina do Opus Majus que termina no meio, com o numero no pe (achada com `procurar`, 12/10)
    "opusmajus_p137": (OPUS, 137, 400),
}


def procurar(inicio: int = 12, fim: int = 140, livro: str = OPUS) -> None:
    """Lista as paginas de um livro que terminam no meio da folha: ou a tinta acaba cedo,
    ou ha um vao grande sem tinta antes do numero do pe da pagina."""
    import fitz

    with fitz.open(livro) as doc:
        for n in range(inicio, min(fim, doc.page_count) + 1):
            pix = doc[n - 1].get_pixmap(dpi=40, colorspace=fitz.csGRAY, alpha=False)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width)
            miolo = a[int(pix.height * 0.06):int(pix.height * 0.94), int(pix.width * 0.08):int(pix.width * 0.92)]
            # tinta = bem mais escuro que o papel (a 40 DPI a letra fina fica cinza, nao preta)
            papel = float(np.median(miolo))
            linhas = np.where((miolo < papel - 30).sum(axis=1) >= 4)[0]
            if linhas.size < 20 or pix.width > pix.height:
                continue
            # o maior vao sem tinta entre duas linhas com tinta (o numero no pe da pagina
            # conta como tinta, entao a pagina curta aparece como "texto, vao grande, numero")
            vaos = np.diff(linhas)
            k = int(np.argmax(vaos))
            vao = vaos[k] / miolo.shape[0]
            cima, comeco_do_vao = linhas[0] / miolo.shape[0], linhas[k] / miolo.shape[0]
            if vao > 0.28 and cima < 0.2 and comeco_do_vao > 0.25:
                print(f"pagina {n}: texto de {cima:.2f} a {comeco_do_vao:.2f} da altura, depois um vao de {vao:.2f}; "
                      f"tamanho {pix.width}x{pix.height}", flush=True)
            baixo = linhas[-1] / miolo.shape[0]
            if 0.25 < baixo < 0.65 and cima < 0.2:
                print(f"pagina {n}: a tinta acaba em {baixo:.2f} da altura (nada no pe); "
                      f"tamanho {pix.width}x{pix.height}", flush=True)


def desenhar() -> None:
    import fitz

    destino = comum.RASCUNHO / "paginas"
    destino.mkdir(parents=True, exist_ok=True)
    registro = {}
    for nome, (livro, pagina, dpi) in PAGINAS.items():
        png = destino / f"{nome}.png"
        if not png.exists():
            with fitz.open(livro) as doc:
                doc[pagina - 1].get_pixmap(dpi=dpi, alpha=False).save(str(png))
        registro[nome] = {"livro": livro, "pagina": pagina, "dpi": dpi, "png": str(png)}
        print("desenhou", nome, flush=True)
    comum.DADOS.mkdir(parents=True, exist_ok=True)
    (comum.DADOS / "paginas-extras.json").write_text(json.dumps(registro, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "procurar":
        procurar(int(sys.argv[2]), int(sys.argv[3]), *(sys.argv[4:5]))
    else:
        desenhar()
