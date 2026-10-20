"""A página dentro da borda preta: o corte sugerido (item 2.13).

Decisões: G7 (a) (05/10/2026, "Sim, desligada de fábrica"); "o programa
sugere o corte, o Kaique aceita" (rodada 4, 08/10); g7-borda-ate-onde
(20/10/2026): "O Kaique escolhe por livro: só o preto, ou até a moldura".

Testes de máquina:
- os campos: desligado de fábrica, "até a moldura" escolhido; projeto antigo
  abre desligado; vão e voltam do arquivo; jeito estranho vale o de fábrica;
- DESLIGADO NADA MUDA: nenhuma das duas contas é chamada, e o corte é o comum;
- "só o preto" (conta do pesquisador): acha a faixa preta de cada lado, não
  tira nada quando não há preto, nunca anda mais de 30%;
- no programa, "só o preto": o corte é a página sem o preto; sem preto, fica
  o corte comum; o corte à mão (a exceção por página) vale como está;
- com a DLL, "até a moldura": o corte fica dentro da página e abraça o
  texto, deixando o preto de fora; com o 2.5 junto, não passa da página.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import borda_preta as bp  # noqa: E402
from core import corte_pelo_conteudo as cc  # noqa: E402
from core import pipeline  # noqa: E402
from core import st_ferramentas  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf, pagina_para_array  # noqa: E402
from core.recortar import detectar_bordas  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402

DPI = 200
LARGURA, ALTURA = 1165, 1654


@pytest.fixture(autouse=True)
def _limpo():
    for g in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()
    yield
    for g in (pipeline._GEOMETRIAS, pipeline._ANGULOS_MEDIDOS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()


def _folha(direita=0, baixo=0, esquerda=0, cima=0):
    """Folha A5 a 200 DPI com um bloco de texto e faixas pretas de scanner."""
    img = np.full((ALTURA, LARGURA, 3), 235, np.uint8)
    for y in range(300, 1300, 34):
        for x in range(200, 900, 52):
            cv2.rectangle(img, (x, y), (x + 38, y + 14), (20, 20, 20), -1)
    if direita:
        img[:, LARGURA - direita:] = 10
    if baixo:
        img[ALTURA - baixo:, :] = 10
    if esquerda:
        img[:, :esquerda] = 10
    if cima:
        img[:cima, :] = 10
    return img


def _pdf(pasta: Path, img, nome="livro") -> str:
    png, caminho = pasta / f"{nome}.png", pasta / f"{nome}.pdf"
    cv2.imwrite(str(png), img)
    doc = fitz.open()
    pg = doc.new_page(width=LARGURA * 72 / DPI, height=ALTURA * 72 / DPI)
    pg.insert_image(pg.rect, filename=str(png))
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _projeto(caminho, **campos):
    campos.setdefault("endireitar", False)
    p = Projeto(caminho_entrada=caminho, qualidade_dpi=DPI, filtro_padrao=ORIGINAL,
                detectar_regioes=False, limpar=False, **campos)
    p.folhas = [ConfigFolha(indice=0, dividir=False)]
    p.paginas = [ConfigPagina(indice=0, folha=0, filtro=ORIGINAL)]
    return p


def _corte(projeto, caminho):
    doc = abrir_pdf(caminho)
    try:
        img = pagina_para_array(doc, 0, dpi=DPI)
    finally:
        doc.close()
    _saida, desenho = pipeline.preparar_metade_e_geometria(img, projeto.folhas[0], projeto.paginas[0],
                                                           projeto, dpi=DPI)
    return img, desenho["recorte"]


# ------------------------------------------------------------------ os campos

def test_desligado_de_fabrica_ate_a_moldura_escolhido_e_projeto_antigo():
    p = Projeto(caminho_entrada="x.pdf")
    assert p.borda_preta is False and p.borda_preta_ate == bp.ATE_A_MOLDURA == bp.JEITO_PADRAO
    dados = p.para_dicionario()
    dados.pop("borda_preta")
    dados.pop("borda_preta_ate")
    antigo = Projeto.de_dicionario(dados)
    assert antigo.borda_preta is False
    p.borda_preta, p.borda_preta_ate = True, bp.SO_O_PRETO
    volta = Projeto.de_dicionario(p.para_dicionario())
    assert volta.borda_preta is True and volta.borda_preta_ate == bp.SO_O_PRETO
    assert bp.jeito_valido("torto") == bp.ATE_A_MOLDURA


# ------------------------------------------------------------ desligado

@pytest.mark.parametrize("ordem", ["endireitar_antes", "cortar_antes"])
def test_desligado_nada_e_chamado_e_o_corte_e_o_comum(tmp_path, monkeypatch, ordem):
    def proibido(*_a, **_k):
        raise AssertionError("conta da borda preta chamada com a opção desligada")

    monkeypatch.setattr(bp, "so_o_preto", proibido)
    monkeypatch.setattr(cc, "medir", proibido)
    caminho = _pdf(tmp_path, _folha(direita=150, baixo=120))
    projeto = _projeto(caminho, ordem_do_preparo=ordem)
    img, recorte = _corte(projeto, caminho)
    assert tuple(recorte) == pytest.approx(detectar_bordas(img, dpi=DPI).tupla)


# ------------------------------------------------------------ "só o preto"

def test_so_o_preto_acha_as_faixas():
    x0, y0, x1, y1 = bp.so_o_preto(_folha(direita=150, baixo=120, esquerda=40, cima=30))
    assert x0 == pytest.approx(40, abs=4) and y0 == pytest.approx(30, abs=4)
    assert x1 == pytest.approx(LARGURA - 150, abs=4) and y1 == pytest.approx(ALTURA - 120, abs=4)


def test_so_o_preto_sem_preto_nao_tira_nada_e_nunca_passa_de_30_por_cento():
    assert bp.so_o_preto(_folha()) == (0.0, 0.0, float(LARGURA), float(ALTURA))
    x0, _y0, _x1, _y1 = bp.so_o_preto(_folha(esquerda=600))
    assert x0 <= int(LARGURA * bp.ANDA_NO_MAXIMO)
    cinza = cv2.cvtColor(_folha(direita=150), cv2.COLOR_BGR2GRAY)
    assert bp.so_o_preto(cinza)[2] == pytest.approx(LARGURA - 150, abs=4)


def test_no_programa_so_o_preto_corta_o_preto(tmp_path):
    caminho = _pdf(tmp_path, _folha(direita=150, baixo=120))
    projeto = _projeto(caminho, borda_preta=True, borda_preta_ate=bp.SO_O_PRETO)
    _img, (x, y, w, h) = _corte(projeto, caminho)
    assert (x, y) == pytest.approx((0.0, 0.0), abs=0.005)
    assert (x + w) * LARGURA == pytest.approx(LARGURA - 150, abs=5)
    assert (y + h) * ALTURA == pytest.approx(ALTURA - 120, abs=5)


def test_no_programa_so_o_preto_sem_preto_fica_o_corte_comum(tmp_path):
    caminho = _pdf(tmp_path, _folha())
    projeto = _projeto(caminho, borda_preta=True, borda_preta_ate=bp.SO_O_PRETO)
    img, recorte = _corte(projeto, caminho)
    assert tuple(recorte) == pytest.approx(detectar_bordas(img, dpi=DPI).tupla)


def test_corte_a_mao_e_a_excecao_da_pagina(tmp_path):
    caminho = _pdf(tmp_path, _folha(direita=150))
    projeto = _projeto(caminho, borda_preta=True)
    projeto.paginas[0].recorte = (0.1, 0.1, 0.5, 0.5)
    _img, recorte = _corte(projeto, caminho)
    assert tuple(recorte) == pytest.approx((0.1, 0.1, 0.5, 0.5))


# ------------------------------------------------------------ com a DLL

precisa_da_dll = pytest.mark.skipif(
    st_ferramentas.padrao().funcao("st_ferramentas_caixas") is None,
    reason="sem a DLL do ScanTailor (st_ferramentas)")


@precisa_da_dll
@pytest.mark.parametrize("com_o_conteudo", [False, True])
def test_ate_a_moldura_fica_dentro_da_pagina_e_tira_o_preto(tmp_path, com_o_conteudo):
    """'Até a moldura': o corte abraça o texto (+1 mm) e o preto da direita e de
    baixo fica de fora; com o 2.5 junto, o tamanho do livro não passa da página."""
    caminho = _pdf(tmp_path, _folha(direita=150, baixo=120, esquerda=60, cima=50))
    projeto = _projeto(caminho, borda_preta=True, borda_preta_ate=bp.ATE_A_MOLDURA,
                       cortar_pelo_conteudo=com_o_conteudo)
    _img, (x, y, w, h) = _corte(projeto, caminho)
    x0, y0, x1, y1 = x * LARGURA, y * ALTURA, (x + w) * LARGURA, (y + h) * ALTURA
    assert x0 >= 60 and y0 >= 50
    assert x1 <= LARGURA - 150 and y1 <= ALTURA - 120
    assert x0 <= 200 and y0 <= 300 and x1 >= 886 and y1 >= 1280       # o texto inteiro dentro
