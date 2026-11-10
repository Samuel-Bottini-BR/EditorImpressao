"""Conserto CANDIDATO (nao aplicado no programa): so para medir e mostrar.

Em core.filtros._limpar_o_papel_de_verdade, o ponto so vai a branco se, alem das tres
perguntas de hoje (longe da letra, nao escuro, cor de papel), a VIZINHANCA dele for
papel: a mediana da luz numa janela de ~1/45 da pagina (feita na miniatura de 400 pontos,
como o fundo dos filtros) fica perto do nivel do papel. Na mancha do verso e no grao, a
vizinhanca e papel; na agua e no ceu de uma pintura, a vizinhanca e a propria pintura.

instalar() troca a funcao do modulo (so neste processo)."""
import os

import cv2
import numpy as np

from core import filtros as F

VIZINHANCA_DE_PAPEL = 0.80     # mediana em volta >= 80% do nivel do papel
LADO_DA_MINIATURA = 400
JANELA_FRACAO = 1 / 45

_real = F._limpar_o_papel_de_verdade
_pintar = F._pintar_de_branco


def vizinhanca_e_papel(original: np.ndarray) -> np.ndarray:
    cinza = F._para_cinza(original)
    nivel = F._percentil(cinza, F.BRANCO_PERCENTIL)
    h, w = cinza.shape
    esc = min(1.0, LADO_DA_MINIATURA / max(1, min(h, w)))
    peq = cv2.resize(cinza, (max(8, round(w * esc)), max(8, round(h * esc))), interpolation=cv2.INTER_AREA)
    k = max(3, int(round(max(peq.shape) * JANELA_FRACAO)) | 1)
    med = cv2.medianBlur(peq, k)
    med = cv2.resize(med, (w, h), interpolation=cv2.INTER_LINEAR)
    ok = med >= VIZINHANCA_DE_PAPEL * nivel
    if os.environ.get("CANDIDATO_V", "2") == "2" and original.ndim == 3:
        # versao 2: OU a area e de TRACO sobre papel (xilogravura, tabela, texto), pela mesma
        # medida da tentativa 20 (F._peso_de_traco): ali o papel entre os tracos continua indo a
        # branco, como hoje; so a area de TOM CONTINUO (pintura, foto) longe do papel fica de fora
        lab = cv2.cvtColor(original, cv2.COLOR_BGR2LAB)
        luz, fundo, nv = F._fundo_e_nivel(lab)
        ok |= F._peso_de_traco(luz, fundo, nv) >= 128
    return ok


def candidato(original, saida, dentro_da_gravura=False):
    if dentro_da_gravura:
        return _real(original, saida, dentro_da_gravura=True)
    pego = {}

    def anotar(img, mascara):
        pego["m"] = mascara

    F._pintar_de_branco = anotar
    try:
        _real(original, saida, dentro_da_gravura=False)
    finally:
        F._pintar_de_branco = _pintar
    if "m" not in pego:
        return saida
    limpa = saida.copy()
    _pintar(limpa, pego["m"] & vizinhanca_e_papel(original))
    return limpa


def instalar():
    F._limpar_o_papel_de_verdade = candidato
