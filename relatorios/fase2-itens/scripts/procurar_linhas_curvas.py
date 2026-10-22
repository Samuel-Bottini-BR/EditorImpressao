"""Procura no acervo páginas com as linhas BEM curvas perto da lombada (item 2.12, 22/10/2026).

PARA QUÊ
    O Samuel não conseguiu ver se o desentortar melhora alguma coisa: nas duas
    fotos de antes (Righetti 96, Cursus 151) não havia curva para tirar. Este
    script mede, em cada página do acervo, quanto as linhas de texto descem ou
    sobem perto da lombada em relação ao meio da página, e grava a lista das
    mais curvas com uma miniatura de cada, para escolher a olho.

COMO MEDE (grosseiro; só para escolher candidatas, a olho depois)
    A página a 100 DPI, em cinza, com a tinta marcada (Otsu), sem as barras e
    faixas pretas. No bloco de texto principal, cada linha é seguida do meio
    para as beiradas (ver medir) e a curva é o quanto ela se afasta da reta
    perto das beiradas. Conferido na página de mentira dos testes: curva de
    2,5 mm mede 2,2; de 5,1 mm mede 4,4; reta mede 0. Página dupla (mais larga
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
DPI = 100
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


def medir(cinza):
    """A curva das linhas de uma página (cinza, a DPI), em mm: cada linha de
    texto é seguida do meio para as beiradas, em faixas estreitas, cada passo
    procurando o pico de tinta perto de onde a linha estava (segue a linha,
    não pula para a vizinha). Tira a reta (inclinação) de cada linha e fica o
    quanto ela se afasta da reta perto das beiradas; a curva da página é a
    mediana disso nas linhas que foram seguidas até o fim. None sem texto."""
    _, tinta = cv2.threshold(cinza, 0, 1, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    tinta = tinta.astype(np.float32)
    por_coluna = tinta.mean(axis=0)
    tinta[:, por_coluna > 0.6] = 0
    tinta[tinta.mean(axis=1) > 0.5] = 0  # a faixa preta do scanner em cima ou embaixo
    if tinta.mean() < 0.02 or tinta.mean() > 0.4:
        return None
    colunas = np.where((por_coluna > 0.02) & (por_coluna <= 0.6))[0]
    if len(colunas) < 50:
        return None
    # o bloco de texto principal: o trecho de colunas com tinta mais largo,
    # separado dos outros por um vão branco de 3 mm (a tira da página vizinha
    # e a sombra da lombada ficam de fora)
    tem = cv2.blur(por_coluna.reshape(1, -1), (max(3, int(DPI * 0.05)), 1)).ravel() > 0.01
    tem &= por_coluna <= 0.6
    vao = max(3, int(DPI * 3 / 25.4))
    trechos, inicio, branco = [], None, 0
    for x, t in enumerate(list(tem) + [False] * (vao + 1)):
        if t:
            if inicio is None:
                inicio = x
            branco, fim = 0, x
        elif inicio is not None:
            branco += 1
            if branco > vao:
                trechos.append((inicio, fim))
                inicio, branco = None, 0
    if not trechos:
        return None
    x0, x1 = max(trechos, key=lambda t: t[1] - t[0])
    largura = x1 - x0
    if largura < 100:
        return None
    faixa = max(8, int(DPI * 0.2))
    passo = max(4, faixa // 2)
    meio = (x0 + x1) // 2

    def perfil(x):
        p = tinta[:, max(0, x - faixa // 2):x + faixa // 2].mean(axis=1)
        return cv2.GaussianBlur(p.reshape(-1, 1), (1, 7), 0).ravel()

    p0 = perfil(meio)
    # os picos do meio: as linhas
    picos = [y for y in range(3, len(p0) - 3) if p0[y] > 0.15 and p0[y] == p0[y - 3:y + 4].max()]
    if len(picos) < 6:
        return None
    janela = max(2, int(DPI * 0.04))
    desvios = []
    for y_meio in picos:
        trilha = {meio: float(y_meio)}
        for sentido in (-1, 1):
            y = float(y_meio)
            x = meio + sentido * passo
            while x0 <= x <= x1:
                p = perfil(x)
                a, b = int(y) - janela, int(y) + janela + 1
                if a < 0 or b > len(p):
                    break
                trecho = p[a:b]
                if trecho.max() < 0.08:
                    x += sentido * passo
                    continue  # espaço entre palavras: segue reto
                y = float(a + int(np.argmax(trecho)))
                trilha[x] = y
                x += sentido * passo
        xs = np.array(sorted(trilha))
        if xs.min() > x0 + 0.1 * largura or xs.max() < x1 - 0.1 * largura:
            continue
        ys = np.array([trilha[x] for x in xs])
        centro = np.abs(xs - meio) < 0.3 * largura
        if centro.sum() < 3:
            continue
        reta = np.polyfit(xs[centro], ys[centro], 1)
        resto = ys - np.polyval(reta, xs)
        beirada = np.abs(xs - meio) > 0.35 * largura
        desvios.append(float(np.abs(resto[beirada]).max()) if beirada.any() else 0.0)
    if len(desvios) < 4:
        return None
    return {"curva_mm": round(float(np.median(desvios)) * 25.4 / DPI, 2),
            "curva_max_mm": round(float(np.percentile(desvios, 90)) * 25.4 / DPI, 2),
            "linhas": len(desvios)}


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
    # com livros dados (rodadas em paralelo, um livro por processo): um arquivo por livro, sem miniaturas
    arquivo = SAIDA / ("achados.json" if not sys.argv[1:] else f"achados-{livros[0][:10].strip()}.json")
    achados = []
    for nome in livros:
        for i, metade, img in paginas_do_livro(nome):
            m = medir(img)
            if m is None:
                continue
            achados.append({"livro": nome, "pagina_pdf": i + 1, "metade": metade, **m})
        print(nome, len(achados), flush=True)
        arquivo.write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    achados.sort(key=lambda a: -a["curva_mm"])
    arquivo.write_text(json.dumps(achados, ensure_ascii=False, indent=1), encoding="utf-8")
    if sys.argv[1:]:
        return 0
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
