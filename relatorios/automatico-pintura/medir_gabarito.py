"""D-585: antes/depois do Preto e branco nas páginas-gabarito, pelo caminho inteiro.

Cada página vira um LIVRO NOVO de uma página (a página-gabarito, ou a página do acervo),
passa pelo Automático de sempre (endireitar, cortar, "Limpar a folha" em Preto e branco,
"Gravuras e fotos" na forma de fábrica, SEM "Só as letras") e sai pelo mesmo corpo do
"Confirmar e processar" (core.pipeline._pagina_pronta), no tamanho do PDF. CLAUDE.md §4.10.

Também anota, para cada gravura marcada, como o Preto e branco a classificou e por quê
(espessura, traço, traço mediano por pedaço, cor larga): é a medida da causa da D-585.

Uso (da raiz da worktree):
    python relatorios/automatico-pintura/medir_gabarito.py --saida _tmp/medida-antes [alvo ...]
    alvo = id do gabarito (ex.: horas_p011), livro:pagina do acervo (ex.: horas:15), "escola-capa" (página 1 do acervo, livro novo)
    ou "escola-capa-do-samuel" (a capa do projeto dele, cópia em _tmp/dados). Sem alvo: todos.
Grava <saida>/<alvo>.png (a página pronta) e <saida>/zonas.json.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))
_DADOS = RAIZ / "_tmp" / "dados-medida"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)
os.environ["TEMP"] = os.environ["TMP"] = str(RAIZ / "_tmp" / "temp")

import cv2  # noqa: E402
import numpy as np  # noqa: E402

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
ESCOLA = ACERVO / "Na escola de Jesus - Catecismo explicado com imagens..pdf"
PROJETO_DELE = (RAIZ / "_tmp/dados/EditorImpressao/projetos/"
                "Na escola de Jesus - Catecismo explicado com imagens/projeto.json")
LIVROS = {"escola": ESCOLA.name, "horas": "Livro de Horas - Luís XIV.pdf",
          "graduale": "Graduale - Saeculum XIV.pdf", "palatino": "Giovambattista Palatino cittadino romano.pdf",
          "marial": "Marial de sermoens - Frei Balthasar Paez. (1).pdf",
          "opus": "Opus Majus.pdf"}
# O Automático de sempre (a receita da D-018), com o Preto e branco escolhido
CAMPOS = {"endireitar": True, "cortar_bordas": True, "limpar": True, "detectar_regioes": True,
          "gravura_forma": "livre", "filtro_padrao": "preto_e_branco", "misto_so_as_letras": False,
          "pb_decoracao_em_preto_e_branco": False}

ZONAS: list[dict] = []


def _espiar() -> None:
    """Anota cada pergunta "é foto ou pintura?" e "é enfeite colorido?" do filtro."""
    from core import filtros as F

    original_foto = F._e_foto_ou_pintura
    original_deco = F._e_decoracao_colorida

    def foto(img3, zona, caixa, menor_lado):
        x, y, w, h = caixa
        dist = cv2.distanceTransform(np.pad(zona.astype(np.uint8), 1), cv2.DIST_L2, 5)
        lab = cv2.cvtColor(img3[y:y + h, x:x + w], cv2.COLOR_BGR2LAB)
        luz, fundo, nivel = F._fundo_e_nivel(lab)
        traco = F._peso_de_traco(luz, fundo, nivel) >= 128
        resposta = original_foto(img3, zona, caixa, menor_lado)
        ZONAS.append({"alvo": ALVO, "area": round(float(zona.sum()) / (img3.shape[0] * img3.shape[1]), 4),
                      "espessura": round(2 * float(dist.max()) / menor_lado, 3),
                      "traco": round(float(traco.mean()), 4), "foto": bool(resposta)})
        return resposta

    def deco(img3, zona, caixa, menor_lado, referencia):
        resposta = original_deco(img3, zona, caixa, menor_lado, referencia)
        # a mesma conta de _e_decoracao_colorida: a fracao da zona que e cor larga
        x, y, w, h = caixa
        fator = 1.0 / F.DECORACAO_REDUCAO
        tamanho = (max(1, round(w * fator)), max(1, round(h * fator)))
        pequeno = cv2.resize(img3[y:y + h, x:x + w], tamanho, interpolation=cv2.INTER_AREA)
        lab = cv2.cvtColor(pequeno, cv2.COLOR_BGR2LAB).astype(np.float32)
        _n, a_papel, b_papel, _r = referencia
        dist = np.hypot(lab[:, :, 1] - 128.0 - a_papel, lab[:, :, 2] - 128.0 - b_papel)
        colorido = (dist > F.DECORACAO_CROMA).astype(np.uint8)
        lado = max(3, int(round(menor_lado * F.DESENHO_FECHAMENTO * fator)) | 1)
        largo = cv2.morphologyEx(colorido, cv2.MORPH_OPEN,
                                 cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (lado, lado)))
        dentro = cv2.resize(zona.astype(np.uint8), tamanho, interpolation=cv2.INTER_NEAREST) > 0
        ZONAS.append({"alvo": ALVO, "area": round(float(zona.sum()) / (img3.shape[0] * img3.shape[1]), 4),
                      "decoracao": bool(resposta),
                      "cor_larga": round(float(largo[dentro].mean()) if dentro.any() else 0.0, 3)})
        return resposta

    F._e_foto_ou_pintura = foto
    F._e_decoracao_colorida = deco


def _livro_de_uma_pagina(pdf: Path, numero: int, nome: str):
    import fitz

    from core.pipeline import analisar_projeto
    from modelos import Projeto

    pasta = _DADOS / "paginas"
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"{nome}.pdf"
    if not destino.is_file():
        with fitz.open(str(pdf)) as doc:
            um = fitz.open()
            um.insert_pdf(doc, from_page=numero - 1, to_page=numero - 1)
            um.save(str(destino))
            um.close()
    projeto = Projeto(caminho_entrada=str(destino), caminho_saida=str(pasta / "saida.pdf"), nome=nome)
    for chave, valor in CAMPOS.items():
        setattr(projeto, chave, valor)
    projeto = analisar_projeto(projeto)
    for pagina in projeto.paginas:
        pagina.filtro = "preto_e_branco"
    return projeto, projeto.paginas[0]


def carregar(alvo: str):
    from modelos import Projeto

    if alvo == "escola-capa":
        return _livro_de_uma_pagina(ESCOLA, 1, "escola_capa")
    if ":" in alvo:                          # livro:pagina do acervo (ex.: horas:15)
        livro, numero = alvo.split(":")
        return _livro_de_uma_pagina(ACERVO / LIVROS[livro], int(numero), f"{livro}_p{int(numero):03d}")
    if alvo == "escola-capa-do-samuel":
        projeto = Projeto.de_dicionario(json.loads(PROJETO_DELE.read_text(encoding="utf-8")))
        projeto.filtro_padrao = "preto_e_branco"
        projeto.misto_so_as_letras = False
        pagina = projeto.paginas[0]
        pagina.filtro = "preto_e_branco"
        return projeto, pagina
    item = json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))["paginas"][alvo]
    return _livro_de_uma_pagina(RAIZ / "gabarito" / item["pdf"], 1, alvo)


def pronta(projeto, pagina):
    from core import pipeline
    from core.pdf_io import abrir_pdf

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        folha = projeto.folhas[pagina.folha]
        img, _mono = pipeline._pagina_pronta(projeto, doc, folha, pagina, pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    return img


ALVO = ""


def main() -> None:
    global ALVO
    ap = argparse.ArgumentParser()
    ap.add_argument("--saida", required=True)
    ap.add_argument("alvos", nargs="*")
    a = ap.parse_args()
    saida = Path(a.saida)
    saida.mkdir(parents=True, exist_ok=True)
    alvos = a.alvos or (list(json.loads((RAIZ / "gabarito" / "lista.json").read_text(encoding="utf-8"))
                             ["paginas"]) + ["escola-capa", "escola-capa-do-samuel"])
    _espiar()
    for alvo in alvos:
        ALVO = alvo
        t0 = time.monotonic()
        try:
            projeto, pagina = carregar(alvo)
            img = pronta(projeto, copy.deepcopy(pagina) if alvo != "escola-capa-do-samuel" else pagina)
        except Exception as erro:  # noqa: BLE001 - anota e segue
            print(f"{alvo}: ERRO {erro!r}", flush=True)
            continue
        cv2.imwrite(str(saida / f"{alvo.replace(':', '_p')}.png"), img)
        minhas = [z for z in ZONAS if z["alvo"] == alvo]
        print(f"{alvo}: {img.shape[1]}x{img.shape[0]} {'cor' if img.ndim == 3 else 'cinza/1bit'} "
              f"{time.monotonic() - t0:.1f}s zonas={minhas}", flush=True)
        (saida / "zonas.json").write_text(json.dumps(ZONAS, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
