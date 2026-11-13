"""Quadrados na capa (Samuel, 13/11/2026, prints 13-01 e 13-02): desenha UMA pagina como o
programa a desenha, com UMA versao do programa (a pasta de uma copia do git), sem janela e sem
mudar nada do programa. So investigacao.

    python rodar_capa.py <raiz da versao> <livro.pdf> <pagina 1-based> <saida> <variante> [...]

Cada variante grava, na pasta <saida>/<variante>/:
  previa.png   a previa da tela (core.pipeline.renderizar_pagina, 110 pontos por polegada, o
               DPI_PREVIA da tela de conferir)
  cartao.png   o cartao do filtro / miniatura (renderizar_com_filtro, 70 pontos)
  pdf.png      a pagina como sai no PDF (core.pipeline._pagina_pronta, qualidade_dpi = 300)
  info.json    as regioes da marcacao (tipo, origem, caixa) e as escolhas
O livro e aberto como livro novo (core.automatico.livro_leve, como a tela abre desde a obra).

Variantes (nome = escolhas, separadas por "+"):
  pb | melhorar | magico | original | fundo   o filtro (fundo = "Tirar o fundo")
  resp0 / resp1     "Respeitar as gravuras achadas" desmarcada / marcada (de fabrica: marcada)
  cinza1            "Gravuras em tons de cinza" marcada
  letras1           "So as letras" ligado (Guardar a tinta forte, de fabrica)
  letras_tudo / letras_apagar   "So as letras" com "Guardar tudo" / "Guardar so o texto"
  samuel            a ORDEM do Samuel (acoes.jsonl dele): Preto e branco a mao com "Respeitar"
                    marcada (a gravura e procurada, D-659), depois "Respeitar" desmarcada.
                    Junto com letras1: o 13-02; sem: o 13-01.
  auto              pelo Automatico: "Limpar a folha" + "Gravuras e fotos" rodados na pagina
                    (core.automatico.rodar), com o filtro e as caixinhas da variante
  projeto=<json>    em vez do livro novo, o projeto.json do Samuel (COPIA), pagina como esta
  semtrocar         com "samuel": nao desmarca a "Respeitar" depois (fica so a ordem)
Ambiente: CONSERTO_C=1 instala nada (o conserto C ja esta no codigo do ramo dele: rode com a
raiz da worktree quadrados-c).
"""
from __future__ import annotations

import copy
import json
import os
import sys
import time
from pathlib import Path

RAIZ = Path(sys.argv[1]).resolve()
SAIDA = Path(sys.argv[4]).resolve()                 # antes do chdir abaixo
TRABALHO = Path(__file__).resolve().parents[1] / "_trabalho"
DADOS = TRABALHO / "dados" / RAIZ.name
(DADOS / "temp").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS)            # nada do Samuel e tocado
os.environ["TEMP"] = os.environ["TMP"] = str(DADOS / "temp")
os.environ["QT_QPA_PLATFORM"] = "offscreen"          # nunca abre janela
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:                                                  # prioridade baixa: o PC do Samuel trava facil
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import etapas, pipeline  # noqa: E402
from core.pdf_io import abrir_pdf, info_paginas  # noqa: E402
from modelos import Projeto  # noqa: E402

FILTROS = {"pb": "preto_e_branco", "melhorar": "melhorar", "magico": "magico_pro",
           "original": "original", "fundo": "tirar_fundo"}


def livro_novo(pdf: str) -> Projeto:
    from core import automatico
    projeto = Projeto(caminho_entrada=pdf, nome=Path(pdf).stem)
    doc = abrir_pdf(pdf)
    try:
        tamanhos = [(i.largura_pt, i.altura_pt) for i in info_paginas(doc)]
    finally:
        doc.close()
    automatico.livro_leve(projeto, tamanhos)
    return projeto


def projeto_do_samuel(caminho: str, pdf: str) -> Projeto:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    p = Projeto.de_dicionario(dados)
    p.caminho_entrada = pdf                         # a COPIA do livro
    return p


def regioes(pag) -> list:
    saida = []
    sel = pag.selecao or []
    for r in sel:
        if not isinstance(r, dict):
            continue
        pts = r.get("pontos") or []
        xs = [q[0] for q in pts] or [0]
        ys = [q[1] for q in pts] or [0]
        saida.append({"tipo": r.get("tipo"), "origem": r.get("origem"), "op": r.get("operacao"),
                      "caixa": [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3),
                                round(max(ys), 3)]})
    return saida


def desenhar(projeto, pag, doc, onde: Path) -> dict:
    tempos = {}
    t = time.monotonic()
    img, _ = pipeline.renderizar_pagina(doc, projeto, pag, dpi=110)
    tempos["previa"] = round(time.monotonic() - t, 1)
    cv2.imwrite(str(onde / "previa.png"), img)
    t = time.monotonic()
    img, _ = pipeline.renderizar_com_filtro(doc, projeto, pag, pag.filtro, dpi=70)
    tempos["cartao"] = round(time.monotonic() - t, 1)
    cv2.imwrite(str(onde / "cartao.png"), img)
    t = time.monotonic()
    folha = projeto.folhas[pag.folha]
    img, _ = pipeline._pagina_pronta(projeto, doc, folha, pag, pipeline._FolhaDaVez(), 0)
    tempos["pdf"] = round(time.monotonic() - t, 1)
    cv2.imwrite(str(onde / "pdf.png"), img)
    return tempos


def rodar_variante(base: Projeto, indice: int, nome: str, doc, saida: Path) -> None:
    partes = nome.split("+")
    curto = "+".join("projeto" if x.startswith("projeto=") else x for x in partes)
    onde = saida / curto
    onde.mkdir(parents=True, exist_ok=True)
    p = copy.deepcopy(base)
    pag = p.paginas[indice]
    filtro = next((FILTROS[x] for x in partes if x in FILTROS), None)
    do_samuel = any(x.startswith("projeto=") for x in partes)
    resp = False if "resp0" in partes else True if "resp1" in partes else (None if do_samuel else True)
    cinza = True if "cinza1" in partes else (None if do_samuel else False)
    letras = next((x for x in partes if x.startswith("letras")), None)
    if "auto" in partes:
        from core import automatico
        opcoes = {"filtro_padrao": filtro or "preto_e_branco",
                  "respeitar_gravuras_achadas": resp is not False,
                  "gravuras_em_tons_de_cinza": bool(cinza),
                  "misto_so_as_letras": bool(letras)}
        if letras in ("letras_tudo", "letras_apagar"):
            opcoes["misto_fora_do_texto"] = "tudo" if letras == "letras_tudo" else "apagar"
        pedido = automatico.Pedido(etapas=[automatico.LIMPAR, automatico.GRAVURAS],
                                   opcoes=opcoes, paginas=[indice], pular_mexidas=False)
        automatico.rodar(p, pedido)
        pag = p.paginas[indice]
    else:
        if filtro is not None:
            pag.filtro = filtro
            etapas.marcar_mexida_a_mao(pag, etapas.FILTRO)       # escolhido a mao no painel
        if "samuel" in partes:
            # a ordem dele: Preto e branco com "Respeitar" marcada (procura a gravura),
            # depois desmarcada
            pag.respeitar_gravuras_achadas = True
            pipeline.renderizar_pagina(doc, p, pag, dpi=110)       # a tela desenha: procura
            pipeline.acertar_no_tamanho_do_pdf(doc, p, pag)       # e acerta no tamanho do PDF
            if "semtrocar" not in partes:
                pag.respeitar_gravuras_achadas = resp
        elif resp is not None:
            pag.respeitar_gravuras_achadas = resp
        if cinza is not None:
            pag.gravuras_em_tons_de_cinza = cinza
        if letras:
            pag.misto_so_as_letras = True
            if letras == "letras_tudo":
                pag.misto_fora_do_texto = "tudo"
            elif letras == "letras_apagar":
                pag.misto_fora_do_texto = "apagar"
    tempos = desenhar(p, pag, doc, onde)
    info = {"variante": nome, "raiz": str(RAIZ), "filtro": pag.filtro,
            "respeitar": getattr(pag, "respeitar_gravuras_achadas", None),
            "cinza": getattr(pag, "gravuras_em_tons_de_cinza", None),
            "so_as_letras": getattr(pag, "misto_so_as_letras", None),
            "limpar_no_livro": bool(getattr(p, "limpar", False)),
            "tempos": tempos, "regioes": regioes(pag)}
    (onde / "info.json").write_text(json.dumps(info, indent=1, ensure_ascii=False), encoding="utf-8")
    print(nome, pag.filtro, tempos, len(info["regioes"]), "regioes", flush=True)


def provas_da_causa() -> None:
    """So para achar a causa (neste processo; o programa nao muda):
    SEM_SOMBRA=1  tira o passo "sem a sombra" inteiro do Preto e branco
                  (core.filtros._sem_a_sombra_da_lombada devolve a binaria como veio)
    SEM_QUADROS=1 tira so a parte dos quadradinhos (_sombra_em_quadros: a sombra da foto de
                  celular, conserto da Lista de bugs de 23/10/2026)
    SEM_FAIXA=1   tira so a parte da faixa da lombada (_faixa_da_sombra_da_lombada)"""
    from core import filtros as F
    if os.environ.get("SEM_SOMBRA") == "1":
        F._sem_a_sombra_da_lombada = lambda cinza, binaria: binaria
    if os.environ.get("SEM_QUADROS") == "1":
        F._sombra_em_quadros = lambda cinza: None
    if os.environ.get("SEM_FAIXA") == "1":
        F._faixa_da_sombra_da_lombada = lambda cinza: None
    if os.environ.get("SEM_PAPEL_ACHADO") == "1":
        # o filtro recebe a marcacao SEM as areas de "papel" que a maquina achou (so a prova)
        from core.selecao import MAO, PAPEL, Selecao
        antes = pipeline.marcacao_que_o_filtro_usa

        def sem_papel(projeto, pagina, selecao):
            sel = antes(projeto, pagina, selecao)
            if sel is None:
                return sel
            return Selecao(regioes=[r for r in sel.regioes if not (r.tipo == PAPEL and r.origem != MAO)])

        pipeline.marcacao_que_o_filtro_usa = sem_papel


def main() -> None:
    provas_da_causa()
    pdf, numero, saida = sys.argv[2], int(sys.argv[3]), SAIDA
    nomes = sys.argv[5:]
    saida.mkdir(parents=True, exist_ok=True)
    doc = abrir_pdf(pdf)
    try:
        bases = {}
        for nome in nomes:
            proj = next((x.split("=", 1)[1] for x in nome.split("+") if x.startswith("projeto=")), None)
            chave = proj or ""
            if chave not in bases:
                bases[chave] = projeto_do_samuel(proj, pdf) if proj else livro_novo(pdf)
            rodar_variante(bases[chave], numero - 1, nome, doc, saida)
    finally:
        doc.close()


if __name__ == "__main__":
    main()
