"""O projeto comecado ANTES do G6 sai igual no programa de hoje?

Dois passos, cada um num processo (para os dois codigos nao se misturarem):

  python projeto_antigo.py antes pid,pid,...
      Roda o programa de ANTES do G6 (commit 7485e1b, o pai da juncao
      4a7f288, tirado com `git archive` para _tmp/antes-g6): cria o projeto
      de cada pagina, analisa, desenha a pagina (300 DPI, sem filtro) e GRAVA
      o projeto em JSON como aquele programa gravava (para_dicionario) - sem
      o campo ordem_do_preparo, que ainda nao existia. Duas variantes:
        "g4"   o livro novo de entao (endireitar pela conta do ScanTailor)
        "prog" endireitar pela conta do programa (projeto de antes de 05/10)

  python projeto_antigo.py agora pid,pid,...
      Roda o programa de HOJE (esta copia): abre cada projeto gravado acima
      (Projeto.de_dicionario), confere que a ordem ficou "cortar_antes",
      desenha a pagina e compara ponto por ponto com a de antes.

Grava projeto-antigo.json ao lado do dados.json. So le o acervo; nada do
programa muda.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[2]
ANTES = RAIZ / "_tmp" / "antes-g6"
PROJETOS = RAIZ / "_tmp" / "projetos-antigos"
TRABALHO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho")
DPI = 300


def _pdf(pid: str) -> Path:
    do_estudo = TRABALHO / "paginas" / f"{pid}.pdf"
    return do_estudo if do_estudo.exists() else RAIZ / "gabarito" / "paginas" / f"{pid}.pdf"


def _desenhar(projeto) -> dict:
    """{metade: (forma, md5)} das paginas do projeto, 300 DPI, sem filtro."""
    from core import pipeline as P
    from core.pdf_io import abrir_pdf

    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        saida = {}
        for pagina in projeto.paginas:
            img, _ = P.renderizar_pagina(doc, projeto, pagina, dpi=DPI)
            saida[pagina.metade] = {"forma": list(img.shape),
                                    "md5": hashlib.md5(img.tobytes()).hexdigest()}
        return saida
    finally:
        doc.close()


def antes(pids: list[str]) -> dict:
    sys.path.insert(0, str(ANTES))
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("corte-g6-antes", raiz=RAIZ / "saida_teste" / "dados_dos_scripts")
    import core.pipeline as P
    from core.filtros import ORIGINAL
    from modelos import Projeto

    assert str(ANTES) in P.__file__, P.__file__          # e mesmo o codigo de antes
    assert not hasattr(Projeto(caminho_entrada="x"), "ordem_do_preparo")
    PROJETOS.mkdir(parents=True, exist_ok=True)
    res = {}
    for pid in pids:
        for variante, conta in (("g4", None), ("prog", "programa")):
            projeto = Projeto(caminho_entrada=str(_pdf(pid)), nome=pid)
            projeto.filtro_padrao = ORIGINAL
            projeto.limpar = False
            projeto.qualidade_dpi = DPI
            if conta:
                projeto.endireitar_como = conta
            projeto = P.analisar_projeto(projeto)
            res[f"{pid}|{variante}"] = _desenhar(projeto)
            dados = Projeto.para_o_disco(projeto.para_dicionario())
            assert "ordem_do_preparo" not in dados
            if variante == "prog":
                dados.pop("endireitar_como", None)     # projeto de antes de 05/10: sem o campo
            (PROJETOS / f"{pid}-{variante}.json").write_text(
                json.dumps(dados, ensure_ascii=False), encoding="utf-8")
            print("antes", pid, variante, res[f"{pid}|{variante}"], flush=True)
    return res


def agora(pids: list[str]) -> dict:
    sys.path.insert(0, str(RAIZ))
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("corte-g6-agora")
    import core.pipeline as P
    from modelos import Projeto

    assert str(ANTES) not in P.__file__, P.__file__
    res = {}
    for pid in pids:
        for variante in ("g4", "prog"):
            dados = json.loads((PROJETOS / f"{pid}-{variante}.json").read_text(encoding="utf-8"))
            projeto = Projeto.de_dicionario(dados)
            r = _desenhar(projeto)
            res[f"{pid}|{variante}"] = {"ordem_do_preparo": projeto.ordem_do_preparo,
                                        "endireitar_como": projeto.endireitar_como, "paginas": r}
            print("agora", pid, variante, projeto.ordem_do_preparo, projeto.endireitar_como, r, flush=True)
    return res


def main() -> int:
    lado, pids = sys.argv[1], sys.argv[2].split(",")
    destino = PASTA / "projeto-antigo.json"
    tudo = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    tudo.setdefault(lado, {}).update(antes(pids) if lado == "antes" else agora(pids))
    if "antes" in tudo and "agora" in tudo:
        comparacao = {}
        for chave, a in tudo["antes"].items():
            g = tudo["agora"].get(chave)
            if g is None:
                continue
            comparacao[chave] = {"ordem_ao_abrir_hoje": g["ordem_do_preparo"],
                                 "identica_ponto_por_ponto": a == g["paginas"]}
        tudo["comparacao"] = comparacao
        iguais = sum(1 for v in comparacao.values() if v["identica_ponto_por_ponto"])
        print(f"identicas: {iguais} de {len(comparacao)}; "
              f"diferentes: {[k for k, v in comparacao.items() if not v['identica_ponto_por_ponto']]}")
    destino.write_text(json.dumps(tudo, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
