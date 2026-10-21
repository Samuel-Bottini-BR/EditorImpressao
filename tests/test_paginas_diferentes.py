"""Destacar as páginas diferentes das outras, igual ao ScanTailor (item 2.15, 20/10/2026).

Testes de máquina:
- a conta é a do DeviationProvider.h do ScanTailor (arquivo em src/, sem
  mudança, com soma): média, desvio-padrão amostral, "menos de 3 páginas
  nunca", página sem número, limite em % da média;
- os ajustes de fábrica são os do ScanTailor (1,5 e 1% no endireitar; 0,35
  e 1% no conteúdo e nas margens; destacar ligado);
- os números do conteúdo e das margens são os dos Settings.cpp dele;
- na análise, a página endireitada num ângulo muito diferente ganha o aviso
  "Inclinação diferente das outras"; com o endireitar desligado, nenhuma.
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from core import analise
from core import paginas_diferentes as pd

RAIZ = Path(__file__).resolve().parent.parent
FONTE = RAIZ / "terceiros" / "scantailor-advanced" / "src" / "core" / "DeviationProvider.h"


def test_a_conta_e_a_do_scantailor():
    """O arquivo copiado tem as linhas que o Python repete (se um dia o
    arquivo mudar, este teste e o das somas avisam)."""
    fonte = FONTE.read_text(encoding="utf-8")
    for linha in ("if (m_keyValueMap.size() < 3) {",
                  "return defaultVal;",
                  "> std::max((coefficient * m_standardDeviation), (threshold / 100) * m_meanValue));",
                  "m_standardDeviation = std::sqrt(differencesSum / (count - 1));",
                  "return std::abs(m_keyValueMap.at(key) - m_meanValue);"):
        assert linha in fonte, linha


def test_ajustes_de_fabrica_do_scantailor():
    # ApplicationSettings.cpp, linhas 18-24 (v1.2.1)
    assert pd.DESTACAR_DE_FABRICA is True
    assert (pd.ENDIREITAR.coeficiente, pd.ENDIREITAR.limite) == (1.5, 1.0)
    assert (pd.CONTEUDO.coeficiente, pd.CONTEUDO.limite) == (0.35, 1.0)
    assert (pd.MARGENS.coeficiente, pd.MARGENS.limite) == (0.35, 1.0)


def test_menos_de_tres_paginas_nunca():
    assert pd.diferentes([0.0, 9.0], pd.ENDIREITAR) == [False, False]
    # o "menos de 3" conta também a página sem número (m_keyValueMap.size())
    assert pd.diferentes([0.0, 0.1, None], pd.ENDIREITAR) == [False, False, False]


def test_a_conta_na_mao():
    valores = [0.2, 0.25, 0.3, 0.2, 0.25, 2.0]
    media = sum(valores) / 6
    desvio = math.sqrt(sum((v - media) ** 2 for v in valores) / 5)
    esperado = [abs(v - media) > max(1.5 * desvio, 0.01 * media) for v in valores]
    assert pd.diferentes(valores, pd.ENDIREITAR) == esperado == [False] * 5 + [True]
    assert pd.ordem_pela_diferenca(valores)[0] == 5


def test_limite_em_porcento_da_media():
    """Com quase nenhuma variação, quem decide é o limite (1% da média)."""
    valores = [100.0, 100.0, 100.0, 100.0, 100.5, 102.0]
    assert pd.diferentes(valores, pd.CONTEUDO) == [False, False, False, False, False, True]


def test_pagina_sem_numero():
    valores = [10.0, 10.0, 10.0, None]
    assert pd.diferentes(valores, pd.CONTEUDO) == [False] * 4
    # no conteúdo o ScanTailor passa defaultVal = true: página sem conteúdo conta como diferente
    assert pd.diferentes(valores, pd.CONTEUDO, sem_numero_conta=True)[3] is True
    assert pd.ordem_pela_diferenca(valores)[-1] == 3, "sem número vai para o fim"


def test_numeros_do_conteudo_e_das_margens():
    assert pd.valor_do_conteudo(30.0, 40.0) == 50.0
    assert math.isnan(pd.valor_do_conteudo(0.4, 40.0))            # toSize().isEmpty()
    assert math.isnan(pd.valor_do_conteudo(None, None))
    assert pd.valor_das_margens(10, 5, 20, 35) == 50.0           # (10+20, 5+35)
    assert math.isnan(pd.valor_do_angulo(None)) and pd.valor_do_angulo(1) == 1.0


def test_aviso_em_portugues_sem_emoji():
    alerta = analise.descrever(analise.ANGULO_DIFERENTE_DAS_OUTRAS)
    assert alerta.titulo == "Inclinação diferente das outras"
    assert all(ord(c) < 0x2000 for c in alerta.titulo + alerta.mensagem)


# ------------------------------------------------------------------ na análise

fitz = pytest.importorskip("fitz")


def _livro(pasta: Path, paginas: int) -> str:
    from tests.test_endireitar_no_programa import _pdf_torto

    destino = fitz.open()
    for i in range(paginas):
        um = fitz.open(_pdf_torto(pasta, 0.5, f"f{i}.pdf"))
        destino.insert_pdf(um)
        um.close()
    caminho = pasta / "livro.pdf"
    destino.save(str(caminho))
    destino.close()
    return str(caminho)


def _medidas_em_fila(angulos):
    from core import endireitar_scantailor as es

    fila = iter(angulos)

    def medir(*_args, **_kwargs):
        angulo = next(fila)
        return es.Medida(angulo, angulo, 5.0, True, 300.0)
    return medir


def test_na_analise_a_pagina_torta_ganha_o_aviso(tmp_path, monkeypatch):
    from core import endireitar_scantailor as es
    from core import pipeline
    from modelos import Projeto

    caminho = _livro(tmp_path, 6)
    monkeypatch.setattr(es, "medir_na_pagina", _medidas_em_fila([0.5, 0.45, 0.55, 0.5, 0.5, 3.0]))
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=False)
    pipeline.analisar_projeto(projeto)
    marcadas = [analise.ANGULO_DIFERENTE_DAS_OUTRAS in p.alertas for p in projeto.paginas]
    assert marcadas == [False] * 5 + [True]
    assert projeto.paginas[5].precisa_revisao


def test_endireitar_desligado_nenhuma(tmp_path):
    from core import pipeline
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=_livro(tmp_path, 4), dividir_folhas=False, endireitar=False)
    pipeline.analisar_projeto(projeto)
    assert not any(analise.ANGULO_DIFERENTE_DAS_OUTRAS in p.alertas for p in projeto.paginas)
