"""Verificador 22/10/2026, item 2.6: monta o arquivo de impressão de verdade e confere a dobra.

1. `montar`: chama core.impressao.montar_para_impressao (o mesmo do botão "gravar o arquivo
   para imprimir") sobre o PDF do livro já processado pelo caminho inteiro, com as opções em JSON.
   `velho`: chama core.cadernos.impor_pdf (o "Montar cadernos no tamanho do scan", o mesmo que o
   processar chama quando a caixinha está marcada) - roda no código que --raiz escolher.
2. `conferir`: SEM usar o código do programa. Desenha cada lado de cada folha, separa a metade da
   esquerda e a da direita, descobre qual página do livro está em cada metade (comparando com as
   páginas do livro processado) e SIMULA A DOBRA: as folhas de cada caderno empilhadas e dobradas
   ao meio, lidas na ordem. Tem de dar 1, 2, 3, ... N e só páginas em branco no fim.
   Também mede as margens (mm) de cada página na folha.

Regra da dobra (impressão frente e verso virando na borda curta; encadernação à esquerda):
para um caderno de s folhas (frente F_i e verso V_i, i = 0 é a de fora), a leitura é
F0.dir, V0.esq, F1.dir, V1.esq, ..., F(s-1).dir, V(s-1).esq, V(s-1).dir, F(s-1).esq, ..., V0.dir, F0.esq.
O tamanho dos cadernos é calculado aqui, pela regra decidida (imp-4): todos com `por_caderno`
páginas, menos o último, com o múltiplo de 4 logo acima do que sobrou.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

MM = 25.4 / 72


def _img(pagina, dpi):
    import fitz  # noqa: F401
    pix = pagina.get_pixmap(dpi=dpi, alpha=False)
    a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
    return a.mean(axis=2)


def _assinatura(cinza):
    import cv2
    p = cv2.resize(cinza.astype(np.float32), (60, 84), interpolation=cv2.INTER_AREA)
    p = p - p.mean()
    n = np.linalg.norm(p)
    return p / n if n > 0 else p


def _caixa(cinza, limiar=245):
    escuros = cinza < limiar
    if escuros.sum() < 50:
        return None
    ys, xs = np.where(escuros)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def conferir(livro: Path, montado: Path, por_caderno: int, dpi=40) -> dict:
    import fitz
    with fitz.open(str(livro)) as doc:
        assin = [_assinatura(_img(p, dpi)) for p in doc]
        total = doc.page_count
    lados = []
    with fitz.open(str(montado)) as doc:
        for n, pg in enumerate(doc):
            cinza = _img(pg, dpi)
            h, w = cinza.shape
            meio = w // 2
            lado = {"numero": n + 1, "largura_mm": round(pg.rect.width * MM, 1),
                    "altura_mm": round(pg.rect.height * MM, 1)}
            for nome, x0, x1 in (("esq", 0, meio), ("dir", meio, w)):
                parte = cinza[:, x0:x1]
                cx = _caixa(parte)
                if cx is None:
                    lado[nome] = None
                    continue
                a = _assinatura(parte[cx[1]:cx[3], cx[0]:cx[2]])
                notas = [float((a * b).sum()) for b in assin]
                ordem = np.argsort(notas)[::-1]
                px_mm = 25.4 / dpi
                lado[nome] = {
                    "pagina": int(ordem[0]) + 1, "semelhanca": round(notas[ordem[0]], 3),
                    "segunda": round(notas[ordem[1]], 3) if len(ordem) > 1 else None,
                    "margens_mm": {  # distância da página até a beirada do papel e até a dobra
                        "fora": round((cx[0] if nome == "esq" else (x1 - x0) - cx[2]) * px_mm, 1),
                        "dobra": round(((x1 - x0) - cx[2] if nome == "esq" else cx[0]) * px_mm, 1),
                        "cima": round(cx[1] * px_mm, 1), "baixo": round((h - cx[3]) * px_mm, 1),
                    },
                    "tamanho_mm": [round((cx[2] - cx[0]) * px_mm, 1), round((cx[3] - cx[1]) * px_mm, 1)],
                }
            lados.append(lado)
    # tamanhos dos cadernos (regra imp-4), calculados aqui
    tamanhos, resto = [], total
    while resto > 0:
        t = por_caderno if resto >= por_caderno else 4 * -(-resto // 4)
        tamanhos.append(t)
        resto -= t
    leitura, i = [], 0
    for t in tamanhos:
        s = t // 4
        folhas = [(lados[i + 2 * k], lados[i + 2 * k + 1]) for k in range(s)]
        i += 2 * s
        pag = lambda l, lado: (l[lado] or {}).get("pagina")  # noqa: E731
        for F, V in folhas:
            leitura += [pag(F, "dir"), pag(V, "esq")]
        for F, V in reversed(folhas):
            leitura += [pag(V, "dir"), pag(F, "esq")]
    sem_branco = [p for p in leitura if p is not None]
    brancos_no_fim = len(leitura) - len(sem_branco)
    certo = (sem_branco == list(range(1, total + 1))
             and all(p is None for p in leitura[len(sem_branco):]))
    return {"livro_paginas": total, "lados_no_arquivo": len(lados), "folhas_de_papel": len(lados) // 2,
            "cadernos_calculados": tamanhos, "leitura_depois_de_dobrar": leitura,
            "dobra_certa": certo, "paginas_em_branco": brancos_no_fim,
            "sobrou_lado": i != len(lados), "lados": lados}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["montar", "velho", "conferir"])
    ap.add_argument("--raiz", type=Path)
    ap.add_argument("--livro", type=Path, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--opcoes", default="{}")
    ap.add_argument("--por-caderno", type=int, default=20)
    o = ap.parse_args()
    if o.modo in ("montar", "velho"):
        sys.path.insert(0, str(o.raiz.resolve()))
        os.chdir(o.raiz.resolve()) if False else None
        import time
        t = time.perf_counter()
        if o.modo == "montar":
            from core import impressao
            op = impressao.OpcoesDeImpressao.de_dicionario(json.loads(o.opcoes))
            r = impressao.montar_para_impressao(o.livro, o.saida, op)
            info = {"opcoes": json.loads(o.opcoes), "folhas_de_papel": r.folhas_de_papel,
                    "paginas_do_arquivo": r.paginas_do_arquivo, "cadernos": r.cadernos,
                    "instrucoes": r.instrucoes, "conferencia_do_programa": r.conferencia,
                    "avisos": [[a.pagina, a.texto] for a in r.avisos]}
        else:
            from core import cadernos
            n = cadernos.impor_pdf(str(o.livro), str(o.saida), o.por_caderno)
            info = {"lados": n, "instrucoes": cadernos.instrucoes_de_impressao(
                __import__("fitz").open(str(o.livro)).page_count, o.por_caderno)}
        info["segundos"] = round(time.perf_counter() - t, 2)
        o.saida.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps(info, ensure_ascii=False)[:1500])
    else:
        r = conferir(o.livro, o.saida, o.por_caderno)
        o.saida.with_name(o.saida.stem + "-dobra.json").write_text(
            json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        print(json.dumps({k: r[k] for k in r if k != "lados"}, ensure_ascii=False))
        piores = sorted((l[s]["semelhanca"], l["numero"], s) for l in r["lados"] for s in ("esq", "dir") if l[s])
        print("menor semelhanca:", piores[:3])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
