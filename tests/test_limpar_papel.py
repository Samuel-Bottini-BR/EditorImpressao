"""A limpeza do papel: tira a mancha do verso sem comer a obra.

Os quatro casos sao os quatro jeitos de errar que ja aconteceram de verdade
durante o desenvolvimento, cada um pego numa pagina do acervo.
"""

from __future__ import annotations

import cv2
import numpy as np

from core.filtros import (
    PECAS_DE_TEXTO_MINIMAS,
    _limpar_o_papel_de_verdade,
)


def _pagina_de_texto(mancha: bool = False) -> np.ndarray:
    """Folha amarelada com muitas letrinhas - e, se pedido, a mancha do verso.

    As "letras" sao quadradinhos de 6x6: area 36, acima do corte de peca de
    letra. A mancha e feita de pontinhos de 2x2 - area 4, abaixo do corte - que
    e exatamente a diferenca medida na pagina 33 do Boecio.
    """
    img = np.full((600, 500, 3), (205, 228, 245), np.uint8)  # BGR: papel ambar

    linhas = 0
    for y in range(20, 560, 18):
        for x in range(20, 300, 12):
            img[y:y + 6, x:x + 6] = 30
            linhas += 1
    assert linhas > PECAS_DE_TEXTO_MINIMAS, "o teste precisa de pagina de texto"

    if mancha:
        for y in range(24, 560, 9):
            for x in range(330, 480, 7):
                img[y:y + 2, x:x + 2] = (150, 175, 195)  # mais fraca que a letra
    return img


def test_tira_a_mancha_do_verso_e_deixa_a_letra():
    img = _pagina_de_texto(mancha=True)
    limpa = _limpar_o_papel_de_verdade(img, img.copy())

    faixa_da_mancha = limpa[:, 330:480]
    assert faixa_da_mancha.min() >= 250, "a mancha do verso continua na folha"

    faixa_da_letra = limpa[:, 20:300]
    assert faixa_da_letra.min() < 60, "a letra foi embora junto com a mancha"


def test_o_papel_vira_branco_puro():
    img = _pagina_de_texto()
    limpa = _limpar_o_papel_de_verdade(img, img.copy())
    # Entre as linhas de letra so ha papel. Amarelado ali vira cor na impressora,
    # que foi a queixa: "a impressora vai entender como cor a ser impressa".
    entre_as_linhas = limpa[12:18, 20:300]
    assert (entre_as_linhas == 255).all(), "sobrou creme entre as linhas"


def test_nao_mexe_em_estampa_sem_texto():
    """A estampa do Catecismo perdia o ceu azul: pouca tinta, fundo claro."""
    img = np.full((600, 500, 3), (235, 200, 170), np.uint8)  # ceu azul palido
    cv2.circle(img, (250, 300), 90, (40, 40, 40), -1)        # a figura

    limpa = _limpar_o_papel_de_verdade(img, img.copy())
    assert np.array_equal(limpa, img), "a limpeza entrou numa pagina sem texto"


def test_nao_apaga_cor_que_nao_e_do_papel():
    """Rubricacao vermelha e ceu azul nao sao papel sujo, sao a obra."""
    img = _pagina_de_texto()
    img[300:340, 350:450] = (60, 60, 200)  # BGR: vermelho de rubrica

    limpa = _limpar_o_papel_de_verdade(img, img.copy())
    vermelho = limpa[300:340, 350:450]
    assert vermelho.mean() < 200, "a rubricacao vermelha foi apagada"
