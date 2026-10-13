"""A marcacao do tamanho do PDF procurada POR TRAS, com os fios de verdade
(decisao da gerente, 13/10/2026).

O que mudou: a previa de uma pagina sem marcacao procura gravura, letra e
papel na pagina pequena (aparece no tempo de sempre) e guarda como PROVISORIA;
a tela pede por tras (ui/tarefas.GerenciadorPrevias.pedir_medida) a procura
na pagina do tamanho do PDF, e quando ela chega a marcacao da pagina passa a
ser essa e a previa e desenhada de novo.

O que se cobra aqui (testes de maquina, com QThreadPool de verdade; o
detector e trocado por um falso, lento na pagina grande, cuja resposta
depende do tamanho da imagem E de qual pagina ela mostra):
    - trocar de pagina antes de a marcacao chegar nao trava;
    - a marcacao de uma pagina nunca vai parar em outra;
    - nenhuma marcacao se perde: a do tamanho do PDF chega em todas, e o que a
      pessoa marcou a mao no meio continua;
    - a previa guardada e desenhada de novo com a marcacao nova, sem sair do
      cache no meio (a tela nao pisca) e sem pedir a busca de novo sem fim.
A conta da troca em si (sem fios) esta em tests/test_misto_no_programa.py.
"""

from __future__ import annotations

import threading
import time

import numpy as np
import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication  # noqa: E402

from core import pipeline as P  # noqa: E402
from core.filtros import MELHORAR  # noqa: E402
from core.selecao import GRAVURA, LETRA, MAO, REDE, Selecao, retangulo  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import app, pasta  # noqa: F401, E402 - fixtures

PAPEL = (200, 222, 232)
FOLHAS = 4
# quanto o detector falso demora na pagina grande: da tempo de trocar de
# pagina (e de marcar a mao) com a busca ainda no meio
DEMORA_NA_GRANDE = 0.3


def _pagina(i: int) -> np.ndarray:
    """Pagina de papel com um bloco escuro numa altura que so ela tem."""
    img = np.full((900, 700, 3), PAPEL, np.uint8)
    y = 100 + 180 * i
    img[y:y + 120, 150:550] = 25
    return img


def _qual_pagina(img: np.ndarray) -> tuple[int, float, float]:
    """(numero da pagina que a imagem mostra, comeco e fim do bloco escuro em
    fracao da altura)."""
    escuras = np.where(img.reshape(img.shape[0], -1).mean(axis=1) < 150)[0]
    y0, y1 = escuras[0] / img.shape[0], (escuras[-1] + 1) / img.shape[0]
    return int(round((y0 * 900 - 100) / 180)), y0, y1


def _livro(pasta) -> Projeto:
    """Livro de FOLHAS paginas diferentes, sem marcacao nenhuma, no filtro
    Melhorar (a regra do "Para revisar" nao vale: a busca por tras so troca
    a marcacao)."""
    import cv2
    import fitz

    caminho = pasta / "livro-sem-marcacao.pdf"
    doc = fitz.open()
    for i in range(FOLHAS):
        ok, png = cv2.imencode(".png", _pagina(i))
        assert ok
        folha = doc.new_page(width=700 * 72 / 150, height=900 * 72 / 150)
        folha.insert_image(folha.rect, stream=png.tobytes())
    doc.save(str(caminho))
    doc.close()
    projeto = Projeto(caminho_entrada=str(caminho), filtro_padrao=MELHORAR, dividir_folhas=False,
                      endireitar=False, cortar_bordas=False)
    projeto.qualidade_dpi = 300                    # a pagina do PDF: 1800 pontos de altura
    projeto.folhas = [ConfigFolha(indice=i, dividir=False) for i in range(FOLHAS)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i, filtro=MELHORAR) for i in range(FOLHAS)]
    for pagina in projeto.paginas:
        pagina.recorte = (0.0, 0.0, 1.0, 1.0)
        pagina.angulo_manual = 0.0
    return projeto


class _Chamadas(list):
    """As chamadas do detector falso, e quantas procuras na pagina grande
    chegaram a rodar ao mesmo tempo."""

    grandes_agora = 0
    grandes_juntas = 0


@pytest.fixture
def detector(monkeypatch):
    """O detector falso. Devolve a lista das chamadas: (pagina que a imagem
    mostra, se era a pagina grande). Pagina grande: gravura ate o meio da
    largura, depois de DEMORA_NA_GRANDE; pequena: ate 60%, na hora."""
    import core.detectar_regioes as D

    chamadas = _Chamadas()
    tranca = threading.Lock()

    def falso(img, **_opcoes):
        grande = img.shape[0] > 1500
        qual, y0, y1 = _qual_pagina(img)
        chamadas.append((qual, grande))
        if grande:
            with tranca:
                chamadas.grandes_agora += 1
                chamadas.grandes_juntas = max(chamadas.grandes_juntas, chamadas.grandes_agora)
            time.sleep(DEMORA_NA_GRANDE)
            with tranca:
                chamadas.grandes_agora -= 1
        s = Selecao()
        s.acrescentar(retangulo(0.2, y0, 0.5 if grande else 0.6, y1, tipo=GRAVURA, origem=REDE))
        return s

    monkeypatch.setattr(D, "detectar", falso)
    return chamadas


@pytest.fixture
def filtradas(monkeypatch):
    """Anota com que marcacao cada pagina foi filtrada: (pagina que a imagem
    mostra, se era a grande, ate onde vai a gravura da maquina)."""
    de_verdade = P.aplicar_filtro_com_selecao
    vistas = []

    def espiao(img, *args, **kwargs):
        selecao = next((a for a in list(args) + list(kwargs.values())
                        if isinstance(a, Selecao)), None)
        ate = [round(r.pontos[1][0], 2) for r in (selecao.regioes if selecao else [])
               if r.origem != MAO]
        vistas.append((_qual_pagina(img)[0], img.shape[0] > 1500, ate))
        return de_verdade(img, *args, **kwargs)

    monkeypatch.setattr(P, "aplicar_filtro_com_selecao", espiao)
    return vistas


def _esperar(condicao, segundos: float = 40.0) -> bool:
    """Roda a fila de eventos do Qt (e por ela que as tarefas avisam) ate a
    condicao valer. False = passou do tempo: alguma coisa travou."""
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        QCoreApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return condicao()


def _da_maquina(pagina) -> list[tuple[int, float]]:
    """O que a maquina marcou na pagina: (de que pagina e o bloco marcado, ate
    onde vai a gravura: 0.6 = a provisoria, 0.5 = a do tamanho do PDF)."""
    return [(int(round((r.pontos[0][1] * 900 - 100) / 180)), round(r.pontos[1][0], 2))
            for r in pagina.obter_selecao().regioes if r.origem != MAO]


def _a_mao(pagina) -> list:
    return [r for r in pagina.obter_selecao().regioes if r.origem == MAO]


def _parado(previas) -> bool:
    return (not previas._pedidas and not previas._medidas_a_espera
            and previas._pool.activeThreadCount() == 0)


def test_trocar_de_pagina_antes_de_a_marcacao_chegar(app, pasta, detector, filtradas):  # noqa: F811
    """Criterio 3 da gerente: passar pelas paginas sem esperar a busca de
    cada uma nao trava, nao mistura a marcacao de uma na outra e nao perde
    nenhuma. E a previa de cada uma e desenhada de novo com a marcacao nova."""
    from ui.tarefas import GerenciadorPrevias

    projeto = _livro(pasta)
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto)
    chegaram = []
    previas.pronta.connect(lambda chave, _img: chegaram.append(chave))
    try:
        for i in range(FOLHAS):
            assert previas.pegar(i, 110) is None
            assert _esperar(lambda: previas.chave(i, 110) in previas._cache), "a prévia não chegou"
            # a previa marcou na pagina pequena, e a pagina sabe que e provisoria
            assert _da_maquina(projeto.paginas[i]) == [(i, 0.6)]
            assert projeto.paginas[i].marcacao_provisoria is True
            assert previas.pedir_medida(i) is True
            assert previas.pedir_medida(i) is False, "a busca nao e pedida duas vezes"
            # NAO espera a busca: vai para a pagina seguinte com ela no meio
        assert _esperar(lambda: _parado(previas)), "travou esperando as buscas por trás"
        for i in range(FOLHAS):
            pagina = projeto.paginas[i]
            # nao perdeu nem misturou: cada pagina com a marcacao DELA, a do tamanho do PDF
            assert _da_maquina(pagina) == [(i, 0.5)], f"página {i + 1}"
            assert pagina.marcacao_provisoria is False
            # a previa foi desenhada de novo, com a marcacao nova, e ficou no cache
            chave = previas.chave(i, 110)
            assert chegaram.count(chave) == 2, "a prévia não foi desenhada de novo"
            assert previas.pegar(i, 110) is not None
            pequenas = [ate for qual, grande, ate in filtradas if qual == i and not grande]
            assert pequenas[-1] == [0.5], "a prévia guardada é a da marcação de antes"
            # e a busca nao e pedida de novo (nem a tela fica redesenhando sem fim)
            assert previas.chave_da_medida(i) in previas._cache
            assert previas.pedir_medida(i) is False
        # cada pagina foi procurada uma vez na pequena e uma na grande, e so
        assert sorted(detector) == sorted([(i, g) for i in range(FOLHAS) for g in (False, True)])
        # as buscas na pagina grande rodaram uma de cada vez: sobra sempre um
        # fio para a previa da pagina para onde a pessoa foi
        assert detector.grandes_juntas == 1
    finally:
        previas.parar()


def test_a_previa_nao_sai_do_cache_enquanto_e_refeita(app, pasta, detector):  # noqa: F811
    """Quando a marcacao nova chega, a previa de antes continua no cache ate
    a nova ficar pronta: a tela nao pisca nem volta para "preparando..."."""
    from ui.tarefas import MARCA_DA_MEDIDA, GerenciadorPrevias

    projeto = _livro(pasta)
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto)
    chave = previas.chave(0, 110)
    no_cache_quando_a_busca_chegou = []
    previas.pronta.connect(
        lambda c, _img: no_cache_quando_a_busca_chegou.append(
            (previas._cache.get(chave) is not None, chave in previas._pedidas))
        if MARCA_DA_MEDIDA in c else None)
    try:
        previas.pegar(0, 110)
        assert _esperar(lambda: chave in previas._cache)
        de_antes = previas._cache[chave]
        assert previas.pedir_medida(0) is True
        assert _esperar(lambda: _parado(previas)), "travou"
        # na hora em que a busca chegou: a previa de antes no cache, e a nova ja pedida
        assert no_cache_quando_a_busca_chegou == [(True, True)]
        assert previas._cache[chave] is not de_antes, "a prévia não foi trocada pela nova"
        assert previas._ordem.count(chave) == 1
    finally:
        previas.parar()


def test_previa_pedida_no_meio_da_busca_nao_fica_com_a_marcacao_de_antes(app, pasta, detector,  # noqa: F811
                                                                         filtradas):
    """A pessoa mexe na pagina (aqui, na clareza) com a busca ainda no meio:
    a previa nova e desenhada ao mesmo tempo que a busca, na mesma pagina. O
    que fica guardado no fim e a previa com a marcacao do tamanho do PDF."""
    from ui.tarefas import GerenciadorPrevias

    projeto = _livro(pasta)
    pagina = projeto.paginas[0]
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto)
    try:
        previas.pegar(0, 110)
        assert _esperar(lambda: previas.chave(0, 110) in previas._cache)
        da_busca = previas.chave_da_medida(0)
        assert previas.pedir_medida(0) is True
        # a busca comeca quando o pool fica parado; espera ela estar no meio
        assert _esperar(lambda: da_busca in previas._pedidas), "a busca não começou"
        pagina.clareza_melhorar = pagina.clareza_melhorar + 10     # outra chave de previa
        assert previas.pegar(0, 110) is None                       # pedida com a busca no meio
        assert _esperar(lambda: _parado(previas)), "travou"
        assert _da_maquina(pagina) == [(0, 0.5)] and pagina.marcacao_provisoria is False
        assert previas.pegar(0, 110) is not None
        pequenas = [ate for qual, grande, ate in filtradas if qual == 0 and not grande]
        assert pequenas[-1] == [0.5], "ficou guardada a prévia da marcação de antes"
    finally:
        previas.parar()


def test_na_tela_marcar_a_mao_no_meio_da_busca_nao_se_perde(app, pasta, detector):  # noqa: F811
    """Na tela de verdade, na aba Marcar: passar pelas paginas sem esperar,
    marcar uma area a mao numa delas com a busca no meio, e voltar. Nada
    trava; cada pagina termina com a marcacao DELA do tamanho do PDF; a area
    marcada a mao continua la, por cima; e o editor mostra o que a pagina tem."""
    from historico_acoes import HistoricoAcoes
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_MARCAR, TelaConferir

    projeto = _livro(pasta)
    tela = TelaConferir()
    previas = GerenciadorPrevias(projeto.caminho_entrada, projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    try:
        tela.barra_abas.setCurrentIndex(tela._abas_ativas.index(ABA_MARCAR))
        for i in range(FOLHAS):
            tela.ir_para_pagina(i)
            # espera so a previa aparecer (e com ela que a tela pede a busca)
            assert _esperar(lambda: previas.chave(i, tela._dpi_atual) in previas._cache
                            and bool(projeto.paginas[i].selecao)), "a prévia não chegou"
            if i == 2:
                # a pessoa marca uma area a mao com a busca desta pagina no meio
                assert _esperar(lambda: tela.editor_selecao.selecao.regioes), "o editor ficou vazio"
                tela.editor_selecao.selecao.acrescentar(
                    retangulo(0.70, 0.05, 0.90, 0.12, tipo=LETRA, origem=MAO))
                tela._selecao_mudou()
        tela.ir_para_pagina(0)
        assert _esperar(lambda: _parado(previas)), "travou"
        # volta em cada pagina, como quem confere: o que faltar e buscado
        for i in list(range(FOLHAS)) + [2]:
            tela.ir_para_pagina(i)
            assert _esperar(lambda: previas.chave(i, tela._dpi_atual) in previas._cache)
            assert _esperar(lambda: _parado(previas)), "travou"
        for i, pagina in enumerate(projeto.paginas):
            assert _da_maquina(pagina) == [(i, 0.5)], f"página {i + 1}"
            assert pagina.marcacao_provisoria is False
            assert len(_a_mao(pagina)) == (1 if i == 2 else 0), f"página {i + 1}"
        da_pessoa = _a_mao(projeto.paginas[2])[0]
        assert da_pessoa.tipo == LETRA
        assert projeto.paginas[2].obter_selecao().regioes[-1].origem == MAO, "a mão fica por cima"
        # o editor (esta na pagina 3) mostra o que a pagina tem
        assert tela.indice_pagina == 2
        assert tela.editor_selecao.selecao.para_lista() == projeto.paginas[2].selecao
    finally:
        previas.parar()
