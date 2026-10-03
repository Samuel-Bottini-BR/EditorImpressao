"""Regra 6 (velocidade), 02/10/2026: a Horas 11 no Preto e branco pagava a
medida de espessura de tamanho cheio (~9,5 s) so porque a medida reduzida
achava 60,4% de tinta contra a trava de 60% (a moldura e a iluminura enchem
metade da folha) e desistia. Sem a trava, a medida reduzida da 44 (o limite
do Otsu com folga e 16; a cheia da 33,9): Otsu com certeza.

O que estes testes protegem (teste de maquina): a escolha automatica usa a
medida reduzida sem a trava so para responder "Otsu com folga", e entao nao
faz a medida cheia; a tinta da folha inteira continua decidindo como antes
(acima de 60%, Sauvola); traco fino continua indo para a medida cheia; e o k
(k_para_a_letra) nao muda - ele continua vendo a medida COM a trava.
"""

from __future__ import annotations

import cv2
import numpy as np

from core import filtros as F

PAPEL = 225


def _folha(grossura: int, escura: bool = False) -> np.ndarray:
    cinza = np.full((3200, 2200), PAPEL, np.uint8)
    for y in range(200, 3000, 160):
        cv2.line(cinza, (200, y), (2000, y), 40, grossura)
    if escura:                       # mais de 60% de tinta na folha inteira
        cinza[:2200, :] = 40
    return cinza


def _sem_a_medida_guardada(monkeypatch):
    """Simula a pagina em que a medida reduzida (a do k) desiste pela trava
    de tinta, e conta as medidas de tamanho cheio (o esqueleto da folha
    inteira, a conta cara)."""
    monkeypatch.setattr(F, "_espessura_do_traco", lambda cinza: None)
    cheias = []
    esqueleto = F._esqueleto

    def contar(tinta):
        if tinta.shape[0] > F.ALTURA_PARA_MEDIR_TRACO:
            cheias.append(tinta.shape)
        return esqueleto(tinta)

    monkeypatch.setattr(F, "_esqueleto", contar)
    return cheias


def test_traco_grosso_com_folga_nao_paga_a_medida_cheia(monkeypatch):
    cheias = _sem_a_medida_guardada(monkeypatch)
    assert F.escolher_algoritmo_automatico(_folha(60)) == F.ALGORITMO_OTSU
    assert cheias == [], "fez a medida de tamanho cheio"


def test_folha_com_tinta_demais_continua_sauvola(monkeypatch):
    """Como na medida cheia: mais de 60% de tinta na folha inteira, Sauvola."""
    _sem_a_medida_guardada(monkeypatch)
    assert F.escolher_algoritmo_automatico(_folha(60, escura=True)) == F.ALGORITMO_SAUVOLA


def test_traco_fino_continua_na_medida_cheia(monkeypatch):
    cheias = _sem_a_medida_guardada(monkeypatch)
    assert F.escolher_algoritmo_automatico(_folha(3)) == F.ALGORITMO_SAUVOLA
    assert cheias, "o traco fino deveria ir para a medida cheia"


def test_a_trava_continua_valendo_para_o_k():
    """A medida sem trava e so da escolha: a medida guardada (a do k) segue
    desistindo acima de 60% de tinta."""
    cinza = np.full((800, 600), 40, np.uint8)
    cinza[::7, :] = PAPEL
    F._KS_GUARDADOS.clear()
    assert F._espessura_do_traco(cinza) is None
    assert F.k_para_a_letra(cinza) == F.K_NORMAL
    assert F._medir_espessura_do_traco(cinza, trava_de_tinta=False) is not None
