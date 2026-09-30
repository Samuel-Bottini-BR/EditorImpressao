"""Gravura pequena: o Melhorar nao roda mais na folha inteira.

Achado no teste de velocidade de 29/09/2026 (regra 6 do plano: nenhum item
pode deixar o programa mais lento). O Preto e branco ficou 8% mais lento no
Marial: o detector passou a marcar como gravura o titulo corrido "de Maria." da
pagina 153 - 0,4% da folha -, e qualquer gravura, por menor que seja, fazia
_limpar_cada_gravura rodar o Melhorar na FOLHA INTEIRA (quase 3 segundos a 300
DPI), alem do recorte da propria gravura. Fora dos recortes esse resultado so e
usado na borda suave em volta da gravura (e nos pedacinhos de gravura pequenos
demais para ter recorte proprio).

Com gravura pequena e sem pedacinhos, a borda suave passa a usar o proprio
filtro da pagina (ver GRAVURA_PEQUENA_ATE em core/filtros.py). O que estes
testes garantem:
  - com gravura pequena, o Melhorar so roda nos recortes das gravuras;
  - dentro do recorte o resultado e o mesmo de antes;
  - fora da borda suave, a pagina final e ponto a ponto a de antes;
  - no filtro Melhorar, a pagina inteira e ponto a ponto a de antes;
  - com gravura grande ou com pedacinho de gravura, tudo como antes.
"""

from __future__ import annotations

import numpy as np
import pytest

import core.filtros as F
from core.selecao import GRAVURA, Selecao, retangulo

FILTROS_DA_GRAVURA = [F.MAGICO_PRO, F.MELHORAR, F.PRETO_E_BRANCO]


def _pagina(alt: int = 1200, larg: int = 900) -> np.ndarray:
    """Folha amarelada de texto (a limpeza do papel liga), com um titulo
    corrido no alto - o caso do Marial 153."""
    img = np.full((alt, larg, 3), (196, 214, 230), np.uint8)
    for y in range(160, alt - 40, 20):
        for x in range(40, larg - 40, 12):
            img[y:y + 7, x:x + 6] = 35
    for x in range(330, 570, 16):          # o titulo: letras maiores
        img[60:92, x:x + 10] = 40
    return img


def _selecao(img: np.ndarray, *caixas: tuple[int, int, int, int]) -> Selecao:
    alt, larg = img.shape[:2]
    selecao = Selecao()
    for x0, y0, x1, y1 in caixas:
        regiao = retangulo(x0 / larg, y0 / alt, x1 / larg, y1 / alt, tipo=GRAVURA)
        regiao.suavidade = 0.004            # a mesma borda suave do detector
        selecao.acrescentar(regiao)
    return selecao


TITULO = (320, 50, 580, 100)                # 1,2% da folha


def _pesos(img: np.ndarray, selecao: Selecao) -> np.ndarray:
    return selecao.peso(img.shape[0], img.shape[1], GRAVURA)


def _como_antes(monkeypatch) -> None:
    """Faz _limpar_cada_gravura ignorar o caminho rapido: o comportamento de
    antes, com o Melhorar da folha inteira."""
    original = F._limpar_cada_gravura
    monkeypatch.setattr(
        F, "_limpar_cada_gravura",
        lambda im, grav, clareza=F.AJUSTE_PADRAO, onde_vale=None, fundo=None:
        original(im, grav, clareza))


def _diferenca(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    return d.max(axis=2) if d.ndim == 3 else d


def test_gravura_pequena_nao_roda_o_melhorar_na_folha_inteira(monkeypatch):
    img = _pagina()
    selecao = _selecao(img, TITULO)
    formas: list[tuple[int, int]] = []
    original = F.filtro_melhorar

    def envelope(im, *a, **k):
        formas.append(tuple(im.shape[:2]))
        return original(im, *a, **k)

    monkeypatch.setattr(F, "filtro_melhorar", envelope)
    # Era no Preto e branco. Desde a regra de 30/09/2026 o Preto e branco nao
    # roda mais o Melhorar em gravura nenhuma (so em foto): o titulo vira
    # desenho. O caminho rapido continua valendo no Magico pro.
    F.aplicar_filtro_com_selecao(img.copy(), F.MAGICO_PRO, selecao)

    assert formas, "a gravura nao passou pelo Melhorar"
    assert img.shape[:2] not in formas, "o Melhorar ainda roda na folha inteira"


def test_dentro_do_recorte_o_resultado_e_o_mesmo():
    img = _pagina()
    selecao = _selecao(img, TITULO)
    pesos = _pesos(img, selecao)
    gravura = pesos > 0.5
    fundo = F.filtro_preto_e_branco(img)

    antes = F._limpar_cada_gravura(img, gravura)
    depois = F._limpar_cada_gravura(img, gravura, onde_vale=pesos > 0, fundo=fundo)

    ys, xs = np.where(gravura)
    recorte = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
    assert np.array_equal(antes[recorte], depois[recorte])


@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_fora_da_borda_suave_a_pagina_e_a_mesma(monkeypatch, filtro):
    """So pode mudar a borda suave em volta do recorte (peso entre 0 e 1)."""
    img = _pagina()
    selecao = _selecao(img, TITULO)
    pesos = _pesos(img, selecao)

    depois = F.aplicar_filtro_com_selecao(img.copy(), filtro, selecao)[0]
    _como_antes(monkeypatch)
    antes = F.aplicar_filtro_com_selecao(img.copy(), filtro, selecao)[0]

    ys, xs = np.where(pesos > 0.5)
    recorte = np.zeros(pesos.shape, bool)
    recorte[ys.min():ys.max() + 1, xs.min():xs.max() + 1] = True
    so_a_borda = (pesos > 0) & ~recorte
    assert not (_diferenca(antes, depois)[~so_a_borda] > 0).any(), \
        "mudou fora da borda suave da gravura"


def test_no_filtro_melhorar_a_pagina_e_identica(monkeypatch):
    """No Melhorar, o filtro da pagina JA e o Melhorar da folha inteira: o
    caminho rapido tem de dar exatamente o mesmo resultado."""
    img = _pagina()
    selecao = _selecao(img, TITULO)
    depois = F.aplicar_filtro_com_selecao(img.copy(), F.MELHORAR, selecao)[0]
    _como_antes(monkeypatch)
    antes = F.aplicar_filtro_com_selecao(img.copy(), F.MELHORAR, selecao)[0]
    assert np.array_equal(antes, depois)


@pytest.mark.parametrize("caixas", [
    [(60, 150, 840, 900)],                  # gravura grande: mais da metade
    [TITULO, (40, 1100, 70, 1130)],          # titulo + um pedacinho (< 0,2%)
], ids=["gravura_grande", "com_pedacinho"])
@pytest.mark.parametrize("filtro", FILTROS_DA_GRAVURA)
def test_fora_do_caso_pequeno_nada_muda(monkeypatch, caixas, filtro):
    img = _pagina()
    selecao = _selecao(img, *caixas)
    depois = F.aplicar_filtro_com_selecao(img.copy(), filtro, selecao)[0]
    _como_antes(monkeypatch)
    antes = F.aplicar_filtro_com_selecao(img.copy(), filtro, selecao)[0]
    assert np.array_equal(antes, depois)
