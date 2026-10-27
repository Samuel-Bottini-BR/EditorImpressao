"""O "Ajustar o pedaço à figura" numa folha GIRADA (item 2.3 + pedaço).

Por que existe (junção do ramo fase2-geometria, o girar, ao fase-1, 06/10/2026):
o girar (core/girar.py) muda o preparo da página, e as zonas da aba Marcar
são levadas para o mesmo pedaço do papel (core/zonas_na_folha.acompanhar). O
"Ajustar o pedaço à figura" (core/ajustar_pedaco.py, que veio do ramo do
pedaço) lê essas zonas e a página sem filtro. Os dois ramos nasceram
separados; aqui se cobra que eles se entendem:

1. Conta pura: um pedaço desenhado com a folha em pé, levado para a folha
   girada de 90, 180 ou 270 graus, continua retângulo de DOIS pontos
   (alinhado com a página), e o ajuste acha a figura na página girada. Com o
   endireitar por cima (alguns graus), ele vira QUATRO cantos, e o ajuste
   ainda acha a figura e devolve dois pontos.
2. Na tela: o aviso e o botão usam a folha COMO VEIO no PDF (o preparar_metade
   é que gira; a folha já girada saía girada duas vezes - o mesmo defeito D1
   que o girar consertou nos cartões), e não usam as zonas enquanto elas ainda
   estão no preparo de antes do giro (até a prévia nova chegar e levá-las).

Teste de máquina.
"""

from __future__ import annotations

import cv2
import numpy as np
import pytest

pytest.importorskip("PySide6")

from core import girar  # noqa: E402
from core import zonas_na_folha as zf  # noqa: E402
from core.ajustar_pedaco import ajustar_os_pedacos, avaliar_os_pedacos  # noqa: E402
from core.endireitar import girar_90, rotacionar  # noqa: E402
from core.filtros import ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao  # noqa: E402
from tests.test_ajustar_pedaco_quatro_cantos import (  # noqa: E402
    ALTURA,
    FIGURA,
    FOLGADO,
    LARGURA,
    _pagina,
)
from tests.test_gravura_na_aba_marcar import app, conferir, livro  # noqa: F401, E402 - fixtures

# A folha em pé, sem divisão, sem corte e sem endireitar: a página é a folha.
G0 = zf.geometria_do_desenho(LARGURA / ALTURA, 0, None, "inteira", None, 0.0)


def _g(rotacao: int, angulo: float = 0.0) -> dict:
    return zf.geometria_do_desenho(LARGURA / ALTURA, rotacao, None, "inteira", None, angulo)


def _selecao_com_pedaco() -> list[dict]:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[FOLGADO[:2], FOLGADO[2:]],
                         origem=MAO, filtro=ORIGINAL))
    return s.para_lista()


def _figura_na_pagina(g: dict) -> tuple[float, float, float, float]:
    """A caixa (fração) que contém a figura na página preparada com g."""
    x0, y0, x1, y1 = FIGURA
    regiao = Regiao(tipo=GRAVURA, forma=RETANGULO,
                    pontos=[(x0 / LARGURA, y0 / ALTURA), (x1 / LARGURA, y1 / ALTURA)])
    pontos = zf.folha_para_pagina([regiao.para_dicionario()], g)[0]["pontos"]
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    return min(xs), min(ys), max(xs), max(ys)


def _caixa(pontos) -> tuple[float, float, float, float]:
    xs = [float(p[0]) for p in pontos]
    ys = [float(p[1]) for p in pontos]
    return min(xs), min(ys), max(xs), max(ys)


def _contem(fora, dentro, folga: float) -> bool:
    return (fora[0] <= dentro[0] + folga and fora[1] <= dentro[1] + folga
            and fora[2] >= dentro[2] - folga and fora[3] >= dentro[3] - folga)


# --- 1. a conta pura ---------------------------------------------------------


@pytest.mark.parametrize("rotacao", [90, 180, 270])
def test_pedaco_levado_para_a_folha_girada_continua_de_dois_pontos_e_ajusta(rotacao):
    g = _g(rotacao)
    regioes = zf.trocar_de_geometria(_selecao_com_pedaco(), G0, g)
    assert len(regioes[0]["pontos"]) == 2, "girar de 90 em 90 deixa o retângulo alinhado"
    selecao = Selecao.de_lista(regioes)
    img = girar_90(_pagina(), rotacao)

    folgas = avaliar_os_pedacos(img, selecao, PRETO_E_BRANCO)
    assert folgas[0].figura and folgas[0].muito and folgas[0].muda

    nova, quantos = ajustar_os_pedacos(img, selecao, PRETO_E_BRANCO)
    assert quantos == 1
    ajustado = _caixa(nova.regioes[0].pontos)
    figura = _figura_na_pagina(g)
    folga = 1.5 / min(img.shape[:2])
    assert _contem(ajustado, figura, folga), "o ajuste cortou a figura"
    assert _contem(_caixa(regioes[0]["pontos"]), ajustado, 1e-9), "o ajuste cresceu"
    # e encolheu de verdade (sobrava papel dos quatro lados)
    assert (ajustado[2] - ajustado[0]) * (ajustado[3] - ajustado[1]) < 0.8 * (
        (FOLGADO[2] - FOLGADO[0]) * (FOLGADO[3] - FOLGADO[1]))

    # de volta à folha em pé, o pedaço ajustado continua em volta da figura
    volta = zf.trocar_de_geometria(nova.para_lista(), g, G0)[0]["pontos"]
    fx0, fy0, fx1, fy1 = FIGURA
    assert _contem(_caixa(volta), (fx0 / LARGURA, fy0 / ALTURA, fx1 / LARGURA, fy1 / ALTURA),
                   2.0 / ALTURA)


def test_folha_girada_e_endireitada_vira_quatro_cantos_e_ajusta():
    angulo = 1.5
    g = _g(90, angulo)
    regioes = zf.trocar_de_geometria(_selecao_com_pedaco(), G0, g)
    assert len(regioes[0]["pontos"]) == 4, "com o endireitar o retângulo deixa de ser alinhado"
    selecao = Selecao.de_lista(regioes)
    img = rotacionar(girar_90(_pagina(), 90), angulo)

    folgas = avaliar_os_pedacos(img, selecao, PRETO_E_BRANCO)
    assert folgas[0].figura and folgas[0].muito

    nova, quantos = ajustar_os_pedacos(img, selecao, PRETO_E_BRANCO)
    assert quantos == 1
    assert len(nova.regioes[0].pontos) == 2
    folga = 3.0 / min(img.shape[:2])
    assert _contem(_caixa(nova.regioes[0].pontos), _figura_na_pagina(g), folga)


# --- 2. na tela --------------------------------------------------------------


@pytest.fixture
def tela(conferir, monkeypatch):
    """A tela de conferir com a folha 1 trocada pela folha sintética (figura
    com papel em volta), sem as prévias de fundo (nada desenha por trás: o
    teste decide quando a "prévia nova chega")."""
    previas = conferir.previas
    previas.parar()
    monkeypatch.setattr(previas, "_comecar", lambda *a, **k: None)

    def pegar_folha(indice, dpi, girada=True, prioridade=None):
        img = _pagina()
        if girada:
            img = girar_90(img, conferir.projeto.folhas[indice].rotacao)
        return img

    monkeypatch.setattr(previas, "pegar_folha", pegar_folha)
    pagina = conferir.projeto.paginas[0]
    pagina.selecao = _selecao_com_pedaco()
    pagina.filtro = PRETO_E_BRANCO
    pagina.geometria_das_zonas = dict(G0)
    conferir.indice_pagina = 0
    return conferir


def _girar_a_folha_1(tela) -> dict:
    """Gira só a folha 1 um quarto à direita, como o botão, e devolve o
    preparo novo da página (o que a prévia nova traria)."""
    tela.barra_girar.definir_alcance(girar.ALCANCE_ESTA)
    tela._girar_folhas(girar.GIRO_DIREITA)
    assert tela.projeto.folhas[0].rotacao == 90
    return _g(90)


def _a_previa_nova_chegou(tela, g) -> None:
    """O que core/pipeline.renderizar_pagina faz ao desenhar a página girada:
    leva as zonas para o preparo novo. Depois a tela refaz o aviso."""
    pagina = tela.projeto.paginas[0]
    zf.acompanhar(pagina, g)
    tela._avaliar_os_pedacos(pagina)


def test_na_tela_o_aviso_e_o_botao_acertam_a_figura_na_folha_girada(tela):
    g = _girar_a_folha_1(tela)
    _a_previa_nova_chegou(tela, g)
    assert not tela.linha_pedaco.isHidden()
    assert "Sobrou papel" in tela.aviso_pedaco.text()
    assert tela.botao_ajustar_pedaco.isEnabled()

    tela.botao_ajustar_pedaco.click()

    pagina = tela.projeto.paginas[0]
    ajustado = _caixa(pagina.obter_selecao().regioes[0].pontos)
    assert _contem(ajustado, _figura_na_pagina(g), 2.0 / 400), "o ajuste cortou a figura"
    assert (ajustado[2] - ajustado[0]) < 0.9 * (FOLGADO[3] - FOLGADO[1])
    tela.desfazer()
    assert pagina.selecao == zf.trocar_de_geometria(_selecao_com_pedaco(), G0, g)


def test_antes_da_previa_nova_o_botao_nao_ajusta_com_as_zonas_de_antes_do_giro(tela):
    """Logo depois de girar, as zonas ainda estão no preparo de antes (a
    prévia nova é que as leva). Ajustar nesse meio-tempo media o retângulo
    velho na página girada e o gravava no lugar errado do papel."""
    _girar_a_folha_1(tela)
    pagina = tela.projeto.paginas[0]
    antes = [dict(r) for r in pagina.selecao]

    tela._avaliar_os_pedacos(pagina)
    assert not tela.botao_ajustar_pedaco.isEnabled()
    tela._ajustar_pedaco_a_figura()
    assert pagina.selecao == antes, "ajustou com as zonas de antes do giro"


# --- 3. "Tirar o fundo" com pedaço, na folha girada ---------------------------


@pytest.mark.parametrize("rotacao", [90, 270])
def test_tirar_o_fundo_com_pedaco_na_folha_girada(tmp_path, monkeypatch, rotacao):
    """O pedaço em "Original" numa página no "Tirar o fundo" (ramo do pedaço)
    com a folha girada (ramo do girar): dentro, a página como veio, girada
    igual; fora, a página sem o fundo, ponto por ponto; e o PDF sai igual à
    prévia. As duas imagens (sem o fundo e como veio) passam pelo MESMO giro
    (core/pipeline._pedacos_na_pagina_sem_fundo)."""
    from core import camadas, pipeline
    from core.filtros import TIRAR_FUNDO
    from tests.test_camadas import sem_figuras
    from tests.test_so_neste_pedaco_no_tirar_o_fundo import (
        _com_pedaco,
        _dentro,
        _fora,
        _projeto,
    )
    from tests.test_tirar_fundo_no_programa import _paginas_do_pdf, _pdf_camadas, _previa

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)
    monkeypatch.setattr(pipeline, "garantir_selecao",
                        lambda _proj, pag, *a, **k: pag.obter_selecao())
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.qualidade_dpi = 100
    projeto.folhas[0].rotacao = rotacao
    pagina = projeto.paginas[0]
    assert pagina.folha == 0
    sem_fundo = _previa(projeto)
    assert sem_fundo.shape[0] < sem_fundo.shape[1] or projeto.folhas[0].dividir, \
        "a folha girada de 1/4 deita a página"
    pagina.filtro = ORIGINAL
    como_veio = _previa(projeto)
    pagina.filtro = TIRAR_FUNDO

    _com_pedaco(pagina, ORIGINAL)                 # desenhado na página já girada
    com_pedaco = _previa(projeto)

    assert com_pedaco.shape == sem_fundo.shape == como_veio.shape
    assert np.array_equal(_dentro(com_pedaco), _dentro(como_veio))
    fora = _fora(com_pedaco)
    assert np.array_equal(com_pedaco[fora], sem_fundo[fora]), "o resto da página mudou"

    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    gravadas = _paginas_do_pdf(projeto.caminho_saida)
    assert np.array_equal(gravadas[0], com_pedaco), "PDF diferente da prévia"
