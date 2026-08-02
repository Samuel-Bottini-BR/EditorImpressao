"""O detector automatico: iluminura, escrita e o que fica no meio.

Paginas sinteticas, e nao paginas do acervo, para o teste rodar em qualquer
maquina e nao depender do modelo de layout estar instalado. As medidas que estes
casos travam sairam do acervo - ver os comentarios em core/detectar_regioes.py.
"""

import numpy as np

from core.detectar_regioes import detectar
from core.selecao import GRAVURA, LETRA

ALTURA, LARGURA = 900, 700
PAPEL = 238


def pagina_crua() -> np.ndarray:
    return np.full((ALTURA, LARGURA, 3), PAPEL, dtype=np.uint8)


def com_moldura(img: np.ndarray) -> np.ndarray:
    """Uma moldura iluminada: azul e laranja saturados, como no Livro de Horas."""
    img[60:840, 60:640] = (255, 40, 0)      # azul saturado
    img[110:790, 110:590] = (0, 120, 255)   # laranja saturado
    img[150:750, 150:550] = PAPEL           # o vazio que a moldura cerca
    return img


def escrever(img: np.ndarray, pautado: bool = False) -> np.ndarray:
    """Linhas de escrita: pedacinhos do tamanho de um glifo, com vao entre eles."""
    for linha in range(20):
        y = 170 + linha * 28
        if pautado:  # a pauta atravessa o painel de ponta a ponta
            img[y + 20 : y + 22, 160:540] = 120
        for palavra in range(9):
            x = 165 + palavra * 42
            for glifo in range(3):
                img[y : y + 14, x + glifo * 11 : x + glifo * 11 + 7] = 25
    return img


def pintar(img: np.ndarray) -> np.ndarray:
    """Uma cena pintada: manchas grandes, sem vao entre linhas.

    A paisagem no meio da moldura do Livro de Horas e clara demais para o corte
    de saturacao, mas TEM detalhe - arvore, ponte, agua. E o detalhe que o
    detector de tinta enxerga; o que ela nao tem e compasso de escrita.
    """
    import cv2

    for i, cor in enumerate(((90, 120, 70), (130, 90, 60), (70, 100, 140),
                             (110, 130, 100), (60, 80, 110))):
        cv2.ellipse(img, (250 + i * 60, 300 + (i % 3) * 130),
                    (90 + i * 12, 70 + i * 9), i * 25, 0, 360, cor, -1)
    return img


def mascara(img, tipo):
    return detectar(img, usar_layout=False).mascara(ALTURA, LARGURA, tipo) > 0


def test_a_cena_pintada_dentro_da_moldura_e_gravura():
    """O buraco que a mascara de cor deixa na iluminura precisa ser tapado.

    A pintura clara nao passa no corte de saturacao, e sem tapar o buraco ela
    era preenchida pelo detector de tinta e saia marcada como LETRA - era o
    manto azul da figura recebendo tratamento de texto.
    """
    gravura = mascara(pintar(com_moldura(pagina_crua())), GRAVURA)

    assert gravura[450, 350], "a cena pintada no meio da moldura nao virou gravura"


def test_o_texto_cercado_pela_moldura_nao_vira_gravura():
    """Tapar TUDO engoliria a pagina escrita que a moldura cerca."""
    img = escrever(com_moldura(pagina_crua()))

    assert not mascara(img, GRAVURA)[450, 350], "a moldura engoliu o bloco de texto"
    assert mascara(img, LETRA)[450, 350], "o bloco de texto nao ficou como letra"


def test_o_texto_em_papel_pautado_tambem_e_poupado():
    """A pauta atravessa o painel e apaga o vao entre as linhas.

    E o caso da pagina 142 do Livro de Horas: sem olhar o TAMANHO dos pedacos de
    tinta, o painel escrito inteiro virava gravura.
    """
    img = escrever(com_moldura(pagina_crua()), pautado=True)

    assert not mascara(img, GRAVURA)[450, 350], "a pauta fez o texto virar gravura"


def test_a_moldura_continua_sendo_gravura():
    for img in (pintar(com_moldura(pagina_crua())),
                escrever(com_moldura(pagina_crua()))):
        assert mascara(img, GRAVURA)[80, 350], "a moldura deixou de ser gravura"


def manchar(img: np.ndarray) -> np.ndarray:
    """Mancha de papel envelhecido: saturada o bastante para passar por cor."""
    janela = img[160:620, 160:540]
    claro = janela.max(axis=2) > 200
    janela[claro] = (60, 170, 230)
    return img


def test_mancha_do_papel_por_cima_do_texto_nao_vira_gravura():
    """Foi o borrao vermelho na pagina 223 da Rhetorica, que e so texto.

    Manchas de envelhecimento passam no corte de saturacao e cobriam 19,6% da
    folha. O que decide nao e o tamanho da mancha e sim o que ha embaixo dela:
    se e escrita, nao e iluminura.
    """
    img = manchar(escrever(pagina_crua()))

    assert not mascara(img, GRAVURA)[400, 350], "a mancha do papel virou gravura"
    assert mascara(img, LETRA)[400, 350], "o texto sob a mancha nao ficou como letra"


def test_escrita_e_desenho_se_separam_pelo_tamanho_do_pedaco():
    """A medida que distingue xilogravura de caligrafia e de partitura.

    O modelo de layout chama de "figure" as tres, e o tratamento que cada uma
    pede e oposto. Meio-tom nao resolve (xilogravura e traco puro) e vao entre
    linhas nao resolve (ornamento 23,7%, partitura 22,6%). O tamanho do pedaco
    de tinta resolve: no acervo, desenho fica entre 4% e 14%, escrita entre 49%
    e 93%.
    """
    from core.detectar_regioes import (
        PEDACOS_DE_GLIFO_DE_ESCRITA,
        _tinta_em_pedacos_de_glifo,
        mascara_de_tinta,
    )

    escrita = mascara_de_tinta(escrever(pagina_crua())[150:750, 150:550])
    desenho = mascara_de_tinta(pintar(pagina_crua())[150:750, 150:550])

    assert _tinta_em_pedacos_de_glifo(escrita) >= PEDACOS_DE_GLIFO_DE_ESCRITA
    assert _tinta_em_pedacos_de_glifo(desenho) < PEDACOS_DE_GLIFO_DE_ESCRITA


def test_capa_inteira_nao_ganha_tarja_de_letra():
    """No verso da capa do Palatino sobrava uma faixa de letra no alto.

    O modelo desenha a caixa da foto em quase toda a folha, e a faixa que fica
    de fora e a mesma capa, cortada pelo retangulo. Virando letra, o veio da
    madeira seria binarizado.
    """
    from core.detectar_regioes import _e_uma_foto_de_pagina_inteira

    vazio = np.zeros((100, 100), bool)
    foto = np.zeros((100, 100), bool)
    foto[:88, :] = True          # a caixa do modelo, como nas capas do acervo
    # A textura da capa que sobra fora da caixa: no acervo isso da de 1,8% a
    # 4,9% da pagina.
    tinta = np.zeros((100, 100), bool)
    tinta[:92, :] = True

    assert _e_uma_foto_de_pagina_inteira(foto, vazio, tinta)

    # com bloco de texto na pagina, nao e foto de pagina inteira
    com_texto = np.zeros((100, 100), bool)
    com_texto[90:, :] = True
    assert not _e_uma_foto_de_pagina_inteira(foto, com_texto, tinta)

    # gravura pequena tambem nao vale
    pequena = np.zeros((100, 100), bool)
    pequena[:30, :] = True
    assert not _e_uma_foto_de_pagina_inteira(pequena, vazio, tinta)


def test_pagina_limpa_nao_marca_nada():
    selecao = detectar(pagina_crua(), usar_layout=False)

    assert selecao.vazia
