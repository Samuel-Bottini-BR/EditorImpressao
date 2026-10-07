"""O dividir do ScanTailor na DLL comum (item 2.1 da Fase 2, 06/10/2026).

Testes de máquina:
- a "cola" copiada de ProjectPages.cpp (adviseNumberOfLogicalPages) é igual,
  letra por letra, ao original v1.2.1 (guardado em terceiros/.../referencia);
- os arquivos do page_split estão entre os conferidos pela soma
  (o teste geral de cópia fiel é tests/test_st_ferramentas.py);
- a função em C numa folha de mentira: folha deitada com a dobra no meio =
  duas páginas, no lugar da dobra; folha em pé = uma página; parâmetro errado
  não derruba nada;
- core/dividir_scantailor.py: a tradução para frações (meio da linha, sobra
  com a ponta que corta menos) e o "indisponível" sem a DLL;
- nas páginas-gabarito do D3 (se a pasta gabarito existir), os números que o
  programa de teste do D3 achou com o mesmo código (Siebmacher 9 a 82%, Opus
  Majus 256 a 50%): a DLL dá o mesmo que o ScanTailor deu lá.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import dividir_scantailor as ds
from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
COLA = TERCEIROS / "ligacao-ferramentas" / "dividir.cpp"
REFERENCIA = TERCEIROS / "referencia" / "ProjectPages.cpp"
GABARITO = RAIZ / "gabarito"

# SHA-256 de src/core/ProjectPages.cpp do ScanTailor Advanced v1.2.1 (commit
# 5eaac18), tirado do git do ScanTailor (fim de linha LF).
SHA256_PROJECTPAGES = "720493a758f8eb7ade6b41b494cbd0e8790c97c448ee3021e3772968adfbebde"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _sem_cr(caminho: Path) -> str:
    return caminho.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


# ------------------------------------------------------------- cópia fiel

def test_referencia_e_o_original():
    assert hashlib.sha256(_sem_cr(REFERENCIA).encode("utf-8")).hexdigest() == SHA256_PROJECTPAGES


def test_cola_copiada_sem_mudanca():
    """O trecho entre as marcas de dividir.cpp é igual às linhas 205-214 de ProjectPages.cpp."""
    cola = _sem_cr(COLA)
    trecho = re.search(r"// ---- COPIADO SEM MUDANCA[^\n]*\n(?:// [^\n]*\n)*(.*?)// ---- FIM DO TRECHO COPIADO",
                       cola, re.S)
    assert trecho, "marcas do trecho copiado sumiram de dividir.cpp"
    original = "\n".join(_sem_cr(REFERENCIA).split("\n")[204:214]) + "\n"
    assert trecho.group(1) == original


def test_page_split_esta_entre_os_conferidos():
    somas = (TERCEIROS / "somas-v1.2.1.txt").read_text(encoding="utf-8")
    for rel in ("PageLayoutEstimator.cpp", "PageLayoutEstimator.h", "VertLineFinder.cpp",
                "PageLayout.cpp", "PageLayout.h", "LayoutType.h"):
        assert f"src/core/filters/page_split/{rel}" in somas


# ------------------------------------------------------------- a DLL

def _folha_dupla(largura=1600, altura=1100, dobra=0.6):
    """Folha deitada com duas páginas de 'texto' e uma dobra escura em `dobra`."""
    img = np.full((altura, largura), 235, np.uint8)
    x_dobra = int(largura * dobra)
    for x0, x1 in ((80, x_dobra - 80), (x_dobra + 80, largura - 80)):
        for y in range(120, altura - 120, 36):
            for x in range(x0, x1 - 40, 70):
                img[y:y + 14, x:x + 50] = 30
    img[:, x_dobra - 6:x_dobra + 6] = 60     # a sombra da dobra, de cima a baixo
    return img


@precisa_da_dll
def test_folha_dupla_divide_na_dobra():
    r = ds.achar(_folha_dupla(dobra=0.6), 150, ds.MODO_AUTOMATICO)
    assert r.disponivel, r.motivo
    assert r.tipo == ds.TIPO_DUAS_PAGINAS
    assert ds.posicao_da_divisao(r) == pytest.approx(0.6, abs=0.02)


@precisa_da_dll
def test_folha_colorida_da_o_mesmo_que_cinza():
    cinza = _folha_dupla(dobra=0.45)
    cor = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    a = ds.achar(cinza, 150, ds.MODO_DUAS_PAGINAS)
    b = ds.achar(cor, 150, ds.MODO_DUAS_PAGINAS)
    assert a.disponivel and b.disponivel
    assert ds.posicao_da_divisao(a) == pytest.approx(ds.posicao_da_divisao(b), abs=1e-9)


@precisa_da_dll
def test_folha_em_pe_fica_uma_pagina():
    img = np.full((1600, 1100), 240, np.uint8)
    for y in range(150, 1450, 36):
        img[y:y + 14, 120:980] = 30
    r = ds.achar(img, 150, ds.MODO_AUTOMATICO)
    assert r.disponivel, r.motivo
    assert r.tipo in (ds.TIPO_SEM_CORTE, ds.TIPO_COM_SOBRA)
    assert ds.posicao_da_divisao(r) is None


@precisa_da_dll
def test_parametro_errado_nao_derruba():
    funcao = st.padrao().funcao("st_ferramentas_dividir")
    import ctypes
    tipo, n = ctypes.c_int(), ctypes.c_int()
    cortes = (ctypes.c_double * 8)()
    erro = ctypes.create_string_buffer(256)
    img = np.zeros((10, 10), np.uint8)
    codigo = funcao(img.ctypes.data, 10, 10, 10, 2, 150, 150, 0, ctypes.byref(tipo), ctypes.byref(n),
                    cortes, erro, len(erro))        # 2 canais: recusado
    assert codigo == st.ERRO_PARAMETRO
    assert b"parametros" in erro.value
    assert ds.achar(img, 150, modo=9).disponivel is False
    assert ds.achar(img, 0).disponivel is False


def test_sem_dll_fica_indisponivel(tmp_path):
    biblioteca = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    r = ds.achar(_folha_dupla(), 150, biblioteca=biblioteca)
    assert not r.disponivel
    assert r.motivo
    assert ds.posicao_da_divisao(r) is None and ds.sobra_da_folha(r) is None


# ------------------------------------------------------------- a tradução

def test_posicao_e_o_meio_da_linha_inclinada():
    r = ds.Resultado(ds.TIPO_DUAS_PAGINAS, (ds.Corte(0.48, 0.52),))
    assert ds.posicao_da_divisao(r) == pytest.approx(0.50)
    assert ds.posicao_da_divisao(ds.Resultado(ds.TIPO_SEM_CORTE)) is None


def test_sobra_fica_com_a_ponta_que_corta_menos():
    r = ds.Resultado(ds.TIPO_COM_SOBRA, (ds.Corte(0.10, 0.14), ds.Corte(0.85, 0.87)))
    assert ds.sobra_da_folha(r) == (0.10, 0.87)
    # beirada de menos de 0,5% nao conta; os dois lados "na beirada" = nada a cortar
    r = ds.Resultado(ds.TIPO_COM_SOBRA, (ds.Corte(0.0, 0.003), ds.Corte(0.998, 1.0)))
    assert ds.sobra_da_folha(r) is None
    r = ds.Resultado(ds.TIPO_COM_SOBRA, (ds.Corte(0.0, 0.0), ds.Corte(0.93, 0.94)))
    assert ds.sobra_da_folha(r) == (0.0, 0.94)


def test_jeito_valido():
    assert ds.jeito_valido("scantailor") == ds.JEITO_SCANTAILOR
    assert ds.jeito_valido(None) == ds.JEITO_PROGRAMA
    assert ds.jeito_valido("qualquer") == ds.JEITO_PROGRAMA


# ------------------------------------------------------------- gabarito (D3)

def _pagina(nome):
    lista = GABARITO / "lista.json"
    if not lista.is_file():
        pytest.skip("sem a pasta gabarito")
    info = json.loads(lista.read_text(encoding="utf-8"))["paginas"][nome]
    img = cv2.imread(str(GABARITO / info["png"]), cv2.IMREAD_COLOR)
    if img is None:
        pytest.skip(f"sem a imagem {info['png']}")
    return img, info["dpi_png"]


@precisa_da_dll
@pytest.mark.parametrize("nome, onde", [("siebmacher_p009", 0.82), ("opusmajus_p256", 0.50)])
def test_gabarito_igual_ao_d3(nome, onde):
    """O D3 (05/10, programa de teste fora do projeto, mesmo código) dividiu
    o Siebmacher 9 a 82% e o Opus Majus 256 a 50% (relatorios/
    fase2-geometria-d3-2026-10-05, tabela). A DLL tem de dar o mesmo."""
    img, dpi = _pagina(nome)
    r = ds.achar(img, dpi, ds.MODO_AUTOMATICO)
    assert r.tipo == ds.TIPO_DUAS_PAGINAS
    assert ds.posicao_da_divisao(r) == pytest.approx(onde, abs=0.01)
