"""O "Limpar pontinhos" na tela (decisão do Samuel, 06/10/2026, P7; provisório até o layout).

"Limpar pontinhos: desligado · o nosso · pouco · normal · muito", de fábrica
"pouco" (o do ScanTailor), no livro (tela "O que fazer") e na página (aba
Filtro, no lugar da caixinha "limpar poeirinha"), só com o Preto e branco.

Testes de máquina (sem janela na tela, tests/conftest.py):
    - livro: começa em "pouco"; cada valor grava no projeto; só aparece com
      o Preto e branco; projeto salvo volta para a tela; projeto antigo
      ("nosso") aparece "o nosso";
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

NA_TELA = ["desligado", "o nosso", "pouco", "normal", "muito"]


def _itens(combo) -> list[str]:
    return [combo.itemText(i) for i in range(combo.count())]


# --- a tela "O que fazer" (o livro) ------------------------------------------

def test_o_livro_comeca_em_pouco(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = janela.tela_opcoes
    assert _itens(tela.combo_pontinhos) == NA_TELA
    assert tela.combo_pontinhos.currentData() == ps.POUCO
    assert tela.rotulo_pontinhos.text() == "Limpar pontinhos:"
    assert janela.projeto.limpar_pontinhos == ps.POUCO


def test_so_aparece_com_o_preto_e_branco_e_guarda_a_escolha(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = janela.tela_opcoes, janela.projeto
    tela.radios_de_filtro[ORIGINAL].setChecked(True)
    assert tela.linha_pontinhos.isHidden()
    tela.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    assert not tela.linha_pontinhos.isHidden()
    tela.combo_pontinhos.setCurrentIndex(tela.combo_pontinhos.findData(ps.MUITO))
    tela.radios_de_filtro[MELHORAR].setChecked(True)
    assert tela.linha_pontinhos.isHidden()
    assert projeto.limpar_pontinhos == ps.MUITO, "esconder não esquece a escolha"


@pytest.mark.parametrize("escolha", ps.ESCOLHAS)
def test_cada_valor_do_livro_grava_no_projeto(janela, pasta, escolha):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = janela.tela_opcoes
    tela.radios_de_filtro[PRETO_E_BRANCO].setChecked(True)
    tela.combo_pontinhos.setCurrentIndex(tela.combo_pontinhos.findData(escolha))
    assert janela.projeto.limpar_pontinhos == escolha


def test_projeto_salvo_volta_para_a_tela(janela, pasta):
    caminho = str(_pdf(pasta))
    janela.abrir_livro(caminho)
    janela._trazer_opcoes_salvas(Projeto(caminho_entrada=caminho, limpar_pontinhos=ps.NORMAL))
    assert janela.tela_opcoes.combo_pontinhos.currentData() == ps.NORMAL
    assert janela.projeto.limpar_pontinhos == ps.NORMAL


def test_projeto_antigo_aparece_o_nosso(janela, pasta):
    """projeto.json de antes: modelos.Projeto.de_dicionario devolve "nosso"."""
    caminho = str(_pdf(pasta))
    janela.abrir_livro(caminho)
    salvo = Projeto.de_dicionario({"caminho_entrada": caminho})
    assert salvo.limpar_pontinhos == "nosso"
    janela._trazer_opcoes_salvas(salvo)
    assert janela.tela_opcoes.combo_pontinhos.currentText() == "o nosso"
    assert janela.projeto.limpar_pontinhos == "nosso"


def test_objeto_sem_o_campo_fica_com_o_de_agora(janela, pasta):
    caminho = str(_pdf(pasta))
    janela.abrir_livro(caminho)
    salvo = Projeto(caminho_entrada=caminho)
    delattr(salvo, "limpar_pontinhos")          # vale o da classe
    janela._trazer_opcoes_salvas(salvo)
    assert janela.projeto.limpar_pontinhos == ps.POUCO


def test_a_escolha_do_livro_esta_nas_opcoes_do_trabalho(janela):
    assert "limpar_pontinhos" in janela.OPCOES_DO_LIVRO


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
    assert conferir.rotulo_pontinhos.text() == "Limpar pontinhos:"


def test_so_aparece_no_preto_e_branco(conferir):
    assert not conferir.seletor_pontinhos.isHidden()
    conferir.ir_para_pagina(2)                    # Melhorar
    assert conferir.seletor_pontinhos.isHidden() and conferir.rotulo_pontinhos.isHidden()
    conferir.ir_para_pagina(0)
    assert not conferir.seletor_pontinhos.isHidden()


def test_a_pagina_mostra_o_que_vem_do_livro_sem_gravar(conferir):
    assert conferir.seletor_pontinhos.currentData() == ps.POUCO
    conferir.projeto.limpar_pontinhos = "nosso"
    conferir.atualizar()
    assert conferir.seletor_pontinhos.currentText() == "o nosso"
    assert conferir.projeto.paginas[0].limpar_pontinhos is None
    assert not conferir.acoes.pode_desfazer, "mostrar não pode virar ação"


def test_trocar_na_pagina_e_acao_do_desfazer(conferir):
    projeto, seletor = conferir.projeto, conferir.seletor_pontinhos
    pagina, outra = projeto.paginas[0], projeto.paginas[1]
    chave_antes = conferir.previas.chave(0, 110)
    seletor.setCurrentIndex(seletor.findData("desligado"))
    assert pagina.limpar_pontinhos == "desligado" and outra.limpar_pontinhos is None
    assert conferir.previas.chave(0, 110) != chave_antes, "a prévia tinha de ser refeita"
    assert conferir.acoes.descricao_desfazer().endswith("Limpar pontinhos na página 1: desligado")
    seletor.setCurrentIndex(seletor.findData(ps.MUITO))
    assert pagina.limpar_pontinhos == ps.MUITO
    conferir.desfazer()
    assert pagina.limpar_pontinhos == "desligado"
    assert seletor.currentData() == "desligado", "a tela volta junto com o desfazer"
    conferir.desfazer()
    assert pagina.limpar_pontinhos is None and seletor.currentData() == ps.POUCO
    conferir.refazer()
    assert pagina.limpar_pontinhos == "desligado"


def test_escolher_o_que_ja_vale_nao_vira_acao(conferir):
    seletor = conferir.seletor_pontinhos
    seletor.setCurrentIndex(seletor.findData(ps.NORMAL))
    seletor.setCurrentIndex(seletor.findData(ps.POUCO))   # o do livro, que já valia antes
    assert conferir.projeto.paginas[0].limpar_pontinhos == ps.POUCO
    conferir.desfazer()
    conferir.desfazer()
    assert not conferir.acoes.pode_desfazer


def test_todas_leva_a_escolha_junto(conferir):
    projeto, seletor = conferir.projeto, conferir.seletor_pontinhos
    seletor.setCurrentIndex(seletor.findData("nosso"))
    conferir._filtro_em_todas()
    assert [p.limpar_pontinhos for p in projeto.paginas] == ["nosso"] * 3
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
    assert "não" in junto and "vírgula" in junto, "texto sem acento"
