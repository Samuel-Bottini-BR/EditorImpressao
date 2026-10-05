r"""Antes | depois do conserto do "so neste pedaco" no Preto e branco (P6 da
conferencia 11, 05/10/2026).

Para cada pagina: o programa abre o PDF do gabarito (analisar_projeto, como o
TarefaAnalise), desenha a pagina uma vez para achar gravura e letra (a mesma
marcacao que a aba Marcar mostra), e um retangulo "gravura ou foto" com "so
neste pedaco: Original" e acrescentado a mao (Regiao com origem MAO e filtro
ORIGINAL, como a aba Marcar grava). Depois o livro e PROCESSADO de verdade
(core.pipeline.processar, o botao "Confirmar e processar") em Preto e branco, e
a pagina e lida de volta do PDF gravado (conferencia.paginas_do_pdf):

    ANTES  = o filtro de 044a7c1 (core/filtros.py daquele commit, lido com
             git show e posto no lugar de aplicar_filtro_com_selecao do
             pipeline; o resto do codigo e o de hoje);
    DEPOIS = o codigo deste ramo.

Medido: tempo do processar (antes e depois, em seguida), se a pagina saiu em
1 bit, e quanto da pintura saiu igual ao original.

Uso: .venv\Scripts\python.exe relatorios\conferir\so-neste-pedaco-2026-10-05\scripts\gerar_antes_depois.py
Grava os .jpg e medidas.json em relatorios\conferir\so-neste-pedaco-2026-10-05\.
LOCALAPPDATA e TEMP descartaveis (fora da pasta real do Samuel).
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
RAIZ = Path(__file__).resolve().parents[4]
TRABALHO = Path(tempfile.mkdtemp(prefix="so_neste_pedaco_"))
os.environ["LOCALAPPDATA"] = str(TRABALHO / "localappdata")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from conferencia import paginas_do_pdf  # noqa: E402
from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao  # noqa: E402
from modelos import Projeto  # noqa: E402

GABARITO = RAIZ / "gabarito" / "paginas"
COMMIT_ANTES = "044a7c1"
FONTE = ImageFont.truetype(r"C:/Windows/Fonts/segoeuib.ttf", 30)
FONTE_P = ImageFont.truetype(r"C:/Windows/Fonts/segoeui.ttf", 24)
MEDIDAS: dict = {}

# O retangulo da simulacao da conferencia 11 (q2), para comparar com ela.
ESCOLA_PEDACO = (0.375, 0.378, 0.997, 0.932)


def _filtro_antes():
    """aplicar_filtro_com_selecao de 044a7c1, num modulo a parte."""
    codigo = subprocess.run(["git", "show", f"{COMMIT_ANTES}:core/filtros.py"], cwd=RAIZ,
                            capture_output=True, check=True).stdout
    arquivo = TRABALHO / "filtros_antes.py"
    arquivo.write_bytes(codigo)
    spec = importlib.util.spec_from_file_location("filtros_antes", arquivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.aplicar_filtro_com_selecao


def _livro(pid: str):
    """(projeto analisado, a imagem preparada em Original, a marcacao da maquina)."""
    projeto = Projeto(caminho_entrada=str(GABARITO / f"{pid}.pdf"), nome=pid)
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto = pipeline.analisar_projeto(projeto)
    pagina = projeto.paginas_ativas[0]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        pagina.filtro = ORIGINAL
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    pagina.filtro = PRETO_E_BRANCO
    return projeto, img, pagina.obter_selecao()


def _caixa_da_gravura(img, selecao, folga=0.006):
    """O retangulo em volta da gravura que a maquina achou, com folga (o que o
    Kaique desenharia em volta da foto)."""
    a, l = img.shape[:2]
    m = selecao.mascara(a, l, GRAVURA)
    ys, xs = np.nonzero(m)
    return (max(0.0, xs.min() / l - folga), max(0.0, ys.min() / a - folga),
            min(1.0, xs.max() / l + folga), min(1.0, ys.max() / a + folga))


def _processar(projeto, saida: Path):
    """O botao "Confirmar e processar" e a pagina lida de volta do PDF."""
    projeto.caminho_saida = str(saida)
    t0 = time.perf_counter()
    pipeline.processar(projeto)
    segundos = time.perf_counter() - t0
    with __import__("fitz").open(str(saida)) as d:
        imagem = d[0].get_images(full=True)[0]
        import fitz
        pix = fitz.Pixmap(d, imagem[0])
        um_bit = pix.n == 1 and pix.colorspace is not None and pix.colorspace.n == 1 \
            and len(np.unique(np.frombuffer(pix.samples, np.uint8))) <= 2
        del pix
    return paginas_do_pdf(saida, projeto.qualidade_dpi)[0], segundos, um_bit


def _pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def _com_rotulo(p, rotulo, sub=""):
    faixa = 46 + (32 if sub else 0)
    tela = Image.new("RGB", (p.width, p.height + faixa), (255, 255, 255))
    d = ImageDraw.Draw(tela)
    d.text((8, 6), rotulo, font=FONTE, fill=(0, 0, 0))
    if sub:
        d.text((8, 44), sub, font=FONTE_P, fill=(70, 70, 70))
    tela.paste(p, (0, faixa))
    return tela


def painel(imagens, rotulos, subs, altura):
    partes = []
    for img, rot, sub in zip(imagens, rotulos, subs):
        p = _pil(img)
        p = p.resize((max(1, round(p.width * altura / p.height)), altura), Image.LANCZOS)
        partes.append(_com_rotulo(p, rot, sub))
    folga = 12
    tela = Image.new("RGB", (sum(p.width for p in partes) + folga * (len(partes) - 1),
                             max(p.height for p in partes)), (170, 170, 170))
    x = 0
    for p in partes:
        tela.paste(p, (x, 0))
        x += p.width + folga
    return tela


def gravar(img: Image.Image, nome: str, largura_max=1800):
    if img.width > largura_max:
        img = img.resize((largura_max, round(img.height * largura_max / img.width)), Image.LANCZOS)
    img.convert("RGB").save(AQUI / nome, quality=88, optimize=True)
    print("gravado", nome, img.size, flush=True)


def _recorte(img, caixa):
    a, l = img.shape[:2]
    x0, y0, x1, y1 = caixa
    return img[int(y0 * a):int(y1 * a), int(x0 * l):int(x1 * l)]


def _contorno(img, caixa):
    out = img.copy()
    a, l = out.shape[:2]
    g = max(4, l // 300)
    x0, y0, x1, y1 = caixa
    cv2.rectangle(out, (int(x0 * l) - g, int(y0 * a) - g), (int(x1 * l) + g, int(y1 * a) + g),
                  (0, 110, 255), g)
    return out


def uma_pagina(pid: str, nome: str, pedaco=None, detalhes=()):
    projeto, img, selecao = _livro(pid)
    if pedaco is None:
        pedaco = _caixa_da_gravura(img, selecao)
    selecao.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[pedaco[:2], pedaco[2:]],
                               origem=MAO, filtro=ORIGINAL))
    projeto.paginas_ativas[0].guardar_selecao(selecao)

    # depois, antes, depois de novo (o tempo do primeiro carrega o que faltar)
    de_hoje = pipeline.aplicar_filtro_com_selecao
    depois, t_dep, um_bit_dep = _processar(projeto, TRABALHO / f"{pid}-depois.pdf")
    pipeline.aplicar_filtro_com_selecao = FILTRO_ANTES
    try:
        antes, t_ant, um_bit_ant = _processar(projeto, TRABALHO / f"{pid}-antes.pdf")
        _a2, t_ant2, _ = _processar(projeto, TRABALHO / f"{pid}-antes2.pdf")
    finally:
        pipeline.aplicar_filtro_com_selecao = de_hoje
    _d2, t_dep2, _ = _processar(projeto, TRABALHO / f"{pid}-depois2.pdf")

    # quanto do pedaco saiu exatamente como o original (fora a margem)
    a, l = img.shape[:2]
    x0, y0, x1, y1 = (int(pedaco[0] * l), int(pedaco[1] * a), int(pedaco[2] * l), int(pedaco[3] * a))
    igual_dep = float(np.all(depois[y0:y1, x0:x1] == img[y0:y1, x0:x1], axis=-1).mean()) \
        if depois.shape == img.shape else None
    igual_ant = float(np.all(antes[y0:y1, x0:x1] == img[y0:y1, x0:x1], axis=-1).mean()) \
        if antes.shape == img.shape else None
    fora = np.ones((a, l), bool)
    fora[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2] = False
    MEDIDAS[pid] = {
        "pedaco": pedaco,
        "processar_s": {"antes": [round(t_ant, 2), round(t_ant2, 2)],
                        "depois": [round(t_dep, 2), round(t_dep2, 2)]},
        "pagina_em_1_bit": {"antes": um_bit_ant, "depois": um_bit_dep},
        "fracao_do_pedaco_igual_ao_original": {"antes": igual_ant, "depois": igual_dep},
        "fora_do_pedaco_pontos_diferentes": int(np.any(antes[fora] != depois[fora], axis=-1).sum())
        if antes.shape == depois.shape else "tamanhos diferentes",
    }
    print(pid, json.dumps(MEDIDAS[pid]), flush=True)
    for nome_png, figura in (("original", img), ("antes", antes), ("depois", depois)):
        cv2.imwrite(str(TRABALHO / f"{pid}-{nome_png}.png"), figura)

    rot = ["Original", "Preto e branco: ANTES", "Preto e branco: DEPOIS"]
    subs = ["laranja: o pedaço marcado em Original", "o pedaço é ignorado",
            "o pedaço sai em Original"]
    gravar(painel([_contorno(img, pedaco), antes, depois], rot, subs, 1100), f"{nome}-pagina.jpg")
    caixa = (max(0, pedaco[0] - 0.02), max(0, pedaco[1] - 0.02),
             min(1, pedaco[2] + 0.02), min(1, pedaco[3] + 0.02))
    gravar(painel([_recorte(x, caixa) for x in (img, antes, depois)], rot, subs, 900),
           f"{nome}-pedaco.jpg", largura_max=2200)
    for i, (det, texto) in enumerate(detalhes):
        gravar(painel([_recorte(x, det) for x in (img, antes, depois)], rot,
                      [texto] * 3, 700), f"{nome}-detalhe{i + 1}.jpg", largura_max=2200)


if __name__ == "__main__":
    FILTRO_ANTES = _filtro_antes()
    try:
        uma_pagina("escola_p007", "escola7", ESCOLA_PEDACO, detalhes=[
            ((0.38, 0.38, 0.70, 0.55), "o céu e as nuvens (tamanho quase real)"),
            ((0.50, 0.80, 0.80, 0.94), "o leão e o pé da pintura"),
            ((0.86, 0.34, 1.00, 0.46), "a beirada do pedaço, em cima à direita"),
        ])
        uma_pagina("opusmajus_p020", "opus20", detalhes=[
            ((0.15, 0.08, 0.75, 0.40), "o rosto e o peito da estátua"),
            ((0.40, 0.60, 1.00, 0.97), "a parede clara e o pé da foto"),
        ])
    finally:
        (AQUI / "medidas.json").write_text(json.dumps(MEDIDAS, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
        print("imagens em tamanho cheio (apagadas no fim):", TRABALHO)
        if os.environ.get("GUARDAR_TRABALHO") != "1":
            shutil.rmtree(TRABALHO, ignore_errors=True)
