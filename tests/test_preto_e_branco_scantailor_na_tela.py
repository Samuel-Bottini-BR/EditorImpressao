"""Os dez jeitos do ScanTailor na lista "Algoritmo" da aba Filtro (item 2.8, 20/10/2026).

Controle mínimo (a aparência é do agente de layout): os dez entram depois dos
três de sempre, separados por uma linha; "Automático" continua o primeiro e o
de fábrica; escolher é ação do desfazer só da página, e a prévia é refeita.
Testes de máquina, sem janela na tela (tests/conftest.py).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import preto_e_branco_scantailor as pbst  # noqa: E402
from core.filtros import ALGORITMOS_PB, NOMES_DOS_ALGORITMOS_PB, PRETO_E_BRANCO  # noqa: E402
from tests.test_limpar_pontinhos_na_tela import conferir  # noqa: F401, E402 - fixture
from tests.test_mesmo_livro_outro_caminho import _pdf, app, pasta  # noqa: F401, E402 - fixtures


def _itens(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


def test_a_lista_tem_os_de_sempre_e_os_dez_do_scantailor(conferir):
    seletor = conferir.seletor_algoritmo_pb
    itens = [t for t in _itens(seletor) if t]          # a linha separadora não tem texto
    assert itens == (["Automático"] + [NOMES_DOS_ALGORITMOS_PB[c] for c in ALGORITMOS_PB]
                     + [pbst.NOMES_NA_TELA[c] for c in pbst.CODIGOS])
    assert len([c for c in pbst.CODIGOS if seletor.findData(c) >= 0]) == 10


def test_de_fabrica_fica_no_automatico(conferir):
    assert conferir.projeto.paginas[0].algoritmo_preto_branco == "auto"
    assert conferir.seletor_algoritmo_pb.currentData() == "auto"


def test_escolher_um_do_scantailor_e_acao_do_desfazer(conferir, monkeypatch):
    projeto, seletor = conferir.projeto, conferir.seletor_algoritmo_pb
    pagina, outra = projeto.paginas[0], projeto.paginas[1]
    assert pagina.filtro == PRETO_E_BRANCO
    # a chave da prévia não leva o algoritmo (é assim desde setembro): quem
    # refaz a prévia é a ação, que joga fora a prévia da página (_registrar)
    jogadas_fora = []
    original = conferir.previas.invalidar
    monkeypatch.setattr(conferir.previas, "invalidar",
                        lambda indice=None: (jogadas_fora.append(indice), original(indice)))
    seletor.setCurrentIndex(seletor.findData("st_sauvola"))
    assert pagina.algoritmo_preto_branco == "st_sauvola" and outra.algoritmo_preto_branco == "auto"
    assert 0 in jogadas_fora, "a prévia tinha de ser refeita"
    assert conferir.acoes.descricao_desfazer().endswith("Sauvola do ScanTailor")
    conferir.desfazer()
    assert pagina.algoritmo_preto_branco == "auto" and seletor.currentData() == "auto"


def test_textos_com_acento_e_sem_emoji():
    for texto in list(pbst.NOMES_NA_TELA.values()) + [pbst.EXPLICACAO_NA_TELA]:
        assert all(ord(c) < 0x2000 for c in texto), texto
    assert "Automático" in pbst.EXPLICACAO_NA_TELA and "páginas" not in pbst.NOMES_NA_TELA.values()
