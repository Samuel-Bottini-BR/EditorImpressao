"""Piloto das perguntas do Dividir (au-d-501 e au-d-500), no "La vida eterna" (CÓPIA das 12 primeiras
folhas), na janela de verdade fora da tela, pelo caminho do Kaique do zero:

1. abre o livro (cópia) -> em que ferramenta ele abre;
2. vai ao Dividir (tecla D) -> a folha inteira, ainda sem dividir;
3. Automático: só "Dividir folhas ao meio", "Rodar" (estando no Dividir) -> para onde a tela vai;
4. o "Para revisar": as folhas 4 e 5 com "Lombada incerta"; "ver" -> vai ao Dividir;
   outro aviso -> vai à página;
5. a folha 4 no Dividir (a linha perto do meio) e onde o ScanTailor cortaria (0,10);
6. fecha, reabre o livro -> em que ferramenta reabre.

Rodar na worktree: D:\\programas\\EditorImpressao\\.venv\\Scripts\\python.exe <este arquivo>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comum as c  # noqa: E402
from comum import anotar, base  # noqa: E402


def estado(j):
    t = j.tela_conferir
    return {"aba": t.aba_atual, "folhas_na_tela": t.trabalha_com_folhas, "pagina": t.indice_pagina + 1,
            "folha": t.indice_folha + 1, "mostrar": getattr(t, "mostrar", None)}


def main():
    pasta = c.preparar("dividir")
    pdf = c.copia_da_vida(12)
    j = base.nova_janela(1280, 657)
    c.p(j, pasta, "00-tela-dos-livros")
    t = c.abrir(j, pdf)
    pr = j.projeto
    anotar("abriu", estado(j))
    anotar("folhas-paginas", [len(pr.folhas), len(pr.paginas)])
    c.p(j, pasta, "01-abriu")

    # 2. o Dividir (tecla D)
    c.letra(j, "d")
    c.esperar_previa(t)
    anotar("no-dividir", estado(j))
    c.p(j, pasta, "02-no-dividir-antes")

    # 3. Automático só com Dividir, rodando com a tela no Dividir
    painel = c.rodar_automatico(j, {"dividir"})
    c.p(j, pasta, "03-automatico-so-dividir")
    c.clicar_rodar(j, painel)
    t = j.tela_conferir
    pr = j.projeto
    c.esperar_previa(t)
    anotar("depois-do-automatico", estado(j))
    anotar("divididas", [(i + 1, f.dividir, round(f.posicao_corte, 3), round(f.confianca_corte, 2),
                          list(f.alertas)) for i, f in enumerate(pr.folhas)])
    c.p(j, pasta, "04-depois-do-automatico")

    # 4. o Para revisar
    t.paineis.abrir("revisar")
    base.esperar(1.0)
    c.p(j, pasta, "05-para-revisar")
    from core import analise
    from core import avisos as avisos_do_livro
    pend = avisos_do_livro.pendentes_do_livro(pr)
    anotar("avisos", [(a.alvo, a.indice + 1, a.codigo) for a in pend])
    lomb = next((a for a in pend if a.codigo == analise.LOMBADA_INCERTA), None)
    outro = next((a for a in pend if a.codigo != analise.LOMBADA_INCERTA
                  and a.codigo != analise.NAO_PARECE_DUPLA), None)
    # o clique num cartão do "Para revisar" (o que o sinal ir_para do cartão chama)
    t._ir_do_para_revisar(1)                       # cartão "Página 2 - Parece em branco"
    c.esperar_previa(t)
    anotar("cartao-pagina-2", estado(j))
    c.p(j, pasta, "06-cartao-pagina-2")
    t._ir_do_para_revisar(6)                       # cartão "Página 7 - Lombada incerta"
    c.esperar_previa(t)
    anotar("cartao-pagina-7", estado(j))
    c.p(j, pasta, "07-cartao-pagina-7")
    from ui.tela_conferir import DUAS
    base.clique(j, t.botoes_mostrar[DUAS])
    base.esperar(2.0)
    c.esperar_previa(t)
    anotar("folha-4-duas-lado-a-lado", {**estado(j), "linha": pr.folhas[3].posicao_corte})
    c.p(j, pasta, "07b-folha-4-duas-lado-a-lado")
    from ui.tela_conferir import UMA
    base.clique(j, t.botoes_mostrar[UMA])
    base.esperar(1.5)
    # o "ver" da lista dos avisos ("ver a lista..."), aviso a aviso
    if outro is not None:
        t._ir_para_o_aviso(outro)
        c.esperar_previa(t)
        anotar("ver-outro-aviso", {"aviso": [outro.alvo, outro.indice + 1, outro.codigo], **estado(j)})
    if lomb is not None:
        t._ir_para_o_aviso(lomb)
        c.esperar_previa(t)
        anotar("ver-lombada-incerta", {"aviso": [lomb.alvo, lomb.indice + 1, lomb.codigo], **estado(j)})

    # 5. a folha 4: a linha do programa e a do ScanTailor
    import numpy as np
    from core import dividir_scantailor as ds
    from core.pdf_io import abrir_pdf, pagina_para_array
    from core.pipeline import DPI_ANALISE, achar_divisao
    doc = abrir_pdf(str(pdf))
    linhas = {}
    try:
        for i in range(len(pr.folhas)):
            img = pagina_para_array(doc, i, dpi=DPI_ANALISE)
            st = ds.posicao_da_divisao(ds.achar(img, DPI_ANALISE, ds.MODO_AUTOMATICO))
            ed = achar_divisao(img, ds.JEITO_SCANTAILOR, DPI_ANALISE)
            linhas[i + 1] = {"scantailor": round(st, 3), "programa": round(ed.posicao, 3),
                             "confianca": round(ed.confianca, 2)}
            if i in (2, 3, 4, 5):
                from PIL import Image
                Image.fromarray(np.ascontiguousarray(img[:, :, ::-1])).save(pasta / f"folha-{i + 1}.png")
    finally:
        doc.close()
    anotar("linhas", linhas)
    (pasta / "linhas.json").write_text(json.dumps(linhas, indent=1), encoding="utf-8")

    # as páginas 7 e 8 (folha 4) como saem no PDF, com a linha do programa
    idx = [pg.indice for pg in pr.paginas if pg.folha in (2, 3, 4)]
    anotar("paginas-das-folhas-3-4-5", [(pg.indice + 1, pg.folha + 1, pg.metade) for pg in pr.paginas
                                         if pg.folha in (2, 3, 4)])
    c.pdf_das_paginas(pr, idx, pasta, "programa")
    # o que sairia com a linha do ScanTailor (simulação: a mesma linha posta à mão, numa CÓPIA)
    import copy
    simul = copy.deepcopy(pr)
    for f in (3, 4):
        simul.folhas[f].posicao_corte = linhas[f + 1]["scantailor"]
    c.pdf_das_paginas(simul, idx, pasta, "scantailor")

    # 6. fechar e reabrir: em que ferramenta reabre
    t._ir_para(0)
    base.esperar(1.0)
    import projetos
    j._salvar_agora()
    base.esperar(1.0)
    base.fechar(j)
    j2 = base.nova_janela(1280, 657)
    c.p(j2, pasta, "08-tela-dos-livros-depois")
    resumos = projetos.listar()
    anotar("resumos", [getattr(r, "nome", str(r)) for r in resumos])
    resumo = next((r for r in resumos if "vida" in (getattr(r, "nome", "") or "").lower()), None)
    t2 = c.abrir(j2, pdf, resumo)
    c.esperar_previa(t2)
    anotar("reabriu", estado(j2))
    c.p(j2, pasta, "09-reabriu")
    base.fechar(j2)
    base.gravar_resultados(pasta)


if __name__ == "__main__":
    main()
