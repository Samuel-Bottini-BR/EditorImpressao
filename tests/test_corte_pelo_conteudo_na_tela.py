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


# ------------------------------------------------- linhas de apoio (g8-guias)

def test_linhas_de_apoio_gravam_no_livro_em_mm_e_desfazem(janela, pasta):
    """g8-guias: a linha que o Kaique põe vale no livro todo, guardada em mm a
    partir do meio da folha (como o ScanTailor); o Ctrl+Z tira."""
    from core import guias

    tela = _na_conferencia(janela, pasta)
    projeto = janela.projeto
    projeto.paginas[tela.indice_pagina].tamanho_folha_cm = (14.8, 21.0)
    tela._mudar_as_linhas_de_apoio([(guias.DE_PE, 0.25)])
    assert projeto.guias == [{"orientacao": guias.DE_PE, "mm": -37.0}]
    tela.desfazer()
    assert projeto.guias == []


def test_desligar_as_linhas_automaticas_e_desfazer(janela, pasta):
    """'Mas ele vai poder tirar a automatica a hora que ele quiser.'"""
    tela = _na_conferencia(janela, pasta)
    projeto = janela.projeto
    assert tela.botao_linhas_automaticas.isChecked() and projeto.guias_automaticas
    tela.botao_linhas_automaticas.click()
    assert projeto.guias_automaticas is False
    tela.desfazer()
    assert projeto.guias_automaticas is True


def test_o_visualizador_usa_as_linhas_do_kaique(app):
    """No "Mover conteúdo", o ímã pega a linha do Kaique e, com as automáticas
    desligadas, não pega mais o meio da folha."""
    from core import guias
    from ui.widgets.visualizador import encaixar_no_ima

    assert encaixar_no_ima((0.205, 0.3, 0.3, 0.4), linhas=[(guias.DE_PE, 0.2)],
                           automaticas=False)[0] == pytest.approx(0.2)
    assert encaixar_no_ima((0.255, 0.3, 0.5, 0.4), automaticas=False) == (0.255, 0.3, 0.5, 0.4)


# ------------------------------------- borda preta (2.13) e "usar em todas"

def test_a_caixinha_da_borda_preta_nasce_desmarcada_com_ate_a_moldura(janela, pasta):
    """G7 (a) "desligada de fábrica"; g7-borda-ate-onde: ao ligar, "até a
    moldura" vem escolhido; trocar grava no livro."""
    from core import borda_preta as bp

    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    assert not tela.cx_borda_preta.isChecked() and projeto.borda_preta is False
    assert tela.combo_borda_preta.currentData() == bp.ATE_A_MOLDURA
    tela.cx_borda_preta.setChecked(True)
    assert projeto.borda_preta is True and projeto.borda_preta_ate == bp.ATE_A_MOLDURA
    tela.combo_borda_preta.setCurrentIndex(tela.combo_borda_preta.findData(bp.SO_O_PRETO))
    assert projeto.borda_preta_ate == bp.SO_O_PRETO
    assert {"borda_preta", "borda_preta_ate"} <= set(janela.OPCOES_DO_LIVRO)


def test_regressao_usar_em_todas_nao_apaga_as_excecoes(janela, pasta, monkeypatch):
    """Bug da Lista de bugs (08/10/2026): "O 'usar em todas' da aba Bordas apaga
    as exceções por página (o Samuel pediu que as exceções fiquem, item 2.13)".
    No código antigo o corte ia para TODAS as páginas e a exceção da página 3
    se perdia; agora a janela vem com as exceções desmarcadas."""
    from ui import dialogo_escolher_paginas as dep

    tela = _na_conferencia(janela, pasta)
    projeto = janela.projeto
    excecao = [0.2, 0.2, 0.6, 0.6]
    projeto.paginas[2].recorte = excecao
    tela.ir_para_pagina(0)
    projeto.paginas[0].recorte = [0.05, 0.05, 0.9, 0.9]
    monkeypatch.setattr(type(tela), "_escolher_paginas_do_corte",
                        lambda self: dep.paginas_de_fabrica(self.projeto, self.indice_pagina),
                        raising=False)
    tela._recorte_em_todas()
    assert list(projeto.paginas[2].recorte) == excecao                   # a exceção ficou
    assert list(projeto.paginas[1].recorte) == [0.05, 0.05, 0.9, 0.9]
    tela.desfazer()
    assert projeto.paginas[1].recorte is None


def test_janela_em_quais_paginas_selecionar_todas_e_nenhuma(janela, pasta):
    from ui.dialogo_escolher_paginas import DialogoEscolherPaginas

    _na_conferencia(janela, pasta)
    projeto = janela.projeto
    projeto.paginas[2].recorte = [0.2, 0.2, 0.6, 0.6]
    d = DialogoEscolherPaginas(projeto, 0)
    assert d.escolhidas() == [0, 1, 3]
    d.botao_todas.click()
    assert d.escolhidas() == [0, 1, 2, 3]
    d.botao_nenhuma.click()
    assert d.escolhidas() == []


def test_cancelar_a_janela_nao_muda_nada(janela, pasta, monkeypatch):
    tela = _na_conferencia(janela, pasta)
    projeto = janela.projeto
    tela.ir_para_pagina(0)
    projeto.paginas[0].recorte = [0.05, 0.05, 0.9, 0.9]
    monkeypatch.setattr(type(tela), "_escolher_paginas_do_corte", lambda self: [])
    feitas = len(janela.acoes.feitas)
    tela._recorte_em_todas()
    assert projeto.paginas[1].recorte is None and len(janela.acoes.feitas) == feitas


def test_2_14_lista_cortar_fora_ou_pintar(janela, pasta):
    """Item 2.14: "O Kaique escolhe por livro" entre cortar fora e pintar de
    branco; vem "cortar fora"; trocar grava no livro."""
    from core import borda_preta as bp

    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    assert tela.combo_borda_fazer.currentData() == bp.CORTAR_FORA
    tela.cx_borda_preta.setChecked(True)
    tela.combo_borda_fazer.setCurrentIndex(tela.combo_borda_fazer.findData(bp.PINTAR))
    assert projeto.borda_preta_fazer == bp.PINTAR
    assert "borda_preta_fazer" in janela.OPCOES_DO_LIVRO
