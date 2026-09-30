"""Recalcula a regua do item 1.3 com as zonas corrigidas em 30/09/2026 e compara com as antigas.

Uso (no .venv do programa; NAO roda OCR nenhum, so le as linhas ja gravadas):
    .venv\\Scripts\\python.exe relatorios\\conferencia-2-2026-09-30\\scripts\\recalcular_regua.py

Le:
- gabarito/ocr-zonas.antes-2026-09-30.json (zonas antigas) e gabarito/ocr-zonas.json (novas);
- saida_teste/ocr-1.3/linhas/<detector>/  (linhas de cada OCR da comparacao de 28/09);
- saida_teste/ocr-comparar/<motor>/       (linhas das pontes de 29/09, para a comparacao automatica).
Grava relatorios/conferencia-2-2026-09-30/regua-1.3-recalculada.json e imprime:
  1. o resumo da secao 3 do relatorio de 28/09, com as zonas antigas e as novas;
  2. pagina a pagina, docTR fast_base (D2) e Kraken (K1): texto achado e figura tomada;
  3. o par Kraken + docTR (onde os dois concordam / qualquer um);
  4. a comparacao automatica de 29/09 (core/ocr_comparar.py): a decisao "revisar/concorda"
     nao depende das zonas; o que depende e o "erro conhecido" de cada pagina, que aqui e
     recalculado (texto < 98% ou figura > 1% em qualquer um dos dois) para ver se muda;
     e o texto combinado (voto por linha), medido com as zonas novas.

Nao mexe nos arquivos dos relatorios de 28 e 29/09 (os resultados.json de la ficam como estavam).
Seguro mudar: a impressao. Arriscado: as metas (98% / 1%), que sao as do plano.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "relatorios" / "fase1-1.3-comparacao-ocr-2026-09-28" / "scripts"))

import comum as C  # noqa: E402  (a regua do 1.3, sem mudanca)
from core.ocr_comparar import comparar  # noqa: E402
from core.ocr_comum import de_dict  # noqa: E402

ANTES = RAIZ / "gabarito" / "ocr-zonas.antes-2026-09-30.json"
DEPOIS = RAIZ / "gabarito" / "ocr-zonas.json"
SAIDA = Path(__file__).resolve().parents[1] / "regua-1.3-recalculada.json"
CACHE_COMPARAR = RAIZ / "saida_teste" / "ocr-comparar"
DETECTORES = {"R0": ("R0", False), "T1": ("T1", False), "T2": ("T1", True), "T3a": ("T3a", True),
              "T3b": ("T3b", True), "D1": ("D1", False), "D2": ("D2", False), "P1": ("P1", False),
              "P2": ("P2", False), "P3": ("P3", False), "K1": ("K1", False)}
LIMIAR_IA = 20.0


def zonas(arq: Path) -> dict:
    return json.loads(arq.read_text(encoding="utf-8"))["paginas"]


def linhas_de(det: str, pagina: str):
    pasta, filtrar = DETECTORES[det]
    dados = C.ler_linhas(pasta, pagina)
    if dados is None:
        return None
    ls = dados["linhas"]
    return [l for l in ls if l.get("conf", 100) >= LIMIAR_IA] if filtrar else ls


def medir_tudo(Z: dict) -> dict:
    res: dict = {}
    for pagina in C.PAGINAS:
        img = C.ler_imagem(pagina)
        forma = img.shape[:2]
        zm = C.mascaras_zonas(Z[pagina], forma)
        tinta = C.tinta(img, C.dpi_trabalho(pagina))
        rp = {}
        mascaras = {}
        for det in DETECTORES:
            ls = linhas_de(det, pagina)
            if ls is None:
                rp[det] = None
                continue
            m = C.mascara_linhas(ls, forma)
            mascaras[det] = m
            # tambem sem o alargamento de 15% ("a caixa encosta" x "a caixa cobre")
            rp[det] = C.medir(tinta, zm, m, C.mascara_linhas(ls, forma, alargar=0.0))
        if "K1" in mascaras and "D2" in mascaras:
            rp["K1+D2 concordam"] = C.medir(tinta, zm, mascaras["K1"] & mascaras["D2"])
            rp["K1+D2 qualquer"] = C.medir(tinta, zm, mascaras["K1"] | mascaras["D2"])
        # comparacao automatica de 29/09: texto combinado (voto por linha)
        a = de_dict(json.loads((CACHE_COMPARAR / "doctr" / f"{pagina}.json").read_text(encoding="utf-8")))
        b = de_dict(json.loads((CACHE_COMPARAR / "kraken" / f"{pagina}.json").read_text(encoding="utf-8")))
        comp = comparar([a, b])
        voto = C.mascara_linhas([{"poligono": np.asarray(l.poligono).tolist()} for _, l in comp.linhas], forma)
        rp["voto"] = C.medir(tinta, zm, voto)
        rp["_revisar"] = bool(comp.para_revisar)
        rp["_motivos"] = list(comp.motivos)
        res[pagina] = rp
    return res


def resumo(res: dict, det: str) -> dict:
    textos = [res[p][det]["texto_achado"] for p in C.PAGINAS_19 if res[p].get(det) and res[p][det]["texto_achado"] is not None]
    pags = [(res[p][det]["texto_achado"], p) for p in C.PAGINAS_19 if res[p].get(det) and res[p][det]["texto_achado"] is not None]
    obrig = [(res[p][det]["figura_tomada"] or 0.0, p) for p in C.OBRIGATORIAS if res[p].get(det)]
    area = [(res[p][det]["figura_area"] or 0.0, p) for p in C.OBRIGATORIAS if res[p].get(det)]
    cru = [((res[p][det].get("figura_tomada_sem_alargar") or 0.0), p) for p in C.OBRIGATORIAS if res[p].get(det)]
    acima = sorted(p for f, p in obrig if f > 0.01)
    todas_acima = sorted(p for p in C.PAGINAS if res[p].get(det) and (res[p][det]["figura_tomada"] or 0) > 0.01)
    return {"texto_medio_19": float(np.mean(textos)) if textos else None,
            "paginas_98": f"{sum(t >= 0.98 for t in textos)} de {len(textos)}",
            "pior_pagina": min(pags) if pags else None,
            "figura_pior_obrigatoria": max(obrig) if obrig else None,
            "obrigatorias_acima_1pct": acima,
            "area_pior_obrigatoria": max(area) if area else None,
            "sem_alargar_pior_obrigatoria": max(cru) if cru else None,
            "sem_alargar_obrigatorias_acima_1pct": sorted(p for f, p in cru if f > 0.01),
            "paginas_figura_acima_1pct_22": todas_acima}


def pct(v) -> str:
    return "-" if v is None else f"{100 * v:.2f}%"


def erro(r) -> bool:
    """Erro visivel pela regua: texto < 98% ou figura > 1%."""
    if r is None:
        return False
    return (r["texto_achado"] is not None and r["texto_achado"] < 0.98) or \
           (r["figura_tomada"] is not None and r["figura_tomada"] > 0.01)


def main() -> None:
    antes, depois = medir_tudo(zonas(ANTES)), medir_tudo(zonas(DEPOIS))
    saida = {"antes": {}, "depois": {}, "paginas": {}}
    print("=== 1. Resumo (secao 3 do relatorio de 28/09) ===")
    for det in list(DETECTORES) + ["K1+D2 concordam", "K1+D2 qualquer", "voto"]:
        ra, rd = resumo(antes, det), resumo(depois, det)
        saida["antes"][det], saida["depois"][det] = ra, rd
        print(f"{det:16s} texto {pct(ra['texto_medio_19'])} -> {pct(rd['texto_medio_19'])} | "
              f">=98%: {ra['paginas_98']} -> {rd['paginas_98']} | "
              f"figura pior obrig.: {pct(ra['figura_pior_obrigatoria'][0])} {ra['figura_pior_obrigatoria'][1]} -> "
              f"{pct(rd['figura_pior_obrigatoria'][0])} {rd['figura_pior_obrigatoria'][1]} | "
              f"obrig.>1%: {ra['obrigatorias_acima_1pct']} -> {rd['obrigatorias_acima_1pct']} | "
              f"22 pags >1%: {len(ra['paginas_figura_acima_1pct_22'])} -> {len(rd['paginas_figura_acima_1pct_22'])} "
              f"{rd['paginas_figura_acima_1pct_22']} | sem alargar, obrig.>1%: "
              f"{ra['sem_alargar_obrigatorias_acima_1pct']} -> {rd['sem_alargar_obrigatorias_acima_1pct']}")
    print("\n=== 2. Pagina a pagina (D2 docTR fast_base, K1 Kraken, voto da comparacao) ===")
    for p in C.PAGINAS:
        linha = {}
        for det in ("D2", "K1", "voto", "K1+D2 concordam"):
            a, d = antes[p].get(det), depois[p].get(det)
            linha[det] = {"antes": a, "depois": d}
        ea = erro(antes[p]["D2"]) or erro(antes[p]["K1"])
        ed = erro(depois[p]["D2"]) or erro(depois[p]["K1"])
        linha["revisar"] = depois[p]["_revisar"]
        linha["motivos"] = depois[p]["_motivos"]
        linha["erro_visivel_antes"], linha["erro_visivel_depois"] = ea, ed
        saida["paginas"][p] = linha
        txt = "  ".join(f"{det} texto {pct(linha[det]['antes']['texto_achado'])}->{pct(linha[det]['depois']['texto_achado'])} "
                        f"fig {pct(linha[det]['antes']['figura_tomada'])}->{pct(linha[det]['depois']['figura_tomada'])}"
                        for det in ("D2", "K1"))
        print(f"{p:16s} {'REVISAR ' if linha['revisar'] else 'concorda'} erro visivel {ea}->{ed}  {txt}")
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"\ngravado: {SAIDA}")


if __name__ == "__main__":
    main()
