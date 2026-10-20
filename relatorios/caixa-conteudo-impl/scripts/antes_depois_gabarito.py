"""Antes/depois do corte pelo conteúdo (item 2.5) nas páginas-gabarito e nas
de folha grande, para OLHAR. Uma imagem por página, duas metades:
  - esquerda, ANTES (como sai hoje): o corte comum do programa, em laranja;
  - direita, DEPOIS (com "Cortar seguindo o conteúdo" ligado, a página
    sozinha, sem o tamanho do livro): o corte do ScanTailor + 1 mm, em verde;
    o que ficou de fora (o aviso da g8), em vermelho; o corte alargado (a
    opção da g8), em lilás tracejado.
Usa as funções do programa (core.recortar.detectar_bordas e as de
core.pipeline / core.corte_pelo_conteudo), na folha inteira, sem endireitar
(as páginas do gabarito são folhas cruas). Grava img/antes-depois/*.jpg e
dados/antes-depois.json. Somente leitura do acervo; uma página por vez.
Uso: python antes_depois_gabarito.py [nome ...]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from core import corte_pelo_conteudo as cc  # noqa: E402
from core import pipeline  # noqa: E402
from core.recortar import detectar_bordas  # noqa: E402
import olhar_folha_grande as grande  # noqa: E402

PASTA = Path(__file__).resolve().parents[1]
SAIDA = PASTA / "img" / "antes-depois"
LARANJA, VERDE, VERMELHO, LILAS = (240, 120, 20), (20, 160, 70), (220, 40, 40), (150, 60, 200)


def paginas():
    lista = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"]
    for nome, d in sorted(lista.items()):
        yield nome, (lambda d=d: (cv2.imread(str(RAIZ / "gabarito" / d["png"]), cv2.IMREAD_COLOR),
                                  float(d["dpi_png"]), d.get("dpi_scan")))
    for nome, pdf, n in grande.PAGINAS:
        def carregar(pdf=pdf, n=n):
            img, scan = grande.desenhar_pagina(pdf, n)
            return img, grande.DPI_DO_DESENHO, scan
        yield nome, carregar


def tracejado(d, caixa, cor, e):
    grande.ret(d, _C(caixa), cor, e, tracejado=True)


class _C:
    def __init__(self, c):
        self.c = tuple(c)

    def como_tupla(self):
        return self.c


def main() -> None:
    so = set(sys.argv[1:])
    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = PASTA / "dados" / "antes-depois.json"
    dados = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for nome, carregar in paginas():
        if so and nome not in so:
            continue
        img, dpi, scan = carregar()
        alt, larg = img.shape[:2]
        comum = detectar_bordas(img, dpi=dpi)
        x, y, w, h = comum.tupla
        antes = (x * larg, y * alt, (x + w) * larg, (y + h) * alt)
        medido = pipeline._medir_o_conteudo(img, dpi, scan, comum.pecas)
        depois = cc.caixa_do_corte(medido.medida)
        tiradas = cc.tiradas_do_corte(depois, medido.candidatas) if depois else []
        alargado = (cc.alargar(depois, tiradas, medido.medida.mm_por_ponto, larg, alt)
                    if tiradas else None)
        dados[nome] = {"antes": [round(v, 1) for v in antes],
                       "depois": None if depois is None else [round(v, 1) for v in depois],
                       "tiradas": [[round(v, 1) for v in t] for t in tiradas],
                       "alargado": None if alargado is None else [round(v, 1) for v in alargado],
                       "motivo": medido.medida.motivo}
        e = max(3, larg // 300)
        quadros = []
        for titulo, desenhar in (("ANTES (hoje): corte comum", "antes"),
                                 ("DEPOIS: segue o conteúdo", "depois")):
            pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            d = ImageDraw.Draw(pil)
            if desenhar == "antes":
                grande.ret(d, _C(antes), LARANJA, e)
            else:
                if depois:
                    grande.ret(d, _C(depois), VERDE, e)
                for t in tiradas:
                    d.rectangle(t, outline=VERMELHO, width=e)
                if alargado:
                    grande.ret(d, _C(alargado), LILAS, max(2, e - 1), tracejado=True)
            pil.thumbnail((900, 1200))
            faixa = Image.new("RGB", (pil.width, 40), (255, 255, 255))
            try:
                f = ImageFont.truetype("arial.ttf", 20)
            except OSError:
                f = ImageFont.load_default()
            texto = f"{nome}  {titulo}"
            if desenhar == "depois" and tiradas:
                texto += f"  (aviso: {len(tiradas)} de fora)"
            if desenhar == "depois" and not depois:
                texto += f"  (sem caixa: {medido.medida.motivo})"
            ImageDraw.Draw(faixa).text((6, 8), texto, fill=(0, 0, 0), font=f)
            q = Image.new("RGB", (pil.width, pil.height + 40), (255, 255, 255))
            q.paste(faixa, (0, 0))
            q.paste(pil, (0, 40))
            quadros.append(q)
        largura = sum(q.width for q in quadros) + 16
        final = Image.new("RGB", (largura, max(q.height for q in quadros)), (220, 220, 220))
        final.paste(quadros[0], (0, 0))
        final.paste(quadros[1], (quadros[0].width + 16, 0))
        final.save(SAIDA / f"{nome}.jpg", quality=84)
        print(nome, "tiradas", len(tiradas), "depois", dados[nome]["depois"], flush=True)
        destino.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
        del img


if __name__ == "__main__":
    main()
