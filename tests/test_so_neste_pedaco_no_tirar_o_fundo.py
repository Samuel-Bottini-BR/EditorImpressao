"""O "so neste pedaco" da aba Marcar numa pagina no filtro "Tirar o fundo".

Conferencia 14 (Samuel): "FUNDO: Sim, do mesmo jeito (só muda se alguém
marcar um pedaço)". O mesmo jeito do Original (conferencia 13, S4, commit
294cb91): a area marcada obedece INTEIRA ao filtro escolhido para ela, e o
resto da pagina fica como o "Tirar o fundo" deixou.

O que se cobra (teste de maquina, com o PDF com camadas montado na hora de
tests/test_camadas.py, e o detector de figuras do core/camadas.py trocado
por um que nao acha nada, como em tests/test_tirar_fundo_no_programa.py):

    - pedaco em "Original": dentro dele, a pagina como veio (o papel
      amarelado de verdade, nao o branco do fundo tirado); fora, a pagina sem
      o fundo, ponto por ponto;
    - pedaco em Preto e branco: dentro, so preto e branco;
    - pagina sem pedaco: exatamente como antes (o mesmo objeto; nenhum
      desenho a mais da folha, nenhum filtro);
    - previa = PDF, ponto por ponto, com o pedaco;
    - pagina que core/camadas.py deixa intacta: o pedaco vale como no
      Original;
    - a funcao do filtro (aplicar_filtro_com_selecao) com "Tirar o fundo" e
      pedaco: o pedaco vale; sem pedaco, o mesmo objeto.
"""

from __future__ import annotations

import fitz
import numpy as np
import pytest

from core import camadas, pipeline
from core.filtros import (
    ORIGINAL,
    PRETO_E_BRANCO,
    TIRAR_FUNDO,
    aplicar_filtro,
    aplicar_filtro_com_selecao,
)
from core.selecao import GRAVURA, MAO, RETANGULO, Regiao, Selecao, retangulo
from tests.test_camadas import PAPEL_RGB, sem_figuras
from tests.test_tirar_fundo_no_programa import (
    _paginas_do_pdf,
    _papel,
    _pdf_camadas,
    _previa,
)
from tests.test_tirar_fundo_no_programa import _projeto as _projeto_de_la

# o retangulo marcado, longe das letras do PDF de teste (o trecho de papel
# que tests/test_tirar_fundo_no_programa._papel usa fica dentro dele)
PEDACO = (0.80, 0.35, 0.97, 0.65)


@pytest.fixture(autouse=True)
def detector_sem_figuras(monkeypatch):
    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", sem_figuras)


@pytest.fixture(autouse=True)
def marcacao_guardada(monkeypatch):
    """A pagina em Original (a referencia "como veio") usa garantir_selecao;
    aqui ela devolve a marcacao guardada, sem o modelo de leiaute (lento, e
    nao e o assunto)."""
    monkeypatch.setattr(pipeline, "garantir_selecao",
                        lambda _proj, pag, *a, **k: pag.obter_selecao())


def _projeto(caminho, **kw):
    """O projeto de tests/test_tirar_fundo_no_programa, com "Procurar
    gravura e letra" ligado (o normal; sem ele nao ha aba Marcar, e o pedaco
    nao vale). A pagina no "Tirar o fundo" nao chama o detector."""
    projeto = _projeto_de_la(caminho, **kw)
    projeto.detectar_regioes = True
    return projeto


def _com_pedaco(pagina, filtro_do_pedaco: str) -> None:
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[PEDACO[:2], PEDACO[2:]],
                         origem=MAO, filtro=filtro_do_pedaco))
    pagina.guardar_selecao(s)


def _caixa(img) -> tuple[int, int, int, int]:
    altura, largura = img.shape[:2]
    return (int(round(PEDACO[0] * largura)), int(round(PEDACO[1] * altura)),
            int(round(PEDACO[2] * largura)), int(round(PEDACO[3] * altura)))


def _dentro(img):
    x0, y0, x1, y1 = _caixa(img)
    return img[y0 + 2:y1 - 2, x0 + 2:x1 - 2]


def _fora(img) -> np.ndarray:
    x0, y0, x1, y1 = _caixa(img)
    fora = np.ones(img.shape[:2], bool)
    fora[y0 - 2:y1 + 3, x0 - 2:x1 + 3] = False
    return fora


def test_pedaco_em_original_mostra_o_papel_como_veio(tmp_path):
    projeto = _projeto(_pdf_camadas(tmp_path))
    pagina = projeto.paginas[0]
    sem_fundo = _previa(projeto)                         # sem pedaco
    assert _papel(sem_fundo).min() > 250                  # o fundo saiu (papel branco)
    pagina.filtro = ORIGINAL
    como_veio = _previa(projeto)
    pagina.filtro = TIRAR_FUNDO

    _com_pedaco(pagina, ORIGINAL)
    com_pedaco = _previa(projeto)

    assert com_pedaco.shape == sem_fundo.shape
    # dentro: a pagina como veio (o papel amarelado), ponto por ponto
    assert np.array_equal(_dentro(com_pedaco), _dentro(como_veio))
    papel = _papel(com_pedaco)[::-1]                      # BGR -> RGB
    assert np.abs(papel - np.array(PAPEL_RGB)).max() < 6, papel
    # fora: a pagina sem o fundo, ponto por ponto
    fora = _fora(com_pedaco)
    assert np.array_equal(com_pedaco[fora], sem_fundo[fora]), "o resto da pagina mudou"


def test_pedaco_em_preto_e_branco_sai_em_preto_e_branco(tmp_path):
    projeto = _projeto(_pdf_camadas(tmp_path))
    pagina = projeto.paginas[0]
    sem_fundo = _previa(projeto)
    pagina.filtro = ORIGINAL
    como_veio = _previa(projeto)
    pagina.filtro = TIRAR_FUNDO
    _com_pedaco(pagina, PRETO_E_BRANCO)
    com_pedaco = _previa(projeto)

    esperado, _ = aplicar_filtro(como_veio.copy(), PRETO_E_BRANCO)
    if esperado.ndim == 2:
        esperado = np.repeat(esperado[..., None], 3, axis=2)
    assert set(np.unique(_dentro(com_pedaco)).tolist()) <= {0, 255}
    assert np.array_equal(_dentro(com_pedaco), _dentro(esperado)), \
        "o pedaco nao saiu como o Preto e branco da pagina como veio"
    fora = _fora(com_pedaco)
    assert np.array_equal(com_pedaco[fora], sem_fundo[fora])


def test_sem_pedaco_nada_muda_e_nada_a_mais_e_desenhado(tmp_path, monkeypatch):
    """A pagina sem pedaco (com ou sem marcacao da maquina) sai como antes, e
    a folha nao e desenhada uma vez a mais (o tempo nao muda)."""
    projeto = _projeto(_pdf_camadas(tmp_path))
    pagina = projeto.paginas[0]
    antes = _previa(projeto)

    s = Selecao()
    s.acrescentar(retangulo(0.1, 0.1, 0.9, 0.5, origem="rede"))   # a maquina, sem filtro
    pagina.guardar_selecao(s)
    desenhos = {"n": 0}
    original = pipeline.pagina_para_array

    def contar(*a, **k):
        desenhos["n"] += 1
        return original(*a, **k)

    monkeypatch.setattr(pipeline, "pagina_para_array", contar)
    depois = _previa(projeto)
    assert np.array_equal(antes, depois)
    sem_marcacao = desenhos["n"]

    _com_pedaco(pagina, ORIGINAL)
    desenhos["n"] = 0
    _previa(projeto)
    assert desenhos["n"] == sem_marcacao + 1, "com pedaco, a folha como veio e desenhada uma vez"


def test_pdf_com_pedaco_sai_igual_a_previa(tmp_path):
    """Com corte e endireitar ligados (a geometria medida na folha como veio
    vale para as duas imagens)."""
    projeto = _projeto(_pdf_camadas(tmp_path), geometria=True)
    projeto.qualidade_dpi = 150
    sem_pedaco = _previa(projeto, dpi=150)
    _com_pedaco(projeto.paginas[0], ORIGINAL)
    previa = _previa(projeto, dpi=150)
    projeto.caminho_saida = str(tmp_path / "saida.pdf")
    pipeline.processar(projeto)
    gravada = _paginas_do_pdf(projeto.caminho_saida)
    assert len(gravada) == 1
    assert gravada[0].shape == previa.shape
    assert np.array_equal(gravada[0], previa)
    assert not np.array_equal(_dentro(gravada[0]), _dentro(sem_pedaco)),         "o pedaco nao valeu no PDF"
    fora = _fora(gravada[0])
    assert np.array_equal(gravada[0][fora], sem_pedaco[fora])


def test_pagina_intacta_o_pedaco_vale_como_no_original(tmp_path, monkeypatch):
    """core/camadas.py deixa a pagina intacta (o detector falha): ela sai como
    veio, e o pedaco vale como no Original."""
    def quebrado(_img):
        raise RuntimeError("sem detector")

    monkeypatch.setattr(camadas, "DETECTOR_DE_FIGURAS", quebrado)
    projeto = _projeto(_pdf_camadas(tmp_path, "intacta.pdf"))
    projeto.detectar_regioes = True           # o normal (sem ele nao ha aba Marcar)
    # o Original usa garantir_selecao; aqui ela devolve a marcacao guardada
    # (sem o modelo, que e lento e nao e o assunto)
    monkeypatch.setattr(pipeline, "garantir_selecao",
                        lambda _proj, pag, *a, **k: pag.obter_selecao())
    pagina = projeto.paginas[0]
    _com_pedaco(pagina, PRETO_E_BRANCO)
    no_fundo = _previa(projeto)
    pagina.filtro = ORIGINAL
    no_original = _previa(projeto)
    assert np.array_equal(no_fundo, no_original)
    assert set(np.unique(_dentro(no_fundo)).tolist()) <= {0, 255}


def test_sem_procurar_gravura_e_letra_o_pedaco_nao_vale(tmp_path):
    """Sem "Procurar gravura e letra" (projeto.detectar_regioes) a aba Marcar
    nem aparece, e no Original o pedaco tambem nao vale (garantir_selecao
    devolve a marcacao vazia): o mesmo aqui, para o pedaco nunca mudar o
    PDF sem poder ser visto."""
    projeto = _projeto(_pdf_camadas(tmp_path))
    projeto.detectar_regioes = False
    antes = _previa(projeto)
    _com_pedaco(projeto.paginas[0], ORIGINAL)
    assert np.array_equal(_previa(projeto), antes)


def test_a_funcao_do_filtro_obedece_ao_pedaco():
    img = np.full((300, 200, 3), (160, 200, 215), np.uint8)
    img[100:120, 20:180] = (30, 30, 40)
    s = Selecao()
    s.acrescentar(Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.05, 0.2), (0.95, 0.5)],
                         origem=MAO, filtro=PRETO_E_BRANCO))
    saida, mono = aplicar_filtro_com_selecao(img.copy(), TIRAR_FUNDO, s)
    assert not mono
    assert set(np.unique(saida[65:145, 15:185]).tolist()) <= {0, 255}
    assert np.array_equal(saida[:55], img[:55]) and np.array_equal(saida[155:], img[155:])
    vazia = Selecao()
    vazia.acrescentar(retangulo(0.1, 0.1, 0.9, 0.9))
    mesma, mono = aplicar_filtro_com_selecao(img, TIRAR_FUNDO, vazia)
    assert mesma is img and mono is False
