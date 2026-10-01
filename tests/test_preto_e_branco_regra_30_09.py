"""A regra do Preto e branco do Samuel (30/09/2026), testada em paginas sinteticas.

"No Preto e branco, tudo sai em preto e branco, inclusive moldura dourada,
titulo colorido e iluminura. A moldura nao deve sair dourada (como no detector
antigo) nem preta chapada (como no novo): deve sair como desenho em preto e
branco, com os tracos e detalhes em preto e o fundo da faixa em branco, sem
perder o desenho. O titulo 'NOVEMBRE.' da Horas 26 sai preto no Preto e branco.
Nos outros filtros (Magico pro, Melhorar, Original), sai com a cor original."

Foto e pintura de tom continuo: saem em tons de cinza (decisao P1 do Samuel,
conferencia 2 de 30/09); a pagina com foto sai em cinza (1 canal), nao em 1 bit.

Emenda do Samuel (conferencia 3, 30/09, cartao N2): "Mantem a cor original
(como o ANTES); traco preto so se eu escolher" - de fabrica a moldura dourada e
a iluminura mantem a cor original; o desenho em preto e branco so com a opcao
decoracao_em_preto_e_branco (Projeto.pb_decoracao_em_preto_e_branco).

Quem faz: core/filtros.py, _preto_e_branco_com_gravura. Teste de maquina: as
paginas sao desenhadas aqui, sem o acervo.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import (
    MAGICO_PRO,
    MELHORAR,
    PRETO_E_BRANCO,
    aplicar_filtro_com_selecao,
)
from core.selecao import GRAVURA, Selecao, retangulo

PAPEL = (200, 222, 232)          # creme, em BGR
DOURADO = (70, 175, 215)         # faixa dourada clara, em BGR
CONTORNO = (40, 60, 120)         # linha marrom-avermelhada do contorno


def _moldura(altura=1200, largura=900, faixa=48, margem=100):
    """Pagina creme com uma moldura dourada (faixa de `faixa` pontos) com o
    contorno marrom fino dos dois lados, como as das Horas 13, 26 e 27.
    Devolve a imagem e a mascara da faixa (para marcar como gravura)."""
    img = np.full((altura, largura, 3), PAPEL, np.uint8)
    faixa_m = np.zeros((altura, largura), np.uint8)
    cv2.rectangle(faixa_m, (margem, margem), (largura - margem, altura - margem), 255, faixa)
    img[faixa_m > 0] = DOURADO
    meia = faixa // 2
    for d in (-meia, meia):     # o contorno fino, fora e dentro da faixa
        cv2.rectangle(img, (margem + d, margem + d),
                      (largura - margem - d, altura - margem - d), CONTORNO, 3)
    return img, faixa_m > 0


def _gravura_so_na_moldura(faixa):
    """Selecao de gravura que cobre so a faixa da moldura (forma livre)."""
    s = Selecao()
    altura, largura = faixa.shape
    # quatro tiras (cima, baixo, esquerda, direita) cobrindo a faixa, como
    # a forma livre do detector marca uma moldura
    ys, xs = np.nonzero(faixa)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    esp = 60
    for (a, b, c, d) in ((x0 - 6, y0 - 6, x1 + 6, y0 + esp), (x0 - 6, y1 - esp, x1 + 6, y1 + 6),
                         (x0 - 6, y0 - 6, x0 + esp, y1 + 6), (x1 - esp, y0 - 6, x1 + 6, y1 + 6)):
        s.acrescentar(retangulo(a / largura, b / altura, c / largura, d / altura, tipo=GRAVURA))
    return s


# --- a moldura dourada vira desenho -----------------------------------------

def test_de_fabrica_a_moldura_dourada_mantem_a_cor_original():
    """Emenda N2 do Samuel (conferencia 3, 30/09): "Mantem a cor original
    (como o ANTES); traco preto so se eu escolher". Sem curva nenhuma: o
    dourado sai igual ao original (nem escurecido, nem lavado) e o papel em
    volta, branco."""
    img, faixa = _moldura()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO,
                                             _gravura_so_na_moldura(faixa))
    assert mono is False, "com a moldura em cor a pagina nao cabe em 1 bit"
    assert saida.ndim == 3
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    diferenca = np.abs(saida[miolo].astype(int) - img[miolo].astype(int))
    assert int(np.percentile(diferenca, 99)) <= 2, "o dourado da moldura mudou de cor"
    # o papel de dentro da moldura (fora da zona) e o de volta da faixa: brancos
    assert float(saida[500:700, 300:600].min()) >= 250
    perto = cv2.dilate(faixa.astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    papel_da_zona = perto & ~cv2.dilate(faixa.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    assert float(np.median(saida[papel_da_zona].min(axis=1))) >= 250, "o papel em volta da faixa ficou creme"


def test_a_moldura_dourada_sai_como_desenho_em_um_bit_se_a_pessoa_escolher():
    """Nem dourada nem preta chapada: contorno preto, miolo da faixa branco.
    So com a opcao "No Preto e branco, molduras e iluminuras tambem em preto e
    branco" (decoracao_em_preto_e_branco)."""
    img, faixa = _moldura()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO,
                                             _gravura_so_na_moldura(faixa),
                                             decoracao_em_preto_e_branco=True)

    assert mono is True, "sem foto, a pagina inteira tem de caber em 1 bit"
    assert saida.ndim == 2 and set(np.unique(saida)) <= {0, 255}

    # o meio da faixa (longe do contorno) sai branco: nao e preta chapada
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    assert miolo.any()
    preto_no_miolo = float((saida[miolo] == 0).mean())
    assert preto_no_miolo < 0.05, f"a faixa saiu preta chapada ({preto_no_miolo:.0%})"

    # e o contorno fino sai preto: o desenho nao se perde
    meia = 24
    y = 100 - meia            # a linha de fora, no alto da moldura
    linha = saida[y - 1:y + 2, 300:600]
    assert float((linha == 0).mean()) > 0.6, "o contorno da moldura sumiu"


def test_nos_outros_filtros_a_moldura_continua_dourada():
    """Melhorar e Magico pro: a moldura com a cor do original."""
    img, faixa = _moldura()
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    for filtro in (MELHORAR, MAGICO_PRO):
        saida, mono = aplicar_filtro_com_selecao(img.copy(), filtro,
                                                 _gravura_so_na_moldura(faixa))
        assert mono is False
        sat = cv2.cvtColor(saida, cv2.COLOR_BGR2HSV)[:, :, 1]
        assert float(np.median(sat[miolo])) > 80, f"{filtro}: a moldura perdeu o dourado"


# --- o titulo colorido dentro da gravura sai preto -------------------------

def _titulo(img, mascara, x, y, cor):
    """Um "titulo" de letras de traco fino (7 pontos): hastes e anilhas, sem
    as juntas grossas das fontes do OpenCV (que chegam a 21 pontos e nao
    parecem letra impressa)."""
    for i in range(6):
        cx = x + i * 90
        if i % 2:
            cv2.ellipse(img, (cx + 25, y + 45), (25, 45), 0, 0, 360, cor, 7)
            cv2.ellipse(mascara, (cx + 25, y + 45), (25, 45), 0, 0, 360, 255, 7)
        else:
            cv2.line(img, (cx + 25, y), (cx + 25, y + 90), cor, 7)
            cv2.line(mascara, (cx + 25, y), (cx + 25, y + 90), 255, 7)


def test_o_titulo_colorido_dentro_da_gravura_sai_preto():
    """O 'NOVEMBRE.' da Horas 26: azul no original, preto no Preto e branco.

    A zona e a faixa estreita do titulo, como o detector a marca junto da
    moldura (zona fina: nao e foto - ver FOTO_ESPESSURA_MINIMA)."""
    img = np.full((2400, 1800, 3), PAPEL, np.uint8)
    letra = np.zeros(img.shape[:2], np.uint8)
    _titulo(img, letra, 100, 210, (150, 80, 40))        # azul medio
    _titulo(img, letra, 300, 510, (50, 50, 200))        # vermelho
    miolo = cv2.erode(letra, np.ones((3, 3), np.uint8)) > 0

    s = Selecao()
    s.acrescentar(retangulo(0.03, 190 / 2400, 0.97, 320 / 2400, tipo=GRAVURA))
    s.acrescentar(retangulo(0.10, 490 / 2400, 0.60, 620 / 2400, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)

    assert mono is True
    assert float((saida[miolo] == 0).mean()) > 0.95, "o titulo colorido nao saiu preto"
    # e o papel em volta, branco
    assert float((saida[1300:1500, 50:1750] == 255).mean()) > 0.99


# --- a xilogravura: traco preto, papel branco, sem virar mancha -----------

def test_a_gravura_de_traco_vira_desenho_com_o_papel_branco():
    img = np.full((800, 600, 3), (196, 212, 226), np.uint8)
    for x in range(60, 540, 8):           # hachura vertical fina
        img[100:700, x:x + 3] = (70, 75, 85)
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)

    assert mono is True
    assert set(np.unique(saida)) <= {0, 255}
    faixa = saida[300:500, 60:540]
    preto = float((faixa == 0).mean())
    # 3 de cada 8 pontos sao traco: nem sumiu, nem virou mancha
    assert 0.25 < preto < 0.55, f"fracao de preto na hachura: {preto:.2f}"


def test_a_nota_quadrada_larga_sai_cheia():
    """Mancha de tinta preta mais larga que o elemento (nota do Graduale):
    nao pode sair oca, so com o contorno."""
    img = np.full((1200, 900, 3), (205, 215, 225), np.uint8)
    for x in range(100, 800, 120):
        img[500:560, x:x + 60] = (45, 45, 50)      # notas de 60 x 60, tinta
    s = Selecao()
    s.acrescentar(retangulo(0.02, 0.41, 0.98, 0.48, tipo=GRAVURA))   # faixa fina
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert mono is True
    assert float((saida[510:550, 110:150] == 0).mean()) > 0.95, "a nota saiu oca"


# --- a foto de tom continuo sai em tons de cinza (decisao P1, 30/09) ---------

def _pagina_com_foto():
    """Moldura dourada com uma "foto" colorida em degrade no miolo."""
    img, faixa = _moldura(altura=1200, largura=900)
    degrade = np.linspace(60, 200, 400).astype(np.uint8)
    foto = np.dstack([degrade[None, :]] * 3).repeat(400, axis=0).astype(np.int16)
    foto[:, :, 0] -= 30          # um pouco amarelada: a foto tem cor
    img[400:800, 250:650] = np.clip(foto, 0, 255).astype(np.uint8)
    s = _gravura_so_na_moldura(faixa)
    s.acrescentar(retangulo(250 / 900, 400 / 1200, 650 / 900, 800 / 1200, tipo=GRAVURA))
    return img, faixa, s


def test_foto_sai_em_tons_de_cinza_e_a_moldura_vira_desenho():
    """Decisao P1 do Samuel: a foto sai em tons de cinza (sem cor, sem
    pontilhado); com a moldura em desenho (opcao marcada), a pagina sai em
    cinza, 1 canal."""
    img, faixa, s = _pagina_com_foto()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s,
                                             decoracao_em_preto_e_branco=True)

    assert mono is False, "com foto a pagina nao cabe em 1 bit"
    assert saida.ndim == 2, "a foto em tons de cinza: a pagina sai em 1 canal, sem cor"
    miolo_da_foto = saida[450:750, 300:600]
    assert len(np.unique(miolo_da_foto)) > 30, "a foto perdeu o tom continuo"
    # escuro continua escuro e claro continua claro (o degrade nao virou outro)
    assert int(miolo_da_foto[:, :20].mean()) < int(miolo_da_foto[:, -20:].mean()) - 60


def test_foto_em_cinza_vem_do_original_e_nao_do_melhorar():
    """A estatua do Opus 20 tem a cor do papel: o Melhorar a levava quase a
    branco. O cinza vem do original (so o desfoque e o esticao dos niveis)."""
    import core.filtros as F

    img, faixa, s = _pagina_com_foto()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s,
                                          decoracao_em_preto_e_branco=True)
    esperado = F._foto_em_tons_de_cinza(
        img, F._niveis_da_foto(img, s.peso(1200, 900, GRAVURA) > 0))
    diferenca = np.abs(saida[450:750, 300:600].astype(int) - esperado[450:750, 300:600].astype(int))
    assert int(diferenca.max()) <= 1


def test_papel_dentro_da_zona_da_foto_sai_branco():
    """"Papel em volta branco": um canto de papel que o detector marcou como
    foto (o caso do Marial 7) nao pode ficar cinza, mesmo com pontos brancos
    puros na pagina (o preenchimento do corte)."""
    img = np.full((1200, 900, 3), (190, 210, 222), np.uint8)
    img[:, :20] = 255                      # o branco do preenchimento do corte
    for y in range(500, 1150, 30):          # texto no resto da pagina
        img[y:y + 10, 100:800:14] = 40
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 0.5, 0.35, tipo=GRAVURA))   # canto de papel liso
    saida, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert float(np.median(saida[50:350, 100:400])) >= 250, "o papel da zona ficou cinza"


def test_de_fabrica_foto_em_cinza_e_moldura_em_cor_na_mesma_pagina():
    """De fabrica: a foto em tons de cinza (sem cor) e a moldura com a cor
    original, na mesma pagina (que sai em cor, 3 canais)."""
    img, faixa, s = _pagina_com_foto()
    saida, mono = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s)
    assert mono is False and saida.ndim == 3
    foto = saida[450:750, 300:600].astype(int)
    assert int(np.abs(foto[:, :, 0] - foto[:, :, 2]).max()) <= 1, "a foto ficou com cor"
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    sat = cv2.cvtColor(saida, cv2.COLOR_BGR2HSV)[:, :, 1]
    assert float(np.median(sat[miolo])) > 80, "a moldura perdeu o dourado"


def test_moldura_ao_lado_da_foto_continua_desenho_se_a_pessoa_escolher():
    img, faixa, s = _pagina_com_foto()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, s,
                                          decoracao_em_preto_e_branco=True)
    miolo = cv2.erode(faixa.astype(np.uint8), np.ones((25, 25), np.uint8)) > 0
    assert set(np.unique(saida[miolo])) <= {0, 255}, "a moldura tinha de sair em preto e branco"
    assert float((saida[miolo] == 0).mean()) < 0.05


def test_pagina_em_cinza_com_gravura_nao_quebra():
    cinza = np.full((600, 400), 210, np.uint8)
    cinza[100:500:6, 50:350] = 60
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 1.0, tipo=GRAVURA))
    saida, mono = aplicar_filtro_com_selecao(cinza, PRETO_E_BRANCO, s)
    assert saida.shape[:2] == cinza.shape and mono is True


def test_sem_foto_o_preto_e_branco_nao_roda_o_melhorar(monkeypatch):
    """Regra 6 (velocidade): com moldura e titulo so (sem foto), o Preto e
    branco nao passa mais pelo Melhorar - era ~3 s por pagina a 300 DPI."""
    import core.filtros as F

    chamadas = []
    original = F.filtro_melhorar
    monkeypatch.setattr(F, "filtro_melhorar",
                        lambda *a, **k: chamadas.append(1) or original(*a, **k))
    img, faixa = _moldura()
    for traco in (False, True):
        F.aplicar_filtro_com_selecao(img.copy(), PRETO_E_BRANCO, _gravura_so_na_moldura(faixa),
                                     decoracao_em_preto_e_branco=traco)
    assert not chamadas, "o Melhorar rodou no Preto e branco"


# --- o vermelho fora da gravura sai preto (decisao V1, 30/09) ---------------

@pytest.mark.parametrize("cor", [(50, 50, 200), (50, 130, 200)], ids=["vermelho", "dourado"])
def test_titulo_colorido_fora_da_gravura_sai_preto(cor):
    """Decisao V1 do Samuel ("o que e vermelho - titulos, rubrica - sai
    preto"): o "TABLE" vermelho da Horas 13 e as letras "A" douradas da Horas
    27 sumiam no Preto e branco (a conversao para cinza pelo maior canal lia a
    tinta colorida como clara). Pagina sem marcacao nenhuma: o caminho de
    sempre do Preto e branco."""
    from core.filtros import aplicar_filtro

    img = np.full((1400, 1000, 3), PAPEL, np.uint8)
    letra = np.zeros(img.shape[:2], np.uint8)
    _titulo(img, letra, 120, 200, cor)
    for y in range(600, 1300, 40):          # texto preto comum no resto
        img[y:y + 12, 100:900:16] = (30, 30, 30)
    saida, mono = aplicar_filtro(img.copy(), PRETO_E_BRANCO)
    assert mono is True
    miolo = cv2.erode(letra, np.ones((3, 3), np.uint8)) > 0
    assert float((saida[miolo] == 0).mean()) > 0.9, "o titulo colorido sumiu no Preto e branco"
