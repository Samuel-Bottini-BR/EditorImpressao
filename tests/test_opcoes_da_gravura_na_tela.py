"""As opções do detector de gravuras na tela (item 1.2; decisão do Samuel, 30/09/2026).

"o programa tem que ter essas opções para o usuário conseguir usar" e
"Todo livro começa no contorno 'livre', com a caixinha 'Este livro tem fotos'
para trocar para 'retangular'. Quero poder trocar também só numa página".

Testes de máquina:
- a tela "O que fazer" tem o grupo "Gravuras e fotos" e grava cada escolha no
  projeto; o livro começa com as opções de fábrica; a sensibilidade só fica
  habilitada com "Este livro tem fotos"; o grupo some sem "Limpar a folha";
- reabrir o livro traz as opções salvas para a tela;
- mudar as opções num livro com trabalho só vale ao clicar "Conferir": aí a
  gravura achada sozinha é marcada para refazer, a marcação à mão fica, uma
  cópia do trabalho é guardada antes e o aviso aparece;
- mudar e sair sem "Conferir" não grava a opção nova (como as outras).

Pasta de dados própria (as fixtures de tests/test_mesmo_livro_outro_caminho.py);
nenhuma janela aparece na tela (tests/conftest.py).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

fitz = pytest.importorskip("fitz")

import projetos  # noqa: E402
from core import pipeline  # noqa: E402
from core.selecao import MAO, Selecao, retangulo  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    _analisar,
    _pdf,
    _trabalhar_e_fechar,
    app,
    janela,
    pasta,
)


def _tela(janela):
    return janela.tela_opcoes


def test_o_livro_comeca_com_as_opcoes_de_fabrica(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = _tela(janela), janela.projeto
    assert tela.cx_achar_gravuras.isChecked()
    assert not tela.cx_tem_fotos.isChecked()
    assert tela.deslizante_sensibilidade.value() == 100
    assert not tela.cx_imagens_claras.isChecked()
    assert tela.cx_igualar_luz.isChecked()
    assert (projeto.gravura_forma, projeto.gravura_sensibilidade,
            projeto.gravura_mais_sensivel, projeto.gravura_normalizar) == ("livre", 100, False, True)
    assert not tela.deslizante_sensibilidade.isEnabled(), "sensibilidade só vale com fotos"


def test_cada_controle_grava_no_projeto(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela, projeto = _tela(janela), janela.projeto
    tela.cx_tem_fotos.setChecked(True)
    assert projeto.gravura_forma == "retangular"
    assert tela.deslizante_sensibilidade.isEnabled()
    tela.deslizante_sensibilidade.setValue(70)
    assert projeto.gravura_sensibilidade == 70 and tela.valor_sensibilidade.text() == "70"
    tela.cx_imagens_claras.setChecked(True)
    tela.cx_igualar_luz.setChecked(False)
    assert projeto.gravura_mais_sensivel and not projeto.gravura_normalizar
    tela.cx_achar_gravuras.setChecked(False)
    assert projeto.gravura_forma == "desligada"
    assert tela.painel_opcoes_gravura.isHidden()
    tela.cx_achar_gravuras.setChecked(True)
    assert projeto.gravura_forma == "retangular"


def test_o_grupo_some_sem_limpar_a_folha(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    tela.cx_limpar.setChecked(False)
    assert tela.painel_gravuras.isHidden()
    tela.cx_limpar.setChecked(True)
    assert not tela.painel_gravuras.isHidden()


def test_o_resumo_fala_das_gravuras(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    tela.escolher_filtro_do_livro("magico_pro")
    assert "separar as gravuras do texto" in tela.resumo.text()
    tela.cx_tem_fotos.setChecked(True)
    assert "fotos em retângulo" in tela.resumo.text()
    tela.cx_achar_gravuras.setChecked(False)
    assert "não procurar gravuras" in tela.resumo.text()


def test_textos_sem_jargao_e_com_acento(janela, pasta):
    tela = _tela(janela)
    textos = [tela.cx_achar_gravuras.text(), tela.cx_tem_fotos.text(),
              tela.cx_imagens_claras.text(), tela.cx_igualar_luz.text(),
              tela.rotulo_sensibilidade.text(), tela.explicacao_sensibilidade.text()]
    junto = " ".join(textos).lower()
    for jargao in ("scantailor", "retangular", "normaliz", "dpi", "máscara"):
        assert jargao not in junto
    assert "página" in tela.cx_igualar_luz.text() and "também" in tela.cx_imagens_claras.text()


def _marcar_paginas(janela):
    """Duas páginas com marcação: a 0 com uma região da máquina e uma à mão
    (assinatura das opções de fábrica); a 1 só à mão."""
    from core.detectar_regioes import GRAVURA_SCANTAILOR, OpcoesDaGravura, assinatura_da_gravura

    paginas = janela.projeto.paginas
    s0 = Selecao()
    s0.acrescentar(retangulo(0.1, 0.1, 0.5, 0.5, origem="rede"))
    s0.acrescentar(retangulo(0.6, 0.6, 0.8, 0.8, origem=MAO, filtro="original"))
    paginas[0].guardar_selecao(s0)
    paginas[0].gravura_feita_com = assinatura_da_gravura(GRAVURA_SCANTAILOR, OpcoesDaGravura())
    s1 = Selecao()
    s1.acrescentar(retangulo(0.2, 0.2, 0.3, 0.3, origem=MAO))
    paginas[1].guardar_selecao(s1)
    janela._salvar_agora()
    return s0.para_lista(), s1.para_lista()


def test_mudar_as_opcoes_num_livro_com_trabalho_refaz_so_a_gravura_automatica(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    antes_0, antes_1 = _marcar_paginas(janela)
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    gravado_antes = estado.read_bytes()
    janela.avisos.clear()

    # volta para "O que fazer", marca "Este livro tem fotos" e clica "Conferir"
    janela._sair_da_conferencia()
    _tela(janela).cx_tem_fotos.setChecked(True)
    _analisar(janela)

    projeto = janela.projeto
    assert projeto.gravura_forma == "retangular", "a opção nova não valeu"
    # a marcação continua lá (é refeita na hora de desenhar a página)
    assert projeto.paginas[0].selecao == antes_0 and projeto.paginas[1].selecao == antes_1
    assert pipeline._gravura_a_refazer(projeto, projeto.paginas[0])
    assert not pipeline._gravura_a_refazer(projeto, projeto.paginas[1]), \
        "página só com marcação à mão não é refeita"
    # cópia do trabalho de antes, e o aviso
    copias = sorted(estado.parent.glob("projeto.antigo-*.json"))
    assert len(copias) == 1 and copias[0].read_bytes() == gravado_antes
    assert janela.avisos and "procuradas de novo" in janela.avisos[-1]
    assert "à mão fica" in janela.avisos[-1] and str(copias[0].parent)[2:] in janela.avisos[-1]
    # e a opção nova foi para o disco
    assert json.loads(estado.read_text(encoding="utf-8"))["gravura_forma"] == "retangular"


def test_reabrir_traz_as_opcoes_salvas(janela, pasta):
    livro = _pdf(pasta)
    janela.abrir_livro(str(livro))
    _tela(janela).cx_tem_fotos.setChecked(True)
    _tela(janela).deslizante_sensibilidade.setValue(40)
    _analisar(janela)
    janela._salvar_agora()
    janela.previas.parar()
    janela.previas = None
    janela.tela_opcoes.folhear.fechar()

    janela.abrir_livro(str(livro))
    assert _tela(janela).cx_tem_fotos.isChecked()
    assert _tela(janela).deslizante_sensibilidade.value() == 40
    assert janela.projeto.gravura_forma == "retangular"


def test_mudar_sem_conferir_nao_grava_a_opcao_nova(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    janela._sair_da_conferencia()
    _tela(janela).cx_achar_gravuras.setChecked(False)
    janela._salvar_agora()
    estado = Path(janela.resumo.pasta) / projetos.ARQUIVO_ESTADO
    assert json.loads(estado.read_text(encoding="utf-8"))["gravura_forma"] == "livre"


def test_conferir_sem_mudar_nada_nao_avisa_nem_copia(janela, pasta):
    livro = _pdf(pasta)
    _trabalhar_e_fechar(janela, str(livro))
    janela.abrir_livro(str(livro))
    _analisar(janela)
    _marcar_paginas(janela)
    janela.avisos.clear()
    janela._sair_da_conferencia()
    _analisar(janela)
    assert not janela.avisos
    assert not list(Path(janela.resumo.pasta).glob("projeto.antigo-*.json"))


# ---------------------------------------------------------------------------
# a tela nao espreme o grupo (parecer do verificador de 30/09, r01-r04)
# ---------------------------------------------------------------------------

def test_mais_opcoes_comeca_fechado_e_abre(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    tela.escolher_filtro_do_livro("magico_pro")
    assert tela.painel_mais_opcoes.isHidden() and tela.botao_mais_opcoes.text() == "Mais opções"
    tela.botao_mais_opcoes.click()
    assert not tela.painel_mais_opcoes.isHidden()
    assert tela.botao_mais_opcoes.text() == "Menos opções"


def test_mais_opcoes_abre_sozinho_quando_algo_avancado_mudou(janela, pasta):
    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    janela.projeto.gravura_mais_sensivel = True
    tela.mostrar_opcoes()
    assert tela.botao_mais_opcoes.isChecked() and not tela.painel_mais_opcoes.isHidden()


@pytest.mark.parametrize("largura, altura", [(1152, 560), (1280, 520), (1366, 600)])
def test_janela_baixa_nao_espreme_as_linhas(janela, pasta, largura, altura):
    """Numa janela baixa aparece a rolagem; nenhuma linha fica mais baixa que
    precisa (a 1440 x 880 com 125%, as linhas ficavam com 2 pontos: r01)."""
    from PySide6.QtWidgets import QApplication

    janela.abrir_livro(str(_pdf(pasta)))
    tela = _tela(janela)
    tela.escolher_filtro_do_livro("magico_pro")
    tela.cx_tem_fotos.setChecked(True)
    tela.botao_mais_opcoes.setChecked(True)
    janela.resize(largura, altura)
    janela.show()
    for _ in range(5):
        QApplication.processEvents()
    controles = [tela.cx_dividir, tela.cx_limpar, tela.cx_achar_gravuras, tela.cx_tem_fotos,
                 tela.cx_imagens_claras, tela.cx_igualar_luz, tela.cx_endireitar,
                 tela.cx_cortar, tela.cx_cadernos, tela.deslizante_sensibilidade,
                 *tela._frases_da_gravura]
    for controle in controles:
        assert controle.height() >= controle.minimumSizeHint().height(), controle
    for frase in tela._frases_da_gravura:
        assert frase.height() >= frase.heightForWidth(frase.width()) - 1, frase.text()
    assert tela.rolagem.verticalScrollBar().maximum() > 0, "janela baixa: tem de aparecer a rolagem"
    janela.hide()


# ---------------------------------------------------------------------------
# a tela acompanha o desfazer e o refazer (parecer do verificador, 30/09, r15)
# ---------------------------------------------------------------------------

def _filtro_marcado(tela) -> str:
    return tela._filtro_escolhido()


def test_a_tela_o_que_fazer_acompanha_o_desfazer(janela, pasta):
    """Desfeito o "Sim" da pergunta do fundo (uma ação que muda o filtro do
    livro, "livro.filtro_padrao"), a tela "O que fazer" tem de mostrar o
    filtro de antes - estando à vista ou não."""
    from PySide6.QtWidgets import QApplication

    from historico_acoes import aplicar
    from modelos import Acao

    janela.abrir_livro(str(_pdf(pasta)))
    _analisar(janela)
    projeto = janela.projeto
    acao = Acao.nova("tirar_o_fundo_do_livro", "pagina", [0],
                     {"livro.filtro_padrao": projeto.filtro_padrao},
                     {"livro.filtro_padrao": "magico_pro"}, "Filtro do livro")
    aplicar(projeto, acao, acao.depois)
    janela.acoes.registrar(acao)

    janela.show()
    janela._sair_da_conferencia()            # "O que fazer" à vista
    QApplication.processEvents()
    tela = _tela(janela)
    assert _filtro_marcado(tela) == "magico_pro"

    janela.tela_conferir.desfazer()          # menu Editar, com "O que fazer" à vista
    QApplication.processEvents()
    assert projeto.filtro_padrao == "original"
    assert _filtro_marcado(tela) == "original", "a tela ficou mostrando o filtro desfeito"
    assert "mágico" not in tela.resumo.text().lower()

    # refazer com a tela escondida: ela se reacerta ao aparecer
    janela.telas.setCurrentIndex(3)          # CONFERIR
    janela.tela_conferir.refazer()
    janela._sair_da_conferencia()
    QApplication.processEvents()
    assert _filtro_marcado(tela) == "magico_pro"
    janela.hide()
