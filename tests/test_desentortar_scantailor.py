"""O desentortar do ScanTailor (item 2.12 da Fase 2, 21/10/2026).

Testes de máquina (o "ficou melhor ou pior" é teste de olho, do Samuel):
- a cola (desentortar.cpp) copia as funções do OutputGenerator.cpp e o
  Utils::rotate sem mudar uma letra; os arquivos do src/dewarping estão entre
  os conferidos pela soma (tests/test_st_ferramentas.py confere as somas);
- os ajustes de fábrica são os do ScanTailor (lidos dos próprios .h dele);
- DE FÁBRICA NADA MUDA: o modo de fábrica é "desligado", e desligado o passo
  devolve a MESMA imagem, sem conta nenhuma (a prova nas páginas-gabarito
  está em relatorios/fase2-itens/2.12/);
- ligado, numa página de mentira com as linhas curvas perto da lombada, as
  linhas saem retas; cinza e colorida; entrada ruim e DLL ausente não derrubam.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import desentortar_scantailor as ds
from core import st_ferramentas as st
from modelos import ConfigPagina

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
LIGACAO = TERCEIROS / "ligacao-ferramentas" / "desentortar.cpp"
REFERENCIAS = {
    None: TERCEIROS / "referencia" / "OutputGenerator.cpp",
    "Utils.cpp": TERCEIROS / "referencia" / "output" / "Utils.cpp",
}
# Soma SHA-256 (sem o CR) de src/core/filters/output/Utils.cpp do ScanTailor
# v1.2.1 (git show v1.2.1:src/core/filters/output/Utils.cpp).
SOMA_DO_UTILS = "0ef0ea826a6730666ec44097c833556bb607c57128cbc9c2b1f2f4b11c08c761"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


# ------------------------------------------------------------- cópia fiel

def test_funcoes_copiadas_sem_mudanca():
    """Cada bloco entre as marcas COPIADO SEM MUDANCA é idêntico às linhas do original."""
    ligacao = LIGACAO.read_text(encoding="utf-8").splitlines()
    blocos = 0
    for i, linha in enumerate(ligacao):
        achado = re.match(r"// ===== COPIADO SEM MUDANCA \((?:(\S+), )?linhas (\d+)-(\d+)\) =====", linha)
        if not achado:
            continue
        original = REFERENCIAS[achado.group(1)].read_text(encoding="utf-8").splitlines()
        a, b = int(achado.group(2)), int(achado.group(3))
        fim = ligacao.index("// ===== FIM DO COPIADO =====", i)
        assert ligacao[i + 1:fim] == original[a - 1:b], f"bloco {achado.group(1) or ''} {a}-{b} mudou"
        blocos += 1
    assert blocos == 7


def test_a_referencia_do_utils_e_a_do_scantailor():
    texto = (TERCEIROS / "referencia" / "output" / "Utils.cpp").read_bytes().replace(b"\r", b"")
    assert hashlib.sha256(texto).hexdigest() == SOMA_DO_UTILS


def test_os_arquivos_do_desentortar_estao_entre_os_conferidos():
    """Todo o src/dewarping, o math/spfit e o math/adiff vieram, com a soma."""
    somas = (TERCEIROS / "somas-v1.2.1.txt").read_text(encoding="utf-8")
    for pasta in ("dewarping", "math/spfit", "math/adiff"):
        arquivos = sorted((TERCEIROS / "src" / pasta).glob("*.*"))
        assert arquivos, pasta
        for arq in arquivos:
            assert f"src/{pasta}/{arq.name}" in somas, arq
    assert len(list((TERCEIROS / "src" / "dewarping").glob("*.*"))) == 22


# ------------------------------------------------------------- os de fábrica

def test_os_de_fabrica_sao_os_do_scantailor():
    """Profundidade 2,0 (de 1,0 a 3,0) e "desligado" com o endireitar depois
    ligado: os do próprio ScanTailor."""
    saida = TERCEIROS / "src" / "core" / "filters" / "output"
    dp = (saida / "DepthPerception.h").read_text(encoding="utf-8")

    def valor(nome):
        return float(re.search(nome + r"\(\) \{\s*return ([\d.]+);", dp).group(1))

    assert valor("defaultValue") == ds.PROFUNDIDADE_DE_FABRICA
    assert valor("minValue") == ds.PROFUNDIDADE_MINIMA
    assert valor("maxValue") == ds.PROFUNDIDADE_MAXIMA
    do = (saida / "DewarpingOptions.h").read_text(encoding="utf-8")
    assert "DewarpingOptions(DewarpingMode mode = OFF, bool needPostDeskew = true)" in do
    assert "enum DewarpingMode { OFF, AUTO, MANUAL, MARGINAL };" in do
    assert ds.FABRICA == ds.DESLIGADO
    assert ds.ENDIREITAR_DEPOIS_DE_FABRICA is True
    assert ds._CODIGO_DO_MODO == {ds.AUTOMATICO: 1, ds.PELAS_MARGENS: 3}


def test_pagina_nova_vem_desligada():
    pagina = ConfigPagina(indice=0, folha=0)
    assert pagina.desentortar == ds.DESLIGADO
    assert not ds.ligado(pagina)


def test_modo_estranho_ou_sem_campo_fica_desligado():
    class Velha:  # projeto em memória de antes do item 2.12
        pass

    assert ds.modo_da_pagina(Velha()) == ds.DESLIGADO
    for estranho in (None, "", "AUTO", "manual", 1, True):
        assert ds.modo_valido(estranho) == ds.DESLIGADO


def test_desligado_devolve_a_mesma_imagem_sem_conta():
    """O passo do preparo, desligado, devolve O MESMO objeto e nem abre a DLL."""
    class SemDLL:
        def funcao(self, nome):
            raise AssertionError("desligado não pode chamar a DLL")

    img = np.full((50, 40, 3), 200, np.uint8)
    pagina = ConfigPagina(indice=0, folha=0)
    assert ds.aplicar(img, pagina, 300, biblioteca=SemDLL()) is img


def test_lado_vem_da_metade():
    assert ds.lado_da_pagina(ConfigPagina(indice=0, folha=0, metade="inteira")) == 0
    assert ds.lado_da_pagina(ConfigPagina(indice=0, folha=0, metade="esquerda")) == 1
    assert ds.lado_da_pagina(ConfigPagina(indice=0, folha=0, metade="direita")) == 2


# ------------------------------------------------------------- ligado

def pagina_curva(altura: int = 2100, largura: int = 1500, curva: int = 60) -> np.ndarray:
    """Página de mentira a 300 DPI: 40 linhas de "letras" (retângulos escuros)
    que descem `curva` pontos perto da beirada direita (a lombada), como uma
    página direita de livro aberto no scanner."""
    img = np.full((altura, largura, 3), 235, np.uint8)
    rng = np.random.default_rng(1)
    for k in range(40):
        y0 = 200 + k * 42
        x = 150
        while x < largura - 150:
            w = int(rng.integers(12, 30))
            t = max(0.0, (x - (largura - 500)) / 350.0)
            dy = int(curva * t * t)
            cv2.rectangle(img, (x, y0 + dy), (x + w, y0 + dy + 22), (40, 40, 40), -1)
            x += w + int(rng.integers(6, 14))
    return img


def _centros_das_linhas(tinta_da_faixa: np.ndarray) -> list[float]:
    """O centro (y) de cada linha de texto numa faixa vertical da página."""
    perfil = tinta_da_faixa.sum(axis=1)
    n, rotulos = cv2.connectedComponents((perfil > 5).astype(np.uint8).reshape(-1, 1))
    ys = np.arange(len(perfil))
    centros = []
    for r in range(1, n):
        faixa = rotulos.ravel() == r
        centros.append(float((ys[faixa] * perfil[faixa]).sum() / perfil[faixa].sum()))
    return centros


def queda_das_linhas(img: np.ndarray) -> float:
    """Quanto as linhas descem (em pontos) da parte reta (x 150-500) até a
    lombada (x 1300-1330): a mediana da diferença do centro de tinta, linha a
    linha (a k-ésima linha de uma faixa com a k-ésima da outra). Linhas retas
    = perto de 0. Se as duas faixas não tiverem o mesmo número de linhas, a
    medida não vale (devolve infinito)."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tinta = (cinza < 128).astype(np.float64)
    retas = _centros_das_linhas(tinta[:, 150:500])
    curvas = _centros_das_linhas(tinta[:, 1300:1330])
    if len(retas) != len(curvas) or not retas:
        return float("inf")
    return float(np.median(np.array(curvas) - np.array(retas)))


def test_a_pagina_de_mentira_tem_mesmo_as_linhas_curvas():
    assert queda_das_linhas(pagina_curva()) > 25
    assert abs(queda_das_linhas(pagina_curva(curva=0))) < 3


@precisa_da_dll
def test_automatico_deixa_as_linhas_retas():
    img = pagina_curva()
    antes = img.copy()
    r = ds.desentortar(img, 300, ds.AUTOMATICO, lado=2)
    assert r.disponivel, r.motivo
    assert r.achou_curvas
    assert r.imagem.shape == img.shape and r.imagem.dtype == np.uint8
    assert np.array_equal(img, antes)  # não mexe na entrada
    assert queda_das_linhas(img) > 25
    assert abs(queda_das_linhas(r.imagem)) < 10


@precisa_da_dll
def test_automatico_pela_pagina_no_passo_do_preparo():
    img = pagina_curva()
    pagina = ConfigPagina(indice=0, folha=0, metade="direita")
    pagina.desentortar = ds.AUTOMATICO
    saida = ds.aplicar(img, pagina, 300)
    assert saida is not img
    assert abs(queda_das_linhas(saida)) < 10


@precisa_da_dll
def test_pelas_margens_roda_e_devolve_do_mesmo_tamanho():
    img = pagina_curva()
    r = ds.desentortar(img, 300, ds.PELAS_MARGENS, lado=2)
    assert r.disponivel, r.motivo
    assert r.imagem.shape == img.shape


@precisa_da_dll
def test_cinza_imagem_nao_contigua_e_largura_impar():
    img = pagina_curva(largura=1501)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r = ds.desentortar(cinza, 300, ds.AUTOMATICO, lado=2)
    assert r.disponivel, r.motivo
    assert r.imagem.shape == cinza.shape and r.imagem.ndim == 2
    pedaco = img[:, :1499]  # não contígua
    r2 = ds.desentortar(pedaco, (300, 300), ds.AUTOMATICO, lado=2)
    assert r2.disponivel and r2.imagem.shape == pedaco.shape


@precisa_da_dll
def test_pagina_em_branco_nao_quebra():
    branca = np.full((800, 600, 3), 240, np.uint8)
    r = ds.desentortar(branca, 300, ds.AUTOMATICO)
    assert r.disponivel, r.motivo
    assert not r.achou_curvas


@pytest.mark.parametrize("img, dpi, modo, extra", [
    (np.zeros((10, 10, 4), np.uint8), 300, ds.AUTOMATICO, {}),
    (np.zeros((10, 10), np.float32), 300, ds.AUTOMATICO, {}),
    (np.zeros((100, 100), np.uint8), 0, ds.AUTOMATICO, {}),
    (np.zeros((100, 100), np.uint8), 300, ds.DESLIGADO, {}),
    (np.zeros((100, 100), np.uint8), 300, "manual", {}),
    (np.zeros((100, 100), np.uint8), 300, ds.AUTOMATICO, {"lado": 5}),
    (np.zeros((100, 100), np.uint8), 300, ds.AUTOMATICO, {"profundidade": 4.0}),
    (np.zeros((100, 100), np.uint8), 5, ds.AUTOMATICO, {}),
])
def test_entrada_ruim_nao_chega_a_dll(img, dpi, modo, extra):
    class SemDLL:
        def funcao(self, nome):
            raise AssertionError("não devia chegar à DLL")

    r = ds.desentortar(img, dpi, modo, biblioteca=SemDLL(), **extra)
    assert not r.disponivel and r.motivo


def test_sem_a_dll_a_pagina_sai_como_veio(monkeypatch):
    anotados = []
    monkeypatch.setattr(ds.st, "anotar_no_erros_log", lambda *a: anotados.append(a))
    monkeypatch.setattr(ds, "_AVISADOS", set())
    sem = st.BibliotecaScanTailor(RAIZ / "nao-existe" / "st_ferramentas.dll")
    img = pagina_curva(altura=600, largura=500, curva=0)
    pagina = ConfigPagina(indice=0, folha=0)
    pagina.desentortar = ds.AUTOMATICO
    assert ds.aplicar(img, pagina, 300, biblioteca=sem) is img
    assert len(anotados) == 1  # vai ao erros.log, uma vez
    ds.aplicar(img, pagina, 300, biblioteca=sem)
    assert len(anotados) == 1
