"""Montar cadernos para impressão (imposicao).

O usuario imprime frente e verso, separa as folhas em grupos e dobra cada
grupo ao meio. Para isso as páginas precisam sair fora de ordem, na ordem
certa da dobra.

A conta, para um caderno de N páginas, com a folha i comecando em zero:

    frente da folha i:  [ N - 2i ]  [ 1 + 2i ]
    verso  da folha i:  [ 2 + 2i ]  [ N - 1 - 2i ]

Confira com N = 8 (2 folhas):
    folha 0 frente: 8 1   verso: 2 7
    folha 1 frente: 6 3   verso: 4 5
Dobrando as duas juntas ao meio, a leitura sai 1,2,3,4,5,6,7,8. E o que
queremos.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import fitz

# Multiplo obrigatorio: cada folha carrega 4 paginas (2 frente + 2 verso).
MULTIPLO = 4
PAGINAS_POR_CADERNO_PADRAO = 20


@dataclass(frozen=True)
class Lado:
    """Um lado de uma folha fisica: duas páginas do livro, lado a lado.

    Os números são indices de página comecando em zero, já no livro inteiro.
    None quer dizer página em branco (sobra do fechamento do caderno).
    """

    esquerda: int | None
    direita: int | None
    frente: bool


def paginas_por_caderno_valido(valor: int) -> int:
    """Arredonda para o múltiplo de 4 mais próximo, no mínimo 4."""
    if valor < MULTIPLO:
        return MULTIPLO
    # Arredondamento comercial: o round() do Python leva 4,5 para 4, e um
    # empate aqui deve subir (caderno um pouco maior e melhor que menor).
    return int((valor + MULTIPLO // 2) // MULTIPLO) * MULTIPLO


def ordem_do_caderno(paginas_no_caderno: int, deslocamento: int = 0) -> list[Lado]:
    """Devolve os lados de um caderno, na ordem em que devem ser impressos.

    deslocamento e o número da primeira página deste caderno no livro.
    """
    n = paginas_por_caderno_valido(paginas_no_caderno)
    lados: list[Lado] = []

    for i in range(n // 4):
        # As formulas sao 1-based (a folha 1 traz a pagina 1); por isso o -1
        # ao converter para indice de lista.
        lados.append(
            Lado(
                esquerda=deslocamento + (n - 2 * i) - 1,
                direita=deslocamento + (1 + 2 * i) - 1,
                frente=True,
            )
        )
        lados.append(
            Lado(
                esquerda=deslocamento + (2 + 2 * i) - 1,
                direita=deslocamento + (n - 1 - 2 * i) - 1,
                frente=False,
            )
        )
    return lados


def montar_ordem(total_paginas: int, paginas_por_caderno: int) -> list[Lado]:
    """Ordem de impressão do livro inteiro, caderno por caderno.

    As páginas que passarem do total viram branco: são o arredondamento do
    último caderno.
    """
    n = paginas_por_caderno_valido(paginas_por_caderno)
    lados: list[Lado] = []

    for inicio in range(0, total_paginas, n):
        for lado in ordem_do_caderno(n, deslocamento=inicio):
            lados.append(
                Lado(
                    esquerda=lado.esquerda if _existe(lado.esquerda, total_paginas) else None,
                    direita=lado.direita if _existe(lado.direita, total_paginas) else None,
                    frente=lado.frente,
                )
            )
    return lados


def _existe(indice: int | None, total: int) -> bool:
    return indice is not None and 0 <= indice < total


def contar_cadernos(total_paginas: int, paginas_por_caderno: int) -> int:
    n = paginas_por_caderno_valido(paginas_por_caderno)
    return max(1, -(-total_paginas // n))  # divisao para cima


def folhas_por_caderno(paginas_por_caderno: int) -> int:
    return paginas_por_caderno_valido(paginas_por_caderno) // 4


def impor_pdf(
    caminho_entrada: str | Path,
    caminho_saida: str | Path,
    paginas_por_caderno: int = PAGINAS_POR_CADERNO_PADRAO,
    progresso=None,
) -> int:
    """Le um PDF em ordem normal e grava outro já imposto em cadernos.

    Cada folha de saida e uma página em paisagem com duas páginas do livro lado
    a lado - o usuario só manda imprimir frente e verso, sem configurar nada.

    A copia e feita com show_pdf_page, que preserva texto vetorial e não
    rasteriza nada. E tambem o caminho rapido do modo "só cadernos".
    """
    entrada = fitz.open(caminho_entrada)
    saida = fitz.open()

    try:
        total = entrada.page_count
        if total == 0:
            raise ValueError("PDF de entrada sem páginas")

        # Todas as folhas saem do mesmo tamanho, senao a impressora embaralha
        # as margens. Usamos a maior pagina como molde.
        largura = max(entrada[i].rect.width for i in range(total))
        altura = max(entrada[i].rect.height for i in range(total))

        lados = montar_ordem(total, paginas_por_caderno)

        for numero, lado in enumerate(lados):
            folha = saida.new_page(width=largura * 2, height=altura)
            _colocar(folha, entrada, lado.esquerda, fitz.Rect(0, 0, largura, altura))
            _colocar(folha, entrada, lado.direita, fitz.Rect(largura, 0, largura * 2, altura))
            if progresso is not None:
                progresso(numero + 1, len(lados))

        Path(caminho_saida).parent.mkdir(parents=True, exist_ok=True)
        saida.save(caminho_saida, garbage=3, deflate=True)
        return saida.page_count
    finally:
        saida.close()
        entrada.close()


def _colocar(folha: fitz.Page, origem: fitz.Document, indice: int | None, area: fitz.Rect) -> None:
    """Encaixa uma página da origem na área dada. indice None deixa em branco."""
    if indice is None or not 0 <= indice < origem.page_count:
        return
    folha.show_pdf_page(area, origem, indice)


def instrucoes_de_impressao(total_paginas: int, paginas_por_caderno: int) -> list[str]:
    """Texto em portugues para a tela final. Sem jargao."""
    n = paginas_por_caderno_valido(paginas_por_caderno)
    folhas = folhas_por_caderno(n)
    cadernos = contar_cadernos(total_paginas, n)
    return [
        "Imprima frente e verso, virando na borda curta.",
        f"Separe as folhas em grupos de {folhas}.",
        f"Dobre cada grupo ao meio - são {cadernos} cadernos prontos.",
    ]
