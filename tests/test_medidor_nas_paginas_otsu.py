"""O medidor de forca do Preto e branco nas paginas de letra grossa (as que a
escolha automatica poe no Otsu com a borda do Sauvola), 02/10/2026.

Achado do verificador na conferencia dos consertos da conferencia 6
(relatorios/conferir/conferencia-6-consertos-2026-10-02/verificador/): depois
de 1b174e4, na Horas 47, o medidor no 0 ("mais fraco") devolvia a letra fina e
falhada que o Samuel recusou ("Ainda esta apagando as letras, o original esta
muito melhor para ler"), e no 100 ("mais escuro") algumas letras voltavam a
falhar ("nous", "Prechant"): o mais escuro saia mais claro que o meio.

O que estes testes protegem (teste de maquina):
- o medidor e COERENTE: em cada ponto da folha, o que e preto num valor do
  medidor continua preto em todo valor mais escuro (0 <= 25 <= 50 <= 75 <= 100);
- o "mais fraco" afina, mas nao picota: a letra nao volta a ser a do Otsu
  sozinho;
- o 50 (o padrao) e exatamente o resultado do conserto 1b174e4.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

from core import filtros as F
from tests.test_conferencia_6 import _pagina_com_moldura_escura_e_letra_clara

FORCAS = (0, 25, 50, 75, 100)


def _preto(binaria: np.ndarray) -> np.ndarray:
    return binaria == 0


def _monotono(resultados: dict[int, np.ndarray]) -> list[str]:
    """Os pares (mais fraco, mais escuro) em que algum ponto preto do mais
    fraco virou branco no mais escuro."""
    erros = []
    for fraco, escuro in zip(FORCAS, FORCAS[1:]):
        sumiu = _preto(resultados[fraco]) & ~_preto(resultados[escuro])
        if sumiu.any():
            erros.append(f"{fraco}->{escuro}: {int(sumiu.sum())} pontos clarearam")
    return erros


# --- folha sintetica (rapida) ----------------------------------------------


def test_o_medidor_e_coerente_na_folha_otsu():
    cinza, _traco = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    assert F.escolher_algoritmo_automatico(cinza) == F.ALGORITMO_OTSU
    resultados = {f: F.filtro_preto_e_branco(img, forca=f) for f in FORCAS}
    assert not _monotono(resultados), _monotono(resultados)
    tinta = [int(_preto(resultados[f]).sum()) for f in FORCAS]
    assert tinta[0] < tinta[2] < tinta[4], f"o medidor nao mexe: {tinta}"


def test_o_mais_fraco_nao_volta_a_letra_picotada():
    """Na folha sintetica o Otsu sozinho pega 61% do traco desenhado; no 50,
    91%. No 0 a letra pode afinar, mas fica longe do Otsu sozinho."""
    cinza, traco = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    so_otsu = float(_preto(F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU))[traco].mean())
    no_0 = float(_preto(F.filtro_preto_e_branco(img, forca=0))[traco].mean())
    no_50 = float(_preto(F.filtro_preto_e_branco(img, forca=50))[traco].mean())
    assert no_0 <= no_50
    assert no_0 >= 0.85, f"no 0 a letra saiu falhada: so {no_0:.0%} do traco"
    assert no_0 > so_otsu + 0.2


def test_o_50_e_o_resultado_do_conserto_de_1b174e4():
    """No 50 nada muda: o Otsu com a borda do Sauvola no k do meio."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    janela = F.janela_para_altura(cinza.shape[0])
    otsu = F._com_a_tinta_colorida(img, F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU))
    esperado = F._despeckle(
        F._otsu_com_a_borda_do_sauvola(cinza, otsu, janela, F.k_para_a_letra(cinza)),
        cinza.shape[0])
    assert np.array_equal(F.filtro_preto_e_branco(img, forca=50), esperado)


def test_o_mais_escuro_nao_puxa_risco_solto():
    """O "mais escuro" engrossa a letra; o risco fraco solto (a pauta a ponta
    seca do Graduale, a mancha), que nao encosta em letra, continua de fora."""
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    cinza[1080:1084, 300:700] = 185
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    escuro = F.filtro_preto_e_branco(img, forca=100)
    assert (escuro[1080:1084, 300:700] == 0).mean() < 0.05


def test_o_medidor_nao_mexe_no_otsu_escolhido_a_mao():
    cinza, _ = _pagina_com_moldura_escura_e_letra_clara()
    img = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    a_mao = [F.filtro_preto_e_branco(img, forca=f, algoritmo=F.ALGORITMO_OTSU) for f in (0, 50, 100)]
    assert np.array_equal(a_mao[0], a_mao[1]) and np.array_equal(a_mao[1], a_mao[2])


# --- a Horas 47 de verdade (pula se o gabarito nao estiver na maquina) ------

GABARITO = Path(__file__).resolve().parent.parent / "gabarito" / "paginas"
precisa_do_gabarito = pytest.mark.skipif(
    not (GABARITO / "horas_p047.pdf").is_file(), reason="gabarito ausente nesta maquina")

# o quadro de texto da Horas 47 desenhada a 300 DPI (6267 x 4267 pontos)
TEXTO_H47 = (slice(1620, 3540), slice(900, 3120))


def _pecas(binaria: np.ndarray) -> int:
    return cv2.connectedComponentsWithStats(cv2.bitwise_not(binaria), connectivity=8)[0] - 1


@precisa_do_gabarito
def test_horas_47_o_medidor_e_coerente_e_nao_picota():
    """Medido em 02/10/2026 no quadro de texto: Otsu sozinho (a letra
    recusada) 659 pecas; no 50, 435 (a letra cheia). Letra picotada = mais
    pecas. No 0 a letra afina (menos tinta) mas fica perto do 50 em pecas."""
    import fitz

    doc = fitz.open(str(GABARITO / "horas_p047.pdf"))
    pix = doc[0].get_pixmap(dpi=300, alpha=False)
    img = cv2.cvtColor(np.frombuffer(pix.samples, np.uint8)
                       .reshape(pix.height, pix.width, pix.n).copy(), cv2.COLOR_RGB2BGR)
    doc.close()
    resultados = {f: F.filtro_preto_e_branco(img, forca=f) for f in FORCAS}
    assert not _monotono(resultados), _monotono(resultados)

    cinza = F._cinza_para_binarizar(img)
    so_otsu = F._despeckle(
        F._com_a_tinta_colorida(img, F.binarizar(cinza, algoritmo=F.ALGORITMO_OTSU)),
        cinza.shape[0])
    p_otsu = _pecas(so_otsu[TEXTO_H47])
    p0, p50 = _pecas(resultados[0][TEXTO_H47]), _pecas(resultados[50][TEXTO_H47])
    assert p0 <= p50 + 0.25 * (p_otsu - p50), (p_otsu, p0, p50)
    t = [float(_preto(resultados[f][TEXTO_H47]).mean()) for f in FORCAS]
    assert t[0] < t[2] < t[4], t
