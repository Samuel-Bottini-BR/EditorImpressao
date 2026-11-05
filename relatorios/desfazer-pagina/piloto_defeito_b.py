"""Defeito B do verificador (05/11/2026) na janela de VERDADE: a página posta em branco aparece
branca em todas as ferramentas e a faixa diz o que sai, também depois do "voltar a página".

Relatório do verificador (relatorios/verificacao-04-11/relatorio.md, §5): "A página posta em
branco, no Cortar, mostra a imagem da página vizinha [...] Se o Kaique apertar "voltar a página",
[...] a faixa diz "Esta página vai sair em Original" — mas o PDF continua saindo branco."

Mesmo jeito do piloto_d623.py (janela fora da tela, botão direito, cliques e teclas por mensagens
do Windows ao hwnd, prints por PrintWindow), no Gradus (cópia). No fim grava o PDF das 6 primeiras
páginas (as outras tiradas numa CÓPIA do projeto, só para o PDF sair rápido) e mede a tinta de
cada página do PDF.

Rodar (na cópia desfazer-pagina):
    D:\programas\EditorImpressao\.venv\Scripts\python.exe relatorios\desfazer-pagina\piloto_defeito_b.py
"""
from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import piloto_d623 as P  # noqa: E402

base = P.base
P.SCRATCH = Path(r"C:\Users\fotog\AppData\Local\Temp\claude\195a7ef9582f81cd"
                 r"\e4fd3df2-ffc2-4ff8-9d6b-c5c2f4b2d0ca\scratchpad\piloto-defeito-b")
P.PRINTS = AQUI / "prints-defeito-b"
P.LOG = open(AQUI / "anotacoes-defeito-b.txt", "w", encoding="utf-8")
anotar, p = P.anotar, P.p


def escura(img) -> float:
    import numpy as np
    a = np.asarray(img)
    cinza = a.mean(axis=2) if a.ndim == 3 else a
    return round(float((cinza < 200).mean()), 4)


def na_tela(j):
    """A imagem que o visualizador da ferramenta da vez mostra, e a frase da faixa."""
    import numpy as np
    from PySide6.QtGui import QImage
    t = j.tela_conferir
    vis = t.visualizadores.get(t.aba_atual)
    out = {"ferramenta": t.aba_atual, "pagina": t.indice_pagina + 1, "faixa": t.texto_faixa.text()}
    if vis is not None and vis._pixmap is not None:
        img = vis._pixmap.toImage().convertToFormat(QImage.Format_RGB32)
        a = np.frombuffer(img.constBits(), np.uint8).reshape(img.height(), img.bytesPerLine() // 4, 4)
        out["tinta_na_tela"] = escura(a[:, :img.width(), :3])
    if t.aba_atual == "filtro":
        out["cartoes"] = {k: (None if c.ultima_amostra is None else escura(c.ultima_amostra))
                          for k, c in t.cartoes.items()}
    out["botao_da_pagina"] = t.botao_em_branco.text()
    return out


def ferramenta(j, nome):
    j.tela_conferir.escolher_ferramenta(nome)
    P.esperar_previa(j)
    base.esperar(2.5)


def main():
    base.preparar(str(P.RAIZ), str(P.SCRATCH), limpar=True)
    from ui.tela_conferir import UMA
    from ui.widgets.tira_miniaturas import Miniatura
    import projetos
    pasta = P.preparar_copia()
    resumo_do_livro = projetos.ler_resumo(pasta)
    j = base.nova_janela(P.LARGURA, P.ALTURA)
    j.abrir_livro(resumo_do_livro.caminho_entrada, resumo=resumo_do_livro)
    anotar("abriu-em-s", P.esperar_tela(j))
    t = j.tela_conferir
    base.clique(j, t.botoes_mostrar[UMA]); base.esperar(1.0)
    ferramenta(j, "cortar")
    P.ir_pagina(j, 2)
    anotar("página 2 no Cortar (a vizinha)", na_tela(j))
    p(j, "pagina-2-no-cortar")

    # botão direito na miniatura 2 -> "adicionar página em branco depois"
    mini = next(m for m in t.tira.findChildren(Miniatura) if m.numero == 2)
    P.botao_direito(j, mini)
    P.clicar_no_item(t._menu_desfazer, "adicionar página em branco depois")
    P.esperar_previa(j)
    anotar("depois de adicionar", P.resumo(j))

    P.ir_pagina(j, 3)
    for nome in ("cortar", "endireitar", "mover", "filtros"):
        ferramenta(j, nome)
        anotar(f"página 3 posta, {nome}", na_tela(j))
        p(j, f"posta-{nome}")

    # "voltar a página" (o botão de "Esta página", no Cortar), clicado
    ferramenta(j, "cortar")
    base.clique(j, t.botao_em_branco); base.esperar(2.0)
    P.esperar_previa(j); base.esperar(2.0)
    anotar("em_branco depois do voltar", j.projeto.paginas[2].em_branco)
    for nome in ("cortar", "filtros"):
        ferramenta(j, nome)
        anotar(f"página 3 depois do voltar, {nome}", na_tela(j))
        p(j, f"voltar-{nome}")
    ferramenta(j, "dividir")
    anotar("página 3, dividir (ferramenta das folhas)", na_tela(j))
    p(j, "dividir")

    # o PDF: as 6 primeiras páginas (numa CÓPIA do projeto, as outras tiradas)
    from core.pdf_io import abrir_pdf, pagina_para_array
    from core.pipeline import processar
    projeto = copy.deepcopy(j.projeto)
    for pg in projeto.paginas[6:]:
        pg.apagada = True
    projeto.montar_cadernos = False
    projeto.caminho_saida = str(base.TRAB / "seis-paginas.pdf")
    t0 = time.time()
    saida = processar(projeto)
    doc = abrir_pdf(saida)
    try:
        tinta = [escura(pagina_para_array(doc, n, dpi=60)) for n in range(doc.page_count)]
    finally:
        doc.close()
    anotar("PDF das 6 primeiras (tinta de cada página)", {"segundos": round(time.time() - t0, 1),
                                                          "tinta": tinta})
    anotar("fim", P.resumo(j))
    base.fechar(j)


if __name__ == "__main__":
    main()
