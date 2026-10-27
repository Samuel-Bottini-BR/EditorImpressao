"""As provas de comportamento da etapa 6 da obra de 26/10/2026: ver o livro na área de trabalho
(CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede é o que está
no lugar da página (a ferramenta, os pares ou o antes e depois), QUAIS páginas formam os pares e em
que ordem, a imagem que cada página dos pares recebe (a prévia, já dividida), a página da vez, o
zoom e o projeto gravado.

  D-015 (22/10, a mais recente): "Uma página / Duas lado a lado" na barra de baixo, como no livro
      aberto do UPDF aprovado · 904 A: "A — Sim, no menu Ver".
  D-006 (06/10): "eu não quero padrão eu quero como opção um botão que eu clique e veja pagina
      lado a lado" · 202 A: "Pares rolando, um embaixo do outro."
  D-058 (20/10): o menu Ver ganha "Ver lado a lado".
  D-007 (26/10): "quando eu escolher para começar no automatico e dividir as folhas o livro tem
      que aparecer em uma pagina por vez para mim."
  D-343 (05/10): "Na opção 2 (pares), clicar abre as duas páginas lado a lado, como vai ser
      impresso."
  D-021 (29/07, paráfrase): navegação com a roda do mouse, Page Up/Down, Home/End · PEDIDOS.md:
      "Page Up / Page Down pula 10 páginas" ("Pula 10 páginas de cada vez") · pedido da etapa 6
      (27/10): "roda do mouse troca de página (quando não está com zoom)".
  Desenho decidido da barra de baixo (rodada 13): "antes / depois", "– 78% +", "ajustar à tela".
  Troca da etapa 4: quando a lista de páginas muda, a tela fica na mesma folha (também no lado a
      lado).

Livro sintético (papel amarelado com "texto"), dividido pelo Automático como o Kaique faz.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt  # noqa: E402
from PySide6.QtGui import QKeyEvent, QWheelEvent  # noqa: E402

from core import automatico as A  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402

DPI = 100
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- o livro de teste -------------------------------------------------------------

def _pagina(numero: int, largura: int = 420, altura: int = 600) -> np.ndarray:
    """Papel amarelado com "texto" e, no alto, `numero` quadradinhos pretos (para saber
    qual página é qual na imagem que os pares recebem)."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 120, 30):
        img[y:y + 9, 70:largura - 70] = 25
    for k in range(numero % 12):
        img[60:80, 70 + k * 24:86 + k * 24] = 0
    return img


def _pdf(caminho: Path, folhas: int) -> str:
    """Um livro aberto de `folhas` folhas (duas páginas por folha, a dobra no meio)."""
    doc = fitz.open()
    for f in range(folhas):
        img = np.concatenate([_pagina(2 * f), _pagina(2 * f + 1)], axis=1)
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


# --- a janela ---------------------------------------------------------------------

@pytest.fixture(scope="module")
def app():
    from PySide6.QtWidgets import QApplication

    return QApplication.instance() or QApplication([])


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    import projetos

    projetos_dir = tmp_path / "projetos"
    projetos_dir.mkdir()
    monkeypatch.setattr(projetos, "pasta_dos_projetos", lambda: projetos_dir)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "dados"))
    return tmp_path


@pytest.fixture
def janela(app, pasta):
    from ui.janela_principal import JanelaPrincipal

    janela = JanelaPrincipal()
    janela.resize(1280, 657)
    yield janela
    janela._fechar_a_janela_do_automatico()
    if janela.aviso_do_fundo is not None:
        janela.aviso_do_fundo.done(0)
    if janela.previas is not None:
        janela.previas.parar()
    janela.close()


def _assentar(vezes: int = 6) -> None:
    from PySide6.QtWidgets import QApplication

    for _ in range(vezes):
        QApplication.processEvents()


def _esperar(condicao, segundos: float = 40.0, motivo: str = "") -> None:
    import time

    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


def _dividido(janela, tmp_path: Path, folhas: int = 5):
    """O caminho do Kaique: abrir o livro e rodar o Automático só com "Dividir"."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", folhas))
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    tela = janela.tela_conferir
    assert len(janela.projeto.paginas) == 2 * folhas
    return tela


def _roda(vista, passos: int, ctrl: bool = False) -> None:
    """Uma volta da roda do mouse em cima da página (como o Windows manda)."""
    from PySide6.QtWidgets import QApplication

    centro = QPointF(vista.width() / 2, vista.height() / 2)
    evento = QWheelEvent(centro, vista.mapToGlobal(centro), QPoint(0, 0), QPoint(0, 120 * passos),
                         Qt.NoButton, Qt.ControlModifier if ctrl else Qt.NoModifier,
                         Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


def _tecla(janela, tecla) -> None:
    """A tecla como a janela recebe (JanelaPrincipal.keyPressEvent)."""
    janela.keyPressEvent(QKeyEvent(QEvent.KeyPress, tecla, Qt.NoModifier))


def _quadradinhos(img: np.ndarray) -> int:
    """Quantos quadradinhos pretos a página tem no alto (o número dela, ver _pagina)."""
    cinza = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    faixa = cinza[: int(cinza.shape[0] * 0.18)] < 60       # acima do "texto" (que começa a 23%)
    colunas = faixa.any(axis=0).astype(np.int8)
    return int((np.diff(np.concatenate([[0], colunas])) == 1).sum())


# --- D-015 / D-006 / D-007: "Uma página" / "Duas lado a lado" ---------------------

def test_d015_duas_lado_a_lado_na_barra_de_baixo_com_os_pares_do_livro(janela, tmp_path):
    """D-015 ("Uma página / Duas lado a lado" na barra de baixo), D-006/202 A (pares rolando),
    D-347 (a 1 sozinha à direita; o par da mesma altura). Dividido pelo Automático, o livro abre
    em "Uma página" (D-007); "Duas lado a lado" põe no lugar da página os pares das páginas
    COMO VÃO SAIR: a 1 sozinha à direita, depois 2-3, 4-5...; cada página recebe a prévia já
    dividida (em pé, a página certa); "Uma página" volta. No código antigo a barra de baixo
    não tinha esses botões (o lado a lado só existia no livro aberto e na grade)."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _dividido(janela, tmp_path)
    assert tela.mostrar == UMA and tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert tela.botoes_mostrar[UMA].isChecked() and not tela.botoes_mostrar[DUAS].isChecked()
    assert tela.item_atual.metade in ("esquerda", "direita")        # uma página, não a folha

    tela.ir_para_pagina(3)
    tela.botoes_mostrar[DUAS].click()
    _assentar()
    pares = tela.lado_a_lado
    assert tela.vista_da_pagina.currentWidget() is pares
    assert pares.indices == list(range(10))
    assert pares._linhas()[:3] == [[None, 0], [1, 2], [3, 4]]
    assert pares.indice_da_vez() == 3 and tela.indice_pagina == 3
    # a 1 sozinha, na metade da direita; o par da mesma altura, lado a lado
    ret = dict(pares.retangulos_exatos())
    meio = pares.folhas.width() / 2
    assert ret[0].left() >= meio - 1
    assert abs(ret[1].height() - ret[2].height()) < 0.5 and ret[1].right() <= ret[2].left() + 1
    # as páginas recebem a prévia (dividida: em pé) e cada uma é a dela
    _esperar(lambda: all(i in pares.guardadas for i in (1, 2, 3, 4)), motivo="as prévias dos pares")
    for posicao in (1, 2, 3, 4):
        pix = pares.guardadas[posicao]
        assert pix.height() > pix.width(), "a página dos pares não está dividida"
        imagem = pix.toImage().convertToFormat(pix.toImage().Format.Format_Grayscale8)
        largura, altura = imagem.width(), imagem.height()
        dados = np.frombuffer(imagem.constBits(), np.uint8).reshape(altura, imagem.bytesPerLine())[:, :largura]
        assert _quadradinhos(dados) == posicao % 12, f"a posição {posicao} recebeu outra página"

    tela.botoes_mostrar[UMA].click()
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem and tela.indice_pagina == 3


def test_d058_menu_ver_tem_ver_lado_a_lado_e_anda_com_a_barra(janela, tmp_path):
    """D-058 (menu Ver: "Ver lado a lado") e D-015 ("e no menu Ver"): marcar o item mostra os
    pares; a barra de baixo acompanha; escolher "Uma página" na barra desmarca o menu. No
    código antigo o item não existia."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _dividido(janela, tmp_path)
    item = janela.menu.acoes["lado_a_lado"]
    assert item.isCheckable() and not item.isChecked()
    item.trigger()
    assert tela.mostrar == DUAS and tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert tela.botoes_mostrar[DUAS].isChecked()
    tela.botoes_mostrar[UMA].click()
    assert not item.isChecked() and tela.vista_da_pagina.currentWidget() is tela.area_imagem


def test_d007_todo_livro_abre_uma_pagina_por_vez(janela, tmp_path):
    """D-007 + D-006 ("não quero padrão"): mesmo depois de escolher "Duas lado a lado", o livro
    que se abre de novo aparece uma página por vez. No código antigo não havia escolha."""
    from ui.widgets.paginas_rolando import DUAS, UMA

    tela = _dividido(janela, tmp_path)
    tela.definir_mostrar(DUAS)
    janela._salvar_agora()
    janela.abrir_livro(janela.projeto.caminho_entrada)
    tela = janela.tela_conferir
    assert tela.mostrar == UMA and tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert not janela.menu.acoes["lado_a_lado"].isChecked()
    assert not tela.trabalha_com_folhas


def test_no_dividir_a_folha_inteira_continua(janela, tmp_path):
    """D-007 / D-501: a folha inteira com a linha fica só dentro do Dividir. Com "Duas lado a
    lado" escolhido, o Dividir continua mostrando a folha (para consertar), e os botões do ver
    ficam apagados com a explicação; voltando às páginas, os pares voltam."""
    from ui.tela_conferir import ABA_CORTE
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.definir_mostrar(DUAS)
    tela.escolher_ferramenta("dividir")
    assert tela.aba_atual == ABA_CORTE
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem
    assert not tela.botoes_mostrar[DUAS].isEnabled() and "Dividir" in tela.botoes_mostrar[DUAS].toolTip()
    tela.escolher_ferramenta("mao")
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado


def test_pares_sao_os_do_livro_que_vai_sair(janela, tmp_path):
    """"Pares certos (página da esquerda e da direita do livro, capa sozinha)": a página tirada
    do livro não está no PDF, então não entra nos pares, e os pares andam (a 5 vira par da 6).
    "Trazer de volta" a devolve."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(3)
    tela.apagar_pagina()                                   # "Tirar do livro"
    assert janela.projeto.paginas[3].apagada
    tela.definir_mostrar(DUAS)
    pares = tela.lado_a_lado
    assert pares.indices == [0, 1, 2, 4, 5, 6, 7, 8, 9]
    assert [pares.indices[i] for i in pares._linhas()[2]] == [4, 5]   # as páginas 5 e 6
    tela.desfazer()
    assert pares.indices == list(range(10))


def test_troca_da_etapa_4_lista_muda_e_o_lado_a_lado_fica_na_mesma_folha(janela, tmp_path):
    """Troca da etapa 4: "a página da vez agora fica na mesma folha quando a lista muda
    (lista_de_paginas_mudou); quem fizer o 'Ver lado a lado' deve usar o mesmo cuidado."
    Com os pares à vista na folha 4, desfazer o "não dividir" da folha 2 muda os números das
    páginas: a tela e os pares continuam na folha 4."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("dividir")
    tela._ir_para(1)
    tela._nao_dividir()                                    # a folha 2 vira uma página só
    assert len(janela.projeto.paginas) == 9
    tela.escolher_ferramenta("mao")
    primeira_da_folha_4 = next(p.indice for p in janela.projeto.paginas if p.folha == 3)
    assert primeira_da_folha_4 == 5
    tela.ir_para_pagina(primeira_da_folha_4)
    tela.definir_mostrar(DUAS)
    assert tela.lado_a_lado.indice_da_vez() == 5
    tela.desfazer()                                        # a folha 2 volta a ter duas páginas
    assert len(janela.projeto.paginas) == 10
    assert tela.indice_folha == 3 and tela.indice_pagina == 6
    assert tela.lado_a_lado.indices == list(range(10))
    assert tela.lado_a_lado.indice_da_vez() == 6
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado


def test_d343_clicar_num_par_da_grade_abre_lado_a_lado(janela, tmp_path):
    """D-343: "Na opção 2 (pares), clicar abre as duas páginas lado a lado, como vai ser
    impresso." Na grade "Todas as páginas" em pares, clicar no par 4-5 volta ao trabalho com
    os pares nele. Uma a uma, o clique volta a uma página só (como sempre). No código antigo o
    clique só ia à página."""
    from ui.widgets.paginas_rolando import UMA
    from ui.widgets.todas_as_paginas import EM_PARES, UMA_A_UMA

    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("mao")
    tela.abrir_todas_as_paginas()
    tela.todas.definir_vista(UMA_A_UMA)
    tela.todas._clicou(2)
    assert tela.mostrar == UMA and tela.indice_pagina == 2
    tela.abrir_todas_as_paginas()
    tela.todas.definir_vista(EM_PARES)
    tela.todas._clicou(3)
    assert tela.pilha_da_tela.currentWidget() is tela.trabalho
    assert tela.vista_da_pagina.currentWidget() is tela.lado_a_lado
    assert tela.indice_pagina == 3 and tela.lado_a_lado.indice_da_vez() == 3


# --- barra de baixo: antes / depois, zoom, ajustar à tela ---------------------------

def test_antes_depois_mostra_o_original_e_como_vai_sair(janela, tmp_path):
    """Desenho decidido da barra de baixo: "antes / depois" (o Original × como vai sair, a
    chave "Comparar com o Original" da tela cheia, R11 601 A). Numa página em Preto e branco, o
    lado "antes" é o papel amarelado do Original e o "depois" o papel branco do Preto e branco;
    o projeto não muda. No código antigo não havia o botão."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(2)
    tela._escolher_filtro(PRETO_E_BRANCO)
    filtros = [p.filtro for p in janela.projeto.paginas]
    tela.botao_antes_depois.click()
    vista = tela.vista_antes_depois
    assert tela.vista_da_pagina.currentWidget() is vista
    _esperar(lambda: vista.antes is not None and vista.depois is not None, motivo="as duas prévias")
    assert vista.comparando and vista.rotulos == ("antes: Original", "depois: Preto e branco")

    def papel(pix):
        imagem = pix.toImage()
        cor = imagem.pixelColor(imagem.width() // 2, 8)     # papel, no alto da página
        return cor.red(), cor.green(), cor.blue()

    r, _g, b = papel(vista.antes)
    assert r - b > 30, "o 'antes' não é o Original (papel amarelado)"
    r, _g, b = papel(vista.depois)
    assert abs(r - b) < 12, "o 'depois' não é como vai sair (Preto e branco)"
    assert [p.filtro for p in janela.projeto.paginas] == filtros
    tela.botao_antes_depois.click()
    assert tela.vista_da_pagina.currentWidget() is tela.area_imagem


def test_zoom_da_barra_de_baixo(janela, tmp_path):
    """Desenho decidido: "– 78% +" e "ajustar à tela" na barra de baixo. "+" aproxima e o
    número mostra o zoom; "ajustar à tela" volta a 100%; no lado a lado (a página cabe na
    tela) os botões do zoom ficam apagados."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("mao")
    vista = tela.editor_selecao
    assert tela.rotulo_do_zoom.text() == "100%" and not tela.botao_menos_zoom.isEnabled()
    tela.botao_mais_zoom.click()
    assert abs(vista.zoom - 1.25) < 1e-6 and tela.rotulo_do_zoom.text() == "125%"
    assert tela.botao_menos_zoom.isEnabled()
    tela.botao_ajustar_a_tela.click()
    assert vista.zoom == 1.0 and tela.rotulo_do_zoom.text() == "100%"
    tela.definir_mostrar(DUAS)
    assert not tela.botao_mais_zoom.isEnabled() and not tela.botao_ajustar_a_tela.isEnabled()


# --- D-021: roda do mouse, Page Up/Down, Home/End ----------------------------------

def test_d021_roda_troca_de_pagina_sem_zoom_e_da_zoom_com_zoom(janela, tmp_path):
    """Pedido da etapa 6 (27/10): "roda do mouse troca de página (quando não está com zoom)".
    Sem zoom, a roda para baixo vai à próxima página e para cima à anterior; com zoom, a roda
    dá zoom como antes (D-026) e não troca de página; Ctrl+roda dá zoom sempre. Vale também
    no Endireitar (outra peça de página). No código antigo a roda só dava zoom."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(4)
    vista = tela.editor_selecao
    _roda(vista, -1)
    assert tela.indice_pagina == 5 and vista.zoom == 1.0
    _roda(vista, 1)
    assert tela.indice_pagina == 4
    _roda(vista, 1, ctrl=True)                             # Ctrl+roda: zoom
    assert tela.indice_pagina == 4 and abs(vista.zoom - 1.25) < 1e-6
    _roda(vista, 1)                                        # com zoom: zoom, não página
    assert tela.indice_pagina == 4 and vista.zoom > 1.25
    assert tela.rotulo_do_zoom.text() == f"{round(vista.zoom * 100)}%"
    tela.escolher_ferramenta("endireitar")
    tela.mudar_o_zoom(None)
    _roda(tela.visualizadores["angulo"], -1)
    assert tela.indice_pagina == 5


def test_d021_page_down_pula_10_e_home_end(janela, tmp_path):
    """D-021 + PEDIDOS.md ("Page Up / Page Down pula 10 páginas"): na área de trabalho Page
    Down anda 10 páginas, Page Up volta 10, Home vai à primeira e End à última (no Dividir,
    folhas). No código antigo nenhuma delas fazia nada na área de trabalho."""
    tela = _dividido(janela, tmp_path, folhas=13)          # 26 páginas
    tela.escolher_ferramenta("mao")
    tela.ir_para_pagina(0)
    _tecla(janela, Qt.Key_PageDown)
    assert tela.indice_pagina == 10
    _tecla(janela, Qt.Key_PageDown)
    _tecla(janela, Qt.Key_PageDown)
    assert tela.indice_pagina == 25                        # para na última
    _tecla(janela, Qt.Key_PageUp)
    assert tela.indice_pagina == 15
    _tecla(janela, Qt.Key_Home)
    assert tela.indice_pagina == 0
    _tecla(janela, Qt.Key_End)
    assert tela.indice_pagina == 25
    tela.escolher_ferramenta("dividir")
    _tecla(janela, Qt.Key_Home)
    assert tela.indice_folha == 0
    _tecla(janela, Qt.Key_PageDown)
    assert tela.indice_folha == 10
