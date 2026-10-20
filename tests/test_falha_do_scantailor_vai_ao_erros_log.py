"""Teste de reversão: a falha das ferramentas do ScanTailor chega ao erros.log.

Bug (verificador, 20/10/2026, parecer do 2.8 em `relatorios/conferir/2.8-verificado-2026-10-20/`):
quando o preto e branco do ScanTailor falha (memória, DLL), a página cai no
"Automático", mas o motivo ia só para o `logging` do Python, que o programa
não grava em arquivo nenhum - o erros.log ficava vazio, e a queda não deixava
rastro. O endireitar do ScanTailor tinha o mesmo padrão (e o limpar pontinhos
e as cores, do mesmo jeito). Conserto: os quatro "avisar uma vez" também
gravam com registro.registrar_erro, como o detector de gravura (item 1.2).

No código antigo os quatro testes falham (nada é gravado); no novo, passam.
"""

from __future__ import annotations

import pytest

import registro
from core import cores_scantailor as cs
from core import endireitar_scantailor as es
from core import pontinhos_scantailor as ps
from core import preto_e_branco_scantailor as pbst


@pytest.fixture
def gravados(monkeypatch):
    anotados: list[tuple[str, str]] = []
    monkeypatch.setattr(registro, "registrar_erro", lambda origem, detalhe: anotados.append((origem, detalhe)))
    for modulo in (pbst, cs, ps, es):
        monkeypatch.setattr(modulo, "_AVISADOS", set())
    return anotados


def test_preto_e_branco_do_scantailor(gravados):
    pbst._avisar_uma_vez("Faltou memória para o preto e branco desta página.", "código 2")
    assert gravados and "Faltou memória" in gravados[0][1] and "código 2" in gravados[0][1]


def test_endireitar_do_scantailor(gravados):
    es.avisar_uma_vez(es.Medida(None, motivo="A DLL não abriu.", detalhe_tecnico="WinError 126"))
    assert gravados and "A DLL não abriu." in gravados[0][1]


def test_limpar_pontinhos_do_scantailor(gravados):
    ps._avisar_uma_vez("A DLL não abriu.", "WinError 126")
    assert gravados and "WinError 126" in gravados[0][1]


def test_cores_do_scantailor(gravados):
    cs._avisar_uma_vez("Faltou memória para as cores desta página.", "código 2")
    assert gravados and "Faltou memória" in gravados[0][1]


def test_uma_vez_por_sessao(gravados):
    for _ in range(3):
        pbst._avisar_uma_vez("mesmo motivo", "mesmo detalhe")
    assert len(gravados) == 1
