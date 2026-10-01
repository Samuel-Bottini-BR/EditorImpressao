"""Consertos da conferencia 5 do Samuel (01/10/2026), testes de maquina.

Respostas literais em relatorios/conferencia-samuel-2026-10-01.md. Cada teste
diz o cartao que ele protege. As imagens sao sinteticas (pequenas e rapidas);
o teste de olho e a rodada de antes/depois nas paginas-gabarito.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

from core.filtros import aplicar_filtro_com_selecao
from core.selecao import GRAVURA, Selecao, retangulo

PAPEL = (200, 222, 232)          # BGR do papel creme
OURO = (60, 170, 215)            # BGR de um dourado


def _pagina_com_letra_dourada_na_decoracao():
    """Moldura dourada larga (decoracao), uma pintura com traco fino e, no
    papel da zona, um "O" dourado grosso (anel) e, ao lado, um "I" dourado. A zona de gravura
    cobre a moldura e o papel de dentro (como a iluminura da Horas 11, em que
    o oval com o titulo esta dentro da zona). Fora da zona, linhas de texto."""
    img = np.full((1200, 900, 3), PAPEL, np.uint8)
    for y in range(700, 1150, 30):
        img[y:y + 10, 120:780:14] = 40
    cv2.rectangle(img, (60, 60), (840, 600), OURO, 60)
    img[440:560, 120:780] = (150, 210, 140)        # uma pintura com traco fino
    img[440:560, 120:780:3] = (30, 50, 20)         # (para a zona nao ser "foto")
    cv2.ellipse(img, (400, 330), (22, 36), 0, 0, 360, OURO, 10)       # o "O"
    img[290:370, 520:530] = OURO                                       # o "I"
    s = Selecao()
    s.acrescentar(retangulo(0.0, 0.0, 1.0, 0.56, tipo=GRAVURA))
    return img, s


# --- A2: "queremos a pagina inteiramente branca" (Horas 11) ------------------

@pytest.mark.parametrize("filtro", ["magico_pro", "preto_e_branco"])
def test_miolo_da_letra_dourada_vai_a_branco(filtro):
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), filtro, s)
    saida = saida if saida.ndim == 3 else cv2.cvtColor(saida, cv2.COLOR_GRAY2BGR)
    miolo = saida[315:345, 393:407]
    assert int(miolo.min()) >= 250, "o miolo do O ficou creme"


def test_sem_fio_creme_em_volta_da_letra_dourada():
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", s)
    # a faixa de papel encostada no "I" (sem o conserto: 201 a 247, creme)
    assert int(saida[300:360, 530:536].min()) >= 250, "fio creme do lado de fora da letra"
    assert int(saida[300:360, 514:520].min()) >= 250, "fio creme do lado de fora da letra"


def test_a_letra_dourada_continua_com_a_cor_no_magico_pro():
    img, s = _pagina_com_letra_dourada_na_decoracao()
    saida, _ = aplicar_filtro_com_selecao(img.copy(), "magico_pro", s)
    centro = saida[300:360, 523:527].astype(int)
    assert int(np.abs(centro - np.array(OURO)).max()) <= 3, "o dourado da letra mudou"
