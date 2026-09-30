"""Testes da comparação automática entre os OCRs (core/ocr_comparar.py), item 1.3.

DUAS PARTES
    1. Sintéticos (rodam sempre, em menos de 1 s): páginas de mentira com
       linhas desenhadas à mão: iguais, com uma palavra a mais, com uma
       letra a mais, com contornos de jeitos diferentes, linhas perdidas, OCR
       que falhou, 1 e 3 OCRs, entrada quebrada. Nenhuma exceção sai.
    2. As 22 páginas do 1.3, com os resultados das pontes guardados por
       relatorios/fase1-1.3-comparar-ocr-2026-09-29/scripts/rodar_pontes.py
       em saida_teste/ocr-comparar (fora do git; pulado se faltar): o par de
       fábrica (docTR + Kraken) manda para revisar exatamente as 10 páginas
       calibradas. Com OCR_22=1, roda também as pontes de verdade (docTR e
       Kraken, ~5 min) e confere que dão a mesma decisão.

ARRISCADO MUDAR
    REVISAR_FABRICA: é o resultado da calibração de 29/09/2026 (ver o
    relatório da pasta acima). Mudou um limite em core/ocr_comparar.py e este
    teste quebrou: refaça a calibração e diga o que mudou, página a página.
"""

from __future__ import annotations

import ast
import json
import os
import time
from pathlib import Path

import numpy as np
import pytest

from core import ocr_comparar
from core.ocr_comparar import Comparacao, comparar
from core.ocr_comum import LinhaOCR, ResultadoOCR, de_dict, indisponivel, para_dict, retangulo

RAIZ = Path(__file__).resolve().parent.parent
CACHE = RAIZ / "saida_teste" / "ocr-comparar"
IMAGENS_13 = RAIZ / "saida_teste" / "ocr-1.3" / "imagens"

LARGURA, ALTURA = 1000, 1400
H = 40   # altura das linhas de mentira


def _linhas_de_texto(n=10, x0=100, x1=900, y0=100, passo=60, h=H):
    return [(x0, y0 + i * passo, x1, y0 + i * passo + h) for i in range(n)]


def _resultado(motor, caixas, *, perdidas=0, largura=LARGURA, altura=ALTURA, poligonos=None):
    linhas = [LinhaOCR(retangulo(*c)) for c in caixas]
    linhas += [LinhaOCR(np.asarray(p, np.float32)) for p in (poligonos or [])]
    return ResultadoOCR(motor, linhas, perdidas=perdidas, largura=largura, altura=altura)


def _ondulado(x0, y0, x1, y1, passo=25, amplitude=4):
    """Um contorno "de Kraken": justo, com a borda ondulada, um pouco mais alto que o retângulo."""
    cima = [(x, y0 - 3 + (amplitude if (i % 2) else 0)) for i, x in enumerate(range(x0, x1 + 1, passo))]
    baixo = [(x, y1 + 3 - (amplitude if (i % 2) else 0)) for i, x in enumerate(range(x1, x0 - 1, -passo))]
    return cima + baixo


# =====================================================================
# 1. Sintéticos
# =====================================================================

def test_iguais_concordam_e_a_mascara_e_o_texto():
    caixas = _linhas_de_texto()
    c = comparar([_resultado("doctr", caixas), _resultado("kraken", caixas)])
    assert isinstance(c, Comparacao)
    assert c.comparou and c.concorda and not c.para_revisar
    assert c.motivos == [] and c.zonas == []
    assert c.mascara.shape == (ALTURA, LARGURA) and c.mascara.dtype == bool
    x0, y0, x1, y1 = caixas[0]
    assert c.mascara[y0 + 5, x0 + 5] and not c.mascara[5, 5]
    assert len(c.linhas) == 20 and c.motores == ("doctr", "kraken")


def test_contornos_de_jeitos_diferentes_nao_contam():
    # docTR: retângulos; Kraken: contornos ondulados, mais altos, e cada linha
    # partida em 3 pedaços (o Kraken separa colunas). Mesmo texto: concorda.
    caixas = _linhas_de_texto()
    pedacos = []
    for x0, y0, x1, y1 in caixas:
        for a, b in ((x0, 360), (380, 640), (660, x1)):
            pedacos.append(_ondulado(a, y0, b, y1))
    c = comparar([_resultado("doctr", caixas), _resultado("kraken", [], poligonos=pedacos)])
    assert c.concorda, c.motivos
    assert c.medidas["linhas"] == {"doctr": 10, "kraken": 30}
    assert c.medidas["linhas_partidas"]["doctr/kraken"] == 10   # medido, mas não decide


def test_uma_palavra_a_mais_manda_para_revisar():
    caixas = _linhas_de_texto()
    extra = (400, 1200, 560, 1200 + H)          # uma palavra no pé da página (4 x 1 alturas de linha)
    c = comparar([_resultado("doctr", caixas + [extra]), _resultado("kraken", caixas)])
    assert c.para_revisar
    assert c.motivos == ["O docTR achou texto nesta área e o Kraken não: confira se há texto ou mancha."]
    assert len(c.zonas) == 1
    zona = c.zonas[0]
    assert zona.acharam == ("doctr",) and zona.nao_acharam == ("kraken",)
    x0, y0, x1, y1 = zona.caixa
    assert x0 <= 410 and x1 >= 550 and y0 <= 1210 and y1 >= 1230
    assert zona.tamanho >= ocr_comparar.AREA_MINIMA
    # a palavra que só um viu fica FORA do texto combinado
    assert not c.mascara[1220, 480]


def test_varias_zonas_do_outro_lado_viram_uma_frase_com_a_contagem():
    caixas = _linhas_de_texto(n=5)
    extras = [(100, 900, 260, 900 + H), (500, 1000, 700, 1000 + H)]
    c = comparar([_resultado("doctr", caixas), _resultado("kraken", caixas + extras)])
    assert c.motivos == ["O Kraken achou texto em 2 lugares e o docTR não: confira se há texto ou mancha."]


def test_uma_letra_a_mais_nao_manda_para_revisar():
    caixas = _linhas_de_texto()
    letra = (500, 1200, 530, 1200 + H)            # uma letra solta (menos de 1 altura de linha ao quadrado)
    c = comparar([_resultado("doctr", caixas + [letra]), _resultado("kraken", caixas)])
    assert c.concorda, c.motivos
    assert 0 < c.medidas["maior_zona"] < ocr_comparar.AREA_MINIMA


def test_linha_perdida_avisada_manda_para_revisar():
    caixas = _linhas_de_texto()
    c = comparar([_resultado("doctr", caixas), _resultado("kraken", caixas, perdidas=8)])
    assert c.para_revisar
    assert c.motivos == ["O Kraken avisou que não conseguiu desenhar 8 linhas nesta página: confira se falta texto."]
    um = comparar([_resultado("doctr", caixas), _resultado("kraken", caixas, perdidas=1)])
    assert "desenhar 1 linha nesta" in um.motivos[0]


def test_ocr_que_falhou_manda_para_revisar():
    caixas = _linhas_de_texto()
    falhou = indisponivel("kraken", "O detector de linhas do Kraken demorou demais e foi fechado.", "x")
    c = comparar([_resultado("doctr", caixas), falhou])
    assert c.para_revisar and not c.comparou
    assert c.motivos == ["O Kraken não conseguiu ler esta página, então não deu para comparar."]
    assert c.mascara is not None and c.mascara.any()   # a máscara é a do que leu
    assert c.motores == ("doctr",)


def test_um_ocr_so_nao_compara():
    caixas = _linhas_de_texto()
    c = comparar([_resultado("doctr", caixas)])
    assert not c.comparou and c.concorda and c.motivos == []
    assert c.mascara[caixas[0][1] + 5, caixas[0][0] + 5]
    assert len(c.linhas) == 10
    sozinho_perdeu = comparar([_resultado("kraken", caixas, perdidas=2)])
    assert sozinho_perdeu.para_revisar and not sozinho_perdeu.comparou


def test_nenhum_resultado():
    c = comparar([])
    assert c.concorda and c.mascara is None and c.motores == ()
    dois_falharam = comparar([indisponivel("doctr", "a"), indisponivel("kraken", "b")])
    assert dois_falharam.para_revisar and dois_falharam.mascara is None and len(dois_falharam.motivos) == 2


def test_pagina_sem_texto_nos_dois_concorda():
    c = comparar([_resultado("doctr", []), _resultado("kraken", [])])
    assert c.concorda and c.comparou
    assert c.mascara.shape == (ALTURA, LARGURA) and not c.mascara.any()


def test_so_um_acha_a_pagina_inteira():
    caixas = _linhas_de_texto()
    c = comparar([_resultado("doctr", caixas), _resultado("tesseract", [])])
    assert c.para_revisar
    assert c.motivos == ["O docTR achou texto em 10 lugares e o Tesseract não: confira se há texto ou mancha."]
    assert not c.mascara.any()


def test_tres_ocrs_voto_da_maioria():
    caixas = _linhas_de_texto(n=5)
    so_do_tesseract = (100, 1200, 700, 1200 + H)    # só o Tesseract: fica fora
    dos_dois = (100, 1000, 700, 1000 + H)           # docTR e Kraken, sem o Tesseract: entra
    c = comparar([_resultado("doctr", caixas + [dos_dois]), _resultado("kraken", caixas + [dos_dois]),
                  _resultado("tesseract", caixas + [so_do_tesseract])])
    assert c.para_revisar and c.comparou
    assert c.mascara[1020, 400] and not c.mascara[1220, 400]
    assert set(c.motivos) == {
        "O docTR e o Kraken acharam texto nesta área e o Tesseract não: confira se há texto ou mancha.",
        "O Tesseract achou texto nesta área e o docTR e o Kraken não: confira se há texto ou mancha.",
    }


def test_resultados_em_escalas_diferentes():
    caixas = _linhas_de_texto()
    metade = [tuple(v / 2 for v in c) for c in caixas]
    c = comparar([_resultado("doctr", caixas),
                  _resultado("kraken", metade, largura=LARGURA // 2, altura=ALTURA // 2)])
    assert c.concorda, c.motivos
    assert c.mascara.shape == (ALTURA, LARGURA)


def test_entrada_quebrada_nao_levanta_excecao():
    ruim = ResultadoOCR("kraken", [LinhaOCR(np.array([[np.nan, 1], [2, 3], [4, 5]], np.float32))],
                        largura=LARGURA, altura=ALTURA)
    for entrada in ([_resultado("doctr", _linhas_de_texto()), ruim],
                    [object(), object()],
                    [_resultado("doctr", [], largura=0, altura=0), _resultado("kraken", [], largura=0, altura=0)]):
        c = comparar(entrada)
        assert isinstance(c, Comparacao)
        if entrada[1] is ruim:
            assert c.medidas["linhas_invalidas"] == 1
        if not c.concorda:
            assert c.motivos
    quebrado = comparar([object(), object()])
    assert quebrado.para_revisar and "Não deu para comparar" in quebrado.motivos[0]
    assert "erro" in quebrado.medidas


def test_para_dict_e_de_dict_ida_e_volta():
    r = ResultadoOCR("kraken", [LinhaOCR(retangulo(1, 2, 30, 12), None, 0, np.array([[1, 10], [30, 10]], np.float32)),
                                LinhaOCR(retangulo(5, 20, 9, 30), 0.5, 2)],
                     perdidas=3, segundos=1.5, largura=40, altura=50, extra={"regioes": {"text": 1}})
    volta = de_dict(json.loads(json.dumps(para_dict(r))))
    assert volta.motor == "kraken" and volta.perdidas == 3 and volta.extra == {"regioes": {"text": 1}}
    assert np.array_equal(volta.linhas[0].poligono, r.linhas[0].poligono)
    assert np.array_equal(volta.linhas[0].linha_de_base, r.linhas[0].linha_de_base)
    assert volta.linhas[1].confianca == 0.5 and volta.linhas[1].linha_de_base is None
    assert volta.palavras is None
    fora = de_dict(para_dict(indisponivel("doctr", "motivo", "detalhe")))
    assert not fora.disponivel and fora.motivo == "motivo"


def test_core_nao_importa_ui_nem_qt():
    for arquivo in ("ocr_comparar.py", "ocr_comum.py", "ocr_kraken.py"):
        arvore = ast.parse((RAIZ / "core" / arquivo).read_text(encoding="utf-8"))
        nomes = set()
        for no in ast.walk(arvore):
            if isinstance(no, ast.Import):
                nomes |= {a.name for a in no.names}
            elif isinstance(no, ast.ImportFrom) and no.module:
                nomes.add(no.module)
        assert not any(n.split(".")[0] in ("ui", "PySide6", "PyQt5", "PyQt6") for n in nomes), (arquivo, nomes)


# =====================================================================
# 2. As 22 páginas do 1.3
# =====================================================================

PAGINAS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010",
    "escola_p007", "horas_p011", "horas_p013", "horas_p047",
    "opusmajus_p011", "opusmajus_p003", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "horas_p026", "horas_p027", "escola_p035",
    "rhetorica_p018", "siebmacher_p009", "palatino_p057",
    "graduale_p221", "graduale_p222", "graduale_p223",
]
# Calibração de 29/09/2026 com docTR + Kraken: as páginas com erro conhecido
# vão para revisar (o Graduale 223, onde os dois perdem o MESMO texto, não
# dá para pegar comparando), e as boas não.
REVISAR_FABRICA = {"palatino_p005", "palatino_p007", "palatino_p009", "palatino_p057", "horas_p011",
                   "horas_p013", "opusmajus_p003", "opusmajus_p165", "opusmajus_p256", "siebmacher_p009"}

tem_cache = pytest.mark.skipif(
    not all((CACHE / m / f"{p}.json").is_file() for m in ("doctr", "kraken") for p in PAGINAS),
    reason="resultados das pontes não guardados em saida_teste/ocr-comparar (rode rodar_pontes.py)")


def _ler(motor, pagina):
    return de_dict(json.loads((CACHE / motor / f"{pagina}.json").read_text(encoding="utf-8")))


@tem_cache
@pytest.mark.parametrize("pagina", PAGINAS)
def test_par_de_fabrica_nas_22_paginas(pagina):
    inicio = time.perf_counter()
    c = comparar([_ler("doctr", pagina), _ler("kraken", pagina)])
    assert time.perf_counter() - inicio < 5
    assert c.comparou
    assert c.para_revisar == (pagina in REVISAR_FABRICA), (pagina, c.motivos, c.medidas.get("maior_zona"))
    if c.para_revisar:
        assert c.motivos and all(m.endswith(".") for m in c.motivos)
    if pagina == "opusmajus_p256":
        assert any("8 linhas" in m for m in c.motivos)
    assert c.mascara is not None and c.mascara.shape == (_ler("doctr", pagina).altura, _ler("doctr", pagina).largura)


@pytest.mark.skipif(os.environ.get("OCR_22") != "1", reason="só com OCR_22=1 (roda o Kraken, ~5 min)")
@pytest.mark.skipif(not IMAGENS_13.is_dir(), reason="páginas do 1.3 fora do disco")
def test_pontes_de_verdade_dao_a_mesma_decisao():
    from core.ocr_doctr import CAMINHO_MODELO, DetectorDoctr
    from core.ocr_kraken import MotorKraken, achar_pasta_do_motor

    if not CAMINHO_MODELO.is_file() or achar_pasta_do_motor() is None:
        pytest.skip("docTR ou Kraken ausente")
    with DetectorDoctr() as doctr, MotorKraken() as kraken:
        for pagina in PAGINAS:
            imagem = IMAGENS_13 / f"{pagina}.png"
            c = comparar([doctr.segmentar(imagem), kraken.segmentar(imagem)])
            assert c.para_revisar == (pagina in REVISAR_FABRICA), (pagina, c.motivos)
