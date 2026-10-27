"""Item 5 (06/10/2026): a janela parava ~4,5 s no fim do "Processar".

O verificador mediu 4,56 s de janela parada no fim do Processar de um livro
de 10 folhas (parecer do girar 2.3, ressalva 8). Causa achada pelo
implementador: o EscritorPDF punha cada pagina no PDF como PNG; o MuPDF
desfaz o PNG e guarda a imagem crua, e so a comprime no doc.save(deflate) -
as 10 imagens de uma vez, em C, SEM soltar o GIL do Python. O fio de
processar e outro, mas a janela tambem precisa do GIL: parava inteira (4,3 s
medidos sem janela, saida_teste/r5/medir_processar.py).

Conserto: a imagem e comprimida pelo zlib do Python (que solta o GIL) na
hora de escrever a pagina, e entra no PDF ja comprimida; o save so grava.

Testes de maquina:
    - a imagem ja esta comprimida no PDF antes do save;
    - o PDF guarda exatamente os mesmos pixels de antes (cor, cinza, 1 bit);
    - o fim (fechar) quase nao prende o GIL (um fio Python continua rodando).
"""

from __future__ import annotations

import threading
import time

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core.pdf_io import EscritorPDF  # noqa: E402


def _imagem(altura: int, largura: int, cor: bool = True, semente: int = 0) -> np.ndarray:
    """Parecida com uma folha escaneada: papel com variacao suave, ruido e
    'linhas de texto' escuras (comprime como uma pagina de verdade)."""
    rng = np.random.default_rng(semente)
    y = np.linspace(0, 1, altura)[:, None]
    x = np.linspace(0, 1, largura)[None, :]
    papel = 215 + 25 * np.sin(6 * x + 3 * y)
    img = papel + rng.normal(0, 6, (altura, largura))
    for linha in range(60, altura - 60, 48):
        img[linha:linha + 18, 80:largura - 80] -= 150 * (rng.random((18, largura - 160)) > 0.4)
    img = np.clip(img, 0, 255).astype(np.uint8)
    if not cor:
        return img
    return np.dstack([img, np.clip(img.astype(int) - 12, 0, 255).astype(np.uint8),
                      np.clip(img.astype(int) - 30, 0, 255).astype(np.uint8)])


def _pixels_guardados(caminho) -> list[tuple]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            (info,) = pagina.get_images(full=True)
            pix = fitz.Pixmap(doc, info[0])
            saida.append((pix.width, pix.height, pix.n, bytes(pix.samples)))
        return saida


def test_a_imagem_entra_no_pdf_ja_comprimida(tmp_path):
    escritor = EscritorPDF(tmp_path / "x.pdf")
    escritor.escrever_imagem(_imagem(600, 400), dpi=300)
    doc = escritor.doc
    (info,) = doc[0].get_images(full=True)
    xref = info[0]
    assert doc.xref_get_key(xref, "Filter") == ("name", "/FlateDecode")
    bruto = doc.xref_stream_raw(xref)
    assert len(bruto) < 600 * 400 * 3 / 2, "a imagem ficou crua para o save comprimir"
    escritor.fechar()


@pytest.mark.parametrize("tipo", ["cor", "cinza", "um_bit"])
def test_os_pixels_guardados_sao_os_mesmos_de_antes(tmp_path, tipo):
    """Mesmo resultado do jeito de antes (PNG que o MuPDF desfazia): os
    pixels guardados no PDF sao identicos."""
    from core.pdf_io import _codificar_png

    img = _imagem(500, 360, cor=(tipo == "cor"), semente=3)
    mono = tipo == "um_bit"
    novo = tmp_path / "novo.pdf"
    with EscritorPDF(novo) as escritor:
        escritor.escrever_imagem(img, dpi=300, monocromatico=mono)

    antigo = tmp_path / "antigo.pdf"            # o jeito de antes, a mao
    doc = fitz.open()
    largura_pt, altura_pt = 360 / 300 * 72, 500 / 300 * 72
    pagina = doc.new_page(width=largura_pt, height=altura_pt)
    pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt),
                        stream=_codificar_png(img, monocromatico=mono))
    doc.save(antigo, garbage=3, deflate=True)
    doc.close()

    assert _pixels_guardados(novo) == _pixels_guardados(antigo)
    with fitz.open(novo) as a, fitz.open(antigo) as b:
        assert a[0].rect == b[0].rect
        assert a[0].get_pixmap(dpi=72).samples == b[0].get_pixmap(dpi=72).samples


def test_o_fim_da_gravacao_quase_nao_prende_a_janela(tmp_path):
    """Um fio Python (como a janela) continua rodando enquanto outro fio
    escreve e grava o PDF: nenhuma parada maior que 1 s. Antes, so o save
    destas 6 paginas prendia o GIL por uns 2 a 3 s."""
    paradas: list[float] = []
    fim = threading.Event()

    def relogio():
        ultimo = time.perf_counter()
        while not fim.is_set():
            time.sleep(0.01)
            agora = time.perf_counter()
            paradas.append(agora - ultimo)
            ultimo = agora

    imagens = [_imagem(3300, 2400, semente=i) for i in range(6)]

    def gravar():
        with EscritorPDF(tmp_path / "grande.pdf") as escritor:
            for img in imagens:
                escritor.escrever_imagem(img, dpi=300)

    vigia = threading.Thread(target=relogio)
    vigia.start()
    fio = threading.Thread(target=gravar)
    fio.start()
    fio.join()
    fim.set()
    vigia.join()
    assert (tmp_path / "grande.pdf").stat().st_size > 0
    assert max(paradas) < 1.0, f"o fio da janela ficou {max(paradas):.2f} s parado"
