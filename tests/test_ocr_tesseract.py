"""Testes da ponte até o Tesseract (core/ocr_tesseract.py), item 1.3.

DUAS PARTES
    1. Sem o Tesseract (rodam sempre, em segundos): um "Tesseract de mentira"
       (um script Python do próprio .venv no lugar do tesseract.exe) que
       morre, trava, não grava a saída, grava lixo, escreve muito aviso. Em
       todos: aviso em português, nenhuma exceção, nada travado. E a leitura
       do hOCR, o comando montado e a procura do tesseract.exe.
    2. Com o Tesseract instalado e os modelos em modelos\\tessdata (fora do
       git): as linhas iguais às da comparação de 28/09 (configuração "T1":
       modelo do idioma do livro, --psm 3): mesma contagem e área em comum
       >= 99% nos dois sentidos. Pulados se faltar o Tesseract, o modelo ou
       as páginas do 1.3 (saida_teste\\ocr-1.3, fora do git).

       Por padrão rodam 6 páginas (~15 s). As 22 (~1 min) rodam com OCR_22=1:
           set OCR_22=1 && .venv\\Scripts\\python.exe -m pytest tests\\test_ocr_tesseract.py -s
       Com -s, o tempo de cada página aparece na tela.

ARRISCADO MUDAR
    AREA_MINIMA (0,99), "mesma contagem" e IDIOMA_DO_LIVRO / a regra do DPI
    (são as da comparação do 1.3).
"""

from __future__ import annotations

import json
import os
import sys
import textwrap
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

from core import ocr_tesseract
from core.ocr_comum import ResultadoOCR
from core.ocr_tesseract import MotorTesseract

RAIZ = Path(__file__).resolve().parent.parent
IMAGENS_13 = RAIZ / "saida_teste" / "ocr-1.3" / "imagens"
REFERENCIA_T1 = RAIZ / "saida_teste" / "ocr-1.3" / "linhas" / "T1"
LISTA = RAIZ / "gabarito" / "lista.json"
AREA_MINIMA = 0.99

# O modelo "normal" de cada livro na comparação (scripts/comum.py, IDIOMA_LIVRO).
IDIOMA_DO_LIVRO = {
    "palatino": "ita", "escola": "por", "horas": "fra", "opusmajus": "eng",
    "rhetorica": "lat", "siebmacher": "script/Fraktur", "graduale": "lat",
}
TODAS_AS_PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]
# As 6 do padrão: a menor (Opus 20), as duas sem nenhuma linha (Horas 11,
# Graduale 222), o Fraktur (Siebmacher 9), uma de 72 DPI com texto (Horas 13)
# e o retrato do Palatino 5.
PAGINAS_PADRAO = ["opusmajus_p020", "horas_p011", "graduale_p222", "siebmacher_p009",
                  "horas_p013", "palatino_p005"]
PAGINAS = TODAS_AS_PAGINAS if os.environ.get("OCR_22") == "1" else PAGINAS_PADRAO


def _pagina(altura=40, largura=30, cor=(10, 20, 30)):
    img = np.zeros((altura, largura, 3), np.uint8)
    img[:] = cor
    return img


def _indisponivel_com_aviso(r: ResultadoOCR, trecho: str):
    assert isinstance(r, ResultadoOCR)
    assert r.motor == "tesseract"
    assert not r.disponivel and r.linhas is None
    assert trecho in r.motivo
    assert r.detalhe_tecnico   # o erro técnico existe (vai para o log), separado do aviso


# =====================================================================
# 1. Sem o Tesseract: a ponte com um Tesseract de mentira
# =====================================================================

HOCR_DE_EXEMPLO = """<?xml version="1.0" encoding="UTF-8"?>
<html><body>
 <div class='ocr_page' id='page_1' title='image "x.png"; bbox 0 0 300 400; ppageno 0'>
  <div class='ocr_carea' id='block_1_1' title="bbox 10 10 290 100">
   <p class='ocr_par' id='par_1_1' lang='lat' title="bbox 10 10 290 100">
    <span class='ocr_line' id='line_1_1' title="bbox 10 10 290 40; baseline 0 -5; x_size 30">
     <span class='ocrx_word' id='word_1_1' title='bbox 10 12 100 40; x_wconf 90'>AVE</span>
     <span class='ocrx_word' id='word_1_2' title='bbox 120 12 290 40; x_wconf 70'>MARIA</span>
    </span>
    <span class='ocr_header' id='line_1_2' title="bbox 20 60 200 100; baseline 0 -3">
     <span class='ocrx_word' id='word_1_3' title='bbox 20 60 200 100; x_wconf 11'>GRATIA</span>
    </span>
    <span class='ocr_textfloat' id='line_1_3' title="bbox 5 300 30 330">
    </span>
   </p>
  </div>
 </div>
</body></html>
"""

_TESSERACT_DE_MENTIRA = textwrap.dedent('''
    import json, sys, time
    modo, registro = sys.argv[1], sys.argv[2]
    argumentos = sys.argv[3:]
    import cv2, numpy as np
    img = cv2.imdecode(np.fromfile(argumentos[0], np.uint8), cv2.IMREAD_UNCHANGED)
    with open(registro, "w", encoding="utf-8") as f:
        json.dump({"argumentos": argumentos, "pixel_bgr": [int(v) for v in np.atleast_1d(img[0, 0])],
                   "forma": list(img.shape)}, f)
    saida = argumentos[1] + ".hocr"
    if modo == "morre":
        sys.stderr.write("Error opening data file lat.traineddata\\n"); sys.exit(1)
    if modo == "trava":
        time.sleep(60)
    if modo == "sem_saida":
        sys.exit(0)
    if modo == "lixo":
        open(saida, "w").write("isto nao e hocr"); sys.exit(0)
    if modo == "fala_muito":
        for i in range(20000):
            sys.stderr.write("Estimating resolution as 312, aviso longo de teste numero %d\\n" % i)
    open(saida, "w", encoding="utf-8").write(HOCR)
''')


@pytest.fixture
def tesseract_de_mentira(tmp_path):
    script = tmp_path / "tesseract_de_mentira.py"
    script.write_text("HOCR = " + repr(HOCR_DE_EXEMPLO) + "\n" + _TESSERACT_DE_MENTIRA, encoding="utf-8")
    modelos = tmp_path / "tessdata"
    (modelos / "script").mkdir(parents=True)
    for nome in ("lat", "ita", "script/Fraktur"):
        (modelos / f"{nome}.traineddata").write_bytes(b"x")
    registro = tmp_path / "registro.json"

    def fabricar(modo: str, **opcoes) -> MotorTesseract:
        return MotorTesseract(comando=[sys.executable, "-X", "utf8", str(script), modo, str(registro)],
                              pasta_dos_modelos=modelos, **opcoes)

    fabricar.registro = registro
    return fabricar


def test_tesseract_ausente_da_aviso_e_nao_quebra(tmp_path):
    motor = MotorTesseract(tmp_path / "nao_existe" / "tesseract.exe")
    inicio = time.perf_counter()
    _indisponivel_com_aviso(motor.segmentar(_pagina()), "não está instalado")
    assert time.perf_counter() - inicio < 2
    assert motor.versao() is None
    motor.fechar()


def test_achar_tesseract_nao_quebra():
    exe = ocr_tesseract.achar_tesseract()
    assert exe is None or exe.is_file()
    assert len(ocr_tesseract.lugares_do_tesseract()) >= 2


def test_modelo_do_idioma_ausente(tesseract_de_mentira):
    r = tesseract_de_mentira("certo").segmentar(_pagina(), idioma="grc")
    _indisponivel_com_aviso(r, "não tem o modelo deste idioma")
    assert "grc" in r.detalhe_tecnico
    r = tesseract_de_mentira("certo").segmentar(_pagina(), idioma="ita+grc")
    _indisponivel_com_aviso(r, "não tem o modelo deste idioma")


@pytest.mark.parametrize("idioma", ["", "lat eng", "../lat", "lat;rm", None, 3])
def test_idioma_invalido(tesseract_de_mentira, idioma):
    _indisponivel_com_aviso(tesseract_de_mentira("certo").segmentar(_pagina(), idioma=idioma),
                            "não tem o modelo deste idioma")
    assert not tesseract_de_mentira.registro.exists()   # nem chamou o programa


def test_tesseract_que_morre(tesseract_de_mentira):
    r = tesseract_de_mentira("morre").segmentar(_pagina())
    _indisponivel_com_aviso(r, "não conseguiu ler esta página")
    assert "traineddata" in r.detalhe_tecnico   # a saída de erro vai para o log


def test_tesseract_que_trava_passa_do_tempo(tesseract_de_mentira):
    inicio = time.perf_counter()
    r = tesseract_de_mentira("trava", tempo_por_pagina=1.5).segmentar(_pagina())
    _indisponivel_com_aviso(r, "demorou demais")
    assert time.perf_counter() - inicio < 15


def test_cancelar_fecha_o_tesseract(tesseract_de_mentira):
    inicio = time.perf_counter()
    r = tesseract_de_mentira("trava").segmentar(_pagina(), cancelar=lambda: time.perf_counter() - inicio > 0.5)
    _indisponivel_com_aviso(r, "Cancelado")
    assert time.perf_counter() - inicio < 15


def test_cancelar_que_quebra_vira_cancelar(tesseract_de_mentira):
    def quebra():
        raise RuntimeError("bug de quem chamou")

    _indisponivel_com_aviso(tesseract_de_mentira("trava").segmentar(_pagina(), cancelar=quebra), "Cancelado")


@pytest.mark.parametrize("modo", ["sem_saida", "lixo"])
def test_saida_errada(tesseract_de_mentira, modo):
    _indisponivel_com_aviso(tesseract_de_mentira(modo).segmentar(_pagina()), "não entendeu")


def test_tesseract_que_escreve_muito_aviso_nao_trava(tesseract_de_mentira):
    # 20.000 linhas na saída de erro (~1,5 MB): sem ler em paralelo, o cano enche.
    inicio = time.perf_counter()
    r = tesseract_de_mentira("fala_muito", tempo_por_pagina=60).segmentar(_pagina())
    assert r.disponivel, (r.motivo, r.detalhe_tecnico)
    assert time.perf_counter() - inicio < 30


def test_resposta_certa_comando_e_cores(tesseract_de_mentira):
    motor = tesseract_de_mentira("certo")
    r = motor.segmentar(_pagina(cor=(10, 20, 30)), idioma="script/Fraktur", dpi=300)
    assert r.disponivel and r.motivo is None
    assert (r.largura, r.altura) == (30, 40)
    assert len(r.linhas) == 3 and len(r.palavras) == 3
    registro = json.loads(tesseract_de_mentira.registro.read_text(encoding="utf-8"))
    # a página chegou sem mudar a cor (o PNG guarda o BGR do programa como a imagem de verdade)
    assert registro["pixel_bgr"] == [10, 20, 30] and registro["forma"] == [40, 30, 3]
    argumentos = registro["argumentos"]
    assert argumentos[0].endswith("pagina.png")
    assert argumentos[2:] == ["-l", "script/Fraktur", "-c", "tessedit_create_hocr=1", "--tessdata-dir",
                              motor.pasta_dos_modelos.as_posix(), "--psm", "3", "--dpi", "300"]
    assert r.extra["dpi"] == 300 and r.extra["idioma"] == "script/Fraktur"


@pytest.mark.parametrize("dpi, esperado", [(None, None), (72, None), (149.9, None), (150, 150),
                                           (200.1, 200), (300, 300), ("lixo", None)])
def test_dpi_so_a_partir_de_150(dpi, esperado):
    argumentos = ocr_tesseract._montar_comando(Path("e.png"), Path("s"), "lat", dpi, Path("m"))
    if esperado is None:
        assert "--dpi" not in argumentos
    else:
        assert argumentos[-2:] == ["--dpi", str(esperado)]


def test_rgb_e_cinza_chegam_certos(tesseract_de_mentira):
    motor = tesseract_de_mentira("certo")
    assert motor.segmentar(_pagina(cor=(10, 20, 30)), ordem="RGB").disponivel
    assert json.loads(tesseract_de_mentira.registro.read_text(encoding="utf-8"))["pixel_bgr"] == [30, 20, 10]
    assert motor.segmentar(np.full((5, 6), 77, np.uint8)).disponivel
    assert json.loads(tesseract_de_mentira.registro.read_text(encoding="utf-8"))["pixel_bgr"] == [77, 77, 77]


def test_imagem_invalida_nao_chama_o_programa(tesseract_de_mentira, tmp_path):
    motor = tesseract_de_mentira("certo")
    for ruim in (np.zeros((10, 10), np.float32), np.zeros((0, 5, 3), np.uint8),
                 np.zeros((4, 4, 2), np.uint8), tmp_path / "nao_existe.png", None):
        r = motor.segmentar(ruim)
        assert not r.disponivel and "não conseguiu ler esta página" in r.motivo
    assert not motor.segmentar(_pagina(), ordem="CMYK").disponivel
    assert not tesseract_de_mentira.registro.exists()


def test_temporarios_sao_apagados(tesseract_de_mentira, tmp_path, monkeypatch):
    pasta = tmp_path / "temporarios"
    pasta.mkdir()
    monkeypatch.setattr(ocr_tesseract.tempfile, "tempdir", str(pasta))
    assert tesseract_de_mentira("certo").segmentar(_pagina()).disponivel
    assert not tesseract_de_mentira("trava", tempo_por_pagina=1).segmentar(_pagina()).disponivel
    assert list(pasta.iterdir()) == []


def test_ler_hocr():
    palavras, linhas = ocr_tesseract.ler_hocr(HOCR_DE_EXEMPLO.encode("utf-8"))
    assert [l.palavras for l in linhas] == [2, 1, 0]
    assert linhas[0].confianca == pytest.approx(80.0)
    assert linhas[2].confianca == 0.0   # linha sem palavra: confiança 0, como na comparação
    assert np.allclose(linhas[1].poligono, [[20, 60], [200, 60], [200, 100], [20, 100]])
    assert linhas[0].poligono.dtype == np.float32
    assert palavras[1].caixa == (120.0, 12.0, 290.0, 40.0) and palavras[1].confianca == 70.0
    with pytest.raises(ValueError):
        ocr_tesseract.ler_hocr(b"<html>nada</html>")


# =====================================================================
# 2. Com o Tesseract de verdade: igual à comparação do 1.3
# =====================================================================

_EXE = ocr_tesseract.achar_tesseract()
precisa_do_tesseract = pytest.mark.skipif(_EXE is None, reason="Tesseract não instalado")
precisa_das_paginas = pytest.mark.skipif(
    not (IMAGENS_13.is_dir() and REFERENCIA_T1.is_dir() and LISTA.is_file()),
    reason="páginas e linhas do 1.3 não estão em saida_teste/ocr-1.3 (fora do git)")

_TEMPOS: dict[str, tuple] = {}


@pytest.fixture(scope="module")
def motor_de_verdade():
    motor = MotorTesseract()
    yield motor
    if _TEMPOS:
        print(f"\n[Tesseract {motor.versao()}] por página (abre o programa a cada página):")
        for pagina, (segundos, linhas, ref, area) in _TEMPOS.items():
            print(f"    {pagina:16s} {segundos:5.2f} s  {linhas:4d} linhas (1.3: {ref:4d})  "
                  f"área em comum {100 * area:6.2f}%")
        valores = sorted(v[0] for v in _TEMPOS.values())
        print(f"    mediana {valores[len(valores) // 2]:.2f} s em {len(valores)} página(s)")


def _mascara(poligonos, largura: int, altura: int) -> np.ndarray:
    mascara = np.zeros((altura, largura), np.uint8)
    for p in poligonos:
        pontos = np.round(np.asarray(p, np.float64)).astype(np.int32).reshape(-1, 1, 2)
        cv2.fillPoly(mascara, [pontos], 1)
    return mascara.astype(bool)


def _dpi_da_comparacao(pagina: str) -> float:
    lista = json.loads(LISTA.read_text(encoding="utf-8"))
    return min(float(lista["paginas"][pagina]["dpi_scan"]), 300.0)


@precisa_do_tesseract
def test_versao_e_a_da_comparacao(motor_de_verdade):
    versao = motor_de_verdade.versao()
    assert versao and versao.startswith(ocr_tesseract.VERSAO_DA_COMPARACAO), versao


@precisa_do_tesseract
@precisa_das_paginas
@pytest.mark.parametrize("pagina", PAGINAS)
def test_mesmas_linhas_da_comparacao_do_13(motor_de_verdade, pagina):
    idioma = IDIOMA_DO_LIVRO[pagina.split("_")[0]]
    if ocr_tesseract.modelos_que_faltam(idioma, ocr_tesseract.PASTA_DOS_MODELOS):
        pytest.skip(f"modelo {idioma} não está em modelos/tessdata")
    referencia = json.loads((REFERENCIA_T1 / f"{pagina}.json").read_text(encoding="utf-8"))
    assert referencia["modelo"] == idioma
    r = motor_de_verdade.segmentar(IMAGENS_13 / f"{pagina}.png", idioma=idioma,
                                   dpi=_dpi_da_comparacao(pagina))
    assert r.disponivel, (r.motivo, r.detalhe_tecnico)
    novo = _mascara([l.poligono for l in r.linhas], r.largura, r.altura)
    antes = _mascara([l["poligono"] for l in referencia["linhas"]], r.largura, r.altura)
    comum = np.count_nonzero(novo & antes)
    if np.count_nonzero(antes) == 0 and np.count_nonzero(novo) == 0:
        area = 1.0     # nenhuma linha nas duas (Horas 11, Graduale 222)
    else:
        area = min(comum / max(1, np.count_nonzero(antes)), comum / max(1, np.count_nonzero(novo)))
    _TEMPOS[pagina] = (r.segundos, len(r.linhas), len(referencia["linhas"]), area)
    assert len(r.linhas) == len(referencia["linhas"]), pagina
    assert area >= AREA_MINIMA, pagina
    # as mesmas confianças por linha (a mesma leitura por baixo)
    assert [round(l.confianca, 3) for l in r.linhas] == [round(l["conf"], 3) for l in referencia["linhas"]]


@precisa_do_tesseract
@precisa_das_paginas
def test_pagina_em_memoria_bgr_da_o_mesmo_que_o_arquivo(motor_de_verdade):
    if ocr_tesseract.modelos_que_faltam("eng", ocr_tesseract.PASTA_DOS_MODELOS):
        pytest.skip("modelo eng não está em modelos/tessdata")
    pagina = IMAGENS_13 / "opusmajus_p020.png"
    pelo_arquivo = motor_de_verdade.segmentar(pagina, idioma="eng", dpi=300)
    bgr = cv2.imdecode(np.fromfile(str(pagina), np.uint8), cv2.IMREAD_COLOR)
    pela_memoria = motor_de_verdade.segmentar(bgr, idioma="eng", dpi=300)
    assert pelo_arquivo.disponivel and pela_memoria.disponivel
    assert [l.poligono.tolist() for l in pelo_arquivo.linhas] == [l.poligono.tolist() for l in pela_memoria.linhas]
