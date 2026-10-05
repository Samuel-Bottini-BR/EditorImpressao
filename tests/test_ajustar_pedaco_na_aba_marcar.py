"""O aviso e o botão "Ajustar o pedaço à figura" na aba Marcar (conferência 13, S3).

Pedido do Samuel: "(b) e (c) juntas - Mas caso ele não queira mudar, fica do
jeito que está." O que se cobra aqui, na tela de verdade (sem janela visível):

    - a linha "Pedaço:" só aparece com um pedaço em retângulo com OUTRO filtro;
    - folga larga: aviso com a porcentagem e o botão aceso;
    - nada muda sozinho: avaliar não toca na marcação;
    - o botão encolhe o retângulo até a figura, numa ação do Histórico, e o
      Desfazer devolve o retângulo de antes; o Refazer, o ajustado;
    - o tipo, o filtro e o resto da marcação ficam.

A conta (core/ajustar_pedaco.py) tem os testes dela em
tests/test_ajustar_pedaco.py; aqui a imagem sem filtro da página é a mesma
página sintética de lá (o PDF do teste é branco, sem figura).
"""

from __future__ import annotations

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao, retangulo  # noqa: E402
from tests.test_ajustar_pedaco import FOLGADO, JUSTO, _pagina  # noqa: E402
from tests.test_gravura_na_aba_marcar import app, conferir, livro  # noqa: F401, E402 - fixtures


def _com_pedaco(pagina, caixa, filtro_do_pedaco=ORIGINAL, filtro_da_pagina=PRETO_E_BRANCO):
    s = Selecao()
    s.acrescentar(retangulo(0.05, 0.04, 0.95, 0.27, origem="rede"))          # a maquina
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[caixa[:2], caixa[2:]],
                         origem=MAO, filtro=filtro_do_pedaco))
    pagina.guardar_selecao(s)
    pagina.filtro = filtro_da_pagina


@pytest.fixture
def tela(conferir, monkeypatch):
    """A tela com a pagina sem filtro trocada pela pagina sintetica (com
    figura e folga de papel), e sem as previas de fundo."""
    monkeypatch.setattr(conferir, "_pagina_sem_filtro_para_o_ajuste", lambda _p: _pagina())
    return conferir


def _pedaco(pagina):
    return Selecao.de_lista(pagina.selecao).regioes[1]


def test_sem_pedaco_com_outro_filtro_a_linha_nao_aparece(tela):
    pagina = tela.projeto.paginas[0]
    tela._avaliar_os_pedacos(pagina)
    assert tela.linha_pedaco.isHidden()
    _com_pedaco(pagina, FOLGADO, filtro_do_pedaco=PRETO_E_BRANCO)    # o mesmo da pagina
    tela._avaliar_os_pedacos(pagina)
    assert tela.linha_pedaco.isHidden()


def test_folga_larga_avisa_e_nao_muda_nada_sozinho(tela):
    pagina = tela.projeto.paginas[0]
    _com_pedaco(pagina, FOLGADO)
    antes = [dict(r) for r in pagina.selecao]
    tela._avaliar_os_pedacos(pagina)
    assert not tela.linha_pedaco.isHidden()
    assert tela.botao_ajustar_pedaco.isEnabled()
    assert tela.botao_ajustar_pedaco.text() == "Ajustar o pedaço à figura"
    assert not tela.botao_ajustar_pedaco.icon().isNull(), "sem a pista visual"
    texto = tela.aviso_pedaco.text()
    assert "Sobrou papel em volta da figura" in texto and "%" in texto, texto
    assert "Ajustar o pedaço à figura" in tela.aviso_pedaco.toolTip()
    assert pagina.selecao == antes, "o aviso mudou a marcacao sozinho"


def test_pedaco_justo_nao_avisa(tela):
    pagina = tela.projeto.paginas[0]
    _com_pedaco(pagina, JUSTO)
    tela._avaliar_os_pedacos(pagina)
    assert not tela.linha_pedaco.isHidden()
    assert "Sobrou papel" not in tela.aviso_pedaco.text()


def test_o_botao_ajusta_e_o_desfazer_devolve(tela):
    pagina = tela.projeto.paginas[0]
    tela.indice_pagina = 0
    _com_pedaco(pagina, FOLGADO)
    maquina_antes = pagina.selecao[0]
    tela._avaliar_os_pedacos(pagina)

    tela.botao_ajustar_pedaco.click()

    ajustado = _pedaco(pagina)
    (x0, y0), (x1, y1) = ajustado.pontos
    assert x0 > FOLGADO[0] and y0 > FOLGADO[1] and x1 < FOLGADO[2] and y1 < FOLGADO[3]
    assert ajustado.filtro == ORIGINAL and ajustado.tipo == GRAVURA and ajustado.origem == MAO
    assert pagina.selecao[0] == maquina_antes, "o resto da marcacao mudou"
    assert "ajustado" in tela.acoes.descricao_desfazer()

    tela.desfazer()
    assert _pedaco(pagina).pontos == [FOLGADO[:2], FOLGADO[2:]]
    tela.refazer()
    assert _pedaco(pagina).pontos == ajustado.pontos
