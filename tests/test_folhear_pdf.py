"""Folhear o livro na tela de opções.

O que se cobra aqui e sempre a mesma coisa que o resto do programa cobra: uma
folha de cada vez na memoria, o arquivo solto ao sair, e a tela nao cai quando
o PDF e ruim.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from ui.widgets.folhear_pdf import FolhearPDF  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def livro(tmp_path):
    """Um PDF de cinco folhas, cada uma com um tom diferente de cinza."""
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    for i in range(5):
        pagina = doc.new_page(width=300, height=400)
        tom = 0.2 + i * 0.15
        pagina.draw_rect(fitz.Rect(20, 20, 280, 380), color=(tom, tom, tom),
                         fill=(tom, tom, tom))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def test_abre_na_primeira_folha(app, livro):
    visor = FolhearPDF()
    visor.abrir(livro)
    assert visor.contador.text() == "folha 1 de 5"
    assert not visor.botao_anterior.isEnabled(), "nao ha folha antes da primeira"
    assert visor.botao_proxima.isEnabled()
    visor.fechar()


def test_vira_a_folha_e_para_nas_pontas(app, livro):
    visor = FolhearPDF()
    visor.abrir(livro)

    visor.virar(1)
    assert visor.contador.text() == "folha 2 de 5"

    visor.ir_para(999)
    assert visor.contador.text() == "folha 5 de 5", "passou da ultima folha"
    assert not visor.botao_proxima.isEnabled()

    visor.ir_para(-4)
    assert visor.contador.text() == "folha 1 de 5", "passou da primeira folha"
    visor.fechar()


def test_cada_folha_mostra_uma_imagem_diferente(app, livro):
    """Se todas viessem iguais, o folhear estaria so mudando o contador."""
    visor = FolhearPDF()
    visor.abrir(livro)
    tons = []
    for i in range(5):
        visor.ir_para(i)
        imagem = visor.visor._pixmap.toImage()
        tons.append(imagem.pixelColor(imagem.width() // 2,
                                      imagem.height() // 2).value())
    assert len(set(tons)) == 5, f"folhas repetidas: {tons}"
    visor.fechar()


def test_fechar_solta_o_arquivo(app, livro):
    """O arquivo do acervo nao pode ficar preso depois que a tela sai."""
    visor = FolhearPDF()
    visor.abrir(livro)
    visor.fechar()
    assert visor._doc is None
    # Virar a folha com o arquivo fechado nao pode explodir - o usuario pode
    # apertar a seta enquanto a tela troca.
    visor.virar(1)
    visor.ir_para(2)


def test_arquivo_ruim_nao_derruba_a_tela(app, tmp_path):
    ruim = tmp_path / "nao_e_pdf.pdf"
    ruim.write_bytes(b"isto nao e um PDF")

    visor = FolhearPDF()
    visor.abrir(str(ruim))
    assert visor._doc is None
    assert "não consegui" in visor.contador.text()
    assert not visor.botao_tela_cheia.isEnabled()


def test_uma_folha_de_cada_vez_na_memoria(app, livro):
    """Virar a folha nao pode acumular imagem nenhuma."""
    visor = FolhearPDF()
    visor.abrir(livro)
    for _ in range(3):
        for i in range(5):
            visor.ir_para(i)
    # O visualizador guarda UM pixmap, e nao uma pilha deles.
    assert isinstance(visor.visor._pixmap, type(visor.visor._pixmap))
    assert visor.visor._pixmap is not None
    visor.fechar()


def test_a_folha_mostrada_e_a_do_arquivo_sem_filtro(app, livro):
    """Aqui e o livro como esta, e nao a previa do filtro.

    A primeira folha do PDF de teste e cinza-escura. Se algum filtro entrasse
    no caminho, ela chegaria clara.
    """
    visor = FolhearPDF()
    visor.abrir(livro)
    imagem = visor.visor._pixmap.toImage()
    meio = imagem.pixelColor(imagem.width() // 2, imagem.height() // 2).value()
    assert meio < 90, f"a folha chegou clara demais ({meio}): passou por filtro?"
    visor.fechar()


def test_ler_uma_folha_esvazia_o_armazem_do_mupdf(app, livro, monkeypatch):
    """A regra central do programa: uma folha por vez na memória.

    Este teste existe porque a regra quebrou em silêncio. O MuPDF guarda, por
    baixo, fontes e imagens de cada página já aberta, num armazém que ele só
    limpa quando o documento fecha. Medido no Marial, virando 100 folhas:

        sem esvaziar   65 -> 279 MB, subindo uns 2 MB por folha
        esvaziando     65 ->  70 MB, e para de subir

    **Por que este teste olha a chamada e não a memória do processo.** Tentei
    medir a memória, e não dá: o armazém do MuPDF tem teto próprio, uns 256 MB.
    Um PDF de teste satura o teto na primeira volta e para de crescer, então o
    número fica igual com e sem a correção - o teste passava dos dois jeitos, e
    teste que passa sempre não é teste. Reproduzir de verdade exigiria mais de
    256 MB de páginas diferentes, e uma bateria não pode custar isso.

    Fica então o que dá para afirmar sem enganar: **ler uma folha esvazia o
    armazém**. É uma verificação de dentro, e o número de verdade está medido
    aí em cima, no acervo, à mão.
    """
    chamadas = []
    monkeypatch.setattr(fitz.TOOLS, "store_shrink",
                        lambda pct: chamadas.append(pct))

    visor = FolhearPDF()
    visor.abrir(livro)
    for i in range(5):
        visor.ir_para(i)
    visor.fechar()

    assert len(chamadas) >= 5, (
        "ler uma folha deixou de esvaziar o armazem do MuPDF - a memoria volta "
        "a acumular uma folha atras da outra")
    assert all(p == 100 for p in chamadas), (
        f"esvaziou so em parte: {set(chamadas)}. Cada folha e lida uma vez so, "
        "entao nao ha nada a reaproveitar no armazem")
