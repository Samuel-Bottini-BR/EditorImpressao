"""A prévia da página no modo recorte: retângulo com 8 alças arrastáveis.

Roda sem abrir janela, com a plataforma "offscreen" do Qt.
"""

from __future__ import annotations

import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

QtWidgets = pytest.importorskip("PySide6.QtWidgets")
QtCore = pytest.importorskip("PySide6.QtCore")

from ui.widgets.visualizador import (  # noqa: E402
    GUIA_BORDA_BAIXO,
    GUIA_BORDA_CIMA,
    GUIA_BORDA_DIREITA,
    GUIA_BORDA_ESQUERDA,
    GUIA_CENTRO_H,
    GUIA_CENTRO_V,
    MODO_RECORTE,
    PADDING_MOLDURA,
    RECORTE_ESPELHADO,
    RECORTE_LIVRE,
    RECORTE_PROPORCAO,
    TAMANHOS_DE_PAPEL_CM,
    Visualizador,
    encaixar_no_ima,
    guias_ativas,
    medidas_do_recorte_em_cm,
    recorte_cabe_na_pagina,
    recorte_para_tamanho_cm,
)


@pytest.fixture(scope="module")
def app():
    existente = QtWidgets.QApplication.instance()
    yield existente or QtWidgets.QApplication([])


@pytest.fixture
def visualizador(app):
    from PySide6.QtCore import QRect

    v = Visualizador()
    v.resize(400, 400)
    pagina = np.full((300, 300, 3), 235, np.uint8)
    v.definir_imagem(pagina)
    v.definir_modo(MODO_RECORTE)
    v.definir_recorte((0.3, 0.3, 0.4, 0.4))
    # A área de desenho só é calculada de verdade num paintEvent; fixamos uma
    # área quadrada conhecida para o teste não depender de abrir a janela.
    v._area = QRect(0, 0, 400, 400)
    return v


def arrastar(v, alca, dx_px, dy_px):
    """Simula arrastar a alça `alca` por (dx_px, dy_px) pixels de tela."""
    from PySide6.QtCore import QPoint

    r = v._retangulo_recorte()
    origem = v._alcas(r)[alca]
    v._arrastando = alca
    v._recorte_inicial = v.recorte
    v._ponto_inicial = origem
    v._mover_recorte(QPoint(origem.x() + dx_px, origem.y() + dy_px))


def test_alca_direita_do_meio_aumenta_a_largura(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "l", 40, 0)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0
    assert (x1, y1, h1) == (x0, y0, h0)


def test_canto_superior_direito_aumenta_largura_e_altura(visualizador):
    """Regressão: 'ne' continha 'e', não 'l', e a largura nunca mudava."""
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "ne", 40, -40)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0, "largura deveria aumentar ao puxar o canto direito"
    assert h1 > h0, "altura deveria aumentar ao puxar o canto de cima"
    assert x1 == x0


def test_canto_inferior_direito_aumenta_largura_e_altura(visualizador):
    """Regressão: 'se' continha 'e', não 'l', e a largura nunca mudava."""
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "se", 40, 40)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0, "largura deveria aumentar ao puxar o canto direito"
    assert h1 > h0, "altura deveria aumentar ao puxar o canto de baixo"
    assert x1 == x0


def test_canto_superior_esquerdo_aumenta_mexendo_em_x(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "no", -40, -40)
    x1, y1, w1, h1 = visualizador.recorte
    assert x1 < x0
    assert w1 > w0
    assert y1 < y0
    assert h1 > h0


def test_canto_inferior_esquerdo_aumenta_mexendo_em_x(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "so", -40, 40)
    x1, y1, w1, h1 = visualizador.recorte
    assert x1 < x0
    assert w1 > w0
    assert h1 > h0


def test_alca_de_cima_mexe_so_na_altura(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "n", 0, -40)
    x1, y1, w1, h1 = visualizador.recorte
    assert (x1, w1) == (x0, w0)
    assert y1 < y0
    assert h1 > h0


def test_alca_de_baixo_mexe_so_na_altura(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "s", 0, 40)
    x1, y1, w1, h1 = visualizador.recorte
    assert (x1, w1) == (x0, w0)
    assert h1 > h0


def test_alca_esquerda_do_meio_mexe_so_na_largura(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    arrastar(visualizador, "o", -40, 0)
    x1, y1, w1, h1 = visualizador.recorte
    assert (y1, h1) == (y0, h0)
    assert x1 < x0
    assert w1 > w0


def test_modo_de_arraste_comeca_livre(visualizador):
    assert visualizador.modo_arraste_recorte == RECORTE_LIVRE


def test_espelhado_lado_mantem_o_centro(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    centro0 = x0 + w0 / 2
    visualizador.definir_modo_arraste_recorte(RECORTE_ESPELHADO)
    arrastar(visualizador, "l", 40, 0)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0
    assert (y1, h1) == (y0, h0)
    assert x1 + w1 / 2 == pytest.approx(centro0, abs=1e-6)


def test_espelhado_canto_mexe_nos_dois_eixos(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    centro0 = (x0 + w0 / 2, y0 + h0 / 2)
    visualizador.definir_modo_arraste_recorte(RECORTE_ESPELHADO)
    arrastar(visualizador, "se", 40, 40)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0
    assert h1 > h0
    centro1 = (x1 + w1 / 2, y1 + h1 / 2)
    assert centro1 == pytest.approx(centro0, abs=1e-6)


def test_proporcao_travada_mantem_a_razao(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    razao0 = w0 / h0
    visualizador.definir_modo_arraste_recorte(RECORTE_PROPORCAO)
    arrastar(visualizador, "l", 40, 0)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 > w0
    assert h1 > h0, "travar proporção deveria crescer a altura junto"
    assert w1 / h1 == pytest.approx(razao0, abs=1e-6)


def test_proporcao_travada_no_canto_mantem_a_razao(visualizador):
    x0, y0, w0, h0 = visualizador.recorte
    razao0 = w0 / h0
    visualizador.definir_modo_arraste_recorte(RECORTE_PROPORCAO)
    arrastar(visualizador, "se", 40, 10)
    x1, y1, w1, h1 = visualizador.recorte
    assert w1 / h1 == pytest.approx(razao0, abs=1e-6)


# --- Problema 4: moldura ao redor da página, "ajustar à tela" nunca preenche
# o widget inteiro -----------------------------------------------------------

def test_ajustar_a_tela_sobra_moldura_retrato(app):
    v = Visualizador()
    v.resize(400, 400)
    v.definir_imagem(np.full((600, 400, 3), 235, np.uint8))  # retrato
    assert v._largura_base() <= 400 - 2 * PADDING_MOLDURA + 1e-6
    assert v._altura_base() <= 400 - 2 * PADDING_MOLDURA + 1e-6


def test_ajustar_a_tela_sobra_moldura_paisagem(app):
    v = Visualizador()
    v.resize(400, 400)
    v.definir_imagem(np.full((300, 500, 3), 235, np.uint8))  # paisagem
    assert v._largura_base() <= 400 - 2 * PADDING_MOLDURA + 1e-6
    assert v._altura_base() <= 400 - 2 * PADDING_MOLDURA + 1e-6


# --- Problema 1.1: números em cm ------------------------------------------

def test_medidas_do_recorte_sem_corte_da_o_tamanho_todo_da_pagina():
    # Página A5 (14,8 x 21,0 cm) a 300 DPI, sem nenhum corte.
    largura_px = round(14.8 / 2.54 * 300)
    altura_px = round(21.0 / 2.54 * 300)
    m = medidas_do_recorte_em_cm((0.0, 0.0, 1.0, 1.0), largura_px, altura_px, 300)
    assert m["esquerda"] == pytest.approx(0.0, abs=0.02)
    assert m["direita"] == pytest.approx(0.0, abs=0.02)
    assert m["largura_final"] == pytest.approx(14.8, abs=0.05)
    assert m["altura_final"] == pytest.approx(21.0, abs=0.05)


def test_medidas_do_recorte_corte_simetrico():
    # Página de 20cm de largura a 300 DPI, cortando 10% de cada lado.
    largura_px = round(20.0 / 2.54 * 300)
    m = medidas_do_recorte_em_cm((0.1, 0.0, 0.8, 1.0), largura_px, 1000, 300)
    assert m["esquerda"] == pytest.approx(2.0, abs=0.02)
    assert m["direita"] == pytest.approx(2.0, abs=0.02)
    assert m["largura_final"] == pytest.approx(16.0, abs=0.05)


def test_medidas_independem_da_qualidade_da_previa():
    """O mesmo recorte, renderizado em DPIs diferentes, tem que dar o mesmo cm -
    é o ponto central de passar o dpi junto com a imagem."""
    m_rapida = medidas_do_recorte_em_cm((0.2, 0.1, 0.5, 0.7), 1100, 1500, 110)
    m_alta = medidas_do_recorte_em_cm((0.2, 0.1, 0.5, 0.7), 3000, 4090, 300)
    assert m_rapida["largura_final"] == pytest.approx(m_alta["largura_final"], abs=0.05)
    assert m_rapida["altura_final"] == pytest.approx(m_alta["altura_final"], abs=0.05)


def test_medidas_com_dpi_zero_nao_quebra():
    m = medidas_do_recorte_em_cm((0.1, 0.1, 0.8, 0.8), 1000, 1000, 0)
    assert m["largura_final"] == 0.0


def test_labels_de_cm_so_aparecem_arrastando(visualizador):
    """Antes de arrastar (self._arrastando is None), _desenhar_recorte não
    deve tentar desenhar a medida - checado indiretamente: chamar o método
    de desenho de medidas não deve levantar mesmo sem pixmap none-safe."""
    assert visualizador._arrastando is None
    # sanity: o pixmap existe (fixture já chamou definir_imagem)
    assert visualizador._pixmap is not None


# --- Problema 1.2: escolher o tamanho da folha direto ----------------------

def test_recorte_para_tamanho_cm_da_o_tamanho_pedido():
    largura_px = round(20.0 / 2.54 * 300)  # página de 20 cm de largura
    altura_px = round(30.0 / 2.54 * 300)   # e 30 cm de altura
    recorte = recorte_para_tamanho_cm(14.8, 21.0, largura_px, altura_px, 300)
    m = medidas_do_recorte_em_cm(recorte, largura_px, altura_px, 300)
    assert m["largura_final"] == pytest.approx(14.8, abs=0.02)
    assert m["altura_final"] == pytest.approx(21.0, abs=0.02)


def test_recorte_para_tamanho_cm_fica_centralizado():
    largura_px = round(20.0 / 2.54 * 300)
    altura_px = round(30.0 / 2.54 * 300)
    x, y, w, h = recorte_para_tamanho_cm(10.0, 10.0, largura_px, altura_px, 300)
    assert x + w / 2 == pytest.approx(0.5, abs=1e-6)
    assert y + h / 2 == pytest.approx(0.5, abs=1e-6)


def test_recorte_cabe_na_pagina_quando_tamanho_pequeno():
    largura_px = round(20.0 / 2.54 * 300)
    altura_px = round(30.0 / 2.54 * 300)
    recorte = recorte_para_tamanho_cm(10.0, 10.0, largura_px, altura_px, 300)
    assert recorte_cabe_na_pagina(recorte)


def test_recorte_nao_cabe_quando_tamanho_maior_que_a_pagina():
    largura_px = round(10.0 / 2.54 * 300)
    altura_px = round(10.0 / 2.54 * 300)
    # A4 (21 x 29,7 cm) não cabe numa página de 10x10 cm.
    recorte = recorte_para_tamanho_cm(*TAMANHOS_DE_PAPEL_CM["A4"],
                                       largura_px, altura_px, 300)
    assert not recorte_cabe_na_pagina(recorte)


def test_tamanhos_de_papel_tem_os_tres_combinados():
    assert set(TAMANHOS_DE_PAPEL_CM) == {"A4", "A5", "Carta"}


# --- Problema 1.4: mover o conteúdo com linhas-guia + ímã ------------------

def test_conteudo_centralizado_ativa_as_duas_guias_de_centro():
    conteudo = (0.25, 0.4, 0.5, 0.2)  # centro em (0.5, 0.5)
    ativas = guias_ativas(conteudo)
    assert GUIA_CENTRO_H in ativas
    assert GUIA_CENTRO_V in ativas
    assert GUIA_BORDA_ESQUERDA not in ativas


def test_conteudo_encostado_na_borda_esquerda():
    conteudo = (0.0, 0.4, 0.5, 0.2)
    assert GUIA_BORDA_ESQUERDA in guias_ativas(conteudo)
    assert GUIA_CENTRO_H not in guias_ativas(conteudo)


def test_conteudo_encostado_na_borda_direita():
    conteudo = (0.5, 0.4, 0.5, 0.2)
    assert GUIA_BORDA_DIREITA in guias_ativas(conteudo)


def test_conteudo_longe_de_qualquer_guia_nao_ativa_nada():
    conteudo = (0.2, 0.3, 0.3, 0.1)  # nem centralizado, nem em nenhuma borda
    assert guias_ativas(conteudo) == []


def test_ima_puxa_para_o_centro_quando_perto():
    quase_centralizado = (0.245, 0.4, 0.5, 0.2)  # centro em x=0.495, a 0.005 do meio
    x, y, w, h = encaixar_no_ima(quase_centralizado)
    assert x + w / 2 == pytest.approx(0.5, abs=1e-9)


def test_ima_nao_mexe_quando_longe_de_qualquer_guia():
    livre = (0.2, 0.3, 0.3, 0.1)
    assert encaixar_no_ima(livre) == livre


def test_ima_nunca_muda_o_tamanho():
    quase_borda = (0.005, 0.4, 0.5, 0.2)
    x, y, w, h = encaixar_no_ima(quase_borda)
    assert (w, h) == (0.5, 0.2)


def test_ima_encosta_na_borda_de_baixo():
    conteudo = (0.3, 0.795, 0.4, 0.2)  # y+h = 0.995, a 0.005 da borda de baixo
    x, y, w, h = encaixar_no_ima(conteudo)
    assert y + h == pytest.approx(1.0, abs=1e-9)
    assert GUIA_BORDA_BAIXO in guias_ativas((x, y, w, h))


def test_ima_encosta_no_topo():
    conteudo = (0.3, 0.01, 0.4, 0.2)
    x, y, w, h = encaixar_no_ima(conteudo)
    assert y == pytest.approx(0.0, abs=1e-9)
    assert GUIA_BORDA_CIMA in guias_ativas((x, y, w, h))


def test_widget_bem_pequeno_nao_quebra(app):
    """A folga não pode virar negativa e inverter a conta num widget minúsculo."""
    v = Visualizador()
    v.resize(10, 10)
    v.definir_imagem(np.full((300, 300, 3), 235, np.uint8))
    assert v._largura_base() > 0
    assert v._altura_base() > 0


# --- Bug real achado ao vivo (reprodução por outro agente, pywinauto):
# "só abri o selecionador pro lado esquerdo" -----------------------------
#
# `_mover_recorte` só limitava w/h por BAIXO (`max(minimo, w)`), nunca por
# cima antes do clamp de x/y. Perto da borda da página, um arrasto que fazia
# w (ou h) passar de `1.0 - x` deixava `x = min(x, 1.0 - w)` com `1.0 - w`
# NEGATIVO - o clamp empurrava o lado ESQUERDO (x) para fora, mesmo em alças
# que nunca deveriam mexer em x (ex.: "l"/leste, só deveria mexer na
# largura). Reproduzido de verdade: partindo de um recorte quase-página-
# inteira, arrastar QUALQUER alça/canto para fora convergia para o mesmo
# resultado deslocado (~-0.07), não importa o lado tocado.
#
# A correção: cada eixo tem um lado ANCORADO (o que não está sendo
# arrastado, fica exatamente onde estava) e um lado que se move - só o lado
# que se move é limitado a [0, 1], o ancorado nunca muda de valor.

@pytest.fixture
def visualizador_perto_da_borda(app):
    from PySide6.QtCore import QRect

    v = Visualizador()
    v.resize(400, 400)
    pagina = np.full((300, 300, 3), 235, np.uint8)
    v.definir_imagem(pagina)
    v.definir_modo(MODO_RECORTE)
    # quase a página inteira, igual ao caso relatado (comum depois da
    # deteccao automatica de borda)
    v.definir_recorte((0.03, 0.03, 0.94, 0.94))
    v._area = QRect(0, 0, 400, 400)
    return v


@pytest.mark.parametrize("alca", ["l", "ne", "se"])
def test_arrastar_para_fora_na_borda_direita_nao_move_o_lado_esquerdo(
        visualizador_perto_da_borda, alca):
    x0, y0, w0, h0 = visualizador_perto_da_borda.recorte
    arrastar(visualizador_perto_da_borda, alca, 200, 0)  # bem para fora da tela
    x1, _y1, w1, _h1 = visualizador_perto_da_borda.recorte
    assert x1 == pytest.approx(x0, abs=1e-6), (
        f"lado esquerdo (ancorado) nao pode se mover ao arrastar '{alca}' para fora: "
        f"{x0} -> {x1}")
    assert x1 >= 0.0, "recorte nao pode ter coordenada negativa"
    assert x1 + w1 <= 1.0 + 1e-6, "recorte nao pode passar da borda direita da pagina"


@pytest.mark.parametrize("alca", ["o", "no", "so"])
def test_arrastar_para_fora_na_borda_esquerda_nao_move_o_lado_direito(
        visualizador_perto_da_borda, alca):
    x0, y0, w0, h0 = visualizador_perto_da_borda.recorte
    direita0 = x0 + w0
    arrastar(visualizador_perto_da_borda, alca, -200, 0)  # bem para fora da tela
    x1, _y1, w1, _h1 = visualizador_perto_da_borda.recorte
    assert x1 + w1 == pytest.approx(direita0, abs=1e-6), (
        f"lado direito (ancorado) nao pode se mover ao arrastar '{alca}' para fora")
    assert x1 >= -1e-6, "recorte nao pode ter coordenada negativa"


@pytest.mark.parametrize("alca", ["n", "no", "ne"])
def test_arrastar_para_fora_no_topo_nao_move_a_base(
        visualizador_perto_da_borda, alca):
    x0, y0, w0, h0 = visualizador_perto_da_borda.recorte
    baixo0 = y0 + h0
    arrastar(visualizador_perto_da_borda, alca, 0, -200)
    _x1, y1, _w1, h1 = visualizador_perto_da_borda.recorte
    assert y1 + h1 == pytest.approx(baixo0, abs=1e-6)
    assert y1 >= -1e-6


@pytest.mark.parametrize("alca", ["s", "so", "se"])
def test_arrastar_para_fora_na_base_nao_move_o_topo(
        visualizador_perto_da_borda, alca):
    x0, y0, w0, h0 = visualizador_perto_da_borda.recorte
    arrastar(visualizador_perto_da_borda, alca, 0, 200)
    _x1, y1, _w1, h1 = visualizador_perto_da_borda.recorte
    assert y1 == pytest.approx(y0, abs=1e-6)
    assert y1 + h1 <= 1.0 + 1e-6


def test_arrastar_para_fora_nunca_produz_coordenada_negativa_em_nenhum_modo(
        visualizador_perto_da_borda):
    """Mesma reprodução, agora conferindo os modos Espelhado e Proporção
    travada também - o mesmo padrão de bug (clamp que empurra o lado
    ancorado) poderia existir ali, já que os três modos compartilhavam o
    clamp final antigo."""
    for modo in (RECORTE_ESPELHADO, RECORTE_PROPORCAO):
        visualizador_perto_da_borda.definir_recorte((0.03, 0.03, 0.94, 0.94))
        visualizador_perto_da_borda.definir_modo_arraste_recorte(modo)
        arrastar(visualizador_perto_da_borda, "l", 200, 0)
        x1, y1, w1, h1 = visualizador_perto_da_borda.recorte
        assert x1 >= -1e-6 and y1 >= -1e-6, f"{modo}: {(x1, y1, w1, h1)}"
        assert x1 + w1 <= 1.0 + 1e-6 and y1 + h1 <= 1.0 + 1e-6, f"{modo}: {(x1, y1, w1, h1)}"


# --- Passo 8 do plano: exibição composta (recorte + margem da folha) e o
# mapeamento tela<->fração ganhando uma etapa a mais ------------------------
#
# Decisão 3 (confirmada com o Samuel): a área de trabalho passa a mostrar a
# imagem JÁ COMPOSTA (recorte + margem branca de verdade), ao vivo. A fração
# do `recorte` sobre o CONTEÚDO continua sendo a fonte da verdade salva -
# só o mapeamento tela->fração ganha uma etapa a mais (onde o conteúdo fica
# dentro do canvas maior). Por padrão (`definir_composicao` nunca chamado, o
# caso de sempre - nenhuma folha escolhida) o conteúdo OCUPA o canvas
# inteiro, e todo o comportamento continua idêntico ao de antes - é
# exatamente isso que os 48 testes acima (nenhum alterado) continuam
# provando: eles nunca chamam `definir_composicao`.

def test_sem_composicao_a_area_do_conteudo_e_a_area_inteira(visualizador):
    """Estado padrão (nenhuma folha escolhida): comportamento de sempre."""
    assert visualizador._area_do_conteudo() == visualizador._area


def test_tamanho_da_pagina_usa_o_pixmap_quando_nao_ha_composicao(app):
    v = Visualizador()
    v.definir_imagem(np.full((300, 400, 3), 235, np.uint8))
    assert v.tamanho_da_pagina_px() == (400, 300)


@pytest.fixture
def visualizador_composto(app):
    """Um canvas de 400x400 (a "folha"), com o conteúdo (200x200) ocupando
    só o quadrado central - metade da largura e da altura, como aconteceria
    com uma folha duas vezes maior que o recorte em cada eixo."""
    from PySide6.QtCore import QRect

    v = Visualizador()
    v.resize(400, 400)
    canvas = np.full((400, 400, 3), 255, np.uint8)
    v.definir_imagem(canvas)
    v.definir_modo(MODO_RECORTE)
    v.definir_recorte((0.3, 0.3, 0.4, 0.4))
    v._area = QRect(0, 0, 400, 400)
    v.definir_composicao((0.25, 0.25, 0.5, 0.5), (200, 200))
    return v


def test_area_do_conteudo_fica_dentro_do_canvas_maior(visualizador_composto):
    r = visualizador_composto._area_do_conteudo()
    assert (r.left(), r.top(), r.width(), r.height()) == (100, 100, 200, 200)


def test_tamanho_da_pagina_usa_o_conteudo_quando_ha_composicao(visualizador_composto):
    """Precisa continuar sendo o tamanho do CONTEÚDO (o recorte), não o do
    canvas maior - é o que `ui/tela_conferir.py::_escolher_tamanho_da_folha`
    usa para calcular os cm do recorte atual."""
    assert visualizador_composto.tamanho_da_pagina_px() == (200, 200)


def test_retangulo_do_recorte_fica_dentro_da_area_do_conteudo(visualizador_composto):
    """recorte=(0.3,0.3,0.4,0.4) é fração do CONTEÚDO (100,100,200,200) - não
    do canvas de 400x400 inteiro."""
    r = visualizador_composto._retangulo_recorte()
    esperado_x = 100 + 0.3 * 200   # 160
    esperado_y = 100 + 0.3 * 200   # 160
    esperado_w = 0.4 * 200         # 80
    esperado_h = 0.4 * 200         # 80
    assert r.left() == pytest.approx(esperado_x, abs=1)
    assert r.top() == pytest.approx(esperado_y, abs=1)
    assert r.width() == pytest.approx(esperado_w, abs=1)
    assert r.height() == pytest.approx(esperado_h, abs=1)


def test_arrastar_com_composicao_normaliza_pelo_conteudo_nao_pelo_canvas(
        visualizador_composto):
    """O ponto central do teste: arrastar 40px de tela, com o conteúdo
    ocupando metade do canvas (200px em vez de 400px), tem que mexer o DOBRO
    na fração do recorte do que mexeria sem composição nenhuma - porque
    40/200 = 0,2, não 40/400 = 0,1. Isso é o "mapeamento tela->fração ganha
    uma etapa a mais" da decisão 3."""
    x0, y0, w0, h0 = visualizador_composto.recorte
    arrastar(visualizador_composto, "l", 40, 0)
    x1, y1, w1, h1 = visualizador_composto.recorte
    assert w1 - w0 == pytest.approx(0.2, abs=1e-6)
    assert (x1, y1, h1) == (x0, y0, h0)


def test_definir_composicao_com_conteudo_igual_ao_canvas_nao_muda_nada(app):
    """Quando a folha não coube (rede de segurança) ou não foi escolhida, a
    composição devolve o conteúdo tal como era - (0,0,1,1) tem que dar
    exatamente o mesmo resultado de nunca ter chamado `definir_composicao`."""
    from PySide6.QtCore import QRect

    v = Visualizador()
    v.resize(400, 400)
    v.definir_imagem(np.full((300, 300, 3), 235, np.uint8))
    v.definir_modo(MODO_RECORTE)
    v.definir_recorte((0.3, 0.3, 0.4, 0.4))
    v._area = QRect(0, 0, 400, 400)
    v.definir_composicao((0.0, 0.0, 1.0, 1.0), (300, 300))

    assert v._area_do_conteudo() == v._area
    assert v.tamanho_da_pagina_px() == (300, 300)


# --- Bug real achado no teste ao vivo do Samuel (22/09/2026): "a área da
# folha ao redor do recorte não está branca de verdade" -------------------
#
# Reproduzido de verdade (renderizando o widget offscreen e amostrando o
# pixel real, não só lendo o código): `_desenhar_recorte` escurece tudo que
# fica FORA do retângulo do recorte, dentro de `self._area` inteira - antes
# do passo 8 isso fazia sentido (self._area era sempre a imagem toda, e o
# que ficava fora do recorte era conteúdo que seria cortado fora). Depois do
# passo 8, `self._area` pode ser o canvas da FOLHA inteira, maior que o
# conteúdo - e a mesma sombra (preto a 70/255 de opacidade) passou a cobrir
# também a margem branca da folha, tingindo o branco 255 de cinza
# (255 - 70 = 185, exatamente o valor medido). A correção usa
# `_area_do_conteudo()` como limite da sombra, não `self._area`.

def _renderizar_para_imagem(v) -> "QImage":
    from PySide6.QtGui import QImage

    img = QImage(v.width(), v.height(), QImage.Format_RGB32)
    v.render(img)
    return img


def test_margem_da_folha_fica_branca_de_verdade(app):
    from PySide6.QtCore import QRect

    from core.folha import compor_na_folha, conteudo_como_retangulo

    conteudo = np.full((200, 200, 3), 60, np.uint8)   # conteudo escuro, bem diferente do branco

    composto = compor_na_folha(conteudo, (20.0, 20.0), dpi=300, escala=1.0,
                                deslocamento=(0.0, 0.0))

    v = Visualizador()
    v.resize(500, 500)
    v.definir_imagem(composto)
    v.definir_modo(MODO_RECORTE)
    v.definir_recorte((0.0, 0.0, 1.0, 1.0))   # recorte = todo o conteudo, sem corte
    v._area = QRect(32, 32, 436, 436)
    tamanho_conteudo_px = (conteudo.shape[1], conteudo.shape[0])
    retangulo_conteudo = conteudo_como_retangulo(
        1.0, (0.0, 0.0), (20.0, 20.0), tamanho_conteudo_px, 300)
    v.definir_composicao(retangulo_conteudo, tamanho_conteudo_px)

    img = _renderizar_para_imagem(v)

    # um ponto dentro do pixmap (self._area) mas fora da area do conteudo -
    # e a margem branca da folha
    a = v._area
    cor = img.pixelColor(a.left() + 5, a.top() + 5)
    assert (cor.red(), cor.green(), cor.blue()) == (255, 255, 255), (
        f"margem da folha deveria ser branca, veio {(cor.red(), cor.green(), cor.blue())}")


# --- Fase 2 aprovada pelo Samuel (22/09/2026): mover o conteúdo dentro da
# folha, com linhas-guia + ímã ------------------------------------------------
#
# Distinto de MODO_RECORTE (que edita o RECORTE, a fração da imagem
# original): aqui o que se arrasta é o CONTEÚDO já recortado, dentro do
# canvas maior da folha. `guias_ativas`/`encaixar_no_ima` já existiam,
# testados, mas nunca ligados em nenhuma tela - ligados agora.

@pytest.fixture
def visualizador_modo_conteudo(app):
    from PySide6.QtCore import QRect

    from ui.widgets.visualizador import MODO_CONTEUDO

    v = Visualizador()
    v.resize(400, 400)
    v.definir_imagem(np.full((400, 400, 3), 255, np.uint8))
    v.definir_modo(MODO_CONTEUDO)
    v._area = QRect(0, 0, 400, 400)
    # conteudo ocupa metade do canvas (200x200), comecando fora do centro
    v.definir_composicao((0.2, 0.2, 0.5, 0.5), (200, 200))
    return v


def arrastar_conteudo(v, dx_px, dy_px):
    """Mesmo estilo do helper `arrastar` (recorte): chama o método interno
    direto, sem passar por QMouseEvent - move a partir do centro da área do
    conteúdo atual."""
    from PySide6.QtCore import QPoint

    origem = v._area_do_conteudo().center()
    v._arrastando = "conteudo"
    v._retangulo_conteudo_inicial = v._retangulo_conteudo
    v._ponto_inicial = origem
    v._mover_conteudo(QPoint(origem.x() + dx_px, origem.y() + dy_px))


def test_arrastar_conteudo_move_x_e_y_mantendo_o_tamanho(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    x0, y0, w0, h0 = v._retangulo_conteudo
    arrastar_conteudo(v, 40, 20)   # 40/400=0.1 ; 20/400=0.05
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 == pytest.approx(x0 + 0.1, abs=1e-6)
    assert y1 == pytest.approx(y0 + 0.05, abs=1e-6)
    assert (w1, h1) == (w0, h0)


def test_arrastar_conteudo_nao_sai_do_canvas(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    arrastar_conteudo(v, 4000, 0)   # bem para fora da tela
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 + w1 <= 1.0 + 1e-6
    assert x1 >= 0.0 - 1e-6


def test_arrastar_conteudo_nao_sai_do_canvas_do_outro_lado(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    arrastar_conteudo(v, -4000, -4000)
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 >= -1e-6 and y1 >= -1e-6


def test_arrastar_conteudo_gruda_no_centro_pelo_ima(visualizador_modo_conteudo):
    """conteudo w=h=0.5: centralizado seria x=y=0.25. Começa em (0.2,0.2) -
    arrastar quase até lá tem que grudar exatamente no centro (ímã)."""
    v = visualizador_modo_conteudo
    dx_px = (0.25 - 0.2 - 0.005) * 400   # fica a 0.005 do centro, dentro da tolerância
    arrastar_conteudo(v, dx_px, dx_px)
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 + w1 / 2 == pytest.approx(0.5, abs=1e-9)
    assert y1 + h1 / 2 == pytest.approx(0.5, abs=1e-9)


def test_arrastar_conteudo_longe_de_guia_nao_gruda(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    arrastar_conteudo(v, 4, 4)   # bem pouco, longe de qualquer guia
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 + w1 / 2 != pytest.approx(0.5, abs=1e-9)


def _construir_evento(tipo, ponto, botao, botoes):
    from PySide6.QtCore import QPointF, Qt
    from PySide6.QtGui import QMouseEvent

    return QMouseEvent(tipo, QPointF(ponto), botao, botoes, Qt.NoModifier)


def test_clicar_na_margem_branca_tambem_arrasta_o_conteudo(visualizador_modo_conteudo):
    """BUG REAL achado ao vivo (22/09/2026, reprodução com mouse de verdade
    via pywinauto): o Samuel relatou "ainda não consigo movimentar o
    conteudo" mesmo depois da folha branca já estar certa. Reproduzindo com
    cliques reais: um clique bem no meio do retângulo do conteúdo arrastava
    perfeitamente, mas o retângulo do conteúdo é só uma fração pequena da
    folha visível e não tinha NENHUMA pista visual (sem alça, sem cursor
    diferente) de onde esse ponto começava - um clique real (nunca
    pixel-perfect) caía na margem branca com facilidade, e o clique não
    fazia nada ali, parecendo simplesmente "não funciona".

    Antes desta correção, este teste esperava o oposto (clicar fora do
    conteúdo NÃO arrastava nada) - era a causa raiz do bug. Agora qualquer
    clique dentro da folha visível (`self._area`) arrasta o conteúdo, como
    mover uma foto dentro de uma moldura."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QMouseEvent

    v = visualizador_modo_conteudo
    margem = QPoint(5, 5)   # dentro da folha (0,0,400,400), fora do conteudo (~80,80,200,200)
    v.mousePressEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonPress, margem, Qt.LeftButton, Qt.LeftButton))
    assert v._arrastando == "conteudo"


def test_clicar_fora_da_folha_nao_inicia_arrasto(visualizador_modo_conteudo):
    """Fora de `self._area` (a folha) de verdade - nada pra arrastar ali."""
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QMouseEvent

    v = visualizador_modo_conteudo
    fora = QPoint(-20, -20)   # fora da propria folha (0,0,400,400)
    v.mousePressEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonPress, fora, Qt.LeftButton, Qt.LeftButton))
    assert v._arrastando is None


def test_soltar_o_mouse_emite_conteudo_movido_com_o_retangulo_final(
        visualizador_modo_conteudo):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QMouseEvent

    v = visualizador_modo_conteudo
    origem = v._area_do_conteudo().center()
    destino = QPoint(origem.x() + 40, origem.y() + 20)

    recebidos = []
    v.conteudo_movido.connect(lambda r: recebidos.append(r))

    v.mousePressEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonPress, origem, Qt.LeftButton, Qt.LeftButton))
    v.mouseMoveEvent(_construir_evento(
        QMouseEvent.Type.MouseMove, destino, Qt.NoButton, Qt.LeftButton))
    v.mouseReleaseEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonRelease, destino, Qt.LeftButton, Qt.NoButton))

    assert len(recebidos) == 1
    assert recebidos[0] == v._retangulo_conteudo


# --- Fase 3 (confirmado pelo Samuel, 22/09/2026: "quero conseguir
# redimensionar o conteudo tambem") - arrastar um CANTO do conteúdo pra
# mudar o tamanho, sempre proporcional (mantém a razão largura/altura -
# esticar só um lado distorceria a imagem). Mesmo algoritmo de
# RECORTE_PROPORCAO (`_mover_recorte`), ancorado no centro do conteúdo -
# a posição (`conteudo_deslocamento`) não muda ao redimensionar, só o
# tamanho (`conteudo_escala`). Ímã/guias (`guias_ativas`) não se aplicam ao
# redimensionar - não existe noção de "tamanho padrão" pra grudar em nenhum
# lugar do código; ficou de fora por decisão consciente, ver relatório.

def arrastar_alca_conteudo(v, canto, dx_px, dy_px):
    """Mesmo estilo de `arrastar_conteudo`, mas pega uma ALÇA de canto do
    retângulo do conteúdo em vez do meio dele."""
    from PySide6.QtCore import QPoint

    origem = v._alcas(v._area_do_conteudo())[canto]
    v._arrastando = f"conteudo_{canto}"
    v._retangulo_conteudo_inicial = v._retangulo_conteudo
    v._ponto_inicial = origem
    v._redimensionar_conteudo(QPoint(origem.x() + dx_px, origem.y() + dy_px), canto)


def test_arrastar_canto_se_aumenta_o_conteudo_mantendo_a_proporcao(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    x0, y0, w0, h0 = v._retangulo_conteudo   # (0.2, 0.2, 0.5, 0.5) - 200x200px
    centro0 = (x0 + w0 / 2, y0 + h0 / 2)

    arrastar_alca_conteudo(v, "se", 40, 40)   # arrasta o canto inferior direito pra fora

    x1, y1, w1, h1 = v._retangulo_conteudo
    assert w1 > w0 and h1 > h0
    # proporcional: a razao largura/altura nao muda
    assert w1 / h1 == pytest.approx(w0 / h0, rel=1e-6)
    # ancorado no centro: o centro do retangulo nao se move
    assert (x1 + w1 / 2, y1 + h1 / 2) == pytest.approx(centro0, abs=1e-6)


def test_arrastar_canto_no_para_dentro_diminui_o_conteudo(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    w0, h0 = v._retangulo_conteudo[2], v._retangulo_conteudo[3]

    arrastar_alca_conteudo(v, "no", 30, 30)   # arrasta o canto superior esquerdo pra dentro

    w1, h1 = v._retangulo_conteudo[2], v._retangulo_conteudo[3]
    assert w1 < w0 and h1 < h0
    assert w1 / h1 == pytest.approx(w0 / h0, rel=1e-6)


def test_redimensionar_conteudo_nao_encolhe_alem_do_minimo(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    arrastar_alca_conteudo(v, "se", -4000, -4000)   # bem pra dentro, exagerado
    w1, h1 = v._retangulo_conteudo[2], v._retangulo_conteudo[3]
    assert w1 > 0.0 and h1 > 0.0
    assert min(w1, h1) >= 0.05 - 1e-6


def test_redimensionar_conteudo_nao_sai_do_canvas(visualizador_modo_conteudo):
    v = visualizador_modo_conteudo
    arrastar_alca_conteudo(v, "se", 4000, 4000)   # bem exagerado pra fora
    x1, y1, w1, h1 = v._retangulo_conteudo
    assert x1 >= -1e-6 and y1 >= -1e-6
    assert x1 + w1 <= 1.0 + 1e-6 and y1 + h1 <= 1.0 + 1e-6


def test_clicar_na_alca_do_canto_inicia_redimensionar_nao_mover(visualizador_modo_conteudo):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QMouseEvent

    v = visualizador_modo_conteudo
    canto = v._alcas(v._area_do_conteudo())["se"]
    v.mousePressEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonPress, canto, Qt.LeftButton, Qt.LeftButton))
    assert v._arrastando == "conteudo_se"


def test_soltar_apos_redimensionar_tambem_emite_conteudo_movido(visualizador_modo_conteudo):
    from PySide6.QtCore import QPoint, Qt
    from PySide6.QtGui import QMouseEvent

    v = visualizador_modo_conteudo
    canto = v._alcas(v._area_do_conteudo())["se"]
    destino = QPoint(canto.x() + 30, canto.y() + 30)

    recebidos = []
    v.conteudo_movido.connect(lambda r: recebidos.append(r))

    v.mousePressEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonPress, canto, Qt.LeftButton, Qt.LeftButton))
    v.mouseMoveEvent(_construir_evento(
        QMouseEvent.Type.MouseMove, destino, Qt.NoButton, Qt.LeftButton))
    v.mouseReleaseEvent(_construir_evento(
        QMouseEvent.Type.MouseButtonRelease, destino, Qt.LeftButton, Qt.NoButton))

    assert len(recebidos) == 1
    assert recebidos[0] == v._retangulo_conteudo
    # depois de soltar, nao fica preso arrastando
    assert v._arrastando is None
