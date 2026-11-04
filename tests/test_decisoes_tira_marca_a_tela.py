"""D-612, conserto do teste do Samuel (04/11/2026, prints a-75 e a-76, Dividir em "Duas lado a
lado"): "quando eu clico em uma pagina estado o lado a lado escolhido, ele não escolhe exatamente
aquela que eu estou clicando, deveria escolher exatamente a pagina que eu estou clicando, isso
confunde muito." A tela mostrava a folha 6 (as páginas 11 e 12) e a tira marcava só a 11; depois a
folha 5 (9 e 10) e a tira marcava só a 10. Pedido da gerente: "A miniatura marcada tem que ser a da
página ou folha que está na tela."

O que se mede: com a folha dividida e a vista "Duas lado a lado" no Dividir (a folha inteira na
tela, D-601), a tira junta as duas metades da folha (D-611 atualizada: "SIm, mas tem que verificar
se vai ficar assim em todo os lugares né? a miniatura corresponder com o numero real"), e clicar
numa delas leva à folha e marca só ela, dentro do par da folha (a gerente: "Deixar uma só miniatura
marcada, dentro do par que está na tela, está certo."). Com "Uma página", só a da metade à vista
(como antes, D-605). Nas
outras ferramentas com "Duas lado a lado", clicar numa página dos pares escolhe exatamente ela, e a
miniatura marcada é a dela. Em `d2567fab` o primeiro falha (a tira juntava 1 | 2-3, e não as duas metades da folha).
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
def test_reversao_d612_dividir_duas_lado_a_lado_a_marcada_fica_no_par_da_folha(janela, tmp_path):
    """Folha 1 dividida (miniaturas 0 e 1), folhas 2 e 3 inteiras (2 e 3). Em "Duas lado a lado":
    a tira junta as duas metades da folha 1 (o par da tela grande, D-611 atualizada); clicar na
    miniatura da direita da folha 1 → a folha 1 na tela e só ela marcada, dentro do par da folha;
    clicar na folha 2 → só a 2, sozinha (folha inteira). Resposta da gerente: "Deixar uma só
    miniatura marcada, dentro do par que está na tela, está certo." """
    tela = _no_dividir_dividida(janela, tmp_path)
    tela.botao_nao_dividir.click()                       # "dividir esta" na folha 1
    _assentar(10)
    tela.definir_mostrar(DUAS)
    _assentar(5)
    tira = tela.tira
    assert len(tira._miniaturas) == 4
    linha0, coluna0 = tira.posicao(0)
    linha1, coluna1 = tira.posicao(1)
    assert (linha0, coluna0 // 3) == (linha1, coluna1 // 3), "as duas metades da folha 1 juntas"
    assert tira.posicao(2)[1] // 3 != coluna1 // 3
    tira.selecionada.emit(1)                             # a metade da direita da folha 1
    _assentar()
    assert tela.indice_folha == 0
    assert _marcadas(tela) == [1], _marcadas(tela)
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
