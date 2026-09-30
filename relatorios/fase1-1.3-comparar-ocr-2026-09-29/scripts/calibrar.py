"""Calibra e mede a comparação automática entre os OCRs (core/ocr_comparar.py) nas 22 páginas do 1.3.

Uso (no .venv do programa, depois de rodar_pontes.py):
    .venv\\Scripts\\python.exe relatorios\\fase1-1.3-comparar-ocr-2026-09-29\\scripts\\calibrar.py

Lê saida_teste\\ocr-comparar\\<motor>\\<pagina>.json (fora do git) e grava
resultados.json ao lado desta pasta de scripts. Imprime:
  1. página a página, para cada combinação de OCRs ligados: concorda ou
     revisar, e por quê; e se isso bate com o erro já conhecido da página;
  2. o texto combinado (voto por linha) contra a união e a interseção,
     medido com a régua da comparação do 1.3 (as zonas de
     gabarito/ocr-zonas.json, tinta pela Sauvola, caixas alargadas 15%).

O "erro conhecido" de cada página (ERROS_CONHECIDOS) vem do relatório do 1.3
(relatorios/fase1-1.3-comparacao-ocr-2026-09-28, seções 4 a 6) e, no
Palatino 7, da folha de contato olhada nesta tarefa.
Seguro mudar: a impressão. Arriscado: ERROS_CONHECIDOS (é o gabarito da calibração).
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "relatorios" / "fase1-1.3-comparacao-ocr-2026-09-28" / "scripts"))

import comum as C  # noqa: E402  (a régua do 1.3)
from core.ocr_comparar import comparar  # noqa: E402
from core.ocr_comum import de_dict  # noqa: E402

CACHE = RAIZ / "saida_teste" / "ocr-comparar"
SAIDA = Path(__file__).resolve().parents[1] / "resultados.json"

# O que já se sabe de cada página com o par de fábrica (docTR fast_base + Kraken).
ERROS_CONHECIDOS = {
    "palatino_p005": "docTR: duas caixinhas na borda do retrato (1,7% da figura)",
    "palatino_p007": "docTR: caixas em letras fantasmas da mancha do verso; Kraken: contorno grande no papel "
                     "embaixo (visto na folha de contato em 29/09)",
    "palatino_p009": "docTR: capitular Q (2,1%) e 4 caixas em fantasmas da mancha do verso",
    "palatino_p057": "os dois perdem parte do título (docTR 96,7%, Kraken 96,1% achado)",
    "horas_p011": "Kraken: perde parte do título (96,9%) e põe contornos na iluminura",
    "horas_p013": "docTR encosta na moldura dourada (8,2%); Kraken perde o \"DE\" grande",
    "opusmajus_p003": "docTR: emblema da editora (7,6%); Kraken perde o \"OF\"",
    "opusmajus_p165": "Kraken: uma linha num traço do diagrama (6,6%)",
    "opusmajus_p256": "Kraken: perde a tabela (33%) e avisa 8 linhas perdidas; docTR 86,9%",
    "siebmacher_p009": "Kraken: toma a moldura ornamental por texto (83%)",
    "graduale_p223": "os dois perdem texto (docTR 97,2%, Kraken 94,8%)",
}
COMBINACOES = [("doctr", "kraken"), ("doctr", "tesseract"), ("kraken", "tesseract"),
               ("doctr", "kraken", "tesseract")]


def ler(motor: str, pagina: str):
    return de_dict(json.loads((CACHE / motor / f"{pagina}.json").read_text(encoding="utf-8")))


def mascara_alargada(linhas, shape) -> np.ndarray:
    return C.mascara_linhas([{"poligono": np.asarray(l.poligono).tolist()} for l in linhas], shape)


def main() -> None:
    zonas = C.carregar_zonas()
    saida: dict = {"paginas": {}, "combinada": {}}
    tempos = []
    print("=== 1. Decisão página a página ===")
    for combo in COMBINACOES:
        acertos = revisar_a_toa = erro_perdido = 0
        print(f"\n--- {' + '.join(combo)} ---")
        for pagina in C.PAGINAS:
            resultados = [ler(m, pagina) for m in combo]
            inicio = time.perf_counter()
            comp = comparar(resultados)
            tempos.append(time.perf_counter() - inicio)
            conhecido = ERROS_CONHECIDOS.get(pagina) if combo == ("doctr", "kraken") else None
            decisao = "REVISAR " if comp.para_revisar else "concorda"
            nota = ""
            if combo == ("doctr", "kraken"):
                if comp.para_revisar and conhecido:
                    acertos += 1
                elif comp.para_revisar and not conhecido:
                    revisar_a_toa += 1
                    nota = "  <- revisar sem erro conhecido"
                elif conhecido:
                    erro_perdido += 1
                    nota = "  <- ERRO CONHECIDO NÃO PEGO"
                else:
                    acertos += 1
            print(f"{pagina:16s} {decisao} maior zona {comp.medidas.get('maior_zona', 0):5.2f}  "
                  f"{' | '.join(comp.motivos) or '-'}{nota}")
            saida["paginas"].setdefault(pagina, {})["+".join(combo)] = {
                "para_revisar": comp.para_revisar, "motivos": comp.motivos,
                "zonas": [z.__dict__ for z in comp.zonas], "medidas": comp.medidas,
                "erro_conhecido": conhecido}
        if combo == ("doctr", "kraken"):
            print(f"certo {acertos} de 22; revisar à toa {revisar_a_toa}; erro conhecido não pego {erro_perdido}")
            saida["resumo_fabrica"] = {"certo": acertos, "revisar_a_toa": revisar_a_toa,
                                       "erro_nao_pego": erro_perdido}
    print(f"\ntempo de comparar(): mediana {1000 * float(np.median(tempos)):.0f} ms, "
          f"máximo {1000 * max(tempos):.0f} ms por página")
    saida["tempo_ms"] = {"mediana": 1000 * float(np.median(tempos)), "maximo": 1000 * max(tempos)}

    print("\n=== 2. Texto combinado (docTR + Kraken), régua do 1.3 ===")
    somas = {k: [] for k in ("voto", "uniao", "intersecao")}
    figuras = {k: [] for k in somas}
    for pagina in C.PAGINAS:
        img = C.ler_imagem(pagina)
        forma = img.shape[:2]
        tinta = C.tinta(img, C.dpi_trabalho(pagina))
        zm = C.mascaras_zonas(zonas[pagina], forma)
        a, b = ler("doctr", pagina), ler("kraken", pagina)
        comp = comparar([a, b])
        mascaras = {
            "voto": mascara_alargada([l for _, l in comp.linhas], forma),
            "uniao": mascara_alargada(a.linhas + b.linhas, forma),
            "intersecao": mascara_alargada(a.linhas, forma) & mascara_alargada(b.linhas, forma),
        }
        linha = {}
        for nome, m in mascaras.items():
            medida = C.medir(tinta, zm, m)
            linha[nome] = {"texto_achado": medida["texto_achado"], "figura_tomada": medida["figura_tomada"]}
            if medida["texto_achado"] is not None and pagina in C.PAGINAS_19:
                somas[nome].append(medida["texto_achado"])
            if medida["figura_tomada"] is not None:
                figuras[nome].append((medida["figura_tomada"], pagina))
        saida["combinada"][pagina] = linha
        print(f"{pagina:16s} " + "  ".join(
            f"{n}: texto {100 * (v['texto_achado'] or 0):5.1f}% figura "
            f"{'-' if v['figura_tomada'] is None else f'{100 * v['figura_tomada']:5.2f}%'}"
            for n, v in linha.items()))
    for nome in somas:
        acima = [p for f, p in figuras[nome] if f > 0.01]
        print(f"{nome:10s}: texto achado (média, 19 páginas) {100 * np.mean(somas[nome]):.1f}%; "
              f"páginas com mais de 1% de figura: {len(acima)} {acima}")
        saida.setdefault("resumo_combinada", {})[nome] = {
            "texto_medio_19": float(np.mean(somas[nome])), "paginas_figura_acima_1pct": acima}
    SAIDA.write_text(json.dumps(saida, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(f"\ngravado: {SAIDA}")


if __name__ == "__main__":
    main()
