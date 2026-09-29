"""O seletor de gravura do ScanTailor Advanced, compilado (item 1.2 da Fase 1).

Testes de máquina:
- DLL ausente ou quebrada: o módulo diz "indisponível" e não derruba nada;
- página sintética: a mancha de meio-tom vira gravura, a letra não;
- cópia fiel: as funções do ScanTailor em st_gravura.cpp são as do original;
- régua: na página do teste de 24/09, a DLL dá a mesma máscara que o próprio
  ScanTailor gravou (só roda neste PC, onde a pasta gabarito/ existe).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pytest

from core import gravura_scantailor as gs

RAIZ = Path(__file__).resolve().parent.parent
LIGACAO = RAIZ / "terceiros" / "scantailor-advanced" / "ligacao" / "st_gravura.cpp"
REFERENCIA = RAIZ / "terceiros" / "scantailor-advanced" / "referencia" / "OutputGenerator.cpp"
GEOMETRIA = RAIZ / "tests" / "dados" / "gravura_scantailor_24_09.json"
GABARITO = RAIZ / "gabarito" / "scantailor-24-09"

precisa_da_dll = pytest.mark.skipif(not gs.disponivel(), reason="DLL do ScanTailor não compilada")


def pagina_sintetica(dpi: int = 150) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Página branca com linhas de "letras" e uma gravura de meio-tom.

    Devolve (imagem BGR, onde está a gravura, onde está a escrita).
    """
    escala = dpi / 150
    altura, largura = int(1650 * escala), int(1275 * escala)   # 11 x 8,5 polegadas
    img = np.full((altura, largura, 3), 236, np.uint8)
    gravura = np.zeros((altura, largura), bool)
    escrita = np.zeros((altura, largura), bool)
    # gravura: retângulo de tom médio com textura (hachura clara/escura)
    y0, y1, x0, x1 = int(700 * escala), int(1250 * escala), int(250 * escala), int(1000 * escala)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    tom = 110 + 40 * np.sin(xx / (3.0 * escala)) * np.cos(yy / (5.0 * escala))
    img[y0:y1, x0:x1] = tom.astype(np.uint8)[..., None]
    gravura[y0:y1, x0:x1] = True
    # escrita: blocos pretos do tamanho de letra, em linhas, acima da gravura
    for linha in range(12):
        y = int((150 + linha * 40) * escala)
        for letra in range(40):
            x = int((150 + letra * 24) * escala)
            img[y:y + int(18 * escala), x:x + int(12 * escala)] = 20
            escrita[y:y + int(18 * escala), x:x + int(12 * escala)] = True
    return img, gravura, escrita


# ------------------------------------------------------------- sem a DLL

def test_dll_ausente_devolve_indisponivel(tmp_path):
    detector = gs.DetectorGravuraScanTailor(tmp_path / "nao_existe.dll")
    resultado = detector.detectar(np.full((100, 80, 3), 200, np.uint8), 150)
    assert not resultado.disponivel
    assert resultado.mascara is None
    assert "não foi encontrado" in resultado.motivo
    assert not detector.disponivel


def test_dll_quebrada_devolve_indisponivel(tmp_path):
    falsa = tmp_path / "st_gravura.dll"
    falsa.write_bytes(b"isto nao e uma DLL")
    detector = gs.DetectorGravuraScanTailor(falsa)
    resultado = detector.detectar(np.full((100, 80), 200, np.uint8), 150)
    assert not resultado.disponivel
    assert "não abriu" in resultado.motivo
    assert resultado.detalhe_tecnico


def test_figuras_pelo_scantailor_sem_dll_usa_a_reserva(tmp_path, monkeypatch):
    monkeypatch.setattr(gs, "_padrao", gs.DetectorGravuraScanTailor(tmp_path / "nao_existe.dll"))
    img = np.full((60, 40, 3), 200, np.uint8)
    reserva = gs.figuras_pelo_scantailor(img, reserva=lambda i: np.full(i.shape[:2], 0.5, np.float32))
    assert reserva.shape == (60, 40) and float(reserva.max()) == 0.5
    sem_reserva = gs.figuras_pelo_scantailor(img)
    assert sem_reserva.dtype == np.float32 and float(sem_reserva.max()) == 0.0


@precisa_da_dll
def test_entrada_invalida_nao_derruba():
    for ruim in (np.zeros((10, 10, 3), np.float32), np.zeros((0, 5, 3), np.uint8), np.zeros((5, 5, 2), np.uint8)):
        resultado = gs.detectar_gravura(ruim, 150)
        assert not resultado.disponivel and resultado.motivo
    assert not gs.detectar_gravura(np.zeros((10, 10), np.uint8), 0).disponivel


# ------------------------------------------------------------- com a DLL

@precisa_da_dll
def test_origem_diz_de_onde_veio():
    assert "v1.2.1" in gs.origem()


@precisa_da_dll
@pytest.mark.parametrize("dpi", [150, 300])
def test_pagina_sintetica_acha_a_gravura_e_nao_a_letra(dpi):
    img, gravura, escrita = pagina_sintetica(dpi)
    resultado = gs.detectar_gravura(img, dpi)
    assert resultado.disponivel, resultado.motivo
    m = resultado.mascara
    assert m.shape == img.shape[:2] and m.dtype == bool
    assert m[gravura].mean() > 0.95
    assert m[escrita].mean() < 0.02


@precisa_da_dll
def test_cinza_bgr_e_rgb_dao_a_mesma_mascara():
    img, _, _ = pagina_sintetica(150)
    bgr = gs.detectar_gravura(img, 150).mascara
    rgb = gs.detectar_gravura(np.ascontiguousarray(img[..., ::-1]), 150, ordem="RGB").mascara
    cinza = gs.detectar_gravura(np.ascontiguousarray(img[..., 0]), 150).mascara
    assert np.array_equal(bgr, rgb)
    assert np.array_equal(bgr, cinza)


@precisa_da_dll
def test_forma_desligada_e_retangular():
    img, gravura, _ = pagina_sintetica(150)
    assert not gs.detectar_gravura(img, 150, forma="desligada").mascara.any()
    ret = gs.detectar_gravura(img, 150, forma="retangular").mascara
    assert ret[gravura].mean() > 0.95


@precisa_da_dll
def test_figuras_pelo_scantailor_tem_a_assinatura_das_camadas():
    img, gravura, _ = pagina_sintetica(150)
    peso = gs.figuras_pelo_scantailor(img)
    assert peso.dtype == np.float32 and peso.shape == img.shape[:2]
    assert set(np.unique(peso)).issubset({0.0, 1.0})
    assert peso[gravura].mean() > 0.95


# ------------------------------------------------------------- cópia fiel

def test_funcoes_copiadas_sem_mudanca():
    """Cada bloco entre as marcas COPIADO SEM MUDANCA é idêntico às linhas do original."""
    ligacao = LIGACAO.read_text(encoding="utf-8").splitlines()
    original = REFERENCIA.read_text(encoding="utf-8").splitlines()
    blocos = 0
    for i, linha in enumerate(ligacao):
        achado = re.match(r"// ===== COPIADO SEM MUDANCA \(linhas (\d+)-(\d+)\) =====", linha)
        if not achado:
            continue
        a, b = int(achado.group(1)), int(achado.group(2))
        fim = ligacao.index("// ===== FIM DO COPIADO =====", i)
        assert ligacao[i + 1:fim] == original[a - 1:b], f"bloco {a}-{b} mudou"
        blocos += 1
    assert blocos == 7


# ------------------------------------------------------------- a régua

@precisa_da_dll
@pytest.mark.skipif(not (GABARITO / "palatino_p005.png").is_file(), reason="gabarito só existe neste PC")
def test_mesma_mascara_que_o_scantailor_no_palatino_5():
    """Refaz o que o ScanTailor fez em 24/09 (mesma rotação, escala e retângulo de
    trabalho, medidos pelo conferir_gravura_scantailor.py) e compara ponto a ponto
    com a máscara que o próprio ScanTailor gravou."""
    import cv2

    geometria = json.loads(GEOMETRIA.read_text(encoding="utf-8"))["palatino_p005"]
    entrada = cv2.imread(str(GABARITO / "palatino_p005.png"), cv2.IMREAD_COLOR)
    resultado = gs.detectar_como_no_scantailor(
        entrada, geometria["dpi_saida"], geometria["transformacao"], geometria["retangulo_trabalho"])
    assert resultado.disponivel, resultado.motivo
    x, y, w, h = geometria["retangulo_trabalho"]
    cx, cy, cw, ch = geometria["retangulo_conteudo"]
    nossa = resultado.mascara[cy - y:cy - y + ch, cx - x:cx - x + cw]
    ok, pilha = cv2.imreadmulti(str(GABARITO / "out" / "cache" / "automask" / "palatino_p005.tif"),
                                flags=cv2.IMREAD_GRAYSCALE)
    dele = pilha[0][cy:cy + ch, cx:cx + cw] > 0
    uniao = np.logical_or(nossa, dele).sum()
    iou = np.logical_and(nossa, dele).sum() / uniao
    assert iou >= 0.99, iou
