r"""Antes | depois do conserto do "so neste pedaco" numa pagina em Original
(conferencia 13, S4, Samuel: "Sim, do mesmo jeito"; 05/10/2026).

A Escola de Jesus 7 com a PAGINA em Original e um retangulo "letra e traco"
em volta do bloco de texto de cima, com "so neste pedaco: Preto e branco"
(Regiao com origem MAO e filtro PRETO_E_BRANCO, como a aba Marcar grava). O
livro e PROCESSADO de verdade (core.pipeline.processar, o botao "Confirmar e
processar") e a pagina e lida de volta do PDF gravado:

    ANTES  = o filtro de 19c1ba7 (core/filtros.py daquele commit, lido com
             git show e posto no lugar de aplicar_filtro_com_selecao do
             pipeline; o resto do codigo e o de hoje);
    DEPOIS = o codigo deste ramo.

Copia adaptada de relatorios/conferir/so-neste-pedaco-2026-10-05/scripts/
gerar_antes_depois.py.

Uso: .venv\Scripts\python.exe relatorios\conferir\pedaco-em-original-2026-10-05\scripts\gerar_antes_depois.py
Grava os .jpg e medidas.json em relatorios\conferir\pedaco-em-original-2026-10-05\.
LOCALAPPDATA descartavel (fora da pasta real do Samuel).
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
TRABALHO = Path(tempfile.mkdtemp(prefix="pedaco_em_original_"))
os.environ["LOCALAPPDATA"] = str(TRABALHO / "localappdata")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import fitz  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from conferencia import paginas_do_pdf  # noqa: E402
from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.selecao import LETRA, MAO, RETANGULO, Regiao  # noqa: E402
from modelos import Projeto  # noqa: E402

GABARITO = RAIZ / "gabarito" / "paginas"
COMMIT_ANTES = "19c1ba7"
FONTE = ImageFont.truetype(r"C:/Windows/Fonts/segoeuib.ttf", 30)
FONTE_P = ImageFont.truetype(r"C:/Windows/Fonts/segoeui.ttf", 24)
MEDIDAS: dict = {}

# O bloco de texto de cima da Escola 7 (titulo ate "E Deus disse"), com folga.
ESCOLA_PEDACO = (0.005, 0.07, 0.995, 0.365)


def _filtro_antes():
    """aplicar_filtro_com_selecao de 19c1ba7, num modulo a parte."""
    codigo = subprocess.run(["git", "show", f"{COMMIT_ANTES}:core/filtros.py"], cwd=RAIZ,
                            capture_output=True, check=True).stdout
    arquivo = TRABALHO / "filtros_antes.py"
    arquivo.write_bytes(codigo)
    spec = importlib.util.spec_from_file_location("filtros_antes", arquivo)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.aplicar_filtro_com_selecao


def _livro(pid: str):
    """(projeto analisado com a pagina em Original, a imagem preparada, a
    marcacao da maquina)."""
    projeto = Projeto(caminho_entrada=str(GABARITO / f"{pid}.pdf"), nome=pid)
    projeto.filtro_padrao = ORIGINAL
    projeto = pipeline.analisar_projeto(projeto)
    pagina = projeto.paginas_ativas[0]
    pagina.filtro = ORIGINAL
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    return projeto, img, pagina.obter_selecao()


def _processar(projeto, saida: Path):
    """O botao "Confirmar e processar" e a pagina lida de volta do PDF."""
    projeto.caminho_saida = str(saida)
    t0 = time.perf_counter()
    pipeline.processar(projeto)
    segundos = time.perf_counter() - t0
    tamanho = saida.stat().st_size
    return paginas_do_pdf(saida, projeto.qualidade_dpi)[0], segundos, tamanho


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
    cv2.rectangle(out, (int(x0 * l), int(y0 * a)), (int(x1 * l), int(y1 * a)),
                  (0, 110, 255), g)
    return out


def uma_pagina(pid: str, nome: str, pedaco, detalhes=()):
    projeto, img, selecao = _livro(pid)
    selecao.acrescentar(Regiao(tipo=LETRA, forma=RETANGULO, pontos=[pedaco[:2], pedaco[2:]],
                               origem=MAO, filtro=PRETO_E_BRANCO))
    projeto.paginas_ativas[0].guardar_selecao(selecao)

    # depois, antes, antes de novo, depois de novo (o primeiro carrega o que faltar)
    de_hoje = pipeline.aplicar_filtro_com_selecao
    depois, t_dep, kb_dep = _processar(projeto, TRABALHO / f"{pid}-depois.pdf")
    pipeline.aplicar_filtro_com_selecao = FILTRO_ANTES
    try:
        antes, t_ant, kb_ant = _processar(projeto, TRABALHO / f"{pid}-antes.pdf")
        _a2, t_ant2, _ = _processar(projeto, TRABALHO / f"{pid}-antes2.pdf")
    finally:
        pipeline.aplicar_filtro_com_selecao = de_hoje
    _d2, t_dep2, _ = _processar(projeto, TRABALHO / f"{pid}-depois2.pdf")

    a, l = img.shape[:2]
    x0, y0, x1, y1 = (int(pedaco[0] * l), int(pedaco[1] * a), int(pedaco[2] * l), int(pedaco[3] * a))
    fora = np.ones((a, l), bool)
    fora[max(0, y0 - 2):y1 + 2, max(0, x0 - 2):x1 + 2] = False
    dentro_dep = depois[y0 + 2:y1 - 2, x0 + 2:x1 - 2]
    MEDIDAS[pid] = {
        "pedaco": pedaco,
        "processar_s": {"antes": [round(t_ant, 2), round(t_ant2, 2)],
                        "depois": [round(t_dep, 2), round(t_dep2, 2)]},
        "tamanho_do_pdf_bytes": {"antes": kb_ant, "depois": kb_dep},
        "antes_igual_ao_original_em_tudo": bool(antes.shape == img.shape
                                                and np.array_equal(antes, img)),
        "depois_dentro_do_pedaco_cores_distintas": int(len(np.unique(
            dentro_dep.reshape(-1, dentro_dep.shape[-1]), axis=0))),
        "depois_fora_do_pedaco_pontos_diferentes_do_original": int(
            np.any(depois[fora] != img[fora], axis=-1).sum())
        if depois.shape == img.shape else "tamanhos diferentes",
    }
    print(pid, json.dumps(MEDIDAS[pid]), flush=True)
    if os.environ.get("GUARDAR_TRABALHO") == "1":
        for nome_png, figura in (("original", img), ("antes", antes), ("depois", depois)):
            cv2.imwrite(str(TRABALHO / f"{pid}-{nome_png}.png"), figura)

    rot = ["Original", "ANTES (19c1ba7)", "DEPOIS"]
    subs = ["laranja: o pedaço marcado em Preto e branco", "o pedaço é ignorado",
            "o pedaço sai em Preto e branco"]
    gravar(painel([_contorno(img, pedaco), antes, depois], rot, subs, 1100), f"{nome}-pagina.jpg")
    caixa = (max(0, pedaco[0] - 0.005), max(0, pedaco[1] - 0.02),
             min(1, pedaco[2] + 0.005), min(1, pedaco[3] + 0.06))
    gravar(painel([_recorte(x, caixa) for x in (img, antes, depois)], rot, subs, 700),
           f"{nome}-pedaco.jpg", largura_max=2400)
    for i, (det, texto) in enumerate(detalhes):
        gravar(painel([_recorte(x, det) for x in (img, antes, depois)], rot,
                      [texto] * 3, 700), f"{nome}-detalhe{i + 1}.jpg", largura_max=2400)


if __name__ == "__main__":
    FILTRO_ANTES = _filtro_antes()
    try:
        uma_pagina("escola_p007", "escola7", ESCOLA_PEDACO, detalhes=[
            ((0.0, 0.06, 0.5, 0.26), "o título e as primeiras linhas (perto do tamanho real)"),
            ((0.0, 0.30, 0.6, 0.48), "a beirada de baixo do pedaço: Preto e branco em cima, Original embaixo"),
        ])
    finally:
        (AQUI / "medidas.json").write_text(json.dumps(MEDIDAS, ensure_ascii=False, indent=1),
                                           encoding="utf-8")
        print("imagens em tamanho cheio:", TRABALHO)
        if os.environ.get("GUARDAR_TRABALHO") != "1":
            shutil.rmtree(TRABALHO, ignore_errors=True)
