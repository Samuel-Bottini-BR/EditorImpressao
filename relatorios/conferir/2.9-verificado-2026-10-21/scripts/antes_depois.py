"""Verificador, 21/10/2026 (item 2.9): antes/depois MEU, em tres paginas de verdade de letra clara em fundo escuro:
Horas 187 (a do implementador: lombada de couro com o titulo dourado), a capa do "Historia do Direito Politico
Brasileiro" (escaneada, letra branca em fundo escuro) e um slide (paragrafos brancos em fundo escuro), as duas
ultimas achadas pela minha procura (scripts/procurar.py). Cada pagina sai pelo caminho do programa
(analisar_projeto -> renderizar_pagina no DPI do projeto, o mesmo do PDF), em Preto e branco e Melhorar, com a
caixinha desmarcada (hoje) e marcada. Grava img/29-<nome>.jpg (pagina inteira, 5 colunas) e img/29-<nome>-perto.jpg
(o pedaco com letra, ampliado). So le os livros; pasta de dados isolada.
Uso: python antes_depois.py <raiz do codigo>"""
import os
import sys
import tempfile
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(sys.argv[1]).resolve()
os.environ["LOCALAPPDATA"] = str(Path(tempfile.gettempdir()) / "verif29_dados")
sys.path.insert(0, str(RAIZ))
from core import pipeline as P  # noqa: E402
from core.filtros import MELHORAR, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
TRAB = BASE / "trabalho" / "paginas"; TRAB.mkdir(parents=True, exist_ok=True)
IMG = BASE / "img"
HORAS = next(Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE").glob("Livro de Horas*.pdf"))
DSI = Path(r"D:\Livros para editar\2 - TEOLOGIA\Doutrina Social da Igreja")
PAGINAS = {   # nome: (pdf, pagina, pedaco de perto em fracao (x0, y0, x1, y1))
    "horas-187": (HORAS, 187, (0.0, 0.18, 1.0, 0.34)),
    "capa-direito": (DSI / "Corporativismo, Integralismo, Distributismo e Municipalismo à luz da DSI"
                     / "José Pedro Galvão de Sousa - História do Direito Político Brasileiros.pdf", 1, (0.0, 0.0, 1.0, 0.5)),
    "slide": (DSI / "TCC" / "PARTE 4 - O MEIO AMBIENTE HOJE - DSI EM MEIO A IDEOLOGIAS.pdf", 27, (0.0, 0.0, 0.6, 0.6)),
}
F = ImageFont.truetype("arialbd.ttf", 28)
COLS = [("Original", None, None), ("Hoje: Preto e branco", PRETO_E_BRANCO, False),
        ("Preto e branco + Letra clara", PRETO_E_BRANCO, True), ("Hoje: Melhorar", MELHORAR, False),
        ("Melhorar + Letra clara", MELHORAR, True)]


def rgb(a):
    return Image.fromarray(a if a.ndim == 3 else np.stack([a] * 3, -1))


for nome, (pdf, num, caixa) in PAGINAS.items():
    so = TRAB / f"{nome}.pdf"
    with fitz.open(pdf) as o, fitz.open() as d:
        d.insert_pdf(o, from_page=num - 1, to_page=num - 1); d.save(so)
    projeto = P.analisar_projeto(Projeto(caminho_entrada=str(so), nome=nome))
    doc = abrir_pdf(str(so))
    pg = projeto.paginas_ativas[0]
    imgs = []
    for rot, filtro, claro in COLS:
        if filtro is None:
            pix = doc[0].get_pixmap(dpi=projeto.qualidade_dpi)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
        else:
            pg.filtro, pg.claro_no_escuro = filtro, claro
            a, _ = P.renderizar_pagina(doc, projeto, pg, dpi=projeto.qualidade_dpi)
            if a.ndim == 3:
                a = a[:, :, ::-1]          # o programa trabalha em BGR (OpenCV); a imagem sai em RGB
        imgs.append((rot, rgb(np.ascontiguousarray(a))))
    doc.close()
    for sufixo, corte, alvo in (("", None, 380), ("-perto", caixa, 520)):
        partes = []
        for rot, im in imgs:
            if corte:
                w, h = im.size
                im = im.crop((int(corte[0] * w), int(corte[1] * h), int(corte[2] * w), int(corte[3] * h)))
            im = im.resize((alvo, max(1, round(im.height * alvo / im.width))), Image.LANCZOS)
            partes.append((rot, im))
        hmax = max(p.height for _, p in partes)
        t = Image.new("RGB", (len(partes) * (alvo + 16), hmax + 44), (255, 255, 255))
        dr = ImageDraw.Draw(t)
        for k, (rot, im) in enumerate(partes):
            t.paste(im, (k * (alvo + 16), 44)); dr.text((k * (alvo + 16) + 4, 6), rot, fill=(160, 60, 0), font=F)
        t.save(IMG / f"29-{nome}{sufixo}.jpg", quality=88)
    print(nome, projeto.qualidade_dpi, [im.size for _, im in imgs][:2], flush=True)
