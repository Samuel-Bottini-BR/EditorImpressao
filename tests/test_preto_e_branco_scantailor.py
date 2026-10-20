"""Os dez jeitos de preto e branco do ScanTailor (item 2.8 da Fase 2, 20/10/2026).

Testes de máquina (o "ficou melhor ou pior" é teste de olho, do Samuel):
- a cola (saida.cpp) copia as funções do OutputGenerator.cpp sem mudar uma letra;
- os ajustes de fábrica são os do ScanTailor (lidos do próprio BlackWhiteOptions.cpp);
- o medidor "Força do preto" vira o ajuste do limiar dele (50 = 0, o de fábrica);
- os dez jeitos rodam e devolvem só preto e branco, do tamanho da página,
  com a letra preta e o papel branco; mais escuro no medidor = mais preto;
- entrada ruim não chega à DLL; sem a DLL, cai no "Automático", igual ponto a ponto;
- DE FÁBRICA NADA MUDA: a página nova vem com "Automático", e o "Automático"
  não passa pelo ScanTailor (a prova com imagens idênticas nas páginas-gabarito
  está em relatorios/fase2-itens/2.8/).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from core import filtros as F
from core import preto_e_branco_scantailor as pbst
from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
LIGACAO = TERCEIROS / "ligacao-ferramentas" / "saida.cpp"
REFERENCIA = TERCEIROS / "referencia" / "OutputGenerator.cpp"
OPCOES_DO_SCANTAILOR = TERCEIROS / "src" / "core" / "filters" / "output" / "BlackWhiteOptions.cpp"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def pagina_de_texto(largura: int = 600, altura: int = 400, colorida: bool = False) -> np.ndarray:
    """Papel com uma sombra forte de um lado (luz desigual: 235 na esquerda, 95
    na direita), linhas de "letras" (hastes com 30% da luz do papel em volta) e
    um pouco de grão - o caso de onde o ScanTailor tira o igualar a luz e as
    suavizações. Sempre a mesma (semente fixa)."""
    rng = np.random.default_rng(7)
    x = np.linspace(0, 1, largura, dtype=np.float32)
    img = (235 - 140 * x)[None, :].repeat(altura, 0)
    for y0, x0 in _hastes(largura):
        img[y0:y0 + 30, x0:x0 + 6] *= 0.3
    img = np.clip(img + rng.normal(0, 6, img.shape), 0, 255).astype(np.uint8)
    if colorida:
        return np.dstack([np.clip(img.astype(np.int16) - 10, 0, 255).astype(np.uint8), img, img])
    return img


def _hastes(largura: int = 600):
    return [(60 + linha * 80, 40 + k * 26) for linha in range(4) for k in range(20)
            if 40 + k * 26 + 6 <= largura]


def mascara_das_letras(forma) -> np.ndarray:
    letra = np.zeros(forma[:2], bool)
    for y0, x0 in _hastes(forma[1]):
        letra[y0:y0 + 30, x0:x0 + 6] = True
    return letra


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
    assert blocos == 8


def test_os_arquivos_do_scantailor_estao_entre_os_conferidos():
    """Os arquivos trazidos para o 2.8 têm a soma do original (o teste geral,
    tests/test_st_ferramentas.py, confere as somas)."""
    somas = (TERCEIROS / "somas-v1.2.1.txt").read_text(encoding="utf-8")
    for rel in ("src/imageproc/Binarize.cpp", "src/imageproc/SavGolFilter.cpp",
                "src/imageproc/SavGolKernel.cpp", "src/core/filters/output/BlackWhiteOptions.cpp",
                "src/core/filters/output/BlackWhiteOptions.h"):
        assert rel in somas, rel


# ------------------------------------------------------------- os de fábrica

def test_os_de_fabrica_sao_os_do_scantailor():
    """Os números de pbst.FABRICA são os do construtor de BlackWhiteOptions do ScanTailor."""
    texto = OPCOES_DO_SCANTAILOR.read_text(encoding="utf-8")
    construtor = texto[texto.index("BlackWhiteOptions::BlackWhiteOptions()"):]
    construtor = construtor[:construtor.index("{}")]

    def valor(campo):
        return re.search(rf"{campo}\(([^)]*)\)", construtor).group(1)

    assert int(valor("m_thresholdAdjustment")) == 0
    assert valor("m_savitzkyGolaySmoothingEnabled") == "true" and pbst.FABRICA.savitzky_golay
    assert valor("m_morphologicalSmoothingEnabled") == "true" and pbst.FABRICA.morfologica
    assert valor("m_normalizeIllumination") == "true" and pbst.FABRICA.normalizar
    assert int(valor("m_windowSize")) == pbst.FABRICA.janela == 200
    assert float(valor("m_sauvolaCoef")) == pbst.FABRICA.coef_sauvola
    assert float(valor("m_wolfCoef")) == pbst.FABRICA.coef_wolf
    assert int(valor("m_wolfLowerBound")) == pbst.FABRICA.wolf_minimo
    assert int(valor("m_wolfUpperBound")) == pbst.FABRICA.wolf_maximo
    assert valor("m_binarizationMethod") == "T_OTSU"


def test_os_dez_na_ordem_do_scantailor():
    texto = (TERCEIROS / "src" / "core" / "filters" / "output" / "BlackWhiteOptions.h").read_text(encoding="utf-8")
    enum = re.search(r"enum BinarizationMethod \{([^}]*)\}", texto).group(1)
    nomes = [n.strip() for n in enum.split(",") if n.strip()]
    assert len(nomes) == 10
    assert [f"st_{n[2:].lower()}" for n in nomes] == list(pbst.CODIGOS)
    assert list(pbst.METODOS.values()) == list(range(10))
    assert set(pbst.NOMES_NA_TELA) == set(pbst.CODIGOS)


def test_o_filtro_conhece_os_mesmos_codigos():
    assert F._CODIGOS_DO_SCANTAILOR == frozenset(pbst.METODOS)
    # e nenhum deles colide com os de antes
    assert not F._CODIGOS_DO_SCANTAILOR & set(F.ALGORITMOS_PB) and "auto" not in F._CODIGOS_DO_SCANTAILOR


def test_de_fabrica_a_pagina_vem_com_o_automatico():
    """O que muda a imagem vem desligado de fábrica (regra de 13/10): a página
    nova continua no "Automático", que não passa pelo ScanTailor."""
    from modelos import ConfigPagina

    assert ConfigPagina(indice=0, folha=0).algoritmo_preto_branco == "auto"
    assert not pbst.e_do_scantailor("auto")


def test_o_medidor_vira_o_ajuste_do_limiar():
    assert pbst.ajuste_do_medidor(50) == 0
    assert pbst.ajuste_do_medidor(0) == -100 and pbst.ajuste_do_medidor(100) == 100
    assert pbst.ajuste_do_medidor(60) == 20 and pbst.ajuste_do_medidor(45) == -10
    assert pbst.ajuste_do_medidor(250) == 100 and pbst.ajuste_do_medidor(-5) == -100
    assert pbst.ajuste_do_medidor("estranho") == 0
    valores = [pbst.ajuste_do_medidor(v) for v in range(0, 101)]
    assert valores == sorted(valores)


# ------------------------------------------------------------- entrada ruim

@pytest.mark.parametrize("img, dpi, metodo, ajuste", [
    (np.zeros((10, 10), np.float32), 300, "st_otsu", 0),       # tipo errado
    (np.zeros((10, 10, 4), np.uint8), 300, "st_otsu", 0),      # 4 canais
    (np.zeros((10, 10), np.uint8), 0, "st_otsu", 0),           # DPI zero
    (np.zeros((10, 10), np.uint8), 300, "sauvola", 0),         # não é do ScanTailor
    (np.zeros((10, 10), np.uint8), 300, "st_otsu", 101),       # ajuste fora
])
def test_entrada_ruim_nao_chega_a_dll(img, dpi, metodo, ajuste):
    resultado = pbst.binarizar(img, dpi, metodo, ajuste)
    assert not resultado.disponivel and resultado.motivo


def test_sem_a_dll_cai_no_automatico_igual(monkeypatch):
    """Sem a DLL, um jeito do ScanTailor dá exatamente o "Automático"."""
    img = pagina_de_texto()
    monkeypatch.setattr(pbst, "preto_e_branco", lambda *a, **k: None)
    assert np.array_equal(F.filtro_preto_e_branco(img, algoritmo="st_sauvola"),
                          F.filtro_preto_e_branco(img, algoritmo="auto"))


# ------------------------------------------------------------- com a DLL

@precisa_da_dll
@pytest.mark.parametrize("metodo", pbst.CODIGOS)
def test_os_dez_dao_preto_e_branco_com_a_letra_preta(metodo):
    img = pagina_de_texto()
    resultado = pbst.binarizar(img, 300, metodo)
    assert resultado.disponivel, (resultado.motivo, resultado.detalhe_tecnico)
    saida = resultado.imagem
    assert saida.shape == img.shape and saida.dtype == np.uint8
    assert set(np.unique(saida)) <= {0, 255}
    letra = mascara_das_letras(img.shape)
    assert (saida[letra] == 0).mean() > 0.9, "a letra não ficou preta"
    # o papel fica branco, inclusive do lado da sombra
    assert (saida[~letra] == 255).mean() > 0.95


@precisa_da_dll
def test_colorida_e_cinza_e_imagem_nao_contigua():
    img = pagina_de_texto(colorida=True)
    a = pbst.binarizar(img, 300, "st_otsu")
    b = pbst.binarizar(np.ascontiguousarray(img[:, ::-1])[:, ::-1], 300, "st_otsu")
    assert a.disponivel and b.disponivel
    assert np.array_equal(a.imagem, b.imagem)
    cinza = pbst.binarizar(pagina_de_texto(), 300, "st_otsu")
    assert cinza.disponivel and cinza.imagem.shape == img.shape[:2]


@precisa_da_dll
def test_largura_que_nao_e_multiplo_de_32():
    img = pagina_de_texto(largura=601, altura=397)
    resultado = pbst.binarizar(img, 300, "st_wolf")
    assert resultado.disponivel and resultado.imagem.shape == (397, 601)


@precisa_da_dll
def test_mais_escuro_no_medidor_da_mais_preto():
    img = pagina_de_texto()
    pretos = [int((pbst.binarizar(img, 300, "st_otsu", ajuste).imagem == 0).sum())
              for ajuste in (-60, 0, 60)]
    assert pretos[0] <= pretos[1] <= pretos[2] and pretos[0] < pretos[2]


@precisa_da_dll
def test_as_tres_etapas_de_fabrica_fazem_diferenca():
    """Desligar o igualar a luz muda o resultado na página com sombra (é a
    etapa que o ScanTailor faz antes de separar): sem ela, o Otsu (um limiar
    para a página inteira) pinta de preto o papel do lado da sombra."""
    img = pagina_de_texto()
    ligado = pbst.binarizar(img, 300, "st_otsu").imagem
    desligado = pbst.binarizar(img, 300, "st_otsu", 0, pbst.Opcoes(normalizar=False)).imagem
    letra = mascara_das_letras(img.shape)
    assert (ligado[~letra] == 255).mean() > 0.95
    assert (desligado[~letra] == 0).mean() > 0.2


@precisa_da_dll
def test_nao_mexe_na_imagem_de_entrada():
    img = pagina_de_texto(colorida=True)
    copia = img.copy()
    pbst.binarizar(img, 300, "st_sauvola")
    assert np.array_equal(img, copia)


@precisa_da_dll
def test_no_filtro_do_programa():
    """Pela porta do programa (filtro_preto_e_branco): preto e branco, e a
    letra colorida continua preta por cima (regra V1/A1)."""
    img = pagina_de_texto(colorida=True)
    img[300:330, 300:330] = (0, 0, 200)          # um quadrado vermelho vivo, borda nítida
    saida = F.filtro_preto_e_branco(img, algoritmo="st_otsu", despeckle=False)
    assert set(np.unique(saida)) <= {0, 255}
    assert (saida[305:325, 305:325] == 0).all()
    # é o do ScanTailor, não o Automático
    assert not np.array_equal(saida, F.filtro_preto_e_branco(img, algoritmo="auto", despeckle=False))


@precisa_da_dll
def test_o_dpi_vem_do_limpar_a_sujeira():
    """O programa passa o DPI de verdade no Pontinhos; sem ele, sai pela altura."""
    from core import pontinhos_scantailor as ps

    img = pagina_de_texto()
    com_dpi = F.filtro_preto_e_branco(img, algoritmo="st_otsu",
                                      despeckle=ps.Pontinhos(ps.DESLIGADO, 150.0))
    direto = F._com_a_tinta_colorida(img, pbst.binarizar(img, 150, "st_otsu").imagem)
    assert np.array_equal(com_dpi, direto)


def test_o_pipeline_mede_o_dpi_para_os_jeitos_do_scantailor():
    from core import pipeline as P
    from core import pontinhos_scantailor as ps
    from modelos import ConfigPagina, Projeto

    projeto = Projeto(caminho_entrada="x.pdf")
    projeto.limpar_pontinhos = ps.DESLIGADO
    pagina = ConfigPagina(indice=0, folha=0, filtro=F.PRETO_E_BRANCO)
    img = np.full((3000, 2000), 255, np.uint8)
    assert P.pontinhos_da_pagina(projeto, pagina, img, 300.0, 300.0).dpi is None
    pagina.algoritmo_preto_branco = "st_wolf"
    assert P.pontinhos_da_pagina(projeto, pagina, img, 300.0, 300.0).dpi == 300.0
    assert P._vai_limpar_pelo_scantailor(projeto, pagina) == bool(projeto.limpar)
