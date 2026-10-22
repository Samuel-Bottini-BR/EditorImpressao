"""Procura no acervo páginas com as linhas BEM curvas perto da lombada (item 2.12, 22/10/2026).

PARA QUÊ
    O Samuel não conseguiu ver se o desentortar melhora alguma coisa: nas duas
    fotos de antes (Righetti 96, Cursus 151) não havia curva para tirar. Este
    script mede, em cada página do acervo, quanto as linhas de texto descem ou
    sobem perto da lombada em relação ao meio da página, e grava a lista das
    mais curvas com uma miniatura de cada, para escolher a olho.

COMO MEDE (rápido e grosseiro; só para escolher candidatas)
    A página a 75 DPI, em cinza, com a tinta marcada (Otsu). Para a metade de
    cima e a de baixo, compara o perfil de tinta (soma por linha) de uma faixa
    vertical perto de cada beirada com o da faixa do meio: o deslocamento que
    melhor encaixa os dois perfis é quanto as linhas "andaram" ali. A curva é
    o maior deslocamento das beiradas, em milímetros, depois de tirar a parte
    que é só inclinação (a média das duas beiradas). Página dupla (mais larga
    que alta) é medida em cada metade. O Righetti (folhas deitadas) é girado
    270° antes, como o Kaique faria.

Só lê o acervo (somente leitura). Saída em relatorios/conferir/fase2-itens/2.12/procura/ (fora do git).

Uso: python procurar_linhas_curvas.py [livro ...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
RAIZ = Path(__file__).resolve().parents[3]
SAIDA = RAIZ / "relatorios" / "conferir" / "fase2-itens" / "2.12" / "procura"
DPI = 75
LIVROS = [
    "Cursus philosophicus. Tomo.2.pdf",
    "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf",
    "Marial de sermoens - Frei Balthasar Paez. (1).pdf",
    "Rhetorica Christiana -  Fray Diego Valadés.pdf",
    "Sobre a Consolação da Filosofia - Severino Boécio.pdf",
    "Na escola de Jesus - Catecismo explicado com imagens..pdf",
    "Livro de Horas - Luís XIV.pdf",
    "Graduale - Saeculum XIV.pdf",
    "Antiphon_25.pdf",
    "ljs47.pdf",
    "Giovambattista Palatino cittadino romano.pdf",
    "Matemática Para vencer.pdf",
]


def _deslocamento(a: np.ndarray, b: np.ndarray, maximo: int) -> tuple[int, float]:
    """O deslocamento (em pontos) que melhor encaixa o perfil b no a, e a nota."""
    a = (a - a.mean()) / (a.std() + 1e-6)
    b = (b - b.mean()) / (b.std() + 1e-6)
    melhor, nota = 0, -1e9
    for d in range(-maximo, maximo + 1):
        if d >= 0:
            c = float((a[d:] * b[:len(b) - d]).mean())
        else:
            c = float((a[:d] * b[-d:]).mean())
        if c > nota:
            melhor, nota = d, c
    return melhor, nota


def medir(cinza: np.ndarray) -> dict | None:
    """A curva das linhas de uma página (cinza, 75 DPI), em mm, ou None se não há texto que baste."""
    _, tinta = cv2.threshold(cinza, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    altura, largura = tinta.shape
    if tinta.mean() < 0.02 or tinta.mean() > 0.4:
        return None
    por_coluna = tinta.mean(axis=0)
    # sem as barras pretas (lombada, beirada do scanner): coluna com mais de 60% de tinta
    tinta[:, por_coluna > 0.6] = 0
    colunas = np.where((por_coluna > 0.02) & (por_coluna <= 0.6))[0]
    linhas = np.where(tinta.mean(axis=1) > 0.02)[0]
    if len(colunas) < 50 or len(linhas) < 50:
        return None
    x0, x1 = colunas.min(), colunas.max()
    y0, y1 = linhas.min(), linhas.max()
    # o bloco de texto principal: do 5% ao 95% das colunas com tinta (fora a tira da página vizinha)
    x0, x1 = int(np.percentile(colunas, 5)), int(np.percentile(colunas, 95))
    faixa = max(6, (x1 - x0) // 10)
    meio = (x0 + x1) // 2
    maximo = int(6 / 25.4 * DPI)  # até 6 mm
    resultado = {}
    for nome, (ya, yb) in {"cima": (y0, (y0 + y1) // 2), "baixo": ((y0 + y1) // 2, y1)}.items():
        if yb - ya < 40:
            return None
        ref = tinta[ya:yb, meio - faixa // 2:meio + faixa // 2].sum(axis=1).astype(float)
        esq = tinta[ya:yb, x0:x0 + faixa].sum(axis=1).astype(float)
        dir_ = tinta[ya:yb, x1 - faixa:x1].sum(axis=1).astype(float)
        de, ne = _deslocamento(ref, esq, maximo)
        dd, nd = _deslocamento(ref, dir_, maximo)
        if min(ne, nd) < 0.2:
            return None
        resultado[nome] = (de, dd)
    # tira a inclinação (a parte igual e oposta nas duas beiradas) e fica a curva
    curvas = []
    for de, dd in resultado.values():
        inclinacao = (dd - de) / 2.0
        curvas += [abs(de + inclinacao), abs(dd - inclinacao)]
    return {"curva_mm": round(max(curvas) * 25.4 / DPI, 2),
            "cima": resultado["cima"], "baixo": resultado["baixo"]}


def paginas_do_livro(nome: str):
    doc = fitz.open(ACERVO / nome)
    try:
        for i in range(doc.page_count):
            pix = doc[i].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()
            if nome.startswith("Mario Righetti"):
                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            if img.shape[1] > 1.2 * img.shape[0]:
                metade = img.shape[1] // 2
                yield i, "esquerda", img[:, :metade]
                yield i, "direita", img[:, metade:]
            else:
                yield i, "inteira", img
    finally:
        doc.close()


def main() -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)
    livros = sys.argv[1:] or LIVROS
    achados = []
    for nome in livros:
        for i, metade, img in paginas_do_livro(nome):
            m = medir(img)
            if m is None:
                continue
            achados.append({"livro": nome, "pagina_pdf": i + 1, "metade": metade, **m})
        print(nome, len(achados), flush=True)
        (SAIDA / "achados.json").write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    achados.sort(key=lambda a: -a["curva_mm"])
    (SAIDA / "achados.json").write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    # miniaturas das 40 mais curvas
    for k, a in enumerate(achados[:40]):
        for i, metade, img in paginas_do_livro_uma(a["livro"], a["pagina_pdf"] - 1):
            if metade == a["metade"]:
                cv2.imwrite(str(SAIDA / f"{k:02d}_{a['livro'][:12].strip()}_p{a['pagina_pdf']:03d}_{metade}_{a['curva_mm']}mm.jpg"), img)
    return 0


def paginas_do_livro_uma(nome: str, indice: int):
    doc = fitz.open(ACERVO / nome)
    try:
        pix = doc[indice].get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width).copy()
    finally:
        doc.close()
    if nome.startswith("Mario Righetti"):
        img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    if img.shape[1] > 1.2 * img.shape[0]:
        metade = img.shape[1] // 2
        yield indice, "esquerda", img[:, :metade]
        yield indice, "direita", img[:, metade:]
    else:
        yield indice, "inteira", img


if __name__ == "__main__":
    raise SystemExit(main())
