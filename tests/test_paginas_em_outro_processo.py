"""As paginas do PDF sao desenhadas num processo a parte (a janela nao congela).

Bug grave achado pelo verificador (30/09/2026, sonda4_congela.py): a janela
ficava ~16 s sem responder ao terminar a analise de um livro de 80 paginas.
Causa medida: o PyMuPDF segura o GIL enquanto desenha (~0,5 s por pagina de
JPEG 2000 do Internet Archive), e as previas, as miniaturas e a analise,
desenhando em threads de fundo, deixavam a thread da janela sem vez.
Conserto: core/paginas_em_outro_processo.py.

O que se cobra (teste de maquina):
    - a pagina que vem do servidor e IGUAL, ponto por ponto, a desenhada aqui
      (mesma forma, mesmo tipo, array que se pode alterar);
    - desenhar no servidor nao prende a thread que pediu: outra thread do
      programa continua rodando enquanto a pagina e desenhada;
    - erro de PDF chega como ErroPDF (a mesma mensagem de antes);
    - servidor que cai e trocado por outro e a pagina sai mesmo assim;
    - EDITOR_PAGINAS_AQUI=1 desliga tudo (desenha aqui, como antes);
    - documento feito na memoria (sem arquivo) e desenhado aqui.
"""

from __future__ import annotations

import threading
import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import paginas_em_outro_processo as servidor  # noqa: E402
from core.pdf_io import ErroPDF, abrir_pdf, pagina_para_array  # noqa: E402


@pytest.fixture
def livro(tmp_path):
    """Um PDF com uma imagem grande (demora a desenhar) e texto."""
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    ruido = np.random.default_rng(3).integers(0, 255, (2400, 1800, 3), dtype=np.uint8)
    import cv2

    ok, jpeg = cv2.imencode(".jpg", ruido, [cv2.IMWRITE_JPEG_QUALITY, 95])
    for i in range(3):
        pagina = doc.new_page(width=595, height=842)
        pagina.insert_image(pagina.rect, stream=jpeg.tobytes())
        pagina.insert_text((60, 80), f"folha {i}", fontsize=24)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _aqui(monkeypatch, doc, indice, dpi):
    monkeypatch.setenv(servidor.VARIAVEL_DESLIGA, "1")
    imagem = pagina_para_array(doc, indice, dpi=dpi)
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA)
    return imagem


@pytest.mark.parametrize("dpi", [50, 150, 300])
def test_a_pagina_do_servidor_e_igual_a_desenhada_aqui(livro, monkeypatch, dpi):
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    doc = abrir_pdf(livro)
    try:
        for indice in range(3):
            de_fora = servidor.pagina(str(livro), indice, dpi)
            assert de_fora is not None, "o servidor nao respondeu"
            daqui = _aqui(monkeypatch, doc, indice, dpi)
            assert de_fora.shape == daqui.shape and de_fora.dtype == daqui.dtype
            assert np.array_equal(de_fora, daqui)
            assert de_fora.flags.writeable and de_fora.flags.c_contiguous
            assert np.array_equal(pagina_para_array(doc, indice, dpi=dpi), daqui)
    finally:
        doc.close()


def test_desenhar_no_servidor_nao_prende_as_outras_threads(livro, monkeypatch):
    """O defeito em si: enquanto uma thread de fundo espera a pagina, a
    thread principal continua rodando (antes ficava parada ~0,5 s por
    pagina, o tempo inteiro do desenho)."""
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    servidor.pagina(str(livro), 0, 50)                  # servidor ja de pe
    doc = abrir_pdf(livro)

    def desenhar():
        for _ in range(3):
            for indice in range(3):
                pagina_para_array(doc, indice, dpi=300)

    fundo = threading.Thread(target=desenhar)
    maior = 0.0
    ultimo = time.perf_counter()
    fundo.start()
    while fundo.is_alive():
        time.sleep(0.005)
        agora = time.perf_counter()
        maior = max(maior, agora - ultimo)
        ultimo = agora
    doc.close()
    assert maior < 0.15, f"a thread principal ficou {maior:.2f} s parada"


def test_erro_de_pdf_chega_como_erro_pdf(livro, monkeypatch):
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    livro.write_bytes(b"isto nao e um pdf")
    with pytest.raises(ErroPDF):
        servidor.pagina(str(livro), 0, 100)


def test_servidor_que_cai_e_trocado_e_a_pagina_sai(livro, monkeypatch):
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    assert servidor.pagina(str(livro), 0, 50) is not None
    for s in list(servidor._todos):
        s.processo.kill()                                 # os dois caem
        s.processo.wait(10)
    imagem = servidor.pagina(str(livro), 1, 50)
    assert imagem is not None, "nao trocou o servidor que caiu"
    # o outro que caiu e trocado quando chega a vez dele
    assert servidor.pagina(str(livro), 2, 50) is not None
    assert len(servidor._todos) == servidor.QUANTOS_SERVIDORES
    assert all(s.vivo() for s in servidor._todos)


def test_desligado_desenha_aqui(livro, monkeypatch):
    monkeypatch.setenv(servidor.VARIAVEL_DESLIGA, "1")
    assert not servidor.ligado()
    assert servidor.pagina(str(livro), 0, 50) is None
    doc = abrir_pdf(livro)
    try:
        assert pagina_para_array(doc, 0, dpi=50).shape[2] == 3
    finally:
        doc.close()


def test_documento_sem_arquivo_e_desenhado_aqui(monkeypatch):
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    chamadas = []
    monkeypatch.setattr(servidor, "pagina", lambda *a: chamadas.append(a))
    doc = fitz.open()
    doc.new_page(width=200, height=300).insert_text((20, 40), "oi")
    imagem = pagina_para_array(doc, 0, dpi=72)
    assert imagem.shape[:2] == (300, 200) and not chamadas


def test_o_servidor_solta_o_pdf_quando_para(livro, monkeypatch, tmp_path):
    """Arquivo aberto fica preso no Windows: depois de desenhar, a pessoa tem
    de poder mover, renomear ou apagar o PDF (achado pelo outro implementador
    em 30/09). O servidor fecha o livro depois de meio segundo sem pedido."""
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    for indice in range(3):
        assert servidor.pagina(str(livro), indice, 100) is not None
    time.sleep(servidor.SEGUNDOS_PARADO + 0.5)
    movido = livro.rename(tmp_path / "movido.pdf")
    movido.unlink()
    assert not movido.exists()


def test_soltar_livro_solta_o_pdf_na_hora(livro, monkeypatch, tmp_path):
    """Ao fechar ou trocar de livro (GerenciadorPrevias.parar, tira.parar), o
    PDF fica livre na hora, sem esperar o meio segundo."""
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    assert servidor.pagina(str(livro), 0, 100) is not None
    servidor.soltar_livro(str(livro))
    movido = livro.rename(tmp_path / "movido.pdf")
    assert movido.exists()


def test_o_mesmo_livro_mudado_no_disco_e_relido(livro, monkeypatch, tmp_path):
    """O servidor guarda o livro aberto entre pedidos seguidos; se o arquivo
    mudar no disco, ele le o novo (a marca do arquivo muda)."""
    monkeypatch.delenv(servidor.VARIAVEL_DESLIGA, raising=False)
    antes = servidor.pagina(str(livro), 0, 50)
    servidor.soltar_livro(None)
    doc = fitz.open()
    doc.new_page(width=300, height=300).insert_text((20, 40), "outro", fontsize=30)
    doc.save(str(tmp_path / "novo.pdf"))
    doc.close()
    livro.unlink()
    (tmp_path / "novo.pdf").rename(livro)
    depois = servidor.pagina(str(livro), 0, 50)
    assert depois.shape != antes.shape
