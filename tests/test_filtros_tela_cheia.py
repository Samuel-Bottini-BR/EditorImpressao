"""A tela cheia dos filtros (etapa 6 do layout; rodada 11, 601 A; rodada 10, 503; rodada 14, 904 A)."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from tests.test_misto_consertos import conferir_original, pasta  # noqa: F401, E402 - fixtures
from tests.test_gravura_na_aba_marcar import app  # noqa: F401, E402 - fixture


def _tela_cheia(tela):
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia
    return FiltrosEmTelaCheia(tela)


def test_abre_pelo_icone_do_titulo_do_painel(conferir_original, monkeypatch):  # noqa: F811
    from ui.widgets.filtros_tela_cheia import FiltrosEmTelaCheia

    abertas = []
    monkeypatch.setattr(FiltrosEmTelaCheia, "exec", lambda self: abertas.append(self) or 0)
    conferir_original.paineis.filtro_da_pagina.botao_tela_cheia.click()
    assert len(abertas) == 1
    dialogo = abertas[0]
    assert dialogo.titulo.text() == "Filtros da página 1"
    assert list(dialogo.cartoes) == dialogo.filtros and len(dialogo.filtros) >= 4
    assert not dialogo.chave_comparar.isChecked(), "a chave começa desligada (601 A)"


def test_escolher_nao_muda_a_pagina_e_usar_muda(conferir_original):  # noqa: F811
    from core.filtros import MELHORAR, ORIGINAL

    tela = conferir_original
    pagina = tela.projeto.paginas[0]
    assert pagina.filtro == ORIGINAL
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MELHORAR)
    assert pagina.filtro == ORIGINAL, "escolher na tela cheia só mostra"
    assert dialogo.botao_usar.text() == "Usar Melhorar"
    dialogo._ajuste_mudou(80)
    dialogo.usar()
    assert pagina.filtro == MELHORAR and pagina.clareza_melhorar == 80
    tela.desfazer()
    assert pagina.clareza_melhorar != 80
    tela.desfazer()
    assert pagina.filtro == ORIGINAL


def test_aplicar_em_todas(conferir_original):  # noqa: F811
    from core.filtros import MAGICO_PRO

    tela = conferir_original
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MAGICO_PRO)
    dialogo.botoes_alcance["todas"].click()
    dialogo.usar()
    assert all(p.filtro == MAGICO_PRO for p in tela.projeto.paginas)


def test_comparar_com_o_original_sem_outro_filtro_avisa(conferir_original):  # noqa: F811
    from core.filtros import ORIGINAL, PRETO_E_BRANCO

    dialogo = _tela_cheia(conferir_original)
    dialogo.escolher(ORIGINAL)
    dialogo.chave_comparar.setChecked(True)
    assert "outro filtro" in dialogo.vista.aviso and not dialogo.vista.comparando
    dialogo.escolher(PRETO_E_BRANCO)
    assert dialogo.vista.aviso == ""
    dialogo.reject()


def test_fechar_sem_mudar_nao_muda(conferir_original):  # noqa: F811
    from core.filtros import MELHORAR

    tela = conferir_original
    antes = [p.filtro for p in tela.projeto.paginas]
    dialogo = _tela_cheia(tela)
    dialogo.escolher(MELHORAR)
    dialogo.botao_sem_mudar.click()
    assert [p.filtro for p in tela.projeto.paginas] == antes
    assert not tela.acoes.pode_desfazer
