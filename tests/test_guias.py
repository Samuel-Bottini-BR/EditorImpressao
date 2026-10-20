"""As linhas de apoio (item 2.5, g8-guias): core/guias.py.

Decisão do Samuel (13/10/2026): "As duas" (as automáticas de hoje e as do
Kaique), com "Mas ele vai poder tirar a automatica a hora que ele quiser."

Testes de máquina, sem tela:
- com as automáticas ligadas e sem linhas do Kaique, o ímã é o de sempre
  (o mesmo resultado das funções antigas do visualizador);
- desligadas, o meio e as beiradas da folha não puxam mais;
- a linha do Kaique puxa a beirada do conteúdo mais perto dela;
- guardadas em mm a partir do meio da folha (como o ScanTailor): ida e volta,
  e a mesma linha cai no mesmo lugar em todas as páginas da mesma folha;
- linha estragada no arquivo é ignorada; "tirar esta linha" acha a mais perto.
"""

from __future__ import annotations

import pytest

from core import guias as g

A5 = (14.8, 21.0)


@pytest.mark.parametrize("conteudo", [
    (0.255, 0.3, 0.5, 0.4), (0.004, 0.006, 0.5, 0.4), (0.3, 0.3, 0.4, 0.4),
    (0.495, 0.595, 0.5, 0.4), (0.1, 0.1, 0.2, 0.2)])
def test_sem_linhas_do_kaique_o_ima_e_o_de_sempre(conteudo):
    """O comportamento de hoje (ui/widgets/visualizador.encaixar_no_ima e
    guias_ativas, que agora chamam esta) não muda."""
    from ui.widgets import visualizador as v

    assert g.encaixar(conteudo) == v.encaixar_no_ima(conteudo)
    assert g.ativas(conteudo) == v.guias_ativas(conteudo)


def test_conta_antiga_do_ima():
    """A conta de antes (cópia congelada do visualizador de 19/10/2026)."""
    assert g.encaixar((0.255, 0.3, 0.5, 0.4)) == pytest.approx((0.25, 0.3, 0.5, 0.4))
    assert g.encaixar((0.004, 0.006, 0.5, 0.4)) == pytest.approx((0.0, 0.0, 0.5, 0.4))
    assert g.ativas((0.255, 0.3, 0.5, 0.4)) == [g.CENTRO_H, g.CENTRO_V]
    assert g.encaixar((0.1, 0.1, 0.2, 0.2)) == (0.1, 0.1, 0.2, 0.2)


def test_automaticas_desligadas_nao_puxam():
    """'ele vai poder tirar a automatica a hora que ele quiser'."""
    assert g.encaixar((0.255, 0.3, 0.5, 0.4), automaticas=False) == (0.255, 0.3, 0.5, 0.4)
    assert g.ativas((0.255, 0.3, 0.5, 0.4), automaticas=False) == []


def test_linha_do_kaique_puxa_a_beirada_mais_perto():
    linhas = [(g.DE_PE, 0.2), (g.DEITADA, 0.8)]
    # a beirada da esquerda (0,205) gruda na linha de pé em 0,2
    assert g.encaixar((0.205, 0.3, 0.3, 0.4), linhas, automaticas=False) == pytest.approx(
        (0.2, 0.3, 0.3, 0.4))
    # a beirada de baixo (0,3 + 0,495 = 0,795) gruda na deitada em 0,8
    assert g.encaixar((0.4, 0.3, 0.3, 0.495), linhas, automaticas=False) == pytest.approx(
        (0.4, 0.305, 0.3, 0.495))
    assert g.ativas((0.205, 0.3, 0.3, 0.4), linhas, automaticas=False) == ["kaique:0"]


def test_as_duas_juntas_ganha_a_mais_perto():
    linhas = [(g.DE_PE, 0.012)]
    assert g.encaixar((0.009, 0.3, 0.3, 0.4), linhas)[0] == pytest.approx(0.012)
    assert g.encaixar((0.003, 0.3, 0.3, 0.4), linhas)[0] == pytest.approx(0.0)


def test_nunca_poe_o_conteudo_para_fora_da_folha():
    linhas = [(g.DE_PE, 0.95)]
    assert g.encaixar((0.945, 0.3, 0.3, 0.4), linhas, automaticas=False)[0] == 0.945


def test_milimetros_do_meio_ida_e_volta():
    linha = g.de_fracao(g.DE_PE, 0.25, A5)
    assert linha.mm == pytest.approx(-37.0)                  # 37 mm à esquerda do meio
    assert g.em_fracao(linha, A5) == pytest.approx(0.25)
    deitada = g.de_fracao(g.DEITADA, 0.75, A5)
    assert deitada.mm == pytest.approx(52.5)
    assert g.em_fracao(deitada, A5) == pytest.approx(0.75)


def test_vai_e_volta_do_arquivo_e_ignora_linha_estragada():
    linhas = [g.Guia(g.DE_PE, -37.0), g.Guia(g.DEITADA, 52.5)]
    assert g.do_projeto(g.para_salvar(linhas)) == linhas
    estragadas = [{"orientacao": "torta", "mm": 1}, {"mm": 2}, {"orientacao": g.DE_PE, "mm": "x"},
                  {"orientacao": g.DE_PE, "mm": float("nan")}, None]
    assert g.do_projeto(estragadas) == []
    assert g.do_projeto(None) == []


def test_tirar_esta_linha_acha_a_mais_perto():
    linhas = [(g.DE_PE, 0.2), (g.DEITADA, 0.8), (g.DE_PE, 0.21)]
    assert g.mais_perto(linhas, x=0.212, y=0.5) == 2
    assert g.mais_perto(linhas, x=0.5, y=0.79) == 1
    assert g.mais_perto(linhas, x=0.5, y=0.5) is None


def test_projeto_tem_os_campos_com_o_de_fabrica_de_hoje():
    from modelos import Projeto

    p = Projeto(caminho_entrada="x.pdf")
    assert p.guias == [] and p.guias_automaticas is True
    dados = p.para_dicionario()
    dados.pop("guias")
    dados.pop("guias_automaticas")
    volta = Projeto.de_dicionario(dados)
    assert volta.guias == [] and volta.guias_automaticas is True
    p.guias = g.para_salvar([g.Guia(g.DE_PE, 10.0)])
    assert Projeto.de_dicionario(p.para_dicionario()).guias == [{"orientacao": g.DE_PE, "mm": 10.0}]
