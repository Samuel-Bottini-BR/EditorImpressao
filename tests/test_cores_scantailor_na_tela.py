"""As caixinhas "Letras com a cor delas" e "Reduzir cores" na aba Filtro (item 2.11, 20/10/2026).

Controle mínimo (aparência do agente de layout): desmarcadas de fábrica;
"Letras com a cor delas" só aparece no Preto e branco; marcar é ação do
desfazer só desta página e refaz a prévia; "usar em todas" leva as duas.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import cores_scantailor as cs  # noqa: E402
from core.filtros import MELHORAR  # noqa: E402
from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures


def test_desmarcadas_de_fabrica(conferir):
    assert conferir.caixa_letras_com_a_cor.text() == "Letras com a cor delas"
    assert conferir.caixa_reduzir_cores.text() == "Reduzir cores"
    assert not conferir.caixa_letras_com_a_cor.isChecked()
    assert not conferir.caixa_reduzir_cores.isChecked()


def test_letras_so_no_preto_e_branco(conferir):
    assert not conferir.caixa_letras_com_a_cor.isHidden()
    conferir.ir_para_pagina(2)            # Melhorar
    assert conferir.projeto.paginas[2].filtro == MELHORAR
    assert conferir.caixa_letras_com_a_cor.isHidden()
    assert not conferir.caixa_reduzir_cores.isHidden()


def test_marcar_e_acao_do_desfazer_so_desta_pagina(conferir, monkeypatch):
    projeto = conferir.projeto
    jogadas_fora = []
    original = conferir.previas.invalidar
    monkeypatch.setattr(conferir.previas, "invalidar",
                        lambda indice=None: (jogadas_fora.append(indice), original(indice)))
    conferir.caixa_letras_com_a_cor.setChecked(True)
    assert projeto.paginas[0].letras_com_a_cor and not projeto.paginas[1].letras_com_a_cor
    assert 0 in jogadas_fora
    assert conferir.acoes.descricao_desfazer().endswith("Letras com a cor delas na página 1: marcada")
    conferir.caixa_reduzir_cores.setChecked(True)
    assert projeto.paginas[0].reduzir_cores
    conferir.desfazer()
    assert not projeto.paginas[0].reduzir_cores and not conferir.caixa_reduzir_cores.isChecked()
    conferir.desfazer()
    assert not projeto.paginas[0].letras_com_a_cor


def test_usar_em_todas_leva_as_duas(conferir):
    conferir.caixa_letras_com_a_cor.setChecked(True)
    conferir.caixa_reduzir_cores.setChecked(True)
    conferir._filtro_em_todas()
    assert all(p.letras_com_a_cor and p.reduzir_cores for p in conferir.projeto.paginas)


def test_textos_sem_emoji():
    for texto in (cs.ROTULO_LETRAS, cs.ROTULO_REDUZIR, cs.EXPLICACAO_LETRAS, cs.EXPLICACAO_REDUZIR):
        assert all(ord(c) < 0x2000 for c in texto)
