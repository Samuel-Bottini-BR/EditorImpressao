"""Monta as tabelas do relatorio do 1.3 a partir de resultados.json.

Uso (ambiente de teste):
    .venv-ocr\\Scripts\\python.exe tabelas.py
Grava relatorios\\...\\tabelas.md (so as tabelas; o texto do relatorio e escrito
a mao e junta as tabelas em gerar_relatorio.py).

Seguro mudar: a ordem das colunas. Arriscado: as metas (98% de texto, 1% de
figura) -- sao as do plano e da pesquisa.
"""

from __future__ import annotations

import json
import statistics as st

import comum as C

META_TEXTO = 0.98
META_FIGURA = 0.01
ORDEM = ["R0", "T1", "T2", "T3a", "T3b", "D1", "D2", "P1", "P2", "P3", "K1"]
CURTO = {  # nome curto da pagina para as colunas
    "palatino_p005": "Pal 5", "palatino_p007": "Pal 7", "palatino_p009": "Pal 9",
    "palatino_p010": "Pal 10", "palatino_p057": "Pal 57", "escola_p007": "Esc 7",
    "escola_p035": "Esc 35", "horas_p011": "Hor 11", "horas_p013": "Hor 13",
    "horas_p047": "Hor 47", "horas_p026": "Hor 26", "horas_p027": "Hor 27",
    "opusmajus_p011": "Opus 11", "opusmajus_p003": "Opus 3", "opusmajus_p020": "Opus 20",
    "opusmajus_p165": "Opus 165", "opusmajus_p256": "Opus 256", "rhetorica_p018": "Rhet 18",
    "siebmacher_p009": "Sieb 9", "graduale_p221": "Grad 221", "graduale_p222": "Grad 222",
    "graduale_p223": "Grad 223",
}
HORAS = ["horas_p011", "horas_p013", "horas_p047", "horas_p026", "horas_p027"]
GRADUALE = C.PAGINAS_MANUSCRITO_EXTRA


def p(v, casas=1) -> str:
    return "-" if v is None else f"{100 * v:.{casas}f}"


def tempo_de(res: dict, det: str, pag: str):
    r = res["paginas"][pag].get(det)
    if not r or det == "R0":
        return None
    return r.get("tempo_s")


def carregar() -> dict:
    return json.loads((C.RELATORIO / "resultados.json").read_text(encoding="utf-8"))


def resumo(res: dict, paginas: list[str]) -> list[dict]:
    linhas = []
    for det in ORDEM:
        vals = [res["paginas"][pg].get(det) for pg in paginas]
        feitos = [(pg, v) for pg, v in zip(paginas, vals) if v]
        if not feitos:
            continue
        achados = [v["texto_achado"] for _, v in feitos if v["texto_achado"] is not None]
        obrig = [(pg, v) for pg, v in feitos if pg in C.OBRIGATORIAS and v["figura_tomada"] is not None]
        todas_fig = [(pg, v) for pg, v in feitos if v["figura_tomada"] is not None]
        tempos = [tempo_de(res, det, pg) for pg, _ in feitos]
        tempos = [t for t in tempos if t is not None]
        pequenos = sum(v["pequenos"] for _, v in feitos)
        perdidos = sum(len(v["pequenos_perdidos"]) for _, v in feitos)
        pior = min(feitos, key=lambda x: x[1]["texto_achado"] if x[1]["texto_achado"] is not None else 9)
        linhas.append({
            "det": det, "n": len(feitos),
            "media": st.mean(achados) if achados else None,
            "acima": sum(a >= META_TEXTO for a in achados),
            "pior": (CURTO[pior[0]], pior[1]["texto_achado"]),
            "obrig_max": max((v["figura_tomada"] for _, v in obrig), default=None),
            "obrig_reprov": [CURTO[pg] for pg, v in obrig if v["figura_tomada"] > META_FIGURA],
            "obrig_area_max": max((v["figura_area"] for _, v in obrig), default=None),
            "fig_max": max((v["figura_tomada"] for _, v in todas_fig), default=None),
            "fig_reprov": [CURTO[pg] for pg, v in todas_fig if v["figura_tomada"] > META_FIGURA],
            "pequenos": pequenos, "perdidos": perdidos,
            "tempo_med": st.median(tempos) if tempos else None,
            "tempo_total": sum(tempos) if tempos else None,
        })
    return linhas


def tabela_resumo(res: dict) -> str:
    # Sem a coluna "o que e": a tabela de configuracoes do relatorio ja diz, e
    # com ela a tabela passava da largura do PDF A4.
    out = ["| OCR | Texto achado (média) | Páginas com 98% ou mais | Pior página | Figura tomada, pior obrigatória | Obrigatórias acima de 1% | Área de figura coberta, pior obrigatória | Itens pequenos perdidos | Tempo por página |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in resumo(res, C.PAGINAS_19):
        tempo = "0" if r["det"] == "R0" else (f"{r['tempo_med']:.1f} s" if r["tempo_med"] is not None else "-")
        reprov = ", ".join(r["obrig_reprov"]) if r["obrig_reprov"] else "nenhuma"
        out.append(f"| {r['det']} | {p(r['media'])}% | {r['acima']} de {r['n']} | "
                   f"{r['pior'][0]} ({p(r['pior'][1])}%) | {p(r['obrig_max'], 2)}% | {reprov} | "
                   f"{p(r['obrig_area_max'], 1)}% | {r['perdidos']} de {r['pequenos']} | {tempo} |")
    return "\n".join(out)


def tabela_por_pagina(res: dict, paginas: list[str], campo: str, casas: int = 1) -> str:
    cab = "| OCR | " + " | ".join(CURTO[pg] for pg in paginas) + " |"
    sep = "|---|" + "---|" * len(paginas)
    out = [cab, sep]
    for det in ORDEM:
        cel = []
        for pg in paginas:
            r = res["paginas"][pg].get(det)
            if not r:
                cel.append("")
                continue
            v = r[campo]
            if v is None:
                cel.append("-")
                continue
            txt = p(v, casas)
            if campo == "texto_achado" and v < META_TEXTO:
                txt = f"**{txt}**"
            if campo in ("figura_tomada", "figura_area") and v > META_FIGURA:
                txt = f"**{txt}**"
            cel.append(txt)
        out.append(f"| {det} | " + " | ".join(cel) + " |")
    return "\n".join(out)


def tabela_tempo(res: dict, paginas: list[str]) -> str:
    cab = "| OCR | " + " | ".join(CURTO[pg] for pg in paginas) + " | Total |"
    out = [cab, "|---|" + "---|" * (len(paginas) + 1)]
    for det in ORDEM:
        if det in ("R0", "T2"):
            continue
        cel, total = [], 0.0
        for pg in paginas:
            t = tempo_de(res, det, pg)
            cel.append("" if t is None else f"{t:.1f}")
            total += t or 0
        out.append(f"| {det} | " + " | ".join(cel) + f" | {total:.0f} s |")
    return "\n".join(out)


def tabela_linhas_iguais(res: dict) -> str:
    """Confere a deducao da pesquisa: trocar o modelo do Tesseract muda as linhas?"""
    out = ["| Página | T1 (linhas) | T3a sem filtro | T3b sem filtro | T2 (depois do filtro) | T3a (depois do filtro) | T3b (depois do filtro) |",
           "|---|---|---|---|---|---|---|"]
    for pg in C.PAGINAS:
        r = res["paginas"][pg]
        def n(k):
            return "-" if not r.get(k) else str(r[k]["linhas"])
        out.append(f"| {CURTO[pg]} | {n('T1')} | {n('T3a sem filtro')} | {n('T3b sem filtro')} | {n('T2')} | {n('T3a')} | {n('T3b')} |")
    return "\n".join(out)


def tabela_manuscrito(res: dict) -> str:
    pags = HORAS + GRADUALE
    return tabela_por_pagina(res, pags, "texto_achado")


# Ordem por livro, para as tabelas por pagina (19 paginas em duas metades,
# senao a tabela nao cabe na largura do PDF A4).
POR_LIVRO = ["palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010", "palatino_p057",
             "escola_p007", "escola_p035", "horas_p011", "horas_p013", "horas_p026", "horas_p027",
             "horas_p047", "opusmajus_p003", "opusmajus_p011", "opusmajus_p020", "opusmajus_p165",
             "opusmajus_p256", "rhetorica_p018", "siebmacher_p009"]
OBRIG_ORDEM = ["palatino_p005", "escola_p035", "horas_p011", "horas_p013", "horas_p026",
               "horas_p027", "opusmajus_p020"]


def tabela_falsas(res: dict) -> str:
    out = ["| OCR | Linhas falsas fora de texto (papel, mancha do verso, pauta) | Linhas falsas dentro de figura | Só no Graduale (pauta de música) |",
           "|---|---|---|---|"]
    for det in ORDEM:
        fora = fig = grad = 0
        tem = False
        for pg, r in res["paginas"].items():
            v = r.get(det)
            if not v:
                continue
            tem = True
            fora += v["falsas_fora"]
            fig += v["falsas_na_figura"]
            if pg in GRADUALE:
                grad += v["falsas_fora"]
        if tem:
            out.append(f"| {det} | {fora} | {fig} | {grad} |")
    return "\n".join(out)


def tabela_pares() -> str:
    pares = json.loads((C.RELATORIO / "pares.json").read_text(encoding="utf-8"))
    out = ["| Par | Como junta | Texto achado (média, 19 páginas) | Páginas com 98% ou mais | Pior obrigatória (figura) | Páginas com figura acima de 1% (de 22) | Graduale 221 / 222 / 223 |",
           "|---|---|---|---|---|---|---|"]
    nomes = {"e": "os dois concordam", "ou": "qualquer um"}
    for chave, modos in pares.items():
        for modo, pags in modos.items():
            txt = [v["texto_achado"] for pg, v in pags.items() if pg in C.PAGINAS_19]
            obrig = [v["figura_tomada"] for pg, v in pags.items() if pg in C.OBRIGATORIAS]
            acima = [CURTO[pg] for pg, v in pags.items() if v["figura_tomada"] is not None and v["figura_tomada"] > META_FIGURA]
            grad = " / ".join(p(pags[pg]["texto_achado"]) for pg in GRADUALE)
            out.append(f"| {chave} | {nomes[modo]} | {p(st.mean(txt))}% | {sum(t >= META_TEXTO for t in txt)} de 19 | "
                       f"{p(max(obrig), 2)}% | {len(acima)}{(' (' + ', '.join(acima) + ')') if acima else ''} | {grad} |")
    return "\n".join(out)


def tabelas_relatorio() -> dict:
    res = carregar()
    com_fig = [pg for pg in POR_LIVRO if any(
        (res["paginas"][pg].get(d) or {}).get("figura_tomada") is not None for d in ORDEM)]
    return {
        "RESUMO": tabela_resumo(res),
        "TEXTO_A": tabela_por_pagina(res, POR_LIVRO[:10], "texto_achado"),
        "TEXTO_B": tabela_por_pagina(res, POR_LIVRO[10:], "texto_achado"),
        "FIG_A": tabela_por_pagina(res, com_fig[:8], "figura_tomada", 2),
        "FIG_B": tabela_por_pagina(res, com_fig[8:], "figura_tomada", 2),
        "AREA_A": tabela_por_pagina(res, com_fig[:8], "figura_area", 1),
        "AREA_B": tabela_por_pagina(res, com_fig[8:], "figura_area", 1),
        "OBRIG_CRU": tabela_por_pagina(res, OBRIG_ORDEM, "figura_tomada_sem_alargar", 2),
        "MANUSCRITO": tabela_manuscrito(res),
        "TEMPO_A": tabela_tempo(res, C.PAGINAS[:11]),
        "TEMPO_B": tabela_tempo(res, C.PAGINAS[11:]),
        "LINHAS_TESS": tabela_linhas_iguais(res),
        "FALSAS": tabela_falsas(res),
        "PARES": tabela_pares(),
    }


def main() -> dict:
    res = carregar()
    t = {
        "RESUMO": tabela_resumo(res),
        "TEXTO_19": tabela_por_pagina(res, C.PAGINAS_19, "texto_achado"),
        "FIGURA_19": tabela_por_pagina(res, [pg for pg in C.PAGINAS_19 if any(
            (res["paginas"][pg].get(d) or {}).get("figura_tomada") is not None for d in ORDEM)], "figura_tomada", 2),
        "AREA_19": tabela_por_pagina(res, [pg for pg in C.PAGINAS_19 if any(
            (res["paginas"][pg].get(d) or {}).get("figura_area") is not None for d in ORDEM)], "figura_area", 1),
        "MANUSCRITO": tabela_manuscrito(res),
        "TEMPO": tabela_tempo(res, C.PAGINAS),
        "LINHAS_TESS": tabela_linhas_iguais(res),
    }
    texto = "\n\n".join(f"## {k}\n\n{v}" for k, v in t.items())
    (C.TRABALHO / "tabelas-geradas.md").write_text(texto, encoding="utf-8")  # rascunho, fora do git
    return t


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for k, v in main().items():
        print("##", k)
        print(v)
        print()
