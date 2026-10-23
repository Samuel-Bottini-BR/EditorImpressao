"""As cores do ScanTailor: "Letras com a cor delas" e "Reduzir cores" (item 2.11, 20/10/2026).

Testes de máquina:
- a cola copia o segmentImage/posterizeImage do OutputGenerator.cpp sem mudança
  (o teste de cópia fiel está em tests/test_preto_e_branco_scantailor.py);
- os números de fábrica são os do ScanTailor (lidos dos .cpp dele);
- desmarcadas de fábrica, e projeto antigo abre desmarcado;
- com "Letras com a cor delas", a letra vermelha sai vermelha e a preta, preta;
  o papel continua branco; a página deixa de ser monocromática;
- "Reduzir cores" deixa poucas cores na página de cor;
- no "Tirar o fundo" nada muda; sem a DLL a página sai como sem as caixinhas.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from core import cores_scantailor as cs
from core import pipeline as P
from core import st_ferramentas as st
from core.filtros import MELHORAR, PRETO_E_BRANCO, TIRAR_FUNDO
from modelos import ConfigFolha, ConfigPagina, Projeto

RAIZ = Path(__file__).resolve().parent.parent
OUTPUT = RAIZ / "terceiros" / "scantailor-advanced" / "src" / "core" / "filters" / "output"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def pagina_com_letras_coloridas() -> np.ndarray:
    """Papel creme; uma linha de hastes pretas e uma de hastes vermelhas."""
    img = np.zeros((300, 500, 3), np.uint8)
    img[:] = (205, 225, 235)
    for k in range(15):
        img[60:100, 30 + k * 30:38 + k * 30] = (30, 30, 30)
        img[180:220, 30 + k * 30:38 + k * 30] = (40, 40, 200)
    return img


def projeto_e_pagina(filtro=PRETO_E_BRANCO, letras=False, reduzir=False):
    projeto = Projeto(caminho_entrada="x.pdf", detectar_regioes=False)
    projeto.folhas = [ConfigFolha(indice=0, dividir=False)]
    pagina = ConfigPagina(indice=0, folha=0, filtro=filtro)
    pagina.letras_com_a_cor, pagina.reduzir_cores = letras, reduzir
    projeto.paginas = [pagina]
    return projeto, pagina


def test_os_de_fabrica_sao_os_do_scantailor():
    bw = (OUTPUT / "BlackWhiteOptions.cpp").read_text(encoding="utf-8")
    seg = bw[bw.index("ColorSegmenterOptions::ColorSegmenterOptions()"):]
    seg = seg[:seg.index("{}")]
    assert "m_isEnabled(false)" in seg
    assert int(re.search(r"m_noiseReduction\((\d+)\)", seg).group(1)) == cs.FABRICA.ruido
    for cor in ("red", "green", "blue"):
        assert f"m_{cor}ThresholdAdjustment(0)" in seg
    comum = (OUTPUT / "ColorCommonOptions.cpp").read_text(encoding="utf-8")
    post = comum[comum.index("PosterizationOptions::PosterizationOptions()"):]
    post = post[:post.index("{}")]
    assert "m_isEnabled(false)" in post
    assert int(re.search(r"m_level\((\d+)\)", post).group(1)) == cs.FABRICA.nivel
    assert "m_isNormalizationEnabled(false)" in post and not cs.FABRICA.normalizar_cores
    assert "m_forceBlackAndWhite(true)" in post and cs.FABRICA.forcar_preto_e_branco


def test_desmarcadas_de_fabrica_e_projeto_antigo():
    pagina = ConfigPagina(indice=0, folha=0)
    assert pagina.letras_com_a_cor is False and pagina.reduzir_cores is False
    projeto, _ = projeto_e_pagina()
    dados = projeto.para_dicionario()
    for p in dados["paginas"]:
        p.pop("letras_com_a_cor", None)
        p.pop("reduzir_cores", None)
    nova = Projeto.de_dicionario(dados).paginas[0]
    assert nova.letras_com_a_cor is False and nova.reduzir_cores is False


def test_desmarcadas_nada_muda():
    img = pagina_com_letras_coloridas()
    a = P._filtrar(*projeto_e_pagina(), img)
    assert cs.aplicar(img, a[0], PRETO_E_BRANCO, False, False) is None
    assert cs.aplicar(img, a[0], MELHORAR, True, False) is None, "letras só no Preto e branco"
    assert cs.aplicar(img, a[0], TIRAR_FUNDO, True, True) is None


def test_entrada_ruim_nao_chega_a_dll():
    img = pagina_com_letras_coloridas()
    assert not cs.cores(img, 300).disponivel                          # nada a fazer
    assert not cs.cores(img, 300, preto_e_branco=np.zeros((5, 5), np.uint8)).disponivel
    assert not cs.cores(img.astype(np.float32), 300, posterizar=True).disponivel


@precisa_da_dll
def test_letras_com_a_cor_delas():
    img = pagina_com_letras_coloridas()
    saida, mono = P._filtrar(*projeto_e_pagina(letras=True), img)
    assert not mono and saida.ndim == 3
    preta = saida[70:90, 32:36].reshape(-1, 3).mean(0)
    vermelha = saida[190:210, 32:36].reshape(-1, 3).mean(0)
    assert preta.max() < 90, preta
    assert vermelha[2] > 120 and vermelha[2] > vermelha[0] + 60, vermelha
    assert (saida[130:160] == 255).all(), "o papel continua branco"
    # sem a caixinha a letra vermelha sai preta (a regra V1 de sempre)
    sem, mono_sem = P._filtrar(*projeto_e_pagina(), img)
    assert mono_sem and sem[190:210, 32:36].max() == 0


@precisa_da_dll
def test_reduzir_cores_na_pagina_de_cor():
    rng = np.random.default_rng(1)
    img = rng.integers(0, 256, (200, 300, 3), dtype=np.uint8)
    projeto, pagina = projeto_e_pagina(MELHORAR, reduzir=True)
    saida, mono = P._filtrar(projeto, pagina, img)
    antes = len(np.unique(P._filtrar(*projeto_e_pagina(MELHORAR), img)[0].reshape(-1, 3), axis=0))
    depois = len(np.unique(saida.reshape(-1, 3), axis=0))
    assert not mono and depois < antes and depois <= (cs.FABRICA.nivel + 1) ** 3  # uma cor por grupo (nivel+1 faixas por canal)


@precisa_da_dll
def test_sem_a_dll_sai_como_sem_as_caixinhas(monkeypatch):
    img = pagina_com_letras_coloridas()
    monkeypatch.setattr(cs, "cores", lambda *a, **k: st.Resultado(None, "sem a DLL"))
    com = P._filtrar(*projeto_e_pagina(letras=True), img)
    sem = P._filtrar(*projeto_e_pagina(), img)
    assert np.array_equal(com[0], sem[0]) and com[1] == sem[1]
