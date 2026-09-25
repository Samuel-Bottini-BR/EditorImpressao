"""Bateria do acervo: reconhecimento rapido de cada PDF.

Uso:
    python teste_acervo.py recon "pasta"

Nao processa nada: so le o cabecalho de cada PDF e amostra algumas paginas,
para sabermos com o que estamos lidando antes de gastar hora de CPU.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import fitz
import numpy as np

from core import analise
from core.dividir import detectar_lombada
from core.endireitar import detectar_angulo
from core.pdf_io import abrir_pdf, dpi_real_da_pagina, pagina_para_array

AMOSTRA = 12          # paginas por livro no reconhecimento
DPI_AMOSTRA = 110


def _amostrar(total: int, quantas: int) -> list[int]:
    """Indices espalhados pelo livro, sempre incluindo a primeira e a ultima."""
    if total <= quantas:
        return list(range(total))
    passos = np.linspace(0, total - 1, quantas)
    return sorted({int(round(p)) for p in passos})


def recon(caminho: Path) -> dict:
    """Amostra AMOSTRA paginas de um livro a DPI_AMOSTRA e devolve um
    dicionario com o perfil dele: tamanho, DPI real, fracao de paginas em
    paisagem/coloridas/tortas/em branco, e sinais usados para detectar mancha
    do verso e amarelado - tudo para dimensionar o trabalho antes de gastar
    hora de CPU processando o acervo inteiro."""
    doc = abrir_pdf(caminho)
    try:
        total = doc.page_count
        indices = _amostrar(total, AMOSTRA)

        larguras = [doc[i].rect.width for i in indices]
        alturas = [doc[i].rect.height for i in indices]
        dpis = [dpi_real_da_pagina(doc, i) for i in indices]

        paisagens = coloridas = tortas = brancas = 0
        angulos, saturacoes, versos, amarelados = [], [], [], []

        t0 = time.perf_counter()
        for i in indices:
            img = pagina_para_array(doc, i, dpi=DPI_AMOSTRA)
            lombada = detectar_lombada(img)
            inclinacao = detectar_angulo(img)
            tem_cor, sat = analise.detectar_cor(img)
            tinta = analise.fracao_de_tinta(img)

            paisagens += int(lombada.e_paisagem)
            coloridas += int(tem_cor)
            tortas += int(abs(inclinacao.angulo) >= 0.3)
            brancas += int(tinta < analise.FRACAO_TINTA_BRANCA)
            angulos.append(inclinacao.angulo)
            saturacoes.append(sat)

            import cv2

            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            luz, b = lab[:, :, 0], lab[:, :, 2].astype(np.float32)
            papel = luz >= np.percentile(luz, 75)
            amarelados.append(float(b[papel].mean() - 128.0) if papel.sum() else 0.0)

            cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            nivel = float(np.percentile(cinza, 80))
            versos.append(float(((cinza > nivel * 0.62) & (cinza < nivel * 0.88)).mean()))
            del img

        segundos = time.perf_counter() - t0

        return {
            "arquivo": caminho.name,
            "mb": caminho.stat().st_size / 1024 / 1024,
            "paginas": total,
            "largura_pt": float(np.median(larguras)),
            "altura_pt": float(np.median(alturas)),
            "dpi": float(np.median(dpis)),
            "amostradas": len(indices),
            "paisagem_pct": 100 * paisagens / len(indices),
            "cor_pct": 100 * coloridas / len(indices),
            "torta_pct": 100 * tortas / len(indices),
            "branca_pct": 100 * brancas / len(indices),
            "angulo_max": max(abs(a) for a in angulos),
            "saturacao": float(np.median(saturacoes)),
            "amarelado": float(np.median(amarelados)),
            "verso": float(np.median(versos)),
            "s_por_pagina": segundos / len(indices),
        }
    finally:
        doc.close()


def main(argumentos: list[str]) -> int:
    """Roda `recon` em todo PDF de uma pasta e imprime uma tabela-resumo,
    terminando com uma projecao de quanto tempo a analise do acervo inteiro levaria."""
    # a pasta e sempre o ultimo argumento; o que vier antes e so rotulo
    pasta = Path(argumentos[-1]) if len(argumentos) > 1 else Path(".")
    arquivos = sorted(pasta.glob("*.pdf"))
    if not arquivos:
        print(f"nenhum PDF em {pasta}")
        return 1

    print(f"{'arquivo':<46} {'pags':>5} {'MB':>6} {'DPI':>5} {'dupla':>6} "
          f"{'cor':>5} {'torta':>6} {'amarelo':>8} {'verso':>6} {'s/pag':>6}")
    print("-" * 118)

    resultados = []
    for arquivo in arquivos:
        try:
            r = recon(arquivo)
        except Exception as erro:  # noqa: BLE001
            print(f"{arquivo.name[:44]:<46} ERRO: {erro}")
            continue
        resultados.append(r)
        print(f"{r['arquivo'][:44]:<46} {r['paginas']:>5} {r['mb']:>6.0f} "
              f"{r['dpi']:>5.0f} {r['paisagem_pct']:>5.0f}% {r['cor_pct']:>4.0f}% "
              f"{r['torta_pct']:>5.0f}% {r['amarelado']:>+8.1f} "
              f"{r['verso'] * 100:>5.1f}% {r['s_por_pagina']:>6.2f}")

    total_paginas = sum(r["paginas"] for r in resultados)
    tempo = sum(r["paginas"] * r["s_por_pagina"] for r in resultados)
    print("-" * 118)
    print(f"{len(resultados)} livros, {total_paginas} páginas.")
    print(f"So a ANALISE do acervo inteiro levaria ~{tempo / 60:.0f} min "
          f"(a 110 DPI, sem processar nada).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
