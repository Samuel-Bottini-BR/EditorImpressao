"""O livro comecado ANTES do endireitar novo continua identico com o conserto?

Abre, com o programa do ramo do conserto (--raiz), os 40 projetos que a
conferencia de antes gravou com o programa de ANTES do G6 (commit 7485e1b;
_tmp/projetos-antigos/*.json, sem o campo ordem_do_preparo), desenha cada
pagina (300 DPI, sem filtro) e compara o md5 com o que aquele programa
desenhou (../corte-g6-2026-10-13/projeto-antigo.json, chave "antes").

USO   python projeto_antigo_no_conserto.py --raiz <pasta do programa com o conserto>
Grava o resultado em conferencias.json (chave "projeto_antigo").
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
MINHA_RAIZ = PASTA.parents[2]
PROJETOS = MINHA_RAIZ / "_tmp" / "projetos-antigos"
DE_ANTES = PASTA.parent / "corte-g6-2026-10-13" / "projeto-antigo.json"


def main() -> int:
    raiz = Path(sys.argv[sys.argv.index("--raiz") + 1]).resolve()
    sys.path.insert(0, str(raiz))
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("conserto-antigo", raiz=MINHA_RAIZ / "saida_teste" / "dados_dos_scripts")
    import core.pipeline as P
    import core.recortar as R
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    assert Path(R.__file__).resolve().is_relative_to(raiz), R.__file__
    assert "girada" in R.detectar_bordas.__code__.co_varnames, "esta copia nao tem o conserto"
    antes = json.loads(DE_ANTES.read_text(encoding="utf-8"))["antes"]
    diferentes, ordens = [], set()
    for chave, esperado in sorted(antes.items()):
        pid, variante = chave.split("|")
        dados = json.loads((PROJETOS / f"{pid}-{variante}.json").read_text(encoding="utf-8"))
        projeto = Projeto.de_dicionario(dados)
        ordens.add(projeto.ordem_do_preparo)
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            agora = {}
            for pagina in projeto.paginas:
                img, _ = P.renderizar_pagina(doc, projeto, pagina, dpi=300)
                agora[pagina.metade] = {"forma": list(img.shape), "md5": hashlib.md5(img.tobytes()).hexdigest()}
        finally:
            doc.close()
        if agora != esperado:
            diferentes.append(chave)
        print(chave, projeto.ordem_do_preparo, "identica" if agora == esperado else "DIFERENTE", flush=True)
    resultado = {"total": len(antes), "identicas": len(antes) - len(diferentes), "diferentes": diferentes,
                 "ordem_ao_abrir": sorted(ordens), "programa": str(raiz)}
    destino = PASTA / "conferencias.json"
    tudo = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    tudo["projeto_antigo"] = resultado
    destino.write_text(json.dumps(tudo, indent=1, ensure_ascii=False), encoding="utf-8")
    print(resultado)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
