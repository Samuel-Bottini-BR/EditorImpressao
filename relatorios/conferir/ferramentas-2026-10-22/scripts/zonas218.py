"""Verificador 22/10/2026, item 2.18: áreas mudadas à mão, pelo caminho inteiro.

Cada caso: a página do gabarito vira um livro novo (analisar_projeto), a marcação que o programa
acha sozinho é feita como na tela (renderizar_pagina), a área à mão entra POR CIMA dela (como a
pessoa faria com o retângulo + "Marcar como"), e o PDF sai pelo core.pipeline.processar.
"hoje" = o mesmo caminho sem a área à mão.

USO: python zonas218.py --raiz <worktree novo> --saida <pasta>
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

_DADOS = Path(tempfile.gettempdir()) / "vfr22_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)


def caso(raiz, pid, filtro, pasta: Path, rotulo, mexer):
    """mexer(selecao) -> selecao nova (ou None = não mexe)."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto, processar, renderizar_pagina
    from modelos import Projeto

    pdf = pasta / f"{pid}-{rotulo}.pdf"
    projeto = Projeto(caminho_entrada=str(raiz / "gabarito" / "paginas" / f"{pid}.pdf"),
                      caminho_saida=str(pdf), nome=pid)
    projeto = analisar_projeto(projeto)
    projeto.filtro_padrao = filtro
    for p in projeto.paginas:
        p.filtro = filtro
    info = {}
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for pagina in projeto.paginas_ativas:
            renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
            sel = pagina.obter_selecao()
            from core.editar_zonas import caixa_da_area
            info["areas_achadas"] = [{"tipo": r.tipo, "origem": r.origem, "op": r.operacao,
                                      "caixa": [round(v, 3) for v in caixa_da_area(r)]}
                                     for r in sel.regioes]
            nova = mexer(sel) if mexer else None
            if nova is not None:
                pagina.guardar_selecao(nova)
                info["areas_depois"] = [{"tipo": r.tipo, "origem": r.origem,
                                         "caixa": [round(v, 3) for v in caixa_da_area(r)], "cor": r.cor}
                                        for r in nova.regioes]
    finally:
        doc.close()
    processar(projeto)
    (pasta / f"{pid}-{rotulo}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raiz", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--so", default="")
    o = ap.parse_args()
    raiz = o.raiz.resolve()
    pasta = o.saida.resolve()
    pasta.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)
    from core import editar_zonas as ez
    from core.filtros import PRETO_E_BRANCO
    from core.selecao import (AUTOMATICO, MAO, PINTAR, REDE, RETANGULO, SOMAR, TINTA_COR,
                              TINTA_PRETA, Regiao, Selecao)

    def ret(tipo, x0, y0, x1, y1, cor=""):
        return Regiao(tipo=tipo, forma=RETANGULO, pontos=[(x0, y0), (x1, y1)], operacao=SOMAR,
                      origem=MAO, cor=cor)

    def com(*novas):
        def f(sel):
            return Selecao(list(sel.regioes) + list(novas))
        return f

    def sem_achadas(sel):
        return Selecao([r for r in sel.regioes if r.origem not in (AUTOMATICO, REDE)])

    def maior_achada_branca(sel):
        achadas = [(i, r) for i, r in enumerate(sel.regioes) if r.origem in (AUTOMATICO, REDE)]
        if not achadas:
            return None
        def area(r):
            x0, y0, x1, y1 = ez.caixa_da_area(r)
            return (x1 - x0) * (y1 - y0)
        i, r = max(achadas, key=lambda t: area(t[1]))
        return ez.com_a_area_trocada(sel, i, ez.pintada_de_branco(r))

    def gravura_achada(acao):
        def f(sel):
            idx = [i for i, r in enumerate(sel.regioes) if r.origem in (AUTOMATICO, REDE) and r.tipo == "gravura"]
            if not idx:
                return None
            i = idx[0]
            if acao == "apagar":
                return ez.sem_a_area(sel, i)
            return ez.com_a_area_trocada(sel, i, ez.pintada_de_branco(sel.regioes[i]))
        return f

    titulo = (0.12, 0.13, 0.76, 0.27)
    casos = [
        ("horas_p013", "hoje", None),
        ("horas_p013", "titulo-tinta-cor", com(ret(TINTA_COR, *titulo))),
        ("horas_p013", "titulo-tinta-preta", com(ret(TINTA_PRETA, *titulo))),
        ("horas_p013", "canto-pintar", com(ret(PINTAR, 0.86, 0.0, 1.0, 0.07))),
        ("escola_p007", "hoje", None),
        ("escola_p007", "endereco-pintar", com(ret(PINTAR, 0.10, 0.95, 0.90, 1.0))),
        ("escola_p007", "endereco-pintar-cinza", com(ret(PINTAR, 0.10, 0.95, 0.90, 1.0, cor="#c0c0c0"))),
        ("marial_p007", "hoje", None),
        ("marial_p007", "sem-as-achadas", sem_achadas),
        ("marial_p007", "maior-achada-branca", maior_achada_branca),
        ("marial_p007x", "mancha-apagada", gravura_achada("apagar")),
        ("marial_p007x", "mancha-pintada-de-branco", gravura_achada("branco")),
        ("marial_p007x", "mancha-pintar-por-cima", com(ret(PINTAR, 0.0, 0.0, 0.22, 0.23))),
    ]
    for pid, rotulo, mexer in casos:
        if o.so and o.so not in pid:
            continue
        info = caso(raiz, pid.rstrip("x"), PRETO_E_BRANCO, pasta, rotulo, mexer)
        print(pid, rotulo, json.dumps(info, ensure_ascii=False)[:600], flush=True)

    # mover / mudar o tamanho / copiar (as contas da ferramenta "Mover e mudar o tamanho da área")
    r = ret(PINTAR, 0.2, 0.2, 0.4, 0.3)
    contas = {
        "original": ez.caixa_da_area(r),
        "movida_0.1_0.05": ez.caixa_da_area(ez.movida(r, 0.1, 0.05)),
        "redimensionada_para_0.1_0.1_0.5_0.6": ez.caixa_da_area(ez.redimensionada(r, (0.1, 0.1, 0.5, 0.6))),
        "copia": ez.caixa_da_area(ez.copia(r)),
        "original_continua_igual": ez.caixa_da_area(r),
    }
    (pasta / "contas.json").write_text(json.dumps(contas, indent=1), encoding="utf-8")
    print(contas)


if __name__ == "__main__":
    main()
