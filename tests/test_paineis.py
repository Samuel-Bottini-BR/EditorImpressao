"""Etapa 3: os quatro painéis da direita.

Eles recebem o que eram linhas de botões atravessando a tela. O que se cobra:
que nada tenha se perdido no caminho, que "Para revisar" agrupe **por tipo** de
alerta, e que o Histórico use o arquivo de desfazer que já existe - e não um
segundo mecanismo ao lado.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from core import analise  # noqa: E402
from core.selecao import GRAVURA, LETRA, PAPEL  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from ui.widgets.paineis import (  # noqa: E402
    LARGURA,
    ColunaDePaineis,
    PainelFiltroDaPagina,
    PainelHistorico,
    PainelMarcarComo,
    PainelParaRevisar,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def _projeto(paginas: int = 10) -> Projeto:
    p = Projeto(caminho_entrada="x.pdf", nome="x")
    p.folhas = [ConfigFolha(indice=i) for i in range(paginas)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(paginas)]
    return p


def _itens(painel) -> list[QPushButton]:
    """Os botões do CORPO. O cabeçalho também é um botão - ele recolhe."""
    return [b for b in painel.findChildren(QPushButton) if b is not painel.cabecalho]


def _textos(painel) -> list[str]:
    return [b.text() for b in _itens(painel)]


# --- a coluna ---------------------------------------------------------------


def test_os_quatro_paineis_na_ordem_do_desenho(app):
    coluna = ColunaDePaineis()
    assert list(coluna.paineis) == ["revisar", "marcar", "filtro", "historico"]
    assert coluna.width() == LARGURA == 172


def test_cada_painel_recolhe(app):
    coluna = ColunaDePaineis()
    painel = coluna.marcar_como
    assert not painel.recolhido

    painel.alternar()
    assert painel.recolhido
    assert not painel.corpo.isVisibleTo(painel)

    painel.alternar()
    assert not painel.recolhido


def test_o_menu_ver_esconde_um_painel(app):
    coluna = ColunaDePaineis()
    coluna.mostrar_painel("historico", False)
    assert not coluna.historico.isVisibleTo(coluna)
    coluna.mostrar_painel("historico", True)
    assert coluna.historico.isVisibleTo(coluna)


# --- Para revisar: agrupado POR TIPO ---------------------------------------


def test_para_revisar_agrupa_por_tipo_e_nao_lista_paginas(app):
    """Uma lista de "página 3, 17, 40" não diz o que há de errado com elas."""
    projeto = _projeto(20)
    for indice in (2, 7):
        projeto.paginas[indice].alertas = [analise.ANGULO_SUSPEITO_]
    projeto.paginas[11].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    textos = _textos(painel)
    assert any("(2)" in t for t in textos), "não agrupou os dois de ângulo"
    assert any("(1)" in t for t in textos)
    assert "3" not in painel.cabecalho.text() or "Para revisar" in painel.cabecalho.text()


def test_para_revisar_mostra_o_titulo_do_alerta_e_nao_o_objeto(app):
    """descrever() devolve um Alerta; sem o .titulo saía "Alerta(codigo=..."."""
    projeto = _projeto(3)
    projeto.paginas[0].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    textos = " ".join(_textos(painel))
    assert "Alerta(" not in textos, "o painel mostrou a repr do objeto"
    assert analise.descrever(analise.COR).titulo in textos


def test_para_revisar_ignora_o_que_ja_foi_conferido(app):
    projeto = _projeto(5)
    projeto.paginas[0].alertas = [analise.COR]
    projeto.paginas[0].revisada = True
    projeto.paginas[1].alertas = [analise.COR]
    projeto.paginas[1].apagada = True

    painel = PainelParaRevisar()
    painel.atualizar(projeto)
    assert not _textos(painel), "contou página já conferida ou apagada"


def test_clicar_leva_a_primeira_do_tipo(app):
    projeto = _projeto(20)
    for indice in (6, 13):
        projeto.paginas[indice].alertas = [analise.COR]

    painel = PainelParaRevisar()
    painel.atualizar(projeto)

    destinos = []
    painel.ir_para.connect(destinos.append)
    _itens(painel)[0].click()
    assert destinos == [6]


# --- Marcar como ------------------------------------------------------------


def test_marcar_como_tem_os_tres_um_embaixo_do_outro(app):
    painel = PainelMarcarComo()
    assert set(painel.botoes) == {GRAVURA, LETRA, PAPEL}
    assert painel.dentro.count() == 3


def test_marcar_como_avisa_quem_escolheu(app):
    painel = PainelMarcarComo()
    escolhas = []
    painel.escolheu.connect(escolhas.append)
    painel.definir_tipo(LETRA)
    assert escolhas == [LETRA]
    assert painel.tipo == LETRA


# --- Filtro da página -------------------------------------------------------


def test_o_painel_de_filtro_mostra_o_filtro_e_a_tecla(app):
    from core.filtros import MAGICO_PRO

    pagina = ConfigPagina(indice=0, folha=0, filtro=MAGICO_PRO)
    painel = PainelFiltroDaPagina()
    painel.atualizar(pagina)

    from PySide6.QtWidgets import QLabel

    textos = " ".join(r.text() for r in painel.findChildren(QLabel))
    assert "Mágico pro" in textos
    assert "tecla 4" in textos


def test_o_painel_de_filtro_traz_os_cinco_do_so_neste_pedaco(app):
    """Os cinco valores da linha "Filtro só neste pedaço" não se perderam."""
    from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO

    painel = PainelFiltroDaPagina()
    painel.atualizar(ConfigPagina(indice=0, folha=0, filtro=PRETO_E_BRANCO))

    textos = _textos(painel)
    for esperado in ("o mesmo da página", "Original", "Preto e branco",
                     "Melhorar", "Mágico pro"):
        assert esperado in textos, f'sumiu "{esperado}" de "só neste pedaço"'


def test_o_deslizante_e_o_daquele_filtro(app):
    from PySide6.QtWidgets import QSlider

    from core.filtros import MELHORAR

    pagina = ConfigPagina(indice=0, folha=0, filtro=MELHORAR,
                          clareza_melhorar=73)
    painel = PainelFiltroDaPagina()
    painel.atualizar(pagina)

    barras = painel.findChildren(QSlider)
    assert barras, "o filtro Melhorar perdeu o deslizante"
    assert barras[0].value() == 73


def test_o_original_nao_tem_deslizante(app):
    from PySide6.QtWidgets import QSlider

    from core.filtros import ORIGINAL

    painel = PainelFiltroDaPagina()
    painel.atualizar(ConfigPagina(indice=0, folha=0, filtro=ORIGINAL))
    assert not painel.findChildren(QSlider), "o Original ganhou um ajuste que não tem"


# --- Histórico --------------------------------------------------------------


def test_o_historico_usa_o_arquivo_de_desfazer_que_ja_existe(app, tmp_path):
    """Um segundo mecanismo seria duas verdades sobre o mesmo trabalho."""
    from historico_acoes import HistoricoAcoes
    from modelos import Acao

    acoes = HistoricoAcoes(tmp_path)
    for numero in range(3):
        acoes.registrar(Acao.nova("filtro", "pagina", [numero],
                                  {"filtro": "a"}, {"filtro": "b"},
                                  f"trocou o filtro da página {numero + 1}"))

    painel = PainelHistorico()
    painel.atualizar(acoes)

    textos = _textos(painel)
    assert len(textos) == 3
    assert "página 1" in textos[0]
    assert "página 3" in textos[-1], "a mais recente não ficou embaixo"


def test_clicar_no_historico_pede_para_voltar_ate_ali(app, tmp_path):
    from historico_acoes import HistoricoAcoes
    from modelos import Acao

    acoes = HistoricoAcoes(tmp_path)
    for numero in range(3):
        acoes.registrar(Acao.nova("filtro", "pagina", [numero], {}, {},
                                  f"ação {numero}"))

    painel = PainelHistorico()
    painel.atualizar(acoes)

    posicoes = []
    painel.voltar_para.connect(posicoes.append)
    _itens(painel)[0].click()
    assert posicoes == [1], "clicar na primeira ação não voltou até ela"


def test_historico_vazio_diz_que_esta_vazio(app, tmp_path):
    from historico_acoes import HistoricoAcoes
    from PySide6.QtWidgets import QLabel

    painel = PainelHistorico()
    painel.atualizar(HistoricoAcoes(tmp_path))
    textos = " ".join(r.text() for r in painel.findChildren(QLabel))
    assert "nada ainda" in textos
