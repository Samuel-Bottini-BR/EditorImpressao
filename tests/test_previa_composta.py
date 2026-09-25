"""Passo 8 do plano "corrigir bugs do teste do Boécio": a aba Bordas mostra
a prévia JÁ COMPOSTA (recorte + margem branca da folha), ao vivo, e o
visualizador sabe onde o conteúdo fica dentro do canvas maior (decisão 3).

Roda com um PDF de verdade e `GerenciadorPrevias` real (a composição só
acontece depois que a prévia assíncrona chega), mesmo padrão de
`tests/test_marcacao_em_todas.py`.
"""

from __future__ import annotations

import time

import pytest

fitz = pytest.importorskip("fitz")
pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.folha import conteudo_como_retangulo  # noqa: E402
from historico_acoes import HistoricoAcoes  # noqa: E402
from modelos import ConfigFolha, ConfigPagina, Projeto  # noqa: E402


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def livro(tmp_path):
    caminho = tmp_path / "livro.pdf"
    doc = fitz.open()
    # pagina quadrada, facilita a conta de cm
    doc.new_page(width=400, height=400)
    doc.save(str(caminho))
    doc.close()
    return caminho


def _projeto(caminho, recorte, tamanho_folha_cm) -> Projeto:
    p = Projeto(caminho_entrada=str(caminho), nome="x")
    p.dividir_folhas = False
    p.endireitar = False
    p.cortar_bordas = True
    p.limpar = False
    p.folhas = [ConfigFolha(indice=0)]
    p.paginas = [ConfigPagina(
        indice=0, folha=0, recorte=recorte, tamanho_folha_cm=tamanho_folha_cm)]
    return p


def _esperar_ate(condicao, tempo_limite=5.0) -> bool:
    fim = time.perf_counter() + tempo_limite
    while time.perf_counter() < fim:
        QApplication.processEvents()
        if condicao():
            return True
        time.sleep(0.01)
    return condicao()


@pytest.fixture
def conferir_bordas(app, livro):
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_BORDAS, TelaConferir

    projeto = _projeto(livro, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=(20.0, 20.0))
    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)

    vis = tela.visualizadores[ABA_BORDAS]
    assert _esperar_ate(lambda: vis.tamanho_da_pagina_px() != (0, 0)), (
        "a prévia composta nunca chegou")
    yield tela, vis
    previas.parar()


def test_previa_da_aba_bordas_por_padrao_mostra_a_imagem_nao_cortada(conferir_bordas):
    """Fora do modo "Mover conteúdo" (o padrão), a aba Bordas mostra a folha
    girada/dividida mas NUNCA cortada - ver `_atualizar_previa_para_recorte`
    e o bug real do Samuel (23/09/2026, corte comprimindo sozinho). Por isso
    o pixmap exibido bate exatamente com `tamanho_da_pagina_px()` aqui: os
    dois vêm da MESMA imagem, sem composição."""
    _tela, vis = conferir_bordas
    largura, altura = vis.tamanho_da_pagina_px()
    assert vis._pixmap is not None
    assert vis._pixmap.width() == largura
    assert vis._pixmap.height() == altura


def test_recorte_nao_pula_de_posicao_ao_soltar_o_mouse(conferir_bordas):
    """Bug real relatado pelo Samuel ao vivo (23/09/2026): arrastar a alça
    direita do recorte na aba Bordas, soltar, e a linha verde "pula" para
    outro lugar - ele descreveu como "corto até a metade da coroa, mas o
    corte vai pra frente sozinho". Causa raiz: a aba mostrava a prévia JÁ
    cortada por `pagina.recorte` (a mesma usada por Marcar/Filtro) - o
    retângulo era desenhado como fração de uma imagem que já era um recorte,
    e cada atualização reaplicava a fração em cima do resultado anterior,
    comprimindo o corte sozinho. `_atualizar_previa_para_recorte` corrige
    mostrando sempre a imagem girada/dividida, nunca cortada.

    Este teste vai pelo caminho REAL (sinal -> `_registrar` -> invalida o
    cache -> prévia assíncrona nova), não só a matemática interna do widget -
    é exatamente o tipo de teste que faltava (a suíte de `test_visualizador.py`
    nunca refaz a prévia depois de soltar, por isso nunca pegou isto)."""
    from PySide6.QtCore import QPoint

    tela, vis = conferir_bordas

    r0 = vis._retangulo_recorte()
    alcas = vis._alcas(r0)
    origem = alcas["l"]

    vis._arrastando = "l"
    vis._ponto_inicial = origem
    vis._recorte_inicial = vis.recorte
    destino = QPoint(origem.x() - 30, origem.y())
    vis._mover_recorte(destino)
    x_durante = vis._retangulo_recorte().right()

    vis._arrastando = None
    vis.recorte_movido.emit(vis.recorte)

    assert _esperar_ate(
        lambda: tela.projeto.paginas[0].recorte is not None
        and abs(tela.projeto.paginas[0].recorte[2] - vis.recorte[2]) < 1e-6
    )
    QApplication.processEvents()

    x_depois = vis._retangulo_recorte().right()
    # tolerância de 1px: arredondamento de int()/round(), não o pulo do bug
    assert abs(x_depois - x_durante) <= 1, (
        f"o retângulo pulou de x={x_durante} (durante o arrasto, onde o "
        f"mouse estava) para x={x_depois} (depois de soltar e recarregar) - "
        "provavelmente voltou a compor com o recorte já aplicado")


def test_previa_fica_maior_que_o_conteudo_no_modo_mover_conteudo(conferir_bordas):
    """Só DENTRO do modo "Mover conteúdo" a prévia mostra a folha composta
    (recorte já aplicado + margem branca) - maior que o conteúdo, porque aí
    sim é a posição/tamanho do conteúdo dentro da folha que está em jogo."""
    tela, vis = conferir_bordas
    tela.botao_mover_conteudo.setChecked(True)
    tela._alternar_mover_conteudo()
    assert _esperar_ate(lambda: vis._pixmap is not None and vis._pixmap.width() > vis.tamanho_da_pagina_px()[0])

    largura_conteudo, altura_conteudo = vis.tamanho_da_pagina_px()
    assert vis._pixmap.width() > largura_conteudo
    assert vis._pixmap.height() > altura_conteudo


# --- Fase 2 aprovada pelo Samuel (22/09/2026): mover o conteúdo dentro da
# folha, ligado de ponta a ponta (botão -> modo do widget -> sinal ->
# ConfigPagina.conteudo_deslocamento) --------------------------------------

def test_botao_mover_conteudo_fica_habilitado_com_folha_escolhida(conferir_bordas):
    tela, _vis = conferir_bordas
    assert tela.botao_mover_conteudo.isEnabled()


def test_sem_folha_escolhida_botao_mover_conteudo_fica_desabilitado(app, livro):
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_BORDAS, TelaConferir

    projeto = _projeto(livro, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=None)
    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)
    vis = tela.visualizadores[ABA_BORDAS]
    assert _esperar_ate(lambda: vis.tamanho_da_pagina_px() != (0, 0))

    assert not tela.botao_mover_conteudo.isEnabled()
    previas.parar()


def test_alternar_mover_conteudo_troca_o_modo_do_visualizador(conferir_bordas):
    from ui.widgets.visualizador import MODO_CONTEUDO, MODO_RECORTE

    tela, vis = conferir_bordas
    assert vis.modo == MODO_RECORTE

    tela.botao_mover_conteudo.setChecked(True)
    tela._alternar_mover_conteudo()
    assert vis.modo == MODO_CONTEUDO

    tela.botao_mover_conteudo.setChecked(False)
    tela._alternar_mover_conteudo()
    assert vis.modo == MODO_RECORTE


def test_mover_conteudo_grava_o_deslocamento_na_pagina(conferir_bordas):
    from core.folha import deslocamento_do_retangulo

    tela, vis = conferir_bordas
    # a prévia composta (que este teste depende de `vis._retangulo_conteudo`/
    # `tamanho_da_pagina_px()` refletirem) só existe no modo "Mover conteúdo"
    # - fora dele a aba Bordas mostra a imagem não cortada, ver
    # `_atualizar_previa_para_recorte`.
    tela.botao_mover_conteudo.setChecked(True)
    tela._alternar_mover_conteudo()
    assert _esperar_ate(lambda: vis._retangulo_conteudo != (0.0, 0.0, 1.0, 1.0))

    pagina = tela.projeto.paginas[0]
    assert pagina.conteudo_deslocamento == (0.0, 0.0)

    # desloca o retangulo do conteudo 10% para a direita e 5% para baixo
    x, y, w, h = vis._retangulo_conteudo
    novo_retangulo = (x + 0.1, y + 0.05, w, h)

    tela._mover_conteudo(novo_retangulo)

    _escala, esperado = deslocamento_do_retangulo(
        novo_retangulo, pagina.tamanho_folha_cm, vis.tamanho_da_pagina_px(), vis.dpi_atual())
    assert pagina.conteudo_deslocamento == pytest.approx(
        (round(esperado[0], 4), round(esperado[1], 4)), abs=1e-6)
    # conteudo_escala nao muda nesta entrega (so mover, nao redimensionar)
    assert pagina.conteudo_escala == 1.0


def test_redimensionar_conteudo_grava_a_escala_na_pagina(conferir_bordas):
    """Fase 3 (confirmada pelo Samuel, 22/09/2026: "quero conseguir
    redimensionar o conteudo tambem"): quando o retângulo que chega de
    `Visualizador.conteudo_movido` tem w/h DIFERENTE do que a página já
    tinha (arrastou um canto, não só o meio), `conteudo_escala` também
    precisa ser gravado - antes desta correção só `conteudo_deslocamento`
    era persistido, `_escala` era descartado (`_escala, deslocamento = ...`)."""
    from core.folha import deslocamento_do_retangulo

    tela, vis = conferir_bordas
    pagina = tela.projeto.paginas[0]
    assert pagina.conteudo_escala == 1.0

    x, y, w, h = vis._retangulo_conteudo
    fator = 0.8   # encolhe mantendo o centro
    novo_w, novo_h = w * fator, h * fator
    centro_x, centro_y = x + w / 2, y + h / 2
    novo_retangulo = (centro_x - novo_w / 2, centro_y - novo_h / 2, novo_w, novo_h)

    tela._mover_conteudo(novo_retangulo)

    escala_esperada, _deslocamento = deslocamento_do_retangulo(
        novo_retangulo, pagina.tamanho_folha_cm, vis.tamanho_da_pagina_px(), vis.dpi_atual())
    assert pagina.conteudo_escala == pytest.approx(round(escala_esperada, 4), abs=1e-6)


def test_mover_conteudo_e_uma_acao_do_historico_desfazivel(conferir_bordas):
    tela, vis = conferir_bordas
    pagina = tela.projeto.paginas[0]

    x, y, w, h = vis._retangulo_conteudo
    tela._mover_conteudo((x + 0.1, y, w, h))
    assert pagina.conteudo_deslocamento != (0.0, 0.0)

    tela.acoes.desfazer(tela.projeto)
    assert tela.projeto.paginas[0].conteudo_deslocamento == (0.0, 0.0)


def test_tamanho_da_pagina_continua_sendo_o_do_recorte_nao_o_da_folha(conferir_bordas):
    """`tamanho_da_pagina_px` alimenta o cálculo de cm do recorte
    (`_escolher_tamanho_da_folha`) - tem que continuar sendo o tamanho do
    CONTEÚDO, nunca o da folha maior."""
    _tela, vis = conferir_bordas
    largura_px, altura_px = vis.tamanho_da_pagina_px()
    dpi = vis.dpi_atual()
    # o conteudo e o recorte (0.25,0.25,0.5,0.5) da pagina 400x400pt a
    # DPI_PREVIA - o importante e ser bem menor que os 20x20cm da folha
    largura_cm = largura_px / dpi * 2.54
    altura_cm = altura_px / dpi * 2.54
    assert largura_cm < 15.0, f"tamanho_da_pagina_px parece ser o da FOLHA: {largura_cm}cm"
    assert altura_cm < 15.0


def test_retangulo_do_conteudo_bate_com_conteudo_como_retangulo(conferir_bordas):
    """A área do conteúdo dentro do canvas que o widget usa para desenhar e
    mapear o mouse tem que ser EXATAMENTE a mesma que
    `core.folha.conteudo_como_retangulo` calcularia - a mesma fonte da
    verdade usada por `compor_na_folha` na exportação final.

    Só vale dentro do modo "Mover conteúdo" - fora dele a aba Bordas mostra a
    imagem não cortada, ver `_atualizar_previa_para_recorte`."""
    tela, vis = conferir_bordas
    tela.botao_mover_conteudo.setChecked(True)
    tela._alternar_mover_conteudo()
    assert _esperar_ate(lambda: vis._retangulo_conteudo != (0.0, 0.0, 1.0, 1.0))

    tamanho_conteudo_px = vis.tamanho_da_pagina_px()
    esperado = conteudo_como_retangulo(
        1.0, (0.0, 0.0), (20.0, 20.0), tamanho_conteudo_px, vis.dpi_atual())
    assert vis._retangulo_conteudo == pytest.approx(esperado, abs=1e-6)


def test_sem_tamanho_de_folha_a_previa_continua_do_tamanho_do_conteudo(app, livro):
    """`tamanho_folha_cm=None` (padrão) - comportamento de sempre, pixmap ==
    conteúdo, sem margem nenhuma."""
    from ui.tarefas import GerenciadorPrevias
    from ui.tela_conferir import ABA_BORDAS, TelaConferir

    projeto = _projeto(livro, recorte=(0.25, 0.25, 0.5, 0.5), tamanho_folha_cm=None)
    tela = TelaConferir()
    previas = GerenciadorPrevias(str(livro), projeto, tela)
    tela.carregar(projeto, HistoricoAcoes(), previas)

    vis = tela.visualizadores[ABA_BORDAS]
    assert _esperar_ate(lambda: vis.tamanho_da_pagina_px() != (0, 0))

    assert vis._pixmap is not None
    assert (vis._pixmap.width(), vis._pixmap.height()) == vis.tamanho_da_pagina_px()
    assert vis._retangulo_conteudo == (0.0, 0.0, 1.0, 1.0)
    previas.parar()
