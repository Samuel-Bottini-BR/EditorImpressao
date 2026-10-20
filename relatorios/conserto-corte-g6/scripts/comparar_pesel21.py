"""Acerto do Pesel 21 (implementador, 20/10/2026): quais das 89 paginas do
livro novo (C) mudam, ponto por ponto (md5 da pagina pronta), contra
  - o fase-1 (dados-antes.json, C: a ordem nova SEM o conserto da cunha) e
  - o conserto de 13/10 (dados-depois.json, C: d97b937).
A medida nova e dados-pesel21.json (medir.py com MEDIR_CONFIGS=C,
MEDIR_SAIDA=dados-pesel21.json, MEDIR_SUFIXO=__pesel21).

Grava comparacao-pesel21.json e escreve a tabela em Markdown no terminal.
So le; nada do programa muda.

USO  python comparar_pesel21.py
"""

from __future__ import annotations

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent


def _ler(nome: str) -> dict:
    return json.loads((PASTA / nome).read_text(encoding="utf-8"))


def main() -> int:
    fase1, d97, novo = _ler("dados-antes.json"), _ler("dados-depois.json"), _ler("dados-pesel21.json")
    paginas = sorted(b for b, v in novo.items() if "C" in v)
    erros = sorted(b for b, v in novo.items() if "C" not in v)
    muda_d97 = [b for b in paginas if novo[b]["C"]["md5"] != d97[b]["C"]["md5"]]
    muda_fase1 = [b for b in paginas if novo[b]["C"]["md5"] != fase1[b]["C"]["md5"]]
    d97_fase1 = [b for b in paginas if d97[b]["C"]["md5"] != fase1[b]["C"]["md5"]]

    def tam(r):
        return f"{r['tamanho_mm'][0] / 10:.1f} × {r['tamanho_mm'][1] / 10:.1f}".replace(".", ",")

    def pct(v):
        return f"{100 * v:.1f}%".replace(".", ",")

    print(f"paginas medidas: {len(paginas)}; com erro: {erros}")
    print(f"mudam contra o d97b937: {len(muda_d97)} {muda_d97}")
    print(f"mudam contra o fase-1: {len(muda_fase1)} {muda_fase1}")
    print(f"(d97b937 contra o fase-1: {len(d97_fase1)} {d97_fase1})")
    print()
    print("| Pagina | fase-1 | d97b937 | agora | faixa escura: fase-1 / d97b937 / agora | igual ao fase-1? | igual ao d97b937? |")
    print("|---|---|---|---|---|---|---|")
    linhas = {}
    for b in sorted(set(muda_d97) | set(muda_fase1)):
        f, d, n = fase1[b]["C"], d97[b]["C"], novo[b]["C"]
        linhas[b] = {"fase1": {"tamanho_mm": f["tamanho_mm"], "beirada_escuro": f["beirada_escuro"], "recorte": f["recorte"]},
                     "d97b937": {"tamanho_mm": d["tamanho_mm"], "beirada_escuro": d["beirada_escuro"], "recorte": d["recorte"]},
                     "agora": {"tamanho_mm": n["tamanho_mm"], "beirada_escuro": n["beirada_escuro"], "recorte": n["recorte"]},
                     "igual_fase1": b not in muda_fase1, "igual_d97b937": b not in muda_d97}
        print(f"| {b} | {tam(f)} | {tam(d)} | {tam(n)} | {pct(f['beirada_escuro'])} / {pct(d['beirada_escuro'])} / "
              f"{pct(n['beirada_escuro'])} | {'sim' if b not in muda_fase1 else 'nao'} | {'sim' if b not in muda_d97 else 'nao'} |")
    (PASTA / "comparacao-pesel21.json").write_text(json.dumps(
        {"paginas": len(paginas), "erros": erros, "mudam_contra_d97b937": muda_d97,
         "mudam_contra_fase1": muda_fase1, "d97b937_contra_fase1": d97_fase1, "detalhe": linhas},
        indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
