"""`core/pipeline.py::processar` compondo o recorte dentro do tamanho de folha
escolhido (Problema 2/4 do teste do Boécio, seção 3a do plano, passo 6).

Gera um PDF de verdade, processa com `processar()`, reabre o PDF gerado com
`fitz` e MEDE (tamanho físico da página + um pixel de borda) - é o jeito
descrito no plano de confirmar que a composição chega até o arquivo final, não
só até uma função isolada.
"""

from __future__ import annotations

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core.filtros import ORIGINAL
from core.pipeline import preparar_metade, preparar_para_recorte, processar
from modelos import ConfigFolha, ConfigPagina, Projeto


def _pdf_de_origem(caminho, largura_cm: float, altura_cm: float, cor_bgr) -> None:
    """Uma página só, do tamanho físico dado, pintada de uma cor sólida."""
    import cv2

    dpi = 300
    largura_px = round(largura_cm / 2.54 * dpi)
    altura_px = round(altura_cm / 2.54 * dpi)
    arte = np.full((altura_px, largura_px, 3), cor_bgr, dtype=np.uint8)
    ok, buffer = cv2.imencode(".png", arte)
    assert ok

    doc = fitz.open()
    largura_pt = largura_cm / 2.54 * 72.0
    altura_pt = altura_cm / 2.54 * 72.0
    pagina = doc.new_page(width=largura_pt, height=altura_pt)
    pagina.insert_image(fitz.Rect(0, 0, largura_pt, altura_pt), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()


def _projeto_uma_pagina(entrada, saida, recorte, tamanho_folha_cm) -> Projeto:
    projeto = Projeto(caminho_entrada=str(entrada), caminho_saida=str(saida), nome="x")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = True     # sem isso pagina.recorte nunca e aplicado
    projeto.limpar = False           # ORIGINAL: sem filtro, so a cor sólida importa
    projeto.montar_cadernos = False
    projeto.detectar_regioes = False
    projeto.qualidade_dpi = 300
    projeto.filtro_padrao = ORIGINAL

    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    projeto.paginas = [ConfigPagina(
        indice=0, folha=0, filtro=ORIGINAL,
        recorte=recorte, tamanho_folha_cm=tamanho_folha_cm,
    )]
    return projeto


def _abrir_pagina_gerada(caminho):
    doc = fitz.open(str(caminho))
    pagina = doc[0]
    pix = pagina.get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    return pagina.rect.width, pagina.rect.height, img, doc


# --- tamanho físico da página final -----------------------------------------

def test_folha_maior_que_o_recorte_gera_pagina_do_tamanho_da_folha(tmp_path):
    """Página de origem 20x20cm, recorte central de 10x10cm, folha de 20x20cm:
    a página final tem que sair com 20x20cm - não com o tamanho do recorte."""
    entrada = tmp_path / "entrada.pdf"
    saida = tmp_path / "saida.pdf"
    _pdf_de_origem(entrada, 20.0, 20.0, (40, 40, 200))  # vermelho (BGR)

    projeto = _projeto_uma_pagina(
        entrada, saida, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=(20.0, 20.0))

    processar(projeto)

    largura_pt, altura_pt, _img, doc = _abrir_pagina_gerada(saida)
    try:
        largura_cm = largura_pt / 72.0 * 2.54
        altura_cm = altura_pt / 72.0 * 2.54
        assert largura_cm == pytest.approx(20.0, abs=0.05)
        assert altura_cm == pytest.approx(20.0, abs=0.05)
    finally:
        doc.close()


def test_folha_maior_sobra_pixel_branco_na_borda(tmp_path):
    """O mesmo caso acima: o CANTO da página final tem que estar branco (a
    margem), e o CENTRO tem que ser a cor do recorte - a composição de
    verdade, não só o tamanho certo por coincidência."""
    entrada = tmp_path / "entrada.pdf"
    saida = tmp_path / "saida.pdf"
    _pdf_de_origem(entrada, 20.0, 20.0, (40, 40, 200))  # vermelho (BGR)

    projeto = _projeto_uma_pagina(
        entrada, saida, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=(20.0, 20.0))

    processar(projeto)

    _largura_pt, _altura_pt, img, doc = _abrir_pagina_gerada(saida)
    try:
        canto = img[3, 3]
        assert canto[0] > 240 and canto[1] > 240 and canto[2] > 240, (
            f"canto devia ser branco, veio {canto}")
        cy, cx = img.shape[0] // 2, img.shape[1] // 2
        centro = img[cy, cx]
        # img veio do fitz (RGB); a cor de origem foi dada em BGR (convencao
        # cv2) como (40, 40, 200) = vermelho - confere o canal R (indice 0).
        assert centro[0] > centro[2] + 40, f"centro devia ser avermelhado: {centro}"
    finally:
        doc.close()


def test_sem_tamanho_de_folha_a_pagina_final_e_do_tamanho_do_recorte(tmp_path):
    """`tamanho_folha_cm=None` (padrao) continua sendo o comportamento de
    sempre: a pagina final e do tamanho do RECORTE, sem sobra nenhuma."""
    entrada = tmp_path / "entrada.pdf"
    saida = tmp_path / "saida.pdf"
    _pdf_de_origem(entrada, 20.0, 20.0, (40, 40, 200))

    projeto = _projeto_uma_pagina(
        entrada, saida, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=None)

    processar(projeto)

    largura_pt, altura_pt, _img, doc = _abrir_pagina_gerada(saida)
    try:
        largura_cm = largura_pt / 72.0 * 2.54
        assert largura_cm == pytest.approx(10.0, abs=0.05), (
            "sem tamanho_folha_cm a pagina devia ter o tamanho do recorte (10cm)")
    finally:
        doc.close()


def test_folha_menor_que_o_recorte_e_rede_de_seguranca_usa_o_recorte(tmp_path):
    """Decisão 2 do plano: na exportação, o pipeline nunca corta nada
    escondido - se a folha registrada não couber de verdade, o tamanho do
    recorte prevalece (redundante com o aviso já mostrado na tela antes)."""
    entrada = tmp_path / "entrada.pdf"
    saida = tmp_path / "saida.pdf"
    _pdf_de_origem(entrada, 20.0, 20.0, (40, 40, 200))

    # recorte de 10x10cm, mas uma folha MENOR (5x5cm) foi registrada
    # (por exemplo: o recorte cresceu depois de a folha ja ter sido escolhida)
    projeto = _projeto_uma_pagina(
        entrada, saida, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=(5.0, 5.0))

    processar(projeto)

    largura_pt, altura_pt, _img, doc = _abrir_pagina_gerada(saida)
    try:
        largura_cm = largura_pt / 72.0 * 2.54
        assert largura_cm == pytest.approx(10.0, abs=0.05), (
            "a folha pequena demais nao pode cortar o recorte escondido")
    finally:
        doc.close()


# --- teste de guarda: preparar_metade nunca ganha padding -------------------
#
# Passo 7 do plano: `preparar_metade` também alimenta `avaliar.py` (a régua
# de qualidade dos filtros, que mede o acervo inteiro offline). Se a
# composição (recorte + margem branca) entrasse aqui, contaminaria as
# métricas com pixels brancos que não vêm do scan - por isso a decisão de
# arquitetura do plano isola `compor_na_folha` só em `processar`, depois do
# filtro. Este teste é a garantia de que isso continua assim.

def test_preparar_metade_nunca_aplica_padding_mesmo_com_tamanho_folha_cm():
    img_folha = np.full((600, 800, 3), 100, dtype=np.uint8)
    folha = ConfigFolha(indice=0, dividir=False)
    pagina = ConfigPagina(
        indice=0, folha=0,
        recorte=(0.25, 0.25, 0.5, 0.5),
        tamanho_folha_cm=(50.0, 50.0),   # bem maior que o recorte
    )
    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.dividir_folhas = False
    projeto.endireitar = False
    projeto.cortar_bordas = True

    saida = preparar_metade(img_folha, folha, pagina, projeto)

    # tamanho do RECORTE (50% de 800x600) - nenhuma sobra branca de folha
    assert saida.shape[1] == pytest.approx(400, abs=2), (
        "preparar_metade nao pode aplicar o tamanho de folha - isso e do "
        "processar(), depois do filtro")
    assert saida.shape[0] == pytest.approx(300, abs=2)


# --- teste de guarda: preparar_para_recorte nunca corta ---------------------
#
# Bug real achado ao vivo (23/09/2026, Samuel): a aba Bordas mostrava a
# mesma prévia já cortada por `pagina.recorte` que as outras abas usam - o
# retângulo do recorte era desenhado como fração de uma imagem que já era um
# recorte, e comprimia sozinho a cada atualização ("corto até a metade da
# coroa, mas o corte vai pra frente"). `preparar_para_recorte` é a base
# ESTÁVEL (girada/dividida, nunca cortada) que resolve isso - este teste
# garante que ela nunca aplica o recorte, não importa o que `pagina.recorte`
# diga.

def test_preparar_para_recorte_nunca_corta_so_gira_e_divide():
    img_folha = np.full((600, 800, 3), 100, dtype=np.uint8)
    folha = ConfigFolha(indice=0, dividir=False)
    pagina = ConfigPagina(indice=0, folha=0, recorte=(0.25, 0.25, 0.5, 0.5))

    saida = preparar_para_recorte(img_folha, folha, pagina)

    assert saida.shape[:2] == img_folha.shape[:2], (
        "preparar_para_recorte nao pode aplicar pagina.recorte - a aba "
        "Bordas precisa da imagem inteira para desenhar o recorte por cima")


def test_preparar_para_recorte_ainda_gira_e_divide():
    from core.dividir import dividir_imagem

    img_folha = np.full((600, 800, 3), 100, dtype=np.uint8)
    folha = ConfigFolha(indice=0, dividir=True, posicao_corte=0.5)
    pagina_esq = ConfigPagina(indice=0, folha=0, metade="esquerda")

    saida = preparar_para_recorte(img_folha, folha, pagina_esq)
    esperado, _ = dividir_imagem(img_folha, 0.5)

    assert saida.shape == esperado.shape
    assert np.array_equal(saida, esperado)
