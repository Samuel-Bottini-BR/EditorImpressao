"""A previa da tela e o PDF final dao o MESMO corte automatico (Lista de bugs, 28/09/2026).

O defeito: a previa (110 DPI) e o PDF (300 DPI) calculavam o corte cada um na
sua imagem, e as duas imagens nao sao iguais - o MuPDF desenha a pagina de
outro jeito em 110 DPI, e a conta do corte tem limiares (80% de coluna
escura, 0,2% de tinta descartada, fechamento de 5x5 pontos) que caem de um
lado numa imagem e do outro na outra. No gabarito, ate 8% de diferenca
(Palatino 5): o Kaique via um corte na tela e recebia outro no PDF.

A pagina de teste e sintetica (texto + uma coluna de pontinhos de sujeira na
margem esquerda), gravada num PDF de verdade, como o acervo: a imagem e
embutida a 400 DPI e o programa a desenha na resolucao que pedir.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import pipeline
from core.pdf_io import abrir_pdf
from core.pipeline import preparar_metade
from modelos import ConfigFolha, ConfigPagina, Projeto
from tests.test_corte_nao_come_conteudo import _pagina_de_texto


def _pdf_com_sujeira_na_margem(caminho) -> None:
    """Pagina de 3,5 x 5 polegadas (escaneada a 400 DPI) com texto e uma coluna
    de pontinhos cinzas a 3,5% da beirada esquerda. Achada por busca: com o
    codigo de antes, a previa deixava os pontinhos de fora e o PDF os pegava."""
    img = cv2.resize(_pagina_de_texto(numero=False), (1400, 2000), interpolation=cv2.INTER_CUBIC)
    for y in range(200, 1800, 25):
        cv2.circle(img, (49, y), 2, (120, 120, 120), -1)
    ok, png = cv2.imencode(".png", img)
    assert ok
    doc = fitz.open()
    pagina = doc.new_page(width=1400 * 72 / 400, height=2000 * 72 / 400)
    pagina.insert_image(pagina.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()


def _projeto(caminho, endireitar: bool) -> Projeto:
    projeto = Projeto(caminho_entrada=str(caminho), nome="teste")
    projeto.dividir_folhas = False
    projeto.endireitar = endireitar
    projeto.limpar = False            # sem filtro: so o corte e o endireitar
    projeto.montar_cadernos = False
    projeto.detectar_regioes = False
    projeto.folhas = [ConfigFolha(indice=0)]
    projeto.paginas = [ConfigPagina(indice=0, folha=0)]
    return projeto


def _fracao_da_previa(caminho, dpi: int, endireitar: bool) -> tuple[float, float]:
    """O caminho da previa da tela (ui/tarefas.py -> renderizar_pagina)."""
    pipeline._GEOMETRIAS.clear()      # cada caminho calcula sozinho, sem ajuda
    projeto = _projeto(caminho, endireitar)
    doc = abrir_pdf(str(caminho))
    try:
        largura_pt, altura_pt = doc[0].rect.width, doc[0].rect.height
        img, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=dpi)
    finally:
        doc.close()
    return img.shape[1] / (largura_pt * dpi / 72), img.shape[0] / (altura_pt * dpi / 72)


def _fracao_do_pdf(caminho, tmp_path, endireitar: bool) -> tuple[float, float]:
    """O caminho do botao "Confirmar e processar" (processar -> PDF gravado):
    o tamanho da pagina gravada, em fracao da pagina de entrada."""
    pipeline._GEOMETRIAS.clear()
    projeto = _projeto(caminho, endireitar)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    entrada, saida = fitz.open(str(caminho)), fitz.open(projeto.caminho_saida)
    try:
        return (saida[0].rect.width / entrada[0].rect.width,
                saida[0].rect.height / entrada[0].rect.height)
    finally:
        entrada.close()
        saida.close()


@pytest.mark.parametrize("endireitar", [False, True])
def test_previa_e_pdf_dao_o_mesmo_corte(tmp_path, endireitar):
    caminho = tmp_path / "pagina.pdf"
    _pdf_com_sujeira_na_margem(caminho)

    previa = _fracao_da_previa(caminho, 110, endireitar)    # a previa "rapida" da tela
    media = _fracao_da_previa(caminho, 180, endireitar)     # a previa "media"
    pdf = _fracao_do_pdf(caminho, tmp_path, endireitar)     # o PDF final (300 DPI)

    # Meio por cento: um ponto de arredondamento na previa de 110 DPI (a pagina
    # tem 385 pontos de largura nela). Antes do conserto: 5,7%.
    for nome, outra in (("previa rapida", previa), ("previa media", media)):
        assert abs(outra[0] - pdf[0]) < 0.005 and abs(outra[1] - pdf[1]) < 0.005, (
            f"{nome} {outra} e PDF {pdf} cortam diferente")


def test_preparar_metade_nunca_abre_o_pdf(monkeypatch):
    """Os cartoes e a tela ampliada chamam preparar_metade no fio da tela: ele
    so usa o corte ja guardado, nunca desenha a pagina de novo (congelaria a
    tela). Sem nada guardado, calcula na propria imagem, como antes."""
    def proibido(*_a, **_k):
        raise AssertionError("preparar_metade abriu o PDF")

    monkeypatch.setattr(pipeline, "abrir_pdf", proibido)
    monkeypatch.setattr(pipeline, "pagina_para_array", proibido)
    pipeline._GEOMETRIAS.clear()
    img = _pagina_de_texto()
    projeto = Projeto(caminho_entrada=__file__)          # um arquivo que existe
    projeto.dividir_folhas = False

    saida = preparar_metade(img, ConfigFolha(indice=0), ConfigPagina(indice=0, folha=0), projeto)

    assert saida.shape[0] < img.shape[0]


def test_sem_o_pdf_o_corte_continua_funcionando():
    """Se o PDF do projeto nao abre (arquivo movido, projeto de teste), o corte
    e calculado na propria imagem, como antes - nunca da erro."""
    img = _pagina_de_texto()
    img[:, :30] = 0                                      # borda preta do scanner
    projeto = Projeto(caminho_entrada=r"C:\nao\existe\livro.pdf")
    projeto.dividir_folhas = False

    saida = preparar_metade(img, ConfigFolha(indice=0), ConfigPagina(indice=0, folha=0), projeto)

    assert saida.shape[1] < img.shape[1] and saida[:, :5].mean() > 100
