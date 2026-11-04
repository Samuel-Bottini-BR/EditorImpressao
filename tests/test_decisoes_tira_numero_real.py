"""D-611 atualizada (04/11/2026). Pergunta ao Samuel: "no Dividir, a tela grande mostra a folha 6,
com as páginas 11 e 12, mas a tira junta a 10 com a 11. Quer que a tira junte igual à tela grande, a
11 com a 12?" → "SIm, mas tem que verificar se vai ficar assim em todo os lugares né? a miniatura
corresponder com o numero real". E o defeito dos prints a-75/a-76 (D-612): "deveria escolher
exatamente a pagina que eu estou clicando, isso confunde muito."

O que se confere, percorrendo as ferramentas (Mão, Mover, Cortar, Endireitar, Retângulo e Dividir) e
as duas vistas ("Uma página" e "Duas lado a lado"), num livro com a capa aberta (D-616: a página 1 é
a capa, a contracapa vai para o fim) e com a ordem mudada à mão (D-615: arrastar uma miniatura):
  - o número embaixo de cada miniatura é o número de verdade da página (a posição dela no livro, o
    mesmo de "página N de M"; no Dividir, também o da página);
  - clicar numa miniatura leva exatamente àquela página (a da vez é ela; no Dividir, a folha dela);
  - a miniatura marcada é a da página que está na tela (uma só);
  - com "Duas lado a lado", a tira junta os mesmos pares da tela grande: nas outras ferramentas, os
    do livro aberto que vai sair (a 1 sozinha, 2-3, 4-5...; a página tirada do livro fica sozinha);
    no Dividir, as duas metades da mesma folha;
  - clicar numa página dos pares escolhe exatamente ela.
Em `33aa7cc8` os testes de reversão falham (no Dividir a tira juntava 1 | 2-3 | 4-5).
"""

from __future__ import annotations

import pytest

pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint  # noqa: E402

from core import automatico as A  # noqa: E402
from tests.test_decisoes_capa_aberta import _livro, _rodar  # noqa: E402
from tests.test_decisoes_dividir import app, janela, pasta  # noqa: E402,F401
from tests.test_decisoes_ordem_folhas import _arrastar, _assentar  # noqa: E402
from ui.widgets.paginas_rolando import DUAS, UMA  # noqa: E402

FERRAMENTAS = ("mao", "mover", "cortar", "endireitar", "retangulo")


def _livro_pronto(janela, tmp_path, folhas: int = 4):
    """Livro de folhas abertas, dividido pelo Automático com "A 1ª folha é a capa aberta" (D-616),
    e a última página arrastada para ser a 3ª (D-615)."""
    janela.resize(1400, 900)
    janela.show()
    janela.abrir_livro(_livro(tmp_path, folhas))
    assert _rodar(janela, [A.DIVIDIR], {"capa_aberta": True})
    tela = janela.tela_conferir
    tela.escolher_ferramenta("mao")
    _assentar()
    projeto = janela.projeto
    assert (projeto.paginas[0].folha, projeto.paginas[0].metade) == (0, "direita")   # a capa
    _arrastar(tela, len(projeto.paginas) - 1, 2)                           # a contracapa → a 3ª
    assert (projeto.paginas[2].folha, projeto.paginas[2].metade) == (0, "esquerda")
    return tela, projeto


def _rotulos(tira) -> list[int]:
    return [m.rotulo_numero if m.rotulo_numero is not None else m.numero for m in tira._miniaturas]


def _marcadas(tira) -> list[int]:
    return [i for i, m in enumerate(tira._miniaturas) if m.selecionada]


def _pares_da_tira(tira) -> list[list[int]]:
    """Os quadros juntos na tira (o mesmo par: a mesma linha e o mesmo bloco de colunas)."""
    blocos: dict[tuple[int, int], list[int]] = {}
    for i in range(len(tira._miniaturas)):
        linha, coluna = tira.posicao(i)
        blocos.setdefault((linha, coluna // 3), []).append(i)
    return sorted(blocos.values())


def _pares_da_tela(tela) -> list[list[int]]:
    """Os pares da tela grande ("Duas lado a lado" fora do Dividir), em índices de página."""
    pares = tela.lado_a_lado
    linhas: dict[int, list[int]] = {}
    for posicao, _ret in pares.retangulos():
        linhas.setdefault(pares._linha_de(posicao), []).append(pares.indices[posicao])
    return sorted(sorted(v) for v in linhas.values())


def _confere_as_paginas(tela, projeto, ferramenta, mostrar):
    tira = tela.tira
    n = len(projeto.paginas)
    assert _rotulos(tira) == list(range(1, n + 1)), (ferramenta, mostrar, _rotulos(tira))
    for i in range(n):
        tira.selecionada.emit(i)
        _assentar()
        assert tela.indice_pagina == i, (ferramenta, mostrar, i)
        assert tela.rotulo_da_pagina.text().startswith(f"página {i + 1} de"), tela.rotulo_da_pagina.text()
        assert _marcadas(tira) == [i], (ferramenta, mostrar, i, _marcadas(tira))
        if mostrar == DUAS and not projeto.paginas[i].apagada:
            assert tela.lado_a_lado.indice_da_vez() == i
    if mostrar == DUAS:
        # os mesmos pares da tela grande (a tirada do livro sozinha na tira e fora da tela)
        da_tira = [p for p in _pares_da_tira(tira)
                   if not all(projeto.paginas[i].apagada for i in p)]
        assert da_tira == _pares_da_tela(tela), (ferramenta, da_tira, _pares_da_tela(tela))


def test_reversao_d611_em_todas_as_ferramentas_e_vistas_a_miniatura_e_a_pagina_de_verdade(
        janela, tmp_path):
    tela, projeto = _livro_pronto(janela, tmp_path)
    for mostrar in (UMA, DUAS):
        for ferramenta in FERRAMENTAS:
            tela.escolher_ferramenta(ferramenta)
            tela.definir_mostrar(mostrar)
            _assentar(3)
            _confere_as_paginas(tela, projeto, ferramenta, mostrar)
    # uma página tirada do livro: a tira fica com os pares da tela grande
    tela.definir_mostrar(UMA)
    tela.ir_para_pagina(3)
    tela.apagar_pagina()
    assert projeto.paginas[3].apagada
    tela.definir_mostrar(DUAS)
    _assentar(3)
    _confere_as_paginas(tela, projeto, "mao (com a 4 tirada)", DUAS)


def test_reversao_d611_no_dividir_a_tira_junta_pela_folha_e_o_numero_e_o_da_pagina(janela, tmp_path):
    """Dividir: cada miniatura tem o número da página dela; clicar leva à folha dela e marca só ela;
    com "Duas lado a lado" a tira junta as duas metades da mesma folha (as que ficaram longe, pela
    capa aberta e pelo arrastar, ficam sozinhas)."""
    tela, projeto = _livro_pronto(janela, tmp_path)
    tela.escolher_ferramenta("dividir")
    for mostrar in (UMA, DUAS):
        tela.definir_mostrar(mostrar)
        _assentar(3)
        tira = tela.tira
        passos = tela._passos_do_dividir()
        assert _rotulos(tira) == [p + 1 for p in passos]
        for k, posicao in enumerate(passos):
            tira.selecionada.emit(k)
            _assentar()
            assert tela.indice_pagina == posicao
            assert tela.indice_folha == projeto.paginas[posicao].folha
            assert _marcadas(tira) == [k], (mostrar, k, _marcadas(tira))
    # "Duas lado a lado": os pares da tira são as folhas (as metades seguidas da mesma folha)
    esperados = []
    for k, posicao in enumerate(passos):
        folha = projeto.paginas[posicao].folha
        if esperados and projeto.paginas[passos[esperados[-1][-1]]].folha == folha and len(esperados[-1]) == 1:
            esperados[-1].append(k)
        else:
            esperados.append([k])
    assert _pares_da_tira(tela.tira) == sorted(esperados)
    folhas_juntas = [p for p in esperados if len(p) == 2]
    assert folhas_juntas, "nenhuma folha com as duas metades juntas"


def test_d611_clicar_nas_paginas_dos_pares_escolhe_exatamente_ela(janela, tmp_path):
    """Nos pares da tela grande (Mão e Mover), clicar em cada página escolhe exatamente ela, e a
    miniatura marcada é a dela."""
    from tests.test_decisoes_mover_lado import _arrastar_na_tela

    tela, projeto = _livro_pronto(janela, tmp_path)
    for ferramenta in ("mao", "mover"):
        tela.escolher_ferramenta(ferramenta)
        tela.definir_mostrar(DUAS)
        _assentar(5)
        pares = tela.lado_a_lado
        vista = tela.vista_da_pagina.currentWidget()
        for posicao, _ret in list(pares.retangulos()):
            indice = pares.indices[posicao]
            ret = next(r for p, r in pares.retangulos() if p == posicao)
            pares.ensureVisible(ret.center().x(), ret.center().y())
            _assentar()
            ponto = pares.folhas.mapTo(vista, ret.center()) - QPoint(0, ret.height() // 4)
            _arrastar_na_tela(tela, ponto, 0)
            assert tela.indice_pagina == indice, (ferramenta, posicao, indice)
            assert _marcadas(tela.tira) == [indice]
