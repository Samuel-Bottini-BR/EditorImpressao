"""O "Limpar pontinhos" na tela (decisão do Samuel, 06/10/2026, P7; provisório até o layout).

"Limpar a sujeira: Sem limpeza · Limpeza bruta · Limpeza cuidadosa (leve,
média, forte)" (nomes da Rodada 10 do layout, 07/10/2026; antes "Limpar
pontinhos: desligado · o nosso · pouco · normal · muito"), de fábrica
core/pontinhos_scantailor.PADRAO ("o nosso" ou "desligado"; desde 07/10/2026
nunca o do ScanTailor, que só vale quando escolhido), no livro (tela "O que fazer") e na página (aba
Filtro, no lugar da caixinha "limpar poeirinha"), só com o Preto e branco.

Testes de máquina (sem janela na tela, tests/conftest.py):
    - livro: começa no de fábrica; cada valor grava no projeto; só aparece com
      o Preto e branco; projeto salvo volta para a tela; projeto antigo
      ("nosso") aparece "Limpeza bruta";
    - página: mostra o que vale (do livro ou dela) sem gravar; trocar é ação
      do desfazer só dela; "todas" leva junto; só no Preto e branco; a
      prévia é refeita (a chave muda), também quando muda no livro;
    - textos com acento, sem jargão e sem emoji.
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")

from core import pontinhos_scantailor as ps  # noqa: E402
from core.filtros import MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _pdf,
    app,
    janela,
    pasta,
)

NA_TELA = ["Sem limpeza", "Limpeza bruta", "Limpeza cuidadosa (leve)",
           "Limpeza cuidadosa (média)", "Limpeza cuidadosa (forte)"]


def _itens(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


# --- o livro: no Automático, etapa "Limpar a folha" (era a tela "O que fazer"
# até a etapa 3 da obra, 26/10/2026) ---------------------------------------------

def _no_limpar(janela, pasta, projeto_salvo=None):
    """O livro aberto e a janela do Automático na etapa "Limpar a folha". Com
    `projeto_salvo`, o Automático começa das escolhas dele (como no livro que
    reabre com o trabalho)."""
    janela.abrir_livro(str(_pdf(pasta)))
    if projeto_salvo is not None:
        janela.estado_do_automatico.do_projeto(projeto_salvo)
    return janela.abrir_o_automatico("limpar")


def test_o_livro_comeca_no_de_fabrica_e_nunca_no_do_scantailor(janela, pasta):
    """Decisão do Samuel de 07/10/2026: o do ScanTailor "só deve ser usado se
    for selecionado junto, e não como automatico junto do preto e branco"."""
    jan = _no_limpar(janela, pasta)
    combo = jan.combo_pontinhos
    assert _itens(combo) == NA_TELA
    assert combo.currentData() == ps.PADRAO
    assert combo.currentData() not in ps.DO_SCANTAILOR
    assert "Limpar a sujeira:" in [r.text() for r in jan.linhas["limpar_pontinhos"].findChildren(
        type(jan.frase))]
    assert janela.projeto.limpar_pontinhos == ps.PADRAO
    janela._fechar_a_janela_do_automatico()


def test_so_aparece_com_o_preto_e_branco_e_guarda_a_escolha(janela, pasta):
    jan = _no_limpar(janela, pasta)
    estado = janela.estado_do_automatico
    linha = jan.linhas["limpar_pontinhos"]
    jan.radios_de_filtro[ORIGINAL].setChecked(True)
    assert linha.isHidden()
    jan.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    assert not linha.isHidden()
    jan.combo_pontinhos.setCurrentIndex(jan.combo_pontinhos.findData(ps.MUITO))
    jan.radios_de_filtro[MELHORAR].setChecked(True)
    assert linha.isHidden()
    assert estado.opcoes["limpar_pontinhos"] == ps.MUITO, "esconder não esquece a escolha"
    janela._fechar_a_janela_do_automatico()


@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_cada_valor_do_livro_grava_no_projeto(janela, pasta, escolha):
    from core import automatico as A

    jan = _no_limpar(janela, pasta)
    jan.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    jan.combo_pontinhos.setCurrentIndex(jan.combo_pontinhos.findData(escolha))
    janela.estado_do_automatico.marcadas = {A.LIMPAR}
    janela._fechar_a_janela_do_automatico()
    assert janela.rodar_o_automatico(esperar=True)
    assert janela.projeto.limpar_pontinhos == escolha


def test_projeto_salvo_volta_para_a_tela(janela, pasta):
    caminho = str(_pdf(pasta))
    jan = _no_limpar(janela, pasta, Projeto(caminho_entrada=caminho, limpar_pontinhos=ps.NORMAL))
    assert jan.combo_pontinhos.currentData() == ps.NORMAL
    janela._fechar_a_janela_do_automatico()


def test_projeto_antigo_aparece_a_limpeza_bruta(janela, pasta):
    """projeto.json de antes: modelos.Projeto.de_dicionario devolve "nosso"."""
    caminho = str(_pdf(pasta))
    salvo = Projeto.de_dicionario({"caminho_entrada": caminho})
    assert salvo.limpar_pontinhos == "nosso"
    jan = _no_limpar(janela, pasta, salvo)
    assert jan.combo_pontinhos.currentText() == "Limpeza bruta"
    janela._fechar_a_janela_do_automatico()


def test_objeto_sem_o_campo_fica_com_o_de_agora(janela, pasta):
    caminho = str(_pdf(pasta))
    salvo = Projeto(caminho_entrada=caminho)
    delattr(salvo, "limpar_pontinhos")          # vale o da classe
    jan = _no_limpar(janela, pasta, salvo)
    assert jan.combo_pontinhos.currentData() == ps.PADRAO
    janela._fechar_a_janela_do_automatico()


def test_a_escolha_do_livro_esta_nas_opcoes_do_trabalho(janela):
    from core import automatico as A

    assert "limpar_pontinhos" in A.todas_as_opcoes()


# --- a aba Filtro (a página) ---------------------------------------------------

@pytest.fixture
def conferir(app, pasta):
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import TelaConferir

    caminho = _pdf(pasta, folhas=3)
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste", dividir_folhas=False,
                      detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(3)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=PRETO_E_BRANCO) for i in range(3)]
    projeto.paginas[2].filtro = MELHORAR
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    yield tela
    previas.parar()


def test_a_caixinha_antiga_saiu(conferir):
    assert not hasattr(conferir, "caixa_despeckle")
    assert _itens(conferir.seletor_pontinhos) == NA_TELA
    # etapa 4 do layout: o nome é o título da parte no painel Filtro, e o
    # rótulo virou a frase de explicação embaixo dele
    assert conferir.paineis.filtro_da_pagina.partes["limpar"].cabeca.titulo.text() == "Limpar a sujeira"
    assert conferir.rotulo_pontinhos.text().startswith("Limpa a sujeira do papel")


def test_so_aparece_no_preto_e_branco(conferir):
    assert not conferir.seletor_pontinhos.isHidden()
    conferir.ir_para_pagina(2)                    # Melhorar
    assert conferir.seletor_pontinhos.isHidden() and conferir.rotulo_pontinhos.isHidden()
    conferir.ir_para_pagina(0)
    assert not conferir.seletor_pontinhos.isHidden()


def test_a_pagina_mostra_o_que_vem_do_livro_sem_gravar(conferir):
    assert conferir.seletor_pontinhos.currentData() == ps.PADRAO
    conferir.projeto.limpar_pontinhos = ps.NORMAL     # nunca o de fabrica (07/10)
    conferir.atualizar()
    assert conferir.seletor_pontinhos.currentText() == "Limpeza cuidadosa (média)"
    assert conferir.projeto.paginas[0].limpar_pontinhos is None
    assert not conferir.acoes.pode_desfazer, "mostrar não pode virar ação"


def test_trocar_na_pagina_e_acao_do_desfazer(conferir):
    projeto, seletor = conferir.projeto, conferir.seletor_pontinhos
    pagina, outra = projeto.paginas[0], projeto.paginas[1]
    chave_antes = conferir.previas.chave(0, 110)
    # (o valor escolhido nunca e o de fabrica, que pode ser "desligado" ou
    # "nosso": escolher o que ja vale nao vira acao)
    seletor.setCurrentIndex(seletor.findData(ps.NORMAL))
    assert pagina.limpar_pontinhos == ps.NORMAL and outra.limpar_pontinhos is None
    assert conferir.previas.chave(0, 110) != chave_antes, "a prévia tinha de ser refeita"
    assert conferir.acoes.descricao_desfazer().endswith("Limpar a sujeira na página 1: Limpeza cuidadosa (média)")
    seletor.setCurrentIndex(seletor.findData(ps.MUITO))
    assert pagina.limpar_pontinhos == ps.MUITO
    conferir.desfazer()
    assert pagina.limpar_pontinhos == ps.NORMAL
    assert seletor.currentData() == ps.NORMAL, "a tela volta junto com o desfazer"
    conferir.desfazer()
    assert pagina.limpar_pontinhos is None and seletor.currentData() == ps.PADRAO
    conferir.refazer()
    assert pagina.limpar_pontinhos == ps.NORMAL


def test_escolher_o_que_ja_vale_nao_vira_acao(conferir):
    seletor = conferir.seletor_pontinhos
    seletor.setCurrentIndex(seletor.findData(ps.NORMAL))
    seletor.setCurrentIndex(seletor.findData(ps.PADRAO))  # o do livro, que já valia antes
    assert conferir.projeto.paginas[0].limpar_pontinhos == ps.PADRAO
    conferir.desfazer()
    conferir.desfazer()
    assert not conferir.acoes.pode_desfazer


def test_todas_leva_a_escolha_junto(conferir):
    projeto, seletor = conferir.projeto, conferir.seletor_pontinhos
    seletor.setCurrentIndex(seletor.findData(ps.MUITO))   # nunca o de fabrica
    conferir._filtro_em_todas()
    assert [p.limpar_pontinhos for p in projeto.paginas] == [ps.MUITO] * 3
    conferir.desfazer()
    assert projeto.paginas[1].limpar_pontinhos is None


def test_mudar_no_livro_tambem_refaz_a_previa(conferir):
    chave_antes = conferir.previas.chave(1, 110)
    conferir.projeto.limpar_pontinhos = ps.MUITO
    assert conferir.previas.chave(1, 110) != chave_antes


def test_textos_com_acento_sem_jargao_e_sem_emoji(conferir):
    textos = _itens(conferir.seletor_pontinhos) + [
        conferir.seletor_pontinhos.toolTip(), conferir.rotulo_pontinhos.text()]
    junto = " ".join(textos)
    for jargao in ("despeckle", "scantailor", "dpi", "binari", "pixel"):
        assert jargao not in junto.lower(), jargao
    assert all(ord(c) < 0x2000 for c in junto), "emoji ou símbolo estranho"
    assert "está" in junto and "vírgula" in junto, "texto sem acento"
