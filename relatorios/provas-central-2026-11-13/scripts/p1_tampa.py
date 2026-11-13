"""Print 1 (ac-tampa; D-559, D-692): a faixa preta da tampa do scanner some pelo Automático.

Righetti (cópia: folhas 91 a 100 do PDF, a folha 96 é a 6ª). Caminho do Kaique: abre o livro,
gira as folhas ¼ à esquerda ("todas as folhas"), roda o Automático com Dividir + Endireitar +
Cortar (opções de fábrica), primeiro com "O que fica fora da página: Cortar fora", depois, do
zero, com "Pintar de branco". Prints da janela (grab) e das páginas do PDF.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import comum

RAIZ = str(Path(__file__).resolve().parents[1])
CRU = Path(__file__).resolve().parent / "cru" / "p1"
CRU.mkdir(parents=True, exist_ok=True)
NOTAS: dict = {}


def nota(chave, valor):
    NOTAS[chave] = valor
    print(chave, "=>", valor, flush=True)


def subconjunto() -> Path:
    import fitz

    destino = Path(__file__).resolve().parent / "livros" / "righetti_folhas_91a100.pdf"
    if not destino.exists():
        with fitz.open(str(destino.parent / "righetti.pdf")) as origem, fitz.open() as novo:
            novo.insert_pdf(origem, from_page=90, to_page=99)
            novo.save(str(destino))
    return destino


def paginas_da_folha(projeto, folha: int) -> list[int]:
    return [i for i, p in enumerate(projeto.paginas_ativas) if p.folha == folha]


def uma_rodada(modo: str, pdf: Path) -> None:
    from core import automatico as A
    from core.pipeline import processar
    import copy
    import fitz

    import shutil
    copia = pdf.with_name(f"righetti_folhas_91a100_{modo}.pdf")
    shutil.copy2(pdf, copia)                 # cada rodada começa do zero (livro sem projeto)
    j = comum.nova_janela()
    j.abrir_livro(str(copia))
    nota(f"{modo}: abrir (s)", comum.esperar_tela(j))
    tela, projeto = j.tela_conferir, j.projeto
    nota(f"{modo}: folhas", len(projeto.folhas))
    nota(f"{modo}: rotacao ao abrir", [f.rotacao for f in projeto.folhas])
    nota(f"{modo}: paginas ao abrir", len(projeto.paginas_ativas))
    # gira todas as folhas ¼ à esquerda (a faixa, que está à direita no scan, vai para cima)
    from core import girar
    tela.ir_para_pagina(paginas_da_folha(projeto, 5)[0])
    comum.esperar(1.0)
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela._girar_esquerda()
    comum.esperar(1.0)
    nota(f"{modo}: rotacao depois de girar", [f.rotacao for f in projeto.folhas])
    if modo == "cortar":
        tela.ir_para_pagina(paginas_da_folha(projeto, 5)[0])
        comum.esperar(4.0)
        comum.ate(lambda: tela.previas.ja_pronta(tela.indice_pagina, tela._dpi_atual) is not None, 120)
        comum.esperar(2.0)
        comum.foto(j, CRU / "tela-antes-girada.png")
        import copy as _c
        from core.pipeline import processar as _proc
        import fitz as _f
        p0 = _c.copy(projeto)
        p0.caminho_saida = str(CRU / "saida-antes.pdf")
        with _f.open(str(_proc(p0))) as d0:
            nota("antes: paginas no pdf", len(d0))
            d0[5].get_pixmap(dpi=100).save(str(CRU / "pdf-antes-folha96.png"))
    estado = j.estado_do_automatico
    fazer = "cortar" if modo.startswith("cortar") else "pintar"
    estado.opcoes["borda_preta_fazer"] = fazer
    if modo == "cortar_borda":
        estado.opcoes["borda_preta"] = True
    estado.marcadas = {A.DIVIDIR, A.ENDIREITAR, A.CORTAR}
    grande = j.abrir_o_automatico(A.CORTAR)
    grande.resize(1280, 657)
    grande.move(0, 0)
    comum.esperar(3.0)
    nota(f"{modo}: combo do automatico", grande.controles["borda_preta_fazer"].currentText())
    nota(f"{modo}: combo visivel", not grande.linhas["borda_preta_fazer"].isHidden())
    nota(f"{modo}: tamanho da janela do automatico", [grande.width(), grande.height()])
    comum.esperar(6.0)
    comum.foto(grande, CRU / f"automatico-cortar-{modo}.png")
    j._fechar_a_janela_do_automatico()
    comum.esperar(0.5)
    estado.opcoes["borda_preta_fazer"] = fazer
    if modo == "cortar_borda":
        estado.opcoes["borda_preta"] = True
    estado.marcadas = {A.DIVIDIR, A.ENDIREITAR, A.CORTAR}
    estado.alcance = "livro"
    ok = j.rodar_o_automatico(esperar=True, perguntar=False)
    nota(f"{modo}: rodou", ok)
    comum.esperar(2.0)
    nota(f"{modo}: projeto.borda_preta_fazer", projeto.borda_preta_fazer)
    nota(f"{modo}: projeto.borda_preta", projeto.borda_preta)
    nota(f"{modo}: tampa nas folhas", [f.tampa_do_scanner for f in projeto.folhas])
    paginas = paginas_da_folha(projeto, 5)
    nota(f"{modo}: paginas da folha 96 (indice no PDF de saida, 0=1a)", paginas)
    for n, i in enumerate(paginas):
        tela.ir_para_pagina(i)
        comum.esperar(3.0)
        comum.ate(lambda: tela.previas.ja_pronta(i, tela._dpi_atual) is not None, 180)
        comum.esperar(3.0)
        comum.foto(j, CRU / f"tela-depois-{modo}-{'esq' if n == 0 else 'dir'}.png")
    # o PDF, como o "Confirmar e processar" grava
    p = copy.copy(projeto)
    p.caminho_saida = str(CRU / f"saida-{modo}.pdf")
    saida = processar(p)
    nota(f"{modo}: pdf", str(saida))
    with fitz.open(str(saida)) as d:
        nota(f"{modo}: paginas no pdf", len(d))
        for n, i in enumerate(paginas):
            pg = d[i]
            nota(f"{modo}: tamanho da pagina {i+1} (pt)", [round(pg.rect.width), round(pg.rect.height)])
            pg.get_pixmap(dpi=100).save(str(CRU / f"pdf-{modo}-{'esq' if n == 0 else 'dir'}.png"))
    comum.fechar(j)


def main():
    modo = sys.argv[1]
    comum.preparar(RAIZ, f"p1-{modo}")       # cada jeito numa pasta de dados nova: livro do zero
    pdf = subconjunto()
    # a folha como veio no scan (antes de tudo)
    import fitz
    with fitz.open(str(pdf)) as d:
        d[5].get_pixmap(dpi=100).save(str(CRU / "scan-folha96.png"))
    uma_rodada(modo, pdf)
    (CRU / f"notas-{modo}.json").write_text(json.dumps(NOTAS, ensure_ascii=False, indent=1, default=str),
                                    encoding="utf-8")


if __name__ == "__main__":
    main()
