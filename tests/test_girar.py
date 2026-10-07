"""Girar a folha de 90 em 90 graus, com "aplicar em" (item 2.3; core/girar.py).

Pedido do Samuel (conferencia 14, G1): botoes de girar e menu/teclas, com
"aplicar em: so esta / todas / daqui em diante / so as pares / so as
impares", como o ScanTailor. Testes de maquina (pedido da gerente, 06/10):

1. as contas (quais folhas, que rotacao) - core/girar.py;
2. o giro entra no desfazer/refazer (cada folha volta ao giro que tinha) e
   no projeto.json; projeto antigo, sem o campo, abre sem giro;
3. as zonas da aba Marcar acompanham o giro: ficam sobre o mesmo pedaco do
   papel, na previa e no PDF (e sem o acompanhar elas andariam);
4. depois do giro, o corte e o endireitar sao refeitos, e a previa e o PDF
   dao a mesma pagina.

As paginas sao sinteticas (as de tests/test_zonas_na_folha.py: texto
levemente torto e um quadrado vermelho que serve de marco no papel), para
nao depender do gabarito, que fica fora do git.
"""

from __future__ import annotations

import copy
import json

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from core import girar, pipeline  # noqa: E402
from core import zonas_na_folha as zf  # noqa: E402
from core.selecao import GRAVURA  # noqa: E402
from historico_acoes import HistoricoAcoes, aplicar, montar_acao  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_zonas_na_folha import (  # noqa: E402
    _caixa,
    _cobertura,
    _desenhar,
    _projeto,
    _vermelho,
    _zona_sobre_o_vermelho,
    pdf,  # noqa: F401 - fixture
)


# ---------------------------------------------------------------------------
# 1. As contas
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alcance, esperado", [
    (girar.ALCANCE_ESTA, [2]),
    (girar.ALCANCE_TODAS, [0, 1, 2, 3, 4, 5, 6]),
    (girar.ALCANCE_DAQUI, [2, 3, 4, 5, 6]),
    (girar.ALCANCE_PARES, [1, 3, 5]),          # folhas 2, 4 e 6 da tela
    (girar.ALCANCE_IMPARES, [0, 2, 4, 6]),     # folhas 1, 3, 5 e 7 da tela
    ("nao existe", [2]),                       # nunca o livro inteiro por engano
])
def test_quais_folhas_o_giro_pega(alcance, esperado):
    assert girar.folhas_do_alcance(7, 2, alcance) == esperado


def test_alcance_em_livro_vazio_ou_folha_fora():
    assert girar.folhas_do_alcance(0, 0, girar.ALCANCE_TODAS) == []
    assert girar.folhas_do_alcance(3, 9, girar.ALCANCE_ESTA) == [2]


@pytest.mark.parametrize("antes, giro, depois", [
    (0, girar.GIRO_DIREITA, 90),
    (0, girar.GIRO_ESQUERDA, 270),
    (0, girar.GIRO_MEIA_VOLTA, 180),
    (90, girar.GIRO_ESQUERDA, 0),
    (270, girar.GIRO_DIREITA, 0),
    (90, girar.GIRO_MEIA_VOLTA, 270),
    (180, girar.GIRO_MEIA_VOLTA, 0),
    (44, girar.GIRO_DIREITA, 90),              # valor estranho: o quarto mais perto
])
def test_nova_rotacao(antes, giro, depois):
    assert girar.nova_rotacao(antes, giro) == depois


def test_quatro_quartos_voltam_ao_comeco_e_esquerda_desfaz_direita():
    r = 0
    for _ in range(4):
        r = girar.nova_rotacao(r, girar.GIRO_DIREITA)
    assert r == 0
    assert girar.nova_rotacao(girar.nova_rotacao(0, girar.GIRO_DIREITA), girar.GIRO_ESQUERDA) == 0


def test_os_textos_sao_em_portugues_e_sem_emoji():
    textos = list(girar.NOMES_DOS_GIROS.values()) + list(girar.NOMES_DOS_ALCANCES.values())
    assert "só as ímpares" in textos and "¼ à esquerda" in textos
    for texto in textos:
        assert all(ord(c) < 0x2000 for c in texto), texto
    assert girar.descricao_do_giro(girar.GIRO_DIREITA, girar.ALCANCE_TODAS, 0, 12) \
        == "Girar ¼ à direita: todas as 12 folhas, viradas como a folha 1"
    assert girar.descricao_do_giro(girar.GIRO_ESQUERDA, girar.ALCANCE_ESTA, 4, 1) \
        == "Girar ¼ à esquerda: a folha 5"


# ---------------------------------------------------------------------------
# 2. Desfazer / refazer e o projeto.json
# ---------------------------------------------------------------------------

def _livro(rotacoes) -> Projeto:
    projeto = Projeto(caminho_entrada="x.pdf", nome="giro")
    projeto.folhas = [ConfigFolha(indice=i, dividir=False, rotacao=r) for i, r in enumerate(rotacoes)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(len(rotacoes))]
    return projeto


def _girar(projeto, historico, giro, alcance, atual=0):
    indices = girar.folhas_do_alcance(len(projeto.folhas), atual, alcance)
    campos = girar.campos_do_giro(projeto.folhas, indices, giro, atual)
    acao = montar_acao(projeto, "girar", "folha", indices, campos,
                       girar.descricao_do_giro(giro, alcance, atual, len(indices)))
    aplicar(projeto, acao, acao.depois)
    historico.registrar(acao)


def test_girar_todas_desfaz_cada_folha_para_o_giro_que_tinha(tmp_path):
    """Decisao do Samuel (06/10/2026): no "aplicar em", todas as folhas
    escolhidas ficam viradas como a folha da vez (antes cada uma girava a
    partir de onde estava). O desfazer devolve a cada uma o giro dela."""
    projeto = _livro([0, 90, 180, 270, 0])
    historico = HistoricoAcoes(tmp_path / "proj")
    _girar(projeto, historico, girar.GIRO_DIREITA, girar.ALCANCE_TODAS)
    assert [f.rotacao for f in projeto.folhas] == [90, 90, 90, 90, 90]
    _girar(projeto, historico, girar.GIRO_MEIA_VOLTA, girar.ALCANCE_PARES, atual=1)
    assert [f.rotacao for f in projeto.folhas] == [90, 270, 90, 270, 90]
    assert historico.descricao_desfazer() == \
        "Desfazer: Girar meia volta: as 2 folhas pares, viradas como a folha 2"

    historico.desfazer(projeto)
    assert [f.rotacao for f in projeto.folhas] == [90, 90, 90, 90, 90]
    historico.desfazer(projeto)
    assert [f.rotacao for f in projeto.folhas] == [0, 90, 180, 270, 0]
    historico.refazer(projeto)
    assert [f.rotacao for f in projeto.folhas] == [90, 90, 90, 90, 90]


# Decisao do Samuel (06/10/2026), pergunta "Aplicar em todas: como as outras
# folhas giram?", resposta "Todas ficam viradas como a folha da vez" (como o
# ScanTailor). Folhas com giros diferentes antes; a folha da vez e a 3
# (indice 2, de cabeca para baixo), girada 1/4 a direita: ela vai a 270 e
# todas as escolhidas terminam em 270. As de fora nao mudam.
ANTES = [0, 90, 180, 270, 0, 90]


@pytest.mark.parametrize("alcance, esperado", [
    (girar.ALCANCE_TODAS, [270, 270, 270, 270, 270, 270]),
    (girar.ALCANCE_DAQUI, [0, 90, 270, 270, 270, 270]),
    (girar.ALCANCE_IMPARES, [270, 90, 270, 270, 270, 90]),
    # so a conta: na tela, "so as pares" na folha 3 (impar) avisa e nao gira
    # (decisao do Samuel, 06/10/2026; testes no fim deste arquivo)
    (girar.ALCANCE_PARES, [0, 270, 180, 270, 0, 270]),
    (girar.ALCANCE_ESTA, [0, 90, 270, 270, 0, 90]),
])
def test_aplicar_em_copia_o_giro_final_da_folha_da_vez(tmp_path, alcance, esperado):
    projeto = _livro(ANTES)
    historico = HistoricoAcoes(tmp_path / "proj")
    _girar(projeto, historico, girar.GIRO_DIREITA, alcance, atual=2)
    assert [f.rotacao for f in projeto.folhas] == esperado
    historico.desfazer(projeto)
    assert [f.rotacao for f in projeto.folhas] == ANTES, "o desfazer devolve o giro de cada uma"


def test_so_esta_continua_girando_a_partir_de_onde_esta(tmp_path):
    projeto = _livro(ANTES)
    historico = HistoricoAcoes(tmp_path / "proj")
    _girar(projeto, historico, girar.GIRO_ESQUERDA, girar.ALCANCE_ESTA, atual=1)
    assert [f.rotacao for f in projeto.folhas] == [0, 0, 180, 270, 0, 90]
    _girar(projeto, historico, girar.GIRO_MEIA_VOLTA, girar.ALCANCE_ESTA, atual=1)
    assert [f.rotacao for f in projeto.folhas] == [0, 180, 180, 270, 0, 90]


def test_campos_do_giro_um_valor_igual_para_cada_folha_escolhida():
    projeto = _livro(ANTES)
    campos = girar.campos_do_giro(projeto.folhas, [0, 1, 3, 9], girar.GIRO_MEIA_VOLTA, 3)
    # a folha da vez (indice 3) esta em 270; meia volta = 90. A 9 nao existe.
    assert campos == {"rotacao": {"0": 90, "1": 90, "3": 90}}
    assert girar.rotacao_final(projeto.folhas, girar.GIRO_MEIA_VOLTA, 3) == 90


def test_o_giro_e_o_desfazer_sobrevivem_a_fechar_e_abrir(tmp_path):
    projeto = _livro([0, 0, 0])
    historico = HistoricoAcoes(tmp_path / "proj")
    _girar(projeto, historico, girar.GIRO_ESQUERDA, girar.ALCANCE_DAQUI, atual=1)
    assert [f.rotacao for f in projeto.folhas] == [0, 270, 270]

    reaberto = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert [f.rotacao for f in reaberto.folhas] == [0, 270, 270]
    historico = HistoricoAcoes(tmp_path / "proj")
    historico.carregar()
    historico.desfazer(reaberto)
    assert [f.rotacao for f in reaberto.folhas] == [0, 0, 0]
    historico.refazer(reaberto)
    assert [f.rotacao for f in reaberto.folhas] == [0, 270, 270]


def test_projeto_antigo_sem_o_campo_abre_sem_giro():
    dados = json.loads(json.dumps(_livro([0, 0]).para_dicionario()))
    for folha in dados["folhas"]:
        folha.pop("rotacao")
    projeto = Projeto.de_dicionario(dados)
    assert [f.rotacao for f in projeto.folhas] == [0, 0]


# ---------------------------------------------------------------------------
# 3. As zonas da aba Marcar acompanham o giro
# ---------------------------------------------------------------------------

def _girada(projeto, giro):
    projeto.folhas[0].rotacao = girar.nova_rotacao(projeto.folhas[0].rotacao, giro)


@pytest.mark.parametrize("giros", [
    [girar.GIRO_DIREITA],
    [girar.GIRO_ESQUERDA],
    [girar.GIRO_MEIA_VOLTA],
    [girar.GIRO_DIREITA, girar.GIRO_DIREITA, girar.GIRO_ESQUERDA],
])
def test_girar_mantem_a_zona_sobre_o_mesmo_pedaco_do_papel(pdf, giros):
    projeto = _projeto(pdf, limpar=False)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    assert _cobertura(pdf, projeto) > 0.9                 # comeca sobre o vermelho
    for giro in giros:
        _girada(projeto, giro)
        assert _cobertura(pdf, projeto) > 0.85            # continua sobre ele
    assert projeto.paginas[0].geometria_das_zonas["rotacao"] == projeto.folhas[0].rotacao


def test_sem_o_acompanhar_a_zona_andava_com_o_giro(pdf, monkeypatch):
    """Prova de que o teste acima pega o defeito: sem levar as zonas, a zona
    fica parada na tela e o vermelho gira para outro lugar."""
    monkeypatch.setattr(zf, "acompanhar", lambda pagina, geometria: False)
    projeto = _projeto(pdf, limpar=False)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    _girada(projeto, girar.GIRO_DIREITA)
    assert _cobertura(pdf, projeto) < 0.3


def test_girar_e_desfazer_devolve_as_zonas(pdf, tmp_path):
    projeto = _projeto(pdf, limpar=False)
    zonas = _zona_sobre_o_vermelho(pdf)
    projeto.paginas[0].selecao = copy.deepcopy(zonas)
    _desenhar(pdf, projeto)
    historico = HistoricoAcoes(tmp_path / "proj")
    _girar(projeto, historico, girar.GIRO_DIREITA, girar.ALCANCE_ESTA)
    _desenhar(pdf, projeto)
    assert projeto.paginas[0].selecao != zonas            # a zona foi levada
    assert _cobertura(pdf, projeto) > 0.85

    # grava com a pagina girada, reabre: as zonas continuam no lugar
    reaberto = Projeto.de_dicionario(json.loads(json.dumps(projeto.para_dicionario())))
    assert reaberto.folhas[0].rotacao == 90
    assert _cobertura(pdf, reaberto) > 0.85

    historico.desfazer(projeto)
    _desenhar(pdf, projeto)
    assert np.allclose(projeto.paginas[0].selecao[0]["pontos"], zonas[0]["pontos"], atol=1e-9)
    historico.refazer(projeto)
    assert _cobertura(pdf, projeto) > 0.85


def test_a_zona_vale_no_pdf_depois_de_girar(pdf, tmp_path, monkeypatch):
    """No PDF final o filtro recebe a pagina girada com a zona sobre o
    vermelho (a pagina que o filtro recebe ainda esta sem filtro)."""
    vistos = []
    original = pipeline.aplicar_filtro_com_selecao

    def espiao(img, filtro, selecao, *args, **kwargs):
        vistos.append((img.copy(), selecao))
        return original(img, filtro, selecao, *args, **kwargs)

    monkeypatch.setattr(pipeline, "aplicar_filtro_com_selecao", espiao)
    projeto = _projeto(pdf)
    projeto.paginas[0].selecao = _zona_sobre_o_vermelho(pdf)
    _desenhar(pdf, projeto)
    _girada(projeto, girar.GIRO_ESQUERDA)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    vistos.clear()
    pipeline.processar(projeto)
    assert len(vistos) == 1
    img, selecao = vistos[0]
    assert img.shape[0] < img.shape[1], "a folha em pe girada 1/4 fica deitada"
    vermelho = _vermelho(img)
    zona = selecao.mascara(img.shape[0], img.shape[1], GRAVURA)
    assert vermelho.sum() > 0
    assert (vermelho & zona).sum() / (vermelho | zona).sum() > 0.85


# ---------------------------------------------------------------------------
# 4. Depois do giro: corte e endireitar refeitos; previa = PDF
# ---------------------------------------------------------------------------

def _pagina_do_pdf(caminho, dpi=100) -> np.ndarray:
    doc = fitz.open(str(caminho))
    try:
        pix = doc[0].get_pixmap(dpi=dpi)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, pix.n)[..., :3]
        return img[..., ::-1].copy()           # RGB -> BGR, como o programa
    finally:
        doc.close()


@pytest.mark.parametrize("giro", list(girar.GIROS))
def test_previa_e_pdf_dao_a_mesma_pagina_girada(pdf, tmp_path, giro):
    projeto = _projeto(pdf, limpar=False)
    _girada(projeto, giro)
    pipeline._GEOMETRIAS.clear()
    previa = _desenhar(pdf, projeto, dpi=100)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    final = _pagina_do_pdf(projeto.caminho_saida, dpi=100)

    # a mesma proporcao (o mesmo corte) e o vermelho no mesmo lugar
    assert abs(previa.shape[1] / previa.shape[0] - final.shape[1] / final.shape[0]) < 0.01
    caixa_previa, caixa_final = _caixa(_vermelho(previa)), _caixa(_vermelho(final))
    assert np.allclose(caixa_previa, caixa_final, atol=0.01), (caixa_previa, caixa_final)


@pytest.mark.parametrize("giro", list(girar.GIROS))
def test_o_vermelho_gira_junto_com_a_folha(pdf, giro):
    """O corte e o endireitar sao refeitos na folha girada: o marco no papel
    aparece onde o giro o leva (com a folga do corte, uns poucos %)."""
    projeto = _projeto(pdf, limpar=False)
    x0, y0, x1, y1 = _caixa(_vermelho(_desenhar(pdf, projeto)))
    _girada(projeto, giro)
    girada = _desenhar(pdf, projeto)
    esperado = {
        girar.GIRO_DIREITA: (1 - y1, x0, 1 - y0, x1),      # sentido do relogio
        girar.GIRO_ESQUERDA: (y0, 1 - x1, y1, 1 - x0),
        girar.GIRO_MEIA_VOLTA: (1 - x1, 1 - y1, 1 - x0, 1 - y0),
    }[giro]
    assert np.allclose(_caixa(_vermelho(girada)), esperado, atol=0.04)
    if giro != girar.GIRO_MEIA_VOLTA:
        assert girada.shape[1] > girada.shape[0], "a folha em pe fica deitada"


def test_pagina_que_ninguem_girou_nao_muda(pdf):
    """Girar outra folha nao mexe nesta: a pagina da folha 1, sem giro, sai
    igual (pixel a pixel) antes e depois de girar a folha 2."""
    projeto = _projeto(pdf, limpar=False)
    projeto.folhas.append(ConfigFolha(indice=1, dividir=False, e_paisagem=False))
    _desenhar(pdf, projeto)          # o 1o desenho guarda o corte do PDF (_GEOMETRIAS)
    antes = _desenhar(pdf, projeto)
    indices = girar.folhas_do_alcance(2, 1, girar.ALCANCE_ESTA)
    assert indices == [1]
    acao = montar_acao(projeto, "girar", "folha", indices,
                       girar.campos_do_giro(projeto.folhas, indices, girar.GIRO_DIREITA, 1), "x")
    aplicar(projeto, acao, acao.depois)
    assert projeto.folhas[0].rotacao == 0 and projeto.folhas[1].rotacao == 90
    depois = _desenhar(pdf, projeto)
    assert np.array_equal(antes, depois)


# ---------------------------------------------------------------------------
# "So as pares" numa folha impar (e o contrario): avisa e nao gira
# ---------------------------------------------------------------------------
# Decisao do Samuel (06/10/2026): "O programa avisa: 'va a uma folha par'".
# Antes (decisao provisoria do implementador) a folha da vez nao girava e as
# escolhidas ficavam viradas como ela ficaria - confuso. Agora a tela pergunta
# a girar.aviso_fora_do_alcance e, se vier frase, so avisa.

@pytest.mark.parametrize("atual, alcance", [
    (0, girar.ALCANCE_PARES),        # folha 1 (impar), "so as pares"
    (2, girar.ALCANCE_PARES),        # folha 3
    (1, girar.ALCANCE_IMPARES),      # folha 2 (par), "so as impares"
    (5, girar.ALCANCE_IMPARES),      # folha 6
])
def test_folha_fora_do_alcance_tem_aviso(atual, alcance):
    frase = girar.aviso_fora_do_alcance(atual, alcance)
    assert frase
    if alcance == girar.ALCANCE_PARES:
        assert frase == ("Você está numa folha ímpar. Para girar só as pares, "
                         "vá a uma folha par e gire de lá.")
    else:
        assert frase == ("Você está numa folha par. Para girar só as ímpares, "
                         "vá a uma folha ímpar e gire de lá.")
    assert all(ord(c) < 0x2000 for c in frase), "sem emoji"


@pytest.mark.parametrize("atual, alcance", [
    (1, girar.ALCANCE_PARES), (3, girar.ALCANCE_PARES),
    (0, girar.ALCANCE_IMPARES), (2, girar.ALCANCE_IMPARES),
    (0, girar.ALCANCE_ESTA), (1, girar.ALCANCE_TODAS), (2, girar.ALCANCE_DAQUI),
    (3, "nao existe"),
])
def test_folha_dentro_do_alcance_nao_tem_aviso(atual, alcance):
    assert girar.aviso_fora_do_alcance(atual, alcance) == ""
