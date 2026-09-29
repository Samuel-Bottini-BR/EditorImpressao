"""Item 1.1: tirar o fundo de PDF que ja vem com camadas (Internet Archive).

Os PDFs daqui sao montados na hora com o PyMuPDF, do mesmo jeito que o
Internet Archive monta os dele (docs/pesquisa/fase1-1.1-camadas-internet-archive.md):
primeiro uma imagem de fundo sem mascara, depois, por cima, a pagina inteira
colorida recortada por uma mascara de 1 bit. A mascara aqui e Flate, e nao
JBIG2 (o PyMuPDF nao grava JBIG2); o reconhecimento nao depende do filtro.

O detector de figuras e trocado por um falso na maioria dos testes: assim o
teste roda em qualquer maquina, rapido, sem o modelo de layout, e prova a
emenda que o item 1.2 vai usar para pôr o seletor do ScanTailor no lugar.

No fim, alguns testes leem as paginas de verdade do gabarito (pulados se a
pasta gabarito/ nao existir): reconhecimento das 14 paginas com camadas e a
polaridade da mascara JBIG2 conferida contra o desenho do proprio MuPDF.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import fitz
import numpy as np
import pytest

from core import camadas
from core.camadas import (
    DEIXADA_INTACTA,
    FUNDO_TIRADO,
    SEM_CAMADAS,
    camadas_da_pagina,
    compor,
    ler_camadas,
    pdf_tem_camadas,
    resumo_do_pdf,
    tirar_fundo,
    tirar_fundo_do_pdf,
)

# --- montar PDF de teste ------------------------------------------------------

LARGURA_PT, ALTURA_PT = 300, 400
LARGURA_CIMA, ALTURA_CIMA = 600, 800          # 144 DPI
LARGURA_FUNDO, ALTURA_FUNDO = 200, 267        # 1/3, como nas paginas comuns do IA

PAPEL_RGB = (215, 200, 160)     # papel amarelado
MANCHA_RGB = (170, 150, 110)    # mancha d'agua: mais escura que o papel, mas clara
VERMELHO_RGB = (200, 30, 30)    # o titulo vermelho
PRETO_RGB = (25, 20, 20)

# As "letras": retangulos em fracao da pagina (x0, y0, x1, y1).
LETRAS = [(0.10, 0.08, 0.60, 0.12), (0.10, 0.15, 0.80, 0.18),
          (0.10, 0.85, 0.70, 0.88)]


def _pix_rgb(arr: np.ndarray) -> fitz.Pixmap:
    altura, largura = arr.shape[:2]
    return fitz.Pixmap(fitz.csRGB, largura, altura,
                       np.ascontiguousarray(arr, dtype=np.uint8).tobytes(), False)


def fundo_padrao() -> np.ndarray:
    """Papel com uma mancha d'agua grande (clara) no meio."""
    fundo = np.zeros((ALTURA_FUNDO, LARGURA_FUNDO, 3), np.uint8)
    fundo[:] = PAPEL_RGB
    cv2.circle(fundo, (100, 140), 50, MANCHA_RGB, -1)
    return fundo


def cima_padrao() -> np.ndarray:
    """A camada de cima: metade de cima vermelha, metade de baixo preta.

    Fora da mascara a cor dela e lixo (o Internet Archive enche com a cor da
    tinta vizinha); o teste prova que esse lixo nunca aparece.
    """
    cima = np.zeros((ALTURA_CIMA, LARGURA_CIMA, 3), np.uint8)
    cima[: ALTURA_CIMA // 2] = VERMELHO_RGB
    cima[ALTURA_CIMA // 2:] = PRETO_RGB
    return cima


def mascara_padrao() -> np.ndarray:
    m = np.zeros((ALTURA_CIMA, LARGURA_CIMA), bool)
    for x0, y0, x1, y1 in LETRAS:
        m[int(y0 * ALTURA_CIMA):int(y1 * ALTURA_CIMA),
          int(x0 * LARGURA_CIMA):int(x1 * LARGURA_CIMA)] = True
    return m


def _gravar_mascara(doc: fitz.Document, m: np.ndarray, tipo: str) -> int:
    """Cria o objeto da mascara de 1 bit. Na SMask, 1 = aparece; no estencil
    (/Mask com ImageMask), 1 = escondido - por isso o estencil e gravado
    invertido, para as duas mostrarem as MESMAS letras."""
    altura, largura = m.shape
    bits = m if tipo == "smask" else ~m
    xref = doc.get_new_xref()
    if tipo == "smask":
        doc.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {largura} "
                                f"/Height {altura} /ColorSpace /DeviceGray /BitsPerComponent 1 >>")
    else:
        doc.update_object(xref, f"<< /Type /XObject /Subtype /Image /Width {largura} "
                                f"/Height {altura} /ImageMask true /BitsPerComponent 1 >>")
    doc.update_stream(xref, np.packbits(bits.astype(np.uint8), axis=1).tobytes())
    return xref


def acrescentar_pagina_com_camadas(doc: fitz.Document, fundo=None, cima=None, mascara=None,
                                   tipo: str = "smask", cima_primeiro: bool = False,
                                   rotacao: int = 0, caixa_da_cima=None,
                                   mascara_8_bits: bool = False) -> fitz.Page:
    fundo = fundo_padrao() if fundo is None else fundo
    cima = cima_padrao() if cima is None else cima
    mascara = mascara_padrao() if mascara is None else mascara
    pagina = doc.new_page(width=LARGURA_PT, height=ALTURA_PT)
    caixa = pagina.rect if caixa_da_cima is None else fitz.Rect(caixa_da_cima)
    if cima_primeiro:
        xref_cima = pagina.insert_image(caixa, pixmap=_pix_rgb(cima), keep_proportion=False)
        pagina.insert_image(pagina.rect, pixmap=_pix_rgb(fundo), keep_proportion=False)
    else:
        pagina.insert_image(pagina.rect, pixmap=_pix_rgb(fundo), keep_proportion=False)
        xref_cima = pagina.insert_image(caixa, pixmap=_pix_rgb(cima), keep_proportion=False)
    if mascara_8_bits:
        # SMask de 8 bits (transparencia comum), que NAO e a montagem do IA.
        xref_m = doc.get_new_xref()
        altura, largura = mascara.shape
        doc.update_object(xref_m, f"<< /Type /XObject /Subtype /Image /Width {largura} "
                                  f"/Height {altura} /ColorSpace /DeviceGray /BitsPerComponent 8 >>")
        doc.update_stream(xref_m, (mascara.astype(np.uint8) * 255).tobytes())
        doc.xref_set_key(xref_cima, "SMask", f"{xref_m} 0 R")
    elif mascara is not False:
        xref_m = _gravar_mascara(doc, mascara, tipo)
        doc.xref_set_key(xref_cima, "SMask" if tipo == "smask" else "Mask", f"{xref_m} 0 R")
    if rotacao:
        pagina.set_rotation(rotacao)
    return pagina


def pdf_com_camadas(caminho: Path | None = None, **kw) -> fitz.Document:
    doc = fitz.open()
    acrescentar_pagina_com_camadas(doc, **kw)
    if caminho is not None:
        doc.save(caminho)
    return doc


def pdf_comum(n_imagens: int = 1) -> fitz.Document:
    """Scan comum: uma imagem por pagina (ou duas, sem mascara)."""
    doc = fitz.open()
    pagina = doc.new_page(width=LARGURA_PT, height=ALTURA_PT)
    for _ in range(n_imagens):
        pagina.insert_image(pagina.rect, pixmap=_pix_rgb(cima_padrao()), keep_proportion=False)
    return doc


def desenho_do_mupdf(doc: fitz.Document, indice: int, largura: int, altura: int) -> np.ndarray:
    """A pagina como o MuPDF desenha, em BGR, no tamanho pedido."""
    pagina = doc[indice]
    matriz = fitz.Matrix(largura / pagina.rect.width, altura / pagina.rect.height)
    pix = pagina.get_pixmap(matrix=matriz, alpha=False)
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return cv2.resize(img, (largura, altura), interpolation=cv2.INTER_AREA) \
        if img.shape[:2] != (altura, largura) else img


def sem_figuras(img: np.ndarray) -> np.ndarray:
    return np.zeros(img.shape[:2], np.float32)


def bgr(rgb) -> np.ndarray:
    return np.array(rgb[::-1], np.float32)


# --- (a) reconhecer ------------------------------------------------------------


@pytest.mark.parametrize("tipo", ["smask", "estencil"])
def test_reconhece_a_montagem_do_internet_archive(tipo):
    doc = pdf_com_camadas(tipo=tipo)
    achadas = camadas_da_pagina(doc, 0)
    assert achadas is not None
    assert achadas.tipo_mascara == tipo
    assert achadas.tamanho_cima == (LARGURA_CIMA, ALTURA_CIMA)
    assert achadas.tamanho_fundo == (LARGURA_FUNDO, ALTURA_FUNDO)


def test_scan_comum_de_uma_imagem_nao_tem_camadas():
    assert camadas_da_pagina(pdf_comum(1), 0) is None


def test_duas_imagens_sem_mascara_nao_e_a_montagem():
    assert camadas_da_pagina(pdf_comum(2), 0) is None


def test_pagina_sem_imagem_nao_tem_camadas():
    doc = fitz.open()
    doc.new_page().insert_text((50, 50), "so texto")
    assert camadas_da_pagina(doc, 0) is None


def test_camada_com_mascara_desenhada_primeiro_nao_e_a_montagem():
    assert camadas_da_pagina(pdf_com_camadas(cima_primeiro=True), 0) is None


def test_mascara_de_8_bits_nao_e_a_montagem():
    assert camadas_da_pagina(pdf_com_camadas(mascara_8_bits=True), 0) is None


def test_camada_de_cima_que_nao_cobre_a_pagina_nao_e_a_montagem():
    doc = pdf_com_camadas(caixa_da_cima=(0, 0, LARGURA_PT / 2, ALTURA_PT))
    assert camadas_da_pagina(doc, 0) is None


def test_resumo_do_pdf_conta_as_paginas_com_camadas():
    doc = fitz.open()
    acrescentar_pagina_com_camadas(doc)
    doc.new_page(width=LARGURA_PT, height=ALTURA_PT).insert_image(
        fitz.Rect(0, 0, LARGURA_PT, ALTURA_PT), pixmap=_pix_rgb(cima_padrao()),
        keep_proportion=False)
    acrescentar_pagina_com_camadas(doc, tipo="estencil")
    resumo = resumo_do_pdf(doc)
    assert resumo.paginas == 3
    assert resumo.com_camadas == [0, 2]
    assert pdf_tem_camadas(doc)
    assert not pdf_tem_camadas(pdf_comum(1))


def test_leitor_do_conteudo_acompanha_q_Q_cm_e_ignora_texto():
    conteudo = (b"q 0.18 0 0 0.18 0 0 cm BT (texto com /Falso Do e (parenteses)) Tj "
                b"<48656c6c6f> Tj [(a\\)b) 10 (c)] TJ ET Q\n"
                b"q 423 0 0 635 0 0 cm /img72 Do /Im001 Do Q % comentario /X Do\n")
    desenhos = camadas.imagens_desenhadas(conteudo)
    assert [nome for nome, _ in desenhos] == ["img72", "Im001"]
    assert desenhos[0][1] == pytest.approx((423, 0, 0, 635, 0, 0))


def test_leitor_do_conteudo_desiste_de_imagem_embutida():
    conteudo = b"q 10 0 0 10 0 0 cm BI /W 1 /H 1 /BPC 8 /CS /G ID \x00 EI Q"
    assert camadas.imagens_desenhadas(conteudo) is None


def test_reconhecer_nao_decodifica_as_imagens():
    """Reconhecer tem de ser barato: a lista de imagens e o conteudo da pagina,
    sem abrir o JPEG 2000. Medido por tempo num livro inteiro fica no
    relatorio; aqui so garante que nao ha Pixmap no caminho."""
    doc = pdf_com_camadas()
    original = fitz.Pixmap
    chamadas = []

    class Espiao(original):  # type: ignore[misc, valid-type]
        def __init__(self, *a, **k):
            chamadas.append(a)
            super().__init__(*a, **k)

    fitz.Pixmap = Espiao
    try:
        assert camadas_da_pagina(doc, 0) is not None
    finally:
        fitz.Pixmap = original
    assert chamadas == []


# --- (b) montar a pagina sem o fundo ------------------------------------------


@pytest.mark.parametrize("tipo", ["smask", "estencil"])
def test_papel_vira_branco_e_a_letra_guarda_a_cor(tipo):
    doc = pdf_com_camadas(tipo=tipo)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == FUNDO_TIRADO
    img = resultado.imagem
    assert img.shape[:2] == (ALTURA_CIMA, LARGURA_CIMA)

    m = mascara_padrao()
    miolo = cv2.erode(m.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    longe = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)) == 0

    # papel (inclusive onde estava a mancha d'agua) = branco
    assert img[longe].min() >= 250
    # letra de cima vermelha continua vermelha; a de baixo continua preta
    vermelho = img[miolo & (np.arange(ALTURA_CIMA)[:, None] < ALTURA_CIMA // 2)]
    preto = img[miolo & (np.arange(ALTURA_CIMA)[:, None] >= ALTURA_CIMA // 2)]
    assert np.abs(vermelho.astype(np.float32) - bgr(VERMELHO_RGB)).max() <= 2
    assert np.abs(preto.astype(np.float32) - bgr(PRETO_RGB)).max() <= 2


@pytest.mark.parametrize("tipo", ["smask", "estencil"])
def test_a_pagina_como_o_pdf_desenha_bate_com_o_mupdf(tipo):
    """A leitura das camadas (polaridade da mascara, orientacao, escala do
    fundo) confere com o desenho do proprio MuPDF: peso de figura 1 em toda a
    pagina = a pagina exatamente como o PDF mostra."""
    doc = pdf_com_camadas(tipo=tipo)
    lidas = ler_camadas(doc, 0)
    peso = np.ones((lidas.altura, lidas.largura), np.float32)
    como_o_pdf = compor(lidas, peso)
    mupdf = desenho_do_mupdf(doc, 0, lidas.largura, lidas.altura)
    diferenca = np.abs(como_o_pdf.astype(np.int16) - mupdf.astype(np.int16))
    assert diferenca.mean() < 2.0
    assert np.percentile(diferenca, 99) <= 40   # so a borda da mancha, reamostrada diferente


@pytest.mark.parametrize("rotacao", [90, 180, 270])
def test_pagina_girada_sai_na_mesma_posicao_que_o_mupdf_mostra(rotacao):
    doc = pdf_com_camadas(rotacao=rotacao)
    lidas = ler_camadas(doc, 0)
    como_o_pdf = compor(lidas, np.ones((lidas.altura, lidas.largura), np.float32))
    mupdf = desenho_do_mupdf(doc, 0, lidas.largura, lidas.altura)
    assert como_o_pdf.shape == mupdf.shape
    assert np.abs(como_o_pdf.astype(np.int16) - mupdf.astype(np.int16)).mean() < 2.0


def test_dpi_pedido_define_o_tamanho():
    doc = pdf_com_camadas()
    resultado = tirar_fundo(doc, 0, dpi=72, detector_de_figuras=sem_figuras)
    assert resultado.imagem.shape[:2] == (ALTURA_PT, LARGURA_PT)
    assert resultado.dpi == pytest.approx(72, abs=0.5)


def test_reduzido_a_letra_continua_com_a_cor():
    """No tamanho da previa a tinta e reamostrada: a cor da letra nao pode
    puxar para o lixo que a camada de cima tem fora da mascara."""
    doc = pdf_com_camadas()
    img = tirar_fundo(doc, 0, dpi=72, detector_de_figuras=sem_figuras).imagem
    x0, y0, x1, y1 = LETRAS[0]
    miolo = img[int(y0 * ALTURA_PT) + 3:int(y1 * ALTURA_PT) - 3,
                int(x0 * LARGURA_PT) + 3:int(x1 * LARGURA_PT) - 3]
    assert np.abs(miolo.astype(np.float32) - bgr(VERMELHO_RGB)).max() <= 3


def test_previa_e_pdf_final_decidem_na_mesma_resolucao():
    """O detector e as medidas trabalham sempre a DPI_DA_ANALISE, tirada da
    camada de cima, qualquer que seja o DPI de saida: senao a previa (110 DPI)
    e o PDF final (300 DPI) poderiam decidir diferente."""
    tamanhos = []

    def espiao(img):
        tamanhos.append(img.shape[:2])
        return detector_que_acha_a_foto(img)

    doc = pdf_com_camadas(fundo=fundo_com_foto(), mascara=mascara_com_pontinhos())
    resultados = [tirar_fundo(doc, 0, dpi=d, detector_de_figuras=espiao) for d in (60, None, 300)]
    assert len(set(tamanhos)) == 1
    assert len({(r.situacao, r.zonas_mantidas) for r in resultados}) == 1
    assert resultados[0].imagem.shape[:2] == (round(ALTURA_PT * 60 / 72), round(LARGURA_PT * 60 / 72))
    assert resultados[2].imagem.shape[:2] == (round(ALTURA_PT * 300 / 72), round(LARGURA_PT * 300 / 72))


def test_traco_que_so_existia_no_fundo_fora_das_zonas_pede_conferencia():
    """Moldura grossa que a mascara do Internet Archive furou: os furos so
    tem tinta no fundo. O fundo sai, mas a pagina vem marcada para conferir."""
    fundo = fundo_padrao()
    fundo[:] = PAPEL_RGB
    mascara = mascara_padrao()
    rng = np.random.default_rng(3)
    for y0 in (300, 420, 540):
        faixa = (slice(y0, y0 + 40), slice(30, 570))
        mascara[faixa] = rng.random((40, 540)) > 0.35          # 35% de furos
        yf = slice(int(y0 * ALTURA_FUNDO / ALTURA_CIMA), int((y0 + 40) * ALTURA_FUNDO / ALTURA_CIMA))
        fundo[yf, 10:190] = (40, 35, 30)                        # o fio inteiro, no fundo
    doc = pdf_com_camadas(fundo=fundo, mascara=mascara)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.conferir
    assert "Confira" in resultado.explicacao
    # e uma pagina limpa nao pede
    assert not tirar_fundo(pdf_com_camadas(), 0, detector_de_figuras=sem_figuras).conferir


def test_pagina_sem_camadas_nao_se_aplica():
    resultado = tirar_fundo(pdf_comum(1), 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == SEM_CAMADAS
    assert resultado.imagem is None
    assert resultado.explicacao


# --- figura: o que so existe no fundo -----------------------------------------

# A "foto": um degrade escuro que so existe no fundo, com pontinhos escuros na
# camada de cima (como a estatua do Opus Majus 20).
FOTO = (0.20, 0.30, 0.80, 0.70)


def fundo_com_foto() -> np.ndarray:
    fundo = fundo_padrao()
    fundo[:] = PAPEL_RGB
    x0, y0, x1, y1 = FOTO
    a, b = int(x0 * LARGURA_FUNDO), int(x1 * LARGURA_FUNDO)
    c, d = int(y0 * ALTURA_FUNDO), int(y1 * ALTURA_FUNDO)
    degrade = np.linspace(30, 190, b - a, dtype=np.float32)[None, :, None]
    fundo[c:d, a:b] = np.repeat(np.repeat(degrade, d - c, axis=0), 3, axis=2).astype(np.uint8)
    return fundo


def mascara_com_pontinhos() -> np.ndarray:
    m = mascara_padrao()
    x0, y0, x1, y1 = FOTO
    rng = np.random.default_rng(1)
    zona = (slice(int(y0 * ALTURA_CIMA), int(y1 * ALTURA_CIMA)),
            slice(int(x0 * LARGURA_CIMA), int(x1 * LARGURA_CIMA)))
    pontos = rng.random(m[zona].shape) < 0.03
    m[zona] |= pontos
    return m


def detector_que_acha_a_foto(img: np.ndarray) -> np.ndarray:
    altura, largura = img.shape[:2]
    peso = np.zeros((altura, largura), np.float32)
    x0, y0, x1, y1 = FOTO
    peso[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)] = 1.0
    return peso


def _meio_da_foto(img: np.ndarray) -> np.ndarray:
    altura, largura = img.shape[:2]
    x0, y0, x1, y1 = FOTO
    return img[int((y0 + 0.05) * altura):int((y1 - 0.05) * altura),
               int((x0 + 0.05) * largura):int((x1 - 0.05) * largura)]


def test_figura_achada_fica_como_o_pdf_desenha():
    doc = pdf_com_camadas(fundo=fundo_com_foto(), mascara=mascara_com_pontinhos())
    resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_que_acha_a_foto)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.zonas_mantidas == 1
    img = resultado.imagem
    lidas = ler_camadas(doc, 0)
    como_o_pdf = compor(lidas, np.ones((lidas.altura, lidas.largura), np.float32))
    # dentro da foto: igual ao PDF (tons do fundo preservados)
    dif = np.abs(_meio_da_foto(img).astype(np.int16) - _meio_da_foto(como_o_pdf).astype(np.int16))
    assert dif.mean() < 1.0
    # o lado escuro da foto continua escuro (nao virou pontilhado no branco)
    assert _meio_da_foto(img)[:, :20].mean() < 90
    # fora da foto: papel branco
    assert img[5:40, 5:40].min() >= 250


def test_zona_de_figura_sem_tons_no_fundo_vai_a_branco():
    """O detector de hoje marca paginas inteiras de tabela ou de esquema como
    gravura (Opus 256, Rhetorica 73). Se o fundo dentro da zona e so papel (e
    mancha clara), tudo o que a figura tem esta na camada de cima: a zona sai
    como o resto, com o papel branco."""
    doc = pdf_com_camadas()   # fundo: papel + mancha d'agua clara
    tudo = lambda img: np.ones(img.shape[:2], np.float32)  # noqa: E731
    resultado = tirar_fundo(doc, 0, detector_de_figuras=tudo)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.zonas_mantidas == 0
    m = mascara_padrao()
    longe = cv2.dilate(m.astype(np.uint8), np.ones((9, 9), np.uint8)) == 0
    assert resultado.imagem[longe].min() >= 250


ZONA_DA_GRAVURA = (0.20, 0.30, 0.80, 0.70)


def detector_que_acha_a_gravura(img: np.ndarray) -> np.ndarray:
    altura, largura = img.shape[:2]
    peso = np.zeros((altura, largura), np.float32)
    x0, y0, x1, y1 = ZONA_DA_GRAVURA
    peso[int(y0 * altura):int(y1 * altura), int(x0 * largura):int(x1 * largura)] = 1.0
    return peso


def test_hachura_que_so_ficou_no_fundo_mantem_a_zona():
    """Palatino 5 e 9: a mascara do Internet Archive pega so parte da hachura
    da xilogravura; o resto ficou no fundo. Tirar o fundo ali quebraria a
    gravura: a zona fica como o PDF desenha."""
    fundo = fundo_padrao()
    fundo[:] = PAPEL_RGB
    mascara = mascara_padrao()
    x0, y0, x1, y1 = ZONA_DA_GRAVURA
    # linhas de hachura: metade na camada de cima, metade so no fundo
    for i, y in enumerate(range(int(y0 * ALTURA_CIMA) + 4, int(y1 * ALTURA_CIMA) - 4, 9)):
        faixa = slice(int(x0 * LARGURA_CIMA) + 4, int(x1 * LARGURA_CIMA) - 4)
        if i % 2 == 0:
            mascara[y:y + 3, faixa] = True
        else:
            yf = int(y * ALTURA_FUNDO / ALTURA_CIMA)
            fundo[yf:yf + 2, int(x0 * LARGURA_FUNDO) + 2:int(x1 * LARGURA_FUNDO) - 2] = (60, 50, 40)
    doc = pdf_com_camadas(fundo=fundo, mascara=mascara)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_que_acha_a_gravura)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.zonas_mantidas == 1


def fundo_de_cartao_com_linho(cartao=(150, 130, 110), linho=(235, 235, 225)) -> np.ndarray:
    """Livro de bordados da Pesel: o "papel" e um cartao pardo e a foto (o
    linho bordado) e MAIS CLARA que ele, e so existe no fundo. O cartao
    padrao (cinza 134) ainda passa por papel; o da Pesel de verdade (cinza 95
    a 105) e escuro demais e a pagina fica intacta por outra regra."""
    fundo = np.zeros((ALTURA_FUNDO, LARGURA_FUNDO, 3), np.uint8)
    fundo[:] = cartao
    x0, y0, x1, y1 = ZONA_DA_GRAVURA
    fundo[int(y0 * ALTURA_FUNDO):int(y1 * ALTURA_FUNDO),
          int(x0 * LARGURA_FUNDO):int(x1 * LARGURA_FUNDO)] = linho
    return fundo


def test_papel_escuro_demais_e_capa_ou_cartao_e_fica_intacta():
    """Capa de couro do Siebmacher (cinza 102), cartao da Pesel (83 a 105)."""
    doc = pdf_com_camadas(fundo=fundo_de_cartao_com_linho(cartao=(110, 95, 80)))
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == DEIXADA_INTACTA
    assert resultado.imagem is None


def test_foto_mais_clara_que_o_papel_mantem_a_zona():
    doc = pdf_com_camadas(fundo=fundo_de_cartao_com_linho())
    resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_que_acha_a_gravura)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.zonas_mantidas == 1


def test_foto_mais_clara_que_o_papel_sem_zona_deixa_a_pagina_intacta():
    doc = pdf_com_camadas(fundo=fundo_de_cartao_com_linho())
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == DEIXADA_INTACTA


def test_pintura_com_o_brilho_do_papel_conta_pela_cor():
    """Dourado ou pintura clara: quase o brilho do papel, mas outra cor.
    Aqui um ceu azul-claro: cinza 190 contra 200 do papel."""
    fundo = fundo_padrao()
    fundo[:] = PAPEL_RGB
    x0, y0, x1, y1 = ZONA_DA_GRAVURA
    fundo[int(y0 * ALTURA_FUNDO):int(y1 * ALTURA_FUNDO),
          int(x0 * LARGURA_FUNDO):int(x1 * LARGURA_FUNDO)] = (150, 200, 240)
    doc = pdf_com_camadas(fundo=fundo)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_que_acha_a_gravura)
    assert resultado.zonas_mantidas == 1


def test_pagina_inteira_de_figura_com_tinta_no_fundo_fica_intacta():
    """O detector de hoje marca a pagina inteira do Palatino 5 como gravura, e
    o retrato tem hachura so no fundo: montar daria a propria pagina. O
    resultado diz isso (intacta, imagem None) em vez de fingir que tirou."""
    doc = pdf_com_camadas(fundo=fundo_com_foto(), mascara=mascara_com_pontinhos())
    tudo = lambda img: np.ones(img.shape[:2], np.float32)  # noqa: E731
    resultado = tirar_fundo(doc, 0, detector_de_figuras=tudo)
    assert resultado.situacao == DEIXADA_INTACTA
    assert resultado.imagem is None
    assert resultado.zonas_mantidas == 1


def test_letra_fantasma_embaixo_da_tinta_nao_segura_a_zona():
    """O fundo guarda letras "fantasma" exatamente embaixo da tinta de cima (o
    preenchimento do Internet Archive nao e perfeito; medido no Palatino 5:
    cinza 147 contra 199 do papel). Isso nao e figura: a camada de cima ja
    cobre, e a zona sai branca."""
    fundo = fundo_padrao()
    fundo[:] = PAPEL_RGB
    mascara = mascara_padrao()
    x0, y0, x1, y1 = ZONA_DA_GRAVURA
    for y in range(int(y0 * ALTURA_CIMA) + 6, int(y1 * ALTURA_CIMA) - 6, 12):
        mascara[y:y + 6, int(x0 * LARGURA_CIMA) + 6:int(x1 * LARGURA_CIMA) - 6] = True
        yf = int(y * ALTURA_FUNDO / ALTURA_CIMA)
        fundo[yf:yf + 2, int(x0 * LARGURA_FUNDO) + 2:int(x1 * LARGURA_FUNDO) - 2] = (165, 150, 110)
    doc = pdf_com_camadas(fundo=fundo, mascara=mascara)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=detector_que_acha_a_gravura)
    assert resultado.situacao == FUNDO_TIRADO
    assert resultado.zonas_mantidas == 0


def test_foto_que_o_detector_nao_viu_deixa_a_pagina_intacta():
    """Rede de seguranca: nunca apagar a foto. Se o fundo tem uma area grande
    e escura que nenhuma zona de figura cobre, a pagina fica como esta."""
    doc = pdf_com_camadas(fundo=fundo_com_foto(), mascara=mascara_com_pontinhos())
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == DEIXADA_INTACTA
    assert resultado.imagem is None
    assert "foto" in resultado.explicacao or "figura" in resultado.explicacao


def test_capa_de_pano_fica_intacta():
    """Capa do Opus Majus e da Pesel: a mascara cobre a trama do pano quase
    inteira (0% a 6% de fundo livre). Tirar o fundo deixaria so pontinhos no
    branco; a pagina fica como esta."""
    fundo = np.zeros((ALTURA_FUNDO, LARGURA_FUNDO, 3), np.uint8)
    fundo[:] = (110, 30, 40)                                   # pano vermelho-escuro
    trama = np.zeros((ALTURA_CIMA, LARGURA_CIMA), bool)
    trama[::3, :] = True                                       # fio sim, fio nao
    trama[:, ::3] = True
    doc = pdf_com_camadas(fundo=fundo, mascara=trama)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == DEIXADA_INTACTA
    assert resultado.imagem is None


def test_borda_escura_do_scanner_nao_segura_a_pagina():
    """O preto de fora do livro (Siebmacher) encosta na borda da imagem: nao e
    foto, e a pagina segue sem o fundo."""
    fundo = fundo_padrao()
    fundo[:, -25:] = (15, 15, 15)
    doc = pdf_com_camadas(fundo=fundo)
    resultado = tirar_fundo(doc, 0, detector_de_figuras=sem_figuras)
    assert resultado.situacao == FUNDO_TIRADO
    # a borda preta estava so no fundo: some junto com ele
    assert resultado.imagem[:, -30:].mean() > 250


def test_detector_padrao_e_o_de_hoje_e_pode_ser_trocado():
    assert camadas.DETECTOR_DE_FIGURAS is camadas.figuras_pelo_detector_atual
    img = np.full((300, 220, 3), 230, np.uint8)
    peso = camadas.figuras_pelo_detector_atual(img)
    assert peso.shape == (300, 220)
    assert peso.dtype == np.float32
    assert 0.0 <= float(peso.min()) and float(peso.max()) <= 1.0


# --- a porta da conferencia -----------------------------------------------------


def test_funcao_da_conferencia_devolve_a_imagem(tmp_path):
    caminho = tmp_path / "pagina.pdf"
    pdf_com_camadas(caminho)
    antes = np.zeros((10, 10, 3), np.uint8)
    img = tirar_fundo_do_pdf(caminho, antes, detector_de_figuras=sem_figuras)
    assert img.shape[:2] == (ALTURA_CIMA, LARGURA_CIMA)


def test_funcao_da_conferencia_avisa_quando_nao_se_aplica(tmp_path):
    caminho = tmp_path / "comum.pdf"
    pdf_comum(1).save(caminho)
    with pytest.raises(camadas.NaoSeAplica):
        tirar_fundo_do_pdf(caminho, np.zeros((10, 10, 3), np.uint8))


# --- paginas de verdade do gabarito (pula se a pasta nao existir) -------------

GABARITO = Path(__file__).resolve().parent.parent / "gabarito" / "paginas"
COM_CAMADAS = ["palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
               "palatino_p057", "opusmajus_p003", "opusmajus_p011", "opusmajus_p020",
               "opusmajus_p165", "opusmajus_p256", "rhetorica_p018", "rhetorica_p073",
               "siebmacher_p007", "siebmacher_p009"]
SEM_CAMADAS_NO_GABARITO = ["horas_p011", "escola_p035", "marial_p007", "graduale_p221"]

precisa_do_gabarito = pytest.mark.skipif(not GABARITO.is_dir(),
                                         reason="pasta gabarito/ ausente nesta maquina")


@precisa_do_gabarito
@pytest.mark.parametrize("pid", COM_CAMADAS)
def test_gabarito_paginas_com_camadas_sao_reconhecidas(pid):
    with fitz.open(GABARITO / f"{pid}.pdf") as doc:
        achadas = camadas_da_pagina(doc, 0)
    assert achadas is not None, pid
    esperado = "estencil" if pid.startswith("siebmacher") else "smask"
    assert achadas.tipo_mascara == esperado


@precisa_do_gabarito
@pytest.mark.parametrize("pid", SEM_CAMADAS_NO_GABARITO)
def test_gabarito_paginas_comuns_nao_tem_camadas(pid):
    with fitz.open(GABARITO / f"{pid}.pdf") as doc:
        assert camadas_da_pagina(doc, 0) is None


@precisa_do_gabarito
@pytest.mark.parametrize("pid", ["siebmacher_p009", "rhetorica_p073", "palatino_p005"])
def test_gabarito_mascara_jbig2_le_como_o_mupdf_desenha(pid):
    """Siebmacher: estencil; Rhetorica: SMask com /Decode [1 0]; Palatino:
    SMask comum. Nos tres, a pagina recomposta tem de bater com o desenho do
    MuPDF (se a polaridade estivesse trocada, o papel viria da camada de cima).

    Comparado depois de um borrão leve: no Palatino, hachura fina a 400 DPI,
    o MuPDF reduz a imagem com outro filtro e desloca 0,04 pt, e pixel a pixel
    a diferença média fica em 8 a 11 níveis só por isso (medido em 28/09/2026;
    borrado, 1,8 a 3,2). Com a polaridade trocada ela passaria de 50."""
    with fitz.open(GABARITO / f"{pid}.pdf") as doc:
        lidas = ler_camadas(doc, 0, dpi=100)
        como_o_pdf = compor(lidas, np.ones((lidas.altura, lidas.largura), np.float32))
        mupdf = desenho_do_mupdf(doc, 0, lidas.largura, lidas.altura)
    borrado = [cv2.GaussianBlur(img, (0, 0), 2).astype(np.int16) for img in (como_o_pdf, mupdf)]
    assert np.abs(borrado[0] - borrado[1]).mean() < 5.0
