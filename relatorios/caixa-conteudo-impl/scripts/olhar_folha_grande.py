"""Olhar a caixa do conteúdo do ScanTailor nos livros de "folha grande"
(ljs47, Antiphon, Egenloff), com o DPI que o programa diz e com o DPI do PDF.

POR QUE (pedido da gerente, 20/10/2026)
    O pesquisador anotou em 13/10 que nesses livros a caixa do conteúdo
    "encolhe muito com o DPI do programa e ninguém olhou se corta texto".
    Este script desenha as caixas em cima da página para alguém OLHAR:
      - verde cheio: a caixa do conteúdo com o DPI do programa
        (core.caixas_scantailor.achar_na_pagina: a mesma conta do endireitar,
        do limpar pontinhos e da gravura);
      - vermelho tracejado: a caixa com o DPI que o PDF diz (o desenho a 150
        DPI de uma página de 72 ou 96 DPI "do PDF": o que o pesquisador fez
        em 12/10);
      - azul: a caixa da página (programa).
    E grava os números em dados/folha-grande.json.

Nada aqui muda o programa nem as páginas (somente leitura do acervo).
Uso (da raiz da worktree):
    .venv\\Scripts\\python.exe relatorios\\caixa-conteudo-impl\\scripts\\olhar_folha_grande.py [dpi ...]
Os números extras (opcionais) são DPIs a mais para dizer à DLL, para ver
onde a caixa muda.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from core import caixas_scantailor as cs  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
SAIDA = PASTA / "img" / "folha-grande"
DADOS = PASTA / "dados" / "folha-grande.json"
LIVROS = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
EGENLOFF = Path(r"D:\Livros para editar\Egenloff15271880ModelbuchWHZ_231103_053749.pdf")

# (nome, PDF, página 1..n). As páginas são desenhadas a 150 DPI do PDF.
PAGINAS = [
    ("ljs47_p046", LIVROS / "ljs47.pdf", 46),
    ("ljs47_p068", LIVROS / "ljs47.pdf", 68),
    ("ljs47_p010", LIVROS / "ljs47.pdf", 10),
    ("antiphon_p088", LIVROS / "Antiphon_25.pdf", 88),
    ("antiphon_p123", LIVROS / "Antiphon_25.pdf", 123),
    ("antiphon_p260", LIVROS / "Antiphon_25.pdf", 260),
    ("egenloff_p003", EGENLOFF, 3),
    ("egenloff_p047", EGENLOFF, 47),
    ("egenloff_p012", EGENLOFF, 12),
]
DPI_DO_DESENHO = 150.0

VERDE = (20, 160, 70)
VERMELHO = (220, 40, 40)
AZUL = (30, 110, 230)
LILAS = (150, 60, 200)


def desenhar_pagina(pdf: Path, numero: int) -> tuple[np.ndarray, float | None]:
    """A página a 150 DPI (BGR) e o DPI do scan (a conta de core.pipeline._dpi_do_scan)."""
    with fitz.open(pdf) as doc:
        p = doc[numero - 1]
        pix = p.get_pixmap(matrix=fitz.Matrix(DPI_DO_DESENHO / 72, DPI_DO_DESENHO / 72), alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        maior = max((int(i[2]) for i in p.get_images()), default=0)
        scan = maior / (p.rect.width / 72.0) if maior else None
    return cv2.cvtColor(img, cv2.COLOR_RGB2BGR), scan


def ret(d: ImageDraw.ImageDraw, caixa, cor, e: int, tracejado: bool = False) -> None:
    if caixa is None:
        return
    x0, y0, x1, y1 = caixa.como_tupla()
    if not tracejado:
        d.rectangle([x0, y0, x1, y1], outline=cor, width=e)
        return
    passo = e * 6
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        comprimento = max(abs(b[0] - a[0]), abs(b[1] - a[1]))
        n = max(1, int(comprimento // passo))
        for i in range(0, n, 2):
            t0, t1 = i / n, min(1.0, (i + 1) / n)
            d.line([a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0,
                    a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1], fill=cor, width=e)


def lista(c):
    return None if c is None else [round(v, 1) for v in c.como_tupla()]


def tiras_das_beiradas(img: np.ndarray, caixa, nome: str, vao: int = 140) -> None:
    """As quatro beiradas da caixa, ampliadas: uma tira de 2 x `vao` pontos em
    volta de cada lado (em cima, embaixo, esquerda e direita deitadas), com a
    linha da caixa em verde. Grava <nome>-beiradas.jpg."""
    if caixa is None:
        return
    alt, larg = img.shape[:2]
    x0, y0, x1, y1 = (int(round(v)) for v in caixa.como_tupla())
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).copy()
    cv2.rectangle(rgb, (x0, y0), (x1 - 1, y1 - 1), VERDE, 2)
    tiras = []
    for lado in ("cima", "baixo", "esquerda", "direita"):
        if lado in ("cima", "baixo"):
            y = y0 if lado == "cima" else y1
            t = rgb[max(0, y - vao):min(alt, y + vao), max(0, x0 - vao):min(larg, x1 + vao)]
        else:
            x = x0 if lado == "esquerda" else x1
            t = rgb[max(0, y0 - vao):min(alt, y1 + vao), max(0, x - vao):min(larg, x + vao)]
            t = np.ascontiguousarray(np.rot90(t, -1 if lado == "esquerda" else 1))
        tiras.append((lado, t))
    largura = max(t.shape[1] for _, t in tiras)
    alto = sum(t.shape[0] + 34 for _, t in tiras)
    quadro = Image.new("RGB", (largura, alto), (255, 255, 255))
    d = ImageDraw.Draw(quadro)
    try:
        f = ImageFont.truetype("arial.ttf", 24)
    except OSError:
        f = ImageFont.load_default()
    y = 0
    for lado, t in tiras:
        d.text((6, y + 4), f"{nome}: beirada de {lado} da caixa verde", fill=(0, 0, 0), font=f)
        quadro.paste(Image.fromarray(t), (0, y + 34))
        y += t.shape[0] + 34
    quadro.thumbnail((1800, 4000))
    quadro.save(SAIDA / f"{nome}-beiradas.jpg", quality=85)


def main() -> None:
    extras = [float(v) for v in sys.argv[1:]]
    SAIDA.mkdir(parents=True, exist_ok=True)
    resultado = {}
    for nome, pdf, numero in PAGINAS:
        img, scan = desenhar_pagina(pdf, numero)
        alt, larg = img.shape[:2]
        dpi_prog = cs.dpi_para_as_caixas(larg, alt, DPI_DO_DESENHO, scan)
        prog = cs.achar_na_pagina(img, DPI_DO_DESENHO, scan)
        do_pdf = cs.achar(img, DPI_DO_DESENHO)
        outros = {str(v): cs.achar(img, v) for v in extras}
        r = {
            "pdf": str(pdf), "pagina": numero, "tamanho": [larg, alt],
            "dpi_do_scan": None if scan is None else round(scan, 1),
            "dpi_programa": round(float(dpi_prog), 1),
            "programa": {"pagina": lista(prog.pagina), "conteudo": lista(prog.conteudo),
                         "segundos": round(prog.segundos, 2)},
            "dpi_do_pdf": {"pagina": lista(do_pdf.pagina), "conteudo": lista(do_pdf.conteudo),
                           "segundos": round(do_pdf.segundos, 2)},
            "outros": {k: {"pagina": lista(v.pagina), "conteudo": lista(v.conteudo)} for k, v in outros.items()},
        }
        resultado[nome] = r
        print(nome, "scan", r["dpi_do_scan"], "dito", r["dpi_programa"],
              "prog", r["programa"]["conteudo"], "pdf", r["dpi_do_pdf"]["conteudo"],
              {k: v["conteudo"] for k, v in r["outros"].items()})

        pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        d = ImageDraw.Draw(pil)
        e = max(4, larg // 350)
        ret(d, prog.pagina, AZUL, e)
        ret(d, do_pdf.conteudo, VERMELHO, e, tracejado=True)
        ret(d, prog.conteudo, VERDE, e)
        for v in outros.values():
            ret(d, v.conteudo, LILAS, max(2, e // 2))
        try:
            f = ImageFont.truetype("arial.ttf", max(22, larg // 60))
        except OSError:
            f = ImageFont.load_default()
        d.rectangle([0, 0, larg, max(30, larg // 40)], fill=(255, 255, 255))
        d.text((10, 4), f"{nome}  verde = DPI do programa ({dpi_prog:.0f})  vermelho = DPI do PDF "
                        f"(desenho {DPI_DO_DESENHO:.0f})  azul = pagina", fill=(0, 0, 0), font=f)
        pil.thumbnail((1500, 1500))
        pil.save(SAIDA / f"{nome}.jpg", quality=85)
        tiras_das_beiradas(img, prog.conteudo, nome)
    DADOS.write_text(json.dumps(resultado, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
