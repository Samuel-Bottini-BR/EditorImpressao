"""Antes/depois da borda preta (item 2.13) nas páginas com borda de scanner,
para OLHAR. Três quadros por página, com a CONTA DO PROGRAMA
(core.pipeline.preparar_metade_e_geometria, livro novo, endireitar ligado):
  1. HOJE: o corte comum (opção desligada);
  2. "SÓ O PRETO";
  3. "ATÉ A MOLDURA".
O que fica fora do corte aparece escurecido. Grava img/borda-preta/*.jpg e
dados/borda-preta.json. Somente leitura do acervo; uma página por vez.
Uso: python antes_depois_borda_preta.py [nome ...]
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

from core import borda_preta as bp  # noqa: E402
from core import pipeline  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
SAIDA = PASTA / "img" / "borda-preta"
L = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
EGENLOFF = Path(r"D:\Livros para editar\Egenloff15271880ModelbuchWHZ_231103_053749.pdf")
PAGINAS = [
    ("siebmacher_p007", L / "Schön Neues Modell Buch - Johann Siebmacher.pdf", 7),
    ("siebmacher_p009", L / "Schön Neues Modell Buch - Johann Siebmacher.pdf", 9),
    ("ljs47_p046", L / "ljs47.pdf", 46),
    ("ljs47_p068", L / "ljs47.pdf", 68),
    ("antiphon_p088", L / "Antiphon_25.pdf", 88),
    ("antiphon_p260", L / "Antiphon_25.pdf", 260),
    ("egenloff_p003", EGENLOFF, 3),
    ("egenloff_p047", EGENLOFF, 47),
    ("cursus_p003", L / "Cursus philosophicus. Tomo.2.pdf", 3),
    ("cursus_p314", L / "Cursus philosophicus. Tomo.2.pdf", 314),
    ("matematica_p032", L / "Matemática Para vencer.pdf", 32),
    ("righetti_p055", L / "Mario Righetti - Historia de la Liturgia 02-2 (da_página_262_à_531).pdf", 55),
    ("camoes_p066", None, 66),
    ("camoes_p104", None, 104),
]
CAMOES = Path(r"D:\Livros para editar\HISTÓRIA\Luiz de Camões levantando o seu monumento ou A Historia de Portugal justificada pelos Lusiadas.pdf")
DPI = 150


def quadro(img, recorte, titulo):
    alt, larg = img.shape[:2]
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if recorte is not None:
        x, y, w, h = recorte
        x0, y0, x1, y1 = int(x * larg), int(y * alt), int((x + w) * larg), int((y + h) * alt)
        escuro = Image.new("RGB", pil.size, (40, 40, 40))
        mascara = Image.new("L", pil.size, 150)
        ImageDraw.Draw(mascara).rectangle([x0, y0, x1, y1], fill=0)
        pil = Image.composite(escuro, pil, mascara)
        ImageDraw.Draw(pil).rectangle([x0, y0, x1, y1], outline=(20, 200, 80), width=max(3, larg // 300))
    pil.thumbnail((620, 860))
    q = Image.new("RGB", (pil.width, pil.height + 34), (255, 255, 255))
    try:
        f = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        f = ImageFont.load_default()
    ImageDraw.Draw(q).text((5, 7), titulo, fill=(0, 0, 0), font=f)
    q.paste(pil, (0, 34))
    return q


def main():
    so = set(sys.argv[1:])
    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / "dados" / "borda-preta.json"
    dados = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for nome, pdf, n in PAGINAS:
        if so and nome not in so:
            continue
        pdf = pdf or CAMOES
        if not pdf.exists():
            print(nome, "sem o PDF", flush=True)
            continue
        with fitz.open(pdf) as doc:
            pg = doc[n - 1]
            pix = pg.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72), alpha=False)
        img = cv2.cvtColor(np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3),
                           cv2.COLOR_RGB2BGR)
        quadros, linha = [], {}
        for titulo, campos in (("HOJE (desligada)", {}),
                               ("SÓ O PRETO", {"borda_preta": True, "borda_preta_ate": bp.SO_O_PRETO}),
                               ("ATÉ A MOLDURA", {"borda_preta": True, "borda_preta_ate": bp.ATE_A_MOLDURA})):
            for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
                g.clear()
            projeto = Projeto(caminho_entrada=str(pdf), qualidade_dpi=DPI, **campos)
            folha, pagina = ConfigFolha(indice=n - 1, dividir=False), ConfigPagina(indice=0, folha=0)
            projeto.folhas, projeto.paginas = [folha], [pagina]
            inteira = pipeline.preparar_para_recorte(img, folha, pagina, projeto)
            geometria = pipeline._geometria(inteira, pagina, projeto, dpi=DPI)
            recorte, angulo = geometria
            reta = inteira
            if abs(angulo) >= pipeline.ANGULO_MINIMO:
                reta = pipeline.rotacionar(inteira, angulo)
            linha[titulo] = {"recorte": None if recorte is None else [round(v, 4) for v in recorte],
                             "angulo": round(float(angulo), 2)}
            quadros.append(quadro(reta, recorte, f"{nome}  {titulo}"))
        dados[nome] = linha
        larg = sum(q.width for q in quadros) + 20
        final = Image.new("RGB", (larg, max(q.height for q in quadros)), (210, 210, 210))
        x = 0
        for q in quadros:
            final.paste(q, (x, 0))
            x += q.width + 10
        final.save(SAIDA / f"{nome}.jpg", quality=84)
        print(nome, linha, flush=True)
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
