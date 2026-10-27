"""Item 2.19: unidades (cm, mm, polegadas) e perfis ("receitas"), como o ScanTailor.

Testes de máquina; pasta de dados própria (nada vai para o configuracoes.json
de verdade); nenhuma janela aparece na tela.
"""

from __future__ import annotations

import pytest

from core import perfis, unidades
from tests.test_mesmo_livro_outro_caminho import _pdf, app, janela, pasta  # noqa: F401 - fixtures


# --------------------------------------------------------------- unidades

def test_de_fabrica_centimetros_e_o_texto_de_sempre(pasta):
    assert unidades.da_maquina() == unidades.CM
    assert unidades.texto(1.234) == "1.23 cm"            # o que a tela já mostrava


def test_conversoes(pasta):
    assert unidades.de_cm(2.54, unidades.POLEGADA) == pytest.approx(1.0)
    assert unidades.de_cm(1.5, unidades.MM) == pytest.approx(15.0)
    assert unidades.para_cm(15.0, unidades.MM) == pytest.approx(1.5)
    assert unidades.texto(1.234, unidades.MM) == "12.3 mm"
    assert unidades.valida("parsec") == unidades.CM


def test_a_escolha_da_maquina_vale_no_dialogo_da_folha(app, pasta):
    import configuracoes
    from ui.dialogo_tamanho_da_folha import DialogoTamanhoDaFolha

    configuracoes.escrever("unidade", unidades.MM)
    dialogo = DialogoTamanhoDaFolha(14.8, 21.0)
    assert dialogo.campo_largura.suffix() == " mm"
    assert dialogo.campo_largura.value() == pytest.approx(148.0)
    dialogo.campo_altura.setValue(200.0)
    assert dialogo.tamanho_escolhido() == pytest.approx((14.8, 20.0))   # por dentro, cm


# --------------------------------------------------------------- receitas

def test_de_fabrica_existe_e_e_o_livro_novo(pasta):
    from modelos import Projeto

    assert perfis.nomes()[0] == perfis.NOME_DE_FABRICA
    assert perfis.ler(perfis.NOME_DE_FABRICA) == perfis.do_projeto(Projeto(caminho_entrada="x"))
    assert perfis.do_livro_novo() == ""


def test_guardar_por_e_apagar(pasta):
    from core.filtros import PRETO_E_BRANCO
    from modelos import Projeto

    livro = Projeto(caminho_entrada="a", filtro_padrao=PRETO_E_BRANCO, endireitar=False,
                    margens_iguais=True)
    nome = perfis.guardar("Livros de missa", livro)
    assert nome in perfis.nomes()
    outro = Projeto(caminho_entrada="b")
    assert perfis.aplicar(nome, outro)
    assert (outro.filtro_padrao, outro.endireitar, outro.margens_iguais) == (PRETO_E_BRANCO, False, True)
    assert outro.caminho_entrada == "b"                  # só as escolhas do livro
    assert perfis.apagar(nome) and nome not in perfis.nomes()
    assert not perfis.apagar(perfis.NOME_DE_FABRICA)
    assert perfis.guardar(perfis.NOME_DE_FABRICA, livro) == "De fábrica (minha)"


def test_receita_do_livro_novo(pasta):
    from modelos import Projeto

    nome = perfis.guardar("Sem endireitar", Projeto(caminho_entrada="a", endireitar=False))
    perfis.definir_do_livro_novo(nome)
    novo = Projeto(caminho_entrada="c")
    assert perfis.aplicar_no_livro_novo(novo) == nome and novo.endireitar is False
    perfis.apagar(nome)
    assert perfis.do_livro_novo() == ""                   # apagou: volta ao de fábrica


def test_a_receita_vale_ao_abrir_um_livro_novo(janela, pasta):
    from modelos import Projeto

    nome = perfis.guardar("Sem cortar", Projeto(caminho_entrada="a", cortar_bordas=False))
    perfis.definir_do_livro_novo(nome)
    janela.abrir_livro(str(_pdf(pasta)))
    # etapa 3 da obra (D-018): a receita do livro novo vem MARCADA no Automático
    # (o aviso do livro novo a abre); a página abre como veio ("sempre abre em
    # Original, sem mexer") e nada roda sozinho
    assert janela.projeto.cortar_bordas is False
    janela.tela_conferir.botao_rodar_do_aviso.click()
    from core import automatico as A

    assert A.CORTAR not in janela.estado_do_automatico.marcadas
    assert A.ENDIREITAR in janela.estado_do_automatico.marcadas
    janela._fechar_a_janela_do_automatico()


def test_no_automatico(janela, pasta):
    """As receitas moram no Automático (etapa 3 da obra; era a tela "O que fazer")."""
    from core import automatico as A
    from ui.automatico import CaixaDaReceita

    janela.abrir_livro(str(_pdf(pasta)))
    painel = janela.tela_conferir.paineis.automatico
    estado = painel.estado
    estado.marcadas = {A.LIMPAR, A.CORTAR}
    caixa = CaixaDaReceita(estado)
    caixa.nome.setText("Minha")
    caixa.guardar()
    painel.encher_receitas()
    assert painel.combo_receitas.findData("Minha") >= 0
    painel.combo_receitas.setCurrentIndex(painel.combo_receitas.findData(perfis.NOME_DE_FABRICA))
    painel._escolheu_receita()
    assert A.ENDIREITAR in estado.marcadas
    assert janela.rodar_o_automatico(esperar=True)
    assert janela.projeto.endireitar is True


def test_configuracoes_tem_as_medidas_da_impressao(app, pasta):
    """Item 2.6: a margem da encadernação e o que a impressora não imprime
    ficam em Configurações e valem na janela "Montar para imprimir"."""
    import configuracoes
    from core import impressao as imp
    from ui.tela_configuracoes import TelaConfiguracoes

    tela = TelaConfiguracoes()
    assert tela.margem_da_impressao.value() == 10.0
    assert tela.borda_da_impressora.value() == 3.0
    tela.borda_da_impressora.setValue(5.0)
    assert imp.OpcoesDeImpressao.de_dicionario(configuracoes.ler("impressao")).borda_da_impressora_mm == 5.0
    assert tela.combo_unidade.currentData() == unidades.CM
    assert tela.combo_nucleos.currentData() == 0
