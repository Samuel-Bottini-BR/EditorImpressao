"""O "Ajustar o pedaço à figura" só vale para figura, e só para um pedaço.

Achado do verificador (05/10/2026, parecer do pedaço em Original, defeito 2):
num pedaço de TEXTO (Escola de Jesus 7, bloco de cima em "só neste pedaço:
Preto e branco"), o aviso dizia 47% e o botão cortava o título, a primeira
pergunta, a última linha e metade das palavras nas beiradas; e o botão
ajustava todos os pedaços da página de uma vez.

O que se cobra (teste de máquina):
    - pedaço de texto: não é figura, sem aviso, e o ajuste não muda nada
      (página sintética e, se a pasta gabarito/ existir, a Escola 7 de
      verdade, com o retângulo que o verificador desenhou);
    - pedaço de figura continua sendo ajustado (a pintura da Escola 7);
    - só o pedaço da vez muda: o último desenhado em volta de uma figura;
      o pedaço de texto nunca, em qualquer ordem; com dois de figura, um
      por clique.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from core.ajustar_pedaco import (
    MANCHA_DA_FIGURA,
    ajustar_os_pedacos,
    avaliar_os_pedacos,
    medir_folga,
    parece_figura,
    pedaco_da_vez,
)
from core.filtros import ORIGINAL, PRETO_E_BRANCO
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao
from tests.test_ajustar_pedaco import ALTURA, FOLGADO, LARGURA, PAPEL, _fracao, _pagina

TINTA = (40, 45, 60)


def _pagina_de_texto() -> np.ndarray:
    """Papel creme com um título (letras grandes) e um bloco de texto de
    letras soltas, cada uma um retângulo pequeno, palavras separadas."""
    rng = np.random.default_rng(3)
    img = np.empty((ALTURA, LARGURA, 3), np.uint8)
    img[:] = PAPEL
    img = np.clip(img.astype(np.int16) + rng.integers(-4, 5, img.shape), 0, 255).astype(np.uint8)
    for x in range(40, 360, 22):                      # o título: letras de 14 x 18
        img[30:48, x:x + 14] = TINTA
    for y in range(80, 300, 16):                      # o texto: letras de 5 x 8
        x = 30
        while x < 370:
            for _ in range(rng.integers(2, 8)):          # uma palavra
                if x >= 370:
                    break
                img[y:y + 8, x:x + 5] = TINTA
                x += 7
            x += 6                                        # o espaço entre palavras
    return img


TEXTO = _fracao((20, 20, 380, 310))                  # o bloco de texto inteiro, com folga


def _pedaco(caixa, filtro=ORIGINAL) -> Regiao:
    return Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[caixa[:2], caixa[2:]],
                  origem=MAO, filtro=filtro)


# --- pedaço de texto: nada de aviso, nada de ajuste ---------------------------


def test_pedaco_de_texto_nao_e_figura_nao_avisa_e_nao_e_cortado():
    img = _pagina_de_texto()
    assert parece_figura(img, TEXTO) is False
    folga = medir_folga(img, TEXTO)
    assert folga is not None and not folga.figura
    assert not folga.muito and not folga.muda, "o texto seria cortado"
    assert folga.justa == tuple(float(v) for v in TEXTO)
    s = Selecao()
    s.acrescentar(_pedaco(TEXTO))
    nova, quantos = ajustar_os_pedacos(img, s, PRETO_E_BRANCO)
    assert quantos == 0 and nova.regioes == s.regioes


def test_pedaco_de_figura_continua_sendo_figura():
    img = _pagina()
    assert parece_figura(img, FOLGADO) is True
    folga = medir_folga(img, FOLGADO)
    assert folga.figura and folga.muda and folga.muito


def test_so_papel_dentro_nao_e_nada():
    assert parece_figura(_pagina(), _fracao((310, 160, 390, 190))) is None


# --- só o pedaço da vez muda ------------------------------------------------


def _pagina_mista() -> np.ndarray:
    """Texto em cima (o de _pagina_de_texto, até y=190) e, embaixo, a
    figura de tests/test_ajustar_pedaco (de y=200 a 480)."""
    img = _pagina()
    img[:190] = _pagina_de_texto()[:190]
    return img


TEXTO_DE_CIMA = _fracao((20, 20, 380, 185))
MELHORAR_PAGINA = "melhorar"      # a página num terceiro filtro: os dois pedaços têm outro


@pytest.mark.parametrize("ordem", ["texto_primeiro", "figura_primeiro"])
def test_so_o_pedaco_de_figura_muda_e_o_de_texto_fica(ordem):
    img = _pagina_mista()
    s = Selecao()
    pedacos = [_pedaco(TEXTO_DE_CIMA, PRETO_E_BRANCO), _pedaco(FOLGADO, ORIGINAL)]
    if ordem == "figura_primeiro":
        pedacos.reverse()
    for p in pedacos:
        s.acrescentar(p)
    i_texto = 0 if ordem == "texto_primeiro" else 1
    i_figura = 1 - i_texto

    folgas = avaliar_os_pedacos(img, s, MELHORAR_PAGINA)
    assert not folgas[i_texto].figura and folgas[i_figura].figura
    assert pedaco_da_vez(folgas) == i_figura

    nova, quantos = ajustar_os_pedacos(img, s, MELHORAR_PAGINA)
    assert quantos == 1
    assert nova.regioes[i_texto] == s.regioes[i_texto], "o pedaço de texto mudou"
    (x0, y0), (x1, y1) = nova.regioes[i_figura].pontos
    assert x0 > FOLGADO[0] and y0 > FOLGADO[1] and x1 < FOLGADO[2] and y1 < FOLGADO[3]



def test_dois_pedacos_de_figura_um_por_clique_o_ultimo_primeiro():
    img = _pagina()
    s = Selecao()
    s.acrescentar(_pedaco(FOLGADO, ORIGINAL))                       # 0
    s.acrescentar(_pedaco(_fracao((70, 180, 330, 520)), ORIGINAL))  # 1: o último
    uma, quantos = ajustar_os_pedacos(img, s, PRETO_E_BRANCO)
    assert quantos == 1
    assert uma.regioes[0] == s.regioes[0], "mudou o primeiro antes do último"
    assert uma.regioes[1] != s.regioes[1]
    duas, quantos = ajustar_os_pedacos(img, uma, PRETO_E_BRANCO)
    assert quantos == 1
    assert duas.regioes[1] == uma.regioes[1]
    assert duas.regioes[0] != uma.regioes[0]
    tres, quantos = ajustar_os_pedacos(img, duas, PRETO_E_BRANCO)
    assert quantos == 0 and tres.regioes == duas.regioes


def test_so_texto_nao_tem_pedaco_da_vez():
    img = _pagina_de_texto()
    s = Selecao()
    s.acrescentar(_pedaco(TEXTO))
    folgas = avaliar_os_pedacos(img, s, PRETO_E_BRANCO)
    assert list(folgas) == [0] and pedaco_da_vez(folgas) is None


# --- a Escola de Jesus 7 de verdade (pula sem a pasta gabarito/) --------------

GABARITO = Path(__file__).resolve().parent.parent / "gabarito" / "paginas"


def _escola7_preparada(pdf, ordem):
    """A Escola 7 como a aba Marcar a usa (sem filtro, preparada, a 110 DPI)
    num livro com a ordem do preparo `ordem` (core/ordem_do_preparo), e a
    geometria do desenho (core/zonas_na_folha) dessa pagina."""
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    pipeline._GEOMETRIAS.clear()
    projeto = Projeto(caminho_entrada=str(pdf), nome="escola7", ordem_do_preparo=ordem)
    projeto.filtro_padrao = ORIGINAL
    projeto.detectar_regioes = False
    projeto = pipeline.analisar_projeto(projeto)
    pagina = projeto.paginas_ativas[0]
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=110)
    finally:
        doc.close()
    return img, dict(pagina.geometria_das_zonas)


@pytest.fixture(scope="module")
def _escola7():
    """(imagem do livro novo, geometria dela, geometria do parecer).

    Os retangulos do parecer do verificador (05/10/2026) foram desenhados na
    pagina preparada na ordem de entao, "cortar_antes". Desde o G6
    (09/10/2026) o livro novo endireita antes de cortar, e o corte da pagina
    muda (na Escola 7, com o angulo do ScanTailor de 0,12 grau, sai a faixa
    branca e a linha escura de cima e de baixo: 7% a menos de altura). As
    mesmas fracoes cairiam em outro pedaco do papel; por isso os retangulos
    sao levados para a pagina de agora pela conta das zonas
    (zonas_na_folha.trocar_de_geometria), e o resultado volta ao referencial
    do parecer para conferir os MESMOS limites de antes."""
    pdf = GABARITO / "escola_p007.pdf"
    if not pdf.is_file():
        pytest.skip("sem a pasta gabarito/ (fica fora do git)")
    import cv2

    from core.ordem_do_preparo import CORTAR_ANTES, ORDEM_DO_LIVRO_NOVO

    _, g_parecer = _escola7_preparada(pdf, CORTAR_ANTES)
    img, g_agora = _escola7_preparada(pdf, ORDEM_DO_LIVRO_NOVO)
    lado = max(img.shape[:2])
    if lado > 1000:
        img = cv2.resize(img, None, fx=1000 / lado, fy=1000 / lado, interpolation=cv2.INTER_AREA)
    return img, g_agora, g_parecer


@pytest.fixture(scope="module")
def escola7(_escola7):
    """A Escola 7 como a aba Marcar a usa: sem filtro, preparada, a 110 DPI."""
    return _escola7[0]


def _levar(caixa, de, para):
    """Uma caixa (x0, y0, x1, y1) de um preparo da pagina para outro: a caixa
    em volta do retangulo levado (com angulo, os cantos giram uma fracao de
    ponto)."""
    from core import zonas_na_folha as zf

    regiao = [{"forma": "retangulo", "tipo": "gravura", "operacao": "somar",
               "pontos": [list(caixa[:2]), list(caixa[2:])]}]
    pontos = np.asarray(zf.trocar_de_geometria(regiao, de, para)[0]["pontos"], float)
    return (float(pontos[:, 0].min()), float(pontos[:, 1].min()),
            float(pontos[:, 0].max()), float(pontos[:, 1].max()))


# os retangulos do parecer do verificador (05/10/2026), na pagina preparada
# na ordem "cortar_antes" (ver _escola7)
TEXTO_DA_ESCOLA = (0.018, 0.011, 0.994, 0.372)
PINTURA_COM_FOLGA = (0.344, 0.345, 0.994, 0.966)


def test_escola7_o_bloco_de_texto_nao_e_cortado(_escola7):
    img, g_agora, g_parecer = _escola7
    texto = _levar(TEXTO_DA_ESCOLA, g_parecer, g_agora)
    folga = medir_folga(img, texto)
    assert folga is not None
    assert not folga.figura, "o bloco de texto passou por figura"
    assert not folga.muito and not folga.muda
    s = Selecao()
    s.acrescentar(_pedaco(texto, PRETO_E_BRANCO))
    nova, quantos = ajustar_os_pedacos(img, s, ORIGINAL)
    assert quantos == 0 and nova.regioes == s.regioes


def test_escola7_a_pintura_continua_sendo_ajustada(_escola7):
    img, g_agora, g_parecer = _escola7
    folga = medir_folga(img, _levar(PINTURA_COM_FOLGA, g_parecer, g_agora))
    assert folga.figura and folga.muito and folga.muda
    # a caixa justa, no referencial do parecer: os mesmos limites de antes
    x0, y0, x1, y1 = _levar(folga.justa, g_agora, g_parecer)
    assert 0.37 < x0 < 0.39 and 0.37 < y0 < 0.40 and y1 < 0.94    # sem a linha e a legenda


def test_escola7_texto_e_pintura_na_mesma_pagina(_escola7):
    """O caso do verificador: um pedaço de texto e outro de pintura. O
    botão ajusta a pintura e deixa o texto como foi desenhado."""
    img, g_agora, g_parecer = _escola7
    s = Selecao()
    s.acrescentar(_pedaco(_levar(PINTURA_COM_FOLGA, g_parecer, g_agora), ORIGINAL))
    s.acrescentar(_pedaco(_levar(TEXTO_DA_ESCOLA, g_parecer, g_agora), ORIGINAL))
    nova, quantos = ajustar_os_pedacos(img, s, PRETO_E_BRANCO)
    assert quantos == 1
    assert nova.regioes[1] == s.regioes[1]
    assert nova.regioes[0] != s.regioes[0]


def test_o_corte_da_medida_esta_no_vao():
    """MANCHA_DA_FIGURA fica entre o maior texto medido (0,39) e a menor
    figura (0,51); ver o comentário em core/ajustar_pedaco.py."""
    assert 0.39 < MANCHA_DA_FIGURA < 0.51
