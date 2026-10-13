"""Mede de novo, por conta do verificador, o LIVRO NOVO nas 89 paginas com
duas copias do programa: a de hoje (fase-1) e a do conserto do implementador
(ramo conserto-corte-g6-2026-10-13, commit d97b937).

Usa a MESMA conta da conferencia de antes (../corte-g6-2026-10-13/scripts/
medir.py: faixa escura na beirada, tinta de fora, pecas partidas), so que:
  - o codigo do programa (core, modelos...) vem da pasta dada em --raiz;
  - so o preparo C (livro novo: endireitar antes + conta do ScanTailor);
  - guarda tambem o md5 da pagina pronta (300 DPI, sem filtro), para dizer
    "identica ponto por ponto" sem depender de JPEG.
As paginas prontas ficam em _tmp/<nome>/ (fora do git).

USO
    python medir_conserto.py --raiz <pasta do programa> --nome hoje|conserto
Nada do programa, do acervo nem do gabarito muda; a pasta de dados do
programa e isolada (pasta_de_dados_dos_scripts).
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent                                    # conserto-corte-g6-verificado-2026-10-13
MINHA_RAIZ = PASTA.parents[2]                          # a worktree do verificador
ANTES = PASTA.parent / "corte-g6-2026-10-13" / "scripts"


def main() -> int:
    args = sys.argv[1:]
    raiz = Path(args[args.index("--raiz") + 1]).resolve()
    nome = args[args.index("--nome") + 1]

    sys.path.insert(0, str(ANTES))
    import medir as M                                  # poe a MINHA raiz no caminho...

    # ...e aqui o codigo do programa passa a vir de --raiz, antes de qualquer `import core`
    sys.path[:] = [p for p in sys.path if Path(p).resolve() != MINHA_RAIZ.resolve()]
    sys.path.insert(0, str(raiz))
    import core.recortar as R

    assert Path(R.__file__).resolve().is_relative_to(raiz), R.__file__
    tem_o_conserto = "girada" in R.detectar_bordas.__code__.co_varnames
    print(f"programa em {raiz}; conserto no corte: {'SIM' if tem_o_conserto else 'nao'}", flush=True)

    M.CONFIGS = ("C",)
    M.FINAIS = MINHA_RAIZ / "_tmp" / f"finais-{nome}"
    M.DADOS = PASTA / f"dados-{nome}.json"
    # os PDFs do gabarito sao lidos pela juncao da worktree do verificador
    M._pdf_da_pagina = lambda pid: (
        M.PAGINAS / f"{pid}.pdf" if (M.PAGINAS / f"{pid}.pdf").exists()
        else MINHA_RAIZ / "gabarito" / "paginas" / f"{pid}.pdf")
    lista = MINHA_RAIZ / "gabarito" / "lista.json"
    M.RAIZ = MINHA_RAIZ                                # so para achar gabarito/lista.json
    assert lista.exists()

    medir_a_beirada = M._medir_a_beirada

    def com_md5(final):
        r = medir_a_beirada(final)
        r["md5"] = hashlib.md5(final.tobytes()).hexdigest()
        r["tem_o_conserto"] = tem_o_conserto
        return r

    M._medir_a_beirada = com_md5
    sys.argv = [sys.argv[0]]
    return M.main()


if __name__ == "__main__":
    raise SystemExit(main())
