"""A lista "Desentortar perto da lombada" no Propriedades do Endireitar (item 2.12, 21/10/2026).

Controle mínimo (a aparência é do agente de layout): "Desligado" de fábrica;
mostra o que vale na página sem gravar; trocar é ação do desfazer SÓ desta
página e refaz a prévia; a chave do cache da prévia muda com ele.
Testes de máquina, sem janela na tela (tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import desentortar_scantailor as ds  # noqa: E402
from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures


def _itens(combo):
    return [combo.itemText(i) for i in range(combo.count())]


def test_desligado_de_fabrica_com_os_textos_certos(conferir):
    combo = conferir.combo_desentortar
    assert _itens(combo) == ["Desligado", "Automático (pelas linhas do texto)",
                             "Pelas margens de cima e de baixo"]
    assert combo.currentData() == ds.DESLIGADO
    assert all(p.desentortar == ds.DESLIGADO for p in conferir.projeto.paginas)


def test_trocar_e_acao_do_desfazer_so_desta_pagina(conferir, monkeypatch):
    projeto, combo = conferir.projeto, conferir.combo_desentortar
    jogadas_fora = []
    original = conferir.previas.invalidar
    monkeypatch.setattr(conferir.previas, "invalidar",
                        lambda indice=None: (jogadas_fora.append(indice), original(indice)))
    combo.setCurrentIndex(combo.findData(ds.AUTOMATICO))
    assert projeto.paginas[0].desentortar == ds.AUTOMATICO
    assert projeto.paginas[1].desentortar == ds.DESLIGADO
    assert 0 in jogadas_fora, "a prévia tinha de ser refeita"
    assert conferir.acoes.descricao_desfazer().endswith(
        "Desentortar na página 1: Automático (pelas linhas do texto)")
    conferir.desfazer()
    assert projeto.paginas[0].desentortar == ds.DESLIGADO
    assert combo.currentData() == ds.DESLIGADO
    conferir.refazer()
    assert projeto.paginas[0].desentortar == ds.AUTOMATICO
    assert combo.currentData() == ds.AUTOMATICO


def test_mostra_o_que_vale_em_cada_pagina_sem_gravar(conferir):
    conferir.projeto.paginas[1].desentortar = ds.PELAS_MARGENS
    conferir.ir_para_pagina(1)
    assert conferir.combo_desentortar.currentData() == ds.PELAS_MARGENS
    conferir.ir_para_pagina(0)
    assert conferir.combo_desentortar.currentData() == ds.DESLIGADO
    assert not conferir.acoes.pode_desfazer, "mostrar não pode virar ação"


def test_a_chave_da_previa_muda_com_o_desentortar(conferir):
    previas = conferir.previas
    antes = previas.chave(0, 100)
    conferir.projeto.paginas[0].desentortar = ds.AUTOMATICO
    assert previas.chave(0, 100) != antes


def test_textos_sem_emoji():
    textos = [ds.ROTULO_NA_TELA, ds.EXPLICACAO_NA_TELA, ds.FRASE_DO_DESFAZER,
              *ds.ROTULOS_NA_TELA.values()]
    for texto in textos:
        assert all(ord(c) < 0x2000 for c in texto)
