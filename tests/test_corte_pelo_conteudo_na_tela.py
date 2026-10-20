"""O corte que segue o conteúdo na tela (item 2.5): só o controle mínimo.

Decisões: G8 (a) (05/10/2026, "Trazer como opção [...], desligada - eu quero
pode escolher dentro do programa"); g8-moldura-tinta-fora ("ele avisa e da
opção e de mudar o corte e mostrar ele alargado com o que foi tirado") e
g9-pagina-muito-maior ("deixa essa folha de fora sozinho, e avisa"; o aviso
deixa pôr de volta), 13/10/2026.

Testes de máquina (nenhuma janela aparece; fixtures de
tests/test_mesmo_livro_outro_caminho.py):
- a caixinha da tela "O que fazer" nasce desmarcada, grava no livro e volta
  ao reabrir;
- o botão do aviso "Corte deixou algo de fora" grava o corte alargado como
  corte à mão, e o Ctrl+Z desfaz;
- o botão do aviso "Página muito maior" põe a página de volta na conta, e o
  Ctrl+Z desfaz.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import analise  # noqa: E402
from core import pipeline  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    app,
    janela,
    pasta,
)


def test_a_caixinha_nasce_desmarcada_e_grava_no_livro(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    assert not tela.cx_cortar_pelo_conteudo.isChecked()
    assert projeto.cortar_pelo_conteudo is False
    tela.cx_cortar_pelo_conteudo.setChecked(True)
    assert projeto.cortar_pelo_conteudo is True
    tela.cx_cortar_pelo_conteudo.setChecked(False)
    assert projeto.cortar_pelo_conteudo is False


def test_a_opcao_esta_na_lista_das_opcoes_do_livro(janela):
    assert "cortar_pelo_conteudo" in janela.OPCOES_DO_LIVRO


def _na_conferencia(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    _analisar(janela)
    tela = janela.tela_conferir
    return tela


def test_botao_do_aviso_usa_o_corte_alargado_e_desfaz(janela, pasta, monkeypatch):
    tela = _na_conferencia(janela, pasta)
    projeto = janela.projeto
    pagina = projeto.paginas[tela.indice_pagina]
    projeto.cortar_pelo_conteudo = True
    alargado = (0.05, 0.06, 0.9, 0.88)
    monkeypatch.setattr("ui.tela_conferir.corte_alargado", lambda _p, _pg: alargado)
    pagina.alertas = [analise.CORTE_DEIXOU_TINTA_FORA]
    tela.item_atual.alertas = pagina.alertas
    tela._usar_corte_alargado()
    assert tuple(pagina.recorte) == pytest.approx(alargado)
    assert pagina.revisada
    tela.desfazer()
    assert pagina.recorte is None


def test_botao_do_aviso_poe_a_pagina_de_volta_e_desfaz(janela, pasta):
    tela = _na_conferencia(janela, pasta)
    pagina = janela.projeto.paginas[tela.indice_pagina]
    tela._alinhar_com_as_outras()
    assert pagina.alinhar_com_as_outras is True
    tela.desfazer()
    assert pagina.alinhar_com_as_outras is None


def test_as_correcoes_dos_avisos_existem():
    assert analise.descrever(analise.CORTE_DEIXOU_TINTA_FORA).correcao == "corte_alargado"
    assert analise.descrever(analise.PAGINA_MUITO_MAIOR).correcao == "alinhar_com_as_outras"
    assert hasattr(pipeline, "corte_alargado")
