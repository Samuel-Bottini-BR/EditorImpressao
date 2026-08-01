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


def test_pagina_limpa_nao_marca_nada():
    selecao = detectar(pagina_crua(), usar_layout=False)

    assert selecao.vazia
