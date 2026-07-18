"""Teste de ponta a ponta (Etapa 5), tudo por linha de comando.

Uso:
    python teste_pipeline.py "livro.pdf"

Roda a analise completa, mostra o resumo dos alertas e gera o PDF final nas
combinacoes que mais importam.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from core import analise
from core.pipeline import analisar_projeto, processar, resumo_em_portugues
from modelos import Projeto

SAIDA = Path("saida_teste/pipeline")


def _barra(feito: int, total: int, texto: str) -> None:
    if total and feito % max(1, total // 10) == 0:
        print(f"    {texto}")


def main(caminho: str) -> int:
    SAIDA.mkdir(parents=True, exist_ok=True)

    projeto = Projeto(
        caminho_entrada=caminho,
        caminho_saida=str(SAIDA / "livro - preto e branco.pdf"),
        dividir_folhas=True, limpar=True, endireitar=True,
        cortar_bordas=True, montar_cadernos=False,
    )

    print("Analisando...")
    t0 = time.perf_counter()
    analisar_projeto(projeto, progresso=_barra)
    print(f"  {len(projeto.folhas)} folhas -> {len(projeto.paginas)} paginas "
          f"em {time.perf_counter() - t0:.1f} s")
    print(f"  Resumo: {resumo_em_portugues(projeto, len(projeto.folhas))}")

    # --- painel "Paginas para revisar" --------------------------------------
    itens = [(f.indice + 1, f.alertas) for f in projeto.folhas if f.alertas]
    itens += [(p.indice + 1, p.alertas) for p in projeto.paginas if p.alertas]
    grupos = analise.agrupar_por_tipo(itens)

    marcadas = {n for n, _ in itens}
    universo = len(projeto.folhas) + len(projeto.paginas)
    print(f"\nPaginas para revisar ({len(marcadas)})")
    for codigo, numeros in sorted(grupos.items(), key=lambda kv: -len(kv[1])):
        alerta = analise.descrever(codigo)
        mostra = ", ".join(str(n) for n in numeros[:8])
        resto = f" (+{len(numeros) - 8})" if len(numeros) > 8 else ""
        print(f"  {alerta.titulo:<24} {len(numeros):>3}  ->  {mostra}{resto}")
    print(f"  total marcado: {100 * len(marcadas) / universo:.0f}% "
          f"(a meta e menos de 10%)")

    # --- geracao ------------------------------------------------------------
    combinacoes = [
        ("preto e branco", dict(montar_cadernos=False)),
        ("cadernos", dict(montar_cadernos=True, paginas_por_caderno=20)),
        ("so cadernos", dict(montar_cadernos=True, dividir_folhas=False, limpar=False,
                             endireitar=False, cortar_bordas=False)),
    ]

    for nome, ajustes in combinacoes:
        p = Projeto(**{**projeto.para_dicionario(), "folhas": [], "paginas": []})
        p.folhas, p.paginas = projeto.folhas, projeto.paginas
        for chave, valor in ajustes.items():
            setattr(p, chave, valor)
        p.caminho_saida = str(SAIDA / f"livro - {nome}.pdf")

        print(f"\nGerando '{nome}'...")
        t0 = time.perf_counter()
        caminho_saida = processar(p, progresso=_barra)
        dt = time.perf_counter() - t0
        mb = Path(caminho_saida).stat().st_size / 1024 / 1024
        import fitz
        with fitz.open(caminho_saida) as d:
            n = d.page_count
        print(f"  {n} paginas de saida - {mb:.1f} MB - {dt:.1f} s "
              f"({dt / max(1, n):.2f} s/pagina)")

    print(f"\nOK. PDFs em: {SAIDA.resolve()}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
