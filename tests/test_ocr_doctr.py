"""Testes da ponte até o docTR (core/ocr_doctr.py), item 1.3.

DUAS PARTES
    1. Sem o modelo (rodam sempre, em segundos): modelo ausente, danificado,
       OnnxTR "não instalado", imagem inválida, cancelar, erro dentro do
       detector. Em todos: aviso em português, nenhuma exceção.
    2. Com o modelo (modelos\\doctr\\, fora do git) e as páginas do 1.3
       (saida_teste\\ocr-1.3, fora do git): as 22 páginas dão as MESMAS caixas
       da comparação de 28/09 (configuração "D2"): mesma contagem de palavras
       e de linhas, e área das linhas em comum >= 99% nos dois sentidos.
       Pulados se o modelo, o OnnxTR ou as páginas faltarem.
       Com -s, o tempo de cada página aparece na tela:
           .venv\\Scripts\\python.exe -m pytest tests\\test_ocr_doctr.py -s

ARRISCADO MUDAR
    AREA_MINIMA (0,99) e "mesma contagem": é o critério pedido pela gerente
    para dizer que a ponte = a comparação do 1.3.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import ocr_doctr
from core.ocr_comum import LinhaOCR, ResultadoOCR
from core.ocr_doctr import DetectorDoctr

RAIZ = Path(__file__).resolve().parent.parent
IMAGENS_13 = RAIZ / "saida_teste" / "ocr-1.3" / "imagens"
REFERENCIA_D2 = RAIZ / "saida_teste" / "ocr-1.3" / "linhas" / "D2"
AREA_MINIMA = 0.99

PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]


def _pagina(altura=40, largura=30, cor=(10, 20, 30)):
    img = np.zeros((altura, largura, 3), np.uint8)
    img[:] = cor
    return img


def _indisponivel_com_aviso(r: ResultadoOCR, trecho: str):
    assert isinstance(r, ResultadoOCR)
    assert r.motor == "doctr"
    assert not r.disponivel and r.linhas is None
    assert trecho in r.motivo
    assert r.detalhe_tecnico   # o erro técnico existe (vai para o log), separado do aviso


# =====================================================================
# 1. Sem o modelo
# =====================================================================

def test_modelo_ausente_da_aviso_e_nao_quebra(tmp_path):
    detector = DetectorDoctr(tmp_path / "nao_existe.onnx")
    inicio = time.perf_counter()
    _indisponivel_com_aviso(detector.segmentar(_pagina()), "não está instalado")
    # a segunda página não tenta de novo (e não demora)
    _indisponivel_com_aviso(detector.segmentar(_pagina()), "não está instalado")
    assert time.perf_counter() - inicio < 2
    assert not detector.aberto
    detector.fechar()
    detector.fechar()   # fechar duas vezes não quebra


def test_onnxtr_nao_instalado(tmp_path, monkeypatch):
    modelo = tmp_path / "modelo.onnx"
    modelo.write_bytes(b"qualquer")

    def falta():
        raise ImportError("No module named 'onnxtr'")

    monkeypatch.setattr(ocr_doctr, "_importar_onnxtr", falta)
    r = DetectorDoctr(modelo, soma_esperada=None).segmentar(_pagina())
    _indisponivel_com_aviso(r, "falta a biblioteca OnnxTR")
    assert "No module named" in r.detalhe_tecnico


def _tem_onnxtr() -> bool:
    return importlib.util.find_spec("onnxtr") is not None


@pytest.mark.skipif(not _tem_onnxtr(), reason="OnnxTR não instalado no .venv")
def test_modelo_danificado_pela_soma(tmp_path):
    modelo = tmp_path / ocr_doctr.NOME_DO_MODELO
    modelo.write_bytes(b"isto nao e um modelo")
    _indisponivel_com_aviso(DetectorDoctr(modelo).segmentar(_pagina()), "danificado")


@pytest.mark.skipif(not _tem_onnxtr(), reason="OnnxTR não instalado no .venv")
def test_modelo_que_nao_abre(tmp_path):
    modelo = tmp_path / "lixo.onnx"
    modelo.write_bytes(b"isto nao e um modelo")
    r = DetectorDoctr(modelo, soma_esperada=None).segmentar(_pagina())
    _indisponivel_com_aviso(r, "não conseguiu abrir")


def test_imagem_invalida_nao_carrega_o_modelo(tmp_path):
    detector = DetectorDoctr(tmp_path / "nao_existe.onnx")
    for ruim in (np.zeros((10, 10), np.float32), np.zeros((0, 5, 3), np.uint8),
                 np.zeros((4, 4, 2), np.uint8), tmp_path / "nao_existe.png", None, 42):
        r = detector.segmentar(ruim)
        assert not r.disponivel and r.motivo
        assert "não conseguiu ler esta página" in r.motivo
    assert not detector.segmentar(_pagina(), ordem="CMYK").disponivel
    assert detector._falha_ao_abrir is None   # nem tentou abrir o modelo


def test_cancelar_antes_de_comecar(tmp_path):
    detector = DetectorDoctr(tmp_path / "nao_existe.onnx")
    _indisponivel_com_aviso(detector.segmentar(_pagina(), cancelar=lambda: True), "Cancelado")

    def quebra():
        raise RuntimeError("bug de quem chamou")

    _indisponivel_com_aviso(detector.segmentar(_pagina(), cancelar=quebra), "Cancelado")


class _PreditorDeMentira:
    """Faz o papel do preditor do OnnxTR: devolve caixas fixas, ou quebra."""

    def __init__(self, caixas=None, quebra=False):
        self.caixas = caixas
        self.quebra = quebra
        self.recebido = None

    def __call__(self, paginas):
        self.recebido = paginas
        if self.quebra:
            raise RuntimeError("onnxruntime: falhou por dentro")
        return [self.caixas]


class _MontadorDeMentira:
    """Junta as palavras em linhas pela altura (só para o teste)."""

    @staticmethod
    def _resolve_lines(caixas):
        grupos: dict[float, list[int]] = {}
        for i, c in enumerate(caixas):
            grupos.setdefault(round(float(c[1]), 2), []).append(i)
        return list(grupos.values())


def _detector_com(preditor) -> DetectorDoctr:
    detector = DetectorDoctr("nao_importa.onnx", soma_esperada=None)
    detector._preditor = preditor
    detector._montador = _MontadorDeMentira()
    return detector


def test_erro_dentro_do_detector_vira_aviso():
    r = _detector_com(_PreditorDeMentira(quebra=True)).segmentar(_pagina())
    _indisponivel_com_aviso(r, "não conseguiu ler esta página")
    assert "falhou por dentro" in r.detalhe_tecnico


def test_caixas_viram_pontos_da_imagem_e_cores_em_rgb():
    caixas = np.array([[0.1, 0.1, 0.3, 0.2, 0.9],
                       [0.4, 0.1, 0.6, 0.2, 0.7],
                       [0.1, 0.5, 0.5, 0.6, 0.8]], np.float32)
    preditor = _PreditorDeMentira(caixas)
    r = _detector_com(preditor).segmentar(_pagina(altura=200, largura=100, cor=(10, 20, 30)))
    assert r.disponivel and r.motivo is None
    assert (r.largura, r.altura) == (100, 200)
    assert preditor.recebido[0][0, 0].tolist() == [30, 20, 10]   # BGR do programa -> RGB
    assert len(r.palavras) == 3
    assert r.palavras[0].caixa == pytest.approx((10, 20, 30, 40))
    assert r.palavras[1].confianca == pytest.approx(0.7)
    assert len(r.linhas) == 2
    primeira = r.linhas[0]
    assert isinstance(primeira, LinhaOCR)
    assert primeira.poligono.dtype == np.float32 and primeira.poligono.shape == (4, 2)
    assert np.allclose(primeira.poligono, [[10, 20], [60, 20], [60, 40], [10, 40]], atol=1e-4)
    assert primeira.palavras == 2 and primeira.confianca == pytest.approx(0.8)
    assert not r.precisa_revisar


def test_pagina_sem_texto_e_resposta_valida():
    r = _detector_com(_PreditorDeMentira(np.zeros((0, 5), np.float32))).segmentar(_pagina())
    assert r.disponivel and r.linhas == [] and r.palavras == []


def test_cinza_e_quatro_canais():
    preditor = _PreditorDeMentira(np.zeros((0, 5), np.float32))
    detector = _detector_com(preditor)
    assert detector.segmentar(np.full((5, 6), 77, np.uint8)).disponivel
    assert preditor.recebido[0].shape == (5, 6, 3) and preditor.recebido[0][0, 0].tolist() == [77, 77, 77]
    quatro = np.zeros((3, 3, 4), np.uint8)
    quatro[..., 0] = 7
    assert detector.segmentar(quatro).disponivel
    assert preditor.recebido[0][0, 0].tolist() == [0, 0, 7]
    assert detector.segmentar(quatro, ordem="RGB").disponivel
    assert preditor.recebido[0][0, 0].tolist() == [7, 0, 0]


def test_imagem_por_caminho_com_acento(tmp_path):
    preditor = _PreditorDeMentira(np.zeros((0, 5), np.float32))
    caminho = tmp_path / "página çã.png"
    ok, png = cv2.imencode(".png", _pagina(cor=(1, 2, 3)))
    caminho.write_bytes(png.tobytes())
    assert _detector_com(preditor).segmentar(caminho).disponivel
    assert preditor.recebido[0][0, 0].tolist() == [3, 2, 1]


def test_opcoes_fixas_sao_as_da_comparacao():
    assert ocr_doctr.OPCOES_DO_PREDITOR == {"assume_straight_pages": True, "preserve_aspect_ratio": True,
                                            "symmetric_pad": True, "batch_size": 2}
    assert ocr_doctr.LIMIARES == {"bin_thresh": 0.1, "box_thresh": 0.1}
    assert ocr_doctr.ARQUITETURA == "fast_base"
    assert ocr_doctr.CAMINHO_MODELO.parent == RAIZ / "modelos" / "doctr"


def test_requirements_trava_o_onnxtr():
    linhas = (RAIZ / "requirements.txt").read_text(encoding="utf-8").splitlines()
    assert f"onnxtr=={ocr_doctr.VERSAO_ONNXTR}" in [l.strip() for l in linhas]


@pytest.mark.parametrize("arquivo", ["ocr_doctr.py", "ocr_comum.py", "ocr_tesseract.py"])
def test_core_nao_importa_ui_nem_qt(arquivo):
    arvore = ast.parse((RAIZ / "core" / arquivo).read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes |= {a.name for a in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module)
    assert not any(n.split(".")[0] in ("ui", "PySide6", "PyQt5", "PyQt6") for n in nomes), nomes


# =====================================================================
# 2. Com o modelo: igual à comparação do 1.3
# =====================================================================

precisa_do_modelo = pytest.mark.skipif(
    not (ocr_doctr.CAMINHO_MODELO.is_file() and _tem_onnxtr()),
    reason="modelo do docTR (modelos\\doctr) ou OnnxTR ausente")
precisa_das_paginas = pytest.mark.skipif(
    not (IMAGENS_13.is_dir() and REFERENCIA_D2.is_dir()),
    reason="páginas e caixas do 1.3 não estão em saida_teste/ocr-1.3 (fora do git)")

_TEMPOS: dict[str, tuple] = {}


@pytest.fixture(scope="module")
def detector_de_verdade():
    detector = DetectorDoctr()
    yield detector
    detector.fechar()
    if _TEMPOS:
        print(f"\n[docTR fast_base] carregar o modelo: {detector.segundos_para_abrir:.1f} s; por página:")
        for pagina, (segundos, linhas, ref, palavras, ref_p, area) in _TEMPOS.items():
            print(f"    {pagina:16s} {segundos:5.2f} s  {linhas:4d} linhas (1.3: {ref:4d})  "
                  f"{palavras:4d} palavras (1.3: {ref_p:4d})  área em comum {100 * area:6.2f}%")
        valores = sorted(v[0] for v in _TEMPOS.values())
        print(f"    mediana {valores[len(valores) // 2]:.2f} s em {len(valores)} página(s)")


def _mascara(poligonos, largura: int, altura: int) -> np.ndarray:
    mascara = np.zeros((altura, largura), np.uint8)
    for p in poligonos:
        pontos = np.round(np.asarray(p, np.float64)).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(mascara, [pontos], 1)
    return mascara.astype(bool)


@precisa_do_modelo
@precisa_das_paginas
@pytest.mark.parametrize("pagina", PAGINAS)
def test_mesmas_caixas_da_comparacao_do_13(detector_de_verdade, pagina):
    referencia = json.loads((REFERENCIA_D2 / f"{pagina}.json").read_text(encoding="utf-8"))
    r = detector_de_verdade.segmentar(IMAGENS_13 / f"{pagina}.png")
    assert r.disponivel, (r.motivo, r.detalhe_tecnico)
    novo = _mascara([l.poligono for l in r.linhas], r.largura, r.altura)
    antes = _mascara([l["poligono"] for l in referencia["linhas"]], r.largura, r.altura)
    comum = np.count_nonzero(novo & antes)
    area = min(comum / max(1, np.count_nonzero(antes)), comum / max(1, np.count_nonzero(novo)))
    _TEMPOS[pagina] = (r.segundos, len(r.linhas), len(referencia["linhas"]),
                       len(r.palavras), referencia["palavras"], area)
    assert len(r.palavras) == referencia["palavras"], pagina
    assert len(r.linhas) == len(referencia["linhas"]), pagina
    assert comum / max(1, np.count_nonzero(antes)) >= AREA_MINIMA, pagina
    assert comum / max(1, np.count_nonzero(novo)) >= AREA_MINIMA, pagina
    assert sum(l.palavras for l in r.linhas) == len(r.palavras)


@precisa_do_modelo
@precisa_das_paginas
def test_pagina_em_memoria_bgr_da_o_mesmo_que_o_arquivo(detector_de_verdade):
    pagina = IMAGENS_13 / "palatino_p057.png"
    pelo_arquivo = detector_de_verdade.segmentar(pagina)
    bgr = cv2.imdecode(np.fromfile(str(pagina), np.uint8), cv2.IMREAD_COLOR)
    pela_memoria = detector_de_verdade.segmentar(bgr)       # BGR, como o programa usa
    assert pelo_arquivo.disponivel and pela_memoria.disponivel
    assert len(pelo_arquivo.linhas) == len(pela_memoria.linhas)
    for a, b in zip(pelo_arquivo.linhas, pela_memoria.linhas):
        assert np.array_equal(a.poligono, b.poligono)


@precisa_do_modelo
def test_modelo_de_verdade_confere_a_soma_e_nao_baixa_nada(monkeypatch):
    import onnxtr.utils.data as dados

    def proibido(*_a, **_k):
        raise AssertionError("o OnnxTR tentou baixar da internet")

    monkeypatch.setattr(dados, "download_from_url", proibido)
    import onnxtr.models.engine as motor
    monkeypatch.setattr(motor, "download_from_url", proibido)
    with DetectorDoctr() as detector:
        r = detector.segmentar(_pagina(altura=64, largura=64, cor=(255, 255, 255)))
        assert r.disponivel, (r.motivo, r.detalhe_tecnico)
        assert detector.info["onnxtr"].lstrip("v") == ocr_doctr.VERSAO_ONNXTR
    assert not detector.aberto
