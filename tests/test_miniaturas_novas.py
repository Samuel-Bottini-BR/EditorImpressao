"""As miniaturas com o cabeçalho "PÁGINAS" e a tela "Todas as páginas" (etapa 5 do layout, 21/10/2026).

Rodada 7 (204 A, 205), rodada 8 (301 A), rodada 13 (801 A: "Confirmar e processar" desce para a barra
de baixo com as miniaturas fechadas ou de lado; 808 A: "ver todas" no cabeçalho) e rodada 14 (901 A:
"Todas as páginas" abre uma a uma).
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_gravura_na_aba_marcar import app, conferir, livro  # noqa: F401, E402 - fixtures


def test_cabecalho_paginas_com_seta_pontinhos_alca_e_ver_todas(conferir):  # noqa: F811
    m = conferir.miniaturas
    assert m.titulo.text() == "PÁGINAS"
    for peca in (m.alca, m.seta, m.pontos, m.botao_ver_todas):
        assert peca.parent() is not None and not peca.isHidden()
    assert [a.text() for a in m.menu.actions() if not a.isSeparator()] == [
        "Ver em pares", "Lugar", "Fechar as miniaturas"]


def test_processar_ao_lado_e_na_barra_de_baixo(conferir):  # noqa: F811
    from ui.widgets.miniaturas import DIREITA, EMBAIXO, ESQUERDA

    botao, m = conferir.botao_processar, conferir.miniaturas
    assert conferir.lugar_embaixo.isAncestorOf(botao)
    m.seta.click()                                          # fechou: desce (801 A)
    assert not m.aberta and not conferir.lugar_embaixo.isAncestorOf(botao)
    m.seta.click()
    assert m.aberta and conferir.lugar_embaixo.isAncestorOf(botao)
    for lugar in (ESQUERDA, DIREITA):
        conferir._por_as_miniaturas(lugar)
        assert m.lugar == lugar and not conferir.lugar_embaixo.isAncestorOf(botao)
        assert m.tira.vertical
    conferir._por_as_miniaturas(EMBAIXO)
    assert conferir.lugar_embaixo.isAncestorOf(botao) and not m.tira.vertical


def test_em_pares_como_no_livro_aberto(conferir):  # noqa: F811
    tira = conferir.tira
    tira.definir_arranjo(False, True)
    assert [tira.posicao(i) for i in range(5)] == [(0, 1), (0, 3), (0, 4), (0, 6), (0, 7)]
    tira.definir_arranjo(True, True)
    assert [tira.posicao(i) for i in range(5)] == [(0, 1), (1, 0), (1, 1), (2, 0), (2, 1)]
    tira.definir_arranjo(False, False)
    assert tira.posicao(3) == (0, 3)


def test_ver_todas_abre_uma_a_uma_e_volta_na_pagina(conferir):  # noqa: F811
    conferir.abrir_todas_as_paginas()
    todas = conferir.todas
    assert conferir.pilha_da_tela.currentWidget() is todas and todas.vista == "uma"
    assert len(todas.quadros) == len(conferir.projeto.paginas)
    todas.definir_vista("pares")
    assert len(todas.quadros) == 1 + (len(conferir.projeto.paginas) - 1 + 1) // 2
    todas.definir_vista("uma")
    todas.quadros[2].clicado.emit(2)
    assert conferir.pilha_da_tela.currentWidget() is conferir.trabalho
    assert conferir.indice_pagina == 2
    conferir.abrir_todas_as_paginas()
    assert conferir.todas.vista == "uma", "abre sempre uma a uma (901 A)"
    conferir.todas.botao_voltar.click()
    assert conferir.pilha_da_tela.currentWidget() is conferir.trabalho


def test_as_miniaturas_ficam_para_o_proximo_livro(app, monkeypatch):  # noqa: F811
    """Samuel, 21/10/2026 ("Sim, lembrar para todos os livros"): o lugar das
    miniaturas, se estão abertas e se estão em pares ficam guardados
    (configuracoes.json, "miniaturas") e a próxima tela abre igual; valor
    estranho volta ao de fábrica."""
    import configuracoes
    from ui.tela_conferir import TelaConferir, miniaturas_guardadas
    from ui.widgets.miniaturas import DIREITA, EMBAIXO, ESQUERDA

    guardado = {}
    monkeypatch.setattr(configuracoes, "ler", lambda chave: guardado.get(chave))
    monkeypatch.setattr(configuracoes, "escrever", lambda chave, valor: guardado.__setitem__(chave, valor))

    primeira = TelaConferir()
    m = primeira.miniaturas
    assert (m.lugar, m.aberta, m.em_pares) == (EMBAIXO, True, False), "de fábrica"
    assert "miniaturas" not in guardado, "abrir a tela não grava nada"
    m.lugar_pedido.emit(ESQUERDA)                 # o "Lugar" dos três pontinhos
    m.acao_em_pares.setChecked(True)              # "Ver em pares"
    m.seta.click()                                # fechou
    assert guardado["miniaturas"] == {"lugar": ESQUERDA, "aberta": False, "em_pares": True}

    outra = TelaConferir()
    n = outra.miniaturas
    assert (n.lugar, n.aberta, n.em_pares) == (ESQUERDA, False, True)
    assert not outra.lugar_esquerda.isHidden() and outra.lugar_esquerda.isAncestorOf(n)
    assert not outra.lugar_embaixo.isAncestorOf(outra.botao_processar), "fechada de lado: processar na barra"

    primeira._por_as_miniaturas(DIREITA)
    assert guardado["miniaturas"]["lugar"] == DIREITA
    guardado["miniaturas"] = {"lugar": "no teto", "aberta": "sim", "em_pares": 1}
    assert miniaturas_guardadas() == {"lugar": EMBAIXO, "aberta": True, "em_pares": False}
    guardado["miniaturas"] = "quebrado"
    assert miniaturas_guardadas() == {"lugar": EMBAIXO, "aberta": True, "em_pares": False}
    assert configuracoes.PADROES["miniaturas"] == miniaturas_guardadas()
