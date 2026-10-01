r"""Recalibra a comparacao automatica dos OCRs (core/ocr_comparar.py) com as zonas APROVADAS (01/10/2026).

Uso (no .venv do programa; NAO roda OCR nenhum, so le as linhas ja gravadas):
    .venv\Scripts\python.exe relatorios\fase1-1.3-recalibrar-comparacao-2026-10-01\scripts\recalibrar.py

Le:
- gabarito/ocr-zonas.json (final: aprovado pelo Samuel na conferencia 2, com a D5 de 01/10:
  as letrinhas dos diagramas do Opus 165 sao texto) e gabarito/ocr-zonas.antes-2026-10-01.json
  (o de 30/09, so para mostrar o que a D5 mudou);
- saida_teste/ocr-comparar/<motor>/<pagina>.json (linhas das pontes de 29/09, fora do git).
Grava resultados.json ao lado da pasta scripts/ e imprime:
  1. a regua pagina a pagina (docTR = D2, Kraken = K1, e o texto combinado "voto" que o
     programa vai usar): texto achado, figura tomada, itens pequenos perdidos;
  2. a decisao da comparacao com os numeros de hoje (concorda / revisar) contra o "erro
     visivel pela regua" (a mesma regra de 30/09: texto < 98% ou figura > 1% no docTR OU no
     Kraken; o Palatino 7 conta como erro pelo que se viu de olho em 29/09);
  3. a busca: TOLERANCIA x ESPESSURA_MINIMA x AREA_MINIMA numa grade, e quantas paginas cada
     combinacao acerta, quantas manda revisar a toa e quantos erros deixa passar;
  4. a folga dos limites de hoje (a maior zona de discordancia numa pagina boa e a menor numa
     pagina com erro pego).

So mede: nao muda core/ocr_comparar.py (a busca troca os numeros so dentro deste processo).
Seguro mudar: a impressao e a grade. Arriscado: a regra do erro (98% / 1%), que e a do plano.
"""

from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "relatorios" / "fase1-1.3-comparacao-ocr-2026-09-28" / "scripts"))

import comum as C  # noqa: E402  (a regua do 1.3, sem mudanca)
import core.ocr_comparar as OC  # noqa: E402
from core.ocr_comum import de_dict  # noqa: E402

CACHE = RAIZ / "saida_teste" / "ocr-comparar"
ZONAS_FINAIS = RAIZ / "gabarito" / "ocr-zonas.json"
ZONAS_30_09 = RAIZ / "gabarito" / "ocr-zonas.antes-2026-10-01.json"
SAIDA = Path(__file__).resolve().parents[1] / "resultados.json"
ERRO_DE_OLHO = {"palatino_p007": "docTR: caixas em letras fantasmas da mancha do verso; Kraken: contorno "
                                 "grande no papel embaixo (folha de contato, 29/09)"}
HOJE = {"TOLERANCIA": OC.TOLERANCIA, "ESPESSURA_MINIMA": OC.ESPESSURA_MINIMA, "AREA_MINIMA": OC.AREA_MINIMA}


def ler(motor: str, pagina: str):
    return de_dict(json.loads((CACHE / motor / f"{pagina}.json").read_text(encoding="utf-8")))


def mascara(linhas, forma) -> np.ndarray:
    return C.mascara_linhas([{"poligono": np.asarray(l.poligono).tolist()} for l in linhas], forma)


def erra(r: dict) -> bool:
    return (r["texto_achado"] is not None and r["texto_achado"] < 0.98) or \
           (r["figura_tomada"] is not None and r["figura_tomada"] > 0.01)


def pct(v) -> str:
    return "  -   " if v is None else f"{100 * v:6.2f}"


def regua(arquivo: Path) -> dict:
    Z = json.loads(arquivo.read_text(encoding="utf-8"))["paginas"]
    saida = {}
    for p in C.PAGINAS:
        img = C.ler_imagem(p)
        forma = img.shape[:2]
        zm = C.mascaras_zonas(Z[p], forma)
        tinta = C.tinta(img, C.dpi_trabalho(p))
        a, b = ler("doctr", p), ler("kraken", p)
        comp = OC.comparar([a, b])
        r = {"D2": C.medir(tinta, zm, mascara(a.linhas, forma)),
             "K1": C.medir(tinta, zm, mascara(b.linhas, forma)),
             "voto": C.medir(tinta, zm, mascara([l for _, l in comp.linhas], forma))}
        r["erro"] = erra(r["D2"]) or erra(r["K1"]) or p in ERRO_DE_OLHO
        r["erro_voto"] = erra(r["voto"])
        saida[p] = r
    return saida


def decisoes(dados: dict) -> dict:
    """maior zona de discordancia e linhas perdidas avisadas, com os numeros do modulo agora."""
    out = {}
    for p, (a, b) in dados.items():
        comp = OC.comparar([a, b])
        out[p] = {"maior_zona": float(comp.medidas.get("maior_zona", 0.0)),
                  "perdidas": a.perdidas + b.perdidas, "para_revisar": comp.para_revisar,
                  "motivos": comp.motivos}
    return out


def classificar(revisar: bool, erro: bool) -> str:
    if revisar and erro:
        return "certo (revisar, tem erro)"
    if not revisar and not erro:
        return "certo (concorda, sem erro)"
    return "REVISAR A TOA" if revisar else "ERRO NAO PEGO"


def main() -> None:
    final, antes = regua(ZONAS_FINAIS), regua(ZONAS_30_09)
    dados = {p: (ler("doctr", p), ler("kraken", p)) for p in C.PAGINAS}
    saida: dict = {"numeros_de_hoje": HOJE, "paginas": {}, "grade": [], "folga": {}}

    print("=== 1. Regua com as zonas aprovadas (texto achado % / figura tomada %) ===")
    print(f"{'pagina':16s} {'docTR':>15s} {'Kraken':>15s} {'voto':>15s}  erro  pequenos perdidos (voto)")
    for p in C.PAGINAS:
        r = final[p]
        print(f"{p:16s} " + " ".join(f"{pct(r[d]['texto_achado'])}/{pct(r[d]['figura_tomada'])}"
                                     for d in ("D2", "K1", "voto"))
              + f"  {'SIM ' if r['erro'] else 'nao '} {len(r['voto']['pequenos_perdidos'])} de {r['voto']['pequenos']}")
    o165a, o165d = antes["opusmajus_p165"], final["opusmajus_p165"]
    print("\nOpus 165 (D5), zonas 30/09 -> finais: " + "; ".join(
        f"{d} texto {pct(o165a[d]['texto_achado'])}->{pct(o165d[d]['texto_achado'])}, figura "
        f"{pct(o165a[d]['figura_tomada'])}->{pct(o165d[d]['figura_tomada'])}, pequenos perdidos "
        f"{len(o165a[d]['pequenos_perdidos'])}/{o165a[d]['pequenos']}->"
        f"{len(o165d[d]['pequenos_perdidos'])}/{o165d[d]['pequenos']}"
        for d in ("D2", "K1", "voto")))
    print("   letras perdidas pelo voto:", o165d["voto"]["pequenos_perdidos"])
    saida["opus165_d5"] = {"antes": {d: o165a[d] for d in ("D2", "K1", "voto")},
                           "depois": {d: o165d[d] for d in ("D2", "K1", "voto")}}

    print("\n=== 2. Decisao da comparacao (numeros de hoje) x erro visivel pela regua ===")
    hoje = decisoes(dados)
    conta = {"certo": 0, "a_toa": 0, "nao_pego": 0}
    for p in C.PAGINAS:
        d, r = hoje[p], final[p]
        c = classificar(d["para_revisar"], r["erro"])
        conta["certo" if c.startswith("certo") else "a_toa" if "TOA" in c else "nao_pego"] += 1
        print(f"{p:16s} {'REVISAR ' if d['para_revisar'] else 'concorda'} maior zona {d['maior_zona']:6.2f} "
              f"erro {'SIM' if r['erro'] else 'nao'} (voto erra: {'SIM' if r['erro_voto'] else 'nao'})  -> {c}")
        saida["paginas"][p] = {"regua": {k: final[p][k] for k in ("D2", "K1", "voto")},
                               "erro": r["erro"], "erro_voto": r["erro_voto"], "comparacao": d,
                               "classificacao": c}
    print(f"certo {conta['certo']} de 22; revisar a toa {conta['a_toa']}; erro nao pego {conta['nao_pego']}")
    saida["resumo_hoje"] = conta

    print("\n=== 3. Busca na grade (TOLERANCIA x ESPESSURA_MINIMA x AREA_MINIMA) ===")
    erro = {p: final[p]["erro"] for p in C.PAGINAS}
    melhores = []
    try:
        for tol, esp in itertools.product([0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6],
                                          [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8]):
            OC.TOLERANCIA, OC.ESPESSURA_MINIMA = tol, esp
            dz = decisoes(dados)
            boas = [dz[p]["maior_zona"] for p in C.PAGINAS if not erro[p]]
            for area in np.round(np.arange(0.2, 3.01, 0.05), 2):
                rev = {p: dz[p]["perdidas"] > 0 or dz[p]["maior_zona"] >= area for p in C.PAGINAS}
                toa = sorted(p for p in C.PAGINAS if rev[p] and not erro[p])
                perd = sorted(p for p in C.PAGINAS if erro[p] and not rev[p])
                pegos = [dz[p]["maior_zona"] for p in C.PAGINAS if erro[p] and rev[p] and dz[p]["perdidas"] == 0]
                melhores.append({"TOLERANCIA": tol, "ESPESSURA_MINIMA": esp, "AREA_MINIMA": float(area),
                                 "certo": 22 - len(toa) - len(perd), "a_toa": toa, "nao_pego": perd,
                                 "maior_zona_boa": max(boas), "menor_zona_pega": min(pegos) if pegos else None})
    finally:
        OC.TOLERANCIA, OC.ESPESSURA_MINIMA = HOJE["TOLERANCIA"], HOJE["ESPESSURA_MINIMA"]
    melhores.sort(key=lambda m: (m["certo"], -len(m["a_toa"])), reverse=True)
    teto = melhores[0]["certo"]
    sem_toa = max(m["certo"] for m in melhores if not m["a_toa"])
    print(f"melhor da grade: {teto} de 22; melhor sem nenhum revisar a toa: {sem_toa} de 22")
    for m in melhores[:8]:
        print(f"  TOL {m['TOLERANCIA']:.2f} ESP {m['ESPESSURA_MINIMA']:.2f} AREA {m['AREA_MINIMA']:.2f}: "
              f"certo {m['certo']}, a toa {m['a_toa']}, nao pego {m['nao_pego']}")
    saida["grade"] = melhores[:60]
    saida["grade_teto"], saida["grade_teto_sem_a_toa"] = teto, sem_toa

    print("\n=== 4. Folga dos limites de hoje ===")
    boas = sorted(((hoje[p]["maior_zona"], p) for p in C.PAGINAS if not erro[p]), reverse=True)
    pegas = sorted((hoje[p]["maior_zona"], p) for p in C.PAGINAS
                   if erro[p] and hoje[p]["para_revisar"] and hoje[p]["perdidas"] == 0)
    soltas = sorted(((hoje[p]["maior_zona"], p) for p in C.PAGINAS if erro[p] and not hoje[p]["para_revisar"]),
                    reverse=True)
    print(f"paginas boas, maiores zonas: {[(round(v, 2), p) for v, p in boas[:4]]}")
    print(f"erros pegos pela zona, menores: {[(round(v, 2), p) for v, p in pegas[:4]]}")
    print(f"erros nao pegos, maiores zonas: {[(round(v, 2), p) for v, p in soltas]}")
    print(f"limite AREA_MINIMA {OC.AREA_MINIMA}: {OC.AREA_MINIMA / boas[0][0]:.2f}x a maior zona boa; "
          f"a menor zona pega e {pegas[0][0] / OC.AREA_MINIMA:.2f}x o limite")
    saida["folga"] = {"zonas_boas": boas, "zonas_pegas": pegas, "erros_nao_pegos": soltas}
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"\ngravado: {SAIDA}")


if __name__ == "__main__":
    main()
