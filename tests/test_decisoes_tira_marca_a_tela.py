"""D-612, conserto do teste do Samuel (04/11/2026, prints a-75 e a-76, Dividir em "Duas lado a
lado"): "quando eu clico em uma pagina estado o lado a lado escolhido, ele não escolhe exatamente
aquela que eu estou clicando, deveria escolher exatamente a pagina que eu estou clicando, isso
confunde muito." A tela mostrava a folha 6 (as páginas 11 e 12) e a tira marcava só a 11; depois a
folha 5 (9 e 10) e a tira marcava só a 10. Pedido da gerente: "A miniatura marcada tem que ser a da
página ou folha que está na tela."

O que se mede: com a folha dividida e a vista "Duas lado a lado" no Dividir (a folha inteira na
tela, D-601), clicar na miniatura de qualquer uma das duas metades leva à folha e marca as DUAS
miniaturas dela (e nenhuma outra). Com "Uma página", só a da metade à vista (como antes, D-605). Nas
outras ferramentas com "Duas lado a lado", clicar numa página dos pares escolhe exatamente ela, e a
miniatura marcada é a dela. Em `d2567fab` o primeiro falha (só uma das duas ficava marcada).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_decisoes_dividir_metade import (  # noqa: E402,F401
    _assentar,
    _no_dividir_dividida,
    app,
    janela,
    pasta,
    precisa_da_dll,
)
from ui.widgets.paginas_rolando import DUAS, UMA  # noqa: E402


def _marcadas(tela) -> list[int]:
    return [i for i, m in enumerate(tela.tira._miniaturas) if m.selecionada]


@precisa_da_dll
def test_reversao_d612_dividir_duas_lado_a_lado_marca_as_duas_metades_da_folha(janela, tmp_path):
    """Folha 1 dividida (miniaturas 0 e 1), folhas 2 e 3 inteiras (2 e 3). Em "Duas lado a lado":
    clicar na miniatura da direita da folha 1 → a folha 1 na tela e as miniaturas 0 e 1 marcadas;
    clicar na da esquerda → as mesmas duas; clicar na folha 2 → só a 2."""
    tela = _no_dividir_dividida(janela, tmp_path)
    tela.botao_nao_dividir.click()                       # "dividir esta" na folha 1
    _assentar(10)
    tela.definir_mostrar(DUAS)
    _assentar(5)
    tira = tela.tira
    assert len(tira._miniaturas) == 4
    tira.selecionada.emit(1)                             # a metade da direita da folha 1
    _assentar()
    assert tela.indice_folha == 0
    assert _marcadas(tela) == [0, 1], _marcadas(tela)
    tira.selecionada.emit(0)                             # a metade da esquerda
    _assentar()
    assert tela.indice_folha == 0 and _marcadas(tela) == [0, 1]
    tira.selecionada.emit(2)                             # a folha 2, inteira
    _assentar()
    assert tela.indice_folha == 1 and _marcadas(tela) == [2]


@precisa_da_dll
def test_d612_dividir_uma_pagina_marca_so_a_metade_a_vista(janela, tmp_path):
    """Guarda (D-601, D-605): com "Uma página", a tela mostra só a metade, e só a miniatura dela
    fica marcada."""
    tela = _no_dividir_dividida(janela, tmp_path)
    tela.botao_nao_dividir.click()
    _assentar(10)
    tela.definir_mostrar(UMA)
    tela.tira.selecionada.emit(1)
    _assentar()
    assert _marcadas(tela) == [1]


@precisa_da_dll
def test_d612_nos_pares_clicar_na_pagina_escolhe_exatamente_ela(janela, tmp_path):
    """Outras ferramentas com "Duas lado a lado": clicar em cada página dos pares (na tela) escolhe
    exatamente ela, e a miniatura marcada é a dela. Também com o Mover (a peça dele por cima)."""
    from tests.test_decisoes_mover_lado import _arrastar_na_tela

    tela = _no_dividir_dividida(janela, tmp_path)
    tela.botao_nao_dividir.click()
    _assentar(10)
    for ferramenta in ("mao", "mover"):
        tela.escolher_ferramenta(ferramenta)
        tela.definir_mostrar(DUAS)
        _assentar(5)
        pares = tela.lado_a_lado
        vista = tela.vista_da_pagina.currentWidget()
        for posicao, ret in list(pares.retangulos()):
            indice = pares.indices[posicao]
            ret = next(r for p, r in pares.retangulos() if p == posicao)
            pares.ensureVisible(ret.center().x(), ret.center().y())
            _assentar()
            ponto = pares.folhas.mapTo(vista, ret.center())
            # longe dos cantos do Mover: um quarto para dentro do lado de fora da página
            ponto.setY(ponto.y() - ret.height() // 4)
            _arrastar_na_tela(tela, ponto, 0)
            assert tela.indice_pagina == indice, (ferramenta, posicao, indice, tela.indice_pagina)
            assert _marcadas(tela) == [indice]
