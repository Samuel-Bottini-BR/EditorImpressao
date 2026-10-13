"""Quanto o conserto custa, e o que ele muda, nas 10 paginas que o teste de
velocidade processa (Marial, paginas 146 a 155)?

O teste de velocidade deu, em Preto e branco, 2 s a mais em 10 paginas com o
conserto. Para saber se isso pode vir do conserto, mede-se direto, com o
codigo do ramo do conserto (--raiz), nessas mesmas 10 paginas:
  - o tempo de achar o corte e o angulo (core.pipeline._geometria) COM o
    conserto e SEM ele (a mesma funcao, com o `girada` tirado da chamada de
    detectar_bordas), 5 vezes cada, alternando; vale o menor tempo;
  - o corte achado dos dois jeitos e o tamanho da pagina que sai (pagina
    maior = filtro mais demorado).
As 10 paginas sao copiadas do livro (so lido) para um PDF em _tmp.

USO   python custo_nas_paginas_do_teste.py --raiz <pasta do programa com o conserto>
Grava custo-nas-paginas-do-teste.json.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MINHA_RAIZ = AQUI.parents[3]
LIVRO = Path(r"D:\programas\EditorImpressao\gabarito\velocidade\marial_300.pdf")
PAGINAS = list(range(145, 155))            # paginas 146 a 155, contando de zero


def main() -> int:
    raiz = Path(sys.argv[sys.argv.index("--raiz") + 1]).resolve()
    sys.path.insert(0, str(raiz))
    from pasta_de_dados_dos_scripts import isolar_pasta_de_dados

    isolar_pasta_de_dados("custo-velocidade", raiz=MINHA_RAIZ / "saida_teste" / "dados_dos_scripts")
    import fitz

    import core.pipeline as P
    import core.recortar as R
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import Projeto

    assert Path(R.__file__).resolve().is_relative_to(raiz)
    pequeno = MINHA_RAIZ / "_tmp" / "marial-146-155.pdf"
    if not pequeno.exists():
        origem = fitz.open(str(LIVRO))
        novo = fitz.open()
        novo.insert_pdf(origem, from_page=PAGINAS[0], to_page=PAGINAS[-1])
        novo.save(str(pequeno))
        novo.close()
        origem.close()
    projeto = P.analisar_projeto(Projeto(caminho_entrada=str(pequeno), nome="marial-146-155"))
    assert projeto.ordem_do_preparo == "endireitar_antes"
    com_o_conserto = R.detectar_bordas

    def sem_o_conserto(img, dpi=None, girada=None):
        return com_o_conserto(img, dpi=dpi)

    doc = abrir_pdf(str(pequeno))
    saida = []
    try:
        for pagina in projeto.paginas:
            folha = projeto.folhas[pagina.folha]
            inteira = P.preparar_para_recorte(pagina_para_array(doc, folha.indice, dpi=300), folha, pagina, projeto)
            tempos = {"com": [], "sem": []}
            geo = {}
            for _ in range(5):
                for nome, funcao in (("com", com_o_conserto), ("sem", sem_o_conserto)):
                    P.detectar_bordas = funcao
                    t0 = time.perf_counter()
                    geo[nome] = P._geometria(inteira, pagina, projeto, dpi=300)
                    tempos[nome].append(time.perf_counter() - t0)
            P.detectar_bordas = com_o_conserto
            a, l = inteira.shape[:2]

            def tamanho(recorte):
                return None if recorte is None else [round(recorte[2] * l), round(recorte[3] * a)]

            linha = {"pagina": 146 + pagina.indice, "angulo": round(float(geo["com"][1]), 3),
                     "com_ms": round(1000 * min(tempos["com"]), 1), "sem_ms": round(1000 * min(tempos["sem"]), 1),
                     "recorte_com": [round(float(v), 5) for v in geo["com"][0]],
                     "recorte_sem": [round(float(v), 5) for v in geo["sem"][0]],
                     "tamanho_com_px": tamanho(geo["com"][0]), "tamanho_sem_px": tamanho(geo["sem"][0])}
            linha["a_mais_ms"] = round(linha["com_ms"] - linha["sem_ms"], 1)
            linha["corte_mudou"] = linha["recorte_com"] != linha["recorte_sem"]
            if linha["tamanho_com_px"] and linha["tamanho_sem_px"]:
                linha["area_pct"] = round(100 * (linha["tamanho_com_px"][0] * linha["tamanho_com_px"][1]
                                                 / (linha["tamanho_sem_px"][0] * linha["tamanho_sem_px"][1]) - 1), 2)
            saida.append(linha)
            print(linha, flush=True)
    finally:
        doc.close()
    total = {"a_mais_nas_10_ms": round(sum(x["a_mais_ms"] for x in saida), 1),
             "geometria_sem_nas_10_ms": round(sum(x["sem_ms"] for x in saida), 1),
             "paginas_que_giram": sum(1 for x in saida if abs(x["angulo"]) >= 0.1),
             "paginas_com_corte_diferente": [x["pagina"] for x in saida if x["corte_mudou"]]}
    print(total)
    (AQUI / "custo-nas-paginas-do-teste.json").write_text(
        json.dumps({"total": total, "paginas": saida}, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
