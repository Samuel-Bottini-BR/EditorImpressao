"""Girar a folha (item 2.3): o que a tela mostra depois do giro.

Consertos pedidos pela gerente em 06/10/2026, a partir do parecer do
verificador (relatorios/conferir/girar-2026-10-06/verificador/):

    D1 - os cartoes da aba Filtro (Preto e branco, Melhorar, Magico pro)
         mostravam a folha girada DUAS vezes (a folha crua ja vinha girada
         do GerenciadorPrevias e o preparar_metade girava de novo), e nao
         mudavam quando se girava com a aba aberta (a chave do cache dos
         cartoes nao levava o giro). Cada cartao tem de estar no mesmo giro
         da previa, nos quatro giros.

Testes de maquina, sem janela na tela (tests/conftest.py). O livro de teste
tem um bloco preto no canto de cima, a esquerda: o canto em que a tinta cai
diz o giro da imagem (0: em cima a esquerda; 90: em cima a direita; 180: em
baixo a direita; 270: em baixo a esquerda).
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core import girar, pipeline  # noqa: E402
from core.filtros import MAGICO_PRO, MELHORAR, ORIGINAL, PRETO_E_BRANCO  # noqa: E402
from tests.test_mesmo_livro_outro_caminho import (  # noqa: F401, E402 - fixtures
    app,
    janela,
    pasta,
)

# o canto em que cai o bloco preto, para cada giro da folha
CANTO_DO_GIRO = {0: "cima-esquerda", 90: "cima-direita",
                 180: "baixo-direita", 270: "baixo-esquerda"}


def _pdf_com_canto(pasta: Path, folhas: int = 3) -> Path:
    """Folhas em pe, com um bloco preto grande no canto de cima, a esquerda."""
    (pasta / "livros").mkdir(exist_ok=True)
    caminho = pasta / "livros" / "Livro do canto.pdf"
    doc = fitz.open()
    for i in range(folhas):
        pagina = doc.new_page(width=400, height=560)
        pagina.draw_rect(fitz.Rect(30, 30, 170, 150), color=(0, 0, 0), fill=(0, 0, 0))
        pagina.insert_text((60, 300), f"folha {i}", fontsize=14)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _canto(img: np.ndarray) -> str:
    """Em que canto esta o centro da tinta escura (o bloco preto)."""
    cinza = img if img.ndim == 2 else img.mean(axis=2)
    ys, xs = np.nonzero(cinza < 100)
    assert len(xs), "imagem sem tinta"
    altura, largura = cinza.shape
    vertical = "cima" if ys.mean() < altura / 2 else "baixo"
    horizontal = "esquerda" if xs.mean() < largura / 2 else "direita"
    return f"{vertical}-{horizontal}"


def _bombear_ate(app, condicao, segundos: float = 15.0) -> bool:
    """Deixa as tarefas de fundo (previas, cartoes) chegarem."""
    limite = time.monotonic() + segundos
    while time.monotonic() < limite:
        app.processEvents()
        if condicao():
            return True
        time.sleep(0.02)
    app.processEvents()
    return condicao()


def _aberta_na_aba_filtro(janela, pasta, folhas: int = 3):
    """O livro do canto aberto, sem dividir, sem cortar e sem endireitar (a
    previa e a folha inteira, so girada), na aba Filtro."""
    janela.abrir_livro(str(_pdf_com_canto(pasta, folhas)))
    projeto = janela.projeto
    projeto.dividir_folhas = False
    projeto.cortar_bordas = False
    projeto.endireitar = False
    projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(projeto))
    tela = janela.tela_conferir
    janela.resize(1280, 657)
    janela.show()
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index("filtro"))
    return tela


def _espiar_cartoes(tela) -> dict:
    """Anota a ultima imagem posta em cada cartao."""
    postas: dict = {}
    for chave, cartao in tela.cartoes.items():
        original = cartao.definir_amostra

        def definir(img, _c=chave, _o=original):
            postas[_c] = img
            _o(img)

        cartao.definir_amostra = definir
    return postas


@pytest.mark.parametrize("filtro_da_pagina", [ORIGINAL, MELHORAR])
def test_d1_os_cartoes_ficam_no_giro_da_previa_girando_com_a_aba_aberta(
        janela, pasta, app, filtro_da_pagina):
    """D1: gira 1/4 a direita quatro vezes com a aba Filtro aberta; depois de
    cada giro, os cartoes dos outros filtros chegam no MESMO giro da previa
    (e nao no dobro, nem no de antes)."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    projeto.paginas[0].filtro = filtro_da_pagina
    tela.ir_para_pagina(0)
    postas = _espiar_cartoes(tela)
    outros = [c for c in (ORIGINAL, PRETO_E_BRANCO, MELHORAR, MAGICO_PRO)
              if c != filtro_da_pagina and c in tela.cartoes]
    assert len(outros) == 3

    for giro_esperado in (90, 180, 270, 0):
        tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
        assert projeto.folhas[0].rotacao == giro_esperado
        canto = CANTO_DO_GIRO[giro_esperado]

        # a previa (a imagem grande) chega no giro certo
        assert _bombear_ate(app, lambda: tela.previas.pegar(0, tela._dpi_atual) is not None)
        previa = tela.previas.pegar(0, tela._dpi_atual)
        assert _canto(previa) == canto

        def todos_no_giro():
            return all(postas.get(c) is not None and _canto(postas[c]) == canto
                       for c in outros)

        chegou = _bombear_ate(app, todos_no_giro)
        vistos = {c: (None if postas.get(c) is None else _canto(postas[c])) for c in outros}
        assert chegou, f"giro {giro_esperado}: cartoes {vistos}, previa {canto}"
        # e a mesma proporcao da previa (em pe / deitada)
        for c in outros:
            img = postas[c]
            assert (img.shape[0] > img.shape[1]) == (previa.shape[0] > previa.shape[1]), c


def test_d1_a_amostra_dos_cartoes_e_a_previa_em_cada_giro(janela, pasta, app):
    """A base dos cartoes (_imagem_sem_filtro) e a mesma imagem da previa,
    so menor, em cada giro: girada uma vez so."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    for giro in (90, 180, 270):
        projeto.folhas[1].rotacao = giro
        tela.ir_para_pagina(1)
        assert _bombear_ate(app, lambda: tela._imagem_sem_filtro() is not None)
        base = tela._imagem_sem_filtro()
        assert _canto(base) == CANTO_DO_GIRO[giro], giro
        doc = fitz.open(projeto.caminho_entrada)
        try:
            previa, _ = pipeline.renderizar_pagina(doc, projeto, projeto.paginas[1], dpi=70)
        finally:
            doc.close()
        assert base.shape[:2] == previa.shape[:2]
        assert float(np.abs(base.astype(int) - previa.astype(int)).mean()) < 2.0


def test_d1_o_comparar_da_tela_ampliada_tambem_gira_uma_vez(janela, pasta, app):
    """O "comparar" da tela ampliada tinha o mesmo defeito (folha crua ja
    girada passada ao preparar_metade)."""
    tela = _aberta_na_aba_filtro(janela, pasta)
    projeto = janela.projeto
    projeto.folhas[0].rotacao = 90
    tela.ir_para_pagina(0)
    from ui.tela_ampliada import MODO_FILTRO, TelaAmpliada

    ampliada = TelaAmpliada(tela, modo=MODO_FILTRO, parent=janela)   # sem o exec (modal)
    indice = ampliada.combo_comparar.findData(PRETO_E_BRANCO)
    ampliada.combo_comparar.setCurrentIndex(indice)
    assert _bombear_ate(app, lambda: ampliada._imagem_do_outro_filtro() is not None)
    assert _canto(ampliada._imagem_do_outro_filtro()) == CANTO_DO_GIRO[90]
    ampliada.close()


# ---------------------------------------------------------------------------
# D4: uma vez, logo depois de girar "todas", a folha 4 mostrou a imagem da
# folha 2 (print p14 do verificador: aba Bordas, "atualizando...").
# ---------------------------------------------------------------------------


def _livro_e_projeto(pasta: Path, folhas: int = 4):
    from modelos import ConfigFolha, ConfigPagina, Projeto

    caminho = _pdf_com_canto(pasta, folhas)
    projeto = Projeto(caminho_entrada=str(caminho), nome="canto")
    projeto.folhas = [ConfigFolha(indice=i) for i in range(folhas)]
    projeto.paginas = [ConfigPagina(indice=i, folha=i) for i in range(folhas)]
    return caminho, projeto


def test_d4_a_previa_que_chega_depois_do_giro_nao_entra_no_cache(pasta, app, monkeypatch):
    """Corrida: a previa da pagina 1 foi pedida no giro 0 e so foi desenhada
    depois de a pessoa girar (a tarefa le o projeto quando roda). Ela chegava
    e era guardada sob a chave do giro 0 - com a folha girada dentro. Ao
    desfazer o giro, a tela mostrava essa imagem errada, de graca, do cache.
    Agora o que chega de antes do invalidar e jogado fora (e pedido de novo).
    """
    import threading

    from ui import tarefas as mod_tarefas

    caminho, projeto = _livro_e_projeto(pasta)
    soltar = threading.Event()

    def renderizar_que_espera(doc, projeto_, pagina, dpi):
        soltar.wait(5)
        giro = projeto_.folhas[pagina.folha].rotacao       # lido na hora, como o de verdade
        return np.full((10, 10, 3), giro % 250, np.uint8), False

    monkeypatch.setattr(mod_tarefas, "renderizar_pagina", renderizar_que_espera)
    previas = mod_tarefas.GerenciadorPrevias(str(caminho), projeto, None)
    chegadas: list = []
    previas.pronta.connect(lambda chave, img: chegadas.append(chave))
    try:
        assert previas.pegar(1, 110) is None                  # pedida no giro 0
        chave_do_giro_0 = previas.chave(1, 110)
        projeto.folhas[1].rotacao = 90                        # a pessoa gira...
        previas.invalidar(1)                                  # ...e a tela invalida
        soltar.set()
        _bombear_ate(app, lambda: not previas._pool.activeThreadCount(), 5)
        for _ in range(5):
            app.processEvents()
        assert chave_do_giro_0 not in chegadas, "a previa velha foi entregue como nova"
        projeto.folhas[1].rotacao = 0                         # desfazer
        previas.invalidar(1)
        assert previas.pegar(1, 110) is None, "o cache devolveu a folha girada no giro 0"
        assert _bombear_ate(app, lambda: previas.pegar(1, 110) is not None, 5)
        assert int(previas.pegar(1, 110).max()) == 0, "e a de agora chega certa"
    finally:
        soltar.set()
        previas.parar()


def test_d4_a_folha_crua_leva_o_giro_do_pedido(pasta, app, monkeypatch):
    """A folha crua (aba Onde cortar) pedida no giro 0 e desenhada depois do
    giro sai no giro 0, que e o que a chave dela diz."""
    import threading

    from ui import tarefas as mod_tarefas

    caminho, projeto = _livro_e_projeto(pasta)
    soltar = threading.Event()
    original = mod_tarefas.abrir_pdf

    def abrir_que_espera(c):
        soltar.wait(5)
        return original(c)

    monkeypatch.setattr(mod_tarefas, "abrir_pdf", abrir_que_espera)
    previas = mod_tarefas.GerenciadorPrevias(str(caminho), projeto, None)
    try:
        assert previas.pegar_folha(2, 40) is None
        projeto.folhas[2].rotacao = 90
        soltar.set()
        projeto.folhas[2].rotacao = 0
        assert _bombear_ate(app, lambda: previas.pegar_folha(2, 40) is not None, 10)
        assert _canto(previas.pegar_folha(2, 40)) == CANTO_DO_GIRO[0]
    finally:
        soltar.set()
        previas.parar()


@pytest.mark.parametrize("aba", ["bordas", "angulo"])
def test_d4_trocar_de_pagina_nao_deixa_a_imagem_da_outra_pagina(janela, pasta, app,
                                                                monkeypatch, aba):
    """Andando para uma pagina cuja previa ainda nao chegou, a tela mostrava a
    imagem da pagina de antes com "atualizando..." (o visualizador guarda a
    imagem anterior para nao piscar ao ajustar a MESMA pagina). Agora, de
    outra pagina, mostra "Preparando a previa..." ate a certa chegar."""
    janela.abrir_livro(str(_pdf_com_canto(pasta, 4)))
    projeto = janela.projeto
    projeto.dividir_folhas = False
    projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(projeto))
    tela = janela.tela_conferir
    tela.barra_abas.setCurrentIndex(tela._abas_ativas.index(aba))
    vis = tela.visualizadores[aba]
    imagem = np.full((50, 40, 3), 200, np.uint8)
    prontas = {0}
    monkeypatch.setattr(tela.previas, "pegar",
                        lambda i, d: imagem if i in prontas else None)
    monkeypatch.setattr(tela.previas, "pegar_para_recorte",
                        lambda i, d: imagem if i in prontas else None)
    tela.ir_para_pagina(0)
    assert vis._pixmap is not None
    tela.ir_para_pagina(1)
    assert vis.carregando
    assert vis._pixmap is None, "a imagem da pagina 1 ficou na tela da pagina 2"
    # na MESMA pagina, enquanto a nova nao chega, a de antes continua (nao pisca)
    prontas.add(1)
    tela.ir_para_pagina(1)
    assert vis._pixmap is not None
    prontas.discard(1)
    tela.atualizar()
    assert vis._pixmap is not None and vis.carregando


# ---------------------------------------------------------------------------
# D2: as miniaturas da tira e a capa do cartao da tela inicial acompanham o
# giro, sem ler o livro de novo quando gira uma folha so.
# ---------------------------------------------------------------------------


def _imagem_do_pixmap(pixmap) -> np.ndarray:
    imagem = pixmap.toImage().convertToFormat(pixmap.toImage().Format.Format_RGB888)
    largura, altura = imagem.width(), imagem.height()
    linha = imagem.bytesPerLine()
    dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(altura, linha)
    return dados[:, :largura * 3].reshape(altura, largura, 3).copy()


def _cantos_da_tira(tela) -> list:
    return [None if m._pixmap is None else _canto(_imagem_do_pixmap(m._pixmap))
            for m in tela.tira._miniaturas]


def test_d2_a_tira_mostra_cada_folha_no_giro_dela(janela, pasta, app, monkeypatch):
    tela = _aberta_na_aba_filtro(janela, pasta, folhas=3)
    assert _bombear_ate(app, lambda: None not in _cantos_da_tira(tela))
    assert _cantos_da_tira(tela) == [CANTO_DO_GIRO[0]] * 3

    # girar uma folha so: so o quadro dela muda, e o PDF nao e lido de novo
    from ui.widgets import tira_miniaturas

    lidas = []
    original = tira_miniaturas.pagina_para_array
    monkeypatch.setattr(tira_miniaturas, "pagina_para_array",
                        lambda *a, **k: lidas.append(a) or original(*a, **k))
    antes = [m._pixmap.cacheKey() for m in tela.tira._miniaturas]
    tela.ir_para_pagina(1)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    app.processEvents()
    assert _cantos_da_tira(tela) == [CANTO_DO_GIRO[0], CANTO_DO_GIRO[90], CANTO_DO_GIRO[0]]
    depois = [m._pixmap.cacheKey() for m in tela.tira._miniaturas]
    assert depois[0] == antes[0] and depois[2] == antes[2], "redesenhou folha que nao girou"
    assert depois[1] != antes[1]

    # "todas", meia volta; e desfazer
    tela.barra_girar.definir_alcance(girar.ALCANCE_TODAS)
    tela.barra_girar.botoes_de_giro[girar.GIRO_MEIA_VOLTA].click()
    app.processEvents()
    assert _cantos_da_tira(tela) == [CANTO_DO_GIRO[180], CANTO_DO_GIRO[270], CANTO_DO_GIRO[180]]
    tela.desfazer()
    app.processEvents()
    assert _cantos_da_tira(tela) == [CANTO_DO_GIRO[0], CANTO_DO_GIRO[90], CANTO_DO_GIRO[0]]
    for _ in range(10):
        app.processEvents()
    assert not lidas, "girar leu o livro de novo para a tira"


def test_d2_a_tira_divide_a_folha_girada(app, pasta):
    """Folha dividida e girada: cada metade sai da folha JA girada (a ordem
    do programa: girar, depois dividir)."""
    from ui.widgets.tira_miniaturas import TiraMiniaturas

    tira = TiraMiniaturas("x")
    try:
        larga = np.full((40, 60, 3), 255, np.uint8)
        larga[:, :30] = 0                                  # metade esquerda preta
        tira.montar(2, "", {0: 0, 1: 0}, {0: ("esquerda", 0.5), 1: ("direita", 0.5)},
                    giros={0: 180})
        if tira._tarefa is not None:
            tira._tarefa.parar = True
        tira._receber(0, larga)
        esquerda = _imagem_do_pixmap(tira._miniaturas[0]._pixmap)
        direita = _imagem_do_pixmap(tira._miniaturas[1]._pixmap)
        # meia volta: o preto foi para a direita - a metade esquerda e branca
        assert esquerda.mean() > 200 and direita.mean() < 60
        assert tira.definir_giros({0: 0}) == 1
        assert _imagem_do_pixmap(tira._miniaturas[0]._pixmap).mean() < 60
        assert tira.definir_giros({0: 0}) == 0, "giro igual nao redesenha"
    finally:
        tira.parar()


def test_d2_a_capa_do_cartao_acompanha_o_giro_da_primeira_folha(janela, pasta, app):
    import cv2

    import projetos

    tela = _aberta_na_aba_filtro(janela, pasta, folhas=3)
    capa = projetos.garantir_miniatura(janela.resumo)
    assert capa and _canto(cv2.imread(capa)) == CANTO_DO_GIRO[0]
    hora = Path(capa).stat().st_mtime_ns

    # girar outra folha nao mexe na capa
    tela.ir_para_pagina(2)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    projetos.esperar_gravacoes(10)
    assert Path(capa).stat().st_mtime_ns == hora

    tela.ir_para_pagina(0)
    tela.barra_girar.botoes_de_giro[girar.GIRO_DIREITA].click()
    assert projetos.esperar_gravacoes(10)
    assert _canto(cv2.imread(capa)) == CANTO_DO_GIRO[90]
    tela.desfazer()
    assert projetos.esperar_gravacoes(10)
    assert _canto(cv2.imread(capa)) == CANTO_DO_GIRO[0]


def test_d2_a_capa_e_desenhada_fora_do_fio_da_janela(pasta, monkeypatch):
    """projetos.refazer_miniatura_por_tras volta na hora: quem desenha e o
    fio de gravar."""
    import threading

    import projetos

    caminho = _pdf_com_canto(pasta, 1)
    resumo = projetos.Resumo(pasta=str(pasta / "proj"), caminho_entrada=str(caminho))
    Path(resumo.pasta).mkdir()
    fios = []
    original = projetos._escrever_miniatura
    monkeypatch.setattr(projetos, "_escrever_miniatura",
                        lambda *a: fios.append(threading.current_thread()) or original(*a))
    projetos.refazer_miniatura_por_tras(resumo, 270)
    assert projetos.esperar_gravacoes(10)
    assert fios and fios[0] is not threading.main_thread()
    import cv2

    assert _canto(cv2.imread(str(Path(resumo.pasta) / "capa.png"))) == CANTO_DO_GIRO[270]
    # pasta que nao existe mais (tirado da lista): nao recria
    sumida = projetos.Resumo(pasta=str(pasta / "sumiu"), caminho_entrada=str(caminho))
    projetos.refazer_miniatura_por_tras(sumida, 90)
    assert projetos.esperar_gravacoes(10)
    assert not (pasta / "sumiu").exists()


# ---------------------------------------------------------------------------
# A pendencia da D2 (anotada pelo implementador do girar, 06/10/2026): mudar o
# corte ou o angulo de uma pagina com zonas ainda no formato antigo, antes de
# a conversao chegar nela, deslocava as zonas. Ganha a mesma protecao do giro
# (9f8d4e5): espera, avisa e pede a conversao.
# ---------------------------------------------------------------------------


def _livro_com_zona_antiga(janela, pasta, monkeypatch):
    from core import zonas_na_folha as zf
    from core.selecao import GRAVURA, MAO, RETANGULO, Regiao

    # a previa (outro fio) nao converte a pagina no meio do teste
    monkeypatch.setattr(zf, "acompanhar", lambda pagina, geometria: False)
    janela.abrir_livro(str(_pdf_com_canto(pasta, 4)))
    janela.projeto.detectar_regioes = False
    janela._analise_pronta(pipeline.analisar_projeto(janela.projeto))
    tela = janela.tela_conferir
    pagina = janela.projeto.paginas[0]
    pagina.selecao = [Regiao(tipo=GRAVURA, forma=RETANGULO, pontos=[(0.1, 0.1), (0.4, 0.3)],
                             origem=MAO).para_dicionario()]
    pagina.geometria_das_zonas = None              # formato antigo
    pedidos = []
    monkeypatch.setattr(janela, "_comecar_a_converter_as_zonas", lambda: pedidos.append(1))
    return tela, pagina, pedidos


def _preparo(janela, indice):
    p = janela.projeto.paginas[indice]
    f = janela.projeto.folhas[p.folha]
    return (f.rotacao, f.dividir, f.posicao_corte, p.recorte, p.angulo_manual)


@pytest.mark.parametrize("mudanca", [
    "mover_corte", "corte_em_todas", "alternar_dividir", "mover_recorte", "sem_recorte",
    "recorte_em_todas", "mover_angulo", "angulo_zero",
])
def test_pendencia_d2_corte_e_angulo_esperam_as_zonas_antigas(janela, pasta, monkeypatch,
                                                              mudanca):
    from core import zonas_na_folha as zf

    tela, pagina, pedidos = _livro_com_zona_antiga(janela, pasta, monkeypatch)
    acoes = {
        "mover_corte": lambda: tela._mover_corte(0.42),
        "corte_em_todas": tela._corte_em_todas,
        "alternar_dividir": tela._alternar_dividir,
        "mover_recorte": lambda: tela._mover_recorte((0.1, 0.1, 0.8, 0.8)),
        "sem_recorte": tela._sem_recorte,
        "recorte_em_todas": tela._recorte_em_todas,
        "mover_angulo": lambda: tela._mover_angulo(2.5),
        "angulo_zero": tela._angulo_zero,
    }
    tela.ir_para_pagina(0)
    if mudanca == "recorte_em_todas":
        janela.projeto.paginas[0].recorte = [0.05, 0.05, 0.9, 0.9]
    antes = _preparo(janela, 0)
    feitas = len(janela.acoes.feitas)
    acoes[mudanca]()
    assert _preparo(janela, 0) == antes, "mudou o preparo da pagina com zonas antigas"
    assert len(janela.acoes.feitas) == feitas
    assert janela.avisos and "preparando as marcações" in janela.avisos[-1]
    assert pedidos == [1]

    # convertida (a geometria anotada), a mudanca vale
    pagina.geometria_das_zonas = zf.geometria_do_desenho(400 / 560, 0, None, "inteira", None, 0.0)
    acoes[mudanca]()
    assert len(janela.acoes.feitas) == feitas + 1


def test_pendencia_d2_outra_pagina_sem_zonas_antigas_muda_normalmente(janela, pasta,
                                                                       monkeypatch):
    tela, _pagina, pedidos = _livro_com_zona_antiga(janela, pasta, monkeypatch)
    tela.ir_para_pagina(2)
    tela._mover_angulo(1.5)
    assert janela.projeto.paginas[2].angulo_manual == 1.5
    assert not janela.avisos and not pedidos


def test_pendencia_d2_desfazer_de_outra_sessao_tambem_espera(janela, pasta, monkeypatch):
    """O historico de acoes volta ao abrir o livro: um Ctrl+Z que mudaria o
    corte de uma pagina ainda nao convertida espera tambem."""
    from modelos import Acao

    tela, _pagina, pedidos = _livro_com_zona_antiga(janela, pasta, monkeypatch)
    janela.projeto.paginas[0].angulo_manual = 3.0
    janela.acoes.feitas.append(Acao.nova("ajustar_angulo", "pagina", [0],
                                         {"angulo_manual": None}, {"angulo_manual": 3.0},
                                         "Angulo da página 1"))
    tela.desfazer()
    assert janela.projeto.paginas[0].angulo_manual == 3.0
    assert janela.avisos and pedidos == [1]
