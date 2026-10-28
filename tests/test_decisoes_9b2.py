"""As provas de comportamento da etapa 9b-2 da obra de 26/10/2026: a área de trabalho
(CLAUDE.md §11, regra 4; Livro de decisões, docs/plano/DECISOES.md).

Cada teste diz a decisão e as palavras do Samuel. Aparência não conta: o que se mede é o projeto
gravado, a imagem que sai (no PDF ou na tela), a página da vez e o desfazer. Os que provam um
conserto de defeito (CLAUDE.md §4.7) falham no código antigo (`obra-2026-10-26` = 27b4c52): o
resultado está em relatorios/obra-etapa9b2/reversao-no-codigo-antigo.txt.

  D-558 (27/10, `ac-grade-inserir`): "quando falei dividir é dividir a pagina, usando a
      funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser feito."
  D-559 (27/10, `ac-tampa`): "Como eu decidi: sumir em todo o livro, e o Kaique escolhe por livro
      cortar ou pintar de branco" (D-097 "É para sumir totalmente."; D-092 "O Kaique escolhe por
      livro").
  D-547 / D-473 / D-066 / D-064: a tela mostra a página como sai no PDF ("precisamos que o pdf saia
      que nem está na tela"; "é só colocar uma bolinha de carregamento, pode ter uma pro livro
      inteiro e outra para a pagina que estamos").
  D-568 (`v-roda`): "sem zoom troca de página; Ctrl + roda dá zoom" + com zoom anda pela página.
  D-570 (`v-zoom-pares`): "Sim, zoom também no lado a lado".  D-571 (`v-100`): "A página inteira
      cabendo na tela".
  D-554 (`ac-margens-iguais`): "Também na tela do corte".
  D-563 (`ac-desentortar-texto`): "Tirar, voltar como era antes".  D-564 (`ac-gravura-cinza`):
      "Não fazer: gravura continua em preto e branco".
  D-020: "Ctrl+Z desfaz qualquer alteração" (lista única 1.3, 1.6, 1.7, 1.9, 4.6; promessa P-129).
  D-090 / D-091 (P-061): "usar em todas" com as exceções desmarcadas, que nunca apaga exceção.
"""

from __future__ import annotations

import copy
import inspect
import time
from pathlib import Path

import numpy as np
import pytest

fitz = pytest.importorskip("fitz")
cv2 = pytest.importorskip("cv2")
pytest.importorskip("PySide6")

from core import automatico as A  # noqa: E402

DPI = 100
AMARELADO = (170, 215, 235)            # BGR: papel velho


# --- os livros de teste -----------------------------------------------------------

def _pagina(largura: int = 600, altura: int = 840, marca: int = 0) -> np.ndarray:
    """Papel amarelado com margem larga, linhas de "texto" pretas e, no alto, `marca`
    quadradinhos (para saber qual página é qual)."""
    img = np.full((altura, largura, 3), AMARELADO, np.uint8)
    for y in range(140, altura - 160, 40):
        img[y:y + 12, 110:largura - 110] = 25
    for k in range(marca % 12):
        img[60:80, 110 + k * 24:126 + k * 24] = 0
    return img


def _aberto(marca: int = 0) -> np.ndarray:
    """Um livro aberto: duas páginas lado a lado (a dobra no meio)."""
    return np.concatenate([_pagina(marca=2 * marca), _pagina(marca=2 * marca + 1)], axis=1)


def _pdf(caminho: Path, imagens) -> str:
    doc = fitz.open()
    for img in imagens:
        ok, buffer = cv2.imencode(".png", img)
        assert ok
        largura, altura = img.shape[1] / DPI * 72, img.shape[0] / DPI * 72
        pagina = doc.new_page(width=largura, height=altura)
        pagina.insert_image(fitz.Rect(0, 0, largura, altura), stream=buffer.tobytes())
    doc.save(str(caminho))
    doc.close()
    return str(caminho)


def _paginas_do_pdf(caminho: str) -> list[np.ndarray]:
    with fitz.open(caminho) as doc:
        saida = []
        for pagina in doc:
            pix = pagina.get_pixmap(dpi=DPI, colorspace=fitz.csRGB)
            saida.append(np.frombuffer(pix.samples, np.uint8).reshape(
                pix.height, pix.width, pix.n)[..., :3].copy())
        return saida


def _gerar(janela, tmp_path: Path, nome: str) -> list[np.ndarray]:
    """O PDF do livro aberto, como o "Confirmar e processar" grava: as páginas desenhadas."""
    from core.pipeline import processar

    projeto = copy.copy(janela.projeto)
    projeto.caminho_saida = str(tmp_path / f"{nome}.pdf")
    return _paginas_do_pdf(processar(projeto))


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
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        _assentar(2)
        if condicao():
            return
        time.sleep(0.02)
    raise AssertionError(f"não aconteceu a tempo: {motivo}")


# --- D-563 e D-564: as contas que ele mandou tirar saíram -----------------------------------

def test_d563_a_conta_desentortar_so_o_bloco_do_texto_saiu():
    """D-563 (27/10/2026, Central `ac-desentortar-texto`: "Tirar, voltar como era antes
    (recomendo)"). A conta "desentortar seguindo só o bloco do texto" (D-493/D-530, etapa 10b,
    pronta e não ligada) saiu: a caixa do conteúdo do desentortar não tem mais o jeito "só o
    bloco" nem a conta das notas da margem. Falha no código antigo (a conta estava lá)."""
    from core import desentortar_scantailor as ds

    assert "so_o_bloco" not in inspect.signature(ds.caixa_do_conteudo).parameters
    assert not hasattr(ds, "_so_o_bloco_do_texto")
    assert not hasattr(ds, "BLOCO_PERCENTIL")


def test_d563_a_caixa_do_conteudo_continua_a_de_sempre():
    """D-563 ("voltar como era antes"): a caixa do conteúdo que vai ao desentortar é a de
    sempre, com o texto e as notas da margem dentro (nada ficou de fora)."""
    from core import desentortar_scantailor as ds

    img = np.full((1400, 1200, 3), 225, np.uint8)
    for y in range(160, 1260, 36):
        for x in range(260, 940, 22):
            img[y:y + 16, x:x + 14] = 30
    for y in (300, 336, 900):                           # notas da esquerda
        img[y:y + 12, 120:200] = 40
    x, _y, largura, _a = ds.caixa_do_conteudo(img, (0, 0, 1200, 1400), 300)
    assert x <= 125 and x + largura >= 930


def test_d564_a_chave_da_gravura_escura_em_cinza_saiu():
    """D-564 (27/10/2026, Central `ac-gravura-cinza`: "Não fazer: gravura continua em preto e
    branco (recomendo)"). A chave `GRAVURA_ESCURA_EM_CINZA` (D-532, etapa 9d, desligada) e a
    conta dela saíram. Falha no código antigo. A prova de que a gravura de fundo escuro do
    Palatino 74 sai em 1 bit pelo caminho inteiro é
    tests/test_decisoes_nucleo2.py::test_d564_palatino_74_continua_em_1_bit."""
    from core import filtros

    assert not hasattr(filtros, "GRAVURA_ESCURA_EM_CINZA")
    assert not hasattr(filtros, "_e_gravura_escura_ou_reticula")


# --- D-554: "Margens iguais" também na tela do Cortar ----------------------------------------

def test_d554_margens_iguais_na_tela_do_cortar_e_o_mesmo_valor_do_automatico(janela, tmp_path):
    """D-554 (27/10/2026, Central `ac-margens-iguais`: "Também na tela do corte"; confirma a
    D-494; D-075: "Mas eu vou conseguir alterar isso né?"). Na ferramenta Cortar há a caixinha
    "Margens iguais", desmarcada de fábrica; marcar liga as margens iguais DO LIVRO (o mesmo
    valor da etapa do Automático, que passa a mostrá-la marcada), numa ação do desfazer; o PDF
    sai com todas as páginas do mesmo tamanho. Falha no código antigo (não havia a caixinha)."""
    from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR

    imagens = [_pagina(600, 840), _pagina(520, 760), _pagina(640, 800)]
    janela.abrir_livro(_pdf(tmp_path / "tamanhos.pdf", imagens))
    tela = janela.tela_conferir
    tela.escolher_ferramenta(FERRAMENTA_CORTAR)
    _assentar()
    caixa = tela.caixa_margens_iguais
    assert caixa.text() == "Margens iguais" and not caixa.isHidden()
    assert caixa.isChecked() is False and janela.projeto.margens_iguais is False

    caixa.click()
    _assentar()
    assert janela.projeto.margens_iguais is True
    assert A.MARGENS in tela.paineis.automatico.estado.marcadas      # o Automático mostra
    assert "Margens iguais" in janela.acoes.feitas[-1].descricao

    tela.desfazer()
    _assentar()
    assert janela.projeto.margens_iguais is False and not caixa.isChecked()
    tela.refazer()
    _assentar()
    assert janela.projeto.margens_iguais is True and caixa.isChecked()

    paginas = _gerar(janela, tmp_path, "margens")
    tamanhos = {p.shape[:2] for p in paginas}
    assert len(paginas) == 3 and len(tamanhos) == 1, tamanhos


# --- D-568, D-570, D-571: a roda e o zoom --------------------------------------------------

def _dividido(janela, tmp_path: Path, folhas: int = 5):
    """O caminho do Kaique: abrir o livro aberto e rodar o Automático só com "Dividir"."""
    janela.abrir_livro(_pdf(tmp_path / "livro.pdf", [_aberto(f) for f in range(folhas)]))
    estado = janela.estado_do_automatico
    estado.marcadas = {A.DIVIDIR}
    estado.alcance = "livro"
    assert janela.rodar_o_automatico(esperar=True, perguntar=False)
    assert len(janela.projeto.paginas) == 2 * folhas
    return janela.tela_conferir


def _roda(vista, passos: int, ctrl: bool = False, shift: bool = False) -> None:
    """Uma volta da roda do mouse em cima da página (como o Windows manda)."""
    from PySide6.QtCore import QPoint, QPointF, Qt
    from PySide6.QtGui import QWheelEvent
    from PySide6.QtWidgets import QApplication

    teclas = Qt.NoModifier
    if ctrl:
        teclas |= Qt.ControlModifier
    if shift:
        teclas |= Qt.ShiftModifier
    centro = QPointF(vista.width() / 2, vista.height() / 2)
    evento = QWheelEvent(centro, vista.mapToGlobal(centro), QPoint(0, 0), QPoint(0, 120 * passos),
                         Qt.NoButton, teclas, Qt.NoScrollPhase, False)
    QApplication.sendEvent(vista, evento)


@pytest.mark.parametrize("ferramenta", ["mao", "endireitar"])
def test_d568_com_zoom_a_roda_anda_pela_pagina(janela, tmp_path, ferramenta):
    """D-568 (27/10/2026, Central `v-roda`: "Como ficou: sem zoom troca de página; Ctrl + roda
    dá zoom"; com zoom anda pela página). Com zoom, a roda para baixo mostra a parte de baixo
    da página (o deslocamento sobe), não troca de página e não muda o zoom; para cima volta;
    a página não sai da tela (para na beirada). Na Mão (o editor de marcar) e numa ferramenta
    de página (Endireitar). Falha no código antigo (com zoom a roda dava zoom)."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta(ferramenta)
    tela.ir_para_pagina(4)
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    vista = tela.editor_selecao if ferramenta == "mao" else tela.visualizadores["angulo"]
    _esperar(lambda: getattr(vista, "_pixmap", None) is not None, motivo="a prévia")
    tela.mudar_o_zoom(2.0)
    zoom = vista.zoom
    assert zoom > 1.9
    antes = vista.deslocamento.y()
    _roda(vista, -1)
    assert tela.indice_pagina == 4 and vista.zoom == zoom
    assert vista.deslocamento.y() < antes                 # andou para baixo na página
    for _ in range(60):                                   # muito: para na beirada
        _roda(vista, -1)
    fundo = vista.deslocamento.y()
    _roda(vista, -1)
    assert vista.deslocamento.y() == fundo and tela.indice_pagina == 4
    _roda(vista, 1)
    assert vista.deslocamento.y() > fundo                 # volta para cima
    _roda(vista, 1, ctrl=True)                            # Ctrl+roda: zoom
    assert vista.zoom > zoom
    tela.mudar_o_zoom(2.0)                                # bem perto: a página passa dos lados
    de_lado = vista.deslocamento.x()
    _roda(vista, -1, shift=True)                          # Shift: para os lados
    assert vista.deslocamento.x() < de_lado and tela.indice_pagina == 4
    tela.mudar_o_zoom(None)                               # sem zoom: troca de página
    _roda(vista, -1)
    assert tela.indice_pagina == 5


def test_d570_zoom_tambem_no_lado_a_lado(janela, tmp_path):
    """D-570 (27/10/2026, Central `v-zoom-pares`: "Sim, zoom também no lado a lado"). No "Duas
    lado a lado" o "+" da barra de baixo aumenta as páginas dos pares (a altura de cada página
    na tela cresce na mesma conta), o número mostra o zoom, Ctrl+roda também dá zoom, e
    "ajustar à tela" volta o par inteiro à tela (100%). A página da vez continua a mesma.
    Falha no código antigo (no lado a lado os botões do zoom ficavam apagados e nada mudava)."""
    from ui.widgets.paginas_rolando import DUAS

    tela = _dividido(janela, tmp_path)
    tela.ir_para_pagina(4)
    tela.definir_mostrar(DUAS)
    _assentar()
    pares = tela.lado_a_lado
    assert tela.botao_mais_zoom.isEnabled() and tela.rotulo_do_zoom.text() == "100%"
    alturas = dict(pares.altura_das_paginas())
    tela.botao_mais_zoom.click()
    _assentar()
    assert tela.rotulo_do_zoom.text() == "125%" and abs(pares.zoom - 1.25) < 1e-6
    depois = dict(pares.altura_das_paginas())
    assert all(abs(depois[i] - 1.25 * alturas[i]) < 2 for i in alturas)
    assert tela.indice_pagina == 4
    _roda(pares.viewport(), 1, ctrl=True)
    _assentar()
    assert pares.zoom > 1.5 and tela.rotulo_do_zoom.text() == f"{round(pares.zoom * 100)}%"
    tela.botao_ajustar_a_tela.click()
    _assentar()
    assert pares.zoom == 1.0 and tela.rotulo_do_zoom.text() == "100%"
    assert dict(pares.altura_das_paginas()) == alturas


def test_d571_100_por_cento_e_a_pagina_inteira_cabendo_na_tela(janela, tmp_path):
    """D-571 (27/10/2026, Central `v-100`: "A página inteira cabendo na tela (recomendo)"). A
    conferir: com "100%" na barra de baixo, a página desenhada cabe inteira na área da página
    (e encosta nela na largura ou na altura: não é menor que a tela); "ajustar à tela" leva a
    100%. Vale na Mão e numa ferramenta de página."""
    tela = _dividido(janela, tmp_path)
    tela.escolher_ferramenta("endireitar")
    janela.show()
    janela.move(-3000, -3000)
    _assentar()
    vista = tela.visualizadores["angulo"]
    _esperar(lambda: getattr(vista, "_pixmap", None) is not None, motivo="a prévia")
    tela.mudar_o_zoom(1.6)
    tela.botao_ajustar_a_tela.click()
    _assentar()
    vista.repaint()
    assert tela.rotulo_do_zoom.text() == "100%"
    from ui.widgets.visualizador import PADDING_MOLDURA

    area = vista._area
    assert area.left() >= 0 and area.top() >= 0
    assert area.right() <= vista.width() and area.bottom() <= vista.height()
    folga = 2 * PADDING_MOLDURA + 2                       # a moldura em volta da página
    assert (area.width() >= vista.width() - folga) or (area.height() >= vista.height() - folga)


# --- D-558: "dividir" na grade "Todas as páginas" --------------------------------------------

def test_d558_dividir_na_grade_nas_folhas_escolhidas_com_a_conta_do_dividir_esta(janela, tmp_path):
    """D-558 (27/10/2026, Central `ac-grade-inserir`: "quando falei dividir é dividir a pagina,
    usando a funcionalidade do scantailor que colocamos no aplicativo, é isso que deveria ser
    feito."; D-334). Livro aberto de 4 folhas, sem "Dividir": na grade "Todas as páginas",
    escolher as folhas 2 e 3 e clicar "dividir" → por trás, com andamento, as duas viram duas
    páginas cada, na lombada (a mesma conta do "dividir esta", o jeito do ScanTailor de
    fábrica); as outras ficam inteiras; numa ação só do desfazer (o Ctrl+Z junta as duas de
    novo); o PDF sai com 6 páginas, as divididas com metade da largura. Falha no código antigo
    (não havia o "dividir" na grade)."""
    from core import dividir_a_mao

    folha_aberta = np.concatenate([_pagina(), _pagina()], axis=1)
    janela.abrir_livro(_pdf(tmp_path / "aberto.pdf", [folha_aberta] * 4))
    tela = janela.tela_conferir
    assert len(janela.projeto.paginas) == 4
    medidas = []
    original = dividir_a_mao.medir_para_dividir

    def contar(projeto, folha, jeito):
        lombada, tampa = original(projeto, folha, jeito)
        medidas.append((folha, jeito, lombada.posicao))
        return lombada, tampa

    dividir_a_mao.medir_para_dividir = contar
    try:
        tela.abrir_todas_as_paginas()
        tela.todas.comecar_a_escolher([1, 2])
        _assentar()
        botao = tela.todas.botoes_da_escolha["dividir"]
        assert botao.isEnabled() and botao.text() == "dividir"
        historico = len(janela.acoes.feitas)
        botao.click()
        assert getattr(tela, "_tarefa_de_dividir", None) is not None       # por trás
        _esperar(lambda: len(janela.projeto.paginas) == 6, motivo="dividir as escolhidas")
    finally:
        dividir_a_mao.medir_para_dividir = original
    projeto = janela.projeto
    assert sorted(f for f, _j, _p in medidas) == [1, 2]
    assert all(j == "scantailor" for _f, j, _p in medidas)                 # o do ScanTailor
    assert [f.dividir for f in projeto.folhas] == [False, True, True, False]
    for f, _j, posicao in medidas:                                       # a linha medida
        assert projeto.folhas[f].posicao_corte == round(posicao, 4)
        assert abs(posicao - 0.5) < 0.05                                 # na lombada
        assert "dividir" in projeto.folhas[f].mexida_a_mao
    assert len(janela.acoes.feitas) == historico + 1                     # uma ação só
    paginas = _gerar(janela, tmp_path, "dividido")
    larguras = [p.shape[1] for p in paginas]
    assert len(paginas) == 6
    assert abs(larguras[1] - larguras[0] / 2) < larguras[0] * 0.08
    tela.desfazer()
    _assentar()
    assert len(projeto.paginas) == 4 and not any(f.dividir for f in projeto.folhas)


# --- D-559: a faixa da tampa do scanner some em todo o livro, também no Automático ----------

def _righetti_sintetico() -> np.ndarray:
    """A folha do Righetti como ela fica depois de girada (medida no livro de verdade, folha 96
    a 150 DPI; a mesma de tests/test_decisoes_dividir.py): uma tira clara da tampa em cima, a
    faixa preta de ~2 cm atravessando a folha, o fundo preto do scanner à esquerda e o livro
    aberto."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    img[:, :270] = 12
    img[105:235, :] = 12
    img[:105, :] = 236
    for y in range(300, 1200, 24):
        img[y:y + 8, 330:900] = 30
        img[y:y + 8, 1010:1580] = 30
    return img


def _com_moldura_impressa() -> np.ndarray:
    """Livro aberto com moldura impressa PRETA e grossa (4,5 mm) em cada página: tem de sobrar
    inteira (D-495; a regra da tampa não pode pegá-la)."""
    altura, largura = 1275, 1650
    img = np.full((altura, largura, 3), 240, np.uint8)
    for x0, x1 in ((60, 780), (870, 1590)):
        cv2.rectangle(img, (x0, 60), (x1, altura - 60), (15, 15, 15), 27)
        for y in range(160, altura - 160, 24):
            img[y:y + 8, x0 + 80:x1 - 80] = 30
    return img


def _faixa_em_cima(img: np.ndarray, parte: float = 0.2, cheia: float = 0.9) -> int:
    """Quantas linhas, no alto da página, são pretas de ponta a ponta (a faixa da tampa)."""
    cinza = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    alto = cinza[: int(cinza.shape[0] * parte)]
    return int(((alto < 60).mean(axis=1) > cheia).sum())


def _rodar(janela, etapas_, alcance="livro", opcoes=None) -> bool:
    """O que o Kaique faz no painel Automático: marca as etapas e roda (no mesmo fio)."""
    estado = janela.estado_do_automatico
    estado.marcadas = set(etapas_)
    estado.opcoes.update(opcoes or {})
    estado.alcance = alcance
    return janela.rodar_o_automatico(esperar=True, perguntar=False)


def test_d559_a_tampa_some_em_todo_o_livro_pelo_automatico_e_o_livro_escolhe_cortar_ou_pintar(
        janela, tmp_path):
    """D-559 (27/10/2026, Central `ac-tampa`: "Como eu decidi: sumir em todo o livro, e o Kaique
    escolhe por livro cortar ou pintar de branco"; D-097: "É para sumir totalmente." / "tem que
    ficar rente a folha de papel, não pode ter preto ali."; D-092: "O Kaique escolhe por
    livro"). Substitui a D-495/D-499 (só ao dividir à mão). Livro de 3 folhas como o Righetti
    (já de pé), o Automático só com "Endireitar" (nenhum dividir à mão): a tampa é achada nas
    três; no PDF nenhuma página tem a faixa preta em cima. Com o livro em "cortar fora" (o de
    fábrica) a página fica mais baixa que a folha (cortada na beirada da tampa); em "pintar de
    branco", do tamanho da folha, com o lugar da faixa branco. O Ctrl+Z do Automático devolve a
    folha sem a tampa. Falha no código antigo (o Automático nunca tirava a tampa)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf", [_righetti_sintetico()] * 3))
    projeto = janela.projeto
    assert projeto.borda_preta_fazer == "cortar"                       # de fábrica
    _rodar(janela, [A.ENDIREITAR])
    assert all(f.tampa_do_scanner and len(f.tampa_do_scanner) == 5 for f in projeto.folhas)
    cortadas = _gerar(janela, tmp_path, "cortar")
    assert len(cortadas) == 3
    assert all(_faixa_em_cima(p) == 0 for p in cortadas)
    folha_alta = 1275                                                  # a folha, no PDF a 100 DPI
    assert all(p.shape[0] < 0.88 * folha_alta for p in cortadas)       # cortada na tampa

    projeto.borda_preta_fazer = "pintar"
    pintadas = _gerar(janela, tmp_path, "pintar")
    assert all(_faixa_em_cima(p) == 0 for p in pintadas)
    assert all(p.shape[0] > 0.97 * folha_alta for p in pintadas)       # do tamanho da folha
    cinza = cv2.cvtColor(pintadas[0], cv2.COLOR_RGB2GRAY)
    faixa = cinza[int(0.10 * cinza.shape[0]): int(0.17 * cinza.shape[0]), int(0.3 * cinza.shape[1]):]
    assert float(faixa.mean()) > 200                                   # o lugar da faixa: branco

    janela.tela_conferir.desfazer()
    _assentar()
    assert all(f.tampa_do_scanner is None for f in projeto.folhas)


def test_d559_a_moldura_impressa_preta_nao_some_pelo_automatico(janela, tmp_path):
    """D-559 com o cuidado da D-495 ("livro com moldura impressa preta não perde a moldura"):
    o Automático procura a tampa no livro aberto com moldura preta grossa e não acha nada
    (tampa_do_scanner = [giro]: procurada, nada); a moldura sai inteira no PDF. A regra é a
    da etapa 4, passada nas 2.903 folhas do acervo sem pegar moldura nenhuma
    (relatorios/obra-etapa4/varrer-tampa-acervo.json)."""
    janela.abrir_livro(_pdf(tmp_path / "moldura.pdf", [_com_moldura_impressa()] * 2))
    projeto = janela.projeto
    _rodar(janela, [A.ENDIREITAR])
    assert all(f.tampa_do_scanner == [0] for f in projeto.folhas)
    paginas = _gerar(janela, tmp_path, "moldura")
    assert all(_faixa_em_cima(p, 0.12, 0.6) >= 10 for p in paginas)    # a linha de cima da moldura


def test_d559_a_escolha_cortar_ou_pintar_fica_a_vista_no_automatico(janela, tmp_path):
    """D-559 ("o Kaique escolhe por livro cortar ou pintar de branco") + D-092: a escolha "O que
    fica fora da página" (cortar fora / pintar de branco) do Automático vale também para a
    tampa e fica à vista com a borda preta desmarcada (antes só aparecia com ela marcada)."""
    janela.abrir_livro(_pdf(tmp_path / "tampa.pdf", [_righetti_sintetico()]))
    janela.estado_do_automatico.opcoes["borda_preta"] = False
    grande = janela.abrir_o_automatico(A.CORTAR)
    try:
        _assentar()
        assert not grande.linhas["borda_preta_fazer"].isHidden()
        assert grande.linhas["borda_preta_ate"].isHidden()                # o "até onde": só com ela
        assert "tampa do scanner" in grande.controles["borda_preta_fazer"].toolTip()
    finally:
        janela._fechar_a_janela_do_automatico()
