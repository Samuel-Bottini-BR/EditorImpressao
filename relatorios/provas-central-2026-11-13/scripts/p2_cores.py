"""Print 2 (dv-211-215; D-189, D-191): Preto e branco + "Letras com a cor delas" + "Reduzir cores".

Livro de Horas, página 26 (cópia: páginas 25 a 27 do PDF; a 26 é a 2ª). O MESMO caminho nos dois
programas: abre como livro novo (ajustes de fábrica), vai à página 26, painel Filtro: "Preto e
branco", e em "Mais ajustes" marca "Letras com a cor delas" e "Reduzir cores". Print da janela e
a página como sai no PDF (core.pipeline.processar, o que o "Confirmar e processar" grava).

    python p2_cores.py <raiz do programa> <nome: antes|hoje>
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import comum  # noqa: E402

RAIZ, NOME = sys.argv[1], sys.argv[2]
CRU = AQUI / "cru" / "p2" / NOME
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", valor, flush=True)


def subconjunto() -> Path:
    import fitz

    destino = AQUI / "livros" / f"horas_paginas_25a27_{NOME}.pdf"
    with fitz.open(str(AQUI / "livros" / "horas.pdf")) as origem, fitz.open() as novo:
        novo.insert_pdf(origem, from_page=24, to_page=26)
        novo.save(str(destino))
    return destino


def main():
    import faulthandler; faulthandler.dump_traceback_later(900, exit=True)
    comum.preparar(RAIZ, f"p2-{NOME}")
    import subprocess
    nota("commit", subprocess.run(["git", "-C", RAIZ, "log", "--oneline", "-1"], capture_output=True,
                                  text=True).stdout.strip())
    from core import filtros as F
    from core.pipeline import processar
    import fitz

    pdf = subconjunto()
    j = comum.nova_janela()
    j.abrir_livro(str(pdf))
    # programa de antes (27/10): depois de abrir vinha a tela "O que fazer"; o Kaique clicava
    # "Conferir" com as escolhas de fábrica
    comum.esperar(5.0)
    opcoes = getattr(j, "tela_opcoes", None)
    if opcoes is not None and j.telas.currentWidget() is opcoes:
        comum.foto(j, CRU / "tela-o-que-fazer.png")
        opcoes.botao_conferir.click()
        nota("clicou Conferir na tela O que fazer", True)
    nota("abrir (s)", comum.esperar_tela(j))
    tela, projeto = j.tela_conferir, j.projeto
    nota("paginas", len(projeto.paginas_ativas))
    tela.ir_para_pagina(1)
    comum.esperar(1.0)
    tela.paineis.abrir("filtro")             # o ícone do painel "Filtro da página"
    comum.esperar(1.0)
    tela._escolher_filtro(F.PRETO_E_BRANCO)
    comum.esperar(1.0)
    from ui.widgets.paineis import ParteQueAbre
    partes = {p.nome: p for p in tela.findChildren(ParteQueAbre)}
    nota("partes do painel", sorted(partes))
    for nome, parte in partes.items():
        if nome in ("Mais ajustes",):
            parte.abrir(True)
        elif nome in ("Só as letras",):
            parte.abrir(False)                   # fechada para as caixinhas caberem na tela
    comum.esperar(1.0)
    tela.caixa_letras_com_a_cor.setChecked(True)
    comum.esperar(0.5)
    tela.caixa_reduzir_cores.setChecked(True)
    comum.esperar(1.0)
    pagina = projeto.paginas_ativas[1]
    nota("filtro", pagina.filtro)
    nota("letras_com_a_cor", pagina.letras_com_a_cor)
    nota("reduzir_cores", pagina.reduzir_cores)
    nota("caixinhas visiveis", [tela.caixa_letras_com_a_cor.isVisible(), tela.caixa_reduzir_cores.isVisible()])
    comum.esperar(5.0)
    comum.ate(lambda: tela.previas.ja_pronta(1, tela._dpi_atual) is not None, 300)
    comum.esperar(5.0)
    comum.foto(j, CRU / "janela.png")
    # a parte "Mais ajustes" rolada até as caixinhas, se o painel rolar
    try:
        from PySide6.QtWidgets import QScrollArea
        caixa = tela.caixa_reduzir_cores
        w = caixa.parentWidget()
        while w is not None and not isinstance(w, QScrollArea):
            w = w.parentWidget()
        if w is not None:
            w.ensureWidgetVisible(caixa, 50, 120)
            comum.esperar(1.0)
            comum.foto(j, CRU / "janela-caixinhas.png")
            nota("painel rolado", True)
    except Exception as erro:
        nota("rolar", repr(erro))
    # o PDF
    p = copy.copy(projeto)
    p.caminho_saida = str(CRU / "saida.pdf")
    saida = processar(p)
    with fitz.open(str(saida)) as d:
        nota("paginas no pdf", len(d))
        d[1].get_pixmap(dpi=300).save(str(CRU / "pdf-p26-300dpi.png"))
    (CRU / "notas.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")
    comum.fechar(j)


if __name__ == "__main__":
    main()
