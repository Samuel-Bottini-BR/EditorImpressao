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


# ------------------------------------------------------------- no preparo da página

def _livro(ordem: str, desentortar: str):
    from core import pipeline
    from modelos import ConfigFolha, Projeto

    pipeline._GEOMETRIAS.clear()
    projeto = Projeto(caminho_entrada="x.pdf", qualidade_dpi=300, cortar_bordas=False,
                      endireitar=False, ordem_do_preparo=ordem)
    folha = ConfigFolha(indice=0)
    pagina = ConfigPagina(indice=0, folha=0, metade="inteira")
    pagina.desentortar = desentortar
    projeto.folhas, projeto.paginas = [folha], [pagina]
    return projeto, folha, pagina


@pytest.mark.parametrize("ordem", ["endireitar_antes", "cortar_antes"])
def test_desligado_o_preparo_sai_como_sempre(ordem):
    from core import pipeline

    img = pagina_curva()
    projeto, folha, pagina = _livro(ordem, ds.DESLIGADO)
    saida, _ = pipeline.preparar_metade_e_geometria(img, folha, pagina, projeto, dpi=300)
    assert np.array_equal(saida, img)


@precisa_da_dll
@pytest.mark.parametrize("ordem", ["endireitar_antes", "cortar_antes"])
def test_ligado_o_preparo_desentorta_nas_duas_ordens(ordem):
    from core import pipeline

    img = pagina_curva()
    projeto, folha, pagina = _livro(ordem, ds.AUTOMATICO)
    pagina.metade = "inteira"
    saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert saida.shape == img.shape
    assert abs(queda_das_linhas(saida)) < 10


def test_a_marcacao_de_gravura_e_refeita_so_com_o_desentortar_ligado():
    """Com o desentortar ligado o detector vê outra página: a assinatura muda.
    Desligado, é a de sempre (nenhum livro já começado refaz a marcação)."""
    from core import pipeline

    projeto, _, pagina = _livro("endireitar_antes", ds.DESLIGADO)
    de_sempre = pipeline._assinatura_da_gravura_da_pagina(projeto, pagina)
    assert ds.SUFIXO_DA_GRAVURA not in de_sempre
    pagina.desentortar = ds.AUTOMATICO
    ligado = pipeline._assinatura_da_gravura_da_pagina(projeto, pagina)
    assert ligado == de_sempre + ds.SUFIXO_DA_GRAVURA + ds.AUTOMATICO
    pagina.desentortar = ds.PELAS_MARGENS
    assert pipeline._assinatura_da_gravura_da_pagina(projeto, pagina) != ligado


def test_o_campo_vai_e_volta_do_arquivo_e_o_antigo_abre_desligado():
    from modelos import Projeto

    projeto, _, pagina = _livro("endireitar_antes", ds.PELAS_MARGENS)
    dados = projeto.para_dicionario()
    assert Projeto.de_dicionario(dados).paginas[0].desentortar == ds.PELAS_MARGENS
    dados = projeto.para_dicionario()  # de_dicionario consome o dicionario
    for p in dados["paginas"]:
        p.pop("desentortar")
    assert Projeto.de_dicionario(dados).paginas[0].desentortar == ds.DESLIGADO


# ------------------------------------------------------------- o corte é só uma medida (22/10/2026)
#
# Escolha do Samuel na Central (22/10/2026, pergunta "a-212-desentortar"): "A —
# Como o ScanTailor: cortar uma vez só, no fim". O desentortar recebe a página
# endireitada SEM o corte (com o papel do scan em volta) e a caixa do corte; a
# DLL (versão 8) devolve a página já do tamanho do corte.

def _caixa_rente(img, folga=12):
    """O corte rente de 1 mm (12 pontos a 300 DPI) em volta da tinta, como o
    corte automático do programa: (x0, y0, x1, y1)."""
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(cinza < 128)
    return (int(xs.min()) - folga, int(ys.min()) - folga, int(xs.max()) + folga + 1, int(ys.max()) + folga + 1)


def tinta_que_ficou_no_lugar(antes: np.ndarray, depois: np.ndarray, tolerancia: int = 4) -> float:
    """A fração da tinta de `antes` que continua tinta em `depois`, aceitando
    `tolerancia` pontos de desvio. Numa página RETA, o desentortar não tem o
    que mudar: perto de 1,0 = as letras ficaram onde estavam."""
    a = cv2.cvtColor(antes, cv2.COLOR_BGR2GRAY) < 128
    b = cv2.cvtColor(depois, cv2.COLOR_BGR2GRAY) < 128
    lado = 2 * tolerancia + 1
    b = cv2.dilate(b.astype(np.uint8), np.ones((lado, lado), np.uint8)) > 0
    return float((a & b).sum() / a.sum())


@precisa_da_dll
def test_a_saida_tem_o_tamanho_do_corte():
    img = pagina_curva()
    x0, y0, x1, y1 = _caixa_rente(img)
    for modo in (ds.AUTOMATICO, ds.PELAS_MARGENS):
        r = ds.desentortar(img, 300, modo, lado=2, corte=(x0, y0, x1 - x0, y1 - y0),
                           conteudo=ds.caixa_do_conteudo(img, (x0, y0, x1, y1), 300))
        assert r.disponivel, r.motivo
        assert r.imagem.shape == (y1 - y0, x1 - x0, 3)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    r = ds.desentortar(cinza, 300, ds.AUTOMATICO, lado=2, corte=(x0, y0, x1 - x0, y1 - y0))
    assert r.disponivel and r.imagem.shape == (y1 - y0, x1 - x0)


@pytest.mark.parametrize("corte", [(-1, 0, 10, 10), (0, 0, 0, 10), (90, 0, 20, 10), (0, 95, 10, 10)])
def test_corte_fora_da_pagina_nao_chega_a_dll(corte):
    class SemDLL:
        def funcao(self, nome):
            raise AssertionError("não devia chegar à DLL")

    r = ds.desentortar(np.zeros((100, 100), np.uint8), 300, ds.AUTOMATICO, corte=corte, biblioteca=SemDLL())
    assert not r.disponivel and r.motivo


def test_caixa_do_conteudo_e_a_da_tinta_sem_o_que_encosta_na_beirada():
    """A caixa do conteúdo (m_contentRect) é a da tinta dentro do corte, como a
    do ScanTailor; a faixa preta do scanner e a sombra da lombada (que
    encostam na beirada do corte) ficam de fora."""
    img = pagina_curva(curva=0)
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ys, xs = np.where(cinza < 128)
    tinta = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    img[:80, :] = 10  # faixa preta do scanner, em cima
    img[:, -40:] = 10  # sombra da lombada, à direita
    x, y, w, h = ds.caixa_do_conteudo(img, (0, 0, img.shape[1], img.shape[0]), 300)
    assert abs(x - tinta[0]) <= 6 and abs(y - tinta[1]) <= 6
    assert abs(x + w - tinta[2]) <= 6 and abs(y + h - tinta[3]) <= 6
    branca = np.full((300, 300, 3), 240, np.uint8)  # sem tinta: o próprio corte
    assert ds.caixa_do_conteudo(branca, (10, 20, 210, 220), 300) == (10, 20, 200, 200)


@precisa_da_dll
def test_reversao_pagina_reta_com_corte_rente_nao_mexe_nas_letras():
    """REVERSÃO do defeito de 22/10/2026 (item 2.12, Righetti 96 e Cursus 151):
    o desentortar recebia a página JÁ CORTADA rente (1 mm) e tomava o corte
    inteiro como caixa do conteúdo; sem papel em volta, ele redesenhava a
    página até numa página reta, apertando e empurrando as letras (no Righetti
    96 o começo das linhas e o cabeçalho sumiam). Agora o corte é só uma
    medida, como no ScanTailor: a página vai com o papel em volta e a caixa do
    conteúdo é a da tinta. Medida: numa página RETA, com o corte rente, a tinta
    tem de ficar no lugar (no código de antes: 0,971 da tinta; agora 0,996).
    Pelo caminho do programa (preparar_metade), nas duas ordens."""
    from core import pipeline
    from modelos import ConfigFolha, Projeto

    img = pagina_curva(curva=0)
    altura, largura = img.shape[:2]
    x0, y0, x1, y1 = _caixa_rente(img)
    for ordem in ("endireitar_antes", "cortar_antes"):
        pipeline._GEOMETRIAS.clear()
        projeto = Projeto(caminho_entrada="x.pdf", qualidade_dpi=300, cortar_bordas=True,
                          endireitar=False, ordem_do_preparo=ordem)
        folha = ConfigFolha(indice=0, dividir=False)  # a página direita já separada
        pagina = ConfigPagina(indice=0, folha=0, metade="direita")
        pagina.recorte = (x0 / largura, y0 / altura, (x1 - x0) / largura, (y1 - y0) / altura)
        projeto.folhas, projeto.paginas = [folha], [pagina]
        hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
        pagina.desentortar = ds.AUTOMATICO
        saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
        assert saida.shape == hoje.shape
        assert tinta_que_ficou_no_lugar(hoje, saida) > 0.99, ordem


def test_desligado_nao_passa_pelo_desentortar_nem_com_corte_e_giro(monkeypatch):
    """Desligado (o de fábrica), o preparo é o de sempre ponto por ponto: nem
    chega ao desentortar, com corte e com giro, nas duas ordens."""
    from core import pipeline
    from core.endireitar import rotacionar, rotacionar_e_cortar
    from core.recortar import caixa_em_pontos
    from modelos import ConfigFolha, Projeto

    def nao(*a, **k):
        raise AssertionError("desligado não pode chamar o desentortar")

    monkeypatch.setattr(ds, "aplicar_no_corte", nao)
    monkeypatch.setattr(ds, "aplicar", nao)
    img = pagina_curva(curva=0)
    recorte = (0.08, 0.08, 0.84, 0.84)
    for ordem in ("endireitar_antes", "cortar_antes"):
        pipeline._GEOMETRIAS.clear()
        projeto = Projeto(caminho_entrada="x.pdf", qualidade_dpi=300, cortar_bordas=True,
                          endireitar=True, ordem_do_preparo=ordem)
        folha = ConfigFolha(indice=0)
        pagina = ConfigPagina(indice=0, folha=0, metade="inteira")
        pagina.recorte, pagina.angulo_manual = recorte, 1.5
        projeto.folhas, projeto.paginas = [folha], [pagina]
        saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
        x0, y0, x1, y1 = caixa_em_pontos(img.shape, recorte)
        esperado = (rotacionar_e_cortar(img, 1.5, (x0, y0, x1, y1)) if ordem == "endireitar_antes"
                    else rotacionar(img[y0:y1, x0:x1], 1.5))
        assert np.array_equal(saida, esperado), ordem


@pytest.mark.parametrize("ordem", ["endireitar_antes", "cortar_antes"])
def test_ligado_sem_a_dll_sai_o_mesmo_corte_e_giro_de_sempre(monkeypatch, ordem):
    """Sem a DLL, o caminho do papel em volta devolve o corte da página reta:
    o mesmo corte e o mesmo giro do desligado (no livro antigo, girado em volta
    do centro do CORTE). Só os cantos que o giro trazia de fora mudam: antes
    branco, agora o papel de verdade."""
    from core import pipeline
    from modelos import ConfigFolha, Projeto

    monkeypatch.setattr(ds, "_AVISADOS", set())
    monkeypatch.setattr(ds.st, "anotar_no_erros_log", lambda *a: None)
    sem = st.BibliotecaScanTailor(RAIZ / "nao-existe" / "st_ferramentas.dll")
    monkeypatch.setattr(ds.st, "padrao", lambda: sem)
    img = pagina_curva(curva=0)
    img[:, :] = np.clip(img.astype(int) - 20, 0, 255).astype(np.uint8)  # papel cinza: o branco do giro aparece
    pipeline._GEOMETRIAS.clear()
    projeto = Projeto(caminho_entrada="x.pdf", qualidade_dpi=300, cortar_bordas=True,
                      endireitar=True, ordem_do_preparo=ordem)
    folha = ConfigFolha(indice=0)
    pagina = ConfigPagina(indice=0, folha=0, metade="inteira")
    pagina.recorte, pagina.angulo_manual = (0.08, 0.08, 0.84, 0.84), 2.0
    projeto.folhas, projeto.paginas = [folha], [pagina]
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    pagina.desentortar = ds.AUTOMATICO
    ligado = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=300)
    assert ligado.shape == hoje.shape
    miolo = (slice(60, -60), slice(60, -60))
    diferenca = np.abs(ligado[miolo].astype(int) - hoje[miolo].astype(int))
    assert diferenca.max() <= 2
    if ordem == "cortar_antes":  # o canto: antes o branco do giro, agora o papel
        assert hoje[2, 2].min() == 255 and ligado[2, 2].max() < 255


ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
MARIAL = ACERVO / "Marial de sermoens - Frei Balthasar Paez. (1).pdf"


@precisa_da_dll
@pytest.mark.skipif(not MARIAL.is_file(), reason="sem o acervo (só no PC do Samuel)")
def test_reversao_marial_41_pagina_reta_fica_como_esta(tmp_path):
    """REVERSÃO do defeito de 22/10/2026 num livro de verdade: Marial de
    sermoens, página 41 do PDF (página reta, duas colunas, notas na margem),
    livro novo de fábrica, desentortar automático. No código de antes (a página
    já cortada, o corte como caixa do conteúdo) o automático redesenhava a
    página e só 0,49 da tinta ficava no lugar; agora, com o papel em volta e a
    caixa do conteúdo da tinta, a página reta sai como está (1,00; aceito 0,95,
    com 6 pontos de tolerância)."""
    import fitz
    from core import pipeline
    from core.pdf_io import abrir_pdf, pagina_para_array
    from modelos import Projeto

    pdf = tmp_path / "marial_41.pdf"
    origem, novo = fitz.open(MARIAL), fitz.open()
    novo.insert_pdf(origem, from_page=40, to_page=40)
    novo.save(pdf)
    novo.close()
    origem.close()
    projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(pdf), nome="marial"))
    doc = abrir_pdf(str(pdf))
    try:
        pagina = projeto.paginas_ativas[0]
        folha = projeto.folhas[pagina.folha]
        img = pagina_para_array(doc, 0, dpi=projeto.qualidade_dpi)
    finally:
        doc.close()
    hoje = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
    pagina.desentortar = ds.AUTOMATICO
    saida = pipeline.preparar_metade(img, folha, pagina, projeto, dpi=projeto.qualidade_dpi)
    assert saida.shape == hoje.shape
    assert tinta_que_ficou_no_lugar(hoje, saida, tolerancia=6) > 0.95
