"""O corte de bordas deixa ~1 mm de papel depois da ultima tinta (conferencia 5, P2).

O defeito (achado em 01/10/2026, relatorios/corte-crista-2026-10-01/LEIA-ME.md):
a folga do corte era meio por cento do lado, contada em pontos INTEIROS da
imagem reduzida (800 pontos de altura) onde o corte e calculado, e o
arredondamento para baixo comia parte dela. Na Escola 7, a 300 DPI, sobravam 7
pontos (0,6 mm) depois do "A" de "CRISTA". Pior em pagina grande ou em
resolucao alta: a mesma conta da 1 ponto da imagem reduzida, que pode ser
0,2 mm.

Decisao do Samuel (conferencia 5, P2): "Sim, 1 mm". A folga agora e em
milimetros da pagina (core/recortar.FOLGA_MM), qualquer que seja a
resolucao em que o corte e calculado.

Paginas sinteticas (texto do test_corte_nao_come_conteudo, ampliado), para o
teste nao depender do acervo nem do gabarito.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core import pipeline
from core.recortar import detectar_bordas
from modelos import ConfigFolha, ConfigPagina, Projeto
from tests.test_corte_nao_come_conteudo import _TINTA, _pagina_de_texto

fitz = pytest.importorskip("fitz")


def _pagina_no_dpi(dpi: int) -> np.ndarray:
    """A pagina de texto como sairia desenhada a `dpi`: 5 x 7,1 polegadas
    (127 x 181 mm, o tamanho de uma pagina do Palatino)."""
    largura, altura = round(5.0 * dpi), round(5.0 * dpi * 800 / 560)
    return cv2.resize(_pagina_de_texto(), (largura, altura), interpolation=cv2.INTER_CUBIC)


def _folgas(img: np.ndarray, recorte) -> dict[str, int]:
    """Pontos de papel entre a tinta e cada borda do corte, convertida para
    pontos como o fatiar faz (int da fracao). Tambem confere que nao ficou
    tinta fora do corte."""
    altura, largura = img.shape[:2]
    x, y, w, h = recorte.tupla if hasattr(recorte, "tupla") else recorte
    x0, y0 = int(x * largura), int(y * altura)
    x1, y1 = int((x + w) * largura), int((y + h) * altura)
    tinta = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) < _TINTA
    linhas, colunas = np.flatnonzero(tinta.any(axis=1)), np.flatnonzero(tinta.any(axis=0))
    t0, t1 = int(colunas.min()), int(colunas.max()) + 1
    u0, u1 = int(linhas.min()), int(linhas.max()) + 1
    assert x0 <= t0 and t1 <= x1 and y0 <= u0 and u1 <= y1, "o corte comeu tinta"
    return {"esq": t0 - x0, "dir": x1 - t1, "topo": u0 - y0, "pe": y1 - u1}


@pytest.mark.parametrize("dpi", [150, 300, 400, 600])
def test_folga_de_1_mm_em_qualquer_resolucao(dpi):
    """De cada lado, pelo menos 1 mm de papel depois da ultima tinta (11,8
    pontos a 300 DPI), e nao muito mais que isso (a queixa de sobrar papel).
    Antes: 0,2 a 0,9 mm, conforme a resolucao e o lado."""
    img = _pagina_no_dpi(dpi)
    um_mm = dpi / 25.4

    recorte = detectar_bordas(img, dpi=dpi)

    for lado, folga in _folgas(img, recorte).items():
        assert folga >= um_mm, f"{dpi} DPI, lado {lado}: {folga / um_mm:.2f} mm de folga"
        assert folga <= 2.5 * um_mm, f"{dpi} DPI, lado {lado}: {folga / um_mm:.2f} mm de folga"


def test_a_folga_e_a_mesma_em_milimetros_em_qualquer_resolucao():
    """O corte calculado a 150 e a 600 DPI da a mesma folga em milimetros
    (dentro de meio milimetro): ela nao depende mais do tamanho da imagem."""
    medidas = {}
    for dpi in (150, 600):
        img = _pagina_no_dpi(dpi)
        folgas = _folgas(img, detectar_bordas(img, dpi=dpi))
        medidas[dpi] = {lado: f / (dpi / 25.4) for lado, f in folgas.items()}
    for lado in medidas[150]:
        assert abs(medidas[150][lado] - medidas[600][lado]) < 0.5, (lado, medidas)


def _pdf_da_pagina(caminho, dpi_scan: int = 300) -> None:
    """A pagina de texto gravada num PDF de verdade, escaneada a `dpi_scan`."""
    img = _pagina_no_dpi(dpi_scan)
    ok, png = cv2.imencode(".png", img)
    assert ok
    doc = fitz.open()
    pagina = doc.new_page(width=img.shape[1] * 72 / dpi_scan, height=img.shape[0] * 72 / dpi_scan)
    pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()


def test_o_pdf_final_tem_1_mm_de_papel_depois_da_ultima_tinta(tmp_path):
    """O caminho do botao "Confirmar e processar" (processar -> PDF a 300
    DPI): na pagina gravada, de cada lado, pelo menos 1 mm de papel entre a
    beirada e a tinta. E a previa (110 DPI) mostra o mesmo corte."""
    caminho = tmp_path / "pagina.pdf"
    _pdf_da_pagina(caminho)
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.limpar = False
    projeto.montar_cadernos = False
    projeto.detectar_regioes = False
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    assert projeto.qualidade_dpi == 300

    pipeline._GEOMETRIAS.clear()
    pipeline.processar(projeto)

    saida = fitz.open(projeto.caminho_saida)
    try:
        pix = saida[0].get_pixmap(dpi=300, alpha=False)
        largura_pdf = saida[0].rect.width
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    finally:
        saida.close()
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if img.shape[2] == 3 else img[:, :, 0]
    tinta = cinza < _TINTA
    linhas, colunas = np.flatnonzero(tinta.any(axis=1)), np.flatnonzero(tinta.any(axis=0))
    folgas = {"esq": colunas.min(), "dir": img.shape[1] - 1 - colunas.max(),
              "topo": linhas.min(), "pe": img.shape[0] - 1 - linhas.max()}
    um_mm = 300 / 25.4
    for lado, folga in folgas.items():
        assert folga >= um_mm, f"PDF final, lado {lado}: {folga / um_mm:.2f} mm de folga"

    # previa = PDF (conserto de 28/09): a previa rapida mostra o mesmo corte
    pipeline._GEOMETRIAS.clear()
    doc = fitz.open(str(caminho))
    try:
        previa, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=110)
        largura_entrada = doc[0].rect.width
    finally:
        doc.close()
    fracao_previa = previa.shape[1] / (largura_entrada * 110 / 72)
    assert abs(fracao_previa - largura_pdf / largura_entrada) < 0.005
