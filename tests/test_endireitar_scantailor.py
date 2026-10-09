"""O endireitar do ScanTailor na DLL comum (item 2.2 da Fase 2, 06/10/2026).

Testes de máquina:
- a limpeza das sombras copiada de deskew/Task.cpp (linhas 222-271) é igual,
  letra por letra, ao original v1.2.1 (guardado em terceiros/.../referencia);
- os arquivos trazidos para o endireitar estão entre os conferidos pela soma
  (o teste geral de cópia fiel é tests/test_st_ferramentas.py);
- o SENTIDO do ângulo: numa folha de mentira girada 2° para cada lado, o
  ângulo devolvido endireita (é o contrário do giro);
- página em branco: zero; parâmetro estranho e DLL ausente não derrubam nada;
- nas páginas-gabarito do D3 (se a pasta gabarito existir), os números que o
  programa de teste do D3 achou com o mesmo código, a 300 DPI;
- as contas que a pessoa escolhe (jeito do livro e da página) e a
  discordância de mais de 0,3° (decisão C1 do Samuel).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pytest

from core import endireitar_scantailor as es
from core import st_ferramentas as st

RAIZ = Path(__file__).resolve().parent.parent
TERCEIROS = RAIZ / "terceiros" / "scantailor-advanced"
COLA = TERCEIROS / "ligacao-ferramentas" / "endireitar.cpp"
REFERENCIA = TERCEIROS / "referencia" / "deskew" / "Task.cpp"
GABARITO = RAIZ / "gabarito" / "paginas"

# SHA-256 de src/core/filters/deskew/Task.cpp do ScanTailor Advanced v1.2.1
# (commit 5eaac18), tirado do git do ScanTailor (git show v1.2.1:..., fim de
# linha LF).
SHA256_DESKEW_TASK = "ecd94429240f2e1ac2856e41fb7efad0fca2a7516799870591c7696d6cadbb6c"

precisa_da_dll = pytest.mark.skipif(not st.disponivel(), reason="st_ferramentas.dll não compilada")


def _sem_cr(caminho: Path) -> str:
    return caminho.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")


# ------------------------------------------------------------- cópia fiel

def test_referencia_e_o_original():
    assert hashlib.sha256(_sem_cr(REFERENCIA).encode("utf-8")).hexdigest() == SHA256_DESKEW_TASK


def test_cola_copiada_sem_mudanca():
    """O trecho entre as marcas de endireitar.cpp é igual às linhas 222-271 de deskew/Task.cpp."""
    cola = _sem_cr(COLA)
    trecho = re.search(r"// ---- COPIADO SEM MUDANCA[^\n]*\n(.*?)// ---- FIM DO TRECHO COPIADO", cola, re.S)
    assert trecho, "marcas do trecho copiado sumiram de endireitar.cpp"
    original = "\n".join(_sem_cr(REFERENCIA).split("\n")[221:271]) + "\n"
    assert trecho.group(1) == original
    assert "void Task::cleanup(" in original and "QSize Task::from150dpi(" in original


def test_arquivos_do_endireitar_estao_entre_os_conferidos():
    somas = (TERCEIROS / "somas-v1.2.1.txt").read_text(encoding="utf-8")
    for rel in ("src/imageproc/SkewFinder.cpp", "src/imageproc/SkewFinder.h",
                "src/imageproc/UpscaleIntegerTimes.cpp", "src/imageproc/UpscaleIntegerTimes.h",
                "src/core/BlackOnWhiteEstimator.cpp", "src/core/BlackOnWhiteEstimator.h"):
        assert f"  {rel}" in somas, rel


# ------------------------------------------------------------- sem a DLL

def test_dll_ausente_fica_indisponivel(tmp_path):
    biblioteca = st.BibliotecaScanTailor(tmp_path / "nao_existe.dll")
    medida = es.medir(np.full((200, 100), 255, np.uint8), 150, biblioteca=biblioteca)
    assert not medida.disponivel
    assert medida.angulo is None and medida.motivo


def test_formato_estranho_fica_indisponivel():
    assert not es.medir(None, 150).disponivel
    assert not es.medir(np.zeros((10, 10, 2), np.uint8), 150).disponivel
    assert not es.medir(np.full((100, 100), 255, np.uint8), 5).disponivel     # DPI fora da faixa


# ------------------------------------------------------------- a DLL

def _folha_de_texto(graus: float) -> np.ndarray:
    """Folha com "linhas de texto" giradas `graus` no sentido do OpenCV."""
    img = np.full((1754, 1240), 255, np.uint8)
    for y in range(200, 1550, 40):
        for x in range(150, 1090, 60):
            cv2.rectangle(img, (x, y), (x + 45, y + 18), 0, -1)
    m = cv2.getRotationMatrix2D((620, 877), graus, 1.0)
    return cv2.warpAffine(img, m, (1240, 1754), borderValue=255)


@precisa_da_dll
@pytest.mark.parametrize("graus", [2.0, -2.0, 0.6])
def test_o_angulo_endireita(graus):
    """Página girada +g (OpenCV): o ScanTailor manda girar -g (sentido do programa)."""
    medida = es.medir(_folha_de_texto(graus), 150)
    assert medida.disponivel
    assert medida.confianca >= es.CONFIANCA_BOA
    assert medida.angulo == pytest.approx(-graus, abs=0.15)
    assert medida.preto_no_branco


@precisa_da_dll
def test_folha_colorida_da_o_mesmo_que_a_cinza():
    cinza = _folha_de_texto(1.0)
    cor = cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)
    assert es.medir(cor, 150).angulo == pytest.approx(es.medir(cinza, 150).angulo, abs=1e-9)


@precisa_da_dll
def test_pagina_em_branco_da_zero():
    medida = es.medir(np.full((1200, 800), 255, np.uint8), 150)
    assert medida.disponivel and medida.angulo == 0.0


@precisa_da_dll
def test_sem_dpi_supoe_dez_polegadas():
    medida = es.medir(_folha_de_texto(1.0), None)
    assert medida.disponivel and medida.dpi == pytest.approx(175.0)


# Os números do D3 (05/10/2026, relatorios/fase2-geometria-d3-2026-10-05/dados/
# medidas.json): o mesmo código do ScanTailor, a página do PDF desenhada a 300
# DPI e dita 300 DPI, nas páginas em que o ScanTailor não cortou sobra.
NUMEROS_DO_D3 = {
    "palatino_p005": 0.50,
    "boecio_p008": -1.12,
    "opusmajus_p011": -0.25,
    "opusmajus_p165": 0.31,
}


@precisa_da_dll
@pytest.mark.skipif(not GABARITO.is_dir(), reason="sem a pasta do gabarito")
@pytest.mark.parametrize("nome,angulo", sorted(NUMEROS_DO_D3.items()))
def test_numeros_do_d3(nome, angulo):
    from core.pdf_io import abrir_pdf, pagina_para_array

    doc = abrir_pdf(str(GABARITO / f"{nome}.pdf"))
    try:
        img = pagina_para_array(doc, 0, dpi=300)
    finally:
        doc.close()
    assert es.medir(img, 300).angulo == pytest.approx(angulo, abs=0.006)


# ------------------------------------------------------------- as contas

def test_jeitos():
    assert es.PADRAO == es.JEITO_SCANTAILOR
    assert es.JEITO_DO_PROJETO_ANTIGO == es.JEITO_PROGRAMA
    assert es.jeito_valido("qualquer") == es.PADRAO
    livro = SimpleNamespace(endireitar_como=es.JEITO_PROGRAMA)
    assert es.jeito_da_pagina(livro, SimpleNamespace(endireitar_como=None)) == es.JEITO_PROGRAMA
    assert es.jeito_da_pagina(livro, SimpleNamespace(endireitar_como=es.JEITO_SCANTAILOR)) \
        == es.JEITO_SCANTAILOR
    assert es.jeito_da_pagina(SimpleNamespace(), SimpleNamespace()) == es.PADRAO


def test_discordancia_de_mais_de_0_3_grau():
    assert not es.discordam(0.4, 0.1)            # 0,3 exatos: não é "mais de"
    assert es.discordam(0.4, 0.05)
    assert es.discordam(-0.5, 0.0)
    assert not es.discordam(0.7, 0.75)
    assert not es.discordam(None, 0.5)           # sem a DLL, nada a mostrar
