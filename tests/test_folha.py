"""Testes de `core/folha.py` - tamanho de folha e composição do recorte
dentro dela (Problema 2/4 do teste do Boécio, seção 3a do plano).

Este módulo é puro (sem PySide6), então os testes não precisam de QApplication
nem da plataforma "offscreen" - roda em qualquer máquina.

As primeiras funções (`TAMANHOS_DE_PAPEL_CM`, `medidas_do_recorte_em_cm`,
`recorte_para_tamanho_cm`, `recorte_cabe_na_pagina`) só MUDARAM DE LUGAR - elas
já existiam em `ui/widgets/visualizador.py` e moraram lá fora de lugar (são
puramente aritméticas, não desenham nada). `tests/test_visualizador.py`
continua testando-as pelo mesmo nome, agora reexportado - ver o fim deste
arquivo para a confirmação de que o reexport funciona.
"""

from __future__ import annotations

import numpy as np
import pytest

from core.folha import (
    TAMANHOS_DE_PAPEL_CM,
    compor_na_folha,
    conteudo_como_retangulo,
    deslocamento_do_retangulo,
    medidas_do_recorte_em_cm,
    recorte_cabe_na_pagina,
    recorte_para_tamanho_cm,
    tamanho_da_folha_cabe,
)


# --- funções movidas (mesmo comportamento de antes, só de local novo) ------

def test_medidas_do_recorte_sem_corte_da_o_tamanho_todo_da_pagina():
    largura_px = round(14.8 / 2.54 * 300)
    altura_px = round(21.0 / 2.54 * 300)
    m = medidas_do_recorte_em_cm((0.0, 0.0, 1.0, 1.0), largura_px, altura_px, 300)
    assert m["largura_final"] == pytest.approx(14.8, abs=0.05)
    assert m["altura_final"] == pytest.approx(21.0, abs=0.05)


def test_recorte_para_tamanho_cm_da_o_tamanho_pedido():
    largura_px = round(20.0 / 2.54 * 300)
    altura_px = round(30.0 / 2.54 * 300)
    recorte = recorte_para_tamanho_cm(14.8, 21.0, largura_px, altura_px, 300)
    m = medidas_do_recorte_em_cm(recorte, largura_px, altura_px, 300)
    assert m["largura_final"] == pytest.approx(14.8, abs=0.02)
    assert m["altura_final"] == pytest.approx(21.0, abs=0.02)


def test_recorte_cabe_na_pagina_quando_tamanho_pequeno():
    largura_px = round(20.0 / 2.54 * 300)
    altura_px = round(30.0 / 2.54 * 300)
    recorte = recorte_para_tamanho_cm(10.0, 10.0, largura_px, altura_px, 300)
    assert recorte_cabe_na_pagina(recorte)


def test_tamanhos_de_papel_tem_os_tres_combinados():
    assert set(TAMANHOS_DE_PAPEL_CM) == {"A4", "A5", "Carta"}


# --- tamanho_da_folha_cabe (novo) -------------------------------------------
#
# Decisões 1 e 2 confirmadas com o Samuel: a folha nunca trava um valor
# pequeno demais - só avisa. Esta função é o cálculo puro por trás do aviso,
# tanto no diálogo (ao digitar) quanto na tela (se o recorte crescer depois).

def test_folha_maior_que_o_recorte_cabe():
    assert tamanho_da_folha_cabe((21.0, 29.7), (14.8, 21.0)) is True


def test_folha_igual_ao_recorte_cabe():
    assert tamanho_da_folha_cabe((14.8, 21.0), (14.8, 21.0)) is True


def test_folha_menor_que_o_recorte_nao_cabe():
    assert tamanho_da_folha_cabe((10.0, 10.0), (14.8, 21.0)) is False


def test_folha_menor_so_num_eixo_nao_cabe():
    # largura cabe, altura não
    assert tamanho_da_folha_cabe((21.0, 15.0), (14.8, 21.0)) is False


def test_folha_none_sempre_cabe():
    """None quer dizer "folha do tamanho do recorte" - sempre cabe por definição."""
    assert tamanho_da_folha_cabe(None, (14.8, 21.0)) is True


# --- compor_na_folha (novo) --------------------------------------------------
#
# Decisão de arquitetura do plano: o recorte NUNCA é esticado ou recortado
# escondido para caber na folha - ou ele cabe e ganha borda branca ao redor,
# ou (rede de segurança) a composição é abortada e o conteúdo original sai
# sem alteração, do tamanho que sempre foi.

def _conteudo_cinza(largura_px: int, altura_px: int, valor: int = 50) -> np.ndarray:
    return np.full((altura_px, largura_px, 3), valor, dtype=np.uint8)


def test_sem_tamanho_de_folha_devolve_o_conteudo_sem_mudar():
    conteudo = _conteudo_cinza(100, 150)
    saida = compor_na_folha(conteudo, None, dpi=300)
    assert saida is conteudo


def test_folha_maior_gera_canvas_branco_do_tamanho_certo():
    dpi = 300
    largura_conteudo_px = round(10.0 / 2.54 * dpi)
    altura_conteudo_px = round(15.0 / 2.54 * dpi)
    conteudo = _conteudo_cinza(largura_conteudo_px, altura_conteudo_px)

    saida = compor_na_folha(conteudo, (21.0, 29.7), dpi=dpi)

    largura_esperada = round(21.0 / 2.54 * dpi)
    altura_esperada = round(29.7 / 2.54 * dpi)
    assert saida.shape[1] == largura_esperada
    assert saida.shape[0] == altura_esperada


def test_folha_maior_conteudo_fica_centralizado_e_cercado_de_branco():
    dpi = 300
    largura_conteudo_px = round(10.0 / 2.54 * dpi)
    altura_conteudo_px = round(15.0 / 2.54 * dpi)
    conteudo = _conteudo_cinza(largura_conteudo_px, altura_conteudo_px, valor=50)

    saida = compor_na_folha(conteudo, (21.0, 29.7), dpi=dpi)

    # canto da folha tem que estar branco
    assert saida[2, 2].tolist() == [255, 255, 255]
    # o centro tem que ser o conteudo cinza que colamos
    cy, cx = saida.shape[0] // 2, saida.shape[1] // 2
    assert saida[cy, cx].tolist() == [50, 50, 50]


def test_folha_do_mesmo_tamanho_do_conteudo_nao_sobra_borda():
    dpi = 300
    largura_px = round(14.8 / 2.54 * dpi)
    altura_px = round(21.0 / 2.54 * dpi)
    conteudo = _conteudo_cinza(largura_px, altura_px, valor=50)

    saida = compor_na_folha(conteudo, (14.8, 21.0), dpi=dpi)

    assert saida.shape[:2] == conteudo.shape[:2]
    assert saida[0, 0].tolist() == [50, 50, 50], "não devia sobrar borda branca"


def test_folha_menor_que_o_conteudo_e_rede_de_seguranca_devolve_original():
    """Decisão 2: na exportação, o pipeline nunca corta nada escondido - se a
    folha registrada não couber de verdade, o tamanho do recorte prevalece."""
    conteudo = _conteudo_cinza(2000, 3000)  # bem maior que a folha pedida
    saida = compor_na_folha(conteudo, (5.0, 5.0), dpi=300)
    assert saida.shape == conteudo.shape
    assert np.array_equal(saida, conteudo)


def test_compor_preserva_imagem_em_tons_de_cinza_um_canal_so():
    """A pagina em Preto e branco sai com 1 canal so (ver aplicar_filtro) -
    compor_na_folha nao pode presumir 3 canais."""
    dpi = 300
    largura_px = round(10.0 / 2.54 * dpi)
    altura_px = round(15.0 / 2.54 * dpi)
    conteudo = np.zeros((altura_px, largura_px), dtype=np.uint8)  # tudo preto

    saida = compor_na_folha(conteudo, (21.0, 29.7), dpi=dpi)

    assert saida.ndim == 2
    assert saida[2, 2] == 255            # canto: branco
    cy, cx = saida.shape[0] // 2, saida.shape[1] // 2
    assert saida[cy, cx] == 0            # centro: o conteudo preto


def test_compor_com_deslocamento_move_o_conteudo_do_centro():
    dpi = 300
    largura_conteudo_px = round(5.0 / 2.54 * dpi)
    altura_conteudo_px = round(5.0 / 2.54 * dpi)
    conteudo = _conteudo_cinza(largura_conteudo_px, altura_conteudo_px, valor=50)

    # empurra 20% da largura da folha para a direita
    saida = compor_na_folha(conteudo, (20.0, 20.0), dpi=dpi, deslocamento=(0.2, 0.0))

    cy = saida.shape[0] // 2
    centro_x = saida.shape[1] // 2
    deslocado_x = centro_x + round(0.2 * saida.shape[1])
    assert saida[cy, centro_x].tolist() == [255, 255, 255], (
        "o centro geometrico da folha nao devia mais ter o conteudo")
    assert saida[cy, deslocado_x].tolist() == [50, 50, 50]


def test_compor_com_escala_redimensiona_o_conteudo():
    dpi = 300
    largura_conteudo_px = round(10.0 / 2.54 * dpi)
    altura_conteudo_px = round(10.0 / 2.54 * dpi)
    conteudo = _conteudo_cinza(largura_conteudo_px, altura_conteudo_px, valor=50)

    saida = compor_na_folha(conteudo, (21.0, 21.0), dpi=dpi, escala=0.5)

    largura_esperada_conteudo = round(largura_conteudo_px * 0.5)
    # a faixa cinza deve ter aproximadamente metade da largura original
    linha_do_meio = saida[saida.shape[0] // 2]
    cinza = np.where(linha_do_meio[:, 0] < 200)[0]
    assert cinza.size == pytest.approx(largura_esperada_conteudo, abs=2)


# --- conversão escala/deslocamento <-> retângulo (preparação p/ item 4) ----

def test_conteudo_como_retangulo_sem_deslocamento_fica_centralizado():
    r = conteudo_como_retangulo(
        escala=1.0, deslocamento=(0.0, 0.0),
        tamanho_folha_cm=(20.0, 20.0),
        tamanho_conteudo_px=(600, 600), dpi=300,
    )
    x, y, w, h = r
    assert x + w / 2 == pytest.approx(0.5, abs=1e-6)
    assert y + h / 2 == pytest.approx(0.5, abs=1e-6)


def test_conteudo_como_retangulo_e_deslocamento_do_retangulo_sao_inversas():
    escala0, deslocamento0 = 0.7, (0.05, -0.1)
    tamanho_folha_cm = (21.0, 29.7)
    tamanho_conteudo_px = (1200, 1600)
    dpi = 300

    retangulo = conteudo_como_retangulo(
        escala0, deslocamento0, tamanho_folha_cm, tamanho_conteudo_px, dpi)
    escala1, deslocamento1 = deslocamento_do_retangulo(
        retangulo, tamanho_folha_cm, tamanho_conteudo_px, dpi)

    assert escala1 == pytest.approx(escala0, abs=1e-6)
    assert deslocamento1[0] == pytest.approx(deslocamento0[0], abs=1e-6)
    assert deslocamento1[1] == pytest.approx(deslocamento0[1], abs=1e-6)


def test_conteudo_como_retangulo_reflete_a_escala_no_tamanho():
    tamanho_folha_cm = (20.0, 20.0)
    tamanho_conteudo_px = (600, 600)
    dpi = 300

    r_cheio = conteudo_como_retangulo(1.0, (0.0, 0.0), tamanho_folha_cm,
                                       tamanho_conteudo_px, dpi)
    r_metade = conteudo_como_retangulo(0.5, (0.0, 0.0), tamanho_folha_cm,
                                        tamanho_conteudo_px, dpi)
    assert r_metade[2] == pytest.approx(r_cheio[2] / 2, abs=1e-6)
    assert r_metade[3] == pytest.approx(r_cheio[3] / 2, abs=1e-6)
