"""A tela inicial nova: cartões em vez de linhas.

Os quatro defeitos que ela veio consertar, todos visíveis num print antigo:
quatro projetos com o mesmo nome e nenhum jeito de distingui-los; um botão
apagado sem explicar por quê; a caixa de arrastar tomando um terço da tela; e
"abrir de novo" que não retomava trabalho nenhum.
"""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from ui.tela_inicio import (  # noqa: E402
    ALTURA_DO_CARTAO,
    LARGURA_DO_CARTAO,
    CartaoDeProjeto,
    TelaInicio,
)


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def raiz(tmp_path, monkeypatch):
    pasta = tmp_path / "projetos"
    pasta.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: pasta)
    monkeypatch.setattr(projetos.historico, "carregar", lambda: [])
    return pasta


def _livro(caminho, semente: bytes = b"A"):
    caminho.write_bytes(semente * 300_000)
    return caminho


def _resumo(caminho, nome: str, conferidas: int = 0, total: int = 50):
    p = Projeto(caminho_entrada=str(caminho), nome=caminho.stem)
    p.folhas = [ConfigFolha(indice=i) for i in range(total)]
    p.paginas = [ConfigPagina(indice=i, folha=i) for i in range(total)]
    for pagina in p.paginas[:conferidas]:
        pagina.revisada = True
    resumo = projetos.criar(p, total_paginas=total)
    resumo.nome = nome
    projetos.atualizar(resumo, p)
    return resumo


# --- a lista ----------------------------------------------------------------


def test_um_cartao_por_projeto(app, raiz, tmp_path):
    _resumo(_livro(tmp_path / "a.pdf", b"A"), "Um")
    _resumo(_livro(tmp_path / "b.pdf", b"B"), "Dois")

    tela = TelaInicio()
    cartoes = [tela.grade.itemAt(i).widget() for i in range(tela.grade.count())]
    cartoes = [c for c in cartoes if isinstance(c, CartaoDeProjeto)]
    assert len(cartoes) == 2
    assert {c.resumo.nome for c in cartoes} == {"Um", "Dois"}


def test_remontar_nao_deixa_cartao_fantasma(app, raiz, tmp_path):
    """Tirar do layout não tira da tela: o widget continua sendo pintado.

    Sem `setParent(None)`, sobrava um cartão desenhado ao lado dos de verdade -
    o mesmo defeito de "projetos repetidos" que os cartões vieram consertar.
    """
    resumo = _resumo(_livro(tmp_path / "a.pdf"), "Um")
    tela = TelaInicio()
    velho = tela.grade.itemAt(0).widget()

    projetos.renomear(resumo, "Outro nome")
    tela.recarregar()

    assert velho.parent() is None, "o cartão antigo continua na tela"


def test_a_busca_filtra_pelo_nome(app, raiz, tmp_path):
    _resumo(_livro(tmp_path / "a.pdf", b"A"), "Consolação da Filosofia")
    _resumo(_livro(tmp_path / "b.pdf", b"B"), "Gradus primus")

    tela = TelaInicio()
    tela.busca.setText("gradus")

    cartoes = [tela.grade.itemAt(i).widget() for i in range(tela.grade.count())]
    cartoes = [c for c in cartoes if isinstance(c, CartaoDeProjeto)]
    assert [c.resumo.nome for c in cartoes] == ["Gradus primus"]


def test_busca_sem_resultado_explica_em_vez_de_ficar_vazia(app, raiz, tmp_path):
    _resumo(_livro(tmp_path / "a.pdf"), "Um")
    tela = TelaInicio()
    tela.busca.setText("nao existe")

    recado = tela.grade.itemAt(0).widget()
    assert not isinstance(recado, CartaoDeProjeto)
    assert "nao existe" in recado.text() or "não existe" in recado.text()


def test_sem_projeto_nenhum_convida_a_arrastar(app, raiz):
    tela = TelaInicio()
    recado = tela.grade.itemAt(0).widget()
    assert "Arraste" in recado.text()


# --- o cartão ---------------------------------------------------------------


def test_o_cartao_tem_o_tamanho_do_desenho(app, raiz, tmp_path):
    resumo = _resumo(_livro(tmp_path / "a.pdf"), "Um")
    cartao = CartaoDeProjeto(resumo, TelaInicio())
    assert cartao.width() == LARGURA_DO_CARTAO == 304
    assert cartao.height() == ALTURA_DO_CARTAO == 220


def test_o_cartao_diz_onde_o_trabalho_parou(app, raiz, tmp_path):
    resumo = _resumo(_livro(tmp_path / "a.pdf"), "Um", conferidas=31, total=50)
    assert resumo.frase_do_progresso == "31 de 50 conferidas"
    assert abs(resumo.progresso - 0.62) < 0.01


def test_nome_comprido_sai_com_reticencias_e_nao_vaza(app, raiz, tmp_path):
    comprido = "Na escola de Jesus - Catecismo explicado com imagens e figuras"
    resumo = _resumo(_livro(tmp_path / "a.pdf"), comprido)

    cartao = CartaoDeProjeto(resumo, TelaInicio())
    cartao.resize(LARGURA_DO_CARTAO, ALTURA_DO_CARTAO)
    cartao.show()
    cartao._encurtar_o_nome()

    mostrado = cartao.rotulo_nome.text()
    assert mostrado != comprido, "o nome comprido não foi encurtado"
    assert comprido in cartao.rotulo_nome.toolTip(), "o nome inteiro sumiu de vez"
    cartao.close()


def test_cartao_de_pdf_perdido_fica_laranja_e_explica(app, raiz, tmp_path):
    """Nunca um botão apagado sem explicação - era a queixa do print."""
    livro = _livro(tmp_path / "a.pdf")
    resumo = _resumo(livro, "Sumido")
    livro.unlink()

    cartao = CartaoDeProjeto(resumo, TelaInicio())
    assert cartao.perdido
    assert "ef9f27" in cartao.styleSheet().lower(), "o cartão perdido não ficou laranja"

    textos = _todos_os_textos(cartao)
    assert any("saiu do lugar" in t for t in textos)
    assert any("procurar de novo" in t for t in textos)


def test_cartao_pronto_oferece_a_pasta_e_nao_continuar(app, raiz, tmp_path):
    resumo = _resumo(_livro(tmp_path / "a.pdf"), "Pronto", conferidas=50, total=50)
    resumo.pdf_gerado = True
    projetos.gravar_resumo(resumo)

    cartao = CartaoDeProjeto(resumo, TelaInicio())
    textos = _todos_os_textos(cartao)
    assert any("pronto, PDF gerado" in t for t in textos)
    assert any("abrir a pasta" in t for t in textos)


def _todos_os_textos(widget) -> list[str]:
    from PySide6.QtWidgets import QLabel, QPushButton

    textos = []
    for filho in widget.findChildren(QLabel):
        textos.append(filho.text())
    for filho in widget.findChildren(QPushButton):
        textos.append(filho.text())
    return textos


# --- as travas que protegem o trabalho --------------------------------------


def test_livro_trocado_nao_abre_o_projeto(app, raiz, tmp_path, monkeypatch):
    """Aplicar ajustes de um livro em outro estraga tudo em silêncio."""
    livro = _livro(tmp_path / "a.pdf", b"A")
    resumo = _resumo(livro, "Um")
    _livro(tmp_path / "a.pdf", b"Z")          # outro livro, mesmo nome

    avisos = []
    monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.warning",
                        lambda *a, **k: avisos.append(a[2]))

    tela = TelaInicio()
    abertos = []
    tela.continuar_projeto.connect(lambda r: abertos.append(r))
    tela.pedir_para_continuar(resumo)

    assert not abertos, "abriu o projeto num livro que não é aquele"
    assert avisos and "não é o livro deste projeto" in avisos[0]


def test_livro_que_mudou_de_pasta_abre_sozinho(app, raiz, tmp_path, monkeypatch):
    antes, depois = tmp_path / "antes", tmp_path / "depois"
    antes.mkdir()
    depois.mkdir()
    livro = _livro(antes / "a.pdf")
    resumo = _resumo(livro, "Um")
    livro.rename(depois / "a.pdf")
    monkeypatch.setattr(projetos, "_pastas_conhecidas", lambda: [antes, depois])

    tela = TelaInicio()
    abertos = []
    tela.continuar_projeto.connect(lambda r: abertos.append(r))
    tela.pedir_para_continuar(resumo)

    assert abertos, "não religou o livro que mudou de pasta"
    assert abertos[0].caminho_entrada == str(depois / "a.pdf")


def test_comecar_de_novo_pede_confirmacao(app, raiz, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox

    resumo = _resumo(_livro(tmp_path / "a.pdf"), "Um")
    tela = TelaInicio()

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.No)
    pedidos = []
    tela.recomecar_projeto.connect(lambda r: pedidos.append(r))
    tela.pedir_para_recomecar(resumo)
    assert not pedidos, "recomeçou sem confirmação - é destrutivo"

    monkeypatch.setattr(QMessageBox, "question", lambda *a, **k: QMessageBox.Yes)
    tela.pedir_para_recomecar(resumo)
    assert pedidos


def test_a_faixa_de_arrastar_e_uma_linha(app, raiz):
    """Abrir livro novo se faz uma vez por livro, e tomava um terço da tela."""
    tela = TelaInicio()
    assert tela.area.height() <= 70, "a caixa de arrastar voltou a ser grande"
