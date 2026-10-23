"""A caixinha "Letra clara em fundo escuro" na aba Filtro (item 2.9, 20/10/2026).

Controle mínimo (a aparência é do agente de layout): desmarcada de fábrica;
mostra o que vale na página sem gravar; marcar é ação do desfazer SÓ desta
página e refaz a prévia; some junto com o bloco AJUSTE no Original.
Testes de máquina, sem janela na tela (tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import claro_no_escuro as cne  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures


def test_desmarcada_de_fabrica_com_o_texto_certo(conferir):
    caixa = conferir.caixa_claro_no_escuro
    assert caixa.text() == "Letra clara em fundo escuro"
    assert not caixa.isChecked()
    assert not conferir.projeto.paginas[0].claro_no_escuro


def test_marcar_e_acao_do_desfazer_so_desta_pagina(conferir, monkeypatch):
    projeto, caixa = conferir.projeto, conferir.caixa_claro_no_escuro
    jogadas_fora = []
    original = conferir.previas.invalidar
    monkeypatch.setattr(conferir.previas, "invalidar",
                        lambda indice=None: (jogadas_fora.append(indice), original(indice)))
    caixa.setChecked(True)
    assert projeto.paginas[0].claro_no_escuro and not projeto.paginas[1].claro_no_escuro
    assert 0 in jogadas_fora, "a prévia tinha de ser refeita"
    assert conferir.acoes.descricao_desfazer().endswith(
        "Letra clara em fundo escuro na página 1: marcada")
    conferir.desfazer()
    assert not projeto.paginas[0].claro_no_escuro and not caixa.isChecked()
    conferir.refazer()
    assert projeto.paginas[0].claro_no_escuro and caixa.isChecked()


def test_mostra_o_que_vale_em_cada_pagina_sem_gravar(conferir):
    conferir.projeto.paginas[1].claro_no_escuro = True
    conferir.ir_para_pagina(1)
    assert conferir.caixa_claro_no_escuro.isChecked()
    conferir.ir_para_pagina(0)
    assert not conferir.caixa_claro_no_escuro.isChecked()
    assert not conferir.acoes.pode_desfazer, "mostrar não pode virar ação"


def test_some_no_original(conferir):
    conferir.projeto.paginas[0].filtro = ORIGINAL
    conferir.atualizar()
    assert conferir.bloco_ajuste.isHidden(), "a caixinha mora no bloco AJUSTE, que some no Original"


def test_textos_sem_emoji():
    for texto in (cne.ROTULO_NA_TELA, cne.EXPLICACAO_NA_TELA, cne.FRASE_DO_DESFAZER):
        assert all(ord(c) < 0x2000 for c in texto)
