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

import os
from pathlib import Path

import cv2
import numpy as np
import pytest

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


# --- a trava do atalho (05/10/2026) -------------------------------------------
#
# Ressalva do verificador (parecer de 02/10, `7f50e70`): o atalho confia que a
# copia reduzida e a pagina inteira "enxergam" a mesma tinta. Numa foto em
# retícula fina (pontinhos de impressao), a copia reduzida ve cinza liso (muita
# tinta, traco "grosso") e a pagina inteira ve pontinhos (pouca tinta, traco
# fino): numa folha artificial com retícula de 1 ponto em 85% da folha, a
# escolha trocava de Sauvola (a da medida cheia) para Otsu. Agora o atalho so
# age quando as duas tintas sao parecidas (ver DIFERENCA_DE_TINTA_DO_ATALHO em
# core/filtros.py); senao, a medida cheia decide, como antes de `7f50e70`.


def _folha_com_reticula(fracao_da_foto: float, periodo: int = 1) -> np.ndarray:
    """A folha do verificador (contraexemplo_reticula.py, 02/10): retícula de
    `periodo` pontos cobrindo `fracao_da_foto` da altura, e texto fino (3
    pontos) embaixo."""
    altura, largura = 3300, 2300
    cinza = np.full((altura, largura), PAPEL, np.uint8)
    yy, xx = np.mgrid[0:altura, 0:largura]
    foto = yy < int(altura * fracao_da_foto)
    pontos = ((yy // periodo + xx // periodo) % 2 == 0)
    cinza[foto & pontos] = 60
    for y in range(int(altura * fracao_da_foto) + 60, altura - 40, 45):
        cv2.line(cinza, (150, y), (largura - 150, y), 40, 3)
    return cinza


def _escolha_da_medida_cheia(cinza: np.ndarray) -> str:
    """O que a medida de tamanho cheio responde (a escolha de antes do atalho)."""
    _lim, tinta = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    tinta = (tinta > 0).astype(np.uint8)
    if not (0.002 <= tinta.mean() <= 0.6):
        return F.ALGORITMO_SAUVOLA
    distancia = cv2.distanceTransform(tinta, cv2.DIST_L2, 5)
    esqueleto = F._esqueleto(tinta > 0)
    espessura = float(2.0 * distancia[esqueleto].mean())
    return (F.ALGORITMO_OTSU if espessura >= F.ESPESSURA_DE_LETRA_GROSSA
            else F.ALGORITMO_SAUVOLA)


@pytest.mark.parametrize("fracao_da_foto", [0.6, 0.85, 0.9])
def test_reticula_fina_nao_troca_a_escolha(fracao_da_foto):
    """A folha do verificador: a copia reduzida acha 64 a 91% de tinta, a
    pagina inteira 34 a 46%. O atalho nao pode agir; a escolha e a da medida
    cheia (Sauvola)."""
    cinza = _folha_com_reticula(fracao_da_foto)
    F._KS_GUARDADOS.clear()
    assert F._espessura_do_traco(cinza) is None, "a trava de 60% devia agir aqui"
    assert F.escolher_algoritmo_automatico(cinza) == _escolha_da_medida_cheia(cinza) \
        == F.ALGORITMO_SAUVOLA


def _tinta_cheia(cinza: np.ndarray) -> float:
    _lim, tinta = cv2.threshold(cinza, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return cv2.countNonZero(tinta) / float(tinta.size)


@pytest.mark.parametrize("diferenca, atalho_age", [
    (0.0065, True),     # Horas 11: 60,4% na copia reduzida, 59,7% na pagina inteira
    (0.014, True),      # a maior diferenca de verdade no acervo (Opus Majus 1)
    (0.222, False),     # Opus Majus 450: 96,5% x 74,3%
])
def test_o_atalho_so_age_com_as_tintas_parecidas(monkeypatch, diferenca, atalho_age):
    """O traco grosso (que o atalho resolveria sem a medida cheia) com a tinta
    da copia reduzida trocada pela da pagina inteira mais `diferenca`."""
    cheias = _sem_a_medida_guardada(monkeypatch)
    monkeypatch.setattr(F, "_tinta_da_copia_reduzida",
                        lambda cinza: _tinta_cheia(cinza) + diferenca)
    assert F.escolher_algoritmo_automatico(_folha(60)) == F.ALGORITMO_OTSU
    if atalho_age:
        assert cheias == [], "fez a medida de tamanho cheio com as tintas parecidas"
    else:
        assert cheias, "o atalho agiu com as tintas diferentes demais"


def test_a_tinta_da_copia_reduzida_e_a_da_medida_guardada():
    """_tinta_da_copia_reduzida reduz a folha do mesmo jeito que a medida do k
    (_medir_espessura_do_traco): mesma altura, mesma interpolacao, mesmo Otsu."""
    cinza = _folha_com_reticula(0.85)
    escala = F.ALTURA_PARA_MEDIR_TRACO / cinza.shape[0]
    reduzida = cv2.resize(cinza, (int(cinza.shape[1] * escala), int(cinza.shape[0] * escala)),
                          interpolation=cv2.INTER_AREA)
    assert F._tinta_da_copia_reduzida(cinza) == pytest.approx(_tinta_cheia(reduzida))
    assert F._tinta_da_copia_reduzida(cinza) > 0.8 > 0.5 > _tinta_cheia(cinza)


# A Horas 11 de verdade, como o programa a entrega ao filtro (analise, corte,
# endireitar; "Limpar a folha" desligado, a 300 DPI): 5633 x 3684 pontos, 60,4%
# de tinta na copia reduzida e 59,7% na pagina inteira. Pula se a pasta
# gabarito/paginas nao existir (ela fica fora do git; numa copia de trabalho
# do git worktree, aponte EDITOR_IMPRESSAO_GABARITO para a pasta do gabarito).
PAGINAS_DO_GABARITO = Path(os.environ.get(
    "EDITOR_IMPRESSAO_GABARITO",
    Path(__file__).resolve().parent.parent / "gabarito")) / "paginas"


@pytest.mark.skipif(not (PAGINAS_DO_GABARITO / "horas_p011.pdf").is_file(),
                    reason="gabarito/paginas ausente nesta copia")
def test_horas_11_de_verdade_continua_no_atalho(monkeypatch):
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto, renderizar_pagina
    from modelos import Projeto

    pdf = PAGINAS_DO_GABARITO / "horas_p011.pdf"
    projeto = analisar_projeto(Projeto(caminho_entrada=str(pdf), nome=pdf.stem))
    projeto.limpar = False
    doc = abrir_pdf(str(pdf))
    try:
        img, _mono = renderizar_pagina(doc, projeto, projeto.paginas[0],
                                       dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    cinza = F._cinza_para_binarizar(img)
    F._KS_GUARDADOS.clear()
    assert F._espessura_do_traco(cinza) is None, "a trava de 60% devia agir na Horas 11"

    cheias = []
    esqueleto = F._esqueleto

    def contar(tinta):
        if tinta.shape[0] > F.ALTURA_PARA_MEDIR_TRACO:
            cheias.append(tinta.shape)
        return esqueleto(tinta)

    monkeypatch.setattr(F, "_esqueleto", contar)
    assert F.escolher_algoritmo_automatico(cinza) == F.ALGORITMO_OTSU
    assert cheias == [], "a Horas 11 voltou a pagar a medida de tamanho cheio (~9,5 s)"
