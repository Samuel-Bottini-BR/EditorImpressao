"""O modo Misto (Fase 2, 05/10/2026), testado em paginas sinteticas.

Pedido do Samuel (conferencia 5, X3): "eu quero ter a opcao de colocar [o
filtro] onde eu escolher, se quero so nos textos ou nas gravuras, como tem no
ScanTailor Advanced". Proposta aceita (D1, 02/10): "Modo Misto: o Preto e
branco so nas letras; gravuras e fotos ficam como estao; e voce corrige a mao,
marcando zonas, onde o automatico errar." E a caixinha "So as letras" do item
1.5 (30/09): "marcada, so as letras viram preto e branco, e gravuras, fotos,
molduras, iluminuras e outros detalhes coloridos ficam como no original."

Quem faz: core/misto.py (aplicar_misto). Ainda NAO ligado ao programa (nem
tela, nem projeto): so por linha de comando. Testes de maquina; as paginas
sao desenhadas aqui, sem o acervo.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import ORIGINAL, PRETO_E_BRANCO, aplicar_filtro_com_selecao
from core.misto import aplicar_misto
from core.selecao import GRAVURA, LETRA, MAO, PAPEL, SUBTRAIR, Selecao, retangulo

PAPEL_CREME = (200, 222, 232)       # BGR
DOURADO = (70, 175, 215)
CONTORNO = (40, 60, 120)


def _texto(img, y0, y1, x0=100, x1=900, passo=16, cor=(30, 30, 30)):
    """Linhas de "letras": tracos de 4 x 12 pontos a cada `passo`."""
    for y in range(y0, y1, 40):
        for x in range(x0, x1, passo):
            img[y:y + 12, x:x + 4] = cor


def _moldura(altura=1200, largura=900, faixa=48, margem=100):
    img = np.full((altura, largura, 3), PAPEL_CREME, np.uint8)
    m = np.zeros((altura, largura), np.uint8)
    cv2.rectangle(m, (margem, margem), (largura - margem, altura - margem), 255, faixa)
    img[m > 0] = DOURADO
    meia = faixa // 2
    for d in (-meia, meia):
        cv2.rectangle(img, (margem + d, margem + d),
                      (largura - margem - d, altura - margem - d), CONTORNO, 3)
    return img, m > 0


def _so_na_moldura(faixa):
    s = Selecao()
    altura, largura = faixa.shape
    ys, xs = np.nonzero(faixa)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    esp = 60
    for (a, b, c, d) in ((x0 - 6, y0 - 6, x1 + 6, y0 + esp), (x0 - 6, y1 - esp, x1 + 6, y1 + 6),
                         (x0 - 6, y0 - 6, x0 + esp, y1 + 6), (x1 - esp, y0 - 6, x1 + 6, y1 + 6)):
        s.acrescentar(retangulo(a / largura, b / altura, c / largura, d / altura, tipo=GRAVURA))
    return s


def _pagina_com_foto():
    """Texto em cima e uma "foto" colorida em degrade embaixo, marcada."""
    img = np.full((1200, 900, 3), PAPEL_CREME, np.uint8)
    _texto(img, 80, 380)
    degrade = np.linspace(60, 200, 400).astype(np.int16)
    foto = np.dstack([degrade[None, :]] * 3).repeat(400, axis=0)
    foto[:, :, 0] -= 40                     # amarelada: tem cor
    foto[:, :, 2] += 20
    img[600:1000, 250:650] = np.clip(foto, 0, 255).astype(np.uint8)
    s = Selecao()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 650 / 900, 1000 / 1200, tipo=GRAVURA))
    return img, s


def _pagina_com_hachura():
    """Texto em cima e uma xilogravura (hachura cinza-escura sobre papel
    creme) embaixo, marcada como gravura."""
    img = np.full((1200, 900, 3), PAPEL_CREME, np.uint8)
    _texto(img, 80, 380)
    for x in range(200, 700, 10):
        img[600:1000, x:x + 3] = (80, 85, 95)
    s = Selecao()
    s.acrescentar(retangulo(180 / 900, 580 / 1200, 720 / 900, 1020 / 1200, tipo=GRAVURA))
    return img, s


# --- sem gravura: e o Preto e branco de sempre --------------------------------

def test_sem_marcacao_e_o_preto_e_branco_de_sempre():
    img = np.full((800, 600, 3), PAPEL_CREME, np.uint8)
    _texto(img, 100, 700, x1=550)
    saida, mono = aplicar_misto(img.copy(), Selecao())
    esperado, mono_esperado = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, Selecao())
    assert mono is True and mono_esperado is True
    assert np.array_equal(saida, esperado)


def test_sem_gravura_marcada_e_identico_ao_preto_e_branco():
    """Pagina so de texto com letra e papel marcados (o que o detector faz):
    nada muda em relacao ao Preto e branco de hoje."""
    img = np.full((800, 600, 3), PAPEL_CREME, np.uint8)
    _texto(img, 100, 700, x1=550)
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.1, 0.95, 0.9, tipo=LETRA))
    s.acrescentar(retangulo(0.0, 0.92, 1.0, 1.0, tipo=PAPEL))
    saida, mono = aplicar_misto(img.copy(), s)
    esperado, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert mono is True
    assert np.array_equal(saida, esperado)


# --- as letras viram preto e branco --------------------------------------------

def test_as_letras_saem_em_preto_e_branco_e_o_vermelho_sai_preto():
    """Regra V1 (30/09): no Preto e branco o vermelho sai preto - vale nas
    letras do Misto."""
    img, s = _pagina_com_foto()
    _texto(img, 420, 440, cor=(50, 50, 200))           # uma linha vermelha
    saida, _ = aplicar_misto(img.copy(), s)
    texto = saida[60:450, 60:860]
    assert (texto.min(axis=2) == texto.max(axis=2)).all(), "o texto ficou com cor"
    assert set(np.unique(texto)) <= {0, 255}, "o texto tinha de sair em preto e branco"
    assert float((saida[424:430, 101:800:16] == 0).mean()) > 0.9, "a linha vermelha nao saiu preta"


# --- foto: fica como esta ----------------------------------------------------

def test_a_foto_fica_como_no_original_com_a_cor():
    img, s = _pagina_com_foto()
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is False and saida.ndim == 3
    miolo = (slice(650, 950), slice(300, 600))
    diferenca = np.abs(saida[miolo].astype(int) - img[miolo].astype(int))
    assert int(diferenca.max()) <= 1, "a foto mudou: no Misto ela fica como esta"


def test_foto_em_cinza_quando_pedido():
    """Variante para o Samuel escolher (foto em tons de cinza, como no Preto
    e branco de 30/09)."""
    img, s = _pagina_com_foto()
    saida, _ = aplicar_misto(img.copy(), s, foto_em_cinza=True)
    foto = saida[650:950, 300:600].astype(int)
    if saida.ndim == 3:
        assert int(np.abs(foto[:, :, 0] - foto[:, :, 2]).max()) <= 1, "a foto ficou com cor"
    assert len(np.unique(foto)) > 30, "a foto perdeu o tom continuo"


# --- moldura dourada: a cor original (como no Preto e branco de hoje) ----------

def test_a_moldura_dourada_mantem_a_cor_original():
    img, faixa = _moldura()
    _texto(img, 300, 900, x0=250, x1=650)
    saida, mono = aplicar_misto(img.copy(), _so_na_moldura(faixa))
    assert mono is False and saida.ndim == 3
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    diferenca = np.abs(saida[miolo].astype(int) - img[miolo].astype(int))
    assert int(np.percentile(diferenca, 99)) <= 2, "o dourado mudou de cor"
    # o texto de dentro: preto e branco
    dentro = saida[300:900, 250:650]
    assert (dentro.min(axis=2) == dentro.max(axis=2)).all() and set(np.unique(dentro)) <= {0, 255}


def test_so_moldura_da_o_mesmo_que_o_preto_e_branco_de_hoje():
    """Moldura e iluminura ja ficam em cor no Preto e branco (emenda N2): com
    so moldura na pagina, Misto e Preto e branco dao a mesma imagem."""
    img, faixa = _moldura()
    _texto(img, 300, 900, x0=250, x1=650)
    s = _so_na_moldura(faixa)
    saida, _ = aplicar_misto(img.copy(), s)
    esperado, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert np.array_equal(saida, esperado)


# --- gravura de traco: o desenho fica como esta, o papel dela vai a branco -----

def test_a_gravura_de_traco_mantem_o_tom_e_o_papel_vai_a_branco():
    img, s = _pagina_com_hachura()
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is False
    cinza = saida if saida.ndim == 2 else cv2.cvtColor(saida, cv2.COLOR_BGR2GRAY)
    original = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    traco = original[700:900, 200:700] < 120
    # o traco fica com o tom do original (nao vira preto chapado)
    assert abs(float(cinza[700:900, 200:700][traco].mean()) - float(original[700:900, 200:700][traco].mean())) < 6
    # e o papel entre os tracos vai a branco
    papel = ~cv2.dilate(traco.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    assert float(np.median(cinza[700:900, 200:700][papel])) >= 245


def test_gravura_de_traco_sem_branquear_o_papel_quando_pedido():
    """Variante "exatamente como o original" (o Misto do ScanTailor): o papel
    de dentro da gravura fica creme."""
    img, s = _pagina_com_hachura()
    saida, _ = aplicar_misto(img.copy(), s, papel_da_gravura_branco=False)
    miolo = (slice(700, 900), slice(204, 209))          # entre dois tracos
    diferenca = np.abs(saida[miolo].astype(int) - img[miolo].astype(int))
    assert int(diferenca.max()) <= 1


# --- as zonas feitas a mao ----------------------------------------------------

def test_letra_marcada_a_mao_ganha_da_gravura_automatica():
    """O detector pos o titulo dentro da gravura (Horas 26, NOVEMBRE.): a
    pessoa marca "letra" por cima e ali sai preto e branco."""
    img, s = _pagina_com_foto()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 450 / 900, 700 / 1200, tipo=LETRA, origem=MAO))
    saida, _ = aplicar_misto(img.copy(), s)
    pedaco = saida[610:690, 260:440]
    if pedaco.ndim == 3:
        assert (pedaco.min(axis=2) == pedaco.max(axis=2)).all()
        pedaco = pedaco[:, :, 0]
    assert set(np.unique(pedaco)) <= {0, 255}, "a letra marcada a mao tinha de sair em preto e branco"


def test_letra_automatica_nao_tira_a_gravura():
    """So a marcacao A MAO ganha da gravura: a letra que o detector proprio
    achou nao fura a foto."""
    img, s = _pagina_com_foto()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 450 / 900, 700 / 1200, tipo=LETRA,
                            origem="automatico"))
    saida, _ = aplicar_misto(img.copy(), s)
    miolo = (slice(650, 690), slice(300, 440))
    assert int(np.abs(saida[miolo].astype(int) - img[miolo].astype(int)).max()) <= 1


def test_gravura_tirada_a_mao_vira_preto_e_branco():
    img, s = _pagina_com_foto()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 650 / 900, 1000 / 1200, tipo=GRAVURA,
                            origem=MAO, operacao=SUBTRAIR))
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is True
    assert set(np.unique(saida)) <= {0, 255}


def test_gravura_marcada_a_mao_fica_como_esta():
    img = np.full((1200, 900, 3), PAPEL_CREME, np.uint8)
    _texto(img, 80, 380)
    img[600:1000, 250:650] = (60, 120, 180)             # pintura lisa
    s = Selecao()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 650 / 900, 1000 / 1200, tipo=GRAVURA,
                            origem=MAO))
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is False
    miolo = (slice(650, 950), slice(300, 600))
    assert int(np.abs(saida[miolo].astype(int) - img[miolo].astype(int)).max()) <= 1


def test_so_neste_pedaco_em_original_vale_no_misto():
    """'So neste pedaco' com o Original (aba Marcar): o conteudo do pedaco
    fica como o original; o papel dele segue a pagina (branco)."""
    img = np.full((1200, 900, 3), PAPEL_CREME, np.uint8)
    _texto(img, 80, 1100, cor=(40, 60, 120))            # tinta marrom
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.5, 1.0, 1.0, tipo=LETRA, origem=MAO, filtro=ORIGINAL))
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is False and saida.ndim == 3
    # a tinta do pedaco: a cor do original
    assert tuple(int(v) for v in saida[885, 101]) == (40, 60, 120)
    # a tinta de fora do pedaco: preta
    assert int(saida[205, 101].max()) == 0
    # o papel do pedaco: branco
    assert int(saida[1018:1032, 300:310].min()) >= 250


def test_so_neste_pedaco_em_preto_e_branco_tira_a_gravura():
    img, s = _pagina_com_foto()
    s.acrescentar(retangulo(250 / 900, 600 / 1200, 650 / 900, 1000 / 1200, tipo=GRAVURA,
                            origem=MAO, filtro=PRETO_E_BRANCO))
    saida, mono = aplicar_misto(img.copy(), s)
    assert mono is True


def test_papel_marcado_a_mao_vai_a_branco_mesmo_na_gravura():
    img, s = _pagina_com_foto()
    s.acrescentar(retangulo(250 / 900, 900 / 1200, 650 / 900, 1000 / 1200, tipo=PAPEL, origem=MAO))
    saida, _ = aplicar_misto(img.copy(), s)
    assert int(saida[920:980, 300:600].min()) >= 250


# --- robustez -------------------------------------------------------------------

def test_pagina_em_cinza_nao_quebra():
    cinza = np.full((600, 400), 210, np.uint8)
    cinza[50:250:20, 40:360:8] = 40
    cinza[300:550, 100:300] = np.linspace(40, 200, 200).astype(np.uint8)[None, :]
    s = Selecao()
    s.acrescentar(retangulo(0.25, 0.5, 0.75, 0.92, tipo=GRAVURA))
    saida, mono = aplicar_misto(cinza, s)
    assert saida.shape[:2] == cinza.shape and mono is False


def test_nao_muda_a_imagem_de_entrada():
    img, s = _pagina_com_foto()
    copia = img.copy()
    aplicar_misto(img, s)
    assert np.array_equal(img, copia)


@pytest.mark.parametrize("selecao", [None, Selecao()])
def test_selecao_vazia_ou_nenhuma(selecao):
    img = np.full((300, 200, 3), PAPEL_CREME, np.uint8)
    img[100:110, 20:180:6] = 30
    saida, mono = aplicar_misto(img, selecao)
    assert mono is True and saida.ndim == 2


# --- parte C (05/10): o que fica FORA das linhas do leitor de texto ------------
#
# Pedido do Samuel (05/10): ver lado a lado A (rede de seguranca), B (tudo o
# que nao e gravura vira preto e branco, o Misto do ScanTailor) e C (so dentro
# das linhas). Experimental: o padrao continua B, e nada muda para quem nao pede.

from core.misto import FORA_APAGAR, FORA_REDE, FORA_TUDO, mascara_das_linhas  # noqa: E402
from core.ocr_comum import LinhaOCR, ResultadoOCR, retangulo as caixa  # noqa: E402


def _pagina_com_nota_e_mancha():
    """Duas linhas de texto (dentro das linhas do leitor), uma "nota" preta
    fora delas e uma mancha cinza-clara fora delas."""
    img = np.full((900, 700, 3), PAPEL_CREME, np.uint8)
    _texto(img, 100, 180, x1=600)                    # linhas y 100 e 140
    img[400:440, 300:340] = (20, 20, 20)             # a nota: tao escura quanto a letra
    _texto(img, 680, 720, x0=150, x1=400, cor=(130, 140, 150))   # "escrita do verso", clara
    linhas = np.zeros(img.shape[:2], bool)
    linhas[90:160, 90:610] = True
    return img, linhas


def test_padrao_e_o_misto_de_sempre():
    img, linhas = _pagina_com_nota_e_mancha()
    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.1, 0.9, 0.2, tipo=LETRA))
    sempre, _ = aplicar_misto(img.copy(), s)
    com_linhas, _ = aplicar_misto(img.copy(), s, fora_do_texto=FORA_TUDO, linhas=linhas,
                                  altura_linha=12.0)
    assert np.array_equal(sempre, com_linhas)


def test_so_as_linhas_apaga_o_que_esta_fora():
    img, linhas = _pagina_com_nota_e_mancha()
    saida, _ = aplicar_misto(img.copy(), Selecao(), fora_do_texto=FORA_APAGAR, linhas=linhas,
                             altura_linha=12.0)
    assert int(saida[410:430, 310:330].min()) == 255, "fora das linhas tinha de ir a branco"
    assert int(saida[100:112, 100:104].max()) == 0, "o texto das linhas sumiu"


def test_rede_guarda_a_nota_escura_e_tira_a_mancha_clara():
    img, linhas = _pagina_com_nota_e_mancha()
    sempre, _ = aplicar_misto(img.copy(), Selecao())
    assert float((sempre[682:690, 151:400:16] == 0).mean()) > 0.9, "a pagina de teste mudou"
    medidas: dict = {}
    saida, _ = aplicar_misto(img.copy(), Selecao(), fora_do_texto=FORA_REDE, linhas=linhas,
                             altura_linha=12.0, medidas=medidas)
    assert int(saida[100:112, 100:104].max()) == 0
    assert float((saida[400:440, 300:340] == 0).mean()) > 0.2, "a nota escura sumiu"
    assert int(saida[675:730, 140:410].min()) == 255, "a escrita clara do verso ficou"
    assert 0 < medidas["guardada_fora"] < medidas["tinta_fora"]


def test_rede_sem_linha_nenhuma_vira_o_misto_de_sempre():
    img, _linhas = _pagina_com_nota_e_mancha()
    vazio = np.zeros(img.shape[:2], bool)
    saida, _ = aplicar_misto(img.copy(), Selecao(), fora_do_texto=FORA_REDE, linhas=vazio,
                             altura_linha=0.0)
    esperado, _ = aplicar_misto(img.copy(), Selecao())
    assert np.array_equal(saida, esperado)


def test_a_gravura_continua_protegida_em_qualquer_opcao():
    img, s = _pagina_com_foto()
    linhas = np.zeros(img.shape[:2], bool)
    linhas[70:400, 90:910] = True
    for modo in (FORA_REDE, FORA_APAGAR):
        saida, _ = aplicar_misto(img.copy(), s, fora_do_texto=modo, linhas=linhas,
                                 altura_linha=12.0)
        miolo = (slice(650, 950), slice(300, 600))
        assert int(np.abs(saida[miolo].astype(int) - img[miolo].astype(int)).max()) <= 1, modo


def test_mascara_das_linhas_une_os_leitores_e_alarga():
    r1 = ResultadoOCR("doctr", [LinhaOCR(caixa(10, 100, 200, 120))], largura=300, altura=300)
    r2 = ResultadoOCR("kraken", [LinhaOCR(caixa(10, 200, 200, 220))], largura=300, altura=300)
    mascara, altura = mascara_das_linhas([r1, r2], (300, 300))
    assert altura == pytest.approx(20.0, abs=1)
    assert mascara[110, 100] and mascara[210, 100]
    assert mascara[98, 100], "a linha tinha de ser alargada (15% da altura)"
    assert not mascara[150, 100]
    vazio, a0 = mascara_das_linhas([ResultadoOCR("kraken", None)], (300, 300))
    assert not vazio.any() and a0 == 0.0
