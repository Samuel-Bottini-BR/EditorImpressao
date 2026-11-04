"""As provas de comportamento da D-619 e da D-620 (04/11/2026), do print a-69 do Samuel
(CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Palavras dele, no print a-69 (Cortar, Gradus Primus): "para o livro todo, não entendi essa
mensagem, elas não deveriam ser opções para se escolher, essa opção de qualidade não deveria ser
para todas as ferramentas?"

  D-619 ("1- B"): o quadro "Para o livro todo" do Propriedades continua só mostrando o que o
      Automático já fez no livro (D-051), com o título "Já feito no livro todo". O "mudar no
      Automático..." e a caixinha "Margens iguais" (D-554) ficam.
  D-620 ("2- Pode"): a "Qualidade da prévia" (Rápida / Média / Alta), que já vale para o
      programa todo, sai do painel do Cortar e vai para a barra de baixo, ao lado do zoom, e
      aparece em todas as ferramentas.

Todos os testes daqui são REVERSÃO: falham no código de antes (`2329129f`, ramo
`obra-2026-10-26`). Medem o comportamento (onde a lista mora, o que fica gravado, o que muda na
prévia), não a aparência; se a barra cabe a 1366 com as letras de verdade, quem confere são os
prints da janela real (relatorios/painel-livro/).

Nada aparece na tela (tests/conftest.py). Pasta de dados própria (fixture `pasta`).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")
pytest.importorskip("cv2")

from tests.promessas import ajudantes as aj  # noqa: E402
from tests.test_promessas import app, janela, livro, pasta, tela  # noqa: E402,F401 - fixtures


def _ferramentas():
    from ui.widgets.trilha_agrupada import (
        FERRAMENTA_CORTAR,
        FERRAMENTA_DIVIDIR,
        FERRAMENTA_ENDIREITAR,
        FERRAMENTA_FILTROS,
        FERRAMENTA_MOVER,
    )

    return (FERRAMENTA_DIVIDIR, FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR,
            FERRAMENTA_MOVER, FERRAMENTA_FILTROS)


def _escolher(tela, ferramenta) -> None:
    tela.trilha.escolher(ferramenta)
    aj.assentar()


def _textos(widget) -> list[str]:
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QLabel

    textos = [w.text() for w in widget.findChildren(QLabel) + widget.findChildren(QAbstractButton)]
    for c in widget.findChildren(QComboBox):
        textos.extend(c.itemText(i) for i in range(c.count()))
    return [t for t in textos if t]


def _na_barra_de_baixo(widget) -> bool:
    pai = widget.parentWidget()
    while pai is not None:
        if pai.objectName() == "barraDeBaixo":
            return True
        pai = pai.parentWidget()
    return False


# --- D-620: a qualidade da prévia na barra de baixo ------------------------------------------

def test_d620_a_qualidade_mora_na_barra_de_baixo_em_todas_as_ferramentas(janela, tela):  # noqa: F811
    """D-620 ("2- Pode"): a lista Rápida / Média / Alta está na barra de baixo, à vista em todas
    as ferramentas, e o painel do Cortar não tem mais o seletor nem o título."""
    from ui.tela_conferir import ABA_BORDAS

    lista = tela.seletor_qualidade
    assert _na_barra_de_baixo(lista), "a lista da qualidade não está na barra de baixo"
    assert [lista.itemText(i) for i in range(lista.count())] == ["Rápida", "Média", "Alta"]
    assert [lista.itemData(i) for i in range(lista.count())] == ["rapida", "media", "alta"]
    for ferramenta in _ferramentas():
        _escolher(tela, ferramenta)
        assert lista.isVisible(), f"a qualidade sumiu na ferramenta {ferramenta}"
        assert tela.rotulo_do_zoom.isVisible()
    painel_do_cortar = tela.propriedades_das_abas[ABA_BORDAS]
    assert not painel_do_cortar.isAncestorOf(lista)
    textos = _textos(painel_do_cortar)
    assert "Qualidade da prévia" not in textos, "o título saiu do painel do Cortar"
    assert "Rápida" not in textos and "Alta" not in textos, "o seletor saiu do painel do Cortar"


def test_d620_a_qualidade_fica_ao_lado_do_zoom(janela, tela):  # noqa: F811
    """D-620: "ao lado do zoom". Na linha da barra de baixo, entre a lista e o grupo do zoom
    ("–", "N%", "+", "ajustar à tela") não há nenhuma outra peça."""
    linha = tela.seletor_qualidade.parentWidget().layout()
    pecas = [linha.itemAt(i).widget() for i in range(linha.count())]
    pecas = [p for p in pecas if p is not None]
    zoom = [tela.botao_menos_zoom, tela.rotulo_do_zoom, tela.botao_mais_zoom,
            tela.botao_ajustar_a_tela]
    posicoes_do_zoom = [pecas.index(p) for p in zoom]
    assert posicoes_do_zoom == list(range(posicoes_do_zoom[0], posicoes_do_zoom[0] + 4))
    do_grupo = [i for i, p in enumerate(pecas)
                if p is tela.seletor_qualidade or p is getattr(tela, "rotulo_da_qualidade", None)]
    assert do_grupo, "a qualidade não está na linha da barra de baixo"
    assert (min(do_grupo) == posicoes_do_zoom[-1] + 1
            or max(do_grupo) == posicoes_do_zoom[0] - 1), "a qualidade não está ao lado do zoom"


def test_d620_trocar_numa_ferramenta_vale_no_programa_todo(janela, tela):  # noqa: F811
    """D-620: continua uma escolha só, para o programa inteiro (configuracoes "qualidade_previa"),
    com o mesmo efeito de antes: a resolução da prévia muda, fica gravada, e a mesma lista vale
    nas outras ferramentas e no próximo livro aberto."""
    import configuracoes
    from ui.tela_conferir import QUALIDADES_DA_PREVIA
    from ui.widgets.trilha_agrupada import FERRAMENTA_ENDIREITAR, FERRAMENTA_MOVER

    lista = tela.seletor_qualidade
    _escolher(tela, FERRAMENTA_ENDIREITAR)
    lista.setCurrentIndex(lista.findData("alta"))
    aj.assentar()
    assert configuracoes.ler("qualidade_previa") == "alta"
    assert tela._dpi_normal == QUALIDADES_DA_PREVIA["alta"]
    assert tela.previas.dpi_da_tela == QUALIDADES_DA_PREVIA["alta"]
    _escolher(tela, FERRAMENTA_MOVER)
    assert lista.currentData() == "alta" and lista.isVisible()
    assert tela._dpi_normal == QUALIDADES_DA_PREVIA["alta"]
    lista.setCurrentIndex(lista.findData("media"))
    aj.assentar()
    assert configuracoes.ler("qualidade_previa") == "media"
    assert tela._dpi_normal == QUALIDADES_DA_PREVIA["media"]


def test_d620_a_lista_mostra_a_qualidade_gravada_ao_abrir(app, pasta, livro):  # noqa: F811
    """D-620: a escolha gravada (de uma vez anterior) aparece na lista da barra de baixo ao abrir
    o programa, como aparecia no painel do Cortar."""
    import configuracoes
    from ui.janela_principal import JanelaPrincipal

    configuracoes.escrever("qualidade_previa", "media")
    janela = JanelaPrincipal()
    try:
        tela = janela.tela_conferir
        assert tela.seletor_qualidade.currentData() == "media"
        assert tela._qualidade_da_previa == "media"
    finally:
        janela.close()
        aj.assentar()


# --- D-619: o título "Já feito no livro todo" ------------------------------------------------

@pytest.mark.parametrize("qual", ["dividir", "cortar", "endireitar"])
def test_d619_o_quadro_do_livro_diz_ja_feito_no_livro_todo(janela, tela, qual):  # noqa: F811
    """D-619 ("1- B"): no Dividir, no Cortar e no Endireitar o quadro do livro tem o título
    "Já feito no livro todo" (em maiúsculas, como as outras partes) e não mais "Para o livro
    todo"; continua só mostrando (as linhas do que o Automático fez) com o "mudar no
    Automático..." (D-051, D-002)."""
    from PySide6.QtWidgets import QFrame, QLabel, QPushButton

    from ui.tela_conferir import ABA_ANGULO, ABA_BORDAS, ABA_CORTE
    from ui.widgets.trilha_agrupada import (
        FERRAMENTA_CORTAR,
        FERRAMENTA_DIVIDIR,
        FERRAMENTA_ENDIREITAR,
    )

    ferramenta, aba = {"dividir": (FERRAMENTA_DIVIDIR, ABA_CORTE),
                       "cortar": (FERRAMENTA_CORTAR, ABA_BORDAS),
                       "endireitar": (FERRAMENTA_ENDIREITAR, ABA_ANGULO)}[qual]
    _escolher(tela, ferramenta)
    painel = tela.propriedades_das_abas[aba]
    quadros = [q for q in painel.findChildren(QFrame) if q.objectName() == "parteDoLivro"]
    assert len(quadros) == 1
    quadro = quadros[0]
    titulos = [r.text() for r in quadro.findChildren(QLabel) if r.objectName() == "parteDoPainel"]
    assert titulos == ["JÁ FEITO NO LIVRO TODO"], titulos
    assert "PARA O LIVRO TODO" not in _textos(painel)
    botoes = [b.text() for b in quadro.findChildren(QPushButton)]
    assert botoes == ["mudar no Automático..."], "o quadro só mostra e leva ao Automático"


def test_d619_a_caixinha_margens_iguais_continua_no_quadro_do_cortar(janela, tela):  # noqa: F811
    """D-619: a caixinha "Margens iguais" (D-554) fica no quadro do Cortar, com o título novo, e
    continua mudando o valor do livro."""
    from PySide6.QtWidgets import QFrame, QLabel

    from ui.tela_conferir import ABA_BORDAS
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR

    _escolher(tela, FERRAMENTA_CORTAR)
    painel = tela.propriedades_das_abas[ABA_BORDAS]
    quadro = [q for q in painel.findChildren(QFrame) if q.objectName() == "parteDoLivro"][0]
    assert quadro.isAncestorOf(tela.caixa_margens_iguais)
    assert "JÁ FEITO NO LIVRO TODO" in [r.text() for r in quadro.findChildren(QLabel)]
    antes = bool(janela.projeto.margens_iguais)
    tela.caixa_margens_iguais.click()
    aj.assentar()
    assert bool(janela.projeto.margens_iguais) is (not antes)
