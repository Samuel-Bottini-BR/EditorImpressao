"""A imposicao e a única parte com resposta certa exata - entao ela e testada
de verdade: montamos o caderno e 'dobramos' de volta, conferindo se a leitura
sai 1, 2, 3, ..., N.
"""

from __future__ import annotations

import pytest

from core.cadernos import (
    contar_cadernos,
    folhas_por_caderno,
    montar_ordem,
    ordem_do_caderno,
    paginas_por_caderno_valido,
)


def _ler_dobrado(lados) -> list[int | None]:
    """Reconstroi a ordem de leitura de um caderno já dobrado.

    Numa dobra, a folha i traz as páginas 2i+1 e 2i+2 no comeco do caderno e
    as duas ultimas no fim. Percorrendo as folhas de fora para dentro montamos
    a metade da frente; o resto vem invertido, da última para a primeira.
    """
    frentes = [lado for lado in lados if lado.frente]
    versos = [lado for lado in lados if not lado.frente]

    inicio: list[int | None] = []
    fim: list[int | None] = []
    for frente, verso in zip(frentes, versos):
        inicio.append(frente.direita)   # pagina impar
        inicio.append(verso.esquerda)   # a seguinte
        fim.append(frente.esquerda)     # ultima
        fim.append(verso.direita)       # penultima
    return inicio + list(reversed(fim))


def test_exemplo_do_docstring():
    lados = ordem_do_caderno(8)
    assert [(l.esquerda, l.direita, l.frente) for l in lados] == [
        (7, 0, True),   # folha 0 frente: paginas 8 e 1 (indices 7 e 0)
        (1, 6, False),  # folha 0 verso:  paginas 2 e 7
        (5, 2, True),   # folha 1 frente: paginas 6 e 3
        (3, 4, False),  # folha 1 verso:  paginas 4 e 5
    ]


@pytest.mark.parametrize("n", [4, 8, 12, 16, 20, 40])
def test_dobrar_devolve_a_ordem_de_leitura(n):
    """O teste que importa: dobrar o caderno tem que dar 1, 2, 3, ..., n."""
    assert _ler_dobrado(ordem_do_caderno(n)) == list(range(n))


@pytest.mark.parametrize("n", [4, 8, 20])
def test_cada_pagina_aparece_uma_vez(n):
    lados = ordem_do_caderno(n)
    vistas = [p for lado in lados for p in (lado.esquerda, lado.direita)]
    assert sorted(vistas) == list(range(n))


def test_livro_inteiro_cobre_todas_as_paginas():
    total, por_caderno = 136, 20
    lados = montar_ordem(total, por_caderno)
    vistas = sorted(p for lado in lados for p in (lado.esquerda, lado.direita) if p is not None)
    assert vistas == list(range(total))


def test_ultimo_caderno_completa_com_branco():
    # 10 paginas num caderno de 20: sobram 10 brancas
    lados = montar_ordem(10, 20)
    brancas = sum(1 for lado in lados for p in (lado.esquerda, lado.direita) if p is None)
    assert brancas == 10
    assert len(lados) == 10  # 20 paginas = 5 folhas = 10 lados


def test_paginas_por_caderno_arredonda_para_multiplo_de_quatro():
    assert paginas_por_caderno_valido(20) == 20
    assert paginas_por_caderno_valido(18) == 20
    assert paginas_por_caderno_valido(17) == 16
    assert paginas_por_caderno_valido(1) == 4
    assert paginas_por_caderno_valido(0) == 4


def test_contagem_de_cadernos_e_folhas():
    assert contar_cadernos(136, 20) == 7   # 6 cheios + 1 parcial
    assert contar_cadernos(140, 20) == 7
    assert folhas_por_caderno(20) == 5


def test_conferencia_da_sequencia_responde_a_pergunta_do_kaique():
    """"Como ter certeza que estão na sequência correta sem olhar folha por folha?"

    A conferência simula a dobra: empilhadas as folhas de um caderno e dobradas
    ao meio, a leitura tem de sair 1, 2, 3... até o fim. Antes o programa só
    dizia como dobrar, e não conferia nada.
    """
    from core.cadernos import conferir_sequencia, instrucoes_de_impressao

    for total, por_caderno in ((4, 4), (8, 8), (20, 20), (199, 20), (907, 20)):
        certo, recado = conferir_sequencia(total, por_caderno)
        assert certo, (total, por_caderno, recado)
        assert "Conferido" in recado

    # o número de páginas em branco do último caderno entra no recado
    certo, recado = conferir_sequencia(199, 20)
    assert certo and "sobra 1 página em branco" in recado

    certo, recado = conferir_sequencia(907, 20)
    assert certo and "sobram 13 páginas em branco" in recado

    # a conferência não entra na lista numerada: ela não é um passo a fazer,
    # e sim o resultado de uma conferência já feita. A tela final a mostra
    # embaixo dos passos.
    passos = instrucoes_de_impressao(199, 20)
    assert len(passos) == 3
    assert not any("Conferido" in linha for linha in passos)


def test_conferencia_pega_imposicao_errada(monkeypatch):
    """Se a conta da imposicao quebrar, a conferencia tem de reprovar."""
    from core import cadernos

    certa = cadernos.ordem_do_caderno

    def trocada(paginas_no_caderno, deslocamento=0):
        lados = certa(paginas_no_caderno, deslocamento)
        if len(lados) >= 2:            # troca duas folhas de lugar
            lados[0], lados[1] = lados[1], lados[0]
        return lados

    monkeypatch.setattr(cadernos, "ordem_do_caderno", trocada)
    certo, recado = cadernos.conferir_sequencia(20, 20)
    assert not certo
    assert "Não imprima assim" in recado
