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


def _medidas_em_fila(angulos, monkeypatch=None):
    """Uma medida falsa do ScanTailor que devolve os ângulos na ordem das chamadas.

    Estabilizado na etapa 9b-1 (27/10/2026): a análise mede as folhas em vários trabalhadores ao
    mesmo tempo (item 2.16, core/nucleos.py), e a ordem das CHAMADAS deixava de ser a ordem das
    páginas quando duas linhas corriam juntas: o ângulo de 3° caía noutra página e o teste
    falhava às vezes (na rodada inteira do GitHub). Com `monkeypatch`, a análise fica com um
    trabalhador só (o laço de sempre, core/nucleos.em_ordem): a ordem das chamadas é a das
    páginas. O programa não muda."""
    from core import endireitar_scantailor as es
    from core import nucleos

    if monkeypatch is not None:
        monkeypatch.setattr(nucleos, "quantos_trabalhadores", lambda *_a, **_k: 1)
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
    monkeypatch.setattr(es, "medir_na_pagina", _medidas_em_fila([0.5, 0.45, 0.55, 0.5, 0.5, 3.0], monkeypatch))
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


# ------------------------------------------------------------------ o mínimo de 1 grau (decisão da gerente, 20-21/10)

def test_minimo_de_um_grau():
    """A conta pura do ScanTailor marca a página de 0,5° num livro quase todo
    reto; com o mínimo de 1° (o que vale no programa) ela não é marcada, e a
    de 5° continua."""
    reto = [0.0, 0.05, -0.05, 0.0, 0.02, 0.5]
    assert pd.diferentes(reto, pd.ENDIREITAR)[5] is True                  # ScanTailor puro
    assert pd.diferentes_e_longe(reto, pd.ENDIREITAR, 1.0)[5] is False
    torto = [0.0, 0.05, -0.05, 0.0, 0.02, 5.0]
    assert pd.diferentes_e_longe(torto, pd.ENDIREITAR, 1.0)[5] is True
    assert pd.AFASTAMENTO_MINIMO_DO_ANGULO == 1.0
    # mínimo 0 = a conta pura do ScanTailor
    assert pd.diferentes_e_longe(reto, pd.ENDIREITAR, 0.0) == pd.diferentes(reto, pd.ENDIREITAR)
    assert pd.diferentes_e_longe([None, None, None], pd.ENDIREITAR, 1.0) == [False] * 3


def test_na_analise_pouco_torta_nao_ganha_o_aviso(tmp_path, monkeypatch):
    from core import endireitar_scantailor as es
    from core import pipeline
    from modelos import Projeto

    caminho = _livro(tmp_path, 6)
    monkeypatch.setattr(es, "medir_na_pagina", _medidas_em_fila([0.5, 0.48, 0.52, 0.5, 0.5, 1.2], monkeypatch))
    projeto = Projeto(caminho_entrada=caminho, dividir_folhas=False)
    pipeline.analisar_projeto(projeto)
    assert not any(analise.ANGULO_DIFERENTE_DAS_OUTRAS in p.alertas for p in projeto.paginas)
